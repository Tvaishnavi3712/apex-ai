"""
Resume Extract - HR Action (Context-Driven)
Extract structured data from resume documents

Context-Driven Architecture:
- Extraction fields from playbook context.extraction_config
- Skills taxonomy from context.skills_config.taxonomy
- Experience parsing from context.extraction_config.experience
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

try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default extraction configuration
DEFAULT_EXTRACTION_CONFIG = {
    "required_fields": ["name", "email", "phone"],
    "extract_sections": ["contact", "summary", "experience", "education", "skills"],
    "confidence_threshold": 0.75
}


@register_factory("resume_extract")
async def resume_extract(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract resume data from document (context-driven).

    Context keys used:
        - extraction_config: Field extraction configuration
        - skills_config: Skills taxonomy for normalization

    Input:
        document_intake: Document intake results
        text_content: Extracted text
        job_id: Job position ID (for targeted extraction)

    Output:
        candidate_name: Candidate full name
        email: Email address
        phone: Phone number
        skills: Extracted skills
        experience: Work experience
        education: Education history
        extraction_confidence: Overall confidence
    """
    context = context or input_data.get('context', {})
    extraction_config = context.get('extraction_config', DEFAULT_EXTRACTION_CONFIG)
    skills_config = context.get('skills_config', {})

    logger.info(
        "Resume extract invoked",
        context_driven=bool(context)
    )

    # Get document content
    doc_intake = input_data.get('document_intake', {})
    text_content = doc_intake.get('text_content') or input_data.get('text_content', '')

    if not text_content:
        return {
            "error": "No text content to extract from",
            "extraction_complete": False,
            "context_driven": bool(context),
            "factory_id": "resume_extract",
            "factory_version": "2.0.0"
        }

    # Extract contact information
    contact = _extract_contact(text_content)

    # Extract skills
    skills_taxonomy = skills_config.get('taxonomy', {})
    skills = _extract_skills(text_content, skills_taxonomy)

    # Extract experience
    experience = _extract_experience(text_content)

    # Extract education
    education = _extract_education(text_content)

    # Extract summary
    summary = _extract_summary(text_content)

    # Calculate confidence
    confidence_scores = {
        'name': 0.9 if contact.get('name') else 0.0,
        'email': 0.95 if contact.get('email') else 0.0,
        'phone': 0.9 if contact.get('phone') else 0.0,
        'skills': min(0.8, len(skills) * 0.1) if skills else 0.0,
        'experience': 0.85 if experience else 0.0,
        'education': 0.85 if education else 0.0
    }
    avg_confidence = sum(confidence_scores.values()) / len(confidence_scores)

    # Check required fields
    required = extraction_config.get('required_fields', ['name', 'email'])
    missing_required = []
    if 'name' in required and not contact.get('name'):
        missing_required.append('name')
    if 'email' in required and not contact.get('email'):
        missing_required.append('email')
    if 'phone' in required and not contact.get('phone'):
        missing_required.append('phone')

    return {
        "candidate_name": contact.get('name'),
        "email": contact.get('email'),
        "phone": contact.get('phone'),
        "location": contact.get('location'),
        "linkedin": contact.get('linkedin'),
        "summary": summary,
        "skills": skills,
        "skill_count": len(skills),
        "experience": experience,
        "experience_years": _calculate_experience_years(experience),
        "education": education,
        "highest_degree": _get_highest_degree(education),
        "confidence_scores": confidence_scores,
        "extraction_confidence": round(avg_confidence, 3),
        "missing_required_fields": missing_required,
        "extraction_complete": len(missing_required) == 0,
        "requires_review": avg_confidence < extraction_config.get('confidence_threshold', 0.75),
        "extracted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "resume_extract",
        "factory_version": "2.0.0",
        "context_keys_used": ["extraction_config", "skills_config"]
    }


