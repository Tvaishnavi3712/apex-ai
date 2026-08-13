"""
Supplier Validate - Manufacturing Action (Context-Driven)
Validate supplier information and compliance

Context-Driven Architecture:
- Supplier requirements from playbook context.supplier_config
- Compliance rules from context.compliance_config
- Quality standards from context.supplier_quality_config
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


# Default supplier configuration
DEFAULT_SUPPLIER_CONFIG = {
    "require_w9": True,
    "require_insurance": True,
    "insurance_minimum": 1000000,
    "require_quality_cert": True,
    "valid_certifications": ["ISO9001", "AS9100", "IATF16949"]
}

# Default compliance configuration
DEFAULT_COMPLIANCE_CONFIG = {
    "require_conflict_minerals": True,
    "require_environmental": True,
    "sanctions_check": True
}


@register_factory("supplier_validate")
async def supplier_validate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate supplier information (context-driven).

    Context keys used:
        - supplier_config: Supplier requirements
        - compliance_config: Regulatory compliance requirements
        - supplier_quality_config: Quality standards for suppliers

    Input:
        supplier_info: Supplier information to validate
        po_extract: PO data with vendor info

    Output:
        validation_passed: Whether validation passed
        validation_results: Detailed validation results
        compliance_status: Compliance check results
        approval_status: Supplier approval status
    """
    context = context or input_data.get('context', {})
    supplier_config = context.get('supplier_config', DEFAULT_SUPPLIER_CONFIG)
    compliance_config = context.get('compliance_config', DEFAULT_COMPLIANCE_CONFIG)
    quality_config = context.get('supplier_quality_config', {})

    logger.info(
        "Supplier validate invoked",
        context_driven=bool(context)
    )

    # Get supplier info
    supplier_info = input_data.get('supplier_info', {})
    po_data = input_data.get('po_extract', {})

    # If supplier not provided directly, get from PO
    if not supplier_info and po_data:
        supplier_info = po_data.get('vendor_info', {})

    vendor_name = supplier_info.get('vendor_name', 'Unknown')
    vendor_id = supplier_info.get('vendor_id', '')

    # Perform validation checks
    validation_results = {}
    issues = []

    # Tax documentation check
    if supplier_config.get('require_w9', True):
        has_w9 = supplier_info.get('w9_on_file', False)
        validation_results['tax_documentation'] = {
            'check': 'W-9 on file',
            'passed': has_w9,
            'message': 'W-9 on file' if has_w9 else 'W-9 required'
        }
        if not has_w9:
            issues.append('Missing W-9')

    # Insurance check
    if supplier_config.get('require_insurance', True):
        insurance = supplier_info.get('insurance', {})
        has_insurance = insurance.get('active', False)
        coverage = insurance.get('coverage_amount', 0)
        min_coverage = supplier_config.get('insurance_minimum', 1000000)

        insurance_valid = has_insurance and coverage >= min_coverage
        validation_results['insurance'] = {
            'check': 'Liability insurance',
            'passed': insurance_valid,
            'coverage': coverage,
            'minimum_required': min_coverage,
            'message': f'Coverage ${coverage:,}' if insurance_valid else f'Insufficient coverage (need ${min_coverage:,})'
        }
        if not insurance_valid:
            issues.append('Insufficient insurance coverage')

    # Quality certification check
    if supplier_config.get('require_quality_cert', True):
        certifications = supplier_info.get('certifications', [])
        valid_certs = supplier_config.get('valid_certifications', [])

        has_valid_cert = any(cert in valid_certs for cert in certifications)
        validation_results['quality_certification'] = {
            'check': 'Quality certification',
            'passed': has_valid_cert,
            'certifications': certifications,
            'valid_certifications': valid_certs,
            'message': f'Has {certifications}' if has_valid_cert else 'Missing quality certification'
        }
        if not has_valid_cert:
            issues.append('Missing quality certification')

    # Compliance checks
    compliance_results = _perform_compliance_checks(
        supplier_info,
        compliance_config
    )
    validation_results['compliance'] = compliance_results

    if not compliance_results.get('passed', True):
        issues.extend(compliance_results.get('issues', []))

    # Quality performance check
    performance = _check_quality_performance(vendor_id, quality_config)
    validation_results['quality_performance'] = performance

    if performance.get('score', 100) < quality_config.get('minimum_score', 70):
        issues.append('Below minimum quality performance score')

    # Overall validation result
    all_passed = all(
        r.get('passed', True)
        for r in validation_results.values()
        if isinstance(r, dict)
    )

    # Determine approval status
    if all_passed:
        approval_status = 'approved'
    elif len(issues) <= 2:
        approval_status = 'conditional'
    else:
        approval_status = 'not_approved'

    # Expiration date for approval
    if approval_status in ['approved', 'conditional']:
        expiration_date = datetime.utcnow() + timedelta(days=365)
    else:
        expiration_date = None

    return {
        "vendor_name": vendor_name,
        "vendor_id": vendor_id,
        "validation_passed": all_passed,
        "validation_results": validation_results,
        "issues_found": issues,
        "issue_count": len(issues),
        "approval_status": approval_status,
        "approval_expiration": expiration_date.strftime('%Y-%m-%d') if expiration_date else None,
        "quality_score": performance.get('score', 0),
        "compliance_status": compliance_results.get('status', 'unknown'),
        "next_steps": _get_next_steps(approval_status, issues),
        "validated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "supplier_validate",
        "factory_version": "2.0.0",
        "context_keys_used": ["supplier_config", "compliance_config", "supplier_quality_config"]
    }


