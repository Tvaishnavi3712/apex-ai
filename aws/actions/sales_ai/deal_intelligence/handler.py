"""
Deal Intelligence Action (Context-Driven)
Aggregate signals to provide deal health assessment and win probability

Context-Driven Architecture:
- Deal stage definitions are read from playbook context.deal_config
- Risk indicators are read from context.deal_config.risk_indicators
- Positive indicators are read from context.deal_config.positive_indicators
- Scoring weights are read from context.deal_config.scoring_weights
- Health thresholds are read from context.deal_config.health_thresholds

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


# Default deal stage definitions (used when context not provided)
DEFAULT_DEAL_STAGES = {
    "discovery": {"order": 1, "typical_win_rate": 10},
    "qualification": {"order": 2, "typical_win_rate": 20},
    "demo_evaluation": {"order": 3, "typical_win_rate": 35},
    "proposal": {"order": 4, "typical_win_rate": 50},
    "negotiation": {"order": 5, "typical_win_rate": 70},
    "verbal_commit": {"order": 6, "typical_win_rate": 85},
    "closed_won": {"order": 7, "typical_win_rate": 100}
}

# Default risk indicators
DEFAULT_RISK_INDICATORS = {
    "no_champion": {"impact": -15, "description": "No internal champion identified"},
    "no_timeline": {"impact": -10, "description": "No defined decision timeline"},
    "no_budget": {"impact": -20, "description": "Budget not confirmed or allocated"},
    "competitor_preferred": {"impact": -25, "description": "Prospect prefers competitor"},
    "single_threaded": {"impact": -10, "description": "Only one contact engaged"},
    "stalled": {"impact": -15, "description": "No activity in extended period"},
    "high_objections": {"impact": -20, "description": "Multiple unresolved objections"},
    "low_engagement": {"impact": -15, "description": "Low prospect engagement score"}
}

# Default positive indicators
DEFAULT_POSITIVE_INDICATORS = {
    "champion_identified": {"impact": 15, "description": "Strong internal champion"},
    "budget_confirmed": {"impact": 20, "description": "Budget allocated for project"},
    "timeline_defined": {"impact": 10, "description": "Clear decision timeline"},
    "multi_threaded": {"impact": 10, "description": "Multiple stakeholders engaged"},
    "high_engagement": {"impact": 15, "description": "High prospect engagement"},
    "technical_win": {"impact": 15, "description": "Technical evaluation passed"},
    "business_case_built": {"impact": 12, "description": "ROI business case accepted"},
    "verbal_commitment": {"impact": 25, "description": "Verbal commitment received"}
}

# Default scoring weights
DEFAULT_SCORING_WEIGHTS = {
    "base_score": 30,
    "engagement_high_threshold": 70,
    "engagement_low_threshold": 30,
    "engagement_high_score": 15,
    "engagement_low_score": -15,
    "buying_intent_high_threshold": 60,
    "buying_intent_medium_threshold": 40,
    "buying_intent_low_threshold": 20,
    "buying_high_score": 20,
    "buying_medium_score": 10,
    "buying_low_score": -10,
    "objection_high_threshold": 60,
    "objection_medium_threshold": 30,
    "objection_high_score": -20,
    "objection_medium_score": -10,
    "objection_low_score": 5,
    "competitor_high_threshold": 70,
    "competitor_high_score": -25,
    "competitor_negative_score": 10,
    "stage_multiplier": 0.3,
    "momentum_accelerating_threshold": 60,
    "momentum_decelerating_threshold": 40
}

# Default health thresholds
DEFAULT_HEALTH_THRESHOLDS = {
    "healthy_minimum": 60,
    "at_risk_minimum": 35,
    "min_probability": 5,
    "max_probability": 95
}


@apex_action(ApexActionSchema(
    name="deal_intelligence",
    description="Aggregate deal signals for health assessment",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Deal intelligence parameters")
        .add_object("emotion_analysis", "Results from emotion analysis", required=False)
        .add_object("buying_signals", "Results from buying signal detection", required=False)
        .add_object("objection_analysis", "Results from objection detection", required=False)
        .add_object("competitor_analysis", "Results from competitor tracking", required=False)
        .add_object("deal_context", "CRM deal context (stage, value, etc.)", required=False)
        .add_string("transcript", "Optional transcript for additional analysis", required=False)
        .add_object("context", "Playbook context with deal configuration", required=False),
    output_schema=ActionOutputSchema(description="Deal intelligence assessment")
        .add_number("win_probability", "Predicted win probability 0-100")
        .add_string("deal_health", "Overall deal health: healthy, at_risk, critical")
        .add_string("recommended_stage", "Suggested deal stage")
        .add_array("risk_factors", "Identified risk factors")
        .add_array("positive_indicators", "Positive deal indicators")
        .add_array("next_best_actions", "Prioritized next actions")
        .add_object("deal_score_breakdown", "Score component breakdown")
))
def deal_intelligence(
    emotion_analysis: Dict = None,
    buying_signals: Dict = None,
    objection_analysis: Dict = None,
    competitor_analysis: Dict = None,
    deal_context: Dict = None,
    transcript: str = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Aggregate signals into deal intelligence (context-driven).

    Args:
        emotion_analysis: Emotion analysis results
        buying_signals: Buying signal results
        objection_analysis: Objection detection results
        competitor_analysis: Competitor tracking results
        deal_context: CRM deal context
        transcript: Optional transcript
        context: Playbook context with deal configuration

    Context keys used:
        - deal_config: Deal intelligence configuration
            - stages: Deal stage definitions with win rates
            - risk_indicators: Risk indicator impacts
            - positive_indicators: Positive indicator impacts
            - scoring_weights: Scoring weight parameters
            - health_thresholds: Deal health thresholds

    Returns:
        Deal health assessment with recommendations
    """
    emotion_analysis = emotion_analysis or {}
    buying_signals = buying_signals or {}
    objection_analysis = objection_analysis or {}
    competitor_analysis = competitor_analysis or {}
    deal_context = deal_context or {}
    context = context or {}

    # Get configuration from context
    deal_config = context.get('deal_config', {})
    deal_stages = deal_config.get('stages', DEFAULT_DEAL_STAGES)
    risk_indicators = deal_config.get('risk_indicators', DEFAULT_RISK_INDICATORS)
    positive_indicators = deal_config.get('positive_indicators', DEFAULT_POSITIVE_INDICATORS)
    scoring_weights = deal_config.get('scoring_weights', DEFAULT_SCORING_WEIGHTS)
    health_thresholds = deal_config.get('health_thresholds', DEFAULT_HEALTH_THRESHOLDS)

    logger.info(
        "Deal intelligence invoked",
        context_driven=bool(context),
        has_custom_config=bool(deal_config)
    )

    result = {
        "win_probability": 0,
        "deal_health": "unknown",
        "recommended_stage": "discovery",
        "current_stage": deal_context.get("stage", "unknown"),
        "risk_factors": [],
        "positive_indicators": [],
        "next_best_actions": [],
        "deal_score_breakdown": {},
        "conversation_insights": {},
        "trend": "stable",
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False,
        "context_driven": bool(context)
    }

    # Initialize base score from context
    base_score = scoring_weights.get('base_score', 30)

    # Score from emotion analysis using context-driven weights
    emotion_score = 0
    engagement = emotion_analysis.get("engagement_score", 50)
    engagement_high_threshold = scoring_weights.get('engagement_high_threshold', 70)
    engagement_low_threshold = scoring_weights.get('engagement_low_threshold', 30)

    if engagement >= engagement_high_threshold:
        emotion_score = scoring_weights.get('engagement_high_score', 15)
        result["positive_indicators"].append({
            "indicator": "high_engagement",
            "impact": emotion_score,
            "source": "emotion_analysis"
        })
    elif engagement <= engagement_low_threshold:
        emotion_score = scoring_weights.get('engagement_low_score', -15)
        result["risk_factors"].append({
            "risk": "low_engagement",
            "impact": emotion_score,
            "source": "emotion_analysis"
        })

    result["deal_score_breakdown"]["emotion_contribution"] = emotion_score

    # Score from buying signals using context-driven weights
    buying_score = 0
    buying_intent = buying_signals.get("buying_intent_score", 0)
    buying_high_threshold = scoring_weights.get('buying_intent_high_threshold', 60)
    buying_medium_threshold = scoring_weights.get('buying_intent_medium_threshold', 40)
    buying_low_threshold = scoring_weights.get('buying_intent_low_threshold', 20)

    if buying_intent >= buying_high_threshold:
        buying_score = scoring_weights.get('buying_high_score', 20)
        result["positive_indicators"].append({
            "indicator": "strong_buying_signals",
            "impact": buying_score,
            "source": "buying_signals"
        })
    elif buying_intent >= buying_medium_threshold:
        buying_score = scoring_weights.get('buying_medium_score', 10)
    elif buying_intent < buying_low_threshold:
        buying_score = scoring_weights.get('buying_low_score', -10)
        result["risk_factors"].append({
            "risk": "weak_buying_signals",
            "impact": buying_score,
            "source": "buying_signals"
        })

    result["deal_score_breakdown"]["buying_signal_contribution"] = buying_score

    # Score from objection analysis using context-driven weights
    objection_score = 0
    objection_severity = objection_analysis.get("objection_severity_score", 0)
    objection_high_threshold = scoring_weights.get('objection_high_threshold', 60)
    objection_medium_threshold = scoring_weights.get('objection_medium_threshold', 30)

    if objection_severity >= objection_high_threshold:
        objection_score = scoring_weights.get('objection_high_score', -20)
        result["risk_factors"].append({
            "risk": "high_objections",
            "impact": objection_score,
            "source": "objection_analysis"
        })
    elif objection_severity >= objection_medium_threshold:
        objection_score = scoring_weights.get('objection_medium_score', -10)
    else:
        objection_score = scoring_weights.get('objection_low_score', 5)

    result["deal_score_breakdown"]["objection_contribution"] = objection_score

    # Score from competitor analysis using context-driven weights
    competitor_score = 0
    competitive_threat = competitor_analysis.get("competitive_threat_level", 0)
    competitor_sentiment = competitor_analysis.get("competitor_sentiment", "neutral")
    competitor_high_threshold = scoring_weights.get('competitor_high_threshold', 70)

    if competitive_threat >= competitor_high_threshold:
        competitor_score = scoring_weights.get('competitor_high_score', -25)
        result["risk_factors"].append({
            "risk": "competitor_preferred",
            "impact": competitor_score,
            "source": "competitor_analysis"
        })
    elif competitor_sentiment == "negative_toward_competitor":
        competitor_score = scoring_weights.get('competitor_negative_score', 10)
        result["positive_indicators"].append({
            "indicator": "competitor_dissatisfaction",
            "impact": competitor_score,
            "source": "competitor_analysis"
        })

    result["deal_score_breakdown"]["competitive_contribution"] = competitor_score

    # Deal context adjustments using context-driven stages
    context_score = 0
    current_stage = deal_context.get("stage", "discovery")
    stage_multiplier = scoring_weights.get('stage_multiplier', 0.3)
    if current_stage in deal_stages:
        stage_info = deal_stages[current_stage]
        context_score = stage_info["typical_win_rate"] * stage_multiplier

    result["deal_score_breakdown"]["stage_contribution"] = round(context_score)

    # Calculate total win probability using context-driven thresholds
    total_score = base_score + emotion_score + buying_score + objection_score + competitor_score + context_score
    min_prob = health_thresholds.get('min_probability', 5)
    max_prob = health_thresholds.get('max_probability', 95)
    result["win_probability"] = max(min_prob, min(max_prob, round(total_score)))

    # Determine deal health using context-driven thresholds
    healthy_min = health_thresholds.get('healthy_minimum', 60)
    at_risk_min = health_thresholds.get('at_risk_minimum', 35)

    if result["win_probability"] >= healthy_min:
        result["deal_health"] = "healthy"
    elif result["win_probability"] >= at_risk_min:
        result["deal_health"] = "at_risk"
    else:
        result["deal_health"] = "critical"

    # Recommend stage based on signals
    result["recommended_stage"] = _recommend_stage(buying_signals, objection_analysis, deal_stages)

    # Generate next best actions
    result["next_best_actions"] = _generate_next_actions(
        result["risk_factors"],
        result["positive_indicators"],
        buying_signals,
        objection_analysis,
        result["deal_health"]
    )

    # Determine trend using context-driven thresholds
    momentum = buying_signals.get("deal_momentum", 50)
    momentum_accel_threshold = scoring_weights.get('momentum_accelerating_threshold', 60)
    momentum_decel_threshold = scoring_weights.get('momentum_decelerating_threshold', 40)

    if momentum > momentum_accel_threshold:
        result["trend"] = "improving"
    elif momentum < momentum_decel_threshold:
        result["trend"] = "declining"
    else:
        result["trend"] = "stable"

    # Add conversation insights summary
    result["conversation_insights"] = {
        "engagement_level": emotion_analysis.get("prospect_emotions", {}).get("engagement_trend", "unknown"),
        "dominant_emotion": emotion_analysis.get("prospect_emotions", {}).get("dominant_emotion", "unknown"),
        "buying_momentum": buying_signals.get("momentum_direction", "unknown"),
        "primary_objections": [obj.get("objection_category") for obj in objection_analysis.get("handling_recommendations", [])[:2]],
        "competitive_situation": competitor_analysis.get("competitor_sentiment", "unknown")
    }

    return result


