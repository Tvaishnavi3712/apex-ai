"""
Verify Government Id — CommunityWide FCU (Credit Union demo stub)
Verify state DL via AAMVA DLDV or US Passport via DOS API
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="verify_government_id",
    description="Verify state DL via AAMVA DLDV or US Passport via DOS API",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="verify_government_id input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="verify_government_id output")
        .add_string("verified", 'VERIFIED / FAILED / EXPIRED')
        .add_string("verification_method", 'DLDV / DOS / Mitek')
        .add_number("photo_match_pct", 'Photo match confidence (0-100)')
        .add_string("document_authentic", 'GENUINE / FORGED_SUSPECTED')
))
def verify_government_id(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'verified': 'VERIFIED', 'verification_method': 'AAMVA DLDV', 'photo_match_pct': 97.4, 'document_authentic': 'GENUINE'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
