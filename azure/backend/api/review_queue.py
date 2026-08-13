"""
Human Review Queue API.

Backed by the `apex-ai-platform-review-queue` Cosmos DB table seeded via
`scripts/seed_stp_demo.py`. Drives the /review page in the UI — every
item shown there now comes from a real API rather than a hardcoded array
in the .tsx file.

Endpoints:
  GET /api/v1/review-queue/        — list items, optionally filtered by industry
  GET /api/v1/review-queue/{id}    — fetch one item
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from core.config import settings
from services.cosmos import CosmosService

router = APIRouter()
_db = CosmosService(settings.TABLE_REVIEW_QUEUE)


@router.get("/")
async def list_review_items(
    industry: Optional[str] = Query(None, description="Filter by industry key"),
    state:    Optional[str] = Query(None, description="Filter by state (pending | approved | rejected | escalated)"),
    limit:    int           = Query(100, le=500),
) -> Dict[str, Any]:
    """List review queue items, optionally filtered."""
    filters: Dict[str, str] = {}
    if industry:
        filters["industry"] = industry
    if state:
        filters["state"] = state
    items = await _db.scan(filters=filters, limit=limit)
    # Frontend expects a stable shape — minor normalisation here.
    out: List[Dict[str, Any]] = []
    for it in items:
        out.append({
            "id":             it.get("review_id") or it.get("id"),
            "industry":       it.get("industry"),
            "priority":       it.get("priority", "NORMAL"),
            "title":          it.get("title", ""),
            "source":         it.get("source", ""),
            "submitted_at":   it.get("submitted_at"),
            "playbook":       it.get("playbook_name") or it.get("playbook", ""),
            "playbook_id":    it.get("playbook_id"),
            "amount":         it.get("amount", ""),
            "amount_label":   it.get("amount_label", ""),
            "issues":         it.get("issues", []),
            "reason_tone":    it.get("reason_tone", "slate"),
            "extracted":      it.get("extracted", []),
            "document_name":  it.get("document_name", ""),
            "doc_key":        it.get("doc_key"),
            "next_on_approve":   it.get("next_on_approve"),
            "next_on_reject":    it.get("next_on_reject"),
            "next_on_escalate":  it.get("next_on_escalate"),
            "state":          it.get("state", "pending"),
            "decided_at":     it.get("decided_at"),
            "decided_by":     it.get("decided_by"),
            "comment":        it.get("comment"),
        })
    return {"items": out, "count": len(out)}


@router.get("/{review_id}")
async def get_review_item(review_id: str) -> Dict[str, Any]:
    """Fetch a single review item by id."""
    item = await _db.get_item({"review_id": review_id})
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review item {review_id} not found",
        )
    return item
