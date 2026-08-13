"""
Pipelines API endpoints.

A "pipeline" is a derived view: it groups deployed playbooks by industry
and exposes each playbook's actions as ordered stages. There is no separate
DynamoDB table — pipelines are computed on the fly from existing playbooks.
"""

from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from services.dynamodb import DynamoDBService
from core.config import settings

router = APIRouter()
db = DynamoDBService(settings.DYNAMODB_PLAYBOOKS)

# Map action names → visual stage kind used by the UI's `tag-*` classes.
_STAGE_KIND_KEYWORDS = {
    "extract":  ["extract", "ocr", "parse", "read"],
    "validate": ["validate", "verify", "check", "match"],
    "classify": ["classify", "route", "categorize", "triage", "tag"],
    "store":    ["store", "save", "persist", "write", "dynamo", "s3"],
    "notify":   ["notify", "alert", "email", "slack", "webhook"],
    "execute":  ["execute", "approve", "run", "post", "submit"],
}


def _stage_kind_for(name: str) -> str:
    n = (name or "").lower()
    for kind, keywords in _STAGE_KIND_KEYWORDS.items():
        if any(k in n for k in keywords):
            return kind
    return "execute"


class PipelineStage(BaseModel):
    """A single stage in a pipeline."""
    name: str
    kind: str = Field(..., description="Visual stage type: extract|validate|classify|store|notify|execute|route")


class Pipeline(BaseModel):
    """A pipeline = a playbook rendered as an ordered chain of stages."""
    id: str
    name: str
    description: str = ""
    industry: str = "general"
    status: str = "draft"
    stages: List[PipelineStage] = []
    action_count: int = 0
    last_run: Optional[str] = None


def _playbook_to_pipeline(pb: Dict[str, Any]) -> Pipeline:
    actions = pb.get("actions") or []
    stages: List[PipelineStage] = []
    for action in actions:
        name = action.get("name") or action.get("action_id") or action.get("handler") or "action"
        stages.append(PipelineStage(name=name, kind=_stage_kind_for(name)))

    return Pipeline(
        id=pb.get("playbook_id") or pb.get("id") or "",
        name=pb.get("name") or "Unnamed",
        description=pb.get("description") or pb.get("intent", "")[:140],
        industry=pb.get("industry") or "general",
        status=pb.get("status") or "draft",
        stages=stages,
        action_count=len(actions),
        last_run=pb.get("last_run"),
    )


@router.get("/", response_model=List[Pipeline])
async def list_pipelines(
    industry: Optional[str] = Query(None, description="Filter by industry"),
    limit: int = Query(100, le=500),
):
    """List all pipelines (derived from playbooks)."""
    filters = {}
    if industry:
        filters["industry"] = industry
    items = await db.scan(filters=filters, limit=limit)
    return [_playbook_to_pipeline(pb) for pb in items]


# ──────────────────────────────────────────────────────────────────────
# STP Phase 2 — rich pipeline detail endpoint
# (Must be defined BEFORE the /{pipeline_id} wildcard route so the literal
# `details` segment isn't swallowed by the path param.)
# ──────────────────────────────────────────────────────────────────────

from services.dynamodb import DynamoDBService as _DDB_DETAILS
from core.config import settings as _settings_DETAILS

_pipelines_detail_db_v2 = _DDB_DETAILS(_settings_DETAILS.DYNAMODB_PIPELINES)


@router.get("/details")
async def list_pipeline_details_v2(
    industry: Optional[str] = Query(None, description="Filter by industry key (e.g. 'nuclear_operations')"),
    limit:    int            = Query(100, le=500),
):
    """Rich pipeline rows with stages, stats, throughput.

    Reads from `apex-ai-platform-pipelines` directly — no Pydantic coercion,
    frontend gets the raw shape it expects. Filterable by industry.
    """
    filters = {"industry": industry} if industry else {}
    items = await _pipelines_detail_db_v2.scan(filters=filters, limit=limit)
    out = []
    for it in items:
        out.append({
            "id":             it.get("pipeline_id") or it.get("id"),
            "name":           it.get("name"),
            "industry":       it.get("industry"),
            "industry_label": it.get("industry_label"),
            "throughput":     it.get("throughput", ""),
            "status":         it.get("status", "Active"),
            "playbook_id":    it.get("playbook_id"),
            "stages":         it.get("stages", []),
            "stats":          it.get("stats", {}),
        })
    return {"items": out, "count": len(out)}


@router.get("/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(pipeline_id: str):
    """Get a single pipeline by underlying playbook ID."""
    item = await db.get_item({"playbook_id": pipeline_id})
    if not item:
        from fastapi import HTTPException, status as http_status
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline {pipeline_id} not found",
        )
    return _playbook_to_pipeline(item)


# ════════════════════════════════════════════════════════════════════════════
# Killer Feature 3 — Workflow Debt Eliminator / Value Map
# ════════════════════════════════════════════════════════════════════════════

