#!/usr/bin/env python3
"""
Seed STP Phase 2 demo content into DynamoDB.

This is the single source of truth for STP demo data. Eliminates the
hardcoded `SAMPLE_AGENTS` / `INITIAL_PIPELINES` / `INITIAL_ITEMS` arrays in
the frontend by ensuring every page reads its STP content from a live API.

Tables seeded:
  • apex-ai-platform-agents          → 5 STP agents (ChatSTP + 4 specialists)
  • apex-ai-platform-pipelines       → 4 STP pipelines (one per UC)
  • apex-ai-platform-review-queue    → 1 STP review item (P-3A bearing replacement)

Idempotent: re-running upserts. Pass `--force` to overwrite existing rows.

Usage:
    cd backend && source venv/bin/activate
    python3 scripts/seed_stp_demo.py            # safe upsert
    python3 scripts/seed_stp_demo.py --force    # overwrite even if present
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Make the backend package importable when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import settings  # noqa: E402
from services.dynamodb import DynamoDBService  # noqa: E402


# ───────────────────────── 5 STP agents ─────────────────────────

STP_AGENTS: List[Dict[str, Any]] = [
    {
        "agent_id": "agent-stp-chatstp",
        "name": "ChatSTP",
        "description": "User-facing router · classifies the query and delegates to the matching specialist (Policy / Maintenance / Diagnostics / Reliability).",
        "type": "supervisor",
        "industry": "nuclear_operations",
        "status": "active",
        "environment": "development",
        "model_id": "us.anthropic.claude-haiku-3-5-v1",
        "playbook_id": None,
        "instructions": "You are ChatSTP — the user-facing router for the STP nuclear knowledge assistant. Classify each query and delegate to the right specialist. Never paraphrase a specialist's response — return their answer verbatim.",
        "action_group_ids": ["intent_classify"],
        "knowledge_base_ids": [],
        "collaborator_ids": ["agent-stp-policy", "agent-stp-maintenance", "agent-stp-diagnostics", "agent-stp-reliability"],
        "bedrock_agent_arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_chatstp_router-JxzvXpBkNX",
        "invocation_count": 61,
    },
    {
        "agent_id": "agent-stp-policy",
        "name": "PolicyAgent",
        "description": "STP UC-1 · Verbatim policy & procedure citations from the STP-4xx, 0POP-, 0PMP-, and Tech Spec corpus.",
        "type": "collaborator",
        "industry": "nuclear_operations",
        "status": "active",
        "environment": "development",
        "model_id": "us.anthropic.claude-sonnet-4-5-v1",
        "playbook_id": None,  # populated after playbook lookup
        "playbook_name": "policy_procedure_lookup",
        "instructions": "You are PolicyAgent. Answer policy and procedure questions with verbatim citations. Always include doc number, section, and effective date. Never paraphrase the cited text.",
        "action_group_ids": ["policy_search", "policy_cite_extract"],
        "knowledge_base_ids": [],
        "collaborator_ids": [],
        "bedrock_agent_arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_policy_agent-9pZgSy5aWz",
        "invocation_count": 24,
    },
    {
        "agent_id": "agent-stp-maintenance",
        "name": "MaintenanceAgent",
        "description": "STP UC-2 · Equipment PM history with engineer attribution from Oracle PMHISTORY mirror.",
        "type": "collaborator",
        "industry": "nuclear_operations",
        "status": "active",
        "environment": "development",
        "model_id": "us.anthropic.claude-haiku-3-5-v1",
        "playbook_id": None,
        "playbook_name": "equipment_pm_history",
        "instructions": "You are MaintenanceAgent. Look up PM history for the requested equipment and attribute to the engineers + technicians who performed it. Include WO id, date, parts used, and a link to the work package PDF.",
        "action_group_ids": ["oracle_pm_lookup", "engineer_attribution", "wp_attachment_fetch"],
        "knowledge_base_ids": [],
        "collaborator_ids": [],
        "bedrock_agent_arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_maintenance_agent-JQoz4G5QqB",
        "invocation_count": 18,
    },
    {
        "agent_id": "agent-stp-diagnostics",
        "name": "DiagnosticsAgent",
        "description": "STP UC-3 · Failure-mode aggregation across the work-package corpus with cited WO evidence.",
        "type": "collaborator",
        "industry": "nuclear_operations",
        "status": "active",
        "environment": "development",
        "model_id": "us.anthropic.claude-sonnet-4-5-v1",
        "playbook_id": None,
        "playbook_name": "equipment_issue_analysis",
        "instructions": "You are DiagnosticsAgent. Search the work-package corpus for the requested equipment and aggregate by failure mode. Cite at least 3 specific WO ids as evidence. Never make up failure modes — if the corpus is empty, say so.",
        "action_group_ids": ["wp_corpus_search", "failure_mode_aggregate"],
        "knowledge_base_ids": [],
        "collaborator_ids": [],
        "bedrock_agent_arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_diagnostics_agent-s3l3Wc9HUp",
        "invocation_count": 12,
    },
    {
        "agent_id": "agent-stp-reliability",
        "name": "ReliabilityAgent",
        "description": "STP UC-4 · Predictive maintenance — RUL forecast + anomaly detection + risk score + PM advance recommendation via ApexSignal.",
        "type": "collaborator",
        "industry": "nuclear_operations",
        "status": "active",
        "environment": "development",
        "model_id": "us.anthropic.claude-opus-4-6-v1",
        "playbook_id": None,
        "playbook_name": "predictive_maintenance",
        "instructions": "You are ReliabilityAgent. Synthesize RUL prediction, anomaly detection, risk score, and PM recommendation into one actionable response. Always lead with the risk tier (CRITICAL/HIGH/MODERATE/LOW), then days-until-failure with confidence band, then the recommended PM advance with avoidance estimate. End every response with [Decision logged to apex.audit_log: <id>].",
        "action_group_ids": ["rul_predict", "anomaly_detect", "pm_recommend", "risk_score_compute"],
        "knowledge_base_ids": [],
        "collaborator_ids": [],
        "bedrock_agent_arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_reliability_agent-oVMXghD955",
        "invocation_count": 7,
    },
]


# ───────────────────────── 4 STP pipelines ─────────────────────────

def _stage(stype: str, label: str, action: str) -> Dict[str, Any]:
    return {
        "id": f"stage-{action}",
        "type": stype,
        "label": label,
        "action": action,
        "config": {},
        "schema": {},
    }


STP_PIPELINES: List[Dict[str, Any]] = [
    {
        "pipeline_id": "pipe-stp-policy",
        "name": "Policy & Procedure Lookup",
        "industry": "nuclear_operations",
        "industry_label": "Nuclear Operations & Reliability",
        "throughput": "24 queries/day",
        "status": "Active",
        "playbook_id": None,
        "playbook_name": "policy_procedure_lookup",
        "stages": [
            _stage("extract", "Intent Classify", "intent_classify"),
            _stage("execute", "Policy Search", "policy_search"),
            _stage("extract", "Cite Extract", "policy_cite_extract"),
            _stage("notify", "Verbatim Response", "email_send"),
        ],
        "stats": {"avg_latency": "3.2s", "accuracy": "99.0%", "auto_approve": "100%", "last_run": "14 min ago"},
    },
    {
        "pipeline_id": "pipe-stp-pm-history",
        "name": "Equipment PM History",
        "industry": "nuclear_operations",
        "industry_label": "Nuclear Operations & Reliability",
        "throughput": "18 lookups/day",
        "status": "Active",
        "playbook_id": None,
        "playbook_name": "equipment_pm_history",
        "stages": [
            _stage("extract", "Intent Classify", "intent_classify"),
            _stage("execute", "Oracle PM Lookup", "oracle_pm_lookup"),
            _stage("execute", "Engineer Attribution", "engineer_attribution"),
            _stage("execute", "WP PDF Fetch", "wp_attachment_fetch"),
        ],
        "stats": {"avg_latency": "4.8s", "accuracy": "97.4%", "auto_approve": "95%", "last_run": "3 min ago"},
    },
    {
        "pipeline_id": "pipe-stp-issue-analysis",
        "name": "Equipment Issue Analysis",
        "industry": "nuclear_operations",
        "industry_label": "Nuclear Operations & Reliability",
        "throughput": "12 analyses/day",
        "status": "Active",
        "playbook_id": None,
        "playbook_name": "equipment_issue_analysis",
        "stages": [
            _stage("extract", "Intent Classify", "intent_classify"),
            _stage("analyze", "WP Corpus Search", "wp_corpus_search"),
            _stage("analyze", "Failure Modes", "failure_mode_aggregate"),
            _stage("notify", "Ranked Findings", "email_send"),
        ],
        "stats": {"avg_latency": "6.2s", "accuracy": "94.2%", "auto_approve": "88%", "last_run": "7 min ago"},
    },
    {
        "pipeline_id": "pipe-stp-predictive",
        "name": "Predictive Maintenance",
        "industry": "nuclear_operations",
        "industry_label": "Nuclear Operations & Reliability",
        "throughput": "8 alerts/day",
        "status": "Active",
        "playbook_id": None,
        "playbook_name": "predictive_maintenance",
        "stages": [
            _stage("extract", "Intent Classify", "intent_classify"),
            _stage("analyze", "Anomaly Detect", "anomaly_detect"),
            _stage("analyze", "RUL Predict", "rul_predict"),
            _stage("analyze", "Risk Score", "risk_score_compute"),
            _stage("decide", "PM Recommendation", "pm_recommend"),
        ],
        "stats": {"avg_latency": "9.1s", "accuracy": "91.8%", "auto_approve": "72%", "last_run": "11 min ago"},
    },
]


# ───────────────────────── 1 STP review item ─────────────────────────

STP_REVIEW_ITEMS: List[Dict[str, Any]] = [
    {
        "review_id": "STP-RLY-2026-04-30",
        "industry": "nuclear_operations",
        "priority": "URGENT",
        "title": "PM-7B advance · Pump-3A bearing replacement",
        "source": "ReliabilityAgent · 3 min ago",
        "submitted_at": "2026-04-30T08:14:22Z",
        "playbook_id": None,
        "playbook_name": "predictive_maintenance",
        "amount": "$340,000",
        "amount_label": "Estimated avoidance",
        "issues": [
            "P-3A axial vibration trending 0.34 in/s — 13% above 0.30 in/s Tech-Spec limit.",
            "Pattern matches 3 prior bearing-degradation events on this same pump.",
            "ReliabilityAgent recommends PM-7B advance from Day 22 to Day 5.",
        ],
        "reason_tone": "red",
        "extracted": [
            {"k": "Equipment",          "v": "P-3A · RCS · Westinghouse Model-93A",    "conf": 99},
            {"k": "Anomaly",            "v": "ANOM-P3A-2026-04-22",                     "conf": 99},
            {"k": "Predicted failure",  "v": "11 days (CI 80%: 7-14d, 95%: 5-17d)",    "conf": 87},
            {"k": "Cited prior WOs",    "v": "WO-2025-03311, WO-2025-03987, WO-2026-00188", "conf": 99},
            {"k": "Recommended PM",     "v": "PM-7B (RCP Bearing Inspection / 0PMP-RCS-7B)", "conf": 99},
            {"k": "Avoidance estimate", "v": "$340,000 · 18 outage hours",              "conf": 92},
            {"k": "Audit log",          "v": "AUD-stp-demo-1746068062",                 "conf": 99},
        ],
        "document_name": "STP-RLY-2026-04-30_predictive_alert.pdf",
        "next_on_approve": {"label": "Schedule PM-7B advance", "description": "Notifying Operations to schedule PM-7B advance and locking out P-3A per OSHA 1910.147.", "duration_ms": 2200},
        "next_on_reject":  {"label": "Return to ReliabilityAgent for re-analysis", "description": "Re-running RUL prediction with adjusted vibration baseline.", "duration_ms": 1600},
        "next_on_escalate": {"label": "Escalate to System Engineering", "description": "Routing to RCS System Engineer for engineering disposition. ASME XI Inspector tagged.", "duration_ms": 1800},
        "state": "pending",
        "created_at": "2026-04-30T08:14:22Z",
    },
]


# ───────────────────────── seeder ─────────────────────────

async def resolve_playbook_uuids() -> Dict[str, str]:
    """Map playbook name → UUID by scanning the playbooks table.

    The agents/pipelines/review-items above carry `playbook_name` strings; we
    convert them to the canonical `playbook_id` UUIDs that the seeded
    playbooks have so the frontend can deep-link cleanly.
    """
    db = DynamoDBService(settings.DYNAMODB_PLAYBOOKS)
    rows = await db.scan(filters={"industry": "nuclear_operations"}, limit=20)
    return {r["name"]: r["playbook_id"] for r in rows if r.get("name") and r.get("playbook_id")}


async def upsert_table(
    table_name: str, key_field: str, items: List[Dict[str, Any]],
    force: bool, label: str,
) -> int:
    """Upsert items into the given table. Returns count actually written."""
    db = DynamoDBService(table_name)
    written = 0
    skipped = 0
    for item in items:
        key = item.get(key_field)
        if not key:
            print(f"  ✗ {label} item missing {key_field!r}: {item}")
            continue
        if not force:
            existing = await db.get_item({key_field: key})
            if existing:
                skipped += 1
                continue
        # Stamp common metadata
        now = datetime.now(timezone.utc).isoformat()
        item.setdefault("created_at", now)
        item["updated_at"] = now
        await db.put_item(item)
        written += 1
    print(f"  ✓ {label}: {written} written, {skipped} skipped (already present)")
    return written


async def main(force: bool) -> int:
    print(f"╔═══════════════════════════════════════════╗")
    print(f"║  STP Phase 2 — DynamoDB seeder            ║")
    print(f"║  force={force}                              ║")
    print(f"╚═══════════════════════════════════════════╝\n")

    # Resolve playbook UUIDs so agents/pipelines/review can deep-link
    pb_map = await resolve_playbook_uuids()
    print(f"Resolved {len(pb_map)} nuclear playbook(s) by name:")
    for n, u in pb_map.items():
        print(f"  • {n:30s} → {u}")
    print()

    def fill_playbook_id(rows: List[Dict[str, Any]]) -> None:
        for r in rows:
            n = r.pop("playbook_name", None)
            if n and n in pb_map:
                r["playbook_id"] = pb_map[n]

    fill_playbook_id(STP_AGENTS)
    fill_playbook_id(STP_PIPELINES)
    fill_playbook_id(STP_REVIEW_ITEMS)

    # ─── Agents ───
    await upsert_table(
        settings.DYNAMODB_AGENTS,
        "agent_id",
        STP_AGENTS,
        force,
        "Agents",
    )

    # ─── Pipelines (table created on demand if it doesn't exist) ───
    pipelines_table = getattr(settings, "DYNAMODB_PIPELINES", "apex-ai-platform-pipelines")
    await upsert_table(
        pipelines_table,
        "pipeline_id",
        STP_PIPELINES,
        force,
        "Pipelines",
    )

    # ─── Review queue (table created on demand if it doesn't exist) ───
    review_table = getattr(settings, "DYNAMODB_REVIEW_QUEUE", "apex-ai-platform-review-queue")
    await upsert_table(
        review_table,
        "review_id",
        STP_REVIEW_ITEMS,
        force,
        "Review queue",
    )

    print("\n✓ STP seed complete.")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing rows (default: skip if present)")
    args = ap.parse_args()
    sys.exit(asyncio.run(main(force=args.force)))
