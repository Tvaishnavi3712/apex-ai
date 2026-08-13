"""
Action data models
Represents actions/tools for Foundry Agent Service Gateway
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Type of action"""
    LAMBDA = "lambda"
    GATEWAY_PREBUILT = "gateway_prebuilt"
    OPENAPI = "openapi"
    MCP = "mcp"


class ActionCategory(str, Enum):
    """Action category"""
    DOCUMENT = "document"
    DATA_LOOKUP = "data_lookup"
    BUSINESS_LOGIC = "business_logic"
    NOTIFICATION = "notification"
    INTEGRATION = "integration"
    HUMAN_IN_LOOP = "human_in_loop"


class ActionSchema(BaseModel):
    """Action input/output schema"""
    type: str = "object"
    description: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)


class ActionBase(BaseModel):
    """Base action model"""
    name: str = Field(..., description="Action name (unique identifier)")
    display_name: Optional[str] = Field(None, description="Human-readable name")
    description: str = Field(default="", description="What this action does")
    type: str = Field(default="lambda", description="Action type")
    category: str = Field(default="business_logic", description="Action category")
    industry: str = Field(default="general", description="Target industry or 'general'")

    # Schema (optional - may not be present in older data)
    input_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input parameters schema")
    output_schema: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Output schema")

    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict, description="Type-specific config")
    # Lambda: function_arn
    # OpenAPI: spec_s3_uri
    # Gateway prebuilt: service_name

    # Handler path for registered actions
    handler_path: Optional[str] = Field(None, description="Handler path for lambda actions")


class ActionCreate(ActionBase):
    """Model for creating a new action"""
    pass


class Action(ActionBase):
    """Full action model with metadata"""
    action_id: str = Field(..., description="Action ID")
    version: str = Field(default="1.0")

    # Gateway references
    gateway_target_id: Optional[str] = Field(None, description="Foundry Agent Service Gateway target ID")
    lambda_arn: Optional[str] = Field(None, description="Lambda function ARN")

    # Status
    status: str = Field(default="active", description="active, deprecated, disabled")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system")

    # Usage tracking
    invocation_count: int = Field(default=0)
    last_invocation: Optional[datetime] = None
    avg_latency_ms: Optional[float] = None

    class Config:
        from_attributes = True


class ActionPack(BaseModel):
    """Collection of related actions (industry pack)"""
    name: str = Field(..., description="Pack name")
    version: str = Field(default="1.0")
    industry: str = Field(..., description="Target industry")
    description: str = Field(..., description="Pack description")
    actions: List[str] = Field(..., description="List of action IDs in this pack")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="cbts")
