"""
Skills Match - HR Action (Context-Driven)
Match candidate skills against job requirements

Context-Driven Architecture:
- Job requirements from playbook context.job_requirements
- Skills taxonomy from context.skills_config.taxonomy
- Scoring weights from context.scoring_weights
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


# Default scoring weights
DEFAULT_SCORING_WEIGHTS = {
    "required_skill": 15,
    "preferred_skill": 8,
    "bonus_skill": 3,
    "missing_required_penalty": -20
}


@register_factory("skills_match")
async def skills_match(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Match candidate skills against job requirements (context-driven).

    Context keys used:
        - job_requirements: Required and preferred skills
        - skills_config: Skills taxonomy and synonyms
        - scoring_weights: Score weights per skill type

    Input:
        resume_extract: Extracted resume data
        job_id: Job position ID

    Output:
        skills_score: Skills match score (0-100)
        matched_required: Required skills matched
        matched_preferred: Preferred skills matched
        missing_required: Missing required skills
        skill_gaps: Skills gaps with training recommendations
    """
    context = context or input_data.get('context', {})
    job_requirements = context.get('job_requirements', {})
    skills_config = context.get('skills_config', {})
    scoring_weights = context.get('scoring_weights', DEFAULT_SCORING_WEIGHTS)

    logger.info(
        "Skills match invoked",
        context_driven=bool(context)
    )

    # Get candidate skills from resume extraction
    resume = input_data.get('resume_extract', {})
    candidate_skills = set(s.lower() for s in resume.get('skills', []))

    # Get job requirements
    required_skills = set(s.lower() for s in job_requirements.get('required_skills', []))
    preferred_skills = set(s.lower() for s in job_requirements.get('preferred_skills', []))
    bonus_skills = set(s.lower() for s in job_requirements.get('bonus_skills', []))

    # Get skill synonyms for better matching
    synonyms = skills_config.get('synonyms', {})

    # Expand candidate skills with synonyms
    expanded_skills = set(candidate_skills)
    for skill in candidate_skills:
        if skill in synonyms:
            expanded_skills.update(s.lower() for s in synonyms[skill])

    # Calculate matches
    matched_required = required_skills & expanded_skills
    matched_preferred = preferred_skills & expanded_skills
    matched_bonus = bonus_skills & expanded_skills
    missing_required = required_skills - expanded_skills

    # Calculate score
    score = 0
    max_score = 0

    # Required skills
    required_weight = scoring_weights.get('required_skill', 15)
    score += len(matched_required) * required_weight
    max_score += len(required_skills) * required_weight

    # Missing required penalty
    penalty = scoring_weights.get('missing_required_penalty', -20)
    score += len(missing_required) * penalty

    # Preferred skills
    preferred_weight = scoring_weights.get('preferred_skill', 8)
    score += len(matched_preferred) * preferred_weight
    max_score += len(preferred_skills) * preferred_weight

    # Bonus skills
    bonus_weight = scoring_weights.get('bonus_skill', 3)
    score += len(matched_bonus) * bonus_weight
    max_score += len(bonus_skills) * bonus_weight

    # Normalize to 0-100
    if max_score > 0:
        normalized_score = max(0, min(100, (score / max_score) * 100))
    else:
        normalized_score = 50  # Default if no requirements specified

    # Generate skill gaps with recommendations
    skill_gaps = []
    for skill in missing_required:
        skill_gaps.append({
            'skill': skill,
            'importance': 'required',
            'training_recommendation': _get_training_recommendation(skill, skills_config)
        })

    # Determine match quality
    if len(missing_required) == 0:
        match_quality = 'excellent' if normalized_score >= 80 else 'good'
    elif len(missing_required) <= 2:
        match_quality = 'moderate'
    else:
        match_quality = 'poor'

    return {
        "skills_score": round(normalized_score, 1),
        "match_quality": match_quality,
        "candidate_skills": list(candidate_skills),
        "candidate_skill_count": len(candidate_skills),
        "matched_required": list(matched_required),
        "matched_required_count": len(matched_required),
        "matched_preferred": list(matched_preferred),
        "matched_preferred_count": len(matched_preferred),
        "matched_bonus": list(matched_bonus),
        "missing_required": list(missing_required),
        "missing_required_count": len(missing_required),
        "required_coverage": round(len(matched_required) / len(required_skills) * 100, 1) if required_skills else 100,
        "skill_gaps": skill_gaps,
        "trainable": len(missing_required) <= 2,
        "analyzed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "skills_match",
        "factory_version": "2.0.0",
        "context_keys_used": ["job_requirements", "skills_config", "scoring_weights"]
    }


def _get_training_recommendation(skill: str, skills_config: Dict) -> str:
    """Get training recommendation for a missing skill."""
    training_map = skills_config.get('training_recommendations', {})

    if skill in training_map:
        return training_map[skill]

    # Default recommendations based on skill type
    if any(term in skill for term in ['python', 'java', 'javascript', 'code']):
        return f"Online course: Introduction to {skill.title()}"
    elif any(term in skill for term in ['aws', 'azure', 'cloud']):
        return f"Certification: {skill.upper()} Fundamentals"
    elif any(term in skill for term in ['leadership', 'management']):
        return "Leadership development program"
    else:
        return f"Training: {skill.title()} fundamentals"


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(skills_match(event))
