"""
Draft Ctr — CommunityWide FCU (Credit Union demo stub)
Auto-draft FinCEN Form 112 CTR for cash transactions ≥ $10,000
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="draft_ctr",
    description="Auto-draft FinCEN Form 112 CTR for cash transactions ≥ $10,000",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="draft_ctr input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="draft_ctr output")
        .add_string("ctr_id", 'Generated CTR ID')
        .add_string("filing_deadline", 'Transaction date + 15 days')
        .add_string("aggregated", 'true / false for multi-transaction')
        .add_string("subject_member_id", 'Member number')
))
def draft_ctr(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'ctr_id': 'CTR-2026-05-1187', 'filing_deadline': '2026-06-13', 'aggregated': 'false', 'subject_member_id': '29341'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
