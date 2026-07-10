"""
Competitor Mentions Detection Action
Track and analyze competitor references in sales conversations

Supports both Lambda and Small Factory pattern
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog
import re

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

try:
    from services.bedrock_claude import get_bedrock_claude_service
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


# Generic competitor reference patterns
COMPETITOR_PATTERNS = {
    "direct_mention": [
        r"(using|use|have|with|from) ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)",
        r"(competitor|another vendor|other solution|alternative)",
        r"(they|the other company|that vendor) (said|offer|have|told)",
    ],
    "comparison_request": [
        r"(how|why) (are you|is this|do you) (better|different|compare)",
        r"(what|how) (makes|sets) you (apart|different)",
        r"(vs|versus|compared to|against)",
        r"(advantage|benefit) over",
    ],
    "switching_concern": [
        r"(switching|migration|transition) (cost|effort|pain)",
        r"(locked|committed|contract) (into|with)",
        r"(already|currently) (invested|paying|using)",
        r"(change|switch) (from|away from)",
    ],
    "feature_comparison": [
        r"(do you|can you|does it) (have|support|offer|do)",
        r"(they|competitor) (has|have|can|does)",
        r"(feature|capability|functionality) (that|which)",
        r"(missing|lacking|doesn't have)",
    ]
}

# Common competitor sentiment
COMPETITOR_SENTIMENT = {
    "positive_about_competitor": [
        r"(really |very )?(like|love|happy with|satisfied)",
        r"(works|working) (well|great|fine)",
        r"(good|great) (relationship|experience)",
    ],
    "negative_about_competitor": [
        r"(frustrated|unhappy|disappointed) with",
        r"(problems|issues|challenges) with",
        r"(looking|want) to (change|switch|move)",
        r"(doesn't|does not|can't|cannot) (work|scale|support)",
    ],
    "neutral_about_competitor": [
        r"(evaluating|considering|looking at) (options|alternatives)",
        r"(gathering|collecting) (information|proposals)",
    ]
}


@apex_action(ApexActionSchema(
    name="competitor_mentions",
    description="Track competitor references in sales conversations",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Competitor tracking parameters")
        .add_string("transcript", "Conversation transcript", required=True)
        .add_array("known_competitors", "List of known competitor names", required=False)
        .add_string("our_company", "Our company name for exclusion", required=False),
    output_schema=ActionOutputSchema(description="Competitor analysis")
        .add_array("mentions", "All competitor mentions")
        .add_object("competitive_landscape", "Analysis of competitive situation")
        .add_string("competitor_sentiment", "Prospect sentiment toward competitors")
        .add_array("battlecard_triggers", "Relevant battlecard topics")
        .add_number("competitive_threat_level", "Threat level 0-100")
))
def competitor_mentions(
    transcript: str,
    known_competitors: List[str] = None,
    our_company: str = None
) -> dict:
    """
    Detect and analyze competitor mentions

    Args:
        transcript: Conversation transcript
        known_competitors: Known competitor names
        our_company: Our company name to exclude

    Returns:
        Competitor mention analysis
    """
    known_competitors = known_competitors or []

    result = {
        "mentions": [],
        "competitive_landscape": {
            "competitors_mentioned": [],
            "comparison_topics": [],
            "switching_barriers": []
        },
        "competitor_sentiment": "neutral",
        "sentiment_details": {},
        "battlecard_triggers": [],
        "competitive_threat_level": 0,
        "win_against_competitor_tips": [],
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False
    }

    if not transcript:
        return result

    transcript_lower = transcript.lower()

    # Detect known competitor mentions
    for competitor in known_competitors:
        competitor_lower = competitor.lower()
        if competitor_lower in transcript_lower:
            # Find all mentions
            pattern = re.compile(re.escape(competitor_lower), re.IGNORECASE)
            for match in pattern.finditer(transcript_lower):
                start = max(0, match.start() - 60)
                end = min(len(transcript), match.end() + 60)
                context = transcript[start:end]

                result["mentions"].append({
                    "competitor": competitor,
                    "context": f"...{context}...",
                    "position_percent": round((match.start() / len(transcript)) * 100),
                    "mention_type": "direct"
                })

            if competitor not in result["competitive_landscape"]["competitors_mentioned"]:
                result["competitive_landscape"]["competitors_mentioned"].append(competitor)

    # Detect generic competitor patterns
    for pattern_type, patterns in COMPETITOR_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, transcript_lower)
            for match in matches:
                start = max(0, match.start() - 40)
                end = min(len(transcript), match.end() + 40)
                context = transcript[start:end]

                # Skip if it's our company
                if our_company and our_company.lower() in context.lower():
                    continue

                mention = {
                    "matched_text": match.group(),
                    "context": f"...{context}...",
                    "position_percent": round((match.start() / len(transcript)) * 100),
                    "mention_type": pattern_type
                }

                if pattern_type == "comparison_request":
                    result["competitive_landscape"]["comparison_topics"].append(match.group())
                    result["battlecard_triggers"].append({
                        "trigger": match.group(),
                        "topic": "competitive_comparison",
                        "suggested_response": "Use differentiation talking points"
                    })
                elif pattern_type == "switching_concern":
                    result["competitive_landscape"]["switching_barriers"].append(match.group())

                result["mentions"].append(mention)

    # Analyze competitor sentiment
    sentiment_scores = {"positive": 0, "negative": 0, "neutral": 0}

    for sentiment, patterns in COMPETITOR_SENTIMENT.items():
        for pattern in patterns:
            matches = re.findall(pattern, transcript_lower)
            if matches:
                sentiment_key = sentiment.replace("_about_competitor", "")
                sentiment_scores[sentiment_key] += len(matches)

    # Determine overall sentiment
    if sentiment_scores["negative"] > sentiment_scores["positive"]:
        result["competitor_sentiment"] = "negative_toward_competitor"
        result["win_against_competitor_tips"].append("Prospect is frustrated with current solution - emphasize reliability and support")
    elif sentiment_scores["positive"] > sentiment_scores["negative"]:
        result["competitor_sentiment"] = "positive_toward_competitor"
        result["win_against_competitor_tips"].append("Prospect likes current solution - focus on incremental improvements and lower switching risk")
    else:
        result["competitor_sentiment"] = "neutral"
        result["win_against_competitor_tips"].append("Prospect is evaluating options - provide strong ROI case and references")

    result["sentiment_details"] = sentiment_scores

    # Calculate competitive threat level
    threat_factors = {
        "competitor_mentions": len(result["mentions"]) * 10,
        "positive_sentiment": sentiment_scores["positive"] * 15,
        "switching_barriers": len(result["competitive_landscape"]["switching_barriers"]) * 20,
        "comparison_requests": len(result["competitive_landscape"]["comparison_topics"]) * 5
    }

    threat_reducers = {
        "negative_sentiment": sentiment_scores["negative"] * 10
    }

    threat_level = sum(threat_factors.values()) - sum(threat_reducers.values())
    result["competitive_threat_level"] = max(0, min(100, threat_level))

    # Generate battlecard triggers
    if result["competitive_threat_level"] > 50:
        result["battlecard_triggers"].append({
            "trigger": "high_competitive_threat",
            "topic": "competitive_displacement",
            "suggested_response": "Deploy competitive displacement playbook"
        })

    return result


class CompetitorMentionsAction(ApexActionBase):
    name = "competitor_mentions"
    description = "Track competitor references"
    category = "sales_intelligence"
    industry = "sales_ai"

    def execute(self, **kwargs) -> dict:
        return competitor_mentions(**kwargs)


@register_factory("competitor_mentions")
async def competitor_mentions_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Small Factory handler for competitor tracking"""
    logger.info("Competitor mentions factory invoked")

    result = competitor_mentions(
        transcript=input_data.get("transcript", ""),
        known_competitors=input_data.get("known_competitors", []),
        our_company=input_data.get("our_company")
    )

    if input_data.get("use_ai", True) and CLAUDE_ENABLED:
        try:
            claude = get_bedrock_claude_service()
            ai_response = await claude.analyze_conversation(
                transcript=input_data.get("transcript", "")[:2000],
                analysis_type="custom",
                context={
                    "custom_prompt": "Identify all competitor mentions, analyze competitive dynamics, and suggest winning strategies. Format as JSON."
                }
            )
            if ai_response:
                result["ai_insights"] = ai_response
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI competitor analysis failed", error=str(e))

    result["factory_id"] = "competitor_mentions"
    result["factory_version"] = "1.0.0"
    return result


def handler(event, context):
    return competitor_mentions(**event)
