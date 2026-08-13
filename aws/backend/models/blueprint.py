"""
Blueprint data models
Represents Bedrock Data Automation blueprints for document extraction
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class BlueprintStage(str, Enum):
    """Blueprint deployment stage"""
    DEVELOPMENT = "DEVELOPMENT"
    LIVE = "LIVE"


class FieldType(str, Enum):
    """Field data types"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    ARRAY = "array"
    OBJECT = "object"


class ExpressionType(str, Enum):
    """Types of virtual column expressions"""
    FORMULA = "formula"           # Mathematical: subtotal + tax_amount
    CONCATENATE = "concatenate"   # String concat: vendor_name + " - " + vendor_id
    AGGREGATE = "aggregate"       # Array ops: sum(line_items.amount)
    CONDITIONAL = "conditional"   # If/else: if(amount > 1000, "HIGH", "LOW")
    LOOKUP = "lookup"             # Reference lookup from another field


class SchemaField(BaseModel):
    """Individual field in the extraction schema"""
    name: str = Field(..., description="Field name")
    type: str = Field(default="string", description="Field type")
    description: str = Field(default="", description="Field description for extraction guidance")
    required: bool = Field(default=False)
    # For arrays
    items: Optional[Dict[str, Any]] = Field(None, description="Array item schema")
    # For objects
    properties: Optional[Dict[str, Any]] = Field(None, description="Nested properties")


class VirtualColumn(BaseModel):
    """
    Computed/derived field calculated post-extraction.
    Enables data engineering without code.
    """
    name: str = Field(..., description="Virtual column name (snake_case)")
    type: FieldType = Field(default=FieldType.STRING, description="Output data type")
    expression_type: ExpressionType = Field(..., description="Type of expression")
    expression: str = Field(..., description="Expression to evaluate, e.g., 'subtotal + tax_amount'")
    description: Optional[str] = Field(None, description="Human-readable description")
    source_fields: List[str] = Field(default_factory=list, description="Fields this depends on")


class VirtualTable(BaseModel):
    """
    Aggregated view computed from an array field.
    Creates summary tables from line items.
    """
    name: str = Field(..., description="Virtual table name")
    description: Optional[str] = Field(None)
    source_array: str = Field(..., description="Source array field, e.g., 'line_items'")
    group_by: Optional[List[str]] = Field(None, description="Fields to group by")
    aggregations: List[VirtualColumn] = Field(default_factory=list, description="Aggregation columns")


class BoundingBox(BaseModel):
    """
    Normalized coordinates for a field annotation on a document page.
    All values are 0-1 normalized relative to page dimensions.
    """
    x: float = Field(..., ge=0, le=1, description="Left edge (0-1)")
    y: float = Field(..., ge=0, le=1, description="Top edge (0-1)")
    width: float = Field(..., ge=0, le=1, description="Width (0-1)")
    height: float = Field(..., ge=0, le=1, description="Height (0-1)")
    page: int = Field(..., ge=1, description="Page number (1-indexed)")


class FieldAnnotation(BaseModel):
    """
    Visual annotation linking a field to a location on the sample document.
    Used by the Visual Annotation UI.
    """
    annotation_id: str = Field(..., description="Unique annotation ID")
    field_name: str = Field(..., description="Name of the field this annotates")
    bounding_box: BoundingBox = Field(..., description="Location on document")
    sample_text: Optional[str] = Field(None, description="Sample text extracted from region")


class BlueprintBase(BaseModel):
    """Base blueprint model"""
    name: str = Field(..., description="Blueprint name")
    description: str = Field(default="", description="Blueprint description")
    industry: str = Field(default="general", description="Target industry")
    document_type: str = Field(default="document", description="Type of document: invoice, statement, claim, contract")
    version: str = Field(default="1.0")

    # Extraction schema (optional - may be stored in S3 for older blueprints)
    schema_fields: List[SchemaField] = Field(default_factory=list, description="Fields to extract")

    # Additional extraction instructions
    extraction_instructions: Optional[str] = Field(None, description="Additional guidance for extraction")

    # Virtual fields (computed post-extraction)
    virtual_columns: List[VirtualColumn] = Field(default_factory=list, description="Computed columns")
    virtual_tables: List[VirtualTable] = Field(default_factory=list, description="Aggregated tables")

    # Visual annotations
    annotations: List[FieldAnnotation] = Field(default_factory=list, description="Field annotations on sample doc")
    sample_document_s3_key: Optional[str] = Field(None, description="S3 key of sample document for annotation")

    # Legacy fields from S3-based blueprints
    s3_uri: Optional[str] = Field(None, description="S3 URI for legacy blueprints")
    bda_arn: Optional[str] = Field(None, description="BDA ARN")
    status: Optional[str] = Field(None, description="Blueprint status")


class BlueprintCreate(BlueprintBase):
    """Model for creating a new blueprint"""
    pass


class Blueprint(BlueprintBase):
    """Full blueprint model with metadata"""
    blueprint_id: str = Field(..., description="Internal blueprint ID")
    stage: BlueprintStage = Field(default=BlueprintStage.DEVELOPMENT)

    # BDA references
    bda_blueprint_arn: Optional[str] = Field(None, description="BDA Blueprint ARN")
    bda_blueprint_version: Optional[str] = Field(None, description="BDA Blueprint version")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="system")

    # Optimization stats
    optimization_runs: int = Field(default=0)
    last_optimization: Optional[datetime] = None
    accuracy_score: Optional[float] = Field(None, description="Accuracy from last optimization")

    class Config:
        from_attributes = True


class ClassificationResult(BaseModel):
    """Result from document classification"""
    document_type: str = Field(..., description="Detected document type")
    blueprint_id: Optional[str] = Field(None, description="Matched blueprint ID")
    blueprint_name: Optional[str] = Field(None, description="Matched blueprint name")
    confidence: float = Field(..., ge=0, le=1, description="Classification confidence 0-1")
    reasoning: Optional[str] = Field(None, description="Explanation for classification")
    alternatives: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative classifications")
