"""
Detect Exception — The Boler Company (Manufacturing · Multi-Division demo stub)
Variance scan against expected allocation
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="detect_exception",
    description="Variance scan against expected allocation",
    category="manufacturing_multi_division_intelligence",
    industry="manufacturing_multi_division",
    input_schema=ActionInputSchema(description="detect_exception input")
        .add_string("document_uri", "S3 URI or business identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="detect_exception output")
        .add_string("scan_id", "Scan Id")
        .add_string("exceptions_found", "Exceptions Found")
        .add_string("auto_fixable", "Auto Fixable")
        .add_string("hitl_required", "Hitl Required")
))
def detect_exception(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a Boler-realistic payload for the demo."""
    payload = {'scan_id': 'EXCSCAN-2026-06', 'exceptions_found': '7', 'auto_fixable': '4', 'hitl_required': '3'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
