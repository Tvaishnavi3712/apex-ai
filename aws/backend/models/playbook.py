"""
Playbook data models
Defines the structure for AI agent playbooks (inspired by Sema4.ai)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlaybookType(str, Enum):
    """Type of playbook/agent"""
    SUPERVISOR = "supervisor"
    COLLABORATOR = "collaborator"
    WORKER = "worker"


class DataSourceType(str, Enum):
    """Type of data source"""
    S3 = "s3"
    DYNAMODB = "dynamodb"
    API = "api"
    DATABASE = "database"


class TriggerType(str, Enum):
    """Type of trigger for worker agents"""
    S3 = "s3"
    S3_EVENT = "s3_event"  # Alias for S3
    EVENTBRIDGE = "eventbridge"
    SQS = "sqs"
    SCHEDULE = "schedule"
    API = "api"
    MANUAL = "manual"  # Alias for API


class DataSource(BaseModel):
    """Data source configuration"""
    name: str = Field(..., description="Name of the data source")
    type: DataSourceType = Field(..., description="Type of data source")
    config: Dict[str, Any] = Field(default_factory=dict, description="Source-specific configuration")
    # S3: bucket, prefix
    # DynamoDB: table, key_schema
    # API: endpoint, method, headers


class ActionReference(BaseModel):
    """Reference to an action in the playbook"""
    name: str = Field(..., description="Action name")
    type: str = Field(default="lambda", description="Action type: lambda, gateway_prebuilt")
    description: str = Field(..., description="What this action does")
    config: Dict[str, Any] = Field(default_factory=dict, description="Action configuration")


class Trigger(BaseModel):
    """Trigger configuration for worker agents"""
    type: str = Field(..., description="Trigger type: s3, s3_event, eventbridge, sqs, schedule, api, manual")
    config: Dict[str, Any] = Field(default_factory=dict, description="Trigger-specific configuration")
    # S3: bucket, prefix, events
    # Schedule: cron, rate
    # SQS: queue_url


class PlaybookOutput(BaseModel):
    """Expected output from playbook execution"""
    name: str = Field(..., description="Output field name")
    description: str = Field(..., description="Description of the output")
    type: str = Field(default="string", description="Data type")


class PlaybookBase(BaseModel):
    """Base playbook model"""
    name: str = Field(..., description="Playbook name", min_length=1, max_length=100)
    version: str = Field(default="1.0", description="Playbook version")
    industry: str = Field(default="general", description="Target industry")
    type: PlaybookType = Field(default=PlaybookType.COLLABORATOR, description="Agent type")
    blueprint: Optional[str] = Field(None, description="Associated BDA blueprint ID")

    # Core playbook components (Sema4.ai inspired)
    intent: str = Field(..., description="What the agent should accomplish")
    output: List[PlaybookOutput] = Field(default_factory=list, description="Expected outputs")
    context: Dict[str, Any] = Field(default_factory=dict, description="Business rules and constraints")

    # Data and actions
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")
    actions: List[ActionReference] = Field(default_factory=list, description="Available actions")

    # Recipe (the step-by-step instructions)
    recipe: str = Field(..., description="Natural language instructions for the agent")

    # Triggers (for worker agents)
    triggers: List[Trigger] = Field(default_factory=list, description="Triggers for worker agents")


class PlaybookCreate(PlaybookBase):
    """Model for creating a new playbook"""
    pass


class PlaybookUpdate(BaseModel):
    """Model for updating a playbook"""
    name: Optional[str] = None
    version: Optional[str] = None
    industry: Optional[str] = None
    type: Optional[PlaybookType] = None
    blueprint: Optional[str] = None
    intent: Optional[str] = None
    output: Optional[List[PlaybookOutput]] = None
    context: Optional[Dict[str, Any]] = None
    data_sources: Optional[List[DataSource]] = None
    actions: Optional[List[ActionReference]] = None
    recipe: Optional[str] = None
    triggers: Optional[List[Trigger]] = None


class Playbook(PlaybookBase):
    """Full playbook model with metadata"""
    playbook_id: str = Field(..., description="Unique playbook ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system", description="Creator")
    status: str = Field(default="draft", description="Playbook status: draft, active, archived")

    # AgentCore mapping
    agent_id: Optional[str] = Field(None, description="Associated Bedrock Agent ID")
    agent_arn: Optional[str] = Field(None, description="Associated Bedrock Agent ARN")

    class Config:
        from_attributes = True
