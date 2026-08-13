"""
Objection Detection Action (Context-Driven)
Identify and categorize sales objections with handling recommendations

Context-Driven Architecture:
- Objection categories and patterns are read from playbook context.objection_config
- Handling strategies are read from context.handling_strategies
- Severity thresholds are read from context.objection_config.thresholds

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


# Default objection categories with patterns and handling strategies
DEFAULT_OBJECTION_CATEGORIES = {
    "price": {
        "patterns": [
            r"too (expensive|costly|much|pricey)",
            r"(can't|cannot) afford",
            r"(over|above|out of) (our |the )?budget",
            r"price is (too |a )(high|lot|concern)",
            r"cheaper (option|alternative|competitor)",
            r"(need|want) (a )?discount"
        ],
        "severity": "high",
        "handling_strategies": [
            "Break down the ROI and total cost of ownership",
            "Compare cost of inaction vs investment",
            "Offer flexible payment terms or phased implementation",
            "Focus on value delivered, not just price"
        ]
    },
    "timing": {
        "patterns": [
            r"not (the right|a good) time",
            r"(too |very )?busy (right now|currently|at the moment)",
            r"(maybe |perhaps )?(next|later|after)",
            r"(come|get) back (to us|later|in)",
            r"(other|different|bigger) priorities",
            r"(year|quarter|month|q[1-4]) (end|planning)"
        ],
        "severity": "medium",
        "handling_strategies": [
            "Create urgency with time-limited offer",
            "Show cost of delay with quantified impact",
            "Propose minimal initial commitment",
            "Offer to start planning now for future implementation"
        ]
    },
    "authority": {
        "patterns": [
            r"(need|have) to (check|talk|discuss|run it by)",
            r"not (my|the) decision",
            r"(boss|manager|ceo|cfo|committee|board) (needs|has) to",
            r"(can't|cannot) (approve|decide|commit)",
            r"(need|get) (approval|sign.?off)",
            r"other (stakeholder|people|team member)"
        ],
        "severity": "medium",
        "handling_strategies": [
            "Ask to include decision maker in next meeting",
            "Provide materials for internal presentation",
            "Offer executive briefing session",
            "Map out full buying committee and engage each"
        ]
    },
    "need": {
        "patterns": [
            r"(don't|do not) (see|understand) (the )?need",
            r"(we're |we are )?(fine|happy|okay|satisfied) (with |as is)",
            r"(not|don't) (really )?need (this|it|that)",
            r"(already|currently) (have|use|using)",
            r"(what('s| is) the |why do we )need",
            r"(works|working) (fine|well|okay)"
        ],
        "severity": "high",
        "handling_strategies": [
            "Conduct deeper discovery on pain points",
            "Share relevant case study showing hidden costs",
            "Quantify the problem they may not see",
            "Ask about future goals and how current solution scales"
        ]
    },
    "trust": {
        "patterns": [
            r"(never |not )heard of (you|your company)",
            r"(how long|are you) (in business|around)",
            r"(small|new|startup) company",
            r"(can you|do you) (guarantee|promise|ensure)",
            r"what if (you|it) (fail|doesn't work)",
            r"(reference|testimonial|case study|proof)"
        ],
        "severity": "medium",
        "handling_strategies": [
            "Provide customer references in similar industry",
            "Share case studies with measurable results",
            "Offer pilot program to prove value",
            "Highlight backing, partnerships, or certifications"
        ]
    },
    "competitor": {
        "patterns": [
            r"(using|use|have|with) (competitor|another vendor)",
            r"(competitor) (does|offers|has)",
            r"(why|how) (are you|is this) (better|different)",
            r"(they|competitor) (said|told us|mentioned)",
            r"(switching|change) (cost|effort)",
            r"(locked|committed|contract) (into|with)"
        ],
        "severity": "high",
        "handling_strategies": [
            "Focus on unique differentiators",
            "Address switching costs with migration support",
            "Calculate total cost comparison over time",
            "Offer competitive displacement program"
        ]
    },
    "complexity": {
        "patterns": [
            r"(too |very )?(complex|complicated|difficult)",
            r"(hard|difficult) to (implement|use|learn)",
            r"(don't|won't) have (time|resources) to",
            r"(our |the )team (can't|won't|doesn't)",
            r"(learning|adoption) curve",
            r"(change|training) (management|required)"
        ],
        "severity": "medium",
        "handling_strategies": [
            "Offer implementation support and training",
            "Show ease-of-use with demo or trial",
            "Provide customer success resources",
            "Propose phased rollout to reduce complexity"
        ]
    }
}

# Default thresholds for objection handling
DEFAULT_OBJECTION_THRESHOLDS = {
    "severity_multipliers": {"high": 3, "medium": 2, "low": 1},
    "manager_support_high_count": 2,
    "manager_support_severity_score": 60,
    "late_objection_position": 75,
    "max_recommendations": 5
}


@apex_action(ApexActionSchema(
    name="objection_detect",
    description="Identify and categorize sales objections",
    category="sales_intelligence",
    industry="sales_ai",
    input_schema=ActionInputSchema(description="Objection detection parameters")
        .add_string("transcript", "Conversation transcript", required=True)
        .add_array("speaker_segments", "Speaker-labeled segments", required=False)
        .add_string("prospect_label", "Prospect speaker label", required=False)
        .add_object("context", "Playbook context with objection configuration", required=False),
    output_schema=ActionOutputSchema(description="Objection analysis")
        .add_array("objections", "Detected objections")
        .add_object("objection_summary", "Summary by category")
        .add_number("objection_severity_score", "Overall objection severity")
        .add_array("handling_recommendations", "Recommended responses")
        .add_boolean("requires_manager_support", "Whether manager support needed")
))
def objection_detect(
    transcript: str,
    speaker_segments: List[Dict] = None,
    prospect_label: str = "Customer",
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Detect and categorize sales objections (context-driven).

    Args:
        transcript: Conversation transcript
        speaker_segments: Speaker-labeled segments
        prospect_label: Prospect speaker label
        context: Playbook context with objection configuration

    Returns:
        Objection analysis with handling strategies
    """
    context = context or {}

    # Get configuration from context
    objection_config = context.get('objection_config', {})
    objection_categories = objection_config.get('categories', DEFAULT_OBJECTION_CATEGORIES)
    handling_strategies = context.get('handling_strategies', {})
    thresholds = objection_config.get('thresholds', DEFAULT_OBJECTION_THRESHOLDS)

    logger.info(
        "Objection detect invoked",
        context_driven=bool(context),
        has_custom_categories=bool(objection_config.get('categories'))
    )

    result = {
        "objections": [],
        "objection_summary": {},
        "objection_severity_score": 0,
        "handling_recommendations": [],
        "requires_manager_support": False,
        "objection_timeline": [],
        "unhandled_objections": [],
        "analysis_timestamp": datetime.now().isoformat(),
        "ai_enhanced": False,
        "context_driven": bool(context)
    }

    if not transcript:
        return result

    transcript_lower = transcript.lower()

    # Get severity multipliers from context
    severity_multipliers = thresholds.get('severity_multipliers', {"high": 3, "medium": 2, "low": 1})

    # Track objections by category
    category_counts = {}
    total_severity = 0

    for category, config in objection_categories.items():
        category_objections = []

        for pattern in config.get("patterns", []):
            matches = re.finditer(pattern, transcript_lower)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(transcript), match.end() + 50)
                match_context = transcript[start:end]

                # Get handling strategies from context override or default
                strategies = handling_strategies.get(category, config.get("handling_strategies", []))

                objection = {
                    "category": category,
                    "matched_text": match.group(),
                    "context": f"...{match_context}...",
                    "position_percent": round((match.start() / len(transcript)) * 100),
                    "severity": config.get("severity", "medium"),
                    "handling_strategies": strategies
                }
                category_objections.append(objection)
                result["objections"].append(objection)

        if category_objections:
            category_severity = len(category_objections) * severity_multipliers.get(config.get("severity", "medium"), 1)
            total_severity += category_severity

            strategies = handling_strategies.get(category, config.get("handling_strategies", []))
            category_counts[category] = {
                "count": len(category_objections),
                "severity": config.get("severity", "medium"),
                "primary_strategy": strategies[0] if strategies else ""
            }

    result["objection_summary"] = category_counts

    # Calculate severity score using context thresholds
    max_severity = len(objection_categories) * 3 * 2  # Assume max 2 objections per category at high severity
    result["objection_severity_score"] = min(100, round((total_severity / max_severity) * 100))

    # Determine if manager support needed using context thresholds
    manager_high_count = thresholds.get('manager_support_high_count', 2)
    manager_severity_score = thresholds.get('manager_support_severity_score', 60)
    high_severity_count = sum(1 for obj in result["objections"] if obj["severity"] == "high")
    result["requires_manager_support"] = high_severity_count >= manager_high_count or result["objection_severity_score"] >= manager_severity_score

    # Generate prioritized handling recommendations
    recommendations = []
    for category, summary in sorted(
        category_counts.items(),
        key=lambda x: severity_multipliers.get(x[1]["severity"], 0),
        reverse=True
    ):
        config = objection_categories.get(category, {})
        strategies = handling_strategies.get(category, config.get("handling_strategies", []))
        recommendations.append({
            "objection_category": category,
            "priority": "high" if config.get("severity") == "high" else "medium",
            "recommended_response": strategies[0] if strategies else "",
            "alternative_strategies": strategies[1:3] if len(strategies) > 1 else []
        })

    max_recommendations = thresholds.get('max_recommendations', 5)
    result["handling_recommendations"] = recommendations[:max_recommendations]

    # Check for unhandled objections using context threshold
    late_position = thresholds.get('late_objection_position', 75)
    late_objections = [
        obj for obj in result["objections"]
        if obj["position_percent"] > late_position
    ]
    if late_objections:
        result["unhandled_objections"] = late_objections

    return result


