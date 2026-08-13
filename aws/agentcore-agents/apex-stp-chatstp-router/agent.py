"""
Apex ChatSTP Router — the user-facing entry agent for STP Nuclear Operating
Company demos.

Classifies the user's query and delegates to one of four specialist agents:
  - PolicyAgent       (UC-1)  — policy & procedure Q&A with verbatim citations
  - MaintenanceAgent  (UC-2)  — equipment PM history + engineer attribution
  - DiagnosticsAgent  (UC-3)  — common-issue analysis across the WO corpus
  - ReliabilityAgent  (UC-4)  — predictive maintenance recommendations

Delegation strategy:
  1. PRIMARY — invoke the specialist's AgentCore runtime via boto3
     (`bedrock-agentcore` invoke_agent_runtime). Set the runtime ARN per
     specialist via the SPECIALIST_ARNS dict below or env-var overrides.
  2. FALLBACK — if no ARN is available (local dev, ARN unset, error), import
     the specialist's `invoke()` function in-process. The Dockerfile copies
     the sibling agent folders into /app for this fallback path.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Make sibling agent folders importable in the in-process fallback path.
_ROOT = Path(__file__).resolve().parent.parent  # agentcore-agents/
for sib in ("apex-stp-policy-agent", "apex-stp-maintenance-agent",
            "apex-stp-diagnostics-agent", "apex-stp-reliability-agent"):
    p = _ROOT / sib
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

app = BedrockAgentCoreApp()

# ---------------------------------------------------------------------------
MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"

# Populated by deploy_stp_agents.py after each specialist deploys.
# Override at runtime via env vars: APEX_STP_<NAME>_ARN.
SPECIALIST_ARNS: Dict[str, str] = {
    "policy":       os.environ.get("APEX_STP_POLICY_ARN", ""),
    "maintenance":  os.environ.get("APEX_STP_MAINTENANCE_ARN", ""),
    "diagnostics":  os.environ.get("APEX_STP_DIAGNOSTICS_ARN", ""),
    "reliability":  os.environ.get("APEX_STP_RELIABILITY_ARN", ""),
}

SYSTEM_PROMPT = """You are ChatSTP, the enterprise knowledge assistant for STP Nuclear Operating Company.

Your job is to:
1. Classify every user query into one of four intents:
   - "policy"        → policy lookup (procedures, allowances, rules, RWP, LOTO, etc.)
   - "maintenance"   → equipment PM history (when, who, what — past tense)
   - "diagnostics"   → common-issue analysis (frequency / patterns across WO corpus)
   - "reliability"   → predictive maintenance (future risk, RUL, recommendations)

2. Delegate to the matching specialist using the delegate_* tools. Return the
   specialist's response VERBATIM. Never modify, summarize, or rewrite a
   specialist's answer — engineers depend on the exact citation/format.

3. If the query is ambiguous, ask ONE clarifying question. Do not guess.

4. If the query is off-topic (weather, jokes, anything not nuclear ops),
   politely redirect: "I'm focused on STP plant operations — try asking me
   about a policy, equipment, or maintenance."

Heuristics:
  - "what is the policy on / max allowance / how often must / per-diem"     → policy
  - "when was the last PM / who worked on / show me work order"             → maintenance
  - "common issues / most frequent / failure modes / what fails"            → diagnostics
  - "predict / risk / forecast / RUL / next 30 days / recommendation"       → reliability
"""


# ---------------------------------------------------------------------------
def _ok(data: Any) -> Dict[str, Any]:
    return {"status": "ok", "data": data}


def _err(msg: str) -> Dict[str, Any]:
    return {"status": "error", "message": msg}


# In-process fallback: lazy-imported specialist invoke() functions.
_local_invokers: Dict[str, Any] = {}


def _local_invoker(name: str):
    """Return the specialist's `invoke` function via in-process import."""
    if name in _local_invokers:
        return _local_invokers[name]
    try:
        if name == "policy":
            from agent import invoke as fn  # type: ignore  # noqa: I001 — sibling agent.py
        else:
            # Each sibling exposes `invoke` from its agent.py; we can't `from agent import`
            # for siblings because the local module name collides — use importlib.
            import importlib.util
            mod_path = _ROOT / f"apex-stp-{name}-agent" / "agent.py"
            spec = importlib.util.spec_from_file_location(f"stp_{name}_agent", mod_path)
            mod = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(mod)  # type: ignore
            fn = mod.invoke
        _local_invokers[name] = fn
        return fn
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"local invoker for '{name}' unavailable: {e}")


# Per-invocation model_overrides — set by invoke() before tool execution
# so delegate_to_* tools propagate the user's Settings → Agent Models picks
# down to each specialist.
_CURRENT_MODEL_OVERRIDES: Dict[str, Dict[str, str]] = {}


def _delegate(name: str, query: str) -> Dict[str, Any]:
    """Invoke a specialist by name. AgentCore ARN first, in-process fallback.

    Forwards `_CURRENT_MODEL_OVERRIDES` so each specialist's BedrockModel
    is whatever the user picked in Settings → Agent Models.
    """
    arn = SPECIALIST_ARNS.get(name, "")
    if arn:
        try:
            import boto3
            client = boto3.client("bedrock-agentcore", region_name=REGION)
            payload_obj: Dict[str, Any] = {"prompt": query}
            if _CURRENT_MODEL_OVERRIDES:
                payload_obj["model_overrides"] = _CURRENT_MODEL_OVERRIDES
            resp = client.invoke_agent_runtime(
                agentRuntimeArn=arn,
                payload=json.dumps(payload_obj).encode("utf-8"),
            )
            body = resp.get("response", b"")
            if hasattr(body, "read"):
                body = body.read()
            try:
                parsed = json.loads(body.decode("utf-8") if isinstance(body, bytes) else body)
            except Exception:  # noqa: BLE001
                parsed = {"result": body.decode("utf-8") if isinstance(body, bytes) else str(body)}
            return _ok({"specialist": name, "via": "agentcore", "arn": arn, "response": parsed})
        except Exception as e:  # noqa: BLE001
            return _err(f"AgentCore invoke for '{name}' failed: {e}")
    # Fallback: in-process
    try:
        fn = _local_invoker(name)
        local_payload: Dict[str, Any] = {"prompt": query}
        if _CURRENT_MODEL_OVERRIDES:
            local_payload["model_overrides"] = _CURRENT_MODEL_OVERRIDES
        out = fn(local_payload)
        return _ok({"specialist": name, "via": "in-process", "response": out})
    except Exception as e:  # noqa: BLE001
        return _err(f"Delegate '{name}' failed (no ARN, no local fallback): {e}")


