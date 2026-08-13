"""
BOM Validate - Manufacturing Action (Context-Driven)
Validate Bill of Materials for production

Context-Driven Architecture:
- BOM rules from playbook context.bom_config
- Validation settings from context.bom_validation
- Component requirements from context.component_config
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


# Default BOM configuration
DEFAULT_BOM_CONFIG = {
    "require_all_components": True,
    "allow_substitutions": True,
    "max_bom_levels": 10,
    "validate_lead_times": True
}

# Default BOM validation rules
DEFAULT_BOM_VALIDATION = {
    "check_circular_refs": True,
    "check_obsolete_parts": True,
    "check_inventory": True,
    "minimum_yield_pct": 95
}


@register_factory("bom_validate")
async def bom_validate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate Bill of Materials (context-driven).

    Context keys used:
        - bom_config: BOM structure rules
        - bom_validation: Validation requirements
        - component_config: Component specifications

    Input:
        product_id: Product to validate BOM for
        bom_data: BOM structure (optional - will be looked up)
        quantity: Production quantity

    Output:
        bom_valid: Whether BOM is valid
        validation_results: Detailed validation results
        components: Validated component list
        issues: Any validation issues
    """
    context = context or input_data.get('context', {})
    bom_config = context.get('bom_config', DEFAULT_BOM_CONFIG)
    bom_validation = context.get('bom_validation', DEFAULT_BOM_VALIDATION)
    component_config = context.get('component_config', {})

    logger.info(
        "BOM validate invoked",
        context_driven=bool(context)
    )

    # Get inputs
    product_id = input_data.get('product_id', '')
    bom_data = input_data.get('bom_data', {})
    quantity = input_data.get('quantity', 1)

    # Load BOM if not provided
    if not bom_data:
        bom_data = _load_bom(product_id)

    # Validate BOM structure
    validation_results = {}
    issues = []

    # Check BOM exists and has components
    components = bom_data.get('components', [])
    if not components:
        return {
            "product_id": product_id,
            "bom_valid": False,
            "error": "No BOM found or BOM has no components",
            "validated_at": datetime.utcnow().isoformat(),
            "context_driven": bool(context),
            "factory_id": "bom_validate",
            "factory_version": "2.0.0",
            "context_keys_used": ["bom_config"]
        }

    # Check BOM levels
    max_levels = bom_config.get('max_bom_levels', 10)
    bom_depth = _calculate_bom_depth(bom_data)
    validation_results['bom_depth'] = {
        'check': 'BOM depth',
        'passed': bom_depth <= max_levels,
        'depth': bom_depth,
        'max_allowed': max_levels
    }
    if bom_depth > max_levels:
        issues.append(f'BOM exceeds maximum depth of {max_levels} levels')

    # Check for circular references
    if bom_validation.get('check_circular_refs', True):
        has_circular = _check_circular_references(bom_data)
        validation_results['circular_refs'] = {
            'check': 'Circular references',
            'passed': not has_circular,
            'message': 'No circular references' if not has_circular else 'Circular reference detected'
        }
        if has_circular:
            issues.append('Circular reference detected in BOM')

    # Validate each component
    component_results = []
    total_cost = 0
    obsolete_count = 0
    missing_count = 0

    for comp in components:
        comp_result = _validate_component(
            comp,
            quantity,
            bom_validation,
            component_config
        )
        component_results.append(comp_result)

        if comp_result.get('obsolete'):
            obsolete_count += 1
            issues.append(f"Obsolete component: {comp.get('item_number')}")

        if not comp_result.get('exists', True):
            missing_count += 1
            issues.append(f"Missing component: {comp.get('item_number')}")

        total_cost += comp_result.get('extended_cost', 0)

    # Check obsolete parts
    if bom_validation.get('check_obsolete_parts', True):
        validation_results['obsolete_parts'] = {
            'check': 'Obsolete parts',
            'passed': obsolete_count == 0,
            'count': obsolete_count
        }

    # Check all components exist
    validation_results['components_exist'] = {
        'check': 'All components exist',
        'passed': missing_count == 0,
        'missing_count': missing_count
    }

    # Calculate yield
    yield_pct = _calculate_expected_yield(component_results)
    min_yield = bom_validation.get('minimum_yield_pct', 95)
    validation_results['yield'] = {
        'check': 'Expected yield',
        'passed': yield_pct >= min_yield,
        'expected_yield_pct': yield_pct,
        'minimum_required': min_yield
    }
    if yield_pct < min_yield:
        issues.append(f'Expected yield {yield_pct}% below minimum {min_yield}%')

    # Check lead times
    if bom_validation.get('validate_lead_times', True):
        max_lead_time = max(c.get('lead_time_days', 0) for c in component_results)
        validation_results['lead_time'] = {
            'check': 'Lead time validation',
            'passed': True,
            'max_lead_time_days': max_lead_time
        }

    # Overall validation result
    bom_valid = all(
        r.get('passed', True)
        for r in validation_results.values()
        if isinstance(r, dict)
    )

    return {
        "product_id": product_id,
        "bom_valid": bom_valid,
        "bom_revision": bom_data.get('revision', 'A'),
        "validation_results": validation_results,
        "components": component_results,
        "component_count": len(component_results),
        "bom_depth": bom_depth,
        "total_component_cost": round(total_cost, 2),
        "cost_per_unit": round(total_cost / quantity, 2) if quantity > 0 else 0,
        "issues": issues,
        "issue_count": len(issues),
        "expected_yield_pct": yield_pct,
        "max_lead_time_days": max(c.get('lead_time_days', 0) for c in component_results) if component_results else 0,
        "substitutions_allowed": bom_config.get('allow_substitutions', True),
        "validated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "bom_validate",
        "factory_version": "2.0.0",
        "context_keys_used": ["bom_config", "bom_validation", "component_config"]
    }


