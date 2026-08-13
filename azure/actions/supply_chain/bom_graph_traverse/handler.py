"""
Apex Action: BOM Graph Traversal
Supply Chain Disruption Mitigation — Upward BOM Traversal

This action takes a delayed raw material component and recursively traverses
the Bill of Materials (BOM) upwards to identify all affected finished goods,
then cross-references those against active production schedules across plants.

Usage in Playbook:
  action_id: supply_chain.bom_graph_traverse
  inputs:
    component_id: "MAT-VINYL-RESIN-001"
    delay_days: 7
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import sys
import os

# Allow running standalone without the full Apex SDK
try:
    from actions.sdk.base import ApexActionBase
    BASE_CLASS = ApexActionBase
except ImportError:
    class ApexActionBase:
        pass
    BASE_CLASS = ApexActionBase

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# BOM Graph Data Store (simulates enterprise governed data lake query)
# In production: replaced by Athena/Synapse SQL recursive CTE or graph query
# ---------------------------------------------------------------------------

# Component catalog: raw materials and sub-assemblies
COMPONENT_CATALOG = {
    "MAT-VINYL-RESIN-001": {
        "name": "Vinyl Resin (PVC Compound)",
        "type": "raw_material",
        "unit": "LB",
        "unit_cost": 0.85,
        "primary_supplier": "Gulf Coast Polymers",
        "alt_suppliers": ["Midwest Resins Inc.", "Eastern Polymer Group"],
        "lead_time_days": 14,
    },
    "MAT-VINYL-RESIN-002": {
        "name": "Vinyl Resin (Impact Modified)",
        "type": "raw_material",
        "unit": "LB",
        "unit_cost": 1.10,
        "primary_supplier": "Gulf Coast Polymers",
        "alt_suppliers": ["Midwest Resins Inc."],
        "lead_time_days": 14,
    },
    "SUB-VINYL-PROFILE-A": {
        "name": "Vinyl Window Profile A (Extruded)",
        "type": "sub_assembly",
        "unit": "LF",
        "unit_cost": 3.20,
        "components": [
            {"component_id": "MAT-VINYL-RESIN-001", "qty_per_unit": 2.5},
        ],
    },
    "SUB-VINYL-PROFILE-B": {
        "name": "Vinyl Window Profile B (Commercial Grade)",
        "type": "sub_assembly",
        "unit": "LF",
        "unit_cost": 4.80,
        "components": [
            {"component_id": "MAT-VINYL-RESIN-001", "qty_per_unit": 4.0},
            {"component_id": "MAT-VINYL-RESIN-002", "qty_per_unit": 1.5},
        ],
    },
    "SUB-DOOR-FRAME-C": {
        "name": "Sliding Door Frame Assembly",
        "type": "sub_assembly",
        "unit": "EA",
        "unit_cost": 42.00,
        "components": [
            {"component_id": "MAT-VINYL-RESIN-001", "qty_per_unit": 5.5},
        ],
    },
}

# Finished goods BOM: maps finished goods to their sub-assemblies
FINISHED_GOODS_BOM = {
    "FG-WIN-500": {
        "name": "Premium Vinyl Double-Hung Window (36x48)",
        "product_line": "Residential Windows",
        "unit_price": 285.00,
        "components": [
            {"component_id": "SUB-VINYL-PROFILE-A", "qty_per_unit": 12},
        ],
    },
    "FG-WIN-750": {
        "name": "Commercial Vinyl Fixed Window (48x60)",
        "product_line": "Commercial Windows",
        "unit_price": 420.00,
        "components": [
            {"component_id": "SUB-VINYL-PROFILE-B", "qty_per_unit": 16},
        ],
    },
    "FG-DOOR-200": {
        "name": "Vinyl Sliding Patio Door (72x80)",
        "product_line": "Patio Doors",
        "unit_price": 680.00,
        "components": [
            {"component_id": "SUB-DOOR-FRAME-C", "qty_per_unit": 2},
            {"component_id": "SUB-VINYL-PROFILE-A", "qty_per_unit": 8},
        ],
    },
    "FG-WIN-300": {
        "name": "Economy Vinyl Casement Window (24x36)",
        "product_line": "Residential Windows",
        "unit_price": 195.00,
        "components": [
            {"component_id": "SUB-VINYL-PROFILE-A", "qty_per_unit": 8},
        ],
    },
}

# Active production schedules across 93 plants (sample of affected plants)
PRODUCTION_SCHEDULES = [
    {
        "schedule_id": "SCHED-OH-2026-0501",
        "plant_id": "PLANT-OH-01",
        "plant_name": "Cuyahoga Falls, OH",
        "finished_good_id": "FG-WIN-500",
        "scheduled_start": "2026-05-01",
        "scheduled_end": "2026-05-14",
        "units_planned": 1200,
        "buffer_inventory_days": 3,
    },
    {
        "schedule_id": "SCHED-TX-2026-0503",
        "plant_id": "PLANT-TX-04",
        "plant_name": "Grand Prairie, TX",
        "finished_good_id": "FG-DOOR-200",
        "scheduled_start": "2026-05-03",
        "scheduled_end": "2026-05-17",
        "units_planned": 400,
        "buffer_inventory_days": 2,
    },
    {
        "schedule_id": "SCHED-GA-2026-0506",
        "plant_id": "PLANT-GA-07",
        "plant_name": "Cartersville, GA",
        "finished_good_id": "FG-WIN-750",
        "scheduled_start": "2026-05-06",
        "scheduled_end": "2026-05-20",
        "units_planned": 600,
        "buffer_inventory_days": 5,
    },
    {
        "schedule_id": "SCHED-OH-2026-0508",
        "plant_id": "PLANT-OH-01",
        "plant_name": "Cuyahoga Falls, OH",
        "finished_good_id": "FG-WIN-300",
        "scheduled_start": "2026-05-08",
        "scheduled_end": "2026-05-18",
        "units_planned": 2000,
        "buffer_inventory_days": 4,
    },
]


# ---------------------------------------------------------------------------
# Core Action Class
# ---------------------------------------------------------------------------

class BOMGraphTraverseAction(BASE_CLASS):
    """
    Apex Action: BOM Graph Traversal for Supply Chain Disruption Mitigation.

    Traverses the BOM DAG upward from a delayed component to find all affected
    finished goods, then maps those to active production schedules to calculate
    revenue at risk and recommend mitigation options.
    """

    name = "bom_graph_traverse"
    description = (
        "Traverse BOM upwards from a delayed component to find all affected "
        "finished goods and active plant production schedules."
    )
    category = "supply_chain"
    industry = "manufacturing"

    def execute(
        self,
        component_id: str,
        delay_days: int,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Main execution method.

        Args:
            component_id: The ID of the delayed raw material or sub-assembly.
            delay_days: Number of days the component is delayed.
            context: Optional Apex context dict (passed by Playbook engine).

        Returns:
            Full impact report with affected plants, revenue at risk, and
            mitigation options.
        """
        logger.info(f"[BOMGraphTraverse] Starting upward traversal for: {component_id}, delay: {delay_days}d")

        # Step 1: Find all sub-assemblies that use this component
        affected_sub_assemblies = self._find_affected_sub_assemblies(component_id)
        logger.info(f"  → Affected sub-assemblies: {len(affected_sub_assemblies)}")

        # Step 2: Find all finished goods that use those sub-assemblies
        affected_finished_goods = self._find_affected_finished_goods(
            {component_id} | affected_sub_assemblies
        )
        logger.info(f"  → Affected finished goods: {len(affected_finished_goods)}")

        # Step 3: Cross-reference with active production schedules
        impacted_schedules = self._calculate_schedule_impact(
            affected_finished_goods, delay_days
        )
        logger.info(f"  → Impacted production schedules: {len(impacted_schedules)}")

        # Step 4: Evaluate alternative suppliers
        alternatives = self._evaluate_alternatives(component_id, delay_days)

        # Step 5: Compute totals
        total_revenue_at_risk = sum(s["revenue_at_risk"] for s in impacted_schedules)
        affected_plants = list({s["plant_id"] for s in impacted_schedules})

        severity = (
            "critical" if total_revenue_at_risk > 500_000
            else "high" if total_revenue_at_risk > 100_000
            else "medium"
        )

        return {
            "action": "bom_graph_traverse",
            "status": "completed",
            "severity": severity,
            "trigger_component": {
                "component_id": component_id,
                "name": COMPONENT_CATALOG.get(component_id, {}).get("name", component_id),
                "delay_days": delay_days,
            },
            "blast_radius": {
                "sub_assemblies_affected": len(affected_sub_assemblies),
                "finished_goods_affected": len(affected_finished_goods),
                "plants_affected": len(affected_plants),
                "plant_ids": affected_plants,
            },
            "financial_impact": {
                "total_revenue_at_risk": round(total_revenue_at_risk, 2),
                "total_units_at_risk": sum(s["units_at_risk"] for s in impacted_schedules),
            },
            "impacted_schedules": impacted_schedules,
            "mitigation_options": alternatives,
            "recommendation": self._generate_recommendation(
                alternatives, total_revenue_at_risk, delay_days
            ),
            "traversed_at": datetime.utcnow().isoformat() + "Z",
            "factory_id": "bom_graph_traverse",
            "factory_version": "1.0.0",
        }

    # -----------------------------------------------------------------------
    # Graph Traversal Methods
    # -----------------------------------------------------------------------

    def _find_affected_sub_assemblies(self, component_id: str) -> Set[str]:
        """
        BFS upward through sub-assemblies to find all that use the component.
        In production: replaced by recursive SQL CTE or graph DB query.
        """
        affected: Set[str] = set()
        queue = [component_id]
        visited: Set[str] = set()

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for sub_id, sub_data in COMPONENT_CATALOG.items():
                if sub_data.get("type") == "sub_assembly":
                    component_ids = [
                        c["component_id"]
                        for c in sub_data.get("components", [])
                    ]
                    if current in component_ids:
                        affected.add(sub_id)
                        queue.append(sub_id)

        return affected

    def _find_affected_finished_goods(self, affected_components: Set[str]) -> List[Dict]:
        """
        Find all finished goods that use any of the affected components.
        """
        affected_fgs = []
        for fg_id, fg_data in FINISHED_GOODS_BOM.items():
            component_ids = {
                c["component_id"] for c in fg_data.get("components", [])
            }
            if component_ids & affected_components:
                affected_fgs.append({
                    "finished_good_id": fg_id,
                    "name": fg_data["name"],
                    "product_line": fg_data["product_line"],
                    "unit_price": fg_data["unit_price"],
                })
        return affected_fgs

    def _calculate_schedule_impact(
        self, affected_fgs: List[Dict], delay_days: int
    ) -> List[Dict]:
        """
        Cross-reference affected finished goods against active production schedules.
        Calculates net delay after accounting for buffer inventory.
        """
        fg_ids = {fg["finished_good_id"] for fg in affected_fgs}
        fg_lookup = {fg["finished_good_id"]: fg for fg in affected_fgs}

        impacted = []
        for sched in PRODUCTION_SCHEDULES:
            if sched["finished_good_id"] not in fg_ids:
                continue

            fg = fg_lookup[sched["finished_good_id"]]
            buffer = sched.get("buffer_inventory_days", 0)
            net_delay = max(0, delay_days - buffer)
            units_at_risk = sched["units_planned"] if net_delay > 0 else 0
            revenue_at_risk = round(units_at_risk * fg["unit_price"], 2)

            impacted.append({
                "schedule_id": sched["schedule_id"],
                "plant_id": sched["plant_id"],
                "plant_name": sched["plant_name"],
                "finished_good_id": sched["finished_good_id"],
                "finished_good_name": fg["name"],
                "scheduled_start": sched["scheduled_start"],
                "units_planned": sched["units_planned"],
                "units_at_risk": units_at_risk,
                "buffer_inventory_days": buffer,
                "net_delay_days": net_delay,
                "revenue_at_risk": revenue_at_risk,
                "status": "at_risk" if net_delay > 0 else "buffered",
            })

        return impacted

    def _evaluate_alternatives(self, component_id: str, delay_days: int) -> List[Dict]:
        """
        Evaluate alternative suppliers for the delayed component.
        In production: queries the Approved Vendor List (AVL) in the ERP.
        """
        comp = COMPONENT_CATALOG.get(component_id, {})
        alt_suppliers = comp.get("alt_suppliers", [])
        base_cost = comp.get("unit_cost", 1.0)

        options = []
        for i, supplier in enumerate(alt_suppliers):
            premium_pct = (i + 1) * 5  # 5%, 10% cost premium per alternative
            options.append({
                "option": chr(65 + i),  # A, B, C ...
                "type": "reroute_supplier",
                "supplier": supplier,
                "cost_premium_pct": premium_pct,
                "estimated_delay_days": max(0, delay_days - (i + 1) * 2),
                "capacity_available": True,
                "description": (
                    f"Reroute from {supplier} "
                    f"(+{premium_pct}% cost, "
                    f"{max(0, delay_days - (i+1)*2)}-day delay)"
                ),
            })

        # Add a production resequencing option
        options.append({
            "option": chr(65 + len(alt_suppliers)),
            "type": "resequence_production",
            "supplier": None,
            "cost_premium_pct": 0,
            "estimated_delay_days": delay_days,
            "capacity_available": True,
            "description": (
                f"Resequence production at buffered plants (0% cost premium, "
                f"{delay_days}-day delay for unbuffered lines)"
            ),
        })

        return options

    def _generate_recommendation(
        self,
        options: List[Dict],
        revenue_at_risk: float,
        delay_days: int,
    ) -> str:
        """
        Generates a plain-English recommendation for the Supply Chain Director.
        """
        if not options:
            return "No mitigation options available. Escalate to Supply Chain Director immediately."

        best = options[0]
        fallback = options[-1]

        return (
            f"RECOMMENDED ACTION: ${revenue_at_risk:,.0f} revenue at risk across "
            f"{delay_days} days. "
            f"{best['description']} is the fastest path to resolution. "
            f"If supplier capacity is unavailable, {fallback['description']}."
        )


# ---------------------------------------------------------------------------
# Lambda Entry Point
# ---------------------------------------------------------------------------

def handler(event, lambda_context=None):
    """Azure Functions entry point."""
    action = BOMGraphTraverseAction()
    return action.execute(
        component_id=event.get("component_id", "MAT-VINYL-RESIN-001"),
        delay_days=event.get("delay_days", 7),
        context=event.get("context"),
    )


# ---------------------------------------------------------------------------
# Local Test Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    test_event = {
        "component_id": "MAT-VINYL-RESIN-001",
        "delay_days": 7,
    }

    print("=" * 60)
    print("BOM Graph Traversal — Local Test")
    print("=" * 60)
    result = handler(test_event)
    print(json.dumps(result, indent=2))
