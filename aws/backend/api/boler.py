"""
Boler (The Boler Company) demo backend.

Single consolidated endpoint `/api/v1/boler/dashboard-state` hydrates the 4
frontend pages (Dashboard, Command Center, Apex Signal, Agent Hub). Zero
hardcoded UI values per CLAUDE.md ZERO-HARDCODING RULE.

Mirrors the EPROD + CWFCU pattern. SageMaker / AgentCore are intentionally
skipped for round 1 of this customer demo — all signal endpoints return
deterministic fixtures grounded on the synthetic-data/boler/ corpus + the
4 HTML mockups (dashboard.html, command-center.html, signal.html, agent-hub.html).

AWS architecture story baked in: S3 + Lambda + Step Functions + Bedrock +
DynamoDB + SES + SNS + QuickSight + IAM + KMS.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────
# Demo anchor constants — keep in sync with PDF brief + HTML mockups.
# Single source of truth so every screen displays the same numbers.
# ─────────────────────────────────────────────────────────────────────
CYCLE = "June 2026"
TOTAL_EMPLOYEES = 847
TOTAL_DIVISIONS = 5
TOTAL_ALLOCATED = 2_142_000
PROCESSING_HOURS = 4.2
MANUAL_BASELINE_DAYS = 3.5
EXCEPTIONS_COUNT = 7
APPROVAL_STAGE = 2
TOTAL_STAGES = 3


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
def _monthly_trend() -> Dict[str, Any]:
    """6-month allocation trend per division (Jan-Jun 2026)."""
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "hendrickson":   [998000, 1012000, 1024000, 1031000, 1024000, 1042800],
        "holdings":      [288000, 292000, 298000, 301000, 301100, 313480],
        "manufacturing": [374000, 378000, 382000, 388000, 388600, 394320],
        "real_estate":   [220000, 222400, 224000, 225800, 224000, 224910],
        "corporate":     [162000, 163000, 164500, 165400, 166200, 166490],
    }


# ─────────────────────────────────────────────────────────────────────
# GET /boler/dashboard-state
# ─────────────────────────────────────────────────────────────────────
@router.get("/dashboard-state")
async def boler_dashboard_state() -> Dict[str, Any]:
    """Consolidated demo data feed for The Boler Company.

    Hydrates all 4 Boler demo pages (Dashboard, Command Center, Apex Signal,
    Agent Hub) plus the Human Review surface. Static-ish demo state — refresh
    every 30s on the dashboard, 15s on Command Center.
    """
    now = datetime.now(timezone.utc)

    # ── KPI strip ──────────────────────────────────────────────────────
    kpis = {
        "total_allocated_usd":          TOTAL_ALLOCATED,        # $2,142,000
        "total_allocated_pct_vs_may":   3.2,                     # +3.2%
        "processing_hours":             PROCESSING_HOURS,        # 4.2 hrs
        "manual_baseline_days":         MANUAL_BASELINE_DAYS,    # 3.5 days
        "time_saved_days":              3.3,                     # 3.3 days saved
        "exceptions_flagged":           EXCEPTIONS_COUNT,        # 7
        "exceptions_new_this_cycle":    3,
        "exceptions_high_severity":     2,                       # 2 HIGH require CFO
        "exceptions_variance_usd":      28_120,                  # $28,120 total variance
        "approval_stage":               APPROVAL_STAGE,           # Stage 2 of 3
        "total_stages":                 TOTAL_STAGES,
        "files_processed":              6,                       # 6 carrier files
        "sars_auto_drafted":            7,                       # exceptions auto-drafted
        "loan_packets_cleared":         5,                       # 5 division JEs ready
    }

    # ── Workflow tracker (5 stages) ────────────────────────────────────
    workflow = {
        "stages": [
            {"key": "intake",      "label": "File Intake",         "sub": "Jun 3 · 6 files",      "state": "done"},
            {"key": "extract",     "label": "APEX Extract",        "sub": "Jun 3 · 4.2 hrs",       "state": "done"},
            {"key": "approval1",    "label": "Benefits Approval",   "sub": "Jun 5 · Approved",      "state": "done"},
            {"key": "approval2",    "label": "Accounting Review",   "sub": "Jun 6 · Pending",       "state": "active"},
            {"key": "distribution", "label": "Distribution",        "sub": "Jun 7 · Scheduled",     "state": "pending"},
        ],
        "current_stage_index": 3,   # 4th stage (0-indexed)
        "total_stages":        5,
    }

    # ── 6 carrier files (Source Files Ingested) ────────────────────────
    carrier_files = [
        {"name": "Cigna_Medical_Jun2026.csv",    "employees": 847, "amount_usd": 1_284_320, "status": "Extracted"},
        {"name": "Delta_Dental_Jun2026.csv",     "employees": 831, "amount_usd":   187_450, "status": "Extracted"},
        {"name": "Fidelity_401k_Jun2026.csv",    "employees": 803, "amount_usd":   412_880, "status": "Extracted"},
        {"name": "VSP_Vision_Jun2026.csv",       "employees": 798, "amount_usd":    62_140, "status": "Extracted"},
        {"name": "Hartford_Life_Jun2026.csv",    "employees": 847, "amount_usd":    98_760, "status": "Extracted"},
        {"name": "Cigna_STD_LTD_Jun2026.csv",    "employees": 847, "amount_usd":    94_450, "status": "Extracted"},
    ]

    # ── 5 division allocations ──────────────────────────────────────────
    divisions = [
        {"id": "hendrickson",  "name": "Hendrickson Intl",        "color": "#6c47ff", "employees": 412,
         "allocated_usd": 1_042_800, "budget_usd": 1_034_400, "variance_pct": 0.8, "status": "Approved",
         "cost_center": "6200-001",
         "breakdown": {"medical": 710_800, "dental": 126_800, "vision": 38_200, "retirement": 167_000}},
        {"id": "real_estate",  "name": "Boler Real Estate",       "color": "#2563eb", "employees": 89,
         "allocated_usd":   224_910, "budget_usd":   227_640, "variance_pct": -1.2, "status": "Approved",
         "cost_center": "6200-002",
         "breakdown": {"medical": 142_800, "dental": 28_400, "vision": 8_910, "retirement": 44_800}},
        {"id": "holdings",     "name": "Boler Holdings",          "color": "#f59e0b", "employees": 124,
         "allocated_usd":   313_480, "budget_usd":   300_960, "variance_pct": 4.1, "status": "Review",
         "cost_center": "6200-003",
         "breakdown": {"medical": 198_400, "dental": 39_600, "vision": 12_480, "retirement": 63_000}},
        {"id": "manufacturing","name": "Boler Mfg Services",      "color": "#00c4a0", "employees": 156,
         "allocated_usd":   394_320, "budget_usd":   388_800, "variance_pct": 1.4, "status": "Pending",
         "cost_center": "6200-004",
         "breakdown": {"medical": 249_600, "dental": 49_800, "vision": 15_720, "retirement": 79_200}},
        {"id": "corporate",    "name": "Corporate / Shared Svcs", "color": "#9ca3af", "employees": 66,
         "allocated_usd":   166_490, "budget_usd":   167_000, "variance_pct": -0.3, "status": "Approved",
         "cost_center": "6200-005",
         "breakdown": {"medical": 105_600, "dental": 21_080, "vision": 6_610, "retirement": 33_200}},
    ]

    # ── 7 exceptions (Dashboard panel + Command Center detail viewer) ─
    exceptions = [
        {
            "id": "EXC-2026-0441", "severity": "HIGH",
            "title": "Employee coded to wrong division",
            "description": "Chen, Robert (EMP-4821) was coded to Hendrickson Intl but transferred to Boler Holdings on May 15. All 6 benefit lines still allocated to Hendrickson.",
            "employee": "Chen, Robert", "employee_id": "EMP-4821",
            "agent": "Benefits", "time": "09:41 AM",
            "diff": {"before": "- Hendrickson Intl · Cost Center 6200-001 · $3,840/mo",
                     "after":  "+ Boler Holdings · Cost Center 6200-004 · $3,840/mo"},
            "amount_usd": 3840, "status": "Awaiting CFO",
        },
        {
            "id": "EXC-2026-0442", "severity": "HIGH",
            "title": "Duplicate enrollment — Cigna medical + COBRA",
            "description": "Martinez, Laura (EMP-3312) appears in both active Cigna medical file and COBRA billing file. Terminated Apr 30. COBRA billing should not be charged to Boler Holdings cost center.",
            "employee": "Martinez, Laura", "employee_id": "EMP-3312",
            "agent": "Benefits", "time": "09:38 AM",
            "diff": {"before": "- Active Medical: $1,240/mo charged to Boler Holdings (INVALID)",
                     "after":  "+ COBRA is self-pay — remove from corporate allocation entirely"},
            "amount_usd": 1240, "status": "Awaiting CFO",
        },
        {
            "id": "EXC-2026-0443", "severity": "MEDIUM",
            "title": "Rate change vs. prior month (+8.4%)",
            "description": "Cigna medical · Boler Holdings · $2,180 variance · No rate card update on file. APEX Signal flagged this 90 days ago — renewal in 41 days.",
            "agent": "Signal", "time": "09:35 AM",
            "amount_usd": 2180, "status": "Awaiting Benefits",
        },
        {
            "id": "EXC-2026-0444", "severity": "MEDIUM",
            "title": "Division transfer not reflected",
            "description": "4 employees transferred May 15 — still coded to prior division — $14,320 misallocation. 3 of 4 auto-corrected (Kim, Foster, Reilly). Chen escalated separately as EXC-0441.",
            "agent": "Benefits", "time": "09:22 AM",
            "amount_usd": 14_320, "status": "Auto-Fixed",
        },
        {
            "id": "EXC-2026-0445", "severity": "MEDIUM",
            "title": "401k match rate mismatch",
            "description": "Fidelity file shows 4.5% match rate. HR policy P-COMP-401K-2024 shows 4.0%. $8,240 monthly delta. Root cause TBD — Sarah Mitchell follow-up requested.",
            "agent": "Benefits", "time": "09:31 AM",
            "amount_usd": 8240, "status": "Awaiting Benefits",
        },
        {
            "id": "EXC-2026-0446", "severity": "LOW",
            "title": "Terminated employee — benefits still active",
            "description": "Thompson, D. · Terminated May 28 · Vision + dental still billed · $420 auto-fixed.",
            "employee": "Thompson, D.",
            "agent": "Benefits", "time": "09:18 AM",
            "amount_usd": 420, "status": "Auto-Fixed",
        },
        {
            "id": "EXC-2026-0447", "severity": "LOW",
            "title": "Missing cost center code",
            "description": "3 new hires · No cost center assigned · $6,840 unallocated. Routed to Sarah Mitchell to confirm division placements with hiring managers.",
            "agent": "Benefits", "time": "09:14 AM",
            "amount_usd": 6840, "status": "Awaiting Benefits",
        },
    ]

    # ── 2-Stage Approval Queue ──────────────────────────────────────────
    approval_queue = [
        {"stage": 1, "title": "Stage 1 — Benefits Manager Approval",
         "meta":   "Approved Jun 5, 2026 · 09:22 AM · Sarah Mitchell, Benefits Director",
         "status": "COMPLETE", "status_color": "#16a34a"},
        {"stage": 2, "title": "Stage 2 — Accounting Review & Approval",
         "meta":   "Awaiting · Routed to Ziggy Kravitz, CFO · Due Jun 6, 2026",
         "status": "REVIEW",   "status_color": "#2563eb"},
        {"stage": 3, "title": "Stage 3 — Division Journal Entry Distribution",
         "meta":   "Scheduled Jun 7, 2026 · Auto-distribution via Step Functions + S3",
         "status": "PENDING",  "status_color": "#9ca3af"},
    ]

    # ── Journal Entry Preview (Hendrickson — used on Dashboard) ────────
    je_preview = {
        "division": "Hendrickson Intl",
        "period":   CYCLE,
        "lines": [
            {"side": "DR", "account": "6200-001", "description": "Benefits Expense — Medical",         "amount_usd": 624_480},
            {"side": "DR", "account": "6200-002", "description": "Benefits Expense — Dental",          "amount_usd":  91_840},
            {"side": "DR", "account": "6200-003", "description": "Benefits Expense — 401k Match",      "amount_usd": 201_760},
            {"side": "DR", "account": "6200-004", "description": "Benefits Expense — Vision/Life/LTD", "amount_usd": 124_720},
            {"side": "CR", "account": "2100-001", "description": "Benefits Payable — Cigna",            "amount_usd": 1_042_800},
        ],
        "balanced": True,
        "total_usd": 1_042_800,
    }

    # ── Audit Trail (last 5 entries — feeds Dashboard + right rail) ────
    audit_log = [
        {"time": "09:41:03", "date": "Jun 6, 2026",
         "action": "EXC-0441 reclassification applied",
         "detail": "Chen, R. · Hendrickson → Boler Holdings · $3,840/mo",
         "badge":  "FIXED",    "badge_color": "green"},
        {"time": "09:38:22", "date": "Jun 6, 2026",
         "action": "Stage 2 approval notification sent",
         "detail": "Ziggy Kravitz · Email (SES) + SNS push · Due Jun 6",
         "badge":  "ROUTED",   "badge_color": "blue"},
        {"time": "09:35:14", "date": "Jun 6, 2026",
         "action": "Cigna rate drift alert generated",
         "detail": "+4.1% above contract · 90-day model",
         "badge":  "ALERT",    "badge_color": "red"},
        {"time": "09:31:08", "date": "Jun 6, 2026",
         "action": "401k match rate mismatch flagged",
         "detail": "Fidelity 4.5% vs. HR policy 4.0% · $8,240 delta",
         "badge":  "FLAGGED",  "badge_color": "amber"},
        {"time": "09:22:14", "date": "Jun 5, 2026",
         "action": "Stage 1 approved — Sarah Mitchell",
         "detail": "Benefits Director · 5 resolved · 2 overridden",
         "badge":  "APPROVED", "badge_color": "green"},
        {"time": "09:18:33", "date": "Jun 5, 2026",
         "action": "Thompson, D. — terminated employee removed",
         "detail": "Vision + dental · $420 removed from allocation",
         "badge":  "AUTO-FIXED", "badge_color": "green"},
        {"time": "09:14:22", "date": "Jun 3, 2026",
         "action": "6 carrier files ingested from S3 intake bucket",
         "detail": "847 employees · $2,142,000 total",
         "badge":  "INGESTED", "badge_color": "green"},
    ]

    # ── 5-agent status (Agent Hub left rail + Command Center accuracy) ─
    agents = [
        {"id": "boler-benefits-agent",  "code": "BEN", "name": "Benefits Allocation Agent",
         "description": "Benefits allocation, reclassification + exception detection · Lambda + Bedrock",
         "color": "#6c47ff", "status": "Active", "status_detail": "AgentCore Connected",
         "accuracy_pct": 96.1, "docs_processed": 6, "docs_unit": "carrier files",
         "hitl_queue": 7, "avg_metric": "4.2 hrs", "avg_metric_label": "Processing Time"},
        {"id": "boler-exception-agent", "code": "EXC", "name": "Exception Resolution Agent",
         "description": "HITL exception review + approval routing · Step Functions",
         "color": "#ef4444", "status": "Active", "status_detail": "7 items in queue",
         "accuracy_pct": 98.2, "docs_processed": 7, "docs_unit": "exceptions",
         "hitl_queue": 2, "avg_metric": "2 HIGH", "avg_metric_label": "Critical Items"},
        {"id": "boler-je-agent",         "code": "JE",  "name": "Journal Entry Agent",
         "description": "Division journal entry generation + S3 distribution",
         "color": "#00c4a0", "status": "Active", "status_detail": "3 divisions ready",
         "accuracy_pct": 99.1, "docs_processed": 5, "docs_unit": "journal entries",
         "hitl_queue": 0, "avg_metric": "5 divisions", "avg_metric_label": "JEs Generated"},
        {"id": "boler-signal-agent",     "code": "SIG", "name": "Signal Agent",
         "description": "Predictive benefits intelligence + rate forecasting",
         "color": "#f59e0b", "status": "Active", "status_detail": "4 signals live",
         "accuracy_pct": 89.0, "docs_processed": 4, "docs_unit": "active signals",
         "hitl_queue": 0, "avg_metric": "89%", "avg_metric_label": "Model Confidence"},
        {"id": "boler-audit-agent",      "code": "AUD", "name": "Audit Lens Agent",
         "description": "Governance, lineage + DynamoDB audit trail",
         "color": "#2563eb", "status": "Active", "status_detail": "DynamoDB — 100% coverage",
         "accuracy_pct": 100, "docs_processed": 847, "docs_unit": "records logged",
         "hitl_queue": 0, "avg_metric": "100%", "avg_metric_label": "Audit Coverage"},
    ]

    # ── Agent Accuracy (Command Center bars) ───────────────────────────
    agent_accuracy = [
        {"name": "Benefits Allocation Agent", "accuracy_pct": 96.1, "color": "#00c4a0"},
        {"name": "Reclassification Engine",   "accuracy_pct": 94.3, "color": "#6c47ff"},
        {"name": "Exception Detection",       "accuracy_pct": 98.2, "color": "#00c4a0"},
        {"name": "Journal Entry Generation",  "accuracy_pct": 99.1, "color": "#00c4a0"},
        {"name": "Step Functions Routing",    "accuracy_pct": 100,  "color": "#00c4a0"},
    ]

    # ── Live Agent Activity Feed (Command Center) ──────────────────────
    activity_feed = [
        {"time": "09:41", "agent": "Benefits",      "agent_color": "#6c47ff",
         "message": "EXC-2026-0441 — Chen, R. reclassification applied. Hendrickson → Boler Holdings. $3,840/mo corrected.",
         "tag": "FIXED",       "tag_tone": "green"},
        {"time": "09:38", "agent": "Step Functions","agent_color": "#2563eb",
         "message": "Stage 2 approval notification sent to Ziggy Kravitz (CFO) via SES + SNS. Due Jun 6.",
         "tag": "ROUTED",      "tag_tone": "blue"},
        {"time": "09:35", "agent": "Signal",        "agent_color": "#f59e0b",
         "message": "Boler Holdings benefits trending +4.1% over budget. Rate change on Cigna medical — no rate card update on file.",
         "tag": "ALERT",       "tag_tone": "amber"},
        {"time": "09:31", "agent": "Benefits",      "agent_color": "#6c47ff",
         "message": "401k match rate mismatch — Fidelity shows 4.5%, HR policy is 4.0%. $8,240 delta flagged for Benefits Director review.",
         "tag": "FLAGGED",     "tag_tone": "amber"},
        {"time": "09:28", "agent": "Audit",         "agent_color": "#16a34a",
         "message": "Stage 1 approval logged — Sarah Mitchell, Benefits Director. 5 exceptions resolved, 2 overridden with notes.",
         "tag": "LOGGED",      "tag_tone": "green"},
        {"time": "09:22", "agent": "Benefits",      "agent_color": "#6c47ff",
         "message": "4 division transfer employees detected — still coded to prior division. $14,320 misallocation auto-fixed.",
         "tag": "AUTO-FIXED",  "tag_tone": "green"},
        {"time": "09:18", "agent": "Step Functions","agent_color": "#2563eb",
         "message": "Thompson, D. — terminated May 28, vision + dental still active. Benefits flagged for termination. $420 removed.",
         "tag": "REMOVED",     "tag_tone": "amber"},
        {"time": "09:14", "agent": "Benefits",      "agent_color": "#6c47ff",
         "message": "6 carrier files ingested from S3 intake bucket. 847 employees. $2,142,000 total. Extraction complete in 4.2 hrs.",
         "tag": "INGESTED",    "tag_tone": "green"},
    ]

    # ── Monthly trend chart (Command Center + Dashboard) ───────────────
    monthly_trend = _monthly_trend()

    # ── Apex Signal hero strip ─────────────────────────────────────────
    signal_hero = {
        "active_signals":   4,
        "variance_caught":  28_000,
        "forecasts_live":   3,
        "cycle":            CYCLE,
    }

    # ── Carrier Rate Drift chart (Signal panel 1) ──────────────────────
    carrier_drift = {
        "chart_labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "carriers": [
            {"name": "Cigna Medical",    "series": [0.5, 1.2, 1.8, 2.6, 3.4, 4.1], "color": "#ef4444",
             "current_drift_pct": 4.1, "renewal_days": 41, "alert_tone": "red"},
            {"name": "Delta Dental",      "series": [0.2, 0.4, 0.8, 1.1, 1.5, 1.8], "color": "#f59e0b",
             "current_drift_pct": 1.8, "renewal_days": 89, "alert_tone": "amber"},
            {"name": "VSP Vision",        "series": [0.0, 0.1, 0.1, 0.2, 0.2, 0.2], "color": "#9ca3af",
             "current_drift_pct": 0.2, "renewal_days": 145,"alert_tone": "green"},
            {"name": "Fidelity 401k",     "series": [0.1, 0.0, -0.1, 0.0, -0.1, -0.1], "color": "#0ea5e9",
             "current_drift_pct": -0.1,"renewal_days": 365,"alert_tone": "green"},
        ],
        "contract_cap_pct": 2.5,
        "alert_count":      1,
    }

    # ── Division Budget Variance Forecast (Signal panel 2) ─────────────
    budget_forecast = [
        {"division": "Hendrickson Intl", "budget_usd": 1_020_000, "forecast_usd": 1_041_420, "variance_pct": 2.1, "color": "#ef4444"},
        {"division": "Boler Holdings",   "budget_usd":   300_000, "forecast_usd":   312_300, "variance_pct": 4.1, "color": "#f59e0b"},
        {"division": "Mfg Services",     "budget_usd":   400_000, "forecast_usd":   392_800, "variance_pct": -1.8,"color": "#00c4a0"},
        {"division": "Real Estate",      "budget_usd":   180_000, "forecast_usd":   180_540, "variance_pct": 0.3, "color": "#9ca3af"},
        {"division": "Corp Shared Svcs", "budget_usd":   242_000, "forecast_usd":   236_192, "variance_pct": -2.4,"color": "#00c4a0"},
    ]

    # ── Open Enrollment Impact Forecast (Signal panel 3) ───────────────
    enrollment_forecast = {
        "current_ppo":          761,
        "hdhp_migration":        62,
        "new_dependents":        24,
        "ppo_to_hdhp_savings": -84_000,
        "new_dependent_cost":   62_000,
        "net_projected_savings":-22_000,
        "confidence_pct":        89,
    }

    # ── Live Signal Feed (Signal page bottom panel) ────────────────────
    signal_feed = [
        {"id": "SIG-001", "tone": "alert",    "tag": "ALERT",
         "title": "Cigna Rate Drift · Boler Holdings",
         "detail": "Billed rates trending +4.1% above contracted rate card over 90 days. Renewal in 41 days — no negotiation initiated."},
        {"id": "SIG-002", "tone": "warning",  "tag": "REVIEW",
         "title": "401k Match Rate Mismatch · Fidelity",
         "detail": "Fidelity file shows 4.5% match rate. HR policy document shows 4.0%. $8,240 delta in June cycle. Policy update or carrier correction needed."},
        {"id": "SIG-003", "tone": "warning",  "tag": "FORECAST",
         "title": "Hendrickson Intl Headcount Growth",
         "detail": "+12 new hires in Q2 not yet reflected in benefits budget. Projected $18,400/mo impact starting July. Budget amendment recommended."},
        {"id": "SIG-004", "tone": "watch",    "tag": "WATCH",
         "title": "Step Functions Workflow — Approval SLA",
         "detail": "Stage 2 approval (CFO) has been pending 18 hours. SLA is 24 hours. Distribution to divisions will be delayed if not actioned by 3pm today."},
        {"id": "SIG-005", "tone": "approved", "tag": "GOOD",
         "title": "Mfg Services — Under Budget",
         "detail": "Manufacturing Services division is tracking 1.8% under benefits budget YTD. $14,200 surplus available for reallocation or reserve."},
        {"id": "SIG-006", "tone": "approved", "tag": "COMPLETE",
         "title": "Audit Trail — 100% Coverage",
         "detail": "All 847 employee records, 6 carrier files, 3 approval stages, and 7 exceptions fully logged in DynamoDB. Audit-ready for any review."},
    ]

    # ── HITL Queue (Agent Hub left rail + Human Review) ────────────────
    hitl_queue = [
        {"id": "EXC-2026-0441", "title": "Chen, R. — Wrong Division",
         "subtitle": "Needs Review · $3,840 variance", "severity": "HIGH"},
        {"id": "EXC-2026-0442", "title": "Martinez, L. — Duplicate COBRA",
         "subtitle": "Needs Review · $1,240 overcharge", "severity": "HIGH"},
        {"id": "JE-2026-0031", "title": "Hendrickson JE — Pending CFO",
         "subtitle": "Stage 2 Approval · $1,042,800", "severity": "MEDIUM"},
        {"id": "SIG-2026-0012", "title": "Cigna Rate Alert — Boler Holdings",
         "subtitle": "Signal Review · +4.1% drift", "severity": "MEDIUM"},
    ]

    # ── AWS Architecture (right-rail "Connected Systems") ──────────────
    aws_architecture = [
        {"layer": "File Intake",    "service": "Amazon S3 (restricted bucket)",
         "role":  "Carrier files dropped by HR/Benefits team"},
        {"layer": "Extraction",     "service": "AWS Lambda + Amazon Bedrock",
         "role":  "Document parsing, field extraction, reclassification"},
        {"layer": "Orchestration",  "service": "AWS Step Functions",
         "role":  "Multi-stage approval workflow, SLA enforcement"},
        {"layer": "Storage",        "service": "Amazon DynamoDB",
         "role":  "Audit ledger, exception records, allocation history"},
        {"layer": "Notifications",  "service": "Amazon SES + SNS",
         "role":  "Approval requests, exception alerts, distribution emails"},
        {"layer": "Analytics",      "service": "Amazon QuickSight",
         "role":  "Division dashboards, trend charts, CFO reporting"},
        {"layer": "AI/LLM",          "service": "Amazon Bedrock (Claude)",
         "role":  "Agent intelligence, exception reasoning, narrative generation"},
        {"layer": "Security",       "service": "AWS IAM + KMS",
         "role":  "Role-based access, encryption at rest and in transit"},
    ]

    return {
        "cycle":               CYCLE,
        "total_employees":     TOTAL_EMPLOYEES,
        "total_divisions":     TOTAL_DIVISIONS,
        "kpis":                kpis,
        "workflow":            workflow,
        "carrier_files":       carrier_files,
        "divisions":           divisions,
        "exceptions":          exceptions,
        "approval_queue":      approval_queue,
        "je_preview":          je_preview,
        "audit_log":           audit_log,
        "agents":              agents,
        "agent_accuracy":      agent_accuracy,
        "activity_feed":       activity_feed,
        "monthly_trend":       monthly_trend,
        "signal_hero":         signal_hero,
        "carrier_drift":       carrier_drift,
        "budget_forecast":     budget_forecast,
        "enrollment_forecast": enrollment_forecast,
        "signal_feed":         signal_feed,
        "hitl_queue":          hitl_queue,
        "aws_architecture":    aws_architecture,
        "generated_at":        now.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────
# HITL mutation routes — Exception action buttons (Apply / Override / etc)
# In-memory audit-only · same pattern as cwfcu.py.
# ─────────────────────────────────────────────────────────────────────
BOLER_ACTION_LOG: list = []


def _log_boler_action(action: str, item_id: str, **details) -> Dict[str, Any]:
    entry = {
        "ts":      datetime.now(timezone.utc).isoformat(),
        "action":  action,
        "item_id": item_id,
        **details,
    }
    BOLER_ACTION_LOG.append(entry)
    return entry


@router.post("/exceptions/{exc_id}/apply-reclassification")
async def boler_apply_reclass(exc_id: str) -> Dict[str, Any]:
    entry = _log_boler_action("apply_reclassification", exc_id)
    return {
        "ok": True,
        "toast": {
            "tone": "success",
            "title": f"{exc_id} reclassification applied",
            "detail": "DynamoDB audit logged · downstream JEs regenerated · SES notification sent",
        },
        "audit_entry": entry,
    }


@router.post("/exceptions/{exc_id}/override")
async def boler_override_with_note(exc_id: str, note: str = "") -> Dict[str, Any]:
    entry = _log_boler_action("override_with_note", exc_id, note_len=len(note))
    return {
        "ok": True,
        "toast": {
            "tone": "warn",
            "title": f"{exc_id} overridden with note",
            "detail": f"Override recorded · {len(note)} char note · audit logged",
        },
        "audit_entry": entry,
    }


@router.post("/exceptions/{exc_id}/remove-allocation")
async def boler_remove_allocation(exc_id: str) -> Dict[str, Any]:
    entry = _log_boler_action("remove_allocation", exc_id)
    return {
        "ok": True,
        "toast": {
            "tone": "success",
            "title": f"{exc_id} removed from allocation",
            "detail": "Catch-up credit applied to division JE · DynamoDB audit logged",
        },
        "audit_entry": entry,
    }


@router.post("/exceptions/{exc_id}/dismiss")
async def boler_dismiss(exc_id: str, reason: str = "no_action_needed") -> Dict[str, Any]:
    entry = _log_boler_action("dismiss", exc_id, reason=reason)
    return {
        "ok": True,
        "toast": {
            "tone": "warn",
            "title": f"{exc_id} dismissed",
            "detail": f"Reason: {reason} · entry persists in DynamoDB audit log",
        },
        "audit_entry": entry,
    }


@router.post("/je/{je_id}/distribute")
async def boler_distribute_je(je_id: str) -> Dict[str, Any]:
    entry = _log_boler_action("distribute_je", je_id)
    return {
        "ok": True,
        "toast": {
            "tone": "success",
            "title": f"{je_id} distribution triggered",
            "detail": "Step Functions launched · S3 distribution to division controllers · SES + SNS notifications fired",
        },
        "audit_entry": entry,
    }


# ─────────────────────────────────────────────────────────────────────
# Signal individual endpoints (deterministic — no SageMaker)
# ─────────────────────────────────────────────────────────────────────
@router.get("/signals/carrier-rate-drift")
async def signal_carrier_drift() -> Dict[str, Any]:
    state = await boler_dashboard_state()
    return {"name": "Carrier Rate Drift", "drift": state["carrier_drift"]}


@router.get("/signals/budget-variance-forecast")
async def signal_budget_forecast() -> Dict[str, Any]:
    state = await boler_dashboard_state()
    return {"name": "Division Budget Variance Forecast", "forecast": state["budget_forecast"]}


@router.get("/signals/open-enrollment-forecast")
async def signal_enrollment_forecast() -> Dict[str, Any]:
    state = await boler_dashboard_state()
    return {"name": "Open Enrollment Impact Forecast", "forecast": state["enrollment_forecast"]}
