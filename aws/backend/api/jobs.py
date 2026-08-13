"""
Jobs API — create, duplicate, schedule and execute work against real hardware.

    GET    /jobs                  list jobs
    POST   /jobs                  create
    GET    /jobs/{id}             one job with its recent runs
    PATCH  /jobs/{id}             rename / retarget / reschedule / enable
    POST   /jobs/{id}/duplicate   clone, optionally onto other servers
    DELETE /jobs/{id}             remove
    POST   /jobs/{id}/run         execute now
    GET    /jobs/{id}/runs        run history
    GET    /jobs/meta/options     playbooks + servers + schedules for the create form
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.jobs import (
    PLAYBOOK_SPECS,
    SCHEDULE_LABEL,
    SCHEDULES,
    JobStore,
    build_job,
    duplicate_job,
    enrich,
    execute_job,
    resolve_endpoints,
)
from services.redfish import InventoryData

log = structlog.get_logger()
router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# models
# ─────────────────────────────────────────────────────────────────────────────

class CreateJob(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    playbook_id: str = Field(..., min_length=1)
    targets: List[str] = Field(default_factory=list)
    schedule: str = "manual"
    description: str = ""


class PatchJob(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    targets: Optional[List[str]] = None
    schedule: Optional[str] = None
    enabled: Optional[bool] = None


class DuplicateJob(BaseModel):
    name: Optional[str] = None
    targets: Optional[List[str]] = None
    schedule: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/")
async def list_jobs() -> Dict[str, Any]:
    """All jobs, newest first. Malformed rows are skipped, not fatal."""
    rows: List[Dict[str, Any]] = []
    for job in JobStore.list_jobs():
        try:
            rows.append(enrich(job))
        except Exception as e:  # noqa: BLE001
            log.warning("jobs.row_skipped", job=job.get("id"), error=str(e))
    rows.sort(key=lambda j: j.get("created_at") or "", reverse=True)
    return {"jobs": rows, "count": len(rows)}


@router.get("/meta/options")
async def options() -> Dict[str, Any]:
    """Everything the create form needs: targets, playbooks, schedules."""
    servers = [
        {
            "id": s.get("id"),
            "hostname": s.get("hostname"),
            "platform": s.get("platform"),
            "vendor": s.get("vendor"),
            "status": s.get("status"),
        }
        for s in InventoryData.servers()
    ]

    # Playbooks that can run against hardware, described by what each one
    # actually changes about a run — endpoints walked, report, ticketing.
    playbooks = []
    for pid, spec in PLAYBOOK_SPECS.items():
        endpoints = resolve_endpoints(pid)
        playbooks.append({
            "id": pid,
            "name": spec["label"],
            "description": spec["summary"],
            "endpoint_count": "all" if endpoints is None else len(endpoints),
            "endpoints": endpoints,
            "emits_report": spec["emits_report"],
            "raises_tickets": spec["raises_tickets"],
        })

    return {
        "servers": servers,
        "playbooks": playbooks,
        "schedules": [{"value": s, "label": SCHEDULE_LABEL[s]} for s in SCHEDULES],
    }


@router.post("/")
async def create_job(body: CreateJob) -> Dict[str, Any]:
    """Create a job. Targets must exist in the inventory."""
    unknown = [t for t in body.targets if InventoryData.server(t) is None]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown server(s): {', '.join(unknown)}")

    try:
        job = build_job(
            name=body.name,
            playbook_id=body.playbook_id,
            targets=body.targets,
            schedule=body.schedule,
            description=body.description,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    JobStore.create(job)
    log.info("jobs.created", job=job["id"], targets=len(job["targets"]))
    return enrich(job)


@router.get("/{job_id}")
async def get_job(job_id: str) -> Dict[str, Any]:
    job = JobStore.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    out = enrich(job)
    out["runs"] = JobStore.runs_for(job_id)
    return out


@router.patch("/{job_id}")
async def patch_job(job_id: str, body: PatchJob) -> Dict[str, Any]:
    if JobStore.get_job(job_id) is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    if body.schedule is not None and body.schedule not in SCHEDULES:
        raise HTTPException(status_code=400, detail=f"schedule must be one of {SCHEDULES}")

    if body.targets is not None:
        unknown = [t for t in body.targets if InventoryData.server(t) is None]
        if unknown:
            raise HTTPException(status_code=400, detail=f"Unknown server(s): {', '.join(unknown)}")

    patch = body.model_dump(exclude_unset=True)
    if body.schedule is not None:
        patch["schedule_label"] = SCHEDULE_LABEL[body.schedule]

    updated = JobStore.update(job_id, patch)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return enrich(updated)


@router.post("/{job_id}/duplicate")
async def duplicate(job_id: str, body: Optional[DuplicateJob] = None) -> Dict[str, Any]:
    """Clone a job — the usual way a proven job is rolled onto more servers."""
    source = JobStore.get_job(job_id)
    if source is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    body = body or DuplicateJob()
    if body.targets is not None:
        unknown = [t for t in body.targets if InventoryData.server(t) is None]
        if unknown:
            raise HTTPException(status_code=400, detail=f"Unknown server(s): {', '.join(unknown)}")

    try:
        clone = duplicate_job(source, name=body.name, targets=body.targets, schedule=body.schedule)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    JobStore.create(clone)
    log.info("jobs.duplicated", source=job_id, clone=clone["id"])
    return enrich(clone)


@router.delete("/{job_id}")
async def delete_job(job_id: str) -> Dict[str, Any]:
    if not JobStore.delete(job_id):
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    return {"deleted": job_id}


@router.post("/{job_id}/run")
async def run_job(job_id: str) -> Dict[str, Any]:
    """Execute now, regardless of schedule."""
    job = JobStore.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    if not job.get("targets"):
        raise HTTPException(status_code=400, detail="Job has no targets")

    run = execute_job(job)
    log.info("jobs.ran", job=job_id, status=run["status"], targets=run["target_count"])
    return run


@router.get("/{job_id}/runs")
async def job_runs(job_id: str, limit: int = 20) -> Dict[str, Any]:
    if JobStore.get_job(job_id) is None:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    runs = JobStore.runs_for(job_id, limit=limit)
    return {"job_id": job_id, "runs": runs, "count": len(runs)}


# ─────────────────────────────────────────────────────────────────────────────
# Jira write-back — preview, then approve
# ─────────────────────────────────────────────────────────────────────────────

SEVERITY_FOR = {"FAIL": "S2", "DRIFT": "S3", "WARN": "S4"}


def _issues_for_run(run: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compose one issue per finding.

    Built identically for preview and for creation, so what an approver reads
    is exactly what gets written — the preview cannot drift from the action.
    """
    issues: List[Dict[str, Any]] = []
    for target in run.get("targets", []):
        host = target.get("hostname") or target.get("server_id")
        for f in target.get("findings", []):
            gap = f.get("gap") or {}
            issues.append({
                "summary": f"{f['step']} — {host}",
                "severity": SEVERITY_FOR.get(f["result"], "S4"),
                "category": f.get("category") or "configuration",
                "server_id": target.get("server_id"),
                "hostname": host,
                "bmc_ip": target.get("bmc_ip"),
                "result": f["result"],
                "root_cause": f.get("detail") or "",
                "recommendation": gap.get("action") or "",
                "description": "",
            })
    return issues


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> Dict[str, Any]:
    run = JobStore.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return run


