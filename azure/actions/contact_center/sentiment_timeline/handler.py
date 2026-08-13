"""
Sentiment Timeline - Small Factory (Context-Driven)
Analyzes sentiment throughout a conversation with timeline tracking.

Context-Driven Architecture:
- Sentiment word dictionaries are read from playbook context.sentiment_config
- Classification thresholds are read from context.sentiment_config.thresholds
- Peak detection settings are read from context.sentiment_config.peaks

Supports AI-enhanced sentiment analysis via Claude when available,
with fallback to keyword-based analysis.
"""

from typing import Dict, Any, List, Optional
import re
import structlog
from services.small_factory import register_factory

# Claude integration (optional - graceful fallback)
try:
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


# Default sentiment keywords (used when context not provided)
DEFAULT_POSITIVE_WORDS = {
    "thank", "thanks", "appreciate", "great", "wonderful", "excellent",
    "perfect", "happy", "pleased", "helpful", "good", "love", "fantastic",
    "amazing", "awesome", "satisfied", "delighted"
}

DEFAULT_NEGATIVE_WORDS = {
    "angry", "frustrated", "upset", "terrible", "horrible", "awful",
    "unacceptable", "ridiculous", "disappointed", "annoyed", "furious",
    "worst", "hate", "disgusted", "outraged", "incompetent", "useless"
}

DEFAULT_NEUTRAL_MODIFIERS = {"okay", "fine", "alright", "understand", "see"}

# Default thresholds
DEFAULT_SENTIMENT_THRESHOLDS = {
    "positive": {"min_score": 0.2},
    "negative": {"max_score": -0.2},
    "arc_change": 0.2,
    "peak_count": 3
}


