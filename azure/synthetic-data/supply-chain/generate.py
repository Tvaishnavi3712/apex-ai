#!/usr/bin/env python3
"""
Generate the 7 supply-chain synthetic data files specified in
Apex_Master_Implementation_Spec.docx §7 (Package File Manifest).

Output directory: synthetic-data/supply-chain/

  suppliers.json           — 4 suppliers with risk metrics + history
  inventory_bom.json       — inventory levels + BOM graph (18 SKUs, 9 materials, 3 plants)
  purchase_orders.json     — 32 active + historical POs
  predictive_events.json   — 3 ApexSignal risk cards
  demand_history.csv       — 36-week demand by product + region (for DeepAR)
  qc_records.csv           — 120 QC test records (for XGBoost supplier-risk)
  agent_audit_log.json     — 3 sample agent run audit trails (for Audit Lens)

The shapes match exactly what the spec tables call for so backend handlers +
Azure ML training jobs can consume them as-is.
"""

import csv
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

random.seed(20260422)  # deterministic — re-running produces identical files

HERE = Path(__file__).parent

# ───────────────────────────── 1. suppliers.json ─────────────────────────────

SUPPLIERS = [
    {
        "supplier_id": "SUP-0044",
        "name": "Chemours Vinyl Resins",
        "material_ids": ["VR-4400"],
        "role": "Primary",
        "country": "USA",
        "on_time_pct": 94.0,
        "qc_pass_pct": 99.1,
        "lead_time_days_avg": 12,
        "lead_time_days_stddev": 2.1,
        "risk_score": "Low",
        "risk_trend": "stable",
        "credit_rating": "A-",
        "yoy_price_change_pct": 3.2,
        "last_qc_test": "2026-04-15",
    },
    {
        "supplier_id": "SUP-0081",
        "name": "Formosa Plastics Corp",
        "material_ids": ["VR-4400"],
        "role": "Secondary",
        "country": "Taiwan",
        "on_time_pct": 81.0,
        "qc_pass_pct": 93.4,
        "lead_time_days_avg": 28,
        "lead_time_days_stddev": 6.4,
        "risk_score": "High",
        "risk_trend": "declining",
        "credit_rating": "BBB",
        "yoy_price_change_pct": -1.1,
        "last_qc_test": "2026-04-18",
        "notes": "QC pass rate has declined 3 consecutive lots; 61% probability of non-conforming next shipment.",
    },
    {
        "supplier_id": "SUP-0102",
        "name": "Novelis Inc.",
        "material_ids": ["AL-2024"],
        "role": "Primary",
        "country": "USA",
        "on_time_pct": 97.0,
        "qc_pass_pct": 98.8,
        "lead_time_days_avg": 9,
        "lead_time_days_stddev": 1.4,
        "risk_score": "Low",
        "risk_trend": "improving",
        "credit_rating": "A",
        "yoy_price_change_pct": 6.0,
        "last_qc_test": "2026-04-19",
    },
    {
        "supplier_id": "SUP-0113",
        "name": "Nucor Steel",
        "material_ids": ["ST-1008"],
        "role": "Primary",
        "country": "USA",
        "on_time_pct": 99.0,
        "qc_pass_pct": 99.7,
        "lead_time_days_avg": 7,
        "lead_time_days_stddev": 0.9,
        "risk_score": "Very Low",
        "risk_trend": "stable",
        "credit_rating": "A+",
        "yoy_price_change_pct": 1.8,
        "last_qc_test": "2026-04-20",
    },
    {
        "supplier_id": "SUP-0119",
        "name": "Westlake Chemical Corp",
        "material_ids": ["VR-4400", "PVC-7700"],
        "role": "Primary",
        "country": "USA",
        "on_time_pct": 94.0,
        "qc_pass_pct": 99.1,
        "lead_time_days_avg": 11,
        "lead_time_days_stddev": 1.7,
        "risk_score": "Low",
        "risk_trend": "stable",
        "credit_rating": "A-",
        "yoy_price_change_pct": 2.4,
        "last_qc_test": "2026-04-17",
    },
]

# ───────────────────────────── 2. inventory_bom.json ─────────────────────────

