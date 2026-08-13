"""
Calculate Dti Ltv — CommunityWide FCU (Credit Union demo stub)
Calculate front + back DTI and LTV (when collateral present)
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="calculate_dti_ltv",
    description="Calculate front + back DTI and LTV (when collateral present)",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="calculate_dti_ltv input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="calculate_dti_ltv output")
        .add_number("dti_front_pct", 'Front-end DTI')
        .add_number("dti_back_pct", 'Back-end DTI')
        .add_number("ltv_pct", 'LTV (0 if N/A)')
        .add_string("within_policy", 'true / false')
))
def calculate_dti_ltv(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'dti_front_pct': 32.1, 'dti_back_pct': 38.4, 'ltv_pct': 76.2, 'within_policy': 'true'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
