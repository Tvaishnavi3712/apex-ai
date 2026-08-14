"""
Telecommunications certification cycle orchestrator + SSE progress streaming.

Endpoint:
  POST /api/v1/telecommunications/cycle-start
    Body:  multipart/form-data  file=<ROBOT XML>
    Returns: text/event-stream with progress frames + final result.

Pipeline (pb-tel-1 — Full Certification Cycle):
  Stage 1  EXTRACT   parse_robot_output              ~250 ms
  Stage 2  CLASSIFY  classify_failures              ~120 ms
  Stage 3  VALIDATE  detect_schema_drift            ~180 ms
  Stage 4  ROUTE     jira_create_ticket × N         ~300 ms × N (or mock instant)
  Stage 5  NOTIFY    certification_report           ~80 ms

Each stage emits one or more SSE frames:
  event: stage_start    data: {stage_id, label, started_at}
  event: stage_done     data: {stage_id, ms, summary, output_keys[]}
  event: ticket_created data: {key, url, mock, summary, severity}
  event: cycle_done     data: {cycle_id, jira_url_list, hours_saved, audit_lens_event_id}
  event: error          data: {stage_id, error_message}

Two entry points hit this orchestrator:
  - Path A: UI uploads multipart XML
  - Path B: Lambda (S3 PutObject trigger) POSTs the S3 object key —
           orchestrator pulls the file from S3 and runs the same pipeline.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, AsyncGenerator, Deque, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

# Make actions/ importable when this module is loaded by uvicorn.
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from actions.telecommunications.parse_robot_output.handler import parse_robot_output     # noqa: E402
from actions.telecommunications.classify_failures.handler import classify_failures        # noqa: E402
from actions.telecommunications.detect_schema_drift.handler import detect_schema_drift    # noqa: E402
from actions.core.jira_create_ticket.handler import jira_create_ticket                    # noqa: E402

router = APIRouter()
log = logging.getLogger(__name__)


# ─────────────────────────── cycle history (in-memory) ───────────────────────────
# Ring buffer of the last 50 completed cycles. Used by:
#   • Pipelines page → updates pipe-tel-certification.lastRun
#   • Playbook detail page → fills pb-tel-1.runs[] with real recent runs
#
# In-memory (process-lifetime). Survives backend restart? No — but for a
# 12-15 minute demo that's fine. To persist across restarts, swap to
# Cosmos DB write at the end of _record_cycle.
_CYCLE_HISTORY: Deque[Dict[str, Any]] = deque(maxlen=50)
_history_lock = asyncio.Lock()


async def _record_cycle(record: Dict[str, Any]) -> None:
    """Append a completed cycle to the in-memory history buffer."""
    async with _history_lock:
        _CYCLE_HISTORY.appendleft(record)
        log.info("Recorded cycle %s in history (buffer size: %d)",
                 record.get("cycle_id"), len(_CYCLE_HISTORY))


# ─────────────────────────── HITL (Human-In-The-Loop) ───────────────────────────
# When the pipeline hits a high-risk condition, it pauses on an asyncio.Event
# and emits an `hitl_required` SSE frame so the UI can render an approve/reject
# banner. The same pending request is also exposed via GET /hitl/pending so the
# Command Center HITL queue can show it (especially useful for Path B where
# the SSE caller has already disconnected).
#
# When the user clicks Approve or Reject, POST /hitl/{id}/{decision} records
# the decision and sets the event — the pipeline wakes up and either proceeds
# (approve) or halts (reject). Every decision is logged to cycle history with
# reviewer + timestamp.
#
# Timeout: pipeline waits up to 10 minutes for a human decision; after that
# the cycle is auto-rejected and halts.

_PENDING_HITL:   Dict[str, Dict[str, Any]] = {}
_HITL_EVENTS:    Dict[str, asyncio.Event] = {}
_HITL_DECISIONS: Dict[str, Dict[str, Any]] = {}
_HITL_LOCK = asyncio.Lock()
_HITL_TIMEOUT_SEC = 600   # 10 min before auto-reject


def _new_hitl_request(*, cycle_id: str, agent: str, gate: str, severity: str,
                       reason: str, data: Dict[str, Any]) -> str:
    """Create a new HITL request, store it, and return the request_id.
    Caller is responsible for awaiting _HITL_EVENTS[request_id] and emitting
    the SSE frame."""
    request_id = f"HITL-{cycle_id}-{gate.upper()}"
    _PENDING_HITL[request_id] = {
        "request_id":  request_id,
        "cycle_id":    cycle_id,
        "agent":       agent,
        "gate":        gate,        # 'classify' | 'drift' | 'wave-auth' | etc.
        "severity":    severity,    # 'high' | 'medium' | 'low'
        "reason":      reason,
        "data":        data,
        "created_at":  _now_ms(),
        "status":      "pending",
    }
    _HITL_EVENTS[request_id] = asyncio.Event()
    log.info("HITL request created: %s · %s · agent=%s · gate=%s",
             request_id, severity, agent, gate)
    return request_id


async def _wait_for_hitl(request_id: str) -> Dict[str, Any]:
    """Block until the request is decided (or timeout). Returns the decision
    record. Cleans up state on the way out."""
    event = _HITL_EVENTS.get(request_id)
    if event is None:
        return {"decision": "missing", "reason": "no event registered"}
    try:
        await asyncio.wait_for(event.wait(), timeout=_HITL_TIMEOUT_SEC)
        decision = _HITL_DECISIONS.get(request_id, {"decision": "missing"})
        log.info("HITL %s resolved: %s by %s",
                 request_id, decision.get("decision"), decision.get("reviewer"))
    except asyncio.TimeoutError:
        decision = {
            "decision":   "timeout",
            "reviewer":   "system",
            "decided_at": _now_ms(),
            "reason":     f"no human decision within {_HITL_TIMEOUT_SEC}s",
        }
        log.warning("HITL %s timed out — auto-reject", request_id)
    finally:
        # Mark request as resolved but keep it in PENDING for ~5s so the
        # UI shows the resolution before it disappears, then clean up.
        pending = _PENDING_HITL.get(request_id)
        if pending is not None:
            pending["status"]   = decision.get("decision", "unknown")
            pending["resolved_at"] = _now_ms()
            pending["reviewer"]    = decision.get("reviewer", "system")
        # Defer cleanup so the resolved chip stays visible briefly
        asyncio.get_event_loop().call_later(8.0, _cleanup_hitl, request_id)
    return decision


def _cleanup_hitl(request_id: str) -> None:
    _PENDING_HITL.pop(request_id, None)
    _HITL_EVENTS.pop(request_id, None)
    _HITL_DECISIONS.pop(request_id, None)


# ──────────────────────────── helpers ────────────────────────────

def _sse(event: str, data: Dict[str, Any]) -> str:
    """Encode a Server-Sent Event frame. Use compact JSON — newlines in
    data would split the frame in the wire format."""
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _stage_done_summary(out: Dict[str, Any], stage_id: str) -> str:
    """One-line human-readable summary surfaced in the UI."""
    if stage_id == "parse":
        return (
            f"{out.get('total_tests', 0)} tests parsed "
            f"({out.get('passed_tests', 0)} pass · "
            f"{out.get('failed_tests', 0)} fail · "
            f"{out.get('warn_tests', 0)} warn)"
        )
    if stage_id == "classify":
        p1 = out.get("p1_count", 0)
        p2 = out.get("p2_count", 0)
        p3 = out.get("p3_count", 0)
        return f"P1={p1} · P2={p2} · P3={p3} · recommendation: {out.get('deployment_recommendation','?')}"
    if stage_id == "drift":
        bc = out.get("breaking_changes_count", 0)
        sc = out.get("scripts_impacted_count", 0)
        return f"{bc} breaking change(s) · {sc} script(s) impacted"
    if stage_id == "jira":
        n  = out.get("tickets_opened", 0)
        mk = out.get("mock_count", 0)
        return f"{n} JIRA ticket(s) opened{(' (mock)' if mk == n and n > 0 else '')}"
    if stage_id == "report":
        return f"Certification report emitted · cycle {out.get('cycle_id', '—')}"
    return ""


# ──────────────────────────── orchestrator ────────────────────────────

async def _run_pipeline(xml_path: str, cycle_id: str,
                         trigger: str = "ui_upload",
                         source_label: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Run the 5 stages and yield SSE frames as they happen.

    trigger: 'ui_upload' (Path A) | 's3_event' (Path B) — recorded in
             cycle history so the UI can distinguish where each cycle came from.
    source_label: human-readable filename or s3 key (defaults to xml_path).
    """
    pipeline_started_at = _now_ms()
    yield _sse("cycle_start", {"cycle_id": cycle_id, "xml_path": str(xml_path),
                                "started_at": pipeline_started_at,
                                "trigger": trigger})

    # ─── Stage 1 · parse_robot_output ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "parse", "label": "Parse ROBOT XML",
                                "started_at": t0})
    try:
        parsed = parse_robot_output(file_path=xml_path)
    except Exception as e:
        log.exception("parse_robot_output failed")
        yield _sse("error", {"stage_id": "parse", "error_message": str(e)})
        return
    elapsed = _now_ms() - t0
    yield _sse("stage_done", {"stage_id": "parse", "ms": elapsed,
                               "summary": _stage_done_summary(parsed, "parse"),
                               "output_keys": list(parsed.keys())})

    # ─── Stage 2 · classify_failures ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "classify", "label": "Classify Failures",
                                "started_at": t0})
    try:
        classified = classify_failures(parsed.get("test_results", []))
    except Exception as e:
        log.exception("classify_failures failed")
        yield _sse("error", {"stage_id": "classify", "error_message": str(e)})
        return
    elapsed = _now_ms() - t0
    yield _sse("stage_done", {"stage_id": "classify", "ms": elapsed,
                               "summary": _stage_done_summary(classified, "classify"),
                               "output_keys": list(classified.keys())})

    # ─── Stage 3 · detect_schema_drift ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "drift", "label": "Schema Drift Check",
                                "started_at": t0})
    try:
        drift = detect_schema_drift()
    except Exception as e:
        log.exception("detect_schema_drift failed")
        yield _sse("error", {"stage_id": "drift", "error_message": str(e)})
        return
    elapsed = _now_ms() - t0
    yield _sse("stage_done", {"stage_id": "drift", "ms": elapsed,
                               "summary": _stage_done_summary(drift, "drift"),
                               "output_keys": list(drift.keys())})

    # ─── HITL Gate · CertificationAgent ────────────────────────────────────
    # Pause the pipeline for human approval when the cycle is high-risk:
    #   • > 10 failures (default threshold; matches the v2412 demo cycle)
    #   • OR any schema drift breaking change detected
    # The reviewer must approve to proceed (writes JIRA tickets + emits the
    # cert report) or reject (halts the cycle cleanly with no writes).
    failures: List[Dict[str, Any]] = classified.get("classified_failures", [])
    fail_count       = int(classified.get("fail_count", 0))
    p1_count         = int(classified.get("p1_count", 0))
    breaking_changes = int(drift.get("breaking_changes_count", 0))
    scripts_impacted = int(drift.get("scripts_impacted_count", 0))
    needs_hitl       = (fail_count > 10) or (breaking_changes > 0)

    if needs_hitl:
        reasons = []
        if fail_count > 10:
            reasons.append(f"{fail_count} failures ({p1_count} P1)")
        if breaking_changes > 0:
            reasons.append(f"{breaking_changes} breaking schema change(s) impacting {scripts_impacted} script(s)")
        gate_severity = "high" if (p1_count > 5 or breaking_changes > 1) else "medium"
        reason_str = " · ".join(reasons) + ". CertificationAgent recommends HOLD pending human review."

        request_id = _new_hitl_request(
            cycle_id=cycle_id,
            agent="CertificationAgent",
            gate="cert-cycle",
            severity=gate_severity,
            reason=reason_str,
            data={
                "fail_count":        fail_count,
                "p1_count":          p1_count,
                "p2_count":          classified.get("p2_count", 0),
                "p3_count":          classified.get("p3_count", 0),
                "breaking_changes":  breaking_changes,
                "scripts_impacted":  scripts_impacted,
                "device":            parsed.get("device_under_test"),
                "firmware":          parsed.get("firmware_version"),
                "tickets_proposed":  len(failures),
            },
        )
        yield _sse("hitl_required", {
            "request_id": request_id,
            "cycle_id":   cycle_id,
            "agent":      "CertificationAgent",
            "gate":       "cert-cycle",
            "severity":   gate_severity,
            "reason":     reason_str,
            "proposed_action": f"Open {len(failures)} JIRA tickets + emit certification report (HOLD recommendation).",
        })

        decision = await _wait_for_hitl(request_id)
        yield _sse("hitl_decided", {
            "request_id":  request_id,
            "decision":    decision.get("decision"),
            "reviewer":    decision.get("reviewer"),
            "comment":     decision.get("comment", ""),
            "decided_at":  decision.get("decided_at"),
        })

        if decision.get("decision") != "approve":
            # Rejected or timed out — halt the pipeline cleanly.
            yield _sse("cycle_halted", {
                "cycle_id":  cycle_id,
                "reason":    f"halted by HITL: {decision.get('decision')} ({decision.get('reviewer','—')})",
                "ended_at":  _now_ms(),
            })
            # Record an aborted cycle so it shows up in history.
            await _record_cycle({
                "cycle_id":      cycle_id,
                "started_at":    pipeline_started_at,
                "ended_at":      _now_ms(),
                "duration_ms":   _now_ms() - pipeline_started_at,
                "trigger":       trigger,
                "source":        source_label or str(xml_path),
                "device":        parsed.get("device_under_test"),
                "firmware":      parsed.get("firmware_version"),
                "total":         parsed.get("total_tests"),
                "passed":        parsed.get("passed_tests"),
                "failed":        parsed.get("failed_tests"),
                "warn":          parsed.get("warn_tests"),
                "p1": p1_count, "p2": classified.get("p2_count", 0), "p3": classified.get("p3_count", 0),
                "status":        f"HALTED — HITL {decision.get('decision','?')}",
                "tickets_count": 0,
                "jira_urls":     [], "jira_keys": [],
                "all_mock":      True,
                "hitl_decision": decision,
            })
            return

    # ─── Stage 4 · jira_create_ticket × N (every classified failure) ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "jira", "label": f"Open JIRA Tickets ({len(failures)})",
                                "started_at": t0, "expected_count": len(failures)})

    tickets: List[Dict[str, Any]] = []
    mock_count = 0
    for i, f in enumerate(failures):
        # classify_failures emits {test_id, name, library, redfish_endpoint,
        # failure_message, category, severity, kb_*, recommendation}.
        # Compose the JIRA summary from the test name + failure message so
        # mock keys don't collide on empty strings.
        composed_summary = (
            f.get("summary")
            or (f.get("name") and f.get("failure_message")
                and f"{f['name']} — {f['failure_message']}")
            or f.get("name")
            or f.get("failure_message")
            or "Untitled failure"
        )
        ticket = jira_create_ticket(
            summary          = composed_summary,
            severity         = f.get("severity"),
            category         = f.get("category"),
            test_case_id     = f.get("test_id") or f.get("test_case_id"),
            redfish_endpoint = f.get("redfish_endpoint"),
            root_cause       = f.get("root_cause") or f.get("failure_message"),
            recommendation   = f.get("recommendation"),
            kb_match         = f.get("kb_match"),
            cycle_id         = cycle_id,
        )
        tickets.append({
            "summary":     composed_summary,
            "severity":    f.get("severity"),
            "category":    f.get("category"),
            "key":         ticket.get("ticket_key"),
            "url":         ticket.get("ticket_url"),
            "mock":        ticket.get("mock", False),
            "status":      ticket.get("status"),
            "error":       ticket.get("error"),
        })
        if ticket.get("mock"):
            mock_count += 1
        # Stream incremental ticket frames so the UI can render them as
        # they're created (rather than waiting for the whole batch).
        yield _sse("ticket_created", {
            "i":        i + 1,
            "of":       len(failures),
            "key":      ticket.get("ticket_key"),
            "url":      ticket.get("ticket_url"),
            "mock":     ticket.get("mock", False),
            "summary":  composed_summary,
            "severity": f.get("severity"),
            "category": f.get("category"),
        })
        # Tiny pause so live JIRA stays well under the 250 req/min limit.
        # In mock mode this is fine too — keeps the streaming feel alive.
        await asyncio.sleep(0.10)

    elapsed = _now_ms() - t0
    yield _sse("stage_done", {"stage_id": "jira", "ms": elapsed,
                               "summary": _stage_done_summary({
                                   "tickets_opened": len(tickets),
                                   "mock_count":     mock_count,
                               }, "jira"),
                               "output_keys": ["tickets"]})

    # ─── Stage 5 · certification_report (synthesis) ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "report", "label": "Emit Certification Report",
                                "started_at": t0})
    report = {
        "report_id":                    f"CERT-{cycle_id}",
        "cycle_id":                     cycle_id,
        "device_under_test":            parsed.get("device_under_test"),
        "firmware_version":             parsed.get("firmware_version"),
        "total_tests":                  parsed.get("total_tests"),
        "pass_count":                   parsed.get("passed_tests"),
        "fail_count":                   parsed.get("failed_tests"),
        "warn_count":                   parsed.get("warn_tests"),
        "p1_count":                     classified.get("p1_count"),
        "p2_count":                     classified.get("p2_count"),
        "p3_count":                     classified.get("p3_count"),
        "overall_status":               classified.get("deployment_recommendation"),
        "schema_drift_events":          drift.get("breaking_changes_count"),
        "scripts_impacted_by_drift":    drift.get("scripts_impacted_count"),
        "jira_tickets_opened":          [t["key"] for t in tickets if t.get("key")],
        "hours_saved_vs_manual":        round(40 - (elapsed / 1000 / 60), 1),
        "audit_lens_event_id":          f"DVR-{cycle_id}-CERT",
    }
    elapsed = _now_ms() - t0
    yield _sse("stage_done", {"stage_id": "report", "ms": elapsed,
                               "summary": _stage_done_summary(report, "report"),
                               "output_keys": list(report.keys())})

    # ─── Final cycle_done frame with everything the result panel needs ───
    ended_at = _now_ms()
    duration_ms = ended_at - pipeline_started_at
    yield _sse("cycle_done", {
        "cycle_id":               cycle_id,
        "ended_at":                ended_at,
        "duration_ms":             duration_ms,
        "trigger":                 trigger,
        "report":                  report,
        "tickets":                 tickets,
        "schema_drift":            drift,
        "classification_summary": {
            "p1": classified.get("p1_count", 0),
            "p2": classified.get("p2_count", 0),
            "p3": classified.get("p3_count", 0),
            "recommendation": classified.get("deployment_recommendation"),
        },
        "all_mock":                all(t.get("mock") for t in tickets) if tickets else True,
    })

    # ─── Record into the in-memory cycle history ring buffer ───
    # Frontend Pipelines + Playbook detail pages read this via /cycle-history
    # to render "Last run: X ago" and the run history table.
    await _record_cycle({
        "cycle_id":      cycle_id,
        "started_at":    pipeline_started_at,
        "ended_at":      ended_at,
        "duration_ms":   duration_ms,
        "trigger":       trigger,
        "source":        source_label or str(xml_path),
        "device":        parsed.get("device_under_test"),
        "firmware":      parsed.get("firmware_version"),
        "total":         parsed.get("total_tests"),
        "passed":        parsed.get("passed_tests"),
        "failed":        parsed.get("failed_tests"),
        "warn":          parsed.get("warn_tests"),
        "p1":            classified.get("p1_count", 0),
        "p2":            classified.get("p2_count", 0),
        "p3":            classified.get("p3_count", 0),
        "status":        classified.get("deployment_recommendation", "—"),
        "tickets_count": len(tickets),
        "jira_urls":     [t["url"] for t in tickets[:5] if t.get("url")],
        "jira_keys":     [t["key"] for t in tickets[:5] if t.get("key")],
        "all_mock":      all(t.get("mock") for t in tickets) if tickets else True,
    })


