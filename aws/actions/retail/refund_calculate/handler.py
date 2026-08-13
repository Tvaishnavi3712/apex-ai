"""
Refund Calculate - Retail Action (Context-Driven)
Calculate refund amounts for returns

Context-Driven Architecture:
- Refund rules from playbook context.refund_config
- Tax rules from context.tax_config
- Discount handling from context.discount_config
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


DEFAULT_REFUND_CONFIG = {
    "refund_shipping": False,
    "refund_tax": True,
    "prorate_discounts": True,
    "restocking_fee_pct": 0
}


@register_factory("refund_calculate")
async def refund_calculate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate refund amount (context-driven).

    Context keys used:
        - refund_config: Refund calculation rules
        - tax_config: Tax refund settings
        - discount_config: Discount proration settings

    Input:
        return_items: Items being returned
        original_order: Original order details

    Output:
        refund_amount: Total refund amount
        refund_breakdown: Itemized refund details
    """
    context = context or input_data.get('context', {})
    refund_config = context.get('refund_config', DEFAULT_REFUND_CONFIG)
    tax_config = context.get('tax_config', {})

    logger.info(
        "Refund calculate invoked",
        context_driven=bool(context)
    )

    return_items = input_data.get('return_items', [])
    original_order = input_data.get('original_order', {})

    # Calculate refunds
    item_refunds = []
    subtotal = 0
    tax_refund = 0
    discount_adjustment = 0

    order_discount_pct = original_order.get('discount_pct', 0)

    for item in return_items:
        price = item.get('price', 0)
        quantity = item.get('quantity', 1)
        item_total = price * quantity

        # Apply prorated discount
        if refund_config.get('prorate_discounts', True) and order_discount_pct > 0:
            discount = item_total * (order_discount_pct / 100)
            item_total -= discount
            discount_adjustment += discount

        # Calculate restocking fee
        restocking_pct = refund_config.get('restocking_fee_pct', 0)
        restocking_fee = item_total * (restocking_pct / 100)

        # Calculate tax refund
        if refund_config.get('refund_tax', True):
            tax_rate = item.get('tax_rate', 0.08)
            item_tax = (item_total - restocking_fee) * tax_rate
            tax_refund += item_tax

        item_refund = item_total - restocking_fee

        item_refunds.append({
            'sku': item.get('sku'),
            'description': item.get('description'),
            'quantity': quantity,
            'unit_price': price,
            'line_total': round(price * quantity, 2),
            'discount_applied': round(discount_adjustment, 2) if discount_adjustment else 0,
            'restocking_fee': round(restocking_fee, 2),
            'refund_amount': round(item_refund, 2)
        })

        subtotal += item_refund

    # Shipping refund
    shipping_refund = 0
    if refund_config.get('refund_shipping', False):
        shipping_refund = original_order.get('shipping_cost', 0)

    total_refund = subtotal + tax_refund + shipping_refund

    return {
        "refund_amount": round(total_refund, 2),
        "refund_breakdown": {
            "items_subtotal": round(subtotal, 2),
            "tax_refund": round(tax_refund, 2),
            "shipping_refund": round(shipping_refund, 2),
            "discount_adjustment": round(discount_adjustment, 2)
        },
        "item_refunds": item_refunds,
        "item_count": len(item_refunds),
        "calculated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "refund_calculate",
        "factory_version": "2.0.0",
        "context_keys_used": ["refund_config", "tax_config", "discount_config"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(refund_calculate(event))
