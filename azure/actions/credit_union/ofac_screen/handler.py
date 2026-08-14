"""
Ofac Screen — CommunityWide FCU (Credit Union demo stub)
Screen subject against OFAC SDN, Consolidated, FinCEN 314(a), 594(a)
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="ofac_screen",
    description="Screen subject against OFAC SDN, Consolidated, FinCEN 314(a), 594(a)",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="ofac_screen input")
        .add_string("document_uri", "blob URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="ofac_screen output")
        .add_string("result", 'CLEAR / NEAR_MATCH / TRUE_MATCH')
        .add_number("match_score_pct", 'Best match similarity')
        .add_string("lists_screened", 'Lists screened')
))
def ofac_screen(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'result': 'CLEAR', 'match_score_pct': 0.0, 'lists_screened': 'SDN, Consolidated, 314(a), 594(a)'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
