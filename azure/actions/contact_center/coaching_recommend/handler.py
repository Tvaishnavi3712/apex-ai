"""
Coaching Recommendation Action
Generate coaching recommendations for agents based on performance

Supports both:
- Small Factory pattern (for voice pipeline chains)
- Standalone Lambda invocation

AI-enhanced coaching via Claude when available,
with fallback to rule-based recommendations.
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import structlog

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase

logger = structlog.get_logger()

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

# Claude integration (optional - graceful fallback)
try:
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False


@register_factory("coaching_tips")
async def coaching_tips_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Small Factory version: Generate coaching tips for agent.

    Input:
        compliance: Compliance audit results
        sentiment: Sentiment analysis results
        config.focus_areas: Areas to focus on
        config.detail_level: "brief" or "comprehensive"

    Output:
        tips: List of coaching tips
        priority_areas: Top areas for improvement
        strengths: Identified strengths
        training_modules: Recommended training
    """
    config = input_data.get('config', {})
    compliance_output = input_data.get('compliance', {})
    sentiment_output = input_data.get('sentiment', {})
    escalation_output = input_data.get('escalation', {})

    focus_areas = config.get('focus_areas', ['empathy', 'efficiency', 'accuracy', 'compliance'])
    detail_level = config.get('detail_level', 'brief')
    include_examples = config.get('include_examples', False)

    tips = []
    priority_areas = []
    strengths = []
    training_modules = []

    # Analyze compliance
    compliance_score = compliance_output.get('overall_score', 100)
    violations = compliance_output.get('violations', [])
    compliance_passed = compliance_output.get('passed', True)

    if not compliance_passed:
        priority_areas.append("compliance")
        for violation in violations[:3]:
            rule = violation.get('rule', '').replace('_', ' ').title()
            tips.append({
                "area": "compliance",
                "tip": f"Work on {rule}",
                "priority": "high" if violation.get('severity') == 'high' else "medium",
                "description": violation.get('description', '')
            })
            if detail_level == 'comprehensive' and include_examples:
                tips[-1]["example"] = f"Try using phrases that demonstrate {rule.lower()}"

        training_modules.append({
            "module_id": "compliance_basics",
            "title": "Compliance Fundamentals",
            "duration_minutes": 30,
            "reason": "Address compliance violations"
        })
    else:
        strengths.append("Strong compliance adherence")

    # Analyze sentiment handling
    sentiment_arc = sentiment_output.get('sentiment_arc', 'stable')
    overall_sentiment = sentiment_output.get('overall_sentiment', 'neutral')
    by_speaker = sentiment_output.get('by_speaker', {})

    # Check if agent improved customer sentiment
    customer_sentiment = None
    for speaker, data in by_speaker.items():
        if 'customer' in speaker.lower():
            customer_sentiment = data

    if sentiment_arc == 'improving':
        strengths.append("Successfully improved customer sentiment during call")
    elif sentiment_arc == 'declining' and 'empathy' in focus_areas:
        priority_areas.append("empathy")
        tips.append({
            "area": "empathy",
            "tip": "Focus on empathetic responses",
            "priority": "high",
            "description": "Customer sentiment declined during the call. Practice active listening and acknowledgment."
        })
        training_modules.append({
            "module_id": "active_listening",
            "title": "Active Listening Skills",
            "duration_minutes": 45,
            "reason": "Improve customer rapport"
        })

    if overall_sentiment == 'negative' and 'empathy' not in priority_areas:
        tips.append({
            "area": "empathy",
            "tip": "Use more empathetic language",
            "priority": "medium",
            "description": "Customer expressed negative sentiment. Consider using phrases like 'I understand' and 'I can help with that'."
        })

    # Check for escalation handling
    if escalation_output:
        escalation_detected = escalation_output.get('escalation_detected', False)
        if escalation_detected:
            highest_severity = escalation_output.get('highest_severity', 'low')
            if highest_severity in ['high', 'critical']:
                tips.append({
                    "area": "de-escalation",
                    "tip": "Practice de-escalation techniques",
                    "priority": "high",
                    "description": "Escalation signals detected. Review de-escalation training materials."
                })
                training_modules.append({
                    "module_id": "de_escalation",
                    "title": "De-escalation Techniques",
                    "duration_minutes": 60,
                    "reason": "Handle escalated situations effectively"
                })

    # Add general tips based on focus areas
    if 'efficiency' in focus_areas and not any(t['area'] == 'efficiency' for t in tips):
        tips.append({
            "area": "efficiency",
            "tip": "Maintain call flow efficiency",
            "priority": "low",
            "description": "Continue to manage call time while ensuring thorough assistance."
        })

    if 'accuracy' in focus_areas:
        tips.append({
            "area": "accuracy",
            "tip": "Verify information accuracy",
            "priority": "low",
            "description": "Always confirm details before processing requests."
        })

    # Build summary
    coaching_priority = "urgent" if len(priority_areas) >= 2 else ("high" if priority_areas else "low")

    # Build rule-based result
    rule_based_result = {
        "tips": tips,
        "tip_count": len(tips),
        "priority_areas": priority_areas,
        "strengths": strengths,
        "training_modules": training_modules,
        "coaching_priority": coaching_priority,
        "requires_followup": coaching_priority in ["urgent", "high"],
        "compliance_score": compliance_score,
        "sentiment_trend": sentiment_arc,
        "ai_enhanced": False
    }

    # Try AI-enhanced coaching if enabled
    use_ai = config.get('use_ai', True) and CLAUDE_ENABLED
    transcript = input_data.get('transcribe', {}).get('full_text', '')
    if not transcript:
        transcript = input_data.get('state', {}).get('input', {}).get('transcript', {}).get('full_text', '')

    if use_ai and transcript:
        try:
            ai_result = await _generate_coaching_with_ai(
                transcript,
                compliance_output,
                sentiment_output
            )
            if ai_result:
                # Merge AI tips with rule-based tips (avoid duplicates)
                existing_areas = {tip["area"] for tip in tips}
                for ai_tip in ai_result.get("tips", []):
                    if ai_tip.get("area") not in existing_areas:
                        rule_based_result["tips"].append(ai_tip)
                        existing_areas.add(ai_tip["area"])

                # Add AI-identified strengths
                ai_strengths = ai_result.get("strengths", [])
                for strength in ai_strengths:
                    if strength not in rule_based_result["strengths"]:
                        rule_based_result["strengths"].append(strength)

                # Add AI-recommended training modules
                existing_modules = {m["module_id"] for m in training_modules}
                for ai_module in ai_result.get("training_modules", []):
                    if ai_module.get("module_id") not in existing_modules:
                        rule_based_result["training_modules"].append(ai_module)

                # Update counts
                rule_based_result["tip_count"] = len(rule_based_result["tips"])
                rule_based_result["ai_enhanced"] = True
                rule_based_result["overall_performance_score"] = ai_result.get("overall_performance_score")

                logger.info("AI-enhanced coaching recommendations generated")
        except Exception as e:
            logger.warning("AI coaching generation failed, using rule-based", error=str(e))

    return rule_based_result


