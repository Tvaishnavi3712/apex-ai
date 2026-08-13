"""
Document API endpoints
Handle document upload and BDA processing
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Optional
import uuid
import json
import boto3
from services.azure_openai import get_messages_client
import base64
import os
from datetime import datetime

from services.blob import BlobService
from services.cosmos import CosmosService
from models.blueprint import ClassificationResult
from core.config import settings

router = APIRouter()
s3_incoming = BlobService(settings.CONTAINER_DOCUMENTS_INCOMING)
s3_processed = BlobService(settings.CONTAINER_DOCUMENTS_PROCESSED)


# ---------------------------------------------------------------------------
# Demo file preview — serves the synthetic STP demo docs (and any other
# demo content) from the local `synthetic-data/` tree as plain text so the
# Agent Hub right-panel preview can render them. Strict whitelist on the
# folder name + filename to prevent path traversal.
# ---------------------------------------------------------------------------
_DEMO_DOC_ROOTS = {
    "nuclear_operations": Path(__file__).resolve().parent.parent.parent
        / "synthetic-data" / "nuclear_operations" / "demo_docs",
    "agentic_enterprise": Path(__file__).resolve().parent.parent.parent
        / "synthetic-data" / "agentic_enterprise",
    # Verizon Far Edge — runbook excerpts, release notes, KB, upgrade procedures.
    # Surfaced in Agent Hub's File tab when demoMode === 'verizon_far_edge'.
    "verizon_far_edge": Path(__file__).resolve().parent.parent.parent
        / "synthetic-data" / "verizon_far_edge" / "demo_docs",
}


@router.get("/demo-preview/{folder}/{filename}")
async def demo_preview(folder: str, filename: str):
    """Return the plain-text contents of a demo document for in-app preview.

    Whitelist only — allowed folders are 'nuclear_operations' and
    'agentic_enterprise'. Filename must end in .txt or .md to avoid
    accidentally serving non-text files. No path traversal allowed.
    """
    if folder not in _DEMO_DOC_ROOTS:
        raise HTTPException(status_code=404, detail=f"unknown folder '{folder}'")
    if "/" in filename or ".." in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="invalid filename")
    if not (filename.endswith(".txt") or filename.endswith(".md")
            or filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="only .txt / .md / .json")

    path = _DEMO_DOC_ROOTS[folder] / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail=f"file not found: {filename}")

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"read failed: {e}")

    # Cap response size at 256 KB so we don't DoS the browser with a huge
    # text blob. The demo docs are all <50 KB.
    if len(content) > 256 * 1024:
        content = content[: 256 * 1024] + "\n\n... (truncated at 256 KB)"

    return {
        "folder": folder,
        "filename": filename,
        "size_bytes": path.stat().st_size,
        "content": content,
    }


@router.get("/demo-preview")
async def demo_preview_index():
    """List available demo documents so the UI can show a picker."""
    out: dict = {}
    for folder, root in _DEMO_DOC_ROOTS.items():
        if not root.exists():
            continue
        files = []
        for f in sorted(root.iterdir()):
            if not f.is_file():
                continue
            if not (f.suffix in {".txt", ".md", ".json"}):
                continue
            if f.name.startswith("."):
                continue
            files.append({
                "filename": f.name,
                "size_bytes": f.stat().st_size,
                "url": f"/api/v1/documents/demo-preview/{folder}/{f.name}",
            })
        out[folder] = files
    return out


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    blueprint_id: Optional[str] = Query(None, description="Blueprint to use for processing"),
    agent_id: Optional[str] = Query(None, description="Agent to process this document"),
    metadata: Optional[dict] = None
):
    """Upload a document for processing"""
    document_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
    s3_key = f"{document_id}/{file.filename}"

    # Upload to S3
    content = await file.read()
    await s3_incoming.upload_file(content, s3_key, {
        "document_id": document_id,
        "original_filename": file.filename,
        "blueprint_id": blueprint_id or "",
        "agent_id": agent_id or "",
        "uploaded_at": datetime.utcnow().isoformat()
    })

    # If blueprint specified, trigger BDA processing via Event Grid
    # The S3 event will trigger the processing pipeline

    return {
        "document_id": document_id,
        "filename": file.filename,
        "s3_key": s3_key,
        "status": "uploaded",
        "blueprint_id": blueprint_id,
        "agent_id": agent_id,
        "message": "Document uploaded. Processing will start automatically if blueprint/agent specified."
    }


@router.post("/upload-batch")
async def upload_documents_batch(
    files: List[UploadFile] = File(...),
    blueprint_id: Optional[str] = Query(None),
    agent_id: Optional[str] = Query(None)
):
    """Upload multiple documents for batch processing"""
    results = []

    for file in files:
        result = await upload_document(file, blueprint_id, agent_id)
        results.append(result)

    return {
        "uploaded_count": len(results),
        "documents": results
    }


@router.get("/{document_id}")
async def get_document_status(document_id: str):
    """Get document processing status"""
    # Check incoming bucket
    incoming_files = await s3_incoming.list_files(prefix=f"{document_id}/")

    # Check processed bucket
    processed_files = await s3_processed.list_files(prefix=f"{document_id}/")

    if not incoming_files and not processed_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    status = "uploaded"
    if processed_files:
        status = "processed"

    return {
        "document_id": document_id,
        "status": status,
        "incoming_files": incoming_files,
        "processed_files": processed_files
    }


@router.get("/{document_id}/result")
async def get_document_result(document_id: str):
    """Get document processing result"""
    # Look for result JSON in processed bucket
    result_key = f"{document_id}/result.json"

    try:
        result = await s3_processed.get_json(result_key)
        return {
            "document_id": document_id,
            "status": "completed",
            "result": result
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result not found for document {document_id}. Processing may still be in progress."
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its results"""
    # Delete from both buckets
    await s3_incoming.delete_prefix(f"{document_id}/")
    await s3_processed.delete_prefix(f"{document_id}/")

    return {"status": "deleted", "document_id": document_id}


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: str,
    blueprint_id: str = Query(..., description="Blueprint to use for reprocessing")
):
    """Reprocess a document with a different blueprint"""
    # Check document exists
    incoming_files = await s3_incoming.list_files(prefix=f"{document_id}/")
    if not incoming_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )

    # TODO: Trigger BDA reprocessing

    return {
        "document_id": document_id,
        "blueprint_id": blueprint_id,
        "status": "reprocessing"
    }


