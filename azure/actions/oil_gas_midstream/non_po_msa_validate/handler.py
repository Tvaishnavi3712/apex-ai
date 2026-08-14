"""
Non-PO MSA Validate - Oil & Gas Midstream (EPROD demo stub)
For invoices submitted without a PO, validate the work against the vendor's
governing MSA rate schedule at intake (the EPROD non-PO AP workflow).
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="non_po_msa_validate",
    description="Validate a non-PO invoice against the vendor's MSA at intake",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Non-PO MSA validation input")
        .add_string("vendor_name", "Vendor / contractor name", required=True)
        .add_string("msa_id", "Resolved MSA identifier", required=True)
        .add_number("invoice_total", "Invoice total to validate", required=True)
        .add_string("gas_day", "Service gas-day for rate effectivity", required=False),
    output_schema=ActionOutputSchema(description="Validation result")
        .add_boolean("is_valid", "Whether the invoice conforms to MSA rates")
        .add_string("disposition", "auto_approve | hold_for_review | reject")
        .add_number("variance_pct", "Pct variance vs MSA rate schedule")
))
def non_po_msa_validate(
    vendor_name: str,
    msa_id: str,
    invoice_total: float,
    gas_day: str = None,
) -> dict:
    """Stub: returns a non-PO MSA validation verdict for the EPROD demo."""
    return {
        "vendor_name": vendor_name,
        "msa_id": msa_id,
        "gas_day": gas_day,
        "is_valid": True,
        "disposition": "auto_approve",
        "variance_pct": 0.3,
        "matched_rate_lines": [
            {"line": 1, "msa_rate_usd_hr": 285.00, "billed_rate_usd_hr": 285.00},
            {"line": 2, "msa_rate_usd_bbl": 4.26, "billed_rate_usd_bbl": 4.26},
        ],
        "flagged_lines": [],
        "validated_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return non_po_msa_validate(**event)
