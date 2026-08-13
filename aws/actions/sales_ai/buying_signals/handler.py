"""
Buying Signals Detection Action (Context-Driven)
Identify verbal and behavioral buying signals in sales conversations

Context-Driven Architecture:
- Signal categories and weights are read from playbook context.buying_signal_config
- Negative signal patterns are read from context.buying_signal_config.negative_signals
- Intent score thresholds are read from context.signal_weights
- Recommendation logic is read from context.buying_signal_config.recommendations

Supports both:
- Lambda invocation (standalone)
- Small Factory pattern (chain processing)
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import structlog
import re

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


# Default buying signal categories with weights (used when context not provided)
DEFAULT_BUYING_SIGNAL_CATEGORIES = {
    "timeline_urgency": {
        "weight": 25,
        "description": "Indicates time pressure or urgency",
        "patterns": [
            r"when can (we|you) start",
            r"how (quickly|soon|fast)",
            r"need (this|it) by",
            r"deadline is",
            r"asap",
            r"urgent",
            r"right away",
            r"immediately",
            r"this quarter",
            r"this month",
            r"before (year|quarter|month) end"
        ]
    },
    "budget_discussion": {
        "weight": 20,
        "description": "Discussing budget or pricing details",
        "patterns": [
            r"what('s| is) the (price|cost|pricing)",
            r"how much (does|would|will)",
            r"(budget|funding) (is|for)",
            r"payment (terms|options|plans)",
            r"discount",
            r"volume pricing",
            r"total cost of ownership",
            r"roi|return on investment",
            r"break.?even"
        ]
    },
    "decision_process": {
        "weight": 22,
        "description": "Revealing decision-making process",
        "patterns": [
            r"(need|have) to (talk|check|discuss) with",
            r"(my|our) (boss|manager|ceo|cfo|team|board)",
            r"decision (maker|committee)",
            r"approval (process|needed)",
            r"who else (needs|should)",
            r"stakeholder",
            r"sign off"
        ]
    },
    "implementation_questions": {
        "weight": 23,
        "description": "Asking about implementation details",
        "patterns": [
            r"how (long|difficult) (to|is) implement",
            r"implementation (time|process|plan)",
            r"(training|onboarding) (needed|required|included)",
            r"integration with",
            r"migration (from|process)",
            r"setup (time|process)",
            r"go.?live",
            r"deployment"
        ]
    },
    "comparison_shopping": {
        "weight": 15,
        "description": "Comparing with alternatives",
        "patterns": [
            r"(compared|versus|vs) (to|with)",
            r"(better|different) (than|from)",
            r"(other|alternative) (options|vendors|solutions)",
            r"why (should we|you) (vs|over)",
            r"competitor",
            r"what (makes|sets) you (apart|different)"
        ]
    },
    "ownership_language": {
        "weight": 28,
        "description": "Using ownership or future-state language",
        "patterns": [
            r"when we (use|have|implement)",
            r"(our|my) (new|future)",
            r"(we('ll| will)|i('ll| will)) (use|have|be)",
            r"looking forward to",
            r"excited (about|to)",
            r"can('t| not) wait (to|for)",
            r"(this|that) (will|would) (help|solve|work)"
        ]
    },
    "specific_requirements": {
        "weight": 20,
        "description": "Discussing specific needs and requirements",
        "patterns": [
            r"(we|i) need",
            r"(must|has to|should) (have|include|support)",
            r"requirement(s)?",
            r"(important|critical|essential) (that|for)",
            r"use case",
            r"our (situation|scenario|case)"
        ]
    },
    "next_steps": {
        "weight": 30,
        "description": "Asking about or suggesting next steps",
        "patterns": [
            r"(what('s| are)|next) (step|steps)",
            r"(how|what) do we (proceed|move forward)",
            r"(send|schedule|set up) (me|us|a)",
            r"(trial|pilot|demo|poc)",
            r"(proposal|quote|contract)",
            r"let('s| us) (schedule|set up|plan)",
            r"follow up"
        ]
    }
}

# Default negative signals (anti-buying)
DEFAULT_NEGATIVE_SIGNALS = {
    "budget_constraints": [
        r"(no|don't have|limited) budget",
        r"too expensive",
        r"(can't|cannot) afford",
        r"not (in|within) (our|the) budget"
    ],
    "timing_issues": [
        r"not (right|good) (time|now)",
        r"(maybe|perhaps) (next|later)",
        r"(busy|swamped) (right now|currently)",
        r"check back (in|after)"
    ],
    "authority_deflection": [
        r"(not|don't) (my|the) decision",
        r"(can't|cannot) (commit|decide)",
        r"just (looking|researching|exploring)"
    ],
    "competitor_preference": [
        r"(happy|satisfied) with (current|existing)",
        r"already (have|using|use)",
        r"(prefer|leaning toward) (competitor)"
    ]
}

# Default signal weights and thresholds
DEFAULT_SIGNAL_WEIGHTS = {
    "negative_signal_weight": 15,
    "high_intent_threshold": 70,
    "medium_intent_threshold": 40,
    "momentum_positive_multiplier": 5,
    "momentum_negative_multiplier": 10,
    "base_momentum": 50,
    "max_recommendations": 5
}


@apex_action(ApexActionSchema(
    name="buying_signals",
    description="Identify buying signals in sales conversations",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Buying signal detection parameters")
        .add_string("transcript", "Conversation transcript", required=True)
        .add_array("speaker_segments", "Speaker-labeled segments", required=False)
        .add_string("prospect_label", "Prospect speaker label", required=False)
        .add_object("deal_context", "Deal context (stage, value, etc.)", required=False)
        .add_object("context", "Playbook context with signal configuration", required=False),
    output_schema=ActionOutputSchema(description="Buying signal analysis")
        .add_number("buying_intent_score", "Overall buying intent 0-100")
        .add_array("signals_detected", "All detected buying signals")
        .add_object("signal_breakdown", "Signals by category")
        .add_array("negative_signals", "Anti-buying signals detected")
        .add_number("deal_momentum", "Deal momentum score")
        .add_array("recommended_actions", "Next best actions")
))
def buying_signals(
    transcript: str,
    speaker_segments: List[Dict] = None,
    prospect_label: str = "Customer",
    deal_context: Dict = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Detect buying signals in sales conversations (context-driven).

    Args:
        transcript: Full conversation transcript
        speaker_segments: Speaker-labeled segments
        prospect_label: Label identifying prospect
        deal_context: Context about the deal
        context: Playbook context with signal configuration

    Returns:
        Comprehensive buying signal analysis
    """
    deal_context = deal_context or {}
    context = context or {}

    # Get configuration from context
    buying_signal_config = context.get('buying_signal_config', {})
    signal_categories = buying_signal_config.get('categories', DEFAULT_BUYING_SIGNAL_CATEGORIES)
    negative_signal_patterns = buying_signal_config.get('negative_signals', DEFAULT_NEGATIVE_SIGNALS)
    signal_weights = context.get('signal_weights', DEFAULT_SIGNAL_WEIGHTS)

    logger.info(
        "Buying signals analysis invoked",
        context_driven=bool(context),
        has_custom_categories=bool(buying_signal_config.get('categories'))
    )

    result = {
        "buying_intent_score": 0,
        "signals_detected": [],
        "signal_breakdown": {},
        "negative_signals": [],
        "deal_momentum": signal_weights.get('base_momentum', 50),
        "momentum_direction": "neutral",
        "recommended_actions": [],
        "signal_timeline": [],
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False,
        "context_driven": bool(context)
    }

    if not transcript:
        return result

    transcript_lower = transcript.lower()

    # Detect positive buying signals using context-driven categories
    total_weight = 0
    max_possible_weight = sum(cat.get("weight", 20) for cat in signal_categories.values())

    for category, config in signal_categories.items():
        category_signals = []
        category_weight = config.get("weight", 20)

        for pattern in config.get("patterns", []):
            matches = re.finditer(pattern, transcript_lower)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 30)
                end = min(len(transcript), match.end() + 30)
                match_context = transcript[start:end]

                signal = {
                    "category": category,
                    "matched_pattern": match.group(),
                    "context": f"...{match_context}...",
                    "position_percent": round((match.start() / len(transcript)) * 100),
                    "weight": category_weight,
                    "description": config.get("description", "")
                }
                category_signals.append(signal)
                result["signals_detected"].append(signal)

        if category_signals:
            # Weight contribution (diminishing returns for multiple signals in same category)
            signal_count = len(category_signals)
            effective_weight = category_weight * min(1.5, 0.6 + (0.4 * signal_count))
            total_weight += effective_weight

            result["signal_breakdown"][category] = {
                "count": signal_count,
                "signals": category_signals,
                "effective_weight": round(effective_weight, 1)
            }

    # Detect negative signals using context-driven patterns
    negative_signal_weight = signal_weights.get('negative_signal_weight', 15)
    negative_weight = 0
    for category, patterns in negative_signal_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, transcript_lower)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(transcript), match.end() + 30)
                match_context = transcript[start:end]

                result["negative_signals"].append({
                    "category": category,
                    "matched_pattern": match.group(),
                    "context": f"...{match_context}...",
                    "position_percent": round((match.start() / len(transcript)) * 100)
                })
                negative_weight += negative_signal_weight

    # Calculate buying intent score
    raw_score = (total_weight / max_possible_weight) * 100
    adjusted_score = max(0, raw_score - (negative_weight * 0.5))
    result["buying_intent_score"] = round(min(100, adjusted_score))

    # Calculate deal momentum using context-driven weights
    positive_signals = len(result["signals_detected"])
    negative_signals_count = len(result["negative_signals"])
    base_momentum = signal_weights.get('base_momentum', 50)
    positive_multiplier = signal_weights.get('momentum_positive_multiplier', 5)
    negative_multiplier = signal_weights.get('momentum_negative_multiplier', 10)

    if positive_signals > negative_signals_count * 2:
        result["deal_momentum"] = min(100, base_momentum + (positive_signals * positive_multiplier))
        result["momentum_direction"] = "accelerating"
    elif negative_signals_count > positive_signals:
        result["deal_momentum"] = max(0, base_momentum - (negative_signals_count * negative_multiplier))
        result["momentum_direction"] = "decelerating"
    else:
        result["deal_momentum"] = base_momentum
        result["momentum_direction"] = "stable"

    # Generate recommended actions based on signals and context
    result["recommended_actions"] = _generate_recommendations(
        result["signal_breakdown"],
        result["negative_signals"],
        result["buying_intent_score"],
        deal_context,
        signal_weights,
        buying_signal_config.get('recommendations', {})
    )

    # Generate signal timeline
    if speaker_segments:
        result["signal_timeline"] = _generate_signal_timeline(
            speaker_segments,
            transcript,
            signal_categories
        )

    return result