# ──────────────────────────── routes ────────────────────────────

async def _drain_pipeline_to_completion(xml_path: str, cycle_id: str,
                                         tmp_to_clean: Optional[Path],
                                         trigger: str = "s3_event",
                                         source_label: Optional[str] = None) -> None:
    """Run the pipeline generator end-to-end as a background task. Used for
    Path B (Lambda trigger) so the pipeline completes even though the Lambda
    client disconnected after the first SSE frame. The pipeline writes its
    tickets to JIRA regardless of who's listening to the stream."""
    try:
        async for _frame in _run_pipeline(xml_path, cycle_id,
                                           trigger=trigger,
                                           source_label=source_label):
            pass  # Discard frames — we care about the side effects (JIRA writes + history).
        log.info("Path-B pipeline complete: cycle=%s", cycle_id)
    except Exception:
        log.exception("Path-B pipeline raised: cycle=%s", cycle_id)
    finally:
        if tmp_to_clean is not None:
            try: tmp_to_clean.unlink(missing_ok=True)
            except Exception: pass


@router.post("/cycle-start")
async def cycle_start(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    s3_key: Optional[str] = Form(None),
    bucket: Optional[str] = Form(None),
):
    """Kick off a certification cycle. Returns a Server-Sent Events stream
    with one frame per stage. Accept either:
      - multipart upload (Path A, UI drop)
      - s3_key form field (Path B, Lambda trigger — file already in S3)

    Bucket resolution for Path B (priority order):
      1. `bucket` form field if explicitly provided
      2. `X-Apex-Bucket` request header (Lambda sends this)
      3. `CONTAINER_DOCUMENTS_INCOMING` env var (legacy fallback)
    """
    cycle_id = uuid.uuid4().hex[:12].upper()
    xml_path: Optional[Path] = None
    tmp_to_clean: Optional[Path] = None

    if file is not None:
        tmp_dir = Path("/tmp/apex-cycles")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        xml_path = tmp_dir / f"{cycle_id}_{file.filename}"
        contents = await file.read()
        xml_path.write_bytes(contents)
        tmp_to_clean = xml_path
    elif s3_key:
        # Path B: pull from S3. Resolve bucket: form field → header → env.
        try:
            import boto3
            s3 = boto3.client("s3")
            resolved_bucket = (
                bucket
                or request.headers.get("x-apex-bucket")
                or request.headers.get("X-Apex-Bucket")
                or os.environ.get("CONTAINER_DOCUMENTS_INCOMING", "")
            )
            if not resolved_bucket:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No bucket — pass `bucket` form field, "
                                           "X-Apex-Bucket header, or set CONTAINER_DOCUMENTS_INCOMING env.")
            tmp_dir = Path("/tmp/apex-cycles")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            xml_path = tmp_dir / f"{cycle_id}_{Path(s3_key).name}"
            log.info("Path-B S3 download: bucket=%s key=%s", resolved_bucket, s3_key)
            s3.download_file(resolved_bucket, s3_key, str(xml_path))
            tmp_to_clean = xml_path
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"S3 download failed: {e}")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provide either `file` (multipart) or `s3_key` (form field).")

    # Branch by invocation type:
    #   • Path A (UI upload, `file` present) → stream SSE so the browser sees
    #     stages tick live.
    #   • Path B (Lambda trigger, `s3_key` present) → run the pipeline as a
    #     fire-and-forget background task so it completes regardless of
    #     whether the caller disconnects after the first frame. Return 202
    #     with the cycle_id so the caller has a handle.
    if s3_key:
        background_tasks.add_task(
            _drain_pipeline_to_completion,
            str(xml_path), cycle_id, tmp_to_clean,
            "s3_event", s3_key,
        )
        return JSONResponse(
            status_code=202,
            content={
                "status":     "accepted",
                "cycle_id":   cycle_id,
                "trigger":    "s3-event",
                "s3_key":     s3_key,
                "message":    "Pipeline running in background; tickets will appear in JIRA shortly.",
            },
        )

    # Path A (UI upload) — stream SSE. source_label is the filename the
    # user dropped or sample button they clicked.
    source_label = (file.filename if file else None) or str(xml_path)

    async def stream() -> AsyncGenerator[str, None]:
        try:
            async for frame in _run_pipeline(str(xml_path), cycle_id,
                                              trigger="ui_upload",
                                              source_label=source_label):
                yield frame
        finally:
            if tmp_to_clean is not None:
                try:
                    tmp_to_clean.unlink(missing_ok=True)
                except Exception:
                    pass

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":   "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx/proxy buffering if any
            "Connection":      "keep-alive",
        },
    )


