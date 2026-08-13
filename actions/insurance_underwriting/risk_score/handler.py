"""
Risk Score Action
Calculate risk score for insurance underwriting
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="risk_score",
    description="Calculate risk score for insurance underwriting decisions",
    category="underwriting",
    industry="insurance_underwriting",
    input_schema=ActionInputSchema(description="Risk scoring parameters")
        .add_string("application_id", "Application identifier", required=True)
        .add_string("line_of_business", "Insurance line: auto, home, commercial, life", required=True)
        .add_object("applicant_info", "Applicant information", required=True)
        .add_object("coverage_details", "Requested coverage details", required=True)
        .add_array("risk_factors", "Additional risk factors", required=False),
    output_schema=ActionOutputSchema(description="Risk score result")
        .add_number("risk_score", "Overall risk score 1-999")
        .add_string("risk_tier", "Risk tier: preferred, standard, substandard, decline")
        .add_array("risk_components", "Individual risk components")
        .add_array("adverse_factors", "Factors negatively impacting score")
        .add_array("favorable_factors", "Factors positively impacting score")
        .add_boolean("requires_review", "Whether manual review is required")
))
def risk_score(
    application_id: str,
    line_of_business: str,
    applicant_info: Dict[str, Any],
    coverage_details: Dict[str, Any],
    risk_factors: List[Dict] = None
) -> dict:
    """
    Calculate risk score

    Args:
        application_id: Application ID
        line_of_business: Line of business
        applicant_info: Applicant info
        coverage_details: Coverage details
        risk_factors: Additional risk factors

    Returns:
        Risk score and analysis
    """
    risk_factors = risk_factors or []

    result = {
        "application_id": application_id,
        "line_of_business": line_of_business,
        "risk_score": 500,
        "risk_tier": "standard",
        "risk_components": [],
        "adverse_factors": [],
        "favorable_factors": [],
        "requires_review": False,
        "scoring_date": datetime.now().isoformat()
    }

    base_score = 500
    adjustments = []

    # Age-based scoring
    age = applicant_info.get("age", 35)
    if line_of_business == "auto":
        if age < 25:
            adjustments.append(("age_young", 100))
            result["adverse_factors"].append("Driver under 25")
        elif age > 65:
            adjustments.append(("age_senior", 50))
            result["adverse_factors"].append("Driver over 65")
        elif 30 <= age <= 55:
            adjustments.append(("age_prime", -50))
            result["favorable_factors"].append("Prime age driver")

    # Credit-based scoring
    credit_score = applicant_info.get("credit_score", 700)
    if credit_score >= 750:
        adjustments.append(("credit_excellent", -100))
        result["favorable_factors"].append("Excellent credit score")
    elif credit_score >= 700:
        adjustments.append(("credit_good", -50))
        result["favorable_factors"].append("Good credit score")
    elif credit_score < 600:
        adjustments.append(("credit_poor", 150))
        result["adverse_factors"].append("Poor credit score")

    # Claims history
    claims_count = applicant_info.get("claims_last_5_years", 0)
    if claims_count == 0:
        adjustments.append(("claims_free", -75))
        result["favorable_factors"].append("Claims-free history")
    elif claims_count >= 3:
        adjustments.append(("claims_multiple", 200))
        result["adverse_factors"].append(f"{claims_count} claims in last 5 years")
        result["requires_review"] = True

    # Line-specific factors
    if line_of_business == "auto":
        adjustments.extend(_score_auto_factors(applicant_info, result))
    elif line_of_business == "home":
        adjustments.extend(_score_home_factors(applicant_info, coverage_details, result))
    elif line_of_business == "commercial":
        adjustments.extend(_score_commercial_factors(applicant_info, coverage_details, result))
        result["requires_review"] = True  # Commercial always requires review

    # Apply adjustments
    for factor, adjustment in adjustments:
        base_score += adjustment
        result["risk_components"].append({
            "factor": factor,
            "adjustment": adjustment
        })

    # Normalize score to 1-999
    final_score = max(1, min(999, base_score))
    result["risk_score"] = final_score

    # Determine tier
    if final_score <= 350:
        result["risk_tier"] = "preferred"
    elif final_score <= 550:
        result["risk_tier"] = "standard"
    elif final_score <= 750:
        result["risk_tier"] = "substandard"
        result["requires_review"] = True
    else:
        result["risk_tier"] = "decline"
        result["requires_review"] = True

    return result


def _score_auto_factors(applicant_info: dict, result: dict) -> List[tuple]:
    """Score auto-specific factors"""
    adjustments = []

    # Driving record
    violations = applicant_info.get("violations_last_3_years", 0)
    if violations > 0:
        adjustments.append(("violations", violations * 50))
        result["adverse_factors"].append(f"{violations} traffic violations")

    dui = applicant_info.get("dui_history", False)
    if dui:
        adjustments.append(("dui", 300))
        result["adverse_factors"].append("DUI/DWI history")
        result["requires_review"] = True

    # Vehicle type
    vehicle_type = applicant_info.get("vehicle_type", "sedan")
    if vehicle_type in ["sports_car", "luxury"]:
        adjustments.append(("vehicle_type", 75))
        result["adverse_factors"].append("High-risk vehicle type")

    return adjustments


def _score_home_factors(applicant_info: dict, coverage: dict, result: dict) -> List[tuple]:
    """Score home-specific factors"""
    adjustments = []

    # Construction type
    construction = applicant_info.get("construction_type", "frame")
    if construction == "masonry":
        adjustments.append(("construction_masonry", -50))
        result["favorable_factors"].append("Masonry construction")

    # Roof age
    roof_age = applicant_info.get("roof_age_years", 10)
    if roof_age > 20:
        adjustments.append(("roof_old", 100))
        result["adverse_factors"].append("Roof over 20 years old")

    # Security features
    if applicant_info.get("security_system"):
        adjustments.append(("security", -25))
        result["favorable_factors"].append("Security system installed")

    # Location hazards
    if applicant_info.get("flood_zone"):
        adjustments.append(("flood_zone", 150))
        result["adverse_factors"].append("Located in flood zone")

    return adjustments


def _score_commercial_factors(applicant_info: dict, coverage: dict, result: dict) -> List[tuple]:
    """Score commercial-specific factors"""
    adjustments = []

    # Business type
    business_class = applicant_info.get("business_class", "")
    high_risk_classes = ["restaurant", "construction", "manufacturing", "trucking"]

    if business_class.lower() in high_risk_classes:
        adjustments.append(("high_risk_class", 100))
        result["adverse_factors"].append(f"High-risk business class: {business_class}")

    # Revenue
    annual_revenue = coverage.get("annual_revenue", 0)
    if annual_revenue > 10000000:
        adjustments.append(("high_exposure", 75))
        result["adverse_factors"].append("High revenue exposure")

    # Years in business
    years_in_business = applicant_info.get("years_in_business", 0)
    if years_in_business < 3:
        adjustments.append(("new_business", 75))
        result["adverse_factors"].append("Business less than 3 years old")
    elif years_in_business > 10:
        adjustments.append(("established", -50))
        result["favorable_factors"].append("Established business 10+ years")

    return adjustments


class RiskScoreAction(ApexActionBase):
    """Risk Score Action (class-based)"""

    name = "risk_score"
    description = "Calculate risk score for underwriting"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return risk_score(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return risk_score(**event)
