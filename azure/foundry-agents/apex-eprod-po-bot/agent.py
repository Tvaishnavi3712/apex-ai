"""
Apex EPROD PO Bot - Foundry Agent Service Agent for pre-pay PO-to-Contract validation
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


# Create the Foundry Agent Service app
app = FoundryAgentApp()

SYSTEM_PROMPT = """You are POAgent for EPROD, validating purchase orders against Master Service Agreements. Check each PO line item against MSA scope, contracted unit rates, billing terms, and tax codes (TX-E exempt vs TX-I industrial). Flag rate mismatches >5%, tax code errors, and POs outside MSA scope. Reference MSAs by ID (e.g., MSA-HAL-2024-03, MSA-KIEWIT-2024-07). Route exceptions to procurement within minutes, not weeks."""


@tool
def extract_po_lines(po_number: str) -> dict:
    """
    Extract line items and metadata from a purchase order.

    Args:
        po_number: Purchase order number

    Returns:
        Structured PO line items and header data
    """
    return {
        "po_number": po_number,
        "vendor_name": "Kiewit Energy Group",
        "msa_reference": "MSA-KIEWIT-2024-07",
        "po_date": "2026-05-20",
        "ship_to_asset": "EPD-COMP-Acadian-7",
        "total_amount": 412000.00,
        "tax_code": "TX-E",
        "line_items": [
            {"line": 1, "description": "Compressor station civil works", "qty": 1, "unit_price": 285000.00, "uom": "lump_sum"},
            {"line": 2, "description": "Site survey & geotech", "qty": 1, "unit_price": 78000.00, "uom": "lump_sum"},
            {"line": 3, "description": "Project mgmt - 12 weeks", "qty": 12, "unit_price": 4083.33, "uom": "week"}
        ]
    }


@tool
def lookup_msa_scope(msa_id: str) -> dict:
    """
    Look up the scope and allowed work categories under an MSA.

    Args:
        msa_id: Master Service Agreement identifier

    Returns:
        MSA scope details including allowed work types and unit-rate ranges
    """
    return {
        "msa_id": msa_id,
        "vendor": "Kiewit Energy Group",
        "status": "active",
        "allowed_categories": [
            "compressor_station_construction",
            "pipeline_civil_works",
            "geotech_survey",
            "project_management"
        ],
        "rate_card": {
            "compressor_civil_lump_sum": {"min": 250000, "max": 300000},
            "geotech_survey_lump_sum": {"min": 60000, "max": 85000},
            "project_mgmt_per_week": {"min": 3800, "max": 4200}
        },
        "billing_terms": "Net 45"
    }


@tool
def check_tax_code(asset_code: str, tax_code_on_po: str) -> dict:
    """
    Validate the tax code on a PO against the expected code for the destination asset.

    Args:
        asset_code: EPROD asset code (e.g., EPD-COMP-Acadian-7)
        tax_code_on_po: Tax code as shown on the PO

    Returns:
        Whether the tax code is correct for the asset
    """
    expected = "TX-E" if "COMP" in asset_code or "PL" in asset_code else "TX-I"
    return {
        "asset_code": asset_code,
        "expected_tax_code": expected,
        "po_tax_code": tax_code_on_po,
        "matches": expected == tax_code_on_po,
        "explanation": "Compressor and pipeline assets are exempt (TX-E); industrial assets are TX-I"
    }


@tool
def route_exception(po_number: str, exception_type: str, detail: str) -> dict:
    """
    Route a PO exception to the procurement queue.

    Args:
        po_number: PO number with the exception
        exception_type: rate_mismatch | tax_code_error | scope_violation
        detail: Detail explaining the exception

    Returns:
        Routing confirmation with queue assignment and SLA
    """
    sla = {"rate_mismatch": 4, "tax_code_error": 2, "scope_violation": 8}.get(exception_type, 24)
    return {
        "routed": True,
        "po_number": po_number,
        "queue": "procurement_exceptions",
        "exception_type": exception_type,
        "detail": detail,
        "sla_hours": sla,
        "assigned_to": "procurement_team"
    }


# Create the Foundry agent
model = AzureOpenAIModel(model_id="us.amazon.nova-pro-v1:0")

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[extract_po_lines, lookup_msa_scope, check_tax_code, route_exception]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
