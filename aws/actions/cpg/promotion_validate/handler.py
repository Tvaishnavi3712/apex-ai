"""
Promotion Validate - CPG Action (Context-Driven)
Validate trade promotions and deals

Context-Driven Architecture:
- Promotion rules from playbook context.promotion_config
- Budget constraints from context.budget_config
- Retailer rules from context.retailer_config
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


DEFAULT_PROMOTION_CONFIG = {
    "max_discount_pct": 50,
    "min_margin_pct": 15,
    "require_approval_above": 10000,
    "valid_promotion_types": ["tpr", "bogo", "display", "feature"]
}


@register_factory("promotion_validate")
async def promotion_validate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate trade promotion (context-driven).

    Context keys used:
        - promotion_config: Promotion validation rules
        - budget_config: Budget constraints
        - retailer_config: Retailer-specific rules

    Input:
        promotion_details: Promotion information
        products: Products in promotion
        retailer: Retailer information

    Output:
        validation_passed: Whether promotion is valid
        validation_results: Detailed validation results
        budget_impact: Budget impact analysis
    """
    context = context or input_data.get('context', {})
    promotion_config = context.get('promotion_config', DEFAULT_PROMOTION_CONFIG)
    budget_config = context.get('budget_config', {})
    retailer_config = context.get('retailer_config', {})

    logger.info(
        "Promotion validate invoked",
        context_driven=bool(context)
    )

    promotion = input_data.get('promotion_details', {})
    products = input_data.get('products', [])
    retailer = input_data.get('retailer', {})

    promo_type = promotion.get('type', 'tpr')
    discount_pct = promotion.get('discount_pct', 0)
    spend_amount = promotion.get('spend_amount', 0)
    start_date = promotion.get('start_date')
    end_date = promotion.get('end_date')

    # Validation checks
    validation_results = {}
    issues = []

    # Check promotion type
    valid_types = promotion_config.get('valid_promotion_types', [])
    validation_results['promotion_type'] = {
        'check': 'Promotion type',
        'passed': promo_type in valid_types,
        'type': promo_type
    }
    if promo_type not in valid_types:
        issues.append(f'Invalid promotion type: {promo_type}')

    # Check discount limits
    max_discount = promotion_config.get('max_discount_pct', 50)
    validation_results['discount_limit'] = {
        'check': 'Discount limit',
        'passed': discount_pct <= max_discount,
        'discount_pct': discount_pct,
        'max_allowed': max_discount
    }
    if discount_pct > max_discount:
        issues.append(f'Discount {discount_pct}% exceeds limit {max_discount}%')

    # Check margin
    min_margin = promotion_config.get('min_margin_pct', 15)
    estimated_margin = _calculate_margin(products, discount_pct)
    validation_results['margin_check'] = {
        'check': 'Minimum margin',
        'passed': estimated_margin >= min_margin,
        'estimated_margin': estimated_margin,
        'minimum_required': min_margin
    }
    if estimated_margin < min_margin:
        issues.append(f'Margin {estimated_margin}% below minimum {min_margin}%')

    # Check budget
    available_budget = budget_config.get('available_budget', 100000)
    validation_results['budget_check'] = {
        'check': 'Budget availability',
        'passed': spend_amount <= available_budget,
        'spend_amount': spend_amount,
        'available': available_budget
    }
    if spend_amount > available_budget:
        issues.append(f'Spend ${spend_amount} exceeds budget ${available_budget}')

    # Check approval requirement
    approval_threshold = promotion_config.get('require_approval_above', 10000)
    requires_approval = spend_amount > approval_threshold

    # Overall validation
    all_passed = all(r.get('passed', True) for r in validation_results.values())

    # Calculate ROI estimate
    roi_estimate = _estimate_roi(promotion, products)

    return {
        "promotion_id": promotion.get('promotion_id'),
        "retailer": retailer.get('name'),
        "validation_passed": all_passed,
        "validation_results": validation_results,
        "issues": issues,
        "issue_count": len(issues),
        "requires_approval": requires_approval,
        "approval_threshold": approval_threshold,
        "budget_impact": {
            "spend_amount": spend_amount,
            "available_budget": available_budget,
            "remaining_after": available_budget - spend_amount
        },
        "roi_estimate": roi_estimate,
        "estimated_margin": estimated_margin,
        "validated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "promotion_validate",
        "factory_version": "2.0.0",
        "context_keys_used": ["promotion_config", "budget_config", "retailer_config"]
    }


def _calculate_margin(products: List[Dict], discount_pct: float) -> float:
    """Calculate estimated margin after promotion."""
    base_margin = 35  # Base margin percentage
    return max(0, base_margin - discount_pct)


def _estimate_roi(promotion: Dict, products: List[Dict]) -> Dict:
    """Estimate promotion ROI."""
    spend = promotion.get('spend_amount', 0)
    lift_pct = promotion.get('expected_lift_pct', 20)

    base_revenue = sum(p.get('base_revenue', 1000) for p in products)
    incremental_revenue = base_revenue * (lift_pct / 100)

    roi = ((incremental_revenue - spend) / spend * 100) if spend > 0 else 0

    return {
        'spend': spend,
        'expected_lift_pct': lift_pct,
        'incremental_revenue': round(incremental_revenue, 2),
        'estimated_roi_pct': round(roi, 1)
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(promotion_validate(event))
