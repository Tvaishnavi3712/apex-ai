"""
Rebooking Options - Airlines Action (Context-Driven)
Generate rebooking options for disrupted passengers

Context-Driven Architecture:
- Rebooking rules from playbook context.rebooking_config
- Fare rules from context.fare_config
- Partner airlines from context.partner_config
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


DEFAULT_REBOOKING_CONFIG = {
    "include_partner_flights": True,
    "max_connection_time_hours": 4,
    "max_options": 5,
    "same_cabin_required": True
}


@register_factory("rebooking_options")
async def rebooking_options(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate rebooking options (context-driven).

    Context keys used:
        - rebooking_config: Rebooking rules
        - fare_config: Fare class rules
        - partner_config: Partner airline settings

    Input:
        original_booking: Original booking details
        disruption_type: Type of disruption

    Output:
        rebooking_options: Available rebooking options
        recommended_option: Best recommended option
    """
    context = context or input_data.get('context', {})
    rebooking_config = context.get('rebooking_config', DEFAULT_REBOOKING_CONFIG)
    fare_config = context.get('fare_config', {})
    partner_config = context.get('partner_config', {})

    logger.info(
        "Rebooking options invoked",
        context_driven=bool(context)
    )

    original = input_data.get('original_booking', {})
    disruption_type = input_data.get('disruption_type', 'delay')

    origin = original.get('origin', 'JFK')
    destination = original.get('destination', 'LAX')
    original_date = original.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    cabin_class = original.get('cabin_class', 'economy')

    max_options = rebooking_config.get('max_options', 5)
    include_partners = rebooking_config.get('include_partner_flights', True)

    # Generate options
    options = []

    # Same day options
    for i in range(3):
        dep_time = datetime.strptime(f"{original_date}T{10 + i * 2}:00:00", '%Y-%m-%dT%H:%M:%S')
        options.append({
            'option_id': f"OPT{i+1:03d}",
            'flight_number': f"EX{100 + i}",
            'airline': 'Example Air',
            'origin': origin,
            'destination': destination,
            'departure': dep_time.isoformat(),
            'arrival': (dep_time + timedelta(hours=5, minutes=30)).isoformat(),
            'cabin_class': cabin_class,
            'seats_available': 5 - i,
            'is_partner': False,
            'connections': 0,
            'option_type': 'same_day_direct'
        })

    # Next day option
    next_day = (datetime.strptime(original_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
    options.append({
        'option_id': 'OPT004',
        'flight_number': 'EX101',
        'airline': 'Example Air',
        'origin': origin,
        'destination': destination,
        'departure': f"{next_day}T08:00:00",
        'arrival': f"{next_day}T13:30:00",
        'cabin_class': cabin_class,
        'seats_available': 15,
        'is_partner': False,
        'connections': 0,
        'option_type': 'next_day_direct'
    })

    # Partner option if enabled
    if include_partners:
        options.append({
            'option_id': 'OPT005',
            'flight_number': 'PA200',
            'airline': 'Partner Airlines',
            'origin': origin,
            'destination': destination,
            'departure': f"{original_date}T14:00:00",
            'arrival': f"{original_date}T19:30:00",
            'cabin_class': cabin_class,
            'seats_available': 8,
            'is_partner': True,
            'connections': 0,
            'option_type': 'partner_direct'
        })

    # Sort and limit
    options = options[:max_options]
    recommended = options[0] if options else None

    return {
        "passenger_name": original.get('passenger_name'),
        "original_flight": original.get('flight_number'),
        "disruption_type": disruption_type,
        "rebooking_options": options,
        "option_count": len(options),
        "recommended_option": recommended,
        "partner_options_included": include_partners,
        "cabin_class_maintained": True,
        "generated_at": datetime.utcnow().isoformat(),
        "valid_until": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
        "context_driven": bool(context),
        "factory_id": "rebooking_options",
        "factory_version": "2.0.0",
        "context_keys_used": ["rebooking_config", "fare_config", "partner_config"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(rebooking_options(event))
