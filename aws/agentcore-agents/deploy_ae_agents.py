#!/usr/bin/env python3
"""
Deploy the 3 Agentic Enterprise (vendor-neutral) agents to Bedrock AgentCore.

  apex_ae_orchestrator_agent — UC-1 · Supply Chain Orchestrator
  apex_ae_concierge_agent    — UC-2 · Cruise Concierge (RAG + handoff)
  apex_ae_lease_agent        — UC-3 · Lease Extraction → DuckDB

Mirrors deploy_stp_agents.py:
  1. zip agent.py + vendored deps + bundled synthetic-data files
  2. upload to s3://apex-agentcore-code/
  3. create or update the AgentCore runtime
  4. wait for READY
  5. print runtime ARNs + paste-ready AGENT_ARNS block

Bundled synthetic data:
    Each agent's zip includes synthetic-data/agentic_enterprise/*.json,
    *.md, *.txt copied into a top-level data/ folder. The agent.py loads
    from /app/data/<file> at runtime — NO hardcoded business data.

DRY-RUN BY DEFAULT. Pass --apply to actually deploy.

    python deploy_ae_agents.py            # plan only
    python deploy_ae_agents.py --apply    # actually deploy
    python deploy_ae_agents.py --apply --only orchestrator
"""
from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from typing import Optional

import boto3

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"
S3_BUCKET = "apex-agentcore-code"
AGENTCORE_ROLE = (
    f"arn:aws:iam::{ACCOUNT_ID}:role/"
    "AmazonBedrockAgentCoreSDKRuntime-us-east-1-fa0307c42f"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AWS_ROOT = os.path.dirname(BASE_DIR)
DATA_SOURCE = os.path.join(AWS_ROOT, "synthetic-data", "agentic_enterprise")

AE_AGENTS = [
    {
        "name": "apex_ae_orchestrator_agent",
        "dir": "apex-ae-orchestrator-agent",
        "description": "Agentic Enterprise UC-1 — Supply Chain Orchestrator (vendor-neutral demo)",
        "alias": "orchestrator",
    },
    {
        "name": "apex_ae_concierge_agent",
        "dir": "apex-ae-concierge-agent",
        "description": "Agentic Enterprise UC-2 — Cruise Concierge with RAG + handoff (vendor-neutral demo)",
        "alias": "concierge",
    },
    {
        "name": "apex_ae_lease_agent",
        "dir": "apex-ae-lease-agent",
        "description": "Agentic Enterprise UC-3 — Lease Extraction → DuckDB (vendor-neutral demo)",
        "alias": "lease",
    },
]


# ---------------------------------------------------------------------------
def ensure_s3_bucket(s3) -> None:
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"  [s3] bucket exists: {S3_BUCKET}")
    except Exception:
        print(f"  [s3] creating bucket: {S3_BUCKET}")
        s3.create_bucket(Bucket=S3_BUCKET)


def _pip_install_linux_arm64(requirements_file: str, target_dir: str) -> None:
    """Vendor deps for AgentCore PYTHON_3_12 ARM64 Linux runtime."""
    cmd = [
        sys.executable, "-m", "pip", "install",
        "--quiet",
        "--target", target_dir,
        "--requirement", requirements_file,
        "--platform", "manylinux2014_aarch64",
        "--python-version", "3.12",
        "--implementation", "cp",
        "--only-binary=:all:",
        "--upgrade",
    ]
    print(f"  [pip] vendoring deps to {os.path.basename(target_dir)}/")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [pip] strict install failed; retrying any-platform")
        cmd_retry = [
            sys.executable, "-m", "pip", "install",
            "--quiet", "--target", target_dir,
            "--requirement", requirements_file, "--upgrade",
        ]
        r2 = subprocess.run(cmd_retry, capture_output=True, text=True)
        if r2.returncode != 0:
            raise RuntimeError(f"pip install failed: {r2.stderr}")


def _zip_dir_into(zf: zipfile.ZipFile, src_root: str, prefix: str = "") -> None:
    for root, _dirs, files in os.walk(src_root):
        for fn in files:
            if fn.endswith(".pyc") or "__pycache__" in root:
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, src_root)
            arcname = os.path.join(prefix, rel) if prefix else rel
            zf.write(full, arcname)


