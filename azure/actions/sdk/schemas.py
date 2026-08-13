"""
Schema definitions for Apex Actions
Provides type-safe schema building for Foundry Agent Service
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json


class PropertyType(str, Enum):
    """Supported property types"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class SchemaProperty:
    """Individual property in a schema"""
    type: PropertyType
    description: str
    required: bool = False
    default: Any = None
    enum: Optional[List[Any]] = None
    # For arrays
    items: Optional['SchemaProperty'] = None
    # For objects
    properties: Optional[Dict[str, 'SchemaProperty']] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON Schema format"""
        result = {
            "type": self.type.value,
            "description": self.description
        }

        if self.default is not None:
            result["default"] = self.default

        if self.enum:
            result["enum"] = self.enum

        if self.type == PropertyType.ARRAY and self.items:
            result["items"] = self.items.to_dict()

        if self.type == PropertyType.OBJECT and self.properties:
            result["properties"] = {
                k: v.to_dict() for k, v in self.properties.items()
            }

        return result


@dataclass
class ActionInputSchema:
    """Input schema for an action"""
    properties: Dict[str, SchemaProperty] = field(default_factory=dict)
    description: Optional[str] = None

    def add_property(
        self,
        name: str,
        prop_type: PropertyType,
        description: str,
        required: bool = False,
        **kwargs
    ) -> 'ActionInputSchema':
        """Add a property to the schema (fluent interface)"""
        self.properties[name] = SchemaProperty(
            type=prop_type,
            description=description,
            required=required,
            **kwargs
        )
        return self

    def add_string(self, name: str, description: str, required: bool = False, **kwargs) -> 'ActionInputSchema':
        return self.add_property(name, PropertyType.STRING, description, required, **kwargs)

    def add_number(self, name: str, description: str, required: bool = False, **kwargs) -> 'ActionInputSchema':
        return self.add_property(name, PropertyType.NUMBER, description, required, **kwargs)

    def add_integer(self, name: str, description: str, required: bool = False, **kwargs) -> 'ActionInputSchema':
        return self.add_property(name, PropertyType.INTEGER, description, required, **kwargs)

    def add_boolean(self, name: str, description: str, required: bool = False, **kwargs) -> 'ActionInputSchema':
        return self.add_property(name, PropertyType.BOOLEAN, description, required, **kwargs)

    def add_array(self, name: str, description: str, items: SchemaProperty, required: bool = False) -> 'ActionInputSchema':
        return self.add_property(name, PropertyType.ARRAY, description, required, items=items)

    def add_object(self, name: str, description: str, properties: Dict[str, SchemaProperty], required: bool = False) -> 'ActionInputSchema':
        return self.add_property(name, PropertyType.OBJECT, description, required, properties=properties)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON Schema format for Foundry Agent Service"""
        required_fields = [
            name for name, prop in self.properties.items() if prop.required
        ]

        result = {
            "type": "object",
            "properties": {
                name: prop.to_dict() for name, prop in self.properties.items()
            }
        }

        if self.description:
            result["description"] = self.description

        if required_fields:
            result["required"] = required_fields

        return result


@dataclass
class ActionOutputSchema:
    """Output schema for an action"""
    properties: Dict[str, SchemaProperty] = field(default_factory=dict)
    description: Optional[str] = None

    def add_property(
        self,
        name: str,
        prop_type: PropertyType,
        description: str,
        **kwargs
    ) -> 'ActionOutputSchema':
        """Add a property to the schema"""
        self.properties[name] = SchemaProperty(
            type=prop_type,
            description=description,
            **kwargs
        )
        return self

    def add_string(self, name: str, description: str, **kwargs) -> 'ActionOutputSchema':
        return self.add_property(name, PropertyType.STRING, description, **kwargs)

    def add_number(self, name: str, description: str, **kwargs) -> 'ActionOutputSchema':
        return self.add_property(name, PropertyType.NUMBER, description, **kwargs)

    def add_boolean(self, name: str, description: str, **kwargs) -> 'ActionOutputSchema':
        return self.add_property(name, PropertyType.BOOLEAN, description, **kwargs)

    def add_object(self, name: str, description: str, properties: Dict[str, SchemaProperty]) -> 'ActionOutputSchema':
        return self.add_property(name, PropertyType.OBJECT, description, properties=properties)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON Schema format"""
        result = {
            "type": "object",
            "properties": {
                name: prop.to_dict() for name, prop in self.properties.items()
            }
        }

        if self.description:
            result["description"] = self.description

        return result


# ============================================================================
# Pre-built Schema Builders for Common Patterns
# ============================================================================

def document_extraction_input() -> ActionInputSchema:
    """Standard input schema for document extraction actions"""
    return ActionInputSchema(
        description="Input for document extraction"
    ).add_string(
        "document_s3_uri", "blob URI of the document to process", required=True
    ).add_string(
        "blueprint_arn", "ARN of the BDA blueprint to use", required=False
    ).add_string(
        "output_s3_uri", "blob URI for output (optional)", required=False
    )


def document_extraction_output() -> ActionOutputSchema:
    """Standard output schema for document extraction actions"""
    return ActionOutputSchema(
        description="Output from document extraction"
    ).add_string(
        "status", "Processing status: success, processing, error"
    ).add_string(
        "invocation_arn", "ARN of the BDA invocation"
    ).add_object(
        "extracted_data", "Extracted structured data",
        properties={}  # Dynamic based on blueprint
    ).add_number(
        "confidence_score", "Overall confidence score"
    )


def lookup_input() -> ActionInputSchema:
    """Standard input schema for lookup actions"""
    return ActionInputSchema(
        description="Input for data lookup"
    ).add_string(
        "key", "Lookup key field name", required=True
    ).add_string(
        "value", "Value to look up", required=True
    ).add_string(
        "table_name", "Table/source to search", required=False
    )


def lookup_output() -> ActionOutputSchema:
    """Standard output schema for lookup actions"""
    return ActionOutputSchema(
        description="Output from data lookup"
    ).add_boolean(
        "found", "Whether the record was found"
    ).add_object(
        "data", "Retrieved data",
        properties={}
    ).add_string(
        "status", "Operation status"
    )


def approval_routing_input() -> ActionInputSchema:
    """Standard input schema for approval routing"""
    return ActionInputSchema(
        description="Input for approval routing decision"
    ).add_number(
        "amount", "Amount requiring approval", required=True
    ).add_string(
        "category", "Category of the request", required=False
    ).add_object(
        "context", "Additional context for routing",
        properties={}
    )


def approval_routing_output() -> ActionOutputSchema:
    """Standard output schema for approval routing"""
    return ActionOutputSchema(
        description="Output from approval routing"
    ).add_string(
        "routing_decision", "Where to route: auto_approve, manager, director, vp"
    ).add_string(
        "approver_email", "Email of the assigned approver"
    ).add_string(
        "reason", "Reason for the routing decision"
    )
