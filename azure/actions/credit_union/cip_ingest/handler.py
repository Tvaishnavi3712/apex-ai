"""
Cip Ingest — CommunityWide FCU (Credit Union demo stub)
Ingest CIP application from CWAnyWhere / in-branch / online channel
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="cip_ingest",
    description="Ingest CIP application from CWAnyWhere / in-branch / online channel",
    category="credit_union_intelligence",
    industry="credit_union",
    input_schema=ActionInputSchema(description="cip_ingest input")
        .add_string("document_uri", "blob URI or member identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="cip_ingest output")
        .add_string("application_id", 'Internal CIP application reference')
        .add_string("channel", 'Submission channel')
        .add_string("submitted_at", 'ISO8601 timestamp')
        .add_number("fields_captured", 'Count of fields captured')
))
def cip_ingest(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a CWFCU-realistic payload for the demo."""
    payload = {'application_id': 'CIP-MEM-2026-06-04-DEMO', 'channel': 'CWAnyWhere', 'submitted_at': '2026-06-04T09:14:00Z', 'fields_captured': 22}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
