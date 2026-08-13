"""
Jobs — scheduled, repeatable work against real hardware.

A *job* binds three things an operator already thinks in terms of:

    playbook   what to do            (e.g. telecommunications.full_certification_cycle)
    targets    which servers         (ids from the hardware inventory)
    schedule   when it runs          (manual | hourly | nightly | weekly | on_drift)

Running a job walks each target's BMC over Redfish, evaluates the findings, and
records a run with per-target outcomes. Duplicating a job clones it onto
different targets — the common case when a second site or a second platform
needs the same treatment.

Storage is a small JSON file so jobs survive a restart without requiring the
cloud store to be reachable from a laptop — Cosmos DB sits behind a private
endpoint here. The shape matches a Cosmos DB document, so moving it later is a
transport change only.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from services.redfish import InventoryData, RedfishClient

log = structlog.get_logger()

ROOT = Path(__file__).resolve().parents[2]
STORE_FILE = Path(
    os.environ.get("APEX_JOBS_FILE", str(ROOT / "backend" / ".localdata" / "jobs.json"))
)

SCHEDULES = ("manual", "hourly", "nightly", "weekly", "on_drift")

# ─────────────────────────────────────────────────────────────────────────────
# playbook specs — what a playbook actually changes about a run
# ─────────────────────────────────────────────────────────────────────────────
#
# The playbook is not a label. It selects which Redfish endpoints are walked and
# which post-steps run, so choosing a different playbook produces a visibly
# different run rather than the same walk under another name.
#
# `endpoints: None` means the full catalog. Ids match `redfish_catalog[].id`.

PLAYBOOK_SPECS: Dict[str, Dict[str, Any]] = {
    "telecommunications.full_certification_cycle": {
        "label": "Full certification cycle",
        "endpoints": None,                       # every catalog endpoint
        "emits_report": True,
        "raises_tickets": True,
        "summary": "Complete Redfish sweep, classified failures, certification report, tickets.",
    },
    "telecommunications.new_platform_onboarding": {
        "label": "New platform onboarding",
        # Onboarding cares about identity, health and the security baseline —
        # not per-subsystem depth.
        "endpoints": ["model", "aggregate_health_status", "ilo_bmc_version",
                      "bios_version", "bios", "secure_boot"],
        "emits_report": True,
        "raises_tickets": True,
        "summary": "Identity, health, firmware level and security baseline for a new server type.",
    },
    "telecommunications.schema_drift_response": {
        # Data-driven: walk exactly the endpoints the campaign flagged as needing
        # a monitoring change. Resolved at run time from the catalog.
        "label": "Schema drift response",
        "endpoints": "__requires_change__",
        "emits_report": False,
        "raises_tickets": True,
        "summary": "Only the endpoints whose Redfish shape changed, and the monitoring fix each needs.",
    },
    "telecommunications.wave_deployment_risk_assessment": {
        "label": "Wave deployment risk assessment",
        "endpoints": ["aggregate_health_status", "fans", "thermal_sensors",
                      "power_supply", "ilo_bmc_version", "bios_version"],
        "emits_report": True,
        "raises_tickets": False,             # scoring only — a wave gate, not a ticket factory
        "summary": "Health, thermal and firmware posture scored for wave readiness. Raises no tickets.",
    },
    "telecommunications.playbook_gap_analysis": {
        "label": "Playbook gap analysis",
        "endpoints": None,
        "emits_report": False,
        "raises_tickets": False,
        "summary": "Full sweep compared against the live Ansible playbook. Produces a change spec, not tickets.",
    },
    "telecommunications.operator_kb_query": {
        "label": "Operator knowledge query",
        "endpoints": [],                     # answers from the KB; touches no hardware
        "emits_report": False,
        "raises_tickets": False,
        "summary": "Answers an operator question from the known-issues KB. Does not touch hardware.",
    },
}

DEFAULT_SPEC: Dict[str, Any] = {
    "label": "Custom",
    "endpoints": None,
    "emits_report": False,
    "raises_tickets": True,
    "summary": "Full Redfish sweep.",
}


def spec_for(playbook_id: str) -> Dict[str, Any]:
    return PLAYBOOK_SPECS.get(playbook_id, DEFAULT_SPEC)


def resolve_endpoints(playbook_id: str) -> Optional[List[str]]:
    """
    Turn a spec's endpoint selector into a concrete list.

    Returns None for "walk everything" so it can be passed straight to
    `RedfishClient.interrogate(only=...)`.
    """
    selector = spec_for(playbook_id).get("endpoints")
    if selector is None:
        return None
    if selector == "__requires_change__":
        # `requires_change` is extracted from the campaign document's own summary
        # table, which states per check whether monitoring had to change. The
        # prose in `required_change` is not machine-readable — don't parse it.
        return [c["id"] for c in InventoryData.catalog() if c.get("requires_change")]
    return list(selector)

# Human-readable cadence, shown in the UI and used when describing a job.
SCHEDULE_LABEL = {
    "manual":   "On demand",
    "hourly":   "Every hour",
    "nightly":  "Every night at 02:00",
    "weekly":   "Every Sunday at 02:00",
    "on_drift": "Whenever drift is detected",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class JobStore:
    """File-backed job store. Writes are atomic and guarded by a lock."""

    _lock = threading.Lock()

    @classmethod
    def _read(cls) -> Dict[str, Any]:
        try:
            with open(STORE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "jobs" in data:
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return {"jobs": [], "runs": []}

    @classmethod
    def _write(cls, data: Dict[str, Any]) -> None:
        STORE_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = str(STORE_FILE) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(tmp, STORE_FILE)

    # ── jobs ─────────────────────────────────────────────────────────────────
    @classmethod
    def list_jobs(cls) -> List[Dict[str, Any]]:
        return cls._read().get("jobs", [])

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        return next((j for j in cls.list_jobs() if j.get("id") == job_id), None)

    @classmethod
    def create(cls, job: Dict[str, Any]) -> Dict[str, Any]:
        with cls._lock:
            data = cls._read()
            data["jobs"].append(job)
            cls._write(data)
        return job

    @classmethod
    def update(cls, job_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with cls._lock:
            data = cls._read()
            for j in data["jobs"]:
                if j.get("id") == job_id:
                    j.update({k: v for k, v in patch.items() if v is not None})
                    j["updated_at"] = _now()
                    cls._write(data)
                    return j
        return None

    @classmethod
    def delete(cls, job_id: str) -> bool:
        with cls._lock:
            data = cls._read()
            before = len(data["jobs"])
            data["jobs"] = [j for j in data["jobs"] if j.get("id") != job_id]
            data["runs"] = [r for r in data.get("runs", []) if r.get("job_id") != job_id]
            if len(data["jobs"]) == before:
                return False
            cls._write(data)
            return True

    # ── runs ─────────────────────────────────────────────────────────────────
    @classmethod
    def add_run(cls, run: Dict[str, Any]) -> Dict[str, Any]:
        with cls._lock:
            data = cls._read()
            data.setdefault("runs", []).insert(0, run)
            # Keep history bounded; a demo box shouldn't grow without limit.
            data["runs"] = data["runs"][:200]
            for j in data["jobs"]:
                if j.get("id") == run["job_id"]:
                    j["last_run_at"] = run["started_at"]
                    j["last_status"] = run["status"]
                    j["run_count"] = int(j.get("run_count", 0)) + 1
            cls._write(data)
        return run

    @classmethod
    def runs_for(cls, job_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return [r for r in cls._read().get("runs", []) if r.get("job_id") == job_id][:limit]

    @classmethod
    def get_run(cls, run_id: str) -> Optional[Dict[str, Any]]:
        return next((r for r in cls._read().get("runs", []) if r.get("id") == run_id), None)

    @classmethod
    def annotate_run(cls, run_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Record the outcome of a side effect (e.g. tickets raised) on a run."""
        with cls._lock:
            data = cls._read()
            for r in data.get("runs", []):
                if r.get("id") == run_id:
                    r.update(patch)
                    cls._write(data)
                    return r
        return None