def _recommend_stage(buying_signals: Dict, objection_analysis: Dict, deal_stages: Dict = None) -> str:
    """Recommend deal stage based on signals using context-driven stages."""
    deal_stages = deal_stages or DEFAULT_DEAL_STAGES
    buying_intent = buying_signals.get("buying_intent_score", 0)
    signal_breakdown = buying_signals.get("signal_breakdown", {})

    if "next_steps" in signal_breakdown and buying_intent >= 60:
        if signal_breakdown.get("budget_discussion"):
            return "negotiation"
        return "proposal"
    elif "implementation_questions" in signal_breakdown:
        return "demo_evaluation"
    elif "budget_discussion" in signal_breakdown:
        return "qualification"
    else:
        return "discovery"


def _generate_next_actions(
    risks: List,
    positives: List,
    buying_signals: Dict,
    objections: Dict,
    deal_health: str
) -> List[Dict]:
    """Generate prioritized next actions"""
    actions = []

    # Address highest risks first
    for risk in risks[:2]:
        risk_type = risk.get("risk", "")
        if risk_type == "competitor_preferred":
            actions.append({
                "action": "competitive_positioning",
                "priority": "high",
                "description": "Deploy competitive battlecard and arrange technical comparison",
                "owner": "Sales Rep"
            })
        elif risk_type == "high_objections":
            actions.append({
                "action": "objection_handling_session",
                "priority": "high",
                "description": "Schedule call to address specific objections with solutions",
                "owner": "Sales Rep"
            })
        elif risk_type == "low_engagement":
            actions.append({
                "action": "re_engagement_campaign",
                "priority": "high",
                "description": "Share valuable content and request discovery call",
                "owner": "Sales Rep"
            })

    # Leverage positives
    for positive in positives[:2]:
        indicator = positive.get("indicator", "")
        if indicator == "strong_buying_signals":
            actions.append({
                "action": "advance_to_proposal",
                "priority": "high",
                "description": "Prepare and present formal proposal",
                "owner": "Sales Rep"
            })
        elif indicator == "competitor_dissatisfaction":
            actions.append({
                "action": "migration_offer",
                "priority": "medium",
                "description": "Offer migration support and switching incentive",
                "owner": "Sales Rep"
            })

    # Add from buying signal recommendations
    for rec in buying_signals.get("recommended_actions", [])[:2]:
        actions.append({
            "action": rec.get("action", "follow_up"),
            "priority": rec.get("priority", "medium"),
            "description": rec.get("description", ""),
            "owner": "Sales Rep"
        })

    # Default action if none generated
    if not actions:
        actions.append({
            "action": "schedule_follow_up",
            "priority": "medium",
            "description": "Schedule follow-up call to continue discovery",
            "owner": "Sales Rep"
        })

    # Remove duplicates and limit
    seen = set()
    unique_actions = []
    for action in actions:
        key = action["action"]
        if key not in seen:
            seen.add(key)
            unique_actions.append(action)

    return unique_actions[:5]


