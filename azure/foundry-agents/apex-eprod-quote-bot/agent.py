"""
Apex EPROD Quote Bot - Foundry Agent Service Agent for engineering quote intake and reconciliation
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


# Create the Foundry Agent Service app
app = FoundryAgentApp()

SYSTEM_PROMPT = """You are QuoteAgent for EPROD, processing engineering quotes from vendors like Fluor, Bechtel, Emerson. Extract scope language, milestones, unit prices, validity dates. Reconcile against historical pricing for similar scope. Flag quotes >10% above 12-month vendor average. Track through PO issuance and invoice validation for full quote-to-pay auditability."""


@tool
def extract_quote_scope(document_id: str) -> dict:
    """
    Extract structured quote data from an engineering quote document.

    Args:
        document_id: S3 key or document identifier

    Returns:
        Structured quote: vendor, scope, milestones, unit prices, validity
    """
    return {
        "document_id": document_id,
        "vendor_name": "Fluor Corporation",
        "quote_number": "FL-Q-2026-1142",
        "quote_date": "2026-05-18",
        "validity_until": "2026-07-18",
        "scope_summary": "EPC services for Mont Belvieu NGL fractionator expansion - Train 4",
        "total_quoted": 18420000.00,
        "currency": "USD",
        "milestones": [
            {"name": "FEED complete", "amount": 2200000.00, "target_date": "2026-09-30"},
            {"name": "Detailed engineering 50%", "amount": 4800000.00, "target_date": "2026-12-15"},
            {"name": "Procurement complete", "amount": 6500000.00, "target_date": "2027-04-30"},
            {"name": "Mechanical completion", "amount": 4920000.00, "target_date": "2027-11-15"}
        ],
        "unit_prices": {
            "senior_engineer_hour": 215.00,
            "design_engineer_hour": 175.00,
            "project_controls_hour": 165.00
        }
    }


@tool
def compare_vs_historical(vendor_name: str, scope_category: str, quoted_amount: float) -> dict:
    """
    Compare a new quote against the 12-month historical average for similar scope.

    Args:
        vendor_name: Vendor providing the quote
        scope_category: Scope category (epc_fractionator, etc.)
        quoted_amount: Total quoted amount in USD

    Returns:
        Comparison vs historical average with variance and flag decision
    """
    historical_avg = quoted_amount / 1.08  # synthetic - assume avg is 8% lower
    variance_pct = ((quoted_amount - historical_avg) / historical_avg) * 100
    exceeds = variance_pct > 10.0
    return {
        "vendor_name": vendor_name,
        "scope_category": scope_category,
        "quoted_amount": quoted_amount,
        "historical_12mo_avg": round(historical_avg, 2),
        "sample_size": 7,
        "variance_pct": round(variance_pct, 2),
        "threshold_pct": 10.0,
        "exceeds_threshold": exceeds
    }


@tool
def link_to_po_chain(quote_number: str, po_number: str = None) -> dict:
    """
    Link a quote to its downstream PO and invoice chain for full quote-to-pay auditability.

    Args:
        quote_number: Vendor quote number
        po_number: Optional PO that was issued from this quote

    Returns:
        Quote-to-pay chain linkage details
    """
    return {
        "quote_number": quote_number,
        "po_number": po_number or "pending_issuance",
        "chain_id": f"Q2P-EPD-{abs(hash(quote_number)) % 100000:05d}",
        "status": "linked" if po_number else "quote_only",
        "downstream_invoices": [],
        "audit_visibility": "full"
    }


@tool
def flag_for_review(quote_number: str, reason: str, severity: str = "medium") -> dict:
    """
    Flag a quote for engineering / procurement review.

    Args:
        quote_number: Quote identifier
        reason: Reason for flagging
        severity: low | medium | high

    Returns:
        Review queue confirmation
    """
    return {
        "flagged": True,
        "quote_number": quote_number,
        "queue": "engineering_quote_review",
        "reason": reason,
        "severity": severity,
        "sla_hours": {"low": 72, "medium": 24, "high": 8}.get(severity, 24)
    }


# Create the Foundry agent
model = AzureOpenAIModel(model_id="us.amazon.nova-pro-v1:0")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[extract_quote_scope, compare_vs_historical, link_to_po_chain, flag_for_review]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
