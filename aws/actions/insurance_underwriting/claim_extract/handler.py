"""
Claim Extract - Small Factory
Extracts insurance claim details from conversation.

Supports AI-enhanced extraction via Claude when available,
with fallback to pattern-based extraction.
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime
import structlog
from services.small_factory import register_factory

# Claude integration (optional - graceful fallback)
try:
    from services.bedrock_claude import get_bedrock_claude_service
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


# Claim type indicators
CLAIM_TYPE_PATTERNS = {
    "auto": [
        r"car\s+(accident|crash|collision|hit|damaged|stolen|broken)",
        r"vehicle\s+(accident|crash|collision|damage)",
        r"(rear-?ended|side-?swiped|totaled)",
        r"(fender\s+bender|hit\s+and\s+run)",
        r"(windshield|bumper|door|hood)\s+damage",
    ],
    "home": [
        r"(house|home|property)\s+(damage|fire|flood|theft)",
        r"(roof|basement|garage|kitchen)\s+(leak|damage|fire)",
        r"(water\s+damage|storm\s+damage|hail\s+damage)",
        r"(burglary|break-?in|vandalism)",
        r"(pipe\s+burst|flooding|fire)",
    ],
    "health": [
        r"(medical|hospital|doctor|emergency)\s+(bill|expense|visit)",
        r"(surgery|treatment|procedure|prescription)",
        r"(injured|injury|hospitalized)",
    ],
    "life": [
        r"(death|deceased|passed\s+away)",
        r"(beneficiary|life\s+insurance\s+claim)",
    ],
}

# Field extraction patterns
FIELD_PATTERNS = {
    "incident_date": [
        r"(?:happened|occurred|on|date)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"((?:yesterday|last\s+(?:week|month|night|monday|tuesday|wednesday|thursday|friday|saturday|sunday)))",
    ],
    "incident_location": [
        r"(?:at|in|near|on)\s+([^,\.]+(?:street|avenue|road|highway|intersection|parking\s+lot))",
        r"(?:happened\s+(?:at|in|near))\s+([^,\.]+)",
    ],
    "damage_amount": [
        r"(?:damage|repair|cost|worth|estimate)[^\$]*(\$[\d,]+(?:\.\d{2})?)",
        r"(\$[\d,]+(?:\.\d{2})?)\s*(?:in\s+)?damage",
    ],
    "vehicle_info": [
        r"(\d{4}\s+\w+\s+\w+)",  # Year Make Model
    ],
    "injury_description": [
        r"(?:injured|hurt|pain)\s+(?:my|in\s+my)\s+([^,\.]+)",
        r"(?:broken|fractured|sprained)\s+([^,\.]+)",
    ],
}


def detect_claim_type(text: str, valid_types: List[str]) -> Dict[str, Any]:
    """Detect the type of insurance claim."""
    text_lower = text.lower()
    type_scores = {}

    for claim_type in valid_types:
        patterns = CLAIM_TYPE_PATTERNS.get(claim_type, [])
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text_lower)
            matches.extend(found)

        if matches:
            type_scores[claim_type] = {
                "score": min(len(matches) * 0.3, 1.0),
                "indicators": matches[:3]
            }

    if not type_scores:
        return {"type": "unknown", "confidence": 0.0, "indicators": []}

    # Get highest scoring type
    best_type = max(type_scores.items(), key=lambda x: x[1]["score"])
    return {
        "type": best_type[0],
        "confidence": round(best_type[1]["score"], 2),
        "indicators": best_type[1]["indicators"],
        "all_types": type_scores
    }


def extract_claim_fields(text: str, required_fields: List[str]) -> Dict[str, Any]:
    """Extract claim-specific fields from text."""
    fields = {}
    missing_fields = []

    for field_name in required_fields:
        patterns = FIELD_PATTERNS.get(field_name, [])
        value = None

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                break

        if value:
            fields[field_name] = {
                "value": value,
                "extracted": True
            }
        else:
            fields[field_name] = {
                "value": None,
                "extracted": False
            }
            missing_fields.append(field_name)

    return {"fields": fields, "missing_fields": missing_fields}


@register_factory("claim_extract")
async def claim_extract(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract insurance claim details from conversation.

    Input:
        entities: Extracted entities (from entity_extract)
        intent.primary_intent: Classified intent
        config.claim_types: Valid claim types
        config.required_fields: Fields to extract

    Output:
        claim_type: Type of claim (auto, home, health, life)
        claim_details: Extracted claim information
        completeness_score: How complete the claim info is
        missing_fields: Required fields not found
        extracted_entities: Relevant entities for claim
    """
    config = input_data.get('config', {})
    entities_output = input_data.get('entities', {})
    intent_output = input_data.get('intent', {})
    transcribe_output = input_data.get('transcribe', {})
    state = input_data.get('state', {})

    # Get full text
    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')

    claim_types = config.get('claim_types', ['auto', 'home', 'health', 'life'])
    required_fields = config.get('required_fields', ['incident_date', 'incident_type', 'description'])

    # Detect claim type
    claim_type_info = detect_claim_type(full_text, claim_types)

    # Extract fields
    field_extraction = extract_claim_fields(full_text, required_fields)

    # Get relevant entities
    entities = entities_output.get('entities', {})
    extracted_entities = {
        "policy_number": entities.get('POLICY_NUMBER', [{}])[0].get('value') if entities.get('POLICY_NUMBER') else None,
        "claim_number": entities.get('CLAIM_NUMBER', [{}])[0].get('value') if entities.get('CLAIM_NUMBER') else None,
        "claimant_name": entities.get('PERSON', [{}])[0].get('value') if entities.get('PERSON') else None,
        "incident_date": entities.get('DATE', [{}])[0].get('value') if entities.get('DATE') else None,
        "damage_amount": entities.get('MONEY', [{}])[0].get('value') if entities.get('MONEY') else None,
        "location": entities.get('LOCATION', [{}])[0].get('value') if entities.get('LOCATION') else None,
        "vehicle": entities.get('VEHICLE', [{}])[0].get('value') if entities.get('VEHICLE') else None,
        "contact_phone": entities.get('PHONE', [{}])[0].get('value') if entities.get('PHONE') else None,
        "contact_email": entities.get('EMAIL', [{}])[0].get('value') if entities.get('EMAIL') else None,
    }

    # Remove None values
    extracted_entities = {k: v for k, v in extracted_entities.items() if v is not None}

    # Build claim details
    claim_details = {
        "claim_type": claim_type_info["type"],
        "claim_type_confidence": claim_type_info["confidence"],
        "type_indicators": claim_type_info.get("indicators", []),
        **field_extraction["fields"],
        **extracted_entities
    }

    # Calculate completeness
    total_fields = len(required_fields) + 4  # +4 for key entity fields
    filled_fields = len([f for f in field_extraction["fields"].values() if f.get("extracted")]) + len(extracted_entities)
    completeness_score = round(filled_fields / total_fields, 2) if total_fields > 0 else 0

    # Determine if claim is actionable
    is_actionable = (
        claim_type_info["type"] != "unknown" and
        completeness_score >= 0.5 and
        len(field_extraction["missing_fields"]) <= 2
    )

    # Build rule-based result
    rule_based_result = {
        "claim_type": claim_type_info["type"],
        "claim_type_confidence": claim_type_info["confidence"],
        "claim_details": claim_details,
        "completeness_score": completeness_score,
        "missing_fields": field_extraction["missing_fields"],
        "extracted_entities": extracted_entities,
        "is_actionable": is_actionable,
        "requires_callback": len(field_extraction["missing_fields"]) > 0,
        "ai_enhanced": False
    }

    # Try AI-enhanced extraction if enabled
    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED
    if use_ai and full_text:
        try:
            ai_result = await _extract_claims_with_ai(
                full_text,
                entities_output.get('all_entities', [])
            )
            if ai_result:
                # Merge AI insights with rule-based data
                if ai_result.get("claim_type") and ai_result.get("claim_type") != "unknown":
                    rule_based_result["claim_type"] = ai_result["claim_type"]
                    rule_based_result["claim_type_confidence"] = ai_result.get("claim_type_confidence", 0.9)

                # Merge extracted entities (AI fills gaps)
                ai_entities = ai_result.get("extracted_entities", {})
                for key, value in ai_entities.items():
                    if value and not rule_based_result["extracted_entities"].get(key):
                        rule_based_result["extracted_entities"][key] = value

                # Update completeness based on AI extraction
                filled_count = len([v for v in rule_based_result["extracted_entities"].values() if v])
                total_fields = len(required_fields) + 4
                rule_based_result["completeness_score"] = round(min(filled_count / total_fields, 1.0), 2)

                # Update missing fields
                rule_based_result["missing_fields"] = ai_result.get("missing_fields", field_extraction["missing_fields"])

                # Additional AI insights
                rule_based_result["is_actionable"] = ai_result.get("is_actionable", is_actionable)
                rule_based_result["requires_callback"] = ai_result.get("requires_callback", rule_based_result["requires_callback"])
                rule_based_result["ai_enhanced"] = True
                rule_based_result["confidence_scores"] = ai_result.get("confidence_scores", {})

                logger.info("AI-enhanced claim extraction completed", claim_type=rule_based_result["claim_type"])
        except Exception as e:
            logger.warning("AI claim extraction failed, using rule-based", error=str(e))

    return rule_based_result


async def _extract_claims_with_ai(
    transcript: str,
    entities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Extract claims using Claude for intelligent understanding."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_bedrock_claude_service()
    context = {"entities": entities}

    result = await claude.analyze_conversation(
        transcript=transcript,
        analysis_type="claims",
        context=context
    )

    if result.get("success") and result.get("parsed"):
        return result["parsed"]

    return None
