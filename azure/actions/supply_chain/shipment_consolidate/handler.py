"""
Shipment Consolidate - Supply Chain Action (Context-Driven)
Consolidate multiple shipments for efficiency

Context-Driven Architecture:
- Consolidation rules from playbook context.consolidation_config
- Warehouse settings from context.warehouse_config
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


DEFAULT_CONSOLIDATION_CONFIG = {
    "consolidate_by": "destination_zip",
    "max_shipments_per_consolidation": 10,
    "max_weight_lbs": 150,
    "time_window_hours": 24
}


@register_factory("shipment_consolidate")
async def shipment_consolidate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Consolidate shipments (context-driven).

    Context keys used:
        - consolidation_config: Consolidation rules
        - warehouse_config: Warehouse settings

    Input:
        shipments: List of shipments to consolidate

    Output:
        consolidated_shipments: Consolidated shipment groups
        savings_estimate: Estimated cost savings
    """
    context = context or input_data.get('context', {})
    config = context.get('consolidation_config', DEFAULT_CONSOLIDATION_CONFIG)

    logger.info(
        "Shipment consolidate invoked",
        context_driven=bool(context)
    )

    shipments = input_data.get('shipments', [])

    consolidate_by = config.get('consolidate_by', 'destination_zip')
    max_per_group = config.get('max_shipments_per_consolidation', 10)
    max_weight = config.get('max_weight_lbs', 150)

    # Group shipments
    groups = {}
    for shipment in shipments:
        key = shipment.get(consolidate_by, shipment.get('destination_zip', 'unknown'))
        if key not in groups:
            groups[key] = []
        groups[key].append(shipment)

    # Create consolidated shipments
    consolidated = []
    original_count = len(shipments)
    total_savings = 0

    for key, group_shipments in groups.items():
        current_group = []
        current_weight = 0

        for shipment in group_shipments:
            weight = shipment.get('weight_lbs', 1)

            if len(current_group) >= max_per_group or current_weight + weight > max_weight:
                if current_group:
                    consolidated.append(_create_consolidated_shipment(key, current_group))
                    total_savings += (len(current_group) - 1) * 5  # $5 savings per consolidated shipment
                current_group = []
                current_weight = 0

            current_group.append(shipment)
            current_weight += weight

        if current_group:
            consolidated.append(_create_consolidated_shipment(key, current_group))
            if len(current_group) > 1:
                total_savings += (len(current_group) - 1) * 5

    return {
        "consolidated_shipments": consolidated,
        "consolidated_count": len(consolidated),
        "original_shipment_count": original_count,
        "consolidation_rate": round((1 - len(consolidated) / original_count) * 100, 1) if original_count > 0 else 0,
        "estimated_savings": round(total_savings, 2),
        "consolidation_criteria": consolidate_by,
        "consolidated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "shipment_consolidate",
        "factory_version": "2.0.0",
        "context_keys_used": ["consolidation_config", "warehouse_config"]
    }


def _create_consolidated_shipment(key: str, shipments: List[Dict]) -> Dict:
    """Create a consolidated shipment record."""
    total_weight = sum(s.get('weight_lbs', 1) for s in shipments)
    return {
        'consolidation_key': key,
        'shipment_count': len(shipments),
        'shipment_ids': [s.get('id') for s in shipments],
        'total_weight_lbs': round(total_weight, 1),
        'destination': shipments[0].get('destination_address') if shipments else None,
        'status': 'ready_for_pickup'
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(shipment_consolidate(event))
