"""
Forecast Analysis Action
Analyze demand forecasts for inventory planning
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="forecast_analyze",
    description="Analyze demand forecasts for inventory planning",
    category="planning",
    industry="supply_chain",
    input_schema=ActionInputSchema(description="Forecast analysis parameters")
        .add_string("sku", "SKU identifier", required=True)
        .add_array("historical_demand", "Historical demand data by period", required=True)
        .add_number("forecast_periods", "Number of periods to forecast", required=False)
        .add_string("seasonality", "Seasonality pattern: none, monthly, quarterly", required=False),
    output_schema=ActionOutputSchema(description="Forecast analysis result")
        .add_array("forecast", "Forecasted demand by period")
        .add_number("average_demand", "Average demand")
        .add_number("demand_variability", "Demand variability (coefficient of variation)")
        .add_string("trend", "Trend direction: increasing, decreasing, stable")
        .add_object("seasonality_factors", "Seasonality adjustment factors")
        .add_number("forecast_accuracy", "Historical forecast accuracy")
))
def forecast_analyze(
    sku: str,
    historical_demand: List[Dict],
    forecast_periods: int = 3,
    seasonality: str = "none"
) -> dict:
    """
    Analyze demand forecast

    Args:
        sku: SKU identifier
        historical_demand: Historical demand data
        forecast_periods: Periods to forecast
        seasonality: Seasonality pattern

    Returns:
        Forecast analysis results
    """
    result = {
        "sku": sku,
        "forecast": [],
        "average_demand": 0,
        "demand_variability": 0,
        "trend": "stable",
        "seasonality_factors": {},
        "forecast_accuracy": 0,
        "analysis_date": datetime.now().isoformat()
    }

    if not historical_demand:
        return result

    # Extract demand values
    demands = [d.get("demand", d.get("quantity", 0)) for d in historical_demand]

    # Calculate statistics
    n = len(demands)
    if n == 0:
        return result

    avg_demand = sum(demands) / n
    result["average_demand"] = round(avg_demand, 2)

    # Calculate standard deviation and CV
    if n > 1:
        variance = sum((d - avg_demand) ** 2 for d in demands) / (n - 1)
        std_dev = math.sqrt(variance)
        cv = std_dev / avg_demand if avg_demand > 0 else 0
        result["demand_variability"] = round(cv, 3)

    # Determine trend using simple linear regression
    if n >= 3:
        x_mean = (n - 1) / 2
        y_mean = avg_demand
        numerator = sum((i - x_mean) * (demands[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0

        if slope > avg_demand * 0.05:
            result["trend"] = "increasing"
        elif slope < -avg_demand * 0.05:
            result["trend"] = "decreasing"
        else:
            result["trend"] = "stable"

    # Calculate seasonality factors
    if seasonality != "none" and n >= 4:
        result["seasonality_factors"] = _calculate_seasonality(demands, seasonality)

    # Generate forecast
    for i in range(forecast_periods):
        period_num = n + i + 1

        # Base forecast using exponential smoothing
        alpha = 0.3
        if i == 0:
            forecast_value = demands[-1] * alpha + avg_demand * (1 - alpha)
        else:
            prev_forecast = result["forecast"][-1]["forecast_quantity"]
            forecast_value = demands[-1] * alpha + prev_forecast * (1 - alpha)

        # Apply trend adjustment
        if result["trend"] == "increasing":
            forecast_value *= 1.02
        elif result["trend"] == "decreasing":
            forecast_value *= 0.98

        # Apply seasonality
        if seasonality != "none" and result["seasonality_factors"]:
            season_idx = period_num % len(result["seasonality_factors"])
            season_factor = list(result["seasonality_factors"].values())[season_idx]
            forecast_value *= season_factor

        result["forecast"].append({
            "period": period_num,
            "forecast_quantity": round(forecast_value, 0),
            "lower_bound": round(forecast_value * 0.85, 0),
            "upper_bound": round(forecast_value * 1.15, 0),
            "confidence": 0.85
        })

    # Calculate historical accuracy (mock)
    result["forecast_accuracy"] = round(85 + (10 * (1 - result["demand_variability"])), 1)

    return result


def _calculate_seasonality(demands: List[float], seasonality: str) -> dict:
    """Calculate seasonality factors"""
    if seasonality == "quarterly":
        periods = 4
    elif seasonality == "monthly":
        periods = 12
    else:
        return {}

    n = len(demands)
    if n < periods:
        return {}

    avg = sum(demands) / n
    factors = {}

    for i in range(min(periods, n)):
        # Get all demands for this seasonal period
        period_demands = [demands[j] for j in range(i, n, periods)]
        if period_demands:
            period_avg = sum(period_demands) / len(period_demands)
            factors[f"period_{i+1}"] = round(period_avg / avg, 3) if avg > 0 else 1.0

    return factors


class ForecastAnalyzeAction(ApexActionBase):
    """Forecast Analysis Action (class-based)"""

    name = "forecast_analyze"
    description = "Analyze demand forecasts"
    category = "planning"
    industry = "supply_chain"

    def execute(self, **kwargs) -> dict:
        return forecast_analyze(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return forecast_analyze(**event)
