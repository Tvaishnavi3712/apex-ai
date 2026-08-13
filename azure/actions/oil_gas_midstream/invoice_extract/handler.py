"""
Invoice Extract - Oil & Gas Midstream (EPROD demo stub)
Extract header + line-item data from midstream vendor invoices (gathering,
processing, NGL fractionation, hot-tap, integrity-dig work).
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="invoice_extract",
    description="Extract header and line-item data from midstream vendor invoices",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Midstream invoice extraction input")
        .add_string("document_uri", "blob URI of the invoice document", required=True)
        .add_string("vendor_hint", "Optional vendor name to bias extraction", required=False),
    output_schema=ActionOutputSchema(description="Extracted invoice payload")
        .add_string("invoice_number", "Vendor invoice number")
        .add_string("vendor_name", "Vendor / supplier name")
        .add_string("invoice_date", "Invoice issue date (YYYY-MM-DD)")
        .add_string("service_period", "Service period (e.g. 2026-04-01 to 2026-04-30)")
        .add_number("total_amount", "Total invoice amount in USD")
        .add_string("currency", "Currency code")
        .add_string("afe_number", "AFE number referenced on the invoice, if any")
))
def invoice_extract(document_uri: str, vendor_hint: str = None) -> dict:
    """Stub: returns a realistic midstream invoice payload for the EPROD demo."""
    return {
        "invoice_number": "EPROD-INV-2026-44821",
        "vendor_name": vendor_hint or "Sulphur River Pipeline Services LLC",
        "invoice_date": "2026-04-30",
        "service_period": "2026-04-01 to 2026-04-30",
        "total_amount": 184_532.18,
        "currency": "USD",
        "afe_number": "AFE-2026-NGL-0117",
        "line_items": [
            {"description": "Hot-tap crew labor", "quantity": 48, "uom": "hrs", "amount": 14_400.00},
            {"description": "Integrity dig — Mont Belvieu lateral", "quantity": 1, "uom": "ea", "amount": 92_500.00},
            {"description": "NGL fractionation throughput fee", "quantity": 18_200, "uom": "Bbls", "amount": 77_632.18},
        ],
        "extracted_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return invoice_extract(**event)
