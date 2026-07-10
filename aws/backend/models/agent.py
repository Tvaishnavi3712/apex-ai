"""
Agent data models
Represents Bedrock AgentCore agents
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Type of agent"""
    SUPERVISOR = "supervisor"
    COLLABORATOR = "collaborator"


class AgentStatus(str, Enum):
    """Agent deployment status"""
    DRAFT = "draft"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    FAILED = "failed"
    ARCHIVED = "archived"


class Environment(str, Enum):
    """Deployment environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AgentBase(BaseModel):
    """Base agent model"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    type: AgentType = Field(default=AgentType.COLLABORATOR, description="Agent type")
    playbook_id: str = Field(..., description="Associated playbook ID")
    environment: Environment = Field(default=Environment.DEVELOPMENT)

    # AgentCore configuration
    model_id: str = Field(default="anthropic.claude-opus-4-5-20251101-v1:0", description="Foundation model ID")
    instructions: str = Field(..., description="Agent instructions (from playbook)")

    # Action groups (tools)
    action_group_ids: List[str] = Field(default_factory=list, description="Associated action group IDs")

    # Knowledge bases (RAG)
    knowledge_base_ids: List[str] = Field(default_factory=list, description="Knowledge base IDs")

    # For supervisor agents
    collaborator_ids: List[str] = Field(default_factory=list, description="Collaborator agent IDs")


class AgentCreate(AgentBase):
    """Model for creating a new agent"""
    pass


class AgentUpdate(BaseModel):
    """Model for updating an agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    action_group_ids: Optional[List[str]] = None
    knowledge_base_ids: Optional[List[str]] = None
    collaborator_ids: Optional[List[str]] = None


class Agent(AgentBase):
    """Full agent model with metadata"""
    agent_id: str = Field(..., description="Internal agent ID")
    status: AgentStatus = Field(default=AgentStatus.DRAFT)

    # Bedrock AgentCore references
    bedrock_agent_id: Optional[str] = Field(None, description="Bedrock Agent ID")
    bedrock_agent_arn: Optional[str] = Field(None, description="Bedrock Agent ARN")
    bedrock_agent_version: Optional[str] = Field(None, description="Bedrock Agent version")
    bedrock_alias_id: Optional[str] = Field(None, description="Bedrock Agent alias ID")
    bedrock_alias_arn: Optional[str] = Field(None, description="Bedrock Agent alias ARN")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deployed_at: Optional[datetime] = None
    created_by: str = Field(default="system")

    # Metrics
    invocation_count: int = Field(default=0)
    last_invocation: Optional[datetime] = None

    class Config:
        from_attributes = True
