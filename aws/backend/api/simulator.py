"""
Simulator API — Killer Feature 4 (What-If Simulator).

Scenarios live in DynamoDB (`apex-ai-platform-simulator-scenarios`). Running a
scenario invokes the real Logistics AgentCore runtime with a structured prompt
that includes the scenario context; we return the AgentCore reasoning + final
text as-is — no synthesised animation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.agentcore import AgentCoreService
from services.dynamodb import DynamoDBService
from core.config import settings

router = APIRouter()
scenarios_db = DynamoDBService(settings.DYNAMODB_SIMULATOR_SCENARIOS)
agentcore = AgentCoreService()


class Exposure(BaseModel):
    plant: str
    units: int = 0
    usd:   float = 0.0


class RerouteOption(BaseModel):
    rank:            str                             # 'A' | 'B' | 'C'
    tier:            str                             # PREFERRED | FALLBACK | LAST_RESORT
    supplier:        str
    cost_delta_pct:  float
    delay_days:      int
    capacity:        str                             # SUFFICIENT | PARTIAL | LIMITED
    notes:           str


class Scenario(BaseModel):
    scenario_id:     str
    label:           str
    tagline:         str
    severity:        str                             # HIGH | MEDIUM | CRITICAL
    region:          str
    material:        str
    delay_days:      int
    exposures:       List[Exposure]                  = Field(default_factory=list)
    options:         List[RerouteOption]             = Field(default_factory=list)
    director:        str
    agent_id:        str  = "logisticsbot"           # routes to Logistics AgentCore runtime


class ReasoningStep(BaseModel):
    step:     int
    kind:     str                                    # thought | action | observation | answer
    text:     str
    action:   Optional[str] = None


class RunResponse(BaseModel):
    scenario_id:       str
    status:            str                           # "complete" | "agentcore_offline"
    reasoning:         List[ReasoningStep]           = Field(default_factory=list)
    actions_taken:     List[str]                     = Field(default_factory=list)
    final_answer:      str                           = ""
    latency_ms:        int                           = 0
    agent_id:          str                           = "logisticsbot"


@router.get("/scenarios", response_model=List[Scenario])
async def list_scenarios():
    """Return all scenarios ready for injection."""
    rows = await scenarios_db.scan(limit=100)
    # Sort: seeded scenarios first (stable), user-created last (newest first).
    SEED_IDS = {"port-strike-savannah", "aluminum-tariff-30", "supplier-bankruptcy", "cyber-ransomware-vendor"}
    seeded = [r for r in rows if r.get("scenario_id") in SEED_IDS]
    custom = sorted(
        [r for r in rows if r.get("scenario_id") not in SEED_IDS],
        key=lambda r: r.get("created_at", ""),
        reverse=True,
    )
    return [Scenario(**r) for r in seeded + custom]


@router.get("/scenarios/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    row = await scenarios_db.get_item({"scenario_id": scenario_id})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario {scenario_id} not found")
    return Scenario(**row)


import re as _re
import uuid as _uuid
from decimal import Decimal


def _to_ddb(value: Any) -> Any:
    """Walk a dict/list tree and convert floats to Decimal — DynamoDB rejects float."""
    if isinstance(value, float):
        return Decimal(str(round(value, 4)))
    if isinstance(value, dict):
        return {k: _to_ddb(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_ddb(v) for v in value]
    return value


class ScenarioInput(BaseModel):
    """Payload for creating a new scenario. `scenario_id` is optional — the
    server derives one from `label` if not provided."""
    scenario_id:   Optional[str] = None
    label:         str
    tagline:       str = ""
    severity:      str = "HIGH"
    region:        str = "Global"
    material:      str = ""
    delay_days:    int = 0
    exposures:     List[Exposure] = Field(default_factory=list)
    options:       List[RerouteOption] = Field(default_factory=list)
    director:      str = ""
    agent_id:      str = "logisticsbot"


SEED_IDS = {"port-strike-savannah", "aluminum-tariff-30", "supplier-bankruptcy", "cyber-ransomware-vendor"}


def _slug(s: str) -> str:
    s = _re.sub(r"[^A-Za-z0-9-]+", "-", s.strip().lower())
    s = _re.sub(r"-+", "-", s).strip("-")
    return s or "scenario"


@router.post("/scenarios", response_model=Scenario, status_code=status.HTTP_201_CREATED)
async def create_scenario(payload: ScenarioInput):
    """Inject a new crisis scenario. Persists to DynamoDB so it survives
    restarts and is visible to anyone hitting the Simulator page."""
    sid = payload.scenario_id or f"{_slug(payload.label)}-{_uuid.uuid4().hex[:6]}"
    # Don't let a client clobber a seeded scenario by reusing its id.
    if sid in SEED_IDS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"'{sid}' is a reserved seed scenario id")
    row = Scenario(
        scenario_id=sid,
        label=payload.label,
        tagline=payload.tagline,
        severity=payload.severity,
        region=payload.region,
        material=payload.material,
        delay_days=payload.delay_days,
        exposures=payload.exposures,
        options=payload.options,
        director=payload.director,
        agent_id=payload.agent_id,
    ).model_dump()
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    row["origin"]     = "user-injected"
    await scenarios_db.put_item(_to_ddb(row))
    return Scenario(**row)


@router.put("/scenarios/{scenario_id}", response_model=Scenario)
async def update_scenario(scenario_id: str, payload: ScenarioInput):
    """Update an existing scenario in place."""
    if scenario_id in SEED_IDS and payload.scenario_id and payload.scenario_id != scenario_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot rename a seeded scenario id")
    existing = await scenarios_db.get_item({"scenario_id": scenario_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario {scenario_id} not found")
    merged = {
        **existing,
        "scenario_id": scenario_id,
        "label":       payload.label,
        "tagline":     payload.tagline,
        "severity":    payload.severity,
        "region":      payload.region,
        "material":    payload.material,
        "delay_days":  payload.delay_days,
        "exposures":   [e.model_dump() for e in payload.exposures],
        "options":     [o.model_dump() for o in payload.options],
        "director":    payload.director,
        "agent_id":    payload.agent_id,
        "updated_at":  datetime.now(timezone.utc).isoformat(),
    }
    await scenarios_db.put_item(_to_ddb(merged))
    return Scenario(**merged)


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str):
    """Remove a scenario. Seeded demo scenarios are protected; re-seed with
    `backend/scripts/seed_killer_features.py` if you want them back."""
    if scenario_id in SEED_IDS:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"'{scenario_id}' is a seeded scenario — not deletable via API")
    existing = await scenarios_db.get_item({"scenario_id": scenario_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario {scenario_id} not found")
    await scenarios_db.delete_item({"scenario_id": scenario_id})
    return {"deleted": scenario_id}


@router.post("/run/{scenario_id}", response_model=RunResponse)
async def run_scenario(scenario_id: str):
    """Inject the scenario into the Logistics AgentCore runtime and return its
    real reasoning trace + final mitigation summary.
    """
    row = await scenarios_db.get_item({"scenario_id": scenario_id})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Scenario {scenario_id} not found")
    scenario = Scenario(**row)

    # Build a structured prompt from the scenario so the agent has full context.
    total_var = sum(e.usd for e in scenario.exposures)
    exposure_lines = "\n".join(
        f"  • {e.plant}: {e.units:,} units, ${e.usd:,.0f} at risk" for e in scenario.exposures
    )
    prompt = (
        f"CRISIS SIMULATION — run the disruption playbook end-to-end and show your work.\n\n"
        f"Event: {scenario.label} (severity {scenario.severity})\n"
        f"Region: {scenario.region}\n"
        f"Material: {scenario.material}\n"
        f"Expected delay: {scenario.delay_days} days\n\n"
        f"Known exposure:\n{exposure_lines}\n"
        f"Total value at risk: ${total_var:,.0f}\n\n"
        f"Task: (1) traverse the BOM to confirm affected plants, (2) project total financial impact, "
        f"(3) generate 3 ranked reroute options (PREFERRED/FALLBACK/LAST_RESORT), "
        f"(4) decide whether to auto-dispatch or escalate to the Director, "
        f"(5) compose a crisp summary for {scenario.director}."
    )

    started = datetime.now(timezone.utc)
    result = await agentcore.invoke_agent(scenario.agent_id, prompt)
    latency_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    if not result.get("success"):
        return RunResponse(
            scenario_id=scenario_id,
            status="agentcore_offline",
            final_answer=result.get("response") or "AgentCore runtime unreachable.",
            agent_id=scenario.agent_id,
            latency_ms=latency_ms,
        )

    steps_raw = result.get("reasoning", []) or []
    steps = [
        ReasoningStep(
            step=s.get("step", i + 1),
            kind=s.get("kind", "thought"),
            text=s.get("text", ""),
            action=s.get("action"),
        )
        for i, s in enumerate(steps_raw)
    ]

    return RunResponse(
        scenario_id=scenario_id,
        status="complete",
        reasoning=steps,
        actions_taken=result.get("actions_taken", []) or [],
        final_answer=result.get("response", ""),
        latency_ms=latency_ms,
        agent_id=scenario.agent_id,
    )
