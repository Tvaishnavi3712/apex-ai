"""
Certification report — the artifact a job run produces.

Apex doesn't invent a report shape. `blueprints/telecommunications/certification_report.json`
already defines the canonical end-of-cycle document shared with HQ Planning and
wave-ops, so a run is rendered into *that* schema:

    header · executive_summary · failure_analysis · schema_drift_summary
    deployment_recommendation · governance_trail

Two consequences worth having:

* The blueprint is read from disk, not mirrored in code. Change the blueprint and
  the report follows — which is the point of having blueprints at all.
* `validate_against_blueprint()` reports any property the blueprint declares that
  the report failed to populate, so a drifting schema surfaces as a warning
  instead of a silently thinner document.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

log = structlog.get_logger()

ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_FILE = ROOT / "blueprints" / "telecommunications" / "certification_report.json"

# A finding's compliance result mapped onto the blueprint's severity vocabulary
# ("P1 / P2 / P3") and its failure categories.
SEVERITY_FOR = {"FAIL": "P1", "DRIFT": "P2", "WARN": "P3"}

CATEGORY_FOR = {
    "Secure Boot": "schema_drift_failure",
    "Event Subscription": "schema_drift_failure",
    "Host Identity (Systems/1)": "regression_failure",
    "Thermal / Fan Baseline": "latency_threshold_breach",
}

# Manual effort per finding, from the campaign's own timing: an engineer
# reproducing one finding by hand (jumpserver, curl, compare, write-up).
HOURS_PER_FINDING_MANUAL = 0.75


# ─────────────────────────────────────────────────────────────────────────────
# blueprint
# ─────────────────────────────────────────────────────────────────────────────

class Blueprint:
    """Loads the certification-report blueprint, cached on mtime."""

    _cache: Optional[Dict[str, Any]] = None
    _mtime: float = 0.0

    @classmethod
    def load(cls) -> Dict[str, Any]:
        try:
            mtime = BLUEPRINT_FILE.stat().st_mtime
        except OSError:
            log.warning("report.blueprint_missing", path=str(BLUEPRINT_FILE))
            return {}
        if cls._cache is None or mtime != cls._mtime:
            try:
                cls._cache = json.loads(BLUEPRINT_FILE.read_text(encoding="utf-8"))
                cls._mtime = mtime
            except (OSError, json.JSONDecodeError) as e:
                log.error("report.blueprint_load_failed", error=str(e))
                return {}
        return cls._cache

    @classmethod
    def schema(cls) -> Dict[str, Any]:
        bp = cls.load()
        for key in ("documentSchema", "bdaSchema", "schema"):
            if key in bp:
                return bp[key]
        return {}

    @classmethod
    def properties(cls) -> Dict[str, Any]:
        return cls.schema().get("properties", {}) or {}

    @classmethod
    def meta(cls) -> Dict[str, Any]:
        bp = cls.load()
        return {
            "blueprint_name": bp.get("blueprintName"),
            "blueprint_version": bp.get("blueprintVersion"),
            "document_type": bp.get("documentType"),
            "class": cls.schema().get("class"),
            "formats": (bp.get("outputConfiguration") or {}).get("formats", []),
        }


# ─────────────────────────────────────────────────────────────────────────────
# build
# ─────────────────────────────────────────────────────────────────────────────

def build_report(run: Dict[str, Any]) -> Dict[str, Any]:
    """Render a job run into a blueprint-conforming certification report."""
    targets: List[Dict[str, Any]] = run.get("targets", []) or []
    findings = [
        {**f, "hostname": t.get("hostname") or t.get("server_id")}
        for t in targets for f in (t.get("findings") or [])
    ]

    tickets = {t.get("summary"): t for t in (run.get("jira_tickets") or [])}

    fail_count = sum(1 for f in findings if f["result"] == "FAIL")
    drift_count = sum(1 for f in findings if f["result"] == "DRIFT")
    warn_count = sum(1 for f in findings if f["result"] == "WARN")

    # One "test" per Redfish request issued across all targets.
    total_tests = run.get("total_requests", 0)
    pass_count = max(total_tests - len(findings), 0)

    device = targets[0] if targets else {}
    overall = _overall_status(run.get("status"))

    report = {
        "header": {
            "device_name": _device_name(targets),
            "firmware_version": _firmware(device),
            "certification_date": (run.get("started_at") or "")[:10],
            "overall_status": overall,
            "generated_by": f"Apex · {run.get('playbook_label') or run.get('playbook_id', 'job')}",
            "generation_time_seconds": _duration_seconds(run),
        },
        "executive_summary": {
            "total_tests": total_tests,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "investigate_count": drift_count + warn_count,
            "schema_drift_events": drift_count,
            "jira_tickets_opened": len(run.get("jira_tickets") or []),
            "hours_saved_vs_manual": round(len(findings) * HOURS_PER_FINDING_MANUAL, 2),
        },
        "failure_analysis": [
            _failure_record(f, tickets) for f in _by_severity(findings)
        ],
        "schema_drift_summary": [
            _drift_record(f) for f in findings if f["result"] == "DRIFT"
        ],
        "deployment_recommendation": _recommendation(fail_count, drift_count, warn_count),
        "governance_trail": _governance(run, findings),
    }

    meta = Blueprint.meta()
    validation = validate_against_blueprint(report)

    return {
        "report": report,
        "blueprint": meta,
        "conforms": validation["conforms"],
        "missing_properties": validation["missing"],
        "run_id": run.get("id"),
        "job_name": run.get("job_name"),
    }


# ─────────────────────────────────────────────────────────────────────────────
# sections
# ─────────────────────────────────────────────────────────────────────────────

def _device_name(targets: List[Dict[str, Any]]) -> str:
    names = [t.get("hostname") or t.get("server_id") for t in targets if t]
    if not names:
        return "unknown"
    return names[0] if len(names) == 1 else f"{names[0]} (+{len(names) - 1} more)"


def _firmware(device: Dict[str, Any]) -> str:
    """Firmware level of the certified device, read from the inventory."""
    from services.redfish import InventoryData
    server = InventoryData.server(device.get("server_id", "")) or {}
    parts = [server.get("bmc_firmware"), server.get("bios_version")]
    return " / ".join(p for p in parts if p) or "unknown"


def _duration_seconds(run: Dict[str, Any]) -> float:
    total_ms = sum(t.get("duration_ms", 0) for t in (run.get("targets") or []))
    return round(total_ms / 1000.0, 2)


def _overall_status(status: Optional[str]) -> str:
    """Map a run status onto the blueprint's PASS / CONDITIONAL_PASS / FAIL."""
    if status in ("FAIL", "ERROR"):
        return "FAIL"
    if status in ("DRIFT", "WARN"):
        return "CONDITIONAL_PASS"
    return "PASS"


