"""
Code Suggest - Small Factory
Suggests ICD-10 and CPT codes based on clinical documentation.
AI-enhanced code suggestion via Claude.
"""

from typing import Dict, Any, List, Optional
import re
import structlog
from services.small_factory import register_factory

# Claude integration
try:
    from services.bedrock_claude import get_bedrock_claude_service
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()

# Common ICD-10 codes mapping (simplified)
ICD10_MAPPINGS = {
    "hypertension": {"code": "I10", "description": "Essential (primary) hypertension"},
    "diabetes": {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
    "diabetes type 2": {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
    "diabetes type 1": {"code": "E10.9", "description": "Type 1 diabetes mellitus without complications"},
    "chest pain": {"code": "R07.9", "description": "Chest pain, unspecified"},
    "headache": {"code": "R51.9", "description": "Headache, unspecified"},
    "back pain": {"code": "M54.5", "description": "Low back pain"},
    "anxiety": {"code": "F41.9", "description": "Anxiety disorder, unspecified"},
    "depression": {"code": "F32.9", "description": "Major depressive disorder, single episode, unspecified"},
    "copd": {"code": "J44.9", "description": "Chronic obstructive pulmonary disease, unspecified"},
    "asthma": {"code": "J45.909", "description": "Unspecified asthma, uncomplicated"},
    "pneumonia": {"code": "J18.9", "description": "Pneumonia, unspecified organism"},
    "uti": {"code": "N39.0", "description": "Urinary tract infection, site not specified"},
    "fracture": {"code": "S72.90", "description": "Unspecified fracture of unspecified femur"},
}

# Common CPT codes mapping
CPT_MAPPINGS = {
    "office visit new": {"code": "99203", "description": "Office visit, new patient, low complexity"},
    "office visit established": {"code": "99213", "description": "Office visit, established patient, low complexity"},
    "comprehensive exam": {"code": "99215", "description": "Office visit, established patient, high complexity"},
    "chest xray": {"code": "71046", "description": "Radiologic examination, chest, 2 views"},
    "ekg": {"code": "93000", "description": "Electrocardiogram, routine ECG with interpretation"},
    "blood draw": {"code": "36415", "description": "Collection of venous blood by venipuncture"},
    "cbc": {"code": "85025", "description": "Complete blood count with differential"},
    "metabolic panel": {"code": "80053", "description": "Comprehensive metabolic panel"},
    "urinalysis": {"code": "81003", "description": "Urinalysis, automated, without microscopy"},
}


def match_icd_code(diagnosis: str) -> Optional[Dict[str, Any]]:
    """Match diagnosis to ICD-10 code."""
    diagnosis_lower = diagnosis.lower()

    for keyword, code_info in ICD10_MAPPINGS.items():
        if keyword in diagnosis_lower:
            return {
                "code": code_info["code"],
                "description": code_info["description"],
                "confidence": 0.85,
                "match_type": "keyword",
            }

    return None


def match_cpt_code(procedure: str) -> Optional[Dict[str, Any]]:
    """Match procedure to CPT code."""
    procedure_lower = procedure.lower()

    for keyword, code_info in CPT_MAPPINGS.items():
        if keyword in procedure_lower or procedure_lower in keyword:
            return {
                "code": code_info["code"],
                "description": code_info["description"],
                "confidence": 0.85,
                "match_type": "keyword",
            }

    return None


@register_factory("code_suggest")
async def code_suggest(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Suggest ICD-10 and CPT codes for clinical documentation.

    Input:
        clinical_extract.diagnoses: List of diagnoses
        clinical_extract.procedures: List of procedures
        clinical_extract.sections: Clinical sections
        config.use_ai: Whether to use AI coding
        config.require_review: Require human review

    Output:
        icd_codes: Suggested ICD-10 codes
        cpt_codes: Suggested CPT codes
        coding_confidence: Overall confidence
        requires_review: Whether coding needs review
    """
    config = input_data.get('config', {})
    clinical = input_data.get('clinical_extract', {})
    state = input_data.get('state', {})

    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED
    require_review = config.get('require_review', True)

    diagnoses = clinical.get('diagnoses', [])
    procedures = clinical.get('procedures', [])
    sections = clinical.get('sections', {})

    # Rule-based code matching
    icd_codes = []
    for dx in diagnoses:
        description = dx.get('description', '')
        matched = match_icd_code(description)
        if matched:
            icd_codes.append({
                "diagnosis": description,
                **matched,
            })
        else:
            icd_codes.append({
                "diagnosis": description,
                "code": None,
                "confidence": 0,
                "needs_manual_coding": True,
            })

    cpt_codes = []
    for proc in procedures:
        name = proc.get('name', '')
        matched = match_cpt_code(name)
        if matched:
            cpt_codes.append({
                "procedure": name,
                **matched,
            })

    # AI-enhanced coding
    ai_enhanced = False
    if use_ai and (sections or diagnoses):
        try:
            ai_result = await _suggest_codes_with_ai(
                diagnoses,
                procedures,
                sections.get('assessment', ''),
                sections.get('plan', '')
            )
            if ai_result:
                # Merge AI suggestions for uncoded items
                for i, icd in enumerate(icd_codes):
                    if not icd.get('code') and i < len(ai_result.get('icd_codes', [])):
                        ai_icd = ai_result['icd_codes'][i]
                        icd_codes[i] = {
                            "diagnosis": icd['diagnosis'],
                            "code": ai_icd.get('code'),
                            "description": ai_icd.get('description'),
                            "confidence": ai_icd.get('confidence', 0.7),
                            "match_type": "ai",
                        }

                # Add AI-suggested CPT codes
                if ai_result.get('cpt_codes'):
                    for ai_cpt in ai_result['cpt_codes']:
                        if not any(c.get('code') == ai_cpt.get('code') for c in cpt_codes):
                            cpt_codes.append({
                                "procedure": ai_cpt.get('procedure', ''),
                                "code": ai_cpt.get('code'),
                                "description": ai_cpt.get('description'),
                                "confidence": ai_cpt.get('confidence', 0.7),
                                "match_type": "ai",
                            })

                ai_enhanced = True
                logger.info("AI-enhanced code suggestion completed")
        except Exception as e:
            logger.warning("AI code suggestion failed", error=str(e))

    # Calculate overall confidence
    all_confidences = [c.get('confidence', 0) for c in icd_codes + cpt_codes if c.get('code')]
    avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0

    # Determine if review needed
    needs_review = (
        require_review or
        avg_confidence < 0.8 or
        any(c.get('needs_manual_coding') for c in icd_codes)
    )

    return {
        "icd_codes": icd_codes,
        "icd_count": len([c for c in icd_codes if c.get('code')]),
        "cpt_codes": cpt_codes,
        "cpt_count": len([c for c in cpt_codes if c.get('code')]),
        "coding_confidence": round(avg_confidence, 2),
        "requires_review": needs_review,
        "ai_enhanced": ai_enhanced,
        "uncoded_diagnoses": [c['diagnosis'] for c in icd_codes if not c.get('code')],
    }


async def _suggest_codes_with_ai(
    diagnoses: List[Dict],
    procedures: List[Dict],
    assessment: str,
    plan: str
) -> Optional[Dict[str, Any]]:
    """Use Claude for intelligent code suggestion."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_bedrock_claude_service()

    system_prompt = """You are a certified medical coder specializing in ICD-10 and CPT coding.
Suggest appropriate codes based on clinical documentation.
Be specific with codes - suggest the most specific applicable code.
Always respond with valid JSON."""

    diagnoses_text = "\n".join([f"- {d.get('description', d)}" for d in diagnoses])
    procedures_text = "\n".join([f"- {p.get('name', p)}" for p in procedures])

    user_prompt = f"""Suggest ICD-10 and CPT codes for this clinical documentation:

Diagnoses:
{diagnoses_text or 'Not specified'}

Procedures:
{procedures_text or 'Not specified'}

Assessment:
{assessment[:1000] or 'Not provided'}

Plan:
{plan[:1000] or 'Not provided'}

Respond with JSON:
{{
  "icd_codes": [
    {{"code": "I10", "description": "Essential hypertension", "confidence": 0.95}}
  ],
  "cpt_codes": [
    {{"code": "99213", "procedure": "Office visit", "description": "...", "confidence": 0.9}}
  ]
}}"""

    result = await claude.invoke(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.1,
    )

    if result.get("success"):
        try:
            import json
            response = result["response"]
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass

    return None
