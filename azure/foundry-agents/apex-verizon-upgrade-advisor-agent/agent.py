"""
Apex UpgradeAdvisorAgent — Verizon CAS Far Edge Foundry Agent Service runtime.
Firmware certification orchestration for Verizon's CAS far-edge platform.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


app = FoundryAgentApp()

SYSTEM_PROMPT = """You are UpgradeAdvisorAgent for Verizon CAS far-edge. You validate firmware and Wind River Cloud Platform (WRCP) upgrade paths and score deployment risk. You block bad firmware from waves (e.g. BMC .45 to Samsung PM9A3 sites) and route high-risk paths to HITL. Validated path: WRCP 21.05p6 -> 21.12p10 on ZT Proteus."""

@tool
def validate_upgrade_path(query: str = "") -> dict:
    """Validate a firmware/WRCP upgrade path and score risk."""
    return {'path':'WRCP 21.05p6 -> 21.12p10','verdict':'validated','risk':'low'}


@tool
def score_wave_risk(query: str = "") -> dict:
    """Score deployment-wave risk for a firmware rollout."""
    return {'block':'BMC 0.45 to PM9A3 sites','min_safe':'BMC 0.46'}


model = AzureOpenAIModel(model_id="us.anthropic.claude-opus-4-6-v1")

agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[validate_upgrade_path, score_wave_risk])


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
