"""
Quality Score Action
Calculate quality score for customer interactions

Supports both:
- Small Factory pattern (for voice pipeline chains)
- Standalone Lambda invocation
"""

import os
from datetime import datetime
from typing import List, Dict, Any

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


@register_factory("quality_score")
async def quality_score_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Small Factory version: Calculate quality score for interaction.

    Input:
        sentiment: Sentiment analysis results
        compliance: Compliance audit results
        config.scoring_model: Scoring model to use

    Output:
        overall_score: Quality score 0-100
        quality_tier: exceptional/meets/needs_improvement/unsatisfactory
        component_scores: Individual component scores
        strengths: Identified strengths
        improvement_areas: Areas needing improvement
    """
    config = input_data.get('config', {})
    sentiment_output = input_data.get('sentiment', {})
    compliance_output = input_data.get('compliance', {})
    diarize_output = input_data.get('diarize', {})
    transcribe_output = input_data.get('transcribe', {})

    scoring_model = config.get('scoring_model', 'contact_center_v1')

    # Weights for each component
    weights = {
        "compliance": 0.30,
        "sentiment": 0.25,
        "resolution": 0.20,
        "efficiency": 0.15,
        "professionalism": 0.10
    }

    component_scores = {}
    strengths = []
    improvement_areas = []

    # Compliance score
    compliance_score = compliance_output.get('overall_score', 75)
    component_scores["compliance"] = {
        "score": compliance_score,
        "weight": weights["compliance"],
        "weighted_score": compliance_score * weights["compliance"]
    }

    if compliance_score >= 90:
        strengths.append("Strong compliance adherence")
    elif compliance_score < 70:
        improvement_areas.append("Compliance procedures")

    # Sentiment score (convert from -1 to 1 scale to 0-100)
    sentiment_avg = sentiment_output.get('average_score', 0)
    sentiment_score = min(100, max(0, (sentiment_avg + 1) * 50))

    # Bonus for improving sentiment
    sentiment_arc = sentiment_output.get('sentiment_arc', 'stable')
    if sentiment_arc == 'improving':
        sentiment_score = min(100, sentiment_score + 10)

    component_scores["sentiment"] = {
        "score": round(sentiment_score, 1),
        "weight": weights["sentiment"],
        "weighted_score": sentiment_score * weights["sentiment"],
        "arc": sentiment_arc
    }

    if sentiment_score >= 70:
        strengths.append("Positive customer sentiment")
    elif sentiment_score < 40:
        improvement_areas.append("Customer rapport building")

    # Resolution score (estimated from call flow)
    # In a real implementation, this would come from CRM or call outcome
    # For now, estimate based on sentiment ending
    by_speaker = sentiment_output.get('by_speaker', {})
    customer_final_sentiment = 0
    for speaker, data in by_speaker.items():
        if 'customer' in speaker.lower():
            customer_final_sentiment = data.get('average_score', 0)

    if customer_final_sentiment > 0.2:
        resolution_score = 90
        strengths.append("Issue likely resolved successfully")
    elif customer_final_sentiment > -0.2:
        resolution_score = 70
    else:
        resolution_score = 40
        improvement_areas.append("Resolution effectiveness")

    component_scores["resolution"] = {
        "score": resolution_score,
        "weight": weights["resolution"],
        "weighted_score": resolution_score * weights["resolution"]
    }

    # Efficiency score (based on call duration)
    duration = transcribe_output.get('duration_seconds', 300)
    target_duration = 300  # 5 minutes target

    if duration <= target_duration:
        efficiency_score = 100
    elif duration <= target_duration * 1.5:
        efficiency_score = 80
    elif duration <= target_duration * 2:
        efficiency_score = 60
    else:
        efficiency_score = 40

    component_scores["efficiency"] = {
        "score": efficiency_score,
        "weight": weights["efficiency"],
        "weighted_score": efficiency_score * weights["efficiency"],
        "duration_seconds": duration,
        "target_seconds": target_duration
    }

    if efficiency_score >= 90:
        strengths.append("Efficient call handling")
    elif efficiency_score < 60:
        improvement_areas.append("Call time management")

    # Professionalism score (based on compliance subset)
    rule_results = compliance_output.get('rule_results', {})
    prof_rules = ['proper_greeting', 'proper_closing', 'empathy_shown']
    prof_scores = []
    for rule in prof_rules:
        if rule in rule_results:
            prof_scores.append(rule_results[rule].get('score', 0.5) * 100)

    professionalism_score = sum(prof_scores) / len(prof_scores) if prof_scores else 75

    component_scores["professionalism"] = {
        "score": round(professionalism_score, 1),
        "weight": weights["professionalism"],
        "weighted_score": professionalism_score * weights["professionalism"]
    }

    if professionalism_score >= 90:
        strengths.append("Professional demeanor")
    elif professionalism_score < 60:
        improvement_areas.append("Professional communication")

    # Calculate overall score
    overall_score = sum(c["weighted_score"] for c in component_scores.values())
    overall_score = round(overall_score, 1)

    # Determine quality tier
    if overall_score >= 90:
        quality_tier = "exceptional"
    elif overall_score >= 75:
        quality_tier = "meets"
    elif overall_score >= 60:
        quality_tier = "needs_improvement"
    else:
        quality_tier = "unsatisfactory"

    coaching_recommended = quality_tier in ["needs_improvement", "unsatisfactory"]

    return {
        "overall_score": overall_score,
        "quality_tier": quality_tier,
        "component_scores": component_scores,
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "coaching_recommended": coaching_recommended,
        "scoring_model": scoring_model
    }


@apex_action(ApexActionSchema(
    name="quality_score",
    description="Calculate quality score for customer interactions",
    category="quality",
    industry="contact_center",
    input_schema=ActionInputSchema(description="Quality scoring parameters")
        .add_string("interaction_id", "Interaction/call ID", required=True)
        .add_string("agent_id", "Agent identifier", required=True)
        .add_number("sentiment_score", "Sentiment score from analysis", required=True)
        .add_number("compliance_score", "Compliance score", required=True)
        .add_boolean("resolution_achieved", "Whether issue was resolved", required=True)
        .add_number("handle_time_seconds", "Total handle time in seconds", required=True)
        .add_number("target_handle_time", "Target handle time in seconds", required=False)
        .add_boolean("transfer_occurred", "Whether call was transferred", required=False)
        .add_boolean("callback_required", "Whether callback was required", required=False),
    output_schema=ActionOutputSchema(description="Quality score result")
        .add_number("overall_score", "Overall quality score 0-100")
        .add_string("quality_tier", "Quality tier: exceptional, meets, needs_improvement, unsatisfactory")
        .add_object("component_scores", "Individual component scores")
        .add_array("strengths", "Identified strengths")
        .add_array("improvement_areas", "Areas needing improvement")
        .add_boolean("coaching_recommended", "Whether coaching is recommended")
))
def quality_score(
    interaction_id: str,
    agent_id: str,
    sentiment_score: float,
    compliance_score: float,
    resolution_achieved: bool,
    handle_time_seconds: int,
    target_handle_time: int = 300,
    transfer_occurred: bool = False,
    callback_required: bool = False
) -> dict:
    """
    Calculate quality score

    Args:
        interaction_id: Interaction ID
        agent_id: Agent ID
        sentiment_score: Sentiment score
        compliance_score: Compliance score
        resolution_achieved: Resolution achieved
        handle_time_seconds: Handle time
        target_handle_time: Target handle time
        transfer_occurred: Transfer occurred
        callback_required: Callback required

    Returns:
        Quality scoring results
    """
    result = {
        "interaction_id": interaction_id,
        "agent_id": agent_id,
        "overall_score": 0,
        "quality_tier": "needs_improvement",
        "component_scores": {},
        "strengths": [],
        "improvement_areas": [],
        "coaching_recommended": False,
        "scoring_date": datetime.now().isoformat()
    }

    # Weights for each component
    weights = {
        "compliance": 0.25,
        "sentiment": 0.20,
        "resolution": 0.25,
        "efficiency": 0.15,
        "first_contact": 0.15
    }

    # Calculate component scores
    # Compliance (already 0-100)
    comp_compliance = compliance_score
    result["component_scores"]["compliance"] = {
        "score": comp_compliance,
        "weight": weights["compliance"]
    }

    if comp_compliance >= 90:
        result["strengths"].append("Strong compliance adherence")
    elif comp_compliance < 70:
        result["improvement_areas"].append("Compliance procedures")

    # Sentiment (convert from -1 to 1 scale to 0-100)
    comp_sentiment = min(100, max(0, (sentiment_score + 1) * 50))
    result["component_scores"]["sentiment"] = {
        "score": comp_sentiment,
        "weight": weights["sentiment"]
    }

    if comp_sentiment >= 70:
        result["strengths"].append("Positive customer sentiment")
    elif comp_sentiment < 40:
        result["improvement_areas"].append("Customer rapport building")

    # Resolution
    comp_resolution = 100 if resolution_achieved else 0
    result["component_scores"]["resolution"] = {
        "score": comp_resolution,
        "weight": weights["resolution"]
    }

    if resolution_achieved:
        result["strengths"].append("Issue resolved")
    else:
        result["improvement_areas"].append("Resolution effectiveness")

    # Efficiency (handle time)
    if handle_time_seconds <= target_handle_time:
        comp_efficiency = 100
    elif handle_time_seconds <= target_handle_time * 1.5:
        comp_efficiency = 75
    elif handle_time_seconds <= target_handle_time * 2:
        comp_efficiency = 50
    else:
        comp_efficiency = 25

    result["component_scores"]["efficiency"] = {
        "score": comp_efficiency,
        "weight": weights["efficiency"],
        "handle_time": handle_time_seconds,
        "target": target_handle_time
    }

    if comp_efficiency >= 90:
        result["strengths"].append("Efficient call handling")
    elif comp_efficiency < 50:
        result["improvement_areas"].append("Call efficiency and time management")

    # First Contact Resolution
    if resolution_achieved and not transfer_occurred and not callback_required:
        comp_fcr = 100
        result["strengths"].append("First contact resolution achieved")
    elif resolution_achieved and (transfer_occurred or callback_required):
        comp_fcr = 60
    else:
        comp_fcr = 0
        if transfer_occurred:
            result["improvement_areas"].append("Reduce unnecessary transfers")

    result["component_scores"]["first_contact"] = {
        "score": comp_fcr,
        "weight": weights["first_contact"]
    }

    # Calculate weighted overall score
    overall = sum(
        result["component_scores"][comp]["score"] * weights[comp]
        for comp in weights.keys()
    )
    result["overall_score"] = round(overall, 1)

    # Determine quality tier
    if overall >= 90:
        result["quality_tier"] = "exceptional"
    elif overall >= 75:
        result["quality_tier"] = "meets"
    elif overall >= 60:
        result["quality_tier"] = "needs_improvement"
        result["coaching_recommended"] = True
    else:
        result["quality_tier"] = "unsatisfactory"
        result["coaching_recommended"] = True

    return result


class QualityScoreAction(ApexActionBase):
    """Quality Score Action (class-based)"""

    name = "quality_score"
    description = "Calculate interaction quality score"
    category = "quality"
    industry = "contact_center"

    def execute(self, **kwargs) -> dict:
        return quality_score(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return quality_score(**event)
