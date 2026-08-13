"""
Apex Invoice Bot - Foundry Agent Service Agent for processing vendor invoices
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


# Create the Foundry Agent Service app
app = FoundryAgentApp()

SYSTEM_PROMPT = """You are InvoiceBot, an AI assistant specialized in processing vendor invoices for the Apex AI Platform.

Your capabilities:
1. Extract data from invoice documents
2. Validate invoice information against vendor records
3. Match invoices to purchase orders
4. Route invoices for approval based on amount thresholds
5. Flag exceptions for human review

When processing an invoice:
- First extract all key fields: invoice number, vendor, amount, line items, dates
- Validate the vendor exists in the system
- Check for duplicate invoices
- Apply business rules for approval routing
- If confidence is below 85%, flag for human review

Always be professional and precise. Explain your actions clearly."""


@tool
def lookup_vendor(vendor_name: str) -> dict:
    """
    Look up vendor information in the vendor database.

    Args:
        vendor_name: Name of the vendor to look up

    Returns:
        Vendor details including ID, payment terms, and status
    """
    return {
        "vendor_id": f"VND-{abs(hash(vendor_name)) % 10000:04d}",
        "vendor_name": vendor_name,
        "status": "active",
        "payment_terms": "Net 30",
        "default_gl_code": "6100"
    }


@tool
def check_duplicate_invoice(invoice_number: str, vendor_id: str) -> dict:
    """
    Check if an invoice already exists in the system.

    Args:
        invoice_number: The invoice number to check
        vendor_id: The vendor ID

    Returns:
        Whether the invoice is a duplicate
    """
    return {"is_duplicate": False, "message": "No duplicate found"}


@tool
def route_for_approval(amount: float) -> dict:
    """
    Route an invoice for approval based on business rules.

    Args:
        amount: Invoice amount in dollars

    Returns:
        Routing decision with approver and workflow details
    """
    if amount < 1000:
        return {
            "approval_required": False,
            "auto_approve": True,
            "reason": "Amount below $1,000 auto-approval threshold"
        }
    elif amount < 10000:
        return {
            "approval_required": True,
            "approver_level": "manager",
            "workflow": "standard"
        }
    elif amount < 50000:
        return {
            "approval_required": True,
            "approver_level": "director",
            "workflow": "elevated"
        }
    else:
        return {
            "approval_required": True,
            "approver_level": "vp_finance",
            "workflow": "executive"
        }


@tool
def flag_for_human_review(reason: str) -> dict:
    """
    Flag a work item for human review.

    Args:
        reason: Reason for flagging

    Returns:
        Confirmation of the flag action
    """
    return {
        "flagged": True,
        "status": "pending_review",
        "reason": reason
    }


# Create the Foundry agent
model = AzureOpenAIModel(model_id="us.amazon.nova-pro-v1:0")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[lookup_vendor, check_duplicate_invoice, route_for_approval, flag_for_human_review]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
