"""
Create Work Item - Core Action (Context-Driven)
Create work items for agent processing queues

Context-Driven Architecture:
- Work item configuration from playbook context.work_item_config
- Queue settings from context.aws_resources.sqs_queues
- Priority rules from context.work_item_config.priority_rules
"""

from typing import Dict, Any, Optional
from datetime import datetime
import structlog
import json
import uuid

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


# Default work item configuration
DEFAULT_WORK_ITEM_CONFIG = {
    "default_priority": "medium",
    "priority_rules": {
        "urgent": {"sla_hours": 1},
        "high": {"sla_hours": 4},
        "medium": {"sla_hours": 24},
        "low": {"sla_hours": 72}
    },
    "auto_assign": True
}


@register_factory("create_work_item")
async def create_work_item(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create work item for agent processing (context-driven).

    Context keys used:
        - work_item_config: Work item configuration
        - aws_resources: Queue and storage configuration

    Input:
        item_type: Type of work item
        title: Work item title
        description: Work item description
        data: Work item payload data
        priority: Priority level
        assigned_agent: Agent to assign (optional)

    Output:
        work_item_id: Unique work item identifier
        queue_url: SQS queue URL
        status: Work item status
        sla_due: SLA due timestamp
    """
    context = context or input_data.get('context', {})
    work_item_config = context.get('work_item_config', DEFAULT_WORK_ITEM_CONFIG)
    aws_resources = context.get('aws_resources', {})
    priority_rules = work_item_config.get('priority_rules', DEFAULT_WORK_ITEM_CONFIG['priority_rules'])

    logger.info(
        "Create work item invoked",
        context_driven=bool(context)
    )

    # Extract input parameters
    item_type = input_data.get('item_type', 'general')
    title = input_data.get('title', f'Work Item - {item_type}')
    description = input_data.get('description', '')
    data = input_data.get('data', {})
    priority = input_data.get('priority', work_item_config.get('default_priority', 'medium'))
    assigned_agent = input_data.get('assigned_agent')

    # Generate work item ID
    work_item_id = f"wi-{uuid.uuid4().hex[:12]}"

    # Calculate SLA
    sla_hours = priority_rules.get(priority, {}).get('sla_hours', 24)
    sla_due = datetime.utcnow().timestamp() + (sla_hours * 3600)

    # Build work item
    work_item = {
        "work_item_id": work_item_id,
        "item_type": item_type,
        "title": title,
        "description": description,
        "priority": priority,
        "status": "pending",
        "assigned_agent": assigned_agent,
        "data": data,
        "sla_due": datetime.fromtimestamp(sla_due).isoformat(),
        "sla_hours": sla_hours,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": "system"
    }

    # Store to DynamoDB
    stored = await _store_work_item(work_item, aws_resources)

    # Queue to SQS if configured
    queue_url = None
    queued = False
    sqs_queues = aws_resources.get('sqs_queues', {})
    processing_queue = sqs_queues.get('processing') or sqs_queues.get('work_items')

    if processing_queue:
        queued, queue_url = await _queue_work_item(work_item, processing_queue)

    return {
        "work_item_id": work_item_id,
        "item_type": item_type,
        "title": title,
        "priority": priority,
        "status": "queued" if queued else "pending",
        "assigned_agent": assigned_agent,
        "sla_due": work_item["sla_due"],
        "sla_hours": sla_hours,
        "queue_url": queue_url,
        "queued": queued,
        "stored": stored,
        "created_at": work_item["created_at"],
        "context_driven": bool(context),
        "factory_id": "create_work_item",
        "factory_version": "2.0.0",
        "context_keys_used": ["work_item_config", "aws_resources"]
    }


async def _store_work_item(work_item: Dict[str, Any], aws_resources: Dict[str, Any]) -> bool:
    """Store work item to DynamoDB."""
    if not AWS_ENABLED:
        return True

    try:
        dynamodb_tables = aws_resources.get('dynamodb_tables', {})
        work_items_table = dynamodb_tables.get('work_items')

        if work_items_table:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(work_items_table)
            table.put_item(Item={
                'work_item_id': work_item['work_item_id'],
                'item_type': work_item['item_type'],
                'status': work_item['status'],
                'priority': work_item['priority'],
                'title': work_item['title'],
                'data': json.dumps(work_item['data']),
                'sla_due': work_item['sla_due'],
                'created_at': work_item['created_at']
            })
            return True
    except Exception as e:
        logger.warning("Failed to store work item", error=str(e))

    return False


async def _queue_work_item(work_item: Dict[str, Any], queue_name: str) -> tuple:
    """Queue work item to SQS."""
    if not AWS_ENABLED:
        return True, f"sqs://{queue_name}"

    try:
        sqs = boto3.client('sqs')

        # Get queue URL
        try:
            response = sqs.get_queue_url(QueueName=queue_name)
            queue_url = response['QueueUrl']
        except:
            return False, None

        # Send message
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(work_item),
            MessageAttributes={
                'Priority': {
                    'StringValue': work_item['priority'],
                    'DataType': 'String'
                },
                'ItemType': {
                    'StringValue': work_item['item_type'],
                    'DataType': 'String'
                }
            }
        )

        return True, queue_url

    except Exception as e:
        logger.warning("Failed to queue work item", error=str(e))
        return False, None


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(create_work_item(event))
