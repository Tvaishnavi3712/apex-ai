#!/usr/bin/env python3
"""
Deploy APEX Aerospace Agents to Bedrock Agents
Uses the same pattern as existing APEX agents (invoice-bot, claims-bot, etc.)
"""
import boto3
import json
import time

REGION = "us-east-1"
ACCOUNT_ID = "457795063704"

# Use existing APEX role
AGENT_ROLE_ARN = f"arn:aws:iam::{ACCOUNT_ID}:role/apex-bedrock-agent-role"

# Claude Opus 4.6 model - must use inference profile for on-demand
FOUNDATION_MODEL = "us.anthropic.claude-opus-4-6-v1"

AGENTS = {
    "apex-contract-bot": {
        "description": "AI agent for defense contract analysis and pricing for aerospace & defense",
        "instruction": """You are ContractBot, an AI assistant specialized in defense contract analysis for Essex Industries, an aerospace & defense manufacturer.

Your capabilities:
1. Query and analyze defense contracts from PowerFlow database
2. Compare historical pricing across programs (F-35, F-22, UH-60, C-17)
3. Predict pricing for new RFPs based on historical data
4. Identify contract terms, CLINs, and DFARS clauses
5. Generate price justification narratives for proposals

Compliance context:
- All data is ITAR controlled
- Operations must comply with NIST 800-171, CMMC, DFARS
- You are running in AWS GovCloud (FedRAMP High)

When analyzing contracts:
- Always cite specific contract numbers and CLINs
- Provide confidence levels for pricing predictions
- Flag any compliance concerns
- Reference similar past contracts for context

Be precise, cite sources, and maintain data security awareness."""
    },
    "apex-cnc-bot": {
        "description": "AI agent for CNC G-code analysis and optimization for aerospace manufacturing",
        "instruction": """You are CNCBot, an AI assistant specialized in CNC programming assistance for Essex Industries, an aerospace & defense manufacturer.

Your capabilities:
1. Review and analyze G-code programs for syntax and safety issues
2. Validate feeds and speeds against material specifications
3. Suggest optimizations based on best practices
4. Reference similar historical programs
5. Provide machining guidance for aerospace alloys

Material expertise:
- Ti-6Al-4V (Titanium): SFM 100-150, work hardening, high-pressure coolant required
- 7075-T6 (Aluminum): SFM 800-1500, aggressive cuts OK, watch chip welding
- 15-5 PH (Stainless): SFM 150-250, use sharp tools
- Inconel 718: SFM 60-100, very difficult, minimize heat

Machine types supported: Mazak, DMG Mori, Haas, Hermle

Safety priorities:
- Always check Z clearance on rapids (minimum 0.25")
- Verify spindle speed limits
- Confirm coolant activation before cutting
- Flag potential collision risks

You ASSIST the machinist - all recommendations require human approval.
Be precise and cite specific line numbers when identifying issues."""
    },
    "apex-workorder-bot": {
        "description": "AI agent for work order management with ERP read/write for aerospace manufacturing",
        "instruction": """You are WorkOrderBot, an AI assistant specialized in work order management for Essex Industries, an aerospace & defense manufacturer.

Your capabilities:
1. Query work order status from GovCloud ERP (READ)
2. Retrieve associated documents and specifications (READ)
3. Update work order status and completion data (WRITE)
4. Create new work orders (WRITE)
5. Create Non-Conformance Reports (NCRs) (WRITE)
6. Track quality holds

Compliance context:
- All operations are logged for NIST 800-171 compliance
- ITAR-controlled data handling
- AS9100D quality requirements

Work Order Status Workflow:
OPEN → IN_PROGRESS → ON_HOLD (optional) → COMPLETE → CLOSED

Priority Levels:
- AOG (Aircraft on Ground): 24-hour SLA
- CRITICAL: 72-hour SLA
- HIGH: 168-hour SLA (1 week)
- NORMAL: 336-hour SLA (2 weeks)

For WRITE operations:
- Always confirm the action before executing
- Log all changes to audit trail
- Notify relevant personnel

Be precise with work order numbers and status changes."""
    }
}


