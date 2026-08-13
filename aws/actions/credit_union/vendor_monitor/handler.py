"""
Vendor Monitor — CommunityWide FCU (Credit Union demo stub)
Continuous monitoring of vendor contracts (renewal, SLA, rate drift)
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="vendor_monitor",
    description="Continuous monitoring of vendor contracts (renewal, SLA, rate drift)",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="vendor_monitor input")
        .add_string("document_uri", "S3 URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="vendor_monitor output")
        .add_number("contracts_monitored", 'Count of active contracts')
        .add_number("renewals_due_30d", 'Renewals in next 30 days')
        .add_number("sla_breaches_ytd", 'SLA breaches year-to-date')
        .add_number("rate_drift_alerts", 'Vendors over escalation cap')
))
def vendor_monitor(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'contracts_monitored': 47, 'renewals_due_30d': 3, 'sla_breaches_ytd': 0, 'rate_drift_alerts': 3}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