@router.get("/cycle-status/{cycle_id}")
async def cycle_status(cycle_id: str):
    """Cheap status probe (placeholder for now). Pipeline currently runs
    synchronously within cycle_start; status is the stream itself. This
    endpoint exists so a future async/background-job variant slots in
    without breaking the UI contract."""
    return {"cycle_id": cycle_id, "status": "ephemeral", "note": "cycle-start streams to completion"}


@router.get("/hitl/pending")
async def hitl_pending() -> Dict[str, Any]:
    """List every HITL request — pending or recently-resolved.
    The UI (Command Center, Dashboard) polls this to render the queue.
    """
    items = sorted(
        list(_PENDING_HITL.values()),
        key=lambda r: r.get("created_at", 0),
        reverse=True,
    )
    return {"count": len(items), "items": items}


class _HitlDecisionPayload(BaseModel):
    reviewer: Optional[str] = "James Patchett"
    comment:  Optional[str] = None


@router.post("/hitl/{request_id}/approve")
async def hitl_approve(request_id: str, payload: _HitlDecisionPayload) -> Dict[str, Any]:
    """Approve a pending HITL request. Wakes the paused pipeline so it
    proceeds (writes JIRA tickets, emits report, etc.)."""
    if request_id not in _PENDING_HITL:
        raise HTTPException(status_code=404, detail=f"HITL request not found: {request_id}")
    if request_id not in _HITL_EVENTS:
        raise HTTPException(status_code=409, detail="Request already resolved")

    decision = {
        "request_id": request_id,
        "decision":   "approve",
        "reviewer":   payload.reviewer or "Unknown",
        "comment":    payload.comment or "",
        "decided_at": _now_ms(),
    }
    _HITL_DECISIONS[request_id] = decision
    _HITL_EVENTS[request_id].set()
    log.info("HITL approved: %s by %s", request_id, decision["reviewer"])
    return decision


