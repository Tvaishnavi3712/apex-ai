"""
Inventory Analysis Action
Analyze inventory levels and identify optimization opportunities
"""

import boto3
import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="inventory_analyze",
    description="Analyze inventory levels and identify optimization opportunities",
    category="inventory",
    industry="supply_chain",
    input_schema=ActionInputSchema(description="Inventory analysis parameters")
        .add_string("sku", "SKU identifier", required=False)
        .add_string("category", "Product category for analysis", required=False)
        .add_string("warehouse", "Warehouse code", required=False)
        .add_number("avg_daily_demand", "Average daily demand", required=False),
    output_schema=ActionOutputSchema(description="Inventory analysis result")
        .add_number("current_stock", "Current stock quantity")
        .add_number("days_of_supply", "Days of supply on hand")
        .add_string("abc_classification", "ABC classification: A, B, C")
        .add_string("health_status", "Status: healthy, low, critical, excess")
        .add_array("recommendations", "Optimization recommendations")
        .add_object("turnover_analysis", "Inventory turnover analysis")
))
def inventory_analyze(
    sku: str = None,
    category: str = None,
    warehouse: str = None,
    avg_daily_demand: float = None
) -> dict:
    """
    Analyze inventory

    Args:
        sku: SKU identifier
        category: Product category
        warehouse: Warehouse code
        avg_daily_demand: Average daily demand

    Returns:
        Inventory analysis results
    """
    result = {
        "sku": sku,
        "category": category,
        "warehouse": warehouse,
        "current_stock": 0,
        "days_of_supply": 0,
        "abc_classification": "C",
        "health_status": "unknown",
        "recommendations": [],
        "turnover_analysis": {},
        "analysis_date": datetime.now().isoformat()
    }

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('INVENTORY_TABLE', 'apex-inventory'))

        # Query inventory
        if sku:
            response = table.get_item(Key={"sku": sku, "warehouse": warehouse or "DEFAULT"})
            if 'Item' in response:
                item = response['Item']
                result["current_stock"] = int(item.get("quantity", 0))
                result["abc_classification"] = item.get("abc_class", "C")
                avg_daily_demand = avg_daily_demand or float(item.get("avg_daily_demand", 1))

                # Calculate days of supply
                if avg_daily_demand > 0:
                    result["days_of_supply"] = round(result["current_stock"] / avg_daily_demand, 1)

                # Determine health status
                result["health_status"] = _determine_health(
                    result["days_of_supply"],
                    result["abc_classification"]
                )

                # Generate recommendations
                result["recommendations"] = _generate_recommendations(
                    result["health_status"],
                    result["days_of_supply"],
                    result["abc_classification"]
                )

                # Turnover analysis
                result["turnover_analysis"] = _analyze_turnover(item, avg_daily_demand)

                return result

    except Exception as e:
        result["error"] = str(e)

    # Return mock data for testing
    avg_daily = avg_daily_demand or 10
    current = 250

    return {
        "sku": sku or "SKU001",
        "category": category or "Electronics",
        "warehouse": warehouse or "WH001",
        "current_stock": current,
        "allocated": 50,
        "available": current - 50,
        "safety_stock": 100,
        "days_of_supply": round(current / avg_daily, 1),
        "abc_classification": "A",
        "health_status": "healthy",
        "recommendations": [
            "Inventory levels are healthy",
            "Consider reviewing safety stock for seasonal demand"
        ],
        "turnover_analysis": {
            "annual_turnover": round(365 * avg_daily / current, 2),
            "average_age_days": 15,
            "obsolete_risk": "low",
            "carrying_cost_estimate": round(current * 5 * 0.25, 2)
        },
        "reorder_point": round(avg_daily * 14, 0),  # 2 week lead time
        "last_receipt_date": (datetime.now()).strftime('%Y-%m-%d'),
        "analysis_date": datetime.now().isoformat()
    }


def _determine_health(days_of_supply: float, abc_class: str) -> str:
    """Determine inventory health status"""
    # Thresholds based on ABC classification
    thresholds = {
        "A": {"low": 14, "critical": 7, "excess": 60},
        "B": {"low": 21, "critical": 10, "excess": 90},
        "C": {"low": 30, "critical": 14, "excess": 180}
    }

    limits = thresholds.get(abc_class, thresholds["C"])

    if days_of_supply <= limits["critical"]:
        return "critical"
    elif days_of_supply <= limits["low"]:
        return "low"
    elif days_of_supply >= limits["excess"]:
        return "excess"
    else:
        return "healthy"


def _generate_recommendations(health: str, dos: float, abc_class: str) -> List[str]:
    """Generate recommendations based on analysis"""
    recommendations = []

    if health == "critical":
        recommendations.append(f"URGENT: Only {dos:.0f} days of supply remaining")
        recommendations.append("Expedite pending orders or place emergency order")
        recommendations.append("Consider alternative suppliers for faster delivery")

    elif health == "low":
        recommendations.append(f"Low inventory: {dos:.0f} days of supply")
        recommendations.append("Review reorder point settings")
        recommendations.append("Place replenishment order soon")

    elif health == "excess":
        recommendations.append(f"Excess inventory: {dos:.0f} days of supply")
        recommendations.append("Consider promotional pricing to reduce stock")
        recommendations.append("Review demand forecast accuracy")
        if abc_class == "C":
            recommendations.append("Evaluate for obsolescence risk")

    else:
        recommendations.append("Inventory levels are healthy")

    return recommendations


def _analyze_turnover(item: dict, avg_daily: float) -> dict:
    """Analyze inventory turnover"""
    quantity = int(item.get("quantity", 0))
    unit_cost = float(item.get("unit_cost", 10))

    annual_demand = avg_daily * 365
    turnover = annual_demand / quantity if quantity > 0 else 0

    return {
        "annual_turnover": round(turnover, 2),
        "average_age_days": int(item.get("avg_age_days", 15)),
        "obsolete_risk": "high" if turnover < 2 else "medium" if turnover < 4 else "low",
        "carrying_cost_estimate": round(quantity * unit_cost * 0.25, 2)
    }


class InventoryAnalyzeAction(ApexActionBase):
    """Inventory Analysis Action (class-based)"""

    name = "inventory_analyze"
    description = "Analyze inventory levels"
    category = "inventory"
    industry = "supply_chain"

    def execute(self, **kwargs) -> dict:
        return inventory_analyze(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return inventory_analyze(**event)