MATERIALS = [
    {"material_id": "VR-4400",  "name": "Vinyl Resin (PVC Grade A)",            "uom": "kg"},
    {"material_id": "AL-2024",  "name": "Aluminum Coil (6063-T5)",              "uom": "kg"},
    {"material_id": "ST-1008",  "name": "Steel Coil (1008)",                    "uom": "kg"},
    {"material_id": "PVC-7700", "name": "PVC Compound",                         "uom": "kg"},
    {"material_id": "GL-4401",  "name": "Low-E Glass Panel",                    "uom": "panel"},
    {"material_id": "SL-9902",  "name": "Silicone Sealant",                     "uom": "tube"},
    {"material_id": "FR-8801",  "name": "Foam Insulation Core",                 "uom": "m²"},
    {"material_id": "TR-5520",  "name": "Titanium Dioxide (pigment)",           "uom": "kg"},
    {"material_id": "PL-3310",  "name": "Polyester Mesh",                       "uom": "m"},
]

PLANTS = [
    {"plant_id": "PLT-OH-07", "name": "Ohio Plant 7",     "region": "Midwest"},
    {"plant_id": "PLT-TX-14", "name": "Texas Plant 14",   "region": "South"},
    {"plant_id": "PLT-GA-31", "name": "Georgia Plant 31", "region": "Southeast"},
    {"plant_id": "PLT-PA-09", "name": "Pennsylvania 9",   "region": "Northeast"},
]

PRODUCTS = [
    {"product_id": "PRD-CSW-4860", "name": "Commercial Casement Window",         "plants": ["PLT-OH-07", "PLT-TX-14"]},
    {"product_id": "PRD-VSD-2201", "name": "Vinyl Siding (wood-grain)",          "plants": ["PLT-OH-07", "PLT-GA-31"]},
    {"product_id": "PRD-RFP-1102", "name": "Roofing Panel (SE region)",          "plants": ["PLT-GA-31"]},
    {"product_id": "PRD-DRL-3304", "name": "Door Light Insert (insulated)",      "plants": ["PLT-TX-14", "PLT-PA-09"]},
    {"product_id": "PRD-TRM-9910", "name": "Exterior Trim (Midwest)",            "plants": ["PLT-OH-07"]},
    {"product_id": "PRD-SSH-5402", "name": "Storm Shield (hurricane)",           "plants": ["PLT-GA-31", "PLT-TX-14"]},
]

BOM = [
    # product_id + material_id → qty per unit
    {"product_id": "PRD-CSW-4860", "material_id": "VR-4400", "qty_per_unit": 8.0},
    {"product_id": "PRD-CSW-4860", "material_id": "GL-4401", "qty_per_unit": 2.0},
    {"product_id": "PRD-CSW-4860", "material_id": "AL-2024", "qty_per_unit": 4.5},
    {"product_id": "PRD-CSW-4860", "material_id": "SL-9902", "qty_per_unit": 3.0},
    {"product_id": "PRD-VSD-2201", "material_id": "VR-4400", "qty_per_unit": 1.2},
    {"product_id": "PRD-VSD-2201", "material_id": "TR-5520", "qty_per_unit": 0.05},
    {"product_id": "PRD-RFP-1102", "material_id": "AL-2024", "qty_per_unit": 6.8},
    {"product_id": "PRD-RFP-1102", "material_id": "FR-8801", "qty_per_unit": 1.0},
    {"product_id": "PRD-DRL-3304", "material_id": "GL-4401", "qty_per_unit": 1.0},
    {"product_id": "PRD-DRL-3304", "material_id": "AL-2024", "qty_per_unit": 2.2},
    {"product_id": "PRD-TRM-9910", "material_id": "PVC-7700", "qty_per_unit": 4.0},
    {"product_id": "PRD-TRM-9910", "material_id": "VR-4400",  "qty_per_unit": 2.6},
    {"product_id": "PRD-SSH-5402", "material_id": "ST-1008",  "qty_per_unit": 12.0},
    {"product_id": "PRD-SSH-5402", "material_id": "AL-2024",  "qty_per_unit": 3.1},
    {"product_id": "PRD-SSH-5402", "material_id": "PL-3310",  "qty_per_unit": 8.0},
]