class ObjectionDetectAction(ApexActionBase):
    name = "objection_detect"
    description = "Identify sales objections"
    category = "sales_intelligence"
    industry = "sales_ai"

    def __init__(self, context: Dict[str, Any] = None):
        super().__init__()
        self.context = context or {}

    def execute(self, **kwargs) -> dict:
        return objection_detect(context=self.context, **kwargs)


@register_factory("objection_detect")
async def objection_detect_factory(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Small Factory handler for objection detection (context-driven).

    Context keys used:
        - objection_config: Objection category configuration
            - categories: Objection patterns and severities
            - thresholds: Manager support and severity thresholds
        - handling_strategies: Custom handling strategies by category
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Objection detect factory invoked",
        context_driven=bool(effective_context)
    )

    result = objection_detect(
        transcript=input_data.get("transcript", ""),
        speaker_segments=input_data.get("speaker_segments"),
        prospect_label=input_data.get("prospect_label", "Customer"),
        context=effective_context
    )

    # AI enhancement
    if input_data.get("use_ai", True) and CLAUDE_ENABLED:
        try:
            claude = get_bedrock_claude_service()
            ai_response = await claude.analyze_conversation(
                transcript=input_data.get("transcript", "")[:2000],
                analysis_type="custom",
                context={
                    "custom_prompt": "Identify sales objections, their root causes, and personalized handling strategies. Format as JSON with keys: hidden_objections, root_causes, personalized_strategies"
                }
            )
            if ai_response:
                result["ai_insights"] = ai_response
                result["ai_enhanced"] = True
        except Exception as e:
            logger.warning("AI objection analysis failed", error=str(e))

    result["factory_id"] = "objection_detect"
    result["factory_version"] = "2.0.0"
    result["context_keys_used"] = ["objection_config", "handling_strategies"]
    return result


def handler(event, lambda_context):
    return objection_detect(**event)
