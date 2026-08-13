"""
Work Order Create - Manufacturing Action (Context-Driven)
Create production work orders from demand signals

Context-Driven Architecture:
- Work order settings from playbook context.work_order_config
- Production rules from context.production_config
- Scheduling settings from context.scheduling_config
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


# Default work order configuration
DEFAULT_WORK_ORDER_CONFIG = {
    "auto_release": False,
    "default_priority": "normal",
    "require_bom_validation": True,
    "require_inventory_check": True,
    "default_buffer_days": 2
}

# Default production configuration
DEFAULT_PRODUCTION_CONFIG = {
    "work_centers": ["WC-001", "WC-002", "WC-003"],
    "shift_hours": 8,
    "capacity_buffer_pct": 10
}


@register_factory("work_order_create")
async def work_order_create(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create production work order (context-driven).

    Context keys used:
        - work_order_config: Work order settings
        - production_config: Production line configurations
        - scheduling_config: Production scheduling settings

    Input:
        product_info: Product to produce
        quantity: Quantity needed
        due_date: Required completion date
        bom_validate: BOM validation results
        inventory_check: Inventory availability

    Output:
        work_order_created: Whether WO was created
        work_order: Work order details
        schedule: Production schedule
        material_requirements: Required materials
    """
    context = context or input_data.get('context', {})
    wo_config = context.get('work_order_config', DEFAULT_WORK_ORDER_CONFIG)
    production_config = context.get('production_config', DEFAULT_PRODUCTION_CONFIG)
    scheduling_config = context.get('scheduling_config', {})

    logger.info(
        "Work order create invoked",
        context_driven=bool(context)
    )

    # Get inputs
    product_info = input_data.get('product_info', {})
    quantity = input_data.get('quantity', 0)
    due_date = input_data.get('due_date')
    bom_result = input_data.get('bom_validate', {})
    inventory_result = input_data.get('inventory_check', {})

    product_id = product_info.get('product_id', 'PROD-001')
    product_name = product_info.get('product_name', 'Product')

    # Parse due date
    if due_date:
        try:
            due_dt = datetime.strptime(due_date, '%Y-%m-%d')
        except ValueError:
            due_dt = datetime.utcnow() + timedelta(days=14)
    else:
        due_dt = datetime.utcnow() + timedelta(days=14)

    # Check prerequisites
    prerequisites_met = True
    prerequisite_issues = []

    if wo_config.get('require_bom_validation', True):
        if not bom_result.get('bom_valid', True):
            prerequisites_met = False
            prerequisite_issues.append('BOM validation failed')

    if wo_config.get('require_inventory_check', True):
        if inventory_result.get('shortage_count', 0) > 0:
            prerequisites_met = False
            prerequisite_issues.append('Material shortages detected')

    # Generate work order
    wo_number = f"WO{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    priority = input_data.get('priority', wo_config.get('default_priority', 'normal'))

    # Calculate production schedule
    buffer_days = wo_config.get('default_buffer_days', 2)
    schedule = _calculate_schedule(
        product_info,
        quantity,
        due_dt,
        buffer_days,
        production_config
    )

    # Get material requirements from BOM
    material_requirements = _get_material_requirements(
        product_info,
        quantity,
        bom_result,
        inventory_result
    )

    # Determine status
    if not prerequisites_met:
        status = 'blocked'
    elif wo_config.get('auto_release', False):
        status = 'released'
    else:
        status = 'planned'

    work_order = {
        'wo_number': wo_number,
        'product_id': product_id,
        'product_name': product_name,
        'quantity_ordered': quantity,
        'quantity_completed': 0,
        'quantity_scrapped': 0,
        'priority': priority,
        'status': status,
        'order_date': datetime.utcnow().strftime('%Y-%m-%d'),
        'due_date': due_dt.strftime('%Y-%m-%d'),
        'scheduled_start': schedule['start_date'],
        'scheduled_end': schedule['end_date'],
        'work_center': schedule['assigned_work_center'],
        'routing': schedule['operations'],
        'notes': input_data.get('notes', '')
    }

    # Generate operations/routing
    operations = _generate_operations(product_info, quantity, schedule)

    return {
        "work_order_created": prerequisites_met,
        "work_order_number": wo_number,
        "work_order": work_order,
        "status": status,
        "priority": priority,
        "product_id": product_id,
        "quantity": quantity,
        "schedule": schedule,
        "operations": operations,
        "operation_count": len(operations),
        "material_requirements": material_requirements,
        "material_count": len(material_requirements),
        "prerequisites_met": prerequisites_met,
        "prerequisite_issues": prerequisite_issues,
        "estimated_hours": schedule['total_hours'],
        "estimated_cost": schedule['estimated_cost'],
        "auto_released": wo_config.get('auto_release', False) and prerequisites_met,
        "created_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "work_order_create",
        "factory_version": "2.0.0",
        "context_keys_used": ["work_order_config", "production_config", "scheduling_config"]
    }