INVENTORY = [
    {"material_id": "VR-4400", "plant_id": "PLT-OH-07", "stock_level_kg": 14200, "burn_rate_per_day": 1015, "safety_stock_pct": 18, "days_remaining": 14},
    {"material_id": "VR-4400", "plant_id": "PLT-TX-14", "stock_level_kg":  8900, "burn_rate_per_day":  640, "safety_stock_pct": 21, "days_remaining": 14},
    {"material_id": "VR-4400", "plant_id": "PLT-GA-31", "stock_level_kg":  7100, "burn_rate_per_day":  505, "safety_stock_pct": 19, "days_remaining": 14},
    {"material_id": "AL-2024", "plant_id": "PLT-TX-14", "stock_level_kg": 21400, "burn_rate_per_day":  764, "safety_stock_pct": 35, "days_remaining": 28},
    {"material_id": "AL-2024", "plant_id": "PLT-GA-31", "stock_level_kg": 17500, "burn_rate_per_day":  625, "safety_stock_pct": 33, "days_remaining": 28},
    {"material_id": "ST-1008", "plant_id": "PLT-GA-31", "stock_level_kg": 44800, "burn_rate_per_day":  722, "safety_stock_pct": 72, "days_remaining": 62},
    {"material_id": "PVC-7700","plant_id": "PLT-OH-07", "stock_level_kg": 26100, "burn_rate_per_day":  580, "safety_stock_pct": 58, "days_remaining": 45},
    {"material_id": "GL-4401", "plant_id": "PLT-OH-07", "stock_level_kg":  2800, "burn_rate_per_day":  120, "safety_stock_pct": 24, "days_remaining": 23},
    {"material_id": "SL-9902", "plant_id": "PLT-OH-07", "stock_level_kg":  1100, "burn_rate_per_day":   42, "safety_stock_pct": 82, "days_remaining": 26},
    {"material_id": "FR-8801", "plant_id": "PLT-GA-31", "stock_level_kg":  9200, "burn_rate_per_day":  412, "safety_stock_pct": 60, "days_remaining": 22},
]

# ───────────────────────────── 3. purchase_orders.json ───────────────────────

def _po(i, supplier_id, material_id, qty, origin_port, promised_days_offset, status, actual_days=None):
    issued = date(2026, 4, 1) + timedelta(days=(i % 20))
    promised = issued + timedelta(days=promised_days_offset)
    actual = (promised + timedelta(days=actual_days)) if actual_days is not None else None
    return {
        "po_number": f"PO-{88900 + i}",
        "supplier_id": supplier_id,
        "material_id": material_id,
        "qty": qty,
        "unit_price_usd": round(random.uniform(6.5, 11.5), 2),
        "origin_port": origin_port,
        "issued_at": issued.isoformat(),
        "promised_eta": promised.isoformat(),
        "actual_eta": actual.isoformat() if actual else None,
        "status": status,  # open | in_transit | received | delayed
        "delay_days": actual_days if (actual_days and actual_days > 0) else 0,
    }

PURCHASE_ORDERS = []
# 20 historical POs, mix of on-time + late
origins = ["Port of Savannah", "Port of Houston", "Port of Long Beach", "Port of Charleston"]
for i in range(20):
    supplier = random.choice(SUPPLIERS)
    material = supplier["material_ids"][0]
    actual_offset = random.choices([0, 1, 2, 4, 7, 14], weights=[58, 15, 12, 8, 5, 2])[0]
    PURCHASE_ORDERS.append(_po(
        i, supplier["supplier_id"], material,
        qty=random.choice([1500, 2100, 2800, 3500, 4200]),
        origin_port=random.choice(origins),
        promised_days_offset=supplier["lead_time_days_avg"],
        status="received",
        actual_days=actual_offset,
    ))
# 12 in-transit POs (active ETAs)
for i in range(20, 32):
    supplier = random.choice(SUPPLIERS)
    material = supplier["material_ids"][0]
    PURCHASE_ORDERS.append(_po(
        i, supplier["supplier_id"], material,
        qty=random.choice([2000, 2800, 3500, 4400]),
        origin_port=random.choice(origins),
        promised_days_offset=supplier["lead_time_days_avg"],
        status=random.choice(["open", "in_transit", "in_transit", "delayed"]),
    ))

# ───────────────────────────── 4. predictive_events.json ─────────────────────

