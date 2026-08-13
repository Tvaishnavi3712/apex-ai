"""
Inventory Lookup Action
Check inventory levels and availability for manufacturing parts
"""

import boto3
from boto3.dynamodb.conditions import Key
import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# ============================================================================
# Decorator-based implementation
# ============================================================================

@apex_action(ApexActionSchema(
    name="inventory_lookup",
    description="Check inventory levels and availability for parts in manufacturing operations",
    category="inventory",
    industry="manufacturing",
    input_schema=ActionInputSchema(description="Inventory lookup parameters")
        .add_string("part_number", "Part number or SKU to check", required=True)
        .add_string("warehouse", "Warehouse location code (optional)", required=False)
        .add_number("quantity_needed", "Quantity needed for availability check", required=False)
        .add_boolean("check_substitutes", "Check substitute parts if unavailable", required=False),
    output_schema=ActionOutputSchema(description="Inventory lookup result")
        .add_boolean("available", "Whether requested quantity is available")
        .add_string("part_number", "Part number queried")
        .add_number("on_hand", "Current quantity on hand")
        .add_number("allocated", "Quantity allocated to orders")
        .add_number("available_qty", "Available to promise quantity")
        .add_number("safety_stock", "Safety stock level")
        .add_string("status", "Inventory status: in_stock, low_stock, out_of_stock, discontinued")
        .add_string("next_receipt_date", "Expected date of next receipt if backordered")
))
def inventory_lookup(
    part_number: str,
    warehouse: str = None,
    quantity_needed: float = None,
    check_substitutes: bool = False
) -> dict:
    """
    Look up inventory levels for a part

    Args:
        part_number: Part number or SKU
        warehouse: Optional warehouse code to filter
        quantity_needed: Quantity needed to check availability
        check_substitutes: Whether to check substitute parts if unavailable

    Returns:
        Inventory information and availability status
    """
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('INVENTORY_TABLE', 'apex-ai-platform-inventory')
    table = dynamodb.Table(table_name)

    result = {
        "available": False,
        "part_number": part_number,
        "on_hand": 0,
        "allocated": 0,
        "available_qty": 0,
        "safety_stock": 0,
        "status": "not_found",
        "next_receipt_date": None,
        "warehouse_details": [],
        "substitutes": []
    }

    try:
        # Query by part number
        if warehouse:
            # Query specific warehouse
            response = table.get_item(
                Key={
                    "part_number": part_number,
                    "warehouse": warehouse
                }
            )
            if 'Item' in response:
                result = _aggregate_inventory([response['Item']], quantity_needed)
        else:
            # Query all warehouses for this part
            response = table.query(
                KeyConditionExpression=Key('part_number').eq(part_number)
            )
            if response.get('Items'):
                result = _aggregate_inventory(response['Items'], quantity_needed)

        # Check substitutes if requested and not available
        if check_substitutes and not result['available'] and quantity_needed:
            substitutes = _find_substitutes(part_number, quantity_needed, table)
            result['substitutes'] = substitutes

        return result

    except Exception as e:
        return {
            "available": False,
            "part_number": part_number,
            "error": str(e),
            "status": "error"
        }


def _aggregate_inventory(items: List[dict], quantity_needed: float = None) -> dict:
    """Aggregate inventory across warehouses"""

    def convert_decimal(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return obj

    total_on_hand = 0
    total_allocated = 0
    total_safety_stock = 0
    warehouse_details = []
    next_receipt = None

    for item in items:
        on_hand = convert_decimal(item.get('quantity_on_hand', 0))
        allocated = convert_decimal(item.get('quantity_allocated', 0))
        safety = convert_decimal(item.get('safety_stock', 0))

        total_on_hand += on_hand
        total_allocated += allocated
        total_safety_stock = max(total_safety_stock, safety)

        warehouse_details.append({
            "warehouse": item.get('warehouse'),
            "on_hand": on_hand,
            "allocated": allocated,
            "available": max(0, on_hand - allocated - safety),
            "bin_location": item.get('bin_location')
        })

        # Track next receipt date
        receipt_date = item.get('next_receipt_date')
        if receipt_date:
            if next_receipt is None or receipt_date < next_receipt:
                next_receipt = receipt_date

    available_qty = max(0, total_on_hand - total_allocated - total_safety_stock)

    # Determine status
    if total_on_hand == 0:
        status = "out_of_stock"
    elif available_qty == 0:
        status = "allocated"
    elif available_qty <= total_safety_stock * 0.5:
        status = "low_stock"
    else:
        status = "in_stock"

    # Check availability against needed quantity
    is_available = True
    if quantity_needed:
        is_available = available_qty >= quantity_needed

    return {
        "available": is_available,
        "part_number": items[0].get('part_number') if items else None,
        "on_hand": total_on_hand,
        "allocated": total_allocated,
        "available_qty": available_qty,
        "safety_stock": total_safety_stock,
        "status": status,
        "next_receipt_date": next_receipt,
        "warehouse_details": warehouse_details,
        "substitutes": []
    }


def _find_substitutes(part_number: str, quantity_needed: float, table) -> List[dict]:
    """Find substitute parts that could fulfill the requirement"""
    substitutes = []

    try:
        # Look up substitutes in a substitutes index
        # This is a simplified implementation
        dynamodb = boto3.resource('dynamodb')
        subs_table = dynamodb.Table(os.environ.get('SUBSTITUTES_TABLE', 'apex-ai-platform-substitutes'))

        response = subs_table.query(
            KeyConditionExpression=Key('original_part').eq(part_number)
        )

        for sub in response.get('Items', []):
            sub_part = sub.get('substitute_part')
            # Check availability of substitute
            sub_inventory = inventory_lookup(sub_part, quantity_needed=quantity_needed)
            if sub_inventory.get('available'):
                substitutes.append({
                    "part_number": sub_part,
                    "description": sub.get('description'),
                    "available_qty": sub_inventory.get('available_qty'),
                    "compatibility": sub.get('compatibility', 'direct')
                })
    except Exception:
        pass  # Substitutes lookup is optional

    return substitutes


# ============================================================================
# Class-based implementation
# ============================================================================

class InventoryLookupAction(ApexActionBase):
    """
    Inventory Lookup Action (class-based implementation)
    """

    name = "inventory_lookup"
    description = "Check inventory levels and availability for parts"
    category = "inventory"
    industry = "manufacturing"

    def __init__(self, table_name: str = None):
        super().__init__()
        self.table_name = table_name or os.environ.get(
            'INVENTORY_TABLE',
            'apex-ai-platform-inventory'
        )

    def execute(
        self,
        part_number: str,
        warehouse: str = None,
        quantity_needed: float = None,
        check_substitutes: bool = False,
        **kwargs
    ) -> dict:
        """Execute the inventory lookup"""
        return inventory_lookup(
            part_number=part_number,
            warehouse=warehouse,
            quantity_needed=quantity_needed,
            check_substitutes=check_substitutes
        )


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return inventory_lookup(**event)
