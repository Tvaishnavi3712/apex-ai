"""
Apex EPROD Invoice Bot - AgentCore Agent for vendor invoice extraction and MSA validation
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Create the AgentCore app
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are InvoiceAgent for EPROD (Enterprise Products Partners), processing vendor invoices for midstream operations. Vendors include Halliburton, Schlumberger, Baker Hughes, Kiewit, Fluor, Bechtel. Extract vendor name, invoice number, amount, line items, asset codes (EPD-PL-*, EPD-FT-*, EPD-COMP-*), MSA references. Validate against MSA rate cards. Flag rate variances >2% from contracted MSA. Route invoices >$50K with no PO reference for HITL review. Never write to ERP without human approval."""


@tool
def extract_invoice_fields(document_id: str) -> dict:
    """
    Extract structured fields from a vendor invoice document.

    Args:
        document_id: The S3 key or document identifier for the invoice

    Returns:
        Extracted invoice fields including vendor, amount, line items, asset codes
    """
    return {
        "document_id": document_id,
        "vendor_name": "Halliburton Energy Services",
        "invoice_number": "HAL-2025-08842",
        "invoice_date": "2026-05-12",
        "total_amount": 187420.50,
        "currency": "USD",
        "msa_reference": "MSA-HAL-2024-03",
        "po_reference": "PO-EPD-44217",
        "asset_codes": ["EPD-PL-MtBelvieu-NGL-12", "EPD-COMP-Acadian-7"],
        "line_items": [
            {"description": "Hydraulic fracturing services - Q1", "quantity": 1, "unit_price": 142000.00},
            {"description": "Wireline logging - 14 stages", "quantity": 14, "unit_price": 3244.32}
        ],
        "extraction_confidence": 0.94
    }


@tool
def lookup_msa_rate_card(msa_id: str, line_description: str) -> dict:
    """
    Look up the contracted unit rate for a line item under an active MSA.

    Args:
        msa_id: Master Service Agreement identifier (e.g., MSA-HAL-2024-03)
        line_description: Description of the line item to price

    Returns:
        Contracted rate from the MSA rate card
    """
    return {
        "msa_id": msa_id,
        "msa_status": "active",
        "effective_date": "2024-03-15",
        "expiration_date": "2027-03-14",
        "matched_line": line_description,
        "contracted_unit_rate": 3180.00,
        "rate_unit": "per_stage",
        "rate_card_version": "v2.1"
    }


@tool
def check_rate_variance(billed_rate: float, contracted_rate: float) -> dict:
    """
    Check the variance between billed rate and the contracted MSA rate.

    Args:
        billed_rate: Rate billed on the invoice line
        contracted_rate: Rate from the MSA rate card

    Returns:
        Variance amount, percentage, and whether it exceeds the 2% threshold
    """
    if contracted_rate == 0:
        return {"variance_pct": None, "exceeds_threshold": True, "reason": "Contracted rate unavailable"}
    variance_pct = ((billed_rate - contracted_rate) / contracted_rate) * 100
    exceeds = abs(variance_pct) > 2.0
    return {
        "billed_rate": billed_rate,
        "contracted_rate": contracted_rate,
        "variance_amount": round(billed_rate - contracted_rate, 2),
        "variance_pct": round(variance_pct, 2),
        "threshold_pct": 2.0,
        "exceeds_threshold": exceeds,
        "recommended_action": "flag_for_hitl" if exceeds else "auto_approve"
    }


@tool
def flag_for_hitl(invoice_number: str, reason: str, amount: float = 0.0) -> dict:
    """
    Flag an invoice for human-in-the-loop review.

    Args:
        invoice_number: Invoice number to flag
        reason: Reason for flagging (rate variance, no PO, etc.)
        amount: Invoice amount in USD

    Returns:
        Confirmation of HITL routing
    """
    severity = "high" if amount > 50000 else "medium"
    return {
        "flagged": True,
        "invoice_number": invoice_number,
        "status": "pending_review",
        "queue": "ap_exceptions",
        "severity": severity,
        "reason": reason,
        "sla_hours": 24
    }


# Create the Strands agent
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[extract_invoice_fields, lookup_msa_rate_card, check_rate_variance, flag_for_hitl]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
