"""
EOB Generate - Healthcare Payers Action (Context-Driven)
Generate Explanation of Benefits document

Context-Driven Architecture:
- EOB template from playbook context.eob_config
- Member communication settings from context.member_communications
- Delivery preferences from context.delivery_config
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


# Default EOB configuration
DEFAULT_EOB_CONFIG = {
    "template": "standard_eob",
    "include_sections": [
        "header", "member_info", "provider_info", "service_details",
        "payment_summary", "member_responsibility", "appeal_rights"
    ],
    "language": "en",
    "format": "pdf"
}

# Default delivery configuration
DEFAULT_DELIVERY_CONFIG = {
    "default_method": "mail",
    "electronic_eligible": True,
    "email_enabled": True,
    "portal_enabled": True
}


@register_factory("eob_generate")
async def eob_generate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate Explanation of Benefits (context-driven).

    Context keys used:
        - eob_config: EOB template and content settings
        - member_communications: Communication preferences
        - delivery_config: Delivery method settings

    Input:
        claim_extract: Extracted claim data
        benefits_apply: Benefits calculation result
        payment_post: Payment posting result
        member_info: Member information

    Output:
        eob_generated: Whether EOB was generated
        eob_document: EOB document reference
        delivery_method: How EOB will be delivered
    """
    context = context or input_data.get('context', {})
    eob_config = context.get('eob_config', DEFAULT_EOB_CONFIG)
    delivery_config = context.get('delivery_config', DEFAULT_DELIVERY_CONFIG)
    member_comms = context.get('member_communications', {})

    logger.info(
        "EOB generate invoked",
        context_driven=bool(context)
    )

    # Get input data
    claim = input_data.get('claim_extract', {})
    claim_data = claim.get('claim_data', {})
    benefits = input_data.get('benefits_apply', {})
    payment = input_data.get('payment_post', {})
    member = input_data.get('member_info', {})

    claim_number = claim.get('claim_number', '')

    # Build EOB content
    eob_content = _build_eob_content(
        claim_data,
        benefits,
        payment,
        member,
        eob_config
    )

    # Generate EOB document reference
    eob_id = f"EOB{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Determine delivery method
    member_preferences = member.get('communication_preferences', {})

    if member_preferences.get('paperless', False) and delivery_config.get('electronic_eligible', True):
        if member_preferences.get('email') and delivery_config.get('email_enabled', True):
            delivery_method = 'email'
        elif delivery_config.get('portal_enabled', True):
            delivery_method = 'portal'
        else:
            delivery_method = 'mail'
    else:
        delivery_method = delivery_config.get('default_method', 'mail')

    # Generate document
    document_format = eob_config.get('format', 'pdf')

    eob_document = {
        'eob_id': eob_id,
        'claim_number': claim_number,
        'member_id': member.get('member_id', claim_data.get('patient_info', {}).get('member_id')),
        'document_type': 'explanation_of_benefits',
        'format': document_format,
        'language': eob_config.get('language', 'en'),
        'generated_date': datetime.utcnow().isoformat(),
        'storage_location': f"s3://eob-documents/{eob_id}.{document_format}",
        'sections_included': eob_config.get('include_sections', [])
    }

    # Delivery details
    delivery_details = {
        'method': delivery_method,
        'status': 'queued',
        'scheduled_date': datetime.utcnow().strftime('%Y-%m-%d')
    }

    if delivery_method == 'email':
        delivery_details['email'] = member_preferences.get('email', member.get('email'))
    elif delivery_method == 'mail':
        delivery_details['address'] = member.get('address', {})

    return {
        "claim_number": claim_number,
        "eob_generated": True,
        "eob_id": eob_id,
        "eob_document": eob_document,
        "eob_content_summary": {
            "service_date": claim_data.get('service_dates', {}).get('from_date'),
            "provider": claim_data.get('provider_info', {}).get('name'),
            "billed_amount": benefits.get('billed_amount', 0),
            "allowed_amount": benefits.get('allowed_amount', 0),
            "plan_paid": payment.get('payment_amount', benefits.get('plan_payment', 0)),
            "member_responsibility": benefits.get('member_responsibility', 0)
        },
        "delivery_method": delivery_method,
        "delivery_details": delivery_details,
        "appeal_deadline": _calculate_appeal_deadline(),
        "generated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "eob_generate",
        "factory_version": "2.0.0",
        "context_keys_used": ["eob_config", "member_communications", "delivery_config"]
    }


def _build_eob_content(claim_data: Dict, benefits: Dict,
                       payment: Dict, member: Dict, config: Dict) -> Dict:
    """Build EOB content based on configuration."""
    content = {}
    sections = config.get('include_sections', [])

    if 'header' in sections:
        content['header'] = {
            'title': 'Explanation of Benefits',
            'subtitle': 'This is not a bill',
            'date': datetime.utcnow().strftime('%B %d, %Y')
        }

    if 'member_info' in sections:
        patient = claim_data.get('patient_info', {})
        content['member_info'] = {
            'member_id': patient.get('member_id'),
            'name': f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
            'date_of_birth': patient.get('date_of_birth')
        }

    if 'provider_info' in sections:
        provider = claim_data.get('provider_info', {})
        content['provider_info'] = {
            'name': provider.get('name'),
            'address': provider.get('address', {})
        }

    if 'service_details' in sections:
        content['service_details'] = {
            'service_date': claim_data.get('service_dates', {}),
            'procedures': claim_data.get('procedure_codes', []),
            'diagnoses': claim_data.get('diagnosis_codes', [])
        }

    if 'payment_summary' in sections:
        content['payment_summary'] = {
            'billed': benefits.get('billed_amount', 0),
            'allowed': benefits.get('allowed_amount', 0),
            'plan_paid': payment.get('payment_amount', 0),
            'member_owes': benefits.get('member_responsibility', 0)
        }

    if 'appeal_rights' in sections:
        content['appeal_rights'] = {
            'text': 'You have the right to appeal this decision within 180 days.',
            'deadline': _calculate_appeal_deadline()
        }

    return content


def _calculate_appeal_deadline() -> str:
    """Calculate appeal deadline (180 days from now)."""
    from datetime import timedelta
    deadline = datetime.utcnow() + timedelta(days=180)
    return deadline.strftime('%Y-%m-%d')


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(eob_generate(event))
