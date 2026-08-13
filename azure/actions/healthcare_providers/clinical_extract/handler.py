"""
Clinical Extract - Small Factory
Extracts clinical information from medical documents.
AI-enhanced extraction via Claude when available.
"""

from typing import Dict, Any, List, Optional
import re
import structlog
from services.small_factory import register_factory

# Claude integration (optional)
try:
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()

# Clinical section headers
SECTION_PATTERNS = {
    "chief_complaint": [r"(?:Chief Complaint|CC|Presenting Complaint)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "history_present_illness": [r"(?:History of Present Illness|HPI)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "past_medical_history": [r"(?:Past Medical History|PMH)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "medications": [r"(?:Medications|Current Medications|Meds)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "allergies": [r"(?:Allergies|Drug Allergies|NKDA)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "assessment": [r"(?:Assessment|Diagnosis|Impression)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "plan": [r"(?:Plan|Treatment Plan|Recommendations)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
    "vitals": [r"(?:Vital Signs|Vitals)[:\s]*(.+?)(?=\n[A-Z]|\n\n|$)"],
}

# Vital signs patterns
VITAL_PATTERNS = {
    "blood_pressure": r"(?:BP|Blood Pressure)[:\s]*(\d{2,3}/\d{2,3})",
    "heart_rate": r"(?:HR|Heart Rate|Pulse)[:\s]*(\d{2,3})",
    "temperature": r"(?:Temp|Temperature)[:\s]*(\d{2,3}\.?\d*)",
    "respiratory_rate": r"(?:RR|Resp Rate|Respiratory Rate)[:\s]*(\d{1,2})",
    "oxygen_saturation": r"(?:SpO2|O2 Sat|Oxygen)[:\s]*(\d{2,3})%?",
    "weight": r"(?:Weight|Wt)[:\s]*(\d{2,3}\.?\d*)\s*(?:kg|lbs?|pounds?)?",
    "height": r"(?:Height|Ht)[:\s]*(\d{1,3}(?:\.\d+)?)\s*(?:cm|in|ft)?",
}

# Medication extraction
def extract_medications(text: str) -> List[Dict[str, Any]]:
    """Extract medications from text."""
    medications = []

    # Common medication patterns
    med_pattern = r'([A-Za-z]+(?:in|ol|ide|ate|one|ine|am|il))\s*(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|units?)?(?:\s*(daily|bid|tid|qid|prn|qhs|qd|hs))?'

    matches = re.findall(med_pattern, text, re.IGNORECASE)
    for match in matches:
        medications.append({
            "name": match[0],
            "dose": match[1],
            "unit": match[2] or "mg",
            "frequency": match[3] or "unknown",
        })

    return medications


def extract_diagnoses(text: str) -> List[Dict[str, Any]]:
    """Extract diagnoses from assessment section."""
    diagnoses = []

    # Look for numbered diagnoses
    dx_pattern = r'(?:\d+[\.\)]\s*)([A-Z][a-z]+(?:\s+[a-z]+){0,4})'
    matches = re.findall(dx_pattern, text)

    for match in matches:
        diagnoses.append({
            "description": match.strip(),
            "icd_code": None,  # Will be filled by code_suggest
        })

    return diagnoses


def extract_vitals(text: str) -> Dict[str, Any]:
    """Extract vital signs."""
    vitals = {}

    for vital_name, pattern in VITAL_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            vitals[vital_name] = match.group(1)

    return vitals


@register_factory("clinical_extract")
async def clinical_extract(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract clinical information from medical documents.

    Input:
        document_classify.content: Document text
        patient_identify.patient: Patient info
        config.sections: Sections to extract
        config.use_ai: Whether to use AI extraction

    Output:
        sections: Extracted clinical sections
        vitals: Vital signs
        medications: Medication list
        diagnoses: Diagnosis list
        procedures: Procedure list
    """
    config = input_data.get('config', {})
    doc = input_data.get('document_classify', {})
    patient = input_data.get('patient_identify', {})
    state = input_data.get('state', {})

    content = doc.get('content', '') or doc.get('text', '')
    if not content:
        content = state.get('input', {}).get('document', {}).get('content', '')

    sections_to_extract = config.get('sections', list(SECTION_PATTERNS.keys()))
    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED

    # Extract sections using patterns
    sections = {}
    for section_name in sections_to_extract:
        patterns = SECTION_PATTERNS.get(section_name, [])
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
                break

    # Extract structured data
    vitals = extract_vitals(content)
    medications = extract_medications(content)
    diagnoses = extract_diagnoses(sections.get('assessment', content))

    # Try AI-enhanced extraction
    ai_enhanced = False
    if use_ai and content:
        try:
            ai_result = await _extract_clinical_with_ai(content, sections)
            if ai_result:
                # Merge AI results
                if ai_result.get('medications'):
                    medications = ai_result['medications']
                if ai_result.get('diagnoses'):
                    diagnoses = ai_result['diagnoses']
                if ai_result.get('sections'):
                    for key, value in ai_result['sections'].items():
                        if key not in sections or not sections[key]:
                            sections[key] = value
                ai_enhanced = True
                logger.info("AI-enhanced clinical extraction completed")
        except Exception as e:
            logger.warning("AI extraction failed", error=str(e))

    # Calculate extraction completeness
    expected_sections = ['chief_complaint', 'assessment', 'plan']
    found_sections = [s for s in expected_sections if s in sections and sections[s]]
    completeness = len(found_sections) / len(expected_sections)

    return {
        "sections": sections,
        "vitals": vitals,
        "medications": medications,
        "medication_count": len(medications),
        "diagnoses": diagnoses,
        "diagnosis_count": len(diagnoses),
        "procedures": [],  # Will be extracted by AI or procedure-specific logic
        "completeness_score": round(completeness, 2),
        "ai_enhanced": ai_enhanced,
        "document_type": doc.get('document_type', 'clinical_note'),
    }


async def _extract_clinical_with_ai(content: str, existing_sections: Dict) -> Optional[Dict[str, Any]]:
    """Use Claude for intelligent clinical extraction."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_model_router()

    system_prompt = """You are a medical documentation specialist. Extract clinical information from medical documents accurately.
Focus on: diagnoses, medications (with doses), procedures, and key clinical findings.
Always respond with valid JSON."""

    user_prompt = f"""Extract clinical information from this medical document:

{content[:4000]}

Respond with JSON:
{{
  "diagnoses": [{{"description": "...", "icd_code": "suggested code or null"}}],
  "medications": [{{"name": "...", "dose": "...", "unit": "...", "frequency": "..."}}],
  "procedures": [{{"name": "...", "cpt_code": "suggested code or null"}}],
  "sections": {{
    "chief_complaint": "...",
    "assessment": "...",
    "plan": "..."
  }},
  "key_findings": ["finding 1", "finding 2"]
}}"""

    result = await claude.invoke(
        prompt=user_prompt,
        system_prompt=system_prompt,
        temperature=0.1,
    )

    if result.get("success"):
        try:
            import json
            # Extract JSON from response
            response = result["response"]
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
        except Exception:
            pass

    return None
