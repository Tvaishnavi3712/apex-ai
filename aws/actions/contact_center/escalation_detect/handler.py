"""
Escalation Detection Action (Context-Driven)
Detect escalation signals in customer interactions

Context-Driven Architecture:
- Escalation patterns are read from playbook context.escalation_config
- Severity levels are read from context.escalation_config.severity_levels
- Recommended actions are read from context.escalation_config.recommended_actions
- Supervisor alert thresholds are read from context.escalation_config.alert_thresholds

Supports both:
- Small Factory pattern (for voice pipeline chains)
- Standalone Lambda invocation
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
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


# Default escalation patterns (used when context not provided)
DEFAULT_ESCALATION_PATTERNS = {
    "manager_request": {
        "patterns": [
            r"speak\s+to\s+(?:a\s+)?(?:manager|supervisor)",
            r"transfer\s+(?:me\s+)?to\s+(?:a\s+)?(?:manager|supervisor)",
            r"get\s+me\s+(?:a\s+)?(?:manager|supervisor)",
            r"let\s+me\s+speak\s+(?:to|with)"
        ],
        "severity": "high",
        "category": "escalation_request"
    },
    "complaint_threat": {
        "patterns": [
            r"(?:file|make)\s+a\s+complaint",
            r"report\s+(?:you|this)\s+to",
            r"better\s+business\s+bureau",
            r"consumer\s+(?:protection|affairs)"
        ],
        "severity": "high",
        "category": "complaint_threat"
    },
    "legal_threat": {
        "patterns": [
            r"(?:my|a)\s+(?:lawyer|attorney)",
            r"(?:sue|lawsuit|legal\s+action)",
            r"hear\s+from\s+my\s+lawyer"
        ],
        "severity": "critical",
        "category": "legal_threat"
    },
    "cancellation_threat": {
        "patterns": [
            r"cancel\s+(?:my|the)\s+(?:account|service|policy)",
            r"(?:close|closing)\s+my\s+account",
            r"switch(?:ing)?\s+to\s+(?:another|competitor)",
            r"(?:leave|leaving)\s+your\s+(?:company|service)"
        ],
        "severity": "high",
        "category": "churn_risk"
    },
    "emotional_escalation": {
        "patterns": [
            r"(?:this\s+is\s+)?(?:ridiculous|unacceptable|outrageous)",
            r"(?:furious|livid|extremely\s+angry)",
            r"(?:worst|terrible|horrible)\s+(?:experience|service)",
            r"never\s+(?:again|doing\s+business)"
        ],
        "severity": "medium",
        "category": "emotional"
    }
}

# Default severity levels
DEFAULT_SEVERITY_LEVELS = {"low": 0, "medium": 1, "high": 2, "critical": 3}

# Default recommended actions by category
DEFAULT_RECOMMENDED_ACTIONS = {
    "legal_threat": [
        "Immediately transfer to supervisor",
        "Do not make any commitments",
        "Document all statements"
    ],
    "escalation_request": [
        "Acknowledge supervisor request",
        "Attempt resolution before transfer",
        "Provide warm transfer with context"
    ],
    "churn_risk": [
        "Offer retention options if authorized",
        "Empathize with frustration",
        "Explore alternative solutions"
    ],
    "emotional": [
        "Use active listening",
        "Acknowledge emotions",
        "Avoid defensive responses"
    ],
    "complaint_threat": [
        "Resolve issue immediately if possible",
        "Offer goodwill gesture if appropriate",
        "Document interaction thoroughly"
    ]
}

# Default alert thresholds
DEFAULT_ALERT_THRESHOLDS = {
    "supervisor_alert_severity": 2,
    "extreme_negative_sentiment": -0.6,
    "immediate_attention_severities": ["high", "critical"]
}


@register_factory("escalation_detect")
async def escalation_detect_factory(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Small Factory version: Detect escalation signals (context-driven).

    Context keys used:
        - escalation_config: Escalation detection configuration
            - patterns: Escalation patterns by category
            - severity_levels: Severity level mappings
            - recommended_actions: Actions by category
            - alert_thresholds: Thresholds for alerts

    Input:
        sentiment: Sentiment analysis results
        diarize.segments: Labeled conversation segments

    Output:
        escalation_detected: Whether escalation signals detected
        highest_severity: Highest severity level
        signals: List of detected signals
        recommended_actions: Actions for agent/supervisor
        supervisor_alert: Whether to alert supervisor
    """
    # Get context configuration
    context = context or input_data.get('context', {})
    escalation_config = context.get('escalation_config', {})

    # Get patterns from context or use defaults
    escalation_patterns = escalation_config.get('patterns', DEFAULT_ESCALATION_PATTERNS)
    severity_levels = escalation_config.get('severity_levels', DEFAULT_SEVERITY_LEVELS)
    action_templates = escalation_config.get('recommended_actions', DEFAULT_RECOMMENDED_ACTIONS)
    alert_thresholds = escalation_config.get('alert_thresholds', DEFAULT_ALERT_THRESHOLDS)

    logger.info(
        "Escalation detect factory invoked",
        context_driven=bool(context),
        has_custom_patterns=bool(escalation_config.get('patterns'))
    )

    sentiment_output = input_data.get('sentiment', {})
    diarize_output = input_data.get('diarize', {})
    transcribe_output = input_data.get('transcribe', {})
    state = input_data.get('state', {})

    # Get segments
    segments = diarize_output.get('segments', [])
    if not segments:
        segments = transcribe_output.get('segments', [])

    # Get full text as fallback
    full_text = transcribe_output.get('full_text', '')
    if not full_text:
        full_text = state.get('input', {}).get('transcript', {}).get('full_text', '')

    highest_severity_level = 0
    highest_severity = "low"

    signals = []
    categories_found = set()

    # Analyze customer segments
    customer_texts = []
    for seg in segments:
        speaker = seg.get('speaker', '').lower()
        if 'customer' in speaker or 'caller' in speaker:
            customer_texts.append({
                "text": seg.get('text', ''),
                "start_time": seg.get('start_time', 0)
            })

    # If no labeled segments, use full text
    if not customer_texts:
        customer_texts = [{"text": full_text, "start_time": 0}]

    # Check each customer utterance for escalation patterns (from context)
    for utterance in customer_texts:
        text = utterance['text'].lower()

        for pattern_name, pattern_info in escalation_patterns.items():
            patterns_list = pattern_info.get('patterns', [])
            for pattern in patterns_list:
                if re.search(pattern, text):
                    severity = pattern_info.get('severity', 'medium')
                    severity_level = severity_levels.get(severity, 0)

                    signals.append({
                        "type": pattern_name,
                        "category": pattern_info.get('category', 'unknown'),
                        "severity": severity,
                        "timestamp": utterance['start_time'],
                        "text_snippet": text[:100] + "..." if len(text) > 100 else text
                    })

                    categories_found.add(pattern_info.get('category', 'unknown'))

                    if severity_level > highest_severity_level:
                        highest_severity_level = severity_level
                        highest_severity = severity

                    break  # Move to next pattern type

    # Also check sentiment for emotional escalation (using context threshold)
    extreme_negative_threshold = alert_thresholds.get('extreme_negative_sentiment', -0.6)
    negative_peaks = sentiment_output.get('peaks', {}).get('negative_peaks', [])
    for peak in negative_peaks:
        if peak.get('score', 0) < extreme_negative_threshold:
            signals.append({
                "type": "extreme_negative_sentiment",
                "category": "emotional",
                "severity": "medium",
                "timestamp": peak.get('time', 0),
                "text_snippet": "Extreme negative sentiment detected"
            })
            categories_found.add("emotional")
            if highest_severity_level < 1:
                highest_severity_level = 1
                highest_severity = "medium"

    # Generate recommended actions from context
    recommended_actions = []
    for category in categories_found:
        actions = action_templates.get(category, [])
        recommended_actions.extend(actions)

    # Deduplicate actions
    recommended_actions = list(dict.fromkeys(recommended_actions))

    # Determine if supervisor alert needed (using context threshold)
    supervisor_alert_level = alert_thresholds.get('supervisor_alert_severity', 2)
    immediate_severities = alert_thresholds.get('immediate_attention_severities', ['high', 'critical'])
    supervisor_alert = highest_severity_level >= supervisor_alert_level or "legal_threat" in categories_found

    return {
        "escalation_detected": len(signals) > 0,
        "highest_severity": highest_severity,
        "signals": signals,
        "signal_count": len(signals),
        "categories": list(categories_found),
        "recommended_actions": recommended_actions,
        "supervisor_alert": supervisor_alert,
        "requires_immediate_attention": highest_severity in immediate_severities,
        "context_driven": bool(context),
        "factory_id": "escalation_detect",
        "factory_version": "2.0.0",
        "context_keys_used": ["escalation_config"]
    }


