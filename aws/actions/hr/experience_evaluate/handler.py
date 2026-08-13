"""
Experience Evaluate - HR Action (Context-Driven)
Evaluate candidate work experience against job requirements

Context-Driven Architecture:
- Experience requirements from playbook context.experience_requirements
- Scoring rules from context.scoring_rules
- Industry mappings from context.experience_requirements.industries
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import re

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


# Default experience requirements
DEFAULT_EXPERIENCE_CONFIG = {
    "minimum_years": 3,
    "preferred_years": 5,
    "relevant_industries": [],
    "relevant_titles": [],
    "management_required": False
}


@register_factory("experience_evaluate")
async def experience_evaluate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluate candidate experience (context-driven).

    Context keys used:
        - experience_requirements: Years and type of experience required
        - scoring_rules: Experience scoring rules

    Input:
        resume_extract: Extracted resume data

    Output:
        experience_score: Experience match score (0-100)
        total_years: Total years of experience
        relevant_years: Relevant experience years
        meets_minimum: Whether meets minimum requirement
        experience_gaps: Identified gaps
    """
    context = context or input_data.get('context', {})
    exp_requirements = context.get('experience_requirements', DEFAULT_EXPERIENCE_CONFIG)
    scoring_rules = context.get('scoring_rules', {})

    logger.info(
        "Experience evaluate invoked",
        context_driven=bool(context)
    )

    # Get experience from resume
    resume = input_data.get('resume_extract', {})
    experience = resume.get('experience', [])
    total_years = resume.get('experience_years', 0)

    # Get requirements
    min_years = exp_requirements.get('minimum_years', 3)
    preferred_years = exp_requirements.get('preferred_years', 5)
    relevant_industries = exp_requirements.get('relevant_industries', [])
    relevant_titles = exp_requirements.get('relevant_titles', [])
    management_required = exp_requirements.get('management_required', False)

    # Calculate relevant experience
    relevant_years = 0
    has_management = False
    relevant_positions = []

    for position in experience:
        title = position.get('title', '').lower()
        company = position.get('company', '').lower()

        # Check for relevant title
        is_relevant = False
        for relevant_title in relevant_titles:
            if relevant_title.lower() in title:
                is_relevant = True
                break

        # Estimate position duration
        position_years = 2.5  # Default estimate

        if is_relevant:
            relevant_years += position_years
            relevant_positions.append(position)

        # Check for management experience
        management_keywords = ['manager', 'director', 'lead', 'head', 'vp', 'chief']
        if any(kw in title for kw in management_keywords):
            has_management = True

    # Calculate score
    score = 0

    # Years of experience scoring
    if total_years >= preferred_years:
        score += 40
    elif total_years >= min_years:
        score += 30 * (total_years / preferred_years)
    else:
        score += 20 * (total_years / min_years)

    # Relevant experience scoring
    if relevant_years >= min_years:
        score += 40
    else:
        score += 40 * (relevant_years / min_years)

    # Management experience
    if management_required:
        if has_management:
            score += 20
        else:
            score -= 10
    else:
        if has_management:
            score += 10  # Bonus

    # Normalize
    score = max(0, min(100, score))

    # Identify gaps
    experience_gaps = []
    if total_years < min_years:
        experience_gaps.append({
            'gap': 'insufficient_years',
            'required': min_years,
            'actual': total_years,
            'severity': 'high'
        })

    if management_required and not has_management:
        experience_gaps.append({
            'gap': 'no_management_experience',
            'required': 'Management experience',
            'actual': 'None found',
            'severity': 'high'
        })

    if relevant_years < min_years / 2:
        experience_gaps.append({
            'gap': 'limited_relevant_experience',
            'required': f'{min_years} years relevant',
            'actual': f'{relevant_years:.1f} years',
            'severity': 'medium'
        })

    return {
        "experience_score": round(score, 1),
        "total_years": round(total_years, 1),
        "relevant_years": round(relevant_years, 1),
        "position_count": len(experience),
        "relevant_position_count": len(relevant_positions),
        "has_management_experience": has_management,
        "meets_minimum_years": total_years >= min_years,
        "meets_preferred_years": total_years >= preferred_years,
        "experience_gaps": experience_gaps,
        "gap_count": len(experience_gaps),
        "required_years": min_years,
        "preferred_years": preferred_years,
        "evaluated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "experience_evaluate",
        "factory_version": "2.0.0",
        "context_keys_used": ["experience_requirements", "scoring_rules"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(experience_evaluate(event))
