"""
Auth Check - Healthcare Payers Action (Context-Driven)
Check prior authorization requirements and status

Context-Driven Architecture:
- Auth requirements from playbook context.auth_config
- Service categories from context.service_categories
- Auth rules from context.authorization_rules
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


# Default auth requirements
DEFAULT_AUTH_CONFIG = {
    "always_required": [
        "inpatient_admission", "surgery", "imaging_advanced",
        "dme_high_cost", "specialty_drugs", "transplant"
    ],
    "threshold_required": {
        "outpatient_surgery": {"cost_threshold": 5000},
        "imaging_standard": {"units_threshold": 3},
        "therapy": {"visits_threshold": 12}
    },
    "exempt_services": [
        "preventive_care", "emergency", "maternity_delivery"
    ]
}

# Service category mappings
DEFAULT_SERVICE_CATEGORIES = {
    "99213": "office_visit",
    "99214": "office_visit",
    "70553": "imaging_advanced",
    "70551": "imaging_advanced",
    "27447": "surgery",
    "43239": "surgery"
}


@register_factory("auth_check")
async def auth_check(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Check prior authorization requirements (context-driven).

    Context keys used:
        - auth_config: Authorization requirements
        - service_categories: Service to category mappings
        - authorization_rules: Auth decision rules

    Input:
        claim_extract: Extracted claim data
        member_info: Member eligibility info

    Output:
        auth_required: Whether authorization is required
        auth_status: Authorization status if exists
        auth_number: Authorization number if approved
        denial_reason: Reason if denied
    """
    context = context or input_data.get('context', {})
    auth_config = context.get('auth_config', DEFAULT_AUTH_CONFIG)
    service_categories = context.get('service_categories', DEFAULT_SERVICE_CATEGORIES)
    auth_rules = context.get('authorization_rules', {})

    logger.info(
        "Auth check invoked",
        context_driven=bool(context)
    )

    # Get claim data
    claim = input_data.get('claim_extract', {})
    claim_data = claim.get('claim_data', {})
    member = input_data.get('member_info', {})

    procedures = claim_data.get('procedure_codes', [])
    billed_amount = claim_data.get('billed_amount', 0)

    # Categorize services
    service_cats = []
    for proc in procedures:
        code = proc.get('code', '')
        category = service_categories.get(code, 'other')
        service_cats.append({
            'code': code,
            'category': category,
            'units': proc.get('units', 1)
        })

    # Check if auth required
    auth_required = False
    auth_reasons = []

    always_required = auth_config.get('always_required', [])
    exempt_services = auth_config.get('exempt_services', [])
    threshold_required = auth_config.get('threshold_required', {})

    for svc in service_cats:
        category = svc['category']

        # Check exemptions first
        if category in exempt_services:
            continue

        # Check always required
        if category in always_required:
            auth_required = True
            auth_reasons.append(f"{category} always requires authorization")
            continue

        # Check threshold-based requirements
        if category in threshold_required:
            thresholds = threshold_required[category]

            if 'cost_threshold' in thresholds:
                if billed_amount >= thresholds['cost_threshold']:
                    auth_required = True
                    auth_reasons.append(f"{category} exceeds cost threshold ${thresholds['cost_threshold']}")

            if 'units_threshold' in thresholds:
                if svc['units'] >= thresholds['units_threshold']:
                    auth_required = True
                    auth_reasons.append(f"{category} exceeds units threshold {thresholds['units_threshold']}")

    # Look up existing authorization
    auth_number = None
    auth_status = 'not_required'
    auth_valid = True
    denial_reason = None

    if auth_required:
        # Simulated auth lookup
        existing_auth = input_data.get('existing_auth', {})

        if existing_auth:
            auth_number = existing_auth.get('auth_number')
            auth_status = existing_auth.get('status', 'pending')

            # Validate auth
            auth_valid = _validate_auth(existing_auth, claim_data)

            if not auth_valid:
                denial_reason = "Authorization does not cover submitted services"
        else:
            auth_status = 'required_not_found'
            auth_valid = False
            denial_reason = "Prior authorization required but not found"

    # Determine processing recommendation
    if not auth_required:
        recommendation = 'process'
    elif auth_status == 'approved' and auth_valid:
        recommendation = 'process'
    elif auth_status == 'pending':
        recommendation = 'pend_for_auth'
    else:
        recommendation = 'deny_no_auth'

    return {
        "claim_number": claim.get('claim_number'),
        "auth_required": auth_required,
        "auth_reasons": auth_reasons,
        "auth_status": auth_status,
        "auth_number": auth_number,
        "auth_valid": auth_valid,
        "denial_reason": denial_reason,
        "service_categories": service_cats,
        "recommendation": recommendation,
        "exempt_services_found": [s['category'] for s in service_cats if s['category'] in exempt_services],
        "checked_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "auth_check",
        "factory_version": "2.0.0",
        "context_keys_used": ["auth_config", "service_categories", "authorization_rules"]
    }


def _validate_auth(auth: Dict, claim_data: Dict) -> bool:
    """Validate authorization covers claim services."""
    if auth.get('status') != 'approved':
        return False

    # Check date validity
    auth_end = auth.get('end_date')
    service_date = claim_data.get('service_dates', {}).get('from_date')

    if auth_end and service_date:
        if service_date > auth_end:
            return False

    # Check units remaining
    units_authorized = auth.get('units_authorized', 0)
    units_used = auth.get('units_used', 0)
    claim_units = sum(p.get('units', 1) for p in claim_data.get('procedure_codes', []))

    if claim_units > (units_authorized - units_used):
        return False

    return True


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(auth_check(event))
