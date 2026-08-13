"""
COB Calculate - Healthcare Payers Action (Context-Driven)
Calculate Coordination of Benefits for dual coverage

Context-Driven Architecture:
- COB rules from playbook context.cob_config
- Priority rules from context.cob_priority_rules
- Calculation methods from context.cob_calculation_method
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


# Default COB configuration
DEFAULT_COB_CONFIG = {
    "calculation_method": "traditional",  # traditional, maintenance_of_benefits, non_duplication
    "allow_profit": False,
    "max_payment_rule": "lesser_of_allowed_or_billed"
}

# COB priority rules (NAIC model)
DEFAULT_PRIORITY_RULES = {
    "rule_order": [
        "subscriber_vs_dependent",
        "active_vs_inactive",
        "birthday_rule",
        "longer_coverage",
        "default_to_primary"
    ]
}


@register_factory("cob_calculate")
async def cob_calculate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate Coordination of Benefits (context-driven).

    Context keys used:
        - cob_config: COB calculation settings
        - cob_priority_rules: Rules for determining payment order
        - cob_calculation_method: Method for calculating secondary payment

    Input:
        claim_extract: Extracted claim data
        benefits_apply: Primary benefits result
        other_coverage: Other insurance coverage info

    Output:
        cob_applies: Whether COB applies
        payment_order: Primary/secondary determination
        secondary_payment: Calculated secondary payment
        total_coverage: Combined coverage amount
    """
    context = context or input_data.get('context', {})
    cob_config = context.get('cob_config', DEFAULT_COB_CONFIG)
    priority_rules = context.get('cob_priority_rules', DEFAULT_PRIORITY_RULES)

    logger.info(
        "COB calculate invoked",
        context_driven=bool(context)
    )

    # Get input data
    claim = input_data.get('claim_extract', {})
    primary_benefits = input_data.get('benefits_apply', {})
    other_coverage = input_data.get('other_coverage', {})

    # Check if COB applies
    cob_applies = bool(other_coverage and other_coverage.get('has_other_coverage', False))

    if not cob_applies:
        return {
            "claim_number": claim.get('claim_number'),
            "cob_applies": False,
            "payment_order": "primary_only",
            "this_plan_position": "primary",
            "allowed_amount": primary_benefits.get('allowed_amount', 0),
            "plan_payment": primary_benefits.get('plan_payment', 0),
            "member_responsibility": primary_benefits.get('member_responsibility', 0),
            "calculated_at": datetime.utcnow().isoformat(),
            "context_driven": bool(context),
            "factory_id": "cob_calculate",
            "factory_version": "2.0.0",
            "context_keys_used": ["cob_config"]
        }

    # Determine payment order
    payment_order = _determine_payment_order(
        input_data.get('member_info', {}),
        other_coverage,
        priority_rules
    )

    this_plan_position = payment_order.get('this_plan_position', 'primary')

    # Get amounts
    billed_amount = primary_benefits.get('billed_amount', 0)
    allowed_amount = primary_benefits.get('allowed_amount', 0)

    # Calculate based on position
    calculation_method = cob_config.get('calculation_method', 'traditional')

    if this_plan_position == 'primary':
        # We're primary - pay normal benefits
        plan_payment = primary_benefits.get('plan_payment', 0)
        member_responsibility = primary_benefits.get('member_responsibility', 0)
        secondary_payment = 0
        cob_savings = 0
    else:
        # We're secondary
        primary_paid = other_coverage.get('primary_paid', 0)
        primary_allowed = other_coverage.get('primary_allowed', allowed_amount)

        if calculation_method == 'traditional':
            # Traditional: Pay up to allowed amount minus primary payment
            secondary_payment = max(0, allowed_amount - primary_paid)
        elif calculation_method == 'maintenance_of_benefits':
            # MOB: Pay what we would have paid as primary, minus primary payment
            would_pay_as_primary = primary_benefits.get('plan_payment', 0)
            secondary_payment = max(0, would_pay_as_primary - primary_paid)
        else:  # non_duplication
            # Non-dup: Only pay if our allowed exceeds primary allowed
            if allowed_amount > primary_allowed:
                secondary_payment = min(allowed_amount - primary_allowed, allowed_amount - primary_paid)
            else:
                secondary_payment = 0

        # Apply non-profit rule
        if not cob_config.get('allow_profit', False):
            total_payments = primary_paid + secondary_payment
            if total_payments > billed_amount:
                secondary_payment = max(0, billed_amount - primary_paid)

        plan_payment = secondary_payment
        member_responsibility = max(0, billed_amount - primary_paid - secondary_payment)
        cob_savings = primary_benefits.get('plan_payment', 0) - secondary_payment

    total_coverage = primary_benefits.get('plan_payment', 0) if this_plan_position == 'primary' else (
        other_coverage.get('primary_paid', 0) + plan_payment
    )

    return {
        "claim_number": claim.get('claim_number'),
        "cob_applies": True,
        "payment_order": payment_order.get('order', []),
        "this_plan_position": this_plan_position,
        "determination_reason": payment_order.get('reason', 'default'),
        "calculation_method": calculation_method,
        "billed_amount": round(billed_amount, 2),
        "allowed_amount": round(allowed_amount, 2),
        "primary_paid": round(other_coverage.get('primary_paid', 0) if this_plan_position == 'secondary' else plan_payment, 2),
        "secondary_payment": round(secondary_payment if this_plan_position == 'secondary' else 0, 2),
        "plan_payment": round(plan_payment, 2),
        "member_responsibility": round(member_responsibility, 2),
        "total_coverage": round(total_coverage, 2),
        "cob_savings": round(cob_savings if this_plan_position == 'secondary' else 0, 2),
        "calculated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "cob_calculate",
        "factory_version": "2.0.0",
        "context_keys_used": ["cob_config", "cob_priority_rules", "cob_calculation_method"]
    }


def _determine_payment_order(member: Dict, other_coverage: Dict, priority_rules: Dict) -> Dict:
    """Determine primary/secondary payment order using NAIC rules."""

    this_plan = member.get('coverage_info', {})
    other_plan = other_coverage.get('other_plan_info', {})

    # Apply rules in order
    for rule in priority_rules.get('rule_order', []):
        if rule == 'subscriber_vs_dependent':
            # Subscriber's plan is primary over dependent's plan
            if this_plan.get('relationship') == 'self' and other_plan.get('relationship') != 'self':
                return {
                    'this_plan_position': 'primary',
                    'order': ['this_plan', 'other_plan'],
                    'reason': 'subscriber_vs_dependent'
                }
            elif other_plan.get('relationship') == 'self' and this_plan.get('relationship') != 'self':
                return {
                    'this_plan_position': 'secondary',
                    'order': ['other_plan', 'this_plan'],
                    'reason': 'subscriber_vs_dependent'
                }

        elif rule == 'birthday_rule':
            # For dependents, parent with earlier birthday is primary
            this_bday = this_plan.get('subscriber_birthday', '12-31')
            other_bday = other_plan.get('subscriber_birthday', '12-31')

            if this_bday < other_bday:
                return {
                    'this_plan_position': 'primary',
                    'order': ['this_plan', 'other_plan'],
                    'reason': 'birthday_rule'
                }
            elif other_bday < this_bday:
                return {
                    'this_plan_position': 'secondary',
                    'order': ['other_plan', 'this_plan'],
                    'reason': 'birthday_rule'
                }

    # Default to primary
    return {
        'this_plan_position': 'primary',
        'order': ['this_plan', 'other_plan'],
        'reason': 'default'
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(cob_calculate(event))
