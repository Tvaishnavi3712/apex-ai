"""
Cip Calculate Risk Tier — CommunityWide FCU (Credit Union demo stub)
Calculate member CIP risk tier from screen + occupation + jurisdiction
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="cip_calculate_risk_tier",
    description="Calculate member CIP risk tier from screen + occupation + jurisdiction",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="cip_calculate_risk_tier input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="cip_calculate_risk_tier output")
        .add_string("risk_tier", 'LOW / MEDIUM / HIGH')
        .add_string("edd_required", 'true / false')
        .add_string("rationale", 'Risk factors driving the tier')
))
def cip_calculate_risk_tier(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'risk_tier': 'LOW', 'edd_required': 'false', 'rationale': 'Domestic US citizen, stable employment, clean ChexSystems, no PEP'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
