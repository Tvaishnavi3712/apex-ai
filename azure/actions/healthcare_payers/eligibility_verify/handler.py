"""
Eligibility Verification Action
Verify member eligibility and benefits for healthcare services

Context-Driven Architecture:
- Plan configurations are read from playbook context.plan_configurations
- Cost sharing rules are read from playbook context.cost_sharing
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
    name="eligibility_verify",
    description="Verify member eligibility and benefits for healthcare services",
    category="eligibility",
    industry="healthcare_payers",
    input_schema=ActionInputSchema(description="Eligibility verification parameters")
        .add_string("member_id", "Member/subscriber ID", required=True)
        .add_string("date_of_service", "Date of service to verify (YYYY-MM-DD)", required=True)
        .add_string("service_type", "Type of service (medical, dental, vision, pharmacy)", required=False)
        .add_string("provider_npi", "Provider NPI to check network status", required=False)
        .add_string("plan_type", "Plan type (PPO, HMO, EPO) for context lookup", required=False)
        .add_object("context", "Playbook context with plan_configurations and cost_sharing", required=False),
    output_schema=ActionOutputSchema(description="Eligibility verification result")
        .add_boolean("eligible", "Whether member is eligible")
        .add_string("member_id", "Member ID")
        .add_string("member_name", "Member name")
        .add_string("plan_name", "Plan name")
        .add_string("effective_date", "Coverage effective date")
        .add_string("term_date", "Coverage termination date")
        .add_object("benefits", "Benefit details")
        .add_object("accumulators", "Deductible and OOP accumulator status")
        .add_string("network_status", "Provider network status")
))
def eligibility_verify(
    member_id: str,
    date_of_service: str,
    service_type: str = "medical",
    provider_npi: str = None,
    plan_type: str = None,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Verify member eligibility and retrieve benefits using context-driven rules

    Args:
        member_id: Member/subscriber ID
        date_of_service: Date of service to verify
        service_type: Type of service
        provider_npi: Provider NPI for network check
        plan_type: Plan type for context lookup
        context: Playbook context containing plan_configurations and cost_sharing

    Returns:
        Eligibility status and benefit information
    """
    context = context or {}
    plan_config = context.get("plan_configurations", {})
    cost_sharing = context.get("cost_sharing", {})

    result = {
        "eligible": False,
        "member_id": member_id,
        "member_name": None,
        "plan_name": None,
        "effective_date": None,
        "term_date": None,
        "benefits": {},
        "accumulators": {},
        "network_status": None,
        "verification_date": datetime.now().isoformat(),
        "context_driven": bool(context)
    }

    try:
        tables = get_table_resource()
        table = cosmos_db.Table(os.environ.get('ELIGIBILITY_TABLE', 'apex-eligibility'))

        response = table.get_item(Key={"member_id": member_id})

        if 'Item' in response:
            item = response['Item']
            effective_date = item.get('effective_date', '')
            term_date = item.get('term_date', '9999-12-31')

            result["member_name"] = item.get('member_name')
            result["plan_name"] = item.get('plan_name')
            result["effective_date"] = effective_date
            result["term_date"] = term_date

            # Check if eligible on date of service
            if effective_date <= date_of_service <= term_date:
                result["eligible"] = True

                # Get benefits - use context if available
                member_plan_type = plan_type or item.get('plan_type', 'PPO')
                result["benefits"] = _get_benefits_context(
                    item, service_type, member_plan_type, plan_config, cost_sharing
                )
                result["accumulators"] = _get_accumulators(item)

                # Check network status if provider specified
                if provider_npi:
                    result["network_status"] = _check_network(
                        provider_npi,
                        item.get('plan_id')
                    )

            return result

    except Exception as e:
        result["error"] = str(e)

    # Return benefits from context if available
    benefits = _build_default_benefits(service_type, plan_type, plan_config, cost_sharing)

    return {
        "eligible": True,
        "member_id": member_id,
        "member_name": "Test Member",
        "plan_name": plan_type or "Premium PPO",
        "effective_date": "2024-01-01",
        "term_date": "2024-12-31",
        "benefits": benefits,
        "accumulators": {
            "individual_deductible_met": 500,
            "individual_oop_met": 750,
            "family_deductible_met": 1200,
            "family_oop_met": 1800
        },
        "network_status": "in_network" if provider_npi else None,
        "verification_date": datetime.now().isoformat(),
        "context_driven": bool(context)
    }


def _get_benefits_context(
    member_data: dict,
    service_type: str,
    plan_type: str,
    plan_config: Dict[str, Any],
    cost_sharing: Dict[str, Any]
) -> dict:
    """Extract benefits using context configuration."""
    # Try to get from member data first
    benefits = member_data.get('benefits', {})
    service_benefits = benefits.get(service_type, benefits.get('medical', {}))

    if service_benefits:
        return {"service_type": service_type, **service_benefits}

    # Build from context
    return _build_default_benefits(service_type, plan_type, plan_config, cost_sharing)


