"""
Human Review - Core Action (Context-Driven)
Route items for human review and manage review workflow

Context-Driven Architecture:
- Review routing rules from playbook context.review_routing
- SLA configuration from context.review_routing.sla
- Assignment rules from context.review_routing.assignment
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
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

try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:
    import boto3

    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default review configuration
DEFAULT_REVIEW_CONFIG = {
    "review_triggers": {
        "score_below": 70,
        "compliance_failure": True,
        "confidence_below": 0.85
    },
    "sla": {
        "review_within_hours": 48,
        "escalation_hours": 72
    },
    "assignment": {
        "round_robin": True,
        "by_team": True,
        "max_queue_size": 20
    }
}


@register_factory("human_review")
async def human_review(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Route item for human review (context-driven).

    Context keys used:
        - review_routing: Review configuration
            - review_triggers: Conditions that trigger review
            - sla: Service level agreement settings
            - assignment: Reviewer assignment rules

    Input:
        item_id: Item identifier
        item_type: Type of item (invoice, claim, resume, etc.)
        reason: Reason for review
        priority: Review priority (low, medium, high, urgent)
        data: Item data for review
        upstream_results: Results from upstream factories

    Output:
        review_id: Unique review identifier
        assigned_to: Reviewer assignment
        due_date: Review due date based on SLA
        queue_position: Position in review queue
        review_url: URL to review interface
    """
    context = context or input_data.get('context', {})
    review_config = context.get('review_routing', DEFAULT_REVIEW_CONFIG)
    sla_config = review_config.get('sla', DEFAULT_REVIEW_CONFIG['sla'])
    assignment_config = review_config.get('assignment', DEFAULT_REVIEW_CONFIG['assignment'])

    logger.info(
        "Human review invoked",
        context_driven=bool(context)
    )

    # Extract input parameters
    item_id = input_data.get('item_id', f"item-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    item_type = input_data.get('item_type', 'unknown')
    reason = input_data.get('reason', 'Manual review requested')
    priority = input_data.get('priority', 'medium')
    data = input_data.get('data', {})
    upstream_results = input_data.get('upstream_results', {})

    # Auto-detect review triggers if not explicitly requested
    if not reason or reason == 'Manual review requested':
        reason = _detect_review_reason(upstream_results, review_config.get('review_triggers', {}))

    # Generate review ID
    review_id = f"review-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(item_id) % 10000:04d}"

    # Calculate SLA due date
    review_hours = sla_config.get('review_within_hours', 48)
    if priority == 'urgent':
        review_hours = min(review_hours, 4)
    elif priority == 'high':
        review_hours = min(review_hours, 24)

    due_date = datetime.utcnow() + timedelta(hours=review_hours)

    # Assign reviewer
    assigned_to = await _assign_reviewer(
        item_type=item_type,
        priority=priority,
        assignment_config=assignment_config
    )

    # Create review record
    review_record = {
        "review_id": review_id,
        "item_id": item_id,
        "item_type": item_type,
        "reason": reason,
        "priority": priority,
        "status": "pending",
        "assigned_to": assigned_to,
        "due_date": due_date.isoformat(),
        "escalation_date": (due_date + timedelta(hours=sla_config.get('escalation_hours', 72) - review_hours)).isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "review_url": f"/reviews/{review_id}",
        "queue_position": await _get_queue_position(assigned_to),
        "context_driven": bool(context),
        "factory_id": "human_review",
        "factory_version": "2.0.0",
        "context_keys_used": ["review_routing"]
    }

    # Store review record
    await _store_review_record(review_record, context.get('aws_resources', {}))

    logger.info(
        "Review created",
        review_id=review_id,
        assigned_to=assigned_to,
        priority=priority
    )

    return review_record


def _detect_review_reason(upstream_results: Dict[str, Any], triggers: Dict[str, Any]) -> str:
    """Detect reason for review based on upstream results and triggers."""
    reasons = []

    for factory_name, result in upstream_results.items():
        if not isinstance(result, dict):
            continue

        # Check score threshold
        score = result.get('score') or result.get('quality_score')
        if score is not None and score < triggers.get('score_below', 70):
            reasons.append(f"Low score in {factory_name}: {score}")

        # Check compliance failure
        if triggers.get('compliance_failure') and result.get('compliant') is False:
            reasons.append(f"Compliance failure in {factory_name}")

        # Check confidence threshold
        confidence = result.get('confidence')
        if confidence is not None and confidence < triggers.get('confidence_below', 0.85):
            reasons.append(f"Low confidence in {factory_name}: {confidence}")

        # Check for explicit review flags
        if result.get('requires_review') or result.get('review_required'):
            reasons.append(f"Review flagged by {factory_name}")

    return '; '.join(reasons) if reasons else "Manual review requested"


async def _assign_reviewer(
    item_type: str,
    priority: str,
    assignment_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Assign reviewer based on configuration."""
    # In production, this would query a reviewer management system
    # Simplified implementation for now
    return {
        "type": "role",
        "role": "supervisor",
        "team": item_type,
        "assignment_method": "round_robin" if assignment_config.get('round_robin') else "manual"
    }


async def _get_queue_position(assigned_to: Dict[str, Any]) -> int:
    """Get current queue position for assigned reviewer."""
    # In production, this would query the review queue
    return 1


async def _store_review_record(record: Dict[str, Any], aws_resources: Dict[str, Any]) -> bool:
    """Store review record to Cosmos DB."""
    if not AWS_ENABLED:
        return True

    try:
        cosmos_containers = aws_resources.get('cosmos_containers', {})
        reviews_table = cosmos_containers.get('reviews') or cosmos_containers.get('human_reviews')

        if reviews_table:
            tables = get_table_resource()
            table = cosmos_db.Table(reviews_table)
            table.put_item(Item={
                'review_id': record['review_id'],
                'item_id': record['item_id'],
                'status': record['status'],
                'priority': record['priority'],
                'assigned_to': json.dumps(record['assigned_to']),
                'due_date': record['due_date'],
                'created_at': record['created_at']
            })
            return True
    except Exception as e:
        logger.warning("Failed to store review record", error=str(e))

    return False


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(human_review(event))
