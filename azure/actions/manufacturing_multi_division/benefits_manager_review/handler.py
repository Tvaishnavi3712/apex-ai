"""
Benefits Manager Review — The Boler Company (Manufacturing · Multi-Division demo stub)
Stage-1 HITL review (Sarah Mitchell)
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="benefits_manager_review",
    description="Stage-1 HITL review (Sarah Mitchell)",
    category="manufacturing_multi_division_intelligence",
    industry="manufacturing_multi_division",
    input_schema=ActionInputSchema(description="benefits_manager_review input")
        .add_string("document_uri", "blob URI or business identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="benefits_manager_review output")
        .add_string("review_id", "Review Id")
        .add_string("approver", "Approver")
        .add_string("decision", "Decision")
        .add_string("sla_remaining_hours", "Sla Remaining Hours")
))
def benefits_manager_review(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a Boler-realistic payload for the demo."""
    payload = {'review_id': 'REV-2026-06-BEN', 'approver': 'Sarah Mitchell', 'decision': 'APPROVED', 'sla_remaining_hours': '2.5'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
