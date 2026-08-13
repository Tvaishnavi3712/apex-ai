#!/usr/bin/env python3
"""
Deploy APEX Aerospace Agents to Bedrock AgentCore using S3 code deployment
No Docker required - uploads code to S3 and creates runtimes
"""
import boto3
import json
import time
import os
import zipfile
import io
from datetime import datetime

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"

# S3 bucket for agent code
S3_BUCKET = "apex-agentcore-code"

# AgentCore role (same as existing agents)
AGENTCORE_ROLE = f"arn:aws:iam::{ACCOUNT_ID}:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-fa0307c42f"

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Aerospace agents to deploy
AEROSPACE_AGENTS = [
    {
        "name": "apex_contract_bot",
        "dir": "apex-contract-bot",
        "description": "Defense contract analysis and pricing for aerospace & defense"
    },
    {
        "name": "apex_cnc_bot",
        "dir": "apex-cnc-bot",
        "description": "CNC G-code analysis and optimization for aerospace manufacturing"
    },
    {
        "name": "apex_workorder_bot",
        "dir": "apex-workorder-bot",
        "description": "Work order management with ERP read/write for aerospace manufacturing"
    }
]


def ensure_s3_bucket(s3_client):
    """Ensure S3 bucket exists."""
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET)
        print(f"  S3 bucket exists: {S3_BUCKET}")
    except:
        print(f"  Creating S3 bucket: {S3_BUCKET}")
        s3_client.create_bucket(Bucket=S3_BUCKET)


def upload_agent_code(s3_client, agent_name: str, agent_dir: str) -> str:
    """Upload agent code to S3 as a ZIP file."""
    agent_path = os.path.join(BASE_DIR, agent_dir)
    s3_key = f"agents/{agent_name}/code.zip"

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add agent.py
        agent_file = os.path.join(agent_path, "agent.py")
        if os.path.exists(agent_file):
            zf.write(agent_file, "agent.py")
            print(f"  Added agent.py to ZIP")

        # Add requirements.txt
        req_file = os.path.join(agent_path, "requirements.txt")
        if os.path.exists(req_file):
            zf.write(req_file, "requirements.txt")
            print(f"  Added requirements.txt to ZIP")

    # Upload ZIP to S3
    zip_buffer.seek(0)
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=zip_buffer.read()
    )
    print(f"  Uploaded {s3_key}")

    return s3_key


def create_or_update_runtime(agentcore, agent_name: str, s3_key: str, description: str):
    """Create or update AgentCore runtime using S3 code ZIP."""

    # Parse bucket and key
    # s3_key is like "agents/apex_contract_bot/code.zip"

    # Check if runtime exists
    existing_runtime_id = None
    try:
        runtimes = agentcore.list_agent_runtimes()
        for runtime in runtimes.get('agentRuntimes', []):
            if runtime['agentRuntimeName'] == agent_name:
                existing_runtime_id = runtime['agentRuntimeId']
                print(f"  Found existing runtime: {existing_runtime_id}")
                break
    except Exception as e:
        print(f"  Error listing runtimes: {e}")

    code_config = {
        'codeConfiguration': {
            'code': {
                's3': {
                    'bucket': S3_BUCKET,
                    'prefix': s3_key  # Points to the ZIP file
                }
            },
            'runtime': 'PYTHON_3_12',
            'entryPoint': ['agent.py']
        }
    }

    if existing_runtime_id:
        # Update existing runtime
        print(f"  Updating runtime...")
        try:
            agentcore.update_agent_runtime(
                agentRuntimeId=existing_runtime_id,
                agentRuntimeArtifact=code_config,
                description=description
            )
            print(f"  Updated runtime: {existing_runtime_id}")
            return existing_runtime_id
        except Exception as e:
            print(f"  Error updating runtime: {e}")
            # If update fails, try to create new
            pass

    # Create new runtime
    print(f"  Creating new runtime: {agent_name}")
    try:
        response = agentcore.create_agent_runtime(
            agentRuntimeName=agent_name,
            agentRuntimeArtifact=code_config,
            roleArn=AGENTCORE_ROLE,
            networkConfiguration={
                'networkMode': 'PUBLIC'
            },
            description=description,
            lifecycleConfiguration={
                'idleRuntimeSessionTimeout': 900,
                'maxLifetime': 28800
            },
            protocolConfiguration={
                'serverProtocol': 'HTTP'
            },
            tags={
                'Project': 'APEX',
                'Industry': 'aerospace_defense',
                'Compliance': 'ITAR'
            }
        )

        runtime_id = response['agentRuntimeId']
        print(f"  Created runtime: {runtime_id}")
        return runtime_id

    except Exception as e:
        print(f"  Error creating runtime: {e}")
        raise