def _generate_recommendations(
    signal_breakdown: Dict,
    negative_signals: List,
    intent_score: int,
    deal_context: Dict,
    signal_weights: Dict = None,
    recommendation_config: Dict = None
) -> List[Dict]:
    """Generate next best action recommendations using context configuration."""
    signal_weights = signal_weights or DEFAULT_SIGNAL_WEIGHTS
    recommendation_config = recommendation_config or {}
    recommendations = []

    # Get thresholds from context
    high_intent_threshold = signal_weights.get('high_intent_threshold', 70)
    medium_intent_threshold = signal_weights.get('medium_intent_threshold', 40)
    max_recommendations = signal_weights.get('max_recommendations', 5)

    # Get custom recommendations from context or use defaults
    high_intent_actions = recommendation_config.get('high_intent', {})
    medium_intent_actions = recommendation_config.get('medium_intent', {})
    negative_signal_actions = recommendation_config.get('negative_signals', {})

    # High intent recommendations
    if intent_score >= high_intent_threshold:
        if "next_steps" in signal_breakdown:
            action = high_intent_actions.get('next_steps', {
                "action": "propose_next_step",
                "priority": "high",
                "description": "Prospect asked about next steps - provide clear proposal or trial offer",
                "timing": "immediate"
            })
            recommendations.append(action)
        if "timeline_urgency" in signal_breakdown:
            action = high_intent_actions.get('timeline_urgency', {
                "action": "fast_track_deal",
                "priority": "high",
                "description": "Time pressure detected - accelerate sales process",
                "timing": "same_day"
            })
            recommendations.append(action)

    # Medium intent recommendations
    if medium_intent_threshold <= intent_score < high_intent_threshold:
        if "budget_discussion" in signal_breakdown:
            action = medium_intent_actions.get('budget_discussion', {
                "action": "roi_presentation",
                "priority": "medium",
                "description": "Budget discussions active - provide ROI analysis and case studies",
                "timing": "next_meeting"
            })
            recommendations.append(action)
        if "decision_process" in signal_breakdown:
            action = medium_intent_actions.get('decision_process', {
                "action": "multi_thread",
                "priority": "medium",
                "description": "Multiple stakeholders involved - request introductions",
                "timing": "next_meeting"
            })
            recommendations.append(action)

    # Handle negative signals
    for neg_signal in negative_signals:
        category = neg_signal["category"]
        if category == "budget_constraints":
            action = negative_signal_actions.get('budget_constraints', {
                "action": "value_justification",
                "priority": "high",
                "description": "Address budget concerns with ROI data and flexible payment options",
                "timing": "immediate"
            })
            recommendations.append(action)
        elif category == "timing_issues":
            action = negative_signal_actions.get('timing_issues', {
                "action": "create_urgency",
                "priority": "medium",
                "description": "Create urgency with limited-time offer or cost of delay analysis",
                "timing": "follow_up"
            })
            recommendations.append(action)
        elif category == "competitor_preference":
            action = negative_signal_actions.get('competitor_preference', {
                "action": "competitive_positioning",
                "priority": "high",
                "description": "Address competitive situation with differentiation points",
                "timing": "immediate"
            })
            recommendations.append(action)

    # Low intent recommendations
    if intent_score < medium_intent_threshold:
        action = recommendation_config.get('low_intent', {
            "action": "discovery_questions",
            "priority": "high",
            "description": "Low buying intent - conduct deeper discovery to uncover pain points",
            "timing": "immediate"
        })
        recommendations.append(action)

    # Default recommendation if none generated
    if not recommendations:
        action = recommendation_config.get('default', {
            "action": "continue_discovery",
            "priority": "medium",
            "description": "Continue building relationship and understanding needs",
            "timing": "ongoing"
        })
        recommendations.append(action)

    return recommendations[:max_recommendations]


