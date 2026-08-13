"""
Sales Summary Action
Generate comprehensive sales call summary with action items and CRM updates

Supports both Lambda and Small Factory pattern
"""

import os
from datetime import datetime, timedelta
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
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()


@apex_action(ApexActionSchema(
    name="sales_summary",
    description="Generate comprehensive sales call summary",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Summary parameters")
        .add_string("transcript", "Conversation transcript", required=True)
        .add_object("emotion_analysis", "Emotion analysis results", required=False)
        .add_object("buying_signals", "Buying signal results", required=False)
        .add_object("objection_analysis", "Objection detection results", required=False)
        .add_object("deal_intelligence", "Deal intelligence results", required=False)
        .add_object("deal_context", "CRM deal context", required=False),
    output_schema=ActionOutputSchema(description="Sales call summary")
        .add_string("executive_summary", "Brief executive summary")
        .add_array("key_discussion_points", "Main topics discussed")
        .add_array("action_items", "Follow-up action items")
        .add_object("crm_update", "Suggested CRM field updates")
        .add_string("next_meeting_agenda", "Suggested agenda for next meeting")
        .add_object("deal_snapshot", "Current deal status snapshot")
))
def sales_summary(
    transcript: str,
    emotion_analysis: Dict = None,
    buying_signals: Dict = None,
    objection_analysis: Dict = None,
    deal_intelligence: Dict = None,
    deal_context: Dict = None
) -> dict:
    """
    Generate comprehensive sales call summary

    Args:
        transcript: Conversation transcript
        emotion_analysis: Emotion analysis results
        buying_signals: Buying signal results
        objection_analysis: Objection detection results
        deal_intelligence: Deal intelligence results
        deal_context: CRM deal context

    Returns:
        Complete call summary with CRM updates
    """
    emotion_analysis = emotion_analysis or {}
    buying_signals = buying_signals or {}
    objection_analysis = objection_analysis or {}
    deal_intelligence = deal_intelligence or {}
    deal_context = deal_context or {}

    result = {
        "executive_summary": "",
        "key_discussion_points": [],
        "action_items": [],
        "crm_update": {},
        "next_meeting_agenda": "",
        "deal_snapshot": {},
        "call_metadata": {},
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False
    }

    if not transcript:
        result["executive_summary"] = "No transcript provided for analysis."
        return result

    # Generate executive summary
    result["executive_summary"] = _generate_executive_summary(
        transcript, emotion_analysis, buying_signals, deal_intelligence
    )

    # Extract key discussion points
    result["key_discussion_points"] = _extract_discussion_points(
        transcript, buying_signals, objection_analysis
    )

    # Generate action items
    result["action_items"] = _generate_action_items(
        buying_signals, objection_analysis, deal_intelligence
    )

    # Generate CRM update suggestions
    result["crm_update"] = _generate_crm_update(
        deal_intelligence, buying_signals, objection_analysis, deal_context
    )

    # Generate next meeting agenda
    result["next_meeting_agenda"] = _generate_next_agenda(
        result["action_items"], objection_analysis, deal_intelligence
    )

    # Create deal snapshot
    result["deal_snapshot"] = {
        "win_probability": deal_intelligence.get("win_probability", 0),
        "deal_health": deal_intelligence.get("deal_health", "unknown"),
        "recommended_stage": deal_intelligence.get("recommended_stage", "unknown"),
        "engagement_level": emotion_analysis.get("engagement_score", 0),
        "buying_intent": buying_signals.get("buying_intent_score", 0),
        "open_objections": len(objection_analysis.get("unhandled_objections", [])),
        "trend": deal_intelligence.get("trend", "stable")
    }

    # Call metadata
    word_count = len(transcript.split())
    result["call_metadata"] = {
        "word_count": word_count,
        "estimated_duration_minutes": round(word_count / 150),  # ~150 wpm
        "summary_generated_at": datetime.now().isoformat()
    }

    return result


