"""
Azure OpenAI-runtime compatibility shim backed by Azure OpenAI.

Action handlers were written against the AWS azure-openai client and call
`invoke_model(modelId=..., body=...)` with the Anthropic Messages payload,
then read `response['body'].read()`.

Rather than rewrite every handler, this module provides an object with the same
surface that translates to Azure OpenAI and returns a Azure OpenAI-shaped response.
Only the client construction changes; handler bodies work unchanged on Azure:

    # AWS build
    azure_openai = boto3.client("azure-openai", region_name=...)
    # Azure build
    llm = get_bedrock_runtime()

Auth is Entra ID (DefaultAzureCredential) — no keys.
"""

from __future__ import annotations

import io
import json
import os
from typing import Any, Dict, List, Optional


def _deployment_for(model_id: str) -> str:
    """Map a Azure OpenAI model id / logical tier onto an Azure OpenAI deployment."""
    m = (model_id or "").lower()
    if "haiku" in m or "mini" in m or "micro" in m or "lite" in m:
        return os.environ.get("AZURE_OPENAI_DEPLOYMENT_FAST", "gpt-5-mini")
    if "opus" in m or "pro" in m:
        return os.environ.get("AZURE_OPENAI_DEPLOYMENT_QUALITY", "gpt-5.4")
    return os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4")


class _Body:
    """Mimics botocore's StreamingBody so `response['body'].read()` works."""

    def __init__(self, payload: bytes) -> None:
        self._buf = io.BytesIO(payload)

    def read(self, *args: Any, **kwargs: Any) -> bytes:
        return self._buf.read()


class AzureBedrockRuntimeShim:
    """Drop-in replacement for a azure-openai client, backed by Azure OpenAI."""

    def __init__(self, region_name: Optional[str] = None) -> None:
        self.region = region_name or os.environ.get("AZURE_LOCATION", "eastus")
        self.endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        self._use_mock = os.environ.get(
            "AZURE_OPENAI_MOCK", os.environ.get("USE_LOCAL_MOCK", "false")
        ).lower() == "true"
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        from openai import AzureOpenAI

        if not self.endpoint:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set")
        self._client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            ),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
        return self._client

    # ── the Azure OpenAI-compatible entrypoint ────────────────────────────────────
    def invoke_model(
        self,
        modelId: str = "",            # noqa: N803 — boto3 casing, kept deliberately
        body: Any = None,
        contentType: str = "application/json",   # noqa: N803
        accept: str = "application/json",
        **_: Any,
    ) -> Dict[str, Any]:
        """Translate an Anthropic Messages request into an Azure OpenAI call."""
        req = self._parse_body(body)
        messages = self._to_openai_messages(req)
        deployment = _deployment_for(modelId)

        if self._use_mock:
            text = "[local-mock] " + (messages[-1]["content"][:160] if messages else "")
            return {"body": _Body(self._azure_openai_shape(text, deployment))}

        resp = self._get_client().chat.completions.create(
            model=deployment,
            messages=messages,
            max_completion_tokens=int(req.get("max_tokens", 4096)),
            temperature=float(req.get("temperature", 0.3)),
        )
        text = resp.choices[0].message.content or ""
        usage = {
            "input_tokens": getattr(resp.usage, "prompt_tokens", 0),
            "output_tokens": getattr(resp.usage, "completion_tokens", 0),
        }
        return {"body": _Body(self._azure_openai_shape(text, deployment, usage))}

    # ── translation helpers ──────────────────────────────────────────────────
    @staticmethod
    def _parse_body(body: Any) -> Dict[str, Any]:
        if body is None:
            return {}
        if isinstance(body, (bytes, bytearray)):
            body = body.decode("utf-8", errors="ignore")
        if isinstance(body, str):
            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {"messages": [{"role": "user", "content": body}]}
        return body if isinstance(body, dict) else {}

    @staticmethod
    def _to_openai_messages(req: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Anthropic Messages -> OpenAI chat messages.

        Multimodal blocks (e.g. base64 documents/images) are reduced to their
        text parts, with a marker so the model knows a document was attached.
        """
        out: List[Dict[str, str]] = []
        if req.get("system"):
            out.append({"role": "system", "content": str(req["system"])})

        for msg in req.get("messages", []) or []:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if isinstance(content, str):
                out.append({"role": role, "content": content})
                continue

            parts: List[str] = []
            for block in content or []:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict):
                    if block.get("type") == "text":
                        parts.append(block.get("text", ""))
                    elif block.get("type") in ("image", "document"):
                        parts.append("[attached document]")
            out.append({"role": role, "content": "\n".join(p for p in parts if p)})

        return out or [{"role": "user", "content": ""}]

    @staticmethod
    def _azure_openai_shape(text: str, model: str, usage: Optional[Dict[str, int]] = None) -> bytes:
        """Wrap a completion in the Anthropic-on-Azure OpenAI response shape."""
        return json.dumps({
            "id": "msg_azure",
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": [{"type": "text", "text": text}],
            "stop_reason": "end_turn",
            "usage": usage or {"input_tokens": 0, "output_tokens": 0},
        }).encode()


_shim: Optional[AzureBedrockRuntimeShim] = None


def get_bedrock_runtime(region_name: Optional[str] = None) -> AzureBedrockRuntimeShim:
    """Process-wide azure-openai-compatible client backed by Azure OpenAI."""
    global _shim
    if _shim is None:
        _shim = AzureBedrockRuntimeShim(region_name)
    return _shim
