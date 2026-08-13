"""
Blueprint API endpoints
Manage Bedrock Data Automation blueprints
"""

from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File
from typing import List, Optional, Dict, Any
import uuid
import json
import boto3
import base64
import os
from datetime import datetime

from models.blueprint import Blueprint, BlueprintCreate, BlueprintStage, SchemaField, FieldType
import logging

from services.dynamodb import DynamoDBService
from services.list_cache import TTLCache, dedupe_by
from services.s3 import S3Service
from core.config import settings

logger = logging.getLogger(__name__)

# Short-lived cache for the list scan; invalidated on write or re-seed.
_list_cache = TTLCache()

router = APIRouter()
db = DynamoDBService(settings.DYNAMODB_BLUEPRINTS)
s3 = S3Service(settings.S3_BLUEPRINTS)


@router.get("/", response_model=List[Blueprint])
async def list_blueprints(
    industry: Optional[str] = Query(None),
    document_type: Optional[str] = Query(None),
    stage: Optional[BlueprintStage] = Query(None),
    limit: int = Query(500, le=1000)
):
    """List all blueprints with optional filters"""
    filters = {}
    if industry:
        filters["industry"] = industry
    if document_type:
        filters["document_type"] = document_type
    if stage:
        filters["stage"] = stage.value

    cache_key = f"blueprints:{industry}:{document_type}:{stage}:{limit}"

    async def _load():
        return await db.scan(filters=filters, limit=limit)

    items = await _list_cache.get_or_set(cache_key, _load)

    # Re-seeding an industry can create a second row for a blueprint that
    # already exists. Collapse duplicates — newest wins — so each appears once.
    before = len(items)
    items = dedupe_by(items, key="name", prefer="updated_at")
    if before != len(items):
        logger.info(
            "list_blueprints: collapsed %d duplicate row(s) — %d rows, %d blueprints",
            before - len(items), before, len(items),
        )
    # Tolerate legacy DynamoDB rows that pre-date the current Blueprint
    # schema — skip the malformed ones so a single bad record doesn't
    # 500 the whole list response.
    out: List[Blueprint] = []
    skipped = 0
    for item in items:
        try:
            out.append(Blueprint(**item))
        except Exception:
            skipped += 1
            continue
    if skipped:
        import logging
        logging.getLogger(__name__).warning(
            "list_blueprints: skipped %d malformed legacy items", skipped,
        )
    return out


