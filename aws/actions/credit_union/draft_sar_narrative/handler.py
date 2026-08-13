"""
Draft Sar Narrative — CommunityWide FCU (Credit Union demo stub)
Auto-draft FinCEN-compliant SAR narrative for detected pattern
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="draft_sar_narrative",
    description="Auto-draft FinCEN-compliant SAR narrative for detected pattern",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="draft_sar_narrative input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="draft_sar_narrative output")
        .add_string("sar_id", 'Generated SAR ID')
        .add_string("narrative", 'Part IV narrative text')
        .add_string("statutory_cite", 'e.g. 31 U.S.C. § 5324')
        .add_string("filing_deadline", 'Detection date + 30 days')
        .add_number("confidence_pct", 'Agent confidence at draft')
))
def draft_sar_narrative(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'sar_id': 'SAR-2026-0142', 'narrative': 'On or about May 12 through May 28, 2026, the subject conducted 7 cash deposits totaling $47,300...', 'statutory_cite': '31 U.S.C. § 5324', 'filing_deadline': '2026-06-27', 'confidence_pct': 96.1}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
