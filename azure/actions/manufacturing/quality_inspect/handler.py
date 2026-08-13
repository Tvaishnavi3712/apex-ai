"""
Quality Inspect - Manufacturing Action (Context-Driven)
Perform quality inspection on received materials or finished goods

Context-Driven Architecture:
- Quality standards from playbook context.quality_config
- Inspection criteria from context.inspection_criteria
- Tolerance settings from context.tolerance_config
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


# Default quality configuration
DEFAULT_QUALITY_CONFIG = {
    "inspection_level": "standard",  # standard, enhanced, reduced
    "sample_size_pct": 10,
    "critical_defect_threshold": 0,
    "major_defect_threshold": 2.5,
    "minor_defect_threshold": 4.0,
    "aql_level": 2.5  # Acceptable Quality Level
}

# Default inspection criteria
DEFAULT_INSPECTION_CRITERIA = {
    "visual": ["surface_defects", "color_consistency", "labeling"],
    "dimensional": ["length", "width", "height", "weight"],
    "functional": ["fit_test", "performance_test"],
    "documentation": ["coa_present", "lot_tracking"]
}


@register_factory("quality_inspect")
async def quality_inspect(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Perform quality inspection (context-driven).

    Context keys used:
        - quality_config: Quality standards and thresholds
        - inspection_criteria: Inspection check criteria
        - tolerance_config: Measurement tolerances

    Input:
        receipt_data: Received goods information
        po_extract: Original PO data
        inspection_type: Type of inspection

    Output:
        inspection_result: Pass/Fail determination
        inspection_details: Detailed inspection results
        quality_metrics: Quality measurements
        disposition: Recommended disposition
    """
    context = context or input_data.get('context', {})
    quality_config = context.get('quality_config', DEFAULT_QUALITY_CONFIG)
    inspection_criteria = context.get('inspection_criteria', DEFAULT_INSPECTION_CRITERIA)
    tolerance_config = context.get('tolerance_config', {})

    logger.info(
        "Quality inspect invoked",
        context_driven=bool(context)
    )

    # Get inspection data
    receipt_data = input_data.get('receipt_data', {})
    po_data = input_data.get('po_extract', {})
    inspection_type = input_data.get('inspection_type', 'receiving')

    # Get items to inspect
    items = receipt_data.get('items', po_data.get('line_items', []))

    # Get quality parameters
    sample_pct = quality_config.get('sample_size_pct', 10)
    aql = quality_config.get('aql_level', 2.5)
    inspection_level = quality_config.get('inspection_level', 'standard')

    # Perform inspection on each item
    inspection_results = []
    overall_defects = {'critical': 0, 'major': 0, 'minor': 0}
    total_inspected = 0
    total_passed = 0

    for item in items:
        item_number = item.get('item_number', '')
        quantity = item.get('quantity', 0)

        # Calculate sample size
        sample_size = max(1, int(quantity * sample_pct / 100))

        # Perform inspection checks
        checks = _perform_inspection_checks(
            item_number,
            inspection_criteria,
            tolerance_config
        )

        # Count defects
        item_defects = {'critical': 0, 'major': 0, 'minor': 0}
        for check in checks:
            if not check['passed']:
                severity = check.get('defect_severity', 'minor')
                item_defects[severity] = item_defects.get(severity, 0) + 1
                overall_defects[severity] = overall_defects.get(severity, 0) + 1

        # Calculate defect rate
        defect_rate = sum(item_defects.values()) / len(checks) * 100 if checks else 0

        # Determine pass/fail
        critical_threshold = quality_config.get('critical_defect_threshold', 0)
        major_threshold = quality_config.get('major_defect_threshold', 2.5)

        if item_defects['critical'] > critical_threshold:
            item_result = 'fail'
            disposition = 'reject'
        elif defect_rate > aql:
            item_result = 'fail'
            disposition = 'review'
        else:
            item_result = 'pass'
            disposition = 'accept'

        total_inspected += sample_size
        if item_result == 'pass':
            total_passed += sample_size

        inspection_results.append({
            'item_number': item_number,
            'description': item.get('description'),
            'quantity_received': quantity,
            'sample_size': sample_size,
            'inspection_checks': checks,
            'defects_found': item_defects,
            'defect_rate': round(defect_rate, 2),
            'result': item_result,
            'disposition': disposition
        })

    # Calculate overall result
    critical_threshold = quality_config.get('critical_defect_threshold', 0)
    if overall_defects['critical'] > critical_threshold:
        overall_result = 'fail'
        overall_disposition = 'reject_lot'
    elif total_passed / total_inspected < 0.95 if total_inspected > 0 else True:
        overall_result = 'conditional_pass'
        overall_disposition = 'partial_accept'
    else:
        overall_result = 'pass'
        overall_disposition = 'accept'

    # Generate inspection record
    inspection_id = f"QC{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    return {
        "inspection_id": inspection_id,
        "inspection_type": inspection_type,
        "inspection_level": inspection_level,
        "po_number": po_data.get('po_number'),
        "receipt_number": receipt_data.get('receipt_number'),
        "inspection_result": overall_result,
        "overall_disposition": overall_disposition,
        "inspection_details": inspection_results,
        "items_inspected": len(inspection_results),
        "quality_metrics": {
            "total_items_sampled": total_inspected,
            "total_passed": total_passed,
            "pass_rate": round(total_passed / total_inspected * 100, 1) if total_inspected > 0 else 100,
            "aql_threshold": aql,
            "defects_by_severity": overall_defects,
            "total_defects": sum(overall_defects.values())
        },
        "sample_size_pct": sample_pct,
        "criteria_used": list(inspection_criteria.keys()),
        "inspector": input_data.get('inspector', 'system'),
        "inspected_at": datetime.utcnow().isoformat(),
        "next_steps": _get_next_steps(overall_disposition),
        "context_driven": bool(context),
        "factory_id": "quality_inspect",
        "factory_version": "2.0.0",
        "context_keys_used": ["quality_config", "inspection_criteria", "tolerance_config"]
    }


