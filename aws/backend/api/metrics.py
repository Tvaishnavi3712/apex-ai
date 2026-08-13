"""
Metrics API — aggregate operational stats for the Command Center dashboard.

The `summary` endpoint rolls up work items + agents into the six KPIs shown
on the Command Center page. All metrics are computed on the fly from the
existing DynamoDB tables; no separate metrics store.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from services.dynamodb import DynamoDBService
from core.config import settings

router = APIRouter()
work_items_db = DynamoDBService(settings.DYNAMODB_WORK_ITEMS)
agents_db = DynamoDBService(settings.DYNAMODB_AGENTS)
review_decisions_db = DynamoDBService(settings.DYNAMODB_REVIEW_DECISIONS)
sessions_db = DynamoDBService(settings.DYNAMODB_SESSIONS)

# Pricing assumption (USD per processed document).
# Used as the multiplier for avg_cost_per_doc until real cost attribution is wired.
_DEFAULT_COST_PER_DOC = 1.42


def _parse_dt(value: Any) -> Optional[datetime]:
    """Best-effort ISO-8601 parser that always returns a tz-aware UTC datetime."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        s = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _avg_confidence(item: Dict[str, Any]) -> Optional[float]:
    result = item.get("result") or {}
    scores = result.get("confidence_scores") or {}
    if not scores:
        return None
    try:
        vals = [float(v) for v in scores.values() if v is not None]
        return sum(vals) / len(vals) if vals else None
    except Exception:
        return None


def _latency_seconds(item: Dict[str, Any]) -> Optional[float]:
    started = _parse_dt(item.get("started_at"))
    completed = _parse_dt(item.get("completed_at"))
    if not started or not completed:
        return None
    return max(0.0, (completed - started).total_seconds())


def _percentile(values: List[float], p: float) -> Optional[float]:
    """Linear-interpolation percentile. p in [0,1]."""
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    idx = p * (len(values) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(values) - 1)
    frac = idx - lo
    return values[lo] + (values[hi] - values[lo]) * frac


class DecisionBreakdown(BaseModel):
    auto_approved: int = 0
    routed_for_approval: int = 0
    human_review: int = 0
    rejected_or_failed: int = 0


class AgentPerformance(BaseModel):
    agent_id: str
    name: str
    accuracy: Optional[float] = None
    docs_today: int = 0


class MetricsSummary(BaseModel):
    docs_today: int = 0
    docs_today_delta_pct: Optional[float] = None

    accuracy: Optional[float] = Field(None, description="Average confidence (0..1) across items with scores")
    accuracy_delta_pct: Optional[float] = None

    avg_cost_per_doc: float = _DEFAULT_COST_PER_DOC
    avg_cost_delta_pct: Optional[float] = None

    p95_latency_seconds: Optional[float] = None
    p95_latency_delta_seconds: Optional[float] = None

    active_agents: int = 0

    throughput_by_hour: List[int] = Field(default_factory=list, description="24 counts, one per hour, oldest first")
    decisions: DecisionBreakdown = Field(default_factory=DecisionBreakdown)
    agent_performance: List[AgentPerformance] = Field(default_factory=list)


