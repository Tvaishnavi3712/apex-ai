"""
Apex EPROD Tariff Bot - AgentCore Agent for FERC tariff extraction and shipper invoice validation
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

# Create the AgentCore app
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are TariffAgent for EPROD - the wow use case. Extract FERC tariff filings (Enterprise NGL Pipeline, Seaway Crude, Acadian Gas, Panhandle Eastern, Texas Eastern). Track the PPI-FG index for forecasting July-1 index cycle rate changes. Validate every shipper invoice line against the gas-day-effective FERC tariff. Flag billed rates >1.5% above effective FERC rate. Calculate monthly overbilling exposure x affected shipper lines x days."""


@tool
def extract_ferc_tariff(filing_id: str) -> dict:
    """
    Extract structured tariff data from a FERC filing document.

    Args:
        filing_id: FERC filing identifier or S3 key

    Returns:
        Extracted tariff: pipeline, rate schedules, effective dates, PPI-FG index linkage
    """
    return {
        "filing_id": filing_id,
        "pipeline": "Texas Eastern Transmission",
        "ferc_docket": "RP26-142-000",
        "filing_type": "annual_index_adjustment",
        "effective_date": "2026-07-01",
        "ppi_fg_index_value": 138.42,
        "ppi_fg_change_pct": 2.31,
        "rate_schedules": [
            {"schedule": "FT-1", "zone": "M2-30", "rate_per_dth": 0.4218, "reservation_charge": 8.7350},
            {"schedule": "IT-1", "zone": "M2-30", "rate_per_dth": 0.5142, "reservation_charge": 0.0000},
            {"schedule": "FT-1", "zone": "M3", "rate_per_dth": 0.5891, "reservation_charge": 12.4180}
        ],
        "extraction_confidence": 0.97
    }


@tool
def lookup_gas_day_rate(pipeline: str, schedule: str, zone: str, gas_day: str) -> dict:
    """
    Look up the FERC tariff rate that was effective on a specific gas day.

    Args:
        pipeline: Pipeline name (e.g., Texas Eastern Transmission)
        schedule: Rate schedule (e.g., FT-1, IT-1)
        zone: Service zone (e.g., M2-30, M3)
        gas_day: Gas day in YYYY-MM-DD format

    Returns:
        Effective tariff rate for that gas day
    """
    return {
        "pipeline": pipeline,
        "schedule": schedule,
        "zone": zone,
        "gas_day": gas_day,
        "effective_filing": "RP26-142-000",
        "rate_per_dth": 0.4218,
        "reservation_charge": 8.7350,
        "rate_basis": "index_adjusted_july_1_2026"
    }


@tool
def calculate_variance(billed_rate: float, ferc_rate: float, dth_volume: float) -> dict:
    """
    Calculate the variance between a billed rate and the gas-day-effective FERC rate.

    Args:
        billed_rate: Rate billed on the shipper invoice line ($/Dth)
        ferc_rate: Effective FERC tariff rate ($/Dth)
        dth_volume: Volume billed in dekatherms

    Returns:
        Variance pct, overbilled amount, and flag decision
    """
    if ferc_rate == 0:
        return {"variance_pct": None, "exceeds_threshold": True, "reason": "FERC rate unavailable"}
    variance_pct = ((billed_rate - ferc_rate) / ferc_rate) * 100
    overbilled = (billed_rate - ferc_rate) * dth_volume
    exceeds = variance_pct > 1.5
    return {
        "billed_rate": billed_rate,
        "ferc_rate": ferc_rate,
        "variance_pct": round(variance_pct, 3),
        "threshold_pct": 1.5,
        "dth_volume": dth_volume,
        "overbilled_amount": round(overbilled, 2),
        "exceeds_threshold": exceeds,
        "recommended_action": "dispute_invoice_line" if exceeds else "auto_approve"
    }


@tool
def compute_monthly_exposure(pipeline: str, affected_lines: int, avg_overbill_per_line: float, days: int = 30) -> dict:
    """
    Compute monthly overbilling exposure across affected shipper lines.

    Args:
        pipeline: Pipeline name
        affected_lines: Number of shipper invoice lines with variance
        avg_overbill_per_line: Average overbill amount per line per day
        days: Number of days in the exposure window (default 30)

    Returns:
        Total monthly exposure dollar figure
    """
    total_exposure = affected_lines * avg_overbill_per_line * days
    return {
        "pipeline": pipeline,
        "affected_lines": affected_lines,
        "avg_overbill_per_line_per_day": avg_overbill_per_line,
        "days": days,
        "total_monthly_exposure": round(total_exposure, 2),
        "currency": "USD",
        "escalation_required": total_exposure > 100000
    }


# Create the Strands agent
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[extract_ferc_tariff, lookup_gas_day_rate, calculate_variance, compute_monthly_exposure]
)


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
