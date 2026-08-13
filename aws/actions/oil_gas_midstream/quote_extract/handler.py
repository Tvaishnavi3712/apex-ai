"""
Quote Extract - Oil & Gas Midstream (EPROD demo stub)
Extract structured pricing from engineering / construction quotes covering
hot-tap, integrity-dig, NGL fractionation, and pipeline tie-in scopes.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="quote_extract",
    description="Extract structured pricing from a midstream engineering quote",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="Quote extraction input")
        .add_string("document_uri", "S3 URI of the quote document", required=True),
    output_schema=ActionOutputSchema(description="Extracted quote payload")
        .add_string("quote_id", "Vendor quote identifier")
        .add_string("vendor_name", "Vendor / engineering firm")
        .add_string("quote_date", "Quote issue date")
        .add_string("scope_summary", "Short scope-of-work summary")
        .add_number("quote_total", "Total quoted amount in USD")
        .add_string("currency", "Currency code")
        .add_string("validity_period", "Quote validity window")
))
def quote_extract(document_uri: str) -> dict:
    """Stub: returns a midstream engineering quote payload."""
    return {
        "quote_id": "Q-2026-EPROD-0918",
        "vendor_name": "Gulf Coast Integrity Engineering LLC",
        "quote_date": "2026-04-08",
        "scope_summary": "16in NGL lateral integrity dig + NDE + hot-tap restoration",
        "quote_total": 712_400.00,
        "currency": "USD",
        "validity_period": "60 days from issue",
        "line_items": [
            {"description": "Mobilization & site prep", "amount": 48_500.00},
            {"description": "Integrity dig (3 anomalies)", "amount": 412_900.00},
            {"description": "NDE — UT / MFL inspection", "amount": 156_000.00},
            {"description": "Hot-tap restoration & FERC §2.78 docs", "amount": 95_000.00},
        ],
        "extracted_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return quote_extract(**event)