# Escalation patterns with severity
ESCALATION_PATTERNS = {
    "manager_request": {
        "patterns": [
            r"speak to (?:a |your )?(?:manager|supervisor)",
            r"transfer me to (?:a |your )?(?:manager|supervisor)",
            r"get me (?:a |your )?(?:manager|supervisor)",
            r"let me speak (?:to |with )(?:someone|a manager)"
        ],
        "severity": "high",
        "category": "escalation_request"
    },
    "complaint_threat": {
        "patterns": [
            r"(?:file|make|report) a complaint",
            r"report (?:you|this) to",
            r"(?:contact|call|email) (?:corporate|headquarters)",
            r"better business bureau|bbb",
            r"consumer (?:protection|affairs)"
        ],
        "severity": "high",
        "category": "complaint_threat"
    },
    "legal_threat": {
        "patterns": [
            r"(?:my |a |the )?(?:lawyer|attorney)",
            r"(?:sue|lawsuit|legal action)",
            r"(?:hear from|contact) my lawyer"
        ],
        "severity": "critical",
        "category": "legal_threat"
    },
    "social_media_threat": {
        "patterns": [
            r"(?:post|put|share) (?:this |it )?(?:on |to )?(?:social media|twitter|facebook|instagram|yelp)",
            r"go viral",
            r"(?:negative |bad )?(?:review|reviews)"
        ],
        "severity": "medium",
        "category": "social_media_threat"
    },
    "cancellation_threat": {
        "patterns": [
            r"cancel (?:my |the )?(?:account|service|subscription|membership)",
            r"(?:close|closing) my account",
            r"(?:switch|switching) to (?:another|competitor|your competitor)",
            r"(?:leave|leaving) your (?:company|service)"
        ],
        "severity": "high",
        "category": "churn_risk"
    },
    "emotional_escalation": {
        "patterns": [
            r"(?:this is |you(?:'re| are) )?(?:ridiculous|unacceptable|outrageous)",
            r"(?:i(?:'m| am) )?(?:furious|livid|extremely angry)",
            r"(?:worst|terrible|horrible) (?:experience|service|company)",
            r"(?:never|ever) (?:again|doing business)"
        ],
        "severity": "medium",
        "category": "emotional"
    }
}


