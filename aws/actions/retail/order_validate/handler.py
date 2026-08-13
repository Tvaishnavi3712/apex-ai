"""
Order Validate - Retail Action (Context-Driven)
Validate orders before processing

Context-Driven Architecture:
- Validation rules from playbook context.order_validation
- Fraud rules from context.fraud_config
- Inventory rules from context.inventory_config
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


# Default order validation rules
DEFAULT_ORDER_VALIDATION = {
    "max_order_total": 10000,
    "max_quantity_per_item": 10,
    "require_shipping_address": True,
    "validate_payment": True
}

# Default fraud configuration
DEFAULT_FRAUD_CONFIG = {
    "enabled": True,
    "high_risk_threshold": 70,
    "auto_decline_threshold": 90,
    "check_velocity": True,
    "check_address_mismatch": True
}


@register_factory("order_validate")
async def order_validate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate order before processing (context-driven).

    Context keys used:
        - order_validation: Order validation rules
        - fraud_config: Fraud detection settings
        - inventory_config: Inventory check settings

    Input:
        order_data: Order information to validate
        customer_info: Customer details
        payment_info: Payment information

    Output:
        order_valid: Whether order passed validation
        validation_results: Detailed validation results
        fraud_score: Fraud risk score
    """
    context = context or input_data.get('context', {})
    validation_rules = context.get('order_validation', DEFAULT_ORDER_VALIDATION)
    fraud_config = context.get('fraud_config', DEFAULT_FRAUD_CONFIG)
    inventory_config = context.get('inventory_config', {})

    logger.info(
        "Order validate invoked",
        context_driven=bool(context)
    )

    # Get input data
    order_data = input_data.get('order_data', {})
    customer_info = input_data.get('customer_info', {})
    payment_info = input_data.get('payment_info', {})

    order_id = order_data.get('order_id', '')
    items = order_data.get('items', [])

    # Perform validations
    validation_results = {}
    issues = []

    # Order total validation
    order_total = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
    max_total = validation_rules.get('max_order_total', 10000)

    validation_results['order_total'] = {
        'check': 'Order total limit',
        'passed': order_total <= max_total,
        'value': order_total,
        'limit': max_total
    }
    if order_total > max_total:
        issues.append(f'Order total ${order_total} exceeds limit ${max_total}')

    # Quantity validation
    max_qty = validation_rules.get('max_quantity_per_item', 10)
    qty_valid = all(item.get('quantity', 1) <= max_qty for item in items)

    validation_results['item_quantities'] = {
        'check': 'Item quantity limits',
        'passed': qty_valid,
        'max_allowed': max_qty
    }
    if not qty_valid:
        issues.append(f'Item quantity exceeds limit of {max_qty}')

    # Shipping address validation
    if validation_rules.get('require_shipping_address', True):
        shipping = order_data.get('shipping_address', {})
        address_valid = all([
            shipping.get('street'),
            shipping.get('city'),
            shipping.get('state'),
            shipping.get('zip')
        ])
        validation_results['shipping_address'] = {
            'check': 'Shipping address',
            'passed': address_valid,
            'message': 'Valid' if address_valid else 'Incomplete address'
        }
        if not address_valid:
            issues.append('Incomplete shipping address')

    # Payment validation
    if validation_rules.get('validate_payment', True):
        payment_valid = _validate_payment(payment_info)
        validation_results['payment'] = {
            'check': 'Payment validation',
            'passed': payment_valid['valid'],
            'message': payment_valid['message']
        }
        if not payment_valid['valid']:
            issues.append(payment_valid['message'])

    # Inventory check
    inventory_results = _check_inventory(items, inventory_config)
    validation_results['inventory'] = {
        'check': 'Inventory availability',
        'passed': inventory_results['all_available'],
        'unavailable_items': inventory_results['unavailable']
    }
    if not inventory_results['all_available']:
        issues.extend([f"Item {i} out of stock" for i in inventory_results['unavailable']])

    # Fraud check
    fraud_score = 0
    fraud_result = {'risk_level': 'low'}

    if fraud_config.get('enabled', True):
        fraud_result = _calculate_fraud_score(
            order_data,
            customer_info,
            payment_info,
            fraud_config
        )
        fraud_score = fraud_result['score']

        validation_results['fraud'] = {
            'check': 'Fraud detection',
            'passed': fraud_score < fraud_config.get('auto_decline_threshold', 90),
            'score': fraud_score,
            'risk_level': fraud_result['risk_level'],
            'flags': fraud_result.get('flags', [])
        }

        if fraud_score >= fraud_config.get('auto_decline_threshold', 90):
            issues.append('High fraud risk - auto declined')

    # Determine overall result
    all_passed = all(r.get('passed', True) for r in validation_results.values())
    high_risk = fraud_score >= fraud_config.get('high_risk_threshold', 70)

    if all_passed and not high_risk:
        validation_status = 'approved'
    elif all_passed and high_risk:
        validation_status = 'review_required'
    else:
        validation_status = 'declined'

    return {
        "order_id": order_id,
        "order_valid": all_passed,
        "validation_status": validation_status,
        "validation_results": validation_results,
        "issues": issues,
        "issue_count": len(issues),
        "order_total": round(order_total, 2),
        "item_count": len(items),
        "fraud_score": fraud_score,
        "fraud_risk_level": fraud_result['risk_level'],
        "requires_review": validation_status == 'review_required',
        "next_steps": _get_next_steps(validation_status),
        "validated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "order_validate",
        "factory_version": "2.0.0",
        "context_keys_used": ["order_validation", "fraud_config", "inventory_config"]
    }


