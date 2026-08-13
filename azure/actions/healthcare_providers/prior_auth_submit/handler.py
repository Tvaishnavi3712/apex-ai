"""
Prior Auth Submit - Healthcare Providers Action (Context-Driven)
Submit prior authorization requests to payers

Context-Driven Architecture:
- Authorization settings from playbook context.auth_config
- Payer requirements from context.payer_auth_requirements
- Submission preferences from context.submission_config
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


# Default authorization configuration
DEFAULT_AUTH_CONFIG = {
    "submission_methods": ["electronic", "fax", "phone"],
    "preferred_method": "electronic",
    "auto_submit": True,
    "track_status": True,
    "follow_up_days": 3
}

# Default payer auth requirements
DEFAULT_PAYER_AUTH_REQUIREMENTS = {
    "default": {
        "required_documents": ["clinical_notes", "diagnosis", "treatment_plan"],
        "supporting_documents": ["lab_results", "imaging_results"],
        "urgency_levels": ["routine", "urgent", "emergent"],
        "expected_turnaround_days": {"routine": 14, "urgent": 3, "emergent": 1}
    }
}


@register_factory("prior_auth_submit")
async def prior_auth_submit(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Submit prior authorization request (context-driven).

    Context keys used:
        - auth_config: Authorization submission settings
        - payer_auth_requirements: Payer-specific requirements
        - submission_config: Submission method preferences

    Input:
        patient_extract: Patient information
        insurance_verify: Insurance verification results
        service_info: Service requiring authorization
        clinical_info: Supporting clinical documentation

    Output:
        submission_status: Whether submission was successful
        auth_request_number: Assigned request number
        expected_decision_date: Expected decision timeline
    """
    context = context or input_data.get('context', {})
    auth_config = context.get('auth_config', DEFAULT_AUTH_CONFIG)
    payer_requirements = context.get('payer_auth_requirements', DEFAULT_PAYER_AUTH_REQUIREMENTS)

    logger.info(
        "Prior auth submit invoked",
        context_driven=bool(context)
    )

    # Get input data
    patient = input_data.get('patient_extract', {})
    insurance = input_data.get('insurance_verify', {})
    service_info = input_data.get('service_info', {})
    clinical_info = input_data.get('clinical_info', {})

    # Determine payer
    carrier = insurance.get('carrier', 'Unknown')
    payer_key = carrier.lower().replace(' ', '_')

    # Get payer-specific requirements
    payer_reqs = payer_requirements.get(payer_key, payer_requirements.get('default', {}))

    # Validate required documents
    required_docs = payer_reqs.get('required_documents', [])
    provided_docs = clinical_info.get('documents', [])
    provided_doc_types = [d.get('type', '') for d in provided_docs]

    missing_docs = [doc for doc in required_docs if doc not in provided_doc_types]

    # Determine urgency
    urgency = service_info.get('urgency', 'routine')
    turnaround = payer_reqs.get('expected_turnaround_days', {}).get(urgency, 14)

    # Generate auth request number
    auth_request_number = f"AUTH{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Determine submission method
    submission_methods = auth_config.get('submission_methods', ['electronic'])
    preferred_method = auth_config.get('preferred_method', 'electronic')

    if preferred_method in submission_methods:
        submission_method = preferred_method
    else:
        submission_method = submission_methods[0] if submission_methods else 'fax'

    # Build auth request
    auth_request = {
        'request_number': auth_request_number,
        'patient': {
            'name': patient.get('patient_name'),
            'dob': patient.get('date_of_birth'),
            'member_id': insurance.get('policy_number')
        },
        'insurance': {
            'carrier': carrier,
            'plan': insurance.get('plan_name'),
            'group': insurance.get('verification_result', {}).get('group_name')
        },
        'service': {
            'type': service_info.get('service_type', 'procedure'),
            'procedure_code': service_info.get('procedure_code'),
            'diagnosis_codes': service_info.get('diagnosis_codes', []),
            'description': service_info.get('description'),
            'requested_date': service_info.get('requested_date'),
            'units': service_info.get('units', 1)
        },
        'clinical_justification': clinical_info.get('justification', ''),
        'urgency': urgency,
        'requesting_provider': {
            'npi': service_info.get('provider_npi'),
            'name': service_info.get('provider_name')
        },
        'rendering_provider': service_info.get('rendering_provider', {}),
        'facility': service_info.get('facility', {})
    }

    # Check if auto-submit is enabled
    auto_submit = auth_config.get('auto_submit', True)

    if missing_docs and auto_submit:
        submission_status = 'pending_documents'
        status_message = f"Missing required documents: {', '.join(missing_docs)}"
    elif auto_submit:
        submission_status = 'submitted'
        status_message = f"Authorization request submitted via {submission_method}"
    else:
        submission_status = 'ready_for_submission'
        status_message = "Authorization request ready for manual submission"

    # Calculate expected decision date
    expected_decision_date = datetime.utcnow() + timedelta(days=turnaround)

    # Follow-up schedule
    follow_up_days = auth_config.get('follow_up_days', 3)
    follow_up_date = datetime.utcnow() + timedelta(days=follow_up_days)

    return {
        "patient_name": patient.get('patient_name'),
        "carrier": carrier,
        "submission_status": submission_status,
        "status_message": status_message,
        "auth_request_number": auth_request_number,
        "auth_request": auth_request,
        "submission_method": submission_method,
        "urgency": urgency,
        "missing_documents": missing_docs,
        "documents_provided": len(provided_docs),
        "expected_turnaround_days": turnaround,
        "expected_decision_date": expected_decision_date.strftime('%Y-%m-%d'),
        "follow_up_date": follow_up_date.strftime('%Y-%m-%d'),
        "tracking": {
            "track_status": auth_config.get('track_status', True),
            "auto_follow_up": auth_config.get('auto_follow_up', True),
            "notification_method": "email"
        },
        "submitted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "prior_auth_submit",
        "factory_version": "2.0.0",
        "context_keys_used": ["auth_config", "payer_auth_requirements", "submission_config"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(prior_auth_submit(event))