def _generate_signal_timeline(
    segments: List[Dict],
    full_transcript: str,
    signal_categories: Dict = None
) -> List[Dict]:
    """Generate timeline of buying signals through conversation using context categories."""
    signal_categories = signal_categories or DEFAULT_BUYING_SIGNAL_CATEGORIES
    timeline = []

    for i, segment in enumerate(segments):
        text = segment.get("text", "").lower()
        speaker = segment.get("speaker", "unknown")

        # Check for signals in this segment using context-driven categories
        signals_in_segment = []
        for category, config in signal_categories.items():
            for pattern in config.get("patterns", []):
                if re.search(pattern, text):
                    signals_in_segment.append(category)
                    break

        if signals_in_segment:
            timeline.append({
                "segment_index": i,
                "speaker": speaker,
                "signals": signals_in_segment,
                "position_percent": round((i / len(segments)) * 100)
            })

    return timeline


class BuyingSignalsAction(ApexActionBase):
    """Buying Signals Detection Action (class-based)"""

    name = "buying_signals"
    description = "Identify buying signals in sales conversations"
    category = "sales_intelligence"
    industry = "sales_ai"

    def execute(self, **kwargs) -> dict:
        return buying_signals(**kwargs)


# Small Factory registration
@register_factory("buying_signals")
async def buying_signals_factory(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Small Factory handler for buying signal detection (context-driven).

    Context keys used:
        - buying_signal_config: Signal category configuration
            - categories: Signal patterns and weights
            - negative_signals: Anti-buying signal patterns
            - recommendations: Action recommendations by scenario
        - signal_weights: Scoring weights and thresholds

    Expected input_data:
        - transcript: Conversation transcript
        - speaker_segments: Speaker-labeled segments (optional)
        - prospect_label: Prospect speaker label (optional)
        - deal_context: Deal context (optional)

    Returns:
        Buying signal analysis with intent scoring
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Buying signals factory invoked",
        context_driven=bool(effective_context)
    )

    use_ai = input_data.get("use_ai", True)

    result = buying_signals(
        transcript=input_data.get("transcript", ""),
        speaker_segments=input_data.get("speaker_segments"),
        prospect_label=input_data.get("prospect_label", "Customer"),
        deal_context=input_data.get("deal_context"),
        context=effective_context
    )

    # AI enhancement for deeper analysis
    if use_ai and CLAUDE_ENABLED:
        try:
            ai_result = await _ai_buying_signals(
                input_data.get("transcript", ""),
                result
            )
            if ai_result:
                result["ai_insights"] = ai_result
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI buying signals analysis failed", error=str(e))

    result["factory_id"] = "buying_signals"
    result["factory_version"] = "2.0.0"
    result["context_keys_used"] = ["buying_signal_config", "signal_weights"]

    return result


async def _ai_buying_signals(transcript: str, rule_based_result: dict) -> Optional[Dict]:
    """Use Claude for deeper buying signal analysis"""
    if not CLAUDE_ENABLED:
        return None

    try:
        claude = get_bedrock_claude_service()

        prompt = f"""Analyze this sales conversation for buying signals.

Transcript:
{transcript[:3000]}

Rule-based analysis found:
- Buying intent score: {rule_based_result['buying_intent_score']}
- Positive signals: {len(rule_based_result['signals_detected'])}
- Negative signals: {len(rule_based_result['negative_signals'])}

Provide additional insights:
1. Subtle buying signals not captured by patterns
2. Hidden objections or concerns
3. Decision timeline estimate
4. Key stakeholder dynamics
5. Deal risk assessment
6. Specific closing strategy recommendation

Format as JSON."""

        response = await claude.analyze_conversation(
            transcript=transcript,
            analysis_type="custom",
            context={"custom_prompt": prompt}
        )

        return response
    except Exception as e:
        logger.error("AI buying signals error", error=str(e))
        return None


def handler(event, context):
    """Lambda entry point"""
    return buying_signals(**event)
