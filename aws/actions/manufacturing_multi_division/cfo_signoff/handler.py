"""
Cfo Signoff — The Boler Company (Manufacturing · Multi-Division demo stub)
Stage-2 HITL sign-off (Ziggy Kravitz)
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="cfo_signoff",
    description="Stage-2 HITL sign-off (Ziggy Kravitz)",
    category="manufacturing_multi_division_intelligence",
    industry="manufacturing_multi_division",
    input_schema=ActionInputSchema(description="cfo_signoff input")
        .add_string("document_uri", "S3 URI or business identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="cfo_signoff output")
        .add_string("signoff_id", "Signoff Id")
        .add_string("approver", "Approver")
        .add_string("decision", "Decision")
        .add_string("material_variance_flagged", "Material Variance Flagged")
        .add_string("total_je_amount", "Total Je Amount")
))
def cfo_signoff(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a Boler-realistic payload for the demo."""
    payload = {'signoff_id': 'SIGNOFF-2026-06-CFO', 'approver': 'Ziggy Kravitz', 'decision': 'APPROVED', 'material_variance_flagged': 'true', 'total_je_amount': '1284320.00'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