def analyze_segment_sentiment(
    text: str,
    positive_words: set = None,
    negative_words: set = None,
    thresholds: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Analyze sentiment of a single text segment using context-driven configuration.

    Args:
        text: Text to analyze
        positive_words: Set of positive sentiment words (from context)
        negative_words: Set of negative sentiment words (from context)
        thresholds: Sentiment classification thresholds (from context)
    """
    # Use context values or defaults
    positive_words = positive_words or DEFAULT_POSITIVE_WORDS
    negative_words = negative_words or DEFAULT_NEGATIVE_WORDS
    thresholds = thresholds or DEFAULT_SENTIMENT_THRESHOLDS

    words = set(re.findall(r'\b\w+\b', text.lower()))

    positive_count = len(words & positive_words)
    negative_count = len(words & negative_words)
    total_sentiment_words = positive_count + negative_count

    if total_sentiment_words == 0:
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "positive_signals": [],
            "negative_signals": []
        }

    # Calculate score from -1 (negative) to 1 (positive)
    score = (positive_count - negative_count) / max(total_sentiment_words, 1)
    score = max(-1.0, min(1.0, score))

    # Get thresholds from context
    positive_threshold = thresholds.get("positive", {}).get("min_score", 0.2)
    negative_threshold = thresholds.get("negative", {}).get("max_score", -0.2)

    if score > positive_threshold:
        sentiment = "positive"
    elif score < negative_threshold:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "score": round(score, 2),
        "positive_signals": list(words & positive_words),
        "negative_signals": list(words & negative_words)
    }


@register_factory("sentiment_timeline")
async def sentiment_timeline(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze sentiment throughout the conversation (context-driven).

    Context keys used:
        - sentiment_config: Sentiment analysis configuration
            - positive_words: List of positive sentiment words
            - negative_words: List of negative sentiment words
            - thresholds: Classification thresholds
            - peaks: Peak detection settings

    Input:
        diarize.segments: Labeled conversation segments
        config.granularity: "segment" or "overall"
        config.include_peaks: Include sentiment peaks

    Output:
        timeline: Sentiment scores over time
        overall_sentiment: Overall sentiment classification
        average_score: Average sentiment score (-1 to 1)
        sentiment_arc: Narrative arc of sentiment
        peaks: High and low sentiment points
        by_speaker: Sentiment breakdown by speaker
    """
    # Get context configuration
    context = context or input_data.get('context', {})
    sentiment_config = context.get('sentiment_config', {})

    # Build sentiment dictionaries from context
    positive_words = set(sentiment_config.get('positive_words', [])) or DEFAULT_POSITIVE_WORDS
    negative_words = set(sentiment_config.get('negative_words', [])) or DEFAULT_NEGATIVE_WORDS
    thresholds = sentiment_config.get('thresholds', DEFAULT_SENTIMENT_THRESHOLDS)
    peak_config = sentiment_config.get('peaks', {'count': 3})

    logger.info(
        "Sentiment timeline invoked",
        context_driven=bool(context),
        has_custom_words=bool(sentiment_config.get('positive_words'))
    )

    config = input_data.get('config', {})
    diarize_output = input_data.get('diarize', {})
    transcribe_output = input_data.get('transcribe', {})

    # Get segments from diarize or transcribe
    segments = diarize_output.get('segments', [])
    if not segments:
        segments = transcribe_output.get('segments', [])

    if not segments:
        # Fallback to full text
        state = input_data.get('state', {})
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')
        if full_text:
            segments = [{'text': full_text, 'start_time': 0, 'end_time': 0, 'speaker': 'Unknown'}]

    granularity = config.get('granularity', 'segment')
    include_peaks = config.get('include_peaks', True)

    # Analyze each segment
    timeline = []
    by_speaker: Dict[str, List[float]] = {}
    all_scores = []

    for i, segment in enumerate(segments):
        text = segment.get('text', '')
        speaker = segment.get('speaker', 'Unknown')
        start_time = segment.get('start_time', 0)
        end_time = segment.get('end_time', 0)

        # Pass context-driven configuration to sentiment analysis
        sentiment_data = analyze_segment_sentiment(
            text=text,
            positive_words=positive_words,
            negative_words=negative_words,
            thresholds=thresholds
        )

        timeline_entry = {
            "segment_index": i,
            "start_time": start_time,
            "end_time": end_time,
            "speaker": speaker,
            "sentiment": sentiment_data["sentiment"],
            "score": sentiment_data["score"]
        }

        if granularity == 'segment':
            timeline_entry["positive_signals"] = sentiment_data["positive_signals"]
            timeline_entry["negative_signals"] = sentiment_data["negative_signals"]

        timeline.append(timeline_entry)
        all_scores.append(sentiment_data["score"])

        # Track by speaker
        if speaker not in by_speaker:
            by_speaker[speaker] = []
        by_speaker[speaker].append(sentiment_data["score"])

    # Calculate overall metrics using context thresholds
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    positive_threshold = thresholds.get("positive", {}).get("min_score", 0.2)
    negative_threshold = thresholds.get("negative", {}).get("max_score", -0.2)
    arc_change_threshold = thresholds.get("arc_change", 0.2)

    if avg_score > positive_threshold:
        overall_sentiment = "positive"
    elif avg_score < negative_threshold:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"

    # Determine sentiment arc using context threshold
    if len(all_scores) >= 3:
        first_third = sum(all_scores[:len(all_scores)//3]) / (len(all_scores)//3)
        last_third = sum(all_scores[-len(all_scores)//3:]) / (len(all_scores)//3)

        if last_third > first_third + arc_change_threshold:
            sentiment_arc = "improving"
        elif last_third < first_third - arc_change_threshold:
            sentiment_arc = "declining"
        else:
            sentiment_arc = "stable"
    else:
        sentiment_arc = "stable"

    # Find peaks using context-driven peak count
    peak_count = peak_config.get('count', 3)
    peaks = {"positive_peaks": [], "negative_peaks": []}
    if include_peaks and timeline:
        # Find most positive and negative moments
        sorted_by_score = sorted(timeline, key=lambda x: x['score'])

        # Top N positive peaks (from context)
        peaks["positive_peaks"] = [
            {
                "segment_index": t["segment_index"],
                "time": t["start_time"],
                "score": t["score"],
                "speaker": t["speaker"]
            }
            for t in sorted_by_score[-peak_count:] if t["score"] > 0
        ]

        # Top N negative peaks (from context)
        peaks["negative_peaks"] = [
            {
                "segment_index": t["segment_index"],
                "time": t["start_time"],
                "score": t["score"],
                "speaker": t["speaker"]
            }
            for t in sorted_by_score[:peak_count] if t["score"] < 0
        ]

    # Calculate per-speaker averages using context thresholds
    speaker_sentiment = {
        speaker: {
            "average_score": round(sum(scores) / len(scores), 2),
            "sentiment": "positive" if sum(scores)/len(scores) > positive_threshold else ("negative" if sum(scores)/len(scores) < negative_threshold else "neutral"),
            "segment_count": len(scores)
        }
        for speaker, scores in by_speaker.items()
    }

    # Build rule-based result
    rule_based_result = {
        "timeline": timeline,
        "overall_sentiment": overall_sentiment,
        "average_score": round(avg_score, 2),
        "sentiment_arc": sentiment_arc,
        "peaks": peaks,
        "by_speaker": speaker_sentiment,
        "segment_count": len(timeline),
        "ai_enhanced": False,
        "context_driven": bool(context),
        "factory_id": "sentiment_timeline",
        "factory_version": "2.0.0",
        "context_keys_used": ["sentiment_config"]
    }

    # Try AI-enhanced sentiment analysis if enabled
    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED
    full_text = ""
    for seg in segments:
        full_text += f"{seg.get('speaker', 'Unknown')}: {seg.get('text', '')}\n"

    if use_ai and full_text:
        try:
            ai_result = await _analyze_sentiment_with_ai(full_text)
            if ai_result:
                # AI provides nuanced sentiment understanding
                rule_based_result["overall_sentiment"] = ai_result.get("overall_sentiment", overall_sentiment)
                rule_based_result["average_score"] = ai_result.get("average_score", avg_score)
                rule_based_result["sentiment_arc"] = ai_result.get("sentiment_arc", sentiment_arc)

                # Merge AI-detected emotional peaks
                if ai_result.get("emotional_peaks"):
                    rule_based_result["emotional_peaks"] = ai_result["emotional_peaks"]

                # AI-enhanced speaker sentiment
                ai_by_speaker = ai_result.get("by_speaker", {})
                for speaker, ai_data in ai_by_speaker.items():
                    if speaker in rule_based_result["by_speaker"]:
                        rule_based_result["by_speaker"][speaker]["ai_sentiment"] = ai_data.get("sentiment")
                        rule_based_result["by_speaker"][speaker]["ai_score"] = ai_data.get("average_score")

                rule_based_result["ai_enhanced"] = True
                rule_based_result["key_observations"] = ai_result.get("key_observations", [])

                logger.info(
                    "AI-enhanced sentiment analysis completed",
                    overall=rule_based_result["overall_sentiment"],
                    arc=rule_based_result["sentiment_arc"]
                )
        except Exception as e:
            logger.warning("AI sentiment analysis failed, using rule-based", error=str(e))

    return rule_based_result


async def _analyze_sentiment_with_ai(transcript: str) -> Dict[str, Any]:
    """Analyze sentiment using Claude for nuanced understanding."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_model_router()

    result = await claude.analyze_conversation(
        transcript=transcript,
        analysis_type="sentiment",
        context=None
    )

    if result.get("success") and result.get("parsed"):
        return result["parsed"]

    return None
