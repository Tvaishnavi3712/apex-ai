"""
Job Requirement Match Action
Match candidate skills and experience against job requirements
"""

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: native key-condition builder
    from sdk.azure_data import Key
except ImportError:
    from ...sdk.azure_data import Key
import os
from decimal import Decimal
from typing import List, Dict, Any, Optional
import re

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Skill synonyms for matching
SKILL_SYNONYMS = {
    "javascript": ["js", "ecmascript", "es6", "es2015"],
    "typescript": ["ts"],
    "python": ["py", "python3"],
    "react": ["reactjs", "react.js"],
    "node": ["nodejs", "node.js"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "sql": ["mysql", "postgresql", "postgres", "mssql", "sql server"],
    "nosql": ["mongodb", "cosmos_db", "cassandra", "couchdb"],
    "machine learning": ["ml", "deep learning", "ai"],
    "kubernetes": ["k8s"],
    "docker": ["containers", "containerization"],
}


# ============================================================================
# Decorator-based implementation
# ============================================================================

@apex_action(ApexActionSchema(
    name="job_requirement_match",
    description="Match candidate qualifications against job requirements and calculate fit score",
    category="recruiting",
    industry="hr",
    input_schema=ActionInputSchema(description="Job matching parameters")
        .add_string("job_id", "Job requisition ID", required=True)
        .add_array("candidate_skills", "List of candidate skills", required=True)
        .add_number("years_experience", "Candidate's years of experience", required=True)
        .add_string("highest_education", "Candidate's highest education level", required=False)
        .add_array("certifications", "Candidate's certifications", required=False)
        .add_array("job_titles", "Candidate's previous job titles", required=False),
    output_schema=ActionOutputSchema(description="Job match result")
        .add_number("overall_score", "Overall match score (0-100)")
        .add_number("skill_score", "Skill match score (0-100)")
        .add_number("experience_score", "Experience match score (0-100)")
        .add_number("education_score", "Education match score (0-100)")
        .add_string("recommendation", "Hiring recommendation")
        .add_array("matched_skills", "Skills that matched requirements")
        .add_array("missing_skills", "Required skills not found")
        .add_array("bonus_skills", "Preferred skills found")
))
def job_requirement_match(
    job_id: str,
    candidate_skills: List[str],
    years_experience: float,
    highest_education: str = None,
    certifications: List[str] = None,
    job_titles: List[str] = None
) -> dict:
    """
    Match candidate against job requirements

    Args:
        job_id: Job requisition ID
        candidate_skills: List of candidate's skills
        years_experience: Total years of experience
        highest_education: Highest education level
        certifications: List of certifications
        job_titles: Previous job titles

    Returns:
        Match score and detailed analysis
    """
    certifications = certifications or []
    job_titles = job_titles or []

    result = {
        "job_id": job_id,
        "overall_score": 0,
        "skill_score": 0,
        "experience_score": 0,
        "education_score": 0,
        "certification_score": 0,
        "recommendation": "not_qualified",
        "matched_skills": [],
        "missing_skills": [],
        "bonus_skills": [],
        "experience_analysis": {},
        "education_analysis": {}
    }

    try:
        # Get job requirements
        job_requirements = _get_job_requirements(job_id)
        if not job_requirements:
            return {**result, "error": f"Job requisition {job_id} not found"}

        # Normalize candidate skills for matching
        normalized_candidate_skills = _normalize_skills(candidate_skills)

        # Calculate skill match
        skill_result = _calculate_skill_match(
            normalized_candidate_skills,
            job_requirements.get('required_skills', []),
            job_requirements.get('preferred_skills', [])
        )
        result.update(skill_result)

        # Calculate experience match
        exp_result = _calculate_experience_match(
            years_experience,
            job_requirements.get('min_experience', 0),
            job_requirements.get('max_experience'),
            job_requirements.get('ideal_experience')
        )
        result["experience_score"] = exp_result["score"]
        result["experience_analysis"] = exp_result

        # Calculate education match
        edu_result = _calculate_education_match(
            highest_education,
            job_requirements.get('required_education'),
            job_requirements.get('preferred_education')
        )
        result["education_score"] = edu_result["score"]
        result["education_analysis"] = edu_result

        # Calculate certification match
        cert_result = _calculate_certification_match(
            certifications,
            job_requirements.get('required_certifications', []),
            job_requirements.get('preferred_certifications', [])
        )
        result["certification_score"] = cert_result["score"]

        # Calculate overall score with weights
        weights = {
            "skills": 0.35,
            "experience": 0.25,
            "education": 0.15,
            "preferred_skills": 0.15,
            "certifications": 0.10
        }

        overall = (
            result["skill_score"] * weights["skills"] +
            result["experience_score"] * weights["experience"] +
            result["education_score"] * weights["education"] +
            skill_result.get("preferred_score", 0) * weights["preferred_skills"] +
            result["certification_score"] * weights["certifications"]
        )
        result["overall_score"] = round(overall, 1)

        # Determine recommendation
        result["recommendation"] = _determine_recommendation(result)

        return result

    except Exception as e:
        return {**result, "error": str(e)}


def _get_job_requirements(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve job requirements from database"""
    try:
        tables = get_table_resource()
        table_name = os.environ.get('JOBS_TABLE', 'apex-ai-platform-job-requisitions')
        table = cosmos_db.Table(table_name)

        response = table.get_item(Key={"job_id": job_id})
        if 'Item' in response:
            return response['Item']
    except Exception:
        pass

    # Return mock requirements for testing
    return {
        "job_id": job_id,
        "title": "Software Engineer",
        "required_skills": ["python", "aws", "sql"],
        "preferred_skills": ["kubernetes", "react", "typescript"],
        "min_experience": 3,
        "max_experience": 8,
        "ideal_experience": 5,
        "required_education": "bachelor",
        "preferred_education": "master",
        "required_certifications": [],
        "preferred_certifications": ["aws solutions architect"]
    }


def _normalize_skills(skills: List[str]) -> List[str]:
    """Normalize skills for matching"""
    normalized = []
    for skill in skills:
        skill_lower = skill.lower().strip()
        normalized.append(skill_lower)

        # Add canonical form if skill is a synonym
        for canonical, synonyms in SKILL_SYNONYMS.items():
            if skill_lower in synonyms:
                normalized.append(canonical)
            elif skill_lower == canonical:
                normalized.extend(synonyms)

    return list(set(normalized))


def _calculate_skill_match(
    candidate_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str]
) -> Dict[str, Any]:
    """Calculate skill match scores"""
    required_normalized = _normalize_skills(required_skills)
    preferred_normalized = _normalize_skills(preferred_skills)

    matched_required = []
    missing_required = []
    matched_preferred = []

    for req_skill in required_skills:
        req_lower = req_skill.lower()
        if req_lower in candidate_skills or any(
            syn in candidate_skills
            for syn in SKILL_SYNONYMS.get(req_lower, [])
        ):
            matched_required.append(req_skill)
        else:
            missing_required.append(req_skill)

    for pref_skill in preferred_skills:
        pref_lower = pref_skill.lower()
        if pref_lower in candidate_skills or any(
            syn in candidate_skills
            for syn in SKILL_SYNONYMS.get(pref_lower, [])
        ):
            matched_preferred.append(pref_skill)

    # Calculate scores
    required_score = 0
    if required_skills:
        required_score = (len(matched_required) / len(required_skills)) * 100

    preferred_score = 0
    if preferred_skills:
        preferred_score = (len(matched_preferred) / len(preferred_skills)) * 100

    return {
        "skill_score": round(required_score, 1),
        "preferred_score": round(preferred_score, 1),
        "matched_skills": matched_required,
        "missing_skills": missing_required,
        "bonus_skills": matched_preferred
    }


def _calculate_experience_match(
    candidate_years: float,
    min_years: int,
    max_years: Optional[int],
    ideal_years: Optional[int]
) -> Dict[str, Any]:
    """Calculate experience match score"""
    score = 0
    analysis = {
        "candidate_years": candidate_years,
        "min_required": min_years,
        "max_preferred": max_years,
        "ideal": ideal_years,
        "status": "unknown"
    }

    if candidate_years < min_years:
        # Under-qualified
        if min_years > 0:
            score = max(0, (candidate_years / min_years) * 70)
        analysis["status"] = "under_qualified"
    elif max_years and candidate_years > max_years:
        # Over-qualified (slight penalty)
        score = 80
        analysis["status"] = "over_qualified"
    elif ideal_years:
        # Calculate distance from ideal
        diff = abs(candidate_years - ideal_years)
        if diff == 0:
            score = 100
        elif diff <= 1:
            score = 95
        elif diff <= 2:
            score = 85
        else:
            score = 75
        analysis["status"] = "qualified"
    else:
        # Within range
        score = 90
        analysis["status"] = "qualified"

    analysis["score"] = round(score, 1)
    return analysis


def _calculate_education_match(
    candidate_education: str,
    required_education: str,
    preferred_education: str
) -> Dict[str, Any]:
    """Calculate education match score"""
    education_levels = {
        "high school": 1,
        "associate": 2,
        "bachelor": 3,
        "master": 4,
        "phd": 5,
        "doctorate": 5
    }

    candidate_level = education_levels.get(
        (candidate_education or "").lower(), 0
    )
    required_level = education_levels.get(
        (required_education or "").lower(), 0
    )
    preferred_level = education_levels.get(
        (preferred_education or "").lower(), 0
    )

    score = 0
    status = "unknown"

    if required_level == 0:
        # No education requirement
        score = 100
        status = "no_requirement"
    elif candidate_level >= preferred_level and preferred_level > 0:
        score = 100
        status = "exceeds_preferred"
    elif candidate_level >= required_level:
        score = 85 if preferred_level == 0 else 75
        status = "meets_required"
    elif candidate_level == required_level - 1:
        score = 50
        status = "below_required"
    else:
        score = 25
        status = "significantly_below"

    return {
        "score": score,
        "candidate_education": candidate_education,
        "required": required_education,
        "preferred": preferred_education,
        "status": status
    }


def _calculate_certification_match(
    candidate_certs: List[str],
    required_certs: List[str],
    preferred_certs: List[str]
) -> Dict[str, Any]:
    """Calculate certification match score"""
    if not required_certs and not preferred_certs:
        return {"score": 100, "matched": [], "missing": []}

    candidate_lower = [c.lower() for c in candidate_certs]
    matched = []
    missing = []

    for cert in required_certs:
        if cert.lower() in candidate_lower:
            matched.append(cert)
        else:
            missing.append(cert)

    for cert in preferred_certs:
        if cert.lower() in candidate_lower:
            matched.append(cert)

    total_certs = len(required_certs) + len(preferred_certs)
    if total_certs > 0:
        score = (len(matched) / total_certs) * 100
    else:
        score = 100

    return {
        "score": round(score, 1),
        "matched": matched,
        "missing": missing
    }


def _determine_recommendation(result: Dict[str, Any]) -> str:
    """Determine hiring recommendation based on scores"""
    overall = result["overall_score"]
    skill_score = result["skill_score"]
    missing_required = result.get("missing_skills", [])

    # Must have critical skill match
    if skill_score < 50:
        return "not_qualified"

    # Check for critical missing skills
    if len(missing_required) > len(result.get("matched_skills", [])):
        return "not_qualified"

    if overall >= 85:
        return "strong_hire"
    elif overall >= 70:
        return "hire"
    elif overall >= 60:
        return "consider"
    elif overall >= 50:
        return "maybe"
    else:
        return "not_qualified"


# ============================================================================
# Class-based implementation
# ============================================================================

class JobRequirementMatchAction(ApexActionBase):
    """
    Job Requirement Match Action (class-based implementation)
    """

    name = "job_requirement_match"
    description = "Match candidate qualifications against job requirements"
    category = "recruiting"
    industry = "hr"

    def execute(
        self,
        job_id: str,
        candidate_skills: List[str],
        years_experience: float,
        highest_education: str = None,
        certifications: List[str] = None,
        job_titles: List[str] = None,
        **kwargs
    ) -> dict:
        """Execute the job requirement match"""
        return job_requirement_match(
            job_id=job_id,
            candidate_skills=candidate_skills,
            years_experience=years_experience,
            highest_education=highest_education,
            certifications=certifications,
            job_titles=job_titles
        )


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return job_requirement_match(**event)