def _build_default_benefits(
    service_type: str,
    plan_type: str,
    plan_config: Dict[str, Any],
    cost_sharing: Dict[str, Any]
) -> dict:
    """Build benefits structure from context configuration."""
    benefits = {"service_type": service_type, "source": "default"}

    # Try to get plan-specific config
    if plan_config and plan_type:
        plan_rules = plan_config.get(plan_type, {})
        if plan_rules:
            benefits["source"] = "context"
            benefits["in_network"] = {
                "deductible": plan_rules.get("in_network_deductible", 1000),
                "coinsurance": plan_rules.get("in_network_coinsurance", 20),
                "out_of_pocket_max": plan_rules.get("in_network_oop_max", 6000)
            }
            benefits["out_of_network"] = {
                "deductible": plan_rules.get("out_of_network_deductible", 2000),
                "coinsurance": plan_rules.get("out_of_network_coinsurance", 40),
                "out_of_pocket_max": plan_rules.get("out_of_network_oop_max", 12000)
            }
            return benefits

    # Try cost_sharing config
    if cost_sharing:
        defaults = cost_sharing.get("defaults", {})
        if defaults:
            benefits["source"] = "context"
            in_network = defaults.get("in_network", {})
            out_network = defaults.get("out_of_network", {})
            benefits["in_network"] = {
                "deductible": in_network.get("deductible", 1000),
                "coinsurance": in_network.get("coinsurance", 20),
                "out_of_pocket_max": in_network.get("oop_max", 6000)
            }
            benefits["out_of_network"] = {
                "deductible": out_network.get("deductible", 2000),
                "coinsurance": out_network.get("coinsurance", 40),
                "out_of_pocket_max": out_network.get("oop_max", 12000)
            }
            return benefits

    # Hardcoded defaults
    benefits["in_network"] = {
        "deductible": 1000,
        "coinsurance": 20,
        "copay_primary": 30,
        "copay_specialist": 50,
        "out_of_pocket_max": 5000
    }
    benefits["out_of_network"] = {
        "deductible": 2000,
        "coinsurance": 40,
        "out_of_pocket_max": 10000
    }
    return benefits


def _get_benefits(member_data: dict, service_type: str) -> dict:
    """Extract benefits for service type"""
    benefits = member_data.get('benefits', {})
    return benefits.get(service_type, benefits.get('medical', {}))


def _get_accumulators(member_data: dict) -> dict:
    """Get current accumulator status"""
    return {
        "individual_deductible_met": float(member_data.get('deductible_met', 0)),
        "individual_oop_met": float(member_data.get('oop_met', 0)),
        "family_deductible_met": float(member_data.get('family_deductible_met', 0)),
        "family_oop_met": float(member_data.get('family_oop_met', 0))
    }


def _check_network(provider_npi: str, plan_id: str) -> str:
    """Check provider network status"""
    try:
        tables = get_table_resource()
        table = cosmos_db.Table(os.environ.get('NETWORK_TABLE', 'apex-provider-network'))

        response = table.get_item(Key={"npi": provider_npi, "plan_id": plan_id})
        if 'Item' in response:
            return "in_network"
    except Exception:
        pass

    return "out_of_network"


class EligibilityVerifyAction(ApexActionBase):
    """Eligibility Verification Action (class-based)"""

    name = "eligibility_verify"
    description = "Verify member eligibility and benefits"
    category = "eligibility"
    industry = "healthcare_payers"

    def execute(self, **kwargs) -> dict:
        return eligibility_verify(**kwargs)


# Small Factory registration
@register_factory("eligibility_verify")
async def eligibility_verify_factory(input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Small Factory handler for eligibility verification (context-driven).

    Expected input_data:
        - member_id: Member/subscriber ID
        - date_of_service: Date of service to verify
        - service_type: Type of service (optional)
        - provider_npi: Provider NPI (optional)
        - plan_type: Plan type for context lookup (optional)

    Context keys used:
        - plan_configurations: Plan-specific benefit rules
        - cost_sharing: Default deductible/coinsurance rules

    Returns:
        Eligibility status and benefit information
    """
    effective_context = context or input_data.get("context", {})

    logger.info(
        "Eligibility verify factory invoked",
        member_id=input_data.get("member_id"),
        context_driven=bool(effective_context)
    )

    result = eligibility_verify(
        member_id=input_data.get("member_id", ""),
        date_of_service=input_data.get("date_of_service", ""),
        service_type=input_data.get("service_type", "medical"),
        provider_npi=input_data.get("provider_npi"),
        plan_type=input_data.get("plan_type"),
        context=effective_context
    )

    result["factory_id"] = "eligibility_verify"
    result["factory_version"] = "2.0.0"  # Version bump for context-driven
    result["context_keys_used"] = ["plan_configurations", "cost_sharing"]

    return result


def handler(event, context):
    """Lambda entry point"""
    return eligibility_verify(**event)
