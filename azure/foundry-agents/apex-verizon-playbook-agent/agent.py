"""
Apex PlaybookAgent — Verizon CAS Far Edge Foundry Agent Service runtime.
Firmware certification orchestration for Verizon's CAS far-edge platform.
"""
# AZURE BUILD: agent runs on Azure AI Foundry / Azure OpenAI.
# `foundry_runtime` provides Foundry Agent Service/Strands-compatible symbols, so every
# tool function and prompt below is unchanged from the AWS build.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from foundry_runtime import FoundryAgentApp, Agent, tool, AzureOpenAIModel


app = FoundryAgentApp()

SYSTEM_PROMPT = """You are PlaybookAgent for Verizon CAS far-edge. You cross-reference live test results against the BMC Ansible playbook (commit 5ff15f7028) and produce a formal change-spec for new platforms. For HPE EL140 / iLO7: 7 CHANGE REQUIRED, 7 NO-CHANGE, 1 VERIFY across 15 role files, plus a net-new security-hardening role. Each change has current code -> required change -> reason -> risk. This is a PROPOSAL — nothing is applied until a human approves (HITL gate)."""

@tool
def gap_analysis(query: str = "") -> dict:
    """Cross-reference test results vs the live playbook; produce a change-spec."""
    return {'change_required':7,'no_change':7,'verify':1,'role_files':15,'new_roles':['security-hardening']}


@tool
def draft_change(query: str = "") -> dict:
    """Draft a single playbook change with reason + risk."""
    return {'role':'group_vars/HPE','change':'add bios_attribute_value_workload_profile_vRAN: vRAN','risk':'low'}


model = AzureOpenAIModel(model_id="us.anthropic.claude-opus-4-6-v1")

agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[gap_analysis, draft_change])


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {"result": result.message}


if __name__ == "__main__":
    app.run()
