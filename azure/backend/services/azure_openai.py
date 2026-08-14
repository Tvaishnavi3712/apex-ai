"""
Azure OpenAI / AI Foundry adapter — the Azure implementation of Apex's model router.

Apex's model router on Azure: a single `invoke()` entrypoint with logical
model tiers resolved to Azure OpenAI deployments.

Multi-LLM tiering is preserved: logical model names map to Azure *deployment*
names (set per environment), rather than to Azure OpenAI inference-profile IDs. That
keeps the cost-optimised / balanced / quality-first routing story intact on Azure.

Auth: Entra ID via DefaultAzureCredential (no API keys). Falls back to a
deterministic stub when `USE_LOCAL_MOCK=true` so local dev and demos never block
on a model endpoint.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger()

# Logical name -> Azure deployment name. Override per environment via env vars.
# Deployment names must exist on the target Azure OpenAI / AI Foundry resource.
_DEPLOY = os.environ.get  # shorthand


class AzureOpenAIService:
    """Azure implementation of the Apex model-router port."""

    # Apex on Azure runs on the latest OpenAI models (not Claude, as on Azure).
    # Logical tier names are the primary API; the "claude-*" keys are kept only
    # so shared/ported call sites resolve without edits.
    _FAST    = _DEPLOY("AZURE_OPENAI_DEPLOYMENT_FAST",    "gpt-5-mini")
    _BALANCE = _DEPLOY("AZURE_OPENAI_DEPLOYMENT",         "gpt-5.4")   # latest GA
    # NOTE: gpt-5-pro is a reasoning model served ONLY by the Responses API — it
    # returns 400 on chat.completions. Quality tier therefore uses the newest
    # chat-completions-capable model. Set AZURE_OPENAI_DEPLOYMENT_QUALITY to
    # override once Responses-API support is added.
    _QUALITY = _DEPLOY("AZURE_OPENAI_DEPLOYMENT_QUALITY", "gpt-5.4")
    _EMBED   = _DEPLOY("AZURE_OPENAI_DEPLOYMENT_EMBED",   "text-embedding-3-small")

    MODELS: Dict[str, str] = {
        # ── primary (OpenAI-native tier names) ──
        "fast":            _FAST,
        "balanced":        _BALANCE,
        "quality":         _QUALITY,
        "embeddings":      _EMBED,
        # explicit model pins
        "gpt-5-mini":      _FAST,
        "gpt-5.4":         _BALANCE,
        "gpt-5-pro":       _QUALITY,
        # ── compatibility aliases (ported AWS call sites) ──
        "claude-haiku":    _FAST,
        "nova-lite":       _FAST,
        "claude-3-sonnet": _BALANCE,
        "claude-sonnet":   _BALANCE,
        "claude-3-opus":   _QUALITY,
        "claude-opus":     _QUALITY,
    }
    DEFAULT_MODEL = "balanced"

    def __init__(self, region: str = "eastus"):
        self.region = region
        self.endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21")
        # Independent of USE_LOCAL_MOCK: Azure OpenAI is publicly reachable, so it can
        # run for real while the private data stores stay mocked. Defaults to the
        # global flag when AZURE_OPENAI_MOCK is unset.
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
            raise RuntimeError(
                "AZURE_OPENAI_ENDPOINT is not set. Set it in backend/.env.azure, "
                "or set USE_LOCAL_MOCK=true for local development."
            )
        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )
        self._client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            azure_ad_token_provider=token_provider,
            api_version=self.api_version,
        )
        return self._client

    def resolve_deployment(self, model: str) -> str:
        """Logical model name -> Azure deployment name."""
        return self.MODELS.get(model, self.MODELS[self.DEFAULT_MODEL])

    async def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 4096,
        temperature: float = 0.3,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a model with a prompt. 

        Returns:
            {success, response, model, usage:{input_tokens,output_tokens}, stop_reason}
        """
        deployment = self.resolve_deployment(model)

        if self._use_mock:
            return {
                "success": True,
                "response": f"[local-mock:{deployment}] {prompt[:180]}",
                "model": deployment,
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "stop_reason": "stop",
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = self._get_client().chat.completions.create(
                model=deployment,
                messages=messages,
                max_completion_tokens=max_tokens,
                temperature=temperature,
            )
            choice = resp.choices[0]
            return {
                "success": True,
                "response": choice.message.content,
                "model": deployment,
                "usage": {
                    "input_tokens": getattr(resp.usage, "prompt_tokens", 0),
                    "output_tokens": getattr(resp.usage, "completion_tokens", 0),
                },
                "stop_reason": choice.finish_reason,
            }
        except Exception as e:  # noqa: BLE001
            logger.error("azure_openai.invoke_failed", deployment=deployment, error=str(e))
            return {"success": False, "error": str(e), "response": None, "model": deployment}

    async def analyze_conversation(
        self,
        transcript: str,
        analysis_type: str = "summary",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Convenience wrapper for transcript analysis."""
        prompts = {
            "summary":   "Summarize this conversation, capturing decisions and outcomes.",
            "sentiment": "Analyze sentiment and emotional trajectory. Return JSON.",
            "claims":    "Extract any claims, commitments, or obligations. Return JSON.",
            "fraud":     "Flag any fraud or risk indicators with rationale. Return JSON.",
            "coaching":  "Provide coaching feedback on handling and next-best actions.",
        }
        return await self.invoke(
            prompt=f"{prompts.get(analysis_type, prompts['summary'])}\n\n---\n{transcript}",
            system_prompt="You are an expert analyst. Be precise and cite evidence from the text.",
            context=context,
        )


# Provider-neutral alias.
ModelRouter = AzureOpenAIService


_router: Optional[AzureOpenAIService] = None


def get_model_router(region: str = "eastus") -> AzureOpenAIService:
    """Process-wide Azure OpenAI model router."""
    global _router
    if _router is None:
        _router = AzureOpenAIService(region=region)
    return _router


class MessagesCompatClient:
    """
    Messages-style client over Azure OpenAI.

    Some API routes were written against a `invoke_model(modelId=, body=)` call
    that takes an Anthropic-Messages payload (including base64 image blocks) and
    returns `{"content":[{"text": ...}]}`. This adapter preserves that shape so
    those routes work unchanged, translating to Azure OpenAI underneath —
    including true multimodal passthrough for image content.
    """

    def __init__(self, region: str = "eastus") -> None:
        self._svc = AzureOpenAIService(region=region)

    def invoke_model(self, modelId: str = "", body: Any = None, **_: Any) -> Dict[str, Any]:  # noqa: N803
        import base64 as _b64
        import io
        import json as _json

        req = body
        if isinstance(req, (bytes, bytearray)):
            req = req.decode("utf-8", errors="ignore")
        if isinstance(req, str):
            try:
                req = _json.loads(req)
            except _json.JSONDecodeError:
                req = {"messages": [{"role": "user", "content": req}]}
        req = req if isinstance(req, dict) else {}

        messages: list = []
        if req.get("system"):
            messages.append({"role": "system", "content": str(req["system"])})

        for msg in req.get("messages", []) or []:
            content = msg.get("content", "")
            if isinstance(content, str):
                messages.append({"role": msg.get("role", "user"), "content": content})
                continue
            parts: list = []
            for block in content or []:
                if not isinstance(block, dict):
                    parts.append({"type": "text", "text": str(block)})
                elif block.get("type") == "text":
                    parts.append({"type": "text", "text": block.get("text", "")})
                elif block.get("type") == "image":
                    src = block.get("source", {}) or {}
                    media = src.get("media_type", "image/png")
                    data = src.get("data", "")
                    parts.append({"type": "image_url",
                                  "image_url": {"url": f"data:{media};base64,{data}"}})
            messages.append({"role": msg.get("role", "user"), "content": parts})

        deployment = self._svc.resolve_deployment(modelId or self._svc.DEFAULT_MODEL)
        if self._svc._use_mock:  # noqa: SLF001 — same module
            text = "[local-mock] messages-compat"
        else:
            resp = self._svc._get_client().chat.completions.create(  # noqa: SLF001
                model=deployment,
                messages=messages,
                max_completion_tokens=int(req.get("max_tokens", 4096)),
            )
            text = resp.choices[0].message.content or ""

        payload = _json.dumps({
            "content": [{"type": "text", "text": text}],
            "model": deployment,
            "stop_reason": "end_turn",
        }).encode()

        class _Body:
            def __init__(self, b: bytes) -> None:
                self._b = io.BytesIO(b)

            def read(self, *a: Any, **k: Any) -> bytes:
                return self._b.read()

        return {"body": _Body(payload)}


_messages_client: Optional[MessagesCompatClient] = None


def get_messages_client(region: str = "eastus") -> MessagesCompatClient:
    """Messages-shaped Azure OpenAI client for routes that post image/text blocks."""
    global _messages_client
    if _messages_client is None:
        _messages_client = MessagesCompatClient(region=region)
    return _messages_client
