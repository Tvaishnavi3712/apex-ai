"""
Label Compliance Action
Validate product label compliance with regulatory requirements
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="label_compliance",
    description="Validate product label compliance with regulatory requirements",
    category="compliance",
    industry="cpg",
    input_schema=ActionInputSchema(description="Label compliance parameters")
        .add_string("product_id", "Product identifier", required=True)
        .add_object("label_elements", "Label elements to validate", required=True)
        .add_string("target_market", "Target market for validation", required=True)
        .add_string("package_size", "Package display panel size", required=False),
    output_schema=ActionOutputSchema(description="Label compliance result")
        .add_boolean("compliant", "Whether label is compliant")
        .add_number("compliance_score", "Compliance score 0-100")
        .add_array("issues", "Compliance issues found")
        .add_array("recommendations", "Recommendations for improvement")
        .add_object("element_status", "Status of each label element")
))
def label_compliance(
    product_id: str,
    label_elements: Dict[str, Any],
    target_market: str,
    package_size: str = None
) -> dict:
    """
    Check label compliance

    Args:
        product_id: Product identifier
        label_elements: Label elements
        target_market: Target market
        package_size: Package size

    Returns:
        Label compliance results
    """
    result = {
        "product_id": product_id,
        "target_market": target_market,
        "compliant": True,
        "compliance_score": 100,
        "issues": [],
        "recommendations": [],
        "element_status": {},
        "validation_date": datetime.now().isoformat()
    }

    required_elements = _get_required_elements(target_market)
    deductions = 0

    for element, requirements in required_elements.items():
        element_value = label_elements.get(element)

        status = {
            "element": element,
            "present": element_value is not None,
            "compliant": True,
            "issues": []
        }

        if requirements.get("required") and element_value is None:
            status["compliant"] = False
            status["issues"].append("Required element missing")
            result["issues"].append({
                "element": element,
                "issue": "Missing required element",
                "severity": "high"
            })
            deductions += requirements.get("weight", 10)
            result["compliant"] = False

        elif element_value is not None:
            # Validate format
            format_issues = _validate_format(element, element_value, requirements, target_market)
            if format_issues:
                status["issues"].extend(format_issues)
                for issue in format_issues:
                    result["issues"].append({
                        "element": element,
                        "issue": issue,
                        "severity": "medium"
                    })
                    deductions += 5

        result["element_status"][element] = status

    # Calculate score
    result["compliance_score"] = max(0, 100 - deductions)

    # Generate recommendations
    if result["compliance_score"] < 100:
        result["recommendations"] = _generate_recommendations(result["issues"], target_market)

    return result


def _get_required_elements(market: str) -> dict:
    """Get required label elements for market"""
    base_elements = {
        "product_name": {"required": True, "weight": 15},
        "net_quantity": {"required": True, "weight": 10, "format": "metric_imperial"},
        "ingredient_list": {"required": True, "weight": 15},
        "allergen_declaration": {"required": True, "weight": 15},
        "nutrition_facts": {"required": True, "weight": 15},
        "manufacturer_address": {"required": True, "weight": 10}
    }

    if market == "US":
        base_elements["serving_size"] = {"required": True, "weight": 10}
    elif market == "EU":
        base_elements["date_marking"] = {"required": True, "weight": 10}
        base_elements["storage_instructions"] = {"required": True, "weight": 5}
    elif market == "CA":
        base_elements["bilingual_text"] = {"required": True, "weight": 15}

    return base_elements


def _validate_format(element: str, value: Any, requirements: dict, market: str) -> List[str]:
    """Validate element format"""
    issues = []

    if element == "net_quantity":
        if market == "US" and not isinstance(value, dict):
            issues.append("Net quantity should include both metric and imperial units")
        elif market in ["EU", "CA"] and "metric" not in str(value).lower():
            issues.append("Net quantity should be in metric units")

    elif element == "allergen_declaration":
        if isinstance(value, list):
            if market == "EU":
                # EU requires allergens in bold/highlighted
                issues.append("Verify allergens are highlighted in ingredient list")

    elif element == "nutrition_facts":
        if isinstance(value, dict):
            required_nutrients = ["calories", "total_fat", "sodium", "carbohydrates", "protein"]
            for nutrient in required_nutrients:
                if nutrient not in value:
                    issues.append(f"Missing required nutrient: {nutrient}")

    return issues


def _generate_recommendations(issues: List[dict], market: str) -> List[str]:
    """Generate recommendations based on issues"""
    recommendations = []

    high_severity = [i for i in issues if i.get("severity") == "high"]
    if high_severity:
        recommendations.append("Address high-severity issues before product launch")

    if any(i.get("element") == "allergen_declaration" for i in issues):
        recommendations.append(f"Review allergen labeling requirements for {market}")

    if any(i.get("element") == "nutrition_facts" for i in issues):
        recommendations.append("Ensure all required nutrients are included in Nutrition Facts")

    return recommendations


class LabelComplianceAction(ApexActionBase):
    """Label Compliance Action (class-based)"""

    name = "label_compliance"
    description = "Validate product label compliance"
    category = "compliance"
    industry = "cpg"

    def execute(self, **kwargs) -> dict:
        return label_compliance(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return label_compliance(**event)