def upload_agent_code(s3, agent: dict) -> str:
    """Build a self-contained ZIP and push to S3. Returns the s3 key.

    The ZIP layout for AE agents:
        agent.py
        __init__.py
        requirements.txt
        data/                       ← synthetic-data files bundled here
            inventory_warehouses.json
            suppliers.json
            cruise_faq.md
            booking_record.json
            sample_lease.txt
        vendor/                     ← pip-installed deps for ARM64 Linux
            ...
    """
    name = agent["name"]
    src_dir = agent["dir"]
    agent_path = os.path.join(BASE_DIR, src_dir)
    s3_key = f"agents/{name}/code.zip"

    with tempfile.TemporaryDirectory() as stage:
        vendor = os.path.join(stage, "vendor")
        os.makedirs(vendor, exist_ok=True)

        req_file = os.path.join(agent_path, "requirements.txt")
        if os.path.exists(req_file):
            _pip_install_linux_arm64(req_file, vendor)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            agent_py = os.path.join(agent_path, "agent.py")
            if os.path.exists(agent_py):
                zf.write(agent_py, "agent.py")
                print("  [zip] + agent.py")
            init_py = os.path.join(agent_path, "__init__.py")
            if os.path.exists(init_py):
                zf.write(init_py, "__init__.py")
            if os.path.exists(req_file):
                zf.write(req_file, "requirements.txt")

            # Bundle the agentic_enterprise synthetic data into data/
            if os.path.isdir(DATA_SOURCE):
                data_files = 0
                for fn in sorted(os.listdir(DATA_SOURCE)):
                    if fn.startswith(".") or fn.endswith(".duckdb"):
                        continue
                    full = os.path.join(DATA_SOURCE, fn)
                    if os.path.isfile(full):
                        zf.write(full, f"data/{fn}")
                        data_files += 1
                print(f"  [zip] + data/ ({data_files} synthetic-data files)")
            else:
                print(f"  [warn] synthetic-data dir missing: {DATA_SOURCE}")

            file_count = sum(len(files) for _, _, files in os.walk(vendor))
            _zip_dir_into(zf, vendor)
            print(f"  [zip] + vendor/ ({file_count} files)")

        buf.seek(0)
        size_mb = len(buf.getvalue()) / 1024 / 1024
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=buf.read())
        print(f"  [s3] uploaded s3://{S3_BUCKET}/{s3_key} ({size_mb:.1f} MB)")
    return s3_key


def find_existing_runtime(agentcore, name: str) -> Optional[str]:
    try:
        resp = agentcore.list_agent_runtimes()
        for r in resp.get("agentRuntimes", []):
            if r["agentRuntimeName"] == name:
                return r["agentRuntimeId"]
    except Exception as e:
        print(f"  [warn] list_agent_runtimes: {e}")
    return None


def create_or_update_runtime(agentcore, name: str, s3_key: str, description: str) -> Optional[str]:
    existing = find_existing_runtime(agentcore, name)
    artifact = {
        "codeConfiguration": {
            "code": {"s3": {"bucket": S3_BUCKET, "prefix": s3_key}},
            "runtime": "PYTHON_3_12",
            "entryPoint": ["agent.py"],
        }
    }
    if existing:
        print(f"  [agentcore] updating runtime {existing}")
        try:
            agentcore.update_agent_runtime(
                agentRuntimeId=existing,
                agentRuntimeArtifact=artifact,
                roleArn=AGENTCORE_ROLE,
                networkConfiguration={"networkMode": "PUBLIC"},
                protocolConfiguration={"serverProtocol": "HTTP"},
                description=description,
            )
            return existing
        except Exception as e:
            print(f"  [warn] update failed: {e}")
            return existing
    print(f"  [agentcore] creating runtime {name}")
    try:
        resp = agentcore.create_agent_runtime(
            agentRuntimeName=name,
            agentRuntimeArtifact=artifact,
            roleArn=AGENTCORE_ROLE,
            networkConfiguration={"networkMode": "PUBLIC"},
            description=description,
            lifecycleConfiguration={"idleRuntimeSessionTimeout": 900, "maxLifetime": 28800},
            protocolConfiguration={"serverProtocol": "HTTP"},
            tags={"Project": "APEX", "Customer": "AgenticEnterprise"},
        )
        return resp.get("agentRuntimeId")
    except Exception as e:
        print(f"  [error] create_agent_runtime: {e}")
        return None


def wait_for_ready(agentcore, runtime_id: str, timeout: int = 420) -> bool:
    start = time.time()
    last_status = None
    while time.time() - start < timeout:
        try:
            r = agentcore.get_agent_runtime(agentRuntimeId=runtime_id)
            status = r.get("status", "UNKNOWN")
            if status != last_status:
                print(f"  [agentcore] {runtime_id} status={status}")
                last_status = status
            if status == "READY":
                return True
            if status in ("FAILED", "DELETED"):
                return False
        except Exception as e:
            print(f"  [warn] get_agent_runtime: {e}")
        time.sleep(8)
    print(f"  [warn] timeout waiting for {runtime_id}")
    return False


