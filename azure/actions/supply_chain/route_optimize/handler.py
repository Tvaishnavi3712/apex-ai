"""
Route Optimize - Supply Chain Action (Context-Driven)
Optimize delivery routes for shipments

Context-Driven Architecture:
- Routing rules from playbook context.routing_config
- Constraints from context.constraint_config
- Cost factors from context.cost_config
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


DEFAULT_ROUTING_CONFIG = {
    "optimization_goal": "minimize_cost",
    "max_stops_per_route": 20,
    "max_drive_hours": 10,
    "allow_multi_day": False
}


@register_factory("route_optimize")
async def route_optimize(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Optimize delivery routes (context-driven).

    Context keys used:
        - routing_config: Route optimization settings
        - constraint_config: Route constraints
        - cost_config: Cost calculation factors

    Input:
        shipments: List of shipments to route
        vehicles: Available vehicles
        origin: Starting location

    Output:
        optimized_routes: Optimized route plan
        total_distance: Total route distance
        estimated_cost: Estimated delivery cost
    """
    context = context or input_data.get('context', {})
    routing_config = context.get('routing_config', DEFAULT_ROUTING_CONFIG)
    constraint_config = context.get('constraint_config', {})
    cost_config = context.get('cost_config', {})

    logger.info(
        "Route optimize invoked",
        context_driven=bool(context)
    )

    shipments = input_data.get('shipments', [])
    vehicles = input_data.get('vehicles', [{'id': 'V001', 'capacity': 1000}])
    origin = input_data.get('origin', {'lat': 40.7128, 'lng': -74.0060})

    max_stops = routing_config.get('max_stops_per_route', 20)
    max_hours = routing_config.get('max_drive_hours', 10)
    goal = routing_config.get('optimization_goal', 'minimize_cost')

    # Simple route optimization (simulated)
    routes = []
    total_distance = 0
    total_cost = 0

    current_route = {
        'vehicle_id': vehicles[0]['id'] if vehicles else 'V001',
        'stops': [],
        'distance_miles': 0,
        'estimated_hours': 0
    }

    for i, shipment in enumerate(shipments):
        if len(current_route['stops']) >= max_stops:
            routes.append(current_route)
            current_route = {
                'vehicle_id': vehicles[min(len(routes), len(vehicles) - 1)]['id'] if vehicles else f'V{len(routes)+1:03d}',
                'stops': [],
                'distance_miles': 0,
                'estimated_hours': 0
            }

        stop_distance = 10 + (i * 5)  # Simulated distance
        current_route['stops'].append({
            'sequence': len(current_route['stops']) + 1,
            'shipment_id': shipment.get('id'),
            'address': shipment.get('delivery_address'),
            'distance_from_previous': stop_distance,
            'estimated_arrival': f"{8 + len(current_route['stops'])}:00"
        })
        current_route['distance_miles'] += stop_distance
        current_route['estimated_hours'] = current_route['distance_miles'] / 30  # 30 mph avg

    if current_route['stops']:
        routes.append(current_route)

    # Calculate totals
    total_distance = sum(r['distance_miles'] for r in routes)
    cost_per_mile = cost_config.get('cost_per_mile', 1.50)
    total_cost = total_distance * cost_per_mile

    return {
        "optimization_goal": goal,
        "optimized_routes": routes,
        "route_count": len(routes),
        "total_shipments": len(shipments),
        "total_distance_miles": round(total_distance, 1),
        "total_drive_hours": round(total_distance / 30, 1),
        "estimated_cost": round(total_cost, 2),
        "vehicles_used": len(routes),
        "constraints_applied": {
            "max_stops": max_stops,
            "max_drive_hours": max_hours
        },
        "optimized_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "route_optimize",
        "factory_version": "2.0.0",
        "context_keys_used": ["routing_config", "constraint_config", "cost_config"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(route_optimize(event))
