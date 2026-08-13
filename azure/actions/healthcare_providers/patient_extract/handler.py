"""
Patient Extract - Healthcare Providers Action (Context-Driven)
Extract patient demographic and clinical data from intake forms

Context-Driven Architecture:
- Extraction fields from playbook context.extraction_config
- Required fields from context.patient_requirements
- Validation rules from context.validation_rules
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

logger = structlog.get_logger()


# Default extraction configuration
DEFAULT_EXTRACTION_CONFIG = {
    "extract_fields": [
        "patient_name", "date_of_birth", "ssn", "address", "phone",
        "email", "emergency_contact", "insurance_info", "medical_history",
        "current_medications", "allergies", "chief_complaint"
    ],
    "confidence_threshold": 0.85,
    "require_validation": True
}

# Default patient requirements
DEFAULT_PATIENT_REQUIREMENTS = {
    "required_fields": ["patient_name", "date_of_birth", "phone"],
    "optional_fields": ["email", "ssn"],
    "validate_ssn": False,
    "validate_phone": True
}


@register_factory("patient_extract")
async def patient_extract(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract patient information from intake forms (context-driven).

    Context keys used:
        - extraction_config: Fields to extract and thresholds
        - patient_requirements: Required field configurations

    Input:
        document_content: Raw document content
        document_type: Type of intake form

    Output:
        patient_data: Extracted patient information
        validation_results: Field validation results
        extraction_confidence: Overall confidence score
    """
    context = context or input_data.get('context', {})
    extraction_config = context.get('extraction_config', DEFAULT_EXTRACTION_CONFIG)
    patient_requirements = context.get('patient_requirements', DEFAULT_PATIENT_REQUIREMENTS)

    logger.info(
        "Patient extract invoked",
        context_driven=bool(context)
    )

    document_content = input_data.get('document_content', '')
    document_type = input_data.get('document_type', 'intake_form')

    # Extract fields based on configuration
    extract_fields = extraction_config.get('extract_fields', DEFAULT_EXTRACTION_CONFIG['extract_fields'])
    confidence_threshold = extraction_config.get('confidence_threshold', 0.85)

    # Simulated extraction
    extracted_data = {
        "patient_name": {
            "first_name": "Jane",
            "last_name": "Smith",
            "middle_name": "M"
        },
        "date_of_birth": "1985-03-22",
        "ssn": "XXX-XX-1234",  # Masked
        "address": {
            "street": "456 Oak Street",
            "city": "Healthcare City",
            "state": "HC",
            "zip": "12345"
        },
        "phone": {
            "home": "555-123-4567",
            "mobile": "555-987-6543"
        },
        "email": "jane.smith@email.com",
        "emergency_contact": {
            "name": "John Smith",
            "relationship": "Spouse",
            "phone": "555-111-2222"
        },
        "insurance_info": {
            "primary": {
                "carrier": "Blue Cross",
                "policy_number": "BC123456789",
                "group_number": "GRP001",
                "subscriber": "Jane Smith",
                "relationship": "self"
            }
        },
        "medical_history": {
            "conditions": ["Hypertension", "Type 2 Diabetes"],
            "surgeries": ["Appendectomy (2010)"],
            "family_history": ["Heart Disease (Father)"]
        },
        "current_medications": [
            {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily"},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "once daily"}
        ],
        "allergies": [
            {"allergen": "Penicillin", "reaction": "Rash", "severity": "moderate"}
        ],
        "chief_complaint": "Annual wellness visit"
    }

    # Calculate confidence scores
    confidence_scores = {}
    for field in extract_fields:
        if field in extracted_data:
            confidence_scores[field] = 0.92
        else:
            confidence_scores[field] = 0.0

    overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0

    # Validate extracted data
    validation_results = _validate_patient_data(
        extracted_data,
        patient_requirements
    )

    # Check required fields
    required_fields = patient_requirements.get('required_fields', [])
    missing_required = [f for f in required_fields if f not in extracted_data or not extracted_data[f]]

    # Calculate completeness
    fields_extracted = len([f for f in extract_fields if f in extracted_data and extracted_data[f]])
    completeness = fields_extracted / len(extract_fields) * 100 if extract_fields else 0

    return {
        "patient_data": extracted_data,
        "patient_name": f"{extracted_data['patient_name']['first_name']} {extracted_data['patient_name']['last_name']}",
        "date_of_birth": extracted_data.get('date_of_birth'),
        "extraction_confidence": round(overall_confidence, 3),
        "field_confidences": confidence_scores,
        "meets_confidence_threshold": overall_confidence >= confidence_threshold,
        "validation_results": validation_results,
        "validation_passed": all(v.get('valid', False) for v in validation_results.values()),
        "required_fields_present": len(missing_required) == 0,
        "missing_required_fields": missing_required,
        "fields_extracted": fields_extracted,
        "total_fields": len(extract_fields),
        "completeness_percentage": round(completeness, 1),
        "document_type": document_type,
        "has_insurance": bool(extracted_data.get('insurance_info')),
        "has_medical_history": bool(extracted_data.get('medical_history')),
        "medication_count": len(extracted_data.get('current_medications', [])),
        "allergy_count": len(extracted_data.get('allergies', [])),
        "extracted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "patient_extract",
        "factory_version": "2.0.0",
        "context_keys_used": ["extraction_config", "patient_requirements"]
    }


def _validate_patient_data(data: Dict, requirements: Dict) -> Dict[str, Dict]:
    """Validate extracted patient data."""
    results = {}

    # Validate name
    name = data.get('patient_name', {})
    results['patient_name'] = {
        'valid': bool(name.get('first_name') and name.get('last_name')),
        'message': 'Valid' if name.get('first_name') else 'Missing name'
    }

    # Validate DOB
    dob = data.get('date_of_birth')
    results['date_of_birth'] = {
        'valid': bool(dob),
        'message': 'Valid' if dob else 'Missing date of birth'
    }

    # Validate phone
    phone = data.get('phone', {})
    has_phone = bool(phone.get('home') or phone.get('mobile'))
    results['phone'] = {
        'valid': has_phone,
        'message': 'Valid' if has_phone else 'Missing phone number'
    }

    # Validate email format
    email = data.get('email', '')
    email_valid = bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)) if email else True
    results['email'] = {
        'valid': email_valid,
        'message': 'Valid' if email_valid else 'Invalid email format'
    }

    # Validate insurance
    insurance = data.get('insurance_info', {})
    results['insurance_info'] = {
        'valid': bool(insurance.get('primary')),
        'message': 'Primary insurance found' if insurance.get('primary') else 'No insurance information'
    }

    return results


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(patient_extract(event))