class ValueMapRow(BaseModel):
    metric: str
    legacy: str
    apex:   str
    saving: str


class ValueMap(BaseModel):
    pipeline_id: str
    headline:   str
    rows:       List[ValueMapRow]
    narrative:  str


# Front-end Pipelines page hard-codes pipeline IDs (`pipe-*`) that do not
# match the DynamoDB playbook keys (`pb-*`). The seeder patches the value_map
# blob onto the `pb-cbb-*` playbook rows, so we alias the 3 CBB pipelines
# here. Non-CBB pipelines fall through to the synthesis branch below.
PIPELINE_TO_PLAYBOOK: Dict[str, str] = {
    "pipe-cbb-order-mod":  "pb-cbb-1",
    "pipe-cbb-qc":         "pb-cbb-2",
    "pipe-cbb-disruption": "pb-cbb-3",
}


def _synthesize_value_map(pipeline_id: str, name: Optional[str], stages: int) -> ValueMap:
    """Proportional before/after derived from stage count.

    `stages` is clamped by the endpoint (ge=0, le=50); apex-side math uses
    max(1, stages) so a zero-stage pipeline still renders sensibly.
    """
    apex_stages = max(1, stages)
    legacy_steps = apex_stages + 3
    label = (name or pipeline_id).strip() or pipeline_id
    return ValueMap(
        pipeline_id=pipeline_id,
        headline=f"{legacy_steps * 2}h → {apex_stages * 4}s",
        rows=[
            ValueMapRow(metric="Steps",              legacy=f"{legacy_steps} steps",                        apex="1 trigger · 1 agent",   saving=f"−{legacy_steps - 1} steps"),
            ValueMapRow(metric="System Handoffs",    legacy=f"{max(2, apex_stages // 2)}",                  apex="0",                     saving="full consolidation"),
            ValueMapRow(metric="Time to Resolution", legacy=f"{max(2, apex_stages)} hrs manual",            apex=f"{apex_stages * 4} sec", saving="100–1000× faster"),
            ValueMapRow(metric="Human Touchpoints",  legacy=f"{max(1, apex_stages // 2)} people",           apex="0 (Fully Autonomous)",  saving="fully autonomous"),
        ],
        narrative=(
            f"Legacy '{label}' required hand-offs between email, ERP, spreadsheets, "
            "and approvers. Apex compresses the same work into a single agent run "
            "with a full audit trail."
        ),
    )


@router.get("/{pipeline_id}/value-map", response_model=ValueMap)
async def get_pipeline_value_map(
    pipeline_id: str,
    name:   Optional[str] = Query(None, max_length=120, description="Pipeline display name — used by the synthesis fallback."),
    stages: int           = Query(1, ge=0, le=50,        description="Stage count — used by the synthesis fallback."),
):
    """Return the Before-vs-After comparison for a pipeline.

    Lookup order:
      1. Direct DynamoDB playbook row keyed by `pipeline_id`.
      2. Alias map (`PIPELINE_TO_PLAYBOOK`) for the 3 CBB demo pipelines whose
         UI ids don't match the seeded playbook ids.
      3. If the resolved playbook has a `value_map` blob, return it.
      4. Otherwise synthesise from the caller-supplied `name` + `stages`.

    Never raises 404 — an unknown pipeline falls straight through to synthesis
    so the Value Map view is always useful, even offline or for ad-hoc
    pipelines the UI keeps in local state.
    """
    pb = None
    try:
        pb = await db.get_item({"playbook_id": pipeline_id})
        if not pb and pipeline_id in PIPELINE_TO_PLAYBOOK:
            pb = await db.get_item({"playbook_id": PIPELINE_TO_PLAYBOOK[pipeline_id]})
    except Exception:
        # Infra issue (DynamoDB down, network, credential) — don't dead-end
        # the UI; fall through to synthesis. Logging is handled upstream by
        # the DynamoDBService wrapper which logs on each failure.
        pb = None

    if pb:
        vm = pb.get("value_map")
        if isinstance(vm, dict) and vm.get("rows"):
            return ValueMap(
                pipeline_id=pipeline_id,
                headline=vm.get("headline") or "Workflow debt eliminated",
                rows=[ValueMapRow(**r) for r in vm["rows"]],
                narrative=vm.get("narrative") or "",
            )
        # Playbook exists but has no value_map — synthesise using the
        # playbook's own action count + name (better than query params).
        actions = pb.get("actions") or []
        return _synthesize_value_map(
            pipeline_id=pipeline_id,
            name=pb.get("name") or name,
            stages=len(actions) or stages,
        )

    # No playbook row found (e.g. pipe-invoice / pipe-rfp / user's ad-hoc
    # pipelines) — synthesise from the query params the frontend sent.
    return _synthesize_value_map(pipeline_id=pipeline_id, name=name, stages=stages)