async def _generate_coaching_with_ai(
    transcript: str,
    compliance_data: Dict[str, Any],
    sentiment_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate coaching recommendations using Claude."""
    if not CLAUDE_ENABLED:
        return None

    claude = get_model_router()
    context = {
        "compliance_data": {
            "passed": compliance_data.get("passed"),
            "score": compliance_data.get("overall_score"),
            "violations": compliance_data.get("violations", [])
        },
        "sentiment_data": {
            "overall": sentiment_data.get("overall_sentiment"),
            "arc": sentiment_data.get("sentiment_arc"),
            "by_speaker": sentiment_data.get("by_speaker", {})
        }
    }

    result = await claude.analyze_conversation(
        transcript=transcript,
        analysis_type="coaching",
        context=context
    )

    if result.get("success") and result.get("parsed"):
        return result["parsed"]

    return None


# Coaching modules
COACHING_MODULES = {
    "compliance_basics": {
        "title": "Compliance Fundamentals",
        "duration_minutes": 30,
        "focus": ["greeting", "disclosure", "verification"],
        "applies_to": ["compliance"]
    },
    "active_listening": {
        "title": "Active Listening Skills",
        "duration_minutes": 45,
        "focus": ["sentiment", "empathy", "rapport"],
        "applies_to": ["sentiment", "customer_rapport"]
    },
    "problem_solving": {
        "title": "Problem Solving Techniques",
        "duration_minutes": 60,
        "focus": ["resolution", "troubleshooting"],
        "applies_to": ["resolution"]
    },
    "efficiency_training": {
        "title": "Call Efficiency Workshop",
        "duration_minutes": 45,
        "focus": ["time_management", "navigation", "documentation"],
        "applies_to": ["efficiency", "handle_time"]
    },
    "de_escalation": {
        "title": "De-escalation Techniques",
        "duration_minutes": 60,
        "focus": ["escalation", "angry_customers", "emotional_intelligence"],
        "applies_to": ["escalation", "difficult_calls"]
    },
    "product_knowledge": {
        "title": "Product Knowledge Refresh",
        "duration_minutes": 90,
        "focus": ["products", "procedures", "policies"],
        "applies_to": ["resolution", "transfer_rate"]
    }
}


@apex_action(ApexActionSchema(
    name="coaching_recommend",
    description="Generate coaching recommendations for agents based on performance",
    category="coaching",
    industry="contact_center",
    input_schema=ActionInputSchema(description="Coaching recommendation parameters")
        .add_string("agent_id", "Agent identifier", required=True)
        .add_array("improvement_areas", "Identified improvement areas", required=True)
        .add_object("performance_metrics", "Recent performance metrics", required=True)
        .add_array("recent_quality_scores", "Recent quality scores", required=False)
        .add_string("agent_tenure", "Agent tenure: new, developing, experienced", required=False),
    output_schema=ActionOutputSchema(description="Coaching recommendation result")
        .add_array("recommended_modules", "Recommended coaching modules")
        .add_string("priority", "Coaching priority: urgent, high, medium, low")
        .add_object("development_plan", "Suggested development plan")
        .add_array("action_items", "Specific action items for supervisor")
        .add_string("follow_up_date", "Recommended follow-up date")
))
def coaching_recommend(
    agent_id: str,
    improvement_areas: List[str],
    performance_metrics: Dict[str, Any],
    recent_quality_scores: List[float] = None,
    agent_tenure: str = "developing"
) -> dict:
    """
    Generate coaching recommendations

    Args:
        agent_id: Agent ID
        improvement_areas: Areas needing improvement
        performance_metrics: Performance metrics
        recent_quality_scores: Recent scores
        agent_tenure: Agent tenure level

    Returns:
        Coaching recommendations
    """
    recent_quality_scores = recent_quality_scores or []

    result = {
        "agent_id": agent_id,
        "recommended_modules": [],
        "priority": "medium",
        "development_plan": {},
        "action_items": [],
        "follow_up_date": None,
        "recommendation_date": datetime.now().isoformat()
    }

    # Determine priority based on recent scores
    if recent_quality_scores:
        avg_score = sum(recent_quality_scores) / len(recent_quality_scores)
        if avg_score < 60:
            result["priority"] = "urgent"
        elif avg_score < 70:
            result["priority"] = "high"
        elif avg_score < 80:
            result["priority"] = "medium"
        else:
            result["priority"] = "low"

    # Map improvement areas to coaching modules
    for area in improvement_areas:
        area_lower = area.lower().replace(" ", "_")
        for module_id, module in COACHING_MODULES.items():
            if area_lower in module["applies_to"] or any(f in area_lower for f in module["focus"]):
                if module_id not in [m["module_id"] for m in result["recommended_modules"]]:
                    result["recommended_modules"].append({
                        "module_id": module_id,
                        "title": module["title"],
                        "duration_minutes": module["duration_minutes"],
                        "reason": f"Address: {area}",
                        "priority": "high" if len(result["recommended_modules"]) < 2 else "medium"
                    })

    # Generate development plan
    total_duration = sum(m["duration_minutes"] for m in result["recommended_modules"])

    result["development_plan"] = {
        "total_training_minutes": total_duration,
        "recommended_timeline_days": max(7, total_duration // 30),
        "phases": []
    }

    # Phase 1: Immediate focus
    if result["recommended_modules"]:
        result["development_plan"]["phases"].append({
            "phase": 1,
            "focus": "Immediate Priority",
            "modules": [m["module_id"] for m in result["recommended_modules"][:2]],
            "duration_days": 7
        })

    # Phase 2: Ongoing development
    if len(result["recommended_modules"]) > 2:
        result["development_plan"]["phases"].append({
            "phase": 2,
            "focus": "Continued Development",
            "modules": [m["module_id"] for m in result["recommended_modules"][2:]],
            "duration_days": 14
        })

    # Generate action items
    result["action_items"] = [
        f"Schedule 1:1 coaching session with {agent_id}",
        "Review recent call recordings together",
        "Set SMART goals for improvement areas"
    ]

    if result["priority"] in ["urgent", "high"]:
        result["action_items"].append("Increase quality monitoring frequency")
        result["action_items"].append("Provide real-time coaching support")

    # Calculate follow-up date
    if result["priority"] == "urgent":
        days_until_followup = 3
    elif result["priority"] == "high":
        days_until_followup = 7
    else:
        days_until_followup = 14

    from datetime import timedelta
    result["follow_up_date"] = (datetime.now() + timedelta(days=days_until_followup)).strftime('%Y-%m-%d')

    return result


class CoachingRecommendAction(ApexActionBase):
    """Coaching Recommendation Action (class-based)"""

    name = "coaching_recommend"
    description = "Generate agent coaching recommendations"
    category = "coaching"
    industry = "contact_center"

    def execute(self, **kwargs) -> dict:
        return coaching_recommend(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return coaching_recommend(**event)
