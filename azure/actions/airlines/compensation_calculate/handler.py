"""
Compensation Calculate - Airlines Action (Context-Driven)
Calculate passenger compensation for disruptions

Context-Driven Architecture:
- Compensation rules from playbook context.compensation_config
- Regulatory requirements from context.regulatory_config
- Tier benefits from context.loyalty_config
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


DEFAULT_COMPENSATION_CONFIG = {
    "delay_thresholds": {
        "minor": {"hours": 2, "voucher": 50},
        "moderate": {"hours": 4, "voucher": 150},
        "major": {"hours": 6, "voucher": 300}
    },
    "cancellation_compensation": 400,
    "overnight_hotel_limit": 200,
    "meal_voucher": 25
}


@register_factory("compensation_calculate")
async def compensation_calculate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate passenger compensation (context-driven).

    Context keys used:
        - compensation_config: Compensation rules
        - regulatory_config: Regional regulations
        - loyalty_config: Loyalty tier multipliers

    Input:
        disruption_details: Details of the disruption
        passenger_info: Passenger information
        booking_info: Original booking details

    Output:
        compensation_amount: Total compensation
        compensation_breakdown: Itemized compensation
        eligibility: Compensation eligibility details
    """
    context = context or input_data.get('context', {})
    comp_config = context.get('compensation_config', DEFAULT_COMPENSATION_CONFIG)
    regulatory_config = context.get('regulatory_config', {})
    loyalty_config = context.get('loyalty_config', {})

    logger.info(
        "Compensation calculate invoked",
        context_driven=bool(context)
    )

    disruption = input_data.get('disruption_details', {})
    passenger = input_data.get('passenger_info', {})
    booking = input_data.get('booking_info', {})

    disruption_type = disruption.get('type', 'delay')
    delay_hours = disruption.get('delay_hours', 0)
    is_overnight = disruption.get('requires_overnight', False)

    # Calculate base compensation
    compensation = []
    total = 0

    if disruption_type == 'cancellation':
        amount = comp_config.get('cancellation_compensation', 400)
        compensation.append({
            'type': 'cancellation_voucher',
            'amount': amount,
            'description': 'Flight cancellation compensation'
        })
        total += amount

    elif disruption_type == 'delay':
        thresholds = comp_config.get('delay_thresholds', {})

        if delay_hours >= 6:
            amount = thresholds.get('major', {}).get('voucher', 300)
            level = 'major'
        elif delay_hours >= 4:
            amount = thresholds.get('moderate', {}).get('voucher', 150)
            level = 'moderate'
        elif delay_hours >= 2:
            amount = thresholds.get('minor', {}).get('voucher', 50)
            level = 'minor'
        else:
            amount = 0
            level = 'none'

        if amount > 0:
            compensation.append({
                'type': 'delay_voucher',
                'amount': amount,
                'description': f'{level.title()} delay compensation ({delay_hours}h)'
            })
            total += amount

    # Meal voucher
    if delay_hours >= 2:
        meal_amount = comp_config.get('meal_voucher', 25)
        meals = int(delay_hours / 4) + 1
        total_meals = meal_amount * meals
        compensation.append({
            'type': 'meal_voucher',
            'amount': total_meals,
            'description': f'{meals} meal voucher(s)'
        })
        total += total_meals

    # Overnight accommodation
    if is_overnight:
        hotel_limit = comp_config.get('overnight_hotel_limit', 200)
        compensation.append({
            'type': 'hotel_accommodation',
            'amount': hotel_limit,
            'description': 'Overnight hotel accommodation'
        })
        total += hotel_limit

    # Loyalty tier multiplier
    loyalty_tier = passenger.get('loyalty_tier', 'standard')
    multiplier = loyalty_config.get('tier_multipliers', {}).get(loyalty_tier, 1.0)

    if multiplier > 1.0:
        bonus = total * (multiplier - 1)
        compensation.append({
            'type': 'loyalty_bonus',
            'amount': round(bonus, 2),
            'description': f'{loyalty_tier.title()} tier bonus'
        })
        total += bonus

    # Check regulatory requirements
    regulatory_min = regulatory_config.get('minimum_compensation', 0)
    if total < regulatory_min:
        compensation.append({
            'type': 'regulatory_adjustment',
            'amount': regulatory_min - total,
            'description': 'Regulatory minimum adjustment'
        })
        total = regulatory_min

    return {
        "passenger_name": passenger.get('name'),
        "pnr": booking.get('pnr'),
        "flight_number": booking.get('flight_number'),
        "disruption_type": disruption_type,
        "delay_hours": delay_hours,
        "compensation_eligible": total > 0,
        "compensation_amount": round(total, 2),
        "compensation_breakdown": compensation,
        "loyalty_tier": loyalty_tier,
        "tier_multiplier": multiplier,
        "regulatory_minimum": regulatory_min,
        "delivery_method": "email",
        "calculated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "compensation_calculate",
        "factory_version": "2.0.0",
        "context_keys_used": ["compensation_config", "regulatory_config", "loyalty_config"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(compensation_calculate(event))