def _perform_compliance_checks(supplier_info: Dict, compliance_config: Dict) -> Dict:
    """Perform regulatory compliance checks."""
    issues = []

    # Conflict minerals check
    if compliance_config.get('require_conflict_minerals', True):
        has_declaration = supplier_info.get('conflict_minerals_declaration', False)
        if not has_declaration:
            issues.append('Missing conflict minerals declaration')

    # Environmental compliance
    if compliance_config.get('require_environmental', True):
        env_compliant = supplier_info.get('environmental_compliant', True)
        if not env_compliant:
            issues.append('Environmental compliance issue')

    # Sanctions check
    if compliance_config.get('sanctions_check', True):
        # Simulated sanctions check
        sanctions_clear = True  # Would check against OFAC, etc.
        if not sanctions_clear:
            issues.append('Sanctions list match')

    return {
        'passed': len(issues) == 0,
        'status': 'compliant' if len(issues) == 0 else 'non_compliant',
        'issues': issues,
        'checks_performed': ['conflict_minerals', 'environmental', 'sanctions']
    }


def _check_quality_performance(vendor_id: str, quality_config: Dict) -> Dict:
    """Check supplier quality performance history."""
    # Simulated quality metrics
    return {
        'score': 92,
        'on_time_delivery_pct': 95,
        'quality_defect_rate': 0.5,
        'responsiveness_rating': 4.5,
        'orders_last_12_months': 24,
        'trend': 'improving'
    }


def _get_next_steps(approval_status: str, issues: List[str]) -> List[str]:
    """Get next steps based on approval status."""
    steps = {
        'approved': [
            'Supplier approved for purchasing',
            'Add to approved vendor list',
            'Set up in procurement system'
        ],
        'conditional': [
            'Supplier conditionally approved',
            f'Resolve issues: {", ".join(issues[:2])}',
            'Complete full approval within 30 days'
        ],
        'not_approved': [
            'Supplier not approved',
            'Contact supplier to resolve issues',
            f'Required: {", ".join(issues[:3])}',
            'Resubmit after issues resolved'
        ]
    }
    return steps.get(approval_status, steps['not_approved'])


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(supplier_validate(event))
