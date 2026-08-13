"""
Apex STP DiagnosticsAgent — Foundry Agent Service runtime for STP Demo UC-3 (Common-Issue
Analysis across the work-package corpus for an asset or system).

Owns: full-text WO search, failure-mode aggregation, frequency ranking, lead-time
estimation, mitigation recommendations. Powers the "issue analysis" intent of
ChatSTP.
"""
from __future__ import annotations
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional


_AWS_ROOT = Path(__file__).resolve().parents[2]
if str(_AWS_ROOT) not in sys.path:
    sys.path.insert(0, str(_AWS_ROOT))

try:
    from actions.nuclear_operations._shared import (  # type: ignore
        load_failure_events, load_failure_mode_catalog
    )
except Exception:  # noqa: BLE001
    load_failure_events = lambda: None  # type: ignore
    load_failure_mode_catalog = lambda: None  # type: ignore

app = FoundryAgentApp()

MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"
MIN_EVIDENCE_WO_COUNT = 3
TOP_FAILURE_MODES = 5

SYSTEM_PROMPT = """You are DiagnosticsAgent, the failure-mode analyst for STP Nuclear Operating Company.

You answer "what are the common issues with X?" by aggregating across the
historical work-package corpus for a specific equipment tag or system.

NON-NEGOTIABLE RULES:
1. Always rank failure modes by frequency, with the count and percentage of total events.
2. Cite at least 3 specific WO IDs as evidence per failure mode.
3. Format response as:
   Top issues for <equipment>:
   1. <failure_mode> (X% of N events) — typical lead time <N> days, mitigation: <text>.
      Cited from: WO-..., WO-..., WO-...
   2. ...
4. If the corpus has no failure history for the asset, say "No failure history indexed for this asset." NEVER invent failure modes.
5. Stay terse and operational — engineers will skim this.

Demo question: "What are the most common issues with Pump-3A?"
"""


# ---------------------------------------------------------------------------
# Embedded demo failure event corpus
# ---------------------------------------------------------------------------
_DEMO_FAILURE_EVENTS: List[Dict[str, Any]] = [
    # P-3A — vibration spikes (most common)
    {"wo_id": "WO-2025-03311", "equipment_id": "P-3A", "failure_mode": "Vibration above limit (axial)",     "detected_date": "2025-04-12", "lead_time_days": 6,  "system_id": "RCS"},
    {"wo_id": "WO-2025-03987", "equipment_id": "P-3A", "failure_mode": "Vibration above limit (axial)",     "detected_date": "2025-08-22", "lead_time_days": 5,  "system_id": "RCS"},
    {"wo_id": "WO-2026-00188", "equipment_id": "P-3A", "failure_mode": "Vibration above limit (axial)",     "detected_date": "2026-02-14", "lead_time_days": 4,  "system_id": "RCS"},
    # P-3A — seal-cavity leaks
    {"wo_id": "WO-2025-02201", "equipment_id": "P-3A", "failure_mode": "Mechanical seal cavity leak",       "detected_date": "2025-02-18", "lead_time_days": 9,  "system_id": "RCS"},
    {"wo_id": "WO-2025-04102", "equipment_id": "P-3A", "failure_mode": "Mechanical seal cavity leak",       "detected_date": "2025-09-30", "lead_time_days": 11, "system_id": "RCS"},
    # P-3A — bearing temp
    {"wo_id": "WO-2025-03050", "equipment_id": "P-3A", "failure_mode": "Bearing oil over-temperature",      "detected_date": "2025-03-09", "lead_time_days": 3,  "system_id": "RCS"},
    {"wo_id": "WO-2026-00045", "equipment_id": "P-3A", "failure_mode": "Bearing oil over-temperature",      "detected_date": "2026-01-04", "lead_time_days": 2,  "system_id": "RCS"},
    # P-3A — coupling alignment
    {"wo_id": "WO-2025-04501", "equipment_id": "P-3A", "failure_mode": "Coupling misalignment",             "detected_date": "2025-09-02", "lead_time_days": 7,  "system_id": "RCS"},
    # P-3A — motor amp drift
    {"wo_id": "WO-2026-00321", "equipment_id": "P-3A", "failure_mode": "Motor amp signature drift",         "detected_date": "2026-02-25", "lead_time_days": 10, "system_id": "RCS"},

    # P-3B
    {"wo_id": "WO-2025-03801", "equipment_id": "P-3B", "failure_mode": "Vibration above limit (axial)",     "detected_date": "2025-07-04", "lead_time_days": 5,  "system_id": "RCS"},
    {"wo_id": "WO-2025-04711", "equipment_id": "P-3B", "failure_mode": "Mechanical seal cavity leak",       "detected_date": "2025-10-22", "lead_time_days": 8,  "system_id": "RCS"},

    # P-3C
    {"wo_id": "WO-2025-04812", "equipment_id": "P-3C", "failure_mode": "Bearing oil over-temperature",      "detected_date": "2025-11-15", "lead_time_days": 3,  "system_id": "RCS"},
]