def _bucket_hour(items: List[Dict[str, Any]], now: datetime) -> List[int]:
    """24-hour histogram: bucket[0] is 24h ago, bucket[23] is the current hour."""
    buckets = [0] * 24
    for it in items:
        dt = _parse_dt(it.get("completed_at") or it.get("created_at"))
        if not dt:
            continue
        hours_ago = int((now - dt).total_seconds() // 3600)
        if 0 <= hours_ago < 24:
            buckets[23 - hours_ago] += 1
    return buckets


@router.get("/summary", response_model=MetricsSummary)
async def metrics_summary(
    window_hours: int = Query(24, ge=1, le=168),
    cost_per_doc: float = Query(_DEFAULT_COST_PER_DOC, ge=0.0),
):
    """
    Aggregate summary KPIs for the Command Center.

    All numbers are derived from work_items over the last `window_hours`.
    Returns zeros when there is no data so the frontend can render without
    special-case handling.
    """
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=window_hours)
    prev_window_start = window_start - timedelta(hours=window_hours)

    # One scan is enough for small/medium volumes; paginated scan can be added later.
    all_items: List[Dict[str, Any]] = await work_items_db.scan(limit=500)

    current: List[Dict[str, Any]] = []
    previous: List[Dict[str, Any]] = []
    for it in all_items:
        dt = _parse_dt(it.get("completed_at") or it.get("created_at"))
        if not dt:
            continue
        if dt >= window_start:
            current.append(it)
        elif dt >= prev_window_start:
            previous.append(it)

    # --- docs ---
    docs_today = len(current)
    docs_prev = len(previous)
    docs_delta_pct = ((docs_today - docs_prev) / docs_prev * 100.0) if docs_prev else None

    # --- accuracy (avg confidence) ---
    cur_conf = [c for c in (_avg_confidence(i) for i in current) if c is not None]
    prev_conf = [c for c in (_avg_confidence(i) for i in previous) if c is not None]
    accuracy = sum(cur_conf) / len(cur_conf) if cur_conf else None
    prev_accuracy = sum(prev_conf) / len(prev_conf) if prev_conf else None
    accuracy_delta_pct = (
        (accuracy - prev_accuracy) * 100.0 if accuracy is not None and prev_accuracy is not None else None
    )

    # --- latency ---
    cur_lat = [l for l in (_latency_seconds(i) for i in current) if l is not None]
    prev_lat = [l for l in (_latency_seconds(i) for i in previous) if l is not None]
    p95 = _percentile(cur_lat, 0.95)
    p95_prev = _percentile(prev_lat, 0.95)
    p95_delta = (p95 - p95_prev) if (p95 is not None and p95_prev is not None) else None

    # --- cost ---
    avg_cost = cost_per_doc
    prev_cost = cost_per_doc  # constant for now — swap when real cost attribution lands
    cost_delta_pct = ((avg_cost - prev_cost) / prev_cost * 100.0) if prev_cost else None

    # --- decisions (status breakdown over window) ---
    decisions = DecisionBreakdown()
    for it in current:
        st = (it.get("status") or "").lower()
        if st == "completed":
            decisions.auto_approved += 1
        elif st == "needs_review":
            decisions.human_review += 1
        elif st in ("pending", "executing"):
            decisions.routed_for_approval += 1
        elif st in ("failed", "cancelled"):
            decisions.rejected_or_failed += 1

    # --- throughput histogram ---
    throughput = _bucket_hour(current, now)

    # --- agents: count active + per-agent stats ---
    all_agents = await agents_db.scan(limit=200)
    active_agents = sum(1 for a in all_agents if (a.get("status") or "").lower() == "active")

    per_agent: Dict[str, Dict[str, Any]] = {}
    for it in current:
        agent_id = it.get("agent_id") or it.get("processed_by") or ""
        if not agent_id:
            continue
        bucket = per_agent.setdefault(agent_id, {"count": 0, "conf": []})
        bucket["count"] += 1
        c = _avg_confidence(it)
        if c is not None:
            bucket["conf"].append(c)

    name_by_id = {a.get("agent_id"): a.get("name", a.get("agent_id", "")) for a in all_agents}
    agent_perf: List[AgentPerformance] = []
    for agent_id, bucket in per_agent.items():
        accuracy_ag = sum(bucket["conf"]) / len(bucket["conf"]) if bucket["conf"] else None
        agent_perf.append(AgentPerformance(
            agent_id=agent_id,
            name=name_by_id.get(agent_id, agent_id),
            accuracy=accuracy_ag,
            docs_today=bucket["count"],
        ))
    agent_perf.sort(key=lambda a: a.docs_today, reverse=True)

    return MetricsSummary(
        docs_today=docs_today,
        docs_today_delta_pct=docs_delta_pct,
        accuracy=accuracy,
        accuracy_delta_pct=accuracy_delta_pct,
        avg_cost_per_doc=avg_cost,
        avg_cost_delta_pct=cost_delta_pct,
        p95_latency_seconds=p95,
        p95_latency_delta_seconds=p95_delta,
        active_agents=active_agents,
        throughput_by_hour=throughput,
        decisions=decisions,
        agent_performance=agent_perf[:8],
    )


# ════════════════════════════════════════════════════════════════════════════
# Killer Feature 1 — Executive ROI metrics (Value Generated · Hours Repurposed · COI)
# ════════════════════════════════════════════════════════════════════════════

