"""
risk_score_compute — composite risk score (0-100) for an equipment item.

Inputs combine:
  • Active anomalies (from seed_anomalies)
  • Historical failure count (from failure_events)
  • Days since last preventive (from work_orders)
  • Equipment criticality class (from equipment.json)

Each contributes a weighted component; sum is clamped to [0, 100] and
mapped to a 4-tier label (low / moderate / high / critical).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_seed_anomalies, load_failure_events, load_work_orders, load_equipment,
    missing_data_envelope, parse_date, index_by,
)


def _tier_for_score(score: int) -> str:
    """Risk tier from composite 0-100 score.

    Threshold tuning rationale (locked for STP demo):
      • score >= 70 → critical : Q-class asset with active high-z anomaly
                                  + historical failures hits this band.
      • score >= 50 → high     : significant deviation but recoverable.
      • score >= 25 → moderate : worth watching, not yet urgent.
      • else        → low      : nominal.
    """
    if score >= 70:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "moderate"
    return "low"


@apex_action(ApexActionSchema(
    name="risk_score_compute",
    description="Compute a composite 0-100 risk score for an equipment item from anomalies, failure history, PM gap, and criticality class.",
    category="analytics",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Risk score request")
        .add_string("equipment_id", "Equipment id, e.g. P-3A", required=True),
    output_schema=ActionOutputSchema(description="Risk score envelope")
        .add_string("status", "ok | error")
        .add_number("risk_score", "Composite 0-100")
        .add_string("risk_tier", "low | moderate | high | critical")
        .add_string("contributing_factors", "List of {factor, weight, value, contribution}")
        .add_number("historical_failure_count", "Lifetime failure events for this asset")
        .add_number("days_since_last_pm", "Whole days since last preventive WO closed")
        .add_string("criticality_class", "Q | A | B | C"),
))
def risk_score_compute(equipment_id: str) -> dict:
    """Compute the composite risk score for `equipment_id`."""
    if not equipment_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "equipment_id is required"}

    anomalies = load_seed_anomalies()
    if anomalies is None:
        return missing_data_envelope("seed_anomalies.json")
    failure_events = load_failure_events() or []
    work_orders = load_work_orders() or []
    equipment = load_equipment() or []

    eq_idx = index_by(equipment, "equipment_id")
    eq_row = eq_idx.get(equipment_id, {})

    # ── Component 1: anomaly severity (0-50 of 100) ───────────────────────
    eq_anomaly = next((a for a in anomalies if a.get("equipment_id") == equipment_id), None)
    z = float(eq_anomaly.get("z_score", 0)) if eq_anomaly else 0.0
    anomaly_contrib = min(50, int(z * 12.5))

    # ── Component 2: historical failure count (0-25) ──────────────────────
    hist_count = sum(1 for ev in failure_events if ev.get("equipment_id") == equipment_id)
    hist_contrib = min(25, hist_count * 5)

    # ── Component 3: days since last PM (0-15) ────────────────────────────
    pms = [w for w in work_orders
           if w.get("equipment_id") == equipment_id
           and w.get("type") in ("preventive", "surveillance")
           and w.get("status") == "closed"
           and w.get("closed")]
    days_since = 999
    if pms:
        pms.sort(key=lambda w: parse_date(w.get("closed")) or datetime.min, reverse=True)
        last = parse_date(pms[0].get("closed"))
        if last:
            days_since = (datetime.now(timezone.utc).replace(tzinfo=None) - last).days
    pm_gap_contrib = min(15, max(0, (days_since - 90) // 30))

    # ── Component 4: criticality class (0-10) ─────────────────────────────
    crit_map = {"Q": 10, "A": 7, "B": 4, "C": 2}
    crit_contrib = crit_map.get(eq_row.get("criticality"), 0)

    score = min(100, anomaly_contrib + hist_contrib + pm_gap_contrib + crit_contrib)
    tier = _tier_for_score(score)

    factors = [
        {"factor": "active_anomaly", "weight": 50, "value": z, "contribution": anomaly_contrib},
        {"factor": "historical_failures", "weight": 25, "value": hist_count, "contribution": hist_contrib},
        {"factor": "days_since_last_pm", "weight": 15, "value": days_since, "contribution": pm_gap_contrib},
        {"factor": "criticality_class", "weight": 10, "value": eq_row.get("criticality", "unknown"),
         "contribution": crit_contrib},
    ]

    return {
        "status": "ok",
        "equipment_id": equipment_id,
        "risk_score": score,
        "risk_tier": tier,
        "contributing_factors": factors,
        "historical_failure_count": hist_count,
        "days_since_last_pm": days_since,
        "criticality_class": eq_row.get("criticality", "unknown"),
        "active_anomaly": eq_anomaly.get("anomaly_id") if eq_anomaly else None,
    }


def handler(event, context=None):
    return risk_score_compute(equipment_id=event.get("equipment_id", ""))
