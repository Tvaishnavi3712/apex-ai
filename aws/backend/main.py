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

from api import playbooks, agents, blueprints, actions, documents, work_items, chat, voice
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
