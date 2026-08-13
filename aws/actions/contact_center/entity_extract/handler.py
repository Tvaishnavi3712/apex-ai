"""
Entity Extract - Small Factory
Extracts named entities from conversation text.
"""

from typing import Dict, Any, List
import re
from services.small_factory import register_factory


# Entity patterns
ENTITY_PATTERNS = {
    "PERSON": [
        r"(?:my name is|i'm|this is|speaking with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        r"(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+)",
    ],
    "DATE": [
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
        r"((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{0,4})",
        r"((?:yesterday|today|last week|last month|last year))",
        r"(\d{1,2}\s+(?:days?|weeks?|months?)\s+ago)",
    ],
    "LOCATION": [
        r"(?:in|at|near|on)\s+([A-Z][a-z]+(?:\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr))?)",
        r"(?:city of|town of)\s+([A-Z][a-z]+)",
    ],
    "MONEY": [
        r"(\$[\d,]+(?:\.\d{2})?)",
        r"(\d+(?:,\d{3})*(?:\.\d{2})?\s*dollars?)",
    ],
    "POLICY_NUMBER": [
        r"(?:policy\s*(?:number|#|num)?:?\s*)([A-Z]{2,3}-?\d{6,10})",
        r"(?:policy\s*(?:number|#|num)?:?\s*)(\d{8,12})",
    ],
    "CLAIM_NUMBER": [
        r"(?:claim\s*(?:number|#|num)?:?\s*)([A-Z]{2,3}-?\d{6,10})",
        r"(?:claim\s*(?:number|#|num)?:?\s*)(CLM-?\d{6,10})",
    ],
    "PHONE": [
        r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})",
        r"(\d{3}[-.\s]\d{3}[-.\s]\d{4})",
    ],
    "EMAIL": [
        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
    ],
    "VEHICLE": [
        r"(\d{4}\s+(?:Toyota|Honda|Ford|Chevrolet|BMW|Mercedes|Audi|Nissan|Hyundai|Kia|Subaru|Mazda|Lexus|Acura|Volkswagen|Volvo|Jeep|Ram|GMC|Dodge|Cadillac|Buick|Lincoln|Infiniti|Tesla)[^\.,]*)",
    ],
    "ADDRESS": [
        r"(\d+\s+[A-Z][a-z]+(?:\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir|Court|Ct))(?:,?\s+(?:Apt|Suite|Unit|#)\s*\d+)?)",
    ],
}


def extract_entities(text: str, entity_types: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Extract entities from text based on specified types."""
    entities: Dict[str, List[Dict[str, Any]]] = {}

    for entity_type in entity_types:
        patterns = ENTITY_PATTERNS.get(entity_type, [])
        matches = []

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group(1) if match.lastindex else match.group(0)
                # Avoid duplicates
                if not any(m['value'].lower() == value.lower() for m in matches):
                    matches.append({
                        "value": value.strip(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.85  # Pattern-based confidence
                    })

        if matches:
            entities[entity_type] = matches

    return entities


@register_factory("entity_extract")
async def entity_extract(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract named entities from conversation.

    Input:
        transcribe.full_text: Full transcript text
        config.entity_types: List of entity types to extract

    Output:
        entities: Dict of entity type -> list of found entities
        entity_count: Total entities found
        summary: Summary of key entities
    """
    config = input_data.get('config', {})
    transcribe_output = input_data.get('transcribe', {})

    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        state = input_data.get('state', {})
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')

    entity_types = config.get('entity_types', list(ENTITY_PATTERNS.keys()))

    # Extract entities
    entities = extract_entities(full_text, entity_types)

    # Count total
    entity_count = sum(len(ents) for ents in entities.values())

    # Build summary of key entities (first of each type)
    summary = {}
    for entity_type, ents in entities.items():
        if ents:
            summary[entity_type.lower()] = ents[0]['value']

    # Build flat list for easier processing
    all_entities = []
    for entity_type, ents in entities.items():
        for ent in ents:
            all_entities.append({
                "type": entity_type,
                **ent
            })

    # Sort by position in text
    all_entities.sort(key=lambda x: x.get('start', 0))

    return {
        "entities": entities,
        "all_entities": all_entities,
        "entity_count": entity_count,
        "summary": summary,
        "types_found": list(entities.keys())
    }
