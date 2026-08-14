"""
Sales Coaching Action
Generate personalized coaching recommendations for sales reps

Supports both Lambda and Small Factory pattern
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog

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
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


# Coaching areas and skill modules
COACHING_AREAS = {
    "discovery": {
        "skills": ["asking_questions", "active_listening", "pain_identification"],
        "training_modules": ["Discovery Mastery", "SPIN Selling", "Consultative Selling"]
    },
    "objection_handling": {
        "skills": ["acknowledge_concern", "reframe", "provide_evidence"],
        "training_modules": ["Objection Handling Workshop", "Competitive Positioning"]
    },
    "value_articulation": {
        "skills": ["roi_presentation", "storytelling", "business_case"],
        "training_modules": ["Value Selling", "ROI Calculator Training", "Executive Presentations"]
    },
    "closing": {
        "skills": ["trial_close", "creating_urgency", "next_steps"],
        "training_modules": ["Closing Techniques", "Negotiation Skills"]
    },
    "rapport_building": {
        "skills": ["mirroring", "empathy", "personalization"],
        "training_modules": ["Building Trust", "Emotional Intelligence for Sales"]
    },
    "competitor_positioning": {
        "skills": ["differentiation", "competitive_intelligence", "displacement"],
        "training_modules": ["Competitive Battlecards", "Win Against Competition"]
    },
    "engagement": {
        "skills": ["energy_management", "curiosity", "enthusiasm"],
        "training_modules": ["Presentation Skills", "Vocal Dynamics"]
    }
}

# Coaching triggers based on analysis results
COACHING_TRIGGERS = {
    "low_engagement": {
        "area": "engagement",
        "observation": "Prospect engagement dropped during the conversation",
        "recommendations": [
            "Ask more open-ended questions to increase participation",
            "Use the prospect's name more frequently",
            "Reference specific details from their business"
        ]
    },
    "unhandled_objections": {
        "area": "objection_handling",
        "observation": "Objections were raised but not fully addressed",
        "recommendations": [
            "Acknowledge the concern before responding",
            "Use the 'Feel, Felt, Found' technique",
            "Provide specific evidence or case studies"
        ]
    },
    "weak_discovery": {
        "area": "discovery",
        "observation": "Limited pain points or needs uncovered",
        "recommendations": [
            "Use more 'why' and 'what' questions",
            "Dig deeper into initial responses",
            "Map pain to business impact"
        ]
    },
    "missed_buying_signals": {
        "area": "closing",
        "observation": "Buying signals detected but not acted upon",
        "recommendations": [
            "Listen for timeline and budget questions",
            "Use trial closes when interest peaks",
            "Propose specific next steps when signals appear"
        ]
    },
    "competitor_threat": {
        "area": "competitor_positioning",
        "observation": "Competitor mentioned with positive sentiment",
        "recommendations": [
            "Focus on unique differentiators",
            "Share competitive win stories",
            "Address switching concerns proactively"
        ]
    },
    "negative_emotion": {
        "area": "rapport_building",
        "observation": "Prospect showed signs of frustration or skepticism",
        "recommendations": [
            "Slow down and validate their perspective",
            "Ask clarifying questions to understand concerns",
            "Share relevant success stories to build credibility"
        ]
    }
}


@apex_action(ApexActionSchema(
    name="sales_coaching",
    description="Generate personalized sales coaching recommendations",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Coaching parameters")
        .add_object("emotion_analysis", "Emotion analysis results", required=False)
        .add_object("buying_signals", "Buying signal results", required=False)
        .add_object("objection_analysis", "Objection detection results", required=False)
        .add_object("competitor_analysis", "Competitor tracking results", required=False)
        .add_object("deal_intelligence", "Deal intelligence results", required=False)
        .add_string("transcript", "Conversation transcript", required=False)
        .add_string("rep_id", "Sales rep identifier", required=False),
    output_schema=ActionOutputSchema(description="Coaching recommendations")
        .add_array("coaching_tips", "Prioritized coaching recommendations")
        .add_array("strengths", "Areas of strength identified")
        .add_array("improvement_areas", "Areas needing improvement")
        .add_array("training_recommendations", "Suggested training modules")
        .add_object("conversation_score", "Call performance score")
        .add_object("skill_assessment", "Skill-level assessment")
))
def sales_coaching(
    emotion_analysis: Dict = None,
    buying_signals: Dict = None,
    objection_analysis: Dict = None,
    competitor_analysis: Dict = None,
    deal_intelligence: Dict = None,
    transcript: str = None,
    rep_id: str = None
) -> dict:
    """
    Generate personalized coaching recommendations

    Args:
        emotion_analysis: Emotion analysis results
        buying_signals: Buying signal results
        objection_analysis: Objection detection results
        competitor_analysis: Competitor tracking results
        deal_intelligence: Deal intelligence results
        transcript: Conversation transcript
        rep_id: Sales rep identifier

    Returns:
        Comprehensive coaching recommendations
    """
    emotion_analysis = emotion_analysis or {}
    buying_signals = buying_signals or {}
    objection_analysis = objection_analysis or {}
    competitor_analysis = competitor_analysis or {}
    deal_intelligence = deal_intelligence or {}

    result = {
        "coaching_tips": [],
        "strengths": [],
        "improvement_areas": [],
        "training_recommendations": [],
        "conversation_score": {
            "overall": 0,
            "components": {}
        },
        "skill_assessment": {},
        "priority_actions": [],
        "rep_id": rep_id,
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False
    }

    # Analyze each area and generate coaching
    triggered_areas = set()

    # Check emotion-based triggers
    engagement = emotion_analysis.get("engagement_score", 50)
    if engagement < 40:
        triggered_areas.add("low_engagement")
    elif engagement >= 70:
        result["strengths"].append({
            "area": "engagement",
            "observation": "Maintained high prospect engagement throughout the conversation"
        })

    dominant_emotion = emotion_analysis.get("prospect_emotions", {}).get("dominant_emotion", "neutral")
    if dominant_emotion in ["frustration", "skepticism", "disengagement"]:
        triggered_areas.add("negative_emotion")

    # Check objection handling
    unhandled = objection_analysis.get("unhandled_objections", [])
    if unhandled:
        triggered_areas.add("unhandled_objections")
    elif objection_analysis.get("objections") and not unhandled:
        result["strengths"].append({
            "area": "objection_handling",
            "observation": "Effectively addressed prospect objections during the conversation"
        })

    # Check buying signals
    buying_intent = buying_signals.get("buying_intent_score", 0)
    if buying_intent >= 60 and deal_intelligence.get("recommended_stage") not in ["proposal", "negotiation"]:
        triggered_areas.add("missed_buying_signals")

    if buying_intent < 30:
        triggered_areas.add("weak_discovery")

    # Check competitive situation
    competitive_threat = competitor_analysis.get("competitive_threat_level", 0)
    if competitive_threat >= 50:
        triggered_areas.add("competitor_threat")
    elif competitor_analysis.get("competitor_sentiment") == "negative_toward_competitor":
        result["strengths"].append({
            "area": "competitive_positioning",
            "observation": "Successfully highlighted competitive advantages"
        })

    # Generate coaching tips from triggers
    priority_order = ["unhandled_objections", "competitor_threat", "low_engagement",
                      "negative_emotion", "missed_buying_signals", "weak_discovery"]

    for trigger in priority_order:
        if trigger in triggered_areas:
            coaching = COACHING_TRIGGERS[trigger]
            result["coaching_tips"].append({
                "area": coaching["area"],
                "priority": "high" if trigger in ["unhandled_objections", "competitor_threat"] else "medium",
                "observation": coaching["observation"],
                "recommendations": coaching["recommendations"],
                "training_modules": COACHING_AREAS[coaching["area"]]["training_modules"]
            })
            result["improvement_areas"].append({
                "area": coaching["area"],
                "trigger": trigger
            })

            # Add training recommendations
            for module in COACHING_AREAS[coaching["area"]]["training_modules"][:1]:
                if module not in [t["module"] for t in result["training_recommendations"]]:
                    result["training_recommendations"].append({
                        "module": module,
                        "priority": "high" if len(result["training_recommendations"]) == 0 else "medium",
                        "related_area": coaching["area"]
                    })

    # Calculate conversation score
    score_components = {
        "engagement": min(100, engagement + 20) if engagement >= 50 else engagement,
        "objection_handling": 100 - (len(unhandled) * 20),
        "buying_advancement": buying_intent,
        "competitive_positioning": 100 - competitive_threat
    }

    for component, score in score_components.items():
        score_components[component] = max(0, min(100, score))

    overall_score = sum(score_components.values()) / len(score_components)
    result["conversation_score"]["overall"] = round(overall_score)
    result["conversation_score"]["components"] = score_components

    # Skill assessment
    for area, config in COACHING_AREAS.items():
        area_score = 50  # Base score
        if area in [s["area"] for s in result["strengths"]]:
            area_score = 80
        elif area in [i["area"] for i in result["improvement_areas"]]:
            area_score = 35

        result["skill_assessment"][area] = {
            "score": area_score,
            "level": "proficient" if area_score >= 70 else "developing" if area_score >= 50 else "needs_focus",
            "skills": config["skills"]
        }

    # Generate priority actions
    if result["improvement_areas"]:
        top_area = result["improvement_areas"][0]
        result["priority_actions"] = [
            {
                "action": f"Focus on {top_area['area']} in next call",
                "specific_tip": result["coaching_tips"][0]["recommendations"][0] if result["coaching_tips"] else "",
                "follow_up": "Manager 1:1 review recommended" if overall_score < 50 else "Self-review suggested"
            }
        ]

    return result


class SalesCoachingAction(ApexActionBase):
    name = "sales_coaching"
    description = "Generate sales coaching recommendations"
    category = "sales_intelligence"
    industry = "sales_ai"

    def execute(self, **kwargs) -> dict:
        return sales_coaching(**kwargs)


@register_factory("sales_coaching")
async def sales_coaching_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Small Factory handler for sales coaching"""
    logger.info("Sales coaching factory invoked")

    result = sales_coaching(
        emotion_analysis=input_data.get("emotion_analysis"),
        buying_signals=input_data.get("buying_signals"),
        objection_analysis=input_data.get("objection_analysis"),
        competitor_analysis=input_data.get("competitor_analysis"),
        deal_intelligence=input_data.get("deal_intelligence"),
        transcript=input_data.get("transcript"),
        rep_id=input_data.get("rep_id")
    )

    if input_data.get("use_ai", True) and CLAUDE_ENABLED and input_data.get("transcript"):
        try:
            claude = get_model_router()
            ai_response = await claude.analyze_conversation(
                transcript=input_data.get("transcript", "")[:2000],
                analysis_type="coaching",
                context={
                    "conversation_score": result["conversation_score"]["overall"],
                    "improvement_areas": [a["area"] for a in result["improvement_areas"]]
                }
            )
            if ai_response:
                result["ai_coaching"] = ai_response
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI coaching analysis failed", error=str(e))

    result["factory_id"] = "sales_coaching"
    result["factory_version"] = "1.0.0"
    return result


def handler(event, context):
    return sales_coaching(**event)
