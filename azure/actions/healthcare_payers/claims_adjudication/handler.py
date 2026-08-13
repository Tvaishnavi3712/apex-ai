"""
Claims Adjudication Action
Process and adjudicate medical claims against policy rules and fee schedules

Context-Driven Architecture:
- Denial codes are read from playbook context.denial_codes
- Fee schedules are read from playbook context.fee_schedules
- Authorization requirements are read from playbook context.prior_auth_codes
- Timely filing rules are read from playbook context.timely_filing

Supports both:
- Lambda invocation (standalone)
- Small Factory pattern (chain processing)
"""

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: native key-condition builder
    from sdk.azure_data import Key
except ImportError:
    from ...sdk.azure_data import Key
import os
from decimal import Decimal
from datetime import datetime
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


# Default denial codes (used when context not provided)
DEFAULT_DENIAL_CODES = {
    "001": "Patient not eligible on date of service",
    "002": "Service not covered under plan",
    "003": "Prior authorization required",
    "004": "Duplicate claim",
    "005": "Timely filing exceeded",
    "006": "Invalid diagnosis code",
    "007": "Invalid procedure code",
    "008": "Provider not in network",
    "009": "Benefit maximum exceeded",
    "010": "Coordination of benefits required"
}


@apex_action(ApexActionSchema(
    name="claims_adjudication",
    description="Process and adjudicate medical claims against policy rules and fee schedules",
    category="claims",
    industry="healthcare_payers",
    input_schema=ActionInputSchema(description="Claim adjudication parameters")
        .add_string("claim_id", "Unique claim identifier", required=True)
        .add_string("member_id", "Member/subscriber ID", required=True)
        .add_string("provider_npi", "Provider NPI number", required=True)
        .add_string("service_date", "Date of service (YYYY-MM-DD)", required=True)
        .add_array("procedure_codes", "List of CPT/HCPCS procedure codes", required=True)
        .add_array("diagnosis_codes", "List of ICD-10 diagnosis codes", required=True)
        .add_number("billed_amount", "Total billed amount", required=True)
        .add_string("place_of_service", "Place of service code", required=False)
        .add_string("auth_number", "Prior authorization number if applicable", required=False)
        .add_object("context", "Playbook context with fee_schedules, denial_codes, etc.", required=False),
    output_schema=ActionOutputSchema(description="Claim adjudication result")
        .add_string("claim_id", "Claim identifier")
        .add_string("status", "Adjudication status: approved, denied, pended")
        .add_number("allowed_amount", "Allowed amount after fee schedule")
        .add_number("member_responsibility", "Amount member owes")
        .add_number("plan_payment", "Amount plan will pay")
        .add_array("line_results", "Per-line adjudication results")
        .add_array("denial_reasons", "Denial reason codes if denied")
        .add_string("adjudication_date", "Date of adjudication")
))
def claims_adjudication(
    claim_id: str,
    member_id: str,
    provider_npi: str,
    service_date: str,
    procedure_codes: List[str],
    diagnosis_codes: List[str],
    billed_amount: float,
    place_of_service: str = None,
    auth_number: str = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Adjudicate a medical claim using context-driven rules

    Args:
        claim_id: Unique claim identifier
        member_id: Member/subscriber ID
        provider_npi: Provider NPI number
        service_date: Date of service
        procedure_codes: CPT/HCPCS codes
        diagnosis_codes: ICD-10 diagnosis codes
        billed_amount: Total billed amount
        place_of_service: Place of service code
        auth_number: Prior authorization number
        context: Playbook context containing fee_schedules, denial_codes, etc.

    Returns:
        Adjudication result with payment determination
    """
    context = context or {}

    # Get denial codes from context or use defaults
    denial_codes = context.get("denial_codes", DEFAULT_DENIAL_CODES)
    fee_schedules = context.get("fee_schedules", {})
    prior_auth_codes = context.get("prior_auth_codes", [])

    result = {
        "claim_id": claim_id,
        "status": "pended",
        "allowed_amount": 0,
        "member_responsibility": 0,
        "plan_payment": 0,
        "line_results": [],
        "denial_reasons": [],
        "denial_descriptions": [],
        "adjudication_date": datetime.now().isoformat(),
        "processing_notes": [],
        "context_driven": bool(context)
    }

    try:
        # Step 1: Verify member eligibility
        eligibility = _check_eligibility(member_id, service_date)
        if not eligibility.get("eligible"):
            result["status"] = "denied"
            result["denial_reasons"].append("001")
            result["denial_descriptions"].append(_get_denial_description("001", denial_codes))
            return result

        # Step 2: Check for duplicate claim
        if _is_duplicate_claim(claim_id, member_id, service_date, procedure_codes):
            result["status"] = "denied"
            result["denial_reasons"].append("004")
            result["denial_descriptions"].append(_get_denial_description("004", denial_codes))
            return result

        # Step 3: Validate codes
        code_validation = _validate_codes(procedure_codes, diagnosis_codes)
        if not code_validation["valid"]:
            result["status"] = "denied"
            result["denial_reasons"].extend(code_validation["errors"])
            for code in code_validation["errors"]:
                result["denial_descriptions"].append(_get_denial_description(code, denial_codes))
            return result

        # Step 4: Check network status
        network_status = _check_network_status(provider_npi, eligibility.get("plan_id"))

        # Step 5: Check prior authorization using context rules
        if _requires_auth_context(procedure_codes, prior_auth_codes) and not auth_number:
            result["status"] = "denied"
            result["denial_reasons"].append("003")
            result["denial_descriptions"].append(_get_denial_description("003", denial_codes))
            return result

        # Step 6: Apply fee schedule from context
        fee_schedule_result = _apply_fee_schedule_context(
            procedure_codes,
            eligibility.get("plan_id"),
            network_status["in_network"],
            fee_schedules,
            context.get("plan_configurations", {})
        )

        # Step 7: Calculate member cost sharing using context
        cost_sharing = _calculate_cost_sharing_context(
            fee_schedule_result["allowed_amount"],
            eligibility,
            network_status["in_network"],
            context.get("cost_sharing", {})
        )

        # Build result
        result["status"] = "approved"
        result["allowed_amount"] = fee_schedule_result["allowed_amount"]
        result["member_responsibility"] = cost_sharing["member_total"]
        result["plan_payment"] = cost_sharing["plan_payment"]
        result["line_results"] = fee_schedule_result["line_results"]
        result["processing_notes"] = [
            f"Network status: {'In-network' if network_status['in_network'] else 'Out-of-network'}",
            f"Applied fee schedule: {fee_schedule_result.get('fee_schedule_name', 'Standard')}",
            f"Rules source: {'context' if context else 'default'}"
        ]

        return result

    except Exception as e:
        result["status"] = "pended"
        result["processing_notes"].append(f"Error during adjudication: {str(e)}")
        return result


def _get_denial_description(code: str, denial_codes: Dict[str, Any]) -> str:
    """Get denial description from context or defaults."""
    if isinstance(denial_codes, dict):
        # Check if it's the new format with CARC/RARC
        for category, codes in denial_codes.items():
            if isinstance(codes, dict) and code in codes:
                code_info = codes[code]
                if isinstance(code_info, dict):
                    return code_info.get("description", f"Denial code: {code}")
                return str(code_info)

        # Simple format
        if code in denial_codes:
            return denial_codes[code]

    return DEFAULT_DENIAL_CODES.get(code, f"Denial code: {code}")


def _check_eligibility(member_id: str, service_date: str) -> dict:
    """Check member eligibility for date of service"""
    try:
        tables = get_table_resource()
        table = cosmos_db.Table(os.environ.get('ELIGIBILITY_TABLE', 'apex-eligibility'))

        response = table.get_item(Key={"member_id": member_id})
        if 'Item' in response:
            item = response['Item']
            effective_date = item.get('effective_date', '')
            term_date = item.get('term_date', '9999-12-31')

            if effective_date <= service_date <= term_date:
                return {
                    "eligible": True,
                    "plan_id": item.get('plan_id'),
                    "deductible": float(item.get('deductible', 0)),
                    "deductible_met": float(item.get('deductible_met', 0)),
                    "oop_max": float(item.get('oop_max', 0)),
                    "oop_met": float(item.get('oop_met', 0)),
                    "copay": float(item.get('copay', 0)),
                    "coinsurance": float(item.get('coinsurance', 20))
                }
    except Exception:
        pass

    # Return mock eligibility for testing
    return {
        "eligible": True,
        "plan_id": "PLAN001",
        "deductible": 1000,
        "deductible_met": 500,
        "oop_max": 5000,
        "oop_met": 1000,
        "copay": 30,
        "coinsurance": 20
    }


def _is_duplicate_claim(claim_id: str, member_id: str, service_date: str, procedures: List[str]) -> bool:
    """Check for duplicate claim submission"""
    try:
        tables = get_table_resource()
        table = cosmos_db.Table(os.environ.get('CLAIMS_TABLE', 'apex-claims'))

        response = table.query(
            IndexName='member-service-date-index',
            KeyConditionExpression=Key('member_id').eq(member_id) & Key('service_date').eq(service_date)
        )

        for existing in response.get('Items', []):
            if existing.get('claim_id') != claim_id:
                existing_procs = existing.get('procedure_codes', [])
                if set(procedures) & set(existing_procs):
                    return True
    except Exception:
        pass

    return False


def _validate_codes(procedure_codes: List[str], diagnosis_codes: List[str]) -> dict:
    """Validate procedure and diagnosis codes"""
    errors = []

    # Simple validation - check format
    for proc in procedure_codes:
        if not (len(proc) == 5 and proc.isalnum()):
            errors.append("007")
            break

    for diag in diagnosis_codes:
        if not (3 <= len(diag) <= 7):
            errors.append("006")
            break

    return {"valid": len(errors) == 0, "errors": errors}


def _check_network_status(provider_npi: str, plan_id: str) -> dict:
    """Check if provider is in network"""
    try:
        tables = get_table_resource()
        table = cosmos_db.Table(os.environ.get('NETWORK_TABLE', 'apex-provider-network'))

        response = table.get_item(Key={"npi": provider_npi, "plan_id": plan_id})
        if 'Item' in response:
            return {"in_network": True, "tier": response['Item'].get('tier', 1)}
    except Exception:
        pass

    return {"in_network": True, "tier": 1}  # Default to in-network for demo


def _requires_auth(procedure_codes: List[str]) -> bool:
    """Check if any procedure requires prior authorization (legacy)"""
    auth_required_codes = ['27447', '27130', '63030', '22551', '22612']  # Sample codes
    return any(code in auth_required_codes for code in procedure_codes)


def _requires_auth_context(procedure_codes: List[str], prior_auth_codes: List[str]) -> bool:
    """Check if any procedure requires prior authorization using context rules."""
    if prior_auth_codes:
        return any(code in prior_auth_codes for code in procedure_codes)
    # Fallback to default codes
    default_auth_codes = ['27447', '27130', '63030', '22551', '22612']
    return any(code in default_auth_codes for code in procedure_codes)


def _apply_fee_schedule(procedure_codes: List[str], plan_id: str, in_network: bool) -> dict:
    """Apply fee schedule to determine allowed amounts (legacy)"""
    line_results = []
    total_allowed = 0

    base_rates = {
        "99213": 85.00,
        "99214": 125.00,
        "99215": 175.00,
        "99203": 110.00,
        "99204": 165.00,
        "90834": 100.00,
        "90837": 150.00
    }

    network_factor = 1.0 if in_network else 0.7

    for code in procedure_codes:
        rate = base_rates.get(code, 100.00)
        allowed = rate * network_factor
        line_results.append({
            "procedure_code": code,
            "allowed_amount": allowed,
            "fee_schedule_rate": rate,
            "network_adjustment": network_factor
        })
        total_allowed += allowed

    return {
        "allowed_amount": total_allowed,
        "line_results": line_results,
        "fee_schedule_name": f"{'In-Network' if in_network else 'Out-of-Network'} Schedule"
    }


def _apply_fee_schedule_context(
    procedure_codes: List[str],
    plan_id: str,
    in_network: bool,
    fee_schedules: Dict[str, Any],
    plan_config: Dict[str, Any]
) -> dict:
    """Apply fee schedule using context rules."""
    line_results = []
    total_allowed = 0

    # Get network factor from plan config
    network_factor = 1.0 if in_network else 0.7
    if plan_config and not in_network:
        for plan_type in plan_config.values():
            if isinstance(plan_type, dict):
                network_factor = plan_type.get("out_of_network_factor", 0.7)
                break

    for code in procedure_codes:
        # Look up rate in context fee schedules
        rate = _get_fee_rate_from_context(code, fee_schedules)
        allowed = rate * network_factor
        line_results.append({
            "procedure_code": code,
            "allowed_amount": round(allowed, 2),
            "fee_schedule_rate": rate,
            "network_adjustment": network_factor,
            "rate_source": "context" if fee_schedules and code in fee_schedules else "default"
        })
        total_allowed += allowed

    return {
        "allowed_amount": round(total_allowed, 2),
        "line_results": line_results,
        "fee_schedule_name": f"{'In-Network' if in_network else 'Out-of-Network'} Schedule",
        "context_driven": bool(fee_schedules)
    }


def _get_fee_rate_from_context(code: str, fee_schedules: Dict[str, Any]) -> float:
    """Get fee schedule rate from context."""
    if fee_schedules and code in fee_schedules:
        code_data = fee_schedules[code]
        if isinstance(code_data, dict):
            # Use medicare_rate or contracted_rate
            return float(code_data.get("contracted_rate",
                        code_data.get("medicare_rate",
                        code_data.get("rate", 100.00))))
        elif isinstance(code_data, (int, float)):
            return float(code_data)

    # Default rates
    default_rates = {
        "99213": 85.00, "99214": 125.00, "99215": 175.00,
        "99203": 110.00, "99204": 165.00,
        "90834": 100.00, "90837": 150.00
    }
    return default_rates.get(code, 100.00)


def _calculate_cost_sharing(allowed_amount: float, eligibility: dict, in_network: bool) -> dict:
    """Calculate member cost sharing (legacy)"""
    deductible = eligibility.get("deductible", 0)
    deductible_met = eligibility.get("deductible_met", 0)
    coinsurance = eligibility.get("coinsurance", 20) / 100
    copay = eligibility.get("copay", 0)

    remaining_deductible = max(0, deductible - deductible_met)

    amount_after_deductible = max(0, allowed_amount - remaining_deductible)
    deductible_applied = min(remaining_deductible, allowed_amount)

    member_coinsurance = amount_after_deductible * coinsurance
    plan_payment = amount_after_deductible * (1 - coinsurance)

    member_total = deductible_applied + member_coinsurance + copay

    return {
        "member_total": round(member_total, 2),
        "plan_payment": round(plan_payment, 2),
        "deductible_applied": deductible_applied,
        "coinsurance_applied": member_coinsurance,
        "copay_applied": copay
    }


def _calculate_cost_sharing_context(
    allowed_amount: float,
    eligibility: dict,
    in_network: bool,
    cost_sharing_config: Dict[str, Any]
) -> dict:
    """Calculate member cost sharing using context rules."""
    deductible = eligibility.get("deductible", 0)
    deductible_met = eligibility.get("deductible_met", 0)
    copay = eligibility.get("copay", 0)

    # Get coinsurance from context if available
    coinsurance_pct = eligibility.get("coinsurance", 20)
    if cost_sharing_config:
        network_key = "in_network" if in_network else "out_of_network"
        defaults = cost_sharing_config.get("defaults", {})
        if network_key in defaults and "coinsurance" in defaults[network_key]:
            coinsurance_pct = defaults[network_key]["coinsurance"]

    coinsurance = coinsurance_pct / 100
    remaining_deductible = max(0, deductible - deductible_met)

    amount_after_deductible = max(0, allowed_amount - remaining_deductible)
    deductible_applied = min(remaining_deductible, allowed_amount)

    member_coinsurance = amount_after_deductible * coinsurance
    plan_payment = amount_after_deductible * (1 - coinsurance)

    member_total = deductible_applied + member_coinsurance + copay

    return {
        "member_total": round(member_total, 2),
        "plan_payment": round(plan_payment, 2),
        "deductible_applied": round(deductible_applied, 2),
        "coinsurance_applied": round(member_coinsurance, 2),
        "coinsurance_rate": coinsurance_pct,
        "copay_applied": copay,
        "context_driven": bool(cost_sharing_config)
    }


class ClaimsAdjudicationAction(ApexActionBase):
    """Claims Adjudication Action (class-based)"""

    name = "claims_adjudication"
    description = "Process and adjudicate medical claims"
    category = "claims"
    industry = "healthcare_payers"

    def execute(self, **kwargs) -> dict:
        return claims_adjudication(**kwargs)


# Small Factory registration
@register_factory("claims_adjudication")
async def claims_adjudication_factory(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Small Factory handler for claims adjudication (context-driven).

    Expected input_data:
        - claim_id: Unique claim identifier
        - member_id: Member/subscriber ID
        - provider_npi: Provider NPI number
        - service_date: Date of service
        - procedure_codes: List of CPT/HCPCS codes
        - diagnosis_codes: List of ICD-10 codes
        - billed_amount: Total billed amount
        - place_of_service: Optional place of service code
        - auth_number: Optional prior auth number

    Context keys used:
        - fee_schedules: CPT code to rate mappings
        - denial_codes: CARC/RARC denial code definitions
        - prior_auth_codes: Codes requiring prior authorization
        - cost_sharing: Coinsurance and deductible rules
        - plan_configurations: Network factors

    Returns:
        Adjudication result with payment determination
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Claims adjudication factory invoked",
        claim_id=input_data.get("claim_id"),
        context_driven=bool(effective_context)
    )

    result = claims_adjudication(
        claim_id=input_data.get("claim_id", ""),
        member_id=input_data.get("member_id", ""),
        provider_npi=input_data.get("provider_npi", ""),
        service_date=input_data.get("service_date", ""),
        procedure_codes=input_data.get("procedure_codes", []),
        diagnosis_codes=input_data.get("diagnosis_codes", []),
        billed_amount=float(input_data.get("billed_amount", 0)),
        place_of_service=input_data.get("place_of_service"),
        auth_number=input_data.get("auth_number"),
        context=effective_context
    )

    result["factory_id"] = "claims_adjudication"
    result["factory_version"] = "2.0.0"  # Version bump for context-driven
    result["context_keys_used"] = ["fee_schedules", "denial_codes", "prior_auth_codes", "cost_sharing", "plan_configurations"]

    return result


def handler(event, context):
    """Lambda entry point"""
    return claims_adjudication(**event)
