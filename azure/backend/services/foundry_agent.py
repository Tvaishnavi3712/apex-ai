"""
Azure AI Foundry Agent Service adapter — Apex's agent runtime on Azure.

Replaces **Amazon Azure AI Foundry Agent Service**. On AWS, agents were Strands runtimes
invoked by ARN through the AWS CLI. On Azure the equivalent is the **Foundry
Agent Service**: a persistent agent is addressed by *agent id* inside a Foundry
project, driven with threads → messages → runs.

Design
------
`FoundryAgentService` is ~4,700 lines, but almost all of it is the per-demo
in-process simulators (`_invoke_*_simulator`) and response shaping — pure Python
with no cloud dependency. Exactly ONE method talks to the cloud runtime:

    _invoke_runtime(agent_resource_id, prompt, session_id, extra_payload)

so this class subclasses that base and overrides just that method plus the
agent-id registry. Every simulator, router, and formatter is inherited unchanged,
which means all demo modes keep working identically on Azure.

Runtime behaviour
-----------------
* `AGENT_ARNS` becomes a map of `agent_id -> Foundry agent id`, read from
  `AZURE_FOUNDRY_AGENTS` (JSON) or `AZURE_FOUNDRY_AGENT_<AGENT_ID>` env vars.
* Any agent without a configured Foundry id resolves to the in-process
  simulator — the same proven, zero-cold-start path the demos already use.
* Sessions map to Foundry **threads**, so multi-turn state is preserved
  server-side (the Azure analogue of Foundry Agent Service's runtime session).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import structlog

from services.agent_simulators import AgentSimulatorBase

log = structlog.get_logger()


def _load_agent_map() -> Dict[str, str]:
    """
    Build {apex_agent_id: foundry_agent_id}.

    Sources, in priority order:
      1. AZURE_FOUNDRY_AGENTS — a JSON object, e.g. {"mentor-agent": "asst_abc123"}
      2. AZURE_FOUNDRY_AGENT_<UPPER_SNAKE_AGENT_ID> — one var per agent
    """
    mapping: Dict[str, str] = {}

    raw = os.environ.get("AZURE_FOUNDRY_AGENTS", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                mapping.update({str(k): str(v) for k, v in parsed.items()})
        except json.JSONDecodeError:
            log.warning("foundry.agent_map_parse_failed")

    prefix = "AZURE_FOUNDRY_AGENT_"
    for key, value in os.environ.items():
        if key.startswith(prefix) and value:
            agent_id = key[len(prefix):].lower().replace("_", "-")
            mapping[agent_id] = value

    return mapping


class FoundryAgentService(AgentSimulatorBase):
    """Azure implementation of the Apex agent-runtime port."""

    # Runtime id registry. Empty by default: every agent then routes
    # to its in-process simulator, which is how the demos run.
    AGENT_ARNS: Dict[str, str] = _load_agent_map()

    def __init__(self, region: str = "eastus") -> None:
        # The base class holds only simulators; no cloud client setup needed.
        self.region = os.environ.get("AZURE_LOCATION", region)
        self.project_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
        self.default_model = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4")
        self._use_mock = os.environ.get(
            "AZURE_FOUNDRY_MOCK", os.environ.get("USE_LOCAL_MOCK", "false")
        ).lower() == "true"
        self._client = None
        # Refresh in case env was loaded after import.
        if not self.AGENT_ARNS:
            type(self).AGENT_ARNS = _load_agent_map()

    # ── connection ───────────────────────────────────────────────────────────
    @property
    def available(self) -> bool:
        """True when a real Foundry project is configured and usable."""
        return bool(self.project_endpoint) and not self._use_mock

    def _get_client(self):
        if self._client is not None:
            return self._client
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        if not self.project_endpoint:
            raise RuntimeError("AZURE_AI_PROJECT_ENDPOINT is not set")
        self._client = AIProjectClient(
            endpoint=self.project_endpoint, credential=DefaultAzureCredential()
        )
        return self._client

    # ── the single overridden seam ───────────────────────────────────────────
    async def _invoke_runtime(
        self,
        agent_resource_id: str,
        prompt: str,
        session_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a Foundry agent.

        Name is retained so all inherited callers work unchanged; `agent_resource_id`
        carries the Foundry **agent id** on Azure. Returns: {success, response, reasoning, actions_taken}.
        """
        if not self.available:
            return {
                "success": False,
                "error": "Foundry agent runtime not configured — using simulator",
                "response": None,
            }

        try:
            return await self._invoke_foundry_agent(agent_resource_id, prompt, session_id, extra_payload)
        except Exception as e:  # noqa: BLE001 — never break the caller
            log.error("foundry.invoke_failed", agent=agent_resource_id, error=str(e))
            return {"success": False, "error": str(e), "response": None}

    async def _invoke_foundry_agent(
        self,
        foundry_agent_id: str,
        prompt: str,
        session_id: Optional[str] = None,
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """threads → messages → run, then read the assistant's reply + tool trace."""
        import asyncio

        def _run_sync() -> Dict[str, Any]:
            client = self._get_client()
            agents = client.agents

            # A session maps to a Foundry thread, preserving multi-turn state.
            thread_id = self._thread_for_session(agents, session_id)

            content = prompt
            if extra_payload:
                content = f"{prompt}\n\n[context]\n{json.dumps(extra_payload)}"
            agents.messages.create(thread_id=thread_id, role="user", content=content)

            run = agents.runs.create_and_process(
                thread_id=thread_id, agent_id=foundry_agent_id
            )
            if getattr(run, "status", None) == "failed":
                return {
                    "success": False,
                    "error": str(getattr(run, "last_error", "run failed")),
                    "response": None,
                }

            text = self._latest_assistant_text(agents, thread_id)
            reasoning, actions = self._run_trace(agents, thread_id, run)
            return {
                "success": bool(text),
                "response": text,
                "reasoning": reasoning,
                "actions_taken": actions,
            }

        return await asyncio.to_thread(_run_sync)

    # ── helpers ──────────────────────────────────────────────────────────────
    _threads: Dict[str, str] = {}

    def _thread_for_session(self, agents, session_id: Optional[str]) -> str:
        """Reuse a thread per session so conversations keep context."""
        if session_id and session_id in self._threads:
            return self._threads[session_id]
        thread = agents.threads.create()
        if session_id:
            self._threads[session_id] = thread.id
        return thread.id

    @staticmethod
    def _latest_assistant_text(agents, thread_id: str) -> str:
        """Most recent assistant message as plain text."""
        try:
            for msg in agents.messages.list(thread_id=thread_id):
                if getattr(msg, "role", "") != "assistant":
                    continue
                parts = []
                for c in getattr(msg, "content", None) or []:
                    t = getattr(c, "text", None)
                    if t is not None:
                        parts.append(getattr(t, "value", str(t)))
                    elif isinstance(c, dict) and "text" in c:
                        v = c["text"]
                        parts.append(v.get("value", "") if isinstance(v, dict) else str(v))
                if parts:
                    return "\n".join(parts).strip()
        except Exception as e:  # noqa: BLE001
            log.warning("foundry.read_messages_failed", error=str(e))
        return ""

    @staticmethod
    def _run_trace(agents, thread_id: str, run) -> tuple:
        """Extract reasoning steps + tool calls so the Audit Lens stays populated."""
        reasoning, actions = [], []
        try:
            for step in agents.run_steps.list(thread_id=thread_id, run_id=run.id):
                stype = getattr(step, "type", "")
                reasoning.append({"step": stype, "status": getattr(step, "status", "")})
                details = getattr(step, "step_details", None)
                for call in (getattr(details, "tool_calls", None) or []):
                    name = getattr(call, "type", "tool")
                    fn = getattr(call, "function", None)
                    if fn is not None:
                        name = getattr(fn, "name", name)
                    actions.append(name)
        except Exception:  # noqa: BLE001 — trace is best-effort
            pass
        return reasoning, actions

    # ── introspection ────────────────────────────────────────────────────────
    def runtime_status(self) -> Dict[str, Any]:
        """Surface which agents are backed by a real Foundry runtime."""
        return {
            "provider": "azure-ai-foundry-agent-service",
            "project_endpoint": self.project_endpoint or None,
            "configured_agents": sorted(self.AGENT_ARNS.keys()),
            "mode": "live" if self.available else "simulator",
        }


# Provider-neutral aliases.
AgentRuntime = FoundryAgentService
