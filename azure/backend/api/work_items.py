"""
Work Item API endpoints
Manage work items for Worker Agents (Sema4.ai style)
Includes agentic processing workflow
"""

from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional
import uuid
from datetime import datetime

from models.work_item import WorkItem, WorkItemCreate, WorkItemStatus, WorkItemPriority
from services.cosmos import CosmosService
from services.agent_processor import agent_processor
from core.config import settings

router = APIRouter()
db = CosmosService(settings.TABLE_WORK_ITEMS)


@router.get("/", response_model=List[WorkItem])
async def list_work_items(
    agent_id: Optional[str] = Query(None),
    status: Optional[WorkItemStatus] = Query(None),
    priority: Optional[WorkItemPriority] = Query(None),
    limit: int = Query(50, le=200)
):
    """List work items with optional filters"""
    filters = {}
    if agent_id:
        filters["agent_id"] = agent_id
    if status:
        filters["status"] = status.value
    if priority:
        filters["priority"] = priority.value

    items = await db.scan(filters=filters, limit=limit)
    return [WorkItem(**item) for item in items]


@router.get("/queue/{agent_id}")
async def get_agent_queue(agent_id: str):
    """Get pending work items for an agent"""
    items = await db.query(
        key_condition={"agent_id": agent_id},
        filter_expression={"status": WorkItemStatus.PENDING.value},
        index_name="agent-status-index"
    )

    return {
        "agent_id": agent_id,
        "pending_count": len(items),
        "items": [WorkItem(**item) for item in items]
    }


