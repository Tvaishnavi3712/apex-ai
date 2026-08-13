"""
ApexSignal — Proactive Supply Chain Intelligence (Killer Feature 6).

Per ApexSignal_ClaudeCode_Spec.docx §3 + Apex_Master_Implementation_Spec.docx §4.

Endpoints:
  GET  /api/v1/signals/risks                       — Risk Radar tab
  GET  /api/v1/signals/demand                      — Demand Sensing tab (DeepAR forecast)
  GET  /api/v1/signals/stockout                    — Stockout Forecast tab (Linear Learner)
  GET  /api/v1/signals/suppliers                   — Supplier Health tab (XGBoost multi-class)
  POST /api/v1/signals/risks/{event_id}/playbook   — invoke Logistics AgentCore → mitigation plan
  GET  /api/v1/signals/endpoints/status            — SageMaker endpoint statuses (for UI status badge)

Data flow:
  • /risks         reads DynamoDB `predictive-events`, scored against SageMaker
                   lead-time endpoint for probability refresh.
  • /demand        reads DynamoDB `purchase-orders` + historical weeks derived
                   from purchase orders, invokes DeepAR for the forecast.
  • /stockout      reads `inventory-bom` + regional demand aggregate, invokes
                   Linear Learner stockout endpoint per material.
  • /suppliers     reads `suppliers`, invokes XGBoost supplier endpoint on each
                   supplier's most-recent QC reading.
  • /playbook      invokes AgentCoreService.invoke_agent('logisticsbot', …)
                   with scenario context — same pattern as simulator.py.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.dynamodb import DynamoDBService
from services.sagemaker import SageMakerService
from services.agentcore import AgentCoreService
from core.config import settings

router = APIRouter()

_events_db     = DynamoDBService(settings.DYNAMODB_PREDICTIVE_EVENTS)
_suppliers_db  = DynamoDBService(settings.DYNAMODB_SUPPLIERS)
_inv_bom_db    = DynamoDBService(settings.DYNAMODB_INVENTORY_BOM)
_po_db         = DynamoDBService(settings.DYNAMODB_PURCHASE_ORDERS)
_audit_db      = DynamoDBService(settings.DYNAMODB_AGENT_AUDIT_LOG)

_sagemaker = SageMakerService()
_agentcore = AgentCoreService()

# ═════════════════════ Pydantic response models ═════════════════════

class Risk(BaseModel):
    id: str
    type: str
    severity: str
    probability_pct: int
    title: str
    description: str = ""
    affected_material_id: Optional[str] = None
    affected_supplier_id: Optional[str] = None
    affected_plants: List[str] = Field(default_factory=list)
    financial_exposure_usd: float
    days_until_impact: int
    agent_playbook_ready: bool = True


class RiskRadar(BaseModel):
    kpi_active_risks: int
    kpi_exposure_30d_usd: float
    kpi_protected_ytd_usd: float
    kpi_agent_runs_today: int
    # Cumulative count of autonomous agent runs that avoided financial loss
    # (= rows in agent_audit_log with a positive cost_avoided_usd). Used by
    # the Dashboard "Disruptions Prevented" KPI — a today-only counter reads
    # as "0" on a quiet day, which contradicts the YTD $ protected figure
    # shown right below it.
    kpi_disruptions_prevented_total: int
    risks: List[Risk]


class DemandSensing(BaseModel):
    product_id: str
    product_name: str
    weeks_historical: List[str]
    weeks_forecast:   List[str]
    historical: List[float]
    forecast: List[float]
    confidence_lower: List[float]
    confidence_upper: List[float]
    external_signals: List[Dict[str, str]]
    agent_actions:    List[Dict[str, str]]


class StockoutRow(BaseModel):
    material_id: str
    material_name: str
    plant: str
    days_until_stockout: int
    pct_of_safety_stock: int
    status: str                        # Critical | At Risk | Healthy


class StockoutReport(BaseModel):
    critical_material: Optional[str]
    critical_stockout_date: Optional[str]
    rows: List[StockoutRow]


class SupplierHealth(BaseModel):
    supplier_id: str
    name: str
    role: str
    material_ids: List[str]
    on_time_pct: float
    qc_pass_pct: float
    risk_score: str
    risk_trend: str
    predictive_alert: Optional[str] = None


class SupplierHealthReport(BaseModel):
    suppliers: List[SupplierHealth]


class PlaybookResponse(BaseModel):
    event_id: str
    status: str               # "complete" | "agentcore_offline"
    agent_id: str
    final_answer: str
    reasoning_steps: int
    latency_ms: int


# ═════════════════════ /risks ═════════════════════

_SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


@router.get("/risks", response_model=RiskRadar)
async def list_risks():
    """Risk Radar tab — predictive_events with SageMaker probability refresh."""
    rows = await _events_db.scan(limit=200)
    # Sort by severity then days_until_impact
    rows.sort(key=lambda r: (_SEVERITY_ORDER.get(r.get("severity", "LOW"), 9), int(r.get("days_until_impact", 999))))

    # Refresh probability_pct for delay-type risks by hitting SageMaker lead-time
    # endpoint. Best-effort — falls back to stored value on endpoint failure.
    suppliers = {s["supplier_id"]: s for s in await _suppliers_db.scan(limit=50)}
    refreshed: List[Risk] = []
    for r in rows:
        prob = int(r.get("probability_pct", 0))
        if r.get("type") == "delay":
            sup = suppliers.get(r.get("affected_supplier_id", ""), {})
            risk_num = {"Very Low": 1, "Low": 2, "Medium": 3, "High": 4, "Critical": 5}.get(sup.get("risk_score", "Medium"), 3)
            pred = _sagemaker.predict_lead_time({
                "on_time_pct":        float(sup.get("on_time_pct", 90)),
                "lead_time_days_avg": float(sup.get("lead_time_days_avg", 12)),
                "risk_numeric":       risk_num,
                "qty":                3000.0,
                "port_enc":           0.0,
            })
            prob = max(prob, int(round(pred["probability_of_delay"] * 100)))
        refreshed.append(Risk(
            id=r["event_id"],
            type=r.get("type", "delay"),
            severity=r.get("severity", "LOW"),
            probability_pct=prob,
            title=r.get("title", ""),
            description=r.get("description", ""),
            affected_material_id=r.get("affected_material_id"),
            affected_supplier_id=r.get("affected_supplier_id"),
            affected_plants=r.get("affected_plants", []) or [],
            financial_exposure_usd=float(r.get("financial_exposure_usd", 0)),
            days_until_impact=int(r.get("days_until_impact", 0)),
            agent_playbook_ready=bool(r.get("agent_playbook_ready", True)),
        ))

    # KPIs
    active = sum(1 for r in refreshed if r.severity in ("CRITICAL", "HIGH", "MEDIUM"))
    exposure_30d = sum(r.financial_exposure_usd for r in refreshed if r.days_until_impact <= 30)
    # "Protected YTD" = sum of cost_avoided_usd from agent_audit_log this year
    audit = await _audit_db.scan(limit=200)
    protected_ytd = float(sum(a.get("cost_avoided_usd", 0) or 0 for a in audit))
    # "Agent runs today" = audit rows where run_id contains today's date prefix
    today_prefix = datetime.now(timezone.utc).strftime("%Y%m%d")
    runs_today = sum(1 for a in audit if today_prefix in (a.get("run_id") or ""))
    # Cumulative disruptions prevented = every audit row that actually saved
    # money. This is what a "Disruptions Prevented" KPI intuitively means.
    disruptions_prevented_total = sum(
        1 for a in audit if float(a.get("cost_avoided_usd", 0) or 0) > 0
    )

    return RiskRadar(
        kpi_active_risks=active,
        kpi_exposure_30d_usd=round(exposure_30d, 2),
        kpi_protected_ytd_usd=round(protected_ytd, 2),
        kpi_agent_runs_today=runs_today,
        kpi_disruptions_prevented_total=disruptions_prevented_total,
        risks=refreshed,
    )


# ═════════════════════ /demand ═════════════════════

@router.get("/demand", response_model=DemandSensing)
async def demand_sensing(product_id: str = "PRD-VSD-2201"):
    """Demand Sensing tab — real DeepAR forecast for the chosen product.

    Product defaults to Vinyl Siding (the spec's hero chart). The historical
    series is synthesized from the same 36-week training curve the model saw
    so the UI can render a continuous past-through-future line.
    """
    # Build 6-week historical baseline (units/week) from purchase-order activity
    # or fall back to the product's configured base. Keep it simple — DeepAR
    # expects context ≥ 12; the endpoint was trained with context_length=12.
    base_per_product = {
        "PRD-CSW-4860": 4400, "PRD-VSD-2201": 9800, "PRD-RFP-1102": 3200,
        "PRD-DRL-3304": 2100, "PRD-TRM-9910": 5200, "PRD-SSH-5402": 1400,
    }
    product_name = {
        "PRD-VSD-2201": "Vinyl Siding",
        "PRD-CSW-4860": "Commercial Casement Window",
        "PRD-RFP-1102": "Roofing Panel",
        "PRD-DRL-3304": "Door Light Insert",
        "PRD-TRM-9910": "Exterior Trim",
        "PRD-SSH-5402": "Storm Shield",
    }.get(product_id, product_id)
    base = base_per_product.get(product_id, 5000)
    import random as _r
    rng = _r.Random(sum(map(ord, product_id)))
    historical = [int(base * (0.92 + rng.random() * 0.16)) for _ in range(12)]

    pred = _sagemaker.forecast_demand(series=historical, prediction_length=12)

    today = datetime.now(timezone.utc).date()
    weeks_hist = [(today - timedelta(weeks=12 - i)).isoformat() for i in range(12)]
    weeks_fc   = [(today + timedelta(weeks=i + 1)).isoformat() for i in range(12)]

    signals = [
        {"type": "positive",    "description": "Hurricane season forecast: +22% demand spike for roofing in Southeast (Jun–Aug)."},
        {"type": "risk",        "description": "Housing starts down 8% YoY in Midwest. Predicts −14% demand for trim Q3."},
        {"type": "competitor",  "description": "Competitor product recall detected. Potential +9% demand uplift for CBB vinyl products."},
        {"type": "macro",       "description": "Fed rate cut probability 72% in Q3. Historical correlation: +11% new construction starts within 90 days."},
    ]
    actions = [
        {"title": "Pre-position Inventory", "detail": "Move 18,000 units of roofing to Southeast DCs ahead of hurricane demand."},
        {"title": "Reduce Midwest Build",   "detail": "Reduce Q3 trim production run by 12% to avoid overstock."},
        {"title": "Accelerate Procurement", "detail": "Issue early POs for Q4 raw materials to capture current pricing."},
    ]

    return DemandSensing(
        product_id=product_id,
        product_name=product_name,
        weeks_historical=weeks_hist,
        weeks_forecast=weeks_fc,
        historical=[float(x) for x in historical],
        forecast=pred["forecast"],
        confidence_lower=pred["confidence_lower"],
        confidence_upper=pred["confidence_upper"],
        external_signals=signals,
        agent_actions=actions,
    )


# ═════════════════════ /stockout ═════════════════════

@router.get("/stockout", response_model=StockoutReport)
async def stockout_forecast():
    """Stockout Forecast tab — Linear Learner prediction per inventory row."""
    inv_rows = [r for r in await _inv_bom_db.scan(limit=500) if r.get("kind") == "inventory"]
    plant_rows = {r["plant_id"]: r for r in await _inv_bom_db.scan(limit=500) if r.get("kind") == "plant"}
    material_rows = {r["material_id"]: r for r in await _inv_bom_db.scan(limit=500) if r.get("kind") == "material"}
    # Regional demand avg — one scan; cheap for our small dataset
    region_demand_avg = {"Midwest": 2800, "South": 3900, "Southeast": 3600, "Northeast": 2400}

    out: List[StockoutRow] = []
    critical_mat, critical_date = None, None
    for row in inv_rows:
        plant = plant_rows.get(row.get("plant_id"), {})
        mat   = material_rows.get(row.get("material_id"), {})
        region = plant.get("region", "Midwest")
        pred = _sagemaker.predict_stockout({
            "stock_level_kg":    float(row.get("stock_level_kg", 0)),
            "burn_rate_per_day": max(1.0, float(row.get("burn_rate_per_day", 1))),
            "safety_stock_pct":  float(row.get("safety_stock_pct", 50)),
            "region_demand_avg": float(region_demand_avg.get(region, 3000)),
            "trend_delta":       0.0,
        })
        days = pred["days_until_stockout"]
        pct  = int(row.get("safety_stock_pct", 50))
        status = ("Critical" if days <= 20 else "At Risk" if days <= 35 else "Healthy")
        out.append(StockoutRow(
            material_id=row["material_id"],
            material_name=mat.get("name", row["material_id"]),
            plant=plant.get("name", row["plant_id"]),
            days_until_stockout=days,
            pct_of_safety_stock=pct,
            status=status,
        ))
        if status == "Critical" and (critical_date is None or days < int(critical_date)):
            critical_mat = f"{mat.get('name', row['material_id'])} ({row['material_id']})"
            critical_date = days

    out.sort(key=lambda r: r.days_until_stockout)
    crit_iso = None
    if critical_date is not None:
        crit_iso = (datetime.now(timezone.utc).date() + timedelta(days=int(critical_date))).isoformat()

    return StockoutReport(
        critical_material=critical_mat,
        critical_stockout_date=crit_iso,
        rows=out,
    )


# ═════════════════════ /suppliers ═════════════════════

@router.get("/suppliers", response_model=SupplierHealthReport)
async def supplier_health():
    """Supplier Health tab — XGBoost multi-class risk score per supplier.

    Uses the supplier's most recent QC reading stored in `suppliers.json`'s
    last_qc_test (we keep the row's aggregate stats at hand). When we only
    have aggregate on_time_pct + qc_pass_pct, we map them through the model
    via a synthesized moisture/purity/viscosity triple.
    """
    rows = await _suppliers_db.scan(limit=100)
    out: List[SupplierHealth] = []
    for s in rows:
        # Synthesize a recent QC reading from pass-rate (so XGBoost has
        # something to classify). Lower pass-rate → higher moisture + lower purity.
        pass_pct = float(s.get("qc_pass_pct", 98))
        moisture = round(0.06 + (1 - pass_pct / 100) * 1.2, 4)
        purity   = round(pass_pct, 2)
        viscos   = 138.0 if pass_pct > 96 else 150.0
        pred = _sagemaker.predict_supplier_risk(moisture, purity, viscos)
        risk = pred["risk_score"]
        # Honour `suppliers.json` if we have a human-set value there.
        if s.get("risk_score"):
            risk = s["risk_score"]

        alert = None
        if s.get("notes"):
            alert = s["notes"]
        elif risk in ("High", "Critical"):
            alert = f"Model predicts risk score {risk}. Recommend tightening incoming inspection criteria."

        out.append(SupplierHealth(
            supplier_id=s["supplier_id"],
            name=s.get("name", s["supplier_id"]),
            role=s.get("role", "Primary"),
            material_ids=s.get("material_ids", []),
            on_time_pct=float(s.get("on_time_pct", 0)),
            qc_pass_pct=pass_pct,
            risk_score=risk,
            risk_trend=s.get("risk_trend", "stable"),
            predictive_alert=alert,
        ))
    # Order: Very Low → Critical (nice suppliers first), then alphabetical
    order = {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    out.sort(key=lambda s: (order.get(s.risk_score, 5), s.name))
    return SupplierHealthReport(suppliers=out)


# ═════════════════════ /risks/{id}/playbook ═════════════════════

@router.post("/risks/{event_id}/playbook", response_model=PlaybookResponse)
async def generate_playbook(event_id: str):
    """Invoke the real Logistics AgentCore runtime with the risk context to
    generate a mitigation playbook. Same pattern as simulator.py::run_scenario.
    """
    event = await _events_db.get_item({"event_id": event_id})
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Risk {event_id} not found")

    prompt = (
        f"RISK MITIGATION — ApexSignal has flagged {event['severity']} risk \"{event['title']}\".\n\n"
        f"Description: {event.get('description', '')}\n"
        f"Affected material: {event.get('affected_material_id', '?')}\n"
        f"Affected supplier: {event.get('affected_supplier_id', '?')}\n"
        f"Affected plants: {', '.join(event.get('affected_plants', []) or ['?'])}\n"
        f"Days until impact: {event.get('days_until_impact', '?')}\n"
        f"Financial exposure: ${float(event.get('financial_exposure_usd', 0)):,.0f}\n\n"
        f"Produce: (1) exposure summary, (2) 3 ranked mitigation options "
        f"(PREFERRED/FALLBACK/LAST_RESORT), (3) a decision on whether to "
        f"auto-dispatch or escalate to a Director, and (4) a crisp C-suite summary."
    )

    started = datetime.now(timezone.utc)
    result  = await _agentcore.invoke_agent("logisticsbot", prompt)
    latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)

    if not result.get("success"):
        return PlaybookResponse(
            event_id=event_id,
            status="agentcore_offline",
            agent_id="logisticsbot",
            final_answer=result.get("response") or "AgentCore runtime unreachable.",
            reasoning_steps=0,
            latency_ms=latency,
        )

    return PlaybookResponse(
        event_id=event_id,
        status="complete",
        agent_id="logisticsbot",
        final_answer=result.get("response", ""),
        reasoning_steps=len(result.get("reasoning", []) or []),
        latency_ms=latency,
    )


# ═════════════════════ /endpoints/status ═════════════════════

@router.get("/endpoints/status")
async def endpoints_status() -> Dict[str, str]:
    """SageMaker endpoint statuses — used by the UI to show online/offline pills."""
    return _sagemaker.endpoint_status()


# ═════════════════════════════════════════════════════════════════════
# STP Phase 2 — Plant Reliability tab (Nuclear Operations)
# ═════════════════════════════════════════════════════════════════════
#
# Reads the synthetic-data corpus directly (the same corpus the action
# handlers and AgentCore agents use). Once the live SageMaker endpoints
# (apex-signal-stp-rul / -anomaly / -failure-class) are deployed, this
# endpoint will swap to live inference — the response shape is already
# aligned to what the dashboard expects.

import json as _json
from pathlib import Path as _Path


class STPAssetRisk(BaseModel):
    equipment_id: str
    system_id: str
    risk_score: int                # 0-100
    risk_tier: str                 # low | moderate | high | critical
    days_until_failure: int
    confidence_lower_80: int
    confidence_upper_80: int
    active_anomaly: Optional[str]  # ANOM-… id when present
    expected_failure_mode: Optional[str]
    scripted_message: Optional[str]
    recommended_pm: Optional[str]
    estimated_avoidance_usd: int
    estimated_avoidance_hours: int


class STPPlantReliability(BaseModel):
    kpi_critical_assets: int
    kpi_high_risk_assets: int
    kpi_protected_ytd_usd: int       # cumulative avoidance from audit log
    kpi_engineers_retiring_24mo: int
    kpi_work_packages_indexed: int
    kpi_active_anomalies: int
    assets_at_risk: List[STPAssetRisk]
    last_updated: str
    model_versions: Dict[str, str]


def _load_stp_corpus_file(filename: str) -> Optional[Any]:
    """Read a JSON file from synthetic-data/nuclear_operations/. None on failure."""
    path = (
        _Path(__file__).resolve().parents[2]
        / "synthetic-data" / "nuclear_operations" / filename
    )
    if not path.exists():
        return None
    try:
        return _json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


@router.get("/stp/plant-reliability", response_model=STPPlantReliability)
async def stp_plant_reliability() -> STPPlantReliability:
    """STP Phase 2 — Plant Reliability tab data feed.

    Aggregates seed_anomalies + equipment + personnel + work_orders into the
    KPI tiles + at-risk asset table the ApexSignal "Plant Reliability" tab
    renders. Demo-grade today (reads JSON corpus); production swaps to live
    SageMaker scoring once the 3 STP endpoints are deployed.
    """
    anomalies = _load_stp_corpus_file("seed_anomalies.json") or []
    equipment = _load_stp_corpus_file("equipment.json") or []
    personnel = _load_stp_corpus_file("personnel.json") or []
    work_orders = _load_stp_corpus_file("work_orders.json") or []

    eq_by_id = {e["equipment_id"]: e for e in equipment}

    assets: List[STPAssetRisk] = []
    for an in anomalies:
        eq_row = eq_by_id.get(an.get("equipment_id"), {})
        z = float(an.get("z_score", 0))
        # Same tier mapping the risk_score_compute action uses
        if z >= 3.5:
            tier, score = "critical", 90
        elif z >= 3.0:
            tier, score = "high", 75
        elif z >= 2.0:
            tier, score = "moderate", 55
        else:
            tier, score = "low", 25
        d = int(an.get("expected_lead_days", 21))
        assets.append(STPAssetRisk(
            equipment_id=an.get("equipment_id", "unknown"),
            system_id=eq_row.get("system_id", ""),
            risk_score=score,
            risk_tier=tier,
            days_until_failure=d,
            confidence_lower_80=max(1, int(d * 0.7)),
            confidence_upper_80=int(d * 1.3),
            active_anomaly=an.get("anomaly_id"),
            expected_failure_mode=an.get("expected_failure_mode"),
            scripted_message=an.get("scripted_message"),
            recommended_pm=an.get("recommended_pm"),
            estimated_avoidance_usd=int(an.get("estimated_avoidance_usd", 0)),
            estimated_avoidance_hours=int(an.get("estimated_avoidance_hours", 0)),
        ))

    # Sort by risk tier then risk score
    tier_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    assets.sort(key=lambda a: (tier_order.get(a.risk_tier, 9), -a.risk_score))

    # KPI rollups
    kpi_critical = sum(1 for a in assets if a.risk_tier == "critical")
    kpi_high     = sum(1 for a in assets if a.risk_tier in ("critical", "high"))
    kpi_avoid    = sum(a.estimated_avoidance_usd for a in assets)
    # 32 engineers retirement-eligible in next 24 months — synthetic spec
    today = datetime.now(timezone.utc).replace(tzinfo=None)
    horizon = today + timedelta(days=730)
    kpi_retiring = 0
    for p in personnel:
        elig = p.get("retirement_eligible_date")
        if elig:
            try:
                d = datetime.fromisoformat(str(elig))
                if today <= d <= horizon:
                    kpi_retiring += 1
            except Exception:
                continue
    kpi_wps = len([w for w in work_orders if w.get("type") in ("preventive", "corrective", "surveillance")])

    return STPPlantReliability(
        kpi_critical_assets=kpi_critical,
        kpi_high_risk_assets=kpi_high,
        kpi_protected_ytd_usd=kpi_avoid,
        kpi_engineers_retiring_24mo=kpi_retiring,
        kpi_work_packages_indexed=kpi_wps,
        kpi_active_anomalies=len(assets),
        assets_at_risk=assets,
        last_updated=datetime.now(timezone.utc).isoformat(),
        model_versions={
            "rul":           "apex-signal-stp-rul-v1-cached",
            "anomaly":       "apex-signal-stp-anomaly-v1-cached",
            "failure_class": "apex-signal-stp-failure-class-v1-cached",
        },
    )


# ═════════════════════════════════════════════════════════════════════
# STP Phase 2 — proactive alert (the demo's killer moment)
# ═════════════════════════════════════════════════════════════════════
#
# The hero scenario calls for a proactive ReliabilityAgent banner to slide
# in unsolicited ~90s into the demo session — "vibration drift detected,
# 87% probability of bearing failure within 11 days, $340K avoidance."
#
# Implementation:
#   1. Frontend opens a session and remembers the timestamp (localStorage).
#   2. Frontend polls /signals/stp/proactive-alert every 10s starting at
#      session+60s. Backend returns 204 until session_age >= reveal_offset_s,
#      then returns the alert payload + audit_log_id.
#   3. After dismissal (frontend POST /signals/stp/proactive-alert/dismiss),
#      session is marked "dismissed" in memory so it doesn't re-fire.
#
# This is the cleanest path that:
#   • doesn't require a real EventBridge cron (overkill for the demo)
#   • doesn't require websockets (extra moving part during a live demo)
#   • is fully deterministic (always fires at the same offset)
#   • degrades gracefully if the network blips (poller retries)


from collections import defaultdict as _defaultdict
import time as _time


class STPProactiveAlert(BaseModel):
    """Payload pushed by the backend when a session crosses the reveal threshold."""
    alert_id: str
    severity: str                           # CRITICAL / HIGH / MEDIUM
    equipment_id: str
    title: str
    body: str                                # the scripted_message
    detected_at: str
    expected_failure_mode: Optional[str]
    days_until_impact: int
    recommended_pm: Optional[str]
    estimated_avoidance_usd: int
    audit_log_id: str
    cta_label: str
    cta_intent: str                          # the chat intent the CTA fires


# In-memory tracking — fine for tonight's demo (single-instance backend)
_demo_session_starts: Dict[str, float] = {}
_demo_dismissed: set[str] = set()
_DEFAULT_REVEAL_OFFSET_S = 90


def _hero_anomaly() -> Optional[Dict[str, Any]]:
    """Pick the P-3A vibration anomaly for the hero scenario.

    Falls back to whatever's first in seed_anomalies.json.
    """
    anomalies = _load_stp_corpus_file("seed_anomalies.json") or []
    if not anomalies:
        return None
    hero = next((a for a in anomalies if a.get("equipment_id") == "P-3A"), anomalies[0])
    return hero


@router.post("/stp/proactive-alert/start-session")
async def stp_alert_start_session(session_id: str) -> Dict[str, Any]:
    """Frontend calls this when ChatSTP page mounts.

    Records the session start so the backend can compute session age
    and decide when to release the proactive alert.
    """
    _demo_session_starts[session_id] = _time.time()
    _demo_dismissed.discard(session_id)
    return {
        "session_id": session_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "reveal_offset_seconds": _DEFAULT_REVEAL_OFFSET_S,
    }


@router.get("/stp/proactive-alert")
async def stp_proactive_alert(
    session_id: str,
    reveal_offset_seconds: int = _DEFAULT_REVEAL_OFFSET_S,
):
    """Polled by the chat UI every 10s during the demo.

    Returns:
      • 204 when session_age < reveal_offset, or session was dismissed
      • alert payload when session_age >= reveal_offset

    This is deliberately stateless on the frontend — the backend tracks
    which sessions have already fired, so the banner only appears once.
    """
    started_at = _demo_session_starts.get(session_id)
    if started_at is None:
        # Auto-register the session so the first poll establishes the timer
        started_at = _time.time()
        _demo_session_starts[session_id] = started_at

    if session_id in _demo_dismissed:
        # Backend returns the same 204 — UI keeps polling but doesn't re-fire
        from fastapi import Response
        return Response(status_code=204)

    session_age = _time.time() - started_at
    if session_age < reveal_offset_seconds:
        from fastapi import Response
        return Response(status_code=204)

    hero = _hero_anomaly()
    if hero is None:
        from fastapi import Response
        return Response(status_code=204)

    audit_id = f"AUD-{session_id[:8]}-{int(_time.time())}"
    payload = STPProactiveAlert(
        alert_id=hero.get("anomaly_id", "ANOM-UNKNOWN"),
        severity="CRITICAL",
        equipment_id=hero.get("equipment_id", ""),
        title=f"ReliabilityAgent · proactive alert · {hero.get('equipment_id', '')}",
        body=hero.get("scripted_message", ""),
        detected_at=hero.get("detected_at", datetime.now(timezone.utc).isoformat()),
        expected_failure_mode=hero.get("expected_failure_mode"),
        days_until_impact=int(hero.get("expected_lead_days", 11)),
        recommended_pm=hero.get("recommended_pm"),
        estimated_avoidance_usd=int(hero.get("estimated_avoidance_usd", 0)),
        audit_log_id=audit_id,
        cta_label="Open Playbook →",
        cta_intent="predictive_maintenance",
    )
    return payload


@router.post("/stp/proactive-alert/dismiss")
async def stp_alert_dismiss(session_id: str) -> Dict[str, Any]:
    """Mark the alert as dismissed for this session — UI calls this when
    the user clicks 'Dismiss' or 'Open Playbook' on the banner.
    """
    _demo_dismissed.add(session_id)
    return {"session_id": session_id, "dismissed_at": datetime.now(timezone.utc).isoformat()}


@router.post("/stp/proactive-alert/reset")
async def stp_alert_reset(session_id: str) -> Dict[str, Any]:
    """Reset both the session-start timer AND the dismissed flag.

    Lets a presenter re-arm the demo between dry-runs without restarting
    the backend.
    """
    _demo_session_starts.pop(session_id, None)
    _demo_dismissed.discard(session_id)
    return {"session_id": session_id, "reset_at": datetime.now(timezone.utc).isoformat()}


# ═══════════════════════════════════════════════════════════════════════
# Verizon Far Edge predictive endpoints
# ═══════════════════════════════════════════════════════════════════════
#
# Three SageMaker endpoints (deployed by
# backend/scripts/deploy_sagemaker_vz_endpoints.py):
#
#   /signals/vz/wave-risk        → XGBoost binary
#                                  P(this planned wave triggers an outage)
#   /signals/vz/site-cert        → XGBoost binary
#                                  P(individual site fails the 247-test cycle)
#                                  Supports batch via /site-cert/batch
#   /signals/vz/thermal-anomaly  → Random Cut Forest
#                                  per-site anomaly score over hourly readings
#
# All three fall back to deterministic mock predictions if the endpoint is
# offline so the page stays usable during cost-control teardown.

class VZWaveRiskRequest(BaseModel):
    device_type:           str   = "CaaS-Node-Type-B"      # Type-A|B|C
    firmware_from:         str   = "23.06"
    firmware_to:           str   = "24.01"
    region:                str   = "Northeast"
    schema_drift_events:   int   = 0
    historical_pass_rate:  float = 0.93
    season_q:              int   = 1                       # 1..4
    wave_size:             int   = 4000


class VZWaveRiskResponse(BaseModel):
    probability_of_outage: float
    risk_tier:             str
    top_reasons:           List[str]
    endpoint:              str
    explanation:           Dict[str, Any]


_DEVICE_ENUM  = {"CaaS-Node-Type-A": 0, "CaaS-Node-Type-B": 1, "CaaS-Node-Type-C": 2}
_REGION_ENUM  = {"Northeast": 0, "Northwest": 1, "Southeast": 2, "Southwest": 3,
                 "Midwest": 4, "South_Central": 5}
_SLA_ENUM     = {"premium": 0, "standard": 1, "economy": 2}
_STATUS_ENUM  = {"PASS": 0, "CONDITIONAL_PASS": 1, "FAIL": 2}


def _firmware_jump(a: str, b: str) -> int:
    try:
        ay, am = [int(x) for x in a.split(".")]
        by, bm = [int(x) for x in b.split(".")]
        return max(0, (by - ay) * 6 + (bm - am) // 2)
    except Exception:
        return 1


@router.post("/vz/wave-risk", response_model=VZWaveRiskResponse)
async def vz_wave_risk(req: VZWaveRiskRequest) -> VZWaveRiskResponse:
    """Score a wave's outage risk via SageMaker `apex-signal-vz-wave-risk`.

    The 7-feature CSV payload matches the columns produced by
    `synthetic-data/verizon_far_edge/generate_ml_training_data.py::build_wave_risk`.
    """
    features = {
        "device_type_enc":      float(_DEVICE_ENUM.get(req.device_type, 1)),
        "firmware_jump_size":   float(_firmware_jump(req.firmware_from, req.firmware_to)),
        "region_enc":           float(_REGION_ENUM.get(req.region, 0)),
        "schema_drift_events":  float(req.schema_drift_events),
        "historical_pass_rate": float(req.historical_pass_rate),
        "season_q":             float(req.season_q),
        "wave_size":            float(req.wave_size),
    }
    pred = _sagemaker.predict_vz_wave_risk(features)
    return VZWaveRiskResponse(
        probability_of_outage=pred["probability_of_outage"],
        risk_tier=pred["risk_tier"],
        top_reasons=pred["top_reasons"],
        endpoint=pred["endpoint"],
        explanation={
            "input":             req.model_dump(),
            "feature_vector":    features,
            "firmware_jump_size": features["firmware_jump_size"],
        },
    )


class VZSiteCertRequest(BaseModel):
    site_id:               str
    device_type:           str   = "CaaS-Node-Type-B"
    device_age_months:     int   = 36
    incident_count_12m:    int   = 0
    last_cert_status:      str   = "PASS"           # PASS|CONDITIONAL_PASS|FAIL
    current_firmware:      str   = "23.06"
    target_firmware:       str   = "24.12"
    vendor_sla_tier:       str   = "standard"
    region:                str   = "Northeast"
    prior_drift_exposure:  int   = 0


class VZSiteCertResponse(BaseModel):
    site_id:                  str
    probability_of_fail:      float
    predicted_outcome:        str
    feature_contributions:    Dict[str, float]
    endpoint:                 str


@router.post("/vz/site-cert", response_model=VZSiteCertResponse)
async def vz_site_cert(req: VZSiteCertRequest) -> VZSiteCertResponse:
    """Pre-flight cert risk score for a single site."""
    features = {
        "device_age_months":     float(req.device_age_months),
        "incident_count_12m":    float(req.incident_count_12m),
        "last_cert_status_enc":  float(_STATUS_ENUM.get(req.last_cert_status, 1)),
        "firmware_jump_size":    float(_firmware_jump(req.current_firmware, req.target_firmware)),
        "vendor_sla_tier_enc":   float(_SLA_ENUM.get(req.vendor_sla_tier, 1)),
        "region_enc":            float(_REGION_ENUM.get(req.region, 0)),
        "prior_drift_exposure":  float(req.prior_drift_exposure),
    }
    pred = _sagemaker.predict_vz_site_cert(features)
    return VZSiteCertResponse(
        site_id=req.site_id,
        probability_of_fail=pred["probability_of_fail"],
        predicted_outcome=pred["predicted_outcome"],
        feature_contributions=pred["feature_contributions"],
        endpoint=pred["endpoint"],
    )


class VZSiteCertBatchRequest(BaseModel):
    sites: List[VZSiteCertRequest]


@router.post("/vz/site-cert/batch")
async def vz_site_cert_batch(req: VZSiteCertBatchRequest) -> Dict[str, Any]:
    """Score N sites in one call — used by the Apex Signal map to color
    16,247 dots without 16k separate HTTP requests. Capped at 500 sites per
    call so a runaway client can't burn an inference quota."""
    sites = req.sites[:500]
    out: List[Dict[str, Any]] = []
    for site_req in sites:
        features = {
            "device_age_months":     float(site_req.device_age_months),
            "incident_count_12m":    float(site_req.incident_count_12m),
            "last_cert_status_enc":  float(_STATUS_ENUM.get(site_req.last_cert_status, 1)),
            "firmware_jump_size":    float(_firmware_jump(site_req.current_firmware, site_req.target_firmware)),
            "vendor_sla_tier_enc":   float(_SLA_ENUM.get(site_req.vendor_sla_tier, 1)),
            "region_enc":            float(_REGION_ENUM.get(site_req.region, 0)),
            "prior_drift_exposure":  float(site_req.prior_drift_exposure),
        }
        pred = _sagemaker.predict_vz_site_cert(features)
        out.append({
            "site_id":             site_req.site_id,
            "probability_of_fail": pred["probability_of_fail"],
            "predicted_outcome":   pred["predicted_outcome"],
        })
    return {"count": len(out), "scored": out, "endpoint": _sagemaker.predict_vz_site_cert.__doc__.split("·")[0].strip() if hasattr(_sagemaker.predict_vz_site_cert, "__doc__") else "apex-signal-vz-site-cert"}


class VZThermalAnomalyRequest(BaseModel):
    site_id:        str
    readings:       List[float]                      # hourly thermal_c readings
    ambient_temp:   Optional[float] = None


class VZThermalAnomalyResponse(BaseModel):
    site_id:           str
    anomaly_scores:    List[float]
    max_score:         float
    anomaly_detected:  bool
    severity:          str
    endpoint:          str


@router.post("/vz/thermal-anomaly", response_model=VZThermalAnomalyResponse)
async def vz_thermal_anomaly(req: VZThermalAnomalyRequest) -> VZThermalAnomalyResponse:
    """Score a thermal-reading time series for anomalies via Random Cut Forest.

    Reading granularity should be hourly; RCF was trained on ~1 week of
    hourly cabinet-temp readings. Sequences shorter than 24 points still
    return a result but with lower confidence (max_score interpretation
    becomes noisier).
    """
    pred = _sagemaker.detect_vz_thermal_anomaly(req.readings, ambient_temp=req.ambient_temp)
    return VZThermalAnomalyResponse(
        site_id=req.site_id,
        anomaly_scores=pred["anomaly_scores"],
        max_score=pred["max_score"],
        anomaly_detected=pred["anomaly_detected"],
        severity=pred["severity"],
        endpoint=pred["endpoint"],
    )


@router.get("/vz/endpoints/status")
async def vz_endpoints_status() -> Dict[str, Any]:
    """Lightweight badge for the Apex Signal page — describe each of the 3
    Verizon endpoints' SageMaker `EndpointStatus` so the UI can show a
    green/red dot.
    """
    import boto3
    sm_client = boto3.client("sagemaker", region_name="us-east-1")
    names = [
        settings.SAGEMAKER_ENDPOINT_VZ_WAVE_RISK,
        settings.SAGEMAKER_ENDPOINT_VZ_SITE_CERT,
        settings.SAGEMAKER_ENDPOINT_VZ_THERMAL_ANOMALY,
    ]
    result: List[Dict[str, str]] = []
    for n in names:
        try:
            resp = sm_client.describe_endpoint(EndpointName=n)
            result.append({"name": n, "status": resp.get("EndpointStatus", "Unknown")})
        except Exception:
            result.append({"name": n, "status": "NotDeployed"})
    overall = "live" if all(r["status"] == "InService" for r in result) else "degraded"
    return {"overall": overall, "endpoints": result}


@router.get("/vz/firmware-intelligence")
async def vz_firmware_intelligence() -> Dict[str, Any]:
    """Predictive firmware-certification intelligence mined from James Patchett's
    REAL 118-report corpus (synthetic-data/verizon_far_edge/real_test_catalog.json).

    Five forward-looking signals — each anchored on actual data points so the
    demo is credible and reproducible:

      1. conformance_forecast  — predict the next cert's benign-failure count
         per platform (every HPE platform throws 7, ZT 5-6 — pre-classified)
      2. regression_watch      — firmware versions with confirmed/suspected
         regressions (BMC .45 Samsung PM9A3 thermal)
      3. fleet_fragmentation   — firmware-rev spread per platform → drift risk
      4. coverage_gap          — test-type coverage per platform → cert risk
      5. upgrade_confidence    — validated vs untested WRCP upgrade paths
    """
    import json as _json
    from pathlib import Path as _Path

    catalog_path = (
        _Path(__file__).parent.parent.parent
        / "synthetic-data" / "verizon_far_edge" / "real_test_catalog.json"
    )

    # Deterministic fallback if the catalog file isn't present (keeps demo alive)
    try:
        cat = _json.loads(catalog_path.read_text())
        reports = cat.get("reports", [])
        summary = cat.get("summary", {})
    except Exception:
        reports, summary = [], {}

    # ── 1. Conformance noise forecast (from real DMTF reports) ──────────
    dmtf = [r for r in reports
            if r.get("test_type") == "DMTF Redfish Conformance"
            and (r.get("results") or {}).get("fail")]
    seen = {}
    for r in dmtf:
        key = f"{r['platform']} · {r['controller']} {r['firmware_version']}"
        seen[key] = (r.get("results") or {}).get("fail")
    conformance_forecast = [
        {
            "target": k,
            "predicted_failures": v,
            "all_benign": True,
            "signature": "WWW-Authenticate header + X.509 IPv6 cert",
            "action": "pre-classified · auto-certify on next run",
        }
        for k, v in sorted(seen.items(), key=lambda x: -(x[1] or 0))
    ] or [
        {"target": "HPE E930t · iLO6 1.57", "predicted_failures": 7, "all_benign": True,
         "signature": "WWW-Authenticate header + X.509 IPv6 cert",
         "action": "pre-classified · auto-certify on next run"},
    ]

    # ── 2. Firmware regression watch ────────────────────────────────────
    regression_watch = [
        {
            "firmware": "ZT BMC 0.45",
            "platform": "ZT Proteus (Samsung PM9A3 sites)",
            "issue": "Cannot read PM9A3 drive temp → fans spike to 100%",
            "meakv": "MEAKV-1792",
            "status": "CONFIRMED",
            "risk": "critical",
            "fix": "BMC 0.46",
            "recommendation": "BLOCK .45 wave to PM9A3 sites · mandate .46",
        },
        {
            "firmware": "Dell iDRAC 1.30.10.51",
            "platform": "Dell XR8720t",
            "issue": "Inlet-temp Warning thresholds null (LowerWarn/UpperWarn) — NEBS caution gap",
            "meakv": "thermal-comparison",
            "status": "FIXED-IN-NEWER",
            "risk": "medium",
            "fix": "iDRAC 1.30.33.10",
            "recommendation": "Roll forward to 1.30.33.10 — populates -23°C / 58°C inlet warnings",
        },
        {
            "firmware": "HPE iLO7 1.20.00",
            "platform": "HPE EL140 Gen12",
            "issue": "NEBS 62°C inlet ambient caution threshold unset (null) · not Redfish-settable",
            "meakv": "PROPOSED-31",
            "status": "COMPLIANCE-GAP",
            "risk": "medium",
            "fix": "manual iLO UI step post-provisioning",
            "recommendation": "Add to provisioning runbook — flag until automated",
        },
        {
            "firmware": "ZT BMC 0.43",
            "platform": "ZT Proteus (early-rev)",
            "issue": "Redfish 503 during host boot / inventory window",
            "meakv": "troubleshooting",
            "status": "TRANSIENT",
            "risk": "low",
            "fix": "RedfishDBReset + retry-after-boot",
            "recommendation": "watch · remediation in BMC playbook KB",
        },
    ]

    # ── 3. Fleet firmware fragmentation (drift risk) ───────────────────
    frag = {}
    for r in reports:
        v = r.get("firmware_version")
        if v and v != "n/a":
            frag.setdefault(r["platform"], set()).add(f"{r['controller']} {v}")
    fleet_fragmentation = sorted(
        [
            {
                "platform": p,
                "distinct_revs": len(vers),
                "revs": sorted(vers),
                "drift_risk": "high" if len(vers) >= 5 else "medium" if len(vers) >= 3 else "low",
            }
            for p, vers in frag.items()
        ],
        key=lambda x: -x["distinct_revs"],
    )

    # ── 4. Coverage gap (new-platform cert risk) ───────────────────────
    cov = {}
    for r in reports:
        cov.setdefault(r["platform"], set()).add(r.get("test_type"))
    TOTAL_TEST_TYPES = 14
    coverage_gap = sorted(
        [
            {
                "platform": p,
                "covered": len(types),
                "total": TOTAL_TEST_TYPES,
                "coverage_pct": round(len(types) / TOTAL_TEST_TYPES * 100),
                "wave_eligible": len(types) >= 6,
            }
            for p, types in cov.items()
        ],
        key=lambda x: x["covered"],
    )

    # ── 5. Upgrade path confidence ─────────────────────────────────────
    validated = summary.get("wrcp_versions", ["21.05p6", "21.12p10", "22.12mr1"])
    upgrade_confidence = {
        "validated_paths": ["21.05p6 → 21.12p10 (ZT Proteus · alarms clear)"],
        "versions_seen": validated,
        "untested_warning": "Any path skipping a validated rev = HITL gate",
    }

    # ── 6. Golden Configuration drift ──────────────────────────────────
    # Directly addresses James's in-flight "golden config dashboard": compare
    # the LAB-CERTIFIED (golden) firmware to what PRODUCTION is running, flag
    # drift. SSD firmware is the gap he called out as "not yet tracked".
    # Golden revs pinned to the real latest-certified version per controller
    # (the corpus mixes iLO5/iLO6 + report-name noise, so we don't max-parse).
    golden_config = [
        {"platform": "HPE EL140 Gen12", "controller": "iLO7", "lab_certified": "1.20.00",
         "production": "onboarding", "drift_sites": 0, "status": "CERTIFYING", "risk": "medium",
         "note": "New current-gen server type — 7 playbook changes proposed, NEBS 62°C threshold unset"},
        {"platform": "Dell XR8720t", "controller": "iDRAC 10", "lab_certified": "1.30.33.10",
         "production": "1.30.10.51 / 1.30.33.10 mix", "drift_sites": 64, "status": "DRIFT", "risk": "medium",
         "note": "Inlet-temp warning thresholds were null on 1.30.10.51, populated on 1.30.33.10 — roll forward"},
        {"platform": "ZT Proteus", "controller": "BMC", "lab_certified": "0.46",
         "production": "0.45 / 0.46 mix", "drift_sites": 312, "status": "DRIFT", "risk": "critical",
         "note": "BMC .45 still in field on Samsung PM9A3 sites — MEAKV-1792 thermal regression"},
        {"platform": "HPE E930t", "controller": "iLO6", "lab_certified": "1.60",
         "production": "1.57 / 1.60 mix", "drift_sites": 88, "status": "DRIFT", "risk": "medium",
         "note": "Field running 1.57; golden is 1.60 — schedule rolling update"},
        {"platform": "ZT Triton", "controller": "BMC", "lab_certified": "2.31",
         "production": "2.31", "drift_sites": 0, "status": "ALIGNED", "risk": "low",
         "note": "Production matches lab-certified golden"},
    ]
    # The SSD-firmware tracking gap James explicitly flagged in the call
    golden_config_gaps = [
        {"component": "SSD firmware (Samsung PM9A3)", "tracked": False,
         "impact": "Not in the golden-config baseline yet — the .45 thermal regression is invisible to drift checks until added",
         "recommendation": "Add SSD firmware to the golden-config schema (MEAKV-1792 makes this urgent)"},
        {"component": "CPLD firmware (ZT PDB)", "tracked": False,
         "impact": "PDB-CPLD revs not baselined — platform-deployment drift can slip through",
         "recommendation": "Extend golden-config to CPLD components"},
    ]

    return {
        "source": "James Patchett · MTCE Lab · 118 real firmware reports",
        "total_reports": summary.get("total_reports", len(reports)),
        "conformance_forecast": conformance_forecast,
        "regression_watch": regression_watch,
        "fleet_fragmentation": fleet_fragmentation,
        "coverage_gap": coverage_gap,
        "upgrade_confidence": upgrade_confidence,
        "golden_config": golden_config,
        "golden_config_gaps": golden_config_gaps,
    }


@router.get("/vz/orchestration/state")
async def vz_orchestration_state(campaign: str = "el140") -> Dict[str, Any]:
    """Agent-orchestration timeline for the demo (Bob's focus area).

    Models the END-TO-END autonomous run for onboarding a brand-new server
    type — HPE EL140 Gen12 (iLO 7) — whose existing MEAKV tests + BMC playbook
    are BLOCKED. The orchestrator drives the campaign through MULTIPLE
    ITERATIONS and cleanly separates the platform's two tiers:

      • REPORTING & CORRELATION  (kind="correlate")  — read-only intelligence.
        Analyze, classify, cross-correlate, predict, draft change-specs.
        Auto-runs. Mutates NOTHING in the lab.

      • DIRECT LAB ACTION        (kind="action")     — executes against live
        lab hardware (SSH proxy → Redfish PATCH / BIOS / power-cycle / apply
        playbook). EVERY direct action is gated by human approval (HITL).

    Anchored on the real campaign data (PROPOSED-20..32, run1..5 iterations,
    playbook-change-spec, NEBS compliance gap, secure-boot install).
    """
    AGENT = {
        "orchestrator": {"code": "ORC", "name": "OrchestratorAgent", "color": "#6c47ff"},
        "cert":         {"code": "CRT", "name": "CertificationAgent", "color": "#1d4ed8"},
        "playbook":     {"code": "PBK", "name": "PlaybookAgent",      "color": "#0891b2"},
        "signal":       {"code": "SIG", "name": "SignalAgent",        "color": "#d97706"},
    }

    def iters(results):
        return [{"n": i + 1, "label": f"run{i+1}", **r} for i, r in enumerate(results)]

    el140_timeline = [
        {
            "seq": 1, "agent": "cert", "kind": "correlate",
            "title": "Detect blocked coverage",
            "detail": "Read EL140 Gen12 intake. MEAKV-1750 / MEAKV-1793 are BLOCKED — iLO 7 is a new server type the existing BMC playbook does not support.",
            "evidence": "iLO 7 v1.20.00 · BIOS v1.30 · 273-attr registry",
            "requires_hitl": False, "duration_ms": 1400,
        },
        {
            "seq": 2, "agent": "orchestrator", "kind": "correlate",
            "title": "Design test coverage",
            "detail": "Propose PROPOSED-20→32: account mgmt, NTP, DNS, hostname, syslog, Redfish events, NIC/MAC discovery, BIOS WorkloadProfile, secure boot.",
            "evidence": "13 new test cases drafted from the MEAKV catalog + iLO7 registry",
            "requires_hitl": False, "duration_ms": 2100,
        },
        {
            "seq": 3, "agent": "orchestrator", "kind": "gate",
            "title": "HITL · authorize live-lab execution",
            "detail": "Running PROPOSED-20→28 against the live EL140 at 2607:f160:10:90bf:ce:40a:0:e002 mutates lab hardware. Approve to proceed.",
            "evidence": "Target: live lab unit via vcpe-jumpserver2 SSH proxy",
            "requires_hitl": True, "duration_ms": 0,
        },
        {
            "seq": 4, "agent": "cert", "kind": "action",
            "title": "Connect + capture baseline",
            "detail": "SSH proxy → Redfish GET live EL140 baseline (PowerState=On, PostState=FinishedPost, Account 65536, WorkloadProfile=vRAN).",
            "evidence": "GET /redfish/v1/Managers/1 · /Systems/1 · live unit",
            "lab_target": "EL140 · 2607:f160:10:90bf:ce:40a:0:e002",
            "requires_hitl": False, "duration_ms": 1800,
        },
        {
            "seq": 5, "agent": "cert", "kind": "action",
            "title": "Execute PROPOSED-20→28 · 5 iterations each",
            "detail": "Run the provisioning + cert suite through 5 iterations for statistical confidence. Live Redfish calls against the EL140.",
            "evidence": "9 test cases × 5 runs = 45 executions",
            "lab_target": "EL140 · iLO 7 Redfish",
            "iterations": iters([
                {"result": "pass",     "metric": "9/9 pass · 133s ilo-reset"},
                {"result": "pass",     "metric": "9/9 pass · 131s"},
                {"result": "pass-dev", "metric": "8/9 · DNS 6-entry → HTTP 400 ArrayPropertyOutOfBound"},
                {"result": "pass",     "metric": "9/9 pass · DNS retried with 3-entry array"},
                {"result": "pass",     "metric": "9/9 pass · stable"},
            ]),
            "requires_hitl": False, "duration_ms": 5200,
        },
        {
            "seq": 6, "agent": "signal", "kind": "correlate",
            "title": "Pull real reference values from live e930t",
            "detail": "Instead of placeholders, read production NTP/DNS/syslog from a live e930t (iLO 6) in the same lab to validate against real config.",
            "evidence": "NTP 2607:f160:10:9200::a/::b · syslog vcp-faredge-syslog.mon.vzwops.com:5140",
            "requires_hitl": False, "duration_ms": 1600,
        },
        {
            "seq": 7, "agent": "signal", "kind": "correlate",
            "title": "Cross-platform correlation",
            "detail": "Several iLO 7 deviations (DateTime NTP endpoint, RegistryPrefixes events, StaticNameServers 3-entry limit) are ALSO present on iLO 6 — broadening the required playbook scope beyond EL140.",
            "evidence": "3 deviations confirmed on iLO6 + iLO7 · iLO5 unconfirmed",
            "requires_hitl": False, "duration_ms": 2000,
        },
        {
            "seq": 8, "agent": "playbook", "kind": "correlate",
            "title": "Gap analysis → draft change-spec",
            "detail": "Cross-reference the 9 result files against the live Ansible playbook (commit 5ff15f7028). Produce a formal change spec — this is a PROPOSAL, nothing is applied.",
            "evidence": "7 CHANGE REQUIRED · 7 NO CHANGE · 1 VERIFY · across 15 role files",
            "requires_hitl": False, "duration_ms": 2600,
        },
        {
            "seq": 9, "agent": "signal", "kind": "correlate",
            "title": "Compliance + drift scan",
            "detail": "NEBS inlet ambient caution threshold (req 62°C) is unset (null) on EL140. No security-hardening role exists. iDRAC thermal thresholds drifted between 1.30.10.51 → 1.30.33.10.",
            "evidence": "2 compliance gaps · 1 firmware drift flagged",
            "requires_hitl": False, "duration_ms": 1800,
        },
        {
            "seq": 10, "agent": "orchestrator", "kind": "gate",
            "title": "HITL · approve playbook changes",
            "detail": "7 Ansible changes (group_vars/HPE, check_model, bios-config, mac-discover, ilo-hostname, subscribe-redfish-events + new security-hardening role). Review and approve before any commit.",
            "evidence": "Change spec: playbook-change-spec-HPE-EL140-Gen12.md",
            "requires_hitl": True, "duration_ms": 0,
        },
        {
            "seq": 11, "agent": "playbook", "kind": "action",
            "title": "Apply playbook changes · open PR",
            "detail": "Commit the 7 approved changes to the BMC playbook repo and open a PR for the automation team. Direct action — version-controlled + auditable.",
            "evidence": "branch: el140-ilo7-support → PR #(draft)",
            "lab_target": "vcpe-jumpserver2:/home/patchja/bmc_playbook_EL140",
            "requires_hitl": False, "duration_ms": 2200,
        },
        {
            "seq": 12, "agent": "orchestrator", "kind": "gate",
            "title": "HITL · approve BIOS + secure-boot config",
            "detail": "Set BIOS WorkloadProfile=vRAN and install Secure Boot KEK/DB certs on the live EL140 — requires a cold-boot cycle. Approve lab change.",
            "evidence": "PROPOSED-30 · 9-step procedure · ~8–10 min POST",
            "requires_hitl": True, "duration_ms": 0,
        },
        {
            "seq": 13, "agent": "cert", "kind": "action",
            "title": "Configure BIOS + Secure Boot",
            "detail": "PATCH WorkloadProfile=vRAN (11 vRAN settings atomically), POST KEK+DB certs, enable SecureBoot, ForceRestart → cold boot → poll FinishedPost.",
            "evidence": "PATCH /Systems/1/Bios · POST SecureBoot certs · cert count baseline+1",
            "lab_target": "EL140 · iLO 7 Redfish",
            "requires_hitl": False, "duration_ms": 4200,
        },
        {
            "seq": 14, "agent": "cert", "kind": "action",
            "title": "Re-certify · 5 iterations",
            "detail": "Re-run the full PROPOSED suite post-config through 5 iterations to confirm the platform is green and stable.",
            "evidence": "9 cases × 5 runs · all pass",
            "lab_target": "EL140 · iLO 7 Redfish",
            "iterations": iters([
                {"result": "pass", "metric": "9/9 pass"},
                {"result": "pass", "metric": "9/9 pass"},
                {"result": "pass", "metric": "9/9 pass"},
                {"result": "pass", "metric": "9/9 pass"},
                {"result": "pass", "metric": "9/9 pass · SecureBoot ON · vRAN profile applied"},
            ]),
            "requires_hitl": False, "duration_ms": 4800,
        },
        {
            "seq": 15, "agent": "orchestrator", "kind": "correlate",
            "title": "Certification report + audit trail",
            "detail": "EL140 Gen12 certified. New test cases added to the catalog, playbook PR ready, every decision + lab action hash-chained to the audit log.",
            "evidence": "Campaign: PASS WITH DEVIATIONS · 0 fails · full lineage",
            "requires_hitl": False, "duration_ms": 1500,
        },
    ]

    # ── Campaign 2 · Dell XR8720t — Current-Gen Certification ──
    xr8720_timeline = [
        {"seq": 1, "agent": "cert", "kind": "correlate", "title": "Ingest cert campaign",
         "detail": "Read the Dell XR8720t intake — 40 tests across Inventory, Sensor, BIOS, Security, Conformance. iDRAC 10, Xeon 6776P-B (GNR-D).",
         "evidence": "iDRAC 1.30.10.51 · BIOS 1.1.3 · 410-attr registry", "requires_hitl": False, "duration_ms": 1400},
        {"seq": 2, "agent": "cert", "kind": "correlate", "title": "Classify by category",
         "detail": "Inventory MEAKV-648-655 · Sensor 518-523/1789 · BIOS 508-517/1808 · Security PROPOSED-10/13/14 · Conformance MEAKV-507.",
         "evidence": "40 test cases mapped to the MEAKV/PROPOSED catalog", "requires_hitl": False, "duration_ms": 1800},
        {"seq": 3, "agent": "orchestrator", "kind": "gate", "title": "HITL · authorize live-lab cert run",
         "detail": "Running the suite against the live XR8720t mutates lab hardware (BIOS reads, LED, sessions). Approve to proceed.",
         "evidence": "Target: idrac-HDM35J4 · 2607:f160:10:823a:ce:40a:0:e001", "requires_hitl": True, "duration_ms": 0},
        {"seq": 4, "agent": "cert", "kind": "action", "title": "Connect + capture baseline",
         "detail": "SSH proxy → iDRAC 10 Redfish GET. 256 GB DDR5 6400 MT/s MaxPerf · 72c/144t · NIC LinkUp.",
         "evidence": "GET /redfish/v1/Systems/System.Embedded.1", "lab_target": "XR8720t · iDRAC 10", "requires_hitl": False, "duration_ms": 1800},
        {"seq": 5, "agent": "cert", "kind": "action", "title": "Inventory + Sensor + BIOS suite · 5 iterations",
         "detail": "Run inventory, thermal/fan/PSU/voltage sensors, and BIOS config through 5 iterations on the live unit.",
         "evidence": "27 cases × 5 runs", "lab_target": "XR8720t · iDRAC 10",
         "iterations": iters([
             {"result": "pass", "metric": "27/27 healthy"}, {"result": "pass", "metric": "27/27"},
             {"result": "pass-dev", "metric": "BIOS IommuSupport=null (GNR-D)"}, {"result": "pass", "metric": "VT-d functional via ProcVirtualization"},
             {"result": "pass", "metric": "27/27 stable"}]),
         "requires_hitl": False, "duration_ms": 5000},
        {"seq": 6, "agent": "cert", "kind": "action", "title": "DMTF Redfish Conformance · 5 iterations",
         "detail": "Redfish-Protocol-Validator against iDRAC 10 — repeatability check across 5 runs.",
         "evidence": "MEAKV-507 · 379 pass / 9 fail", "lab_target": "XR8720t · iDRAC 10",
         "iterations": iters([
             {"result": "pass-dev", "metric": "379 pass / 9 fail"}, {"result": "pass-dev", "metric": "379 / 9"},
             {"result": "pass-dev", "metric": "379 / 9 (same signature)"}, {"result": "pass-dev", "metric": "379 / 9"},
             {"result": "pass-dev", "metric": "379 / 9 · consistent"}]),
         "requires_hitl": False, "duration_ms": 5000},
        {"seq": 7, "agent": "cert", "kind": "correlate", "title": "Triage 9 conformance failures",
         "detail": "6× WWW-Authenticate header + 1× X.509 IPv6 cert + 1× ETag stale + 1× SSE ID reuse — all known-benign for VCPfe production.",
         "evidence": "Matches the fleet-wide benign signature → auto-certify", "requires_hitl": False, "duration_ms": 1900},
        {"seq": 8, "agent": "signal", "kind": "correlate", "title": "Classify BIOS deviations",
         "detail": "IommuSupport / NumaNodesPerSocket / ProcX2Apic = null — Intel GNR-D platform differences from the AMD R7615 baseline. NUMA topology correct.",
         "evidence": "3 BIOS deviations · all accepted", "requires_hitl": False, "duration_ms": 1700},
        {"seq": 9, "agent": "signal", "kind": "correlate", "title": "LED quirk + thermal drift",
         "detail": "IndicatorLED 'Off' → HTTP 400 on iDRAC 10 (Lit/Blinking only) — test adapted. Inlet-temp warning thresholds null on 1.30.10.51 (fixed in 1.30.33.10).",
         "evidence": "PROPOSED-13 adapted · firmware drift flagged", "requires_hitl": False, "duration_ms": 1600},
        {"seq": 10, "agent": "orchestrator", "kind": "gate", "title": "HITL · approve cert with deviations",
         "detail": "40 tests · 0 failures · 10 accepted deviations · 1 partial (HttpPushUri null, expected). Approve certification.",
         "evidence": "PASS WITH DEVIATIONS", "requires_hitl": True, "duration_ms": 0},
        {"seq": 11, "agent": "orchestrator", "kind": "correlate", "title": "Certification report + audit trail",
         "detail": "Dell XR8720t certified. Every deviation documented + accepted, full lineage hash-chained.",
         "evidence": "29 PASS · 10 PASS-DEV · 1 PARTIAL · 0 FAIL", "requires_hitl": False, "duration_ms": 1500},
    ]

    # ── Campaign 3 · ZT Proteus — Samsung PM9A3 Thermal Regression ──
    proteus_timeline = [
        {"seq": 1, "agent": "signal", "kind": "correlate", "title": "Detect thermal anomaly",
         "detail": "Field telemetry: fans at 100% utilization on ZT Proteus subclouds running BMC .45 with Samsung PM9A3 drives.",
         "evidence": "Anomaly on PM9A3-equipped sites · BMC 0.45", "requires_hitl": False, "duration_ms": 1500},
        {"seq": 2, "agent": "schema", "kind": "correlate", "title": "Hypothesize root cause",
         "detail": "Suspect: BMC .45 cannot read the SAMSUNG PM9A3 (MZQL21T9HCJR-00A07) temperature → fan controller defaults to failsafe (100%).",
         "evidence": "MEAKV-1792 candidate", "requires_hitl": False, "duration_ms": 1600},
        {"seq": 3, "agent": "orchestrator", "kind": "gate", "title": "HITL · authorize lab reproduction",
         "detail": "Reproducing requires downgrading a lab unit .46 → .45 (a firmware write). Approve to proceed.",
         "evidence": "Lab unit · welktxef-d931856-008", "requires_hitl": True, "duration_ms": 0},
        {"seq": 4, "agent": "cert", "kind": "action", "title": "Downgrade BMC .46 → .45",
         "detail": "update-bmc-redfish on the lab unit. Manager.Reset, wait for BMC.",
         "evidence": "BMC 0.46 → 0.45 · Serial 207736270043", "lab_target": "ZT Proteus · BMC Redfish", "requires_hitl": False, "duration_ms": 3000},
        {"seq": 5, "agent": "cert", "kind": "action", "title": "Reproduce · 5 iterations",
         "detail": "Read the PM9A3 thermal sensor + observe fan behavior across 5 runs on BMC .45.",
         "evidence": "5 reads of the PM9A3 temp sensor", "lab_target": "ZT Proteus · BMC .45",
         "iterations": iters([
             {"result": "fail", "metric": "PM9A3 temp = N/A · fans 100%"}, {"result": "fail", "metric": "temp N/A · fans 100%"},
             {"result": "fail", "metric": "temp N/A · fans 100%"}, {"result": "fail", "metric": "temp N/A · fans 100%"},
             {"result": "fail", "metric": "reproduced 5/5 · confirmed"}]),
         "requires_hitl": False, "duration_ms": 5000},
        {"seq": 6, "agent": "schema", "kind": "correlate", "title": "Confirm root cause",
         "detail": "MEAKV-1792 confirmed: BMC .45 PM9A3 thermal read failure → fan failsafe. Deploy-blocking regression.",
         "evidence": "Root cause locked · drive MZQL21T9HCJR-00A07", "requires_hitl": False, "duration_ms": 1500},
        {"seq": 7, "agent": "cert", "kind": "action", "title": "Upgrade BMC .45 → .46",
         "detail": "Apply the fix firmware on the lab unit and re-validate.",
         "evidence": "BMC 0.45 → 0.46", "lab_target": "ZT Proteus · BMC Redfish", "requires_hitl": False, "duration_ms": 3000},
        {"seq": 8, "agent": "cert", "kind": "action", "title": "Re-validate fix · 5 iterations",
         "detail": "Read PM9A3 temp + fan behavior across 5 runs on BMC .46.",
         "evidence": "5 reads post-fix", "lab_target": "ZT Proteus · BMC .46",
         "iterations": iters([
             {"result": "pass", "metric": "PM9A3 temp OK · fans nominal"}, {"result": "pass", "metric": "temp OK"},
             {"result": "pass", "metric": "temp OK"}, {"result": "pass", "metric": "temp OK"},
             {"result": "pass", "metric": "5/5 · fix validated"}]),
         "requires_hitl": False, "duration_ms": 5000},
        {"seq": 9, "agent": "signal", "kind": "correlate", "title": "Compute blast radius",
         "detail": "Every subcloud running BMC .45 with Samsung PM9A3 drives is exposed. Minimum safe BMC = .46.",
         "evidence": "Affected: all PM9A3 sites on .45", "requires_hitl": False, "duration_ms": 1500},
        {"seq": 10, "agent": "orchestrator", "kind": "gate", "title": "HITL · approve wave block",
         "detail": "Block BMC .45 from any wave deployment to PM9A3-equipped sites and mandate .46. Approve.",
         "evidence": "UpgradeAdvisor wave gate", "requires_hitl": True, "duration_ms": 0},
        {"seq": 11, "agent": "upgrade", "kind": "action", "title": "Apply wave block + golden-config update",
         "detail": "Block .45 → PM9A3 sites; add SSD firmware to the golden-config baseline so this drift is caught automatically next time.",
         "evidence": "Block list pushed · golden-config updated", "lab_target": "UpgradeAdvisor + golden-config", "requires_hitl": False, "duration_ms": 2200},
        {"seq": 12, "agent": "orchestrator", "kind": "correlate", "title": "Regression report + audit trail",
         "detail": "Regression characterized, fix validated, wave blocked — all before it shipped to a single production site.",
         "evidence": "Found in lab · prevented in field · full lineage", "requires_hitl": False, "duration_ms": 1500},
    ]

    # ── Campaign 4 · WRCP 24.09.301 — Platform / OS Certification ──
    wrcp_timeline = [
        {"seq": 1, "agent": "cert", "kind": "correlate", "title": "Ingest platform campaign",
         "detail": "Wind River Cloud Platform 24.09.301 vs 2212 baseline — the OS/platform cert layer (distinct from BMC/firmware).",
         "evidence": "1,281 artifacts · 390 MB campaign", "requires_hitl": False, "duration_ms": 1500},
        {"seq": 2, "agent": "orchestrator", "kind": "correlate", "title": "Plan coverage",
         "detail": "Performance (sysbench/latency/network/storage) · Functional (RBAC/K8s/Redfish) · Platform (HA/rehoming/sw-update) · Conformance (sonobuoy) · Deployment MOPs.",
         "evidence": "VZFWE-* / VZWFE-* / MEAKV-1658", "requires_hitl": False, "duration_ms": 1800},
        {"seq": 3, "agent": "orchestrator", "kind": "gate", "title": "HITL · authorize subcloud deploy",
         "detail": "Deploying a WRCP subcloud (MOP VZFWE-25/26) provisions live controllers + worker. Approve.",
         "evidence": "Central Controller install runbook", "requires_hitl": True, "duration_ms": 0},
        {"seq": 4, "agent": "cert", "kind": "action", "title": "Deploy subcloud (MOP VZFWE-25/26)",
         "detail": "Duplex controllers + worker enrolled to the system controller; platform-integ alarms cleared.",
         "evidence": "duplex · distributed-cloud in-sync", "lab_target": "WRCP subcloud", "requires_hitl": False, "duration_ms": 3200},
        {"seq": 5, "agent": "cert", "kind": "action", "title": "Sysbench performance · 5 iterations",
         "detail": "CPU + memory + I/O stress across 6 HW types (HP E910/Ice/SPR · ZT Ice/SPR/Titan), 5 runs each for statistical confidence.",
         "evidence": "1,080 run files aggregated", "lab_target": "WRCP fleet",
         "iterations": iters([
             {"result": "pass", "metric": "within envelope"}, {"result": "pass", "metric": "nominal"},
             {"result": "pass", "metric": "nominal"}, {"result": "pass", "metric": "nominal"},
             {"result": "pass", "metric": "5/5 · no perf regression vs 2212"}]),
         "requires_hitl": False, "duration_ms": 5200},
        {"seq": 6, "agent": "cert", "kind": "action", "title": "Latency (VZWFE-202) · 5 iterations",
         "detail": "RT latency under load across 5 runs — RAN-critical envelope check.",
         "evidence": "sw-latency-summary", "lab_target": "WRCP subcloud",
         "iterations": iters([
             {"result": "pass", "metric": "within RT envelope"}, {"result": "pass", "metric": "within"},
             {"result": "pass", "metric": "within"}, {"result": "pass", "metric": "within"},
             {"result": "pass", "metric": "5/5 stable"}]),
         "requires_hitl": False, "duration_ms": 5000},
        {"seq": 7, "agent": "cert", "kind": "action", "title": "Kubernetes conformance (sonobuoy)",
         "detail": "Run the K8s conformance suite against the subcloud.",
         "evidence": "sonobuoy · pass", "lab_target": "WRCP K8s", "requires_hitl": False, "duration_ms": 3000},
        {"seq": 8, "agent": "signal", "kind": "correlate", "title": "Compare vs 2212 baseline",
         "detail": "Diff performance + functional results against the prior 2212p5 baseline — confirm no regression.",
         "evidence": "VZWFE-535/536 comparison · clean", "requires_hitl": False, "duration_ms": 1800},
        {"seq": 9, "agent": "cert", "kind": "correlate", "title": "Functional sweep",
         "detail": "RBAC · K8s CPU Manager · Local Docker Registry · Redfish API · Alarms · HA · rehoming · software-update.",
         "evidence": "all functional categories pass", "requires_hitl": False, "duration_ms": 1700},
        {"seq": 10, "agent": "orchestrator", "kind": "gate", "title": "HITL · approve platform cert",
         "detail": "Performance, functional, conformance, and deployment all green vs baseline. Approve platform certification.",
         "evidence": "WRCP 24.09.301 cert", "requires_hitl": True, "duration_ms": 0},
        {"seq": 11, "agent": "orchestrator", "kind": "correlate", "title": "Platform cert report + audit trail",
         "detail": "WRCP 24.09.301 certified for the fleet. Same multi-iteration rigor + audit trail as the firmware layer.",
         "evidence": "1,080 perf runs · 0 regressions · full lineage", "requires_hitl": False, "duration_ms": 1500},
    ]

    TIERS = {
        "correlate": {"label": "Reporting & Correlation",
                      "sublabel": "Read-only intelligence · auto-runs · mutates nothing in the lab", "color": "#2563eb"},
        "action":    {"label": "Direct Lab Action",
                      "sublabel": "Executes on live hardware · every action HITL-gated", "color": "#dc2626"},
    }

    CAMPAIGNS = {
        "el140": {
            "id": "el140", "campaign": "HPE EL140 Gen12 · New-Platform Onboarding",
            "platform": "HPE ProLiant Compute EL140 Gen12 · iLO 7 v1.20.00 · BIOS v1.30",
            "source": "Real campaign · James Patchett · MTCE Lab · 2026-06-10",
            "manual_baseline_hrs": 40, "orchestrated_min": 18, "timeline": el140_timeline,
        },
        "xr8720": {
            "id": "xr8720", "campaign": "Dell XR8720t · Current-Gen Certification",
            "platform": "Dell XR8720t · iDRAC 10 (1.30.10.51) · BIOS 1.1.3 · Xeon 6776P-B GNR-D",
            "source": "Real campaign · James Patchett · MTCE Lab · 2026-06-16",
            "manual_baseline_hrs": 36, "orchestrated_min": 14, "timeline": xr8720_timeline,
        },
        "proteus": {
            "id": "proteus", "campaign": "ZT Proteus · Samsung PM9A3 Thermal Regression",
            "platform": "ZT Proteus · BMC 0.45 → 0.46 · Samsung PM9A3 (MZQL21T9HCJR-00A07)",
            "source": "Real finding · James Patchett · MTCE Lab · MEAKV-1792",
            "manual_baseline_hrs": 24, "orchestrated_min": 12, "timeline": proteus_timeline,
        },
        "wrcp": {
            "id": "wrcp", "campaign": "WRCP 24.09.301 · Platform / OS Certification",
            "platform": "Wind River Cloud Platform 24.09.301 (vs 2212 baseline) · CAS far-edge",
            "source": "Real campaign · James Patchett · MTCE Lab",
            "manual_baseline_hrs": 80, "orchestrated_min": 30, "timeline": wrcp_timeline,
        },
    }

    sel = CAMPAIGNS.get(campaign, CAMPAIGNS["el140"])
    tl = sel["timeline"]
    correlate_steps = [s for s in tl if s["kind"] == "correlate"]
    action_steps    = [s for s in tl if s["kind"] == "action"]
    gates           = [s for s in tl if s["kind"] == "gate"]
    total_iters     = sum(len(s.get("iterations", [])) for s in tl)

    return {
        "campaign_id": sel["id"],
        "campaign": sel["campaign"],
        "platform": sel["platform"],
        "source": sel["source"],
        "campaigns": [
            {"id": c["id"], "label": c["campaign"], "platform": c["platform"]}
            for c in CAMPAIGNS.values()
        ],
        "agents": AGENT,
        "tiers": TIERS,
        "summary": {
            "total_steps": len(tl),
            "correlate_steps": len(correlate_steps),
            "action_steps": len(action_steps),
            "hitl_gates": len(gates),
            "total_iterations": total_iters,
            "manual_baseline_hrs": sel["manual_baseline_hrs"],
            "orchestrated_min": sel["orchestrated_min"],
        },
        "timeline": tl,
    }


# ═══════════════════════════════════════════════════════════════════════
# EPROD (Enterprise Products Partners) — midstream predictive endpoints
# ═══════════════════════════════════════════════════════════════════════
#
# Four endpoints powering the Apex Signal page in `eprod` demo mode:
#
#   GET /signals/eprod/vendor-drift     → 12-month rate drift per vendor vs
#                                          contracted MSA rate card
#   GET /signals/eprod/tariff-forecast  → FERC tariff index filing prediction
#                                          (PPI-FG-driven) with confidence band
#   GET /signals/eprod/contract-expiry  → contract expiry risk matrix
#                                          (days-to-expiry × risk tier × spend)
#   GET /signals/eprod/signal-feed      → live anomaly ticker across all
#                                          6 EPROD use cases
#
# Data is deterministic (seeded) so the demo is reproducible. Real-model
# backing (SageMaker XGBoost / DeepAR / RCF) is a follow-up — swap behind
# the same response shape.

import hashlib as _hashlib  # noqa: E402 — kept here, not at top, to avoid
                            # accidentally touching the supply-chain region


def _seeded_rand(seed: str, lo: float, hi: float) -> float:
    """Deterministic float in [lo, hi] from a string seed."""
    h = int(_hashlib.sha256(seed.encode()).hexdigest()[:8], 16)
    return lo + (h % 10_000) / 10_000.0 * (hi - lo)


# ──────────────── vendor drift ────────────────

class VendorDriftPoint(BaseModel):
    month:              str
    billed_avg_pct:     float    # avg billed rate as % of MSA base
    contracted_pct:     float    # always 100.0 — the baseline
    variance_pct:       float


class VendorDriftVendor(BaseModel):
    vendor_id:                 str
    vendor_name:               str
    msa_reference:             str
    annual_spend_usd:          float
    trend_pct:                 float           # YoY drift
    trend_status:              str             # drifting_up | drifting_down | stable
    days_to_renewal:           int
    renewal_date:              str
    exposure_at_renewal_usd:   float
    monthly_series:            List[VendorDriftPoint]


class VendorDriftSummary(BaseModel):
    total_vendors_monitored:  int
    drifting_up_count:        int
    drifting_down_count:      int
    stable_count:             int
    next_renewal_days:        int
    total_annual_spend_usd:   float


class VendorDriftResponse(BaseModel):
    summary:  VendorDriftSummary
    vendors:  List[VendorDriftVendor]
    model:    str = "apex-signal-eprod-vendor-drift (XGBoost regression)"


@router.get("/eprod/vendor-drift", response_model=VendorDriftResponse)
async def eprod_vendor_drift() -> VendorDriftResponse:
    """Vendor rate drift over trailing 12 months vs contracted MSA rate card.

    Demo data is deterministic (seeded by vendor_id) so the page is stable
    between refreshes. Surface 5-7 top-spend vendors so the line chart
    stays readable.
    """
    base_vendors = [
        ("HAL",      "Halliburton",            "MSA-HAL-2024-03",       2_400_000,  4.2),
        ("SLB",      "Schlumberger",           "MSA-SLB-2024-08",       3_180_000,  6.1),
        ("BHI",      "Baker Hughes",           "MSA-BHI-2025-01",       1_540_000,  2.3),
        ("KIEWIT",   "Kiewit Construction",    "MSA-KIEWIT-2024-07",   14_700_000,  3.4),
        ("FLUOR",    "Fluor Engineering",      "MSA-FLUOR-2023-11",     8_900_000, -0.8),
        ("BECHTEL",  "Bechtel",                "MSA-BECHTEL-2024-04",   6_200_000,  1.1),
        ("MRC",      "MRC Global",             "MSA-MRC-2025-02",       2_870_000,  5.7),
    ]
    months = [f"2025-{m:02d}" for m in range(6, 13)] + [f"2026-{m:02d}" for m in range(1, 6)]

    vendors: List[VendorDriftVendor] = []
    drifting_up = drifting_down = stable = 0
    min_days = 365

    import math as _math
    for vid, name, msa, spend, seed_trend in base_vendors:
        # Build 12-month series — historical billed % vs MSA. Anchored to
        # `seed_trend` for stable demo chart shape; the SageMaker call below
        # produces the FORWARD-looking projected drift for the chart pill.
        series: List[VendorDriftPoint] = []
        for i, m in enumerate(months):
            target = (seed_trend * (i / max(1, len(months) - 1)))
            noise = (_seeded_rand(f"{vid}-{m}", -0.6, 0.6))
            billed = 100.0 + target + noise
            series.append(VendorDriftPoint(
                month=m, billed_avg_pct=round(billed, 2),
                contracted_pct=100.0, variance_pct=round(billed - 100.0, 2),
            ))

        # Trailing drift % features computed from the synthesized series
        trailing_3mo = round(series[-1].variance_pct - series[-4].variance_pct, 2)
        trailing_6mo = round(series[-1].variance_pct - series[-7].variance_pct, 2)

        # SageMaker prediction — apex-signal-eprod-vendor-drift. If the
        # endpoint is offline we fall back to a heuristic based on trailing
        # drift × 1.4 (see service `default=`).
        pred = _sagemaker.predict_eprod_vendor_drift({
            "trailing_3mo_drift_pct":  trailing_3mo,
            "trailing_6mo_drift_pct":  trailing_6mo,
            "vendor_tenure_months":    int(_seeded_rand(vid + "-tenure", 12, 60)),
            "industry_segment_enc":    float(hash(vid) % 4),
            "msa_renewal_count":       int(_seeded_rand(vid + "-renewals", 1, 4)),
            "total_spend_log":         round(_math.log(max(1.0, spend)), 3),
        })
        trend = pred["projected_drift_pct"]
        status = pred["status"]

        # Renewal date — deterministic per vendor
        days_to_renewal = int(_seeded_rand(vid + "-renewal", 30, 240))
        min_days = min(min_days, days_to_renewal)
        from datetime import datetime as _dt, timedelta as _td
        renewal_date = (_dt(2026, 5, 27) + _td(days=days_to_renewal)).strftime("%Y-%m-%d")

        if status == "drifting_up":   drifting_up += 1
        elif status == "drifting_down": drifting_down += 1
        else:                          stable += 1

        exposure = spend * (trend / 100.0) if trend > 0 else 0.0
        vendors.append(VendorDriftVendor(
            vendor_id=vid, vendor_name=name, msa_reference=msa,
            annual_spend_usd=float(spend), trend_pct=trend, trend_status=status,
            days_to_renewal=days_to_renewal, renewal_date=renewal_date,
            exposure_at_renewal_usd=round(exposure, 0),
            monthly_series=series,
        ))

    # Project-wide totals — synthesised but anchored to the explicit list above
    total_vendors = 247
    others_up   = 21
    others_down = 8
    others_stable = total_vendors - len(vendors) - others_up - others_down
    return VendorDriftResponse(
        summary=VendorDriftSummary(
            total_vendors_monitored=total_vendors,
            drifting_up_count=drifting_up + others_up,
            drifting_down_count=drifting_down + others_down,
            stable_count=stable + others_stable,
            next_renewal_days=min_days,
            total_annual_spend_usd=48_700_000.0,
        ),
        vendors=vendors,
    )


# ──────────────── FERC tariff forecast ────────────────

class TariffRateHistory(BaseModel):
    effective:    str
    rate:         float
    projected:    bool = False


class TariffPipeline(BaseModel):
    tariff_id:                       str
    pipeline:                        str
    docket_no:                       str
    commodity:                       str
    current_rate_per_bbl_100mi:      float
    projected_next_rate:             float
    projected_change_pct:            float
    confidence_lower:                float
    confidence_upper:                float
    next_filing_date:                str
    days_to_next_filing:             int
    ppi_fg_index:                    float
    ppi_fg_yoy_change_pct:           float
    annual_revenue_impact_usd:       float
    rate_history:                    List[TariffRateHistory]


class TariffForecastSummary(BaseModel):
    pipelines_monitored:             int
    next_index_cycle:                str
    days_to_cycle:                   int
    projected_blended_change_pct:    float
    projected_revenue_uplift_usd:    float


class TariffForecastResponse(BaseModel):
    summary:    TariffForecastSummary
    pipelines:  List[TariffPipeline]
    model:      str = "apex-signal-eprod-tariff-forecast (XGBoost regression + PPI-FG ingest)"


@router.get("/eprod/tariff-forecast", response_model=TariffForecastResponse)
async def eprod_tariff_forecast() -> TariffForecastResponse:
    """FERC tariff index filing prediction.

    Uses the PPI-FG index trend (constructively interpolated) to predict the
    next effective rate change for each pipeline. Confidence band reflects
    PPI-FG forecast uncertainty + historical surcharge variability.
    """
    from datetime import datetime as _dt
    today = _dt(2026, 5, 27)
    next_cycle = _dt(2026, 7, 1)
    days_to_cycle = (next_cycle - today).days

    pipelines_data = [
        ("FERC-EPD-NGL-47.12.0",   "Enterprise NGL Pipeline LP",       "OR21-1144-000", "NGL",   0.180,  4.1, 8_400_000),
        ("FERC-EPD-CRUDE-22.4.0",  "Enterprise Crude Pipeline LLC",    "OR21-988-000",  "Crude", 0.214,  3.6, 12_100_000),
        ("FERC-EPD-GAS-31.8.0",    "Acadian Gas Pipeline",             "RP22-451-000",  "Gas",   0.382,  3.2, 6_700_000),
        ("FERC-EPD-NGL-AT-11.2.0", "Enterprise NGL Aransas Pass",      "OR23-77-000",   "NGL",   0.165,  4.3, 4_900_000),
        ("FERC-EPD-CRUDE-SE-8.1.0","Seaway Crude Pipeline",            "OR24-21-000",   "Crude", 0.198,  3.9, 9_300_000),
    ]
    ppi_fg = 132.4
    ppi_yoy = 3.61

    commodity_enc = {"NGL": 0, "Crude": 1, "Gas": 2}
    pipelines: List[TariffPipeline] = []
    total_uplift = 0.0
    for tid, name, docket, commodity, current, seed_change, revenue in pipelines_data:
        prior_year = round(current * 0.965, 4)
        # SageMaker invocation — apex-signal-eprod-tariff-forecast
        pred = _sagemaker.predict_eprod_tariff_forecast({
            "current_rate_per_dth":     current,
            "prior_year_rate":          prior_year,
            "ppi_fg_index":             ppi_fg,
            "ppi_fg_yoy_change_pct":    ppi_yoy,
            "commodity_enc":            float(commodity_enc.get(commodity, 0)),
            "region_enc":               float(hash(tid) % 4),
            "pipeline_tenure_years":    float((hash(docket) % 12) + 4),
            "surcharge_history_avg":    0.003,
        })
        change_pct = pred["projected_change_pct"] if abs(pred["projected_change_pct"]) > 0.1 else seed_change
        projected = round(current * (1 + change_pct / 100.0), 4)
        ci_pct = (1.0 - pred["confidence"]) * 0.02  # smaller CI when model confident
        ci = round(current * max(ci_pct, 0.006), 4)
        impact = revenue * (change_pct / 100.0)
        total_uplift += impact
        pipelines.append(TariffPipeline(
            tariff_id=tid, pipeline=name, docket_no=docket, commodity=commodity,
            current_rate_per_bbl_100mi=current,
            projected_next_rate=projected,
            projected_change_pct=change_pct,
            confidence_lower=round(projected - ci, 4),
            confidence_upper=round(projected + ci, 4),
            next_filing_date="2026-07-01",
            days_to_next_filing=days_to_cycle,
            ppi_fg_index=ppi_fg, ppi_fg_yoy_change_pct=ppi_yoy,
            annual_revenue_impact_usd=round(impact, 0),
            rate_history=[
                TariffRateHistory(effective="2024-07-01", rate=round(current * 0.929, 4)),
                TariffRateHistory(effective="2025-07-01", rate=round(current * 0.965, 4)),
                TariffRateHistory(effective="2026-05-27", rate=current),
                TariffRateHistory(effective="2026-07-01", rate=projected, projected=True),
            ],
        ))

    blended_change = sum(p.projected_change_pct for p in pipelines) / max(1, len(pipelines))
    return TariffForecastResponse(
        summary=TariffForecastSummary(
            pipelines_monitored=14,
            next_index_cycle="2026-07-01",
            days_to_cycle=days_to_cycle,
            projected_blended_change_pct=round(blended_change, 2),
            projected_revenue_uplift_usd=round(total_uplift, 0),
        ),
        pipelines=pipelines,
    )


# ──────────────── contract expiry risk matrix ────────────────

class ContractExpiryRow(BaseModel):
    contract_id:           str
    vendor_name:           str
    contract_type:         str          # MSA | Service Agreement | ROW | Tariff
    days_to_expiry:        int
    expiry_date:           str
    annual_spend_usd:      float
    renewal_initiated:     bool
    complexity:            str          # high | medium | low
    risk_tier:             str          # critical | high | medium | low
    scope_lines:           int


class ContractExpiryMatrixCell(BaseModel):
    critical:           int
    high:               int
    medium:             int
    low:                int
    total_spend_usd:    float


class ContractExpiryMatrix(BaseModel):
    bucket_0_30:    ContractExpiryMatrixCell
    bucket_31_60:   ContractExpiryMatrixCell
    bucket_61_90:   ContractExpiryMatrixCell
    bucket_91_plus: ContractExpiryMatrixCell


class ContractExpirySummary(BaseModel):
    total_active_contracts:    int
    expiring_90_days:          int
    no_renewal_initiated:      int
    total_exposure_usd:        float


class ContractExpiryResponse(BaseModel):
    summary:    ContractExpirySummary
    matrix:     ContractExpiryMatrix
    contracts:  List[ContractExpiryRow]
    model:      str = "apex-signal-eprod-contract-expiry (XGBoost classifier)"


@router.get("/eprod/contract-expiry", response_model=ContractExpiryResponse)
async def eprod_contract_expiry() -> ContractExpiryResponse:
    """Contract expiry heat-map across active MSA / Service Agreement /
    Right-of-Way / Tariff contracts. Scoring by days-to-expiry × spend
    velocity × renewal-complexity drives the risk tier.
    """
    contracts_data = [
        # contract_id, vendor, type, days, spend, renewal_init, complexity, risk, scope_lines
        ("MSA-HAL-2024-03",            "Halliburton",            "MSA",                47,  2_400_000, False, "high",   "critical", 14),
        ("MSA-SLB-2024-08",            "Schlumberger",           "MSA",                28,  3_180_000, False, "high",   "critical", 18),
        ("MSA-BHI-2025-01",            "Baker Hughes",           "MSA",                73,  1_540_000, True,  "medium", "high",      9),
        ("MSA-KIEWIT-2024-07",         "Kiewit Construction",    "MSA",                89, 14_700_000, True,  "high",   "high",     32),
        ("MSA-FLUOR-2023-11",          "Fluor Engineering",      "MSA",                54,  8_900_000, False, "high",   "critical", 21),
        ("MSA-MRC-2025-02",            "MRC Global",             "Service Agreement",  41,  2_870_000, True,  "medium", "high",      8),
        ("MSA-BECHTEL-2024-04",        "Bechtel",                "MSA",               112,  6_200_000, False, "high",   "high",     19),
        ("ROW-LANDOWNER-A1124",        "Multiple landowners",    "Right-of-Way",       19,    870_000, False, "low",    "high",      3),
        ("ROW-LANDOWNER-B2208",        "Multiple landowners",    "Right-of-Way",       55,  1_240_000, True,  "low",    "medium",    4),
        ("FERC-TARIFF-EPD-NGL-47.12",  "Internal (FERC filing)", "Tariff",             35,         0, True,  "medium", "high",     12),
        ("SVC-EMERSON-2024-09",        "Emerson Process",        "Service Agreement", 142,  1_100_000, False, "medium", "medium",    7),
        ("SVC-CHEMTREAT-2025-03",      "ChemTreat",              "Service Agreement",  68,    920_000, True,  "low",    "medium",    5),
    ]
    from datetime import datetime as _dt, timedelta as _td

    contracts: List[ContractExpiryRow] = []
    bucket_cells = {
        "0_30":   {"critical": 0, "high": 0, "medium": 0, "low": 0, "total_spend_usd": 0.0},
        "31_60":  {"critical": 0, "high": 0, "medium": 0, "low": 0, "total_spend_usd": 0.0},
        "61_90":  {"critical": 0, "high": 0, "medium": 0, "low": 0, "total_spend_usd": 0.0},
        "91_plus":{"critical": 0, "high": 0, "medium": 0, "low": 0, "total_spend_usd": 0.0},
    }
    no_renewal = 0
    exposure_total = 0.0
    expiring_90 = 0
    import math as _math
    complexity_enc = {"low": 0, "medium": 1, "high": 2}
    ctype_enc = {"MSA": 0, "Right-of-Way": 1, "Service Agreement": 2, "Tariff": 3}
    today = _dt(2026, 5, 27)
    for cid, vendor, ctype, days, spend, renewal, complexity, risk, scope in contracts_data:
        # SageMaker invocation — apex-signal-eprod-contract-expiry
        pred = _sagemaker.predict_eprod_contract_expiry({
            "days_to_expiry":         float(days),
            "annual_spend_log":       _math.log(max(1.0, spend)) if spend > 0 else 10.0,
            "scope_lines":            float(scope),
            "renewal_initiated_int":  1.0 if renewal else 0.0,
            "complexity_enc":         float(complexity_enc.get(complexity, 1)),
            "contract_type_enc":      float(ctype_enc.get(ctype, 0)),
            "vendor_tenure_years":    float((hash(cid) % 7) + 2),
        })
        risk = pred["risk_tier"]  # override the seed risk with model output
        expiry = (today + _td(days=days)).strftime("%Y-%m-%d")
        contracts.append(ContractExpiryRow(
            contract_id=cid, vendor_name=vendor, contract_type=ctype,
            days_to_expiry=days, expiry_date=expiry,
            annual_spend_usd=float(spend), renewal_initiated=renewal,
            complexity=complexity, risk_tier=risk, scope_lines=scope,
        ))
        bucket = "0_30" if days <= 30 else "31_60" if days <= 60 else "61_90" if days <= 90 else "91_plus"
        bucket_cells[bucket][risk] += 1
        bucket_cells[bucket]["total_spend_usd"] += spend
        if not renewal: no_renewal += 1
        if days <= 90:
            expiring_90 += 1
            exposure_total += spend

    cells = {k: ContractExpiryMatrixCell(**v) for k, v in bucket_cells.items()}
    return ContractExpiryResponse(
        summary=ContractExpirySummary(
            total_active_contracts=312,
            expiring_90_days=expiring_90 + 18,  # plus tail not in displayed list
            no_renewal_initiated=no_renewal + 4,
            total_exposure_usd=round(exposure_total, 0),
        ),
        matrix=ContractExpiryMatrix(
            bucket_0_30=cells["0_30"], bucket_31_60=cells["31_60"],
            bucket_61_90=cells["61_90"], bucket_91_plus=cells["91_plus"],
        ),
        contracts=contracts,
    )


# ──────────────── live signal feed ────────────────

class SignalFeedItem(BaseModel):
    id:           str
    timestamp:    str           # ISO
    use_case:     str           # invoice / po_contract / non_po_msa / quote / tariff / jib
    agent:        str
    severity:     str           # low | medium | high | critical
    title:        str
    detail:       str
    action:       str


class SignalFeedResponse(BaseModel):
    feed:    List[SignalFeedItem]
    counts:  Dict[str, int]


@router.get("/eprod/signal-feed", response_model=SignalFeedResponse)
async def eprod_signal_feed() -> SignalFeedResponse:
    """Live anomaly ticker across all 6 EPROD use cases. Returns the most
    recent ~12 signal detections, ordered newest-first. Page polls every
    8 seconds; new entries appear with a slide-in animation.
    """
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td

    base = _dt(2026, 5, 27, 6, 42, 15, tzinfo=_tz.utc)
    items_raw = [
        # offset_secs, use_case, agent, severity, title, detail, action
        (0,    "tariff",        "TariffAgent",  "high",     "Invoice rate variance · SLB",
         "INV-SLB-2026-05-1129 billed at $0.184/bbl vs FERC effective $0.180/bbl. 2.2% variance.",
         "Flagged for HITL review"),
        (38,   "invoice",       "InvoiceAgent", "medium",   "Duplicate-payment candidate · Halliburton",
         "Invoice INV-HAL-2026-04-3847 line 3 matches a previously-paid line on INV-HAL-2026-03-3719.",
         "Holding for AP analyst review"),
        (94,   "po_contract",   "POAgent",      "high",     "PO outside MSA scope · Kiewit",
         "PO-2026-EPC-4521 line 6 covers welding services not in MSA-KIEWIT-2024-07 Schedule B.",
         "Returned to procurement"),
        (182,  "non_po_msa",    "VendorAgent",  "low",      "Non-PO MSA match confirmed · ChemTreat",
         "Non-PO transaction $42,500 matched to MSA-CHEMTREAT-2025-03 scope item 3. Approval routed.",
         "Auto-approved within authority"),
        (267,  "jib",           "JIBAgent",     "critical", "JIB charge exceeds AFE · P66 Sweeny",
         "Phillips 66 JIB Apr-2026 line 14 ($2.1M) exceeds AFE-SWEENY-2024-12 remaining balance ($1.7M).",
         "Routed to JV partner reconciliation queue"),
        (345,  "quote",         "QuoteAgent",   "medium",   "Quote variance vs historical · Fluor",
         "QUOTE-FLUOR-2026-Q2-0142 unit cost 12% above 12-month vendor average for engineering hours.",
         "Comparative report attached"),
        (412,  "tariff",        "TariffAgent",  "low",      "FERC index pre-cycle alert · NGL pipeline",
         "PPI-FG index trending +3.6% YoY. Projected July-1 effective rate $0.187/bbl/100mi.",
         "Procurement notified · 35 days lead"),
        (478,  "invoice",       "InvoiceAgent", "medium",   "Tax-code mismatch · Baker Hughes",
         "INV-BHI-2026-05-0921 applied 8.25% TX state tax to interstate-exempt freight line 4.",
         "Tax adjustment proposed"),
        (561,  "jib",           "JIBAgent",     "medium",   "JIB working-interest math drift · Targa",
         "JIB-TARGA-MONT-BELVIEU-2026-03 partner share 39.92% — JV agreement specifies 40.00%.",
         "Variance memo logged"),
        (623,  "po_contract",   "POAgent",      "low",      "PO-Contract rate match · MRC Global",
         "PO-2026-CHEM-0892 all 6 line items match MSA-MRC-2025-02 Schedule A within tolerance.",
         "Routed to standard approval"),
        (705,  "non_po_msa",    "VendorAgent",  "high",     "No active MSA · transaction held",
         "Non-PO submission $187,000 to vendor 'PIPETECH SVCS LLC' — no active MSA on file.",
         "Returned to requestor · MSA required"),
        (782,  "quote",         "QuoteAgent",   "low",      "Quote indexed · Bechtel",
         "QUOTE-BECHTEL-2026-Q1-0089 extracted · 4 milestones · references RFP-EPD-2025-EXP-009.",
         "Cataloged for PO-issuance workflow"),
    ]
    feed: List[SignalFeedItem] = []
    counts: Dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for i, (off, uc, agent, sev, title, detail, action) in enumerate(items_raw):
        ts = (base - _td(seconds=off)).isoformat().replace("+00:00", "Z")
        feed.append(SignalFeedItem(
            id=f"SIG-2026-0527-{i+1:03d}",
            timestamp=ts, use_case=uc, agent=agent, severity=sev,
            title=title, detail=detail, action=action,
        ))
        counts[sev] = counts.get(sev, 0) + 1

    return SignalFeedResponse(feed=feed, counts=counts)
