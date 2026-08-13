"""
Apex Agentic Enterprise — OrchestratorAgent (UC-1, vendor-neutral demo).

Multi-step supply chain orchestrator. Detects an inventory shortage, ranks
alternative suppliers, drafts a purchase order, and routes it to a human
approver — with a full reasoning trace.

Data source rule (per APEX platform convention):
    NO hardcoded business data. Every fact (warehouse inventory, supplier
    lead times) is loaded at runtime from the synthetic-data files bundled
    into the deploy ZIP under /app/data/.

This agent runs on Bedrock AgentCore. The deploy script
`deploy_ae_agents.py` bundles synthetic-data/agentic_enterprise/*.json
into /app/data/ so the runtime container has them locally.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

MODEL_ID = "us.anthropic.claude-opus-4-6-v1"
REGION = "us-east-1"
AGENT_ID = "orchestrator-agent"

# Resolve the bundled data directory next to agent.py at runtime.
# AgentCore extracts the deploy ZIP and runs agent.py from that directory,
# so `__file__`'s parent is where the bundled data/ folder lives. The
# env-var override exists for local testing where the layout may differ.
_AGENT_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("APEX_AE_DATA_DIR", str(_AGENT_DIR / "data")))

SYSTEM_PROMPT = """You are OrchestratorAgent, a vendor-neutral autonomous supply-chain orchestrator.

When an operator reports an inventory shortage, you autonomously execute this plan:
  1. check_inventory(sku) — confirm the shortage across warehouses
  2. find_alternative_supplier(sku, demand_window_days) — rank approved suppliers
  3. draft_purchase_order(supplier_id, sku, quantity) — generate a PO payload
  4. submit_for_approval(po_payload) — route to a human approver

NON-NEGOTIABLE RULES:
1. NEVER auto-submit a PO. Always end with submit_for_approval — humans approve.
2. Lead with shortage facts (warehouses checked + total available + shortfall) BEFORE recommending a supplier.
3. Justify the supplier choice with on-time %, defect rate YTD, lead time, and unit cost. Reviewers do not approve black-box choices.
4. Prefer suppliers with lead time WITHIN the demand window even at higher unit cost — meeting the campaign date matters more than 5% of unit price.
5. Surface every tool call. The reasoning trace IS the audit trail.
6. End every response with: [TRACE: SCO-<run_id>]

