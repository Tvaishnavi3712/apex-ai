"""
PO Match Action
Match an invoice to a purchase order and validate amounts
"""

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: native key-condition builder
    from sdk.azure_data import Key
except ImportError:
    from ...sdk.azure_data import Key
import os
import json
from decimal import Decimal
from typing import Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="po_match",
    description="Match an invoice to a purchase order and validate that amounts are within tolerance",
    category="business_logic",
    industry="financial_services",
    input_schema=ActionInputSchema(description="PO matching parameters")
        .add_string("po_number", "Purchase order number to match", required=True)
        .add_number("invoice_amount", "Invoice total amount", required=True)
        .add_string("vendor_id", "Vendor ID from invoice", required=False)
        .add_number("tolerance_percent", "Amount tolerance percentage (default 5%)", required=False),
    output_schema=ActionOutputSchema(description="PO match result")
        .add_boolean("matched", "Whether PO was found and matched")
        .add_string("match_status", "EXACT_MATCH | WITHIN_TOLERANCE | OVER_TOLERANCE | NOT_FOUND | VENDOR_MISMATCH")
        .add_number("po_amount", "PO amount")
        .add_number("variance", "Difference between invoice and PO amount")
        .add_number("variance_percent", "Variance as percentage")
        .add_string("po_status", "PO status: open, partial, closed")
))
def po_match(
    po_number: str,
    invoice_amount: float,
    vendor_id: str = None,
    tolerance_percent: float = 5.0
) -> dict:
    """
    Match an invoice to a purchase order

    Args:
        po_number: Purchase order number
        invoice_amount: Invoice total amount
        vendor_id: Vendor ID to verify (optional)
        tolerance_percent: Acceptable variance percentage (default 5%)

    Returns:
        Match result with status and variance details
    """
    tables = get_table_resource()
    table_name = os.environ.get('PO_TABLE', 'apex-ai-platform-purchase-orders')
    table = cosmos_db.Table(table_name)

    try:
        # Look up PO
        response = table.get_item(Key={"po_number": po_number})

        if 'Item' not in response:
            return {
                "matched": False,
                "match_status": "NOT_FOUND",
                "po_number": po_number,
                "message": f"Purchase order {po_number} not found"
            }

        po = response['Item']
        po_amount = float(po.get('total_amount', 0))
        po_vendor_id = po.get('vendor_id')
        po_status = po.get('status', 'open')

        # Check vendor match if provided
        if vendor_id and po_vendor_id and vendor_id != po_vendor_id:
            return {
                "matched": False,
                "match_status": "VENDOR_MISMATCH",
                "po_number": po_number,
                "po_vendor_id": po_vendor_id,
                "invoice_vendor_id": vendor_id,
                "message": "Vendor on invoice does not match PO vendor"
            }

        # Calculate variance
        variance = invoice_amount - po_amount
        variance_percent = (abs(variance) / po_amount * 100) if po_amount > 0 else 0

        # Determine match status
        if abs(variance) < 0.01:  # Effectively zero
            match_status = "EXACT_MATCH"
            matched = True
        elif variance_percent <= tolerance_percent:
            match_status = "WITHIN_TOLERANCE"
            matched = True
        else:
            match_status = "OVER_TOLERANCE"
            matched = False

        return {
            "matched": matched,
            "match_status": match_status,
            "po_number": po_number,
            "po_amount": po_amount,
            "invoice_amount": invoice_amount,
            "variance": round(variance, 2),
            "variance_percent": round(variance_percent, 2),
            "tolerance_percent": tolerance_percent,
            "po_status": po_status,
            "po_date": po.get('created_date'),
            "po_description": po.get('description'),
            "remaining_amount": float(po.get('remaining_amount', po_amount))
        }

    except Exception as e:
        return {
            "matched": False,
            "match_status": "ERROR",
            "error": str(e)
        }


class POMatchAction(ApexActionBase):
    """PO Match Action (class-based)"""

    name = "po_match"
    description = "Match invoice to purchase order"
    category = "business_logic"
    industry = "financial_services"

    def __init__(self, table_name: str = None, default_tolerance: float = 5.0):
        super().__init__()
        self.table_name = table_name or os.environ.get('PO_TABLE', 'apex-ai-platform-purchase-orders')
        self.default_tolerance = default_tolerance

    def execute(
        self,
        po_number: str,
        invoice_amount: float,
        vendor_id: str = None,
        tolerance_percent: float = None,
        **kwargs
    ) -> dict:
        return po_match(
            po_number=po_number,
            invoice_amount=invoice_amount,
            vendor_id=vendor_id,
            tolerance_percent=tolerance_percent or self.default_tolerance
        )


def handler(event, context):
    """Lambda entry point"""
    return po_match(**event)