# ─────────────────────────────────────────────────────────────────────────────
# job construction
# ─────────────────────────────────────────────────────────────────────────────

def build_job(
    name: str,
    playbook_id: str,
    targets: List[str],
    schedule: str = "manual",
    description: str = "",
    created_by: str = "apex",
) -> Dict[str, Any]:
    if schedule not in SCHEDULES:
        raise ValueError(f"schedule must be one of {SCHEDULES}")

    return {
        "id": f"job-{uuid.uuid4().hex[:8]}",
        "name": name.strip(),
        "description": description.strip(),
        "playbook_id": playbook_id,
        "targets": list(targets),
        "schedule": schedule,
        "schedule_label": SCHEDULE_LABEL[schedule],
        "enabled": schedule != "manual",
        "created_at": _now(),
        "updated_at": _now(),
        "created_by": created_by,
        "run_count": 0,
        "last_run_at": None,
        "last_status": None,
    }


def duplicate_job(source: Dict[str, Any], name: Optional[str] = None,
                  targets: Optional[List[str]] = None,
                  schedule: Optional[str] = None) -> Dict[str, Any]:
    """
    Clone a job, optionally retargeting it.

    Run history is deliberately NOT copied — a duplicate has not run yet, and
    inheriting the source's results would misreport the new targets' state.
    """
    clone = build_job(
        name=name or f"{source['name']} (copy)",
        playbook_id=source["playbook_id"],
        targets=targets if targets is not None else list(source.get("targets", [])),
        schedule=schedule or source.get("schedule", "manual"),
        description=source.get("description", ""),
        created_by=source.get("created_by", "apex"),
    )
    clone["duplicated_from"] = source["id"]
    return clone


