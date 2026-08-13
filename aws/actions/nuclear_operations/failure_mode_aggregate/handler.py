"""
failure_mode_aggregate — aggregate failure events across multiple equipment / a system.

Used by DiagnosticsAgent for "what's the worst failure mode in the RCS?" type
queries. Returns a frequency table joined to the failure_mode_catalog so each
mode comes back with mitigation guidance.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_failure_events, load_failure_mode_catalog, load_equipment,
    missing_data_envelope, index_by, parse_date,
)


@apex_action(ApexActionSchema(
    name="failure_mode_aggregate",
    description="Aggregate failure events by mode across one or more equipment ids or a whole system.",
    category="analytics",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Failure aggregation request")
        .add_string("equipment_ids", "List of equipment ids (mutually exclusive with system_id)")
        .add_string("system_id", "System id (e.g. RCS) — aggregate across all equipment in this system"),
    output_schema=ActionOutputSchema(description="Failure mode summary envelope")
        .add_string("status", "ok | error")
        .add_string("mode_frequency", "{mode_id: count} dict")
        .add_string("top_5_modes", "Top 5 modes with count, percent, lead days, mitigation")
        .add_number("total_events", "Total events aggregated")
        .add_number("time_window_years", "Year span of aggregated events"),
))
def failure_mode_aggregate(
    equipment_ids: Optional[List[str]] = None,
    system_id: Optional[str] = None,
) -> dict:
    """Aggregate failure events across `equipment_ids` OR all equipment in `system_id`."""
    if not equipment_ids and not system_id:
        return {"status": "error", "error_type": "bad_arguments",
                "message": "Provide equipment_ids or system_id"}

    failure_events = load_failure_events()
    if failure_events is None:
        return missing_data_envelope("failure_events.json")
    catalog = load_failure_mode_catalog() or []
    cat_idx = index_by(catalog, "mode_id")

    target_ids: set = set()
    if equipment_ids:
        target_ids.update(equipment_ids)
    if system_id:
        equipment = load_equipment() or []
        target_ids.update(e["equipment_id"] for e in equipment if e.get("system_id") == system_id)

    matching = [ev for ev in failure_events if ev.get("equipment_id") in target_ids]
    counter: Counter = Counter(ev.get("failure_mode") for ev in matching if ev.get("failure_mode"))
    total = sum(counter.values())

    top: List[Dict[str, Any]] = []
    for mode_id, count in counter.most_common(5):
        cat = cat_idx.get(mode_id, {})
        top.append({
            "mode_id": mode_id,
            "mode_name": cat.get("name", mode_id),
            "count": count,
            "percent": round(100.0 * count / max(1, total), 1),
            "typical_lead_days": cat.get("typical_lead_days"),
            "early_indicators": cat.get("early_indicators", []),
            "mitigation_actions": cat.get("mitigation_actions", []),
        })

    # Time window
    years: List[int] = []
    for ev in matching:
        d = parse_date(ev.get("occurred_at"))
        if d:
            years.append(d.year)
    span = (max(years) - min(years) + 1) if years else 0

    return {
        "status": "ok",
        "scope": {"equipment_ids": list(equipment_ids or []), "system_id": system_id},
        "mode_frequency": dict(counter),
        "top_5_modes": top,
        "total_events": total,
        "time_window_years": span,
    }


def handler(event, context=None):
    return failure_mode_aggregate(
        equipment_ids=event.get("equipment_ids"),
        system_id=event.get("system_id"),
    )
