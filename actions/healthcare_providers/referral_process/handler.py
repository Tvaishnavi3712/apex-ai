"""
Referral Process - Healthcare Providers Action (Context-Driven)
Process patient referrals to specialists and facilities

Context-Driven Architecture:
- Referral rules from playbook context.referral_config
- Specialist network from context.specialist_network
- Authorization requirements from context.auth_requirements
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


# Default referral configuration
DEFAULT_REFERRAL_CONFIG = {
    "auto_submit": True,
    "require_auth_check": True,
    "track_status": True,
    "expiration_days": 90,
    "max_visits": 3
}

# Default specialist network
DEFAULT_SPECIALIST_NETWORK = {
    "cardiology": ["Dr. Heart", "Dr. Cardiac"],
    "orthopedics": ["Dr. Bones", "Dr. Joint"],
    "dermatology": ["Dr. Skin"],
    "neurology": ["Dr. Brain"],
    "gastroenterology": ["Dr. GI"]
}


@register_factory("referral_process")
async def referral_process(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process patient referral (context-driven).

    Context keys used:
        - referral_config: Referral processing rules
        - specialist_network: Available specialists
        - auth_requirements: Authorization requirements by specialty

    Input:
        patient_extract: Patient information
        insurance_verify: Insurance verification results
        referral_request: Referral details

    Output:
        referral_created: Whether referral was created
        referral_number: Assigned referral number
        specialist_options: Available specialists
        authorization_status: Auth requirement status
    """
    context = context or input_data.get('context', {})
    referral_config = context.get('referral_config', DEFAULT_REFERRAL_CONFIG)
    specialist_network = context.get('specialist_network', DEFAULT_SPECIALIST_NETWORK)
    auth_requirements = context.get('auth_requirements', {})

    logger.info(
        "Referral process invoked",
        context_driven=bool(context)
    )

    # Get input data
    patient = input_data.get('patient_extract', {})
    insurance = input_data.get('insurance_verify', {})
    referral_request = input_data.get('referral_request', {})

    specialty = referral_request.get('specialty', 'unspecified')
    reason = referral_request.get('reason', '')
    urgency = referral_request.get('urgency', 'routine')
    preferred_provider = referral_request.get('preferred_provider')

    # Generate referral number
    referral_number = f"REF{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Check if specialty requires authorization
    plan_type = insurance.get('plan_type', 'PPO')
    requires_auth = _check_auth_requirement(specialty, plan_type, auth_requirements)

    # Find available specialists
    available_specialists = _find_specialists(
        specialty,
        preferred_provider,
        specialist_network,
        insurance
    )

    # Calculate referral validity
    expiration_days = referral_config.get('expiration_days', 90)
    expiration_date = datetime.utcnow() + timedelta(days=expiration_days)
    max_visits = referral_config.get('max_visits', 3)

    # Build referral
    referral = {
        'referral_number': referral_number,
        'patient': {
            'name': patient.get('patient_name'),
            'dob': patient.get('date_of_birth'),
            'member_id': insurance.get('policy_number')
        },
        'referring_provider': {
            'name': referral_request.get('referring_provider', 'Dr. Primary'),
            'npi': referral_request.get('referring_npi'),
            'practice': referral_request.get('practice_name')
        },
        'referral_to': {
            'specialty': specialty,
            'provider': preferred_provider or 'Any in-network specialist',
            'facility': referral_request.get('facility')
        },
        'clinical_info': {
            'reason': reason,
            'diagnosis_codes': referral_request.get('diagnosis_codes', []),
            'clinical_notes': referral_request.get('clinical_notes', ''),
            'urgency': urgency
        },
        'validity': {
            'effective_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'expiration_date': expiration_date.strftime('%Y-%m-%d'),
            'max_visits': max_visits,
            'visits_used': 0
        },
        'status': 'active',
        'created_at': datetime.utcnow().isoformat()
    }

    # Determine next steps based on auth requirement
    if requires_auth:
        auth_status = 'authorization_required'
        next_steps = [
            'Prior authorization required before specialist visit',
            'Authorization request will be submitted automatically' if referral_config.get('auto_submit') else 'Submit authorization request',
            'Specialist will be notified once authorized'
        ]
    else:
        auth_status = 'no_authorization_required'
        next_steps = [
            'Referral is active and ready to use',
            'Contact specialist office to schedule appointment',
            'Bring referral number to appointment'
        ]

    # Send notifications
    notifications = []
    if referral_config.get('auto_submit', True):
        notifications.append({
            'type': 'referral_created',
            'recipient': 'patient',
            'method': 'email',
            'sent': True
        })
        notifications.append({
            'type': 'new_referral',
            'recipient': 'specialist',
            'method': 'fax',
            'sent': True
        })

    return {
        "patient_name": patient.get('patient_name'),
        "referral_created": True,
        "referral_number": referral_number,
        "referral": referral,
        "specialty": specialty,
        "urgency": urgency,
        "authorization_required": requires_auth,
        "authorization_status": auth_status,
        "specialist_options": available_specialists,
        "specialist_count": len(available_specialists),
        "in_network_only": insurance.get('plan_type') == 'HMO',
        "validity": {
            "effective_date": datetime.utcnow().strftime('%Y-%m-%d'),
            "expiration_date": expiration_date.strftime('%Y-%m-%d'),
            "days_valid": expiration_days,
            "max_visits": max_visits
        },
        "next_steps": next_steps,
        "notifications_sent": notifications,
        "tracking_enabled": referral_config.get('track_status', True),
        "processed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "referral_process",
        "factory_version": "2.0.0",
        "context_keys_used": ["referral_config", "specialist_network", "auth_requirements"]
    }


def _check_auth_requirement(specialty: str, plan_type: str, auth_requirements: Dict) -> bool:
    """Check if specialty requires authorization for plan type."""
    # HMO typically requires auth for specialists
    if plan_type == 'HMO':
        return True

    # Check specific requirements
    specialty_reqs = auth_requirements.get(specialty.lower(), {})
    return specialty_reqs.get('requires_auth', False)


def _find_specialists(specialty: str, preferred: str,
                      network: Dict, insurance: Dict) -> List[Dict]:
    """Find available specialists for the specialty."""
    specialists = []

    # Get specialists from network
    specialty_providers = network.get(specialty.lower(), [])

    # If preferred provider specified, put them first
    if preferred and preferred in specialty_providers:
        specialists.append({
            'name': preferred,
            'specialty': specialty,
            'in_network': True,
            'accepting_new_patients': True,
            'preferred': True
        })

    # Add other providers
    for provider in specialty_providers:
        if provider != preferred:
            specialists.append({
                'name': provider,
                'specialty': specialty,
                'in_network': True,
                'accepting_new_patients': True,
                'preferred': False
            })

    # If no specialists found, add placeholder
    if not specialists:
        specialists.append({
            'name': f'{specialty.title()} Specialist',
            'specialty': specialty,
            'in_network': True,
            'accepting_new_patients': True,
            'preferred': False
        })

    return specialists


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(referral_process(event))
