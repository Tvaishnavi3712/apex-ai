"""
Payment Calculation Action
Calculate claim payment amounts based on fee schedules and benefit rules

Context-Driven Architecture:
- Fee schedules are read from playbook context.fee_schedules
- Cost sharing rules are read from playbook context.cost_sharing
- Network factors are read from playbook context.plan_configurations
"""

import boto3
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


@apex_action(ApexActionSchema(
    name="payment_calculate",
    description="Calculate claim payment amounts based on fee schedules and benefit rules",
    category="claims",
    industry="healthcare_payers",
    input_schema=ActionInputSchema(description="Payment calculation parameters")
        .add_string("claim_id", "Claim identifier", required=True)
        .add_array("line_items", "Claim line items with procedure codes and units", required=True)
        .add_string("fee_schedule_type", "Fee schedule type (medicare, commercial)", required=True)
        .add_boolean("in_network", "Whether provider is in network", required=True)
        .add_number("deductible_remaining", "Remaining deductible amount", required=True)
        .add_number("coinsurance_pct", "Member coinsurance percentage", required=True)
        .add_number("copay", "Copay amount if applicable", required=False)
        .add_number("oop_remaining", "Remaining out-of-pocket maximum", required=False)
        .add_object("context", "Playbook context with fee_schedules and cost_sharing rules", required=False),
    output_schema=ActionOutputSchema(description="Payment calculation result")
        .add_string("claim_id", "Claim identifier")
        .add_number("total_billed", "Total billed amount")
        .add_number("total_allowed", "Total allowed amount")
        .add_number("total_plan_pay", "Total plan payment")
        .add_number("total_member_pay", "Total member responsibility")
        .add_array("line_calculations", "Per-line payment calculations")
        .add_object("cost_sharing", "Cost sharing breakdown")
))
def payment_calculate(
    claim_id: str,
    line_items: List[Dict],
    fee_schedule_type: str,
    in_network: bool,
    deductible_remaining: float,
    coinsurance_pct: float,
    copay: float = 0,
    oop_remaining: float = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Calculate payment for a claim using context-driven fee schedules

    Args:
        claim_id: Claim identifier
        line_items: List of line items with procedure_code, units, billed_amount
        fee_schedule_type: Fee schedule to apply
        in_network: Network status
        deductible_remaining: Remaining deductible
        coinsurance_pct: Coinsurance percentage
        copay: Copay amount
        oop_remaining: Remaining OOP max
        context: Playbook context containing fee_schedules and cost_sharing rules

    Returns:
        Payment calculation details
    """
    context = context or {}
    oop_remaining = oop_remaining or float('inf')

    result = {
        "claim_id": claim_id,
        "total_billed": 0,
        "total_allowed": 0,
        "total_plan_pay": 0,
        "total_member_pay": 0,
        "line_calculations": [],
        "cost_sharing": {
            "deductible_applied": 0,
            "coinsurance_applied": 0,
            "copay_applied": 0,
            "oop_cap_applied": False
        },
        "calculation_date": datetime.now().isoformat(),
        "context_driven": bool(context)
    }

    # Get fee schedules from context (context-driven architecture)
    fee_schedules = context.get("fee_schedules", {})
    cost_sharing_config = context.get("cost_sharing", {})
    plan_config = context.get("plan_configurations", {})

    # Get network factor from plan configuration or use default
    network_status = "in_network" if in_network else "out_of_network"
    network_factor = 1.0
    if plan_config and not in_network:
        # Look for out_of_network_factor in plan config
        for plan_type in plan_config.values():
            if isinstance(plan_type, dict):
                network_factor = plan_type.get("out_of_network_factor", 0.70)
                break
    elif not in_network:
        network_factor = 0.70

    running_deductible = deductible_remaining
    running_oop = oop_remaining
    total_member = copay  # Start with copay

    for item in line_items:
        proc_code = item.get("procedure_code", "")
        units = item.get("units", 1)
        billed = item.get("billed_amount", 0)

        # Get allowed amount from context fee schedules
        fs_rate = _get_fee_schedule_rate(proc_code, fee_schedule_type, fee_schedules, billed)
        allowed = fs_rate * units * network_factor

        result["total_billed"] += billed
        result["total_allowed"] += allowed

        # Calculate line-level payment
        line_calc = {
            "procedure_code": proc_code,
            "units": units,
            "billed_amount": billed,
            "allowed_amount": round(allowed, 2),
            "fee_schedule_rate": fs_rate,
            "fee_schedule_source": "context" if fee_schedules else "default",
            "deductible_applied": 0,
            "coinsurance_applied": 0,
            "plan_pays": 0,
            "member_pays": 0
        }

        # Apply deductible
        if running_deductible > 0:
            deduct_portion = min(running_deductible, allowed)
            line_calc["deductible_applied"] = round(deduct_portion, 2)
            running_deductible -= deduct_portion
            allowed_after_deductible = allowed - deduct_portion
        else:
            allowed_after_deductible = allowed

        # Apply coinsurance (can be overridden by context cost_sharing rules)
        effective_coinsurance = _get_effective_coinsurance(
            proc_code, coinsurance_pct, in_network, cost_sharing_config
        )
        member_coinsurance = allowed_after_deductible * (effective_coinsurance / 100)
        plan_portion = allowed_after_deductible - member_coinsurance

        line_calc["coinsurance_applied"] = round(member_coinsurance, 2)
        line_calc["coinsurance_rate"] = effective_coinsurance

        # Check OOP cap
        line_member_total = line_calc["deductible_applied"] + member_coinsurance

        if running_oop <= 0:
            # OOP max reached - plan pays everything
            line_calc["plan_pays"] = round(allowed, 2)
            line_calc["member_pays"] = 0
            result["cost_sharing"]["oop_cap_applied"] = True
        elif line_member_total > running_oop:
            # Would exceed OOP max
            line_calc["member_pays"] = round(running_oop, 2)
            line_calc["plan_pays"] = round(allowed - running_oop, 2)
            running_oop = 0
            result["cost_sharing"]["oop_cap_applied"] = True
        else:
            line_calc["member_pays"] = round(line_member_total, 2)
            line_calc["plan_pays"] = round(plan_portion, 2)
            running_oop -= line_member_total

        result["line_calculations"].append(line_calc)
        result["total_plan_pay"] += line_calc["plan_pays"]
        total_member += line_calc["member_pays"]
        result["cost_sharing"]["deductible_applied"] += line_calc["deductible_applied"]
        result["cost_sharing"]["coinsurance_applied"] += line_calc["coinsurance_applied"]

    result["total_member_pay"] = round(total_member, 2)
    result["cost_sharing"]["copay_applied"] = copay
    result["total_plan_pay"] = round(result["total_plan_pay"], 2)
    result["total_allowed"] = round(result["total_allowed"], 2)

    return result


def _get_fee_schedule_rate(
    proc_code: str,
    schedule_type: str,
    fee_schedules: Dict[str, Any],
    billed_amount: float
) -> float:
    """
    Get fee schedule rate from context or calculate default.

    Looks up rate in context.fee_schedules by CPT code.
    Falls back to percentage of billed if not found.
    """
    # Try to find the CPT code in fee_schedules
    if fee_schedules and proc_code in fee_schedules:
        code_data = fee_schedules[proc_code]
        if isinstance(code_data, dict):
            # Fee schedule has detailed structure
            if schedule_type == "medicare":
                return float(code_data.get("medicare_rate", code_data.get("rate", billed_amount * 0.8)))
            elif schedule_type == "medicaid":
                return float(code_data.get("medicaid_rate", code_data.get("rate", billed_amount * 0.7)))
            else:
                # Commercial - use contracted rate or base rate
                return float(code_data.get("contracted_rate", code_data.get("rate", billed_amount * 0.85)))
        elif isinstance(code_data, (int, float)):
            return float(code_data)

    # No context fee schedule - use default percentages
    default_factors = {
        "medicare": 0.75,
        "medicaid": 0.65,
        "commercial": 0.85
    }
    factor = default_factors.get(schedule_type, 0.80)
    return billed_amount * factor


def _get_effective_coinsurance(
    proc_code: str,
    default_coinsurance: float,
    in_network: bool,
    cost_sharing_config: Dict[str, Any]
) -> float:
    """
    Get effective coinsurance rate from context cost_sharing rules.

    Allows service-type-specific coinsurance rates from playbook context.
    """
    if not cost_sharing_config:
        return default_coinsurance

    network_key = "in_network" if in_network else "out_of_network"

    # Check for service-specific coinsurance
    coinsurance_by_service = cost_sharing_config.get("coinsurance_by_service", {})
    network_rates = coinsurance_by_service.get(network_key, {})

    # Determine service type from procedure code
    service_type = _get_service_type_from_code(proc_code)

    if service_type and service_type in network_rates:
        return float(network_rates[service_type])

    # Check for default coinsurance in config
    defaults = cost_sharing_config.get("defaults", {})
    if network_key in defaults and "coinsurance" in defaults[network_key]:
        return float(defaults[network_key]["coinsurance"])

    return default_coinsurance


def _get_service_type_from_code(proc_code: str) -> str:
    """Determine service type from CPT code for cost sharing lookup."""
    code_ranges = {
        "office_visit": ["99201", "99202", "99203", "99204", "99205",
                        "99211", "99212", "99213", "99214", "99215"],
        "preventive": ["99381", "99382", "99383", "99384", "99385",
                      "99391", "99392", "99393", "99394", "99395"],
        "lab": ["80048", "80050", "80053", "80061", "80076", "85025", "85027"],
        "imaging": ["70553", "71046", "71250", "72141", "72148", "73721"],
        "surgery": ["27447", "27130", "63030", "22551", "22612"],
        "mental_health": ["90834", "90837", "90847", "90832"]
    }

    for service_type, codes in code_ranges.items():
        if proc_code in codes:
            return service_type

    return "other"


class PaymentCalculateAction(ApexActionBase):
    """Payment Calculation Action (class-based)"""

    name = "payment_calculate"
    description = "Calculate claim payment amounts"
    category = "claims"
    industry = "healthcare_payers"

    def execute(self, **kwargs) -> dict:
        return payment_calculate(**kwargs)


# Small Factory registration
@register_factory("payment_calculate")
async def payment_calculate_factory(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Small Factory handler for payment calculation (context-driven).

    Expected input_data:
        - claim_id: Claim identifier
        - line_items: List of line items with procedure codes
        - fee_schedule_type: Fee schedule type
        - in_network: Network status
        - deductible_remaining: Remaining deductible
        - coinsurance_pct: Coinsurance percentage
        - copay: Copay amount (optional)
        - oop_remaining: Remaining OOP max (optional)

    Context keys used:
        - fee_schedules: CPT code to rate mappings
        - cost_sharing: Coinsurance/deductible rules by service type
        - plan_configurations: Network factors and plan rules

    Returns:
        Payment calculation details
    """
    # Merge context from input_data if present (for direct calls)
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Payment calculate factory invoked",
        claim_id=input_data.get("claim_id"),
        context_driven=bool(effective_context)
    )

    result = payment_calculate(
        claim_id=input_data.get("claim_id", ""),
        line_items=input_data.get("line_items", []),
        fee_schedule_type=input_data.get("fee_schedule_type", "commercial"),
        in_network=input_data.get("in_network", True),
        deductible_remaining=float(input_data.get("deductible_remaining", 0)),
        coinsurance_pct=float(input_data.get("coinsurance_pct", 20)),
        copay=float(input_data.get("copay", 0)),
        oop_remaining=input_data.get("oop_remaining"),
        context=effective_context
    )

    result["factory_id"] = "payment_calculate"
    result["factory_version"] = "2.0.0"  # Version bump for context-driven
    result["context_keys_used"] = ["fee_schedules", "cost_sharing", "plan_configurations"]

    return result


def handler(event, context):
    """Lambda entry point"""
    return payment_calculate(**event)
