"""
Budget Check - Financial Services Action (Context-Driven)
Validate transactions against budget allocations

Context-Driven Architecture:
- Budget rules from playbook context.budget_config
- Cost center mappings from context.gl_mappings
- Threshold settings from context.budget_config.thresholds
"""

from typing import Dict, Any, Optional
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

try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default budget configuration
DEFAULT_BUDGET_CONFIG = {
    "thresholds": {
        "warning": 80,  # Warning at 80% of budget
        "critical": 95,  # Critical at 95% of budget
        "block": 100    # Block at 100% of budget
    },
    "allow_override": True,
    "require_approval_above_warning": True
}


@register_factory("budget_check")
async def budget_check(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check transaction against budget allocation (context-driven).

    Context keys used:
        - budget_config: Budget checking configuration
        - gl_mappings: GL code to cost center mappings

    Input:
        amount: Transaction amount
        cost_center: Cost center code
        gl_code: GL account code
        department: Department name
        fiscal_period: Fiscal period (optional)

    Output:
        budget_available: Whether budget is available
        budget_status: Status (ok, warning, critical, exceeded)
        remaining_budget: Remaining budget amount
        utilization_percent: Budget utilization percentage
        requires_approval: Whether approval is needed
    """
    context = context or input_data.get('context', {})
    budget_config = context.get('budget_config', DEFAULT_BUDGET_CONFIG)
    gl_mappings = context.get('gl_mappings', {})
    thresholds = budget_config.get('thresholds', DEFAULT_BUDGET_CONFIG['thresholds'])

    logger.info(
        "Budget check invoked",
        context_driven=bool(context)
    )

    # Extract input parameters
    amount = input_data.get('amount', 0)

    # Get from upstream factories
    invoice = input_data.get('invoice_extract', {})
    approval = input_data.get('approval_route', {})

    if not amount and invoice:
        amount = invoice.get('total_amount', 0)

    cost_center = input_data.get('cost_center') or approval.get('cost_center', 'CC-000')
    gl_code = input_data.get('gl_code') or approval.get('gl_code', '6100')
    department = input_data.get('department') or approval.get('department', 'general')
    fiscal_period = input_data.get('fiscal_period', datetime.utcnow().strftime('%Y-%m'))

    # Get budget allocation
    budget_info = await _get_budget_allocation(
        cost_center=cost_center,
        gl_code=gl_code,
        department=department,
        fiscal_period=fiscal_period,
        gl_mappings=gl_mappings
    )

    allocated = budget_info.get('allocated', 100000)
    spent = budget_info.get('spent', 0)
    committed = budget_info.get('committed', 0)

    # Calculate utilization
    current_utilized = spent + committed
    projected_utilized = current_utilized + amount
    remaining = allocated - current_utilized
    remaining_after = allocated - projected_utilized

    utilization_percent = (projected_utilized / allocated * 100) if allocated > 0 else 100

    # Determine status based on thresholds
    warning_threshold = thresholds.get('warning', 80)
    critical_threshold = thresholds.get('critical', 95)
    block_threshold = thresholds.get('block', 100)

    if utilization_percent >= block_threshold:
        budget_status = "exceeded"
        budget_available = budget_config.get('allow_override', True)
    elif utilization_percent >= critical_threshold:
        budget_status = "critical"
        budget_available = True
    elif utilization_percent >= warning_threshold:
        budget_status = "warning"
        budget_available = True
    else:
        budget_status = "ok"
        budget_available = True

    # Determine if approval required
    requires_approval = (
        budget_status in ['warning', 'critical', 'exceeded'] and
        budget_config.get('require_approval_above_warning', True)
    )

    return {
        "budget_available": budget_available,
        "budget_status": budget_status,
        "amount": amount,
        "cost_center": cost_center,
        "gl_code": gl_code,
        "department": department,
        "fiscal_period": fiscal_period,
        "budget_allocated": allocated,
        "budget_spent": spent,
        "budget_committed": committed,
        "current_utilization": round(current_utilized, 2),
        "projected_utilization": round(projected_utilized, 2),
        "remaining_budget": round(remaining, 2),
        "remaining_after_transaction": round(remaining_after, 2),
        "utilization_percent": round(utilization_percent, 2),
        "warning_threshold": warning_threshold,
        "critical_threshold": critical_threshold,
        "requires_approval": requires_approval,
        "can_proceed": budget_available and (not requires_approval or budget_status == "ok"),
        "checked_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "budget_check",
        "factory_version": "2.0.0",
        "context_keys_used": ["budget_config", "gl_mappings"]
    }


async def _get_budget_allocation(
    cost_center: str,
    gl_code: str,
    department: str,
    fiscal_period: str,
    gl_mappings: Dict[str, Any]
) -> Dict[str, Any]:
    """Get budget allocation from ERP/budget system."""
    # In production, this would query budget system
    # Simplified implementation with sample data

    # Sample budget allocations
    sample_budgets = {
        "CC-100": {"allocated": 500000, "spent": 325000, "committed": 50000},
        "CC-200": {"allocated": 250000, "spent": 180000, "committed": 25000},
        "CC-300": {"allocated": 150000, "spent": 120000, "committed": 10000},
        "CC-400": {"allocated": 300000, "spent": 275000, "committed": 15000},  # Near limit
        "CC-000": {"allocated": 100000, "spent": 50000, "committed": 10000}
    }

    return sample_budgets.get(cost_center, {
        "allocated": 100000,
        "spent": 50000,
        "committed": 10000
    })


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(budget_check(event))