def create_agent(bedrock_agent, agent_name: str, config: dict) -> dict:
    """Create a Bedrock Agent."""
    print(f"\n=== Creating {agent_name} ===")

    try:
        response = bedrock_agent.create_agent(
            agentName=agent_name,
            description=config["description"],
            instruction=config["instruction"],
            foundationModel=FOUNDATION_MODEL,
            agentResourceRoleArn=AGENT_ROLE_ARN,
            idleSessionTTLInSeconds=1800,
            tags={
                "Project": "APEX",
                "Industry": "aerospace_defense",
                "Compliance": "ITAR"
            }
        )

        agent_id = response["agent"]["agentId"]
        print(f"  ✅ Created agent: {agent_id}")

        # Wait for agent to be ready
        print(f"  ⏳ Waiting for agent to be ready...")
        time.sleep(5)

        # Prepare the agent
        bedrock_agent.prepare_agent(agentId=agent_id)
        print(f"  ✅ Agent prepared")

        # Wait for preparation
        for _ in range(30):
            status = bedrock_agent.get_agent(agentId=agent_id)
            if status["agent"]["agentStatus"] == "PREPARED":
                break
            time.sleep(2)

        return {
            "agentId": agent_id,
            "agentName": agent_name,
            "status": "PREPARED"
        }

    except bedrock_agent.exceptions.ConflictException:
        print(f"  ⚠️  Agent {agent_name} already exists, updating...")

        # Find existing agent
        agents = bedrock_agent.list_agents()
        for agent in agents.get("agentSummaries", []):
            if agent["agentName"] == agent_name:
                agent_id = agent["agentId"]

                # Update agent
                bedrock_agent.update_agent(
                    agentId=agent_id,
                    agentName=agent_name,
                    description=config["description"],
                    instruction=config["instruction"],
                    foundationModel=FOUNDATION_MODEL,
                    agentResourceRoleArn=AGENT_ROLE_ARN,
                    idleSessionTTLInSeconds=1800
                )
                print(f"  ✅ Updated agent: {agent_id}")

                # Re-prepare
                bedrock_agent.prepare_agent(agentId=agent_id)
                print(f"  ✅ Agent re-prepared")

                return {
                    "agentId": agent_id,
                    "agentName": agent_name,
                    "status": "UPDATED"
                }

        raise Exception(f"Could not find or update agent {agent_name}")


def main():
    print("=" * 60)
    print("APEX AEROSPACE AGENTS - BEDROCK AGENTS DEPLOYMENT")
    print(f"Model: Claude Opus 4.6 ({FOUNDATION_MODEL})")
    print(f"Account: {ACCOUNT_ID}")
    print("=" * 60)

    bedrock_agent = boto3.client("bedrock-agent", region_name=REGION)

    deployed = []
    for agent_name, config in AGENTS.items():
        try:
            result = create_agent(bedrock_agent, agent_name, config)
            deployed.append(result)
        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print("\n" + "=" * 60)
    print("DEPLOYMENT SUMMARY")
    print("=" * 60)

    for agent in deployed:
        agent_arn = f"arn:aws:bedrock:{REGION}:{ACCOUNT_ID}:agent/{agent['agentId']}"
        print(f"\n{agent['agentName']}:")
        print(f"  Agent ID: {agent['agentId']}")
        print(f"  ARN: {agent_arn}")
        print(f"  Status: {agent['status']}")

    print("\n" + "=" * 60)
    print("To invoke an agent:")
    print("  aws bedrock-agent-runtime invoke-agent \\")
    print("    --agent-id <AGENT_ID> \\")
    print("    --agent-alias-id TSTALIASID \\")
    print("    --session-id test-session \\")
    print('    --input-text "Show F-35 contracts"')
    print("=" * 60)


if __name__ == "__main__":
    main()
