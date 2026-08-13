"""
Reorder Point Calculation Action
Calculate reorder points and safety stock levels
"""

import os
from datetime import datetime
from typing import Dict, Any
import math

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Z-scores for service levels
SERVICE_LEVEL_Z = {
    0.90: 1.28,
    0.95: 1.65,
    0.97: 1.88,
    0.98: 2.05,
    0.99: 2.33,
    0.999: 3.09
}


@apex_action(ApexActionSchema(
    name="reorder_point_calc",
    description="Calculate reorder points and safety stock levels",
    category="optimization",
    industry="supply_chain",
    input_schema=ActionInputSchema(description="Reorder point calculation parameters")
        .add_string("sku", "SKU identifier", required=True)
        .add_number("avg_daily_demand", "Average daily demand", required=True)
        .add_number("lead_time_days", "Lead time in days", required=True)
        .add_number("demand_std_dev", "Standard deviation of daily demand", required=False)
        .add_number("lead_time_std_dev", "Standard deviation of lead time", required=False)
        .add_number("service_level", "Target service level (0.90-0.999)", required=False)
        .add_string("abc_class", "ABC classification for policy", required=False),
    output_schema=ActionOutputSchema(description="Reorder point calculation result")
        .add_number("reorder_point", "Reorder point quantity")
        .add_number("safety_stock", "Safety stock quantity")
        .add_number("lead_time_demand", "Average demand during lead time")
        .add_number("service_level", "Target service level")
        .add_object("variability", "Demand and lead time variability")
))
def reorder_point_calc(
    sku: str,
    avg_daily_demand: float,
    lead_time_days: float,
    demand_std_dev: float = None,
    lead_time_std_dev: float = None,
    service_level: float = 0.95,
    abc_class: str = None
) -> dict:
    """
    Calculate reorder point

    Args:
        sku: SKU identifier
        avg_daily_demand: Average daily demand
        lead_time_days: Lead time in days
        demand_std_dev: Demand standard deviation
        lead_time_std_dev: Lead time standard deviation
        service_level: Target service level
        abc_class: ABC classification

    Returns:
        Reorder point calculation results
    """
    # Apply ABC-based service level if not specified
    if service_level is None:
        abc_service_levels = {"A": 0.98, "B": 0.95, "C": 0.90}
        service_level = abc_service_levels.get(abc_class, 0.95)

    # Ensure service level is valid
    service_level = max(0.90, min(0.999, service_level))

    result = {
        "sku": sku,
        "reorder_point": 0,
        "safety_stock": 0,
        "lead_time_demand": 0,
        "service_level": service_level,
        "variability": {},
        "calculation_date": datetime.now().isoformat()
    }

    # Calculate lead time demand
    lead_time_demand = avg_daily_demand * lead_time_days
    result["lead_time_demand"] = round(lead_time_demand, 0)

    # Get Z-score for service level
    z_score = _get_z_score(service_level)

    # Calculate safety stock
    # If variability data provided, use it; otherwise estimate
    if demand_std_dev is not None:
        if lead_time_std_dev is not None:
            # Combined variability formula
            combined_std = math.sqrt(
                (lead_time_days * demand_std_dev ** 2) +
                (avg_daily_demand ** 2 * lead_time_std_dev ** 2)
            )
        else:
            # Only demand variability
            combined_std = demand_std_dev * math.sqrt(lead_time_days)

        safety_stock = z_score * combined_std

        result["variability"] = {
            "demand_std_dev": demand_std_dev,
            "lead_time_std_dev": lead_time_std_dev or 0,
            "combined_std_dev": round(combined_std, 2),
            "cv_demand": round(demand_std_dev / avg_daily_demand, 3) if avg_daily_demand > 0 else 0
        }
    else:
        # Estimate safety stock as percentage of lead time demand
        # Higher for A items, lower for C items
        safety_pct = {"A": 0.30, "B": 0.25, "C": 0.20}.get(abc_class, 0.25)
        safety_stock = lead_time_demand * safety_pct

        result["variability"] = {
            "estimated": True,
            "safety_percentage": safety_pct * 100,
            "note": "Variability estimated; provide demand_std_dev for precise calculation"
        }

    result["safety_stock"] = round(safety_stock, 0)

    # Calculate reorder point
    reorder_point = lead_time_demand + safety_stock
    result["reorder_point"] = round(reorder_point, 0)

    # Additional metrics
    result["metrics"] = {
        "z_score": z_score,
        "days_of_safety_stock": round(safety_stock / avg_daily_demand, 1) if avg_daily_demand > 0 else 0,
        "expected_stockouts_per_year": round((1 - service_level) * 365 / lead_time_days, 2)
    }

    return result


def _get_z_score(service_level: float) -> float:
    """Get Z-score for service level"""
    # Find closest service level
    closest = min(SERVICE_LEVEL_Z.keys(), key=lambda x: abs(x - service_level))
    return SERVICE_LEVEL_Z[closest]


class ReorderPointAction(ApexActionBase):
    """Reorder Point Calculation Action (class-based)"""

    name = "reorder_point_calc"
    description = "Calculate reorder points"
    category = "optimization"
    industry = "supply_chain"

    def execute(self, **kwargs) -> dict:
        return reorder_point_calc(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return reorder_point_calc(**event)
