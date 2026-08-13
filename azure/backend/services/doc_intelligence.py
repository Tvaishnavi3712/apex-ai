"""
Azure AI Document Intelligence adapter — Apex's document extractor on Azure.

Replaces Azure AI Document Intelligence (BDA). On AWS, BDA took a blueprint schema and
returned structured fields. Azure reaches the same outcome with a two-stage
pipeline, which is also how BDA works internally:

    1. LAYOUT   — Document Intelligence performs OCR + layout/table/key-value
                  extraction (`prebuilt-layout`). Deterministic and high-fidelity
                  on forms, tables, and scanned PDFs.
    2. MAP      — the extracted text is mapped onto the Apex blueprint's field
                  schema by the model router, returning typed JSON.

Stage 2 is skipped when a purpose-built custom model is configured for the
document type, in which case Document Intelligence returns the fields directly.

Fallbacks: if Document Intelligence is unavailable the extractor degrades to
LLM-only extraction over decoded text, and finally to an empty-but-valid
envelope — so ingestion never hard-fails a pipeline.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import structlog

log = structlog.get_logger()


class DocumentIntelligenceService:
    """Azure implementation of the Apex document-extractor port."""

    def __init__(self) -> None:
        self.endpoint = os.environ.get("AZURE_DOCINTEL_ENDPOINT", "")
        self._use_mock = os.environ.get(
            "AZURE_DOCINTEL_MOCK", os.environ.get("USE_LOCAL_MOCK", "false")
        ).lower() == "true"
        self._client = None

    # ── connection ───────────────────────────────────────────────────────────
    def _get_client(self):
        if self._client is not None:
            return self._client
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.identity import DefaultAzureCredential

        if not self.endpoint:
            raise RuntimeError("AZURE_DOCINTEL_ENDPOINT is not set")
        self._client = DocumentAnalysisClient(
            endpoint=self.endpoint, credential=DefaultAzureCredential()
        )
        return self._client

    @property
    def available(self) -> bool:
        return bool(self.endpoint) and not self._use_mock

    # ── stage 1: layout / OCR ────────────────────────────────────────────────
    def analyze_layout(self, content: bytes, model: str = "prebuilt-layout") -> Dict[str, Any]:
        """
        Run Document Intelligence over the raw bytes.

        Returns {text, key_values, tables, pages} — a provider-neutral shape the
        rest of Apex can consume regardless of which cloud produced it.
        """
        if not self.available:
            return {"text": self._decode(content), "key_values": {}, "tables": [], "pages": 0}

        try:
            poller = self._get_client().begin_analyze_document(model, document=content)
            result = poller.result()

            key_values: Dict[str, str] = {}
            for kv in getattr(result, "key_value_pairs", None) or []:
                if kv.key and kv.value:
                    key_values[kv.key.content.strip()] = kv.value.content.strip()

            tables: List[List[List[str]]] = []
            for t in getattr(result, "tables", None) or []:
                grid = [["" for _ in range(t.column_count)] for _ in range(t.row_count)]
                for cell in t.cells:
                    if cell.row_index < t.row_count and cell.column_index < t.column_count:
                        grid[cell.row_index][cell.column_index] = cell.content
                tables.append(grid)

            return {
                "text": result.content or "",
                "key_values": key_values,
                "tables": tables,
                "pages": len(getattr(result, "pages", []) or []),
            }
        except Exception as e:  # noqa: BLE001 — ingestion must not hard-fail
            log.warning("docintel.analyze_failed", error=str(e))
            return {"text": self._decode(content), "key_values": {}, "tables": [], "pages": 0}

    # ── stage 2: map onto an Apex blueprint ──────────────────────────────────
    async def extract_with_blueprint(
        self, content: bytes, blueprint: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract a document into the fields declared by an Apex blueprint.

        `blueprint` accepts any of the three formats the seeder supports:
        `documentSchema.fields`, top-level `schema.properties`, or `schema_fields`.

        Returns:
            {success, fields, confidence, source, pages, missing_required}
        """
        fields_spec = self._blueprint_fields(blueprint)
        layout = self.analyze_layout(content)

        # A custom-trained model may already return the exact fields.
        direct = {k: v for k, v in layout["key_values"].items() if k in fields_spec}

        extracted: Dict[str, Any] = dict(direct)
        if len(extracted) < len(fields_spec):
            extracted.update(await self._map_with_model(layout, fields_spec, extracted))

        required = [n for n, s in fields_spec.items() if s.get("required")]
        missing = [n for n in required if not extracted.get(n)]

        return {
            "success": not missing,
            "fields": extracted,
            "confidence": self._confidence(fields_spec, extracted),
            "source": "azure-document-intelligence" if self.available else "fallback-text",
            "pages": layout["pages"],
            "missing_required": missing,
        }

    async def _map_with_model(
        self,
        layout: Dict[str, Any],
        fields_spec: Dict[str, Dict[str, Any]],
        already: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Use the model router to map extracted content onto the blueprint schema."""
        from services.azure_openai import AzureOpenAIService

        wanted = {n: s for n, s in fields_spec.items() if n not in already}
        if not wanted:
            return {}

        schema_desc = "\n".join(
            f"- {n} ({s.get('type','string')}): {s.get('description','')}"
            f"{' [REQUIRED]' if s.get('required') else ''}"
            for n, s in wanted.items()
        )
        body = layout["text"][:12000]
        if layout["key_values"]:
            body += "\n\nDetected key/value pairs:\n" + json.dumps(layout["key_values"], indent=2)

        result = await AzureOpenAIService().invoke(
            prompt=(
                f"Extract these fields from the document.\n\nFIELDS:\n{schema_desc}\n\n"
                f"DOCUMENT:\n{body}\n\n"
                "Return ONLY a JSON object keyed by field name. Use null when a value "
                "is genuinely absent — never invent one."
            ),
            system_prompt=(
                "You are a precise document-extraction engine. Return valid JSON only, "
                "with no prose or code fences. Never fabricate values."
            ),
            temperature=0.0,
        )
        if not result.get("success"):
            return {}

        return self._parse_json(result.get("response") or "")

    # ── helpers ──────────────────────────────────────────────────────────────
    @staticmethod
    def _decode(content: bytes) -> str:
        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:  # noqa: BLE001
            return ""

    @staticmethod
    def _parse_json(text: str) -> Dict[str, Any]:
        """Tolerant JSON extraction (handles ```json fences and stray prose)."""
        t = text.strip()
        if t.startswith("```"):
            t = t.split("```")[1] if "```" in t[3:] else t.lstrip("`")
            t = t[4:] if t.lower().startswith("json") else t
        start, end = t.find("{"), t.rfind("}")
        if start == -1 or end == -1:
            return {}
        try:
            parsed = json.loads(t[start : end + 1])
            return {k: v for k, v in parsed.items() if v is not None}
        except Exception:  # noqa: BLE001
            return {}

    @staticmethod
    def _blueprint_fields(blueprint: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Normalise the supported blueprint formats to {name: spec}."""
        if not blueprint:
            return {}

        bda = ((blueprint.get("documentSchema") or blueprint.get("bdaSchema")) or {}).get("fields")
        if isinstance(bda, dict):
            return bda

        props = (blueprint.get("schema") or {}).get("properties")
        if isinstance(props, dict):
            required = set((blueprint.get("schema") or {}).get("required") or [])
            return {
                n: {**s, "required": n in required or s.get("required", False)}
                for n, s in props.items()
            }

        sf = blueprint.get("schema_fields")
        if isinstance(sf, list):
            return {
                f.get("name"): {
                    "type": f.get("type", "string"),
                    "description": f.get("description", ""),
                    "required": f.get("required", False),
                }
                for f in sf
                if f.get("name")
            }
        if isinstance(sf, dict):
            return sf
        return {}

    @staticmethod
    def _confidence(spec: Dict[str, Any], extracted: Dict[str, Any]) -> float:
        if not spec:
            return 0.0
        filled = sum(1 for n in spec if extracted.get(n) not in (None, "", []))
        return round(filled / len(spec), 3)


# Provider-neutral aliases.
DocExtractor = DocumentIntelligenceService
BDAService = DocumentIntelligenceService
