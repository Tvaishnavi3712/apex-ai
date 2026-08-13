"""
Loan Cross Validate Income — CommunityWide FCU (Credit Union demo stub)
Cross-validate paystub vs W-2 vs tax return vs bank deposits
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="loan_cross_validate_income",
    description="Cross-validate paystub vs W-2 vs tax return vs bank deposits",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="loan_cross_validate_income input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="loan_cross_validate_income output")
        .add_string("validation_status", 'PASS / PARTIAL / FAIL')
        .add_number("income_verified_usd", 'Verified annual income')
        .add_number("discrepancy_pct", 'Discrepancy percentage if any')
))
def loan_cross_validate_income(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'validation_status': 'PASS', 'income_verified_usd': 245000.0, 'discrepancy_pct': 0.0}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
