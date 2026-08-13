"""
Inventory Check - Manufacturing Action (Context-Driven)
Check inventory levels and availability for materials

Context-Driven Architecture:
- Inventory thresholds from playbook context.inventory_config
- Location settings from context.warehouse_config
- Reorder rules from context.reorder_config
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

logger = structlog.get_logger()


# Default inventory configuration
DEFAULT_INVENTORY_CONFIG = {
    "low_stock_threshold_pct": 20,
    "critical_stock_threshold_pct": 10,
    "check_all_locations": True,
    "include_pending_receipts": True
}

# Default warehouse configuration
DEFAULT_WAREHOUSE_CONFIG = {
    "locations": ["MAIN", "OVERFLOW", "STAGING"],
    "primary_location": "MAIN"
}


@register_factory("inventory_check")
async def inventory_check(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check inventory levels (context-driven).

    Context keys used:
        - inventory_config: Inventory threshold settings
        - warehouse_config: Warehouse and location configurations
        - reorder_config: Automatic reorder settings

    Input:
        items: List of items to check
        po_extract: PO data (for PO-based checks)
        check_type: Type of check (availability, levels, reorder)

    Output:
        inventory_status: Overall inventory status
        item_availability: Per-item availability
        shortages: Items with insufficient stock
        reorder_suggestions: Items needing reorder
    """
    context = context or input_data.get('context', {})
    inventory_config = context.get('inventory_config', DEFAULT_INVENTORY_CONFIG)
    warehouse_config = context.get('warehouse_config', DEFAULT_WAREHOUSE_CONFIG)
    reorder_config = context.get('reorder_config', {})

    logger.info(
        "Inventory check invoked",
        context_driven=bool(context)
    )

    # Get items to check
    items = input_data.get('items', [])
    po_data = input_data.get('po_extract', {})
    check_type = input_data.get('check_type', 'availability')

    # If checking from PO, extract items
    if po_data and not items:
        line_items = po_data.get('line_items', [])
        items = [
            {
                'item_number': item.get('item_number'),
                'description': item.get('description'),
                'quantity_needed': item.get('quantity', 0)
            }
            for item in line_items
        ]

    # Get thresholds
    low_threshold = inventory_config.get('low_stock_threshold_pct', 20)
    critical_threshold = inventory_config.get('critical_stock_threshold_pct', 10)
    locations = warehouse_config.get('locations', ['MAIN'])

    # Check each item
    item_availability = []
    shortages = []
    reorder_suggestions = []

    for item in items:
        item_number = item.get('item_number', '')
        quantity_needed = item.get('quantity_needed', 0)

        # Simulated inventory lookup
        inventory_data = _lookup_inventory(item_number, locations, inventory_config)

        on_hand = inventory_data['total_on_hand']
        available = inventory_data['available']
        pending_receipts = inventory_data['pending_receipts']
        reorder_point = inventory_data['reorder_point']

        # Check availability
        can_fulfill = available >= quantity_needed
        shortage_qty = max(0, quantity_needed - available)

        # Determine stock level status
        if reorder_point > 0:
            stock_pct = (on_hand / reorder_point) * 100
        else:
            stock_pct = 100

        if stock_pct <= critical_threshold:
            stock_status = 'critical'
        elif stock_pct <= low_threshold:
            stock_status = 'low'
        else:
            stock_status = 'adequate'

        item_result = {
            'item_number': item_number,
            'description': item.get('description'),
            'quantity_needed': quantity_needed,
            'on_hand': on_hand,
            'available': available,
            'allocated': on_hand - available,
            'pending_receipts': pending_receipts,
            'can_fulfill': can_fulfill,
            'shortage_quantity': shortage_qty,
            'stock_status': stock_status,
            'stock_percentage': round(stock_pct, 1),
            'location_breakdown': inventory_data['by_location']
        }

        item_availability.append(item_result)

        if shortage_qty > 0:
            shortages.append({
                'item_number': item_number,
                'description': item.get('description'),
                'shortage_quantity': shortage_qty,
                'expected_receipt_date': inventory_data.get('next_receipt_date')
            })

        # Check if reorder needed
        if stock_status in ['low', 'critical']:
            reorder_qty = _calculate_reorder_quantity(item_number, inventory_data, reorder_config)
            reorder_suggestions.append({
                'item_number': item_number,
                'description': item.get('description'),
                'current_stock': on_hand,
                'reorder_point': reorder_point,
                'suggested_quantity': reorder_qty,
                'priority': 'high' if stock_status == 'critical' else 'normal'
            })

    # Calculate overall status
    if shortages:
        overall_status = 'shortages_detected'
    elif reorder_suggestions:
        overall_status = 'reorder_needed'
    else:
        overall_status = 'all_available'

    total_items = len(item_availability)
    fulfillable_items = len([i for i in item_availability if i['can_fulfill']])

    return {
        "check_type": check_type,
        "inventory_status": overall_status,
        "total_items_checked": total_items,
        "fulfillable_items": fulfillable_items,
        "fulfillment_rate": round(fulfillable_items / total_items * 100, 1) if total_items > 0 else 100,
        "item_availability": item_availability,
        "shortages": shortages,
        "shortage_count": len(shortages),
        "reorder_suggestions": reorder_suggestions,
        "reorder_count": len(reorder_suggestions),
        "locations_checked": locations,
        "include_pending": inventory_config.get('include_pending_receipts', True),
        "checked_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "inventory_check",
        "factory_version": "2.0.0",
        "context_keys_used": ["inventory_config", "warehouse_config", "reorder_config"]
    }


def _lookup_inventory(item_number: str, locations: List[str], config: Dict) -> Dict:
    """Look up inventory for an item."""
    # Simulated inventory data
    base_qty = hash(item_number) % 500 + 100  # Deterministic based on item number

    by_location = {}
    total = 0
    for loc in locations:
        loc_qty = int(base_qty * (0.6 if loc == 'MAIN' else 0.2))
        by_location[loc] = {
            'on_hand': loc_qty,
            'allocated': int(loc_qty * 0.1),
            'available': int(loc_qty * 0.9)
        }
        total += loc_qty

    available = int(total * 0.9)
    pending = int(total * 0.2) if config.get('include_pending_receipts', True) else 0

    return {
        'total_on_hand': total,
        'available': available,
        'allocated': total - available,
        'pending_receipts': pending,
        'reorder_point': int(total * 0.3),
        'by_location': by_location,
        'next_receipt_date': (datetime.utcnow().replace(day=1) + __import__('datetime').timedelta(days=10)).strftime('%Y-%m-%d')
    }


def _calculate_reorder_quantity(item_number: str, inventory_data: Dict, reorder_config: Dict) -> int:
    """Calculate suggested reorder quantity."""
    reorder_point = inventory_data.get('reorder_point', 100)
    on_hand = inventory_data.get('total_on_hand', 0)

    # Default reorder quantity is 2x reorder point minus current stock
    base_qty = max(0, (reorder_point * 2) - on_hand)

    # Apply minimum order quantity if configured
    min_order = reorder_config.get('minimum_order_qty', {}).get(item_number, 50)
    return max(base_qty, min_order)


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(inventory_check(event))
