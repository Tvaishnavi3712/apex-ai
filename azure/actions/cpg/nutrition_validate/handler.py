"""
Nutrition Validation Action
Validate nutrition facts and claims
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Daily values for nutrients (FDA)
DAILY_VALUES = {
    "total_fat": {"dv": 78, "unit": "g"},
    "saturated_fat": {"dv": 20, "unit": "g"},
    "trans_fat": {"dv": 0, "unit": "g", "no_dv": True},
    "cholesterol": {"dv": 300, "unit": "mg"},
    "sodium": {"dv": 2300, "unit": "mg"},
    "total_carbohydrate": {"dv": 275, "unit": "g"},
    "dietary_fiber": {"dv": 28, "unit": "g"},
    "total_sugars": {"dv": 50, "unit": "g"},
    "added_sugars": {"dv": 50, "unit": "g"},
    "protein": {"dv": 50, "unit": "g"},
    "vitamin_d": {"dv": 20, "unit": "mcg"},
    "calcium": {"dv": 1300, "unit": "mg"},
    "iron": {"dv": 18, "unit": "mg"},
    "potassium": {"dv": 4700, "unit": "mg"}
}

# Nutrient claim thresholds
CLAIM_THRESHOLDS = {
    "free": {"fat": 0.5, "sodium": 5, "sugar": 0.5, "calories": 5},
    "low": {"fat": 3, "sodium": 140, "sugar": None, "calories": 40},
    "reduced": {"minimum_reduction": 25}  # 25% reduction required
}


@apex_action(ApexActionSchema(
    name="nutrition_validate",
    description="Validate nutrition facts and nutrient content claims",
    category="compliance",
    industry="cpg",
    input_schema=ActionInputSchema(description="Nutrition validation parameters")
        .add_string("product_id", "Product identifier", required=True)
        .add_object("nutrition_facts", "Nutrition facts data", required=True)
        .add_number("serving_size_g", "Serving size in grams", required=True)
        .add_array("nutrient_claims", "Nutrient content claims being made", required=False),
    output_schema=ActionOutputSchema(description="Nutrition validation result")
        .add_boolean("valid", "Whether nutrition data is valid")
        .add_object("calculated_dvs", "Calculated daily value percentages")
        .add_array("claim_validations", "Validation results for claims")
        .add_array("issues", "Issues found")
        .add_array("warnings", "Warnings for consideration")
))
def nutrition_validate(
    product_id: str,
    nutrition_facts: Dict[str, float],
    serving_size_g: float,
    nutrient_claims: List[str] = None
) -> dict:
    """
    Validate nutrition facts

    Args:
        product_id: Product identifier
        nutrition_facts: Nutrition data
        serving_size_g: Serving size in grams
        nutrient_claims: Claims to validate

    Returns:
        Nutrition validation results
    """
    nutrient_claims = nutrient_claims or []

    result = {
        "product_id": product_id,
        "serving_size_g": serving_size_g,
        "valid": True,
        "calculated_dvs": {},
        "claim_validations": [],
        "issues": [],
        "warnings": [],
        "validation_date": datetime.now().isoformat()
    }

    # Calculate daily value percentages
    for nutrient, value in nutrition_facts.items():
        nutrient_key = nutrient.lower().replace(" ", "_")
        dv_info = DAILY_VALUES.get(nutrient_key)

        if dv_info and not dv_info.get("no_dv"):
            dv_pct = round((value / dv_info["dv"]) * 100, 1)
            result["calculated_dvs"][nutrient] = {
                "amount": value,
                "unit": dv_info["unit"],
                "daily_value_pct": dv_pct
            }

            # Warn on high values
            if dv_pct > 20 and nutrient_key in ["sodium", "saturated_fat", "added_sugars"]:
                result["warnings"].append(
                    f"High {nutrient}: {dv_pct}% DV per serving"
                )

    # Validate nutrient claims
    for claim in nutrient_claims:
        claim_result = _validate_claim(claim, nutrition_facts, serving_size_g)
        result["claim_validations"].append(claim_result)

        if not claim_result["valid"]:
            result["valid"] = False
            result["issues"].append({
                "claim": claim,
                "issue": claim_result["reason"]
            })

    # Check calorie calculation
    calculated_calories = _calculate_calories(nutrition_facts)
    stated_calories = nutrition_facts.get("calories", 0)

    if abs(calculated_calories - stated_calories) > 20:
        result["warnings"].append(
            f"Calorie discrepancy: stated {stated_calories}, calculated {calculated_calories:.0f}"
        )

    return result


def _validate_claim(claim: str, nutrition_facts: Dict, serving_size_g: float) -> dict:
    """Validate a nutrient content claim"""
    claim_lower = claim.lower()

    result = {
        "claim": claim,
        "valid": False,
        "reason": ""
    }

    # Parse claim
    if "free" in claim_lower:
        claim_type = "free"
    elif "low" in claim_lower:
        claim_type = "low"
    elif "reduced" in claim_lower or "less" in claim_lower:
        claim_type = "reduced"
    else:
        claim_type = "other"

    # Determine nutrient
    nutrient = None
    if "fat" in claim_lower:
        nutrient = "fat"
        actual_value = nutrition_facts.get("total_fat", 0)
    elif "sodium" in claim_lower or "salt" in claim_lower:
        nutrient = "sodium"
        actual_value = nutrition_facts.get("sodium", 0)
    elif "sugar" in claim_lower:
        nutrient = "sugar"
        actual_value = nutrition_facts.get("total_sugars", 0)
    elif "calorie" in claim_lower:
        nutrient = "calories"
        actual_value = nutrition_facts.get("calories", 0)
    else:
        result["reason"] = "Unable to determine nutrient for claim"
        return result

    # Validate against thresholds
    threshold = CLAIM_THRESHOLDS.get(claim_type, {}).get(nutrient)

    if threshold is None:
        result["reason"] = f"No threshold defined for {claim_type} {nutrient}"
        return result

    if actual_value <= threshold:
        result["valid"] = True
        result["reason"] = f"Meets {claim_type} threshold: {actual_value} <= {threshold}"
    else:
        result["reason"] = f"Exceeds {claim_type} threshold: {actual_value} > {threshold}"

    return result


def _calculate_calories(nutrition_facts: Dict) -> float:
    """Calculate calories from macros"""
    fat = nutrition_facts.get("total_fat", 0)
    carbs = nutrition_facts.get("total_carbohydrate", 0)
    protein = nutrition_facts.get("protein", 0)

    return (fat * 9) + (carbs * 4) + (protein * 4)


class NutritionValidateAction(ApexActionBase):
    """Nutrition Validation Action (class-based)"""

    name = "nutrition_validate"
    description = "Validate nutrition facts and claims"
    category = "compliance"
    industry = "cpg"

    def execute(self, **kwargs) -> dict:
        return nutrition_validate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return nutrition_validate(**event)
