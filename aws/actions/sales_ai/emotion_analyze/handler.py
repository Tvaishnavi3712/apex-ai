"""
Emotion Analysis Action
Analyze emotional cues from sales conversations (voice tone, pace, sentiment)

Supports both:
- Lambda invocation (standalone)
- Small Factory pattern (chain processing)
"""

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

# AI Enhancement
try:
    from services.bedrock_claude import get_bedrock_claude_service
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


# Emotion categories for sales conversations
EMOTION_CATEGORIES = {
    "enthusiasm": {"positive": True, "weight": 1.2, "buying_signal": True},
    "interest": {"positive": True, "weight": 1.1, "buying_signal": True},
    "curiosity": {"positive": True, "weight": 1.0, "buying_signal": True},
    "confidence": {"positive": True, "weight": 1.0, "buying_signal": False},
    "satisfaction": {"positive": True, "weight": 1.1, "buying_signal": True},
    "neutral": {"positive": None, "weight": 0.5, "buying_signal": False},
    "hesitation": {"positive": False, "weight": 0.8, "buying_signal": False},
    "confusion": {"positive": False, "weight": 0.7, "buying_signal": False},
    "skepticism": {"positive": False, "weight": 0.9, "buying_signal": False},
    "frustration": {"positive": False, "weight": 1.0, "buying_signal": False},
    "disengagement": {"positive": False, "weight": 1.2, "buying_signal": False},
}

# Emotion indicator phrases
EMOTION_INDICATORS = {
    "enthusiasm": [
        "that's exactly what we need", "this is great", "i love this",
        "perfect", "absolutely", "excited about", "can't wait"
    ],
    "interest": [
        "tell me more", "how does that work", "interesting",
        "i'd like to know", "what about", "can you explain"
    ],
    "hesitation": [
        "i'm not sure", "maybe", "let me think", "i need to consider",
        "have to check with", "not certain"
    ],
    "skepticism": [
        "sounds too good", "what's the catch", "i've heard that before",
        "prove it", "show me data", "competitors say"
    ],
    "frustration": [
        "we've tried that", "doesn't work for us", "waste of time",
        "not what i asked", "you're not listening"
    ],
    "disengagement": [
        "let's move on", "we'll see", "send me something",
        "i'll get back to you", "not a priority"
    ]
}


