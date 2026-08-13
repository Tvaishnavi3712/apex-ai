"""
classify_failures — apply the 4-category classification rules to parsed
ROBOT test results and emit per-failure records ready for JIRA ticket
creation. Categories: latency_threshold_breach, schema_drift_failure,
regression_failure, investigate.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.telecommunications._shared import classify_failure_message, kb_lookup  # noqa: E402


@apex_action(ApexActionSchema(
    name="classify_failures",
    description="Apply Verizon Far Edge classification rules to parsed ROBOT test results.",
    category="classification",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="Failure classification request")
        .add_string("test_results", "List of test records from parse_robot_output", required=True),
    output_schema=ActionOutputSchema(description="Classified failure record")
        .add_string("status", "ok | error")
        .add_number("fail_count", "Number of FAIL tests classified")
        .add_number("warn_count", "Number of WARN/investigate tests")
        .add_number("p1_count",   "P1 (production blocker) count")
        .add_number("p2_count",   "P2 (must-fix-before-wave) count")
        .add_number("p3_count",   "P3 (monitor) count")
        .add_string("classified_failures", "Per-failure records with category, severity, kb_match, recommendation"),
))
def classify_failures(test_results: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    if not test_results:
        return {"status": "error", "error_type": "bad_arguments",
                "message": "test_results is required and must be a non-empty list"}

    classified: List[Dict[str, Any]] = []
    for t in test_results:
        if t.get("status") == "PASS":
            continue
        msg = t.get("failure_message") or ""
        rule = classify_failure_message(msg)
        kb = kb_lookup(msg)
        recommendation = "Open P1 ticket, hold deployment" if rule["severity"] == "P1" else (
                         "Open P2 ticket, fix before next wave"   if rule["severity"] == "P2" else
                         "Monitor next cycle; no immediate action")
        if rule["category"] == "schema_drift_failure":
            recommendation = "Schema drift — run SchemaWatchAgent + remediate impacted scripts before next cycle."
        record = {
            "test_id":         t.get("test_id"),
            "name":            t.get("name"),
            "library":         t.get("library"),
            "redfish_endpoint":t.get("redfish_endpoint"),
            "failure_message": msg,
            "category":        rule["category"],
            "severity":        rule["severity"],
            "kb_match":        (kb or {}).get("id"),
            "kb_title":        (kb or {}).get("title"),
            "kb_workaround":   (kb or {}).get("workaround"),
            "recommendation":  recommendation,
        }
        classified.append(record)

    fail_count = sum(1 for r in classified if r["severity"] in ("P1", "P2"))
    warn_count = sum(1 for r in classified if r["severity"] == "P3")
    p1 = sum(1 for r in classified if r["severity"] == "P1")
    p2 = sum(1 for r in classified if r["severity"] == "P2")
    p3 = sum(1 for r in classified if r["severity"] == "P3")

    # Default deployment recommendation logic
    if p1 == 0 and p2 == 0:
        deployment_recommendation = "PROCEED" if p3 == 0 else "CONDITIONAL_PASS (monitor P3 items)"
    elif p1 <= 5:
        deployment_recommendation = "CONDITIONAL_PASS (remediate P1+P2 before wave)"
    else:
        deployment_recommendation = "FAIL — hold wave deployment"

    return {
        "status":                     "ok",
        "fail_count":                 fail_count,
        "warn_count":                 warn_count,
        "p1_count":                   p1,
        "p2_count":                   p2,
        "p3_count":                   p3,
        "classified_failures":        classified,
        "deployment_recommendation":  deployment_recommendation,
        "hitl_required":              fail_count > 20,
    }
