"""
Coverage Validation Action
Validate coverage requests against underwriting guidelines
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Coverage limits by line
COVERAGE_LIMITS = {
    "auto": {
        "liability_min": 25000,
        "liability_max": 1000000,
        "um_min": 25000,
        "comprehensive_max_age": 15
    },
    "home": {
        "dwelling_min": 100000,
        "dwelling_max": 5000000,
        "min_replacement_pct": 80,
        "deductible_min": 500,
        "deductible_max_pct": 5
    },
    "commercial": {
        "gl_min": 500000,
        "gl_max": 10000000,
        "property_min": 50000
    }
}


@apex_action(ApexActionSchema(
    name="coverage_validate",
    description="Validate coverage requests against underwriting guidelines",
    category="underwriting",
    industry="insurance_underwriting",
    input_schema=ActionInputSchema(description="Coverage validation parameters")
        .add_string("application_id", "Application identifier", required=True)
        .add_string("line_of_business", "Insurance line", required=True)
        .add_object("requested_coverage", "Requested coverage details", required=True)
        .add_object("property_info", "Property/asset information", required=False)
        .add_string("state", "State for regulatory compliance", required=False),
    output_schema=ActionOutputSchema(description="Coverage validation result")
        .add_boolean("valid", "Whether coverage is valid and can be bound")
        .add_array("coverage_items", "Validation status per coverage item")
        .add_array("issues", "Coverage issues requiring attention")
        .add_array("recommendations", "Coverage recommendations")
        .add_boolean("requires_adjustment", "Whether coverage needs adjustment")
))
def coverage_validate(
    application_id: str,
    line_of_business: str,
    requested_coverage: Dict[str, Any],
    property_info: Dict = None,
    state: str = None
) -> dict:
    """
    Validate coverage request

    Args:
        application_id: Application ID
        line_of_business: Line of business
        requested_coverage: Requested coverage
        property_info: Property information
        state: State code

    Returns:
        Coverage validation results
    """
    property_info = property_info or {}

    result = {
        "application_id": application_id,
        "line_of_business": line_of_business,
        "valid": True,
        "coverage_items": [],
        "issues": [],
        "recommendations": [],
        "requires_adjustment": False,
        "validation_date": datetime.now().isoformat()
    }

    limits = COVERAGE_LIMITS.get(line_of_business, {})

    if line_of_business == "auto":
        _validate_auto_coverage(requested_coverage, limits, property_info, result)
    elif line_of_business == "home":
        _validate_home_coverage(requested_coverage, limits, property_info, result)
    elif line_of_business == "commercial":
        _validate_commercial_coverage(requested_coverage, limits, property_info, result)

    # State-specific validations
    if state:
        _validate_state_requirements(requested_coverage, state, line_of_business, result)

    return result


def _validate_auto_coverage(coverage: dict, limits: dict, property_info: dict, result: dict):
    """Validate auto coverage"""
    # Liability validation
    liability = coverage.get("liability_limit", 0)
    liability_item = {
        "coverage": "Liability",
        "requested": liability,
        "valid": True,
        "issues": []
    }

    if liability < limits["liability_min"]:
        liability_item["valid"] = False
        liability_item["issues"].append(f"Below minimum: ${limits['liability_min']:,}")
        result["issues"].append({
            "coverage": "Liability",
            "issue": f"Must be at least ${limits['liability_min']:,}"
        })
        result["valid"] = False
    elif liability > limits["liability_max"]:
        liability_item["valid"] = False
        liability_item["issues"].append(f"Exceeds maximum: ${limits['liability_max']:,}")
        result["requires_adjustment"] = True

    result["coverage_items"].append(liability_item)

    # Comprehensive/Collision for older vehicles
    if coverage.get("comprehensive"):
        vehicle_age = property_info.get("vehicle_age", 0)
        comp_item = {
            "coverage": "Comprehensive/Collision",
            "requested": True,
            "valid": True,
            "issues": []
        }

        if vehicle_age > limits["comprehensive_max_age"]:
            comp_item["issues"].append(f"Vehicle over {limits['comprehensive_max_age']} years")
            result["recommendations"].append(
                "Consider removing comp/collision for older vehicle to reduce premium"
            )

        result["coverage_items"].append(comp_item)

    # UM/UIM should match liability
    um_limit = coverage.get("um_limit", 0)
    if um_limit > 0 and um_limit > liability:
        result["issues"].append({
            "coverage": "UM/UIM",
            "issue": "Cannot exceed liability limit"
        })
        result["requires_adjustment"] = True


def _validate_home_coverage(coverage: dict, limits: dict, property_info: dict, result: dict):
    """Validate home coverage"""
    # Dwelling coverage
    dwelling = coverage.get("dwelling_coverage", 0)
    replacement_cost = property_info.get("replacement_cost", dwelling)
    min_required = replacement_cost * (limits["min_replacement_pct"] / 100)

    dwelling_item = {
        "coverage": "Dwelling",
        "requested": dwelling,
        "replacement_cost": replacement_cost,
        "valid": True,
        "issues": []
    }

    if dwelling < min_required:
        dwelling_item["valid"] = False
        dwelling_item["issues"].append(f"Below {limits['min_replacement_pct']}% replacement cost")
        result["issues"].append({
            "coverage": "Dwelling",
            "issue": f"Must be at least ${min_required:,.0f} ({limits['min_replacement_pct']}% of replacement cost)"
        })
        result["requires_adjustment"] = True

    if dwelling < limits["dwelling_min"]:
        dwelling_item["valid"] = False
        result["issues"].append({
            "coverage": "Dwelling",
            "issue": f"Below company minimum: ${limits['dwelling_min']:,}"
        })
        result["valid"] = False

    result["coverage_items"].append(dwelling_item)

    # Deductible validation
    deductible = coverage.get("deductible", 1000)
    max_deductible = dwelling * (limits["deductible_max_pct"] / 100)

    if deductible < limits["deductible_min"]:
        result["issues"].append({
            "coverage": "Deductible",
            "issue": f"Below minimum: ${limits['deductible_min']}"
        })
    elif deductible > max_deductible:
        result["recommendations"].append(
            f"Deductible exceeds {limits['deductible_max_pct']}% of dwelling - consider reducing"
        )


def _validate_commercial_coverage(coverage: dict, limits: dict, property_info: dict, result: dict):
    """Validate commercial coverage"""
    # General liability
    gl_limit = coverage.get("general_liability", 0)
    gl_item = {
        "coverage": "General Liability",
        "requested": gl_limit,
        "valid": True,
        "issues": []
    }

    if gl_limit < limits["gl_min"]:
        gl_item["valid"] = False
        gl_item["issues"].append(f"Below minimum: ${limits['gl_min']:,}")
        result["issues"].append({
            "coverage": "General Liability",
            "issue": f"Minimum ${limits['gl_min']:,} required"
        })
        result["valid"] = False

    result["coverage_items"].append(gl_item)

    # Professional liability if applicable
    if property_info.get("professional_services"):
        if not coverage.get("professional_liability"):
            result["recommendations"].append(
                "Consider adding Professional Liability coverage for professional services"
            )


def _validate_state_requirements(coverage: dict, state: str, lob: str, result: dict):
    """Validate state-specific requirements"""
    # Example state requirements
    state_minimums = {
        "CA": {"auto_liability": 35000},
        "NY": {"auto_liability": 50000},
        "TX": {"auto_liability": 30000}
    }

    if state in state_minimums and lob == "auto":
        min_liability = state_minimums[state]["auto_liability"]
        if coverage.get("liability_limit", 0) < min_liability:
            result["issues"].append({
                "coverage": "Liability",
                "issue": f"{state} requires minimum ${min_liability:,} liability"
            })
            result["valid"] = False


class CoverageValidateAction(ApexActionBase):
    """Coverage Validation Action (class-based)"""

    name = "coverage_validate"
    description = "Validate coverage requests"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return coverage_validate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return coverage_validate(**event)