def _generate_executive_summary(
    transcript: str,
    emotion: Dict,
    buying: Dict,
    deal_intel: Dict
) -> str:
    """Generate brief executive summary"""
    # Extract key metrics
    engagement = emotion.get("engagement_score", 50)
    buying_intent = buying.get("buying_intent_score", 0)
    deal_health = deal_intel.get("deal_health", "unknown")
    win_prob = deal_intel.get("win_probability", 0)

    # Build summary
    engagement_desc = "high" if engagement >= 70 else "moderate" if engagement >= 40 else "low"
    intent_desc = "strong" if buying_intent >= 60 else "moderate" if buying_intent >= 30 else "weak"

    summary_parts = [
        f"Sales call completed with {engagement_desc} prospect engagement.",
        f"Buying intent is {intent_desc} ({buying_intent}%).",
        f"Deal health: {deal_health} with {win_prob}% win probability."
    ]

    # Add key signals
    if buying.get("signals_detected"):
        signal_count = len(buying["signals_detected"])
        summary_parts.append(f"Detected {signal_count} buying signals.")

    if buying.get("negative_signals"):
        neg_count = len(buying["negative_signals"])
        summary_parts.append(f"Note: {neg_count} concern indicators identified.")

    return " ".join(summary_parts)


def _extract_discussion_points(
    transcript: str,
    buying: Dict,
    objections: Dict
) -> List[Dict]:
    """Extract key discussion points from conversation"""
    points = []

    # Add points from buying signal categories
    signal_breakdown = buying.get("signal_breakdown", {})
    for category, data in signal_breakdown.items():
        if data.get("count", 0) > 0:
            points.append({
                "topic": category.replace("_", " ").title(),
                "type": "buying_signal",
                "detail": f"Discussed {data['count']} times",
                "importance": "high" if category in ["next_steps", "budget_discussion"] else "medium"
            })

    # Add points from objections
    objection_summary = objections.get("objection_summary", {})
    for category, data in objection_summary.items():
        points.append({
            "topic": f"{category.replace('_', ' ').title()} Objection",
            "type": "objection",
            "detail": data.get("primary_strategy", ""),
            "importance": "high" if data.get("severity") == "high" else "medium"
        })

    # Add generic discussion patterns from transcript
    discussion_patterns = [
        (r"pricing|cost|budget|price", "Pricing Discussion"),
        (r"timeline|when|deadline|schedule", "Timeline Discussion"),
        (r"feature|capability|functionality", "Feature Discussion"),
        (r"integration|connect|api", "Integration Discussion"),
        (r"support|training|onboarding", "Support Discussion"),
        (r"contract|terms|agreement", "Contract Discussion")
    ]

    transcript_lower = transcript.lower()
    for pattern, topic in discussion_patterns:
        if re.search(pattern, transcript_lower):
            if topic not in [p["topic"] for p in points]:
                points.append({
                    "topic": topic,
                    "type": "general",
                    "detail": "Topic discussed during call",
                    "importance": "medium"
                })

    # Sort by importance
    importance_order = {"high": 0, "medium": 1, "low": 2}
    points.sort(key=lambda x: importance_order.get(x["importance"], 2))

    return points[:8]


def _generate_action_items(
    buying: Dict,
    objections: Dict,
    deal_intel: Dict
) -> List[Dict]:
    """Generate action items from call analysis"""
    items = []

    # From deal intelligence next actions
    for action in deal_intel.get("next_best_actions", [])[:3]:
        items.append({
            "action": action.get("description", action.get("action", "")),
            "priority": action.get("priority", "medium"),
            "owner": action.get("owner", "Sales Rep"),
            "due": "48 hours" if action.get("priority") == "high" else "1 week",
            "source": "deal_intelligence"
        })

    # From objection handling
    for rec in objections.get("handling_recommendations", [])[:2]:
        items.append({
            "action": f"Address {rec['objection_category']} objection: {rec['recommended_response']}",
            "priority": rec.get("priority", "medium"),
            "owner": "Sales Rep",
            "due": "Next call",
            "source": "objection_handling"
        })

    # From buying signals
    for rec in buying.get("recommended_actions", [])[:2]:
        if rec.get("action") not in [i["action"] for i in items]:
            items.append({
                "action": rec.get("description", ""),
                "priority": rec.get("priority", "medium"),
                "owner": "Sales Rep",
                "due": rec.get("timing", "1 week"),
                "source": "buying_signals"
            })

    # Default action if none generated
    if not items:
        items.append({
            "action": "Send follow-up email with call summary",
            "priority": "medium",
            "owner": "Sales Rep",
            "due": "24 hours",
            "source": "default"
        })

    return items[:6]