@router.post("/hitl/{request_id}/reject")
async def hitl_reject(request_id: str, payload: _HitlDecisionPayload) -> Dict[str, Any]:
    """Reject a pending HITL request. Wakes the paused pipeline so it
    halts cleanly without writing JIRA tickets."""
    if request_id not in _PENDING_HITL:
        raise HTTPException(status_code=404, detail=f"HITL request not found: {request_id}")
    if request_id not in _HITL_EVENTS:
        raise HTTPException(status_code=409, detail="Request already resolved")

    decision = {
        "request_id": request_id,
        "decision":   "reject",
        "reviewer":   payload.reviewer or "Unknown",
        "comment":    payload.comment or "",
        "decided_at": _now_ms(),
    }
    _HITL_DECISIONS[request_id] = decision
    _HITL_EVENTS[request_id].set()
    log.info("HITL rejected: %s by %s", request_id, decision["reviewer"])
    return decision


@router.get("/cycle-history")
async def cycle_history(limit: int = 10) -> Dict[str, Any]:
    """Return the N most recent cycle completions. Used by:
      • Pipelines page → live 'Last run' on pipe-tel-certification
      • Playbook detail (pb-tel-1) → run history table

    Each item:
      cycle_id, started_at, ended_at, duration_ms, trigger ('ui_upload'|'s3_event'),
      source (filename or s3 key), device, firmware, total/pass/fail/warn,
      p1/p2/p3, status, tickets_count, jira_urls (up to 5 sample)
    """
    limit = max(1, min(limit, 50))
    async with _history_lock:
        items = list(_CYCLE_HISTORY)[:limit]
    return {"count": len(_CYCLE_HISTORY), "items": items}


@router.get("/sample-files")
async def sample_files() -> Dict[str, Any]:
    """List the 4 bundled ROBOT XML demo files so the UI can offer a
    one-click 'use sample' button when the customer hasn't dragged a
    file themselves."""
    root = ROOT / "synthetic-data" / "verizon_far_edge" / "robot_outputs"
    files: List[Dict[str, Any]] = []
    if root.is_dir():
        for p in sorted(root.glob("*.xml")):
            files.append({
                "name":           p.name,
                "label":          p.stem.replace("_", " "),
                "size_bytes":     p.stat().st_size,
                "demo_path":      str(p.relative_to(ROOT)),
            })
    return {"count": len(files), "files": files}


@router.get("/jira-config")
async def jira_config() -> Dict[str, Any]:
    """Status probe for the Settings panel + Run page. Tells the UI
    whether we're in mock mode and (if live) whether the credentials
    actually work."""
    sys.path.append(str(ROOT / "backend"))
    from services.jira_client import get_client, reset_client
    reset_client()  # always re-read env on this probe (Settings → Save)
    client = get_client()
    me = client.myself()
    return {
        "config": client.config.public(),
        "probe":  me,
    }