@apex_action(ApexActionSchema(
    name="emotion_analyze",
    description="Analyze emotional cues from sales conversations",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Emotion analysis parameters")
        .add_string("transcript", "Conversation transcript", required=True)
        .add_array("speaker_segments", "Speaker-labeled segments", required=False)
        .add_string("prospect_role", "Prospect speaker label", required=False)
        .add_boolean("include_timeline", "Include emotion timeline", required=False),
    output_schema=ActionOutputSchema(description="Emotion analysis result")
        .add_object("prospect_emotions", "Prospect emotional profile")
        .add_object("rep_emotions", "Sales rep emotional profile")
        .add_array("emotion_timeline", "Emotion changes over conversation")
        .add_number("engagement_score", "Overall engagement score 0-100")
        .add_array("emotional_peaks", "Key emotional moments")
        .add_array("risk_indicators", "Emotional risk signals")
))
def emotion_analyze(
    transcript: str,
    speaker_segments: List[Dict] = None,
    prospect_role: str = "Customer",
    include_timeline: bool = True
) -> dict:
    """
    Analyze emotional cues in sales conversations

    Args:
        transcript: Full conversation transcript
        speaker_segments: Speaker-labeled conversation segments
        prospect_role: Label for prospect speaker
        include_timeline: Whether to generate emotion timeline

    Returns:
        Comprehensive emotion analysis
    """
    result = {
        "prospect_emotions": {
            "dominant_emotion": "neutral",
            "emotion_scores": {},
            "positive_ratio": 0.5,
            "engagement_trend": "stable"
        },
        "rep_emotions": {
            "dominant_emotion": "confident",
            "emotion_scores": {},
            "energy_level": "medium"
        },
        "emotion_timeline": [],
        "engagement_score": 50,
        "emotional_peaks": [],
        "risk_indicators": [],
        "buying_signals_from_emotion": [],
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False
    }

    if not transcript:
        return result

    transcript_lower = transcript.lower()

    # Analyze emotions from transcript
    emotion_counts = {emotion: 0 for emotion in EMOTION_CATEGORIES}

    for emotion, indicators in EMOTION_INDICATORS.items():
        for indicator in indicators:
            if indicator in transcript_lower:
                emotion_counts[emotion] += 1

    # Calculate emotion scores
    total_indicators = sum(emotion_counts.values()) or 1
    emotion_scores = {
        emotion: round((count / total_indicators) * 100, 1)
        for emotion, count in emotion_counts.items()
        if count > 0
    }

    # Determine dominant emotion
    if emotion_scores:
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
    else:
        dominant_emotion = "neutral"

    result["prospect_emotions"]["emotion_scores"] = emotion_scores
    result["prospect_emotions"]["dominant_emotion"] = dominant_emotion

    # Calculate positive ratio
    positive_count = sum(
        count for emotion, count in emotion_counts.items()
        if EMOTION_CATEGORIES.get(emotion, {}).get("positive") is True
    )
    negative_count = sum(
        count for emotion, count in emotion_counts.items()
        if EMOTION_CATEGORIES.get(emotion, {}).get("positive") is False
    )
    total = positive_count + negative_count or 1
    result["prospect_emotions"]["positive_ratio"] = round(positive_count / total, 2)

    # Calculate engagement score
    engagement_factors = {
        "enthusiasm": 25,
        "interest": 20,
        "curiosity": 15,
        "satisfaction": 20,
        "hesitation": -10,
        "skepticism": -15,
        "frustration": -25,
        "disengagement": -30
    }

    engagement_score = 50  # Base score
    for emotion, score_mod in engagement_factors.items():
        if emotion in emotion_scores:
            engagement_score += (emotion_scores[emotion] / 100) * score_mod

    result["engagement_score"] = max(0, min(100, round(engagement_score)))

    # Determine engagement trend
    if result["engagement_score"] >= 70:
        result["prospect_emotions"]["engagement_trend"] = "increasing"
    elif result["engagement_score"] <= 30:
        result["prospect_emotions"]["engagement_trend"] = "decreasing"
    else:
        result["prospect_emotions"]["engagement_trend"] = "stable"

    # Identify emotional peaks (key moments)
    emotional_peaks = []
    for emotion, indicators in EMOTION_INDICATORS.items():
        for indicator in indicators:
            if indicator in transcript_lower:
                idx = transcript_lower.find(indicator)
                # Extract context around the indicator
                start = max(0, idx - 50)
                end = min(len(transcript), idx + len(indicator) + 50)
                context = transcript[start:end]

                emotional_peaks.append({
                    "emotion": emotion,
                    "trigger_phrase": indicator,
                    "context": f"...{context}...",
                    "position_percent": round((idx / len(transcript)) * 100),
                    "significance": EMOTION_CATEGORIES.get(emotion, {}).get("weight", 1.0)
                })

    # Sort by significance and take top 5
    emotional_peaks.sort(key=lambda x: x["significance"], reverse=True)
    result["emotional_peaks"] = emotional_peaks[:5]

    # Identify risk indicators
    risk_emotions = ["frustration", "disengagement", "skepticism"]
    for emotion in risk_emotions:
        if emotion_scores.get(emotion, 0) > 20:
            result["risk_indicators"].append({
                "type": f"high_{emotion}",
                "severity": "high" if emotion_scores[emotion] > 40 else "medium",
                "description": f"Prospect showing signs of {emotion}",
                "recommendation": _get_emotion_recommendation(emotion)
            })

    # Extract buying signals from positive emotions
    for emotion, config in EMOTION_CATEGORIES.items():
        if config.get("buying_signal") and emotion in emotion_scores:
            if emotion_scores[emotion] > 15:
                result["buying_signals_from_emotion"].append({
                    "signal": f"emotional_{emotion}",
                    "strength": "strong" if emotion_scores[emotion] > 30 else "moderate",
                    "description": f"Prospect expressing {emotion}"
                })

    # Generate emotion timeline if requested
    if include_timeline and speaker_segments:
        result["emotion_timeline"] = _generate_emotion_timeline(speaker_segments)

    return result