def _perform_inspection_checks(item_number: str, criteria: Dict, tolerances: Dict) -> List[Dict]:
    """Perform inspection checks based on criteria."""
    checks = []

    # Visual checks
    for check in criteria.get('visual', []):
        passed = hash(f"{item_number}_{check}") % 100 > 5  # 95% pass rate simulation
        checks.append({
            'category': 'visual',
            'check': check,
            'passed': passed,
            'defect_severity': 'minor' if not passed else None,
            'notes': None if passed else f'{check} defect observed'
        })

    # Dimensional checks
    for check in criteria.get('dimensional', []):
        passed = hash(f"{item_number}_{check}") % 100 > 3  # 97% pass rate simulation
        checks.append({
            'category': 'dimensional',
            'check': check,
            'passed': passed,
            'measured_value': 10.0 if passed else 10.5,
            'tolerance': tolerances.get(check, {'min': 9.9, 'max': 10.1}),
            'defect_severity': 'major' if not passed else None
        })

    # Documentation checks
    for check in criteria.get('documentation', []):
        passed = hash(f"{item_number}_{check}") % 100 > 2  # 98% pass rate simulation
        checks.append({
            'category': 'documentation',
            'check': check,
            'passed': passed,
            'defect_severity': 'minor' if not passed else None
        })

    return checks


def _get_next_steps(disposition: str) -> List[str]:
    """Get next steps based on disposition."""
    steps = {
        'accept': [
            'Move to inventory',
            'Update receiving records',
            'Close inspection record'
        ],
        'partial_accept': [
            'Accept conforming items',
            'Segregate non-conforming items',
            'Create NCR for defects',
            'Contact vendor for replacement'
        ],
        'reject_lot': [
            'Quarantine entire lot',
            'Create NCR',
            'Contact vendor immediately',
            'Arrange return shipment'
        ],
        'review': [
            'Escalate to QA supervisor',
            'Perform additional testing',
            'Document findings'
        ]
    }
    return steps.get(disposition, steps['review'])


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(quality_inspect(event))