@router.get("/{blueprint_id}", response_model=Blueprint)
async def get_blueprint(blueprint_id: str):
    """Get a specific blueprint by ID"""
    item = await db.get_item({"blueprint_id": blueprint_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint {blueprint_id} not found"
        )
    return Blueprint(**item)


@router.post("/", response_model=Blueprint, status_code=status.HTTP_201_CREATED)
async def create_blueprint(blueprint: BlueprintCreate):
    """Create a new blueprint"""
    blueprint_id = str(uuid.uuid4())
    now = datetime.utcnow()

    blueprint_data = blueprint.model_dump()
    blueprint_data.update({
        "blueprint_id": blueprint_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "stage": BlueprintStage.DEVELOPMENT.value
    })

    await db.put_item(blueprint_data)
    _list_cache.invalidate()

    # TODO: Create BDA blueprint
    # 1. Convert schema to BDA format
    # 2. Call CreateBlueprint API
    # 3. Store BDA ARN

    return Blueprint(**blueprint_data)


@router.delete("/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blueprint(blueprint_id: str):
    """Delete a blueprint"""
    existing = await db.get_item({"blueprint_id": blueprint_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blueprint {blueprint_id} not found"
        )

    await db.delete_item({"blueprint_id": blueprint_id})
    _list_cache.invalidate()


@router.post("/{blueprint_id}/deploy")
async def deploy_blueprint(blueprint_id: str, target_stage: BlueprintStage = BlueprintStage.LIVE):
    """Deploy blueprint to BDA (copy to LIVE stage)"""
    blueprint = await get_blueprint(blueprint_id)

    # TODO: Implement BDA deployment
    # 1. Call CopyBlueprintStage API
    # 2. Update local record

    return {
        "blueprint_id": blueprint_id,
        "status": "deploying",
        "target_stage": target_stage.value
    }


@router.post("/{blueprint_id}/optimize")
async def optimize_blueprint(
    blueprint_id: str,
    samples: List[UploadFile] = File(..., description="Sample documents"),
    ground_truth: List[UploadFile] = File(..., description="Ground truth JSON files")
):
    """Optimize blueprint with ground truth samples"""
    blueprint = await get_blueprint(blueprint_id)

    if len(samples) != len(ground_truth):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of samples must match number of ground truth files"
        )

    # Upload samples and ground truth to S3
    sample_keys = []
    ground_truth_keys = []

    for i, (sample, gt) in enumerate(zip(samples, ground_truth)):
        sample_key = f"optimization/{blueprint_id}/samples/{sample.filename}"
        gt_key = f"optimization/{blueprint_id}/ground-truth/{gt.filename}"

        await s3.upload_file(await sample.read(), sample_key)
        await s3.upload_file(await gt.read(), gt_key)

        sample_keys.append(sample_key)
        ground_truth_keys.append(gt_key)

    # TODO: Call InvokeBlueprintOptimizationAsync API

    return {
        "blueprint_id": blueprint_id,
        "status": "optimizing",
        "samples_uploaded": len(samples)
    }


@router.post("/{blueprint_id}/test")
async def test_blueprint(blueprint_id: str, document: UploadFile = File(...)):
    """Test blueprint with a sample document"""
    blueprint = await get_blueprint(blueprint_id)

    # Upload document to S3
    doc_key = f"test/{blueprint_id}/{document.filename}"
    await s3.upload_file(await document.read(), doc_key)

    # TODO: Call InvokeDataAutomationAsync with this blueprint

    return {
        "blueprint_id": blueprint_id,
        "status": "processing",
        "document": document.filename
    }


@router.post("/{blueprint_id}/sample-document")
async def upload_sample_document(
    blueprint_id: str,
    file: UploadFile = File(...)
):
    """Upload a sample document for visual annotation"""
    # Verify blueprint exists
    blueprint = await get_blueprint(blueprint_id)

    # Upload to S3
    s3_key = f"samples/{blueprint_id}/{file.filename}"
    content = await file.read()
    await s3.upload_file(content, s3_key, {
        "blueprint_id": blueprint_id,
        "purpose": "annotation_sample",
        "uploaded_at": datetime.utcnow().isoformat()
    })

    # Update blueprint with sample document reference
    now = datetime.utcnow()
    await db.update_item(
        {"blueprint_id": blueprint_id},
        {
            "sample_document_s3_key": s3_key,
            "updated_at": now.isoformat()
        }
    )
    _list_cache.invalidate()

    return {
        "blueprint_id": blueprint_id,
        "sample_document_s3_key": s3_key,
        "filename": file.filename
    }


@router.get("/{blueprint_id}/sample-document")
async def get_sample_document_url(blueprint_id: str):
    """Get presigned URL for sample document"""
    blueprint = await get_blueprint(blueprint_id)

    s3_key = blueprint.sample_document_s3_key
    if not s3_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sample document uploaded for this blueprint"
        )

    # Generate presigned URL
    presigned_url = await s3.get_presigned_url(s3_key, expiration=3600)

    return {
        "blueprint_id": blueprint_id,
        "presigned_url": presigned_url,
        "expires_in_seconds": 3600
    }


@router.post("/generate-from-sample", response_model=Blueprint)
async def generate_blueprint_from_sample(
    file: UploadFile = File(...),
    document_type: Optional[str] = Query(None, description="Hint about document type"),
    industry: str = Query("general", description="Target industry"),
    name: Optional[str] = Query(None, description="Blueprint name")
):
    """
    Generate a blueprint schema from a sample document using AI.

    Claude vision analyzes the document and automatically identifies:
    - Fields to extract
    - Data types
    - Table structures
    - Extraction instructions
    """
    # Read document content (process in-memory for local dev)
    temp_id = str(uuid.uuid4())
    s3_key = f"schema-gen/{temp_id}/{file.filename}"

    content = await file.read()

    # Try to upload to S3, but don't fail if bucket doesn't exist (for local dev)
    try:
        await s3.upload_file(content, s3_key, {
            "purpose": "schema_generation",
            "uploaded_at": datetime.utcnow().isoformat()
        })
    except Exception as s3_error:
        # Log but continue - S3 is optional for schema generation
        print(f"S3 upload skipped (bucket may not exist): {s3_error}")
        s3_key = None

    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )

        # Convert to base64
        document_base64 = base64.standard_b64encode(content).decode('utf-8')

        # Determine media type
        ext = file.filename.lower().split('.')[-1] if '.' in file.filename else 'pdf'
        media_type_map = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        media_type = media_type_map.get(ext, 'application/pdf')

        # Build schema generation prompt
        type_hint = f"This appears to be a **{document_type}** document." if document_type else ""
        industry_hint = f"Use naming conventions common in the **{industry}** industry." if industry else ""

        prompt = f"""Analyze this document and generate a JSON extraction schema.

{type_hint}
{industry_hint}

IMPORTANT: Keep descriptions SHORT (max 10 words). Limit to 25 most important fields.

For each extractable field:
- snake_case name
- type: string, number, date, boolean, or array
- required: true/false
- description: brief extraction hint (max 10 words)

Return ONLY valid JSON, no markdown:
{{
    "document_type": "detected type",
    "description": "Brief description",
    "confidence": 0.95,
    "fields": [
        {{"name": "field_name", "type": "string", "required": true, "description": "Short hint"}}
    ],
    "definitions": []
}}

RESPOND WITH JSON ONLY. NO MARKDOWN CODE BLOCKS."""

        # Call Claude
        model_id = os.environ.get('BEDROCK_CLAUDE_MODEL_ID', 'us.anthropic.claude-opus-4-6-v1')

        # Build content based on file type
        if media_type == 'application/pdf':
            # PDFs use document type
            document_content = {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": document_base64
                }
            }
        else:
            # Images use image type
            document_content = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": document_base64
                }
            }

        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 16384,
                "temperature": 0.3,
                "messages": [{
                    "role": "user",
                    "content": [
                        document_content,
                        {"type": "text", "text": prompt}
                    ]
                }]
            })
        )

        result = json.loads(response['body'].read())
        response_text = result['content'][0]['text']

        # Parse response
        try:
            text = response_text.strip()
            # Handle markdown code blocks
            if text.startswith('```json'):
                text = text[7:]  # Remove ```json
            elif text.startswith('```'):
                text = text[3:]  # Remove ```
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()

            generated = json.loads(text)
        except json.JSONDecodeError as e:
            # Save raw response for debugging
            with open('/tmp/claude_raw_response.txt', 'w') as f:
                f.write(response_text)
            print(f"JSON Parse Error: {e}")
            print(f"Raw response saved to /tmp/claude_raw_response.txt")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse AI-generated schema: {str(e)}"
            )

        # Build blueprint from generated schema
        detected_type = generated.get('document_type', document_type or 'document')
        blueprint_id = str(uuid.uuid4())
        now = datetime.utcnow()

        # Convert fields to SchemaField format
        schema_fields = []
        for field in generated.get('fields', []):
            field_type = _map_field_type(field.get('type', 'string'))
            schema_fields.append({
                "name": field.get('name', 'unnamed'),
                "type": field_type,
                "description": field.get('description', ''),
                "required": field.get('required', False)
            })

        # Create blueprint
        blueprint_data = {
            "blueprint_id": blueprint_id,
            "name": name or f"{detected_type}_blueprint",
            "description": generated.get('description', f'Auto-generated schema for {detected_type}'),
            "industry": industry,
            "document_type": detected_type,
            "version": "1.0",
            "stage": BlueprintStage.DEVELOPMENT.value,
            "schema_fields": schema_fields,
            "extraction_instructions": f"Extract fields as defined. Generated from sample document analysis.",
            "virtual_columns": [],
            "virtual_tables": [],
            "annotations": [],
            "sample_document_s3_key": s3_key,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "created_by": "schema_generate_api"
        }

        # Save to database
        await db.put_item(blueprint_data)
        _list_cache.invalidate()

        return Blueprint(**blueprint_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema generation failed: {str(e)}"
        )