class ExecutiveKpi(BaseModel):
    value_generated_usd:          float            = 0.0
    value_generated_per_sec_usd:  float            = 0.0    # live-ticker rate (avg over last 60s of data)
    hours_repurposed:             float            = 0.0
    hours_repurposed_delta_pct:   Optional[float]  = None   # vs previous equal window
    cost_of_inaction_usd:         float            = 0.0
    coi_delta_pct:                Optional[float]  = None
    window_hours:                 int              = 24


def _item_value_usd(item: Dict[str, Any]) -> float:
    """Pull the work-item's business value (revenue protected / processed)."""
    for key in ("value_usd", "revenue_usd", "exposure_usd"):
        v = item.get(key)
        if v is None:
            continue
        try:
            return float(v)
        except Exception:
            pass
    # Fallback: check nested result.payload.value_usd
    result = item.get("result") or {}
    payload = result.get("payload") or {}
    try:
        return float(payload.get("value_usd") or 0.0)
    except Exception:
        return 0.0


def _item_manual_hours_saved(item: Dict[str, Any]) -> float:
    """Hours of manual work the agent displaced. Falls back to 0.5h per completed item."""
    for key in ("manual_hours_saved", "hours_saved"):
        v = item.get(key)
        if v is None:
            continue
        try:
            return float(v)
        except Exception:
            pass
    return 0.5 if (item.get("status") or "").lower() == "completed" else 0.0


def _item_avoided_loss_usd(item: Dict[str, Any]) -> float:
    """COI contribution — exposure that would have been realised without the agent."""
    for key in ("avoided_loss_usd", "exposure_usd", "value_at_risk_usd"):
        v = item.get(key)
        if v is None:
            continue
        try:
            return float(v)
        except Exception:
            pass
    return 0.0


@router.get("/executive", response_model=ExecutiveKpi)
async def metrics_executive(window_hours: int = Query(24, ge=1, le=168 * 13)):
    """Killer Feature 1 — ROI Command Center.

    Aggregates from the work_items table:
      • value_generated_usd  = Σ value_usd for items in window
      • hours_repurposed     = Σ manual_hours_saved for items in window
      • cost_of_inaction_usd = Σ avoided_loss_usd over the LAST QUARTER (90d),
        not just the window — this is a board-level quarterly number.

    Deltas are computed against the immediately preceding equal-length window.
    """
    now = datetime.now(timezone.utc)
    win_start     = now - timedelta(hours=window_hours)
    prev_start    = win_start - timedelta(hours=window_hours)
    quarter_start = now - timedelta(days=90)

    items = await work_items_db.scan(limit=5000)

    cur_val = 0.0
    cur_hours = 0.0
    cur_recent_val = 0.0  # last 60s for ticker rate
    prev_val = 0.0
    prev_hours = 0.0
    quarter_coi = 0.0
    prev_quarter_coi = 0.0

    ticker_cutoff = now - timedelta(seconds=60)
    prev_quarter_start = quarter_start - timedelta(days=90)

    for it in items:
        dt = _parse_dt(it.get("completed_at") or it.get("created_at"))
        if not dt:
            continue
        v = _item_value_usd(it)
        h = _item_manual_hours_saved(it)
        a = _item_avoided_loss_usd(it)

        if dt >= win_start:
            cur_val   += v
            cur_hours += h
            if dt >= ticker_cutoff:
                cur_recent_val += v
        elif dt >= prev_start:
            prev_val   += v
            prev_hours += h

        if dt >= quarter_start:
            quarter_coi += a
        elif dt >= prev_quarter_start:
            prev_quarter_coi += a

    hours_delta = ((cur_hours - prev_hours) / prev_hours * 100.0) if prev_hours else None
    coi_delta   = ((quarter_coi - prev_quarter_coi) / prev_quarter_coi * 100.0) if prev_quarter_coi else None
    ticker_rate = cur_recent_val / 60.0 if cur_recent_val else 0.0

    return ExecutiveKpi(
        value_generated_usd=round(cur_val, 2),
        value_generated_per_sec_usd=round(ticker_rate, 4),
        hours_repurposed=round(cur_hours, 1),
        hours_repurposed_delta_pct=hours_delta,
        cost_of_inaction_usd=round(quarter_coi, 2),
        coi_delta_pct=coi_delta,
        window_hours=window_hours,
    )


# ════════════════════════════════════════════════════════════════════════════
# Killer Feature 5 — Workforce Intelligence (human × agent collaboration)
# ════════════════════════════════════════════════════════════════════════════

class WeeklyPoint(BaseModel):
    week: str                 # ISO week label, e.g. "W32"
    value: float


