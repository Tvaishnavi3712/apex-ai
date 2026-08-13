#!/usr/bin/env python3
"""
Deploy the 3 CBB demo agents to Bedrock AgentCore.

  apex_customerops_bot  — CBB Demo 1 · Zero-Touch Order Modification
  apex_qc_bot           — CBB Demo 2 · QC Batch Ingestion & Hold
  apex_logistics_bot    — CBB Demo 3 · Disruption Impact & Reroute

Uses the same S3-code pattern as deploy_agentcore_s3.py: zip agent.py +
requirements.txt, upload to s3://apex-agentcore-code/, create or update the
AgentCore runtime, wait for READY, print a JSON block with the new ARNs ready
to paste into backend/services/agentcore.py::AGENT_ARNS.
"""
import boto3
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from typing import Optional

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"
S3_BUCKET = "apex-agentcore-code"
AGENTCORE_ROLE = f"arn:aws:iam::{ACCOUNT_ID}:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-fa0307c42f"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CBB_AGENTS = [
    {"name": "apex_customerops_bot", "dir": "apex-customerops-bot", "description": "CBB CustomerOps — zero-touch order modification"},
    {"name": "apex_qc_bot",          "dir": "apex-qc-bot",          "description": "CBB QC — batch ingestion, tolerance, SAP holds"},
    {"name": "apex_logistics_bot",   "dir": "apex-logistics-bot",   "description": "CBB Logistics — disruption impact + reroute"},
]


def ensure_s3_bucket(s3):
    try:
        s3.head_bucket(Bucket=S3_BUCKET)
        print(f"  [s3] bucket exists: {S3_BUCKET}")
    except Exception:
        print(f"  [s3] creating bucket: {S3_BUCKET}")
        s3.create_bucket(Bucket=S3_BUCKET)


def _pip_install_linux_arm64(requirements_file: str, target_dir: str) -> None:
    """Install deps for the AgentCore ARM64 Linux runtime into target_dir.

    AgentCore's PYTHON_3_12 runtime does NOT auto-install requirements.txt —
    we must vendor the packages into the ZIP. Uses --platform + --only-binary
    so wheels match the runtime CPU (AL2023 / manylinux2014_aarch64).
    """
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
    print(f"  [pip] vendoring deps to {os.path.basename(target_dir)}/ ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Retry without strict platform (falls back to any-platform wheels +
        # pure-python packages) — still fine for bedrock-agentcore/strands.
        print(f"  [pip] strict install failed ({result.stderr.strip()[:120]}); retrying any-platform")
        cmd_retry = [
            sys.executable, "-m", "pip", "install",
            "--quiet",
            "--target", target_dir,
            "--requirement", requirements_file,
            "--upgrade",
        ]
        r2 = subprocess.run(cmd_retry, capture_output=True, text=True)
        if r2.returncode != 0:
            raise RuntimeError(f"pip install failed: {r2.stderr}")


def _zip_dir_into(zf: zipfile.ZipFile, src_root: str) -> None:
    for root, _dirs, files in os.walk(src_root):
        for fn in files:
            # Skip compile caches + dist-info metadata markers we don't need
            if fn.endswith((".pyc",)):
                continue
            if "__pycache__" in root:
                continue
            full = os.path.join(root, fn)
            rel  = os.path.relpath(full, src_root)
            zf.write(full, rel)


def upload_agent_code(s3, name: str, src_dir: str) -> str:
    """Build a self-contained ZIP (agent.py + vendored site-packages) and push to S3."""
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
            # Agent entrypoint
            agent_py = os.path.join(agent_path, "agent.py")
            if os.path.exists(agent_py):
                zf.write(agent_py, "agent.py")
                print("  [zip] + agent.py")
            # requirements.txt (informational; AgentCore ignores it, but good practice)
            if os.path.exists(req_file):
                zf.write(req_file, "requirements.txt")
                print("  [zip] + requirements.txt")
            # Vendored deps (bedrock_agentcore, strands, boto3, ...)
            vendor_files_before = sum(len(files) for _, _, files in os.walk(vendor))
            _zip_dir_into(zf, vendor)
            print(f"  [zip] + vendor/ ({vendor_files_before} files)")

        buf.seek(0)
        size_mb = len(buf.getvalue()) / 1024 / 1024
        s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=buf.read())
        print(f"  [s3] uploaded s3://{S3_BUCKET}/{s3_key}  ({size_mb:.1f} MB)")

    return s3_key


def find_existing_runtime(agentcore, name: str) -> Optional[str]:
    try:
        resp = agentcore.list_agent_runtimes()
        for r in resp.get("agentRuntimes", []):
            if r["agentRuntimeName"] == name:
                return r["agentRuntimeId"]
    except Exception as e:
        print(f"  [warn] list_agent_runtimes failed: {e}")
    return None


