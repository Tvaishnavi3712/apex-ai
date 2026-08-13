"""
Candidate Route - HR Action (Context-Driven)
Route candidates through the hiring workflow

Context-Driven Architecture:
- Routing rules from playbook context.routing_config
- Workflow stages from context.workflow_config
- Notification settings from context.notifications
"""

from typing import Dict, Any, Optional
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


# Default routing configuration
DEFAULT_ROUTING_CONFIG = {
    "auto_advance_score": 80,
    "auto_reject_score": 40,
    "review_queue": "recruiter_review",
    "stages": ["screening", "phone_interview", "technical_interview", "onsite", "offer"]
}


@register_factory("candidate_route")
async def candidate_route(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Route candidate through hiring workflow (context-driven).

    Context keys used:
        - routing_config: Routing rules and thresholds
        - workflow_config: Workflow stages
        - notifications: Notification settings

    Input:
        candidate_score: Overall candidate scoring
        resume_extract: Resume data

    Output:
        routing_decision: Routing decision (advance, review, reject)
        next_stage: Next stage in workflow
        assigned_to: Assigned recruiter/hiring manager
        notifications_sent: Notifications triggered
    """
    context = context or input_data.get('context', {})
    routing_config = context.get('routing_config', DEFAULT_ROUTING_CONFIG)
    workflow_config = context.get('workflow_config', {})

    logger.info(
        "Candidate route invoked",
        context_driven=bool(context)
    )

    # Get scoring from upstream
    scoring = input_data.get('candidate_score', {})
    resume = input_data.get('resume_extract', {})

    overall_score = scoring.get('overall_score', 50)
    recommendation = scoring.get('recommendation', 'review')

    # Get thresholds from context
    auto_advance = routing_config.get('auto_advance_score', 80)
    auto_reject = routing_config.get('auto_reject_score', 40)
    stages = routing_config.get('stages', DEFAULT_ROUTING_CONFIG['stages'])

    # Determine routing decision
    if overall_score >= auto_advance:
        routing_decision = 'advance'
        next_stage = stages[1] if len(stages) > 1 else stages[0]
        assigned_to = _assign_interviewer(next_stage, routing_config)
    elif overall_score < auto_reject:
        routing_decision = 'reject'
        next_stage = 'rejected'
        assigned_to = None
    else:
        routing_decision = 'review'
        next_stage = 'recruiter_review'
        assigned_to = _assign_recruiter(routing_config)

    # Prepare notifications
    notifications_to_send = []

    if routing_decision == 'advance':
        notifications_to_send.append({
            'type': 'candidate_advanced',
            'recipient': 'hiring_manager',
            'channel': 'email'
        })
        notifications_to_send.append({
            'type': 'interview_scheduled',
            'recipient': 'candidate',
            'channel': 'email'
        })
    elif routing_decision == 'reject':
        notifications_to_send.append({
            'type': 'application_rejected',
            'recipient': 'candidate',
            'channel': 'email'
        })
    else:
        notifications_to_send.append({
            'type': 'review_required',
            'recipient': 'recruiter',
            'channel': 'slack'
        })

    # Calculate SLA
    sla_hours = routing_config.get('review_sla_hours', 48)
    sla_due = datetime.utcnow().timestamp() + (sla_hours * 3600)

    return {
        "candidate_name": resume.get('candidate_name'),
        "candidate_email": resume.get('email'),
        "overall_score": overall_score,
        "routing_decision": routing_decision,
        "next_stage": next_stage,
        "current_stage": 'screening',
        "assigned_to": assigned_to,
        "notifications_to_send": notifications_to_send,
        "notification_count": len(notifications_to_send),
        "sla_hours": sla_hours,
        "sla_due": datetime.fromtimestamp(sla_due).isoformat(),
        "workflow_stages": stages,
        "routed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "candidate_route",
        "factory_version": "2.0.0",
        "context_keys_used": ["routing_config", "workflow_config"]
    }


def _assign_recruiter(routing_config: Dict) -> Dict[str, Any]:
    """Assign recruiter for review."""
    return {
        'type': 'recruiter',
        'assignment_method': 'round_robin',
        'queue': routing_config.get('review_queue', 'recruiter_review')
    }


def _assign_interviewer(stage: str, routing_config: Dict) -> Dict[str, Any]:
    """Assign interviewer for next stage."""
    return {
        'type': 'interviewer',
        'stage': stage,
        'assignment_method': 'hiring_manager'
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(candidate_route(event))