def _load_bom(product_id: str) -> Dict:
    """Load BOM for a product (simulated)."""
    return {
        'product_id': product_id,
        'revision': 'B',
        'effective_date': '2024-01-01',
        'components': [
            {
                'item_number': 'COMP-001',
                'description': 'Main Assembly',
                'quantity_per': 1,
                'unit': 'EA',
                'unit_cost': 45.00,
                'lead_time_days': 14
            },
            {
                'item_number': 'COMP-002',
                'description': 'Sub Assembly A',
                'quantity_per': 2,
                'unit': 'EA',
                'unit_cost': 22.50,
                'lead_time_days': 7
            },
            {
                'item_number': 'RAW-001',
                'description': 'Raw Material',
                'quantity_per': 5,
                'unit': 'LB',
                'unit_cost': 3.50,
                'lead_time_days': 5
            },
            {
                'item_number': 'FAST-001',
                'description': 'Fastener Kit',
                'quantity_per': 1,
                'unit': 'KT',
                'unit_cost': 8.00,
                'lead_time_days': 3
            }
        ]
    }


def _calculate_bom_depth(bom_data: Dict, current_depth: int = 1) -> int:
    """Calculate BOM depth (levels of nesting)."""
    # Simplified - would recursively check sub-components
    return current_depth


def _check_circular_references(bom_data: Dict) -> bool:
    """Check for circular references in BOM."""
    # Simplified check - would do full graph traversal
    return False


def _validate_component(comp: Dict, quantity: int,
                        validation_rules: Dict, component_config: Dict) -> Dict:
    """Validate individual component."""
    item_number = comp.get('item_number', '')
    qty_per = comp.get('quantity_per', 1)
    unit_cost = comp.get('unit_cost', 0)

    return {
        'item_number': item_number,
        'description': comp.get('description'),
        'quantity_per': qty_per,
        'total_quantity': qty_per * quantity,
        'unit': comp.get('unit', 'EA'),
        'unit_cost': unit_cost,
        'extended_cost': unit_cost * qty_per * quantity,
        'lead_time_days': comp.get('lead_time_days', 0),
        'exists': True,
        'obsolete': False,
        'substitutes_available': component_config.get('substitutes', {}).get(item_number, [])
    }


def _calculate_expected_yield(components: List[Dict]) -> float:
    """Calculate expected production yield."""
    # Simplified - would use component-specific yield rates
    return 97.5


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(bom_validate(event))
