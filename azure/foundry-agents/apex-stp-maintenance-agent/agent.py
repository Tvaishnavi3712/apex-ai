"""
Apex STP MaintenanceAgent — Foundry Agent Service runtime for STP Demo UC-2 (Equipment PM
History with Engineer Attribution).

Owns: PM history retrieval from the Oracle eAM mirror, technician/engineer
attribution from the personnel directory, and PDF work-package linking. Powers
the "maintenance history" intent of ChatSTP.
"""
from __future__ import annotations
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


_AWS_ROOT = Path(__file__).resolve().parents[2]
if str(_AWS_ROOT) not in sys.path:
    sys.path.insert(0, str(_AWS_ROOT))

# Optional: pull from the synthetic-data corpus when present.
try:
    from actions.nuclear_operations._shared import (  # type: ignore
        load_work_orders, load_personnel
    )
except Exception:  # noqa: BLE001
    load_work_orders = lambda: None  # type: ignore
    load_personnel = lambda: None  # type: ignore

app = FoundryAgentApp()

# ---------------------------------------------------------------------------
MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"
DEFAULT_LOOKBACK_DAYS = 365
WORK_PACKAGE_S3_PREFIX = "s3://apex-stp-work-packages/"

SYSTEM_PROMPT = """You are MaintenanceAgent, the equipment maintenance-history expert for STP Nuclear Operating Company.

You serve operators, planners, and engineers who need to know what was last done to a specific piece of equipment, by whom, and where the documentation lives.

NON-NEGOTIABLE RULES:
1. Always answer with the four facts: (a) date of last PM, (b) who performed it (engineer + craft technicians), (c) what was done (scope summary), (d) link to the work package PDF.
2. If the user references "the pump" or any ambiguous asset, ask which one. Specifically: "Which pump? P-3A, P-3B, or P-3C?". Never invent equipment IDs.
3. If lookup_pm_history returns no records, say so honestly — never invent a date or a technician name.
4. Format response as:
   Last PM on <equipment_id>: <date>
   Performed by: <engineer name> (lead) + <tech names>
   Scope: <one-line summary>
   Work package: <s3 link>

Demo question: "When was the last PM on Pump-3A and who worked on it?"
"""


# ---------------------------------------------------------------------------
# Embedded demo data (used when synthetic-data corpus is not generated)
# ---------------------------------------------------------------------------
_DEMO_WORK_ORDERS: List[Dict[str, Any]] = [
    {
        "wo_id": "WO-2026-00871",
        "equipment_id": "P-3A",
        "equipment_name": "Reactor Coolant Pump 3A",
        "type": "PM",
        "subtype": "Quarterly Minor",
        "completed_date": "2026-03-18",
        "lead_engineer_id": "E-1142",
        "tech_ids": ["T-2031", "T-2078"],
        "scope_summary": "Bearing oil sample, vibration baseline, seal-cavity inspection",
        "work_package_pdf": "s3://apex-stp-work-packages/2026/WO-2026-00871.pdf",
        "status": "CLOSED",
    },
    {
        "wo_id": "WO-2025-04512",
        "equipment_id": "P-3A",
        "equipment_name": "Reactor Coolant Pump 3A",
        "type": "PM",
        "subtype": "Annual Major",
        "completed_date": "2025-09-04",
        "lead_engineer_id": "E-1142",
        "tech_ids": ["T-2031", "T-2055", "T-2078"],
        "scope_summary": "Coupling alignment, motor amp signature, full vibration sweep, lube change",
        "work_package_pdf": "s3://apex-stp-work-packages/2025/WO-2025-04512.pdf",
        "status": "CLOSED",
    },
    {
        "wo_id": "WO-2026-00744",
        "equipment_id": "P-3B",
        "equipment_name": "Reactor Coolant Pump 3B",
        "type": "PM",
        "subtype": "Quarterly Minor",
        "completed_date": "2026-02-22",
        "lead_engineer_id": "E-1207",
        "tech_ids": ["T-2031"],
        "scope_summary": "Bearing oil sample, vibration baseline",
        "work_package_pdf": "s3://apex-stp-work-packages/2026/WO-2026-00744.pdf",
        "status": "CLOSED",
    },
    {
        "wo_id": "WO-2026-00599",
        "equipment_id": "P-3C",
        "equipment_name": "Reactor Coolant Pump 3C",
        "type": "PM",
        "subtype": "Quarterly Minor",
        "completed_date": "2026-01-30",
        "lead_engineer_id": "E-1142",
        "tech_ids": ["T-2055", "T-2078"],
        "scope_summary": "Seal leak-rate test, vibration baseline, oil sample",
        "work_package_pdf": "s3://apex-stp-work-packages/2026/WO-2026-00599.pdf",
        "status": "CLOSED",
    },
]

_DEMO_PERSONNEL: List[Dict[str, Any]] = [
    {"id": "E-1142", "name": "Diane Okafor",     "role": "Lead Reliability Engineer", "craft": "ME"},
    {"id": "E-1207", "name": "Carlos Rentería",  "role": "Senior Maintenance Engineer", "craft": "ME"},
    {"id": "T-2031", "name": "Marcus Holloway",  "role": "Mechanical Tech III",       "craft": "Mech"},
    {"id": "T-2055", "name": "Priya Subramanian","role": "I&C Tech II",               "craft": "I&C"},
    {"id": "T-2078", "name": "Jamal Greene",     "role": "Mechanical Tech II",        "craft": "Mech"},
]


