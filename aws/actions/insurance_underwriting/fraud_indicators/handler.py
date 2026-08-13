"""
Fraud Indicators - Small Factory
Analyzes conversation for potential fraud indicators.

Supports AI-enhanced fraud detection via Claude when available,
with fallback to pattern-based detection.
"""

from typing import Dict, Any, List
import re
import structlog
from services.small_factory import register_factory

# Claude integration (optional - graceful fallback)
try:
    from services.bedrock_claude import get_bedrock_claude_service
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


# Fraud indicator patterns
FRAUD_PATTERNS = {
    "inconsistent_story": {
        "description": "Story details are inconsistent or change",
        "patterns": [
            r"(?:actually|wait|no|I\s+mean)\s+(?:it\s+was|that\s+was)",
            r"I\s+(?:think|believe|guess)\s+(?:it\s+was|maybe)",
            r"(?:let\s+me\s+think|hold\s+on)\s+(?:about\s+)?(?:that|when)",
        ],
        "weight": 25,
    },
    "excessive_damage_claims": {
        "description": "Damage claims seem excessive or exaggerated",
        "patterns": [
            r"(?:everything|all|entire|whole)\s+(?:was|is)\s+(?:destroyed|damaged|ruined)",
            r"total\s+loss",
            r"(?:\$\d{2,},000|\$\d{3,}k)",  # High dollar amounts
        ],
        "weight": 20,
    },
    "reluctant_to_provide_details": {
        "description": "Caller hesitant to provide specific details",
        "patterns": [
            r"I\s+don['\u2019]t\s+(?:remember|recall|know)",
            r"(?:can['\u2019]t|cannot)\s+(?:remember|recall)",
            r"(?:why\s+do\s+you|do\s+I\s+have\s+to)\s+need\s+(?:to\s+know|that)",
            r"(?:does\s+it|is\s+that)\s+(?:matter|important|relevant)",
        ],
        "weight": 15,
    },
    "recent_policy_change": {
        "description": "Recent changes to policy before claim",
        "patterns": [
            r"(?:just|recently)\s+(?:changed|updated|increased)\s+(?:my\s+)?(?:coverage|policy)",
            r"(?:added|increased)\s+(?:coverage|limits)\s+(?:last|a\s+few)\s+(?:week|month)",
        ],
        "weight": 20,
    },
    "multiple_recent_claims": {
        "description": "References to multiple recent claims",
        "patterns": [
            r"(?:another|second|third)\s+(?:claim|accident|incident)",
            r"(?:had|filed)\s+(?:a\s+)?(?:claim|accident)\s+(?:last|few)\s+(?:month|week|year)",
            r"this\s+(?:is|makes)\s+(?:my\s+)?(?:second|third|fourth)",
        ],
        "weight": 20,
    },
    "pressure_for_quick_settlement": {
        "description": "Urgency or pressure for quick payout",
        "patterns": [
            r"(?:need|want)\s+(?:the\s+)?(?:money|payment|check)\s+(?:now|immediately|today|asap|urgent)",
            r"(?:can['\u2019]t|cannot)\s+wait",
            r"(?:how\s+)?(?:soon|fast|quick)\s+(?:can\s+I|will\s+I)\s+(?:get|receive)",
        ],
        "weight": 15,
    },
    "no_witnesses": {
        "description": "Emphasis on lack of witnesses",
        "patterns": [
            r"no\s+(?:one|witnesses)\s+(?:was|were)\s+(?:there|around)",
            r"(?:nobody|no\s+one)\s+saw",
            r"(?:alone|by\s+myself)\s+when\s+(?:it|this)\s+happened",
        ],
        "weight": 10,
    },
    "vague_on_timeline": {
        "description": "Vague or uncertain about timing",
        "patterns": [
            r"(?:sometime|around|about|maybe)\s+(?:last|a\s+few)\s+(?:week|month|day)",
            r"I['\u2019]m\s+not\s+(?:sure|certain)\s+(?:when|what\s+time|exactly)",
            r"(?:could\s+have\s+been|might\s+have\s+been)\s+(?:around|about)",
        ],
        "weight": 10,
    },
}


def detect_fraud_indicators(text: str, indicators: List[str], threshold: int) -> Dict[str, Any]:
    """Detect fraud indicators in text."""
    text_lower = text.lower()
    detected = []
    total_score = 0

    for indicator_name, indicator_def in FRAUD_PATTERNS.items():
        if indicators and indicator_name not in indicators:
            continue

        patterns = indicator_def.get('patterns', [])
        matches = []

        for pattern in patterns:
            found = re.findall(pattern, text_lower)
            matches.extend(found)

        if matches:
            weight = indicator_def.get('weight', 10)
            total_score += weight

            detected.append({
                "indicator": indicator_name,
                "description": indicator_def['description'],
                "evidence": matches[:3],
                "weight": weight,
                "count": len(matches)
            })

    # Cap score at 100
    total_score = min(total_score, 100)

    return {
        "detected": detected,
        "total_score": total_score,
        "exceeds_threshold": total_score >= threshold
    }


