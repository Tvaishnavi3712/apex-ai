"""
Return Process - Retail Action (Context-Driven)
Process customer returns and exchanges

Context-Driven Architecture:
- Return policies from playbook context.return_policy
- Refund rules from context.refund_config
- Restocking settings from context.restocking_config
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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


# Default return policy
DEFAULT_RETURN_POLICY = {
    "return_window_days": 30,
    "require_receipt": True,
    "allow_exchange": True,
    "restocking_fee_pct": 0,
    "non_returnable_categories": ["final_sale", "intimate", "hazmat"]
}

# Default refund configuration
DEFAULT_REFUND_CONFIG = {
    "refund_methods": ["original_payment", "store_credit", "gift_card"],
    "default_method": "original_payment",
    "instant_refund_threshold": 100
}


@register_factory("return_process")
async def return_process(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process customer return (context-driven).

    Context keys used:
        - return_policy: Return window and rules
        - refund_config: Refund method settings
        - restocking_config: Restocking fee rules

    Input:
        order_info: Original order information
        return_items: Items being returned
        return_reason: Reason for return

    Output:
        return_approved: Whether return is approved
        return_details: Return processing details
        refund_amount: Calculated refund amount
    """
    context = context or input_data.get('context', {})
    return_policy = context.get('return_policy', DEFAULT_RETURN_POLICY)
    refund_config = context.get('refund_config', DEFAULT_REFUND_CONFIG)
    restocking_config = context.get('restocking_config', {})

    logger.info(
        "Return process invoked",
        context_driven=bool(context)
    )

    # Get input data
    order_info = input_data.get('order_info', {})
    return_items = input_data.get('return_items', [])
    return_reason = input_data.get('return_reason', '')

    order_number = order_info.get('order_number', '')
    order_date = order_info.get('order_date', '')

    # Generate return number
    return_number = f"RET{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Check return eligibility
    eligibility = _check_return_eligibility(
        order_info,
        return_items,
        return_policy
    )

    if not eligibility['eligible']:
        return {
            "return_number": return_number,
            "return_approved": False,
            "rejection_reason": eligibility['reason'],
            "order_number": order_number,
            "processed_at": datetime.utcnow().isoformat(),
            "context_driven": bool(context),
            "factory_id": "return_process",
            "factory_version": "2.0.0",
            "context_keys_used": ["return_policy"]
        }

    # Process each return item
    processed_items = []
    total_refund = 0
    total_restocking_fee = 0

    for item in return_items:
        item_result = _process_return_item(
            item,
            return_reason,
            return_policy,
            restocking_config
        )
        processed_items.append(item_result)
        total_refund += item_result['refund_amount']
        total_restocking_fee += item_result.get('restocking_fee', 0)

    # Determine refund method
    refund_method = input_data.get('preferred_refund_method')
    available_methods = refund_config.get('refund_methods', ['store_credit'])

    if refund_method and refund_method in available_methods:
        selected_method = refund_method
    else:
        selected_method = refund_config.get('default_method', 'store_credit')

    # Check instant refund eligibility
    instant_threshold = refund_config.get('instant_refund_threshold', 100)
    instant_refund = total_refund <= instant_threshold

    # Build return record
    return_record = {
        'return_number': return_number,
        'order_number': order_number,
        'return_date': datetime.utcnow().strftime('%Y-%m-%d'),
        'return_reason': return_reason,
        'items': processed_items,
        'subtotal': sum(i.get('original_price', 0) for i in processed_items),
        'restocking_fees': total_restocking_fee,
        'refund_amount': total_refund,
        'refund_method': selected_method,
        'status': 'approved'
    }

    # Generate shipping label if needed
    shipping_label = None
    if input_data.get('needs_shipping', True):
        shipping_label = {
            'carrier': 'ups',
            'tracking_number': f"1Z{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'label_url': f"https://labels.example.com/{return_number}"
        }

    return {
        "return_number": return_number,
        "return_approved": True,
        "order_number": order_number,
        "return_record": return_record,
        "items_returned": len(processed_items),
        "subtotal": return_record['subtotal'],
        "restocking_fees": total_restocking_fee,
        "refund_amount": round(total_refund, 2),
        "refund_method": selected_method,
        "instant_refund": instant_refund,
        "refund_status": "processed" if instant_refund else "pending_receipt",
        "shipping_label": shipping_label,
        "return_deadline": (datetime.utcnow() + timedelta(days=14)).strftime('%Y-%m-%d'),
        "instructions": _get_return_instructions(shipping_label),
        "processed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "return_process",
        "factory_version": "2.0.0",
        "context_keys_used": ["return_policy", "refund_config", "restocking_config"]
    }


def _check_return_eligibility(order_info: Dict, items: List[Dict], policy: Dict) -> Dict:
    """Check if return is eligible."""
    order_date = order_info.get('order_date', '')
    return_window = policy.get('return_window_days', 30)
    non_returnable = policy.get('non_returnable_categories', [])

    # Check return window
    if order_date:
        try:
            order_dt = datetime.strptime(order_date, '%Y-%m-%d')
            days_since = (datetime.utcnow() - order_dt).days
            if days_since > return_window:
                return {
                    'eligible': False,
                    'reason': f'Return window of {return_window} days has passed'
                }
        except ValueError:
            pass

    # Check for non-returnable items
    for item in items:
        category = item.get('category', '')
        if category in non_returnable:
            return {
                'eligible': False,
                'reason': f'Item category "{category}" is not returnable'
            }

    return {'eligible': True, 'reason': None}


def _process_return_item(item: Dict, reason: str, policy: Dict, restocking_config: Dict) -> Dict:
    """Process individual return item."""
    original_price = item.get('price', 0)
    quantity = item.get('quantity', 1)

    # Calculate restocking fee
    restocking_pct = policy.get('restocking_fee_pct', 0)

    # Defective items don't get restocking fee
    if reason.lower() in ['defective', 'damaged', 'wrong_item']:
        restocking_fee = 0
    else:
        restocking_fee = original_price * quantity * (restocking_pct / 100)

    refund_amount = (original_price * quantity) - restocking_fee

    return {
        'item_id': item.get('item_id'),
        'sku': item.get('sku'),
        'description': item.get('description'),
        'quantity': quantity,
        'original_price': original_price,
        'restocking_fee': round(restocking_fee, 2),
        'refund_amount': round(refund_amount, 2),
        'condition': item.get('condition', 'new'),
        'disposition': 'restock' if item.get('condition') == 'new' else 'liquidate'
    }


def _get_return_instructions(shipping_label: Dict) -> List[str]:
    """Get return instructions."""
    if shipping_label:
        return [
            'Print the prepaid shipping label',
            'Pack items securely in original packaging if available',
            'Drop off at any UPS location',
            'Keep tracking number for your records'
        ]
    return [
        'Return items to your nearest store location',
        'Bring this return confirmation and original receipt',
        'Refund will be processed at time of return'
    ]


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(return_process(event))
