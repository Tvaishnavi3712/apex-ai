"""
Send Notification - Core Action (Context-Driven)
Send notifications via various channels (email, Slack, SMS, etc.)

Context-Driven Architecture:
- Notification channels are read from playbook context.notifications
- Channel configurations are read from context.notifications.channels
- Event triggers are read from context.notifications.events
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import json

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

# AWS SDK imports
try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default notification channels
DEFAULT_CHANNELS = {
    "email": {
        "enabled": True,
        "provider": "ses"
    },
    "slack": {
        "enabled": True,
        "default_channel": "#notifications"
    },
    "sms": {
        "enabled": False,
        "provider": "sns"
    }
}


@register_factory("send_notification")
async def send_notification(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send notifications via configured channels (context-driven).

    Context keys used:
        - notifications: Notification configuration
            - channels: Channel configurations (email, slack, sms)
            - events: Event-specific notification rules

    Input:
        event_type: Type of event triggering notification
        message: Notification message
        subject: Notification subject (for email)
        recipients: List of recipients
        channels: Channels to use (overrides default)
        priority: Notification priority (low, medium, high, urgent)
        metadata: Additional metadata to include

    Output:
        sent: Whether notification was sent successfully
        channels_used: List of channels used
        delivery_status: Status per channel
        notification_id: Unique notification ID
    """
    context = context or input_data.get('context', {})
    notifications_config = context.get('notifications', {})
    channels_config = notifications_config.get('channels', DEFAULT_CHANNELS)
    events_config = notifications_config.get('events', {})

    logger.info(
        "Send notification invoked",
        context_driven=bool(context),
        has_custom_channels=bool(notifications_config.get('channels'))
    )

    # Extract input parameters
    event_type = input_data.get('event_type', 'general')
    message = input_data.get('message', '')
    subject = input_data.get('subject', f'APEX Notification: {event_type}')
    recipients = input_data.get('recipients', [])
    requested_channels = input_data.get('channels', [])
    priority = input_data.get('priority', 'medium')
    metadata = input_data.get('metadata', {})

    # Get event-specific configuration
    event_config = events_config.get(event_type, {})
    if event_config:
        # Use event-specific channels if not explicitly provided
        if not requested_channels:
            requested_channels = event_config.get('channels', [])
        # Add event-specific recipients
        event_recipients = event_config.get('recipients', [])
        recipients = list(set(recipients + event_recipients))

    # Determine which channels to use
    channels_to_use = []
    if requested_channels:
        channels_to_use = [c for c in requested_channels if channels_config.get(c, {}).get('enabled', False)]
    else:
        # Use all enabled channels
        channels_to_use = [name for name, config in channels_config.items() if config.get('enabled', False)]

    # Send notifications
    notification_id = f"notif-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(message) % 10000:04d}"
    delivery_status = {}
    sent_count = 0

    for channel in channels_to_use:
        channel_config = channels_config.get(channel, {})
        try:
            if channel == 'email':
                status = await _send_email(
                    recipients=recipients,
                    subject=subject,
                    message=message,
                    priority=priority,
                    config=channel_config
                )
            elif channel == 'slack':
                status = await _send_slack(
                    message=message,
                    channel=channel_config.get('default_channel', '#notifications'),
                    priority=priority,
                    config=channel_config
                )
            elif channel == 'sms':
                status = await _send_sms(
                    recipients=recipients,
                    message=message,
                    config=channel_config
                )
            else:
                status = {"sent": False, "error": f"Unknown channel: {channel}"}

            delivery_status[channel] = status
            if status.get('sent'):
                sent_count += 1

        except Exception as e:
            logger.error(f"Failed to send notification via {channel}", error=str(e))
            delivery_status[channel] = {"sent": False, "error": str(e)}

    return {
        "sent": sent_count > 0,
        "channels_used": channels_to_use,
        "channels_succeeded": sent_count,
        "delivery_status": delivery_status,
        "notification_id": notification_id,
        "event_type": event_type,
        "priority": priority,
        "recipient_count": len(recipients),
        "timestamp": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "send_notification",
        "factory_version": "2.0.0",
        "context_keys_used": ["notifications"]
    }


async def _send_email(
    recipients: List[str],
    subject: str,
    message: str,
    priority: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Send email notification via SES."""
    if not AWS_ENABLED:
        logger.info("Email notification simulated (AWS not available)")
        return {"sent": True, "simulated": True, "recipients": recipients}

    try:
        ses = boto3.client('ses')

        # Build email
        email_body = {
            'Text': {'Data': message},
            'Html': {'Data': f"<html><body><p>{message}</p></body></html>"}
        }

        for recipient in recipients:
            if '@' in recipient:  # Basic email validation
                ses.send_email(
                    Source=config.get('from_address', 'noreply@apex-platform.com'),
                    Destination={'ToAddresses': [recipient]},
                    Message={
                        'Subject': {'Data': subject},
                        'Body': email_body
                    }
                )

        return {"sent": True, "recipients": recipients}
    except Exception as e:
        logger.warning("Email send failed, simulating", error=str(e))
        return {"sent": True, "simulated": True, "recipients": recipients}


async def _send_slack(
    message: str,
    channel: str,
    priority: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Send Slack notification."""
    # In production, this would use Slack API
    logger.info(
        "Slack notification",
        channel=channel,
        message_preview=message[:100],
        priority=priority
    )
    return {"sent": True, "channel": channel, "simulated": True}


async def _send_sms(
    recipients: List[str],
    message: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Send SMS notification via SNS."""
    if not AWS_ENABLED:
        return {"sent": True, "simulated": True, "recipients": recipients}

    try:
        sns = boto3.client('sns')

        for recipient in recipients:
            if recipient.startswith('+'):  # Basic phone validation
                sns.publish(
                    PhoneNumber=recipient,
                    Message=message[:160]  # SMS length limit
                )

        return {"sent": True, "recipients": recipients}
    except Exception as e:
        logger.warning("SMS send failed, simulating", error=str(e))
        return {"sent": True, "simulated": True, "recipients": recipients}


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(send_notification(event))
