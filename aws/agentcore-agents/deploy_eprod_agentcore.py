#!/usr/bin/env python3
"""
Deploy 6 EPROD agents to Bedrock AgentCore via S3 code deployment.

Mirrors `deploy_agentcore_s3.py` exactly — same S3 bucket, same IAM role,
same lifecycle config. Only the agent list + tags change.

The 6 agents map 1:1 to EPROD POC use cases:
  apex_eprod_invoice_bot  · UC1 · Invoice Intelligence
  apex_eprod_po_bot       · UC2 · PO-to-Contract Validation
  apex_eprod_vendor_bot   · UC3 · Non-PO MSA Validation
  apex_eprod_quote_bot    · UC4 · Engineering Quote Processing
  apex_eprod_tariff_bot   · UC5 · FERC Tariff Sheet Validation ⭐ wow use case
  apex_eprod_jib_bot      · UC6 · JIB Reconciliation vs AFE ⭐ wow use case

Cost: each ml.m5.large-equivalent runtime is ~$40–60/month for baseline
memory + storage. 6 new runtimes ≈ $300/month on top of the 20 already
provisioned. Tear down between demos with `--destroy`.

Run:
    cd agentcore-agents && python3 deploy_eprod_agentcore.py
    python3 deploy_eprod_agentcore.py --destroy        # tear down all 6
"""
import argparse
import boto3
import io
import os
import sys
import time
import zipfile

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"

# Same S3 bucket + IAM role as the existing 20 runtimes — reuse the
# infrastructure, do not provision new roles.
S3_BUCKET = "apex-agentcore-code"
AGENTCORE_ROLE = f"arn:aws:iam::{ACCOUNT_ID}:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-fa0307c42f"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EPROD_AGENTS = [
    {
        "name":        "apex_eprod_invoice_bot",
        "dir":         "apex-eprod-invoice-bot",
        "description": "EPROD UC1 · Invoice Intelligence — vendor invoice extraction + MSA rate validation",
    },
    {
        "name":        "apex_eprod_po_bot",
        "dir":         "apex-eprod-po-bot",
        "description": "EPROD UC2 · PO-to-Contract Validation — line-item validation against MSA scope + rates",
    },
    {
        "name":        "apex_eprod_vendor_bot",
        "dir":         "apex-eprod-vendor-bot",
        "description": "EPROD UC3 · Non-PO MSA Validation — at-intake validation against active vendor MSAs",
    },
    {
        "name":        "apex_eprod_quote_bot",
        "dir":         "apex-eprod-quote-bot",
        "description": "EPROD UC4 · Engineering Quote Processing — quote intake + historical reconciliation",
    },
    {
        "name":        "apex_eprod_tariff_bot",
        "dir":         "apex-eprod-tariff-bot",
        "description": "EPROD UC5 · FERC Tariff Sheet Validation (wow) — gas-day-effective rate enforcement",
    },
    {
        "name":        "apex_eprod_jib_bot",
        "dir":         "apex-eprod-jib-bot",
        "description": "EPROD UC6 · JIB Reconciliation (wow) — JIB statement match vs AFE + working-interest math",
    },
]


def ensure_s3_bucket(s3_client):
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET)
        print(f"  S3 bucket exists: {S3_BUCKET}")
    except Exception:
        print(f"  Creating S3 bucket: {S3_BUCKET}")
        s3_client.create_bucket(Bucket=S3_BUCKET)


def upload_agent_code(s3_client, agent_name: str, agent_dir: str) -> str:
    """ZIP up agent.py + requirements.txt and upload to S3."""
    agent_path = os.path.join(BASE_DIR, agent_dir)
    s3_key = f"agents/{agent_name}/code.zip"

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ("agent.py", "requirements.txt"):
            fpath = os.path.join(agent_path, fname)
            if os.path.exists(fpath):
                zf.write(fpath, fname)
                print(f"  Added {fname} to ZIP")
            else:
                print(f"  ✗ missing {fname} in {agent_dir}")

    zip_buffer.seek(0)
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=zip_buffer.read())
    print(f"  Uploaded {s3_key}")
    return s3_key


