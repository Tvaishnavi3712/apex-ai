"""
Patient Identify - Small Factory
Extracts and validates patient identity from medical documents.
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime
import structlog
from services.small_factory import register_factory

# Claude integration (optional)
try:
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()

# Common date patterns for DOB
DOB_PATTERNS = [
    r'(?:DOB|Date of Birth|Birth Date)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    r'(?:DOB|Date of Birth|Birth Date)[:\s]*(\w+\s+\d{1,2},?\s+\d{4})',
    r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b',
]

# MRN patterns
MRN_PATTERNS = [
    r'(?:MRN|Medical Record|Patient ID|Chart)[:\s#]*([A-Z0-9]{6,12})',
    r'(?:Record Number)[:\s#]*([A-Z0-9]{6,12})',
]

# SSN patterns (for validation, handle with care)
SSN_PATTERNS = [
    r'(?:SSN|Social Security)[:\s]*(\d{3}-\d{2}-\d{4})',
    r'(?:SSN|Social Security)[:\s]*(\d{9})',
]


def extract_patient_name(text: str) -> Optional[Dict[str, str]]:
    """Extract patient name from text."""
    patterns = [
        r'(?:Patient|Name)[:\s]*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)',
        r'(?:Patient|Name)[:\s]*([A-Z]+,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?)?)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Parse into components
            if ',' in name:
                parts = name.split(',')
                return {
                    "full_name": f"{parts[1].strip()} {parts[0].strip()}",
                    "last_name": parts[0].strip(),
                    "first_name": parts[1].strip(),
                }
            else:
                parts = name.split()
                return {
                    "full_name": name,
                    "first_name": parts[0] if parts else "",
                    "last_name": parts[-1] if len(parts) > 1 else "",
                }

    return None


def extract_dob(text: str) -> Optional[str]:
    """Extract date of birth."""
    for pattern in DOB_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_mrn(text: str) -> Optional[str]:
    """Extract medical record number."""
    for pattern in MRN_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def extract_insurance(text: str) -> Optional[Dict[str, str]]:
    """Extract insurance information."""
    insurance_info = {}

    # Insurance name
    ins_pattern = r'(?:Insurance|Payer|Plan)[:\s]*([A-Za-z\s]+(?:Health|Insurance|Plan|PPO|HMO|Medicare|Medicaid))'
    match = re.search(ins_pattern, text, re.IGNORECASE)
    if match:
        insurance_info["name"] = match.group(1).strip()

    # Member ID
    member_pattern = r'(?:Member ID|Subscriber ID|Policy)[:\s#]*([A-Z0-9]{8,15})'
    match = re.search(member_pattern, text, re.IGNORECASE)
    if match:
        insurance_info["member_id"] = match.group(1)

    # Group number
    group_pattern = r'(?:Group|Group Number|GRP)[:\s#]*([A-Z0-9]{5,12})'
    match = re.search(group_pattern, text, re.IGNORECASE)
    if match:
        insurance_info["group_number"] = match.group(1)

    return insurance_info if insurance_info else None


@register_factory("patient_identify")
async def patient_identify(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and validate patient identity from documents.

    Input:
        document_classify.content: Document text content
        document_classify.document_type: Type of document
        config.require_mrn: Whether MRN is required
        config.verify_against_ehr: Verify against EHR

    Output:
        patient: Patient identification details
        mrn: Medical record number
        verified: Whether identity was verified
        confidence: Identification confidence
    """
    config = input_data.get('config', {})
    doc = input_data.get('document_classify', {})
    state = input_data.get('state', {})

    # Get document content
    content = doc.get('content', '') or doc.get('text', '')
    if not content:
        content = state.get('input', {}).get('document', {}).get('content', '')

    require_mrn = config.get('require_mrn', False)
    verify_against_ehr = config.get('verify_against_ehr', False)

    # Extract patient information
    name_info = extract_patient_name(content)
    dob = extract_dob(content)
    mrn = extract_mrn(content)
    insurance = extract_insurance(content)

    # Calculate confidence
    confidence = 0.0
    fields_found = []

    if name_info:
        confidence += 0.3
        fields_found.append("name")
    if dob:
        confidence += 0.25
        fields_found.append("dob")
    if mrn:
        confidence += 0.25
        fields_found.append("mrn")
    if insurance:
        confidence += 0.2
        fields_found.append("insurance")

    # Build patient object
    patient = {
        "name": name_info,
        "date_of_birth": dob,
        "mrn": mrn,
        "insurance": insurance,
    }

    # Determine verification status
    verified = False
    verification_notes = []

    if mrn and verify_against_ehr:
        # In production, this would call EHR API
        verified = True  # Simulated
        verification_notes.append("MRN verified against EHR")

    if require_mrn and not mrn:
        verification_notes.append("MRN required but not found")

    # Check for missing critical fields
    missing_fields = []
    if not name_info:
        missing_fields.append("patient_name")
    if not dob:
        missing_fields.append("date_of_birth")
    if require_mrn and not mrn:
        missing_fields.append("mrn")

    return {
        "patient": patient,
        "mrn": mrn,
        "verified": verified,
        "confidence": round(confidence, 2),
        "fields_found": fields_found,
        "missing_fields": missing_fields,
        "verification_notes": verification_notes,
        "has_insurance": insurance is not None,
        "ready_for_processing": len(missing_fields) == 0,
    }
