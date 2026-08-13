"""
Medical Necessity Check Action
Evaluate medical necessity for procedures based on clinical guidelines

Context-Driven Architecture:
- Medical necessity rules are read from playbook context.medical_necessity_rules
- Each CPT code maps to required diagnoses, criteria, and documentation
"""

import boto3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase

# Small Factory registration
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


@apex_action(ApexActionSchema(
    name="medical_necessity_check",
    description="Evaluate medical necessity for procedures based on clinical guidelines",
    category="utilization_management",
    industry="healthcare_payers",
    input_schema=ActionInputSchema(description="Medical necessity check parameters")
        .add_string("procedure_code", "CPT/HCPCS procedure code", required=True)
        .add_array("diagnosis_codes", "ICD-10 diagnosis codes", required=True)
        .add_string("clinical_notes", "Clinical documentation summary", required=False)
        .add_array("supporting_documents", "List of supporting document types", required=False)
        .add_string("patient_age", "Patient age for age-based criteria", required=False)
        .add_string("patient_gender", "Patient gender for gender-based criteria", required=False)
        .add_object("context", "Playbook context with medical_necessity_rules", required=False),
    output_schema=ActionOutputSchema(description="Medical necessity determination")
        .add_boolean("medically_necessary", "Whether procedure is medically necessary")
        .add_string("determination", "Determination: approved, denied, pend_for_review")
        .add_number("confidence_score", "Confidence score 0-100")
        .add_array("criteria_met", "Criteria that were met")
        .add_array("criteria_not_met", "Criteria that were not met")
        .add_array("missing_documentation", "Documentation needed for approval")
        .add_string("guideline_reference", "Clinical guideline reference")
))
def medical_necessity_check(
    procedure_code: str,
    diagnosis_codes: List[str],
    clinical_notes: str = None,
    supporting_documents: List[str] = None,
    patient_age: str = None,
    patient_gender: str = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Check medical necessity for a procedure using context-driven rules

    Args:
        procedure_code: CPT/HCPCS code
        diagnosis_codes: ICD-10 diagnosis codes
        clinical_notes: Clinical documentation
        supporting_documents: Supporting document types
        patient_age: Patient age
        patient_gender: Patient gender
        context: Playbook context containing medical_necessity_rules

    Returns:
        Medical necessity determination
    """
    context = context or {}
    supporting_documents = supporting_documents or []

    # Get medical necessity rules from context
    med_necessity_rules = context.get("medical_necessity_rules", {})

    result = {
        "procedure_code": procedure_code,
        "medically_necessary": False,
        "determination": "pend_for_review",
        "confidence_score": 0,
        "criteria_met": [],
        "criteria_not_met": [],
        "missing_documentation": [],
        "guideline_reference": None,
        "review_date": datetime.now().isoformat(),
        "context_driven": bool(context)
    }

    # Get guidelines for procedure from context
    guidelines = _get_guidelines_for_code(procedure_code, med_necessity_rules)

    if not guidelines:
        # No specific guidelines - check for valid diagnosis linkage
        if diagnosis_codes:
            result["medically_necessary"] = True
            result["determination"] = "approved"
            result["confidence_score"] = 70
            result["criteria_met"].append("Valid diagnosis code provided")
            result["guideline_reference"] = "General medical necessity - diagnosis linkage"
        else:
            result["determination"] = "denied"
            result["criteria_not_met"].append("No diagnosis code provided")
        return result

    result["guideline_reference"] = guidelines.get("guideline_reference", f"Clinical Policy: {procedure_code}")
    result["rule_source"] = guidelines.get("source", "default")

    # Check diagnosis codes
    required_dx = guidelines.get("required_diagnoses", [])
    dx_matched = False
    for dx in diagnosis_codes:
        # Check if diagnosis matches (including prefix matching for ICD-10)
        for req_dx in required_dx:
            if dx.startswith(req_dx) or req_dx.startswith(dx):
                dx_matched = True
                result["criteria_met"].append(f"Diagnosis {dx} supports procedure")
                break
        if dx_matched:
            break

    if not dx_matched and required_dx:
        result["criteria_not_met"].append(
            f"No supporting diagnosis found. Required: {', '.join(required_dx[:3])}"
        )

    # Check documentation
    required_docs = guidelines.get("documentation_required", [])
    provided_docs = [doc.lower() for doc in supporting_documents]

    for doc in required_docs:
        doc_lower = doc.lower()
        if any(doc_lower in pd or pd in doc_lower for pd in provided_docs):
            result["criteria_met"].append(f"Documentation provided: {doc}")
        else:
            result["missing_documentation"].append(doc)

    # Evaluate clinical criteria if notes provided
    criteria = guidelines.get("criteria", [])
    if clinical_notes:
        clinical_notes_lower = clinical_notes.lower()
        for criterion in criteria:
            # Simple keyword matching
            keywords = criterion.lower().split()[:3]
            if any(kw in clinical_notes_lower for kw in keywords):
                result["criteria_met"].append(criterion)
            else:
                result["criteria_not_met"].append(criterion)
    else:
        result["criteria_not_met"].extend(criteria)
        result["missing_documentation"].append("Clinical notes")

    # Calculate confidence and determination
    total_criteria = len(criteria) + 1  # +1 for diagnosis
    met_criteria = len([c for c in result["criteria_met"] if not c.startswith("Documentation provided")])

    if dx_matched:
        met_criteria += 1

    confidence = (met_criteria / max(total_criteria, 1)) * 100
    result["confidence_score"] = round(confidence, 1)

    # Get approval thresholds from context or use defaults
    thresholds = med_necessity_rules.get("approval_thresholds", {
        "auto_approve": 80,
        "pend_review": 50
    })

    # Determine result
    if not dx_matched:
        result["determination"] = "denied"
        result["medically_necessary"] = False
    elif confidence >= thresholds.get("auto_approve", 80) and not result["missing_documentation"]:
        result["determination"] = "approved"
        result["medically_necessary"] = True
    elif confidence >= thresholds.get("pend_review", 50):
        result["determination"] = "pend_for_review"
        result["medically_necessary"] = False
    else:
        result["determination"] = "denied"
        result["medically_necessary"] = False

    return result


def _get_guidelines_for_code(procedure_code: str, med_necessity_rules: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get medical necessity guidelines for a procedure code from context.

    Looks up in context.medical_necessity_rules by CPT code.
    """
    if not med_necessity_rules:
        return None

    # Direct code lookup
    if procedure_code in med_necessity_rules:
        rule = med_necessity_rules[procedure_code]
        if isinstance(rule, dict):
            rule["source"] = "context"
            return rule

    # Check if code is in a category
    for category, rules in med_necessity_rules.items():
        if isinstance(rules, dict) and "codes" in rules:
            if procedure_code in rules.get("codes", []):
                return {
                    "required_diagnoses": rules.get("required_diagnoses", []),
                    "criteria": rules.get("criteria", []),
                    "documentation_required": rules.get("documentation_required", []),
                    "guideline_reference": rules.get("guideline_reference", f"Category: {category}"),
                    "source": f"context.{category}"
                }

    return None


class MedicalNecessityAction(ApexActionBase):
    """Medical Necessity Check Action (class-based)"""

    name = "medical_necessity_check"
    description = "Evaluate medical necessity based on clinical guidelines"
    category = "utilization_management"
    industry = "healthcare_payers"

    def execute(self, **kwargs) -> dict:
        return medical_necessity_check(**kwargs)


# Small Factory registration
@register_factory("medical_necessity_check")
async def medical_necessity_factory(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Small Factory handler for medical necessity check (context-driven).

    Expected input_data:
        - procedure_code: CPT/HCPCS code
        - diagnosis_codes: ICD-10 diagnosis codes
        - clinical_notes: Clinical documentation (optional)
        - supporting_documents: Document types (optional)
        - patient_age: Patient age (optional)
        - patient_gender: Patient gender (optional)

    Context keys used:
        - medical_necessity_rules: CPT-to-diagnosis mappings and criteria

    Returns:
        Medical necessity determination
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Medical necessity check factory invoked",
        procedure_code=input_data.get("procedure_code"),
        context_driven=bool(effective_context)
    )

    result = medical_necessity_check(
        procedure_code=input_data.get("procedure_code", ""),
        diagnosis_codes=input_data.get("diagnosis_codes", []),
        clinical_notes=input_data.get("clinical_notes"),
        supporting_documents=input_data.get("supporting_documents"),
        patient_age=input_data.get("patient_age"),
        patient_gender=input_data.get("patient_gender"),
        context=effective_context
    )

    result["factory_id"] = "medical_necessity_check"
    result["factory_version"] = "2.0.0"  # Version bump for context-driven
    result["context_keys_used"] = ["medical_necessity_rules"]

    return result


def handler(event, context):
    """Lambda entry point"""
    return medical_necessity_check(**event)
