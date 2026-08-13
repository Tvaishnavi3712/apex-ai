"""
Carrier Select - Supply Chain Action (Context-Driven)
Select optimal carrier for shipments

Context-Driven Architecture:
- Carrier preferences from playbook context.carrier_config
- Rate cards from context.rate_config
- Service level requirements from context.service_config
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


DEFAULT_CARRIER_CONFIG = {
    "preferred_carriers": ["fedex", "ups", "usps"],
    "selection_criteria": "lowest_cost",
    "require_tracking": True,
    "insurance_threshold": 500
}


@register_factory("carrier_select")
async def carrier_select(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Select optimal carrier (context-driven).

    Context keys used:
        - carrier_config: Carrier preferences
        - rate_config: Carrier rate cards
        - service_config: Service level requirements

    Input:
        shipment_details: Shipment information
        service_level: Required service level

    Output:
        selected_carrier: Recommended carrier
        carrier_options: All carrier options with rates
        estimated_cost: Estimated shipping cost
    """
    context = context or input_data.get('context', {})
    carrier_config = context.get('carrier_config', DEFAULT_CARRIER_CONFIG)
    rate_config = context.get('rate_config', {})
    service_config = context.get('service_config', {})

    logger.info(
        "Carrier select invoked",
        context_driven=bool(context)
    )

    shipment = input_data.get('shipment_details', {})
    service_level = input_data.get('service_level', 'standard')

    weight = shipment.get('weight_lbs', 5)
    destination_zip = shipment.get('destination_zip', '10001')
    declared_value = shipment.get('declared_value', 0)

    preferred = carrier_config.get('preferred_carriers', ['fedex', 'ups'])
    criteria = carrier_config.get('selection_criteria', 'lowest_cost')

    # Get carrier options (simulated)
    carrier_options = []
    for carrier in preferred:
        rate = _get_carrier_rate(carrier, weight, destination_zip, service_level, rate_config)
        transit_days = rate.get('transit_days', 5)

        carrier_options.append({
            'carrier': carrier,
            'service': rate.get('service_name'),
            'rate': rate.get('rate'),
            'transit_days': transit_days,
            'estimated_delivery': (datetime.utcnow() + timedelta(days=transit_days)).strftime('%Y-%m-%d'),
            'tracking_available': True,
            'insurance_included': declared_value <= carrier_config.get('insurance_threshold', 500)
        })

    # Sort by criteria
    if criteria == 'lowest_cost':
        carrier_options.sort(key=lambda x: x['rate'])
    elif criteria == 'fastest':
        carrier_options.sort(key=lambda x: x['transit_days'])

    selected = carrier_options[0] if carrier_options else None

    return {
        "selected_carrier": selected['carrier'] if selected else None,
        "selected_service": selected['service'] if selected else None,
        "estimated_cost": selected['rate'] if selected else 0,
        "estimated_delivery": selected['estimated_delivery'] if selected else None,
        "carrier_options": carrier_options,
        "options_count": len(carrier_options),
        "selection_criteria": criteria,
        "service_level_requested": service_level,
        "selected_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "carrier_select",
        "factory_version": "2.0.0",
        "context_keys_used": ["carrier_config", "rate_config", "service_config"]
    }


def _get_carrier_rate(carrier: str, weight: float, destination: str,
                      service: str, rate_config: Dict) -> Dict:
    """Get carrier rate (simulated)."""
    base_rates = {
        'fedex': {'ground': 8.50, 'express': 22.00, 'overnight': 45.00},
        'ups': {'ground': 9.00, 'express': 21.00, 'overnight': 48.00},
        'usps': {'ground': 6.50, 'express': 18.00, 'overnight': 35.00}
    }

    service_map = {
        'standard': 'ground',
        'expedited': 'express',
        'priority': 'overnight'
    }

    svc = service_map.get(service, 'ground')
    base = base_rates.get(carrier, {}).get(svc, 10.00)
    rate = base + (weight * 0.50)

    transit = {'ground': 5, 'express': 2, 'overnight': 1}

    return {
        'rate': round(rate, 2),
        'service_name': f"{carrier.upper()} {svc.title()}",
        'transit_days': transit.get(svc, 5)
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(carrier_select(event))
