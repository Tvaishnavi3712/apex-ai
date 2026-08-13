"""
Workflow Import API — bring existing Robot Framework / Ansible automation into Apex.

    GET  /samples            real artifacts shipped with the platform
    POST /analyze            parse a workflow and propose an Apex playbook (writes nothing)
    POST /analyze/sample     same, for a shipped sample by filename
    POST /commit             write an approved proposal to playbooks/<industry>/
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services import workflow_import as importer

log = structlog.get_logger()
router = APIRouter()

# Guard against a paste large enough to stall the API.
MAX_CONTENT_BYTES = 8 * 1024 * 1024


class AnalyzeRequest(BaseModel):
    content: str = Field(..., description="Raw file contents")
    filename: str = ""
    name_hint: str = Field("", description="Preferred name for the resulting playbook")


class SampleRequest(BaseModel):
    filename: str
    name_hint: str = ""


class CommitRequest(BaseModel):
    playbook: Dict[str, Any]
    overwrite: bool = False


@router.get("/samples")
async def samples() -> Dict[str, Any]:
    """Robot Framework outputs shipped with the platform, importable as-is."""
    rows = importer.list_samples()
    return {"samples": rows, "count": len(rows)}


@router.post("/analyze")
async def analyze(body: AnalyzeRequest) -> Dict[str, Any]:
    """Parse a workflow and propose a playbook. Nothing is written."""
    if len(body.content.encode("utf-8")) > MAX_CONTENT_BYTES:
        raise HTTPException(status_code=413, detail="File too large (limit 8 MB)")
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="No content supplied")

    try:
        return importer.analyze(body.content, body.filename, body.name_hint)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:  # noqa: BLE001
        log.error("import.analyze_failed", filename=body.filename, error=str(e))
        raise HTTPException(status_code=500, detail=f"Could not analyze this file: {e}")


@router.post("/analyze/sample")
async def analyze_sample(body: SampleRequest) -> Dict[str, Any]:
    """Analyze one of the shipped samples — the one-click demo path."""
    try:
        content = importer.read_sample(body.filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        return importer.analyze(content, body.filename, body.name_hint)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/commit")
async def commit(body: CommitRequest) -> Dict[str, Any]:
    """Write an approved proposal to disk."""
    if not body.playbook:
        raise HTTPException(status_code=400, detail="No playbook supplied")
    try:
        return importer.commit(body.playbook, overwrite=body.overwrite)
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:  # noqa: BLE001
        log.error("import.commit_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Could not write the playbook: {e}")