def create_or_update_runtime(agentcore, name: str, s3_key: str, description: str) -> Optional[str]:
    existing = find_existing_runtime(agentcore, name)
    code_config = {
        "codeConfiguration": {
            "code": {"s3": {"bucket": S3_BUCKET, "prefix": s3_key}},
            "runtime": "PYTHON_3_12",
            "entryPoint": ["agent.py"],
        }
    }

    if existing:
        print(f"  [agentcore] updating existing runtime {existing}")
        try:
            agentcore.update_agent_runtime(
                agentRuntimeId=existing,
                agentRuntimeArtifact=code_config,
                roleArn=AGENTCORE_ROLE,
                networkConfiguration={"networkMode": "PUBLIC"},
                protocolConfiguration={"serverProtocol": "HTTP"},
                description=description,
            )
            return existing
        except Exception as e:
            print(f"  [warn] update failed ({e})")
            return existing  # keep the id; we'll still wait on it

    print(f"  [agentcore] creating runtime {name}")
    try:
        resp = agentcore.create_agent_runtime(
            agentRuntimeName=name,
            agentRuntimeArtifact=code_config,
            roleArn=AGENTCORE_ROLE,
            networkConfiguration={"networkMode": "PUBLIC"},
            description=description,
            lifecycleConfiguration={"idleRuntimeSessionTimeout": 900, "maxLifetime": 28800},
            protocolConfiguration={"serverProtocol": "HTTP"},
            tags={"Project": "APEX", "Customer": "CBB"},
        )
        return resp["agentRuntimeId"]
    except Exception as e:
        print(f"  [error] create failed: {e}")
        return None


def wait_for_ready(agentcore, runtime_id: str, timeout: int = 420) -> bool:
    print("  [wait] waiting for READY...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = agentcore.get_agent_runtime(agentRuntimeId=runtime_id)
            s = r.get("status", "UNKNOWN")
            if s == "READY":
                print(f"  [ok] READY")
                return True
            if s in ("FAILED", "DELETING"):
                print(f"  [fail] status={s} reason={r.get('statusReason')}")
                return False
            print(f"  [...] status={s}")
            time.sleep(12)
        except Exception as e:
            print(f"  [warn] get_agent_runtime: {e}")
            time.sleep(8)
    print("  [timeout]")
    return False


def arn_for(name: str, runtime_id: str) -> str:
    return f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT_ID}:runtime/{name}-{runtime_id}" if "-" not in runtime_id \
        else f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT_ID}:runtime/{runtime_id}"


def main():
    print("=" * 72)
    print(f"CBB AGENTCORE DEPLOY · region={REGION} · account={ACCOUNT_ID}")
    print("=" * 72)

    s3 = boto3.client("s3", region_name=REGION)
    agentcore = boto3.client("bedrock-agentcore-control", region_name=REGION)
    ensure_s3_bucket(s3)

    summary = []

    for agent in CBB_AGENTS:
        print(f"\n--- {agent['name']} ---")
        try:
            key = upload_agent_code(s3, agent["name"], agent["dir"])
            runtime_id = create_or_update_runtime(agentcore, agent["name"], key, agent["description"])
            if not runtime_id:
                summary.append({"name": agent["name"], "status": "ERROR_CREATE"})
                continue
            ok = wait_for_ready(agentcore, runtime_id)
            summary.append({
                "name": agent["name"],
                "runtime_id": runtime_id,
                "arn": f"arn:aws:bedrock-agentcore:{REGION}:{ACCOUNT_ID}:runtime/{runtime_id}",
                "status": "READY" if ok else "NOT_READY",
            })
        except Exception as e:
            print(f"  [fatal] {e}")
            summary.append({"name": agent["name"], "status": "ERROR", "error": str(e)})

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for s in summary:
        print(json.dumps(s, indent=2))

    # Print a ready-to-paste block for backend AGENT_ARNS
    print("\n" + "=" * 72)
    print("Paste into backend/services/agentcore.py::AgentCoreService.AGENT_ARNS:")
    print("=" * 72)
    alias_map = {
        "apex_customerops_bot": ["customerops-bot", "customerops"],
        "apex_qc_bot":          ["qc-bot",          "qcbot"],
        "apex_logistics_bot":   ["logistics-bot",   "logisticsbot"],
    }
    for s in summary:
        if s.get("status") in ("READY", "NOT_READY") and "arn" in s:
            for alias in alias_map.get(s["name"], []):
                print(f'        "{alias}": "{s["arn"]}",')

    print("\nConsole: https://{r}.console.aws.amazon.com/bedrock/home?region={r}#/agent-core/runtimes".format(r=REGION))


if __name__ == "__main__":
    main()
