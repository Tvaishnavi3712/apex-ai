"""
Foundry runtime shim — the Azure replacement for `foundry_runtime` + `strands`.

On AWS each agent was a Strands app:

    from foundry_runtime.runtime import FoundryAgentApp
    from strands import Agent, tool
    from strands.models import AzureOpenAIModel

    app   = FoundryAgentApp()
    model = AzureOpenAIModel(model_id="us.anthropic...", region_name="us-east-1")
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[...])

    @app.entrypoint
    def invoke(payload): ...

This module provides the same four symbols backed by **Azure OpenAI / Azure AI
Foundry Agent Service**, so each agent file only needs its import block changed —
every tool function, system prompt, and helper (700+ lines per agent) is
untouched and keeps working.

Two execution modes:

* **local** (default) — tools are dispatched in-process via Azure OpenAI function
  calling. Fast, no provisioning, ideal for demos and tests.
* **foundry** — `deploy_foundry_agents.py` registers the agent (instructions +
  tool schemas) as a persistent Foundry agent; `AZURE_FOUNDRY_AGENT_<ID>` then
  points the backend at it.
"""

from __future__ import annotations

import inspect
import json
import os
import typing as t
from dataclasses import dataclass, field

__all__ = ["tool", "AzureOpenAIModel", "Agent", "FoundryAgentApp"]


# ── @tool ────────────────────────────────────────────────────────────────────
_PY_TO_JSON = {
    str: "string", int: "integer", float: "number", bool: "boolean",
    list: "array", dict: "object",
}


def tool(fn: t.Callable) -> t.Callable:
    """
    Mark a function as an agent tool (drop-in for `strands.tool`).

    Derives an OpenAI/Foundry function schema from the signature + docstring, so
    existing tool definitions need no changes.
    """
    sig = inspect.signature(fn)
    props: dict[str, t.Any] = {}
    required: list[str] = []

    for name, p in sig.parameters.items():
        if name in ("self", "cls"):
            continue
        ann = p.annotation
        origin = t.get_origin(ann)
        if origin is t.Union:                       # Optional[X] -> X
            args = [a for a in t.get_args(ann) if a is not type(None)]
            ann = args[0] if args else str
        props[name] = {"type": _PY_TO_JSON.get(ann, "string"),
                       "description": f"{name} parameter"}
        if p.default is inspect.Parameter.empty:
            required.append(name)

    fn.__tool_schema__ = {                          # type: ignore[attr-defined]
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": (fn.__doc__ or fn.__name__).strip().split("\n")[0][:1024],
            "parameters": {"type": "object", "properties": props, "required": required},
        },
    }
    fn.__is_tool__ = True                           # type: ignore[attr-defined]
    return fn


# ── model ────────────────────────────────────────────────────────────────────
@dataclass
class AzureOpenAIModel:
    """Azure OpenAI deployment descriptor."""

    model_id: str = ""
    region_name: str = ""          # accepted and ignored; kept for signature parity
    deployment: str = field(default="")

    def __post_init__(self) -> None:
        if not self.deployment:
            self.deployment = self._map(self.model_id)

    @staticmethod
    def _map(model_id: str) -> str:
        """Azure OpenAI model id -> Azure OpenAI deployment."""
        m = (model_id or "").lower()
        if any(k in m for k in ("haiku", "mini", "micro", "lite")):
            return os.environ.get("AZURE_OPENAI_DEPLOYMENT_FAST", "gpt-5-mini")
        if any(k in m for k in ("opus", "pro")):
            return os.environ.get("AZURE_OPENAI_DEPLOYMENT_QUALITY", "gpt-5.4")
        return os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4")


# Legacy alias retained only for un-migrated files.
AzureOpenAIModel = AzureOpenAIModel


# ── agent ────────────────────────────────────────────────────────────────────
class _Result:
    """Agent result wrapper (`result.message`)."""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:            # pragma: no cover
        return self.message


