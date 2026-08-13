"""
Apex EPROD Vendor Bot - AgentCore Agent for non-PO transaction validation against active MSAs
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Create the AgentCore app
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are VendorAgent for EPROD, validating non-PO transactions against active vendor MSAs at intake. Confirm an active MSA exists, verify the transaction falls within MSA scope, check approval thresholds, and document audit-ready evidence. Flag non-PO transactions with no active MSA on file or scope mismatches. Common vendors: Exterran Corp, Emerson Process, ChemTreat, Archrock Services."""


@tool
def find_active_msa(vendor_name: str) -> dict:
    """
    Find an active MSA on file for a given vendor.

    Args:
        vendor_name: Name of the vendor

    Returns:
        Active MSA reference and metadata, or status indicating no MSA exists
    """
    catalog = {
        "Exterran Corp": {"msa_id": "MSA-EXTERRAN-2023-11", "expires": "2026-11-30"},
        "Emerson Process": {"msa_id": "MSA-EMERSON-2024-02", "expires": "2027-02-15"},
        "ChemTreat": {"msa_id": "MSA-CHEMTREAT-2025-01", "expires": "2028-01-10"},
        "Archrock Services": {"msa_id": "MSA-ARCHROCK-2024-09", "expires": "2026-09-22"}
    }
    record = catalog.get(vendor_name)
    if not record:
        return {"vendor_name": vendor_name, "has_active_msa": False, "msa_id": None, "action": "block_intake"}
    return {
        "vendor_name": vendor_name,
        "has_active_msa": True,
        "msa_id": record["msa_id"],
        "status": "active",
        "expires": record["expires"]
    }


@tool
def validate_scope_match(msa_id: str, transaction_description: str) -> dict:
    """
    Validate that a non-PO transaction falls within the MSA scope.

    Args:
        msa_id: Active MSA identifier
        transaction_description: Description of the proposed transaction

    Returns:
        Scope match assessment with confidence
    """
    return {
        "msa_id": msa_id,
        "transaction_description": transaction_description,
        "scope_match": True,
        "matched_category": "compressor_overhaul_services",
        "confidence": 0.91,
        "evidence_excerpt": "Section 3.2 - Vendor shall perform routine overhaul and repair services on EPROD compressor assets"
    }


@tool
def check_approval_threshold(amount: float, vendor_name: str) -> dict:
    """
    Determine the approval level required based on transaction amount.

    Args:
        amount: Transaction amount in USD
        vendor_name: Vendor name

    Returns:
        Approval routing decision
    """
    if amount < 5000:
        level = "supervisor"
    elif amount < 25000:
        level = "manager"
    elif amount < 100000:
        level = "director"
    else:
        level = "vp_operations"
    return {
        "amount": amount,
        "vendor_name": vendor_name,
        "required_approver_level": level,
        "auto_route": True,
        "non_po_policy_applies": True
    }


@tool
def document_audit_evidence(transaction_id: str, msa_id: str, scope_evidence: str) -> dict:
    """
    Persist audit-ready evidence linking a non-PO transaction to its active MSA.

    Args:
        transaction_id: Non-PO transaction identifier
        msa_id: Linked MSA identifier
        scope_evidence: Excerpt or reference proving scope match

    Returns:
        Confirmation that audit evidence has been recorded
    """
    return {
        "recorded": True,
        "transaction_id": transaction_id,
        "msa_id": msa_id,
        "evidence_stored_at": f"s3://apex-audit-evidence/eprod/non-po/{transaction_id}.json",
        "scope_evidence_excerpt": scope_evidence,
        "audit_trail_version": "v1",
        "retention_years": 7
    }


# Create the Strands agent
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[find_active_msa, validate_scope_match, check_approval_threshold, document_audit_evidence]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