@router.post("/classify", response_model=ClassificationResult)
async def classify_document(
    file: UploadFile = File(...),
    industry_hint: Optional[str] = Query(None, description="Hint about expected industry"),
    auto_extract: bool = Query(False, description="Automatically extract if confident match found")
):
    """
    Classify a document using AI to determine document type and matching blueprint.

    Uses Claude vision to analyze the document and match it to appropriate blueprints.
    """
    # Upload document to S3 for processing
    document_id = str(uuid.uuid4())
    s3_key = f"classify/{document_id}/{file.filename}"

    content = await file.read()
    await s3_incoming.upload_file(content, s3_key, {
        "purpose": "classification",
        "uploaded_at": datetime.utcnow().isoformat()
    })

    # Build blob URI
    bucket = settings.CONTAINER_DOCUMENTS_INCOMING
    document_s3_uri = f"s3://{bucket}/{s3_key}"

    try:
        # Initialize Azure OpenAI client
        llm = get_messages_client()

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

        # Get available blueprints
        db_blueprints = CosmosService(settings.TABLE_BLUEPRINTS)
        filters = {"industry": industry_hint} if industry_hint else {}
        blueprints = await db_blueprints.scan(filters=filters, limit=30)

        # Build blueprint context for prompt
        bp_context = "\n".join([
            f"- {bp.get('blueprint_id')}: {bp.get('name', '')} ({bp.get('document_type', '')}) - {bp.get('description', '')[:80]}"
            for bp in blueprints
        ]) if blueprints else "No blueprints available"

        # Build classification prompt
        prompt = f"""Analyze this document and classify it.

Available blueprints:
{bp_context}

Document types to consider: invoice, receipt, bank_statement, purchase_order, contract, resume, claim, bill_of_lading, packing_slip, quality_inspection, offer_letter, tax_form, medical_record, other

Return a JSON response:
{{
    "document_type": "the detected type",
    "blueprint_id": "matching blueprint ID if found",
    "blueprint_name": "blueprint name",
    "confidence": 0.95,
    "reasoning": "Brief explanation"
}}

Only respond with JSON."""

        # Call Claude
        model_id = os.environ.get('AZURE_OPENAI_DEPLOYMENT_DEFAULT', 'anthropic.claude-opus-4-5-20251101-v1:0')

        response = llm.invoke_model(
            modelId=model_id,
            body=json.dumps({
                                "max_tokens": 1024,
                "messages": [{
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
                        {"type": "text", "text": prompt}
                    ]
                }]
            })
        )

        result = json.loads(response['body'].read())
        response_text = result['content'][0]['text']

        # Parse response
        try:
            # Handle markdown code blocks
            text = response_text.strip()
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1])

            classification = json.loads(text)
        except json.JSONDecodeError:
            classification = {
                "document_type": "other",
                "confidence": 0.3,
                "reasoning": response_text[:200]
            }

        # Auto-extract if requested and confident
        if auto_extract and classification.get('confidence', 0) >= 0.8 and classification.get('blueprint_id'):
            # TODO: Trigger extraction with matched blueprint
            pass

        return ClassificationResult(
            document_type=classification.get('document_type', 'other'),
            blueprint_id=classification.get('blueprint_id'),
            blueprint_name=classification.get('blueprint_name'),
            confidence=float(classification.get('confidence', 0.5)),
            reasoning=classification.get('reasoning'),
            alternatives=classification.get('alternatives', [])
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


# ═════════════════════════════════════════════════════════════════════
# STP Phase 2 — static PDF endpoint for the 3 hero documents
# ═════════════════════════════════════════════════════════════════════
#
# The chat citation links from MaintenanceAgent / PolicyAgent point at
# /api/v1/documents/stp/<filename>.pdf. We resolve to the local hero-PDF
# corpus (synthetic-data/nuclear_operations/pdfs/) and stream the file.
#
# Production STP would replace this with S3 presigned URLs against the
# FileNet-export bucket.

_STP_PDF_DIR = (
    Path(__file__).resolve().parents[2]
    / "synthetic-data" / "nuclear_operations" / "pdfs"
)


@router.get("/stp/{filename}")
async def get_stp_pdf(filename: str):
    """Serve a hand-curated STP hero PDF.

    Whitelisted to .pdf files in the synthetic-data/nuclear_operations/pdfs/
    directory. No path traversal — the filename is sanitized to its basename
    and only files that already exist in _STP_PDF_DIR resolve.
    """
    # Reject path traversal attempts up front
    safe_name = Path(filename).name
    if not safe_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are served from this endpoint")

    full = _STP_PDF_DIR / safe_name
    if not full.exists() or not full.is_file():
        raise HTTPException(status_code=404, detail=f"STP PDF not found: {safe_name}")

    return FileResponse(
        str(full),
        media_type="application/pdf",
        filename=safe_name,
        headers={
            "Cache-Control": "public, max-age=300",
            "X-Apex-Source": "stp-synthetic-corpus",
        },
    )
