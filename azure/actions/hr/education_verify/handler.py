"""
Education Verify - HR Action (Context-Driven)
Verify candidate education against job requirements

Context-Driven Architecture:
- Education requirements from playbook context.education_requirements
- Verification settings from context.education_requirements.verification
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


# Default education requirements
DEFAULT_EDUCATION_CONFIG = {
    "minimum_degree": "Bachelors",
    "preferred_degree": "Masters",
    "required_fields": [],
    "preferred_fields": [],
    "require_verification": False
}

# Degree hierarchy
DEGREE_HIERARCHY = {
    'PhD': 4,
    'Doctorate': 4,
    'Masters': 3,
    'MBA': 3,
    'Bachelors': 2,
    'Associates': 1,
    'High School': 0,
    'None': -1
}


@register_factory("education_verify")
async def education_verify(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Verify candidate education (context-driven).

    Context keys used:
        - education_requirements: Required education level and fields

    Input:
        resume_extract: Extracted resume data

    Output:
        education_score: Education match score (0-100)
        highest_degree: Highest degree held
        meets_minimum: Whether meets minimum requirement
        field_match: Whether field of study matches
        verification_status: Verification status
    """
    context = context or input_data.get('context', {})
    edu_requirements = context.get('education_requirements', DEFAULT_EDUCATION_CONFIG)

    logger.info(
        "Education verify invoked",
        context_driven=bool(context)
    )

    # Get education from resume
    resume = input_data.get('resume_extract', {})
    education = resume.get('education', [])
    highest_degree = resume.get('highest_degree')

    # Get requirements
    min_degree = edu_requirements.get('minimum_degree', 'Bachelors')
    preferred_degree = edu_requirements.get('preferred_degree', 'Masters')
    required_fields = edu_requirements.get('required_fields', [])
    preferred_fields = edu_requirements.get('preferred_fields', [])
    require_verification = edu_requirements.get('require_verification', False)

    # Determine highest degree if not provided
    if not highest_degree and education:
        max_level = -1
        for edu in education:
            degree = edu.get('degree', '')
            level = DEGREE_HIERARCHY.get(degree, 0)
            if level > max_level:
                max_level = level
                highest_degree = degree

    # Calculate degree level scores
    candidate_level = DEGREE_HIERARCHY.get(highest_degree, 0)
    min_level = DEGREE_HIERARCHY.get(min_degree, 2)
    preferred_level = DEGREE_HIERARCHY.get(preferred_degree, 3)

    # Calculate score
    score = 0

    # Degree level scoring
    if candidate_level >= preferred_level:
        score += 60
    elif candidate_level >= min_level:
        score += 40 + (20 * (candidate_level - min_level) / max(1, preferred_level - min_level))
    elif candidate_level > 0:
        score += 20 * (candidate_level / min_level)

    # Field of study matching
    candidate_fields = [edu.get('field', '').lower() for edu in education]
    field_match = False
    field_match_type = 'none'

    for field in required_fields:
        if any(field.lower() in cf for cf in candidate_fields):
            field_match = True
            field_match_type = 'required'
            score += 30
            break

    if not field_match:
        for field in preferred_fields:
            if any(field.lower() in cf for cf in candidate_fields):
                field_match = True
                field_match_type = 'preferred'
                score += 20
                break

    if not field_match and not required_fields:
        score += 10  # No field requirement, give partial credit

    # Normalize
    score = max(0, min(100, score))

    # Verification status
    verification_status = 'not_required'
    if require_verification:
        verification_status = 'pending'

    # Check if meets minimum
    meets_minimum = candidate_level >= min_level

    return {
        "education_score": round(score, 1),
        "highest_degree": highest_degree,
        "candidate_degree_level": candidate_level,
        "required_degree_level": min_level,
        "meets_minimum": meets_minimum,
        "exceeds_preferred": candidate_level >= preferred_level,
        "field_match": field_match,
        "field_match_type": field_match_type,
        "candidate_fields": candidate_fields,
        "education_count": len(education),
        "verification_status": verification_status,
        "verification_required": require_verification,
        "verified_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "education_verify",
        "factory_version": "2.0.0",
        "context_keys_used": ["education_requirements"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(education_verify(event))
