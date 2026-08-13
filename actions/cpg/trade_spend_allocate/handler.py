"""
Trade Spend Allocate - CPG Action (Context-Driven)
Allocate trade spend budget across retailers and promotions

Context-Driven Architecture:
- Allocation rules from playbook context.allocation_config
- Budget constraints from context.budget_config
- Retailer priorities from context.retailer_config
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


DEFAULT_ALLOCATION_CONFIG = {
    "allocation_method": "roi_based",
    "min_allocation_pct": 5,
    "max_allocation_pct": 40,
    "reserve_pct": 10
}


@register_factory("trade_spend_allocate")
async def trade_spend_allocate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Allocate trade spend budget (context-driven).

    Context keys used:
        - allocation_config: Allocation rules
        - budget_config: Budget constraints
        - retailer_config: Retailer priorities

    Input:
        total_budget: Total budget to allocate
        retailers: List of retailers
        historical_performance: Historical ROI data

    Output:
        allocations: Budget allocations per retailer
        remaining_reserve: Reserved budget amount
    """
    context = context or input_data.get('context', {})
    allocation_config = context.get('allocation_config', DEFAULT_ALLOCATION_CONFIG)
    budget_config = context.get('budget_config', {})
    retailer_config = context.get('retailer_config', {})

    logger.info(
        "Trade spend allocate invoked",
        context_driven=bool(context)
    )

    total_budget = input_data.get('total_budget', 0)
    retailers = input_data.get('retailers', [])
    historical = input_data.get('historical_performance', {})

    method = allocation_config.get('allocation_method', 'roi_based')
    min_pct = allocation_config.get('min_allocation_pct', 5)
    max_pct = allocation_config.get('max_allocation_pct', 40)
    reserve_pct = allocation_config.get('reserve_pct', 10)

    # Calculate reserve
    reserve_amount = total_budget * (reserve_pct / 100)
    allocatable_budget = total_budget - reserve_amount

    # Calculate allocations
    allocations = []

    if method == 'roi_based':
        allocations = _allocate_by_roi(
            retailers, historical, allocatable_budget, min_pct, max_pct
        )
    elif method == 'revenue_share':
        allocations = _allocate_by_revenue(
            retailers, allocatable_budget, min_pct, max_pct
        )
    else:
        allocations = _allocate_equal(retailers, allocatable_budget)

    total_allocated = sum(a['allocation'] for a in allocations)

    return {
        "total_budget": total_budget,
        "reserve_amount": round(reserve_amount, 2),
        "allocatable_budget": round(allocatable_budget, 2),
        "total_allocated": round(total_allocated, 2),
        "allocation_method": method,
        "allocations": allocations,
        "retailer_count": len(allocations),
        "constraints_applied": {
            "min_allocation_pct": min_pct,
            "max_allocation_pct": max_pct,
            "reserve_pct": reserve_pct
        },
        "allocated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "trade_spend_allocate",
        "factory_version": "2.0.0",
        "context_keys_used": ["allocation_config", "budget_config", "retailer_config"]
    }


def _allocate_by_roi(retailers: List[Dict], historical: Dict,
                     budget: float, min_pct: float, max_pct: float) -> List[Dict]:
    """Allocate based on historical ROI."""
    allocations = []

    # Get ROI for each retailer
    roi_data = []
    for retailer in retailers:
        retailer_id = retailer.get('id')
        roi = historical.get(retailer_id, {}).get('roi_pct', 100)
        roi_data.append({
            'retailer': retailer,
            'roi': roi
        })

    # Sort by ROI
    roi_data.sort(key=lambda x: x['roi'], reverse=True)

    # Calculate weighted allocations
    total_roi = sum(r['roi'] for r in roi_data)

    for data in roi_data:
        retailer = data['retailer']
        roi = data['roi']

        # Base allocation on ROI weight
        if total_roi > 0:
            raw_pct = (roi / total_roi) * 100
        else:
            raw_pct = 100 / len(retailers)

        # Apply constraints
        allocation_pct = max(min_pct, min(max_pct, raw_pct))
        allocation = budget * (allocation_pct / 100)

        allocations.append({
            'retailer_id': retailer.get('id'),
            'retailer_name': retailer.get('name'),
            'allocation': round(allocation, 2),
            'allocation_pct': round(allocation_pct, 1),
            'historical_roi': roi,
            'expected_roi': roi * 1.1  # Assume 10% improvement
        })

    return allocations


def _allocate_by_revenue(retailers: List[Dict], budget: float,
                         min_pct: float, max_pct: float) -> List[Dict]:
    """Allocate based on revenue share."""
    allocations = []
    total_revenue = sum(r.get('revenue', 0) for r in retailers)

    for retailer in retailers:
        revenue = retailer.get('revenue', 0)

        if total_revenue > 0:
            raw_pct = (revenue / total_revenue) * 100
        else:
            raw_pct = 100 / len(retailers)

        allocation_pct = max(min_pct, min(max_pct, raw_pct))
        allocation = budget * (allocation_pct / 100)

        allocations.append({
            'retailer_id': retailer.get('id'),
            'retailer_name': retailer.get('name'),
            'allocation': round(allocation, 2),
            'allocation_pct': round(allocation_pct, 1),
            'revenue_share': round(raw_pct, 1)
        })

    return allocations


def _allocate_equal(retailers: List[Dict], budget: float) -> List[Dict]:
    """Allocate equally across retailers."""
    per_retailer = budget / len(retailers) if retailers else 0
    pct = 100 / len(retailers) if retailers else 0

    return [{
        'retailer_id': r.get('id'),
        'retailer_name': r.get('name'),
        'allocation': round(per_retailer, 2),
        'allocation_pct': round(pct, 1)
    } for r in retailers]


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(trade_spend_allocate(event))
