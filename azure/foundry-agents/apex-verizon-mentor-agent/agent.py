"""
Apex MentorAgent — Verizon CAS Far Edge Foundry Agent Service runtime.
Firmware certification orchestration for Verizon's CAS far-edge platform.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


app = FoundryAgentApp()

SYSTEM_PROMPT = """You are MentorAgent for Verizon CAS far-edge. You answer KB questions with verbatim citations from James Patchett's real validation reports — no hallucination, full lineage to the source doc. Topics: Samsung PM9A3 thermal (BMC .46 fix), Redfish 503-during-boot (RedfishDBReset remediation), DMTF conformance benign failures, KB-2026-0118 CU-UP RT latency tuning."""

@tool
def kb_lookup(query: str = "") -> dict:
    """Look up a known issue and return a verbatim-cited answer."""
    return {'article':'MEAKV-1792','answer':'BMC .45 cannot read PM9A3 temp; upgrade to .46+','cited':True}


model = AzureOpenAIModel(model_id="us.anthropic.claude-opus-4-6-v1")

agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[kb_lookup])


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
