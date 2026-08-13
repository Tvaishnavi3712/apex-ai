"""
Work Item data models
Represents units of work for Worker Agents (inspired by Sema4.ai)
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class WorkItemStatus(str, Enum):
    """Work item lifecycle status"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"
    CANCELLED = "cancelled"


class WorkItemPriority(str, Enum):
    """Work item priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class WorkItemBase(BaseModel):
    """Base work item model"""
    agent_id: str = Field(..., description="Target agent ID")
    playbook_id: str = Field(..., description="Associated playbook ID")

    # Payload
    payload: Dict[str, Any] = Field(default_factory=dict, description="JSON payload data")
    files: List[str] = Field(default_factory=list, description="S3 keys for attached files")

    # Metadata
    priority: WorkItemPriority = Field(default=WorkItemPriority.NORMAL)
    tags: List[str] = Field(default_factory=list)

    # Source info
    source: str = Field(default="api", description="Source: api, s3, email, schedule")
    source_id: Optional[str] = Field(None, description="External reference ID")


class WorkItemCreate(WorkItemBase):
    """Model for creating a new work item"""
    pass


class WorkItemResult(BaseModel):
    """Result of work item processing"""
    status: WorkItemStatus
    output: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    needs_review_reason: Optional[str] = None


class WorkItem(WorkItemBase):
    """Full work item model with execution history"""
    work_item_id: str = Field(..., description="Work item ID")
    status: WorkItemStatus = Field(default=WorkItemStatus.PENDING)

    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Execution
    execution_count: int = Field(default=0, description="Number of execution attempts")
    last_error: Optional[str] = None

    # Result - flexible dict to support various processing outputs
    result: Optional[Dict[str, Any]] = None

    # Audit
    created_by: str = Field(default="system")
    processed_by: Optional[str] = Field(None, description="Agent that processed this item")

    # Session tracking
    session_id: Optional[str] = Field(None, description="Foundry Agent Service session ID")

    class Config:
        from_attributes = True


class WorkItemStatusHistory(BaseModel):
    """Status change history entry"""
    work_item_id: str
    status: WorkItemStatus
    timestamp: datetime
    details: Optional[str] = None
    changed_by: str = "system"
