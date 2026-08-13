"""
Apex QC Agent — AgentCore runtime for CBB Demo 2 (QC Batch Ingestion & Hold).

Owns: QC certificate ingestion, Fabric One tolerance validation, SAP inventory
holds, and Teams plant-manager alerts. Powers the CBB QC agent in Agent Hub.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are QC Agent, the AI assistant for Cornerstone Building Brands' Quality Control organization, focused on Ohio Plant 7 and similar vinyl-resin intake flows.

Domain context:
- Suppliers ship vinyl-resin compound with a QC certificate per lot (PDF).
- 50 certificates are bundled into a daily ZIP from the supplier portal.
- Spec: tensile_strength ≥ spec_min (38.0 MPa for Grade A) AND color_delta_e ≤ 2.0
- Inventory holds go into SAP S/4HANA. Hold IDs are emitted per failing lot.
- Alerts flow to Microsoft Teams (#ohio-plant-7-qc) and procurement@cbb.com.
- Reference against Azure Fabric One Lakehouse for historical baselines.

Active hero work item (if referenced):
- Batch 2141 (today 06:00 ET) — 50 certs from Apex Vinyl Solutions (SUP-0081)
  - 48 PASS · 2 HOLDS: LOT-A44 (tensile 36.5 MPa, 3.8% below spec) and LOT-B12 (color ΔE 2.7, above 2.0 threshold)
  - Quarantined value: $32,550 (2,400 kg + 1,800 kg at $7.75/kg)
  - SAP holds placed: ERP-HOLD-7741, ERP-HOLD-7742
  - Plant Manager Sarah Jenkins notified via Teams at 06:15:42

Recent precedent (last 30 days):
- 1,404 lots ingested · 1,372 cleared (97.7%) · 32 held
- Avg tensile variance on held lots: −4.2%
- Avg color ΔE on held lots: 2.6

When answering:
1. Use tools to look up specific batch/lot data — don't guess numbers.
2. If asked about a FAIL, explain which spec failed (tensile vs color) and by how much.
3. If asked "what should I do", propose: (a) approve the hold, (b) request supplier re-test, or (c) release with manager override (requires dual sign-off).
4. Cite hold IDs (ERP-HOLD-*) and dollar value quarantined.
5. Keep it tight — QC managers are busy. 2–4 short paragraphs or a short bullet list.
"""


@tool
def get_batch_summary(batch_id: str) -> dict:
    """Look up a QC batch summary from the Fabric One Lakehouse.

    Args:
        batch_id: Batch identifier, e.g. '2141' or 'CBB-QC-B-2142'
    """
    seeded = {
        "2141": {
            "batch_id": "2141",
            "supplier": "Apex Vinyl Solutions",
            "supplier_id": "SUP-0081",
            "plant": "Ohio Plant 7",
            "total_certs": 50,
            "passed": 48,
            "failed": 2,
            "failed_lots": ["LOT-A44", "LOT-B12"],
            "hold_ids": ["ERP-HOLD-7741", "ERP-HOLD-7742"],
            "quarantined_value_usd": 32550,
            "notified_at": "2026-04-21T06:15:42-04:00",
        },
        "CBB-QC-B-2142": {
            "batch_id": "CBB-QC-B-2142",
            "supplier": "Apex Vinyl Solutions",
            "supplier_id": "SUP-0081",
            "plant": "Ohio Plant 7",
            "total_certs": 50,
            "passed": 48,
            "failed": 2,
            "failed_lots": ["LOT-A44", "LOT-B12"],
            "hold_ids": [],   # awaiting human approval
            "quarantined_value_usd": 32550,
            "awaiting_approval": True,
        },
    }
    return seeded.get(batch_id, {"batch_id": batch_id, "found": False, "message": "Batch not in Fabric One — check batch ID."})


@tool
def get_lot_detail(lot_id: str) -> dict:
    """Look up a specific lot's measurements against spec.

    Args:
        lot_id: Lot identifier, e.g. 'LOT-A44'
    """
    seeded = {
        "LOT-A44": {
            "lot_id": "LOT-A44",
            "material": "Vinyl Resin Compound (PVC Grade A)",
            "tensile_strength_mpa": 36.5,
            "tensile_spec_min_mpa": 38.0,
            "tensile_variance_pct": -3.9,
            "color_delta_e": 1.2,
            "color_threshold": 2.0,
            "quantity_kg": 2400,
            "unit_price_usd": 7.75,
            "lot_value_usd": 18600,
            "pass_fail": "FAIL",
            "fail_reason": "Tensile strength 3.9% below spec minimum",
        },
        "LOT-B12": {
            "lot_id": "LOT-B12",
            "material": "Vinyl Resin Compound (PVC Grade A)",
            "tensile_strength_mpa": 40.1,
            "tensile_spec_min_mpa": 38.0,
            "tensile_variance_pct": 5.5,
            "color_delta_e": 2.7,
            "color_threshold": 2.0,
            "quantity_kg": 1800,
            "unit_price_usd": 7.75,
            "lot_value_usd": 13950,
            "pass_fail": "FAIL",
            "fail_reason": "Color ΔE 2.7 exceeds 2.0 threshold",
        },
    }
    return seeded.get(lot_id, {"lot_id": lot_id, "found": False})


@tool
def check_fabric_tolerance(tensile_mpa: float, tensile_spec_min: float,
                           color_delta_e: float, color_threshold: float = 2.0) -> dict:
    """Validate a lot against Fabric One spec (tensile + color)."""
    tensile_pass = tensile_mpa >= tensile_spec_min
    color_pass   = color_delta_e <= color_threshold
    overall      = tensile_pass and color_pass
    return {
        "pass": overall,
        "tensile_pass": tensile_pass,
        "tensile_variance_pct": round((tensile_mpa - tensile_spec_min) / tensile_spec_min * 100.0, 2),
        "color_pass": color_pass,
        "color_over_threshold_by": round(max(0, color_delta_e - color_threshold), 2),
        "verdict": "auto_clear" if overall else "hold",
    }


@tool
def place_erp_inventory_hold(lot_id: str, reason: str) -> dict:
    """Place a SAP S/4HANA inventory hold on a lot. Returns the new hold ID."""
    # Deterministic-ish IDs for demo replay
    hold_id = f"ERP-HOLD-{7740 + abs(hash(lot_id)) % 50:04d}"
    return {
        "erp": "SAP S/4HANA",
        "lot_id": lot_id,
        "hold_id": hold_id,
        "reason": reason,
        "status": "HELD",
    }


@tool
def notify_plant_manager(channel: str, summary: str) -> dict:
    """Post a Teams alert to the plant QC channel."""
    return {
        "channel": channel,
        "summary": summary,
        "delivered": True,
        "delivered_at": "2026-04-21T06:15:42-04:00",
    }


# Lazy-init: AgentCore enforces a 30s cold-start budget. Build the Agent on
# the first invoke() so module import stays cheap.
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        model = BedrockModel(model_id="us.amazon.nova-pro-v1:0", region_name="us-east-1")
        _agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[
                get_batch_summary,
                get_lot_detail,
                check_fabric_tolerance,
                place_erp_inventory_hold,
                notify_plant_manager,
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
