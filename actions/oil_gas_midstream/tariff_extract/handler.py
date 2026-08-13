"""
Tariff Extract - Oil & Gas Midstream (EPROD demo stub — wow use case)
Extract structured rate tables from FERC-filed pipeline tariff sheets
(rate per Bbl / MMBtu, shipper categories, fuel & loss factors, effective dates).
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="tariff_extract",
    description="Extract rate tables and shipper categories from a FERC pipeline tariff sheet",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Tariff extraction input")
        .add_string("document_uri", "blob URI of the FERC tariff PDF", required=True)
        .add_string("pipeline_id", "Pipeline / system identifier", required=False),
    output_schema=ActionOutputSchema(description="Extracted tariff payload")
        .add_string("tariff_id", "FERC tariff identifier (e.g. FERC-NGL-2026-04)")
        .add_string("pipeline_name", "Pipeline / system name")
        .add_string("effective_date", "Tariff effective date")
        .add_string("expiry_date", "Tariff expiry or next-review date")
        .add_number("fuel_loss_factor_pct", "Fuel & loss factor as a percentage")
))
def tariff_extract(document_uri: str, pipeline_id: str = None) -> dict:
    """Stub: returns a FERC midstream tariff payload for the EPROD demo."""
    return {
        "tariff_id": "FERC-NGL-2026-04",
        "pipeline_name": "Mont Belvieu C2+ NGL System",
        "pipeline_id": pipeline_id or "PL-MB-C2-001",
        "effective_date": "2026-04-01",
        "expiry_date": "2027-03-31",
        "fuel_loss_factor_pct": 1.25,
        "rate_tables": [
            {"table": "Table 1 — Committed Shipper", "rate_usd_per_bbl": 0.4250, "uom": "Bbl"},
            {"table": "Table 2 — Uncommitted Shipper", "rate_usd_per_bbl": 0.5125, "uom": "Bbl"},
            {"table": "Table 3 — Spot Movement", "rate_usd_per_mmbtu": 0.0875, "uom": "MMBtu"},
        ],
        "shipper_categories": ["committed", "uncommitted", "spot", "affiliate"],
        "extracted_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return tariff_extract(**event)
