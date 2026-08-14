"""
Compliance Check Action (Context-Driven)
Check call transcripts for regulatory and company compliance

Context-Driven Architecture:
- Compliance rules are read from playbook context.compliance_config
- Rule weights are read from context.compliance_config.rules
- Critical checks list is read from context.compliance_config.critical_checks
- Compliance thresholds are read from context.compliance_config.thresholds

Supports both:
- Lambda invocation (standalone)
- Small Factory pattern (chain processing)
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


# Default compliance rules (used when context not provided)
DEFAULT_COMPLIANCE_RULES = {
    "greeting": {
        "required_elements": ["company name", "agent name"],
        "patterns": [r"thank you for calling", r"my name is", r"how may i help"],
        "weight": 10
    },
    "verification": {
        "required_elements": ["identity verification"],
        "patterns": [r"verify your", r"confirm your", r"date of birth", r"last four", r"security question"],
        "weight": 20
    },
    "disclosure": {
        "required_elements": ["call recording disclosure"],
        "patterns": [r"call may be recorded", r"call is being recorded", r"monitoring purposes"],
        "weight": 15
    },
    "mini_miranda": {
        "required_elements": ["debt collection disclosure"],
        "patterns": [r"attempt to collect a debt", r"debt collector", r"information will be used"],
        "weight": 25,
        "applies_to": ["collections"]
    },
    "pii_protection": {
        "prohibited_patterns": [r"\b\d{9}\b", r"\b\d{3}-\d{2}-\d{4}\b"],  # Full SSN patterns
        "description": "Full SSN should not be stated aloud",
        "weight": 30
    },
    "closing": {
        "required_elements": ["closing statement"],
        "patterns": [r"anything else", r"is there anything", r"thank you for calling", r"have a great day"],
        "weight": 10
    }
}

# Default critical checks
DEFAULT_CRITICAL_CHECKS = ["verification", "disclosure", "mini_miranda"]

# Default compliance thresholds
DEFAULT_COMPLIANCE_THRESHOLDS = {
    "compliant_score_minimum": 80,
    "warning_score_minimum": 60,
    "violation_severity_weights": {
        "low": 5,
        "medium": 10,
        "high": 20
    }
}


@apex_action(ApexActionSchema(
    name="compliance_check",
    description="Check call transcripts for regulatory and company compliance",
    category="quality",
    industry="contact_center",
    input_schema=ActionInputSchema(description="Compliance check parameters")
        .add_string("interaction_id", "Interaction/call ID", required=True)
        .add_array("utterances", "List of utterances with speaker and text", required=True)
        .add_string("call_type", "Call type: service, sales, collections", required=True)
        .add_array("required_disclosures", "Required disclosures for this call type", required=False)
        .add_object("context", "Playbook context with compliance configuration", required=False),
    output_schema=ActionOutputSchema(description="Compliance check result")
        .add_boolean("compliant", "Whether call is compliant")
        .add_number("compliance_score", "Compliance score 0-100")
        .add_array("passed_checks", "Compliance checks that passed")
        .add_array("failed_checks", "Compliance checks that failed")
        .add_array("violations", "Compliance violations found")
        .add_array("recommendations", "Recommendations for improvement")
))
def compliance_check(
    interaction_id: str,
    utterances: List[Dict],
    call_type: str,
    required_disclosures: List[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Check compliance in interaction (context-driven).

    Args:
        interaction_id: Interaction ID
        utterances: List of utterances
        call_type: Type of call
        required_disclosures: Required disclosures
        context: Playbook context with compliance configuration

    Context keys used:
        - compliance_config: Compliance check configuration
            - rules: Compliance rules with patterns and weights
            - critical_checks: List of critical check names
            - thresholds: Compliance score thresholds

    Returns:
        Compliance check results
    """
    required_disclosures = required_disclosures or []
    context = context or {}

    # Get configuration from context
    compliance_config = context.get('compliance_config', {})
    compliance_rules = compliance_config.get('rules', DEFAULT_COMPLIANCE_RULES)
    critical_checks = compliance_config.get('critical_checks', DEFAULT_CRITICAL_CHECKS)
    thresholds = compliance_config.get('thresholds', DEFAULT_COMPLIANCE_THRESHOLDS)

    logger.info(
        "Compliance check invoked",
        context_driven=bool(context),
        has_custom_rules=bool(compliance_config.get('rules'))
    )

    result = {
        "interaction_id": interaction_id,
        "call_type": call_type,
        "compliant": True,
        "compliance_score": 100,
        "passed_checks": [],
        "failed_checks": [],
        "violations": [],
        "recommendations": [],
        "check_date": datetime.now().isoformat(),
        "context_driven": bool(context)
    }

    # Combine all text
    full_transcript = " ".join([u.get("text", "").lower() for u in utterances])
    agent_text = " ".join([
        u.get("text", "").lower()
        for u in utterances
        if u.get("speaker", "").lower() in ["agent", "representative"]
    ])

    total_weight = 0
    earned_weight = 0

    for rule_name, rule in compliance_rules.items():
        # Check if rule applies to this call type
        applies_to = rule.get("applies_to")
        if applies_to and call_type not in applies_to:
            continue

        weight = rule.get("weight", 10)
        total_weight += weight

        # Check for prohibited patterns
        if "prohibited_patterns" in rule:
            for pattern in rule["prohibited_patterns"]:
                if re.search(pattern, full_transcript):
                    result["violations"].append({
                        "rule": rule_name,
                        "description": rule.get("description", "Prohibited content found"),
                        "severity": "high"
                    })
                    result["compliant"] = False
                    result["failed_checks"].append({
                        "check": rule_name,
                        "reason": rule.get("description")
                    })
                    continue

        # Check for required patterns
        if "patterns" in rule:
            found = False
            for pattern in rule["patterns"]:
                if re.search(pattern, agent_text):
                    found = True
                    break

            if found:
                earned_weight += weight
                result["passed_checks"].append({
                    "check": rule_name,
                    "elements": rule.get("required_elements", [])
                })
            else:
                result["failed_checks"].append({
                    "check": rule_name,
                    "required": rule.get("required_elements", []),
                    "reason": "Required element not detected"
                })
                result["recommendations"].append(
                    f"Ensure {rule_name} is completed: {', '.join(rule.get('required_elements', []))}"
                )

    # Calculate score
    if total_weight > 0:
        result["compliance_score"] = round((earned_weight / total_weight) * 100, 1)

    # Check for violations - set compliant to false if any
    if result["violations"]:
        result["compliant"] = False

    # Check for critical failures using context-driven critical checks
    for check in result["failed_checks"]:
        if check.get("check") in critical_checks:
            result["compliant"] = False
            break

    return result


