#!/usr/bin/env python3
"""
Deploy APEX Aerospace Agents to Bedrock AgentCore
Builds container images and creates AgentCore runtimes
"""
import boto3
import subprocess
import json
import time
import os
from datetime import datetime

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"
ECR_REPO = f"{ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com/apex-agentcore-agents"

# AgentCore role (same as existing agents)
AGENTCORE_ROLE = f"arn:aws:iam::{ACCOUNT_ID}:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-fa0307c42f"

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


def run_cmd(cmd, capture=True):
    """Run shell command and return output."""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0 and capture:
        print(f"  Error: {result.stderr}")
    return result


def ecr_login():
    """Login to ECR."""
    print("\n=== ECR Login ===")
    cmd = f"aws ecr get-login-password --region {REGION} | docker login --username AWS --password-stdin {ACCOUNT_ID}.dkr.ecr.{REGION}.amazonaws.com"
    result = run_cmd(cmd)
    return result.returncode == 0


def build_and_push_image(agent_dir: str, tag: str) -> str:
    """Build Docker image and push to ECR."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    agent_path = os.path.join(base_dir, agent_dir)

    print(f"\n  Building {agent_dir}...")

    # Build image
    build_cmd = f"docker build -t {ECR_REPO}:{tag} {agent_path}"
    result = run_cmd(build_cmd, capture=False)
    if result.returncode != 0:
        raise Exception(f"Failed to build image for {agent_dir}")

    # Push image
    print(f"  Pushing {tag}...")
    push_cmd = f"docker push {ECR_REPO}:{tag}"
    result = run_cmd(push_cmd, capture=False)
    if result.returncode != 0:
        raise Exception(f"Failed to push image {tag}")

    return f"{ECR_REPO}:{tag}"


def create_or_update_agentcore_runtime(client, agent_name: str, container_uri: str, description: str):
    """Create or update AgentCore runtime."""

    # Check if runtime exists
    try:
        runtimes = client.list_agent_runtimes()
        for runtime in runtimes.get('agentRuntimes', []):
            if runtime['agentRuntimeName'] == agent_name:
                print(f"  Runtime {agent_name} exists, updating...")

                # Update existing runtime
                client.update_agent_runtime(
                    agentRuntimeId=runtime['agentRuntimeId'],
                    agentRuntimeArtifact={
                        'containerConfiguration': {
                            'containerUri': container_uri
                        }
                    },
                    description=description
                )

                print(f"  Updated runtime: {runtime['agentRuntimeId']}")
                return runtime['agentRuntimeId']
    except Exception as e:
        print(f"  Error checking runtimes: {e}")

    # Create new runtime
    print(f"  Creating new runtime: {agent_name}")

    response = client.create_agent_runtime(
        agentRuntimeName=agent_name,
        agentRuntimeArtifact={
            'containerConfiguration': {
                'containerUri': container_uri
            }
        },
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


def wait_for_runtime_ready(client, runtime_id: str, timeout: int = 300):
    """Wait for runtime to be ready."""
    print(f"  Waiting for runtime {runtime_id} to be ready...")

    start_time = time.time()
    while time.time() - start_time < timeout:
        response = client.get_agent_runtime(agentRuntimeId=runtime_id)
        status = response.get('status', 'UNKNOWN')

        if status == 'READY':
            print(f"  Runtime is READY")
            return True
        elif status in ['FAILED', 'DELETING']:
            print(f"  Runtime failed: {status}")
            return False

        print(f"  Status: {status}, waiting...")
        time.sleep(10)

    print(f"  Timeout waiting for runtime")
    return False


def create_runtime_endpoint(client, runtime_id: str, agent_name: str):
    """Create endpoint for the runtime."""
    endpoint_name = f"{agent_name}_endpoint"

    # Check if endpoint exists
    try:
        endpoints = client.list_agent_runtime_endpoints(agentRuntimeId=runtime_id)
        for ep in endpoints.get('endpoints', []):
            if ep.get('name') == endpoint_name:
                print(f"  Endpoint already exists: {ep.get('endpointId')}")
                return ep.get('endpointId')
    except Exception as e:
        print(f"  Error checking endpoints: {e}")

    # Create new endpoint
    try:
        response = client.create_agent_runtime_endpoint(
            agentRuntimeId=runtime_id,
            name=endpoint_name,
            description=f"Endpoint for {agent_name}"
        )
        endpoint_id = response.get('agentRuntimeEndpointId')
        print(f"  Created endpoint: {endpoint_id}")
        return endpoint_id
    except Exception as e:
        print(f"  Error creating endpoint: {e}")
        return None


def main():
    print("=" * 60)
    print("APEX AEROSPACE AGENTS - AGENTCORE DEPLOYMENT")
    print(f"Region: {REGION}")
    print(f"ECR Repo: {ECR_REPO}")
    print("=" * 60)

    # ECR login
    if not ecr_login():
        print("Failed to login to ECR")
        return

    # Generate timestamp tag
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    agentcore = boto3.client('bedrock-agentcore-control', region_name=REGION)

    deployed = []

    for agent in AEROSPACE_AGENTS:
        print(f"\n{'=' * 60}")
        print(f"Deploying {agent['name']}")
        print("=" * 60)

        try:
            # Build unique tag for this agent
            tag = f"{agent['name']}-{timestamp}"

            # Build and push Docker image
            container_uri = build_and_push_image(agent['dir'], tag)

            # Create or update AgentCore runtime
            runtime_id = create_or_update_agentcore_runtime(
                agentcore,
                agent['name'],
                container_uri,
                agent['description']
            )

            # Wait for runtime to be ready
            if wait_for_runtime_ready(agentcore, runtime_id):
                # Create endpoint
                endpoint_id = create_runtime_endpoint(agentcore, runtime_id, agent['name'])

                deployed.append({
                    'name': agent['name'],
                    'runtime_id': runtime_id,
                    'endpoint_id': endpoint_id,
                    'container_uri': container_uri,
                    'status': 'READY'
                })
            else:
                deployed.append({
                    'name': agent['name'],
                    'runtime_id': runtime_id,
                    'status': 'FAILED'
                })

        except Exception as e:
            print(f"  Error deploying {agent['name']}: {e}")
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
        if 'endpoint_id' in d:
            print(f"  Endpoint ID: {d['endpoint_id']}")
        if 'error' in d:
            print(f"  Error: {d['error']}")

    print("\n" + "=" * 60)
    print("View in console:")
    print(f"  https://{REGION}.console.aws.amazon.com/bedrock/home?region={REGION}#/agent-core/runtimes")
    print("=" * 60)


if __name__ == "__main__":
    main()
