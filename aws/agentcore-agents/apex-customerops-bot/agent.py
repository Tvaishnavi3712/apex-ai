"""
Apex CustomerOps Agent — AgentCore runtime for CBB Demo 1 (Zero-Touch Order
Modification).

Owns: distributor order modifications, engineering-tolerance checks, Dynamics
CRM updates, distributor confirmations. Powers the CBB CustomerOps agent in
Agent Hub.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are CustomerOps Agent, the AI assistant for Cornerstone Building Brands' Customer Service team. You specialize in zero-touch order modifications for distributor-submitted changes.

Domain context (CBB, Cornerstone Building Brands):
- Product catalog: commercial windows, doors, and building envelope systems
- Distributors submit order-modification PDFs via email to orders@cbb.com
- Engineering tolerance policy: dimensional changes up to ±5% can be auto-approved; anything beyond must route to Customer Ops Review
- CRM: Microsoft Dynamics CRM (order records stored with full history)
- Data lake: Amazon S3 + Athena federated queries against cbb_orders table

Active hero work item (if referenced):
- CBB-ORD-1044 — Midwest Window & Door Supply (Gold Partner)
  - Product: Commercial Casement Window · SKU CCW-4860-LG
  - Original: 48" × 60" → Requested: 48" × 62" (+3.3% height, within 5% tolerance)
  - Quantity: 24 units · Production start: Apr 28, 2026
  - Status: AUTO_APPROVED — CRM updated, lead time now 16 days (was 14), distributor notified

Recent precedent (last 30 days):
- Auto-approved modifications: 312 (avg variance 2.1%)
- Routed to Customer Ops: 24 (avg variance 7.8%)
- Average processing time: 4.2s

When answering:
1. Use the tools to look up real data when the user asks about specific orders, SKUs, or distributors.
2. Cite concrete numbers (dimensions, quantities, tolerance %, lead-time deltas) — no generic platitudes.
3. If the user asks "what happens next" or "what does approve do", describe the 5-step recipe: BDA extract → Athena lookup → tolerance check → CRM update → distributor email.
4. If asked about a work item you don't have data for, say so and offer to look it up — never invent numbers.
5. Keep responses tight (2–4 short paragraphs or a short bullet list). This is a business-ops chat, not a lecture.
"""


@tool
def get_original_order(order_id: str) -> dict:
    """Look up the original order in the CBB data lake (Athena).

    Args:
        order_id: CBB order ID, e.g. 'CBB-ORD-1044'

    Returns:
        Original order details with dimensions, SKU, quantity, and production status.
    """
    # Demo data seeded to match the hero work items the sales team uses.
    seeded = {
        "CBB-ORD-1044": {
            "order_id": "CBB-ORD-1044",
            "distributor": "Midwest Window & Door Supply",
            "distributor_tier": "Gold Partner",
            "product": "Commercial Casement Window",
            "product_sku": "CCW-4860-LG",
            "original_dimensions": {"width_in": 48, "height_in": 60},
            "quantity": 24,
            "production_status": "SCHEDULED",
            "production_start": "2026-04-28",
            "lead_time_days": 14,
        },
        "CBB-ORD-1047": {
            "order_id": "CBB-ORD-1047",
            "distributor": "Midwest Window & Door Supply",
            "distributor_tier": "Gold Partner",
            "product": "Commercial Casement Window",
            "product_sku": "CCW-4860-LG",
            "original_dimensions": {"width_in": 48, "height_in": 60},
            "quantity": 24,
            "production_status": "STARTED",
            "production_start": "2026-04-24",
            "lead_time_days": 14,
        },
    }
    return seeded.get(order_id, {"order_id": order_id, "found": False, "message": "Order not in data lake — check with distributor for correct order ID."})


@tool
def check_engineering_tolerance(
    original_width_in: float,
    original_height_in: float,
    requested_width_in: float,
    requested_height_in: float,
    tolerance_pct: float = 5.0,
) -> dict:
    """Verify requested dimensions stay within engineering tolerance (default ±5%).

    Returns the delta for each axis plus a pass/fail decision.
    """
    if original_width_in == 0 or original_height_in == 0:
        return {"pass": False, "reason": "Missing original dimensions — cannot compute variance."}
    width_delta_pct  = abs(requested_width_in  - original_width_in)  / original_width_in  * 100.0
    height_delta_pct = abs(requested_height_in - original_height_in) / original_height_in * 100.0
    passed = width_delta_pct <= tolerance_pct and height_delta_pct <= tolerance_pct
    return {
        "pass": passed,
        "width_delta_pct":  round(width_delta_pct, 2),
        "height_delta_pct": round(height_delta_pct, 2),
        "tolerance_pct": tolerance_pct,
        "message": "Within tolerance — safe to auto-approve." if passed
                   else f"Exceeds {tolerance_pct}% tolerance — route to Customer Ops Review.",
    }


@tool
def update_crm_order(order_id: str, new_width_in: float, new_height_in: float, quantity: int) -> dict:
    """Update the order record in Microsoft Dynamics CRM and recalculate lead time.

    Returns the updated order confirmation with new lead time.
    """
    return {
        "crm": "Microsoft Dynamics",
        "order_id": order_id,
        "new_dimensions": {"width_in": new_width_in, "height_in": new_height_in},
        "quantity": quantity,
        "new_lead_time_days": 16,
        "confirmation_id": f"CRM-CONF-{order_id}",
        "status": "UPDATED",
        "timestamp": "2026-04-21T09:17:00Z",
    }


@tool
def send_distributor_email(distributor_email: str, order_id: str, template: str = "order_modification_confirmation") -> dict:
    """Send a templated email to the distributor via SendGrid.

    Args:
        distributor_email: distributor contact email
        order_id: CBB order id being modified
        template: email template name (default 'order_modification_confirmation')
    """
    return {
        "to": distributor_email,
        "template": template,
        "order_id": order_id,
        "attachment": "updated_order_summary.pdf",
        "status": "SENT",
    }


@tool
def route_to_customer_ops(order_id: str, reason: str) -> dict:
    """Route an order modification to the Customer Ops human review queue."""
    return {
        "order_id": order_id,
        "routed_to": "customer-ops-review-queue",
        "reason": reason,
        "priority": "HIGH",
        "sla_hours": 4,
    }


# Lazy-init: AgentCore enforces a 30s cold-start budget for the runtime to
# start serving HTTP traffic. Heavy strands-agents/Bedrock init at module
# import pushes us over that limit, so build the Agent on first invoke().
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            region_name="us-east-1",
        )
        _agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                get_original_order,
                check_engineering_tolerance,
                update_crm_order,
                send_distributor_email,
                route_to_customer_ops,
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
