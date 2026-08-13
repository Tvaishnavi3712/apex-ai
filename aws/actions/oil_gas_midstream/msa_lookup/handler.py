"""
MSA Lookup - Oil & Gas Midstream (EPROD demo stub)
Resolve a vendor / scope-of-work to its governing Master Service Agreement
(rate schedule, working-interest split, FERC clauses, effective dates).
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="msa_lookup",
    description="Resolve vendor + scope to the governing midstream MSA",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="MSA lookup input")
        .add_string("vendor_name", "Vendor / contractor name", required=True)
        .add_string("scope_keyword", "Scope-of-work keyword (e.g. hot-tap, NGL frac)", required=False)
        .add_string("gas_day", "Service gas-day (YYYY-MM-DD) for effective-date check", required=False),
    output_schema=ActionOutputSchema(description="Resolved MSA record")
        .add_string("msa_id", "Master Service Agreement identifier")
        .add_string("msa_title", "MSA title")
        .add_string("effective_date", "MSA effective date")
        .add_string("expiry_date", "MSA expiry date")
        .add_boolean("is_active", "Whether the MSA is active on the requested gas-day")
        .add_string("rate_schedule_uri", "S3 URI of the rate-schedule exhibit")
))
def msa_lookup(vendor_name: str, scope_keyword: str = None, gas_day: str = None) -> dict:
    """Stub: returns a midstream MSA record for the EPROD demo."""
    return {
        "msa_id": "MSA-EPROD-BBCS-2024",
        "msa_title": "Bayou Bend Construction Services — Midstream Capital MSA",
        "vendor_name": vendor_name,
        "scope_keyword": scope_keyword,
        "effective_date": "2024-01-01",
        "expiry_date": "2026-12-31",
        "is_active": True,
        "rate_schedule_uri": "s3://eprod-contracts/msa/BBCS-2024/exhibit-B-rates.pdf",
        "working_interest_pct": 87.5,
        "ferc_compliant": True,
        "looked_up_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return msa_lookup(**event)
