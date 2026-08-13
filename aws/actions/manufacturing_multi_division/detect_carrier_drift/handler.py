"""
Detect Carrier Drift — The Boler Company (Manufacturing · Multi-Division demo stub)
Per-life premium drift vs plan-doc rate
"""
import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="detect_carrier_drift",
    description="Per-life premium drift vs plan-doc rate",
    category="manufacturing_multi_division_intelligence",
    industry="manufacturing_multi_division",
    input_schema=ActionInputSchema(description="detect_carrier_drift input")
        .add_string("document_uri", "S3 URI or business identifier", required=False)
        .add_string("context", "Optional context payload (JSON)", required=False),
    output_schema=ActionOutputSchema(description="detect_carrier_drift output")
        .add_string("drift_scan_id", "Drift Scan Id")
        .add_string("carriers_with_drift", "Carriers With Drift")
        .add_string("worst_carrier", "Worst Carrier")
        .add_string("drift_bps", "Drift Bps")
        .add_string("alert_level", "Alert Level")
))
def detect_carrier_drift(document_uri: str = None, context: str = None) -> dict:
    """Stub: returns a Boler-realistic payload for the demo."""
    payload = {'drift_scan_id': 'DRIFT-2026-06', 'carriers_with_drift': '1', 'worst_carrier': 'Cigna Medical', 'drift_bps': '720', 'alert_level': 'HIGH'}
    payload["extracted_at"] = datetime.utcnow().isoformat()
    return payload
