"""
Schema Generation Action
Uses Claude AI to analyze documents and generate extraction schemas for blueprints
"""

import boto3
import json
import base64
import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema
from sdk.schemas import SchemaProperty, PropertyType


# Field type mapping from Claude to blueprint schema
FIELD_TYPE_MAP = {
    "string": "string",
    "text": "string",
    "number": "number",
    "integer": "integer",
    "float": "number",
    "decimal": "number",
    "currency": "number",
    "amount": "number",
    "boolean": "boolean",
    "bool": "boolean",
    "date": "date",
    "datetime": "date",
    "timestamp": "date",
    "array": "array",
    "list": "array",
    "table": "array",
    "object": "object",
    "nested": "object"
}


@apex_action(ApexActionSchema(
    name="schema_generate",
    description="Analyze a sample document and generate a blueprint extraction schema using AI",
    category="document_intelligence",
    industry="general",
    input_schema=ActionInputSchema(description="Schema generation parameters")
        .add_string("document_s3_uri", "S3 URI of the sample document (s3://bucket/key)", required=True)
        .add_string("document_type", "Hint about document type (invoice, receipt, etc.)", required=False)
        .add_string("industry", "Target industry for field naming conventions", required=False)
        .add_string("blueprint_name", "Name for the generated blueprint", required=False)
        .add_boolean("include_tables", "Whether to include table extraction", required=False),
    output_schema=ActionOutputSchema(description="Generated schema")
        .add_string("status", "Generation status: success, error")
        .add_string("document_type", "Detected document type")
        .add_number("confidence", "Schema generation confidence 0-1")
        .add_object("generated_schema", "Generated blueprint schema with fields")
))
def schema_generate(
    document_s3_uri: str,
    document_type: str = None,
    industry: str = "general",
    blueprint_name: str = None,
    include_tables: bool = True
) -> dict:
    """
    Analyze a document and generate a blueprint schema

    Args:
        document_s3_uri: S3 URI of the sample document
        document_type: Hint about expected document type
        industry: Target industry for naming conventions
        blueprint_name: Optional name for the blueprint
        include_tables: Whether to detect and include table structures

    Returns:
        Generated blueprint schema ready for use
    """
    # Initialize AWS clients
    s3 = boto3.client('s3')
    bedrock = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

    try:
        # Parse S3 URI
        bucket, key = _parse_s3_uri(document_s3_uri)

        # Download document from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        document_bytes = response['Body'].read()
        content_type = response.get('ContentType', 'application/pdf')

        # Convert to base64 for Claude
        document_base64 = base64.standard_b64encode(document_bytes).decode('utf-8')

        # Determine media type
        media_type = _get_media_type(content_type, key)

        # Build schema generation prompt
        prompt = _build_schema_prompt(document_type, industry, include_tables)

        # Call Claude for schema generation
        model_id = os.environ.get('BEDROCK_CLAUDE_MODEL_ID', 'anthropic.claude-opus-4-5-20251101-v1:0')

        claude_response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.3,  # Lower temperature for more consistent schema generation
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": document_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            })
        )

        # Parse Claude response
        result = json.loads(claude_response['body'].read())
        schema_text = result['content'][0]['text']

        # Extract structured schema from Claude's response
        generated = _parse_schema_response(schema_text)

        # Build the final blueprint schema
        detected_type = generated.get('document_type', document_type or 'document')
        confidence = generated.get('confidence', 0.85)

        blueprint_schema = _build_blueprint_schema(
            generated=generated,
            blueprint_name=blueprint_name or f"{detected_type}_blueprint",
            document_type=detected_type,
            industry=industry
        )

        return {
            "status": "success",
            "document_type": detected_type,
            "confidence": confidence,
            "field_count": len(blueprint_schema.get('schema_fields', [])),
            "generated_schema": blueprint_schema
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "document_type": document_type or "unknown",
            "confidence": 0.0,
            "generated_schema": None
        }


def _parse_s3_uri(uri: str) -> tuple:
    """Parse S3 URI into bucket and key"""
    if not uri.startswith('s3://'):
        raise ValueError(f"Invalid S3 URI: {uri}")

    parts = uri[5:].split('/', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid S3 URI format: {uri}")

    return parts[0], parts[1]


def _get_media_type(content_type: str, key: str) -> str:
    """Determine media type for Claude vision"""
    if 'pdf' in content_type.lower():
        return 'application/pdf'
    elif 'png' in content_type.lower():
        return 'image/png'
    elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
        return 'image/jpeg'

    ext = key.lower().split('.')[-1] if '.' in key else ''
    ext_map = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'
    }

    return ext_map.get(ext, 'application/pdf')