def _get_emotion_recommendation(emotion: str) -> str:
    """Get coaching recommendation for handling emotion"""
    recommendations = {
        "frustration": "Acknowledge their concerns, ask clarifying questions, and refocus on their specific needs",
        "disengagement": "Re-engage with a compelling question or share a relevant success story",
        "skepticism": "Provide specific data, case studies, or offer to connect them with references",
        "hesitation": "Address specific concerns, offer a trial or pilot program",
        "confusion": "Simplify your explanation, use analogies, or offer a visual demonstration"
    }
    return recommendations.get(emotion, "Continue building rapport and understanding their needs")


def _generate_emotion_timeline(segments: List[Dict]) -> List[Dict]:
    """Generate emotion timeline from speaker segments"""
    timeline = []

    for i, segment in enumerate(segments):
        text = segment.get("text", "").lower()
        speaker = segment.get("speaker", "unknown")

        # Quick emotion detection for segment
        segment_emotion = "neutral"
        for emotion, indicators in EMOTION_INDICATORS.items():
            if any(ind in text for ind in indicators):
                segment_emotion = emotion
                break

        timeline.append({
            "segment_index": i,
            "speaker": speaker,
            "emotion": segment_emotion,
            "is_positive": EMOTION_CATEGORIES.get(segment_emotion, {}).get("positive"),
            "timestamp_percent": round((i / len(segments)) * 100)
        })

    return timeline


class EmotionAnalyzeAction(ApexActionBase):
    """Emotion Analysis Action (class-based)"""

    name = "emotion_analyze"
    description = "Analyze emotional cues from sales conversations"
    category = "sales_intelligence"
    industry = "sales_ai"

    def execute(self, **kwargs) -> dict:
        return emotion_analyze(**kwargs)


# Small Factory registration
@register_factory("emotion_analyze")
async def emotion_analyze_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Small Factory handler for emotion analysis.

    Expected input_data:
        - transcript: Conversation transcript
        - speaker_segments: Speaker-labeled segments (optional)
        - prospect_role: Prospect speaker label (optional)
        - include_timeline: Whether to include timeline (optional)

    Returns:
        Comprehensive emotion analysis with engagement scoring
    """
    logger.info("Emotion analyze factory invoked")

    # Check for AI enhancement
    use_ai = input_data.get("use_ai", True)

    result = emotion_analyze(
        transcript=input_data.get("transcript", ""),
        speaker_segments=input_data.get("speaker_segments"),
        prospect_role=input_data.get("prospect_role", "Customer"),
        include_timeline=input_data.get("include_timeline", True)
    )

    # AI enhancement for deeper emotion analysis
    if use_ai and CLAUDE_ENABLED:
        try:
            ai_result = await _ai_emotion_analysis(
                input_data.get("transcript", ""),
                result
            )
            if ai_result:
                result["ai_analysis"] = ai_result
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI emotion analysis failed", error=str(e))

    result["factory_id"] = "emotion_analyze"
    result["factory_version"] = "1.0.0"

    return result


async def _ai_emotion_analysis(transcript: str, rule_based_result: dict) -> Optional[Dict]:
    """Use Claude for deeper emotion analysis"""
    if not CLAUDE_ENABLED:
        return None

    try:
        claude = get_bedrock_claude_service()

        prompt = f"""Analyze the emotional dynamics in this sales conversation.

Transcript:
{transcript[:3000]}

Rule-based analysis found:
- Dominant emotion: {rule_based_result['prospect_emotions']['dominant_emotion']}
- Engagement score: {rule_based_result['engagement_score']}

Provide:
1. Deeper emotional insights not captured by keyword matching
2. Subtle emotional shifts and their triggers
3. Relationship dynamics between speakers
4. Emotional buying readiness assessment
5. Specific coaching recommendations based on emotional state

Format as JSON with keys: deeper_insights, emotional_shifts, relationship_dynamics, buying_readiness, coaching_recommendations"""

        response = await claude.analyze_conversation(
            transcript=transcript,
            analysis_type="custom",
            context={"custom_prompt": prompt}
        )

        return response
    except Exception as e:
        logger.error("AI emotion analysis error", error=str(e))
        return None


def handler(event, context):
    """Lambda entry point"""
    return emotion_analyze(**event)