@router.get("/runs/{run_id}/report")
async def certification_report(run_id: str) -> Dict[str, Any]:
    """
    The run rendered into the `certification_report` blueprint.

    The blueprint — not this endpoint — owns the document's shape, so the
    response also reports whether it conformed and what it could not populate.
    """
    run = JobStore.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    if not run.get("emits_report", False):
        raise HTTPException(
            status_code=409,
            detail=(f"The '{run.get('playbook_label') or run.get('playbook_id')}' playbook "
                    f"does not emit a certification report."),
        )

    from services.certification_report import build_report
    return build_report(run)


@router.get("/runs/{run_id}/jira/preview")
async def jira_preview(run_id: str) -> Dict[str, Any]:
    """
    Exactly what would be written to Jira — shown before anything is created.

    Nothing is raised by this call. It is the approval gate.
    """
    run = JobStore.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    try:
        from services.jira_client import get_client
        config = get_client().config.public()
    except Exception as e:  # noqa: BLE001 — preview must work even unconfigured
        log.warning("jobs.jira_config_unavailable", error=str(e))
        config = {"mock_mode": True, "mock_reason": str(e), "project_key": "APEXVZ"}

    issues = _issues_for_run(run)
    return {
        "run_id": run_id,
        "job_name": run.get("job_name"),
        "count": len(issues),
        "issues": issues,
        "jira": config,
        "already_created": run.get("jira_tickets") or [],
    }


@router.post("/runs/{run_id}/jira/create")
async def jira_create(run_id: str) -> Dict[str, Any]:
    """
    Create the previewed issues. Call only after an operator has approved.

    Re-running is refused once tickets exist for the run, so an accidental
    second approval cannot duplicate a whole backlog.
    """
    run = JobStore.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")

    if not run.get("raises_tickets", True):
        raise HTTPException(
            status_code=409,
            detail=(f"The '{run.get('playbook_label') or run.get('playbook_id')}' playbook "
                    f"reports findings for scoring and does not raise tickets."),
        )

    if run.get("jira_tickets"):
        keys = [str(t.get("key") or "?") for t in run["jira_tickets"]]
        raise HTTPException(
            status_code=409,
            detail=f"Tickets already raised for this run: {', '.join(keys)}",
        )

    issues = _issues_for_run(run)
    if not issues:
        raise HTTPException(status_code=400, detail="Run has no findings to raise")

    from actions.core.jira_create_ticket.handler import jira_create_ticket

    created: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []
    for issue in issues:
        try:
            ticket = jira_create_ticket(
                summary=issue["summary"],
                severity=issue["severity"],
                category=issue["category"],
                root_cause=issue["root_cause"],
                recommendation=issue["recommendation"],
                cycle_id=run_id,
            )
            if ticket.get("status") == "error":
                failed.append({"summary": issue["summary"], "error": ticket.get("error")})
            else:
                # The handler names these `ticket_key` / `ticket_url`.
                created.append({
                    "key": ticket.get("ticket_key"),
                    "url": ticket.get("ticket_url"),
                    "mock": ticket.get("mock", False),
                    "summary": issue["summary"],
                    "hostname": issue["hostname"],
                })
        except Exception as e:  # noqa: BLE001 — one bad issue must not abort the rest
            log.warning("jobs.jira_create_failed", summary=issue["summary"], error=str(e))
            failed.append({"summary": issue["summary"], "error": str(e)})

    JobStore.annotate_run(run_id, {"jira_tickets": created, "jira_failed": failed})
    log.info("jobs.jira_created", run=run_id, created=len(created), failed=len(failed))

    return {"run_id": run_id, "created": created, "failed": failed, "count": len(created)}
