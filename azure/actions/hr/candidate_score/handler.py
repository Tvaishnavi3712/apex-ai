"""
Candidate Score - HR Action (Context-Driven)
Calculate overall candidate score based on multiple factors

Context-Driven Architecture:
- Scoring weights from playbook context.scoring_weights
- Score thresholds from context.score_thresholds
- Routing rules from context.routing_config
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


# Default scoring configuration
DEFAULT_SCORING_CONFIG = {
    "weights": {
        "skills": 0.35,
        "experience": 0.30,
        "education": 0.20,
        "culture_fit": 0.15
    },
    "thresholds": {
        "auto_advance": 80,
        "review": 60,
        "reject": 40
    }
}


@register_factory("candidate_score")
async def candidate_score(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate overall candidate score (context-driven).

    Context keys used:
        - scoring_weights: Weight for each scoring component
        - score_thresholds: Thresholds for routing decisions

    Input:
        skills_match: Skills matching results
        experience_evaluate: Experience evaluation results
        education_verify: Education verification results
        resume_extract: Resume extraction data

    Output:
        overall_score: Weighted overall score (0-100)
        component_scores: Individual component scores
        recommendation: Routing recommendation
        strengths: Candidate strengths
        concerns: Areas of concern
    """
    context = context or input_data.get('context', {})
    scoring_config = context.get('scoring_config', DEFAULT_SCORING_CONFIG)
    weights = scoring_config.get('weights', DEFAULT_SCORING_CONFIG['weights'])
    thresholds = scoring_config.get('thresholds', DEFAULT_SCORING_CONFIG['thresholds'])

    logger.info(
        "Candidate score invoked",
        context_driven=bool(context)
    )

    # Get component scores from upstream factories
    skills = input_data.get('skills_match', {})
    experience = input_data.get('experience_evaluate', {})
    education = input_data.get('education_verify', {})
    resume = input_data.get('resume_extract', {})

    # Calculate component scores
    component_scores = {
        'skills': skills.get('skills_score', 50),
        'experience': experience.get('experience_score', 50),
        'education': education.get('education_score', 50),
        'culture_fit': 50  # Default, would come from assessment
    }

    # Calculate weighted overall score
    overall_score = 0
    for component, score in component_scores.items():
        weight = weights.get(component, 0.25)
        overall_score += score * weight

    overall_score = round(overall_score, 1)

    # Determine recommendation based on thresholds
    auto_advance = thresholds.get('auto_advance', 80)
    review_threshold = thresholds.get('review', 60)
    reject_threshold = thresholds.get('reject', 40)

    if overall_score >= auto_advance:
        recommendation = 'advance'
        recommendation_reason = 'Strong candidate - auto-advance to next stage'
    elif overall_score >= review_threshold:
        recommendation = 'review'
        recommendation_reason = 'Moderate fit - recommend recruiter review'
    elif overall_score >= reject_threshold:
        recommendation = 'maybe'
        recommendation_reason = 'Below threshold - consider with reservations'
    else:
        recommendation = 'reject'
        recommendation_reason = 'Does not meet minimum requirements'

    # Identify strengths and concerns
    strengths = []
    concerns = []

    for component, score in component_scores.items():
        if score >= 80:
            strengths.append({
                'area': component,
                'score': score,
                'detail': _get_strength_detail(component, input_data)
            })
        elif score < 60:
            concerns.append({
                'area': component,
                'score': score,
                'detail': _get_concern_detail(component, input_data)
            })

    # Calculate percentile (simulated)
    percentile = min(99, int(overall_score * 0.95))

    return {
        "candidate_name": resume.get('candidate_name'),
        "overall_score": overall_score,
        "percentile": percentile,
        "component_scores": component_scores,
        "weights_used": weights,
        "recommendation": recommendation,
        "recommendation_reason": recommendation_reason,
        "strengths": strengths,
        "concerns": concerns,
        "auto_advance_threshold": auto_advance,
        "meets_minimum": overall_score >= reject_threshold,
        "scored_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "candidate_score",
        "factory_version": "2.0.0",
        "context_keys_used": ["scoring_weights", "score_thresholds"]
    }


def _get_strength_detail(component: str, input_data: Dict) -> str:
    """Get detail about a strength area."""
    if component == 'skills':
        skills = input_data.get('skills_match', {})
        matched = skills.get('matched_required_count', 0)
        return f"Matches {matched} required skills"
    elif component == 'experience':
        exp = input_data.get('experience_evaluate', {})
        years = exp.get('total_years', 0)
        return f"{years} years of relevant experience"
    elif component == 'education':
        edu = input_data.get('education_verify', {})
        degree = edu.get('highest_degree', 'degree')
        return f"Has {degree}"
    return "Strong performance in this area"


def _get_concern_detail(component: str, input_data: Dict) -> str:
    """Get detail about a concern area."""
    if component == 'skills':
        skills = input_data.get('skills_match', {})
        missing = skills.get('missing_required_count', 0)
        return f"Missing {missing} required skills"
    elif component == 'experience':
        exp = input_data.get('experience_evaluate', {})
        years = exp.get('total_years', 0)
        required = exp.get('required_years', 5)
        return f"Has {years} years, requires {required}"
    elif component == 'education':
        return "Education does not meet requirements"
    return "Below expected performance in this area"


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(candidate_score(event))
