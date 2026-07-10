"""
Fraud Detection Action
Analyze claims for potential fraud, waste, and abuse indicators

Context-Driven Architecture:
- CCI edits (unbundling rules) are read from playbook context.cci_edits
- Fraud detection rules/weights are read from playbook context.fraud_detection_rules
- Upcoding patterns are read from playbook context.fraud_detection_rules.upcoding_patterns
"""

import boto3
from boto3.dynamodb.conditions import Key
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog

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

logger = structlog.get_logger()


# Default fraud indicator weights (used when context not provided)
DEFAULT_FRAUD_WEIGHTS = {
    "unbundling": 20,
    "upcoding": 25,
    "duplicate_billing": 30,
    "impossible_day": 35,
    "phantom_billing": 40,
    "excessive_frequency": 15,
    "geographic_anomaly": 10,
    "provider_pattern": 20
}


@apex_action(ApexActionSchema(
    name="fraud_detection",
    description="Analyze claims for potential fraud, waste, and abuse indicators",
    category="fraud",
    industry="healthcare_payers",
    input_schema=ActionInputSchema(description="Fraud detection parameters")
        .add_string("claim_id", "Claim identifier", required=True)
        .add_string("member_id", "Member ID", required=True)
        .add_string("provider_npi", "Provider NPI", required=True)
        .add_string("service_date", "Date of service", required=True)
        .add_array("procedure_codes", "Procedure codes on claim", required=True)
        .add_number("billed_amount", "Total billed amount", required=True)
        .add_array("diagnosis_codes", "Diagnosis codes", required=False)
        .add_number("units", "Total units billed", required=False)
        .add_object("context", "Playbook context with fraud_detection_rules and cci_edits", required=False),
    output_schema=ActionOutputSchema(description="Fraud detection result")
        .add_number("fraud_score", "Fraud risk score 0-100")
        .add_string("risk_level", "Risk level: low, medium, high, critical")
        .add_boolean("requires_review", "Whether manual review is required")
        .add_array("indicators", "Fraud indicators detected")
        .add_array("recommendations", "Recommended actions")
))
def fraud_detection(
    claim_id: str,
    member_id: str,
    provider_npi: str,
    service_date: str,
    procedure_codes: List[str],
    billed_amount: float,
    diagnosis_codes: List[str] = None,
    units: int = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Detect potential fraud indicators in a claim using context-driven rules

    Args:
        claim_id: Claim identifier
        member_id: Member ID
        provider_npi: Provider NPI
        service_date: Date of service
        procedure_codes: Procedure codes
        billed_amount: Billed amount
        diagnosis_codes: Diagnosis codes
        units: Units billed
        context: Playbook context containing fraud_detection_rules and cci_edits

    Returns:
        Fraud analysis results
    """
    context = context or {}
    diagnosis_codes = diagnosis_codes or []
    units = units or len(procedure_codes)

    # Get fraud detection rules from context
    fraud_rules = context.get("fraud_detection_rules", {})
    cci_edits = context.get("cci_edits", {})

    # Get weights from context or use defaults
    fraud_weights = _get_fraud_weights(fraud_rules)

    result = {
        "claim_id": claim_id,
        "fraud_score": 0,
        "risk_level": "low",
        "requires_review": False,
        "indicators": [],
        "recommendations": [],
        "analysis_date": datetime.now().isoformat(),
        "context_driven": bool(context)
    }

    total_score = 0

    # Check for unbundling using CCI edits from context
    unbundling_result = _check_unbundling_context(procedure_codes, cci_edits)
    if unbundling_result["detected"]:
        weight = fraud_weights.get("unbundling", DEFAULT_FRAUD_WEIGHTS["unbundling"])
        total_score += weight
        result["indicators"].append({
            "type": "unbundling",
            "description": unbundling_result["description"],
            "rule_source": unbundling_result.get("rule_source", "default"),
            "weight": weight
        })

    # Check for upcoding patterns from context
    upcoding_result = _check_upcoding_context(provider_npi, procedure_codes, fraud_rules)
    if upcoding_result["detected"]:
        weight = fraud_weights.get("upcoding", DEFAULT_FRAUD_WEIGHTS["upcoding"])
        total_score += weight
        result["indicators"].append({
            "type": "upcoding",
            "description": upcoding_result["description"],
            "weight": weight
        })

    # Check for duplicate billing
    duplicate_result = _check_duplicate(member_id, service_date, procedure_codes, claim_id)
    if duplicate_result["detected"]:
        weight = fraud_weights.get("duplicate_billing", DEFAULT_FRAUD_WEIGHTS["duplicate_billing"])
        total_score += weight
        result["indicators"].append({
            "type": "duplicate_billing",
            "description": duplicate_result["description"],
            "weight": weight
        })

    # Check for impossible day using context thresholds
    impossible_day_result = _check_impossible_day_context(provider_npi, service_date, units, fraud_rules)
    if impossible_day_result["detected"]:
        weight = fraud_weights.get("impossible_day", DEFAULT_FRAUD_WEIGHTS["impossible_day"])
        total_score += weight
        result["indicators"].append({
            "type": "impossible_day",
            "description": impossible_day_result["description"],
            "weight": weight
        })

    # Check for excessive frequency
    frequency_result = _check_frequency(member_id, procedure_codes)
    if frequency_result["detected"]:
        weight = fraud_weights.get("excessive_frequency", DEFAULT_FRAUD_WEIGHTS["excessive_frequency"])
        total_score += weight
        result["indicators"].append({
            "type": "excessive_frequency",
            "description": frequency_result["description"],
            "weight": weight
        })

    # Check billed amount anomaly using context thresholds
    amount_threshold = fraud_rules.get("amount_anomaly_threshold", 10000)
    if billed_amount > amount_threshold:
        amount_anomaly = _check_amount_anomaly(procedure_codes, billed_amount)
        if amount_anomaly["detected"]:
            weight = fraud_weights.get("amount_anomaly", 15)
            total_score += weight
            result["indicators"].append({
                "type": "amount_anomaly",
                "description": amount_anomaly["description"],
                "weight": weight
            })

    # Calculate final score (cap at 100)
    result["fraud_score"] = min(total_score, 100)

    # Determine risk level using context thresholds
    risk_thresholds = fraud_rules.get("risk_thresholds", {
        "critical": 70,
        "high": 50,
        "medium": 25
    })

    if result["fraud_score"] >= risk_thresholds.get("critical", 70):
        result["risk_level"] = "critical"
        result["requires_review"] = True
        result["recommendations"].append("Immediate SIU referral required")
        result["recommendations"].append("Hold payment pending investigation")
    elif result["fraud_score"] >= risk_thresholds.get("high", 50):
        result["risk_level"] = "high"
        result["requires_review"] = True
        result["recommendations"].append("Route to fraud investigation queue")
        result["recommendations"].append("Request additional documentation")
    elif result["fraud_score"] >= risk_thresholds.get("medium", 25):
        result["risk_level"] = "medium"
        result["requires_review"] = True
        result["recommendations"].append("Flag for post-payment review")
    else:
        result["risk_level"] = "low"
        result["recommendations"].append("Process normally")

    return result


def _get_fraud_weights(fraud_rules: Dict[str, Any]) -> Dict[str, int]:
    """Get fraud indicator weights from context rules."""
    weights = dict(DEFAULT_FRAUD_WEIGHTS)

    # Override with context-provided weights
    if "indicator_weights" in fraud_rules:
        for indicator, weight in fraud_rules["indicator_weights"].items():
            weights[indicator] = int(weight)

    return weights


def _check_unbundling_context(procedure_codes: List[str], cci_edits: Dict[str, Any]) -> dict:
    """Check for procedure code unbundling using context CCI edits."""
    # Try to use CCI edits from context
    if cci_edits:
        # Check E&M with procedures
        em_edits = cci_edits.get("em_with_procedures", {})
        for category, rule in em_edits.items():
            if isinstance(rule, dict):
                primary_codes = rule.get("primary_codes", [])
                cannot_bill_with = rule.get("cannot_bill_same_encounter", [])
                for primary in primary_codes:
                    if primary in procedure_codes:
                        for blocked in cannot_bill_with:
                            if blocked in procedure_codes:
                                return {
                                    "detected": True,
                                    "description": f"CCI edit violation: {primary} cannot bill with {blocked}",
                                    "rule_source": f"context.cci_edits.em_with_procedures.{category}"
                                }

        # Check lab panel unbundling
        lab_edits = cci_edits.get("lab_panels", {})
        for panel, rule in lab_edits.items():
            if isinstance(rule, dict):
                panel_code = rule.get("panel_code", "")
                components = rule.get("component_codes", [])
                if panel_code in procedure_codes:
                    for comp in components:
                        if comp in procedure_codes:
                            return {
                                "detected": True,
                                "description": f"Lab unbundling: {comp} is component of panel {panel_code}",
                                "rule_source": f"context.cci_edits.lab_panels.{panel}"
                            }

        # Check surgical unbundling
        surgical_edits = cci_edits.get("surgical_unbundling", {})
        for rule_name, rule in surgical_edits.items():
            if isinstance(rule, dict):
                primary = rule.get("primary_code", "")
                bundled = rule.get("bundled_codes", [])
                if primary in procedure_codes:
                    for bundled_code in bundled:
                        if bundled_code in procedure_codes:
                            return {
                                "detected": True,
                                "description": f"Surgical unbundling: {bundled_code} bundled into {primary}",
                                "rule_source": f"context.cci_edits.surgical_unbundling.{rule_name}"
                            }

    # Fallback to default unbundle pairs
    default_unbundle_pairs = [
        ("99213", "99214"),
        ("99214", "99215"),
        ("93000", "93005"),
        ("93005", "93010"),
        ("36415", "36416")
    ]

    for code1, code2 in default_unbundle_pairs:
        if code1 in procedure_codes and code2 in procedure_codes:
            return {
                "detected": True,
                "description": f"Potential unbundling: {code1} and {code2} billed together",
                "rule_source": "default"
            }

    return {"detected": False}


def _check_upcoding_context(provider_npi: str, procedure_codes: List[str], fraud_rules: Dict[str, Any]) -> dict:
    """Check for upcoding patterns using context rules."""
    # Get upcoding patterns from context
    upcoding_patterns = fraud_rules.get("upcoding_patterns", {})

    if upcoding_patterns:
        # Check high-level E&M from context
        high_level_em = upcoding_patterns.get("high_level_em", {})
        if high_level_em:
            codes = high_level_em.get("codes", [])
            threshold = high_level_em.get("max_per_claim", 1)
            high_level_count = sum(1 for code in procedure_codes if code in codes)
            if high_level_count > threshold:
                return {
                    "detected": True,
                    "description": f"Multiple high-level E&M codes ({high_level_count}) exceeds threshold ({threshold})"
                }

        # Check for systematic upcoding patterns
        level_progressions = upcoding_patterns.get("level_progressions", [])
        for progression in level_progressions:
            if isinstance(progression, dict):
                suspicious_pattern = progression.get("pattern", [])
                if len(suspicious_pattern) >= 2:
                    matches = sum(1 for code in procedure_codes if code in suspicious_pattern)
                    if matches >= 2:
                        return {
                            "detected": True,
                            "description": f"Upcoding pattern detected: multiple levels billed together"
                        }

    # Fallback to default check
    default_high_level_codes = ["99215", "99205", "99245"]
    high_level_count = sum(1 for code in procedure_codes if code in default_high_level_codes)

    if high_level_count >= 2:
        return {
            "detected": True,
            "description": f"Multiple high-level E&M codes ({high_level_count}) on single claim"
        }

    return {"detected": False}


def _check_duplicate(member_id: str, service_date: str, procedures: List[str], claim_id: str) -> dict:
    """Check for duplicate claim submission"""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('CLAIMS_TABLE', 'apex-claims'))

        response = table.query(
            IndexName='member-service-date-index',
            KeyConditionExpression=Key('member_id').eq(member_id) & Key('service_date').eq(service_date)
        )

        for existing in response.get('Items', []):
            if existing.get('claim_id') != claim_id:
                existing_procs = existing.get('procedure_codes', [])
                overlap = set(procedures) & set(existing_procs)
                if overlap:
                    return {
                        "detected": True,
                        "description": f"Duplicate procedures found: {', '.join(overlap)}"
                    }
    except Exception:
        pass

    return {"detected": False}


def _check_impossible_day_context(provider_npi: str, service_date: str, units: int, fraud_rules: Dict[str, Any]) -> dict:
    """Check for impossible day using context thresholds."""
    # Get impossible day rules from context
    impossible_day_rules = fraud_rules.get("impossible_day", {})

    if impossible_day_rules:
        max_units = impossible_day_rules.get("max_units_per_day", 50)
        max_procedures = impossible_day_rules.get("max_procedures_per_day", 30)

        if units > max_units:
            return {
                "detected": True,
                "description": f"Excessive units ({units}) exceeds threshold ({max_units})"
            }
    else:
        # Default check
        if units > 50:
            return {
                "detected": True,
                "description": f"Excessive units ({units}) for single date of service"
            }

    return {"detected": False}


def _check_frequency(member_id: str, procedure_codes: List[str]) -> dict:
    """Check for excessive service frequency"""
    # This would query historical claims for frequency analysis
    # Simplified implementation
    return {"detected": False}


def _check_amount_anomaly(procedure_codes: List[str], billed_amount: float) -> dict:
    """Check for billed amount anomalies"""
    # Simple check - high amount for number of procedures
    avg_per_proc = billed_amount / max(len(procedure_codes), 1)

    if avg_per_proc > 5000:
        return {
            "detected": True,
            "description": f"High average amount per procedure: ${avg_per_proc:.2f}"
        }

    return {"detected": False}


class FraudDetectionAction(ApexActionBase):
    """Fraud Detection Action (class-based)"""

    name = "fraud_detection"
    description = "Analyze claims for fraud indicators"
    category = "fraud"
    industry = "healthcare_payers"

    def execute(self, **kwargs) -> dict:
        return fraud_detection(**kwargs)


# Small Factory registration
@register_factory("fraud_detection")
async def fraud_detection_factory(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Small Factory handler for fraud detection (context-driven).

    Expected input_data:
        - claim_id: Claim identifier
        - member_id: Member ID
        - provider_npi: Provider NPI
        - service_date: Date of service
        - procedure_codes: List of procedure codes
        - billed_amount: Billed amount
        - diagnosis_codes: Diagnosis codes (optional)
        - units: Units billed (optional)

    Context keys used:
        - fraud_detection_rules: Weights, thresholds, patterns
        - cci_edits: CCI unbundling rules

    Returns:
        Fraud analysis results with risk score
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Fraud detection factory invoked",
        claim_id=input_data.get("claim_id"),
        context_driven=bool(effective_context)
    )

    result = fraud_detection(
        claim_id=input_data.get("claim_id", ""),
        member_id=input_data.get("member_id", ""),
        provider_npi=input_data.get("provider_npi", ""),
        service_date=input_data.get("service_date", ""),
        procedure_codes=input_data.get("procedure_codes", []),
        billed_amount=float(input_data.get("billed_amount", 0)),
        diagnosis_codes=input_data.get("diagnosis_codes"),
        units=input_data.get("units"),
        context=effective_context
    )

    result["factory_id"] = "fraud_detection"
    result["factory_version"] = "2.0.0"  # Version bump for context-driven
    result["context_keys_used"] = ["fraud_detection_rules", "cci_edits"]

    return result


def handler(event, context):
    """Lambda entry point"""
    return fraud_detection(**event)
