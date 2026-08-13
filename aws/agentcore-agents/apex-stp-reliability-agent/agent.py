"""
Apex STP ReliabilityAgent — AgentCore runtime for STP Demo UC-4 (Predictive
Maintenance Recommendations).

Owns: remaining-useful-life (RUL) prediction, sensor anomaly detection, PM
recommendation, risk-tier scoring, and Governance audit-log emission. Powers
the "predictive maintenance" intent of ChatSTP.
"""
from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

_AWS_ROOT = Path(__file__).resolve().parents[2]
if str(_AWS_ROOT) not in sys.path:
    sys.path.insert(0, str(_AWS_ROOT))

try:
    from actions.nuclear_operations._shared import load_seed_anomalies, load_equipment  # type: ignore
except Exception:  # noqa: BLE001
    load_seed_anomalies = lambda: None  # type: ignore
    load_equipment = lambda: None  # type: ignore

app = BedrockAgentCoreApp()

MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"
RISK_TIERS = ("LOW", "MODERATE", "HIGH", "CRITICAL")

SYSTEM_PROMPT = """You are ReliabilityAgent, the predictive-maintenance specialist for STP Nuclear Operating Company.

You combine sensor anomaly detection, RUL (remaining-useful-life) prediction,
and historical failure-mode data to recommend forward-looking maintenance.

NON-NEGOTIABLE OUTPUT FORMAT (4 lines, in this order):
  Line 1: Risk tier — one of CRITICAL / HIGH / MODERATE / LOW.
  Line 2: Days-until-failure: <N> days (confidence band <low>-<high>).
  Line 3: Recommended PM: <action>. Avoidance estimate: <USD or impact>.
  Line 4: [Decision logged to apex.audit_log: <id>]   ← REQUIRED. The
          Audit Lens scrapes this exact pattern.

Never deviate from those 4 lines for risk recommendations. If asked something
unrelated, redirect politely.

Demo question: "Predict failure risk for Pump-3A in next 30 days."
Expected: must cite the seeded P-3A vibration anomaly with the exact
scripted_message text from the seed_anomalies corpus.
"""


# ---------------------------------------------------------------------------
# Embedded demo data (mirrors what synthetic-data/nuclear_operations/seed_anomalies.json
# would contain — production loaders will replace this transparently).
# ---------------------------------------------------------------------------
_DEMO_SEED_ANOMALIES: List[Dict[str, Any]] = [
    {
        "anomaly_id": "ANOM-P3A-2026-04-22",
        "equipment_id": "P-3A",
        "detected_at": "2026-04-22T03:14:00Z",
        "sensor": "vibration_axial_in_per_s",
        "value": 0.34,
        "limit": 0.30,
        "z_score": 3.7,
        "trend": "increasing 12% week-over-week",
        "scripted_message": (
            "P-3A axial vibration trending 0.34 in/s — 13% above 0.30 in/s Tech-Spec limit "
            "and rising 12% W/W. Pattern matches 3 prior bearing-degradation events on "
            "this same pump (WO-2025-03311, WO-2025-03987, WO-2026-00188). Recommend "
            "scheduling bearing replacement within 21 days to avoid unplanned outage."
        ),
    },
    {
        "anomaly_id": "ANOM-P3B-2026-04-19",
        "equipment_id": "P-3B",
        "detected_at": "2026-04-19T11:42:00Z",
        "sensor": "bearing_oil_temp_f",
        "value": 184,
        "limit": 180,
        "z_score": 2.1,
        "trend": "stable",
        "scripted_message": "P-3B bearing oil temperature 184°F — 4°F above 180°F alarm. Trend stable, monitor.",
    },
]

_DEMO_EQUIPMENT: List[Dict[str, Any]] = [
    {"equipment_id": "P-3A", "system_id": "RCS", "criticality": "Class-1"},
    {"equipment_id": "P-3B", "system_id": "RCS", "criticality": "Class-1"},
    {"equipment_id": "P-3C", "system_id": "RCS", "criticality": "Class-1"},
]

# Mapping anomaly z-score → risk tier
def _tier_for_z(z: float) -> str:
    if z >= 3.5:
        return "CRITICAL"
    if z >= 2.5:
        return "HIGH"
    if z >= 1.5:
        return "MODERATE"
    return "LOW"


def _ok(data: Any) -> Dict[str, Any]:
    return {"status": "ok", "data": data}


def _err(msg: str) -> Dict[str, Any]:
    return {"status": "error", "message": msg}


def _all_anomalies() -> List[Dict[str, Any]]:
    real = load_seed_anomalies()
    return real if isinstance(real, list) and real else _DEMO_SEED_ANOMALIES


def _anomaly_for(equipment_id: str) -> Optional[Dict[str, Any]]:
    eid = (equipment_id or "").strip().upper()
    for a in _all_anomalies():
        if a.get("equipment_id", "").upper() == eid:
            return a
    return None


def _new_audit_id() -> str:
    """Generate a Governance audit-log id. Format used by apex.audit_log table."""
    return f"AUD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