@router.get("/{work_item_id}", response_model=WorkItem)
async def get_work_item(work_item_id: str):
    """Get a specific work item"""
    item = await db.get_item({"work_item_id": work_item_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item {work_item_id} not found"
        )
    return WorkItem(**item)


@router.post("/", response_model=WorkItem, status_code=status.HTTP_201_CREATED)
async def create_work_item(work_item: WorkItemCreate):
    """Create a new work item"""
    work_item_id = str(uuid.uuid4())
    now = datetime.utcnow()

    work_item_data = work_item.model_dump()
    work_item_data.update({
        "work_item_id": work_item_id,
        "created_at": now.isoformat(),
        "status": WorkItemStatus.PENDING.value
    })

    await db.put_item(work_item_data)

    # TODO: Send to SQS queue for agent to pick up
    # await queue.send_message(work_item_data)

    return WorkItem(**work_item_data)


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def create_work_items_batch(work_items: List[WorkItemCreate]):
    """Create multiple work items"""
    results = []
    for item in work_items:
        result = await create_work_item(item)
        results.append(result)

    return {
        "created_count": len(results),
        "work_items": results
    }


@router.put("/{work_item_id}/status")
async def update_work_item_status(
    work_item_id: str,
    status: WorkItemStatus,
    details: Optional[str] = None
):
    """Update work item status"""
    existing = await db.get_item({"work_item_id": work_item_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item {work_item_id} not found"
        )

    now = datetime.utcnow()
    update_data = {
        "status": status.value,
        "updated_at": now.isoformat()
    }

    if status == WorkItemStatus.EXECUTING:
        update_data["started_at"] = now.isoformat()
        update_data["execution_count"] = existing.get("execution_count", 0) + 1
    elif status in [WorkItemStatus.COMPLETED, WorkItemStatus.FAILED, WorkItemStatus.NEEDS_REVIEW]:
        update_data["completed_at"] = now.isoformat()

    if details and status == WorkItemStatus.FAILED:
        update_data["last_error"] = details

    await db.update_item({"work_item_id": work_item_id}, update_data)

    return {"work_item_id": work_item_id, "status": status.value}


@router.put("/{work_item_id}/result")
async def set_work_item_result(work_item_id: str, result: dict):
    """Set work item result"""
    existing = await db.get_item({"work_item_id": work_item_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item {work_item_id} not found"
        )

    await db.update_item(
        {"work_item_id": work_item_id},
        {
            "result": result,
            "status": WorkItemStatus.COMPLETED.value,
            "completed_at": datetime.utcnow().isoformat()
        }
    )

    return {"work_item_id": work_item_id, "status": "completed"}


@router.post("/{work_item_id}/retry")
async def retry_work_item(work_item_id: str):
    """Retry a failed work item"""
    existing = await db.get_item({"work_item_id": work_item_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item {work_item_id} not found"
        )

    if existing.get("status") not in [WorkItemStatus.FAILED.value, WorkItemStatus.NEEDS_REVIEW.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed or needs_review items"
        )

    await db.update_item(
        {"work_item_id": work_item_id},
        {
            "status": WorkItemStatus.PENDING.value,
            "last_error": None
        }
    )

    # TODO: Re-queue to SQS

    return {"work_item_id": work_item_id, "status": "pending"}


@router.delete("/{work_item_id}")
async def delete_work_item(work_item_id: str):
    """Delete a work item"""
    existing = await db.get_item({"work_item_id": work_item_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work item {work_item_id} not found"
        )

    await db.delete_item({"work_item_id": work_item_id})
    return {"status": "deleted"}


# =====================================================
# AGENTIC PROCESSING ENDPOINTS
# =====================================================

@router.post("/{work_item_id}/process")
async def start_agent_processing(work_item_id: str, background_tasks: BackgroundTasks):
    """
    Start agentic processing of a work item.
    The agent will process the document through all stages:
    Pending → Extracting → Validating → Analyzing → Decision → Complete/Requires Approval
    """
    result = await agent_processor.start_processing(work_item_id)
    return result


@router.get("/{work_item_id}/processing-status")
async def get_processing_status(work_item_id: str):
    """
    Get detailed processing status including current stage and log.
    Use this for real-time status updates during processing.
    """
    result = await agent_processor.get_processing_status(work_item_id)
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("message")
        )
    return result


@router.post("/{work_item_id}/approve")
async def approve_work_item(
    work_item_id: str,
    approver: str = Query(..., description="Name of the approver"),
    comments: str = Query("", description="Approval comments")
):
    """
    Approve a work item that requires human approval.
    Only works on items with status 'needs_review'.
    """
    result = await agent_processor.approve_work_item(work_item_id, approver, comments)
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message")
        )
    return result


@router.post("/demo/create-submission")
async def create_demo_submission(
    submission_type: str = Query("random", description="Type: random, chicago, industrial, miami")
):
    """
    Create a demo CRE submission work item for testing the agentic workflow.
    """
    submissions = {
        "chicago": {
            "name": "Lakefront Development LLC - Mixed-Use Portfolio",
            "type": "ACORD 125 Application",
            "submission_id": "CRE-2026-001-MUP"
        },
        "industrial": {
            "name": "Midwest Industrial Partners - Industrial Portfolio",
            "type": "Statement of Values",
            "submission_id": "CRE-2026-002-IND"
        },
        "miami": {
            "name": "Coastal Hospitality Holdings - Hotels & Retail",
            "type": "Insurance Submission Package",
            "submission_id": "CRE-2026-003-HRT"
        }
    }

    if submission_type == "random":
        import random
        submission_type = random.choice(["chicago", "industrial", "miami"])

    submission = submissions.get(submission_type, submissions["chicago"])

    work_item_id = str(uuid.uuid4())
    now = datetime.utcnow()

    work_item_data = {
        "work_item_id": work_item_id,
        "agent_id": "CREUnderwriteBot",
        "playbook_id": "cre-underwriting-playbook",
        "document_name": submission["name"],
        "document_type": submission["type"],
        "status": "pending",
        "processing_stage": "pending",
        "priority": "normal",
        "source": "demo",
        "created_at": now.isoformat(),
        "payload": {
            "submission_id": submission["submission_id"],
            "property_name": submission["name"],
            "document_type": submission["type"],
            "s3_uri": f"s3://apex-documents/submissions/{work_item_id}.pdf"
        },
        "files": [f"submissions/{work_item_id}.pdf"],
        "tags": ["demo", "cre", submission_type]
    }

    await db.put_item(work_item_data)

    return {
        "status": "created",
        "work_item_id": work_item_id,
        "submission": submission,
        "message": "Demo submission created. Use POST /process to start agent processing."
    }
