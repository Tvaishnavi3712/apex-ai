"""
Apex EPROD JIB Bot - AgentCore Agent for JIB statement reconciliation vs AFE
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Create the AgentCore app
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are JIBAgent for EPROD - the wow use case. Reconcile Joint Interest Billing (JIB) statements from JV operators (Phillips 66 Sweeny, Targa Mont Belvieu, EPROD Operated Permian Basin Expansion) against approved AFEs (Authorization for Expenditure). Verify partner-share math against the JOA working interest %. Flag JIB charges that exceed AFE remaining balance - these are critical overruns requiring escalation to Joint Venture Accounting. Document working-interest math for audit."""


@tool
def extract_jib_statement(document_id: str) -> dict:
    """
    Extract structured data from a Joint Interest Billing statement.

    Args:
        document_id: S3 key or document identifier

    Returns:
        Extracted JIB: operator, JV asset, period, gross/net charges, AFE references
    """
    return {
        "document_id": document_id,
        "operator": "Phillips 66 Sweeny Fractionator JV",
        "jv_asset": "Sweeny Frac Train 3",
        "statement_period": "2026-04",
        "afe_references": ["AFE-SWEENY-2025-018", "AFE-SWEENY-2025-022"],
        "gross_charges": 8420000.00,
        "eprod_working_interest_pct": 25.0,
        "eprod_net_charges": 2105000.00,
        "charge_categories": [
            {"afe_id": "AFE-SWEENY-2025-018", "category": "capital_expansion", "gross": 6200000.00},
            {"afe_id": "AFE-SWEENY-2025-022", "category": "turnaround_maintenance", "gross": 2220000.00}
        ],
        "extraction_confidence": 0.93
    }


@tool
def lookup_afe_balance(afe_id: str) -> dict:
    """
    Look up the approved budget and remaining balance for an AFE.

    Args:
        afe_id: Authorization for Expenditure identifier

    Returns:
        AFE budget, spent-to-date, remaining balance
    """
    catalog = {
        "AFE-SWEENY-2025-018": {"budget": 28000000.00, "spent_to_date": 24100000.00},
        "AFE-SWEENY-2025-022": {"budget": 4500000.00, "spent_to_date": 4380000.00},
        "AFE-TARGA-MTB-2025-007": {"budget": 14200000.00, "spent_to_date": 11600000.00},
        "AFE-PERMIAN-EXP-2026-002": {"budget": 88000000.00, "spent_to_date": 32400000.00}
    }
    rec = catalog.get(afe_id, {"budget": 0.0, "spent_to_date": 0.0})
    remaining = rec["budget"] - rec["spent_to_date"]
    return {
        "afe_id": afe_id,
        "approved_budget": rec["budget"],
        "spent_to_date": rec["spent_to_date"],
        "remaining_balance": round(remaining, 2),
        "status": "active" if remaining > 0 else "depleted",
        "approval_authority": "JV Management Committee"
    }


@tool
def compute_partner_share(gross_charge: float, working_interest_pct: float, joa_reference: str) -> dict:
    """
    Compute EPROD's partner share of a JV charge based on the JOA working interest.

    Args:
        gross_charge: Total gross charge from the JIB statement
        working_interest_pct: EPROD's working interest percentage (e.g., 25.0)
        joa_reference: Joint Operating Agreement reference

    Returns:
        Computed partner share with audit-ready math
    """
    net_share = gross_charge * (working_interest_pct / 100.0)
    return {
        "joa_reference": joa_reference,
        "gross_charge": gross_charge,
        "working_interest_pct": working_interest_pct,
        "computed_net_share": round(net_share, 2),
        "math_formula": f"{gross_charge} x ({working_interest_pct}% / 100) = {round(net_share, 2)}",
        "audit_evidence": "stored",
        "currency": "USD"
    }


@tool
def flag_afe_overrun(afe_id: str, jib_charge: float, remaining_balance: float) -> dict:
    """
    Flag a JIB charge that exceeds AFE remaining balance for escalation to JV Accounting.

    Args:
        afe_id: AFE identifier
        jib_charge: Gross JIB charge applied to this AFE
        remaining_balance: AFE remaining approved balance

    Returns:
        Escalation routing with overrun amount and severity
    """
    overrun = jib_charge - remaining_balance
    is_overrun = overrun > 0
    severity = "critical" if overrun > 500000 else "high" if overrun > 50000 else "medium"
    return {
        "afe_id": afe_id,
        "jib_charge": jib_charge,
        "remaining_balance": remaining_balance,
        "overrun_amount": round(overrun, 2),
        "is_overrun": is_overrun,
        "severity": severity if is_overrun else "none",
        "escalated_to": "joint_venture_accounting" if is_overrun else None,
        "sla_hours": 4 if is_overrun else None,
        "action_required": "supplemental_afe_or_dispute" if is_overrun else "auto_approve"
    }


# Create the Strands agent
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[extract_jib_statement, lookup_afe_balance, compute_partner_share, flag_afe_overrun]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
