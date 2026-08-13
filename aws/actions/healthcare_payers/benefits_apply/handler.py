"""
Benefits Apply - Healthcare Payers Action (Context-Driven)
Apply member benefits to claim for adjudication

Context-Driven Architecture:
- Benefit rules from playbook context.benefit_config
- Coverage tiers from context.coverage_config
- Accumulator settings from context.accumulator_config
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

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


# Default benefit configuration
DEFAULT_BENEFIT_CONFIG = {
    "deductible": {
        "individual": 500,
        "family": 1500
    },
    "out_of_pocket_max": {
        "individual": 3000,
        "family": 6000
    },
    "coinsurance": 0.20,
    "copay": {
        "office_visit": 25,
        "specialist": 50,
        "urgent_care": 75,
        "emergency": 250
    }
}

# Default coverage tiers
DEFAULT_COVERAGE_TIERS = {
    "in_network": {"coinsurance": 0.20, "deductible_applies": True},
    "out_of_network": {"coinsurance": 0.40, "deductible_applies": True},
    "out_of_area": {"coinsurance": 0.30, "deductible_applies": True}
}


@register_factory("benefits_apply")
async def benefits_apply(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Apply member benefits to claim (context-driven).

    Context keys used:
        - benefit_config: Benefit rules and limits
        - coverage_config: Coverage tier configurations
        - accumulator_config: Deductible and OOP accumulator settings

    Input:
        claim_extract: Extracted claim data
        member_info: Member eligibility and plan info
        pricing_result: Pricing lookup results

    Output:
        benefit_determination: Applied benefit amounts
        member_responsibility: Patient responsibility breakdown
        plan_payment: Plan payment amount
        accumulator_updates: Accumulator changes
    """
    context = context or input_data.get('context', {})
    benefit_config = context.get('benefit_config', DEFAULT_BENEFIT_CONFIG)
    coverage_config = context.get('coverage_config', DEFAULT_COVERAGE_TIERS)
    accumulator_config = context.get('accumulator_config', {})

    logger.info(
        "Benefits apply invoked",
        context_driven=bool(context)
    )

    # Get inputs
    claim = input_data.get('claim_extract', {})
    member = input_data.get('member_info', {})
    pricing = input_data.get('pricing_result', {})

    # Get allowed amount from pricing
    allowed_amount = pricing.get('allowed_amount', claim.get('claim_data', {}).get('billed_amount', 0))
    billed_amount = claim.get('claim_data', {}).get('billed_amount', allowed_amount)

    # Determine network tier
    network_status = member.get('network_status', 'in_network')
    tier_config = coverage_config.get(network_status, DEFAULT_COVERAGE_TIERS['in_network'])

    # Get member accumulators
    accumulators = member.get('accumulators', {
        'deductible_met': 0,
        'oop_met': 0
    })

    # Get benefit limits
    deductible_limit = benefit_config.get('deductible', {}).get('individual', 500)
    oop_max = benefit_config.get('out_of_pocket_max', {}).get('individual', 3000)
    coinsurance_rate = tier_config.get('coinsurance', 0.20)
    deductible_applies = tier_config.get('deductible_applies', True)

    # Calculate deductible remaining
    deductible_remaining = max(0, deductible_limit - accumulators.get('deductible_met', 0))
    oop_remaining = max(0, oop_max - accumulators.get('oop_met', 0))

    # Apply benefits
    deductible_applied = 0
    coinsurance_applied = 0
    copay_applied = 0
    plan_payment = 0

    # Determine service type for copay
    service_type = _determine_service_type(claim.get('claim_data', {}))
    copay_amount = benefit_config.get('copay', {}).get(service_type, 0)

    # Calculate member responsibility
    if copay_amount > 0:
        # Copay-based service
        copay_applied = min(copay_amount, oop_remaining)
        plan_payment = max(0, allowed_amount - copay_applied)
    else:
        # Deductible/coinsurance-based service
        if deductible_applies and deductible_remaining > 0:
            deductible_applied = min(allowed_amount, deductible_remaining)

        amount_after_deductible = max(0, allowed_amount - deductible_applied)
        coinsurance_applied = amount_after_deductible * coinsurance_rate

        # Apply OOP max
        total_member_responsibility = deductible_applied + coinsurance_applied
        if total_member_responsibility > oop_remaining:
            coinsurance_applied = max(0, oop_remaining - deductible_applied)

        plan_payment = allowed_amount - deductible_applied - coinsurance_applied

    total_member_responsibility = deductible_applied + coinsurance_applied + copay_applied

    # Calculate accumulator updates
    accumulator_updates = {
        'deductible_update': deductible_applied,
        'oop_update': total_member_responsibility,
        'new_deductible_met': accumulators.get('deductible_met', 0) + deductible_applied,
        'new_oop_met': accumulators.get('oop_met', 0) + total_member_responsibility
    }

    # Provider write-off (if billed > allowed)
    provider_writeoff = max(0, billed_amount - allowed_amount)

    return {
        "claim_number": claim.get('claim_number'),
        "service_type": service_type,
        "network_status": network_status,
        "billed_amount": round(billed_amount, 2),
        "allowed_amount": round(allowed_amount, 2),
        "benefit_determination": {
            "deductible_applied": round(deductible_applied, 2),
            "coinsurance_applied": round(coinsurance_applied, 2),
            "copay_applied": round(copay_applied, 2),
            "coinsurance_rate": coinsurance_rate
        },
        "member_responsibility": round(total_member_responsibility, 2),
        "plan_payment": round(plan_payment, 2),
        "provider_writeoff": round(provider_writeoff, 2),
        "accumulator_updates": accumulator_updates,
        "deductible_remaining_after": max(0, deductible_remaining - deductible_applied),
        "oop_remaining_after": max(0, oop_remaining - total_member_responsibility),
        "oop_max_reached": (accumulators.get('oop_met', 0) + total_member_responsibility) >= oop_max,
        "applied_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "benefits_apply",
        "factory_version": "2.0.0",
        "context_keys_used": ["benefit_config", "coverage_config", "accumulator_config"]
    }


def _determine_service_type(claim_data: Dict) -> str:
    """Determine service type from claim data."""
    procedures = claim_data.get('procedure_codes', [])

    if not procedures:
        return "other"

    # Check first procedure code
    first_code = procedures[0].get('code', '') if procedures else ''

    # Office visit codes
    if first_code.startswith('992'):
        return "office_visit"

    # Emergency codes
    if first_code.startswith('994') or first_code.startswith('995'):
        return "emergency"

    # Urgent care
    if first_code.startswith('993'):
        return "urgent_care"

    return "other"


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(benefits_apply(event))