def _map_field_type(type_str: str) -> str:
    """Map generated type string to FieldType"""
    type_map = {
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
        "array": "array",
        "list": "array",
        "table": "array",
        "object": "object"
    }
    return type_map.get(type_str.lower(), "string")


# Path to blueprints directory (JSON files)
from pathlib import Path
BLUEPRINTS_DIR = Path(__file__).parent.parent.parent / "blueprints"


@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_blueprints(
    industry: Optional[str] = Query(None, description="Seed specific industry only"),
    force: bool = Query(False, description="Force re-seed existing blueprints")
):
    """
    Seed blueprints from JSON files in the blueprints directory.
    Useful for initializing the database with predefined blueprints.
    """
    seeded = []
    errors = []

    if not BLUEPRINTS_DIR.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blueprints directory not found: {BLUEPRINTS_DIR}"
        )

    # Find all JSON files in the blueprints directory
    json_files = list(BLUEPRINTS_DIR.rglob("*.json"))

    for json_file in json_files:
        try:
            # Filter by industry if specified
            if industry and industry not in str(json_file):
                continue

            with open(json_file, 'r') as f:
                blueprint_json = json.load(f)

            if not blueprint_json:
                continue

            # Extract blueprint name from file or content
            blueprint_name = blueprint_json.get('name', json_file.stem)

            # Determine industry from directory path
            parts = json_file.relative_to(BLUEPRINTS_DIR).parts
            file_industry = parts[0] if len(parts) > 1 else "general"

            # If the JSON carries an explicit, stable blueprint_id (e.g.
            # `bp-eprod-invoice`) we honor it so the canvas list, detail
            # page links, and seeded DDB row all line up. Otherwise the
            # legacy "match by name or mint UUID" path runs.
            explicit_bp_id = blueprint_json.get('blueprint_id')

            existing = None
            if explicit_bp_id:
                existing_row = await db.get_item({"blueprint_id": explicit_bp_id})
                existing = [existing_row] if existing_row else None
            if not existing:
                existing = await db.scan(filters={"name": blueprint_name}, limit=1)
            if existing and not force:
                continue

            if explicit_bp_id:
                blueprint_id = explicit_bp_id
            elif existing:
                blueprint_id = existing[0]["blueprint_id"]
            else:
                blueprint_id = str(uuid.uuid4())
            now = datetime.utcnow()

            # Three blueprint JSON formats are supported:
            #   (1) BDA wrapper:    { bdaSchema: { description, fields|properties, ... } }
            #   (2) JSON Schema:    { schema: { type:'object', properties: {...}, required: [...] } }
            #                       (used by STP nuclear blueprints)
            #   (3) Direct flat:    { description, document_type, schema_fields: [...] }
            # The order below matches the precedence — (1) wins if present.
            schema_fields: List[Dict[str, Any]] = []

            def _flatten_jsonschema_properties(props: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
                """Walk a JSON-Schema `properties` map and emit flat field rows.
                Nested objects are recursed; arrays are emitted as a single
                'array' row. Required fields are inferred from the parent
                object's `required` list when available."""
                rows: List[Dict[str, Any]] = []
                for fname, fdef in (props or {}).items():
                    full_name = f"{path}.{fname}" if path else fname
                    ftype = (fdef.get("type") or "string")
                    rows.append({
                        "name": full_name,
                        "type": _map_field_type(ftype),
                        "description": fdef.get("description") or fdef.get("instruction") or "",
                        "required": fdef.get("required", False),
                    })
                    if ftype == "object" and isinstance(fdef.get("properties"), dict):
                        rows.extend(_flatten_jsonschema_properties(fdef["properties"], full_name))
                return rows

            if 'bdaSchema' in blueprint_json:
                # (1) BDA wrapper
                bda_schema = blueprint_json['bdaSchema']
                description = bda_schema.get('description', '')
                document_type = bda_schema.get('documentClass') or bda_schema.get('class', json_file.stem)
                extraction_instructions = bda_schema.get('extractionInstructions', '')
                fields_dict = bda_schema.get('fields') or bda_schema.get('properties', {})
                for field_name, field_def in fields_dict.items():
                    schema_fields.append({
                        "name": field_name,
                        "type": _map_field_type(field_def.get('type', 'string')),
                        "description": field_def.get('description') or field_def.get('instruction', ''),
                        "required": field_def.get('required', False),
                    })
            elif isinstance(blueprint_json.get('schema'), dict) and isinstance(blueprint_json['schema'].get('properties'), dict):
                # (2) Top-level JSON Schema with properties map (STP format)
                json_schema = blueprint_json['schema']
                description = blueprint_json.get('description', '')
                document_type = blueprint_json.get('documentType') or blueprint_json.get('document_type', json_file.stem)
                extraction_instructions = blueprint_json.get('extractionInstructions', '') or blueprint_json.get('extraction_instructions', '')
                schema_fields = _flatten_jsonschema_properties(json_schema.get('properties', {}))
                # Honor a top-level required[] list — flag matching field rows
                required_set = set(json_schema.get('required') or [])
                for row in schema_fields:
                    if row['name'].split('.')[0] in required_set:
                        row['required'] = True
            else:
                # (3) Direct flat format
                description = blueprint_json.get('description', '')
                document_type = blueprint_json.get('document_type', json_file.stem)
                extraction_instructions = blueprint_json.get('extraction_instructions', '')
                schema_fields = blueprint_json.get('schema_fields', [])

            # Build blueprint data
            blueprint_data = {
                "blueprint_id": blueprint_id,
                "name": blueprint_name,
                "description": description,
                "industry": blueprint_json.get('industry', file_industry),
                "document_type": document_type,
                "version": blueprint_json.get('version', '1.0'),
                "stage": BlueprintStage.DEVELOPMENT.value,
                "schema_fields": schema_fields,
                "extraction_instructions": extraction_instructions,
                "virtual_columns": blueprint_json.get('virtual_columns', []),
                "virtual_tables": blueprint_json.get('virtual_tables', []),
                "annotations": blueprint_json.get('annotations', []),
                "sample_document_s3_key": blueprint_json.get('sample_document_s3_key'),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "created_by": "seed"
            }

            await db.put_item(blueprint_data)
            _list_cache.invalidate()
            seeded.append({
                "blueprint_id": blueprint_id,
                "name": blueprint_name,
                "industry": blueprint_data["industry"],
                "file": str(json_file.relative_to(BLUEPRINTS_DIR))
            })

        except Exception as e:
            errors.append({
                "file": str(json_file),
                "error": str(e)
            })

    return {
        "message": f"Seeded {len(seeded)} blueprints",
        "seeded": seeded,
        "errors": errors if errors else None
    }


async def warm_list_cache() -> None:
    """Prime the default gallery query at startup (see playbooks.warm_list_cache)."""
    await _list_cache.warm(
        "blueprints:None:None:None:500",
        lambda: db.scan(filters={}, limit=500),
        label="blueprints",
    )