_DEMO_MODE_CATALOG: List[Dict[str, Any]] = [
    {"failure_mode": "Vibration above limit (axial)",  "mitigation": "Re-baseline coupling alignment; replace bearings if pattern persists."},
    {"failure_mode": "Mechanical seal cavity leak",    "mitigation": "Pressure-test seal cavity; replace mechanical seal kit; inspect shaft sleeve."},
    {"failure_mode": "Bearing oil over-temperature",   "mitigation": "Sample oil for water/iron; flush and refill with spec lubricant; verify cooler ΔT."},
    {"failure_mode": "Coupling misalignment",          "mitigation": "Laser-align coupling; verify thermal-growth offsets per OEM spec."},
    {"failure_mode": "Motor amp signature drift",      "mitigation": "Run motor current-signature analysis; inspect rotor bars and stator winding."},
]


def _ok(data: Any) -> Dict[str, Any]:
    return {"status": "ok", "data": data}


def _err(msg: str) -> Dict[str, Any]:
    return {"status": "error", "message": msg}


def _all_events() -> List[Dict[str, Any]]:
    real = load_failure_events()
    return real if isinstance(real, list) and real else _DEMO_FAILURE_EVENTS


def _all_modes() -> List[Dict[str, Any]]:
    real = load_failure_mode_catalog()
    return real if isinstance(real, list) and real else _DEMO_MODE_CATALOG


def _mitigation_for(mode: str) -> str:
    for m in _all_modes():
        if m.get("failure_mode") == mode:
            return m.get("mitigation", "")
    return ""


# ---------------------------------------------------------------------------
@tool
def search_work_packages(equipment_id: str, optional_topic: str = "") -> dict:
    """Search the work-package corpus for a specific asset, optionally filtered by topic.

    Args:
        equipment_id: Equipment tag (e.g. "P-3A").
        optional_topic: Free-text filter (e.g. "vibration"). Empty for all.

    Returns:
        {"status":"ok","data":{"equipment_id","total","results":[{"wo_id",
        "failure_mode","detected_date","lead_time_days"}]}}
    """
    try:
        eid = (equipment_id or "").strip().upper()
        if not eid:
            return _err("equipment_id is required.")
        rows = [e for e in _all_events() if e.get("equipment_id", "").upper() == eid]
        if optional_topic:
            t = optional_topic.lower()
            rows = [r for r in rows if t in r.get("failure_mode", "").lower()]
        rows.sort(key=lambda r: r.get("detected_date", ""), reverse=True)
        return _ok({
            "equipment_id": eid,
            "topic_filter": optional_topic or None,
            "total": len(rows),
            "results": rows,
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"search_work_packages failed: {e}")


@tool
def aggregate_failure_modes(
    equipment_ids: Optional[List[str]] = None,
    system_id: Optional[str] = None,
) -> dict:
    """Aggregate failure modes across one or more equipment tags or an entire system.

    Returns top failure modes ranked by frequency, with average lead time and
    at least 3 cited WO IDs as evidence per mode. Empty if no events match.

    Args:
        equipment_ids: List of equipment tags. Pass None to include all.
        system_id: Optional system filter (e.g. "RCS"). Combined with equipment_ids.

    Returns:
        {"status":"ok","data":{"scope","total_events","top_modes":[{"failure_mode",
        "count","pct","avg_lead_time_days","evidence_wo_ids","mitigation"}]}}
    """
    try:
        events = _all_events()
        if equipment_ids:
            ids_up = {(e or "").strip().upper() for e in equipment_ids}
            events = [e for e in events if e.get("equipment_id", "").upper() in ids_up]
        if system_id:
            events = [e for e in events if e.get("system_id", "").upper() == system_id.upper()]
        total = len(events)
        if total == 0:
            return _ok({
                "scope": {"equipment_ids": equipment_ids, "system_id": system_id},
                "total_events": 0,
                "top_modes": [],
                "message": "No failure history indexed for this scope.",
            })
        counts = Counter(e["failure_mode"] for e in events)
        top: List[Dict[str, Any]] = []
        for mode, count in counts.most_common(TOP_FAILURE_MODES):
            mode_events = [e for e in events if e["failure_mode"] == mode]
            avg_lead = round(
                sum(int(e.get("lead_time_days", 0)) for e in mode_events) / max(1, len(mode_events)),
                1,
            )
            evidence = [e["wo_id"] for e in mode_events][:max(MIN_EVIDENCE_WO_COUNT, 3)]
            top.append({
                "failure_mode": mode,
                "count": count,
                "pct": round(count / total * 100.0, 1),
                "avg_lead_time_days": avg_lead,
                "evidence_wo_ids": evidence,
                "mitigation": _mitigation_for(mode),
            })
        return _ok({
            "scope": {"equipment_ids": equipment_ids, "system_id": system_id},
            "total_events": total,
            "top_modes": top,
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"aggregate_failure_modes failed: {e}")


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Multi-LLM support — payload may include `model_overrides` from the platform's
# Settings → Agent Models panel. Slot keys: tool_selection, synthesis.
# Defaults match the Quality-First preset for legacy callers.
# ---------------------------------------------------------------------------
AGENT_ID = "diagnostics-agent"
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
    model = AzureOpenAIModel(model_id=synth_model_id, region_name=REGION)
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[search_work_packages, aggregate_failure_modes],
    )
    _agent_cache[key] = agent
    return agent


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Foundry Agent Service HTTP entrypoint."""
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
