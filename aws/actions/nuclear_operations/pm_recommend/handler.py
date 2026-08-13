"""
pm_recommend — suggest a PM advance based on detected anomaly + catalog mitigation.

Combines seed_anomalies (which encodes the demo's recommended PM advance)
with the failure mode catalog so the recommendation includes concrete
mitigation steps. Returns the natural-language recommendation string the
ReliabilityAgent quotes.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_seed_anomalies, load_failure_mode_catalog, load_pm_schedule,
    missing_data_envelope, index_by,
)


@apex_action(ApexActionSchema(
    name="pm_recommend",
    description="Recommend a PM advance / new action for an equipment item based on detected anomalies and historical patterns.",
    category="recommendation",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="PM recommendation request")
        .add_string("equipment_id", "Equipment id, e.g. P-3A", required=True),
    output_schema=ActionOutputSchema(description="PM recommendation envelope")
        .add_string("status", "ok | error")
        .add_string("recommendation", "Natural-language summary, e.g. 'Advance PM-7B from Day 22 to Day 5'")
        .add_string("recommended_pm_template", "PM template id")
        .add_string("current_next_due", "Currently scheduled next-due date")
        .add_string("recommended_new_due", "Recommended new due date")
        .add_string("urgency", "routine | elevated | urgent | critical")
        .add_string("estimated_avoidance", "{downtime_hours, cost_usd}")
        .add_string("mitigation_steps", "List of recommended mitigation strings"),
))
def pm_recommend(equipment_id: str) -> dict:
    """Return a PM-advance recommendation for `equipment_id`."""
    if not equipment_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "equipment_id is required"}

    anomalies = load_seed_anomalies()
    if anomalies is None:
        return missing_data_envelope("seed_anomalies.json")

    catalog = load_failure_mode_catalog() or []
    cat_idx = index_by(catalog, "mode_id")
    pmap = index_by(load_pm_schedule() or [], "equipment_id")

    eq_anomaly = next((a for a in anomalies if a.get("equipment_id") == equipment_id), None)
    pm_row = pmap.get(equipment_id, {})
    today = datetime.now(timezone.utc).date()

    if not eq_anomaly:
        # Routine recommendation — keep current schedule
        return {
            "status": "ok",
            "equipment_id": equipment_id,
            "recommendation": (
                f"No anomaly detected on {equipment_id} in current window. "
                f"Continue with scheduled {pm_row.get('pm_template_name', 'PM')} on "
                f"{pm_row.get('next_due', 'next due date')}."
            ),
            "recommended_pm_template": pm_row.get("pm_template_id"),
            "current_next_due": pm_row.get("next_due"),
            "recommended_new_due": pm_row.get("next_due"),
            "urgency": "routine",
            "estimated_avoidance": {"downtime_hours": 0, "cost_usd": 0},
            "mitigation_steps": [],
        }

    # Use the anomaly's recommended advance
    z = float(eq_anomaly.get("z_score", 0))
    if z >= 3.5:
        urgency = "critical"
    elif z >= 3.0:
        urgency = "urgent"
    elif z >= 2.0:
        urgency = "elevated"
    else:
        urgency = "routine"

    mode_id = eq_anomaly.get("expected_failure_mode")
    mode_data = cat_idx.get(mode_id, {})
    mitigation = mode_data.get("mitigation_actions", [])

    current_offset = int(eq_anomaly.get("current_next_due_offset_days", 30))
    new_offset = int(eq_anomaly.get("recommended_new_offset_days", 7))
    current_due = (today + timedelta(days=current_offset)).isoformat()
    new_due = (today + timedelta(days=new_offset)).isoformat()

    pm_template = eq_anomaly.get("recommended_pm") or pm_row.get("pm_template_id", "PM-?")
    recommendation = (
        f"Advance {pm_template} on {equipment_id} from Day {current_offset} ({current_due}) "
        f"to Day {new_offset} ({new_due}). "
        f"Trigger: {eq_anomaly.get('trend', 'sensor anomaly detected')}."
    )

    return {
        "status": "ok",
        "equipment_id": equipment_id,
        "recommendation": recommendation,
        "recommended_pm_template": pm_template,
        "current_next_due": current_due,
        "recommended_new_due": new_due,
        "urgency": urgency,
        "estimated_avoidance": {
            "downtime_hours": int(eq_anomaly.get("estimated_avoidance_hours", 0)),
            "cost_usd": int(eq_anomaly.get("estimated_avoidance_usd", 0)),
        },
        "mitigation_steps": mitigation,
        "based_on_anomaly": eq_anomaly.get("anomaly_id"),
        "scripted_message": eq_anomaly.get("scripted_message"),
    }


def handler(event, context=None):
    return pm_recommend(equipment_id=event.get("equipment_id", ""))