@register_factory("fraud_indicators")
async def fraud_indicators(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze conversation for potential fraud indicators.

    Input:
        claim: Extracted claim details
        sentiment: Sentiment analysis results
        config.indicators: Specific indicators to check
        config.threshold: Risk threshold (0-100)

    Output:
        fraud_score: Overall fraud risk score (0-100)
        risk_level: low/medium/high
        indicators_detected: List of detected indicators
        recommendation: Suggested action
    """
    config = input_data.get('config', {})
    claim_output = input_data.get('claim', {})
    sentiment_output = input_data.get('sentiment', {})
    transcribe_output = input_data.get('transcribe', {})
    state = input_data.get('state', {})

    # Get text
    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')

    indicators = config.get('indicators', [])
    threshold = config.get('threshold', 70)

    # Detect fraud indicators
    detection_result = detect_fraud_indicators(full_text, indicators, threshold)

    # Adjust score based on sentiment
    sentiment_arc = sentiment_output.get('sentiment_arc', 'stable')
    sentiment_avg = sentiment_output.get('average_score', 0)

    # Negative sentiment + evasiveness adds to fraud score
    sentiment_adjustment = 0
    if sentiment_arc == 'declining' and sentiment_avg < -0.2:
        sentiment_adjustment = 10

    # Claim completeness affects score (incomplete = suspicious)
    completeness = claim_output.get('completeness_score', 1.0)
    completeness_adjustment = int((1 - completeness) * 15)

    final_score = min(100, detection_result['total_score'] + sentiment_adjustment + completeness_adjustment)

    # Determine risk level
    if final_score >= 70:
        risk_level = "high"
        recommendation = "flag_for_siu"  # Special Investigations Unit
    elif final_score >= 40:
        risk_level = "medium"
        recommendation = "additional_verification"
    else:
        risk_level = "low"
        recommendation = "proceed_normally"

    # Build detailed analysis
    analysis = {
        "base_score": detection_result['total_score'],
        "sentiment_adjustment": sentiment_adjustment,
        "completeness_adjustment": completeness_adjustment,
        "indicators_found": len(detection_result['detected']),
    }

    # Build rule-based result
    rule_based_result = {
        "fraud_score": final_score,
        "risk_level": risk_level,
        "exceeds_threshold": final_score >= threshold,
        "indicators_detected": detection_result['detected'],
        "indicator_count": len(detection_result['detected']),
        "recommendation": recommendation,
        "analysis": analysis,
        "requires_review": risk_level in ["high", "medium"],
        "ai_enhanced": False
    }

    # Try AI-enhanced fraud detection if enabled
    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED
    if use_ai and full_text:
        try:
            ai_result = await _detect_fraud_with_ai(
                full_text,
                claim_output,
                sentiment_output,
                list(FRAUD_PATTERNS.keys())
            )
            if ai_result:
                # AI provides sophisticated fraud analysis
                ai_score = ai_result.get("fraud_score", final_score)
                ai_indicators = ai_result.get("indicators_detected", [])

                # Combine rule-based and AI indicators (avoid duplicates)
                rule_indicator_names = {ind["indicator"] for ind in detection_result['detected']}
                for ai_ind in ai_indicators:
                    if ai_ind.get("indicator") not in rule_indicator_names:
                        rule_based_result["indicators_detected"].append(ai_ind)

                # Use AI score if it's more conservative (higher risk detection)
                if ai_score > rule_based_result["fraud_score"]:
                    rule_based_result["fraud_score"] = ai_score
                    # Recalculate risk level
                    if ai_score >= 70:
                        rule_based_result["risk_level"] = "high"
                        rule_based_result["recommendation"] = "flag_for_siu"
                    elif ai_score >= 40:
                        rule_based_result["risk_level"] = "medium"
                        rule_based_result["recommendation"] = "additional_verification"

                rule_based_result["indicator_count"] = len(rule_based_result["indicators_detected"])
                rule_based_result["exceeds_threshold"] = rule_based_result["fraud_score"] >= threshold
                rule_based_result["requires_review"] = rule_based_result["risk_level"] in ["high", "medium"]
                rule_based_result["ai_enhanced"] = True
                rule_based_result["ai_reasoning"] = ai_result.get("reasoning")
                rule_based_result["ai_confidence"] = ai_result.get("confidence")

                logger.info(
                    "AI-enhanced fraud detection completed",
                    fraud_score=rule_based_result["fraud_score"],
                    risk_level=rule_based_result["risk_level"]
                )
        except Exception as e:
            logger.warning("AI fraud detection failed, using rule-based", error=str(e))

    return rule_based_result


async def _detect_fraud_with_ai(
    transcript: str,
    claim_data: Dict[str, Any],
    sentiment_data: Dict[str, Any],
    fraud_indicators: List[str]
) -> Dict[str, Any]:
    """Detect fraud using Claude for sophisticated analysis."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_bedrock_claude_service()
    context = {
        "claim_data": claim_data,
        "sentiment_data": {
            "overall": sentiment_data.get("overall_sentiment"),
            "arc": sentiment_data.get("sentiment_arc"),
            "score": sentiment_data.get("average_score")
        },
        "fraud_indicators": fraud_indicators
    }

    result = await claude.analyze_conversation(
        transcript=transcript,
        analysis_type="fraud",
        context=context
    )

    if result.get("success") and result.get("parsed"):
        return result["parsed"]

    return None