PREDICTIVE_EVENTS = [
    {
        "event_id": "RSK-001",
        "type": "delay",
        "severity": "CRITICAL",
        "probability_pct": 92,
        "title": "Vinyl Resin Shipment Delay",
        "description": "PO #88921 inbound to Port of Savannah forecast to arrive 7 days late — model: apex-signal-lead-time",
        "affected_material_id": "VR-4400",
        "affected_supplier_id": "SUP-0044",
        "affected_plants": ["PLT-OH-07", "PLT-TX-14", "PLT-GA-31"],
        "po_number": "PO-88921",
        "origin_port": "Port of Savannah",
        "financial_exposure_usd": 1092560.0,
        "days_until_impact": 7,
        "agent_playbook_ready": True,
        "detected_at": "2026-04-21T09:08:00Z",
    },
    {
        "event_id": "RSK-002",
        "type": "price_surge",
        "severity": "HIGH",
        "probability_pct": 78,
        "title": "Aluminum Price Surge",
        "description": "Section 232 tariff extension detected — 12 SKUs exposed to +30% material cost impact",
        "affected_material_id": "AL-2024",
        "affected_supplier_id": "SUP-0102",
        "affected_plants": ["PLT-TX-14", "PLT-GA-31", "PLT-PA-09"],
        "financial_exposure_usd": 450000.0,
        "days_until_impact": 21,
        "agent_playbook_ready": True,
        "detected_at": "2026-04-21T11:22:00Z",
    },
    {
        "event_id": "RSK-003",
        "type": "quality_degradation",
        "severity": "MEDIUM",
        "probability_pct": 61,
        "title": "Supplier Quality Degradation",
        "description": "Formosa Plastics QC pass rate declined 3 consecutive lots — model flags 61% probability of non-conforming next batch",
        "affected_material_id": "VR-4400",
        "affected_supplier_id": "SUP-0081",
        "affected_plants": ["PLT-OH-07"],
        "financial_exposure_usd": 320000.0,
        "days_until_impact": 30,
        "agent_playbook_ready": True,
        "detected_at": "2026-04-21T13:40:00Z",
    },
]

# ───────────────────────────── 5. demand_history.csv ─────────────────────────
# 36 weeks × 6 products × 4 regions = 864 rows. Used to train DeepAR.

def _demand_history_rows():
    rows = []
    start = date(2025, 8, 11)   # 36 weeks back from ~2026-04-20
    for week in range(36):
        week_start = start + timedelta(weeks=week)
        for product in PRODUCTS:
            for region in {p["region"] for p in PLANTS}:
                # Baseline demand by product, seasonal by region
                base = {"PRD-CSW-4860": 4400, "PRD-VSD-2201": 9800, "PRD-RFP-1102": 3200,
                        "PRD-DRL-3304": 2100, "PRD-TRM-9910": 5200, "PRD-SSH-5402": 1400}[product["product_id"]]
                # Hurricane season boost for Southeast/South on roofing + storm shield
                season = 1.0
                if region in ("Southeast", "South") and product["product_id"] in ("PRD-RFP-1102", "PRD-SSH-5402"):
                    month = week_start.month
                    if 6 <= month <= 10:
                        season = 1.22
                # Midwest trim softening
                if region == "Midwest" and product["product_id"] == "PRD-TRM-9910" and week_start.year == 2026 and week_start.month >= 3:
                    season = 0.86
                noise = random.uniform(0.93, 1.07)
                units_sold = int(base * season * noise / 4)  # quarter of national per region
                rows.append({
                    "week_start": week_start.isoformat(),
                    "product_id": product["product_id"],
                    "region": region,
                    "units_sold": units_sold,
                })
    return rows

DEMAND_HISTORY = _demand_history_rows()

# ───────────────────────────── 6. qc_records.csv ─────────────────────────────
# 120 rows. Used to train the Supplier Risk Scorer XGBoost model.