class ComplianceCheckAction(ApexActionBase):
    """Compliance Check Action (class-based)"""

    name = "compliance_check"
    description = "Check call compliance"
    category = "quality"
    industry = "contact_center"

    def execute(self, **kwargs) -> dict:
        return compliance_check(**kwargs)


# Small Factory registration
@register_factory("compliance_check")
async def compliance_check_factory(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Small Factory handler for compliance checking (context-driven).

    Context keys used:
        - compliance_config: Compliance check configuration
            - rules: Compliance rules with patterns and weights
            - critical_checks: List of critical check names
            - thresholds: Compliance score thresholds

    Expected input_data:
        - interaction_id: Interaction/call ID
        - utterances: List of utterances with speaker and text
        - call_type: Call type (service, sales, collections)
        - required_disclosures: Required disclosures for this call type (optional)

    Returns:
        Compliance check results with score and recommendations
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Compliance check factory invoked",
        context_driven=bool(effective_context)
    )

    result = compliance_check(
        interaction_id=input_data.get("interaction_id", ""),
        utterances=input_data.get("utterances", []),
        call_type=input_data.get("call_type", "service"),
        required_disclosures=input_data.get("required_disclosures"),
        context=effective_context
    )

    result["context_driven"] = bool(effective_context)
    result["factory_id"] = "compliance_check"
    result["factory_version"] = "2.0.0"
    result["context_keys_used"] = ["compliance_config"]

    return result


def handler(event, context):
    """Lambda entry point"""
    return compliance_check(**event)
