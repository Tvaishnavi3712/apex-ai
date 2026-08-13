"""
I-9 Validate - Small Factory
Validates I-9 Employment Eligibility Verification form.
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

# I-9 Section requirements
I9_SECTIONS = {
    "section_1": {
        "name": "Employee Information and Attestation",
        "required_fields": ["last_name", "first_name", "address", "date_of_birth", "ssn", "citizenship_status"],
        "completed_by": "employee",
        "deadline_days": 1,  # Must be completed by first day of work
    },
    "section_2": {
        "name": "Employer Review and Verification",
        "required_fields": ["document_title", "issuing_authority", "document_number", "expiration_date", "employer_signature"],
        "completed_by": "employer",
        "deadline_days": 3,  # Must be completed within 3 business days
    },
}

# Citizenship status options
CITIZENSHIP_STATUS = {
    "citizen": "A citizen of the United States",
    "noncitizen_national": "A noncitizen national of the United States",
    "permanent_resident": "A lawful permanent resident",
    "alien_authorized": "An alien authorized to work",
}


def validate_ssn(ssn: str) -> Dict[str, Any]:
    """Validate Social Security Number format."""
    # Remove dashes and spaces
    ssn_clean = re.sub(r'[\s-]', '', ssn)

    if not re.match(r'^\d{9}$', ssn_clean):
        return {"valid": False, "error": "SSN must be 9 digits"}

    # Check for invalid SSN patterns
    if ssn_clean.startswith('000') or ssn_clean.startswith('666'):
        return {"valid": False, "error": "Invalid SSN prefix"}

    if ssn_clean[3:5] == '00' or ssn_clean[5:] == '0000':
        return {"valid": False, "error": "Invalid SSN format"}

    return {"valid": True, "masked": f"XXX-XX-{ssn_clean[-4:]}"}


def validate_section1(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate I-9 Section 1 (Employee)."""
    required = I9_SECTIONS["section_1"]["required_fields"]
    issues = []
    fields_valid = {}

    for field in required:
        value = data.get(field, '')

        if not value:
            issues.append(f"Missing required field: {field}")
            fields_valid[field] = False
            continue

        # Field-specific validation
        if field == "ssn":
            ssn_result = validate_ssn(value)
            if not ssn_result["valid"]:
                issues.append(f"SSN: {ssn_result['error']}")
                fields_valid[field] = False
            else:
                fields_valid[field] = True
        elif field == "date_of_birth":
            # Validate DOB format and age
            try:
                dob = datetime.strptime(value, '%Y-%m-%d')
                age = (datetime.now() - dob).days // 365
                if age < 14 or age > 100:
                    issues.append("Date of birth indicates invalid working age")
                    fields_valid[field] = False
                else:
                    fields_valid[field] = True
            except ValueError:
                issues.append("Invalid date of birth format")
                fields_valid[field] = False
        elif field == "citizenship_status":
            if value.lower() not in CITIZENSHIP_STATUS and value not in CITIZENSHIP_STATUS.values():
                issues.append(f"Invalid citizenship status: {value}")
                fields_valid[field] = False
            else:
                fields_valid[field] = True
        else:
            fields_valid[field] = True

    # Check for signature
    if not data.get('employee_signature'):
        issues.append("Employee signature required")

    completion = len([f for f in fields_valid.values() if f]) / len(required) * 100

    return {
        "section": "section_1",
        "fields_valid": fields_valid,
        "issues": issues,
        "completion_percent": round(completion, 1),
        "complete": completion == 100 and len(issues) == 0,
    }


def validate_section2(data: Dict[str, Any], identity_result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate I-9 Section 2 (Employer)."""
    issues = []

    # Check if identity verification passed
    if not identity_result.get('i9_satisfied'):
        issues.append("Identity verification not satisfied - need valid List A or List B + List C documents")

    # Check for employer signature
    if not data.get('employer_signature'):
        issues.append("Employer/authorized representative signature required")

    if not data.get('employer_name'):
        issues.append("Employer name and title required")

    if not data.get('employer_date'):
        issues.append("Employer signature date required")

    # Verify documents are recorded
    verified_docs = identity_result.get('documents_verified', [])
    if not verified_docs:
        issues.append("No documents recorded in Section 2")

    complete = len(issues) == 0 and identity_result.get('i9_satisfied', False)

    return {
        "section": "section_2",
        "issues": issues,
        "documents_recorded": len(verified_docs),
        "complete": complete,
    }


@register_factory("i9_validate")
async def i9_validate(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate I-9 Employment Eligibility Verification form.

    Input:
        identity_verify: Identity verification results
        form_data: I-9 form field data
        config.validate_dates: Check completion deadlines

    Output:
        valid: Whether I-9 is valid
        sections: Section validation results
        issues: All validation issues
        ready_for_filing: Whether form is complete
    """
    config = input_data.get('config', {})
    identity_result = input_data.get('identity_verify', {})
    form_data = input_data.get('form_data', {})
    state = input_data.get('state', {})

    if not form_data:
        form_data = state.get('input', {}).get('i9_form', {})

    validate_dates = config.get('validate_dates', True)

    # Extract section data
    section1_data = form_data.get('section_1', form_data)
    section2_data = form_data.get('section_2', form_data)

    # Validate sections
    section1_result = validate_section1(section1_data)
    section2_result = validate_section2(section2_data, identity_result)

    # Collect all issues
    all_issues = section1_result.get('issues', []) + section2_result.get('issues', [])

    # Check completion timeline if dates provided
    timeline_issues = []
    if validate_dates:
        hire_date = form_data.get('hire_date') or form_data.get('start_date')
        section1_date = section1_data.get('date_signed') or section1_data.get('employee_date')

        if hire_date and section1_date:
            try:
                hire = datetime.strptime(hire_date, '%Y-%m-%d')
                signed = datetime.strptime(section1_date, '%Y-%m-%d')

                if signed > hire:
                    timeline_issues.append("Section 1 must be completed by first day of work")
            except ValueError:
                pass

    all_issues.extend(timeline_issues)

    # Determine overall validity
    valid = (
        section1_result.get('complete', False) and
        section2_result.get('complete', False) and
        len(timeline_issues) == 0
    )

    # Determine if reverification is needed
    needs_reverification = False
    reverification_date = None

    if identity_result.get('documents_verified'):
        for doc in identity_result['documents_verified']:
            if doc.get('expiration_valid') and 'expiring' in str(doc.get('expiration_valid', '')):
                needs_reverification = True

    return {
        "valid": valid,
        "sections": {
            "section_1": section1_result,
            "section_2": section2_result,
        },
        "issues": all_issues,
        "issue_count": len(all_issues),
        "ready_for_filing": valid,
        "needs_reverification": needs_reverification,
        "reverification_date": reverification_date,
        "e_verify_eligible": valid,  # Can proceed to E-Verify if valid
    }
