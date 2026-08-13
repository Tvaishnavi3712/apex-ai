#!/usr/bin/env python3
"""Deploy the 6 Verizon Far Edge agents to Bedrock AgentCore via S3 (no Docker).
Reuses the proven helpers in deploy_agentcore_s3.py."""
import boto3
import json
from deploy_agentcore_s3 import (
    REGION, S3_BUCKET, ensure_s3_bucket, upload_agent_code,
    create_or_update_runtime, wait_for_runtime,
)

VERIZON_AGENTS = [
    {"name": "apex_verizon_orchestrator", "dir": "apex-verizon-orchestrator-agent",
     "description": "Verizon CAS far-edge — drives end-to-end firmware cert orchestration (multi-iteration + HITL tiers)"},
    {"name": "apex_verizon_certification", "dir": "apex-verizon-certification-agent",
     "description": "Verizon CAS far-edge — firmware report -> cert, DMTF conformance triage"},
    {"name": "apex_verizon_schemawatch", "dir": "apex-verizon-schemawatch-agent",
     "description": "Verizon CAS far-edge — firmware regression + Redfish schema drift detection"},
    {"name": "apex_verizon_upgradeadvisor", "dir": "apex-verizon-upgrade-advisor-agent",
     "description": "Verizon CAS far-edge — firmware/WRCP upgrade path validation + wave risk"},
    {"name": "apex_verizon_mentor", "dir": "apex-verizon-mentor-agent",
     "description": "Verizon CAS far-edge — KB Q&A with verbatim citations"},
    {"name": "apex_verizon_playbook", "dir": "apex-verizon-playbook-agent",
     "description": "Verizon CAS far-edge — gap analysis -> Ansible BMC playbook change-spec"},
]


def main():
    print("=" * 60)
    print("APEX VERIZON FAR EDGE AGENTS — AGENTCORE S3 DEPLOYMENT")
    print(f"Region: {REGION} · Bucket: {S3_BUCKET}")
    print("=" * 60)

    s3 = boto3.client("s3", region_name=REGION)
    agentcore = boto3.client("bedrock-agentcore-control", region_name=REGION)
    ensure_s3_bucket(s3)

    deployed = []
    for agent in VERIZON_AGENTS:
        print(f"\n{'=' * 60}\nDeploying {agent['name']}\n{'=' * 60}")
        try:
            s3_prefix = upload_agent_code(s3, agent["name"], agent["dir"])
            runtime_id = create_or_update_runtime(agentcore, agent["name"], s3_prefix, agent["description"])
            ready = wait_for_runtime(agentcore, runtime_id, timeout=240)
            deployed.append({"name": agent["name"], "runtime_id": runtime_id,
                             "status": "READY" if ready else "PENDING"})
        except Exception as e:
            print(f"  ERROR: {e}")
            deployed.append({"name": agent["name"], "status": "ERROR", "error": str(e)})

    print("\n" + "=" * 60 + "\nDEPLOYMENT SUMMARY\n" + "=" * 60)
    for d in deployed:
        print(f"  {d['name']}: {d.get('status')} {d.get('runtime_id','')}")
    with open("verizon_deploy_result.json", "w") as f:
        json.dump(deployed, f, indent=2)
    print("\nWrote verizon_deploy_result.json")


if __name__ == "__main__":
    main()