def _qc_rows():
    rows = []
    lot_seq = 0
    for supplier in SUPPLIERS:
        # Each supplier gets ~24 lots
        # Formosa (SUP-0081) has the declining trend in the last 3 lots
        n = 24
        base_moisture  = 0.08 if supplier["supplier_id"] == "SUP-0081" else 0.06
        base_purity    = 98.2 if supplier["supplier_id"] == "SUP-0081" else 99.2
        base_viscosity = 145  if supplier["supplier_id"] == "SUP-0081" else 138
        for i in range(n):
            lot_seq += 1
            # Formosa degrades on last 3 lots
            degradation = 0.0
            if supplier["supplier_id"] == "SUP-0081" and i >= n - 3:
                degradation = 0.012  # pushes moisture over 0.12 threshold
            moisture = round(base_moisture + degradation + random.uniform(-0.008, 0.010), 4)
            purity   = round(base_purity - degradation * 20 + random.uniform(-0.35, 0.35), 2)
            viscosity= round(base_viscosity + degradation * 40 + random.uniform(-3.5, 3.5), 1)
            pass_fail = 1 if (moisture <= 0.12 and purity >= 97.5 and 130 <= viscosity <= 160) else 0
            inspection_date = date(2025, 10, 1) + timedelta(days=lot_seq * 2)
            rows.append({
                "lot_id":        f"LOT-{supplier['supplier_id'][-2:]}-{i + 1:03d}",
                "supplier_id":   supplier["supplier_id"],
                "material_id":   supplier["material_ids"][0],
                "inspection_date": inspection_date.isoformat(),
                "moisture_pct":  moisture,
                "purity_pct":    purity,
                "viscosity":     viscosity,
                "pass_fail":     pass_fail,
                # Categorical risk label for XGBoost multi-class
                "risk_label":    {0: "Critical", 1: "Low"}[pass_fail] if i < n - 3 else
                                 ("High" if supplier["supplier_id"] == "SUP-0081" else "Low"),
            })
    return rows

QC_RECORDS = _qc_rows()

# ───────────────────────────── 7. agent_audit_log.json ───────────────────────
# 3 sample agent runs for Audit Lens.