class DealIntelligenceAction(ApexActionBase):
    name = "deal_intelligence"
    description = "Aggregate deal signals for assessment"
    category = "sales_intelligence"
    industry = "sales_ai"

    def execute(self, **kwargs) -> dict:
        return deal_intelligence(**kwargs)


@register_factory("deal_intelligence")
async def deal_intelligence_factory(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Small Factory handler for deal intelligence (context-driven).

    Context keys used:
        - deal_config: Deal intelligence configuration
            - stages: Deal stage definitions with win rates
            - risk_indicators: Risk indicator impacts
            - positive_indicators: Positive indicator impacts
            - scoring_weights: Scoring weight parameters
            - health_thresholds: Deal health thresholds

    Expected input_data:
        - emotion_analysis: Results from emotion analysis
        - buying_signals: Results from buying signal detection
        - objection_analysis: Results from objection detection
        - competitor_analysis: Results from competitor tracking
        - deal_context: CRM deal context (stage, value, etc.)
        - transcript: Optional transcript for additional analysis

    Returns:
        Deal health assessment with win probability and recommendations
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Deal intelligence factory invoked",
        context_driven=bool(effective_context)
    )

    result = deal_intelligence(
        emotion_analysis=input_data.get("emotion_analysis"),
        buying_signals=input_data.get("buying_signals"),
        objection_analysis=input_data.get("objection_analysis"),
        competitor_analysis=input_data.get("competitor_analysis"),
        deal_context=input_data.get("deal_context"),
        transcript=input_data.get("transcript"),
        context=effective_context
    )

    if input_data.get("use_ai", True) and CLAUDE_ENABLED and input_data.get("transcript"):
        try:
            claude = get_bedrock_claude_service()
            ai_response = await claude.analyze_conversation(
                transcript=input_data.get("transcript", "")[:2000],
                analysis_type="custom",
                context={
                    "custom_prompt": f"""Based on this sales conversation and the rule-based analysis:
- Win probability: {result['win_probability']}%
- Deal health: {result['deal_health']}
- Risks: {[r['risk'] for r in result['risk_factors']]}

Provide:
1. Additional deal insights not captured
2. Hidden risks or opportunities
3. Specific closing strategy
4. Timeline prediction
Format as JSON."""
                }
            )
            if ai_response:
                result["ai_insights"] = ai_response
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI deal intelligence failed", error=str(e))

    result["context_driven"] = bool(effective_context)
    result["factory_id"] = "deal_intelligence"
    result["factory_version"] = "2.0.0"
    result["context_keys_used"] = ["deal_config"]

    return result


def handler(event, context):
    return deal_intelligence(**event)
