"""
Vendor Lookup Action
Check if a vendor exists in the approved vendor list
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

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# ============================================================================
# Decorator-based implementation (simple)
# ============================================================================

@apex_action(ApexActionSchema(
    name="vendor_lookup",
    description="Check if a vendor exists in the approved vendor list and retrieve vendor details",
    category="data_lookup",
    industry="financial_services",
    input_schema=ActionInputSchema(description="Vendor lookup parameters")
        .add_string("vendor_name", "Name of the vendor to look up", required=True)
        .add_string("vendor_id", "Vendor ID (alternative to name)", required=False)
        .add_string("tax_id", "Vendor tax ID (alternative lookup)", required=False),
    output_schema=ActionOutputSchema(description="Vendor lookup result")
        .add_boolean("found", "Whether the vendor was found in approved list")
        .add_string("vendor_id", "Vendor ID if found")
        .add_string("vendor_name", "Vendor name")
        .add_string("status", "Vendor status: active, inactive, blocked")
        .add_string("payment_terms", "Default payment terms")
        .add_string("category", "Vendor category")
))
def vendor_lookup(
    vendor_name: str = None,
    vendor_id: str = None,
    tax_id: str = None
) -> dict:
    """
    Look up a vendor in the approved vendor list

    Args:
        vendor_name: Name of the vendor (fuzzy match)
        vendor_id: Exact vendor ID
        tax_id: Vendor tax ID

    Returns:
        Vendor information if found, or not found status
    """
    tables = get_table_resource()
    table_name = os.environ.get('VENDORS_TABLE', 'apex-ai-platform-approved-vendors')
    table = cosmos_db.Table(table_name)

    result = {
        "found": False,
        "vendor_id": None,
        "vendor_name": vendor_name,
        "status": "not_found",
        "payment_terms": None,
        "category": None
    }

    try:
        # Try exact lookup by vendor_id first
        if vendor_id:
            response = table.get_item(Key={"vendor_id": vendor_id})
            if 'Item' in response:
                return _format_vendor_result(response['Item'])

        # Try lookup by tax_id
        if tax_id:
            response = table.query(
                IndexName='tax-id-index',
                KeyConditionExpression=Key('tax_id').eq(tax_id)
            )
            if response.get('Items'):
                return _format_vendor_result(response['Items'][0])

        # Try lookup by name (case-insensitive)
        if vendor_name:
            # First try exact match
            response = table.query(
                IndexName='vendor-name-index',
                KeyConditionExpression=Key('vendor_name_lower').eq(vendor_name.lower())
            )
            if response.get('Items'):
                return _format_vendor_result(response['Items'][0])

            # If no exact match, scan for partial match (not ideal for large tables)
            response = table.scan(
                FilterExpression='contains(vendor_name_lower, :name)',
                ExpressionAttributeValues={':name': vendor_name.lower()},
                Limit=5
            )
            if response.get('Items'):
                # Return best match (first result)
                return _format_vendor_result(response['Items'][0])

        return result

    except Exception as e:
        return {
            "found": False,
            "error": str(e),
            "status": "error"
        }


def _format_vendor_result(item: dict) -> dict:
    """Format Cosmos DB item to response"""
    def convert_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return obj

    return {
        "found": True,
        "vendor_id": item.get('vendor_id'),
        "vendor_name": item.get('vendor_name'),
        "status": item.get('status', 'active'),
        "payment_terms": item.get('payment_terms', 'NET30'),
        "category": item.get('category'),
        "address": item.get('address'),
        "tax_id": item.get('tax_id'),
        "contact_email": item.get('contact_email'),
        "approved_date": item.get('approved_date'),
        "credit_limit": convert_decimal(item.get('credit_limit'))
    }


# ============================================================================
# Class-based implementation (complex)
# ============================================================================

class VendorLookupAction(ApexActionBase):
    """
    Vendor Lookup Action (class-based implementation)

    Use this for more complex scenarios requiring custom initialization
    or multiple helper methods.
    """

    name = "vendor_lookup"
    description = "Check if a vendor exists in the approved vendor list"
    category = "data_lookup"
    industry = "financial_services"

    def __init__(self, table_name: str = None):
        super().__init__()
        self.table_name = table_name or os.environ.get(
            'VENDORS_TABLE',
            'apex-ai-platform-approved-vendors'
        )

    def execute(
        self,
        vendor_name: str = None,
        vendor_id: str = None,
        tax_id: str = None,
        **kwargs
    ) -> dict:
        """Execute the vendor lookup"""
        return vendor_lookup(
            vendor_name=vendor_name,
            vendor_id=vendor_id,
            tax_id=tax_id
        )


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return vendor_lookup(**event)
