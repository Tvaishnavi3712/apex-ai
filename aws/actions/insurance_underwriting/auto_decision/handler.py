"""
Auto Decision Action
Make automated underwriting decisions based on rules and scoring

Supports both:
- Small Factory pattern (for voice pipeline chains)
- Standalone Lambda invocation
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

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


@register_factory("auto_decision")
async def auto_decision_factory(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Small Factory version: Make automated decision on claim routing.

    Input:
        priority: Priority calculation results
        fraud: Fraud detection results
        config.auto_approve_threshold: Score threshold for auto-approval
        config.fraud_block_threshold: Score threshold to block for fraud
        config.escalation_rules: Rules for escalation

    Output:
        decision: approve/deny/escalate/review
        routing: Where to route the claim
        reason: Decision reasoning
    """
    config = input_data.get('config', {})
    priority_output = input_data.get('priority', {})
    fraud_output = input_data.get('fraud', {})
    claim_output = input_data.get('claim', {})
    compliance_output = input_data.get('compliance', {})

    auto_approve_threshold = config.get('auto_approve_threshold', 85)
    fraud_block_threshold = config.get('fraud_block_threshold', 70)
    escalation_rules = config.get('escalation_rules', {})

    priority_score = priority_output.get('priority_score', 50)
    priority_level = priority_output.get('priority_level', 'medium')
    fraud_score = fraud_output.get('fraud_score', 0)
    fraud_risk = fraud_output.get('risk_level', 'low')
    compliance_passed = compliance_output.get('passed', True)
    compliance_score = compliance_output.get('overall_score', 100)

    # Parse damage amount
    damage_amount_str = claim_output.get('extracted_entities', {}).get('damage_amount', '$0')
    try:
        damage_amount = float(str(damage_amount_str).replace('$', '').replace(',', ''))
    except (ValueError, AttributeError):
        damage_amount = 0

    decision = None
    routing = None
    reasons = []
    flags = []
    confidence = 0.0

    high_value_threshold = escalation_rules.get('high_value_claim', 50000)
    compliance_violation_threshold = escalation_rules.get('compliance_violations', 2)

    # Decision logic
    if fraud_score >= fraud_block_threshold:
        decision = "deny"
        routing = "siu"
        reasons.append(f"Fraud score ({fraud_score}) exceeds threshold")
        flags.append("high_fraud_risk")
        confidence = 0.9
    elif damage_amount > high_value_threshold:
        decision = "escalate"
        routing = "senior_adjuster"
        reasons.append(f"Claim value exceeds auto-approval limit")
        flags.append("high_value")
        confidence = 0.85
    elif not compliance_passed:
        violation_count = compliance_output.get('violation_count', 0)
        if violation_count >= compliance_violation_threshold:
            decision = "escalate"
            routing = "compliance_review"
            reasons.append(f"Compliance violations require review")
            flags.append("compliance_issues")
            confidence = 0.8
    elif priority_level in ["critical", "high"]:
        decision = "escalate"
        routing = "priority_queue"
        reasons.append(f"High priority requires expedited handling")
        flags.append("high_priority")
        confidence = 0.85
    elif fraud_risk == "low" and claim_output.get('is_actionable', False):
        completeness = claim_output.get('completeness_score', 0)
        if completeness >= 0.7 and priority_score <= auto_approve_threshold:
            decision = "approve"
            routing = "auto_processing"
            reasons.append("Meets criteria for auto-approval")
            confidence = 0.9
        else:
            decision = "review"
            routing = "standard_queue"
            reasons.append("Claim requires standard review")
            confidence = 0.75
    else:
        decision = "review"
        routing = "standard_queue"
        reasons.append("Does not meet criteria for auto-decision")
        confidence = 0.7

    routing_details = {
        "auto_processing": {"queue": "auto_approve_queue", "sla_hours": 4, "handler": "automated"},
        "standard_queue": {"queue": "adjuster_queue", "sla_hours": 24, "handler": "adjuster"},
        "priority_queue": {"queue": "priority_queue", "sla_hours": 8, "handler": "senior_adjuster"},
        "senior_adjuster": {"queue": "senior_adjuster_queue", "sla_hours": 12, "handler": "senior_adjuster"},
        "compliance_review": {"queue": "compliance_queue", "sla_hours": 48, "handler": "compliance_team"},
        "siu": {"queue": "siu_queue", "sla_hours": 72, "handler": "fraud_investigator"}
    }

    return {
        "decision": decision,
        "routing": routing,
        "route_details": routing_details.get(routing, routing_details["standard_queue"]),
        "reasons": reasons,
        "flags": flags,
        "confidence": round(confidence, 2),
        "automation_eligible": decision == "approve",
        "requires_human_review": decision in ["review", "escalate", "deny"],
        "priority_level": priority_level,
        "fraud_risk_level": fraud_risk,
        "scores": {"priority": priority_score, "fraud": fraud_score, "compliance": compliance_score}
    }


