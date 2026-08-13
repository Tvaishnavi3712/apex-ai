"""
Ingredient Validation Action
Validate product ingredients against regulatory databases
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Ingredient status database (simplified)
INGREDIENT_DATABASE = {
    "sugar": {"status": "approved", "category": "sweetener", "gras": True},
    "high_fructose_corn_syrup": {"status": "approved", "category": "sweetener", "gras": True, "restrictions": ["prop65_ca"]},
    "aspartame": {"status": "approved", "category": "artificial_sweetener", "gras": True, "warnings": ["phenylketonurics"]},
    "red_40": {"status": "approved", "category": "color_additive", "gras": False, "fda_cert_required": True},
    "yellow_5": {"status": "approved", "category": "color_additive", "gras": False, "fda_cert_required": True},
    "carrageenan": {"status": "approved", "category": "thickener", "gras": True, "organic_allowed": False},
    "titanium_dioxide": {"status": "restricted", "category": "color_additive", "banned_in": ["EU"], "fda_status": "under_review"},
    "brominated_vegetable_oil": {"status": "banned", "category": "emulsifier", "banned_in": ["US", "EU"]},
    "potassium_bromate": {"status": "banned", "category": "flour_treatment", "banned_in": ["EU", "CA", "UK"]},
    "sodium_benzoate": {"status": "approved", "category": "preservative", "gras": True, "max_level_ppm": 1000}
}


@apex_action(ApexActionSchema(
    name="ingredient_validate",
    description="Validate product ingredients against regulatory databases",
    category="compliance",
    industry="cpg",
    input_schema=ActionInputSchema(description="Ingredient validation parameters")
        .add_string("product_id", "Product identifier", required=True)
        .add_array("ingredients", "List of ingredients to validate", required=True)
        .add_array("target_markets", "Target markets for compliance check", required=False)
        .add_boolean("organic_product", "Whether product is labeled organic", required=False),
    output_schema=ActionOutputSchema(description="Ingredient validation result")
        .add_boolean("all_approved", "Whether all ingredients are approved")
        .add_array("validated_ingredients", "Validation results per ingredient")
        .add_array("warnings", "Warnings requiring attention")
        .add_array("blockers", "Issues blocking product release")
        .add_object("market_compliance", "Compliance status by market")
))
def ingredient_validate(
    product_id: str,
    ingredients: List[str],
    target_markets: List[str] = None,
    organic_product: bool = False
) -> dict:
    """
    Validate product ingredients

    Args:
        product_id: Product identifier
        ingredients: List of ingredients
        target_markets: Target markets
        organic_product: Is organic product

    Returns:
        Ingredient validation results
    """
    target_markets = target_markets or ["US"]

    result = {
        "product_id": product_id,
        "all_approved": True,
        "validated_ingredients": [],
        "warnings": [],
        "blockers": [],
        "market_compliance": {market: True for market in target_markets},
        "validation_date": datetime.now().isoformat()
    }

    for ingredient in ingredients:
        ingredient_lower = ingredient.lower().replace(" ", "_").replace("-", "_")
        db_entry = INGREDIENT_DATABASE.get(ingredient_lower, {})

        validation = {
            "ingredient": ingredient,
            "status": db_entry.get("status", "unknown"),
            "category": db_entry.get("category", "unknown"),
            "gras_status": db_entry.get("gras", None),
            "issues": []
        }

        # Check if banned
        if db_entry.get("status") == "banned":
            validation["issues"].append("BANNED - Cannot be used in products")
            result["all_approved"] = False
            result["blockers"].append(f"{ingredient}: Banned substance")
            for market in target_markets:
                result["market_compliance"][market] = False

        # Check market-specific bans
        banned_markets = db_entry.get("banned_in", [])
        for market in target_markets:
            if market in banned_markets:
                validation["issues"].append(f"Banned in {market}")
                result["market_compliance"][market] = False
                result["blockers"].append(f"{ingredient}: Banned in {market}")
                result["all_approved"] = False

        # Check organic restrictions
        if organic_product and db_entry.get("organic_allowed") is False:
            validation["issues"].append("Not allowed in organic products")
            result["warnings"].append(f"{ingredient}: Not permitted in organic products")

        # Check FDA certification requirements
        if db_entry.get("fda_cert_required"):
            validation["issues"].append("FDA batch certification required")
            result["warnings"].append(f"{ingredient}: Requires FDA color additive certification")

        # Check warnings
        if db_entry.get("warnings"):
            for warning in db_entry["warnings"]:
                validation["issues"].append(f"Warning required: {warning}")
                result["warnings"].append(f"{ingredient}: Requires {warning} warning")

        # Check restrictions
        if db_entry.get("restrictions"):
            for restriction in db_entry["restrictions"]:
                validation["issues"].append(f"Restriction: {restriction}")

        result["validated_ingredients"].append(validation)

    return result


class IngredientValidateAction(ApexActionBase):
    """Ingredient Validation Action (class-based)"""

    name = "ingredient_validate"
    description = "Validate product ingredients"
    category = "compliance"
    industry = "cpg"

    def execute(self, **kwargs) -> dict:
        return ingredient_validate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return ingredient_validate(**event)