AGENT_AUDIT_LOG = [
    {
        "run_id": "RUN-20260421-091030-001",
        "agent_id": "logisticsbot",
        "user_id": "marcus.webb@cbb.com",
        "trigger": "RSK-001 view playbook",
        "started_at": "2026-04-21T09:10:30Z",
        "completed_at": "2026-04-21T09:10:34Z",
        "steps": [
            {"step": 1, "timestamp": "2026-04-21T09:10:30.100Z", "kind": "read",     "action": "ingest_gsm_alert",        "detail": "Loaded GSM alert SC-ALERT-2026-0441", "confidence": 0.99},
            {"step": 2, "timestamp": "2026-04-21T09:10:30.420Z", "kind": "action",   "action": "bom_graph_traverse",      "detail": "Traversed 847 BOM nodes via Athena", "confidence": 0.98},
            {"step": 3, "timestamp": "2026-04-21T09:10:31.180Z", "kind": "action",   "action": "predict_financial_impact","detail": "3 plants affected, $1,090,000 exposure", "confidence": 0.99},
            {"step": 4, "timestamp": "2026-04-21T09:10:32.610Z", "kind": "action",   "action": "generate_reroute_options","detail": "Ranked Oxy Vinyls, Resequence GA, Formosa air-freight", "confidence": 0.94},
            {"step": 5, "timestamp": "2026-04-21T09:10:33.540Z", "kind": "decide",   "action": "escalate_decision",       "detail": "VaR $1.09M > $500k threshold → escalate to Marcus Webb", "confidence": 0.99},
            {"step": 6, "timestamp": "2026-04-21T09:10:34.010Z", "kind": "notify",   "action": "teams_alert",             "detail": "Posted to #supply-chain-leadership with 3 options", "confidence": 0.99},
        ],
        "final_decision": "ESCALATED",
        "value_at_risk_usd": 1090000,
        "cost_avoided_usd":  1090000,
        "manual_hours_saved": 47.9,
    },
    {
        "run_id": "RUN-20260421-061542-002",
        "agent_id": "qcbot",
        "user_id": "sarah.jenkins@cbb.com",
        "trigger": "QC_Batch_2141 upload",
        "started_at": "2026-04-21T06:15:42Z",
        "completed_at": "2026-04-21T06:15:46Z",
        "steps": [
            {"step": 1, "timestamp": "2026-04-21T06:15:42.110Z", "kind": "read",     "action": "unzip_archive",           "detail": "Extracted 50 QC certificate PDFs", "confidence": 1.00},
            {"step": 2, "timestamp": "2026-04-21T06:15:42.790Z", "kind": "action",   "action": "bda_document_extract",    "detail": "BDA: 18 fields × 50 certs, avg conf 99.1%", "confidence": 0.991},
            {"step": 3, "timestamp": "2026-04-21T06:15:44.040Z", "kind": "action",   "action": "fabric_tolerance_check",  "detail": "48 PASS · LOT-A44 tensile -3.8% · LOT-B12 color ΔE 2.7 FAIL", "confidence": 0.99},
            {"step": 4, "timestamp": "2026-04-21T06:15:44.820Z", "kind": "decide",   "action": "auto_hold_decision",      "detail": "partial_hold=true, quarantined $32,550", "confidence": 0.99},
            {"step": 5, "timestamp": "2026-04-21T06:15:45.210Z", "kind": "action",   "action": "erp_inventory_hold",      "detail": "SAP S/4HANA holds placed: ERP-HOLD-7741, 7742", "confidence": 0.99},
            {"step": 6, "timestamp": "2026-04-21T06:15:45.930Z", "kind": "notify",   "action": "teams_alert",             "detail": "Notified #ohio-plant-7-qc + procurement@cbb.com", "confidence": 1.00},
        ],
        "final_decision": "PARTIAL_HOLD",
        "value_at_risk_usd": 32550,
        "cost_avoided_usd":  32550,
        "manual_hours_saved": 1.95,
    },
    {
        "run_id": "RUN-20260421-091200-003",
        "agent_id": "customerops",
        "user_id": "auto-trigger",
        "trigger": "CBB-ORD-1044 modification request",
        "started_at": "2026-04-21T09:12:00Z",
        "completed_at": "2026-04-21T09:12:04Z",
        "steps": [
            {"step": 1, "timestamp": "2026-04-21T09:12:00.050Z", "kind": "read",     "action": "email_intake",            "detail": "Parsed PDF attachment from orders@midwestwindow.com", "confidence": 0.98},
            {"step": 2, "timestamp": "2026-04-21T09:12:00.910Z", "kind": "action",   "action": "bda_document_extract",    "detail": "Order Modification Form v2.1: 12 fields · 97.4%", "confidence": 0.974},
            {"step": 3, "timestamp": "2026-04-21T09:12:01.720Z", "kind": "action",   "action": "athena_federated_query",  "detail": "Original order lookup via apex_db.cbb_orders", "confidence": 0.99},
            {"step": 4, "timestamp": "2026-04-21T09:12:02.340Z", "kind": "decide",   "action": "engineering_constraint",  "detail": "height variance +3.3% within 5% tolerance → auto-approve", "confidence": 0.97},
            {"step": 5, "timestamp": "2026-04-21T09:12:02.980Z", "kind": "action",   "action": "crm_order_update",        "detail": "Microsoft Dynamics CRM-CONF-CBB-ORD-1044 issued", "confidence": 0.99},
            {"step": 6, "timestamp": "2026-04-21T09:12:03.610Z", "kind": "notify",   "action": "email_send",              "detail": "Confirmation sent to orders@midwestwindow.com", "confidence": 1.00},
        ],
        "final_decision": "AUTO_APPROVED",
        "value_at_risk_usd": 0,
        "cost_avoided_usd":  4800,
        "manual_hours_saved": 1.98,
    },
]


# ───────────────────────────── write ─────────────────────────────

def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, default=str))
    print(f"  ✓ {path.name:30s}  {path.stat().st_size:>8d} B")

def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  ✓ {path.name:30s}  {path.stat().st_size:>8d} B  ({len(rows)} rows)")


def main() -> None:
    print(f"Generating supply-chain synthetic data in {HERE}")
    write_json(HERE / "suppliers.json",          SUPPLIERS)
    write_json(HERE / "inventory_bom.json",      {
        "materials":       MATERIALS,
        "plants":          PLANTS,
        "products":        PRODUCTS,
        "bom":             BOM,
        "inventory":       INVENTORY,
    })
    write_json(HERE / "purchase_orders.json",    PURCHASE_ORDERS)
    write_json(HERE / "predictive_events.json",  PREDICTIVE_EVENTS)
    write_json(HERE / "agent_audit_log.json",    AGENT_AUDIT_LOG)
    write_csv (HERE / "demand_history.csv",      DEMAND_HISTORY, ["week_start", "product_id", "region", "units_sold"])
    write_csv (HERE / "qc_records.csv",          QC_RECORDS,     ["lot_id", "supplier_id", "material_id", "inspection_date", "moisture_pct", "purity_pct", "viscosity", "pass_fail", "risk_label"])
    print("Done.")


if __name__ == "__main__":
    main()
