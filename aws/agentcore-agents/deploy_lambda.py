#!/usr/bin/env python3
"""
Deploy APEX Aerospace Agents as Lambda Functions
Alternative to AgentCore deployment when SDK is not available.
"""
import boto3
import json
import zipfile
import os
import io
from pathlib import Path

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"

# Agent configurations
AGENTS = {
    "apex-contract-bot": {
        "description": "Contract analysis and pricing for defense programs",
        "memory": 1024,
        "timeout": 300,
        "handler": "lambda_handler.handler"
    },
    "apex-cnc-bot": {
        "description": "CNC G-code analysis and optimization",
        "memory": 512,
        "timeout": 120,
        "handler": "lambda_handler.handler"
    },
    "apex-workorder-bot": {
        "description": "Work order management with ERP read/write",
        "memory": 512,
        "timeout": 120,
        "handler": "lambda_handler.handler"
    }
}


def create_lambda_handler(agent_name: str) -> str:
    """Create Lambda handler wrapper for agent."""
    return f'''
import json
import boto3
from typing import Dict, Any

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def handler(event, context):
    """Lambda handler for {agent_name}"""
    try:
        prompt = event.get('prompt', event.get('body', ''))
        if isinstance(prompt, str) and prompt.startswith('{{'):
            prompt = json.loads(prompt).get('prompt', '')

        # Call Claude via Bedrock
        response = bedrock.invoke_model(
            modelId='us.anthropic.claude-sonnet-4-20250514-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({{
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4096,
                'messages': [
                    {{'role': 'user', 'content': prompt}}
                ],
                'system': get_system_prompt()
            }})
        )

        result = json.loads(response['body'].read())
        return {{
            'statusCode': 200,
            'body': json.dumps({{
                'response': result['content'][0]['text'],
                'agent': '{agent_name}'
            }})
        }}
    except Exception as e:
        return {{
            'statusCode': 500,
            'body': json.dumps({{'error': str(e)}})
        }}

def get_system_prompt():
    """Return system prompt for this agent."""
    return """You are an AI assistant for Essex Industries, an aerospace & defense manufacturer.
You help with contract analysis, pricing, CNC programming, and work order management.
All data is ITAR controlled. Comply with NIST 800-171 and CMMC requirements."""
'''


def create_lambda_package(agent_name: str, agent_dir: Path) -> bytes:
    """Create deployment package for Lambda."""
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add handler
        handler_code = create_lambda_handler(agent_name)
        zf.writestr('lambda_handler.py', handler_code)

        # Add agent.py if exists
        agent_file = agent_dir / 'agent.py'
        if agent_file.exists():
            zf.write(agent_file, 'agent.py')

    buffer.seek(0)
    return buffer.read()


def deploy_agent(agent_name: str, config: dict):
    """Deploy a single agent as Lambda function."""
    lambda_client = boto3.client('lambda', region_name=REGION)
    iam = boto3.client('iam')

    function_name = agent_name.replace('-', '_')
    role_name = f'{agent_name}-role'

    print(f"\n=== Deploying {agent_name} ===")

    # Create IAM role if not exists
    try:
        trust_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Effect': 'Allow',
                'Principal': {'Service': 'lambda.amazonaws.com'},
                'Action': 'sts:AssumeRole'
            }]
        }

        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f'Role for {agent_name}'
        )

        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonBedrockFullAccess',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess',
            'arn:aws:iam::aws:policy/AmazonAthenaFullAccess'
        ]
        for policy in policies:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy)

        print(f"  ✅ Created role: {role_name}")

        # Wait for role to propagate
        import time
        time.sleep(10)

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"  ⏭️  Role exists: {role_name}")

    role_arn = f'arn:aws:iam::{ACCOUNT_ID}:role/{role_name}'

    # Create deployment package
    agent_dir = Path(__file__).parent / agent_name
    package = create_lambda_package(agent_name, agent_dir)
    print(f"  📦 Created deployment package ({len(package)} bytes)")

    # Create or update Lambda function
    try:
        lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.12',
            Role=role_arn,
            Handler=config['handler'],
            Code={'ZipFile': package},
            Description=config['description'],
            Timeout=config['timeout'],
            MemorySize=config['memory'],
            Environment={
                'Variables': {
                    'AGENT_NAME': agent_name,
                    'APEX_REGION': REGION
                }
            },
            Tags={
                'Project': 'APEX',
                'Industry': 'aerospace_defense',
                'Compliance': 'ITAR'
            }
        )
        print(f"  ✅ Created Lambda: {function_name}")

    except lambda_client.exceptions.ResourceConflictException:
        # Update existing function
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=package
        )
        print(f"  🔄 Updated Lambda: {function_name}")

    # Create function URL for easy invocation
    try:
        url_response = lambda_client.create_function_url_config(
            FunctionName=function_name,
            AuthType='AWS_IAM'
        )
        print(f"  🔗 Function URL: {url_response['FunctionUrl']}")
    except lambda_client.exceptions.ResourceConflictException:
        url_response = lambda_client.get_function_url_config(FunctionName=function_name)
        print(f"  🔗 Function URL: {url_response['FunctionUrl']}")

    return function_name


def main():
    print("=" * 60)
    print("APEX AEROSPACE AGENTS - LAMBDA DEPLOYMENT")
    print("=" * 60)

    deployed = []
    for agent_name, config in AGENTS.items():
        try:
            function_name = deploy_agent(agent_name, config)
            deployed.append((agent_name, function_name))
        except Exception as e:
            print(f"  ❌ Failed to deploy {agent_name}: {e}")

    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)
    for agent_name, function_name in deployed:
        print(f"  ✅ {agent_name} → {function_name}")

    print("\nTo invoke an agent:")
    print("  aws lambda invoke --function-name apex_contract_bot \\")
    print("    --payload '{\"prompt\": \"Show F-35 contracts\"}' response.json")


if __name__ == "__main__":
    main()
