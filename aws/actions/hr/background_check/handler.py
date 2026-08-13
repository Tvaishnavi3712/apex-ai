"""
Background Check - Small Factory
Initiates and tracks background check status.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

CHECK_PACKAGES = {
    "basic": {"name": "Basic", "checks": ["ssn_trace", "national_criminal"], "turnaround_days": 1, "cost": 29.99},
    "standard": {"name": "Standard", "checks": ["ssn_trace", "national_criminal", "county_criminal", "sex_offender"], "turnaround_days": 3, "cost": 49.99},
    "comprehensive": {"name": "Comprehensive", "checks": ["ssn_trace", "national_criminal", "county_criminal", "federal_criminal", "sex_offender", "employment_verification", "education_verification"], "turnaround_days": 5, "cost": 99.99},
}

@register_factory("background_check")
async def background_check(input_data: Dict[str, Any]) -> Dict[str, Any]:
    config = input_data.get('config', {})
    employee = input_data.get('employee_data', {}) or input_data.get('state', {}).get('input', {}).get('employee', {})
    
    package = config.get('package', 'standard')
    package_info = CHECK_PACKAGES.get(package, CHECK_PACKAGES['standard'])
    expedite = config.get('expedite', False)
    
    turnaround = package_info['turnaround_days'] // 2 if expedite else package_info['turnaround_days']
    estimated_completion = (datetime.now() + timedelta(days=max(1, turnaround))).strftime('%Y-%m-%d')
    check_id = f"BGC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "initiated": True,
        "check_id": check_id,
        "package": package,
        "package_name": package_info["name"],
        "checks_included": package_info["checks"],
        "cost": package_info["cost"],
        "expedited": expedite,
        "estimated_completion": estimated_completion,
        "status": "pending",
        "can_proceed_with_hire": True,
        "conditional_start_allowed": True,
    }