# ─────────────────────────────────────────────────────────────────────────────
# execution
# ─────────────────────────────────────────────────────────────────────────────

SEVERITY = {"FAIL": 0, "DRIFT": 1, "WARN": 2}


def execute_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a job against every target and record the outcome.

    Each target gets a real Redfish walk; findings come from that server's own
    evidence, so a job over three servers reports three independent verdicts
    rather than one blended number.
    """
    started = _now()
    targets: List[Dict[str, Any]] = []

    playbook_id = job.get("playbook_id", "")
    spec = spec_for(playbook_id)
    endpoints = resolve_endpoints(playbook_id)

    for server_id in job.get("targets", []):
        server = InventoryData.server(server_id)
        if server is None:
            targets.append({
                "server_id": server_id,
                "hostname": None,
                "status": "ERROR",
                "error": "server not in inventory",
                "requests": 0,
                "findings": [],
            })
            continue

        try:
            client = RedfishClient.for_server(server_id)
            steps = client.interrogate(only=endpoints)

            findings: List[Dict[str, Any]] = []
            seen = set()
            for st in steps:
                for f in st.findings:
                    if f["result"] in SEVERITY and f["step"] not in seen:
                        seen.add(f["step"])
                        findings.append(f)
            findings.sort(key=lambda f: SEVERITY.get(f["result"], 9))

            worst = min((SEVERITY.get(f["result"], 9) for f in findings), default=9)
            status = {0: "FAIL", 1: "DRIFT", 2: "WARN"}.get(worst, "PASS")

            targets.append({
                "server_id": server_id,
                "hostname": server.get("hostname"),
                "platform": server.get("platform"),
                "bmc_ip": server.get("bmc_ip"),
                "status": status,
                "requests": len(steps),
                "duration_ms": sum(s.duration_ms for s in steps),
                "findings": findings,
            })
        except Exception as e:  # noqa: BLE001 — one bad target must not kill the run
            log.warning("jobs.target_failed", job=job["id"], server=server_id, error=str(e))
            targets.append({
                "server_id": server_id,
                "hostname": server.get("hostname"),
                "status": "ERROR",
                "error": str(e),
                "requests": 0,
                "findings": [],
            })

    order = {"ERROR": -1, "FAIL": 0, "DRIFT": 1, "WARN": 2, "PASS": 3}
    overall = min((order.get(t["status"], 3) for t in targets), default=3)
    status = next((k for k, v in order.items() if v == overall), "PASS")

    run = {
        "id": f"run-{uuid.uuid4().hex[:8]}",
        "job_id": job["id"],
        "job_name": job["name"],
        "playbook_id": job["playbook_id"],
        "playbook_label": spec["label"],
        "playbook_summary": spec["summary"],
        # Surfaced so the UI can show why this run walked what it walked.
        "endpoints_walked": endpoints if endpoints is not None else "all",
        "raises_tickets": spec["raises_tickets"],
        "emits_report": spec["emits_report"],
        "started_at": started,
        "finished_at": _now(),
        "status": status,
        "targets": targets,
        "target_count": len(targets),
        "total_requests": sum(t.get("requests", 0) for t in targets),
        "total_findings": sum(len(t.get("findings", [])) for t in targets),
    }
    return JobStore.add_run(run)


# ─────────────────────────────────────────────────────────────────────────────
# enrichment
# ─────────────────────────────────────────────────────────────────────────────

def enrich(job: Dict[str, Any]) -> Dict[str, Any]:
    """Attach resolved target identity so the UI doesn't have to join client-side."""
    out = dict(job)
    resolved = []
    for sid in job.get("targets", []):
        s = InventoryData.server(sid)
        resolved.append({
            "id": sid,
            "hostname": (s or {}).get("hostname"),
            "platform": (s or {}).get("platform"),
            "status": (s or {}).get("status"),
            "known": s is not None,
        })
    out["target_details"] = resolved
    out["schedule_label"] = SCHEDULE_LABEL.get(job.get("schedule", "manual"), "On demand")
    return out