def _build_schema_prompt(document_type: str = None, industry: str = None, include_tables: bool = True) -> str:
    """Build the schema generation prompt for Claude"""

    type_hint = f"This appears to be a **{document_type}** document." if document_type else ""
    industry_hint = f"Use naming conventions common in the **{industry}** industry." if industry else ""
    table_instruction = """
- If you find tables (like line items, transaction lists), create an array field
- For each table, define the structure of a single row as nested properties
""" if include_tables else ""

    return f"""Analyze this document and generate a JSON extraction schema that captures all important information.

{type_hint}
{industry_hint}

## Instructions

1. **Identify all extractable fields** - Look for:
   - Header information (document numbers, dates, references)
   - Entity information (names, addresses, IDs)
   - Financial data (amounts, totals, subtotals)
   - Line items or tables
   - Dates and timestamps
   - Status or categorical fields

2. **For each field, determine**:
   - A snake_case name (e.g., invoice_number, vendor_name)
   - The data type (string, number, date, boolean, array)
   - Whether it appears required (present and important)
   - A clear extraction instruction describing where to find it
{table_instruction}
3. **Use appropriate naming**:
   - Use snake_case for all field names
   - Be specific (use `invoice_date` not just `date`)
   - Group related fields logically

## Response Format

Respond with a JSON object following this exact structure:

```json
{{
    "document_type": "detected document type",
    "confidence": 0.95,
    "description": "Brief description of this document type",
    "fields": [
        {{
            "name": "field_name",
            "type": "string|number|date|boolean|array",
            "required": true,
            "instruction": "Clear instruction for where to find this field",
            "example_value": "Sample value from the document"
        }}
    ],
    "definitions": [
        {{
            "name": "LINEITEM",
            "description": "Definition for array items",
            "properties": [
                {{
                    "name": "description",
                    "type": "string",
                    "instruction": "Line item description"
                }}
            ]
        }}
    ]
}}
```

## Important Notes
- Only include fields that are actually visible in the document
- Be precise with field names - use domain-specific terminology
- For amounts/money, use type "number"
- For dates, use type "date"
- Include extraction instructions that would help locate each field

Only respond with the JSON object, no other text."""


def _parse_schema_response(response_text: str) -> Dict[str, Any]:
    """Parse Claude's schema generation response"""
    try:
        # Clean up response - handle markdown code blocks
        text = response_text.strip()
        if text.startswith('```'):
            lines = text.split('\n')
            # Remove first and last lines (```json and ```)
            text = '\n'.join(lines[1:-1])
        if text.endswith('```'):
            text = text[:-3]

        schema = json.loads(text)
        return schema

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response text: {response_text[:500]}")

        # Return minimal schema on parse error
        return {
            "document_type": "document",
            "confidence": 0.3,
            "description": "Auto-generated schema",
            "fields": [],
            "definitions": []
        }


def _build_blueprint_schema(
    generated: Dict[str, Any],
    blueprint_name: str,
    document_type: str,
    industry: str
) -> Dict[str, Any]:
    """Build a complete blueprint schema from generated fields"""

    # Convert generated fields to schema_fields format
    schema_fields = []
    for field in generated.get('fields', []):
        field_type = FIELD_TYPE_MAP.get(field.get('type', 'string').lower(), 'string')

        schema_field = {
            "name": field.get('name', 'unnamed_field'),
            "type": field_type,
            "description": field.get('instruction', ''),
            "required": field.get('required', False)
        }

        # Handle array types
        if field_type == 'array':
            # Find matching definition
            def_name = field.get('items_ref') or field.get('name', '').upper()
            matching_def = None
            for defn in generated.get('definitions', []):
                if defn.get('name', '').upper() == def_name.upper():
                    matching_def = defn
                    break

            if matching_def:
                schema_field['items'] = {
                    "$ref": f"#/definitions/{matching_def['name']}"
                }

        schema_fields.append(schema_field)

    # Build definitions
    definitions = {}
    for defn in generated.get('definitions', []):
        def_properties = {}
        for prop in defn.get('properties', []):
            def_properties[prop['name']] = {
                "type": FIELD_TYPE_MAP.get(prop.get('type', 'string').lower(), 'string'),
                "description": prop.get('instruction', prop.get('description', ''))
            }

        definitions[defn['name']] = {
            "description": defn.get('description', ''),
            "properties": def_properties
        }

    # Build complete blueprint
    now = datetime.utcnow().isoformat()

    return {
        "blueprint_id": f"{document_type}_{uuid.uuid4().hex[:8]}",
        "name": blueprint_name,
        "description": generated.get('description', f'Auto-generated schema for {document_type}'),
        "industry": industry,
        "document_type": document_type,
        "version": "1.0",
        "stage": "DEVELOPMENT",
        "schema_fields": schema_fields,
        "definitions": definitions,
        "extraction_instructions": f"Extract all fields as defined in the schema. Generated from sample document analysis.",
        "virtual_columns": [],
        "virtual_tables": [],
        "annotations": [],
        "created_at": now,
        "updated_at": now,
        "created_by": "schema_generate_action"
    }


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return schema_generate(**event)
