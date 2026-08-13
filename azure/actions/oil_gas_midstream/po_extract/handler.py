"""
PO Extract - Oil & Gas Midstream (EPROD demo stub)
Extract header + line-item data from midstream purchase orders (capital
projects, MRO, pipeline integrity work).
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema


@apex_action(ApexActionSchema(
    name="po_extract",
    description="Extract header and line-item data from a midstream purchase order",
    category="midstream_document_intelligence",
    industry="oil_gas_midstream",
    input_schema=ActionInputSchema(description="PO extraction input")
        .add_string("document_uri", "blob URI of the PO document", required=True),
    output_schema=ActionOutputSchema(description="Extracted PO payload")
        .add_string("po_number", "Purchase order number")
        .add_string("vendor_name", "Awarded vendor / contractor name")
        .add_string("issue_date", "PO issue date (YYYY-MM-DD)")
        .add_string("afe_number", "Associated AFE number")
        .add_string("contract_id", "Parent contract or MSA identifier")
        .add_number("po_total", "Total PO value in USD")
        .add_string("scope_summary", "Short scope-of-work summary")
))
def po_extract(document_uri: str) -> dict:
    """Stub: returns a midstream PO payload for the EPROD demo."""
    return {
        "po_number": "EPROD-PO-2026-7741",
        "vendor_name": "Bayou Bend Construction Services Inc.",
        "issue_date": "2026-03-12",
        "afe_number": "AFE-2026-CAP-0411",
        "contract_id": "MSA-EPROD-BBCS-2024",
        "po_total": 1_245_000.00,
        "scope_summary": "Mont Belvieu C2+ fractionator tie-in: hot-tap, integrity dig, NDE",
        "line_items": [
            {"line": 1, "description": "Hot-tap crew (FERC §2.78 compliant)", "amount": 245_000.00},
            {"line": 2, "description": "Integrity dig & NDE — 16in NGL lateral", "amount": 685_000.00},
            {"line": 3, "description": "Project management & site safety", "amount": 315_000.00},
        ],
        "extracted_at": datetime.utcnow().isoformat(),
    }


def handler(event, context):
    """Lambda entry point."""
    return po_extract(**event)
