"""
CBTS Apex AI Platform - Backend API
FastAPI application for agent management, playbooks, and document processing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import uuid
from datetime import datetime

from api import playbooks, agents, blueprints, actions, documents, work_items, chat, voice, pipelines, metrics, aws_admin, simulator, signals, llm, review_queue, telecommunications_cycle, eprod_cycle, cwfcu, boler, inventory, jobs, workflow_import
from core.config import settings
from services.dynamodb import DynamoDBService

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


# Default agents to seed
DEFAULT_AGENTS = [
    {
        "name": "CREUnderwriteBot",
        "description": "Commercial Real Estate Underwriting Assistant - Risk analysis, premium calculation, deal recommendations",
        "type": "collaborator",
        "status": "active",
        "environment": "development",
        "playbook_id": "cre-underwriting-playbook",
        "instructions": "You are a Commercial Real Estate Underwriting Assistant. Help users analyze CRE submissions, assess risk scores, calculate premiums, review loss history, and provide underwriting recommendations. Be thorough, professional, and cite specific data from submissions.",
        "model_id": "anthropic.claude-opus-4-5-20251101-v1:0",
    },
    {
        "name": "UnderwriteBot",
        "description": "Insurance Underwriting Assistant - Policy analysis and risk assessment",
        "type": "collaborator",
        "status": "active",
        "environment": "development",
        "playbook_id": "insurance-underwriting-playbook",
        "instructions": "You are an Insurance Underwriting Assistant. Help users analyze insurance submissions, assess risk, and provide underwriting recommendations.",
        "model_id": "anthropic.claude-opus-4-5-20251101-v1:0",
    },
    # ─── Agentic Enterprise (66 Degrees vendor-neutral demo) ───
    # Three agents under one umbrella industry. Each is backed by the
    # in-process simulator in services/agentic_enterprise_demo.py and
    # reads from synthetic-data/agentic_enterprise/*.json. No AgentCore
    # runtime deploy required.
    {
        "name": "OrchestratorAgent",
        "description": "UC-1 · Supply Chain Orchestrator — multi-tool agent that detects shortages, ranks alternative suppliers, drafts POs, and routes to human approval with a full reasoning trace.",
        "type": "orchestrator",
        "status": "active",
        "environment": "development",
        "playbook_id": "supply-chain-orchestrator-playbook",
        "category": "agentic_orchestration",
        "industry": "supply_chain_orchestrator",
        "instructions": "You are an autonomous supply chain orchestrator. When a user reports a shortage, run check_inventory → find_alternative_supplier → draft_purchase_order → submit_for_approval. Surface every tool call in the reasoning trace. Never auto-submit a PO — always route to a human approver.",
        "model_id": "anthropic.claude-opus-4-5-20251101-v1:0",
    },
    {
        "name": "ConciergeAgent",
        "description": "UC-2 · Cruise Concierge — stateful conversational agent with RAG over guest-services FAQ, booking modification, sentiment monitoring, and seamless handoff to a human agent.",
        "type": "collaborator",
        "status": "active",
        "environment": "development",
        "playbook_id": "cruise-concierge-playbook",
        "category": "customer_engagement",
        "industry": "hospitality",
        "instructions": "You are a friendly cruise-line concierge for Coral Star Cruises. Handle booking modifications and answer FAQ questions using RAG. Maintain conversation context across topic switches. Monitor sentiment and trigger human handoff when guests express frustration or explicitly ask.",
        "model_id": "anthropic.claude-opus-4-5-20251101-v1:0",
    },
    {
        "name": "LeaseAgent",
        "description": "UC-3 · Lease Extraction — extracts tenant, expiration, and liability clauses from commercial lease documents, ingests to DuckDB, and answers SQL queries against the structured table.",
        "type": "extractor",
        "status": "active",
        "environment": "development",
        "playbook_id": "lease-extraction-playbook",
        "category": "document_ai",
        "industry": "commercial_real_estate",
        "instructions": "You are a commercial real estate document intelligence agent. When given a lease, extract tenant_name, expiration_date, and liability_clause_text with confidence scores. Push results into the leases DuckDB table. Answer SQL queries against the table.",
        "model_id": "anthropic.claude-opus-4-5-20251101-v1:0",
    },
]


async def seed_default_agents():
    """Seed default agents if they don't exist"""
    db = DynamoDBService(settings.DYNAMODB_AGENTS)

    try:
        # Get existing agents
        existing_agents = await db.scan(limit=100)
        existing_names = {agent.get("name") for agent in existing_agents}

        for agent_data in DEFAULT_AGENTS:
            if agent_data["name"] not in existing_names:
                agent_id = str(uuid.uuid4())
                now = datetime.utcnow()

                full_agent = {
                    **agent_data,
                    "agent_id": agent_id,
                    "created_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                    "invocation_count": 0,
                }

                await db.put_item(full_agent)
                logger.info(f"Seeded default agent: {agent_data['name']}", agent_id=agent_id)
            else:
                logger.info(f"Agent already exists: {agent_data['name']}")

    except Exception as e:
        logger.error(f"Failed to seed default agents: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Apex AI Platform API", version=settings.VERSION)

    # Seed default agents
    await seed_default_agents()

    # Prime the gallery list caches so the first Canvas load is served from
    # cache instead of paying a cold table scan in front of the user.
    for module, label in ((playbooks, "playbooks"), (blueprints, "blueprints")):
        try:
            await module.warm_list_cache()
        except Exception as e:  # noqa: BLE001 — warming must never block startup
            logger.warning(f"List cache warm failed for {label}: {e}")

    yield
    logger.info("Shutting down Apex AI Platform API")


app = FastAPI(
    title="CBTS Apex AI Platform",
    description="Enterprise AI Agent Platform API",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(playbooks.router, prefix="/api/v1/playbooks", tags=["Playbooks"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(blueprints.router, prefix="/api/v1/blueprints", tags=["Blueprints"])
app.include_router(actions.router, prefix="/api/v1/actions", tags=["Actions"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(work_items.router, prefix="/api/v1/work-items", tags=["Work Items"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice Pipeline"])
app.include_router(pipelines.router, prefix="/api/v1/pipelines", tags=["Pipelines"])
app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(simulator.router, prefix="/api/v1/simulator", tags=["Simulator"])
app.include_router(signals.router,   prefix="/api/v1/signals",   tags=["ApexSignal"])
app.include_router(llm.router,       prefix="/api/v1/llm",       tags=["Multi-LLM"])
app.include_router(review_queue.router, prefix="/api/v1/review-queue", tags=["Review Queue"])
app.include_router(aws_admin.router, prefix="/api/v1/aws", tags=["AWS Admin"])
app.include_router(telecommunications_cycle.router, prefix="/api/v1/telecommunications", tags=["Telecom Cycle"])
app.include_router(eprod_cycle.router, prefix="/api/v1/eprod", tags=["EPROD Cycle"])
app.include_router(cwfcu.router, prefix="/api/v1/cwfcu", tags=["CWFCU Credit Union"])
app.include_router(boler.router, prefix="/api/v1/boler", tags=["Boler · Manufacturing Multi-Division"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["Hardware Inventory"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(workflow_import.router, prefix="/api/v1/import", tags=["Workflow Import"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": "apex-ai-platform"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CBTS Apex AI Platform API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
