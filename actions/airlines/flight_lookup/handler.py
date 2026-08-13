"""
Flight Lookup - Airlines Action (Context-Driven)
Look up flight information and status

Context-Driven Architecture:
- Flight data sources from playbook context.flight_config
- Status mappings from context.status_config
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


DEFAULT_FLIGHT_CONFIG = {
    "include_weather": True,
    "include_connections": True,
    "cache_minutes": 5
}


@register_factory("flight_lookup")
async def flight_lookup(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Look up flight information (context-driven).

    Context keys used:
        - flight_config: Flight data settings
        - status_config: Status code mappings

    Input:
        flight_number: Flight number to look up
        date: Flight date

    Output:
        flight_info: Flight details
        status: Current flight status
        delays: Any delay information
    """
    context = context or input_data.get('context', {})
    flight_config = context.get('flight_config', DEFAULT_FLIGHT_CONFIG)
    status_config = context.get('status_config', {})

    logger.info(
        "Flight lookup invoked",
        context_driven=bool(context)
    )

    flight_number = input_data.get('flight_number', '')
    flight_date = input_data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))

    # Simulated flight lookup
    flight_info = {
        'flight_number': flight_number,
        'airline': 'Example Air',
        'aircraft_type': 'Boeing 737-800',
        'origin': {
            'code': 'JFK',
            'city': 'New York',
            'terminal': 'T4',
            'gate': 'B22'
        },
        'destination': {
            'code': 'LAX',
            'city': 'Los Angeles',
            'terminal': 'T6',
            'gate': 'A15'
        },
        'scheduled_departure': f"{flight_date}T08:00:00",
        'scheduled_arrival': f"{flight_date}T11:30:00",
        'actual_departure': f"{flight_date}T08:15:00",
        'estimated_arrival': f"{flight_date}T11:45:00",
        'duration_minutes': 330,
        'distance_miles': 2475
    }

    # Determine status
    status = 'on_time'
    delay_minutes = 15
    delay_reason = None

    if delay_minutes > 30:
        status = 'delayed'
        delay_reason = 'Weather conditions at destination'
    elif delay_minutes > 0:
        status = 'slightly_delayed'

    # Weather info
    weather = None
    if flight_config.get('include_weather', True):
        weather = {
            'origin': {'condition': 'Clear', 'temp_f': 72},
            'destination': {'condition': 'Partly Cloudy', 'temp_f': 68}
        }

    # Connection info
    connections = []
    if flight_config.get('include_connections', True):
        connections = _get_connections(flight_number, flight_date)

    return {
        "flight_number": flight_number,
        "flight_date": flight_date,
        "flight_info": flight_info,
        "status": status,
        "status_description": _get_status_description(status),
        "delay_minutes": delay_minutes,
        "delay_reason": delay_reason,
        "weather": weather,
        "connections": connections,
        "connection_count": len(connections),
        "last_updated": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "flight_lookup",
        "factory_version": "2.0.0",
        "context_keys_used": ["flight_config", "status_config"]
    }


def _get_status_description(status: str) -> str:
    """Get status description."""
    descriptions = {
        'on_time': 'Flight is on schedule',
        'slightly_delayed': 'Minor delay expected',
        'delayed': 'Flight is delayed',
        'cancelled': 'Flight has been cancelled',
        'departed': 'Flight has departed',
        'arrived': 'Flight has arrived',
        'boarding': 'Now boarding'
    }
    return descriptions.get(status, status)


def _get_connections(flight_number: str, date: str) -> List[Dict]:
    """Get connecting flights (simulated)."""
    return [
        {
            'flight_number': f"{flight_number[:-1]}2",
            'destination': 'SFO',
            'departure_time': f"{date}T13:00:00",
            'connection_time_minutes': 75,
            'status': 'on_time'
        }
    ]


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(flight_lookup(event))
