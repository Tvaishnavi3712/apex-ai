"""
oracle_pm_lookup — query the Oracle PM history for an equipment item.

Powers MaintenanceAgent's "When was the last PM on Pump-3A?" answer. Joins
work_orders.json (filtered by equipment_id + type='preventive') with
personnel.json to attribute technicians, plus pm_schedule.json to surface
the next-due date.

The Oracle DB lookup is simulated against the synthetic JSON corpus, but
the response shape is identical to what a production handler hitting a
real Oracle stored procedure would return.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_work_orders, load_personnel, load_pm_schedule,
    missing_data_envelope, not_found_envelope, parse_date, index_by, within_window,
)


@apex_action(ApexActionSchema(
    name="oracle_pm_lookup",
    description="Query Oracle PMHISTORY for last completed PM on a given equipment_id, plus recent corrective history and next-due date.",
    category="data_lookup",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="PM history lookup")
        .add_string("equipment_id", "Equipment id, e.g. P-3A", required=True)
        .add_number("lookback_days", "Window in days for recent_history (default 365)", required=False),
    output_schema=ActionOutputSchema(description="PM history envelope")
        .add_string("status", "ok | error | not_found")
        .add_string("last_pm_date", "ISO date of last completed PM")
        .add_string("last_pm_wo_id", "WO id of last PM")
        .add_string("last_pm_type", "PM type (preventive/surveillance)")
        .add_string("last_pm_technicians", "List of {employee_id, name, role}")
        .add_string("next_pm_due", "Next PM due date")
        .add_string("pm_template_id", "PM template applied")
        .add_string("regulatory_basis", "TS / SR citation")
        .add_number("total_pms_in_window", "Count of PMs in lookback window")
        .add_string("recent_history", "List of recent {wo_id, opened, type, status} rows"),
))
def oracle_pm_lookup(equipment_id: str, lookback_days: int = 365) -> dict:
    """Retrieve the most recent PM and recent corrective history for `equipment_id`."""
    if not equipment_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "equipment_id is required"}

    work_orders = load_work_orders()
    if work_orders is None:
        return missing_data_envelope("work_orders.json")
    personnel = load_personnel()
    if personnel is None:
        return missing_data_envelope("personnel.json")

    pm_schedule = load_pm_schedule() or []
    pmap = index_by(pm_schedule, "equipment_id")
    pmap_row = pmap.get(equipment_id, {})

    eq_wos = [w for w in work_orders if w.get("equipment_id") == equipment_id]
    if not eq_wos:
        return not_found_envelope("equipment_history", equipment_id)

    pm_wos = [w for w in eq_wos
              if w.get("type") in ("preventive", "surveillance")
              and w.get("status") == "closed"
              and w.get("closed")]
    pm_wos.sort(key=lambda w: parse_date(w.get("closed")) or datetime.min, reverse=True)

    if not pm_wos:
        return {
            "status": "ok",
            "last_pm_date": None,
            "last_pm_wo_id": None,
            "last_pm_type": None,
            "last_pm_technicians": [],
            "next_pm_due": pmap_row.get("next_due"),
            "pm_template_id": pmap_row.get("pm_template_id"),
            "regulatory_basis": pmap_row.get("regulatory_basis"),
            "total_pms_in_window": 0,
            "recent_history": [],
            "message": f"No completed PMs found for {equipment_id}",
        }

    latest = pm_wos[0]
    pmap_personnel = index_by(personnel, "employee_id")

    def _attribute(emp_id: str) -> Dict[str, Any]:
        p = pmap_personnel.get(emp_id, {})
        return {"employee_id": emp_id, "name": p.get("name", emp_id), "role": p.get("role", "")}

    technicians = [_attribute(eid) for eid in latest.get("technician_ids", [])]
    if latest.get("lead_engineer_id"):
        lead = _attribute(latest["lead_engineer_id"])
        if lead not in technicians:
            technicians.insert(0, lead)

    in_window_pms = [w for w in pm_wos if within_window(w.get("closed"), days=lookback_days)]
    recent_history = [
        {"wo_id": w["wo_id"], "opened": w.get("opened"),
         "type": w.get("type"), "status": w.get("status")}
        for w in eq_wos[:10]
    ]
    recent_history.sort(key=lambda h: parse_date(h.get("opened")) or datetime.min, reverse=True)

    return {
        "status": "ok",
        "equipment_id": equipment_id,
        "last_pm_date": parse_date(latest.get("closed")).date().isoformat() if parse_date(latest.get("closed")) else latest.get("closed"),
        "last_pm_wo_id": latest.get("wo_id"),
        "last_pm_type": latest.get("type"),
        "last_pm_technicians": technicians,
        "last_pm_narrative": latest.get("narrative"),
        "next_pm_due": pmap_row.get("next_due"),
        "pm_template_id": pmap_row.get("pm_template_id"),
        "pm_template_name": pmap_row.get("pm_template_name"),
        "regulatory_basis": pmap_row.get("regulatory_basis"),
        "procedure_doc": pmap_row.get("procedure_doc"),
        "total_pms_in_window": len(in_window_pms),
        "recent_history": recent_history,
    }


def handler(event, context=None):
    return oracle_pm_lookup(
        equipment_id=event.get("equipment_id", ""),
        lookback_days=int(event.get("lookback_days", 365)),
    )
