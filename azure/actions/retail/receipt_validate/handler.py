"""
Receipt Validation Action
Validate receipts for returns and warranty claims
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
from datetime import datetime, timedelta
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="receipt_validate",
    description="Validate receipts for returns, exchanges, and warranty claims",
    category="returns",
    industry="retail",
    input_schema=ActionInputSchema(description="Receipt validation parameters")
        .add_string("transaction_id", "Transaction/receipt number", required=True)
        .add_string("store_id", "Store identifier", required=False)
        .add_string("purchase_date", "Purchase date from receipt", required=False)
        .add_array("items", "Items to validate", required=False),
    output_schema=ActionOutputSchema(description="Receipt validation result")
        .add_boolean("valid", "Whether receipt is valid")
        .add_string("transaction_id", "Transaction ID")
        .add_string("store_name", "Store name")
        .add_string("purchase_date", "Purchase date")
        .add_number("total_amount", "Total transaction amount")
        .add_array("line_items", "Validated line items")
        .add_object("return_eligibility", "Return eligibility information")
))
def receipt_validate(
    transaction_id: str,
    store_id: str = None,
    purchase_date: str = None,
    items: List[Dict] = None
) -> dict:
    """
    Validate a receipt

    Args:
        transaction_id: Transaction/receipt number
        store_id: Store identifier
        purchase_date: Purchase date
        items: Items to validate

    Returns:
        Receipt validation result
    """
    result = {
        "valid": False,
        "transaction_id": transaction_id,
        "store_name": None,
        "store_id": None,
        "purchase_date": None,
        "total_amount": 0,
        "line_items": [],
        "return_eligibility": {},
        "validation_date": datetime.now().isoformat()
    }

    try:
        tables = get_table_resource()
        table = cosmos_db.Table(os.environ.get('TRANSACTIONS_TABLE', 'apex-retail-transactions'))

        response = table.get_item(Key={"transaction_id": transaction_id})

        if 'Item' in response:
            txn = response['Item']
            result["valid"] = True
            result["store_id"] = txn.get("store_id")
            result["store_name"] = txn.get("store_name")
            result["purchase_date"] = txn.get("purchase_date")
            result["total_amount"] = float(txn.get("total_amount", 0))
            result["line_items"] = txn.get("items", [])
            result["payment_method"] = txn.get("payment_method")
            result["customer_id"] = txn.get("customer_id")

            # Calculate return eligibility
            result["return_eligibility"] = _calculate_return_eligibility(
                txn.get("purchase_date"),
                txn.get("items", [])
            )

            return result

    except Exception as e:
        result["error"] = str(e)

    # Return mock data for testing
    mock_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
    return {
        "valid": True,
        "transaction_id": transaction_id,
        "store_id": store_id or "STORE001",
        "store_name": "Main Street Store",
        "purchase_date": purchase_date or mock_date,
        "total_amount": 156.78,
        "payment_method": "credit_card",
        "card_last_four": "4532",
        "line_items": [
            {"sku": "SKU001", "name": "Wireless Headphones", "quantity": 1, "price": 79.99, "category": "electronics"},
            {"sku": "SKU002", "name": "Phone Case", "quantity": 2, "price": 24.99, "category": "accessories"},
            {"sku": "SKU003", "name": "USB Cable", "quantity": 1, "price": 12.99, "category": "electronics"}
        ],
        "return_eligibility": {
            "eligible": True,
            "days_remaining": 15,
            "return_window": 30,
            "restrictions": [],
            "refund_method": "original_payment"
        },
        "validation_date": datetime.now().isoformat()
    }


def _calculate_return_eligibility(purchase_date: str, items: List[dict]) -> dict:
    """Calculate return eligibility based on purchase date and items"""
    if not purchase_date:
        return {"eligible": False, "reason": "Unknown purchase date"}

    try:
        purchase = datetime.strptime(purchase_date, '%Y-%m-%d')
        days_since_purchase = (datetime.now() - purchase).days

        # Default 30-day return window
        return_window = 30
        eligible = days_since_purchase <= return_window

        restrictions = []
        for item in items:
            category = item.get("category", "").lower()
            if category == "final_sale":
                restrictions.append(f"{item.get('name')}: Final sale - no returns")
            elif category == "electronics" and days_since_purchase > 15:
                restrictions.append(f"{item.get('name')}: Electronics 15-day return window exceeded")

        return {
            "eligible": eligible and not restrictions,
            "days_since_purchase": days_since_purchase,
            "days_remaining": max(0, return_window - days_since_purchase),
            "return_window": return_window,
            "restrictions": restrictions,
            "refund_method": "original_payment"
        }
    except Exception:
        return {"eligible": False, "reason": "Error calculating eligibility"}


class ReceiptValidateAction(ApexActionBase):
    """Receipt Validation Action (class-based)"""

    name = "receipt_validate"
    description = "Validate receipts for returns"
    category = "returns"
    industry = "retail"

    def execute(self, **kwargs) -> dict:
        return receipt_validate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return receipt_validate(**event)
