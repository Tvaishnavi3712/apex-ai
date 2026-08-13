"""
Scorecard Generation Action
Generate supplier performance scorecards
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="scorecard_generate",
    description="Generate supplier performance scorecards",
    category="supplier_management",
    industry="supply_chain",
    input_schema=ActionInputSchema(description="Scorecard generation parameters")
        .add_string("vendor_id", "Vendor identifier", required=True)
        .add_string("period", "Evaluation period (YYYY-MM)", required=True)
        .add_object("delivery_metrics", "Delivery performance metrics", required=True)
        .add_object("quality_metrics", "Quality performance metrics", required=True)
        .add_object("cost_metrics", "Cost performance metrics", required=False)
        .add_object("responsiveness_metrics", "Responsiveness metrics", required=False),
    output_schema=ActionOutputSchema(description="Scorecard result")
        .add_string("vendor_id", "Vendor identifier")
        .add_number("overall_score", "Overall score 0-100")
        .add_string("rating", "Rating: excellent, good, acceptable, needs_improvement, critical")
        .add_object("category_scores", "Scores by category")
        .add_array("strengths", "Identified strengths")
        .add_array("improvements", "Areas for improvement")
        .add_string("trend", "Performance trend vs previous period")
))
def scorecard_generate(
    vendor_id: str,
    period: str,
    delivery_metrics: Dict[str, Any],
    quality_metrics: Dict[str, Any],
    cost_metrics: Dict[str, Any] = None,
    responsiveness_metrics: Dict[str, Any] = None
) -> dict:
    """
    Generate supplier scorecard

    Args:
        vendor_id: Vendor identifier
        period: Evaluation period
        delivery_metrics: Delivery metrics
        quality_metrics: Quality metrics
        cost_metrics: Cost metrics
        responsiveness_metrics: Responsiveness metrics

    Returns:
        Supplier scorecard
    """
    cost_metrics = cost_metrics or {}
    responsiveness_metrics = responsiveness_metrics or {}

    # Define weights
    weights = {
        "delivery": 0.30,
        "quality": 0.30,
        "cost": 0.20,
        "responsiveness": 0.20
    }

    result = {
        "vendor_id": vendor_id,
        "period": period,
        "overall_score": 0,
        "rating": "needs_improvement",
        "category_scores": {},
        "strengths": [],
        "improvements": [],
        "trend": "stable",
        "generation_date": datetime.now().isoformat()
    }

    # Calculate delivery score
    delivery_score = _calculate_delivery_score(delivery_metrics)
    result["category_scores"]["delivery"] = {
        "score": delivery_score,
        "weight": weights["delivery"],
        "metrics": delivery_metrics
    }

    # Calculate quality score
    quality_score = _calculate_quality_score(quality_metrics)
    result["category_scores"]["quality"] = {
        "score": quality_score,
        "weight": weights["quality"],
        "metrics": quality_metrics
    }

    # Calculate cost score
    cost_score = _calculate_cost_score(cost_metrics) if cost_metrics else 75
    result["category_scores"]["cost"] = {
        "score": cost_score,
        "weight": weights["cost"],
        "metrics": cost_metrics
    }

    # Calculate responsiveness score
    resp_score = _calculate_responsiveness_score(responsiveness_metrics) if responsiveness_metrics else 75
    result["category_scores"]["responsiveness"] = {
        "score": resp_score,
        "weight": weights["responsiveness"],
        "metrics": responsiveness_metrics
    }

    # Calculate weighted overall score
    overall = (
        delivery_score * weights["delivery"] +
        quality_score * weights["quality"] +
        cost_score * weights["cost"] +
        resp_score * weights["responsiveness"]
    )
    result["overall_score"] = round(overall, 1)

    # Determine rating
    if overall >= 90:
        result["rating"] = "excellent"
    elif overall >= 80:
        result["rating"] = "good"
    elif overall >= 70:
        result["rating"] = "acceptable"
    elif overall >= 60:
        result["rating"] = "needs_improvement"
    else:
        result["rating"] = "critical"

    # Identify strengths and improvements
    scores = {
        "delivery": delivery_score,
        "quality": quality_score,
        "cost": cost_score,
        "responsiveness": resp_score
    }

    for category, score in scores.items():
        if score >= 90:
            result["strengths"].append(f"Excellent {category} performance ({score})")
        elif score >= 80:
            result["strengths"].append(f"Strong {category} performance ({score})")
        elif score < 70:
            result["improvements"].append(f"Improve {category} performance (current: {score})")

    return result


def _calculate_delivery_score(metrics: dict) -> float:
    """Calculate delivery performance score"""
    otd = metrics.get("on_time_delivery_pct", 0)
    complete_shipment = metrics.get("complete_shipment_pct", 0)
    doc_accuracy = metrics.get("documentation_accuracy_pct", 0)

    # Weighted average
    score = (otd * 0.5) + (complete_shipment * 0.3) + (doc_accuracy * 0.2)
    return round(score, 1)


def _calculate_quality_score(metrics: dict) -> float:
    """Calculate quality performance score"""
    incoming_quality = metrics.get("incoming_quality_pct", 0)
    ppm = metrics.get("ppm_defects", 0)
    car_closure = metrics.get("car_closure_pct", 0)

    # Convert PPM to score (0 PPM = 100, 10000 PPM = 0)
    ppm_score = max(0, 100 - (ppm / 100))

    score = (incoming_quality * 0.4) + (ppm_score * 0.4) + (car_closure * 0.2)
    return round(score, 1)


def _calculate_cost_score(metrics: dict) -> float:
    """Calculate cost performance score"""
    price_variance = metrics.get("price_variance_pct", 0)  # Negative is good
    invoice_accuracy = metrics.get("invoice_accuracy_pct", 0)
    cost_reduction = metrics.get("cost_reduction_pct", 0)

    # Convert variance to score
    variance_score = max(0, 100 - abs(price_variance) * 10)

    score = (variance_score * 0.4) + (invoice_accuracy * 0.4) + (min(cost_reduction * 10, 20) + 80) * 0.2
    return round(min(score, 100), 1)


def _calculate_responsiveness_score(metrics: dict) -> float:
    """Calculate responsiveness score"""
    quote_response = metrics.get("quote_response_days", 5)
    issue_response = metrics.get("issue_response_hours", 24)
    flexibility = metrics.get("flexibility_score", 70)

    # Convert to scores (lower is better for response times)
    quote_score = max(0, 100 - (quote_response - 1) * 20)  # 1 day = 100, 5+ days = 0
    issue_score = max(0, 100 - (issue_response - 4) * 5)  # 4 hours = 100, 24+ hours = 0

    score = (quote_score * 0.3) + (issue_score * 0.4) + (flexibility * 0.3)
    return round(score, 1)


class ScorecardGenerateAction(ApexActionBase):
    """Scorecard Generation Action (class-based)"""

    name = "scorecard_generate"
    description = "Generate supplier scorecards"
    category = "supplier_management"
    industry = "supply_chain"

    def execute(self, **kwargs) -> dict:
        return scorecard_generate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return scorecard_generate(**event)
