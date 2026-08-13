"""
Claim Extract - Healthcare Payers Action (Context-Driven)
Extract claim data from submitted documents

Context-Driven Architecture:
- Extraction fields from playbook context.extraction_config
- Claim types from context.claim_config
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
        "claim_number", "patient_info", "provider_info",
        "service_dates", "diagnosis_codes", "procedure_codes",
        "billed_amount", "units"
    ],
    "confidence_threshold": 0.85,
    "require_validation": True
}

# Claim type patterns
DEFAULT_CLAIM_TYPES = {
    "professional": ["CMS-1500", "837P"],
    "institutional": ["UB-04", "837I"],
    "dental": ["ADA", "837D"],
    "pharmacy": ["NCPDP", "D.0"]
}


@register_factory("claim_extract")
async def claim_extract(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract claim data from documents (context-driven).

    Context keys used:
        - extraction_config: Fields to extract and confidence thresholds
        - claim_config: Claim type configurations

    Input:
        document_content: Raw document content or S3 reference
        document_type: Type of claim form

    Output:
        claim_data: Extracted claim information
        extraction_confidence: Confidence scores
        validation_results: Field validation results
    """
    context = context or input_data.get('context', {})
    extraction_config = context.get('extraction_config', DEFAULT_EXTRACTION_CONFIG)
    claim_config = context.get('claim_config', {})

    logger.info(
        "Claim extract invoked",
        context_driven=bool(context)
    )

    document_content = input_data.get('document_content', '')
    document_type = input_data.get('document_type', 'unknown')

    # Determine claim type
    claim_type = _detect_claim_type(document_type, claim_config)

    # Extract fields based on configuration
    extract_fields = extraction_config.get('extract_fields', DEFAULT_EXTRACTION_CONFIG['extract_fields'])
    confidence_threshold = extraction_config.get('confidence_threshold', 0.85)

    # Simulated extraction results
    extracted_data = {
        "claim_number": _extract_claim_number(document_content),
        "patient_info": {
            "member_id": "MEM123456",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1980-05-15",
            "relationship": "self"
        },
        "provider_info": {
            "npi": "1234567890",
            "tax_id": "12-3456789",
            "name": "Medical Center",
            "address": {
                "street": "123 Medical Way",
                "city": "Healthcare City",
                "state": "HC",
                "zip": "12345"
            }
        },
        "service_dates": {
            "from_date": "2024-01-15",
            "to_date": "2024-01-15"
        },
        "diagnosis_codes": [
            {"code": "J06.9", "description": "Acute upper respiratory infection"},
            {"code": "R05.9", "description": "Cough"}
        ],
        "procedure_codes": [
            {"code": "99213", "description": "Office visit, established patient", "units": 1},
            {"code": "87880", "description": "Strep test", "units": 1}
        ],
        "billed_amount": 250.00,
        "units": 2
    }

    # Calculate confidence scores
    confidence_scores = {}
    for field in extract_fields:
        if field in extracted_data:
            confidence_scores[field] = 0.92  # Simulated confidence
        else:
            confidence_scores[field] = 0.0

    overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0

    # Validate extracted data
    validation_results = _validate_claim_data(extracted_data, extraction_config)

    # Check if meets confidence threshold
    meets_threshold = overall_confidence >= confidence_threshold

    return {
        "claim_number": extracted_data.get('claim_number'),
        "claim_type": claim_type,
        "claim_data": extracted_data,
        "extraction_confidence": round(overall_confidence, 3),
        "field_confidences": confidence_scores,
        "meets_confidence_threshold": meets_threshold,
        "confidence_threshold": confidence_threshold,
        "validation_results": validation_results,
        "validation_passed": all(v.get('valid', False) for v in validation_results.values()),
        "fields_extracted": len([f for f in extract_fields if f in extracted_data]),
        "total_fields": len(extract_fields),
        "extracted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "claim_extract",
        "factory_version": "2.0.0",
        "context_keys_used": ["extraction_config", "claim_config"]
    }


def _detect_claim_type(document_type: str, claim_config: Dict) -> str:
    """Detect claim type from document type."""
    claim_types = claim_config.get('claim_types', DEFAULT_CLAIM_TYPES)

    document_type_lower = document_type.lower()
    for claim_type, patterns in claim_types.items():
        for pattern in patterns:
            if pattern.lower() in document_type_lower:
                return claim_type

    return "professional"  # Default


def _extract_claim_number(content: str) -> str:
    """Extract claim number from content."""
    # Simulated extraction
    return f"CLM{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


def _validate_claim_data(data: Dict, config: Dict) -> Dict[str, Dict]:
    """Validate extracted claim data."""
    results = {}

    # Validate claim number
    claim_number = data.get('claim_number', '')
    results['claim_number'] = {
        'valid': bool(claim_number),
        'message': 'Valid' if claim_number else 'Missing claim number'
    }

    # Validate patient info
    patient = data.get('patient_info', {})
    results['patient_info'] = {
        'valid': bool(patient.get('member_id')),
        'message': 'Valid' if patient.get('member_id') else 'Missing member ID'
    }

    # Validate provider NPI
    provider = data.get('provider_info', {})
    npi = provider.get('npi', '')
    results['provider_info'] = {
        'valid': len(npi) == 10 and npi.isdigit(),
        'message': 'Valid NPI' if len(npi) == 10 else 'Invalid NPI format'
    }

    # Validate diagnosis codes
    diagnoses = data.get('diagnosis_codes', [])
    results['diagnosis_codes'] = {
        'valid': len(diagnoses) > 0,
        'message': f'{len(diagnoses)} diagnosis codes found'
    }

    # Validate procedure codes
    procedures = data.get('procedure_codes', [])
    results['procedure_codes'] = {
        'valid': len(procedures) > 0,
        'message': f'{len(procedures)} procedure codes found'
    }

    return results


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(claim_extract(event))
