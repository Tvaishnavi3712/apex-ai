"""
Intent Classify - Small Factory
Classifies the primary intent of a call/conversation.
"""

from typing import Dict, Any, List
import re
from services.small_factory import register_factory


# Intent patterns for classification
INTENT_PATTERNS = {
    "file_claim": [
        r"file\s+a?\s*claim",
        r"make\s+a?\s*claim",
        r"report\s+(an?\s+)?accident",
        r"car\s+(was\s+)?(hit|damaged|stolen)",
        r"need\s+to\s+claim",
        r"submit\s+a?\s*claim",
    ],
    "check_status": [
        r"check\s+(on\s+)?(my\s+)?claim",
        r"status\s+of\s+(my\s+)?claim",
        r"where\s+(is|are)\s+(my\s+)?claim",
        r"update\s+on\s+(my\s+)?claim",
        r"claim\s+number",
    ],
    "billing_inquiry": [
        r"(my\s+)?bill",
        r"payment",
        r"premium",
        r"how\s+much\s+(do\s+I\s+)?owe",
        r"charge",
        r"invoice",
    ],
    "policy_change": [
        r"change\s+(my\s+)?policy",
        r"update\s+(my\s+)?(coverage|policy|address)",
        r"add\s+(a\s+)?(driver|vehicle|coverage)",
        r"remove\s+(a\s+)?(driver|vehicle)",
        r"cancel\s+(my\s+)?policy",
    ],
    "complaint": [
        r"not\s+happy",
        r"frustrated",
        r"complaint",
        r"speak\s+to\s+(a\s+)?(manager|supervisor)",
        r"unacceptable",
        r"terrible\s+service",
    ],
    "general_inquiry": [
        r"question\s+about",
        r"wondering\s+if",
        r"can\s+you\s+tell\s+me",
        r"information\s+(about|on)",
        r"how\s+does",
    ],
}


@register_factory("intent_classify")
async def intent_classify(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify the primary intent of the conversation.

    Input:
        transcribe.full_text: Full transcript text
        config.intents: List of intents to classify against

    Output:
        primary_intent: Main detected intent
        confidence: Confidence score (0-1)
        secondary_intents: Other detected intents
        intent_signals: Text snippets that triggered classification
    """
    config = input_data.get('config', {})
    transcribe_output = input_data.get('transcribe', {})

    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        # Try to get from state
        state = input_data.get('state', {})
        transcript = state.get('input', {}).get('transcript', {})
        full_text = transcript.get('full_text', '')

    configured_intents = config.get('intents', list(INTENT_PATTERNS.keys()))

    # Score each intent
    intent_scores = {}
    intent_signals = {}

    text_lower = full_text.lower()

    for intent in configured_intents:
        patterns = INTENT_PATTERNS.get(intent, [])
        matches = []

        for pattern in patterns:
            found = re.findall(pattern, text_lower)
            matches.extend(found)

        if matches:
            # Score based on number of matches and pattern strength
            score = min(len(matches) * 0.25, 1.0)
            intent_scores[intent] = score
            intent_signals[intent] = matches[:3]  # Top 3 signals

    # Determine primary intent
    if intent_scores:
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
        primary_intent = sorted_intents[0][0]
        confidence = sorted_intents[0][1]
        secondary_intents = [
            {"intent": i[0], "confidence": i[1]}
            for i in sorted_intents[1:4]
        ]
    else:
        primary_intent = "general_inquiry"
        confidence = 0.3
        secondary_intents = []

    return {
        "primary_intent": primary_intent,
        "confidence": round(confidence, 2),
        "secondary_intents": secondary_intents,
        "intent_signals": intent_signals,
        "all_scores": intent_scores
    }