def runtime_arn(runtime_id: str) -> str:
    return f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT_ID}:runtime/{runtime_id}"


def print_plan(selected: list) -> None:
    print("=" * 72)
    print(f"AGENTIC ENTERPRISE AGENTCORE DEPLOY · DRY-RUN · region={REGION}")
    print("=" * 72)
    print(f"  account           : {ACCOUNT_ID}")
    print(f"  s3 bucket         : {S3_BUCKET}")
    print(f"  agentcore role    : {AGENTCORE_ROLE}")
    print(f"  synthetic data    : {DATA_SOURCE}")
    print(f"  agents to deploy  : {len(selected)}")
    for a in selected:
        print(f"    - {a['name']:32s} ({a['alias']})  ← {a['dir']}/")
    print()
    print("Plan per agent:")
    print("  1. pip install (manylinux2014_aarch64) → vendor/")
    print(f"  2. ZIP agent.py + __init__.py + requirements.txt + data/ + vendor/")
    print(f"  3. PUT s3://{S3_BUCKET}/agents/<name>/code.zip")
    print(f"  4. create_agent_runtime / update_agent_runtime")
    print(f"  5. poll get_agent_runtime until status=READY")
    print()
    print("Re-run with --apply to actually deploy.")


def deploy(selected: list) -> list:
    s3 = boto3.client("s3", region_name=REGION)
    agentcore = boto3.client("bedrock-agentcore-control", region_name=REGION)
    ensure_s3_bucket(s3)

    summary = []
    for agent in selected:
        print(f"\n--- {agent['name']} ---")
        try:
            key = upload_agent_code(s3, agent)
            runtime_id = create_or_update_runtime(
                agentcore, agent["name"], key, agent["description"]
            )
            if not runtime_id:
                summary.append(
                    {"name": agent["name"], "alias": agent["alias"], "status": "ERROR_CREATE"}
                )
                continue
            ok = wait_for_ready(agentcore, runtime_id)
            summary.append(
                {
                    "name": agent["name"],
                    "alias": agent["alias"],
                    "runtime_id": runtime_id,
                    "arn": runtime_arn(runtime_id),
                    "status": "READY" if ok else "NOT_READY",
                }
            )
        except Exception as e:
            print(f"  [fatal] {e}")
            summary.append(
                {"name": agent["name"], "alias": agent["alias"], "status": "ERROR", "error": str(e)}
            )
    return summary


def print_summary(summary: list) -> None:
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for s in summary:
        print(json.dumps(s, indent=2))

    print("\n" + "=" * 72)
    print("Paste into backend/services/agentcore.py::AgentCoreService.AGENT_ARNS:")
    print("=" * 72)
    alias_map = {
        "apex_ae_orchestrator_agent": ["orchestrator-agent", "orchestratoragent", "supply-orchestrator"],
        "apex_ae_concierge_agent":    ["concierge-agent",    "conciergeagent",    "cruise-concierge"],
        "apex_ae_lease_agent":        ["lease-agent",        "leaseagent",        "lease"],
    }
    for s in summary:
        if "arn" in s:
            for alias in alias_map.get(s["name"], []):
                print(f'        "{alias}": "{s["arn"]}",')

    print(
        f"\nConsole: https://{REGION}.console.aws.amazon.com/bedrock/home"
        f"?region={REGION}#/agent-core/runtimes"
    )


# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy 3 Agentic Enterprise AgentCore agents.")
    parser.add_argument("--apply", action="store_true",
                        help="Actually deploy. Without this flag, prints the dry-run plan.")
    parser.add_argument("--only", default="",
                        help="Comma-separated alias filter (e.g. 'orchestrator,lease').")
    args = parser.parse_args()

    only = {x.strip() for x in args.only.split(",") if x.strip()}
    selected = [a for a in AE_AGENTS if not only or a["alias"] in only]
    if not selected:
        print(f"[error] --only filter '{args.only}' matched no agents.")
        sys.exit(2)

    if not args.apply:
        print_plan(selected)
        print("\n(dry-run — no changes applied)")
        return

    print("=" * 72)
    print(f"AGENTIC ENTERPRISE AGENTCORE DEPLOY · APPLY · region={REGION} · account={ACCOUNT_ID}")
    print("=" * 72)
    summary = deploy(selected)
    print_summary(summary)


if __name__ == "__main__":
    main()