def _extract_contact(text: str) -> Dict[str, Any]:
    """Extract contact information from resume."""
    contact = {}

    # Email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    if email_match:
        contact['email'] = email_match.group().lower()

    # Phone
    phone_match = re.search(r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        contact['phone'] = phone_match.group()

    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.I)
    if linkedin_match:
        contact['linkedin'] = linkedin_match.group()

    # Name (usually at the beginning)
    lines = text.strip().split('\n')
    if lines:
        # First non-empty line that looks like a name
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) < 50 and not '@' in line and not 'http' in line.lower():
                # Check if it looks like a name (2-4 words, capitalized)
                words = line.split()
                if 2 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
                    contact['name'] = line
                    break

    return contact


def _extract_skills(text: str, taxonomy: Dict) -> List[str]:
    """Extract skills from resume."""
    skills = set()
    text_lower = text.lower()

    # Common technical skills
    tech_skills = [
        'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
        'node.js', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'sql', 'mongodb',
        'postgresql', 'mysql', 'redis', 'elasticsearch', 'machine learning', 'ai',
        'deep learning', 'tensorflow', 'pytorch', 'data science', 'analytics',
        'agile', 'scrum', 'ci/cd', 'devops', 'git', 'linux', 'rest api', 'graphql'
    ]

    for skill in tech_skills:
        if skill in text_lower:
            skills.add(skill.title() if len(skill) > 3 else skill.upper())

    # Add skills from taxonomy
    for category, category_skills in taxonomy.items():
        for skill in category_skills:
            if skill.lower() in text_lower:
                skills.add(skill)

    return sorted(list(skills))


def _extract_experience(text: str) -> List[Dict[str, Any]]:
    """Extract work experience from resume."""
    experience = []

    # Simple pattern matching for experience sections
    exp_pattern = r'(?:^|\n)([A-Z][^,\n]{5,50})\s*[-–|]\s*([A-Z][^,\n]{5,50})\s*\n\s*(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|Present|Current)'
    matches = re.findall(exp_pattern, text, re.MULTILINE | re.IGNORECASE)

    for match in matches[:5]:  # Limit to 5 positions
        experience.append({
            'title': match[0].strip(),
            'company': match[1].strip(),
            'start_date': match[2].strip(),
            'end_date': match[3].strip(),
            'current': 'present' in match[3].lower() or 'current' in match[3].lower()
        })

    return experience


def _extract_education(text: str) -> List[Dict[str, Any]]:
    """Extract education from resume."""
    education = []

    # Degree patterns
    degree_patterns = [
        (r'(?:Ph\.?D\.?|Doctor(?:ate)?)', 'PhD'),
        (r'(?:M\.?S\.?|Master(?:\'s)?|MBA)', 'Masters'),
        (r'(?:B\.?S\.?|B\.?A\.?|Bachelor(?:\'s)?)', 'Bachelors'),
        (r'(?:Associate(?:\'s)?)', 'Associates')
    ]

    for pattern, degree_type in degree_patterns:
        if re.search(pattern, text, re.I):
            education.append({
                'degree': degree_type,
                'field': _extract_field_of_study(text, degree_type)
            })

    return education


def _extract_field_of_study(text: str, degree: str) -> str:
    """Extract field of study near degree mention."""
    fields = [
        'Computer Science', 'Engineering', 'Business', 'Finance', 'Marketing',
        'Data Science', 'Information Technology', 'Mathematics', 'Physics',
        'Economics', 'Psychology', 'Communications', 'Management'
    ]

    for field in fields:
        if field.lower() in text.lower():
            return field

    return 'Not specified'


def _extract_summary(text: str) -> str:
    """Extract professional summary."""
    # Look for summary section
    summary_match = re.search(
        r'(?:Summary|Profile|Objective|About)\s*:?\s*\n(.{50,500})',
        text,
        re.I
    )
    if summary_match:
        return summary_match.group(1).strip()[:500]
    return None


def _calculate_experience_years(experience: List[Dict]) -> float:
    """Calculate total years of experience."""
    # Simplified calculation
    return len(experience) * 2.5  # Assume average 2.5 years per position


def _get_highest_degree(education: List[Dict]) -> str:
    """Get highest degree level."""
    degree_order = ['PhD', 'Masters', 'Bachelors', 'Associates']
    for degree in degree_order:
        if any(e.get('degree') == degree for e in education):
            return degree
    return None


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(resume_extract(event))