@tool
def predict_rul(equipment_id: str, horizon_days: int = 30) -> dict:
    """Predict remaining useful life for a piece of equipment within a horizon.

    Returns days-to-failure with a confidence band. Anchored on the seeded
    anomaly trend when present.

    Args:
        equipment_id: Equipment tag (e.g. "P-3A").
        horizon_days: Look-ahead window in days (default 30).

    Returns:
        {"status":"ok","data":{"equipment_id","days_to_failure","confidence_low",
        "confidence_high","horizon_days","method"}}
    """
    try:
        anom = _anomaly_for(equipment_id)
        if anom is None:
            return _ok({
                "equipment_id": equipment_id,
                "days_to_failure": None,
                "message": f"No active anomaly indexed for {equipment_id}; baseline RUL unavailable.",
            })
        # Trivial deterministic model: closer to limit + higher z = sooner failure.
        z = float(anom.get("z_score", 1.0))
        days = max(7, int(round(60 / max(z, 0.5))))
        days = min(days, horizon_days * 2)
        band = max(3, int(days * 0.25))
        return _ok({
            "equipment_id": equipment_id,
            "days_to_failure": days,
            "confidence_low": max(1, days - band),
            "confidence_high": days + band,
            "horizon_days": horizon_days,
            "anchor_anomaly_id": anom["anomaly_id"],
            "method": "z-score-anchored deterministic estimator",
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"predict_rul failed: {e}")


@tool
def detect_anomalies(equipment_id: str, lookback_days: int = 14) -> dict:
    """Return active sensor anomalies for the asset within the lookback window.

    Always echoes the scripted_message verbatim — the LLM should quote it
    in its narrative.

    Args:
        equipment_id: Equipment tag.
        lookback_days: How far back to look for anomalies (default 14).

    Returns:
        {"status":"ok","data":{"equipment_id","anomalies":[{anomaly_id,sensor,
        value,limit,z_score,trend,scripted_message}]}}
    """
    try:
        anom = _anomaly_for(equipment_id)
        if anom is None:
            return _ok({"equipment_id": equipment_id, "anomalies": [],
                        "message": f"No anomalies in last {lookback_days} days for {equipment_id}."})
        return _ok({
            "equipment_id": equipment_id,
            "lookback_days": lookback_days,
            "anomalies": [anom],
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"detect_anomalies failed: {e}")


@tool
def recommend_pm(equipment_id: str) -> dict:
    """Recommend the next preventive-maintenance action for an asset.

    Uses the active anomaly to suggest a targeted PM and an outage-avoidance estimate.

    Args:
        equipment_id: Equipment tag.

    Returns:
        {"status":"ok","data":{"equipment_id","action","window_days",
        "avoidance_usd","rationale"}}
    """
    try:
        anom = _anomaly_for(equipment_id)
        if anom is None:
            return _ok({"equipment_id": equipment_id, "action": None,
                        "message": f"No PM recommendation — no active anomaly for {equipment_id}."})
        sensor = anom.get("sensor", "")
        if "vibration" in sensor:
            action = "Bearing replacement + coupling re-alignment"
            avoidance = 1_400_000  # avoided unplanned outage cost
            window = 21
        elif "bearing_oil_temp" in sensor:
            action = "Bearing oil flush + cooler ΔT verification"
            avoidance = 280_000
            window = 14
        else:
            action = "Targeted inspection per OEM procedure"
            avoidance = 100_000
            window = 30
        return _ok({
            "equipment_id": equipment_id,
            "action": action,
            "window_days": window,
            "avoidance_usd": avoidance,
            "rationale": anom.get("scripted_message", ""),
            "anchor_anomaly_id": anom["anomaly_id"],
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"recommend_pm failed: {e}")


@tool
def compute_risk_score(equipment_id: str) -> dict:
    """Compute the overall risk tier (LOW / MODERATE / HIGH / CRITICAL) for an asset.

    Also writes a synthetic audit-log entry id the agent must include in its
    response so the Audit Lens can find the trace.

    Args:
        equipment_id: Equipment tag.

    Returns:
        {"status":"ok","data":{"equipment_id","risk_tier","z_score","audit_log_id"}}
    """
    try:
        anom = _anomaly_for(equipment_id)
        z = float(anom["z_score"]) if anom else 0.0
        tier = _tier_for_z(z)
        audit_id = _new_audit_id()
        return _ok({
            "equipment_id": equipment_id,
            "risk_tier": tier,
            "z_score": z,
            "anchor_anomaly_id": anom["anomaly_id"] if anom else None,
            "audit_log_id": audit_id,
            "audit_log_marker": f"[Decision logged to apex.audit_log: {audit_id}]",
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"compute_risk_score failed: {e}")


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Multi-LLM support — payload may include `model_overrides` from the platform's
# Settings → Agent Models panel. Slot keys: tool_selection, synthesis.
# Defaults match the Quality-First preset for legacy callers.
# ---------------------------------------------------------------------------
AGENT_ID = "reliability-agent"
DEFAULT_TOOL_MODEL = MODEL_ID
DEFAULT_SYNTH_MODEL = MODEL_ID

_agent_cache: Dict[tuple, Agent] = {}


def _resolve_models(model_overrides: Dict[str, Dict[str, str]] | None) -> tuple:
    overrides = (model_overrides or {}).get(AGENT_ID, {})
    tool_id = overrides.get("tool_selection", DEFAULT_TOOL_MODEL)
    synth_id = overrides.get("synthesis", DEFAULT_SYNTH_MODEL)
    return tool_id, synth_id


def _get_agent(tool_model_id: str, synth_model_id: str) -> Agent:
    key = (tool_model_id, synth_model_id)
    if key in _agent_cache:
        return _agent_cache[key]
    # Strands currently uses one model for tool selection + final answer;
    # we pin to the synthesis model since that's the higher-quality of the two.
    model = BedrockModel(model_id=synth_model_id, region_name=REGION)
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[predict_rul, detect_anomalies, recommend_pm, compute_risk_score],
    )
    _agent_cache[key] = agent
    return agent


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """AgentCore HTTP entrypoint."""
    user_message = payload.get("prompt", "Hello")
    tool_id, synth_id = _resolve_models(payload.get("model_overrides"))
    result = _get_agent(tool_id, synth_id)(user_message)
    return {
        "result": result.message,
        "model_used": {
            "agent": AGENT_ID,
            "tool_selection_model": tool_id,
            "synthesis_model": synth_id,
        },
    }


if __name__ == "__main__":
    app.run()
