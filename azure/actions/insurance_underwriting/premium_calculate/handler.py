"""
Premium Calculation Action
Calculate insurance premium based on risk assessment
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Base rates by line of business
BASE_RATES = {
    "auto": {"base": 800, "per_1k_liability": 1.50},
    "home": {"base": 1200, "per_1k_dwelling": 0.50},
    "commercial": {"base": 2500, "per_1k_coverage": 2.00},
    "life": {"base": 500, "per_1k_face": 5.00}
}


@apex_action(ApexActionSchema(
    name="premium_calculate",
    description="Calculate insurance premium based on risk assessment",
    category="pricing",
    industry="insurance_underwriting",
    input_schema=ActionInputSchema(description="Premium calculation parameters")
        .add_string("application_id", "Application identifier", required=True)
        .add_string("line_of_business", "Insurance line", required=True)
        .add_number("risk_score", "Risk score from risk assessment", required=True)
        .add_string("risk_tier", "Risk tier classification", required=True)
        .add_object("coverage_details", "Coverage details and limits", required=True)
        .add_array("discounts", "Applicable discounts", required=False)
        .add_string("payment_plan", "Payment plan: annual, semi, quarterly, monthly", required=False),
    output_schema=ActionOutputSchema(description="Premium calculation result")
        .add_number("annual_premium", "Total annual premium")
        .add_number("base_premium", "Base premium before adjustments")
        .add_array("premium_components", "Premium breakdown by component")
        .add_array("discounts_applied", "Discounts applied")
        .add_number("total_discounts", "Total discount amount")
        .add_object("payment_options", "Available payment options")
))
def premium_calculate(
    application_id: str,
    line_of_business: str,
    risk_score: int,
    risk_tier: str,
    coverage_details: Dict[str, Any],
    discounts: List[str] = None,
    payment_plan: str = "annual"
) -> dict:
    """
    Calculate insurance premium

    Args:
        application_id: Application ID
        line_of_business: Line of business
        risk_score: Risk score
        risk_tier: Risk tier
        coverage_details: Coverage details
        discounts: Applicable discounts
        payment_plan: Payment plan

    Returns:
        Premium calculation details
    """
    discounts = discounts or []

    result = {
        "application_id": application_id,
        "line_of_business": line_of_business,
        "annual_premium": 0,
        "base_premium": 0,
        "premium_components": [],
        "discounts_applied": [],
        "total_discounts": 0,
        "payment_options": {},
        "calculation_date": datetime.now().isoformat()
    }

    # Get base rates
    rates = BASE_RATES.get(line_of_business, BASE_RATES["auto"])
    base = rates["base"]

    # Calculate coverage-based premium
    coverage_premium = 0
    if line_of_business == "auto":
        liability_limit = coverage_details.get("liability_limit", 100000)
        coverage_premium = (liability_limit / 1000) * rates["per_1k_liability"]
        result["premium_components"].append({
            "component": "Liability Coverage",
            "amount": coverage_premium
        })

        # Comprehensive/Collision
        if coverage_details.get("comprehensive"):
            comp_premium = coverage_details.get("vehicle_value", 20000) * 0.02
            coverage_premium += comp_premium
            result["premium_components"].append({
                "component": "Comprehensive",
                "amount": comp_premium
            })

    elif line_of_business == "home":
        dwelling_amount = coverage_details.get("dwelling_coverage", 250000)
        coverage_premium = (dwelling_amount / 1000) * rates["per_1k_dwelling"]
        result["premium_components"].append({
            "component": "Dwelling Coverage",
            "amount": coverage_premium
        })

        # Contents
        contents = coverage_details.get("contents_coverage", dwelling_amount * 0.5)
        contents_premium = (contents / 1000) * 0.25
        coverage_premium += contents_premium
        result["premium_components"].append({
            "component": "Contents Coverage",
            "amount": contents_premium
        })

    elif line_of_business == "commercial":
        total_coverage = coverage_details.get("total_coverage", 1000000)
        coverage_premium = (total_coverage / 1000) * rates["per_1k_coverage"]
        result["premium_components"].append({
            "component": "Commercial Package",
            "amount": coverage_premium
        })

    # Apply risk tier factor
    tier_factors = {
        "preferred": 0.85,
        "standard": 1.0,
        "substandard": 1.35,
        "decline": 2.0
    }
    tier_factor = tier_factors.get(risk_tier, 1.0)

    base_premium = (base + coverage_premium) * tier_factor
    result["base_premium"] = round(base_premium, 2)
    result["premium_components"].append({
        "component": f"Risk Tier Adjustment ({risk_tier})",
        "factor": tier_factor
    })

    # Apply discounts
    total_discount = 0
    discount_rates = {
        "multi_policy": 0.10,
        "claims_free": 0.05,
        "good_driver": 0.05,
        "safe_home": 0.05,
        "paid_in_full": 0.03,
        "loyalty": 0.05,
        "defensive_driver": 0.05,
        "good_student": 0.08
    }

    for discount in discounts:
        rate = discount_rates.get(discount.lower().replace(" ", "_"), 0)
        if rate > 0:
            discount_amount = base_premium * rate
            total_discount += discount_amount
            result["discounts_applied"].append({
                "discount": discount,
                "rate": f"{rate*100:.0f}%",
                "amount": round(discount_amount, 2)
            })

    result["total_discounts"] = round(total_discount, 2)
    annual_premium = base_premium - total_discount
    result["annual_premium"] = round(annual_premium, 2)

    # Payment options
    result["payment_options"] = {
        "annual": {
            "total": round(annual_premium, 2),
            "per_payment": round(annual_premium, 2),
            "fee": 0
        },
        "semi_annual": {
            "total": round(annual_premium * 1.02, 2),
            "per_payment": round((annual_premium * 1.02) / 2, 2),
            "fee": round(annual_premium * 0.02, 2)
        },
        "quarterly": {
            "total": round(annual_premium * 1.04, 2),
            "per_payment": round((annual_premium * 1.04) / 4, 2),
            "fee": round(annual_premium * 0.04, 2)
        },
        "monthly": {
            "total": round(annual_premium * 1.06, 2),
            "per_payment": round((annual_premium * 1.06) / 12, 2),
            "fee": round(annual_premium * 0.06, 2)
        }
    }

    return result


class PremiumCalculateAction(ApexActionBase):
    """Premium Calculation Action (class-based)"""

    name = "premium_calculate"
    description = "Calculate insurance premium"
    category = "pricing"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return premium_calculate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return premium_calculate(**event)
