"""
Pricing Lookup - Healthcare Payers Action (Context-Driven)
Look up pricing/fee schedule for claim services

Context-Driven Architecture:
- Fee schedules from playbook context.fee_schedule_config
- Contract rates from context.contract_config
- Pricing rules from context.pricing_rules
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


# Default fee schedule (Medicare-based)
DEFAULT_FEE_SCHEDULE = {
    "99213": {"rvu": 1.30, "conversion_factor": 33.06, "facility_rate": 0.85},
    "99214": {"rvu": 1.92, "conversion_factor": 33.06, "facility_rate": 0.85},
    "99215": {"rvu": 2.80, "conversion_factor": 33.06, "facility_rate": 0.85},
    "87880": {"rvu": 0.50, "conversion_factor": 33.06, "facility_rate": 1.0},
    "36415": {"rvu": 0.17, "conversion_factor": 33.06, "facility_rate": 1.0}
}

# Default pricing rules
DEFAULT_PRICING_RULES = {
    "use_lesser_of": True,
    "max_allowed_pct_of_billed": 1.0,
    "apply_geographic_adjustment": True,
    "geographic_factor": 1.0
}


@register_factory("pricing_lookup")
async def pricing_lookup(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Look up pricing for claim services (context-driven).

    Context keys used:
        - fee_schedule_config: Fee schedule rates
        - contract_config: Provider contract rates
        - pricing_rules: Pricing calculation rules

    Input:
        claim_extract: Extracted claim data
        provider_info: Provider network and contract info

    Output:
        allowed_amount: Total allowed amount for claim
        line_pricing: Per-line pricing details
        pricing_method: Method used for pricing
    """
    context = context or input_data.get('context', {})
    fee_schedule = context.get('fee_schedule_config', DEFAULT_FEE_SCHEDULE)
    contract_config = context.get('contract_config', {})
    pricing_rules = context.get('pricing_rules', DEFAULT_PRICING_RULES)

    logger.info(
        "Pricing lookup invoked",
        context_driven=bool(context)
    )

    # Get claim data
    claim = input_data.get('claim_extract', {})
    claim_data = claim.get('claim_data', {})
    provider_info = input_data.get('provider_info', claim_data.get('provider_info', {}))

    procedures = claim_data.get('procedure_codes', [])
    billed_amount = claim_data.get('billed_amount', 0)

    # Determine pricing method
    provider_npi = provider_info.get('npi', '')
    contract_rate = contract_config.get('provider_rates', {}).get(provider_npi, {})

    if contract_rate:
        pricing_method = 'contract'
    else:
        pricing_method = 'fee_schedule'

    # Price each line
    line_pricing = []
    total_allowed = 0
    total_billed = 0

    for proc in procedures:
        code = proc.get('code', '')
        units = proc.get('units', 1)
        line_billed = proc.get('billed_amount', billed_amount / len(procedures) if procedures else 0)

        # Look up fee schedule rate
        fee_data = fee_schedule.get(code, {})

        if pricing_method == 'contract' and code in contract_rate:
            # Use contract rate
            unit_rate = contract_rate[code]
            rate_source = 'contract'
        elif fee_data:
            # Calculate from RVU
            rvu = fee_data.get('rvu', 1.0)
            conversion_factor = fee_data.get('conversion_factor', 33.06)
            facility_rate = fee_data.get('facility_rate', 1.0)
            geo_factor = pricing_rules.get('geographic_factor', 1.0)

            unit_rate = rvu * conversion_factor * facility_rate * geo_factor
            rate_source = 'fee_schedule'
        else:
            # Default to percentage of billed
            unit_rate = line_billed * 0.80
            rate_source = 'default'

        line_allowed = unit_rate * units

        # Apply lesser of logic
        if pricing_rules.get('use_lesser_of', True):
            line_allowed = min(line_allowed, line_billed)

        # Apply max allowed percentage
        max_pct = pricing_rules.get('max_allowed_pct_of_billed', 1.0)
        line_allowed = min(line_allowed, line_billed * max_pct)

        line_pricing.append({
            'code': code,
            'description': proc.get('description', ''),
            'units': units,
            'billed_amount': round(line_billed, 2),
            'unit_rate': round(unit_rate, 2),
            'allowed_amount': round(line_allowed, 2),
            'rate_source': rate_source,
            'reduction_amount': round(line_billed - line_allowed, 2)
        })

        total_allowed += line_allowed
        total_billed += line_billed

    # If no procedures, use claim-level billed amount
    if not procedures:
        total_billed = billed_amount
        total_allowed = billed_amount * 0.80  # Default 80% of billed

    return {
        "claim_number": claim.get('claim_number'),
        "billed_amount": round(total_billed, 2),
        "allowed_amount": round(total_allowed, 2),
        "reduction_amount": round(total_billed - total_allowed, 2),
        "reduction_percentage": round((total_billed - total_allowed) / total_billed * 100, 1) if total_billed > 0 else 0,
        "pricing_method": pricing_method,
        "line_count": len(line_pricing),
        "line_pricing": line_pricing,
        "fee_schedule_used": "standard" if not contract_config else "contract",
        "pricing_rules_applied": {
            "lesser_of": pricing_rules.get('use_lesser_of', True),
            "geographic_adjustment": pricing_rules.get('apply_geographic_adjustment', True)
        },
        "priced_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "pricing_lookup",
        "factory_version": "2.0.0",
        "context_keys_used": ["fee_schedule_config", "contract_config", "pricing_rules"]
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(pricing_lookup(event))