class Agent:
    """Azure-backed agent with tool calling."""

    def __init__(
        self,
        model: AzureOpenAIModel | None = None,
        system_prompt: str = "",
        tools: list[t.Callable] | None = None,
        **_: t.Any,
    ) -> None:
        self.model = model or AzureOpenAIModel()
        self.system_prompt = system_prompt
        self.tools = tools or []
        self._by_name = {f.__name__: f for f in self.tools}
        self._client = None

    # -- schemas used by both local dispatch and Foundry provisioning --
    @property
    def tool_schemas(self) -> list[dict]:
        return [getattr(f, "__tool_schema__") for f in self.tools
                if hasattr(f, "__tool_schema__")]

    def _get_client(self):
        if self._client is not None:
            return self._client
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        from openai import AzureOpenAI

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
        if not endpoint:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT is not set")
        self._client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            ),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )
        return self._client

    def __call__(self, message: str, max_turns: int = 6) -> _Result:
        """Run one agent turn, dispatching tool calls in-process."""
        if os.environ.get("AZURE_OPENAI_MOCK", os.environ.get("USE_LOCAL_MOCK", "false")).lower() == "true":
            return _Result(f"[local-mock:{self.model.deployment}] {message[:180]}")

        messages: list[dict[str, t.Any]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": message})

        client = self._get_client()
        schemas = self.tool_schemas

        for _ in range(max_turns):
            kwargs: dict[str, t.Any] = {
                "model": self.model.deployment,
                "messages": messages,
                "max_completion_tokens": 4096,
            }
            if schemas:
                kwargs["tools"] = schemas
                kwargs["tool_choice"] = "auto"

            resp = client.chat.completions.create(**kwargs)
            choice = resp.choices[0]
            calls = getattr(choice.message, "tool_calls", None)

            if not calls:
                return _Result(choice.message.content or "")

            messages.append({
                "role": "assistant",
                "content": choice.message.content,
                "tool_calls": [
                    {"id": c.id, "type": "function",
                     "function": {"name": c.function.name, "arguments": c.function.arguments}}
                    for c in calls
                ],
            })

            for c in calls:
                messages.append({
                    "role": "tool",
                    "tool_call_id": c.id,
                    "content": self._run_tool(c.function.name, c.function.arguments),
                })

        return _Result("Maximum tool-calling turns reached.")

    def _run_tool(self, name: str, raw_args: str) -> str:
        fn = self._by_name.get(name)
        if fn is None:
            return json.dumps({"error": f"unknown tool: {name}"})
        try:
            args = json.loads(raw_args) if raw_args else {}
            return json.dumps(fn(**args), default=str)
        except Exception as e:  # noqa: BLE001 — a tool error must not kill the run
            return json.dumps({"error": str(e)})


# ── app ──────────────────────────────────────────────────────────────────────
class FoundryAgentApp:
    """Registers the agent entrypoint and serves it."""

    def __init__(self, agent: "Agent | None" = None, **_: t.Any) -> None:
        # Some agents construct the app as `FoundryAgentApp(agent=agent)`;
        # extra kwargs are accepted and ignored for signature parity.
        self._entrypoint: t.Callable | None = None
        self.agent: Agent | None = agent

    def entrypoint(self, fn: t.Callable) -> t.Callable:
        self._entrypoint = fn
        return fn

    def invoke(self, payload: dict) -> t.Any:
        if self._entrypoint is None:
            raise RuntimeError("No @app.entrypoint registered")
        return self._entrypoint(payload)

    def run(self) -> None:
        """Serve the agent over HTTP (parity with Foundry Agent Service's local runtime)."""
        import uvicorn
        from fastapi import FastAPI

        api = FastAPI(title="Apex Foundry Agent")

        @api.get("/ping")
        def ping() -> dict:
            return {"status": "healthy", "runtime": "azure-ai-foundry"}

        @api.post("/invocations")
        def invocations(payload: dict) -> t.Any:
            return self.invoke(payload)

        uvicorn.run(api, host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))


FoundryAgentApp = FoundryAgentApp
