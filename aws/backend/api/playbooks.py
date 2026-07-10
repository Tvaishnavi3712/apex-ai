"""
Playbook API endpoints
CRUD operations for AI agent playbooks
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any
import uuid
import os
from datetime import datetime
from pathlib import Path
from decimal import Decimal

from models.playbook import Playbook, PlaybookCreate, PlaybookUpdate
from services.dynamodb import DynamoDBService
from core.config import settings


def convert_for_dynamodb(obj: Any) -> Any:
    """Convert floats to Decimal and dates to strings for DynamoDB compatibility"""
    import datetime as dt
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_for_dynamodb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_for_dynamodb(i) for i in obj]
    return obj


def _map_trigger_type(trigger_type: str) -> str:
    """Map YAML trigger types to enum values"""
    mapping = {
        "s3_event": "s3",
        "s3": "s3",
        "eventbridge": "eventbridge",
        "sqs": "sqs",
        "schedule": "schedule",
        "api": "api",
        "manual": "api",  # Manual triggers use API
    }
    return mapping.get(trigger_type.lower(), "api")

router = APIRouter()
db = DynamoDBService(settings.DYNAMODB_PLAYBOOKS)

# Path to playbooks directory
PLAYBOOKS_DIR = Path(__file__).parent.parent.parent / "playbooks"


@router.get("/", response_model=List[Playbook])
async def list_playbooks(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100)
):
    """List all playbooks with optional filters"""
    filters = {}
    if industry:
        filters["industry"] = industry
    if status:
        filters["status"] = status

    items = await db.scan(filters=filters, limit=limit)
    return [Playbook(**item) for item in items]


@router.get("/{playbook_id}", response_model=Playbook)
async def get_playbook(playbook_id: str):
    """Get a specific playbook by ID or name"""
    # First try by ID
    item = await db.get_item({"playbook_id": playbook_id})

    # If not found by ID, try by name (allows friendly URLs)
    if not item:
        items = await db.scan(filters={"name": playbook_id}, limit=1)
        if items:
            item = items[0]

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playbook {playbook_id} not found"
        )
    return Playbook(**item)


@router.post("/", response_model=Playbook, status_code=status.HTTP_201_CREATED)
async def create_playbook(playbook: PlaybookCreate):
    """Create a new playbook"""
    playbook_id = str(uuid.uuid4())
    now = datetime.utcnow()

    playbook_data = playbook.model_dump()
    playbook_data.update({
        "playbook_id": playbook_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "status": "draft"
    })

    await db.put_item(playbook_data)

    return Playbook(**playbook_data)


@router.put("/{playbook_id}", response_model=Playbook)
async def update_playbook(playbook_id: str, playbook: PlaybookUpdate):
    """Update an existing playbook"""
    existing = await db.get_item({"playbook_id": playbook_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playbook {playbook_id} not found"
        )

    update_data = playbook.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()

    updated = await db.update_item(
        {"playbook_id": playbook_id},
        update_data
    )

    return Playbook(**updated)


@router.delete("/{playbook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playbook(playbook_id: str):
    """Delete a playbook"""
    existing = await db.get_item({"playbook_id": playbook_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playbook {playbook_id} not found"
        )

    await db.delete_item({"playbook_id": playbook_id})


@router.post("/{playbook_id}/deploy")
async def deploy_playbook(playbook_id: str, environment: str = "development"):
    """Deploy a playbook to Bedrock AgentCore"""
    playbook = await get_playbook(playbook_id)

    # TODO: Implement AgentCore deployment
    # 1. Parse playbook to AgentCore configuration
    # 2. Create/update Bedrock Agent
    # 3. Create action groups from playbook actions
    # 4. Set up knowledge bases if needed
    # 5. Create agent alias for the environment

    return {
        "status": "deploying",
        "playbook_id": playbook_id,
        "environment": environment,
        "message": "Deployment initiated"
    }


@router.post("/{playbook_id}/test")
async def test_playbook(playbook_id: str, test_input: dict):
    """Test a playbook with sample input"""
    playbook = await get_playbook(playbook_id)

    # TODO: Implement playbook testing
    # 1. Create a test session
    # 2. Execute playbook with test input
    # 3. Return results

    return {
        "status": "testing",
        "playbook_id": playbook_id,
        "message": "Test execution started"
    }


@router.get("/{playbook_id}/versions")
async def list_playbook_versions(playbook_id: str):
    """List all versions of a playbook"""
    # Query with playbook_id as partition key, version as sort key
    items = await db.query(
        key_condition={"playbook_id": playbook_id},
        index_name="playbook-versions-index"
    )
    return items


@router.get("/by-name/{name}")
async def get_playbook_by_name(name: str):
    """Get a playbook by its name"""
    items = await db.scan(filters={"name": name}, limit=1)
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Playbook with name '{name}' not found"
        )
    return Playbook(**items[0])


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_playbooks(
    industry: Optional[str] = Query(None, description="Seed specific industry only"),
    force: bool = Query(False, description="Force re-seed existing playbooks")
):
    """
    Seed playbooks from YAML files in the playbooks directory.
    Useful for initializing the database with predefined playbooks.
    """
    import yaml

    seeded = []
    errors = []

    # Find all YAML files in the playbooks directory
    if not PLAYBOOKS_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Playbooks directory not found: {PLAYBOOKS_DIR}"
        )

    yaml_files = list(PLAYBOOKS_DIR.rglob("*.yaml")) + list(PLAYBOOKS_DIR.rglob("*.yml"))

    for yaml_file in yaml_files:
        try:
            # Filter by industry if specified
            if industry and industry not in str(yaml_file):
                continue

            with open(yaml_file, 'r') as f:
                playbook_yaml = yaml.safe_load(f)

            if not playbook_yaml:
                continue

            playbook_name = playbook_yaml.get('name', yaml_file.stem)

            # Check if playbook already exists
            existing = await db.scan(filters={"name": playbook_name}, limit=1)
            if existing and not force:
                continue

            # Generate playbook ID or use existing
            playbook_id = existing[0]["playbook_id"] if existing else str(uuid.uuid4())
            now = datetime.utcnow()

            # Transform YAML structure to Playbook model
            actions = []
            for action in playbook_yaml.get('actions', []):
                actions.append({
                    "name": action.get('name', ''),
                    "type": action.get('type', 'lambda'),
                    "description": action.get('description', ''),
                    "config": {
                        "action_id": action.get('action_id', ''),
                        "required": action.get('required', True),
                        "trigger_condition": action.get('trigger_condition', None)
                    }
                })

            # Build playbook data
            playbook_data = {
                "playbook_id": playbook_id,
                "name": playbook_name,
                "version": playbook_yaml.get('version', '1.0'),
                "industry": playbook_yaml.get('industry', playbook_yaml.get('category', 'general')),
                "type": "worker",  # Default to worker for workflow playbooks
                "intent": playbook_yaml.get('intent', ''),
                "recipe": playbook_yaml.get('recipe', ''),
                "actions": actions,
                "context": {
                    "description": playbook_yaml.get('description', ''),
                    "processing_stages": playbook_yaml.get('processing_stages', []),
                    "guardrails": playbook_yaml.get('guardrails', {}),
                    "worker": playbook_yaml.get('worker', {}),
                    "metadata": playbook_yaml.get('metadata', {}),
                },
                "output": [
                    {"name": out.get('name', ''), "description": out.get('type', ''), "type": out.get('type', 'object')}
                    for out in playbook_yaml.get('outputs', [])
                ],
                "triggers": [
                    {
                        "type": _map_trigger_type(t.get('type', 'api')),
                        "config": {k: v for k, v in t.items() if k != 'type'}
                    }
                    for t in playbook_yaml.get('triggers', [])
                ],
                "data_sources": [],
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "status": "active",
                "created_by": "seed"
            }

            # Convert floats to Decimal and dates to strings for DynamoDB
            playbook_data = convert_for_dynamodb(playbook_data)

            await db.put_item(playbook_data)
            seeded.append({
                "playbook_id": playbook_id,
                "name": playbook_name,
                "file": str(yaml_file.relative_to(PLAYBOOKS_DIR))
            })

        except Exception as e:
            errors.append({
                "file": str(yaml_file),
                "error": str(e)
            })

    return {
        "message": f"Seeded {len(seeded)} playbooks",
        "seeded": seeded,
        "errors": errors if errors else None
    }
