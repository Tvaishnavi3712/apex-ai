"""
Apex OrchestratorAgent — Verizon CAS Far Edge Foundry Agent Service runtime.
Firmware certification orchestration for Verizon's CAS far-edge platform.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


app = FoundryAgentApp()

SYSTEM_PROMPT = """You are OrchestratorAgent for Verizon CAS far-edge firmware certification. You drive the end-to-end onboarding of new server types (HPE EL140 Gen12 / iLO7, Dell XR8720t / iDRAC10). You cleanly separate two tiers: READ-ONLY Reporting & Correlation (auto), and DIRECT LAB ACTION (executes on live hardware via SSH proxy + Redfish — every action HITL-gated). You run test campaigns through multiple iterations (run1..run5) for statistical confidence. You never execute a direct lab action without human approval."""

@tool
def plan_onboarding(query: str = "") -> dict:
    """Plan the end-to-end onboarding run for a new server type."""
    return {'campaign':'HPE EL140 Gen12','steps':15,'correlate':7,'action':5,'hitl_gates':3,'iterations':10}


@tool
def classify_step_tier(query: str = "") -> dict:
    """Classify a run step as correlate (read-only) or action (direct lab)."""
    return {'tier':'action','requires_hitl':True,'lab_target':'EL140 iLO7 Redfish'}


model = AzureOpenAIModel(model_id="us.anthropic.claude-opus-4-6-v1")

agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[plan_onboarding, classify_step_tier])


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
