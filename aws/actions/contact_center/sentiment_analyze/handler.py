"""
Sentiment Analysis Action
Analyze customer sentiment from call transcripts and interactions
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import re

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Sentiment indicators
POSITIVE_WORDS = [
    "thank", "thanks", "great", "excellent", "perfect", "wonderful", "helpful",
    "appreciate", "happy", "satisfied", "resolved", "fantastic", "amazing"
]

NEGATIVE_WORDS = [
    "frustrated", "angry", "upset", "terrible", "awful", "horrible", "worst",
    "unacceptable", "ridiculous", "disappointed", "annoyed", "unhappy", "hate"
]

ESCALATION_PHRASES = [
    "speak to manager", "speak to supervisor", "escalate", "file complaint",
    "cancel my account", "close my account", "lawyer", "attorney", "sue",
    "report to", "better business bureau", "social media"
]


@apex_action(ApexActionSchema(
    name="sentiment_analyze",
    description="Analyze customer sentiment from call transcripts and interactions",
    category="analytics",
    industry="contact_center",
    input_schema=ActionInputSchema(description="Sentiment analysis parameters")
        .add_string("interaction_id", "Interaction/call ID", required=True)
        .add_array("utterances", "List of utterances with speaker and text", required=True)
        .add_string("channel", "Channel: voice, chat, email", required=False),
    output_schema=ActionOutputSchema(description="Sentiment analysis result")
        .add_string("overall_sentiment", "Overall sentiment: positive, negative, neutral")
        .add_number("sentiment_score", "Sentiment score -1 to 1")
        .add_array("sentiment_timeline", "Sentiment changes throughout interaction")
        .add_array("key_phrases", "Key positive/negative phrases detected")
        .add_boolean("escalation_risk", "Whether escalation risk is detected")
        .add_object("speaker_sentiment", "Sentiment breakdown by speaker")
))
def sentiment_analyze(
    interaction_id: str,
    utterances: List[Dict],
    channel: str = "voice"
) -> dict:
    """
    Analyze sentiment in interaction

    Args:
        interaction_id: Interaction ID
        utterances: List of utterances
        channel: Communication channel

    Returns:
        Sentiment analysis results
    """
    result = {
        "interaction_id": interaction_id,
        "channel": channel,
        "overall_sentiment": "neutral",
        "sentiment_score": 0,
        "sentiment_timeline": [],
        "key_phrases": [],
        "escalation_risk": False,
        "speaker_sentiment": {},
        "analysis_date": datetime.now().isoformat()
    }

    speaker_scores = {}
    timeline = []
    all_positive = 0
    all_negative = 0

    for i, utterance in enumerate(utterances):
        speaker = utterance.get("speaker", "unknown")
        text = utterance.get("text", "").lower()

        # Count sentiment words
        positive_count = sum(1 for word in POSITIVE_WORDS if word in text)
        negative_count = sum(1 for word in NEGATIVE_WORDS if word in text)

        # Calculate utterance score
        total_words = len(text.split())
        if total_words > 0:
            utterance_score = (positive_count - negative_count) / max(total_words, 10)
        else:
            utterance_score = 0

        # Track by speaker
        if speaker not in speaker_scores:
            speaker_scores[speaker] = {"positive": 0, "negative": 0, "total": 0}
        speaker_scores[speaker]["positive"] += positive_count
        speaker_scores[speaker]["negative"] += negative_count
        speaker_scores[speaker]["total"] += 1

        all_positive += positive_count
        all_negative += negative_count

        # Add to timeline
        if positive_count > 0 or negative_count > 0:
            timeline.append({
                "position": i + 1,
                "speaker": speaker,
                "score": round(utterance_score, 3),
                "sentiment": "positive" if utterance_score > 0 else "negative" if utterance_score < 0 else "neutral"
            })

        # Extract key phrases
        for word in POSITIVE_WORDS:
            if word in text:
                result["key_phrases"].append({
                    "phrase": word,
                    "sentiment": "positive",
                    "speaker": speaker,
                    "position": i + 1
                })

        for word in NEGATIVE_WORDS:
            if word in text:
                result["key_phrases"].append({
                    "phrase": word,
                    "sentiment": "negative",
                    "speaker": speaker,
                    "position": i + 1
                })

        # Check for escalation
        for phrase in ESCALATION_PHRASES:
            if phrase in text:
                result["escalation_risk"] = True
                result["key_phrases"].append({
                    "phrase": phrase,
                    "sentiment": "escalation",
                    "speaker": speaker,
                    "position": i + 1
                })

    # Calculate overall score
    total = all_positive + all_negative
    if total > 0:
        result["sentiment_score"] = round((all_positive - all_negative) / total, 3)

    # Determine overall sentiment
    if result["sentiment_score"] > 0.2:
        result["overall_sentiment"] = "positive"
    elif result["sentiment_score"] < -0.2:
        result["overall_sentiment"] = "negative"
    else:
        result["overall_sentiment"] = "neutral"

    # Calculate speaker sentiment
    for speaker, scores in speaker_scores.items():
        total_speaker = scores["positive"] + scores["negative"]
        if total_speaker > 0:
            speaker_score = (scores["positive"] - scores["negative"]) / total_speaker
        else:
            speaker_score = 0

        result["speaker_sentiment"][speaker] = {
            "score": round(speaker_score, 3),
            "sentiment": "positive" if speaker_score > 0.2 else "negative" if speaker_score < -0.2 else "neutral",
            "positive_count": scores["positive"],
            "negative_count": scores["negative"],
            "utterance_count": scores["total"]
        }

    result["sentiment_timeline"] = timeline

    return result


class SentimentAnalyzeAction(ApexActionBase):
    """Sentiment Analysis Action (class-based)"""

    name = "sentiment_analyze"
    description = "Analyze customer sentiment"
    category = "analytics"
    industry = "contact_center"

    def execute(self, **kwargs) -> dict:
        return sentiment_analyze(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return sentiment_analyze(**event)
