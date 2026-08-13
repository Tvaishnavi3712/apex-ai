#!/usr/bin/env python3
"""Generate the 6 Verizon Far Edge AgentCore agent dirs (agent.py + requirements.txt).
Strands agents · real firmware-cert tooling · anchored on James Patchett's CAS data.
No Docker — deployed via deploy_verizon_agents.py (S3 zip upload)."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_ID = "us.anthropic.claude-opus-4-6-v1"

REQS = "strands-agents>=0.1.0\nboto3>=1.42.0\nbedrock-agentcore>=1.1.0\nuvicorn>=0.30.0\n"

# (dir, runtime_name, class label, system prompt, tool blocks)
AGENTS = [
    ("apex-verizon-orchestrator-agent", "apex_verizon_orchestrator", "OrchestratorAgent",
     "You are OrchestratorAgent for Verizon CAS far-edge firmware certification. You drive the "
     "end-to-end onboarding of new server types (HPE EL140 Gen12 / iLO7, Dell XR8720t / iDRAC10). "
     "You cleanly separate two tiers: READ-ONLY Reporting & Correlation (auto), and DIRECT LAB ACTION "
     "(executes on live hardware via SSH proxy + Redfish — every action HITL-gated). You run test "
     "campaigns through multiple iterations (run1..run5) for statistical confidence. You never execute "
     "a direct lab action without human approval.",
     [("plan_onboarding", "Plan the end-to-end onboarding run for a new server type.",
       "{'campaign':'HPE EL140 Gen12','steps':15,'correlate':7,'action':5,'hitl_gates':3,'iterations':10}"),
      ("classify_step_tier", "Classify a run step as correlate (read-only) or action (direct lab).",
       "{'tier':'action','requires_hitl':True,'lab_target':'EL140 iLO7 Redfish'}")]),

    ("apex-verizon-certification-agent", "apex_verizon_certification", "CertificationAgent",
     "You are CertificationAgent for Verizon CAS far-edge. You parse firmware test reports, classify "
     "every test, and triage DMTF Redfish conformance failures. The recurring 7-failure signature "
     "(6x WWW-Authenticate header + 1x X.509 IPv6 cert) is known-benign for VCPfe production — auto-certify "
     "with cited rationale, matching James Patchett's 'marked test passed' decisions. You run tests through "
     "5 iterations. You never auto-certify without surfacing the evidence for HITL sign-off.",
     [("triage_conformance", "Triage DMTF Redfish conformance failures as benign or real.",
       "{'pass':392,'fail':7,'all_benign':True,'signature':'WWW-Authenticate + X.509 IPv6'}"),
      ("run_cert_iterations", "Run a cert suite through N iterations and aggregate results.",
       "{'iterations':5,'result':'9/9 pass','deviation_runs':[3]}")]),

    ("apex-verizon-schemawatch-agent", "apex_verizon_schemawatch", "SchemaWatchAgent",
     "You are SchemaWatchAgent for Verizon CAS far-edge. You watch firmware-rev deltas for regressions "
     "and Redfish schema drift. You caught the Samsung PM9A3 thermal regression (BMC .45 can't read drive "
     "temp -> fans spike to 100%, fixed in .46) and the Dell iDRAC inlet-temp threshold drift "
     "(null on 1.30.10.51, populated on 1.30.33.10). You feed golden-config and recommend wave blocks.",
     [("detect_regression", "Detect firmware regressions across revisions.",
       "{'firmware':'ZT BMC 0.45','issue':'PM9A3 thermal read fails','fix':'BMC 0.46','risk':'critical'}"),
      ("diff_redfish_schema", "Diff the Redfish surface between two firmware revisions.",
       "{'sensor_count_delta':0,'threshold_drift':'inlet-temp null -> -23/58C'}")]),

    ("apex-verizon-upgrade-advisor-agent", "apex_verizon_upgradeadvisor", "UpgradeAdvisorAgent",
     "You are UpgradeAdvisorAgent for Verizon CAS far-edge. You validate firmware and Wind River Cloud "
     "Platform (WRCP) upgrade paths and score deployment risk. You block bad firmware from waves "
     "(e.g. BMC .45 to Samsung PM9A3 sites) and route high-risk paths to HITL. Validated path: "
     "WRCP 21.05p6 -> 21.12p10 on ZT Proteus.",
     [("validate_upgrade_path", "Validate a firmware/WRCP upgrade path and score risk.",
       "{'path':'WRCP 21.05p6 -> 21.12p10','verdict':'validated','risk':'low'}"),
      ("score_wave_risk", "Score deployment-wave risk for a firmware rollout.",
       "{'block':'BMC 0.45 to PM9A3 sites','min_safe':'BMC 0.46'}")]),

    ("apex-verizon-mentor-agent", "apex_verizon_mentor", "MentorAgent",
     "You are MentorAgent for Verizon CAS far-edge. You answer KB questions with verbatim citations from "
     "James Patchett's real validation reports — no hallucination, full lineage to the source doc. Topics: "
     "Samsung PM9A3 thermal (BMC .46 fix), Redfish 503-during-boot (RedfishDBReset remediation), DMTF "
     "conformance benign failures, KB-2026-0118 CU-UP RT latency tuning.",
     [("kb_lookup", "Look up a known issue and return a verbatim-cited answer.",
       "{'article':'MEAKV-1792','answer':'BMC .45 cannot read PM9A3 temp; upgrade to .46+','cited':True}")]),

    ("apex-verizon-playbook-agent", "apex_verizon_playbook", "PlaybookAgent",
     "You are PlaybookAgent for Verizon CAS far-edge. You cross-reference live test results against the BMC "
     "Ansible playbook (commit 5ff15f7028) and produce a formal change-spec for new platforms. For HPE EL140 "
     "/ iLO7: 7 CHANGE REQUIRED, 7 NO-CHANGE, 1 VERIFY across 15 role files, plus a net-new security-hardening "
     "role. Each change has current code -> required change -> reason -> risk. This is a PROPOSAL — nothing is "
     "applied until a human approves (HITL gate).",
     [("gap_analysis", "Cross-reference test results vs the live playbook; produce a change-spec.",
       "{'change_required':7,'no_change':7,'verify':1,'role_files':15,'new_roles':['security-hardening']}"),
      ("draft_change", "Draft a single playbook change with reason + risk.",
       "{'role':'group_vars/HPE','change':'add bios_attribute_value_workload_profile_vRAN: vRAN','risk':'low'}")]),
]

AGENT_TMPL = '''"""
Apex {label} — Verizon CAS Far Edge AgentCore runtime.
Firmware certification orchestration for Verizon's CAS far-edge platform.
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """{prompt}"""

{tools}

model = BedrockModel(model_id="{model}", region_name="us-east-1")

agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=[{tool_names}])


@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)
    return {{"result": result.message}}


if __name__ == "__main__":
    app.run()
'''

TOOL_TMPL = '''@tool
def {name}(query: str = "") -> dict:
    """{desc}"""
    return {ret}
'''

for d, rt, label, prompt, tools in AGENTS:
    path = os.path.join(BASE, d)
    os.makedirs(path, exist_ok=True)
    tool_src = "\n\n".join(TOOL_TMPL.format(name=n, desc=desc, ret=ret) for n, desc, ret in tools)
    tool_names = ", ".join(n for n, _, _ in tools)
    agent_py = AGENT_TMPL.format(label=label, prompt=prompt, tools=tool_src,
                                 tool_names=tool_names, model=MODEL_ID)
    with open(os.path.join(path, "agent.py"), "w") as f:
        f.write(agent_py)
    with open(os.path.join(path, "requirements.txt"), "w") as f:
        f.write(REQS)
    print(f"  generated {d} ({rt})")

print(f"\nGenerated {len(AGENTS)} Verizon agent dirs.")
