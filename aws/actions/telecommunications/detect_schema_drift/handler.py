"""
detect_schema_drift — compare baseline + current Redfish schemas and emit
the list of breaking changes with their impact map. Powers SchemaWatchAgent.

Uses the pre-computed expected diff JSON in `synthetic-data/verizon_far_edge/
schemas/redfish_schema_diff_expected.json` so the demo is deterministic —
production wiring would replace this with a live DMTF schema comparator.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.telecommunications._shared import load_json, missing_data_envelope  # noqa: E402


@apex_action(ApexActionSchema(
    name="detect_schema_drift",
    description="Compare baseline + current Redfish schemas and emit breaking changes with their script-impact map.",
    category="schema_analysis",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="Schema drift detection request")
        .add_string("baseline_path", "Path to baseline schema JSON. Defaults to v1.14.0 bundled schema.", required=False)
        .add_string("current_path",  "Path to current schema JSON.  Defaults to v1.16.0 bundled schema.", required=False),
    output_schema=ActionOutputSchema(description="Drift report envelope")
        .add_string("status", "ok | error")
        .add_string("baseline_version", "Baseline schema version")
        .add_string("current_version",  "Current schema version")
        .add_number("breaking_changes_count", "Number of breaking changes detected")
        .add_number("scripts_impacted_count", "Total unique scripts impacted across changes")
        .add_number("days_before_cycle",  "How many days ahead of the next cycle this was detected")
        .add_string("breaking_changes",   "List of {id, endpoint, field_old, field_new, change_type, scripts_impacted, remediation, vendor_release_note_ref}")
        .add_string("wave_recommendation","HOLD_PENDING_REMEDIATION | PROCEED_WITH_PATCHES | PROCEED")
        .add_number("estimated_remediation_hours", "Aggregate effort estimate"),
))
def detect_schema_drift(
    baseline_path: Optional[str] = None,
    current_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Return the pre-computed diff report for the demo. In production this
    would parse both schema files and compute the diff live."""
    diff = load_json("schemas/redfish_schema_diff_expected.json")
    if not diff:
        return missing_data_envelope("schemas/redfish_schema_diff_expected.json")

    summary = diff.get("schema_diff_report", {})
    changes = diff.get("changes", [])
    remediation_summary = diff.get("remediation_summary", {})

    return {
        "status":                       "ok",
        "baseline_version":             summary.get("baseline_version"),
        "current_version":              summary.get("current_version"),
        "detected_at":                  summary.get("detected_at"),
        "days_before_cycle":            summary.get("days_before_cycle", 6),
        "breaking_changes_count":       summary.get("breaking_changes_count", len(changes)),
        "scripts_impacted_count":       summary.get("scripts_impacted_count"),
        "breaking_changes":             changes,
        "wave_recommendation":          remediation_summary.get("recommended_action", "HOLD_PENDING_REMEDIATION"),
        "estimated_remediation_hours":  remediation_summary.get("estimated_total_effort_hours"),
        "vendor_release_note_anchor":   "Wind River Linux 24.12 §3.2",
    }
