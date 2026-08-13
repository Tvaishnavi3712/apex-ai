"""
Apex SchemaWatchAgent — Verizon CAS Far Edge Foundry Agent Service runtime.
Firmware certification orchestration for Verizon's CAS far-edge platform.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


app = FoundryAgentApp()

SYSTEM_PROMPT = """You are SchemaWatchAgent for Verizon CAS far-edge. You watch firmware-rev deltas for regressions and Redfish schema drift. You caught the Samsung PM9A3 thermal regression (BMC .45 can't read drive temp -> fans spike to 100%, fixed in .46) and the Dell iDRAC inlet-temp threshold drift (null on 1.30.10.51, populated on 1.30.33.10). You feed golden-config and recommend wave blocks."""

@tool
def detect_regression(query: str = "") -> dict:
    """Detect firmware regressions across revisions."""
    return {'firmware':'ZT BMC 0.45','issue':'PM9A3 thermal read fails','fix':'BMC 0.46','risk':'critical'}


@tool
def diff_redfish_schema(query: str = "") -> dict:
    """Diff the Redfish surface between two firmware revisions."""
    return {'sensor_count_delta':0,'threshold_drift':'inlet-temp null -> -23/58C'}


model = AzureOpenAIModel(model_id="us.anthropic.claude-opus-4-6-v1")

agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[detect_regression, diff_redfish_schema])


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
