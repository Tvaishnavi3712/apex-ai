"""
Apex Talent Bot - Foundry Agent Service Agent for HR recruitment and onboarding
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))), 'actions'))
from sdk.azure_data import get_table_resource

import json
import boto3

cosmos_db = get_table_resource()

SYSTEM_PROMPT = """You are TalentBot, an AI assistant for HR recruitment and employee onboarding.

Your capabilities:
1. Screen resumes and applications
2. Match candidates to job requirements
3. Process onboarding documents (I-9, W-4, offer letters)
4. Verify employment eligibility
5. Track onboarding progress

When screening candidates:
- Extract skills, experience, and qualifications
- Match against job requirements
- Score and rank candidates
- Flag potential concerns

When processing onboarding:
- Verify document completeness
- Extract form data accurately
- Ensure compliance with regulations

Be fair and unbiased in candidate evaluation."""


@tool
def extract_resume(s3_uri: str) -> dict:
    """
    Extract data from a resume document using BDA.

    Args:
        s3_uri: blob URI of the resume document

    Returns:
        Extracted candidate data including skills, experience, education
    """
    return {
        "status": "processing",
        "message": "Resume extraction started"
    }


@tool
def match_candidate_to_job(candidate_profile: dict, job_requirements: dict) -> dict:
    """
    Match a candidate profile against job requirements.

    Args:
        candidate_profile: Candidate's skills, experience, education
        job_requirements: Required skills, experience, qualifications

    Returns:
        Match score and detailed analysis
    """
    candidate_skills = set(candidate_profile.get("skills", []))
    required_skills = set(job_requirements.get("required_skills", []))
    preferred_skills = set(job_requirements.get("preferred_skills", []))

    required_match = len(candidate_skills & required_skills) / max(len(required_skills), 1)
    preferred_match = len(candidate_skills & preferred_skills) / max(len(preferred_skills), 1)
    overall_score = (required_match * 0.7) + (preferred_match * 0.3)

    return {
        "overall_score": round(overall_score * 100, 1),
        "required_skills_match": round(required_match * 100, 1),
        "preferred_skills_match": round(preferred_match * 100, 1),
        "recommendation": "proceed" if overall_score >= 0.7 else "review" if overall_score >= 0.5 else "reject"
    }


@tool
def extract_onboarding_document(s3_uri: str, document_type: str) -> dict:
    """
    Extract data from onboarding documents (I-9, W-4, etc).

    Args:
        s3_uri: blob URI of the onboarding document
        document_type: Type of document (i9, w4, offer_letter)

    Returns:
        Extracted document data
    """
    return {
        "status": "processing",
        "document_type": document_type,
        "message": f"{document_type.upper()} extraction started"
    }


@tool
def verify_employment_eligibility(i9_data: dict) -> dict:
    """
    Verify employment eligibility based on I-9 data.

    Args:
        i9_data: Extracted I-9 form data

    Returns:
        Eligibility verification results
    """
    required_fields = ["first_name", "last_name", "date_of_birth", "ssn", "citizenship_status"]
    missing_fields = [f for f in required_fields if f not in i9_data or not i9_data[f]]

    if missing_fields:
        return {
            "verified": False,
            "status": "incomplete",
            "missing_fields": missing_fields
        }

    return {
        "verified": True,
        "status": "employment_authorized",
        "e_verify_case_number": f"EV{hash(i9_data.get('ssn', ''))%1000000:06d}"
    }


@tool
def create_employee_record(employee_data: dict) -> dict:
    """
    Create a new employee record in the system.

    Args:
        employee_data: Employee information from onboarding

    Returns:
        Created employee record with assigned employee ID
    """
    import uuid
    employee_id = f"EMP{uuid.uuid4().hex[:8].upper()}"
    return {
        "success": True,
        "employee_id": employee_id,
        "status": "onboarding_in_progress",
        "message": "Employee record created successfully"
    }


# Create the agent
model = AzureOpenAIModel(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        extract_resume,
        match_candidate_to_job,
        extract_onboarding_document,
        verify_employment_eligibility,
        create_employee_record
    ]
)

# Create the Foundry Agent Service app
app = FoundryAgentApp(agent=agent)