@apex_action(ApexActionSchema(
    name="escalation_detect",
    description="Detect escalation signals in customer interactions",
    category="real_time",
    industry="contact_center",
    input_schema=ActionInputSchema(description="Escalation detection parameters")
        .add_string("interaction_id", "Interaction/call ID", required=True)
        .add_array("utterances", "List of utterances with speaker and text", required=True)
        .add_boolean("real_time", "Whether this is real-time detection", required=False),
    output_schema=ActionOutputSchema(description="Escalation detection result")
        .add_boolean("escalation_detected", "Whether escalation signals detected")
        .add_string("highest_severity", "Highest severity detected: low, medium, high, critical")
        .add_array("signals", "Escalation signals detected")
        .add_array("recommended_actions", "Recommended actions for agent/supervisor")
        .add_boolean("supervisor_alert", "Whether supervisor should be alerted")
))
def escalation_detect(
    interaction_id: str,
    utterances: List[Dict],
    real_time: bool = False
) -> dict:
    """
    Detect escalation signals

    Args:
        interaction_id: Interaction ID
        utterances: List of utterances
        real_time: Real-time detection mode

    Returns:
        Escalation detection results
    """
    result = {
        "interaction_id": interaction_id,
        "escalation_detected": False,
        "highest_severity": "low",
        "signals": [],
        "recommended_actions": [],
        "supervisor_alert": False,
        "detection_date": datetime.now().isoformat()
    }

    severity_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    highest_severity_level = 0

    # Analyze customer utterances
    customer_utterances = [
        u for u in utterances
        if u.get("speaker", "").lower() in ["customer", "caller", "member"]
    ]

    for utterance in customer_utterances:
        text = utterance.get("text", "").lower()
        position = utterance.get("position", 0)

        for pattern_name, pattern_info in ESCALATION_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, text):
                    severity = pattern_info["severity"]
                    severity_level = severity_levels.get(severity, 0)

                    result["signals"].append({
                        "type": pattern_name,
                        "category": pattern_info["category"],
                        "severity": severity,
                        "text_snippet": text[:100],
                        "position": position,
                        "real_time": real_time
                    })

                    if severity_level > highest_severity_level:
                        highest_severity_level = severity_level
                        result["highest_severity"] = severity

                    result["escalation_detected"] = True
                    break  # Move to next pattern type

    # Generate recommended actions
    if result["escalation_detected"]:
        categories = set(s["category"] for s in result["signals"])

        if "legal_threat" in categories:
            result["supervisor_alert"] = True
            result["recommended_actions"].extend([
                "Immediately transfer to supervisor",
                "Do not make any commitments",
                "Document all statements carefully"
            ])

        if "escalation_request" in categories:
            result["supervisor_alert"] = True
            result["recommended_actions"].extend([
                "Acknowledge request for supervisor",
                "Attempt to resolve before transfer if appropriate",
                "Provide warm transfer with context"
            ])

        if "churn_risk" in categories:
            result["recommended_actions"].extend([
                "Offer retention incentives if authorized",
                "Empathize with customer frustration",
                "Explore alternative solutions"
            ])

        if "emotional" in categories:
            result["recommended_actions"].extend([
                "Use active listening techniques",
                "Acknowledge customer emotions",
                "Avoid defensive responses"
            ])

        if "complaint_threat" in categories or "social_media_threat" in categories:
            result["recommended_actions"].extend([
                "Attempt to resolve issue immediately",
                "Offer goodwill gesture if appropriate",
                "Document interaction thoroughly"
            ])

        # Alert supervisor for high/critical
        if highest_severity_level >= 2:
            result["supervisor_alert"] = True

    return result


class EscalationDetectAction(ApexActionBase):
    """Escalation Detection Action (class-based)"""

    name = "escalation_detect"
    description = "Detect escalation signals"
    category = "real_time"
    industry = "contact_center"

    def execute(self, **kwargs) -> dict:
        return escalation_detect(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return escalation_detect(**event)
