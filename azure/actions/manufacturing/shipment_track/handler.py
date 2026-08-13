"""
Shipment Track - Manufacturing Action (Context-Driven)
Track inbound and outbound shipments

Context-Driven Architecture:
- Tracking settings from playbook context.tracking_config
- Carrier configurations from context.carrier_config
- Alert rules from context.shipment_alerts
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


# Default tracking configuration
DEFAULT_TRACKING_CONFIG = {
    "auto_refresh_hours": 4,
    "alert_on_delay": True,
    "delay_threshold_hours": 24,
    "alert_on_exception": True
}

# Default carrier configuration
DEFAULT_CARRIER_CONFIG = {
    "supported_carriers": ["fedex", "ups", "usps", "freight"],
    "default_carrier": "fedex"
}


@register_factory("shipment_track")
async def shipment_track(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Track shipment status (context-driven).

    Context keys used:
        - tracking_config: Tracking refresh and alert settings
        - carrier_config: Carrier integrations
        - shipment_alerts: Alert rule configurations

    Input:
        tracking_number: Shipment tracking number
        carrier: Shipping carrier
        po_extract: Associated PO data

    Output:
        shipment_status: Current shipment status
        tracking_events: Tracking history
        estimated_delivery: Estimated delivery date
        alerts: Any shipment alerts
    """
    context = context or input_data.get('context', {})
    tracking_config = context.get('tracking_config', DEFAULT_TRACKING_CONFIG)
    carrier_config = context.get('carrier_config', DEFAULT_CARRIER_CONFIG)
    alert_rules = context.get('shipment_alerts', {})

    logger.info(
        "Shipment track invoked",
        context_driven=bool(context)
    )

    # Get tracking info
    tracking_number = input_data.get('tracking_number', '')
    carrier = input_data.get('carrier', carrier_config.get('default_carrier', 'fedex'))
    po_data = input_data.get('po_extract', {})
    shipment_type = input_data.get('shipment_type', 'inbound')

    # Validate carrier
    supported = carrier_config.get('supported_carriers', [])
    if carrier.lower() not in [c.lower() for c in supported]:
        return {
            "tracking_number": tracking_number,
            "error": f"Carrier '{carrier}' not supported",
            "supported_carriers": supported,
            "tracked_at": datetime.utcnow().isoformat(),
            "context_driven": bool(context),
            "factory_id": "shipment_track",
            "factory_version": "2.0.0",
            "context_keys_used": ["carrier_config"]
        }

    # Get tracking data (simulated)
    tracking_data = _get_tracking_data(tracking_number, carrier)

    # Check for delays and exceptions
    alerts = []
    delay_threshold = tracking_config.get('delay_threshold_hours', 24)

    if tracking_data['status'] == 'delayed':
        if tracking_config.get('alert_on_delay', True):
            alerts.append({
                'type': 'delay',
                'severity': 'warning',
                'message': f"Shipment delayed by {tracking_data.get('delay_hours', 0)} hours"
            })

    if tracking_data.get('exception'):
        if tracking_config.get('alert_on_exception', True):
            alerts.append({
                'type': 'exception',
                'severity': 'high',
                'message': tracking_data.get('exception_message', 'Delivery exception')
            })

    # Calculate on-time status
    original_eta = tracking_data.get('original_eta')
    current_eta = tracking_data.get('estimated_delivery')
    on_time = True

    if original_eta and current_eta:
        if current_eta > original_eta:
            on_time = False
            delay_days = (datetime.strptime(current_eta, '%Y-%m-%d') -
                          datetime.strptime(original_eta, '%Y-%m-%d')).days
            alerts.append({
                'type': 'schedule_change',
                'severity': 'info',
                'message': f"ETA pushed {delay_days} day(s)"
            })

    # Format tracking events
    events = tracking_data.get('events', [])

    return {
        "tracking_number": tracking_number,
        "carrier": carrier,
        "shipment_type": shipment_type,
        "shipment_status": tracking_data['status'],
        "status_description": _get_status_description(tracking_data['status']),
        "current_location": tracking_data.get('current_location'),
        "origin": tracking_data.get('origin'),
        "destination": tracking_data.get('destination'),
        "ship_date": tracking_data.get('ship_date'),
        "estimated_delivery": current_eta,
        "original_eta": original_eta,
        "on_time": on_time,
        "tracking_events": events,
        "event_count": len(events),
        "latest_event": events[0] if events else None,
        "alerts": alerts,
        "alert_count": len(alerts),
        "po_number": po_data.get('po_number'),
        "package_info": tracking_data.get('package_info'),
        "proof_of_delivery": tracking_data.get('pod'),
        "next_refresh": (datetime.utcnow() + timedelta(hours=tracking_config.get('auto_refresh_hours', 4))).isoformat(),
        "tracked_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "shipment_track",
        "factory_version": "2.0.0",
        "context_keys_used": ["tracking_config", "carrier_config", "shipment_alerts"]
    }


def _get_tracking_data(tracking_number: str, carrier: str) -> Dict:
    """Get tracking data from carrier (simulated)."""
    # Simulated tracking response
    ship_date = datetime.utcnow() - timedelta(days=3)
    eta = datetime.utcnow() + timedelta(days=2)

    events = [
        {
            'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            'location': 'Distribution Center, Chicago IL',
            'status': 'in_transit',
            'description': 'Departed facility'
        },
        {
            'timestamp': (datetime.utcnow() - timedelta(hours=12)).isoformat(),
            'location': 'Distribution Center, Chicago IL',
            'status': 'arrived',
            'description': 'Arrived at facility'
        },
        {
            'timestamp': (datetime.utcnow() - timedelta(days=1)).isoformat(),
            'location': 'Origin Facility, Los Angeles CA',
            'status': 'in_transit',
            'description': 'In transit to destination'
        },
        {
            'timestamp': (datetime.utcnow() - timedelta(days=2)).isoformat(),
            'location': 'Origin Facility, Los Angeles CA',
            'status': 'picked_up',
            'description': 'Package picked up'
        },
        {
            'timestamp': ship_date.isoformat(),
            'location': 'Shipper Facility',
            'status': 'label_created',
            'description': 'Shipping label created'
        }
    ]

    return {
        'tracking_number': tracking_number,
        'carrier': carrier,
        'status': 'in_transit',
        'current_location': 'Distribution Center, Chicago IL',
        'origin': {
            'city': 'Los Angeles',
            'state': 'CA',
            'country': 'US'
        },
        'destination': {
            'city': 'New York',
            'state': 'NY',
            'country': 'US'
        },
        'ship_date': ship_date.strftime('%Y-%m-%d'),
        'estimated_delivery': eta.strftime('%Y-%m-%d'),
        'original_eta': eta.strftime('%Y-%m-%d'),
        'events': events,
        'package_info': {
            'weight': '25 lbs',
            'dimensions': '18x12x10 in',
            'package_count': 1
        },
        'exception': None,
        'pod': None
    }


def _get_status_description(status: str) -> str:
    """Get human-readable status description."""
    descriptions = {
        'label_created': 'Label created, awaiting pickup',
        'picked_up': 'Package picked up by carrier',
        'in_transit': 'Package in transit',
        'out_for_delivery': 'Out for delivery',
        'delivered': 'Delivered',
        'delayed': 'Shipment delayed',
        'exception': 'Delivery exception'
    }
    return descriptions.get(status, status)


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(shipment_track(event))
