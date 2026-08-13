"""
Quote Reconcile - Oil & Gas Midstream (EPROD demo stub)
Reconcile a vendor's engineering quote against the corresponding AFE budget,
MSA rates, and prior baseline quotes — surfaces over-AFE risk pre-award.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="quote_reconcile",
    description="Reconcile a midstream quote against AFE budget and MSA rates",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Quote reconciliation input")
        .add_string("quote_id", "Quote identifier to reconcile", required=True)
        .add_string("afe_number", "Associated AFE number", required=True)
        .add_string("msa_id", "Governing MSA identifier", required=False),
    output_schema=ActionOutputSchema(description="Reconciliation result")
        .add_boolean("is_reconciled", "Whether the quote ties to AFE / MSA")
        .add_number("afe_variance_pct", "Pct variance vs AFE budget")
        .add_string("recommendation", "approve | negotiate | reject")
))
def quote_reconcile(quote_id: str, afe_number: str, msa_id: str = None) -> dict:
    """Stub: returns a midstream quote ↔ AFE reconciliation verdict."""
    return {
        "quote_id": quote_id,
        "afe_number": afe_number,
        "msa_id": msa_id,
        "is_reconciled": False,
        "afe_variance_pct": 6.8,
        "recommendation": "negotiate",
        "afe_budget_usd": 665_000.00,
        "quote_total_usd": 712_400.00,
        "over_afe_lines": [
            {"description": "Integrity dig (3 anomalies)", "quoted": 412_900.00, "afe_baseline": 365_000.00},
        ],
        "msa_rate_compliance_pct": 98.4,
        "reconciled_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return quote_reconcile(**event)
