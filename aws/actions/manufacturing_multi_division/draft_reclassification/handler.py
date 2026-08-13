"""
Draft Reclassification — The Boler Company (Manufacturing · Multi-Division demo stub)
Draft proposed resolution + supporting evidence for an exception
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="draft_reclassification",
    description="Draft proposed resolution + supporting evidence for an exception",
    category="manufacturing_multi_division_intelligence",
    industry="manufacturing_multi_division",
    input_schema=ActionInputSchema(description="draft_reclassification input")
        .add_string("document_uri", "S3 URI or business identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="draft_reclassification output")
        .add_string("reclass_id", "Reclass Id")
        .add_string("exception_id", "Exception Id")
        .add_string("variance_amount", "Variance Amount")
        .add_string("confidence", "Confidence")
        .add_string("routing", "Routing")
))
def draft_reclassification(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a Boler-realistic payload for the demo."""
    payload = {'reclass_id': 'RECLASS-2026-0445', 'exception_id': 'EXC-2026-0445', 'variance_amount': '11420.00', 'confidence': '0.94', 'routing': 'route_benefits_mgr'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
