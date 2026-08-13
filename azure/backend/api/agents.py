"""
Agent API endpoints
Manage Azure AI Foundry Agent Service agents
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
import uuid
from datetime import datetime

from models.agent import Agent, AgentCreate, AgentUpdate, AgentStatus, Environment
from services.cosmos import CosmosService
from core.config import settings

router = APIRouter()
db = CosmosService(settings.TABLE_AGENTS)


@router.get("/", response_model=List[Agent])
async def list_agents(
    environment: Optional[Environment] = Query(None),
    status: Optional[AgentStatus] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    """List all agents with optional filters"""
    filters = {}
    if environment:
        filters["environment"] = environment.value
    if status:
        filters["status"] = status.value
    if type:
        filters["type"] = type

    items = await db.scan(filters=filters, limit=limit)
    return [Agent(**item) for item in items]


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    item = await db.get_item({"agent_id": agent_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )
    return Agent(**item)


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(agent: AgentCreate):
    """Create a new agent"""
    agent_id = str(uuid.uuid4())
    now = datetime.utcnow()

    agent_data = agent.model_dump()

    # If playbook_id is provided and instructions are empty, fetch from playbook
    if agent_data.get('playbook_id') and not agent_data.get('instructions'):
        try:
            from services.cosmos import CosmosService
            from core.config import settings
            playbook_db = CosmosService(settings.TABLE_PLAYBOOKS)
            playbook = await playbook_db.get_item({"playbook_id": agent_data['playbook_id']})
            if playbook:
                # Use playbook's intent and recipe as instructions
                intent = playbook.get('intent', '')
                recipe = playbook.get('recipe', '')
                agent_data['instructions'] = f"{intent}\n\n{recipe}" if intent or recipe else ""
                # Also copy description if empty
                if not agent_data.get('description'):
                    agent_data['description'] = playbook.get('context', {}).get('description', '') or f"Agent for {playbook.get('name', 'playbook')}"
        except Exception as e:
            # Log but don't fail - instructions will remain empty
            print(f"Warning: Could not fetch playbook for instructions: {e}")

    # Set status to active if created from a playbook, draft otherwise
    initial_status = AgentStatus.ACTIVE.value if agent_data.get('playbook_id') else AgentStatus.DRAFT.value

    agent_data.update({
        "agent_id": agent_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "status": initial_status
    })

    await db.put_item(agent_data)

    return Agent(**agent_data)


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent: AgentUpdate):
    """Update an existing agent"""
    existing = await db.get_item({"agent_id": agent_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    update_data = agent.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()

    updated = await db.update_item(
        {"agent_id": agent_id},
        update_data
    )

    return Agent(**updated)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    """Delete an agent"""
    existing = await db.get_item({"agent_id": agent_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent {agent_id} not found"
        )

    # TODO: Also delete from Azure OpenAI if deployed
    await db.delete_item({"agent_id": agent_id})


@router.post("/{agent_id}/deploy")
async def deploy_agent(agent_id: str, environment: Environment = Environment.DEVELOPMENT):
    """Deploy an agent to Azure AI Foundry Agent Service"""
    agent = await get_agent(agent_id)

    # Update status to deploying
    await db.update_item(
        {"agent_id": agent_id},
        {"status": AgentStatus.DEPLOYING.value, "updated_at": datetime.utcnow().isoformat()}
    )

    # TODO: Implement Azure OpenAI deployment
    # 1. Create Azure OpenAI Agent with instructions
    # 2. Add action groups
    # 3. Add knowledge bases
    # 4. Create agent alias
    # 5. For supervisors, associate collaborators

    return {
        "status": "deploying",
        "agent_id": agent_id,
        "environment": environment.value,
        "message": "Deployment initiated"
    }


@router.post("/{agent_id}/invoke")
async def invoke_agent(agent_id: str, input: dict):
    """Invoke an agent with input"""
    agent = await get_agent(agent_id)

    if agent.status != AgentStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent is not active. Current status: {agent.status}"
        )

    # TODO: Implement Foundry Agent Service invocation
    # 1. Get agent alias
    # 2. Invoke agent with input
    # 3. Return response

    return {
        "agent_id": agent_id,
        "status": "processing",
        "message": "Agent invocation started"
    }


@router.get("/{agent_id}/metrics")
async def get_agent_metrics(agent_id: str):
    """Get agent performance metrics"""
    agent = await get_agent(agent_id)

    # TODO: Query Azure Monitor metrics for this agent

    return {
        "agent_id": agent_id,
        "invocation_count": agent.invocation_count,
        "last_invocation": agent.last_invocation,
        "metrics": {
            "avg_latency_ms": 0,
            "success_rate": 0,
            "error_rate": 0
        }
    }
