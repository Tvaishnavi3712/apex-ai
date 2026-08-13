"""
HR/Recruitment Industry Actions
Actions for resume screening, onboarding, and compensation management
"""

from .job_requirement_match.handler import job_requirement_match, JobRequirementMatchAction
from .compensation_validation.handler import compensation_validation, CompensationValidationAction
from .background_check.handler import background_check, BackgroundCheckAction

__all__ = [
    'job_requirement_match',
    'JobRequirementMatchAction',
    'compensation_validation',
    'CompensationValidationAction',
    'background_check',
    'BackgroundCheckAction',
]