def _calculate_schedule(product_info: Dict, quantity: int, due_date: datetime,
                        buffer_days: int, production_config: Dict) -> Dict:
    """Calculate production schedule."""
    # Estimate production time
    cycle_time_hours = product_info.get('cycle_time_hours', 0.5)
    setup_hours = product_info.get('setup_hours', 2)

    total_hours = setup_hours + (cycle_time_hours * quantity)
    shift_hours = production_config.get('shift_hours', 8)
    production_days = (total_hours / shift_hours) + 1

    # Calculate start date
    end_date = due_date - timedelta(days=buffer_days)
    start_date = end_date - timedelta(days=production_days)

    # Assign work center
    work_centers = production_config.get('work_centers', ['WC-001'])
    assigned_wc = work_centers[0]  # Simple assignment

    return {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_hours': round(total_hours, 1),
        'production_days': round(production_days, 1),
        'assigned_work_center': assigned_wc,
        'shift_hours': shift_hours,
        'estimated_cost': round(total_hours * 75, 2),  # $75/hour
        'operations': ['Setup', 'Production', 'Inspection', 'Packaging']
    }


def _get_material_requirements(product_info: Dict, quantity: int,
                                bom_result: Dict, inventory_result: Dict) -> List[Dict]:
    """Get material requirements for work order."""
    requirements = []

    # Get from BOM result if available
    bom_components = bom_result.get('components', [])

    if bom_components:
        for comp in bom_components:
            qty_per = comp.get('quantity_per', 1)
            total_needed = qty_per * quantity

            # Check inventory
            availability = inventory_result.get('item_availability', [])
            item_inventory = next(
                (i for i in availability if i.get('item_number') == comp.get('item_number')),
                {}
            )

            requirements.append({
                'item_number': comp.get('item_number'),
                'description': comp.get('description'),
                'quantity_per': qty_per,
                'quantity_required': total_needed,
                'available': item_inventory.get('available', 0),
                'shortage': max(0, total_needed - item_inventory.get('available', 0))
            })
    else:
        # Generate sample requirements
        requirements = [
            {
                'item_number': 'RAW-001',
                'description': 'Raw Material A',
                'quantity_per': 2,
                'quantity_required': 2 * quantity,
                'available': 500,
                'shortage': 0
            },
            {
                'item_number': 'COMP-001',
                'description': 'Component B',
                'quantity_per': 1,
                'quantity_required': quantity,
                'available': 200,
                'shortage': 0
            }
        ]

    return requirements


def _generate_operations(product_info: Dict, quantity: int, schedule: Dict) -> List[Dict]:
    """Generate work order operations."""
    operations = []
    seq = 10

    for op_name in schedule.get('operations', ['Setup', 'Production']):
        operations.append({
            'sequence': seq,
            'operation': op_name,
            'work_center': schedule['assigned_work_center'],
            'setup_hours': 0.5 if op_name == 'Setup' else 0,
            'run_hours': schedule['total_hours'] * 0.7 if op_name == 'Production' else schedule['total_hours'] * 0.1,
            'status': 'not_started'
        })
        seq += 10

    return operations


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(work_order_create(event))