def create_or_update_runtime(agentcore, agent_name: str, s3_key: str, description: str):
    existing_runtime_id = None
    try:
        runtimes = agentcore.list_agent_runtimes()
        for r in runtimes.get("agentRuntimes", []):
            if r["agentRuntimeName"] == agent_name:
                existing_runtime_id = r["agentRuntimeId"]
                print(f"  Found existing runtime: {existing_runtime_id}")
                break
    except Exception as e:
        print(f"  Error listing runtimes: {e}")

    code_config = {
        "codeConfiguration": {
            "code": {"s3": {"bucket": S3_BUCKET, "prefix": s3_key}},
            "runtime": "PYTHON_3_12",
            "entryPoint": ["agent.py"],
        }
    }

    if existing_runtime_id:
        print(f"  Updating runtime …")
        try:
            agentcore.update_agent_runtime(
                agentRuntimeId=existing_runtime_id,
                agentRuntimeArtifact=code_config,
                description=description,
            )
            print(f"  Updated runtime: {existing_runtime_id}")
            return existing_runtime_id
        except Exception as e:
            print(f"  Error updating runtime: {e}")

    print(f"  Creating new runtime: {agent_name}")
    response = agentcore.create_agent_runtime(
        agentRuntimeName=agent_name,
        agentRuntimeArtifact=code_config,
        roleArn=AGENTCORE_ROLE,
        networkConfiguration={"networkMode": "PUBLIC"},
        description=description,
        lifecycleConfiguration={
            "idleRuntimeSessionTimeout": 900,
            "maxLifetime": 28800,
        },
        protocolConfiguration={"serverProtocol": "HTTP"},
        tags={
            "Project":  "APEX",
            "Industry": "oil_gas_midstream",
            "Customer": "EPROD",
        },
    )
    runtime_id = response["agentRuntimeId"]
    print(f"  Created runtime: {runtime_id}")
    return runtime_id


def wait_for_runtime(agentcore, runtime_id: str, timeout: int = 300) -> bool:
    print(f"  Waiting for runtime to be ready …")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = agentcore.get_agent_runtime(agentRuntimeId=runtime_id)
            status = r.get("status", "UNKNOWN")
            if status == "READY":
                print(f"  Runtime is READY")
                return True
            if status in ("FAILED", "DELETING"):
                print(f"  Runtime status: {status} ({r.get('statusReason', '')})")
                return False
            print(f"  Status: {status}")
            time.sleep(15)
        except Exception as e:
            print(f"  Error checking status: {e}")
            time.sleep(10)
    print(f"  Timeout waiting for runtime")
    return False


def destroy_all(agentcore):
    print(f"Destroying all EPROD AgentCore runtimes …")
    deleted = 0
    try:
        runtimes = agentcore.list_agent_runtimes().get("agentRuntimes", [])
    except Exception as e:
        print(f"  Error listing runtimes: {e}")
        return

    eprod_names = {a["name"] for a in EPROD_AGENTS}
    for r in runtimes:
        if r["agentRuntimeName"] in eprod_names:
            try:
                agentcore.delete_agent_runtime(agentRuntimeId=r["agentRuntimeId"])
                print(f"  ✓ deleted {r['agentRuntimeName']} ({r['agentRuntimeId']})")
                deleted += 1
            except Exception as e:
                print(f"  [skip] {r['agentRuntimeName']}: {e}")
    print(f"\nDeleted {deleted} / {len(EPROD_AGENTS)} EPROD runtimes")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=[a["name"] for a in EPROD_AGENTS] + ["all"], default="all")
    parser.add_argument("--destroy", action="store_true")
    args = parser.parse_args()

    s3 = boto3.client("s3", region_name=REGION)
    agentcore = boto3.client("bedrock-agentcore-control", region_name=REGION)

    if args.destroy:
        destroy_all(agentcore)
        return 0

    print("=" * 60)
    print("EPROD AGENTS — AGENTCORE S3 DEPLOYMENT")
    print(f"Region: {REGION}")
    print(f"S3 Bucket: {S3_BUCKET}")
    print("=" * 60)

    ensure_s3_bucket(s3)

    targets = EPROD_AGENTS if args.only == "all" else [a for a in EPROD_AGENTS if a["name"] == args.only]
    deployed = []

    for agent in targets:
        print(f"\n{'=' * 60}\nDeploying {agent['name']}\n{'=' * 60}")
        try:
            s3_prefix = upload_agent_code(s3, agent["name"], agent["dir"])
            runtime_id = create_or_update_runtime(agentcore, agent["name"], s3_prefix, agent["description"])
            ok = wait_for_runtime(agentcore, runtime_id)
            deployed.append({"name": agent["name"], "runtime_id": runtime_id, "status": "READY" if ok else "FAILED"})
        except Exception as e:
            print(f"  Error: {e}")
            deployed.append({"name": agent["name"], "status": "ERROR", "error": str(e)})

    print("\n" + "=" * 60 + "\nDEPLOYMENT SUMMARY\n" + "=" * 60)
    for d in deployed:
        print(f"\n{d['name']}:")
        print(f"  Status: {d.get('status', 'UNKNOWN')}")
        if "runtime_id" in d:
            print(f"  Runtime ID: {d['runtime_id']}")
        if "error" in d:
            print(f"  Error: {d['error']}")

    print("\n" + "=" * 60 + "\nALL APEX EPROD AGENTCORE RUNTIMES\n" + "=" * 60)
    try:
        runtimes = agentcore.list_agent_runtimes().get("agentRuntimes", [])
        for r in runtimes:
            if "eprod" in r["agentRuntimeName"].lower():
                print(f"  {r['agentRuntimeName']}: {r['agentRuntimeId']} ({r['status']})")
    except Exception as e:
        print(f"  Error listing: {e}")

    print(f"\nConsole: https://{REGION}.console.aws.amazon.com/bedrock/home?region={REGION}#/agent-core/runtimes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