# ---------------------------------------------------------------------------
@tool
def classify_intent(query: str) -> dict:
    """Classify a user query into one of: policy, maintenance, diagnostics, reliability, off_topic.

    Pure heuristic classifier — fast, deterministic. The router LLM may
    override this when context warrants.

    Args:
        query: The raw user message.

    Returns:
        {"status":"ok","data":{"intent","confidence","reason"}}
    """
    try:
        q = (query or "").lower()
        if not q.strip():
            return _ok({"intent": "unclear", "confidence": 0.0, "reason": "empty query"})

        # Off-topic short-circuits
        for term in ("weather", "joke", "stock price", "score of", "movie", "recipe"):
            if term in q:
                return _ok({"intent": "off_topic", "confidence": 0.9, "reason": f"contains '{term}'"})

        # Reliability — predictive future-tense
        for term in ("predict", "forecast", "risk", "rul", "next 30 days", "recommend", "should we schedule"):
            if term in q:
                return _ok({"intent": "reliability", "confidence": 0.85, "reason": f"contains '{term}'"})

        # Diagnostics — pattern across history
        for term in ("common issue", "most common", "frequent", "failure mode", "what fails", "patterns"):
            if term in q:
                return _ok({"intent": "diagnostics", "confidence": 0.85, "reason": f"contains '{term}'"})

        # Maintenance — past-tense history
        for term in ("last pm", "when was", "who worked", "work order", "wo-", "work package", "history"):
            if term in q:
                return _ok({"intent": "maintenance", "confidence": 0.8, "reason": f"contains '{term}'"})

        # Policy — procedure/rule lookup
        for term in ("policy", "allowance", "per-diem", "rwp", "loto", "lockout", "tagout",
                     "procedure", "max ", "limit on", "how often must"):
            if term in q:
                return _ok({"intent": "policy", "confidence": 0.8, "reason": f"contains '{term}'"})

        return _ok({"intent": "unclear", "confidence": 0.4, "reason": "no clear keyword match"})
    except Exception as e:  # noqa: BLE001
        return _err(f"classify_intent failed: {e}")


@tool
def delegate_to_policy(query: str) -> dict:
    """Forward the query to PolicyAgent (UC-1) and return its response verbatim."""
    return _delegate("policy", query)


@tool
def delegate_to_maintenance(query: str) -> dict:
    """Forward the query to MaintenanceAgent (UC-2) and return its response verbatim."""
    return _delegate("maintenance", query)


@tool
def delegate_to_diagnostics(query: str) -> dict:
    """Forward the query to DiagnosticsAgent (UC-3) and return its response verbatim."""
    return _delegate("diagnostics", query)


@tool
def delegate_to_reliability(query: str) -> dict:
    """Forward the query to ReliabilityAgent (UC-4) and return its response verbatim."""
    return _delegate("reliability", query)


# ---------------------------------------------------------------------------
# Multi-LLM support — payload may include `model_overrides` from Settings.
# The router has ONE configurable slot ("routing"). Specialists' overrides
# pass through unchanged via _CURRENT_MODEL_OVERRIDES (set in invoke() below).
# ---------------------------------------------------------------------------
AGENT_ID = "chatstp"
DEFAULT_ROUTING_MODEL = MODEL_ID

# Cache: one Agent per (routing_model_id) — building one is cheap, but
# re-use within a warm container saves a few microseconds per call.
_agent_cache: Dict[str, Agent] = {}


def _resolve_router_model(model_overrides: Dict[str, Dict[str, str]] | None) -> str:
    """Pick which BedrockModel id powers the router's classification + delegation."""
    overrides = (model_overrides or {}).get(AGENT_ID, {})
    return overrides.get("routing", DEFAULT_ROUTING_MODEL)


def _get_agent(routing_model_id: str) -> Agent:
    if routing_model_id in _agent_cache:
        return _agent_cache[routing_model_id]
    model = BedrockModel(model_id=routing_model_id, region_name=REGION)
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            classify_intent,
            delegate_to_policy,
            delegate_to_maintenance,
            delegate_to_diagnostics,
            delegate_to_reliability,
        ],
    )
    _agent_cache[routing_model_id] = agent
    return agent


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_message = payload.get("prompt", "Hello")
    overrides = payload.get("model_overrides") or {}
    # Stash for delegate_to_* tools to forward to specialists
    global _CURRENT_MODEL_OVERRIDES
    _CURRENT_MODEL_OVERRIDES = overrides
    routing_model = _resolve_router_model(overrides)
    try:
        result = _get_agent(routing_model)(user_message)
        return {
            "result": result.message,
            "model_used": {
                "agent": AGENT_ID,
                "routing_model": routing_model,
            },
        }
    finally:
        _CURRENT_MODEL_OVERRIDES = {}


if __name__ == "__main__":
    app.run()