class MonthlyShift(BaseModel):
    month: str                # YYYY-MM
    strategic_pct: float
    manual_pct: float


class WorkforceReport(BaseModel):
    cognitive_offload:     List[WeeklyPoint]   = Field(default_factory=list)
    hitl_velocity_minutes: List[WeeklyPoint]   = Field(default_factory=list)
    skill_shift:           List[MonthlyShift]  = Field(default_factory=list)


def _iso_week_label(dt: datetime) -> str:
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"


@router.get("/workforce", response_model=WorkforceReport)
async def metrics_workforce(weeks: int = Query(8, ge=1, le=52)):
    """Killer Feature 5 — Workforce Intelligence.

    Computes three trends from live data (no mock values):
      • cognitive_offload     — # of work_items with status in (completed, auto_approved)
                                per ISO week, oldest→newest
      • hitl_velocity_minutes — avg minutes from review_decision.created_at -
                                source work_item completed_at, per ISO week
      • skill_shift           — monthly ratio of strategic (=reviews + approvals)
                                vs manual (=pending|needs_review created)
                                across the last 4 calendar months
    """
    now = datetime.now(timezone.utc)
    weeks_start = now - timedelta(weeks=weeks)

    items = await work_items_db.scan(limit=5000)
    decisions = await review_decisions_db.scan(limit=5000)

    # --- cognitive_offload ---
    offload_buckets: Dict[str, int] = {}
    for it in items:
        dt = _parse_dt(it.get("completed_at") or it.get("created_at"))
        if not dt or dt < weeks_start:
            continue
        status = (it.get("status") or "").lower()
        if status in ("completed", "auto_approved", "auto_clear"):
            label = _iso_week_label(dt)
            offload_buckets[label] = offload_buckets.get(label, 0) + 1

    # --- hitl_velocity_minutes ---
    items_by_id = {it.get("work_item_id") or it.get("id"): it for it in items}
    latency_by_week: Dict[str, List[float]] = {}
    for d in decisions:
        decided = _parse_dt(d.get("decided_at") or d.get("created_at"))
        if not decided or decided < weeks_start:
            continue
        wid = d.get("work_item_id")
        src = items_by_id.get(wid) if wid else None
        ready_at = _parse_dt(src.get("completed_at") or src.get("created_at")) if src else None
        if not ready_at:
            continue
        minutes = max(0.0, (decided - ready_at).total_seconds() / 60.0)
        label = _iso_week_label(decided)
        latency_by_week.setdefault(label, []).append(minutes)

    # --- skill_shift (4 months) ---
    from calendar import month_abbr  # noqa: local helper only
    month_buckets: Dict[str, Dict[str, int]] = {}
    since = now - timedelta(days=120)
    for it in items:
        dt = _parse_dt(it.get("created_at") or it.get("completed_at"))
        if not dt or dt < since:
            continue
        m_label = dt.strftime("%Y-%m")
        b = month_buckets.setdefault(m_label, {"strategic": 0, "manual": 0})
        status = (it.get("status") or "").lower()
        if status in ("needs_review", "pending", "executing"):
            b["manual"] += 1
        else:
            b["strategic"] += 1
    for d in decisions:
        decided = _parse_dt(d.get("decided_at") or d.get("created_at"))
        if not decided or decided < since:
            continue
        m_label = decided.strftime("%Y-%m")
        b = month_buckets.setdefault(m_label, {"strategic": 0, "manual": 0})
        b["strategic"] += 1

    # Format outputs: sorted by week/month ascending, normalised as floats.
    cog = [WeeklyPoint(week=k, value=float(v)) for k, v in sorted(offload_buckets.items())]
    hitl = [
        WeeklyPoint(week=k, value=round(sum(v) / len(v), 1))
        for k, v in sorted(latency_by_week.items()) if v
    ]
    shift: List[MonthlyShift] = []
    for m_label in sorted(month_buckets.keys()):
        b = month_buckets[m_label]
        total = max(1, b["strategic"] + b["manual"])
        strat = round(b["strategic"] / total * 100.0, 1)
        shift.append(MonthlyShift(
            month=m_label,
            strategic_pct=strat,
            manual_pct=round(100.0 - strat, 1),
        ))

    return WorkforceReport(
        cognitive_offload=cog,
        hitl_velocity_minutes=hitl,
        skill_shift=shift[-4:],  # last 4 months max
    )