def _generate_crm_update(
    deal_intel: Dict,
    buying: Dict,
    objections: Dict,
    deal_context: Dict
) -> Dict:
    """Generate CRM field update suggestions"""
    update = {
        "suggested_updates": [],
        "field_values": {}
    }

    # Stage update
    recommended_stage = deal_intel.get("recommended_stage", "")
    current_stage = deal_context.get("stage", "")
    if recommended_stage and recommended_stage != current_stage:
        update["suggested_updates"].append({
            "field": "deal_stage",
            "current_value": current_stage,
            "suggested_value": recommended_stage,
            "reason": "Based on buying signals detected in conversation"
        })
        update["field_values"]["deal_stage"] = recommended_stage

    # Win probability
    win_prob = deal_intel.get("win_probability", 0)
    update["field_values"]["win_probability"] = win_prob
    update["suggested_updates"].append({
        "field": "win_probability",
        "suggested_value": f"{win_prob}%",
        "reason": "Calculated from conversation analysis"
    })

    # Next step
    if buying.get("recommended_actions"):
        next_action = buying["recommended_actions"][0]
        update["field_values"]["next_step"] = next_action.get("description", "")
        update["suggested_updates"].append({
            "field": "next_step",
            "suggested_value": next_action.get("description", ""),
            "reason": "Based on conversation signals"
        })

    # Notes
    notes_parts = []
    if objections.get("objections"):
        obj_categories = list(set([o["category"] for o in objections["objections"]]))
        notes_parts.append(f"Objections raised: {', '.join(obj_categories)}")
    if buying.get("signal_breakdown"):
        signal_cats = list(buying["signal_breakdown"].keys())[:3]
        notes_parts.append(f"Buying signals: {', '.join(signal_cats)}")

    if notes_parts:
        update["field_values"]["call_notes"] = "; ".join(notes_parts)

    # Last activity date
    update["field_values"]["last_activity_date"] = datetime.now().strftime("%Y-%m-%d")

    return update


def _generate_next_agenda(
    action_items: List,
    objections: Dict,
    deal_intel: Dict
) -> str:
    """Generate suggested agenda for next meeting"""
    agenda_items = []

    # Address unresolved objections
    unhandled = objections.get("unhandled_objections", [])
    if unhandled:
        categories = list(set([o["category"] for o in unhandled]))
        agenda_items.append(f"1. Address open concerns: {', '.join(categories)}")

    # Based on deal stage
    stage = deal_intel.get("recommended_stage", "discovery")
    if stage == "discovery":
        agenda_items.append("2. Deep dive into business requirements and success criteria")
    elif stage == "qualification":
        agenda_items.append("2. Confirm budget, timeline, and decision process")
    elif stage == "demo_evaluation":
        agenda_items.append("2. Technical demonstration of key capabilities")
    elif stage == "proposal":
        agenda_items.append("2. Present formal proposal and pricing")
    elif stage == "negotiation":
        agenda_items.append("2. Review contract terms and finalize agreement")

    # Follow up on action items
    high_priority = [a for a in action_items if a.get("priority") == "high"][:2]
    if high_priority:
        agenda_items.append(f"3. Follow up: {high_priority[0]['action'][:50]}...")

    # Next steps
    agenda_items.append("4. Confirm next steps and timeline")

    return "\n".join(agenda_items) if agenda_items else "1. Review previous discussion\n2. Address open items\n3. Define next steps"


class SalesSummaryAction(ApexActionBase):
    name = "sales_summary"
    description = "Generate sales call summary"
    category = "sales_intelligence"
    industry = "sales_ai"

    def execute(self, **kwargs) -> dict:
        return sales_summary(**kwargs)


@register_factory("sales_summary")
async def sales_summary_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Small Factory handler for sales summary"""
    logger.info("Sales summary factory invoked")

    result = sales_summary(
        transcript=input_data.get("transcript", ""),
        emotion_analysis=input_data.get("emotion_analysis"),
        buying_signals=input_data.get("buying_signals"),
        objection_analysis=input_data.get("objection_analysis"),
        deal_intelligence=input_data.get("deal_intelligence"),
        deal_context=input_data.get("deal_context")
    )

    # AI-enhanced summary generation
    if input_data.get("use_ai", True) and CLAUDE_ENABLED:
        try:
            claude = get_model_router()
            ai_response = await claude.analyze_conversation(
                transcript=input_data.get("transcript", "")[:3000],
                analysis_type="summary",
                context={
                    "summary_type": "sales_call",
                    "include_action_items": True
                }
            )
            if ai_response:
                result["ai_summary"] = ai_response.get("summary", "")
                result["ai_action_items"] = ai_response.get("action_items", [])
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI summary generation failed", error=str(e))

    result["factory_id"] = "sales_summary"
    result["factory_version"] = "1.0.0"
    return result


def handler(event, context):
    return sales_summary(**event)