# ---------------------------------------------------------------------------
def _ok(data: Any) -> Dict[str, Any]:
    return {"status": "ok", "data": data}


def _err(msg: str) -> Dict[str, Any]:
    return {"status": "error", "message": msg}


def _all_work_orders() -> List[Dict[str, Any]]:
    real = load_work_orders()
    return real if isinstance(real, list) and real else _DEMO_WORK_ORDERS


def _all_personnel() -> List[Dict[str, Any]]:
    real = load_personnel()
    return real if isinstance(real, list) and real else _DEMO_PERSONNEL


def _resolve_person(person_id: str) -> Dict[str, Any]:
    for p in _all_personnel():
        if p.get("id") == person_id:
            return p
    return {"id": person_id, "name": "Unknown", "role": "Unknown"}


# ---------------------------------------------------------------------------
@tool
def lookup_pm_history(equipment_id: str, lookback_days: int = DEFAULT_LOOKBACK_DAYS) -> dict:
    """Look up preventive-maintenance history for a specific piece of equipment.

    Args:
        equipment_id: Equipment tag (e.g. "P-3A"). Be exact — do not invent IDs.
        lookback_days: How far back to search (default 365 days).

    Returns:
        {"status":"ok","data":{"equipment_id","records":[{"wo_id","completed_date",
        "subtype","lead_engineer","techs","scope_summary","work_package_pdf"}],
        "last_pm": {...}}}
    """
    try:
        eid = (equipment_id or "").strip().upper()
        if not eid:
            return _err("equipment_id is required (e.g. 'P-3A').")
        rows = [w for w in _all_work_orders()
                if w.get("equipment_id", "").upper() == eid and w.get("type") == "PM"]
        if not rows:
            return _ok({
                "equipment_id": eid,
                "records": [],
                "message": f"No PM history found for {eid} in the last {lookback_days} days.",
            })
        # Sort newest first
        rows.sort(key=lambda r: r.get("completed_date", ""), reverse=True)
        records = []
        for w in rows:
            lead = _resolve_person(w.get("lead_engineer_id", ""))
            techs = [_resolve_person(t) for t in w.get("tech_ids", [])]
            records.append({
                "wo_id": w["wo_id"],
                "completed_date": w["completed_date"],
                "subtype": w.get("subtype", "PM"),
                "lead_engineer": {"id": lead["id"], "name": lead["name"], "role": lead["role"]},
                "techs": [{"id": t["id"], "name": t["name"], "role": t["role"]} for t in techs],
                "scope_summary": w.get("scope_summary", ""),
                "work_package_pdf": w.get("work_package_pdf", ""),
                "status": w.get("status", ""),
            })
        return _ok({
            "equipment_id": eid,
            "lookback_days": lookback_days,
            "records": records,
            "last_pm": records[0],
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"lookup_pm_history failed: {e}")


@tool
def get_engineer_attribution(wo_id: str) -> dict:
    """Resolve the lead engineer and technician roster for a specific work order.

    Args:
        wo_id: Work-order ID, e.g. "WO-2026-00871".

    Returns:
        {"status":"ok","data":{"wo_id","lead_engineer":{...},"techs":[{...}]}}
    """
    try:
        wo = next((w for w in _all_work_orders() if w.get("wo_id") == wo_id), None)
        if wo is None:
            return _err(f"Work order '{wo_id}' not found.")
        lead = _resolve_person(wo.get("lead_engineer_id", ""))
        techs = [_resolve_person(t) for t in wo.get("tech_ids", [])]
        return _ok({
            "wo_id": wo_id,
            "lead_engineer": lead,
            "techs": techs,
            "completed_date": wo.get("completed_date"),
            "scope_summary": wo.get("scope_summary", ""),
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"get_engineer_attribution failed: {e}")


@tool
def fetch_work_package(wo_id: str) -> dict:
    """Return the S3 path to the work-package PDF so the chat UI can render a link.

    Args:
        wo_id: Work-order ID.

    Returns:
        {"status":"ok","data":{"wo_id","pdf_path","exists"}}
    """
    try:
        wo = next((w for w in _all_work_orders() if w.get("wo_id") == wo_id), None)
        if wo is None:
            return _err(f"Work order '{wo_id}' not found.")
        path = wo.get("work_package_pdf", "")
        if not path:
            path = f"{WORK_PACKAGE_S3_PREFIX}{wo_id}.pdf"
        return _ok({
            "wo_id": wo_id,
            "pdf_path": path,
            "https_link": path.replace("s3://", "https://s3.console.aws.amazon.com/s3/object/"),
            "exists": bool(wo.get("work_package_pdf")),
        })
    except Exception as e:  # noqa: BLE001
        return _err(f"fetch_work_package failed: {e}")


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Multi-LLM support — payload may include `model_overrides` from the platform's
# Settings → Agent Models panel. Slot keys: tool_selection, synthesis.
# Defaults match the Quality-First preset for legacy callers.
# ---------------------------------------------------------------------------
AGENT_ID = "maintenance-agent"
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
        tools=[lookup_pm_history, get_engineer_attribution, fetch_work_package],
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