def wait_for_runtime(agentcore, runtime_id: str, timeout: int = 300):
    """Wait for runtime to be ready."""
    print(f"  Waiting for runtime to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = agentcore.get_agent_runtime(agentRuntimeId=runtime_id)
            status = response.get('status', 'UNKNOWN')

            if status == 'READY':
                print(f"  Runtime is READY")
                return True
            elif status in ['FAILED', 'DELETING']:
                print(f"  Runtime status: {status}")
                if 'statusReason' in response:
                    print(f"  Reason: {response['statusReason']}")
                return False

            print(f"  Status: {status}")
            time.sleep(15)

        except Exception as e:
            print(f"  Error checking status: {e}")
            time.sleep(10)

    print(f"  Timeout waiting for runtime")
    return False


def main():
    print("=" * 60)
    print("APEX AEROSPACE AGENTS - AGENTCORE S3 DEPLOYMENT")
    print(f"Region: {REGION}")
    print(f"S3 Bucket: {S3_BUCKET}")
    print("=" * 60)

    s3 = boto3.client('s3', region_name=REGION)
    agentcore = boto3.client('bedrock-agentcore-control', region_name=REGION)

    # Ensure S3 bucket
    ensure_s3_bucket(s3)

    deployed = []

    for agent in AEROSPACE_AGENTS:
        print(f"\n{'=' * 60}")
        print(f"Deploying {agent['name']}")
        print("=" * 60)

        try:
            # Upload code to S3
            s3_prefix = upload_agent_code(s3, agent['name'], agent['dir'])

            # Create or update runtime
            runtime_id = create_or_update_runtime(
                agentcore,
                agent['name'],
                s3_prefix,
                agent['description']
            )

            # Wait for runtime
            if wait_for_runtime(agentcore, runtime_id):
                deployed.append({
                    'name': agent['name'],
                    'runtime_id': runtime_id,
                    'status': 'READY'
                })
            else:
                deployed.append({
                    'name': agent['name'],
                    'runtime_id': runtime_id,
                    'status': 'FAILED'
                })

        except Exception as e:
            print(f"  Error: {e}")
            deployed.append({
                'name': agent['name'],
                'status': 'ERROR',
                'error': str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)

    for d in deployed:
        print(f"\n{d['name']}:")
        print(f"  Status: {d.get('status', 'UNKNOWN')}")
        if 'runtime_id' in d:
            print(f"  Runtime ID: {d['runtime_id']}")
        if 'error' in d:
            print(f"  Error: {d['error']}")

    # List all APEX runtimes
    print("\n" + "=" * 60)
    print("ALL APEX AGENTCORE RUNTIMES")
    print("=" * 60)

    runtimes = agentcore.list_agent_runtimes()
    for r in runtimes.get('agentRuntimes', []):
        if 'apex' in r['agentRuntimeName'].lower():
            print(f"  {r['agentRuntimeName']}: {r['agentRuntimeId']} ({r['status']})")

    print("\n" + "=" * 60)
    print("View in console:")
    print(f"  https://{REGION}.console.aws.amazon.com/bedrock/home?region={REGION}#/agent-core/runtimes")
    print("=" * 60)


if __name__ == "__main__":
    main()
