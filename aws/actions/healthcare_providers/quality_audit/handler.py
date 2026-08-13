"""
Quality Audit - Small Factory
Audits clinical documentation for quality and completeness.
"""

from typing import Dict, Any, List
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

# Documentation quality requirements
QUALITY_REQUIREMENTS = {
    "patient_identification": {
        "required_fields": ["name", "date_of_birth", "mrn"],
        "weight": 15,
    },
    "chief_complaint": {
        "required": True,
        "min_length": 10,
        "weight": 15,
    },
    "history_present_illness": {
        "required": True,
        "min_length": 50,
        "weight": 20,
    },
    "assessment": {
        "required": True,
        "min_length": 20,
        "requires_diagnosis": True,
        "weight": 25,
    },
    "plan": {
        "required": True,
        "min_length": 20,
        "weight": 20,
    },
    "signature": {
        "required": True,
        "weight": 5,
    },
}

# Compliance checklist
COMPLIANCE_CHECKS = {
    "legibility": "Documentation is clear and readable",
    "timeliness": "Documentation completed within required timeframe",
    "authentication": "Document is properly signed/authenticated",
    "no_prohibited_abbreviations": "No prohibited abbreviations used",
    "complete_medication_list": "Complete medication list with doses",
    "allergy_documentation": "Allergies documented or NKDA stated",
}


def audit_patient_identification(patient_data: Dict) -> Dict[str, Any]:
    """Audit patient identification completeness."""
    required = QUALITY_REQUIREMENTS["patient_identification"]["required_fields"]
    patient = patient_data.get('patient', {})

    found = []
    missing = []

    for field in required:
        if field == "name" and patient.get('name'):
            found.append(field)
        elif field == "date_of_birth" and patient.get('date_of_birth'):
            found.append(field)
        elif field == "mrn" and patient_data.get('mrn'):
            found.append(field)
        else:
            missing.append(field)

    score = len(found) / len(required) * 100 if required else 100

    return {
        "category": "patient_identification",
        "score": round(score, 1),
        "found_fields": found,
        "missing_fields": missing,
        "passed": score >= 80,
    }


def audit_section(section_name: str, content: str, has_diagnosis: bool = False) -> Dict[str, Any]:
    """Audit a clinical section."""
    req = QUALITY_REQUIREMENTS.get(section_name, {})

    issues = []
    score = 100

    # Check if required
    if req.get('required') and not content:
        return {
            "category": section_name,
            "score": 0,
            "issues": [f"{section_name} is required but missing"],
            "passed": False,
        }

    # Check minimum length
    min_length = req.get('min_length', 0)
    if content and len(content) < min_length:
        score -= 30
        issues.append(f"{section_name} content is too brief (minimum {min_length} characters)")

    # Check for diagnosis requirement
    if req.get('requires_diagnosis') and not has_diagnosis:
        score -= 20
        issues.append("Assessment should include at least one diagnosis")

    return {
        "category": section_name,
        "score": max(0, score),
        "issues": issues,
        "passed": score >= 70,
        "content_length": len(content) if content else 0,
    }


def check_compliance(clinical_data: Dict, patient_data: Dict) -> List[Dict[str, Any]]:
    """Run compliance checks."""
    results = []

    # Check allergy documentation
    content = str(clinical_data.get('sections', {}))
    has_allergies = 'allerg' in content.lower() or 'nkda' in content.lower()
    results.append({
        "check": "allergy_documentation",
        "description": COMPLIANCE_CHECKS["allergy_documentation"],
        "passed": has_allergies,
        "severity": "high" if not has_allergies else None,
    })

    # Check medication list
    medications = clinical_data.get('medications', [])
    meds_complete = len(medications) > 0 or 'no medication' in content.lower()
    results.append({
        "check": "complete_medication_list",
        "description": COMPLIANCE_CHECKS["complete_medication_list"],
        "passed": meds_complete,
        "severity": "medium" if not meds_complete else None,
    })

    # Check for authentication (simplified)
    has_signature = 'signature' in content.lower() or 'md' in content.lower() or 'np' in content.lower()
    results.append({
        "check": "authentication",
        "description": COMPLIANCE_CHECKS["authentication"],
        "passed": has_signature,
        "severity": "high" if not has_signature else None,
    })

    return results


@register_factory("quality_audit")
async def quality_audit(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit clinical documentation for quality and completeness.

    Input:
        clinical_extract: Extracted clinical data
        patient_identify: Patient identification
        code_suggest: Coding information
        config.strict_mode: Enable strict auditing

    Output:
        overall_score: Quality score (0-100)
        passed: Whether documentation passes audit
        section_scores: Per-section scores
        compliance_results: Compliance check results
        issues: List of identified issues
        recommendations: Improvement recommendations
    """
    config = input_data.get('config', {})
    clinical = input_data.get('clinical_extract', {})
    patient = input_data.get('patient_identify', {})
    codes = input_data.get('code_suggest', {})

    strict_mode = config.get('strict_mode', False)
    pass_threshold = 80 if strict_mode else 70

    sections = clinical.get('sections', {})
    has_diagnosis = codes.get('icd_count', 0) > 0 or len(clinical.get('diagnoses', [])) > 0

    # Audit each section
    section_scores = []

    # Patient identification
    section_scores.append(audit_patient_identification(patient))

    # Clinical sections
    for section_name in ['chief_complaint', 'history_present_illness', 'assessment', 'plan']:
        content = sections.get(section_name, '')
        audit_result = audit_section(
            section_name,
            content,
            has_diagnosis if section_name == 'assessment' else False
        )
        section_scores.append(audit_result)

    # Compliance checks
    compliance_results = check_compliance(clinical, patient)

    # Calculate overall score
    weights = QUALITY_REQUIREMENTS
    total_weight = sum(w.get('weight', 10) for w in weights.values())
    weighted_score = 0

    for audit in section_scores:
        category = audit['category']
        weight = weights.get(category, {}).get('weight', 10)
        weighted_score += (audit['score'] / 100) * weight

    # Add compliance impact
    compliance_passed = sum(1 for c in compliance_results if c['passed'])
    compliance_score = (compliance_passed / len(compliance_results)) * 100 if compliance_results else 100
    weighted_score += (compliance_score / 100) * 10  # 10% weight for compliance

    overall_score = round(weighted_score / (total_weight + 10) * 100, 1)

    # Collect issues
    issues = []
    for audit in section_scores:
        issues.extend(audit.get('issues', []))
    for audit in section_scores:
        if audit.get('missing_fields'):
            issues.append(f"Missing: {', '.join(audit['missing_fields'])}")

    for check in compliance_results:
        if not check['passed']:
            issues.append(f"Compliance: {check['description']}")

    # Generate recommendations
    recommendations = []
    if overall_score < 80:
        if any(a['category'] == 'assessment' and a['score'] < 70 for a in section_scores):
            recommendations.append("Expand assessment section with detailed diagnosis and reasoning")
        if any(a['category'] == 'plan' and a['score'] < 70 for a in section_scores):
            recommendations.append("Include specific treatment plan with follow-up instructions")
        if codes.get('uncoded_diagnoses'):
            recommendations.append("Ensure all diagnoses have appropriate ICD-10 codes")

    return {
        "overall_score": overall_score,
        "passed": overall_score >= pass_threshold,
        "pass_threshold": pass_threshold,
        "section_scores": section_scores,
        "compliance_results": compliance_results,
        "compliance_score": round(compliance_score, 1),
        "issues": issues,
        "issue_count": len(issues),
        "recommendations": recommendations,
        "ready_for_billing": overall_score >= 80 and codes.get('icd_count', 0) > 0,
    }
