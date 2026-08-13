"""
Pep Screen — CommunityWide FCU (Credit Union demo stub)
Screen subject against PEP database (WorldCheck, Dow Jones)
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="pep_screen",
    description="Screen subject against PEP database (WorldCheck, Dow Jones)",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="pep_screen input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="pep_screen output")
        .add_string("result", 'NEGATIVE / NEAR_MATCH / POSITIVE')
        .add_string("risk_tier", 'LOW / MEDIUM / HIGH')
        .add_string("match_details", 'PEP match details')
))
def pep_screen(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'result': 'NEGATIVE', 'risk_tier': 'LOW', 'match_details': 'No match'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
