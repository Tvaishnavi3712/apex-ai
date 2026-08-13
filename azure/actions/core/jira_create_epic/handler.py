"""
jira_create_epic — Create a JIRA Cloud epic + optional sub-tasks.

Used by SchemaWatchAgent (pb-tel-3) to bundle every schema-drift impacted
script under a single tracked epic. Returns the epic key + a list of
child ticket keys+urls, so the UI can render the whole epic as one row
with expandable subtasks.

Optimisation: when `child_tickets[]` is passed, this handler creates the
epic first and then loops calling jira_create_ticket for each child so
they all attach to the same parent. Sequential, not parallel — JIRA Cloud
free tier rate-limits aggressively on bursts.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))
sys.path.append(str(Path(__file__).resolve().parents[3] / "backend"))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.core.jira_create_ticket.handler import jira_create_ticket  # noqa: E402
from services.jira_client import get_client  # noqa: E402


@apex_action(ApexActionSchema(
    name="jira_create_epic",
    description="Create a JIRA Cloud epic + optional sub-tasks. Used by "
                "SchemaWatchAgent to bundle every schema-drift remediation "
                "under a single tracked epic.",
    category="integration",
    industry="core",
    input_schema=ActionInputSchema(description="Epic + optional children")
        .add_string("summary",        "Epic summary (one-line title)", required=True)
        .add_string("description",    "Epic body text")
        .add_string("labels",         "Extra labels — list[str]")
        .add_string("child_tickets",  "Optional list of ticket dicts to create as children; each is the input shape of jira_create_ticket")
        .add_string("cycle_id",       "Source cycle id"),
    output_schema=ActionOutputSchema(description="Created epic + child references")
        .add_string("status",         "ok | error | partial")
        .add_string("epic_key",       "JIRA key of the epic")
        .add_string("epic_url",       "Direct browse URL of the epic")
        .add_string("child_count",    "Number of child tickets created successfully")
        .add_string("child_tickets",  "List of {key, url, mock, status} per child")
        .add_string("mock",           "True if mock-mode response")
        .add_string("error",          "Error detail if status != ok"),
))
def jira_create_epic(
    *,
    summary: str,
    description: str = "",
    labels: Optional[List[str]] = None,
    child_tickets: Optional[List[Dict[str, Any]]] = None,
    cycle_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create an epic + sub-tasks. Returns epic key + list of child keys."""
    if not summary:
        return {"status": "error", "error": "summary is required"}

    epic_labels: List[str] = list(labels or []) + ["far-edge", "schema-drift", "wave-blocker"]
    if cycle_id:
        epic_labels.append(f"cycle-{cycle_id}")

    client = get_client()
    epic_result = client.create_issue(
        summary=summary[:240],
        description=description or "Schema drift remediation epic. Created by SchemaWatchAgent.",
        issue_type="Epic",
        labels=epic_labels,
    )

    if not epic_result.get("key"):
        return {
            "status":        "error",
            "epic_key":      None,
            "epic_url":      None,
            "child_count":   0,
            "child_tickets": [],
            "mock":          epic_result.get("mock", False),
            "error":         epic_result.get("raw_error", "unknown JIRA error creating epic"),
        }

    epic_key = epic_result["key"]
    epic_url = epic_result["url"]
    epic_mock = epic_result.get("mock", False)

    # Create child tickets sequentially with a small delay to stay under
    # JIRA Cloud free-tier rate limits (~250 req/min).
    created_children: List[Dict[str, Any]] = []
    if child_tickets:
        for child in child_tickets:
            child_input = dict(child)
            child_input["parent_epic_key"] = epic_key
            if cycle_id:
                child_input.setdefault("cycle_id", cycle_id)
            child_result = jira_create_ticket(**child_input)
            created_children.append({
                "key":         child_result.get("ticket_key"),
                "url":         child_result.get("ticket_url"),
                "mock":        child_result.get("mock", False),
                "status":      child_result.get("status", "error"),
                "summary":     child.get("summary"),
            })
            # Throttle in live mode only. Mock returns instantly.
            if not child_result.get("mock", True):
                time.sleep(0.1)

    success_count = sum(1 for c in created_children if c.get("status") == "ok")
    overall_status = (
        "ok" if (not child_tickets or success_count == len(child_tickets))
        else "partial"
    )

    return {
        "status":        overall_status,
        "epic_key":      epic_key,
        "epic_url":      epic_url,
        "child_count":   success_count,
        "child_tickets": created_children,
        "mock":          epic_mock,
        "error":         None if overall_status == "ok" else
                         f"{len(created_children) - success_count} child ticket(s) failed",
    }
