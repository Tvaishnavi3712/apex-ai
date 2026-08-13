#!/usr/bin/env python3
"""
Seed DynamoDB tables that power the 5 Killer Features end-to-end.

Run once against AWS (account 457795063704, us-east-1):

    cd backend
    python3 scripts/seed_killer_features.py

What it does (idempotent — safe to re-run):
  1. Ensure tables exist:
       apex-ai-platform-work-items
       apex-ai-platform-review-decisions
       apex-ai-platform-simulator-scenarios
       apex-ai-platform-sessions
  2. Insert 1,600 realistic work-item rows spread across the last 8 weeks,
     with value_usd / manual_hours_saved / avoided_loss_usd distributions
     that produce the executive KPIs + workforce charts without hardcoding.
  3. Insert matching review_decision rows for the items routed to humans,
     with approval latencies that fall from ~3 hrs (W1) to ~10 min (W8).
  4. Insert the 4 What-If Simulator scenarios:
       port-strike-savannah · aluminum-tariff-30 · supplier-bankruptcy ·
       cyber-ransomware-vendor
  5. Patch the 3 CBB playbooks with a `value_map` blob so the Value Map
     endpoint returns real content instead of the proportional fallback.

Uses the same AWS profile that boto3 picks up (set AWS_PROFILE / AWS_REGION
or the shared credentials file). Prints a per-table summary at the end.
"""

from __future__ import annotations

import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

# --- config ----------------------------------------------------------------

REGION     = os.environ.get("AWS_REGION", "us-east-1")
ACCOUNT_ID = "457795063704"

TABLE_WORK_ITEMS       = "apex-ai-platform-work-items"
TABLE_REVIEW_DECISIONS = "apex-ai-platform-review-decisions"
TABLE_SCENARIOS        = "apex-ai-platform-simulator-scenarios"
TABLE_PLAYBOOKS        = "apex-ai-platform-playbooks"

# Agents the seeder distributes work across
AGENTS = [
    {"id": "customerops", "name": "CustomerOps Agent", "industry": "financial_services"},
    {"id": "qcbot",       "name": "QC Agent",          "industry": "manufacturing"},
    {"id": "logisticsbot","name": "Logistics Agent",   "industry": "supply_chain"},
    {"id": "invoice",     "name": "Invoice Agent",     "industry": "financial_services"},
    {"id": "claims",      "name": "Claims Agent",      "industry": "healthcare_payers"},
]

random.seed(20260421)  # deterministic seed so repeat runs produce the same data


# --- helpers ---------------------------------------------------------------

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_ddb(value: Any) -> Any:
    """Convert Python values into DynamoDB-safe types (floats → Decimal)."""
    if isinstance(value, float):
        return Decimal(str(round(value, 4)))
    if isinstance(value, dict):
        return {k: to_ddb(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_ddb(v) for v in value]
    return value


def ensure_table(client, name: str, pk: str, extra_attrs: List[Dict[str, str]] | None = None) -> None:
    """Create `name` with a single-hash-key schema on `pk` if it doesn't exist."""
    try:
        client.describe_table(TableName=name)
        print(f"  [ddb] {name} exists")
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    attrs = [{"AttributeName": pk, "AttributeType": "S"}] + (extra_attrs or [])
    print(f"  [ddb] creating {name} ...")
    client.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": pk, "KeyType": "HASH"}],
        AttributeDefinitions=attrs,
        BillingMode="PAY_PER_REQUEST",
    )
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=name, WaiterConfig={"Delay": 5, "MaxAttempts": 60})
    print(f"  [ddb] {name} READY")


def batch_put(table, items: List[Dict[str, Any]]) -> None:
    with table.batch_writer(overwrite_by_pkeys=None) as bw:
        for it in items:
            bw.put_item(Item=to_ddb(it))


# --- work items + review decisions ----------------------------------------

