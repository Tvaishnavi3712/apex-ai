"""
engineer_attribution — given a work-order ID, return the responsible engineers.

Joins work_orders.json + personnel.json + change_history.json so the
MaintenanceAgent can answer "who worked on it?" with names + roles + hours,
plus identify the lead engineer separately from technicians.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_work_orders, load_personnel, load_change_history,
    missing_data_envelope, not_found_envelope, index_by,
)


@apex_action(ApexActionSchema(
    name="engineer_attribution",
    description="Return technicians, lead engineer and total hours charged to a given work order.",
    category="data_lookup",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Work-order attribution lookup")
        .add_string("wo_id", "Work order id, e.g. WO-2026-00871", required=True),
    output_schema=ActionOutputSchema(description="Engineer attribution envelope")
        .add_string("status", "ok | error | not_found")
        .add_string("wo_id", "Work order id")
        .add_string("equipment_id", "Equipment the WO targeted")
        .add_string("technicians", "List of {employee_id, name, role, hours_charged}")
        .add_string("lead_engineer", "Lead engineer record")
        .add_string("lead_planner", "Planner / scheduler if available")
        .add_number("total_hours", "Total hours charged to WO")
        .add_number("change_event_count", "Number of change_history events for this WO"),
))
def engineer_attribution(wo_id: str) -> dict:
    """Resolve technicians, lead engineer, and hour distribution for `wo_id`."""
    if not wo_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "wo_id is required"}

    work_orders = load_work_orders()
    if work_orders is None:
        return missing_data_envelope("work_orders.json")
    personnel = load_personnel()
    if personnel is None:
        return missing_data_envelope("personnel.json")

    wo: Optional[Dict[str, Any]] = next((w for w in work_orders if w.get("wo_id") == wo_id), None)
    if wo is None:
        return not_found_envelope("work_order", wo_id)

    pmap = index_by(personnel, "employee_id")

    def _attribute(emp_id: str, hours: float = 0.0) -> Dict[str, Any]:
        p = pmap.get(emp_id, {})
        return {
            "employee_id": emp_id,
            "name": p.get("name", emp_id),
            "role": p.get("role", "unknown"),
            "hours_charged": round(hours, 1),
        }

    tech_ids = wo.get("technician_ids", []) or []
    total_hours = float(wo.get("hours_charged", 0) or 0)
    # Distribute hours evenly across technicians (real Oracle would have per-tech)
    per_tech = round(total_hours / max(1, len(tech_ids)), 1) if tech_ids else 0.0
    technicians = [_attribute(eid, per_tech) for eid in tech_ids]

    lead = None
    if wo.get("lead_engineer_id"):
        lead = _attribute(wo["lead_engineer_id"], 0.0)

    # Count change-history events for this WO
    history = load_change_history() or []
    change_count = sum(1 for h in history if h.get("wo_id") == wo_id)

    return {
        "status": "ok",
        "wo_id": wo_id,
        "equipment_id": wo.get("equipment_id"),
        "type": wo.get("type"),
        "opened": wo.get("opened"),
        "closed": wo.get("closed"),
        "technicians": technicians,
        "lead_engineer": lead,
        "lead_planner": None,
        "total_hours": total_hours,
        "narrative": wo.get("narrative"),
        "change_event_count": change_count,
    }


def handler(event, context=None):
    return engineer_attribution(wo_id=event.get("wo_id", ""))