def _by_severity(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    order = {"FAIL": 0, "DRIFT": 1, "WARN": 2}
    return sorted(findings, key=lambda f: order.get(f["result"], 9))


def _failure_record(f: Dict[str, Any], tickets: Dict[str, Any]) -> Dict[str, Any]:
    gap = f.get("gap") or {}
    ticket = next(
        (t for summary, t in tickets.items() if summary and f["step"] in summary),
        None,
    )
    return {
        "test_id": f"{f['hostname']}::{f['step']}",
        "category": CATEGORY_FOR.get(f["step"], "investigate"),
        "severity": SEVERITY_FOR.get(f["result"], "P3"),
        "root_cause": f.get("detail") or "",
        "recommendation": gap.get("action") or "",
        "jira_ticket": (ticket or {}).get("key") or "",
        # Populated once the known-issues KB is consulted; empty means no match
        # was claimed, rather than none being possible.
        "kb_match": "",
    }


def _drift_record(f: Dict[str, Any]) -> Dict[str, Any]:
    gap = f.get("gap") or {}
    fields = gap.get("fields") or []
    return {
        "endpoint": f.get("category") or f["step"],
        "change_type": "configuration_drift",
        "scripts_impacted": _scripts_impacted(gap),
        "remediation_steps": gap.get("action") or f.get("detail") or "",
        "observed": [
            {"field": x.get("field"), "current": x.get("current"), "expected": x.get("expected")}
            for x in fields
        ],
    }


def _scripts_impacted(gap: Dict[str, Any]) -> List[str]:
    """Pull the tooling named in the remediation, rather than guessing."""
    text = " ".join(str(gap.get(k) or "") for k in ("action", "remediation_command"))
    return sorted({tok for tok in text.split() if tok.endswith(".py")})


def _recommendation(fail: int, drift: int, warn: int) -> Dict[str, Any]:
    if fail:
        rec, days = "hold", 5
    elif drift:
        rec, days = "conditional", 2
    elif warn:
        rec, days = "conditional", 1
    else:
        rec, days = "proceed", 0

    conditions: List[str] = []
    if fail:
        conditions.append(f"Resolve {fail} P1 failure(s) before this unit joins a wave")
    if drift:
        conditions.append(f"Remediate {drift} configuration drift item(s)")
    if warn:
        conditions.append(f"Review {warn} warning(s); manual step may be required")

    return {
        "overall_recommendation": rec,
        "conditions_to_proceed": conditions,
        "estimated_remediation_days": days,
    }


def _governance(run: Dict[str, Any], findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    actions = [
        f"Walked {run.get('total_requests', 0)} Redfish endpoint(s) "
        f"across {run.get('target_count', 0)} target(s)",
        f"Playbook: {run.get('playbook_id', 'unknown')}",
    ]
    if run.get("endpoints_walked") and run["endpoints_walked"] != "all":
        actions.append(f"Endpoint subset selected by playbook: {', '.join(run['endpoints_walked'])}")
    actions.append(f"Classified {len(findings)} finding(s) by severity")

    created = run.get("jira_tickets") or []
    required, received = [], []
    if findings and run.get("raises_tickets", True):
        required.append(f"Approve creation of {len(findings)} ticket(s)")
        if created:
            received.append(
                f"Approved — {len(created)} ticket(s) created: "
                f"{', '.join(str(t.get('key')) for t in created)}"
            )
    elif findings:
        actions.append("Playbook raises no tickets — findings reported for scoring only")

    return {
        "agent_actions_log": actions,
        "human_approvals_required": required,
        "human_approvals_received": received,
        "audit_lens_event_ids": [run.get("id")] if run.get("id") else [],
    }


# ─────────────────────────────────────────────────────────────────────────────
# validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_against_blueprint(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check the report against the blueprint's declared properties.

    Reports what the blueprint declares but the report didn't populate — so a
    blueprint change shows up as a named gap rather than a quietly thinner doc.
    """
    props = Blueprint.properties()
    if not props:
        return {"conforms": False, "missing": ["blueprint could not be loaded"]}

    missing: List[str] = []
    for name, spec in props.items():
        if name not in report:
            missing.append(name)
            continue
        if spec.get("type") == "object":
            sub = spec.get("properties") or {}
            for key in sub:
                if key not in (report.get(name) or {}):
                    missing.append(f"{name}.{key}")

    return {"conforms": not missing, "missing": missing}
