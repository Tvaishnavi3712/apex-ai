"""
CWFCU (CommunityWide Federal Credit Union) demo backend.

Single consolidated endpoint `/api/v1/cwfcu/dashboard-state` hydrates the 4
frontend pages (Dashboard, Command Center, Apex Signal, Human Review). No
hardcoded UI values — every screen reads from this payload.

Mirrors the EPROD pattern in `eprod_cycle.py`. SageMaker / AgentCore are
intentionally skipped for round 1 of this demo per the customer brief —
all signal endpoints return deterministic fixtures grounded on the
synthetic-data/cwfcu/ corpus + the agent-hub.html / dashboard.html /
signal.html / command-center.html / hitl.html mockups.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────
# Demo anchor constants — keep in sync with frontend mockups.
# Single source of truth so every screen displays the same numbers.
# ─────────────────────────────────────────────────────────────────────
EXAM_DATE = "2026-07-21"        # NCUA exam window opens
TODAY = "2026-06-04"
DAYS_TO_EXAM = 47

# Per-folder NCUA exam readiness (matches dashboard.html + command-center.html)
FOLDER_SCORES = {
    "cip_records":      100,
    "bsa_aml":           96,
    "credit_risk":       91,
    "third_party_risk":  82,
    "hr_policy":         88,
}
# weighted aggregate (equal weights → 87% headline, matches mockups)
READINESS_OVERALL = 87
READINESS_TARGET  = 97


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
def _deterministic_30d_throughput() -> Dict[str, List[Dict[str, Any]]]:
    """30-day docs-processed series anchored at 214/day with weekly seasonality.

    Stable across reloads via a date-derived seed. Mirrors EPROD's pattern.
    """
    now = datetime.now(timezone.utc)
    base = now.date()
    days = [(base - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    docs, hitl = [], []
    for i, d in enumerate(days):
        dow = (i + 4) % 7
        seasonal = 1.0 if dow < 5 else 0.72  # weekends quieter for a CU
        seed_val = (sum(ord(c) for c in d) * 17) % 50
        v = int(round(214 * seasonal + (seed_val - 25) * 0.7))
        h = int(round(v * 0.038 + ((seed_val % 5) - 2) * 0.3))
        docs.append({"date": d, "value": max(64, v)})
        hitl.append({"date": d, "value": max(2, h)})
    return {"docs_processed": docs, "hitl_routed": hitl}


# ─────────────────────────────────────────────────────────────────────
# GET /cwfcu/dashboard-state
# Consolidated payload that hydrates all 4 CWFCU pages.
# ─────────────────────────────────────────────────────────────────────
@router.get("/dashboard-state")
async def cwfcu_dashboard_state() -> Dict[str, Any]:
    """Consolidated CWFCU demo data feed.

    Returns:
      kpis            — 4 headline KPIs (docs, compliance risk, loan time, exam readiness)
      exam_readiness  — headline + per-folder scores + days-to-exam + trajectory
      agents          — 5-agent status with per-agent metrics + hand-off chain
      throughput_30d  — 30-day daily docs processed + HITL routed
      processing_feed — live agent activity feed (terminal-style)
      hitl_queue      — Human Review queue items
      sar_viewer      — SAR Intelligence Viewer (2 SARs with auto-narrative)
      loan_pipeline   — Active Loan Pipeline table (5 loans)
      agent_accuracy  — per-agent accuracy bars
      signal_hero     — Apex Signal hero strip
      vendor_drift    — Vendor Rate Drift chart data (3 vendors)
      regulatory      — NCUA Regulatory Monitor (3 changes)
      exam_trajectory — Exam Readiness Forecast chart data
      signal_feed     — Live Signal Feed grid (6 tiles)
      agent_impact    — Before/After metrics per agent
      generated_at    — server timestamp
    """
    now = datetime.now(timezone.utc)

    # ── KPI strip (dashboard.html + command-center.html) ────────────
    kpis = {
        "docs_processed_mtd":       4812,
        "docs_processed_today":     214,
        "docs_today_delta_pct":     18,
        "compliance_risk_caught_usd": 1_200_000,
        "loan_processing_days":     1.4,
        "loan_processing_baseline_days": 6.2,
        "ncua_exam_readiness_pct":  READINESS_OVERALL,
        "ncua_exam_readiness_delta_pts": 14,   # +14 pts last 30 days
        "hitl_queue_pending":       8,
        "hitl_avg_wait_min":        12,
        "sars_auto_drafted_today":  7,
        "sars_pending_review":      2,
        "loan_packets_cleared_today": 31,
    }

    # ── NCUA exam readiness block (the centerpiece) ─────────────────
    exam_readiness = {
        "overall_pct":   READINESS_OVERALL,
        "target_pct":    READINESS_TARGET,
        "exam_date":     EXAM_DATE,
        "days_to_exam":  DAYS_TO_EXAM,
        "projection_pct": 97,
        "projection_date": "2026-07-14",
        "trajectory_msg": (
            "At current trajectory, APEX will have exam readiness at 97%+ "
            "by July 21 — 6 days before your exam window opens."
        ),
        "folder_scores": [
            {"name": "BSA/AML Program Docs",     "pct": FOLDER_SCORES["bsa_aml"],         "tone": "good"},
            {"name": "Loan Underwriting Files",  "pct": FOLDER_SCORES["credit_risk"],     "tone": "good"},
            {"name": "Member CDD Records",       "pct": 88,                                "tone": "good"},
            {"name": "Vendor Risk Documentation", "pct": FOLDER_SCORES["third_party_risk"],"tone": "warn"},
            {"name": "Board Policy Acknowledgments","pct": 74,                            "tone": "bad"},
        ],
        "auto_assembled_pct": 94,
        "manual_categories_remaining": 3,
    }

    # ── 5-agent status (dashboard.html agent grid + command-center accuracy) ─
    agents = [
        {
            "id": "cwfcu-compliance-agent",
            "name": "Compliance Agent",
            "code": "COM",
            "icon": "shield",
            "icon_bg": "#f0fdf4",
            "accent": "#6c47ff",
            "status": "live",
            "description": "BSA/AML · SAR narratives · NCUA exam prep",
            "primary_metric": {"label": "SARs processed this month", "value": "142"},
            "secondary_metric": {"label": "Accuracy", "value": "96.1%"},
            "fill_pct": 96,
            "fill_color": "#6c47ff",
            "hand_offs": {
                "receives_from": ["cwfcu-onboarding-agent"],
                "sends_to":      ["cwfcu-loan-agent", "cwfcu-policy-agent"],
            },
        },
        {
            "id": "cwfcu-loan-agent",
            "name": "Loan Document Agent",
            "code": "LDA",
            "icon": "document",
            "icon_bg": "#eff6ff",
            "accent": "#2563eb",
            "status": "live",
            "description": "Application packets · Underwriting · Missing docs",
            "primary_metric": {"label": "Loan packets processed", "value": "318"},
            "secondary_metric": {"label": "Straight-through", "value": "93.8%"},
            "fill_pct": 94,
            "fill_color": "#2563eb",
            "hand_offs": {
                "receives_from": ["cwfcu-compliance-agent"],
                "sends_to":      ["cwfcu-vendor-agent"],
            },
        },
        {
            "id": "cwfcu-onboarding-agent",
            "name": "Member Onboarding Agent",
            "code": "ONB",
            "icon": "user",
            "icon_bg": "#faf5ff",
            "accent": "#7c3aed",
            "status": "live",
            "description": "Account opening · ID verification · OFAC screening",
            "primary_metric": {"label": "New members onboarded", "value": "204"},
            "secondary_metric": {"label": "OFAC coverage", "value": "100%"},
            "fill_pct": 100,
            "fill_color": "#7c3aed",
            "hand_offs": {
                "receives_from": [],
                "sends_to":      ["cwfcu-compliance-agent"],
            },
        },
        {
            "id": "cwfcu-vendor-agent",
            "name": "Vendor & Contract Agent",
            "code": "VND",
            "icon": "handshake",
            "icon_bg": "#fff7ed",
            "accent": "#d97706",
            "status": "active",
            "description": "Third-party risk · Contract obligations · Renewals",
            "primary_metric": {"label": "Vendor contracts monitored", "value": "47"},
            "secondary_metric": {"label": "Renewals due 30 days", "value": "3"},
            "fill_pct": 78,
            "fill_color": "#d97706",
            "hand_offs": {
                "receives_from": ["cwfcu-loan-agent"],
                "sends_to":      ["cwfcu-policy-agent"],
            },
        },
        {
            "id": "cwfcu-policy-agent",
            "name": "Policy & HR Agent",
            "code": "POL",
            "icon": "clipboard",
            "icon_bg": "#f0f2f5",
            "accent": "#0d1f35",
            "status": "active",
            "description": "Policy acknowledgments · Training docs · Audit records",
            "primary_metric": {"label": "Employee records current", "value": "84"},
            "secondary_metric": {"label": "Acknowledgment rate", "value": "98.8%"},
            "fill_pct": 99,
            "fill_color": "#0d1f35",
            "hand_offs": {
                "receives_from": ["cwfcu-vendor-agent", "cwfcu-compliance-agent"],
                "sends_to":      [],
            },
        },
    ]

    # ── APEX Signal headline (dark agent card in dashboard.html) ────
    apex_signal = {
        "active_signals": 12,
        "critical_signals": 3,
        "fill_pct": 72,
    }

    # ── Agent Accuracy bars (command-center.html) ───────────────────
    agent_accuracy = [
        {"name": "Compliance Agent",       "accuracy_pct": 96.1, "color": "#00c4a0"},
        {"name": "Loan Document Agent",    "accuracy_pct": 93.8, "color": "#2563eb"},
        {"name": "Member Onboarding Agent","accuracy_pct": 97.2, "color": "#7c3aed"},
        {"name": "Vendor & Contract Agent","accuracy_pct": 91.4, "color": "#d97706"},
        {"name": "Policy & HR Agent",      "accuracy_pct": 98.8, "color": "#6c47ff"},
    ]

    # ── HITL queue (dashboard.html bottom-left panel) ───────────────
    hitl_queue = [
        {
            "id": "SAR-2026-0142",
            "doc": "SAR — Member #44821 · Structuring Pattern",
            "agent": "Compliance Agent",
            "priority": "HIGH",
            "tone": "red",
            "flagged_minutes_ago": 14,
            "action": "review",
        },
        {
            "id": "LN-2026-0441",
            "doc": "Loan Packet — Johnson, M. · Missing W-2 (2024)",
            "agent": "Loan Doc Agent",
            "priority": "HIGH",
            "tone": "red",
            "flagged_minutes_ago": 31,
            "action": "review",
        },
        {
            "id": "VND-FISERV-2026",
            "doc": "Vendor Contract — Fiserv Core Services · Expiring Jul 1",
            "agent": "Vendor Agent",
            "priority": "MEDIUM",
            "tone": "amber",
            "flagged_minutes_ago": 27 * 24 * 60,
            "action": "review",
            "days_remaining": 27,
        },
        {
            "id": "CDD-2026-0391",
            "doc": "CDD Review — Member #39104 · High-risk occupation",
            "agent": "Compliance Agent",
            "priority": "MEDIUM",
            "tone": "amber",
            "flagged_minutes_ago": 120,
            "action": "review",
        },
        {
            "id": "ONB-2026-0201",
            "doc": "Onboarding — Torres, R. · ID verified · Ready to approve",
            "agent": "Onboarding Agent",
            "priority": "LOW",
            "tone": "green",
            "flagged_minutes_ago": 8,
            "action": "approve",
        },
        {
            "id": "ONB-2026-0200",
            "doc": "Onboarding — Anderson, P. · PEP hit · low-risk review",
            "agent": "Onboarding Agent",
            "priority": "MEDIUM",
            "tone": "amber",
            "flagged_minutes_ago": 42,
            "action": "review",
        },
        {
            "id": "LN-2026-0517",
            "doc": "Loan Packet — Williams, D. · 2025 tax return missing",
            "agent": "Loan Doc Agent",
            "priority": "LOW",
            "tone": "green",
            "flagged_minutes_ago": 60,
            "action": "review",
        },
        {
            "id": "POL-2026-0044",
            "doc": "Policy Ack — 22 employees overdue BSA/AML training",
            "agent": "Policy Agent",
            "priority": "MEDIUM",
            "tone": "amber",
            "flagged_minutes_ago": 240,
            "action": "review",
        },
    ]

    # ── Live Agent Activity Feed (command-center.html) ──────────────
    processing_feed = [
        {"time": "09:41", "agent": "Compliance", "color": "#00c4a0",
         "message": "SAR-2026-0441 narrative generated — structuring pattern confirmed across 14 transactions",
         "tag": "HIGH", "tag_tone": "red"},
        {"time": "09:38", "agent": "Loan Doc", "color": "#2563eb",
         "message": "Johnson, M. — loan packet 94% complete. Missing: 2024 W-2. Member notification sent via CWAnyWhere.",
         "tag": "ACTION", "tag_tone": "amber"},
        {"time": "09:35", "agent": "Onboarding", "color": "#7c3aed",
         "message": "Torres, R. — OFAC clear, ID verified, CIP complete. Account ready for approval.",
         "tag": "CLEAR", "tag_tone": "green"},
        {"time": "09:31", "agent": "Vendor", "color": "#d97706",
         "message": "Fiserv Core Services contract expires Jul 1 — 27 days. Renewal package assembled. Routed to IT Director.",
         "tag": "RENEW", "tag_tone": "amber"},
        {"time": "09:28", "agent": "Compliance", "color": "#00c4a0",
         "message": "FinCEN AML/CFT rule update detected — policy gap analysis initiated. 3 procedures flagged for update.",
         "tag": "REG", "tag_tone": "red"},
        {"time": "09:22", "agent": "Loan Doc", "color": "#2563eb",
         "message": "Garcia, L. — auto loan packet complete. All docs verified. Routed to underwriter for final review.",
         "tag": "READY", "tag_tone": "green"},
        {"time": "09:18", "agent": "Onboarding", "color": "#7c3aed",
         "message": "Williams, D. — ID document quality insufficient. Member notified to re-upload via CWAnyWhere app.",
         "tag": "RETRY", "tag_tone": "amber"},
        {"time": "09:14", "agent": "Compliance", "color": "#00c4a0",
         "message": "NCUA exam readiness score updated: 87% (+2 pts). Board policy acknowledgments still at 74% — 22 employees pending.",
         "tag": "EXAM", "tag_tone": "teal"},
        {"time": "09:08", "agent": "Loan Doc", "color": "#2563eb",
         "message": "Batch: 18 mortgage packets ingested from Encompass LOS. Extraction complete. 16 straight-through, 2 to HITL.",
         "tag": "BATCH", "tag_tone": "green"},
    ]

    # ── SAR Intelligence Viewer (command-center.html top-left) ──────
    sar_viewer = [
        {
            "sar_id": "SAR-2026-0441",
            "subject_member": "#44821",
            "summary": "Structuring · 14 transactions · 22 days",
            "amount_usd": 48200,
            "narrative": (
                "On or about May 12 through June 3, 2026, the subject conducted 14 cash deposits "
                "totaling $48,200 at CommunityWide FCU branches in South Bend and Mishawaka, Indiana. "
                "Individual transactions ranged from $2,800 to $4,900, consistent with a pattern "
                "designed to avoid the $10,000 currency transaction reporting threshold..."
            ),
            "description": (
                "Compliance Agent detected 14 cash deposits ranging from $2,800 to $4,900 over a 22-day "
                "period — consistent with structuring to avoid $10,000 CTR threshold. Member occupation: "
                "independent contractor. No prior SAR history."
            ),
            "actions": ["approve_and_file", "edit_narrative", "dismiss"],
            "priority": "HIGH",
        },
        {
            "sar_id": "SAR-2026-0442",
            "subject_member": "#39104",
            "summary": "High-risk CDD · Wire transfers · 3 countries",
            "amount_usd": 22400,
            "narrative": None,
            "description": (
                "CDD review flagged wire transfers to 3 high-risk jurisdictions. Member opened account "
                "4 months ago. Narrative auto-drafted — awaiting compliance officer review."
            ),
            "actions": ["open_for_review"],
            "priority": "MEDIUM",
        },
    ]

    # ── Active Loan Pipeline (command-center.html bottom-left) ──────
    loan_pipeline = [
        {"member": "Johnson, Marcus",   "type": "Home Equity", "amount_usd":  85000,
         "progress_pct": 94,  "progress_color": "#f59e0b", "progress_label": "Missing W-2",
         "status": "PENDING",     "status_color": "#d97706"},
        {"member": "Garcia, Lucia",     "type": "Auto Loan",   "amount_usd":  28400,
         "progress_pct": 100, "progress_color": "#00c4a0", "progress_label": "All docs verified",
         "status": "READY",       "status_color": "#16a34a"},
        {"member": "Patel, Anita",      "type": "Mortgage",    "amount_usd": 215000,
         "progress_pct": 78,  "progress_color": "#2563eb", "progress_label": "Underwriting review",
         "status": "REVIEW",      "status_color": "#2563eb"},
        {"member": "Williams, Darnell", "type": "Personal",    "amount_usd":  12500,
         "progress_pct": 62,  "progress_color": "#6c47ff", "progress_label": "Income verification",
         "status": "IN PROGRESS", "status_color": "#7c3aed"},
        {"member": "Chen, Robert",      "type": "Home Equity", "amount_usd":  62000,
         "progress_pct": 100, "progress_color": "#00c4a0", "progress_label": "All docs verified — approved",
         "status": "APPROVED",    "status_color": "#16a34a"},
    ]

    # ── Apex Signal hero strip (signal.html) ────────────────────────
    signal_hero = {
        "days_to_exam":      DAYS_TO_EXAM,
        "exam_date":         EXAM_DATE,
        "readiness_pct":     READINESS_OVERALL,
        "active_signals":    12,
        "critical_signals":  3,
        "updated_minutes_ago": 2,
    }

    # ── Vendor Rate Drift (signal.html panel 1) ─────────────────────
    vendor_drift = {
        "chart_labels": ["Apr 1", "Apr 15", "May 1", "May 15", "Jun 1", "Jun 4"],
        "vendors": [
            {"name": "Fiserv",      "series": [0.8, 1.2, 2.1, 3.8, 5.2, 6.1],
             "color": "#ef4444", "current_drift_pct": 6.1, "renewal_days": 27, "alert_tone": "red"},
            {"name": "Eltropy",     "series": [0.5, 0.9, 1.6, 2.8, 3.7, 4.2],
             "color": "#f59e0b", "current_drift_pct": 4.2, "renewal_days": 41, "alert_tone": "amber"},
            {"name": "Jack Henry",  "series": [0.3, 0.6, 1.0, 1.7, 2.3, 2.8],
             "color": "#6c47ff", "current_drift_pct": 2.8, "renewal_days": 89, "alert_tone": "amber"},
        ],
        "contract_limit_pct": 2.0,
        "alert_count": 3,
    }

    # ── NCUA Regulatory Monitor (signal.html panel 2) ───────────────
    regulatory = [
        {
            "severity": "HIGH IMPACT",
            "effective": "Jul 1, 2026",
            "title": "FinCEN AML/CFT Program Rule — Final",
            "description": (
                "Risk-based AML program requirements updated. CW FCU policy gap analysis: "
                "3 procedures need update. APEX has drafted revisions."
            ),
            "action_required": "Action required before Jul 1",
            "tone": "red",
        },
        {
            "severity": "MEDIUM IMPACT",
            "effective": "Sep 1, 2026",
            "title": "NCUA Fair Lending Exam Procedures Update",
            "description": (
                "Updated HMDA data collection requirements. Loan Document Agent will auto-update "
                "extraction templates. No manual action required."
            ),
            "action_required": None,
            "tone": "amber",
        },
        {
            "severity": "LOW IMPACT",
            "effective": "Informational",
            "title": "CFPB Small Business Lending Data Rule",
            "description": (
                "CW FCU below $100M threshold — monitoring only. No action required at this time."
            ),
            "action_required": None,
            "tone": "green",
        },
    ]

    # ── Exam Readiness Forecast (signal.html panel 3) ───────────────
    exam_trajectory = {
        "chart_labels":   ["May 1", "May 15", "Jun 1", "Jun 4", "Jun 15", "Jul 1", "Jul 14", "Jul 21"],
        "actual_series":  [72, 76, 83, 87, None, None, None, None],
        "projected_series":[None, None, None, 87, 91, 94, 97, 97],
        "target_series":  [97, 97, 97, 97, 97, 97, 97, 97],
        "folder_bars": [
            {"name": "BSA/AML Documentation",   "pct": 96, "color": "#00c4a0"},
            {"name": "Credit Risk Records",     "pct": 91, "color": "#2563eb"},
            {"name": "Third-Party Risk Docs",   "pct": 82, "color": "#d97706"},
            {"name": "Policy Acknowledgments",  "pct": 74, "color": "#ef4444"},
            {"name": "CIP / Member Records",    "pct": 100,"color": "#00c4a0"},
        ],
        "on_track": True,
    }

    # ── Live Signal Feed (signal.html bottom panel) ─────────────────
    signal_feed = [
        {"tone": "alert",    "agent": "Compliance Agent",
         "title": "Structuring Pattern — Member #44821",
         "detail": "7 cash deposits · $47,300 · 4 branches · SAR deadline Jun 27"},
        {"tone": "warning",  "agent": "Vendor Agent",
         "title": "Fiserv Contract Auto-Renewal TODAY",
         "detail": "27 days remaining · $2.1M annual value · No action taken yet"},
        {"tone": "warning",  "agent": "Policy Agent",
         "title": "BSA Training — 22 Employees Overdue",
         "detail": "74% completion · NCUA exam requirement · 47 days to exam"},
        {"tone": "clear",    "agent": "Onboarding Agent",
         "title": "Torres, R. — CIP Complete",
         "detail": "OFAC clear · ID verified · PEP negative · Ready to open"},
        {"tone": "approved", "agent": "Loan Agent",
         "title": "Garcia, L. — Auto Loan Ready",
         "detail": "$28,400 · All docs verified · Routed to underwriter"},
        {"tone": "forecast", "agent": "Signal",
         "title": "Exam Readiness: 87% → 97%",
         "detail": "Projected by Jul 14 at current pace · 3 open items blocking 100%"},
    ]

    # ── Agent Impact (before / after) ───────────────────────────────
    agent_impact = [
        {"agent": "Member Onboarding Agent",
         "before": {"label": "Manual baseline", "value": "47 min per new member"},
         "after":  {"label": "With Apex",       "value": "11 min 42 sec"},
         "delta":  "-75%"},
        {"agent": "Compliance Agent",
         "before": {"label": "Manual baseline", "value": "2.4 hours per SAR draft"},
         "after":  {"label": "With Apex",       "value": "3 sec (96.1% accuracy)"},
         "delta":  "-99%"},
        {"agent": "Loan Document Agent",
         "before": {"label": "Manual baseline", "value": "6.2 days doc-to-decision"},
         "after":  {"label": "With Apex",       "value": "1.4 days"},
         "delta":  "-77%"},
        {"agent": "Vendor & Contract Agent",
         "before": {"label": "Annual spend",    "value": "Reactive renewals · ~$96K leakage"},
         "after":  {"label": "With Apex",       "value": "Proactive · $0 missed renewals"},
         "delta":  "100% caught"},
        {"agent": "Policy & HR Agent",
         "before": {"label": "Manual baseline", "value": "6 weeks of pre-exam scramble"},
         "after":  {"label": "With Apex",       "value": "Continuous · exam-ready any day"},
         "delta":  "-100% scramble"},
    ]

    return {
        "kpis":             kpis,
        "exam_readiness":   exam_readiness,
        "agents":           agents,
        "apex_signal":      apex_signal,
        "agent_accuracy":   agent_accuracy,
        "throughput_30d":   _deterministic_30d_throughput(),
        "processing_feed":  processing_feed,
        "hitl_queue":       hitl_queue,
        "sar_viewer":       sar_viewer,
        "loan_pipeline":    loan_pipeline,
        "signal_hero":      signal_hero,
        "vendor_drift":     vendor_drift,
        "regulatory":       regulatory,
        "exam_trajectory":  exam_trajectory,
        "signal_feed":      signal_feed,
        "agent_impact":     agent_impact,
        "generated_at":     now.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────
# Individual signal endpoints (deterministic — no SageMaker)
# ─────────────────────────────────────────────────────────────────────
@router.get("/signals/exam-readiness-forecast")
async def signal_exam_readiness_forecast() -> Dict[str, Any]:
    state = await cwfcu_dashboard_state()
    return {
        "name":         "NCUA Exam Readiness Forecast",
        "current_pct":  state["exam_readiness"]["overall_pct"],
        "target_pct":   state["exam_readiness"]["target_pct"],
        "exam_date":    EXAM_DATE,
        "days_to_exam": DAYS_TO_EXAM,
        "trajectory":   state["exam_trajectory"],
        "projection_pct": state["exam_readiness"]["projection_pct"],
        "projection_date": state["exam_readiness"]["projection_date"],
        "on_track":     True,
    }


@router.get("/signals/vendor-renewal-risk")
async def signal_vendor_renewal_risk() -> Dict[str, Any]:
    state = await cwfcu_dashboard_state()
    return {
        "name":      "Vendor Renewal Risk",
        "drift":     state["vendor_drift"],
        "critical_renewals": [
            {"vendor": "Fiserv",     "days": 27,  "annual_usd": 2_100_000, "tone": "red"},
            {"vendor": "Eltropy",    "days": 41,  "annual_usd":   180_000, "tone": "amber"},
            {"vendor": "Jack Henry", "days": 89,  "annual_usd":    96_000, "tone": "amber"},
            {"vendor": "Heartland",  "days": 118, "annual_usd":   142_000, "tone": "green"},
        ],
    }


@router.get("/signals/delinquency-early-warning")
async def signal_delinquency_early_warning() -> Dict[str, Any]:
    """Deterministic delinquency early-warning signal (no SageMaker)."""
    return {
        "name":       "Loan Delinquency Early Warning",
        "current_30d_rate_pct": 2.1,
        "trend":      [
            {"date": "2026-01", "rate_pct": 1.6},
            {"date": "2026-02", "rate_pct": 1.8},
            {"date": "2026-03", "rate_pct": 1.9},
            {"date": "2026-04", "rate_pct": 2.0},
            {"date": "2026-05", "rate_pct": 2.1},
        ],
        "peer_avg_pct": 2.4,
        "interpretation": "CWFCU below national CU peer average — early-warning indicators stable.",
        "watch_items": [
            "12 personal loans in 1-29 day late bucket (was 8 last month)",
            "2 HELOC files in 30-59 day late (no change from prior month)",
            "Self-employed segment delinquency +0.3 pts MoM",
        ],
    }


@router.get("/signals/regulatory-change-monitor")
async def signal_regulatory_change_monitor() -> Dict[str, Any]:
    state = await cwfcu_dashboard_state()
    return {
        "name":   "Regulatory Change Monitor",
        "changes": state["regulatory"],
        "sources_monitored": [
            "FinCEN regulatory feed (live)",
            "NCUA exam guidance",
            "CFPB enforcement actions",
            "FFIEC guidance updates",
            "State NCUA-equivalent regulators (IN, MI)",
        ],
    }


# ─────────────────────────────────────────────────────────────────────
# HITL queue endpoints
# ─────────────────────────────────────────────────────────────────────
@router.get("/hitl/pending")
async def cwfcu_hitl_pending() -> Dict[str, Any]:
    state = await cwfcu_dashboard_state()
    return {
        "items": state["hitl_queue"],
        "summary": {
            "total":      len(state["hitl_queue"]),
            "high":       sum(1 for i in state["hitl_queue"] if i["priority"] == "HIGH"),
            "medium":     sum(1 for i in state["hitl_queue"] if i["priority"] == "MEDIUM"),
            "low":        sum(1 for i in state["hitl_queue"] if i["priority"] == "LOW"),
            "avg_wait_min": 12,
            "agent_confidence_avg_pct": 95,
        },
    }


@router.get("/hitl/item/{item_id}")
async def cwfcu_hitl_item_detail(item_id: str) -> Dict[str, Any]:
    """Per-item HITL detail. SAR-2026-0142 returns the structuring deep-dive
    (matches hitl.html). Other ids return a slimmer demo detail derived from
    the queue summary."""
    if item_id == "SAR-2026-0142":
        return await cwfcu_hitl_current_item()

    # Lookup item in the queue
    state = await cwfcu_dashboard_state()
    queue_item = next((it for it in state["hitl_queue"] if it["id"] == item_id), None)
    if not queue_item:
        return {"item_id": item_id, "error": "not_found"}

    # Build a slim detail packet matching the same shape as current_item but
    # tailored to whatever this HITL row is (loan, vendor, CDD, onboarding).
    title = queue_item["doc"]
    priority = queue_item["priority"]
    agent = queue_item["agent"]

    # Item-specific overrides
    overrides: Dict[str, Any] = {
        "LN-2026-0441": {
            "type": "LOAN PACKET",
            "subject_member": "#51122 (Johnson, M.)",
            "key_findings": [
                "HELOC $85,000 requested · 10-yr draw / 20-yr repay",
                "Property: 5808 Cleveland Rd, Granger, IN — estimated value $385K",
                "Combined LTV 72% (within HELOC policy ≤85%)",
                "FICO 742 · DTI 21% front / 39.8% back · within HELOC policy",
                "MISSING: 2024 W-2 from St Joseph Regional Med Ctr · CWAnyWhere reminder cycle active",
            ],
            "narrative": (
                "Loan packet ingested via CWAnyWhere on 2026-05-30. 15 of 16 required documents "
                "received and validated at 96.7% confidence. Member notified via CWAnyWhere + email "
                "on 2026-05-30 and 2026-06-01 for missing 2024 W-2. Appraisal scheduled with "
                "Heartland Valuation for 2026-06-10. Hold until W-2 receipt + appraisal complete."
            ),
            "regulatory_context": [
                "12 CFR § 1026.43 — Ability-to-Repay (ATR) requirement",
                "Reg Z TRID disclosures required at closing",
                "Indiana HELOC max LTV 85% combined",
            ],
            "ncua_exam_impact": "Routes into Credit Risk folder · contributes to 91% folder score",
            "actions_available": [
                {"id": "approve", "label": "Approve packet",           "tone": "primary"},
                {"id": "request_docs", "label": "Request docs again",   "tone": "secondary"},
                {"id": "decline",  "label": "Decline",                   "tone": "secondary"},
            ],
        },
        "VND-FISERV-2026": {
            "type": "VENDOR CONTRACT",
            "subject_member": "Fiserv Solutions LLC",
            "key_findings": [
                "Contract VND-FISERV-CORE-2024 · auto-renewal deadline TODAY (Jun 4)",
                "Annual value: $2.1M · proposed renewal: $4.83M over 2 yrs",
                "Rate drift: +5.8% vs +3% contract cap · $58K/yr exposure",
                "SLA performance Q2 2026: 99.97% uptime · zero breaches",
                "Tier 1 critical vendor · annual board attestation required",
            ],
            "narrative": (
                "Fiserv Core Banking contract entered auto-renewal window on 2026-05-04. "
                "30-day non-renewal notice deadline is TODAY (2026-06-04). Vendor risk score 38/100 "
                "(LOW). If renewed today at negotiated +2.4% rate cap, 2-year savings vs auto-renewal "
                "default escalator (+5.8%) is approximately $116K. Recommendation: APPROVE renewal "
                "with rate cap negotiation."
            ),
            "regulatory_context": [
                "NCUA 2026 Supervisory Priorities — vendor management focus #4",
                "FFIEC IT Examination Handbook (June 2024) — third-party risk",
                "Board attestation required per BOARD-RES-2026-04 (Vendor Management Policy)",
            ],
            "ncua_exam_impact": "Closes 1 NCUA attention item · vendor mgmt risk assessment",
            "actions_available": [
                {"id": "approve_renewal", "label": "Approve renewal",     "tone": "primary"},
                {"id": "negotiate",       "label": "Open negotiation",     "tone": "secondary"},
                {"id": "decline",         "label": "Decline (let expire)", "tone": "secondary"},
            ],
        },
        "CDD-2026-0391": {
            "type": "CDD REVIEW",
            "subject_member": "#39104 (Mendoza, C.)",
            "key_findings": [
                "Import/export agent · textiles (Mexico, Honduras, Vietnam suppliers)",
                "Wire activity Q2 2026: 40 wires · $356K total",
                "New supplier: Mekong Textile Trading Co (Vietnam) · 594(a) secondary watchlist",
                "Risk tier: HIGH · enhanced monitoring active",
                "Source-of-funds documentation refreshed and on file",
            ],
            "narrative": (
                "Quarterly EDD review for member #39104. Wire activity up 18% vs trailing 12mo baseline; "
                "member-supplied purchase orders documented the increase as Q2 holiday inventory orders. "
                "Mekong Textile Trading Co appears on the OFAC 594(a) Consolidated secondary watchlist — "
                "risk-accepted with continued monitoring per BSA Officer review. Next review 2026-08-14."
            ),
            "regulatory_context": [
                "31 CFR § 1020.210 — anti-money-laundering program",
                "FinCEN EDD guidance for high-risk member relationships",
            ],
            "ncua_exam_impact": "Contributes to BSA/AML folder · 96% complete",
            "actions_available": [
                {"id": "reaffirm",  "label": "Reaffirm HIGH tier",  "tone": "primary"},
                {"id": "escalate", "label": "Escalate to officer",  "tone": "secondary"},
                {"id": "dismiss",   "label": "Close review",         "tone": "secondary"},
            ],
        },
        "ONB-2026-0201": {
            "type": "ONBOARDING",
            "subject_member": "Torres, R.",
            "key_findings": [
                "Indiana DL #IN-3884-2719-09 verified via AAMVA DLDV",
                "SSN validated via SSA SSNVS",
                "Address: 1842 Main St, South Bend, IN — USPS DPV D1",
                "OFAC: CLEAR · PEP: NEGATIVE · ChexSystems: CLEAR",
                "Risk tier: LOW · ready to approve",
            ],
            "narrative": (
                "CIP packet complete. All 14 CIP requirements per 31 CFR § 1020.220 verifiably satisfied. "
                "OFAC, PEP, and ChexSystems screens all CLEAR. Member-services lead recommends "
                "auto-approval with standard CDD cycle."
            ),
            "regulatory_context": [
                "31 CFR § 1020.220 — Customer Identification Program (CIP)",
                "Indiana DL verified through AAMVA DLDV API",
            ],
            "ncua_exam_impact": "Indexed into CIP records folder · 100% complete",
            "actions_available": [
                {"id": "approve",  "label": "Approve account",  "tone": "primary"},
                {"id": "defer",    "label": "Defer to manager",  "tone": "secondary"},
                {"id": "decline",  "label": "Decline",            "tone": "secondary"},
            ],
        },
        "ONB-2026-0200": {
            "type": "ONBOARDING · PEP",
            "subject_member": "Anderson, P.",
            "key_findings": [
                "PEP near-match: spouse of Indiana state senator (LOW-risk)",
                "Match score 92% · WorldCheck One",
                "ID verified · OFAC clear · ChexSystems clear",
                "BSA Officer concurrence required for PEP-near-match approval",
                "Enhanced monitoring applies at MEDIUM tier going forward",
            ],
            "narrative": (
                "Anderson, P. flagged at OFAC + PEP screening for political-exposure relationship "
                "(spouse of Indiana state senator). No sanctions risk. BSA Officer review recommends "
                "approval with enhanced monitoring at MEDIUM tier and quarterly CDD touchpoints."
            ),
            "regulatory_context": [
                "FFIEC BSA/AML Manual — PEP requirements",
                "Internal policy P-COMP-201 — PEP-near-match disposition",
            ],
            "ncua_exam_impact": "Indexed to CIP records folder · PEP disposition logged",
            "actions_available": [
                {"id": "approve_with_edd", "label": "Approve w/ EDD",   "tone": "primary"},
                {"id": "escalate",          "label": "Escalate to CCO",  "tone": "secondary"},
                {"id": "decline",           "label": "Decline",          "tone": "secondary"},
            ],
        },
        "LN-2026-0517": {
            "type": "LOAN PACKET",
            "subject_member": "#38914 (Williams, D.)",
            "key_findings": [
                "Personal loan $12,500 requested · 36-month term",
                "Self-employed (Williams Photography LLC)",
                "MISSING: 2025 tax return (Form 1040 + Schedule C)",
                "FICO 684 (MEDIUM tier)",
                "Equipment quote $14,200 (B&H Photo, itemized)",
            ],
            "narrative": (
                "Personal loan application received from member #38914 for equipment purchase. "
                "Packet 62% complete. Missing 2025 tax return is a hard blocker for self-employed income "
                "verification. CWAnyWhere reminder cycle active. Estimated time-to-close once tax doc "
                "received: 18 hours."
            ),
            "regulatory_context": [
                "Reg Z disclosures required (closed-end consumer loan)",
                "Internal policy P-UW-203 — self-employment income verification",
            ],
            "ncua_exam_impact": "Routes into Credit Risk folder when complete",
            "actions_available": [
                {"id": "request_docs", "label": "Request docs again",   "tone": "primary"},
                {"id": "approve",      "label": "Approve packet",        "tone": "secondary"},
                {"id": "decline",      "label": "Decline",                "tone": "secondary"},
            ],
        },
        "POL-2026-0044": {
            "type": "POLICY · TRAINING",
            "subject_member": "22 employees (BSA/AML 2026 training)",
            "key_findings": [
                "22 of 84 employees overdue on BSA/AML training (74% completion)",
                "18 of 22 are branch tellers — highest-risk role",
                "Reminder cycle 3 of 4 sent · escalation to managers Jun 10",
                "Forecast: 18/22 complete by Jun 10 · 22/22 by Jun 17",
                "Critical: 100% required before NCUA exam window opens Jul 21",
            ],
            "narrative": (
                "Policy & HR Agent tracking ongoing BSA/AML training for 84 active employees. "
                "Current completion rate 74% with 22 employees overdue past the 2026-05-31 deadline. "
                "Auto-reminder cadence has fired 3 times. Final escalation goes to VP Operations "
                "(Margaret Rodriguez) on 2026-06-17 if completions are not 100% by then."
            ),
            "regulatory_context": [
                "12 CFR Part 749 — NCUA records retention + training",
                "Internal P-COMP-201 — annual BSA/AML training requirement",
            ],
            "ncua_exam_impact": "Drags HR/Policy folder to 88% · target 95% before exam",
            "actions_available": [
                {"id": "escalate_now",       "label": "Escalate now",      "tone": "primary"},
                {"id": "send_reminders",     "label": "Resend reminders",   "tone": "secondary"},
                {"id": "report_to_board",    "label": "Report to board",    "tone": "secondary"},
            ],
        },
    }
    ov = overrides.get(item_id, {})
    return {
        "item_id":     item_id,
        "type":        ov.get("type", "REVIEW ITEM"),
        "priority":    priority,
        "agent":       agent,
        "subject_member": ov.get("subject_member", title.split("·")[0].strip()),
        "member_profile": {
            "name":         ov.get("subject_member", title.split("·")[0].strip()),
            "member_since": "2026",
            "address":      "—",
            "occupation":   "—",
            "risk_tier":    priority,
            "prior_sars":   0,
        },
        "key_findings":          ov.get("key_findings", [title]),
        "transaction_data":      [],
        "narrative":             ov.get("narrative",
                                        f"{agent} has surfaced {item_id} for review. {title}"),
        "detection_confidence_pct":              95.0,
        "pattern_classification":                ov.get("type", "Review item"),
        "intentional_structuring_probability_pct": 0.0,
        "ctr_threshold":                         0,
        "statutory_cite":                        "—",
        "sar_deadline":                          "—",
        "ncua_exam_impact":                      ov.get("ncua_exam_impact", "Contributes to NCUA exam folder"),
        "regulatory_context":                    ov.get("regulatory_context", []),
        "actions_available":                     ov.get("actions_available", [
            {"id": "approve",  "label": "Approve",  "tone": "primary"},
            {"id": "dismiss",  "label": "Cancel",   "tone": "secondary"},
        ]),
        "similar_historical_cases_filed": 0,
    }


@router.get("/hitl/current-item")
async def cwfcu_hitl_current_item() -> Dict[str, Any]:
    """Returns the deep-dive SAR-2026-0142 case shown in hitl.html center pane."""
    return {
        "item_id":     "SAR-2026-0142",
        "type":        "SAR · DRAFT",
        "priority":    "HIGH",
        "agent":       "Compliance Agent",
        "subject_member": "#44821",
        "member_profile": {
            "name":         "Arrington, Devon Christopher",
            "member_since": "March 2019",
            "address":      "5814 Bittersweet Rd, Granger, IN 46530 (since May 12, 2026)",
            "occupation":   "Independent Contractor (construction)",
            "risk_tier":    "HIGH",
            "prior_sars":   0,
        },
        "key_findings": [
            "Structuring pattern match — 7 cash deposits totaling $47,300 over 16 days",
            "All deposits between $5,300 and $8,900 (just under $10K CTR threshold)",
            "4 different branch locations across South Bend MSA",
            "Pattern statistical confidence: 96.1%",
            "Member opened with HIGH-risk tier (OFAC near-match + ChexSystems prior)",
        ],
        "transaction_data": [
            {"date": "May 12", "branch": "South Bend", "amount": 8900, "type": "Cash deposit"},
            {"date": "May 14", "branch": "Mishawaka",  "amount": 7200, "type": "Cash deposit"},
            {"date": "May 16", "branch": "Granger",    "amount": 5800, "type": "Cash deposit"},
            {"date": "May 18", "branch": "Elkhart",    "amount": 6400, "type": "Cash deposit"},
            {"date": "May 21", "branch": "South Bend", "amount": 7800, "type": "Cash deposit"},
            {"date": "May 24", "branch": "Mishawaka",  "amount": 5900, "type": "Cash deposit"},
            {"date": "May 28", "branch": "Granger",    "amount": 5300, "type": "Cash deposit"},
        ],
        "narrative": (
            "The subject, account holder #44821, conducted 7 cash deposits totaling $47,300 "
            "between May 12-28, 2026, structured in amounts between $5,800 and $8,900 to avoid "
            "Currency Transaction Report (CTR) filing thresholds under 31 U.S.C. § 5313. "
            "The transactions occurred across 4 branch locations in the South Bend, Indiana area "
            "with no apparent business justification. Transaction pattern is consistent with "
            "structuring as defined under 31 U.S.C. § 5324."
        ),
        "detection_confidence_pct": 96.1,
        "pattern_classification": "Structuring (96.1% confidence)",
        "intentional_structuring_probability_pct": 94.7,
        "ctr_threshold":      10000,
        "statutory_cite":     "31 U.S.C. § 5324",
        "sar_deadline":       "2026-06-27",
        "ncua_exam_impact":   "Closes 2 attention items: BSA pattern detection + EDD monitoring",
        "regulatory_context": [
            "FinCEN Guidance on Structuring (FIN-2014-G002)",
            "NCUA 2026 Supervisory Priorities — BSA/AML focus #1",
        ],
        "actions_available": [
            {"id": "file_sar",  "label": "FILE SAR", "tone": "primary"},
            {"id": "cancel",    "label": "Cancel",   "tone": "secondary"},
            {"id": "switch_reviewer", "label": "Switch reviewer", "tone": "tertiary"},
        ],
        "similar_historical_cases_filed": 14,
    }


# ─────────────────────────────────────────────────────────────────────
# HITL action mutations — buttons in Command Center + Human Review screens
# fire these to record a decision and return a toast-ready payload.
# In-memory only (demo) — survives reloads via the global ACTION_LOG.
# ─────────────────────────────────────────────────────────────────────
ACTION_LOG: list = []   # append-only; surfaced as Audit Lens trail


def _log_action(action: str, item_id: str, **details) -> Dict[str, Any]:
    entry = {
        "ts":      datetime.now(timezone.utc).isoformat(),
        "action":  action,
        "item_id": item_id,
        **details,
    }
    ACTION_LOG.append(entry)
    return entry


@router.post("/hitl/{item_id}/file-sar")
async def cwfcu_hitl_file_sar(item_id: str) -> Dict[str, Any]:
    """File SAR with FinCEN — toast: success."""
    entry = _log_action("file_sar", item_id, fincen_ack=f"FCN-{item_id}-ACK")
    return {
        "ok": True,
        "toast": {
            "tone": "success",
            "title": f"{item_id} filed with FinCEN",
            "detail": f"BSA E-Filing acknowledgment: {entry['fincen_ack']} · Audit Lens entry logged",
        },
        "audit_entry": entry,
    }


@router.post("/hitl/{item_id}/approve")
async def cwfcu_hitl_approve(item_id: str) -> Dict[str, Any]:
    """Approve a HITL item — toast: success."""
    entry = _log_action("approve", item_id)
    return {
        "ok": True,
        "toast": {
            "tone": "success",
            "title": f"{item_id} approved",
            "detail": "Decision logged · downstream agents notified",
        },
        "audit_entry": entry,
    }


@router.post("/hitl/{item_id}/dismiss")
async def cwfcu_hitl_dismiss(item_id: str, reason: str = "no_action_needed") -> Dict[str, Any]:
    """Dismiss a HITL item — toast: warn (reason logged)."""
    entry = _log_action("dismiss", item_id, reason=reason)
    return {
        "ok": True,
        "toast": {
            "tone": "warn",
            "title": f"{item_id} dismissed",
            "detail": f"Reason: {reason} · entry persists in Audit Lens",
        },
        "audit_entry": entry,
    }


@router.post("/hitl/{item_id}/edit-narrative")
async def cwfcu_hitl_edit_narrative(item_id: str, narrative: str = "") -> Dict[str, Any]:
    """Save edited SAR narrative — toast: info."""
    entry = _log_action("edit_narrative", item_id, narrative_len=len(narrative))
    return {
        "ok": True,
        "toast": {
            "tone": "info",
            "title": f"{item_id} narrative updated",
            "detail": f"Saved {len(narrative)} character draft · pending BSA Officer review",
        },
        "audit_entry": entry,
    }


@router.post("/hitl/{item_id}/switch-reviewer")
async def cwfcu_hitl_switch_reviewer(item_id: str, reviewer: str = "Adrienne Williams") -> Dict[str, Any]:
    """Reassign HITL to a different reviewer."""
    entry = _log_action("switch_reviewer", item_id, reviewer=reviewer)
    return {
        "ok": True,
        "toast": {
            "tone": "info",
            "title": f"{item_id} reassigned",
            "detail": f"Now routed to {reviewer}",
        },
        "audit_entry": entry,
    }


@router.post("/vendors/{vendor}/renewal-brief")
async def cwfcu_vendor_renewal_brief(vendor: str) -> Dict[str, Any]:
    """Open vendor renewal brief — toast: info."""
    entry = _log_action("open_renewal_brief", f"vendor:{vendor}")
    return {
        "ok": True,
        "toast": {
            "tone": "info",
            "title": f"{vendor.title()} renewal brief generated",
            "detail": "Brief includes SLA history, rate drift analysis, recommendation · routed to CEO + Margaret Rodriguez",
        },
        "audit_entry": entry,
    }


@router.post("/regulatory/{change_id}/open-gap-analysis")
async def cwfcu_open_regulatory_gap(change_id: str) -> Dict[str, Any]:
    """Open the policy gap-analysis package for a regulatory change."""
    entry = _log_action("open_regulatory_gap", change_id)
    return {
        "ok": True,
        "toast": {
            "tone": "info",
            "title": f"Policy gap analysis opened",
            "detail": f"Change {change_id}: 3 procedures flagged for update · Compliance Agent has drafted revisions",
        },
        "audit_entry": entry,
    }


@router.get("/hitl/recent-reviews")
async def cwfcu_hitl_recent_reviews() -> Dict[str, Any]:
    return {
        "items": [
            {"item_id": "SAR-2026-0138", "title": "Rapid Movement · Member #38204",
             "outcome": "FILED",  "outcome_color": "#16a34a", "reviewed_at": "Yesterday"},
            {"item_id": "LN-2026-0438",  "title": "Mortgage Approval · Patel, A.",
             "outcome": "APPROVED","outcome_color": "#16a34a", "reviewed_at": "Yesterday"},
            {"item_id": "CTR-2026-1187", "title": "CTR Auto-Filed · Member #29341 · $12,400",
             "outcome": "AUTO-ROUTED","outcome_color": "#2563eb", "reviewed_at": "Yesterday"},
            {"item_id": "ONB-2026-0190", "title": "Onboarding Approved · Rosales, E.",
             "outcome": "APPROVED","outcome_color": "#16a34a", "reviewed_at": "May 31"},
        ],
    }
