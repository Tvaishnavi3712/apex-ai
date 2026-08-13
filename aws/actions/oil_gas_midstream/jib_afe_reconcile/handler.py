"""
JIB AFE Reconcile - Oil & Gas Midstream (EPROD demo stub — wow use case)
Reconcile a JIB statement's charges against the underlying AFE records:
flags out-of-scope charges, over-AFE capital, working-interest mis-allocations,
and missing AFE references. The headline EPROD audit-savings use case.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="jib_afe_reconcile",
    description="Reconcile JIB charges against the underlying AFE records",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="JIB ↔ AFE reconciliation input")
        .add_string("jib_period", "JIB billing period (e.g. 2026-04)", required=True)
        .add_string("property_id", "Joint property / unit identifier", required=True)
        .add_number("working_interest_pct", "Recipient working interest percentage", required=False),
    output_schema=ActionOutputSchema(description="Reconciliation result")
        .add_boolean("is_reconciled", "Whether all JIB charges tie to in-scope AFEs")
        .add_number("total_disputed_usd", "Total disputed charge amount")
        .add_string("recommendation", "approve | dispute | escalate")
))
def jib_afe_reconcile(
    jib_period: str,
    property_id: str,
    working_interest_pct: float = 87.5,
) -> dict:
    """Stub: returns a JIB ↔ AFE reconciliation verdict for the EPROD demo."""
    return {
        "jib_period": jib_period,
        "property_id": property_id,
        "working_interest_pct": working_interest_pct,
        "is_reconciled": False,
        "total_disputed_usd": 84_215.75,
        "recommendation": "dispute",
        "out_of_scope_lines": [
            {
                "afe": None,
                "description": "Hot-tap labor & materials charged without AFE reference",
                "amount": 142_900.00,
                "wi_share_usd": 125_037.50,
            },
        ],
        "over_afe_charges": [
            {
                "afe": "AFE-2026-CAP-0411",
                "description": "Mont Belvieu fractionator tie-in",
                "afe_budget_usd": 1_000_000.00,
                "jib_billed_usd": 1_092_300.00,
                "overage_usd": 92_300.00,
                "wi_share_usd": 80_762.50,
            },
        ],
        "wi_allocation_errors": [
            {"line": 4, "expected_wi_pct": 87.5, "billed_wi_pct": 90.0, "delta_usd": 3_178.25},
        ],
        "reconciled_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return jib_afe_reconcile(**event)
