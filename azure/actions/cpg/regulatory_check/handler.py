"""
Regulatory Check Action
Check product regulatory compliance across markets
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Regulatory requirements by market
REGULATORY_REQUIREMENTS = {
    "US": {
        "agency": "FDA",
        "requirements": [
            "Nutrition Facts panel (21 CFR 101.9)",
            "Ingredient statement (21 CFR 101.4)",
            "Allergen declaration (FALCPA)",
            "Net quantity statement",
            "Name and address of manufacturer"
        ],
        "optional_claims_require_approval": ["health_claims", "structure_function_claims"],
        "prop65_if_ca": True
    },
    "EU": {
        "agency": "EFSA",
        "requirements": [
            "Nutrition declaration (Regulation 1169/2011)",
            "Ingredients list",
            "Allergen highlighting",
            "Net quantity",
            "Date marking (best before/use by)",
            "Origin labeling for certain foods"
        ],
        "language_requirements": ["local_language_required"]
    },
    "UK": {
        "agency": "FSA",
        "requirements": [
            "Nutrition information",
            "Ingredients list with allergens emphasized",
            "Net quantity",
            "Date marking",
            "UK business address required"
        ]
    },
    "CA": {
        "agency": "CFIA",
        "requirements": [
            "Nutrition Facts table (Canadian format)",
            "Bilingual labeling (English/French)",
            "Ingredient list",
            "Allergen declaration",
            "Net quantity in metric"
        ]
    }
}


@apex_action(ApexActionSchema(
    name="regulatory_check",
    description="Check product regulatory compliance across markets",
    category="compliance",
    industry="cpg",
    input_schema=ActionInputSchema(description="Regulatory check parameters")
        .add_string("product_id", "Product identifier", required=True)
        .add_string("product_category", "Product category (food, beverage, cosmetic)", required=True)
        .add_array("target_markets", "Target markets for compliance check", required=True)
        .add_object("product_attributes", "Product attributes for evaluation", required=False)
        .add_array("claims", "Marketing claims on product", required=False),
    output_schema=ActionOutputSchema(description="Regulatory check result")
        .add_boolean("compliant", "Whether product is compliant in all markets")
        .add_object("market_status", "Compliance status by market")
        .add_array("requirements", "Requirements per market")
        .add_array("gaps", "Compliance gaps to address")
        .add_array("action_items", "Action items for compliance")
))
def regulatory_check(
    product_id: str,
    product_category: str,
    target_markets: List[str],
    product_attributes: Dict = None,
    claims: List[str] = None
) -> dict:
    """
    Check regulatory compliance

    Args:
        product_id: Product identifier
        product_category: Product category
        target_markets: Target markets
        product_attributes: Product attributes
        claims: Marketing claims

    Returns:
        Regulatory compliance status
    """
    product_attributes = product_attributes or {}
    claims = claims or []

    result = {
        "product_id": product_id,
        "product_category": product_category,
        "compliant": True,
        "market_status": {},
        "requirements": [],
        "gaps": [],
        "action_items": [],
        "check_date": datetime.now().isoformat()
    }

    for market in target_markets:
        market_reqs = REGULATORY_REQUIREMENTS.get(market, {})

        market_result = {
            "market": market,
            "agency": market_reqs.get("agency", "Unknown"),
            "compliant": True,
            "requirements": market_reqs.get("requirements", []),
            "issues": []
        }

        # Check basic requirements
        for req in market_reqs.get("requirements", []):
            # Simplified compliance check
            req_key = req.lower().replace(" ", "_")[:20]
            if product_attributes.get(f"has_{req_key}") is False:
                market_result["compliant"] = False
                market_result["issues"].append(f"Missing: {req}")
                result["gaps"].append({
                    "market": market,
                    "requirement": req,
                    "severity": "high"
                })
                result["action_items"].append(f"Add {req} for {market} compliance")

        # Check claims
        for claim in claims:
            claim_type = _classify_claim(claim)
            if claim_type in market_reqs.get("optional_claims_require_approval", []):
                market_result["issues"].append(f"Claim '{claim}' requires approval")
                result["action_items"].append(
                    f"Obtain approval for '{claim}' claim in {market}"
                )

        # Check language requirements
        if "local_language_required" in market_reqs.get("language_requirements", []):
            if not product_attributes.get(f"label_{market.lower()}_language"):
                market_result["issues"].append("Local language labeling required")
                result["action_items"].append(f"Translate labels for {market}")

        # California Prop 65 for US
        if market == "US" and market_reqs.get("prop65_if_ca"):
            if product_attributes.get("contains_prop65_chemicals"):
                result["action_items"].append(
                    "Add California Prop 65 warning for US distribution"
                )

        if not market_result["compliant"]:
            result["compliant"] = False

        result["market_status"][market] = market_result
        result["requirements"].append({
            "market": market,
            "agency": market_reqs.get("agency"),
            "requirements": market_reqs.get("requirements", [])
        })

    return result


def _classify_claim(claim: str) -> str:
    """Classify marketing claim type"""
    claim_lower = claim.lower()
    if any(w in claim_lower for w in ["reduce", "prevent", "cure", "treat"]):
        return "health_claims"
    if any(w in claim_lower for w in ["supports", "maintains", "promotes"]):
        return "structure_function_claims"
    if any(w in claim_lower for w in ["low", "free", "reduced", "light"]):
        return "nutrient_content_claims"
    return "general_claims"


class RegulatoryCheckAction(ApexActionBase):
    """Regulatory Check Action (class-based)"""

    name = "regulatory_check"
    description = "Check product regulatory compliance"
    category = "compliance"
    industry = "cpg"

    def execute(self, **kwargs) -> dict:
        return regulatory_check(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return regulatory_check(**event)
