"""
wp_corpus_search — find work packages mentioning an equipment + aggregate failure modes.

Powers DiagnosticsAgent's "What are common issues with Pump-3A?" answer.
Joins work_orders.json (filtered by equipment_id) + failure_events.json
(joined by repair_wo_id) + failure_mode_catalog.json to produce a ranked
list of failure modes with frequency counts and cited WO ids.
"""

from __future__ import annotations

import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_work_orders, load_failure_events, load_failure_mode_catalog,
    missing_data_envelope, parse_date, index_by,
)


@apex_action(ApexActionSchema(
    name="wp_corpus_search",
    description="Search work-package corpus for an equipment, aggregate failure modes, and cite supporting WOs.",
    category="analytics",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="WP corpus search request")
        .add_string("equipment_id", "Equipment id, e.g. P-3A", required=True)
        .add_string("optional_topic", "Narrow by free-text topic (default: all)", required=False),
    output_schema=ActionOutputSchema(description="Corpus aggregation envelope")
        .add_string("status", "ok | error")
        .add_number("total_packages_indexed", "Total WO count for this equipment")
        .add_string("packages_matching", "List of {wp_id, wo_id, opened_date, narrative_snippet}")
        .add_string("failure_modes_observed", "List of {mode_id, mode_name, count, percentage}")
        .add_string("failure_modes_distribution", "Same list, sorted desc"),
))
def wp_corpus_search(equipment_id: str, optional_topic: str = "") -> dict:
    """Aggregate failure history for `equipment_id` from the synthetic corpus."""
    if not equipment_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "equipment_id is required"}

    work_orders = load_work_orders()
    if work_orders is None:
        return missing_data_envelope("work_orders.json")
    failure_events = load_failure_events() or []
    catalog = load_failure_mode_catalog() or []
    catalog_idx = index_by(catalog, "mode_id")

    eq_wos = [w for w in work_orders if w.get("equipment_id") == equipment_id]
    if optional_topic:
        topic_lc = optional_topic.lower()
        eq_wos = [w for w in eq_wos if topic_lc in (w.get("narrative") or "").lower()]

    # Build event index keyed by repair_wo_id so we can attach modes to WOs
    event_by_wo: Dict[str, Dict[str, Any]] = {}
    for ev in failure_events:
        wo_id = ev.get("repair_wo_id")
        if wo_id:
            event_by_wo[wo_id] = ev
        # Also tally for this equipment regardless of WO link (events may not always link cleanly)

    # Count modes for this equipment
    mode_counter: Counter = Counter()
    cited_wos: Dict[str, List[str]] = {}
    for ev in failure_events:
        if ev.get("equipment_id") != equipment_id:
            continue
        mode = ev.get("failure_mode")
        if not mode:
            continue
        mode_counter[mode] += 1
        cited_wos.setdefault(mode, []).append(ev.get("repair_wo_id"))

    total_events = sum(mode_counter.values())
    failure_modes_observed: List[Dict[str, Any]] = []
    for mode_id, count in mode_counter.most_common():
        cat = catalog_idx.get(mode_id, {})
        failure_modes_observed.append({
            "mode_id": mode_id,
            "mode_name": cat.get("name", mode_id),
            "count": count,
            "percentage": round(100.0 * count / max(1, total_events), 1),
            "typical_lead_days": cat.get("typical_lead_days"),
            "early_indicators": cat.get("early_indicators", []),
            "mitigation_actions": cat.get("mitigation_actions", []),
            "cited_wo_ids": [w for w in cited_wos.get(mode_id, []) if w][:5],
        })

    # Recent packages (top 10 by opened date)
    sorted_wos = sorted(
        eq_wos, key=lambda w: parse_date(w.get("opened")) or datetime.min, reverse=True,
    )[:10]
    packages_matching = [
        {
            "wp_id": f"wp_{w.get('wo_id')}",
            "wo_id": w.get("wo_id"),
            "opened_date": (parse_date(w.get("opened")) or datetime.min).date().isoformat(),
            "type": w.get("type"),
            "status": w.get("status"),
            "narrative_snippet": (w.get("narrative") or "")[:200],
            "failure_mode": event_by_wo.get(w.get("wo_id"), {}).get("failure_mode"),
        }
        for w in sorted_wos
    ]

    return {
        "status": "ok",
        "equipment_id": equipment_id,
        "total_packages_indexed": len(eq_wos),
        "packages_matching": packages_matching,
        "failure_modes_observed": failure_modes_observed,
        "failure_modes_distribution": failure_modes_observed,  # already sorted
        "total_failure_events": total_events,
    }


def handler(event, context=None):
    return wp_corpus_search(
        equipment_id=event.get("equipment_id", ""),
        optional_topic=event.get("optional_topic", ""),
    )
