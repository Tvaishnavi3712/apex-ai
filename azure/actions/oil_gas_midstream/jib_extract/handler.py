"""
JIB Extract - Oil & Gas Midstream (EPROD demo stub — wow use case)
Extract structured charges from a Joint Interest Billing (JIB) statement —
operator, working-interest partners, AFE references, capital vs operating
charges, gas-day allocations.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="jib_extract",
    description="Extract structured charges from a Joint Interest Billing (JIB) statement",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="JIB extraction input")
        .add_string("document_uri", "blob URI of the JIB statement PDF", required=True),
    output_schema=ActionOutputSchema(description="Extracted JIB payload")
        .add_string("jib_period", "Billing period (e.g. 2026-04)")
        .add_string("operator", "Operator submitting the JIB")
        .add_string("property_id", "Joint property / unit identifier")
        .add_number("total_capital_usd", "Total capital charges for the period")
        .add_number("total_operating_usd", "Total operating charges for the period")
        .add_number("working_interest_pct", "Recipient working interest percentage")
))
def jib_extract(document_uri: str) -> dict:
    """Stub: returns a midstream JIB payload for the EPROD demo (wow use case)."""
    return {
        "jib_period": "2026-04",
        "operator": "Sulphur River Pipeline Services LLC",
        "property_id": "JNT-MB-C2-FRAC-001",
        "working_interest_pct": 87.5,
        "total_capital_usd": 1_412_300.00,
        "total_operating_usd": 524_815.42,
        "afe_references": ["AFE-2026-CAP-0411", "AFE-2026-NGL-0117", "AFE-2025-INT-0902"],
        "capital_charges": [
            {"afe": "AFE-2026-CAP-0411", "description": "Mont Belvieu fractionator tie-in", "amount": 1_092_300.00},
            {"afe": "AFE-2026-NGL-0117", "description": "16in NGL lateral integrity dig", "amount": 320_000.00},
        ],
        "operating_charges": [
            {"category": "Pipeline integrity / NDE", "amount": 184_532.18},
            {"category": "Hot-tap labor & materials", "amount": 142_900.00},
            {"category": "FERC compliance & reporting", "amount": 38_400.00},
            {"category": "Routine inspection & MMBtu metering", "amount": 158_983.24},
        ],
        "extracted_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return jib_extract(**event)