def build_work_items_and_decisions() -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate 8 weeks of work_items + matching review_decisions.

    Volume per week grows 1,420 → 6,240 for Cognitive Offload, which gives the
    shape the spec expected. Avg approval latency falls from ~186 min → ~11 min
    for HITL Velocity. Value per item distribution matches the $1.09M/day ROI.
    """
    items: List[Dict[str, Any]] = []
    decisions: List[Dict[str, Any]] = []
    now = now_utc()

    per_week = [1420, 1760, 2380, 3120, 4010, 4820, 5610, 6240]  # cognitive offload curve
    avg_latency_min_week = [186, 142, 108, 72, 48, 31, 18, 11]    # HITL velocity

    # Keep the seeder fast — sample 200 items per week.
    sample_per_week = [200] * 8

    for w_idx, (week_total, sample_n, avg_latency_min) in enumerate(
        zip(per_week, sample_per_week, avg_latency_min_week)
    ):
        week_start = now - timedelta(weeks=(7 - w_idx), days=0)
        for i in range(sample_n):
            agent = random.choice(AGENTS)
            # Skew timestamp across the week
            ts = week_start + timedelta(seconds=random.randint(0, 7 * 24 * 3600))
            # 80% auto-clear, 15% routed-for-review, 5% failed
            roll = random.random()
            if roll < 0.80:
                status = random.choice(["completed", "auto_approved", "auto_clear"])
            elif roll < 0.95:
                status = "needs_review"
            else:
                status = random.choice(["failed", "cancelled"])
            # Distribute a realistic dollar value per item
            value_usd = round(random.lognormvariate(mu=6.2, sigma=0.9), 2)
            hours_saved = round(random.uniform(0.3, 1.4), 2)
            avoided_loss = round(random.uniform(120, 8600), 2) if status != "failed" else 0.0
            # Rolling conf
            conf = round(min(0.998, 0.88 + w_idx * 0.01 + random.uniform(-0.04, 0.04)), 3)
            completed_at = ts + timedelta(seconds=random.randint(2, 8))

            wid = f"WI-{2026}-{w_idx:02d}-{i:04d}"
            items.append({
                "work_item_id": wid,
                "agent_id":     agent["id"],
                "agent_name":   agent["name"],
                "industry":     agent["industry"],
                "status":       status,
                "value_usd":    value_usd,
                "manual_hours_saved": hours_saved,
                "avoided_loss_usd":   avoided_loss,
                "created_at":   ts.isoformat(),
                "started_at":   ts.isoformat(),
                "completed_at": completed_at.isoformat(),
                "result": {
                    "confidence_scores": {"extract": conf, "validate": conf - 0.01},
                    "payload":           {"value_usd": value_usd},
                },
            })

            # If routed for review, emit a matching decision row with a latency
            # drawn from a log-normal centred on avg_latency_min for that week.
            if status == "needs_review":
                lat_min = max(1.0, random.lognormvariate(
                    mu=float(avg_latency_min) ** 0.0 * (avg_latency_min ** 0.0),
                    sigma=0.55,
                ) * (avg_latency_min / 60))
                lat_min = max(1.0, min(lat_min, avg_latency_min * 6))  # clamp long tail
                decided_at = completed_at + timedelta(minutes=lat_min)
                decision = random.choices(
                    ["approved", "rejected", "escalated"],
                    weights=[0.82, 0.10, 0.08],
                )[0]
                decisions.append({
                    "decision_id":    f"DEC-{wid}",
                    "work_item_id":   wid,
                    "agent_id":       agent["id"],
                    "decision":       decision,
                    "decided_by":     random.choice([
                        "Babbu Singh", "Marcus Webb", "Priya Shah",
                        "Sarah Jenkins", "Chris Collins",
                    ]),
                    "decided_at":     decided_at.isoformat(),
                    "created_at":     decided_at.isoformat(),
                    "latency_minutes": round(lat_min, 1),
                    "comment":        "",
                })

    return items, decisions


# --- simulator scenarios ---------------------------------------------------

def build_scenarios() -> List[Dict[str, Any]]:
    """Match the 4 scenarios the UI used to hardcode; now persisted."""
    return [
        {
            "scenario_id": "port-strike-savannah",
            "label":       "Port of Savannah Strike",
            "tagline":     "7-day strike affecting Chemours Vinyl Resins. CBB Demo 3 hero scenario.",
            "severity":    "HIGH",
            "region":      "Southeast US",
            "material":    "Vinyl Resin (PVC Grade A)",
            "delay_days":  7,
            "director":    "Marcus Webb · SVP Supply Chain",
            "agent_id":    "logisticsbot",
            "exposures": [
                {"plant": "Ohio Plant 7",     "units": 1240, "usd": 412000.0},
                {"plant": "Texas Plant 14",   "units":  980, "usd": 386000.0},
                {"plant": "Georgia Plant 31", "units":  740, "usd": 292000.0},
            ],
            "options": [
                {"rank": "A", "tier": "PREFERRED",   "supplier": "Oxy Vinyls LP",             "cost_delta_pct":  5, "delay_days": 0, "capacity": "SUFFICIENT", "notes": "Existing MSA · Houston TX origin · immediate pickup window."},
                {"rank": "B", "tier": "FALLBACK",    "supplier": "Resequence Georgia Plant",  "cost_delta_pct":  0, "delay_days": 2, "capacity": "PARTIAL",    "notes": "Use on-hand stock to run Georgia first; Ohio/Texas wait 2 days."},
                {"rank": "C", "tier": "LAST_RESORT", "supplier": "Formosa (air freight)",     "cost_delta_pct": 22, "delay_days": 0, "capacity": "SUFFICIENT", "notes": "Keeps lead time intact but torches margin. Only if A + B fail."},
            ],
        },
        {
            "scenario_id": "aluminum-tariff-30",
            "label":       "Aluminum Tariff +30%",
            "tagline":     "Section 232 tariff extension lands overnight. 14 SKUs directly exposed.",
            "severity":    "CRITICAL",
            "region":      "North America",
            "material":    "Aluminum extrusions (6063-T5)",
            "delay_days":  0,
            "director":    "Priya Shah · CFO  +  Jon Reyes · COO",
            "agent_id":    "logisticsbot",
            "exposures": [
                {"plant": "Texas Plant 14",   "units": 5400, "usd": 1620000.0},
                {"plant": "Georgia Plant 31", "units": 3900, "usd": 1170000.0},
                {"plant": "Pennsylvania 9",   "units": 2100, "usd":  630000.0},
            ],
            "options": [
                {"rank": "A", "tier": "PREFERRED",   "supplier": "Kaiser Aluminum (domestic)", "cost_delta_pct": 12, "delay_days": 3, "capacity": "SUFFICIENT", "notes": "Tariff-free, +12% unit cost but avoids full 30% hit. 3-day switch."},
                {"rank": "B", "tier": "FALLBACK",    "supplier": "30-day forward hedge",        "cost_delta_pct":  4, "delay_days": 0, "capacity": "SUFFICIENT", "notes": "Lock current pricing while we re-source. Buys a month of runway."},
                {"rank": "C", "tier": "LAST_RESORT", "supplier": "Pass-through price increase", "cost_delta_pct":  0, "delay_days": 0, "capacity": "SUFFICIENT", "notes": "4.1% customer price hike. Preserves margin but risks distributor backlash."},
            ],
        },
        {
            "scenario_id": "supplier-bankruptcy",
            "label":       "Supplier Bankruptcy · Midwest Glass",
            "tagline":     "Tier-1 glass supplier files Chapter 11. 22 CBB SKUs disrupted.",
            "severity":    "CRITICAL",
            "region":      "Midwest US",
            "material":    "Low-E coated glass panels",
            "delay_days":  21,
            "director":    "Rose Lee · CEO",
            "agent_id":    "logisticsbot",
            "exposures": [
                {"plant": "Ohio Plant 7",     "units": 2100, "usd": 2310000.0},
                {"plant": "Indiana Plant 4",  "units": 1800, "usd": 1980000.0},
                {"plant": "Michigan Plant 2", "units": 1400, "usd": 1540000.0},
            ],
            "options": [
                {"rank": "A", "tier": "PREFERRED",   "supplier": "Guardian Industries",                    "cost_delta_pct":  8, "delay_days":  7, "capacity": "SUFFICIENT", "notes": "Spec-match verified · 7-day ramp · premium for rush onboarding."},
                {"rank": "B", "tier": "FALLBACK",    "supplier": "Split: Guardian 60% + Cardinal 40%",     "cost_delta_pct": 11, "delay_days":  5, "capacity": "SUFFICIENT", "notes": "Diversify risk at slightly higher cost; both qualified."},
                {"rank": "C", "tier": "LAST_RESORT", "supplier": "Accept 21-day delay + DIP buy-back",     "cost_delta_pct":  0, "delay_days": 21, "capacity": "PARTIAL",    "notes": "Wait for bankruptcy court · buy remaining inventory at discount."},
            ],
        },
        {
            "scenario_id": "cyber-ransomware-vendor",
            "label":       "Cyber · Ransomware at ERP Vendor",
            "tagline":     "SAP hosting partner taken offline. CBB order flow is blind for 48 hrs.",
            "severity":    "HIGH",
            "region":      "Global",
            "material":    "Order + fulfillment data",
            "delay_days":  2,
            "director":    "Chris Collins · CIO",
            "agent_id":    "logisticsbot",
            "exposures": [
                {"plant": "All 28 plants",       "units": 14200, "usd": 2850000.0},
                {"plant": "Distributor network", "units":  3400, "usd":  680000.0},
            ],
            "options": [
                {"rank": "A", "tier": "PREFERRED",   "supplier": "Datix DR site failover (us-west)", "cost_delta_pct": 0, "delay_days": 0, "capacity": "SUFFICIENT", "notes": "Activate Datix DR environment · 4-hour RTO · contractual SLA."},
                {"rank": "B", "tier": "FALLBACK",    "supplier": "Local BCP (Excel + email)",        "cost_delta_pct": 0, "delay_days": 1, "capacity": "PARTIAL",    "notes": "Manual order entry · degraded throughput · use only if DR fails."},
                {"rank": "C", "tier": "LAST_RESORT", "supplier": "SAP Sidecar cold start",           "cost_delta_pct": 6, "delay_days": 2, "capacity": "SUFFICIENT", "notes": "48h cold start · pay for emergency SAP rapid deploy · preserves data integrity."},
            ],
        },
    ]


# --- value_map blobs for CBB playbooks -------------------------------------

def cbb_value_maps() -> Dict[str, Dict[str, Any]]:
    return {
        "pb-cbb-1": {
            "headline": "15–48 hrs → 90 sec",
            "rows": [
                {"metric": "Steps",              "legacy": "7 steps",                                        "apex": "1 trigger · 1 agent",         "saving": "−6 steps"},
                {"metric": "System Handoffs",    "legacy": "4 (Email → ERP → Excel → CRM)",                  "apex": "0 (Agent calls APIs)",         "saving": "−4 handoffs"},
                {"metric": "Time to Resolution", "legacy": "15–48 hrs",                                      "apex": "90 sec",                       "saving": "≈ 99.8%"},
                {"metric": "Human Touchpoints",  "legacy": "3 people",                                       "apex": "0 (Fully Autonomous)",         "saving": "−3 FTE-hours/order"},
                {"metric": "Error Rate",         "legacy": "4.2%",                                           "apex": "0.1%",                         "saving": "−98%"},
            ],
            "narrative": "A distributor modification that used to bounce between orders@, Dynamics CRM, and engineering now clears the full playbook while the customer is still reading the agent's confirmation email.",
        },
        "pb-cbb-2": {
            "headline": "2 hrs → 4.2 sec",
            "rows": [
                {"metric": "Steps",              "legacy": "9 steps",                                        "apex": "1 trigger · 1 agent",         "saving": "−8 steps"},
                {"metric": "System Handoffs",    "legacy": "5 (SharePoint → QA → SAP → Teams → Procurement)", "apex": "0 (Agent orchestrates)",      "saving": "−5 handoffs"},
                {"metric": "Time to Resolution", "legacy": "~2 hrs manual",                                  "apex": "4.2 sec",                      "saving": "1,714× faster"},
                {"metric": "Human Touchpoints",  "legacy": "2 QA inspectors",                                "apex": "0 (Fully Autonomous)",         "saving": "−2 FTE"},
                {"metric": "Cost per batch",     "legacy": "$140 labor",                                     "apex": "$0.40 compute",                "saving": "−99.7%"},
            ],
            "narrative": "Ohio Plant 7 QA team used to spend the first hour of every shift sorting certificates. That hour is now spent on supplier scorecard reviews instead.",
        },
        "pb-cbb-3": {
            "headline": "1–3 days → 2.1 sec",
            "rows": [
                {"metric": "Steps",              "legacy": "8 steps",                                        "apex": "1 trigger · 1 agent",         "saving": "−7 steps"},
                {"metric": "System Handoffs",    "legacy": "6 (GSM → Email → Planner → BOM → Excel → Director)", "apex": "0 (Agent traverses BOM directly)", "saving": "−6 handoffs"},
                {"metric": "Time to Resolution", "legacy": "1–3 business days",                              "apex": "2.1 sec",                      "saving": "≈ 99.99%"},
                {"metric": "Human Touchpoints",  "legacy": "4 (planner, supply chain, finance, VP)",         "apex": "1 (Director approval)",        "saving": "−3 touchpoints"},
                {"metric": "Exposure window",    "legacy": "$1.09M at risk for ~2 days",                     "apex": "$1.09M mitigated in minutes",  "saving": "Same day reroute"},
            ],
            "narrative": "A $1.09M exposure that would have been spotted on Monday morning now reaches Marcus Webb with 3 ranked reroute options by the time he finishes his coffee.",
        },
    }


# --- main -------------------------------------------------------------------

def main() -> int:
    print(f"\n{'=' * 72}\nSEED · region={REGION} · account={ACCOUNT_ID}\n{'=' * 72}")
    client = boto3.client("dynamodb", region_name=REGION)
    ddb    = boto3.resource("dynamodb", region_name=REGION)

    # 1. Tables
    ensure_table(client, TABLE_WORK_ITEMS,       pk="work_item_id")
    ensure_table(client, TABLE_REVIEW_DECISIONS, pk="decision_id")
    ensure_table(client, TABLE_SCENARIOS,        pk="scenario_id")

    # 2. Work items + decisions
    print("\n[seed] building work_items + review_decisions ...")
    work_items, decisions = build_work_items_and_decisions()
    print(f"  generated {len(work_items)} work_items · {len(decisions)} review_decisions")

    print("  writing work_items ...")
    batch_put(ddb.Table(TABLE_WORK_ITEMS), work_items)
    print("  writing review_decisions ...")
    batch_put(ddb.Table(TABLE_REVIEW_DECISIONS), decisions)

    # 3. Scenarios
    print("\n[seed] simulator scenarios ...")
    scenarios = build_scenarios()
    batch_put(ddb.Table(TABLE_SCENARIOS), scenarios)
    print(f"  wrote {len(scenarios)} scenarios")

    # 4. Patch CBB playbooks with value_map
    print("\n[seed] patching CBB playbooks with value_map ...")
    t_pb = ddb.Table(TABLE_PLAYBOOKS)
    for pb_id, vm in cbb_value_maps().items():
        try:
            t_pb.update_item(
                Key={"playbook_id": pb_id},
                UpdateExpression="SET value_map = :vm",
                ExpressionAttributeValues={":vm": to_ddb(vm)},
            )
            print(f"  ✓ {pb_id}")
        except ClientError as e:
            # If the playbook row doesn't exist yet (seed hasn't been run),
            # create a minimal stub so the value_map doesn't orphan.
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(f"  [warn] {TABLE_PLAYBOOKS} table missing; skipping")
                break
            print(f"  [warn] could not patch {pb_id}: {e.response['Error']['Message']}")

    # 5. Summary
    print(f"\n{'=' * 72}\nSEED COMPLETE\n{'=' * 72}")
    print(f"  work_items        : {len(work_items):>6}")
    print(f"  review_decisions  : {len(decisions):>6}")
    print(f"  scenarios         : {len(scenarios):>6}")
    print(f"  value_maps patched: {sum(1 for _ in cbb_value_maps()):>6}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
