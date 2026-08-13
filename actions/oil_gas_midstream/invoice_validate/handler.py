"""
Invoice Validate - Oil & Gas Midstream (EPROD demo stub)
Validate extracted midstream invoice line items against PO / MSA / tariff
context — flags off-contract rates, working-interest miscalcs, and missing AFEs.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="invoice_validate",
    description="Validate midstream invoice line items against PO / MSA / tariff context",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Invoice validation input")
        .add_string("invoice_number", "Extracted invoice number", required=True)
        .add_string("po_number", "Associated PO number, if any", required=False)
        .add_string("msa_id", "Associated MSA identifier, if any", required=False)
        .add_number("invoice_total", "Total invoice amount to validate", required=True),
    output_schema=ActionOutputSchema(description="Validation result")
        .add_boolean("is_valid", "Whether the invoice passed all rules")
        .add_number("variance_pct", "Pct variance vs expected total")
        .add_string("disposition", "approve | hold_for_review | reject")
))
def invoice_validate(
    invoice_number: str,
    invoice_total: float,
    po_number: str = None,
    msa_id: str = None,
) -> dict:
    """Stub: returns a midstream-realistic validation verdict for the EPROD demo."""
    return {
        "invoice_number": invoice_number,
        "is_valid": False,
        "variance_pct": 3.42,
        "disposition": "hold_for_review",
        "flagged_lines": [
            {
                "line": 2,
                "reason": "Integrity-dig labor rate exceeds MSA Exhibit B by 4.1%",
                "expected_rate_usd": 285.00,
                "billed_rate_usd": 297.00,
            },
            {
                "line": 3,
                "reason": "NGL fractionation throughput fee billed without referenced AFE",
                "afe_expected": True,
            },
        ],
        "msa_id": msa_id,
        "po_number": po_number,
        "validated_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return invoice_validate(**event)
