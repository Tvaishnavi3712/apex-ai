"""
Benefits Enroll - Small Factory
Processes benefits enrollment for new employees.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

BENEFIT_PLANS = {
    "health": {
        "options": ["basic_hmo", "standard_ppo", "premium_ppo"],
        "default": "standard_ppo",
        "employer_contribution": 0.75,
    },
    "dental": {
        "options": ["basic", "premium"],
        "default": "basic",
        "employer_contribution": 0.50,
    },
    "vision": {
        "options": ["basic", "premium"],
        "default": "basic",
        "employer_contribution": 0.50,
    },
    "401k": {
        "options": ["contribute", "decline"],
        "default": "contribute",
        "employer_match": 0.04,
        "default_contribution": 0.06,
    },
    "life_insurance": {
        "options": ["1x_salary", "2x_salary", "3x_salary"],
        "default": "1x_salary",
        "employer_paid": True,
    },
}

@register_factory("benefits_enroll")
async def benefits_enroll(input_data: Dict[str, Any]) -> Dict[str, Any]:
    config = input_data.get('config', {})
    employee = input_data.get('employee_data', {}) or input_data.get('state', {}).get('input', {}).get('employee', {})
    elections = input_data.get('benefit_elections', {})
    
    start_date = employee.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Process enrollments
    enrollments = []
    for benefit_type, plan_info in BENEFIT_PLANS.items():
        election = elections.get(benefit_type, plan_info['default'])
        enrollments.append({
            "benefit_type": benefit_type,
            "plan_selected": election,
            "effective_date": start_date,
            "status": "enrolled" if election != "decline" else "declined",
        })
    
    # Calculate enrollment window
    enrollment_deadline = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=30)).strftime('%Y-%m-%d')
    
    return {
        "enrolled": True,
        "enrollments": enrollments,
        "enrollment_count": len([e for e in enrollments if e["status"] == "enrolled"]),
        "effective_date": start_date,
        "enrollment_deadline": enrollment_deadline,
        "changes_allowed_until": enrollment_deadline,
        "confirmation_number": f"BEN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    }
