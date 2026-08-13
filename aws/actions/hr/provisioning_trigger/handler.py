"""
Provisioning Trigger - Small Factory
Triggers IT provisioning for new employees.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

ROLE_PROVISIONING = {
    "standard": {
        "systems": ["email", "slack", "hr_portal", "time_tracking"],
        "equipment": ["laptop", "monitor"],
        "access_level": "employee",
    },
    "developer": {
        "systems": ["email", "slack", "hr_portal", "time_tracking", "github", "jira", "aws_console"],
        "equipment": ["laptop", "monitor", "keyboard", "mouse"],
        "access_level": "developer",
    },
    "manager": {
        "systems": ["email", "slack", "hr_portal", "time_tracking", "expense_system", "approval_system"],
        "equipment": ["laptop", "monitor", "desk_phone"],
        "access_level": "manager",
    },
    "executive": {
        "systems": ["email", "slack", "hr_portal", "time_tracking", "expense_system", "approval_system", "executive_dashboard", "board_portal"],
        "equipment": ["laptop", "monitor", "desk_phone", "mobile_phone"],
        "access_level": "executive",
    },
}

@register_factory("provisioning_trigger")
async def provisioning_trigger(input_data: Dict[str, Any]) -> Dict[str, Any]:
    config = input_data.get('config', {})
    employee = input_data.get('employee_data', {}) or input_data.get('state', {}).get('input', {}).get('employee', {})
    background = input_data.get('background_check', {})
    
    # Determine provisioning profile
    job_title = employee.get('job_title', employee.get('title', '')).lower()
    department = employee.get('department', '').lower()
    
    if any(word in job_title for word in ['executive', 'director', 'vp', 'president', 'chief']):
        profile = "executive"
    elif any(word in job_title for word in ['manager', 'supervisor', 'lead']):
        profile = "manager"
    elif any(word in department for word in ['engineering', 'development', 'tech', 'it']):
        profile = "developer"
    else:
        profile = "standard"
    
    provisioning = ROLE_PROVISIONING[profile]
    start_date = employee.get('start_date', datetime.now().strftime('%Y-%m-%d'))
    
    # Create provisioning requests
    system_requests = []
    for system in provisioning["systems"]:
        system_requests.append({
            "system": system,
            "access_level": provisioning["access_level"],
            "status": "requested",
            "target_date": start_date,
        })
    
    equipment_requests = []
    for item in provisioning["equipment"]:
        equipment_requests.append({
            "item": item,
            "status": "ordered",
            "delivery_date": (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d'),
        })
    
    # Check if conditional (pending background check)
    conditional = not background.get('status') == 'clear'
    
    return {
        "triggered": True,
        "provisioning_id": f"PROV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "profile": profile,
        "system_requests": system_requests,
        "system_count": len(system_requests),
        "equipment_requests": equipment_requests,
        "equipment_count": len(equipment_requests),
        "conditional": conditional,
        "conditional_reason": "Pending background check" if conditional else None,
        "target_ready_date": start_date,
        "it_ticket_created": True,
    }
