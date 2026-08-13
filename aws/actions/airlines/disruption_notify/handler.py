"""
Disruption Notify - Airlines Action (Context-Driven)
Notify passengers of flight disruptions

Context-Driven Architecture:
- Notification settings from playbook context.notification_config
- Channel preferences from context.channel_config
- Message templates from context.template_config
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


DEFAULT_NOTIFICATION_CONFIG = {
    "channels": ["sms", "email", "push"],
    "priority_order": ["sms", "push", "email"],
    "include_rebooking_link": True,
    "send_confirmation": True
}


@register_factory("disruption_notify")
async def disruption_notify(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Notify passengers of disruption (context-driven).

    Context keys used:
        - notification_config: Notification settings
        - channel_config: Channel priorities
        - template_config: Message templates

    Input:
        disruption_details: Disruption information
        affected_passengers: List of affected passengers
        rebooking_options: Available rebooking options

    Output:
        notifications_sent: Number of notifications sent
        notification_results: Per-passenger results
    """
    context = context or input_data.get('context', {})
    notification_config = context.get('notification_config', DEFAULT_NOTIFICATION_CONFIG)
    channel_config = context.get('channel_config', {})
    template_config = context.get('template_config', {})

    logger.info(
        "Disruption notify invoked",
        context_driven=bool(context)
    )

    disruption = input_data.get('disruption_details', {})
    passengers = input_data.get('affected_passengers', [])
    rebooking = input_data.get('rebooking_options', {})

    channels = notification_config.get('channels', ['sms', 'email'])
    include_rebooking = notification_config.get('include_rebooking_link', True)

    # Build message
    flight_number = disruption.get('flight_number', '')
    disruption_type = disruption.get('type', 'delay')
    delay_info = disruption.get('delay_info', '')

    message = _build_message(disruption_type, flight_number, delay_info, template_config)

    # Add rebooking link if available
    rebooking_url = None
    if include_rebooking and rebooking:
        rebooking_url = f"https://airline.example.com/rebook/{flight_number}"
        message += f"\n\nRebook your flight: {rebooking_url}"

    # Send notifications
    notification_results = []
    sent_count = 0
    failed_count = 0

    for passenger in passengers:
        pax_channels = passenger.get('notification_preferences', channels)
        results = []

        for channel in pax_channels:
            success = _send_notification(passenger, channel, message)
            results.append({
                'channel': channel,
                'success': success,
                'sent_at': datetime.utcnow().isoformat() if success else None
            })
            if success:
                sent_count += 1
            else:
                failed_count += 1

        notification_results.append({
            'passenger_name': passenger.get('name'),
            'pnr': passenger.get('pnr'),
            'channels_attempted': len(pax_channels),
            'results': results,
            'any_success': any(r['success'] for r in results)
        })

    return {
        "flight_number": flight_number,
        "disruption_type": disruption_type,
        "passengers_notified": len([r for r in notification_results if r['any_success']]),
        "total_passengers": len(passengers),
        "notifications_sent": sent_count,
        "notifications_failed": failed_count,
        "notification_results": notification_results,
        "message_preview": message[:200] + "..." if len(message) > 200 else message,
        "rebooking_link_included": include_rebooking and rebooking_url is not None,
        "channels_used": channels,
        "notified_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "disruption_notify",
        "factory_version": "2.0.0",
        "context_keys_used": ["notification_config", "channel_config", "template_config"]
    }


def _build_message(disruption_type: str, flight_number: str,
                   delay_info: str, template_config: Dict) -> str:
    """Build notification message."""
    templates = template_config.get('templates', {})

    if disruption_type == 'cancellation':
        template = templates.get('cancellation',
            "Your flight {flight} has been cancelled. We apologize for the inconvenience.")
    elif disruption_type == 'delay':
        template = templates.get('delay',
            "Your flight {flight} is delayed. {info}")
    else:
        template = templates.get('general',
            "Important update about your flight {flight}: {info}")

    return template.format(flight=flight_number, info=delay_info)


def _send_notification(passenger: Dict, channel: str, message: str) -> bool:
    """Send notification via channel (simulated)."""
    # Simulated sending - would integrate with actual notification services
    return True


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(disruption_notify(event))