def _validate_payment(payment_info: Dict) -> Dict:
    """Validate payment information."""
    payment_type = payment_info.get('type', '')

    if payment_type == 'credit_card':
        if not payment_info.get('card_token'):
            return {'valid': False, 'message': 'Missing payment token'}
        return {'valid': True, 'message': 'Payment validated'}

    elif payment_type == 'paypal':
        if not payment_info.get('paypal_id'):
            return {'valid': False, 'message': 'Missing PayPal ID'}
        return {'valid': True, 'message': 'PayPal validated'}

    return {'valid': True, 'message': 'Payment accepted'}


def _check_inventory(items: List[Dict], config: Dict) -> Dict:
    """Check inventory availability."""
    unavailable = []

    for item in items:
        # Simulated inventory check
        sku = item.get('sku', '')
        qty = item.get('quantity', 1)

        # Mock: items with SKU ending in 'X' are out of stock
        if sku.endswith('X'):
            unavailable.append(sku)

    return {
        'all_available': len(unavailable) == 0,
        'unavailable': unavailable
    }


def _calculate_fraud_score(order: Dict, customer: Dict,
                           payment: Dict, config: Dict) -> Dict:
    """Calculate fraud risk score."""
    score = 0
    flags = []

    # New customer high value order
    if customer.get('is_new', True) and order.get('total', 0) > 500:
        score += 20
        flags.append('new_customer_high_value')

    # Address mismatch
    if config.get('check_address_mismatch', True):
        billing = payment.get('billing_address', {})
        shipping = order.get('shipping_address', {})
        if billing and shipping and billing.get('zip') != shipping.get('zip'):
            score += 15
            flags.append('address_mismatch')

    # Velocity check
    if config.get('check_velocity', True):
        recent_orders = customer.get('orders_last_24h', 0)
        if recent_orders > 3:
            score += 25
            flags.append('high_velocity')

    # Risk level
    if score >= 70:
        risk_level = 'high'
    elif score >= 40:
        risk_level = 'medium'
    else:
        risk_level = 'low'

    return {
        'score': score,
        'risk_level': risk_level,
        'flags': flags
    }


def _get_next_steps(status: str) -> List[str]:
    """Get next steps based on validation status."""
    steps = {
        'approved': ['Process payment', 'Fulfill order', 'Send confirmation'],
        'review_required': ['Manual review required', 'Contact customer if needed', 'Approve or decline'],
        'declined': ['Notify customer', 'Provide reason', 'Suggest resolution']
    }
    return steps.get(status, [])


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(order_validate(event))