When the user prompt contains a SKU and a quantity (or you can infer them), execute the full 4-step plan.
"""


# ─────────────────────── data loading helpers ───────────────────────


def _load_json(filename: str) -> Dict[str, Any]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Synthetic data not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


# ─────────────────────── tools ───────────────────────


@tool
def check_inventory(sku: str) -> dict:
    """Look up on-hand / available units for a SKU across all warehouses.

    Use this FIRST when an operator reports a shortage. Returns total
    available across the network plus the per-warehouse breakdown and the
    relevant demand_forecast (if any).

    Args:
        sku: SKU identifier, e.g. "SKU-892".

    Returns:
        {"sku", "total_available", "per_warehouse": [...], "demand_forecast": {...}}
    """
    try:
        data = _load_json("inventory_warehouses.json")
        per_warehouse = []
        total_available = 0
        for wh in data.get("warehouses", []):
            row = next(
                (r for r in wh.get("inventory", []) if r["sku"] == sku),
                None,
            )
            if row:
                per_warehouse.append(
                    {
                        "warehouse_id": wh["warehouse_id"],
                        "name": wh["name"],
                        "available": row["available"],
                    }
                )
                total_available += row["available"]
        forecast = data.get("demand_forecast", {}).get(sku, {})
        return {
            "status": "ok",
            "data": {
                "sku": sku,
                "total_available": total_available,
                "per_warehouse": per_warehouse,
                "demand_forecast": forecast,
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"check_inventory failed: {e}"}


@tool
def find_alternative_supplier(sku: str, demand_window_days: int = 11) -> dict:
    """Rank approved suppliers for a SKU.

    Ranking: lead-time within window first, then on-time %, then defect rate,
    then unit cost. Returns the top supplier + 2 alternates.

    Args:
        sku: SKU to source.
        demand_window_days: How many days we have to receive the goods.

    Returns:
        {"sku", "recommended": {...}, "alternates": [...]}
    """
    try:
        data = _load_json("suppliers.json")
        candidates = [
            s for s in data.get("suppliers", []) if sku in s.get("approved_skus", [])
        ]

        def rank_key(s: Dict[str, Any]) -> Tuple[int, float, float, float]:
            lead_ok = 0 if s["lead_time_days"] <= demand_window_days else 1
            return (
                lead_ok,
                -s.get("on_time_pct", 0),
                s.get("defect_rate_ytd", 1.0),
                s.get("unit_cost", {}).get(sku, 999.0),
            )

        candidates.sort(key=rank_key)
        if not candidates:
            return {
                "status": "ok",
                "data": {"sku": sku, "recommended": None, "alternates": []},
            }
        rec = candidates[0]
        return {
            "status": "ok",
            "data": {
                "sku": sku,
                "recommended": {
                    "supplier_id": rec["supplier_id"],
                    "name": rec["name"],
                    "lead_time_days": rec["lead_time_days"],
                    "on_time_pct": rec["on_time_pct"],
                    "defect_rate_ytd": rec["defect_rate_ytd"],
                    "unit_cost_usd": rec["unit_cost"][sku],
                    "min_order_qty": rec.get("min_order_qty", 1),
                    "credit_terms": rec.get("credit_terms", "TBD"),
                    "rationale": rec.get("notes", ""),
                },
                "alternates": [
                    {
                        "supplier_id": s["supplier_id"],
                        "name": s["name"],
                        "lead_time_days": s["lead_time_days"],
                        "unit_cost_usd": s["unit_cost"][sku],
                        "rationale": s.get("notes", ""),
                    }
                    for s in candidates[1:3]
                ],
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"find_alternative_supplier failed: {e}"}


@tool
def draft_purchase_order(
    supplier_id: str,
    sku: str,
    quantity: int,
    unit_cost_usd: float,
    requested_delivery: Optional[str] = None,
    credit_terms: str = "Net 30",
    incoterm: str = "DDP",
) -> dict:
    """Build a draft purchase order payload.

    Args:
        supplier_id: Approved supplier id (e.g. "SUP-321").
        sku: SKU to order.
        quantity: Units to order.
        unit_cost_usd: Per-unit cost from the supplier rec.
        requested_delivery: ISO date the goods must arrive. Defaults to demand
            forecast campaign_start if available, else today + 11 days.
        credit_terms: Net N or similar.
        incoterm: Incoterm shorthand.

    Returns:
        {"po_number", "supplier_id", "sku", "quantity", "unit_cost_usd",
         "total_usd", "incoterm", "requested_delivery", "credit_terms",
         "status": "DRAFT"}
    """
    try:
        if not requested_delivery:
            try:
                inv = _load_json("inventory_warehouses.json")
                forecast = inv.get("demand_forecast", {}).get(sku, {})
                requested_delivery = forecast.get(
                    "campaign_start",
                    (datetime.utcnow() + timedelta(days=11)).strftime("%Y-%m-%d"),
                )
            except Exception:
                requested_delivery = (datetime.utcnow() + timedelta(days=11)).strftime("%Y-%m-%d")
        total = round(unit_cost_usd * quantity, 2)
        po_number = "PO-" + datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        return {
            "status": "ok",
            "data": {
                "po_number": po_number,
                "supplier_id": supplier_id,
                "sku": sku,
                "quantity": quantity,
                "unit_cost_usd": unit_cost_usd,
                "total_usd": total,
                "incoterm": incoterm,
                "requested_delivery": requested_delivery,
                "credit_terms": credit_terms,
                "status": "DRAFT",
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"draft_purchase_order failed: {e}"}


@tool
def submit_for_approval(po_number: str, total_usd: float) -> dict:
    """Route the drafted PO to the human-review queue.

    Severity is HIGH when total_usd > 25000.

    Args:
        po_number: The drafted PO number.
        total_usd: Total cost in USD.

    Returns:
        {"queue_id", "approver", "severity", "sla_hours",
         "status": "PENDING_APPROVAL"}
    """
    try:
        severity = "HIGH" if total_usd > 25000 else "NORMAL"
        queue_id = "WQ-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return {
            "status": "ok",
            "data": {
                "queue_id": queue_id,
                "approver": "merchandising@example.com",
                "severity": severity,
                "sla_hours": 4 if severity == "HIGH" else 24,
                "po_number": po_number,
                "status": "PENDING_APPROVAL",
            },
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": f"submit_for_approval failed: {e}"}


# ─────────────────────── multi-LLM support ───────────────────────


DEFAULT_TOOL_MODEL = MODEL_ID
DEFAULT_SYNTH_MODEL = MODEL_ID
_agent_cache: Dict[tuple, Agent] = {}


def _resolve_models(model_overrides: Optional[Dict[str, Dict[str, str]]]) -> tuple:
    overrides = (model_overrides or {}).get(AGENT_ID, {})
    tool_id = overrides.get("tool_selection", DEFAULT_TOOL_MODEL)
    synth_id = overrides.get("synthesis", DEFAULT_SYNTH_MODEL)
    return tool_id, synth_id


def _get_agent(tool_model_id: str, synth_model_id: str) -> Agent:
    key = (tool_model_id, synth_model_id)
    if key in _agent_cache:
        return _agent_cache[key]
    model = BedrockModel(model_id=synth_model_id, region_name=REGION)
    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[
            check_inventory,
            find_alternative_supplier,
            draft_purchase_order,
            submit_for_approval,
        ],
    )
    _agent_cache[key] = agent
    return agent


@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_message = payload.get("prompt", "Hello")
    tool_id, synth_id = _resolve_models(payload.get("model_overrides"))
    result = _get_agent(tool_id, synth_id)(user_message)
    return {
        "result": result.message,
        "model_used": {
            "agent": AGENT_ID,
            "tool_selection_model": tool_id,
            "synthesis_model": synth_id,
        },
    }


if __name__ == "__main__":
    app.run()
