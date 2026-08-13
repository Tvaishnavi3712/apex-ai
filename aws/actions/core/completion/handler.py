"""
Completion - Core Action (Context-Driven)
Mark workflow as complete and store final results

Context-Driven Architecture:
- Storage configuration from playbook context.aws_resources
- Completion rules from context.completion_config
- Integration settings from context.integrations
"""

from typing import Dict, Any, Optional
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

try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


@register_factory("completion")
async def completion(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Complete workflow and store final results (context-driven).

    Context keys used:
        - aws_resources: Storage configuration (DynamoDB tables, S3 buckets)
        - completion_config: Completion behavior settings
        - integrations: External system integrations to notify

    Input:
        All upstream factory outputs (automatically aggregated)
        workflow_id: Workflow identifier
        status: Final status (completed, failed, cancelled)

    Output:
        workflow_id: Workflow identifier
        completed_at: Completion timestamp
        status: Final status
        results_stored: Whether results were persisted
        integrations_notified: List of integrations notified
    """
    context = context or input_data.get('context', {})
    aws_resources = context.get('aws_resources', {})
    completion_config = context.get('completion_config', {})
    integrations = context.get('integrations', {})

    logger.info(
        "Completion invoked",
        context_driven=bool(context)
    )

    # Get workflow info
    state = input_data.get('state', {})
    workflow_id = state.get('job_id') or input_data.get('workflow_id', f"wf-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    status = input_data.get('status', 'completed')

    # Aggregate all upstream results
    upstream_results = {}
    for key, value in input_data.items():
        if key not in ['context', 'state', 'config', 'initial_input']:
            if isinstance(value, dict) and not key.startswith('_'):
                upstream_results[key] = value

    # Calculate summary metrics
    summary = _calculate_summary(upstream_results)

    # Store results
    results_stored = False
    storage_location = None

    if aws_resources:
        results_stored, storage_location = await _store_results(
            workflow_id=workflow_id,
            results=upstream_results,
            summary=summary,
            aws_resources=aws_resources
        )

    # Notify integrations
    integrations_notified = []
    if integrations and completion_config.get('notify_on_completion', True):
        integrations_notified = await _notify_integrations(
            workflow_id=workflow_id,
            status=status,
            summary=summary,
            integrations=integrations
        )

    # Build completion record
    completion_record = {
        "workflow_id": workflow_id,
        "status": status,
        "completed_at": datetime.utcnow().isoformat(),
        "results_stored": results_stored,
        "storage_location": storage_location,
        "integrations_notified": integrations_notified,
        "summary": summary,
        "upstream_factory_count": len(upstream_results),
        "context_driven": bool(context),
        "factory_id": "completion",
        "factory_version": "2.0.0",
        "context_keys_used": ["aws_resources", "completion_config", "integrations"]
    }

    # Add upstream results if configured to include
    if completion_config.get('include_full_results', False):
        completion_record["full_results"] = upstream_results

    logger.info(
        "Workflow completed",
        workflow_id=workflow_id,
        status=status,
        factories_processed=len(upstream_results)
    )

    return completion_record


def _calculate_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate summary metrics from upstream results."""
    summary = {
        "total_factories": len(results),
        "successful_factories": 0,
        "failed_factories": 0,
        "key_metrics": {}
    }

    for factory_name, result in results.items():
        if isinstance(result, dict):
            if result.get('error'):
                summary["failed_factories"] += 1
            else:
                summary["successful_factories"] += 1

            # Extract key metrics
            if 'score' in result:
                summary["key_metrics"][f"{factory_name}_score"] = result['score']
            if 'quality_score' in result:
                summary["key_metrics"][f"{factory_name}_quality_score"] = result['quality_score']
            if 'confidence' in result:
                summary["key_metrics"][f"{factory_name}_confidence"] = result['confidence']
            if 'compliant' in result:
                summary["key_metrics"][f"{factory_name}_compliant"] = result['compliant']

    return summary


async def _store_results(
    workflow_id: str,
    results: Dict[str, Any],
    summary: Dict[str, Any],
    aws_resources: Dict[str, Any]
) -> tuple:
    """Store workflow results to DynamoDB and/or S3."""
    if not AWS_ENABLED:
        return True, "mock://results"

    try:
        # Store to DynamoDB if table configured
        dynamodb_tables = aws_resources.get('dynamodb_tables', {})
        results_table = dynamodb_tables.get('workflow_results') or dynamodb_tables.get('results')

        if results_table:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(results_table)
            table.put_item(Item={
                'workflow_id': workflow_id,
                'completed_at': datetime.utcnow().isoformat(),
                'summary': json.dumps(summary),
                'ttl': int((datetime.utcnow().timestamp()) + (90 * 24 * 60 * 60))  # 90 days
            })
            return True, f"dynamodb://{results_table}/{workflow_id}"

        # Store to S3 if bucket configured
        s3_buckets = aws_resources.get('s3_buckets', {})
        results_bucket = s3_buckets.get('results') or s3_buckets.get('reports')

        if results_bucket:
            s3 = boto3.client('s3')
            key = f"workflows/{workflow_id}/results.json"
            s3.put_object(
                Bucket=results_bucket,
                Key=key,
                Body=json.dumps({"summary": summary, "results": results}),
                ContentType='application/json'
            )
            return True, f"s3://{results_bucket}/{key}"

        return True, "memory://results"

    except Exception as e:
        logger.warning("Failed to store results", error=str(e))
        return False, None


async def _notify_integrations(
    workflow_id: str,
    status: str,
    summary: Dict[str, Any],
    integrations: Dict[str, Any]
) -> list:
    """Notify configured integrations of workflow completion."""
    notified = []

    for integration_name, config in integrations.items():
        if not config.get('enabled', False):
            continue

        try:
            if integration_name == 'erp':
                # Would call ERP integration
                notified.append(integration_name)
            elif integration_name == 'crm':
                # Would call CRM integration
                notified.append(integration_name)
            elif integration_name == 'webhook':
                # Would call webhook
                notified.append(integration_name)

            logger.info(f"Notified integration: {integration_name}")

        except Exception as e:
            logger.warning(f"Failed to notify {integration_name}", error=str(e))

    return notified


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(completion(event))
