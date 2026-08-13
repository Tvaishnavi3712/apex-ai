"""
Appeal Process - Healthcare Payers Action (Context-Driven)
Process claim appeals and grievances

Context-Driven Architecture:
- Appeal rules from playbook context.appeal_config
- Review levels from context.appeal_levels
- Timeline requirements from context.appeal_timelines
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


# Default appeal configuration
DEFAULT_APPEAL_CONFIG = {
    "appeal_types": ["standard", "expedited", "external"],
    "filing_deadline_days": 180,
    "expedited_criteria": ["urgent_care", "life_threatening", "ongoing_treatment"],
    "auto_escalate_days": 30
}

# Default appeal levels
DEFAULT_APPEAL_LEVELS = {
    "level_1": {
        "name": "Internal Review",
        "timeline_days": 30,
        "reviewer": "medical_director"
    },
    "level_2": {
        "name": "Independent Review",
        "timeline_days": 45,
        "reviewer": "external_reviewer"
    },
    "level_3": {
        "name": "External Appeal",
        "timeline_days": 60,
        "reviewer": "state_regulatory"
    }
}


@register_factory("appeal_process")
async def appeal_process(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process claim appeal (context-driven).

    Context keys used:
        - appeal_config: Appeal processing rules
        - appeal_levels: Review level configurations
        - appeal_timelines: Timeline requirements

    Input:
        claim_number: Original claim number
        appeal_reason: Reason for appeal
        supporting_documents: List of supporting documents
        appeal_type: Type of appeal (standard/expedited)

    Output:
        appeal_accepted: Whether appeal was accepted
        appeal_number: Assigned appeal number
        appeal_level: Current appeal level
        timeline: Expected timeline
    """
    context = context or input_data.get('context', {})
    appeal_config = context.get('appeal_config', DEFAULT_APPEAL_CONFIG)
    appeal_levels = context.get('appeal_levels', DEFAULT_APPEAL_LEVELS)
    appeal_timelines = context.get('appeal_timelines', {})

    logger.info(
        "Appeal process invoked",
        context_driven=bool(context)
    )

    # Get input data
    claim_number = input_data.get('claim_number', '')
    appeal_reason = input_data.get('appeal_reason', '')
    appeal_type = input_data.get('appeal_type', 'standard')
    supporting_docs = input_data.get('supporting_documents', [])
    original_decision_date = input_data.get('original_decision_date')

    # Validate appeal eligibility
    eligibility = _check_appeal_eligibility(
        original_decision_date,
        appeal_config,
        appeal_type
    )

    if not eligibility['eligible']:
        return {
            "claim_number": claim_number,
            "appeal_accepted": False,
            "rejection_reason": eligibility['reason'],
            "processed_at": datetime.utcnow().isoformat(),
            "context_driven": bool(context),
            "factory_id": "appeal_process",
            "factory_version": "2.0.0",
            "context_keys_used": ["appeal_config"]
        }

    # Generate appeal number
    appeal_number = f"APL{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    # Determine appeal level
    current_level = input_data.get('current_level', 'level_1')
    level_config = appeal_levels.get(current_level, DEFAULT_APPEAL_LEVELS['level_1'])

    # Calculate timeline
    if appeal_type == 'expedited':
        timeline_days = min(3, level_config.get('timeline_days', 30) // 10)
    else:
        timeline_days = level_config.get('timeline_days', 30)

    decision_due_date = datetime.utcnow() + timedelta(days=timeline_days)

    # Categorize appeal
    appeal_category = _categorize_appeal(appeal_reason)

    # Determine reviewer assignment
    reviewer_type = level_config.get('reviewer', 'claims_examiner')

    if appeal_category == 'medical_necessity':
        reviewer_type = 'medical_director'
    elif appeal_category == 'coding':
        reviewer_type = 'coding_specialist'

    # Create appeal record
    appeal_record = {
        'appeal_number': appeal_number,
        'claim_number': claim_number,
        'appeal_type': appeal_type,
        'appeal_reason': appeal_reason,
        'appeal_category': appeal_category,
        'current_level': current_level,
        'level_name': level_config.get('name', 'Internal Review'),
        'status': 'received',
        'received_date': datetime.utcnow().isoformat(),
        'decision_due_date': decision_due_date.isoformat(),
        'assigned_reviewer': reviewer_type,
        'supporting_documents': len(supporting_docs)
    }

    # Generate acknowledgment
    acknowledgment = {
        'sent': True,
        'method': 'letter',
        'content': f"Your appeal {appeal_number} has been received and will be reviewed within {timeline_days} days."
    }

    # Next steps
    next_steps = [
        f"Review by {reviewer_type}",
        "Medical record review if applicable",
        f"Decision by {decision_due_date.strftime('%B %d, %Y')}"
    ]

    if current_level != 'level_3':
        next_steps.append("Right to escalate if decision is unfavorable")

    return {
        "claim_number": claim_number,
        "appeal_accepted": True,
        "appeal_number": appeal_number,
        "appeal_type": appeal_type,
        "appeal_category": appeal_category,
        "current_level": current_level,
        "level_name": level_config.get('name'),
        "appeal_record": appeal_record,
        "timeline": {
            "received_date": datetime.utcnow().isoformat(),
            "timeline_days": timeline_days,
            "decision_due_date": decision_due_date.isoformat(),
            "is_expedited": appeal_type == 'expedited'
        },
        "assigned_reviewer": reviewer_type,
        "acknowledgment": acknowledgment,
        "next_steps": next_steps,
        "escalation_available": current_level != 'level_3',
        "processed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "appeal_process",
        "factory_version": "2.0.0",
        "context_keys_used": ["appeal_config", "appeal_levels", "appeal_timelines"]
    }


def _check_appeal_eligibility(original_date: str, config: Dict, appeal_type: str) -> Dict:
    """Check if appeal is eligible based on filing deadline."""
    if not original_date:
        return {'eligible': True, 'reason': None}

    try:
        original_dt = datetime.fromisoformat(original_date.replace('Z', '+00:00'))
        deadline_days = config.get('filing_deadline_days', 180)
        deadline = original_dt + timedelta(days=deadline_days)

        if datetime.utcnow() > deadline:
            return {
                'eligible': False,
                'reason': f'Appeal deadline of {deadline_days} days has passed'
            }
    except (ValueError, TypeError):
        pass

    return {'eligible': True, 'reason': None}


def _categorize_appeal(reason: str) -> str:
    """Categorize appeal based on reason."""
    reason_lower = reason.lower()

    if any(term in reason_lower for term in ['medical necessity', 'medically necessary', 'treatment']):
        return 'medical_necessity'
    elif any(term in reason_lower for term in ['code', 'coding', 'modifier', 'cpt', 'icd']):
        return 'coding'
    elif any(term in reason_lower for term in ['coverage', 'covered', 'benefit', 'exclusion']):
        return 'coverage'
    elif any(term in reason_lower for term in ['network', 'out of network', 'provider']):
        return 'network'
    elif any(term in reason_lower for term in ['authorization', 'auth', 'prior auth']):
        return 'authorization'
    else:
        return 'general'


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(appeal_process(event))
