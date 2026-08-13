"""
Identity Verify - Small Factory
Verifies employee identity documents for onboarding.
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

# Accepted ID document types
ACCEPTED_ID_TYPES = {
    "list_a": [  # Establishes both identity and work authorization
        "us_passport",
        "us_passport_card",
        "permanent_resident_card",
        "employment_authorization_document",
        "foreign_passport_with_i94",
    ],
    "list_b": [  # Establishes identity only
        "drivers_license",
        "state_id",
        "school_id_with_photo",
        "voter_registration_card",
        "military_id",
    ],
    "list_c": [  # Establishes work authorization only
        "social_security_card",
        "birth_certificate",
        "native_american_tribal_document",
    ],
}

# Document validation patterns
DOCUMENT_PATTERNS = {
    "ssn": r'\b\d{3}-?\d{2}-?\d{4}\b',
    "drivers_license": r'[A-Z]{1,2}\d{6,8}',
    "passport": r'[A-Z]\d{8}',
    "state_id": r'[A-Z0-9]{8,12}',
}


def classify_document(doc_type: str) -> Dict[str, Any]:
    """Classify document by I-9 list category."""
    doc_type_lower = doc_type.lower().replace(' ', '_').replace('-', '_')

    for list_name, doc_types in ACCEPTED_ID_TYPES.items():
        if doc_type_lower in doc_types or any(dt in doc_type_lower for dt in doc_types):
            return {
                "list": list_name,
                "accepted": True,
                "establishes_identity": list_name in ["list_a", "list_b"],
                "establishes_work_auth": list_name in ["list_a", "list_c"],
            }

    return {
        "list": None,
        "accepted": False,
        "establishes_identity": False,
        "establishes_work_auth": False,
    }


def validate_document_number(doc_type: str, doc_number: str) -> Dict[str, Any]:
    """Validate document number format."""
    doc_type_lower = doc_type.lower()

    # Find matching pattern
    for pattern_name, pattern in DOCUMENT_PATTERNS.items():
        if pattern_name in doc_type_lower or doc_type_lower in pattern_name:
            if re.match(pattern, doc_number, re.IGNORECASE):
                return {
                    "valid_format": True,
                    "pattern_matched": pattern_name,
                }

    # Generic validation - alphanumeric, reasonable length
    if re.match(r'^[A-Z0-9]{6,15}$', doc_number, re.IGNORECASE):
        return {
            "valid_format": True,
            "pattern_matched": "generic",
        }

    return {
        "valid_format": False,
        "pattern_matched": None,
    }


def check_expiration(expiration_date: str) -> Dict[str, Any]:
    """Check if document is expired or expiring soon."""
    try:
        # Parse various date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y']:
            try:
                exp_date = datetime.strptime(expiration_date, fmt)
                break
            except ValueError:
                continue
        else:
            return {"valid": False, "error": "Could not parse expiration date"}

        today = datetime.now()
        days_until_expiry = (exp_date - today).days

        if days_until_expiry < 0:
            return {
                "valid": False,
                "expired": True,
                "days_expired": abs(days_until_expiry),
            }
        elif days_until_expiry < 30:
            return {
                "valid": True,
                "expiring_soon": True,
                "days_until_expiry": days_until_expiry,
                "warning": "Document expires within 30 days",
            }
        else:
            return {
                "valid": True,
                "expired": False,
                "expiring_soon": False,
                "days_until_expiry": days_until_expiry,
            }

    except Exception as e:
        return {"valid": False, "error": str(e)}


@register_factory("identity_verify")
async def identity_verify(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify employee identity documents.

    Input:
        document_classify: Document classification results
        documents: List of uploaded documents
        config.require_list_a: Require List A document
        config.check_expiration: Validate expiration dates

    Output:
        verified: Whether identity is verified
        documents_verified: List of verified documents
        i9_satisfied: Whether I-9 requirements met
        issues: Any verification issues
    """
    config = input_data.get('config', {})
    doc_classify = input_data.get('document_classify', {})
    documents = input_data.get('documents', [])
    state = input_data.get('state', {})

    if not documents:
        documents = state.get('input', {}).get('documents', [])

    require_list_a = config.get('require_list_a', False)
    check_exp = config.get('check_expiration', True)

    verified_docs = []
    issues = []

    has_identity = False
    has_work_auth = False
    has_list_a = False

    for doc in documents:
        doc_type = doc.get('document_type', doc.get('type', ''))
        doc_number = doc.get('document_number', doc.get('number', ''))
        expiration = doc.get('expiration_date', doc.get('expires', ''))

        # Classify document
        classification = classify_document(doc_type)

        # Validate document number
        number_validation = validate_document_number(doc_type, doc_number) if doc_number else {"valid_format": False}

        # Check expiration
        expiration_check = check_expiration(expiration) if check_exp and expiration else {"valid": True}

        # Build verification result
        doc_result = {
            "document_type": doc_type,
            "document_number": doc_number[:4] + "****" if doc_number else None,  # Mask for security
            "classification": classification,
            "number_valid": number_validation.get('valid_format', False),
            "expiration_valid": expiration_check.get('valid', True),
            "verified": False,
        }

        # Determine if document is verified
        if (classification["accepted"] and
            number_validation.get("valid_format", False) and
            expiration_check.get("valid", True)):
            doc_result["verified"] = True

            if classification["list"] == "list_a":
                has_list_a = True
                has_identity = True
                has_work_auth = True
            if classification["establishes_identity"]:
                has_identity = True
            if classification["establishes_work_auth"]:
                has_work_auth = True

        # Collect issues
        if not classification["accepted"]:
            issues.append(f"Document type '{doc_type}' is not an accepted I-9 document")
        if not number_validation.get("valid_format", False):
            issues.append(f"Invalid document number format for {doc_type}")
        if not expiration_check.get("valid", True):
            if expiration_check.get("expired"):
                issues.append(f"{doc_type} is expired")
            else:
                issues.append(f"Could not validate {doc_type} expiration")
        if expiration_check.get("expiring_soon"):
            issues.append(f"{doc_type} expires in {expiration_check['days_until_expiry']} days")

        verified_docs.append(doc_result)

    # Check I-9 satisfaction
    i9_satisfied = False
    if has_list_a:
        i9_satisfied = True
    elif has_identity and has_work_auth:
        i9_satisfied = True

    if require_list_a and not has_list_a:
        issues.append("List A document required but not provided")
        i9_satisfied = False

    # Overall verification status
    verified = i9_satisfied and len([d for d in verified_docs if d["verified"]]) > 0

    return {
        "verified": verified,
        "documents_verified": verified_docs,
        "verified_count": len([d for d in verified_docs if d["verified"]]),
        "i9_satisfied": i9_satisfied,
        "has_identity_doc": has_identity,
        "has_work_auth_doc": has_work_auth,
        "has_list_a_doc": has_list_a,
        "issues": issues,
        "issue_count": len(issues),
        "ready_for_i9": i9_satisfied and len(issues) == 0,
    }
