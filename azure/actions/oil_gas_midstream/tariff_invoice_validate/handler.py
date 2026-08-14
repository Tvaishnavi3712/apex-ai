"""
Tariff Invoice Validate - Oil & Gas Midstream (EPROD demo stub — wow use case)
Validate a midstream transportation invoice against the active FERC tariff
sheet — rate-table match, shipper-category eligibility, fuel & loss factor,
gas-day effectivity. Surfaces tariff over-bills before they post.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="tariff_invoice_validate",
    description="Validate a midstream transportation invoice against the active FERC tariff",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Tariff ↔ invoice validation input")
        .add_string("invoice_number", "Invoice number to validate", required=True)
        .add_string("tariff_id", "FERC tariff identifier", required=True)
        .add_string("gas_day", "Gas-day of service (YYYY-MM-DD)", required=True)
        .add_string("shipper_category", "Shipper category (committed|uncommitted|spot|affiliate)", required=False),
    output_schema=ActionOutputSchema(description="Validation result")
        .add_boolean("is_valid", "Whether the invoice conforms to the tariff")
        .add_number("variance_pct", "Pct variance vs tariff-expected billing")
        .add_string("disposition", "approve | hold_for_review | reject")
))
def tariff_invoice_validate(
    invoice_number: str,
    tariff_id: str,
    gas_day: str,
    shipper_category: str = "committed",
) -> dict:
    """Stub: returns a tariff ↔ invoice validation verdict for the EPROD demo."""
    return {
        "invoice_number": invoice_number,
        "tariff_id": tariff_id,
        "gas_day": gas_day,
        "shipper_category": shipper_category,
        "is_valid": False,
        "variance_pct": 2.1,
        "disposition": "hold_for_review",
        "fuel_loss_factor_applied_pct": 1.25,
        "flagged_lines": [
            {
                "line": 3,
                "reason": "Billed at uncommitted rate ($0.5125/Bbl) but shipper holds committed capacity",
                "expected_rate_usd_per_bbl": 0.4250,
                "billed_rate_usd_per_bbl": 0.5125,
                "volume_bbls": 18_200,
                "overbill_usd": 1_592.50,
            },
        ],
        "validated_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return tariff_invoice_validate(**event)
