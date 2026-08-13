"""
Allergen Check Action
Check products for allergen content and labeling requirements
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Major allergens by market
MAJOR_ALLERGENS = {
    "US": [  # FDA Big 9
        "milk", "eggs", "fish", "shellfish", "tree_nuts",
        "peanuts", "wheat", "soybeans", "sesame"
    ],
    "EU": [  # EU 14 allergens
        "cereals_gluten", "crustaceans", "eggs", "fish", "peanuts",
        "soybeans", "milk", "nuts", "celery", "mustard",
        "sesame", "sulphites", "lupin", "molluscs"
    ],
    "CA": [
        "eggs", "milk", "mustard", "peanuts", "crustaceans_molluscs",
        "fish", "sesame", "soy", "sulphites", "tree_nuts", "wheat_triticale", "gluten"
    ]
}

# Ingredient to allergen mapping
INGREDIENT_ALLERGENS = {
    "whey": "milk",
    "casein": "milk",
    "lactose": "milk",
    "butter": "milk",
    "cream": "milk",
    "egg_whites": "eggs",
    "albumin": "eggs",
    "mayonnaise": "eggs",
    "soy_lecithin": "soybeans",
    "tofu": "soybeans",
    "miso": "soybeans",
    "flour": "wheat",
    "bread_crumbs": "wheat",
    "semolina": "wheat",
    "almond": "tree_nuts",
    "cashew": "tree_nuts",
    "walnut": "tree_nuts",
    "pecan": "tree_nuts",
    "pistachio": "tree_nuts",
    "shrimp": "shellfish",
    "crab": "shellfish",
    "lobster": "shellfish",
    "anchovy": "fish",
    "tuna": "fish",
    "salmon": "fish"
}


@apex_action(ApexActionSchema(
    name="allergen_check",
    description="Check products for allergen content and labeling requirements",
    category="compliance",
    industry="cpg",
    input_schema=ActionInputSchema(description="Allergen check parameters")
        .add_string("product_id", "Product identifier", required=True)
        .add_array("ingredients", "Product ingredients list", required=True)
        .add_array("target_markets", "Target markets for compliance", required=False)
        .add_boolean("check_cross_contact", "Check for cross-contact risks", required=False),
    output_schema=ActionOutputSchema(description="Allergen check result")
        .add_array("allergens_detected", "Allergens found in product")
        .add_object("market_declarations", "Required declarations by market")
        .add_array("labeling_requirements", "Specific labeling requirements")
        .add_array("cross_contact_warnings", "Cross-contact warnings if applicable")
        .add_boolean("requires_allergen_label", "Whether allergen labeling is required")
))
def allergen_check(
    product_id: str,
    ingredients: List[str],
    target_markets: List[str] = None,
    check_cross_contact: bool = False
) -> dict:
    """
    Check product for allergens

    Args:
        product_id: Product identifier
        ingredients: Ingredients list
        target_markets: Target markets
        check_cross_contact: Check cross-contact

    Returns:
        Allergen analysis results
    """
    target_markets = target_markets or ["US"]

    result = {
        "product_id": product_id,
        "allergens_detected": [],
        "market_declarations": {},
        "labeling_requirements": [],
        "cross_contact_warnings": [],
        "requires_allergen_label": False,
        "check_date": datetime.now().isoformat()
    }

    detected_allergens = set()

    # Check each ingredient for allergens
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower().replace(" ", "_").replace("-", "_")

        # Direct allergen check
        for market, allergens in MAJOR_ALLERGENS.items():
            if market in target_markets:
                for allergen in allergens:
                    if allergen in ingredient_lower:
                        detected_allergens.add(allergen)

        # Check ingredient mapping
        if ingredient_lower in INGREDIENT_ALLERGENS:
            detected_allergens.add(INGREDIENT_ALLERGENS[ingredient_lower])

        # Partial match check
        for ing_key, allergen in INGREDIENT_ALLERGENS.items():
            if ing_key in ingredient_lower:
                detected_allergens.add(allergen)

    result["allergens_detected"] = list(detected_allergens)
    result["requires_allergen_label"] = len(detected_allergens) > 0

    # Generate market-specific declarations
    for market in target_markets:
        market_allergens = MAJOR_ALLERGENS.get(market, [])
        relevant = [a for a in detected_allergens if a in market_allergens]

        if relevant:
            declaration = _generate_declaration(relevant, market)
            result["market_declarations"][market] = {
                "allergens": relevant,
                "declaration_text": declaration,
                "format": _get_format_requirements(market)
            }

            result["labeling_requirements"].append({
                "market": market,
                "requirements": _get_labeling_requirements(market, relevant)
            })

    # Cross-contact warnings
    if check_cross_contact:
        result["cross_contact_warnings"] = _check_cross_contact(ingredients)

    return result


def _generate_declaration(allergens: List[str], market: str) -> str:
    """Generate allergen declaration text"""
    formatted = [a.replace("_", " ").title() for a in allergens]

    if market == "US":
        return f"Contains: {', '.join(formatted)}"
    elif market == "EU":
        return f"Allergens: {', '.join(formatted)} (highlighted in ingredient list)"
    elif market == "CA":
        en = f"Contains: {', '.join(formatted)}"
        fr = f"Contient: {', '.join(formatted)}"
        return f"{en} / {fr}"
    else:
        return f"Contains: {', '.join(formatted)}"


def _get_format_requirements(market: str) -> dict:
    """Get formatting requirements for market"""
    if market == "US":
        return {
            "position": "after_ingredient_list",
            "format": "Contains statement",
            "emphasis": "bold_recommended"
        }
    elif market == "EU":
        return {
            "position": "within_ingredient_list",
            "format": "emphasized_text",
            "emphasis": "bold_required"
        }
    elif market == "CA":
        return {
            "position": "after_ingredient_list",
            "format": "Contains statement",
            "language": "bilingual_required"
        }
    return {}


def _get_labeling_requirements(market: str, allergens: List[str]) -> List[str]:
    """Get specific labeling requirements"""
    requirements = []

    if market == "US":
        requirements.append("Include 'Contains' statement following ingredient list")
        requirements.append("Use common allergen names (e.g., 'milk' not 'lactose')")
    elif market == "EU":
        requirements.append("Emphasize allergens in bold within ingredient list")
        requirements.append("Use allergen name from Annex II of Regulation 1169/2011")
    elif market == "CA":
        requirements.append("Provide allergen declaration in English and French")
        requirements.append("Include source of allergen if not obvious from name")

    return requirements


def _check_cross_contact(ingredients: List[str]) -> List[str]:
    """Check for potential cross-contact risks"""
    warnings = []

    # Common cross-contact scenarios
    has_nuts = any("nut" in i.lower() for i in ingredients)
    has_gluten = any(g in i.lower() for i in ingredients for g in ["wheat", "barley", "rye"])

    if has_nuts:
        warnings.append("May contain traces of other tree nuts due to shared equipment")
    if has_gluten:
        warnings.append("Produced in facility that processes wheat")

    return warnings


class AllergenCheckAction(ApexActionBase):
    """Allergen Check Action (class-based)"""

    name = "allergen_check"
    description = "Check products for allergen content"
    category = "compliance"
    industry = "cpg"

    def execute(self, **kwargs) -> dict:
        return allergen_check(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return allergen_check(**event)