# Original Lambda-style handler below


@apex_action(ApexActionSchema(
    name="auto_decision",
    description="Make automated underwriting decisions based on rules and scoring",
    category="underwriting",
    industry="insurance_underwriting",
    input_schema=ActionInputSchema(description="Auto decision parameters")
        .add_string("application_id", "Application identifier", required=True)
        .add_string("line_of_business", "Insurance line", required=True)
        .add_number("risk_score", "Risk score", required=True)
        .add_string("risk_tier", "Risk tier", required=True)
        .add_boolean("coverage_valid", "Whether coverage is valid", required=True)
        .add_boolean("adverse_history", "Whether adverse loss history exists", required=True)
        .add_number("premium", "Calculated premium", required=True)
        .add_array("underwriting_flags", "Flags from underwriting process", required=False),
    output_schema=ActionOutputSchema(description="Auto decision result")
        .add_string("decision", "Decision: approve, decline, refer")
        .add_string("decision_code", "Decision code")
        .add_array("decision_factors", "Factors influencing decision")
        .add_boolean("auto_approved", "Whether auto-approved without review")
        .add_string("referral_reason", "Reason for referral if applicable")
        .add_object("conditions", "Conditions for approval if any")
))
def auto_decision(
    application_id: str,
    line_of_business: str,
    risk_score: int,
    risk_tier: str,
    coverage_valid: bool,
    adverse_history: bool,
    premium: float,
    underwriting_flags: List[str] = None
) -> dict:
    """
    Make automated underwriting decision

    Args:
        application_id: Application ID
        line_of_business: Line of business
        risk_score: Risk score
        risk_tier: Risk tier
        coverage_valid: Coverage validity
        adverse_history: Adverse history flag
        premium: Calculated premium
        underwriting_flags: UW flags

    Returns:
        Underwriting decision
    """
    underwriting_flags = underwriting_flags or []

    result = {
        "application_id": application_id,
        "decision": "refer",
        "decision_code": "REF",
        "decision_factors": [],
        "auto_approved": False,
        "referral_reason": None,
        "conditions": {},
        "decision_date": datetime.now().isoformat()
    }

    # Automatic decline conditions
    decline_reasons = []

    if risk_tier == "decline":
        decline_reasons.append("Risk tier indicates decline")

    if not coverage_valid:
        decline_reasons.append("Coverage validation failed")

    if risk_score > 900:
        decline_reasons.append("Risk score exceeds threshold")

    # Check for specific flags
    hard_decline_flags = ["dui_recent", "fraud_indicator", "material_misrepresentation"]
    for flag in underwriting_flags:
        if flag.lower() in hard_decline_flags:
            decline_reasons.append(f"Hard decline flag: {flag}")

    if decline_reasons:
        result["decision"] = "decline"
        result["decision_code"] = "DEC"
        result["decision_factors"] = decline_reasons
        return result

    # Referral conditions
    refer_reasons = []

    if risk_tier == "substandard":
        refer_reasons.append("Substandard risk tier requires review")

    if adverse_history:
        refer_reasons.append("Adverse loss history requires review")

    if premium > 10000:
        refer_reasons.append("High premium requires review")

    # Check for soft flags requiring review
    soft_flags = ["new_business_large", "coverage_exception", "prior_decline"]
    for flag in underwriting_flags:
        if flag.lower() in soft_flags:
            refer_reasons.append(f"Referral flag: {flag}")

    if line_of_business == "commercial":
        refer_reasons.append("Commercial lines require underwriter review")

    if refer_reasons:
        result["decision"] = "refer"
        result["decision_code"] = "REF"
        result["decision_factors"] = refer_reasons
        result["referral_reason"] = refer_reasons[0]
        return result

    # Auto-approve conditions
    if (risk_tier in ["preferred", "standard"] and
        not adverse_history and
        coverage_valid and
        risk_score <= 600 and
        not underwriting_flags):

        result["decision"] = "approve"
        result["decision_code"] = "APP"
        result["auto_approved"] = True
        result["decision_factors"] = [
            "Risk score within auto-approve threshold",
            "No adverse loss history",
            "Coverage validated",
            "No underwriting flags"
        ]

        # Add standard conditions
        result["conditions"] = {
            "inspection_required": premium > 5000,
            "photos_required": line_of_business == "home",
            "mvr_current": line_of_business == "auto"
        }

        return result

    # Default to refer
    result["decision"] = "refer"
    result["decision_code"] = "REF"
    result["referral_reason"] = "Does not meet auto-approval criteria"
    result["decision_factors"] = ["Application requires underwriter review"]

    return result


class AutoDecisionAction(ApexActionBase):
    """Auto Decision Action (class-based)"""

    name = "auto_decision"
    description = "Make automated underwriting decisions"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return auto_decision(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return auto_decision(**event)
