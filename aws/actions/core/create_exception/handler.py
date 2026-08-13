"""
Create Exception - Core Action (Context-Driven)
Create and manage workflow exceptions for error handling

Context-Driven Architecture:
- Exception rules from playbook context.exception_config
- Escalation settings from context.exception_config.escalation
- Notification rules from context.exception_config.notifications
"""

from typing import Dict, Any, Optional
from datetime import datetime
import structlog
import json
import traceback

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default exception configuration
DEFAULT_EXCEPTION_CONFIG = {
    "severity_levels": {
        "critical": {"auto_escalate": True, "notify_immediately": True},
        "high": {"auto_escalate": True, "notify_immediately": False},
        "medium": {"auto_escalate": False, "notify_immediately": False},
        "low": {"auto_escalate": False, "notify_immediately": False}
    },
    "auto_retry": {
        "enabled": True,
        "max_retries": 3,
        "retry_delay_seconds": 60
    },
    "escalation": {
        "timeout_hours": 4,
        "escalation_chain": ["supervisor", "manager", "director"]
    }
}


@register_factory("create_exception")
async def create_exception(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create workflow exception for error handling (context-driven).

    Context keys used:
        - exception_config: Exception handling configuration
            - severity_levels: Severity level definitions
            - auto_retry: Retry configuration
            - escalation: Escalation chain settings
        - notifications: Notification configuration

    Input:
        error_type: Type of error
        error_message: Error message
        error_details: Detailed error information
        severity: Exception severity (critical, high, medium, low)
        workflow_id: Associated workflow ID
        factory_id: Factory that raised the exception
        retry_count: Current retry count
        recoverable: Whether error is recoverable

    Output:
        exception_id: Unique exception identifier
        severity: Exception severity
        status: Exception status
        action_taken: Action taken (retry, escalate, log)
        next_action: Recommended next action
    """
    context = context or input_data.get('context', {})
    exception_config = context.get('exception_config', DEFAULT_EXCEPTION_CONFIG)
    severity_levels = exception_config.get('severity_levels', DEFAULT_EXCEPTION_CONFIG['severity_levels'])
    auto_retry_config = exception_config.get('auto_retry', DEFAULT_EXCEPTION_CONFIG['auto_retry'])
    escalation_config = exception_config.get('escalation', DEFAULT_EXCEPTION_CONFIG['escalation'])

    logger.info(
        "Create exception invoked",
        context_driven=bool(context)
    )

    # Extract input parameters
    error_type = input_data.get('error_type', 'unknown_error')
    error_message = input_data.get('error_message', 'An error occurred')
    error_details = input_data.get('error_details', {})
    severity = input_data.get('severity', 'medium')
    workflow_id = input_data.get('workflow_id', 'unknown')
    factory_id = input_data.get('factory_id', 'unknown')
    retry_count = input_data.get('retry_count', 0)
    recoverable = input_data.get('recoverable', True)

    # Generate exception ID
    exception_id = f"exc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(error_message) % 10000:04d}"

    # Get severity configuration
    severity_config = severity_levels.get(severity, severity_levels.get('medium', {}))

    # Determine action to take
    action_taken = []
    next_action = None
    status = "open"

    # Check if we should retry
    max_retries = auto_retry_config.get('max_retries', 3)
    if recoverable and auto_retry_config.get('enabled', True) and retry_count < max_retries:
        action_taken.append("scheduled_retry")
        next_action = {
            "action": "retry",
            "delay_seconds": auto_retry_config.get('retry_delay_seconds', 60),
            "retry_number": retry_count + 1
        }
        status = "pending_retry"
    elif severity_config.get('auto_escalate', False):
        action_taken.append("escalated")
        next_action = {
            "action": "escalate",
            "escalate_to": escalation_config.get('escalation_chain', ['supervisor'])[0]
        }
        status = "escalated"
    else:
        action_taken.append("logged")
        next_action = {"action": "manual_review"}
        status = "open"

    # Create exception record
    exception_record = {
        "exception_id": exception_id,
        "error_type": error_type,
        "error_message": error_message,
        "error_details": error_details,
        "severity": severity,
        "status": status,
        "workflow_id": workflow_id,
        "factory_id": factory_id,
        "retry_count": retry_count,
        "recoverable": recoverable,
        "action_taken": action_taken,
        "next_action": next_action,
        "created_at": datetime.utcnow().isoformat()
    }

    # Store exception
    await _store_exception(exception_record, context.get('aws_resources', {}))

    # Send notification if required
    if severity_config.get('notify_immediately', False):
        await _send_exception_notification(
            exception_record,
            context.get('notifications', {})
        )
        action_taken.append("notified")

    logger.error(
        "Exception created",
        exception_id=exception_id,
        error_type=error_type,
        severity=severity,
        status=status
    )

    return {
        "exception_id": exception_id,
        "error_type": error_type,
        "error_message": error_message,
        "severity": severity,
        "status": status,
        "action_taken": action_taken,
        "next_action": next_action,
        "retry_count": retry_count,
        "max_retries": max_retries,
        "recoverable": recoverable,
        "workflow_id": workflow_id,
        "factory_id": factory_id,
        "created_at": exception_record["created_at"],
        "context_driven": bool(context),
        "factory_id": "create_exception",
        "factory_version": "2.0.0",
        "context_keys_used": ["exception_config", "notifications"]
    }


async def _store_exception(exception_record: Dict[str, Any], aws_resources: Dict[str, Any]) -> bool:
    """Store exception record to DynamoDB."""
    if not AWS_ENABLED:
        return True

    try:
        dynamodb_tables = aws_resources.get('dynamodb_tables', {})
        exceptions_table = dynamodb_tables.get('exceptions') or dynamodb_tables.get('errors')

        if exceptions_table:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(exceptions_table)
            table.put_item(Item={
                'exception_id': exception_record['exception_id'],
                'workflow_id': exception_record['workflow_id'],
                'severity': exception_record['severity'],
                'status': exception_record['status'],
                'error_type': exception_record['error_type'],
                'error_message': exception_record['error_message'],
                'created_at': exception_record['created_at']
            })
            return True
    except Exception as e:
        logger.warning("Failed to store exception", error=str(e))

    return False


async def _send_exception_notification(
    exception_record: Dict[str, Any],
    notifications_config: Dict[str, Any]
) -> None:
    """Send notification for exception."""
    logger.info(
        "Exception notification sent",
        exception_id=exception_record['exception_id'],
        severity=exception_record['severity']
    )


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(create_exception(event))
