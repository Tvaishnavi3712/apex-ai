"""
Apex Logistics Agent — Foundry Agent Service runtime for CBB Demo 3 (Disruption Impact &
Reroute).

Owns: GSM disruption alerts, BOM graph traversal, financial impact projection,
reroute option ranking, and Director escalations. Powers the CBB Logistics
agent in Agent Hub.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


app = FoundryAgentApp()

SYSTEM_PROMPT = """You are Logistics Agent, the AI assistant for Cornerstone Building Brands' Supply Chain team. You specialize in disruption impact analysis and reroute planning.

Domain context:
- Alert source: Global Supply Chain Monitor (GSM) — emits XML alerts for port strikes, supplier delays, natural disasters.
- BOM: Bill of Materials stored as a graph in Amazon Athena (federated). Traversal finds every product + plant downstream of an affected supplier.
- Plants covered: Ohio 7, Texas 14, Georgia 31 (among 28 total).
- Reroute options are ranked PREFERRED / FALLBACK / LAST_RESORT based on (a) alt-supplier capacity, (b) cost delta, (c) lead-time impact.
- Escalation threshold: value_at_risk_usd > $500,000 → Supply Chain Director (Marcus Webb).

Active hero work item (if referenced):
- SC-ALERT-2026-0441 — Port Strike · Port of Savannah, GA · HIGH severity
  - Supplier: Chemours Vinyl Resins (SUP-0044) · Material: Vinyl Resin (PVC Grade A)
  - Expected delay: 7 days
  - BOM traversal: 847 nodes · 3 affected plants
  - Value at risk: $1,090,000 (Ohio $412k + Texas $386k + Georgia $292k)
  - Reroute options (ranked):
    * Option A (PREFERRED): Oxy Vinyls LP · +5% cost · 0-day delay
    * Option B (FALLBACK):  Resequence Georgia · $0 cost · 2-day delay
    * Option C (LAST RESORT): Air freight Formosa · +22% cost · 0-day delay
  - Decision: ESCALATED to Marcus Webb (exceeds $500k threshold)

Recent precedent (last 30 days):
- 142 GSM alerts · 128 auto-mitigated · 14 escalated to Director
- Avg time-to-mitigation: 2.1s
- Auto-dispatched reroute success rate: 96%

When answering:
1. Use tools to pull BOM + financial data — don't make up dollar figures.
2. Always quantify exposure in USD and by plant.
3. When asked "should I approve Option A", explain the trade-off: cost vs delay vs capacity.
4. If the user sounds like Marcus Webb or a Director, offer the 3 options with your recommendation.
5. Keep responses executive-dense — 2–4 short paragraphs, use bullet lists for options. No filler.
"""


@tool
def get_alert_detail(alert_id: str) -> dict:
    """Look up a GSM disruption alert by ID."""
    seeded = {
        "SC-ALERT-2026-0441": {
            "alert_id": "SC-ALERT-2026-0441",
            "event_type": "PortStrike",
            "severity": "HIGH",
            "port": "Port of Savannah, GA",
            "affected_supplier": "Chemours Vinyl Resins",
            "supplier_id": "SUP-0044",
            "material": "Vinyl Resin (PVC Grade A)",
            "delay_days": 7,
            "expected_recovery": "2026-04-28",
            "source_confidence": 0.99,
            "timestamp": "2026-04-21T09:08:00Z",
        },
        "SC-ALERT-2026-0442": {
            "alert_id": "SC-ALERT-2026-0442",
            "event_type": "SupplierDelay",
            "severity": "MEDIUM",
            "port": None,
            "affected_supplier": "ChemCo Industries",
            "supplier_id": "SUP-0092",
            "material": "Vinyl Resin (VR-2201)",
            "delay_days": 7,
            "expected_recovery": "2026-04-28",
            "source_confidence": 0.91,
        },
    }
    return seeded.get(alert_id, {"alert_id": alert_id, "found": False})


@tool
def traverse_bom(supplier_id: str, material: str) -> dict:
    """Traverse the BOM graph for a supplier+material combo to find affected products and plants.

    Returns the traversal result including units at risk per plant.
    """
    traversal = {
        ("SUP-0044", "Vinyl Resin (PVC Grade A)"): {
            "nodes_traversed": 847,
            "affected_plants": [
                {"plant": "Ohio Plant 7",    "units_at_risk": 1240, "value_at_risk_usd": 412000},
                {"plant": "Texas Plant 14",  "units_at_risk":  980, "value_at_risk_usd": 386000},
                {"plant": "Georgia Plant 31","units_at_risk":  740, "value_at_risk_usd": 292000},
            ],
            "total_value_at_risk_usd": 1090000,
            "affected_sku_count": 14,
        }
    }
    key = (supplier_id, material)
    if key in traversal:
        return traversal[key]
    return {
        "nodes_traversed": 0,
        "affected_plants": [],
        "total_value_at_risk_usd": 0,
        "message": f"No BOM links found for {supplier_id} / {material}.",
    }


@tool
def generate_reroute_options(affected_supplier: str, material: str) -> dict:
    """Generate ranked reroute options given the affected supplier + material."""
    if affected_supplier.lower().startswith("chemours"):
        return {
            "options": [
                {"rank": "A", "tier": "PREFERRED",   "supplier": "Oxy Vinyls LP",       "cost_delta_pct": 5,  "delay_days": 0, "capacity": "SUFFICIENT"},
                {"rank": "B", "tier": "FALLBACK",    "supplier": "Resequence Georgia",  "cost_delta_pct": 0,  "delay_days": 2, "capacity": "PARTIAL"},
                {"rank": "C", "tier": "LAST_RESORT", "supplier": "Formosa (air freight)","cost_delta_pct": 22, "delay_days": 0, "capacity": "SUFFICIENT"},
            ],
        }
    return {"options": [], "message": f"No pre-qualified alternates for {affected_supplier}."}


@tool
def project_financial_impact(plants: list, unit_price_usd: float) -> dict:
    """Project total value at risk across a list of affected plants."""
    total = 0.0
    breakdown = []
    for p in plants:
        units = int(p.get("units_at_risk", 0))
        val = units * float(unit_price_usd)
        breakdown.append({"plant": p.get("plant", "?"), "units": units, "value_at_risk_usd": val})
        total += val
    return {"plants": breakdown, "total_value_at_risk_usd": round(total, 2)}


@tool
def escalate_to_director(alert_id: str, value_at_risk_usd: float, recommended_option: str) -> dict:
    """Escalate a disruption to the Supply Chain Director (Marcus Webb) with a recommendation."""
    if value_at_risk_usd <= 500000:
        return {
            "escalated": False,
            "reason": f"${value_at_risk_usd:,.0f} is below $500k auto-escalation threshold. Auto-dispatch instead.",
        }
    return {
        "escalated": True,
        "director": "Marcus Webb",
        "alert_id": alert_id,
        "value_at_risk_usd": value_at_risk_usd,
        "recommended_option": recommended_option,
        "sla_hours": 2,
        "channel": "#supply-chain-leadership",
    }


# Lazy-init: Foundry Agent Service enforces a 30s cold-start budget. Build the Agent on
# the first invoke() so module import stays cheap.
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        model = AzureOpenAIModel(model_id="us.amazon.nova-pro-v1:0")
        _agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                get_alert_detail,
                traverse_bom,
                generate_reroute_options,
                project_financial_impact,
                escalate_to_director,
            ],
        )
    return _agent


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = _get_agent()(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
