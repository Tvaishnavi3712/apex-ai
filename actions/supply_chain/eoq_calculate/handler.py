"""
EOQ Calculation Action
Calculate Economic Order Quantity for inventory replenishment
"""

import os
from datetime import datetime
from typing import Dict, Any
import math

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="eoq_calculate",
    description="Calculate Economic Order Quantity for inventory replenishment",
    category="optimization",
    industry="supply_chain",
    input_schema=ActionInputSchema(description="EOQ calculation parameters")
        .add_string("sku", "SKU identifier", required=True)
        .add_number("annual_demand", "Annual demand quantity", required=True)
        .add_number("order_cost", "Cost per order (ordering cost)", required=True)
        .add_number("unit_cost", "Unit cost of item", required=True)
        .add_number("holding_cost_pct", "Annual holding cost as percentage of unit cost", required=False)
        .add_number("min_order_qty", "Minimum order quantity constraint", required=False)
        .add_number("max_order_qty", "Maximum order quantity constraint", required=False),
    output_schema=ActionOutputSchema(description="EOQ calculation result")
        .add_number("eoq", "Economic Order Quantity")
        .add_number("adjusted_eoq", "EOQ adjusted for constraints")
        .add_number("orders_per_year", "Number of orders per year")
        .add_number("order_cycle_days", "Days between orders")
        .add_number("annual_ordering_cost", "Total annual ordering cost")
        .add_number("annual_holding_cost", "Total annual holding cost")
        .add_number("total_annual_cost", "Total annual inventory cost")
))
def eoq_calculate(
    sku: str,
    annual_demand: float,
    order_cost: float,
    unit_cost: float,
    holding_cost_pct: float = 25,
    min_order_qty: float = None,
    max_order_qty: float = None
) -> dict:
    """
    Calculate EOQ

    Args:
        sku: SKU identifier
        annual_demand: Annual demand
        order_cost: Cost per order
        unit_cost: Unit cost
        holding_cost_pct: Holding cost percentage
        min_order_qty: Minimum order quantity
        max_order_qty: Maximum order quantity

    Returns:
        EOQ calculation results
    """
    result = {
        "sku": sku,
        "eoq": 0,
        "adjusted_eoq": 0,
        "orders_per_year": 0,
        "order_cycle_days": 0,
        "annual_ordering_cost": 0,
        "annual_holding_cost": 0,
        "total_annual_cost": 0,
        "calculation_date": datetime.now().isoformat()
    }

    if annual_demand <= 0 or order_cost <= 0 or unit_cost <= 0:
        result["error"] = "Invalid input: demand, order cost, and unit cost must be positive"
        return result

    # Calculate holding cost per unit
    holding_cost = unit_cost * (holding_cost_pct / 100)

    # Calculate EOQ using Wilson formula: sqrt(2DS/H)
    # D = annual demand, S = order cost, H = holding cost per unit
    eoq = math.sqrt((2 * annual_demand * order_cost) / holding_cost)
    result["eoq"] = round(eoq, 0)

    # Apply constraints
    adjusted_eoq = eoq
    if min_order_qty and adjusted_eoq < min_order_qty:
        adjusted_eoq = min_order_qty
    if max_order_qty and adjusted_eoq > max_order_qty:
        adjusted_eoq = max_order_qty

    result["adjusted_eoq"] = round(adjusted_eoq, 0)

    # Calculate derived metrics
    orders_per_year = annual_demand / adjusted_eoq
    result["orders_per_year"] = round(orders_per_year, 2)
    result["order_cycle_days"] = round(365 / orders_per_year, 1)

    # Calculate costs
    annual_ordering_cost = orders_per_year * order_cost
    average_inventory = adjusted_eoq / 2
    annual_holding_cost = average_inventory * holding_cost

    result["annual_ordering_cost"] = round(annual_ordering_cost, 2)
    result["annual_holding_cost"] = round(annual_holding_cost, 2)
    result["total_annual_cost"] = round(annual_ordering_cost + annual_holding_cost, 2)

    # Additional analysis
    result["analysis"] = {
        "average_inventory": round(average_inventory, 0),
        "inventory_investment": round(average_inventory * unit_cost, 2),
        "unit_cost": unit_cost,
        "holding_cost_per_unit": round(holding_cost, 2),
        "constraints_applied": min_order_qty is not None or max_order_qty is not None
    }

    # Compare with current ordering pattern if different from EOQ
    if abs(adjusted_eoq - eoq) > eoq * 0.1:
        # Calculate cost difference
        optimal_ordering_cost = (annual_demand / eoq) * order_cost
        optimal_holding_cost = (eoq / 2) * holding_cost
        optimal_total = optimal_ordering_cost + optimal_holding_cost

        result["analysis"]["cost_vs_optimal"] = round(
            result["total_annual_cost"] - optimal_total, 2
        )
        result["analysis"]["recommendation"] = "Consider adjusting order quantity constraints"

    return result


class EOQCalculateAction(ApexActionBase):
    """EOQ Calculation Action (class-based)"""

    name = "eoq_calculate"
    description = "Calculate Economic Order Quantity"
    category = "optimization"
    industry = "supply_chain"

    def execute(self, **kwargs) -> dict:
        return eoq_calculate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return eoq_calculate(**event)
