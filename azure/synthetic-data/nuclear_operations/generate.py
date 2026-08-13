"""
STP Nuclear Operations — synthetic data generator.

Produces all JSON fixtures consumed by:
  • actions/nuclear_operations/* handlers
  • foundry_agent-agents/apex-stp-* agents
  • the OpenSearch chatstp-knowledge index ingestion

DESIGN
------
* Deterministic — random seed locked to 42, so re-running yields byte-identical
  output. This is essential for demo dry-runs.
* Idempotent — without `--force`, an existing artifact is skipped.
* Dependency-light — stdlib + numpy + pandas + pyarrow. PDF generation is
  optional (requires reportlab); when reportlab is missing, JSON+text proxies
  are written instead of PDFs so downstream code keeps working.
* The policy/procedure corpus is hand-tuned (not random). The hero answers
  for the demo come straight out of these dicts, so accuracy matters more
  than volume.

USAGE
-----
    python3 generate.py            # generate everything (skip what exists)
    python3 generate.py --force    # regenerate everything
    python3 generate.py --validate # re-read every output and assert schemas
    python3 generate.py --quick    # smaller corpus (60 WOs vs 5000) — for CI

The generator targets ~5 minutes runtime for full output on a laptop.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Determinism — every random source seeded once.
# ---------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUT_DIR = Path(__file__).resolve().parent
_NOW = datetime(2026, 4, 30, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Tunables (CLI --quick halves these)
# ---------------------------------------------------------------------------
@dataclass
class Tunables:
    num_units: int = 3
    num_systems: int = 25
    num_equipment: int = 600
    num_pm_schedules: int = 600
    num_work_orders: int = 5000
    num_change_history: int = 800
    num_failure_events: int = 40
    num_personnel: int = 200
    num_failure_modes: int = 25
    num_anomalies: int = 6
    sensor_assets: int = 30
    sensor_days: int = 90
    sensor_interval_minutes: int = 5

    def quick(self) -> "Tunables":
        return Tunables(
            num_units=2,
            num_systems=10,
            num_equipment=80,
            num_pm_schedules=80,
            num_work_orders=300,
            num_change_history=80,
            num_failure_events=15,
            num_personnel=40,
            num_failure_modes=15,
            num_anomalies=6,
            sensor_assets=8,
            sensor_days=20,
            sensor_interval_minutes=15,
        )


# ---------------------------------------------------------------------------
# Hand-tuned reference data (these power the hero demo answers)
# ---------------------------------------------------------------------------

# 6 hero equipment items the demo cites by ID — ALWAYS present regardless of
# tunables.num_equipment. Synthetic equipment_ids fill the rest.
HERO_EQUIPMENT: List[Dict[str, Any]] = [
    {"equipment_id": "P-3A", "system_id": "RCS", "unit_id": "U1", "type": "pump",
     "manufacturer": "Westinghouse", "model": "Model-93A RCP",
     "install_date": "2003-04-12", "criticality": "Q", "train_id": "A",
     "location_room": "AB-23-RCP-Loop-3"},
    {"equipment_id": "P-3B", "system_id": "RCS", "unit_id": "U1", "type": "pump",
     "manufacturer": "Westinghouse", "model": "Model-93A RCP",
     "install_date": "2003-04-15", "criticality": "Q", "train_id": "B",
     "location_room": "AB-23-RCP-Loop-3"},
    {"equipment_id": "P-3C", "system_id": "RCS", "unit_id": "U1", "type": "pump",
     "manufacturer": "Westinghouse", "model": "Model-93A RCP",
     "install_date": "2003-04-18", "criticality": "Q", "train_id": "C",
     "location_room": "AB-23-RCP-Loop-3"},
    {"equipment_id": "EDG-2", "system_id": "EDG", "unit_id": "U1", "type": "edg",
     "manufacturer": "Caterpillar", "model": "C175-20",
     "install_date": "1999-08-22", "criticality": "Q", "train_id": "B",
     "location_room": "DG-BLDG-2"},
    {"equipment_id": "MOV-7B", "system_id": "ESW", "unit_id": "U1", "type": "valve",
     "manufacturer": "Limitorque", "model": "SMB-3-150",
     "install_date": "2001-11-03", "criticality": "Q", "train_id": "B",
     "location_room": "TB-12-ESW-Pen"},
    {"equipment_id": "HX-22A", "system_id": "CCW", "unit_id": "U1", "type": "hx",
     "manufacturer": "Foster Wheeler", "model": "FW-CCW-22",
     "install_date": "1988-06-15", "criticality": "A", "train_id": "A",
     "location_room": "AB-15-CCW-North"},
]

# 4 hero personnel — referenced by name in the demo script.
HERO_PERSONNEL: List[Dict[str, Any]] = [
    {"employee_id": "EMP-1042", "name": "Diane Okafor", "role": "system_engineer",
     "hire_date": "2008-03-01", "retirement_eligible_date": "2038-03-01",
     "certifications": ["Senior Reactor Engineer", "ASME Section XI Inspector"]},
    {"employee_id": "EMP-2117", "name": "Marcus Holloway", "role": "mech_tech",
     "hire_date": "2011-09-12", "retirement_eligible_date": "2041-09-12",
     "certifications": ["Mechanical Maintenance II", "Confined-Space Entry"]},
    {"employee_id": "EMP-2243", "name": "Jamal Greene", "role": "mech_tech",
     "hire_date": "2014-06-20", "retirement_eligible_date": "2044-06-20",
     "certifications": ["Mechanical Maintenance II"]},
    {"employee_id": "EMP-0871", "name": "Tony Garcia", "role": "system_engineer",
     "hire_date": "1996-02-14", "retirement_eligible_date": "2026-02-14",
     "certifications": ["EDG Specialist", "ASME Section III"]},
]

# Failure mode catalog — 25 entries covering common nuclear-plant failure types.
FAILURE_MODES: List[Dict[str, Any]] = [
    {"mode_id": "FM-001", "name": "bearing_seizure",
     "early_indicators": ["vibration > 4 mm/s", "bearing_temp > 85C"],
     "typical_lead_days": 14,
     "mitigation_actions": ["Replace bearing", "Inspect shaft alignment", "Verify lube oil quality"]},
    {"mode_id": "FM-002", "name": "seal_leak",
     "early_indicators": ["oil_pressure drop > 5%", "visible drip rate > 2 drops/min"],
     "typical_lead_days": 21,
     "mitigation_actions": ["Replace mechanical seal", "Test seal flush system"]},
    {"mode_id": "FM-003", "name": "motor_winding_fault",
     "early_indicators": ["motor_current step > 15%", "winding_temp > 130C"],
     "typical_lead_days": 7,
     "mitigation_actions": ["Megger test", "Replace motor", "Check cooling fan"]},
    {"mode_id": "FM-004", "name": "valve_stem_galling",
     "early_indicators": ["stroke_time > spec", "torque > spec"],
     "typical_lead_days": 30,
     "mitigation_actions": ["Lubricate stem", "Inspect packing", "Replace stem if scored"]},
    {"mode_id": "FM-005", "name": "control_card_failure",
     "early_indicators": ["intermittent signal", "memory_check fail"],
     "typical_lead_days": 5,
     "mitigation_actions": ["Replace card", "Restore configuration"]},
    {"mode_id": "FM-006", "name": "packing_leak",
     "early_indicators": ["weep > 1 drop/min", "stem temperature elevated"],
     "typical_lead_days": 45,
     "mitigation_actions": ["Adjust gland", "Repack", "Replace stem"]},
    {"mode_id": "FM-007", "name": "vibration_excursion",
     "early_indicators": ["axial vibration spike", "harmonic content shift"],
     "typical_lead_days": 10,
     "mitigation_actions": ["Balance impeller", "Verify foundation grout", "Bearing inspection"]},
    {"mode_id": "FM-008", "name": "thermal_overcurrent",
     "early_indicators": ["bearing_temp creep", "motor_current rise"],
     "typical_lead_days": 8,
     "mitigation_actions": ["Verify cooling water flow", "Inspect insulation", "Reduce load if possible"]},
    {"mode_id": "FM-009", "name": "design_deficiency",
     "early_indicators": ["multi-channel drift", "repeated failures across train"],
     "typical_lead_days": 60,
     "mitigation_actions": ["Engineering change request", "Vendor consultation"]},
    {"mode_id": "FM-010", "name": "vendor_quality",
     "early_indicators": ["early-life failure", "lot-correlated defects"],
     "typical_lead_days": 90,
     "mitigation_actions": ["Lot quarantine", "Vendor corrective action request"]},
    {"mode_id": "FM-011", "name": "operator_error",
     "early_indicators": ["procedure deviation", "post-evolution alarm"],
     "typical_lead_days": 0,
     "mitigation_actions": ["Just-in-time training", "Procedure revision review"]},
    {"mode_id": "FM-012", "name": "thermal_cycling_fatigue",
     "early_indicators": ["weld crack indications", "leak-by"],
     "typical_lead_days": 120,
     "mitigation_actions": ["UT inspection", "Weld repair", "Stress relief"]},
    {"mode_id": "FM-013", "name": "instrumentation_drift",
     "early_indicators": ["cal-check out of tolerance"],
     "typical_lead_days": 90,
     "mitigation_actions": ["Recalibrate", "Replace transmitter"]},
    {"mode_id": "FM-014", "name": "lubrication_loss",
     "early_indicators": ["oil level low alarm", "bearing_temp rise"],
     "typical_lead_days": 3,
     "mitigation_actions": ["Top up oil", "Investigate leak source"]},
    {"mode_id": "FM-015", "name": "corrosion_pitting",
     "early_indicators": ["UT thickness loss", "visible pitting on coupons"],
     "typical_lead_days": 365,
     "mitigation_actions": ["Coating refurb", "Cathodic protection", "Material upgrade"]},
    {"mode_id": "FM-016", "name": "electrical_breaker_trip",
     "early_indicators": ["frequent reset", "mechanism wear"],
     "typical_lead_days": 14,
     "mitigation_actions": ["Trip-unit calibration", "Mechanism overhaul"]},
    {"mode_id": "FM-017", "name": "fan_belt_wear",
     "early_indicators": ["belt-flap noise", "tensioner travel"],
     "typical_lead_days": 30,
     "mitigation_actions": ["Replace belt", "Verify alignment"]},
    {"mode_id": "FM-018", "name": "filter_clog",
     "early_indicators": ["differential pressure rise"],
     "typical_lead_days": 7,
     "mitigation_actions": ["Replace filter element"]},
    {"mode_id": "FM-019", "name": "coupling_misalignment",
     "early_indicators": ["1x rotation vibration peak"],
     "typical_lead_days": 14,
     "mitigation_actions": ["Laser-align", "Replace coupling if cracked"]},
    {"mode_id": "FM-020", "name": "gasket_failure",
     "early_indicators": ["weep", "small leak rate increase"],
     "typical_lead_days": 60,
     "mitigation_actions": ["Replace gasket", "Verify flange surface"]},
    {"mode_id": "FM-021", "name": "loose_bolting",
     "early_indicators": ["torque-check failure", "vibration anomaly"],
     "typical_lead_days": 30,
     "mitigation_actions": ["Re-torque to spec", "Replace damaged bolts"]},
    {"mode_id": "FM-022", "name": "cooling_water_fouling",
     "early_indicators": ["heat exchanger DP rise", "outlet temperature rise"],
     "typical_lead_days": 90,
     "mitigation_actions": ["Chemical clean", "Mechanical clean"]},
    {"mode_id": "FM-023", "name": "diaphragm_rupture",
     "early_indicators": ["fluid in actuator vent"],
     "typical_lead_days": 0,
     "mitigation_actions": ["Replace diaphragm", "Inspect actuator"]},
    {"mode_id": "FM-024", "name": "encoder_fault",
     "early_indicators": ["position-feedback noise"],
     "typical_lead_days": 7,
     "mitigation_actions": ["Replace encoder"]},
    {"mode_id": "FM-025", "name": "age_wear",
     "early_indicators": ["multiple subsystems showing degradation"],
     "typical_lead_days": 180,
     "mitigation_actions": ["Component replacement", "End-of-life evaluation"]},
]

# Hand-tuned policy corpus — verbatim text used by PolicyAgent for citations.
# Match what's already embedded in apex-stp-policy-agent/agent.py so the
# in-process fallback and the JSON corpus stay aligned.
POLICY_CORPUS: List[Dict[str, Any]] = [
    {
        "doc_id": "STP-415",
        "doc_number": "STP-415",
        "title": "Business Travel & Per-Diem Allowances",
        "effective_date": "2024-06-01",
        "revision": "Rev 4",
        "owner": "STP Finance / Travel Services",
        "nrc_classification": "Public",
        "sections": [
            {"section": "3.1", "heading": "Lodging",
             "text": "Lodging at on-site business meetings shall be reimbursed at actual cost up to the GSA per-diem rate for the locality."},
            {"section": "3.2", "heading": "Meal Allowance",
             "text": "Per-diem meal allowance for on-site business meetings shall not exceed $75.00 per traveler per calendar day, inclusive of gratuity."},
            {"section": "3.3", "heading": "Incidental Expenses",
             "text": "Incidental expenses (parking, tolls, business calls) shall be reimbursed at actual cost with itemized receipts."},
        ],
        "keywords": ["meal", "allowance", "per-diem", "travel", "site-meeting", "business travel", "$75", "75"],
    },
    {
        "doc_id": "STP-401", "doc_number": "STP-401", "title": "Overtime Authorization",
        "effective_date": "2023-09-15", "revision": "Rev 2", "owner": "STP HR",
        "nrc_classification": "Internal",
        "sections": [
            {"section": "2.1", "heading": "Approval Threshold",
             "text": "All overtime hours in excess of 16 per pay period require Manager approval prior to work performance."},
            {"section": "2.2", "heading": "Fatigue Management",
             "text": "Cumulative work hours shall conform to 10 CFR 26 fatigue-management limits; covered employees may not exceed 16 hours in any 24-hour period without supervisor sign-off."},
        ],
        "keywords": ["overtime", "fatigue", "10 CFR 26", "manager approval"],
    },
    {
        "doc_id": "STP-402", "doc_number": "STP-402", "title": "Paid Time Off",
        "effective_date": "2024-01-01", "revision": "Rev 5", "owner": "STP HR",
        "nrc_classification": "Internal",
        "sections": [
            {"section": "1.1", "heading": "Accrual",
             "text": "Full-time employees accrue PTO at 1.92 hours per pay period during the first 5 years, 2.77 thereafter, capped at 200 hours."},
        ],
        "keywords": ["pto", "paid time off", "accrual", "vacation"],
    },
    {
        "doc_id": "STP-403", "doc_number": "STP-403", "title": "Training Reimbursement",
        "effective_date": "2023-04-01", "revision": "Rev 3", "owner": "STP Training",
        "nrc_classification": "Internal",
        "sections": [
            {"section": "1.0", "heading": "Eligibility",
             "text": "STP will reimburse pre-approved external training up to $5,000/year for active full-time employees with at least 12 months of service."},
        ],
        "keywords": ["training", "reimbursement", "$5,000", "external training"],
    },
    {
        "doc_id": "STP-404", "doc_number": "STP-404", "title": "Site ID Badge Policy",
        "effective_date": "2023-07-01", "revision": "Rev 2", "owner": "STP Security",
        "nrc_classification": "Security-Related",
        "sections": [
            {"section": "1.0", "heading": "Issue & Wear",
             "text": "All personnel inside the protected area shall display a site-issued photo ID badge above the waist at all times. Lost badges must be reported within 30 minutes."},
        ],
        "keywords": ["badge", "id", "photo id", "protected area"],
    },
    {
        "doc_id": "STP-405", "doc_number": "STP-405", "title": "Vendor On-Site Conduct",
        "effective_date": "2024-02-01", "revision": "Rev 1", "owner": "STP Security",
        "nrc_classification": "Security-Related",
        "sections": [
            {"section": "2.0", "heading": "Escort Requirements",
             "text": "All vendors lacking unescorted-access training shall be continuously escorted by an STP employee in the protected area; escort ratios shall not exceed 1:5."},
        ],
        "keywords": ["vendor", "escort", "protected area", "1:5 ratio"],
    },
    {
        "doc_id": "STP-OP-2204", "doc_number": "STP-OP-2204",
        "title": "Reactor Coolant Pump Surveillance & Lockout",
        "effective_date": "2023-11-15", "revision": "Rev 3", "owner": "Operations / RCS",
        "nrc_classification": "Internal",
        "sections": [
            {"section": "5.1", "heading": "Vibration Monitoring",
             "text": "Reactor coolant pump vibration shall be monitored continuously; any single-axis reading exceeding 0.30 in/s peak shall trigger a Tech-Spec entry within 4 hours."},
            {"section": "5.4", "heading": "Lockout / Tagout",
             "text": "Prior to maintenance on any RCP, two-person verification of breaker open and tag-applied shall be documented in the work package per OSHA 1910.147."},
        ],
        "keywords": ["RCP", "reactor coolant pump", "vibration", "0.30", "lockout", "tagout", "LOTO"],
    },
    {
        "doc_id": "STP-TS-3.4.5", "doc_number": "STP-TS-3.4.5",
        "title": "Tech Spec 3.4.5 — ESW Pump Operability",
        "effective_date": "2022-03-01", "revision": "Rev 1", "owner": "Licensing",
        "nrc_classification": "Public",
        "sections": [
            {"section": "3.4.5", "heading": "Limiting Condition for Operation",
             "text": "Two of three Essential Service Water pumps shall be operable in MODES 1, 2, 3, 4. With one pump inoperable, restore within 7 days or be in MODE 3 within the next 6 hours and MODE 5 within the following 36 hours."},
        ],
        "keywords": ["ESW", "essential service water", "operability", "tech spec", "3.4.5", "MODE 3"],
    },
    {
        "doc_id": "0PMP-RCS-7B", "doc_number": "0PMP-RCS-7B",
        "title": "RCP Bearing Inspection & Replacement (PM-7B)",
        "effective_date": "2024-09-01", "revision": "Rev 2", "owner": "Maintenance / Mechanical",
        "nrc_classification": "Internal",
        "sections": [
            {"section": "1.0", "heading": "Scope",
             "text": "This procedure governs scheduled inspection of RCP thrust and journal bearings on Westinghouse Model-93A RCPs at intervals of 730 days."},
            {"section": "4.0", "heading": "Acceptance Criteria",
             "text": "Bearing axial vibration shall be ≤ 0.20 in/s post-maintenance; thrust play shall be 0.020 ± 0.005 in."},
        ],
        "keywords": ["PM-7B", "RCP bearing", "inspection", "Westinghouse", "Model-93A"],
    },
]

# 6 seeded anomalies — match what apex-stp-reliability-agent/agent.py expects.
SEED_ANOMALIES: List[Dict[str, Any]] = [
    {
        "anomaly_id": "ANOM-P3A-2026-04-22", "equipment_id": "P-3A",
        "detected_at": "2026-04-22T03:14:00Z",
        "channel": "vibration_axial_in_per_s", "sensor": "vibration_axial_in_per_s",
        "value": 0.34, "limit": 0.30, "z_score": 3.7,
        "trend": "increasing 12% week-over-week",
        "drift_type": "linear", "magnitude": 0.34 / 0.25,
        "started_at": "2026-04-19T00:00:00Z",
        "expected_failure_mode": "FM-001", "expected_lead_days": 11,
        "scripted_message": (
            "P-3A axial vibration trending 0.34 in/s — 13% above 0.30 in/s Tech-Spec limit "
            "and rising 12% W/W. Pattern matches 3 prior bearing-degradation events on this "
            "same pump (WO-2025-03311, WO-2025-03987, WO-2026-00188). Recommend scheduling "
            "bearing replacement within 21 days to avoid unplanned outage."
        ),
        "recommended_pm": "PM-7B", "current_next_due_offset_days": 22,
        "recommended_new_offset_days": 5,
        "estimated_avoidance_usd": 340000, "estimated_avoidance_hours": 18,
    },
    {
        "anomaly_id": "ANOM-P3B-2026-04-19", "equipment_id": "P-3B",
        "detected_at": "2026-04-19T11:42:00Z",
        "channel": "bearing_oil_temp_f", "sensor": "bearing_oil_temp_f",
        "value": 184, "limit": 180, "z_score": 2.1, "trend": "stable",
        "drift_type": "step", "magnitude": 1.02,
        "started_at": "2026-04-15T00:00:00Z",
        "expected_failure_mode": "FM-014", "expected_lead_days": 30,
        "scripted_message": "P-3B bearing oil temperature 184°F — 4°F above 180°F alarm. Trend stable, monitor.",
        "recommended_pm": "PM-7C", "current_next_due_offset_days": 60,
        "recommended_new_offset_days": 30,
        "estimated_avoidance_usd": 60000, "estimated_avoidance_hours": 4,
    },
    {
        "anomaly_id": "ANOM-EDG2-2026-04-23", "equipment_id": "EDG-2",
        "detected_at": "2026-04-23T08:00:00Z",
        "channel": "bearing_temp_c", "sensor": "bearing_temp_c",
        "value": 91.2, "limit": 85.0, "z_score": 3.4,
        "trend": "rising 1.8°C/day",
        "drift_type": "linear", "magnitude": 91.2 / 72.0,
        "started_at": "2026-04-20T00:00:00Z",
        "expected_failure_mode": "FM-008", "expected_lead_days": 8,
        "scripted_message": (
            "EDG-2 bearing temperature trending 91°C — 6°C above 85°C alarm. Rate-of-rise "
            "1.8°C/day. Recommend cooling-water flow verification (PM-EDG-3A) within 5 days "
            "before next surveillance start."
        ),
        "recommended_pm": "PM-EDG-3A", "current_next_due_offset_days": 14,
        "recommended_new_offset_days": 5,
        "estimated_avoidance_usd": 180000, "estimated_avoidance_hours": 24,
    },
    {
        "anomaly_id": "ANOM-MOV7B-2026-04-26", "equipment_id": "MOV-7B",
        "detected_at": "2026-04-26T16:22:00Z",
        "channel": "motor_current_a", "sensor": "motor_current_a",
        "value": 112.0, "limit": 95.0, "z_score": 4.1,
        "trend": "step change",
        "drift_type": "step", "magnitude": 112.0 / 85.0,
        "started_at": "2026-04-26T00:00:00Z",
        "expected_failure_mode": "FM-003", "expected_lead_days": 7,
        "scripted_message": (
            "MOV-7B motor current step change 85→112 A on 2026-04-26 — 18% above "
            "95 A trip setpoint. Pattern consistent with motor-winding degradation. "
            "Recommend megger test within 72 hours."
        ),
        "recommended_pm": "PM-MOV-2", "current_next_due_offset_days": 90,
        "recommended_new_offset_days": 3,
        "estimated_avoidance_usd": 95000, "estimated_avoidance_hours": 12,
    },
    {
        "anomaly_id": "ANOM-HX22A-2026-04-24", "equipment_id": "HX-22A",
        "detected_at": "2026-04-24T19:08:00Z",
        "channel": "oil_pressure_kpa", "sensor": "oil_pressure_kpa",
        "value": 360.0, "limit": 380.0, "z_score": 2.8,
        "trend": "declining 10 kPa/day",
        "drift_type": "linear", "magnitude": 360.0 / 420.0,
        "started_at": "2026-04-18T00:00:00Z",
        "expected_failure_mode": "FM-002", "expected_lead_days": 6,
        "scripted_message": (
            "HX-22A oil pressure declining 420→360 kPa over 6 days. Pattern matches "
            "seal-leak signature; recommend visual inspection and seal replacement at "
            "next outage window."
        ),
        "recommended_pm": "PM-HX-1", "current_next_due_offset_days": 45,
        "recommended_new_offset_days": 7,
        "estimated_avoidance_usd": 75000, "estimated_avoidance_hours": 8,
    },
    {
        "anomaly_id": "ANOM-P1B-2026-04-28", "equipment_id": "P-1B",
        "detected_at": "2026-04-28T02:15:00Z",
        "channel": "vibration_mm_s", "sensor": "vibration_mm_s",
        "value": 4.2, "limit": 4.0, "z_score": 2.3,
        "trend": "harmonic oscillation ±2 mm/s every ~4 hr",
        "drift_type": "oscillation", "magnitude": 1.05,
        "started_at": "2026-04-25T00:00:00Z",
        "expected_failure_mode": "FM-007", "expected_lead_days": 10,
        "scripted_message": (
            "P-1B exhibiting harmonic vibration oscillation ±2 mm/s on ~4-hr cycle "
            "since 2026-04-25. Possible coupling misalignment or impeller imbalance. "
            "Recommend laser-alignment check within 7 days."
        ),
        "recommended_pm": "PM-1A", "current_next_due_offset_days": 30,
        "recommended_new_offset_days": 7,
        "estimated_avoidance_usd": 45000, "estimated_avoidance_hours": 6,
    },
]


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def gen_units(t: Tunables) -> List[Dict[str, Any]]:
    units = [
        {"unit_id": "U1", "name": "South Texas Project Unit 1",
         "commissioning_date": "1988-08-25", "license_expiry": "2027-08-20",
         "reactor_type": "Westinghouse 4-loop PWR",
         "thermal_mw": 3853, "electrical_mw": 1280},
        {"unit_id": "U2", "name": "South Texas Project Unit 2",
         "commissioning_date": "1989-06-19", "license_expiry": "2028-12-15",
         "reactor_type": "Westinghouse 4-loop PWR",
         "thermal_mw": 3853, "electrical_mw": 1280},
        {"unit_id": "U3", "name": "South Texas Project Unit 3 (planned)",
         "commissioning_date": "2032-01-01", "license_expiry": "2072-01-01",
         "reactor_type": "Westinghouse AP1000",
         "thermal_mw": 3415, "electrical_mw": 1117},
    ]
    return units[: t.num_units]


def gen_systems(t: Tunables, units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    catalog = [
        ("RCS", "Reactor Coolant System", 1),
        ("RHR", "Residual Heat Removal", 2),
        ("ESW", "Essential Service Water", 2),
        ("CCW", "Component Cooling Water", 2),
        ("MFW", "Main Feedwater", 3),
        ("AFW", "Auxiliary Feedwater", 2),
        ("EDG", "Emergency Diesel Generator", 2),
        ("CVCS", "Chemical & Volume Control", 2),
        ("RWST", "Refueling Water Storage", 2),
        ("SI", "Safety Injection", 1),
        ("CTMT", "Containment", 1),
        ("MS", "Main Steam", 2),
        ("CD", "Condensate", 3),
        ("SW", "Service Water", 3),
        ("INST", "Instrument Air", 3),
        ("FP", "Fire Protection", 2),
        ("HVC", "HVAC Containment", 2),
        ("RAD", "Radwaste", 3),
        ("SDC", "Shutdown Cooling", 2),
        ("CHEM", "Chemistry Sampling", 3),
        ("PCC", "Primary Containment Cooling", 2),
        ("EDS", "Electrical Distribution Switchgear", 2),
        ("BAT", "Station Battery", 2),
        ("UPS", "Uninterruptible Power", 2),
        ("FH", "Fuel Handling", 2),
    ]
    out: List[Dict[str, Any]] = []
    for u in units:
        for sid, name, cls in catalog[: max(8, t.num_systems // len(units))]:
            out.append({
                "system_id": sid,
                "unit_id": u["unit_id"],
                "name": name,
                "ANSI_class": cls,
                "description": f"{name} for {u['name']}",
            })
    return out[: t.num_systems]


def gen_equipment(t: Tunables, systems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    eq = [dict(e) for e in HERO_EQUIPMENT]
    rng = random.Random(SEED + 1)
    types = ["pump", "valve", "motor", "hx", "edg", "transformer", "switchgear", "sensor"]
    mfgs = ["Westinghouse", "Flowserve", "GE", "Sulzer", "Caterpillar", "ABB",
            "Siemens", "Crane", "Limitorque", "Foster Wheeler"]
    crit = ["Q", "A", "B", "C"]
    for i in range(len(eq), t.num_equipment):
        sys_row = rng.choice(systems)
        etype = rng.choice(types)
        idx = i + 100
        eq.append({
            "equipment_id": f"{etype.upper()[0]}-{idx}",
            "system_id": sys_row["system_id"],
            "unit_id": sys_row["unit_id"],
            "type": etype,
            "manufacturer": rng.choice(mfgs),
            "model": f"M-{rng.randint(100, 999)}-{etype[:3].upper()}",
            "install_date": _random_date(rng, 1988, 2010).date().isoformat(),
            "criticality": rng.choices(crit, weights=[0.10, 0.25, 0.40, 0.25])[0],
            "train_id": rng.choice(["A", "B", "C", None]),
            "location_room": f"{rng.choice(['AB', 'TB', 'DG-BLDG', 'RB'])}-{rng.randint(1, 99):02d}-{sys_row['system_id']}",
        })
    return eq


def gen_pm_schedule(t: Tunables, equipment: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rng = random.Random(SEED + 2)
    out: List[Dict[str, Any]] = []
    pm_templates = [
        ("PM-7B", "RCP Bearing Inspection", 730, "TS 3.4.5", "0PMP-RCS-7B"),
        ("PM-7A", "RCP Visual Surveillance", 90, "SR 3.4.5.1", "0PMP-RCS-7A"),
        ("PM-7C", "RCP Oil Sample", 180, "SR 3.4.5.2", "0PMP-RCS-7C"),
        ("PM-EDG-3A", "EDG Cooling Water Flow Verification", 365, "SR 3.8.1.10", "0PMP-EDG-3A"),
        ("PM-EDG-2", "EDG Surveillance Run", 30, "SR 3.8.1.2", "0PMP-EDG-2"),
        ("PM-MOV-2", "MOV Stroke-Time Test", 90, "SR 3.7.8.1", "0PMP-MOV-2"),
        ("PM-MOV-3", "MOV Megger Test", 365, "SR 3.7.8.3", "0PMP-MOV-3"),
        ("PM-HX-1", "HX Heat Transfer Test", 365, "SR 3.7.7.1", "0PMP-HX-1"),
        ("PM-HX-2", "HX Tube Cleaning", 730, "ASME OM-3", "0PMP-HX-2"),
        ("PM-1A", "Pump Vibration Baseline", 365, "ASME OM-6", "0PMP-1A"),
    ]
    for eq in equipment[: t.num_pm_schedules]:
        tpl = rng.choice(pm_templates)
        last_completed = _random_date(rng, 2025, 2026)
        next_due = last_completed + timedelta(days=tpl[2])
        out.append({
            "equipment_id": eq["equipment_id"],
            "pm_template_id": tpl[0],
            "pm_template_name": tpl[1],
            "frequency_days": tpl[2],
            "last_completed": last_completed.date().isoformat(),
            "next_due": next_due.date().isoformat(),
            "regulatory_basis": tpl[3],
            "procedure_doc": tpl[4],
        })
    return out


def gen_personnel(t: Tunables) -> List[Dict[str, Any]]:
    out = [dict(p) for p in HERO_PERSONNEL]
    rng = random.Random(SEED + 3)
    first = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
             "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
             "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher",
             "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Helen",
             "Donald", "Sandra", "Mark", "Donna", "Paul", "Carol", "Steven", "Ruth",
             "Andrew", "Sharon", "Kenneth", "Michelle", "George", "Laura", "Joshua",
             "Sarah", "Kevin", "Kimberly", "Brian", "Deborah", "Edward", "Dorothy"]
    last = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts"]
    roles = ["NSO", "mech_tech", "IC_tech", "system_engineer", "RP",
             "supervisor", "planner"]
    role_weights = [0.10, 0.30, 0.15, 0.20, 0.05, 0.10, 0.10]
    for i in range(len(out), t.num_personnel):
        hire = _random_date(rng, 1990, 2022)
        retire = hire + timedelta(days=365 * 30)
        # Ensure ~32 are retirement-eligible within next 24 months
        if i < 32:
            hire = _NOW.replace(tzinfo=None) - timedelta(days=365 * 30 - rng.randint(0, 730))
            retire = hire + timedelta(days=365 * 30)
        out.append({
            "employee_id": f"EMP-{2000 + i:04d}",
            "name": f"{rng.choice(first)} {rng.choice(last)}",
            "role": rng.choices(roles, weights=role_weights)[0],
            "hire_date": hire.date().isoformat(),
            "retirement_eligible_date": retire.date().isoformat(),
            "certifications": rng.sample(
                ["Senior Reactor Operator", "Reactor Operator", "Mechanical Maintenance II",
                 "I&C Technician III", "Welder Class II", "Confined-Space Entry",
                 "ASME Section XI Inspector", "EDG Specialist", "ASME Section III"],
                k=rng.randint(1, 3),
            ),
        })
    return out


def gen_work_orders(
    t: Tunables, equipment: List[Dict[str, Any]], personnel: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    rng = random.Random(SEED + 4)
    rcodes = ["bearing_wear", "seal_leak", "seismic", "thermal_cycling",
              "vendor_quality", "operator_error", "design_deficiency", "age_wear"]
    types = ["corrective", "preventive", "surveillance", "modification"]
    type_weights = [0.40, 0.35, 0.20, 0.05]
    statuses = ["closed", "closed", "closed", "closed", "in_progress", "open", "cancelled"]
    techs_pool = [p["employee_id"] for p in personnel if p["role"] in
                  ("mech_tech", "IC_tech", "supervisor")]

    out: List[Dict[str, Any]] = []
    # ─── Hand-tuned hero work orders cited in the demo ──────────────────────
    hero = [
        ("WO-2025-03311", "P-3A", "corrective", "bearing_wear", "2025-08-12T08:00:00Z",
         "2025-08-15T17:00:00Z", ["EMP-2117", "EMP-2243"], "EMP-1042",
         "Replaced inboard journal bearing on P-3A; vibration returned to 0.18 in/s post-maintenance."),
        ("WO-2025-03987", "P-3A", "corrective", "bearing_wear", "2025-12-04T09:30:00Z",
         "2025-12-06T16:00:00Z", ["EMP-2117"], "EMP-1042",
         "Investigated rising P-3A vibration; replaced thrust bearing per 0PMP-RCS-7B; root cause: lube oil contamination."),
        ("WO-2026-00188", "P-3A", "corrective", "bearing_wear", "2026-01-22T07:00:00Z",
         "2026-01-24T18:00:00Z", ["EMP-2117", "EMP-2243"], "EMP-1042",
         "Bearing replacement following 2025-12 event; oil chemistry corrective action implemented."),
        ("WO-2026-00871", "P-3A", "preventive", None, "2026-03-18T08:00:00Z",
         "2026-03-18T14:30:00Z", ["EMP-2117", "EMP-2243"], "EMP-1042",
         "Scheduled PM-7B bearing inspection per 0PMP-RCS-7B; all acceptance criteria met."),
        ("WO-2024-04211", "EDG-2", "preventive", None, "2024-09-05T08:00:00Z",
         "2024-09-05T15:00:00Z", ["EMP-0871"], "EMP-0871",
         "Tony Garcia performed EDG-2 cooling water flow verification per 0PMP-EDG-3A; results within spec."),
    ]
    for (wo_id, eq_id, typ, rcode, opened, closed, techs, lead, narr) in hero:
        out.append({
            "wo_id": wo_id, "equipment_id": eq_id, "status": "closed",
            "type": typ, "opened": opened, "closed": closed,
            "technician_ids": techs, "lead_engineer_id": lead,
            "root_cause_code": rcode,
            "parts_used": [{"part_id": "PRT-RCP-BRG-INB", "qty": 1, "cost": 18500}] if rcode == "bearing_wear" else [],
            "hours_charged": 24.0 if typ == "corrective" else 6.5,
            "narrative": narr,
        })
    # ─── Random fill ────────────────────────────────────────────────────────
    eq_ids = [e["equipment_id"] for e in equipment]
    year_counter: Dict[int, int] = {}
    for _ in range(len(out), t.num_work_orders):
        opened_dt = _random_date(rng, 2021, 2026)
        year = opened_dt.year
        year_counter[year] = year_counter.get(year, 0) + 1
        wo_id = f"WO-{year}-{year_counter[year]:05d}"
        if any(h["wo_id"] == wo_id for h in out[:5]):
            continue
        typ = rng.choices(types, weights=type_weights)[0]
        status = rng.choice(statuses)
        closed_dt = (opened_dt + timedelta(hours=rng.randint(2, 96))) if status == "closed" else None
        out.append({
            "wo_id": wo_id, "equipment_id": rng.choice(eq_ids), "status": status,
            "type": typ,
            "opened": opened_dt.isoformat() + "Z",
            "closed": (closed_dt.isoformat() + "Z") if closed_dt else None,
            "technician_ids": rng.sample(techs_pool, k=min(rng.randint(1, 3), len(techs_pool))),
            "lead_engineer_id": rng.choice([p["employee_id"] for p in personnel if p["role"] == "system_engineer"]),
            "root_cause_code": rng.choice(rcodes) if typ == "corrective" else None,
            "parts_used": [],
            "hours_charged": round(rng.gammavariate(2, 4), 1),
            "narrative": _gen_narrative(rng, typ),
        })
    return out


def _gen_narrative(rng: random.Random, typ: str) -> str:
    fragments = {
        "corrective": [
            "Investigated equipment alarm.",
            "Replaced suspect component.",
            "Verified post-maintenance functional test.",
            "Root cause documented in attached evaluation.",
        ],
        "preventive": [
            "Performed scheduled PM per applicable procedure.",
            "All acceptance criteria met.",
            "No abnormal conditions observed.",
        ],
        "surveillance": [
            "Performed surveillance test per Tech Spec requirements.",
            "Acceptance criteria satisfied; equipment declared operable.",
        ],
        "modification": [
            "Implemented engineering change package.",
            "Field walkdown verified configuration.",
        ],
    }
    bits = fragments.get(typ, fragments["corrective"])
    return " ".join(rng.sample(bits, k=min(2, len(bits))))


def gen_change_history(t: Tunables, work_orders: List[Dict[str, Any]],
                       personnel: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rng = random.Random(SEED + 5)
    fields = ["status", "technician_ids", "narrative", "parts_used", "lead_engineer_id"]
    out: List[Dict[str, Any]] = []
    for _ in range(t.num_change_history):
        wo = rng.choice(work_orders)
        emp = rng.choice(personnel)
        out.append({
            "wo_id": wo["wo_id"],
            "field": rng.choice(fields),
            "old_value": "[redacted]",
            "new_value": "[redacted]",
            "changed_by": emp["employee_id"],
            "timestamp": (datetime.fromisoformat(wo["opened"].replace("Z", "+00:00"))
                          + timedelta(hours=rng.randint(0, 72))).isoformat(),
        })
    return out


def gen_failure_events(t: Tunables, equipment: List[Dict[str, Any]],
                       work_orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rng = random.Random(SEED + 6)
    out: List[Dict[str, Any]] = []
    # Hero events for P-3A — must align with WO-2025-03311 etc.
    out.extend([
        {"event_id": "FE-2025-04", "equipment_id": "P-3A",
         "occurred_at": "2025-08-12T05:42:00Z", "failure_mode": "FM-001",
         "downtime_hours": 12, "cost_usd": 95000,
         "root_cause": "lube oil contamination", "repair_wo_id": "WO-2025-03311"},
        {"event_id": "FE-2025-09", "equipment_id": "P-3A",
         "occurred_at": "2025-12-04T07:15:00Z", "failure_mode": "FM-001",
         "downtime_hours": 18, "cost_usd": 142000,
         "root_cause": "thrust bearing fatigue", "repair_wo_id": "WO-2025-03987"},
        {"event_id": "FE-2026-01", "equipment_id": "P-3A",
         "occurred_at": "2026-01-22T04:00:00Z", "failure_mode": "FM-007",
         "downtime_hours": 14, "cost_usd": 110000,
         "root_cause": "vibration excursion (recurrence)", "repair_wo_id": "WO-2026-00188"},
    ])
    eq_ids = [e["equipment_id"] for e in equipment]
    modes = [m["mode_id"] for m in FAILURE_MODES]
    wo_ids = [w["wo_id"] for w in work_orders]
    for _ in range(len(out), t.num_failure_events):
        out.append({
            "event_id": f"FE-{rng.randint(2021, 2026)}-{rng.randint(1, 99):02d}",
            "equipment_id": rng.choice(eq_ids),
            "occurred_at": _random_date(rng, 2021, 2026).isoformat() + "Z",
            "failure_mode": rng.choice(modes),
            "downtime_hours": rng.randint(2, 72),
            "cost_usd": int(np.random.lognormal(11.5, 0.7)),
            "root_cause": rng.choice(["bearing wear", "seal leak", "operator error",
                                      "vendor quality", "thermal cycling", "design deficiency"]),
            "repair_wo_id": rng.choice(wo_ids),
        })
    return out


def gen_sensor_streams(t: Tunables, equipment: List[Dict[str, Any]]) -> "pd.DataFrame":
    """Time-series for `sensor_assets` items × 4 channels × interval over `sensor_days`."""
    import pandas as pd
    pumps_motors = [e for e in equipment if e["type"] in ("pump", "motor", "edg")]
    selected = pumps_motors[: t.sensor_assets]

    channels = [
        ("vibration_mm_s", 2.5, 0.4),
        ("bearing_temp_c", 72, 3),
        ("motor_current_a", 85, 4),
        ("oil_pressure_kpa", 420, 12),
    ]
    end = _NOW.replace(tzinfo=None)
    start = end - timedelta(days=t.sensor_days)
    minutes = t.sensor_days * 24 * 60
    interval = t.sensor_interval_minutes
    n_points = minutes // interval
    timestamps = [start + timedelta(minutes=i * interval) for i in range(n_points)]

    rows: List[Dict[str, Any]] = []
    for eq in selected:
        for chan, mu, sd in channels:
            base = np.random.normal(mu, sd, size=n_points)
            for ts, val in zip(timestamps, base):
                rows.append({
                    "timestamp": ts, "equipment_id": eq["equipment_id"],
                    "channel": chan, "value": float(round(val, 3)),
                })
    df = pd.DataFrame(rows)

    # Inject the 6 seeded anomalies in the last `lookback_days` portion.
    df = _inject_anomalies(df, end)
    return df


def _inject_anomalies(df: "pd.DataFrame", end: datetime) -> "pd.DataFrame":
    """Apply each SEED_ANOMALIES entry to df in-place. Linear/step/oscillation."""
    for an in SEED_ANOMALIES:
        eq = an["equipment_id"]
        chan = an.get("channel") or an.get("sensor", "")
        # Map UC-4 friendly channel names → df channels
        chan_map = {
            "vibration_axial_in_per_s": "vibration_mm_s",
            "bearing_oil_temp_f": "bearing_temp_c",
            "motor_current_a": "motor_current_a",
            "oil_pressure_kpa": "oil_pressure_kpa",
            "vibration_mm_s": "vibration_mm_s",
            "bearing_temp_c": "bearing_temp_c",
        }
        df_chan = chan_map.get(chan, chan)
        mask = (df["equipment_id"] == eq) & (df["channel"] == df_chan)
        if not mask.any():
            continue
        target_value = an["value"]
        baseline = df.loc[mask, "value"].mean()
        delta = target_value - baseline
        days_back = an["expected_lead_days"]
        window_start = end - timedelta(days=days_back)
        time_mask = mask & (df["timestamp"] >= window_start)
        n = int(time_mask.sum())
        if n == 0:
            continue
        if an["drift_type"] == "linear":
            ramp = np.linspace(0, delta, n)
            df.loc[time_mask, "value"] = df.loc[time_mask, "value"].values + ramp
        elif an["drift_type"] == "step":
            df.loc[time_mask, "value"] = df.loc[time_mask, "value"].values + delta
        elif an["drift_type"] == "oscillation":
            phase = np.linspace(0, n / 48, n) * 2 * np.pi
            df.loc[time_mask, "value"] = df.loc[time_mask, "value"].values + np.sin(phase) * abs(delta)
    return df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_date(rng: random.Random, year_start: int, year_end: int) -> datetime:
    days = (datetime(year_end, 12, 31) - datetime(year_start, 1, 1)).days
    return datetime(year_start, 1, 1) + timedelta(days=rng.randint(0, days),
                                                  hours=rng.randint(0, 23),
                                                  minutes=rng.randint(0, 59))


def _write_json(path: Path, data: Any, force: bool) -> bool:
    """Write JSON if missing or force=True. Returns True if written."""
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2, default=str)
    return True


def _write_parquet(path: Path, df: "pd.DataFrame", force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
    return True


def _step(label: str, n: int, t0: float) -> None:
    elapsed = (datetime.now().timestamp() - t0)
    print(f"  ✓ {label:30s} {n:>8,} rows  ({elapsed:5.2f}s)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate(force: bool, quick: bool) -> Dict[str, Any]:
    t = Tunables().quick() if quick else Tunables()
    print(f"⚛  STP Nuclear synthetic data generator (mode={'quick' if quick else 'full'})")
    print(f"   Output dir: {OUT_DIR}")

    summary: Dict[str, Any] = {}

    # ── Structured corpora ────────────────────────────────────────────────
    t0 = datetime.now().timestamp()
    units = gen_units(t)
    if _write_json(OUT_DIR / "units.json", units, force):
        _step("units.json", len(units), t0)
    summary["units"] = len(units)

    t0 = datetime.now().timestamp()
    systems = gen_systems(t, units)
    if _write_json(OUT_DIR / "systems.json", systems, force):
        _step("systems.json", len(systems), t0)
    summary["systems"] = len(systems)

    t0 = datetime.now().timestamp()
    equipment = gen_equipment(t, systems)
    if _write_json(OUT_DIR / "equipment.json", equipment, force):
        _step("equipment.json", len(equipment), t0)
    summary["equipment"] = len(equipment)

    t0 = datetime.now().timestamp()
    pm = gen_pm_schedule(t, equipment)
    if _write_json(OUT_DIR / "pm_schedule.json", pm, force):
        _step("pm_schedule.json", len(pm), t0)
    summary["pm_schedule"] = len(pm)

    t0 = datetime.now().timestamp()
    personnel = gen_personnel(t)
    if _write_json(OUT_DIR / "personnel.json", personnel, force):
        _step("personnel.json", len(personnel), t0)
    summary["personnel"] = len(personnel)

    t0 = datetime.now().timestamp()
    work_orders = gen_work_orders(t, equipment, personnel)
    if _write_json(OUT_DIR / "work_orders.json", work_orders, force):
        _step("work_orders.json", len(work_orders), t0)
    summary["work_orders"] = len(work_orders)

    t0 = datetime.now().timestamp()
    change_history = gen_change_history(t, work_orders, personnel)
    if _write_json(OUT_DIR / "change_history.json", change_history, force):
        _step("change_history.json", len(change_history), t0)
    summary["change_history"] = len(change_history)

    t0 = datetime.now().timestamp()
    failure_events = gen_failure_events(t, equipment, work_orders)
    if _write_json(OUT_DIR / "failure_events.json", failure_events, force):
        _step("failure_events.json", len(failure_events), t0)
    summary["failure_events"] = len(failure_events)

    t0 = datetime.now().timestamp()
    if _write_json(OUT_DIR / "failure_mode_catalog.json", FAILURE_MODES, force):
        _step("failure_mode_catalog.json", len(FAILURE_MODES), t0)
    summary["failure_mode_catalog"] = len(FAILURE_MODES)

    t0 = datetime.now().timestamp()
    if _write_json(OUT_DIR / "seed_anomalies.json", SEED_ANOMALIES, force):
        _step("seed_anomalies.json", len(SEED_ANOMALIES), t0)
    summary["seed_anomalies"] = len(SEED_ANOMALIES)

    t0 = datetime.now().timestamp()
    if _write_json(OUT_DIR / "policies_corpus.json", POLICY_CORPUS, force):
        _step("policies_corpus.json", len(POLICY_CORPUS), t0)
    summary["policies_corpus"] = len(POLICY_CORPUS)

    # ── Sensor time-series (heaviest artifact) ────────────────────────────
    t0 = datetime.now().timestamp()
    try:
        import pandas as pd  # noqa: F401  (only needed when writing parquet)
        df = gen_sensor_streams(t, equipment)
        if _write_parquet(OUT_DIR / "sensor_streams.parquet", df, force):
            _step("sensor_streams.parquet", len(df), t0)
        summary["sensor_streams"] = len(df)
    except ImportError:
        print("  ⚠  pandas/pyarrow missing — skipping sensor_streams.parquet")
        summary["sensor_streams"] = 0

    return summary


def validate() -> int:
    """Re-read every output file and assert basic shape. Returns exit code."""
    print("⚛  Validating synthetic data …")
    errors: List[str] = []

    def check(path: Path, kind: str = "json") -> Optional[Any]:
        if not path.exists():
            errors.append(f"missing: {path.name}")
            return None
        try:
            if kind == "json":
                with path.open() as fp:
                    return json.load(fp)
            return True
        except Exception as e:
            errors.append(f"unreadable {path.name}: {e}")
            return None

    expected = {
        "units.json": (1, 5),
        "systems.json": (5, 100),
        "equipment.json": (6, 1000),
        "pm_schedule.json": (5, 1000),
        "personnel.json": (4, 500),
        "work_orders.json": (5, 6000),
        "change_history.json": (50, 1500),
        "failure_events.json": (3, 100),
        "failure_mode_catalog.json": (15, 30),
        "seed_anomalies.json": (6, 6),
        "policies_corpus.json": (5, 50),
    }
    for name, (lo, hi) in expected.items():
        data = check(OUT_DIR / name)
        if data is not None and not (lo <= len(data) <= hi):
            errors.append(f"{name}: row count {len(data)} outside [{lo}, {hi}]")

    # FK integrity: every wo.equipment_id exists in equipment.json
    eq_data = check(OUT_DIR / "equipment.json")
    wo_data = check(OUT_DIR / "work_orders.json")
    if eq_data and wo_data:
        eq_ids = {e["equipment_id"] for e in eq_data}
        for wo in wo_data:
            if wo["equipment_id"] not in eq_ids:
                errors.append(f"FK-violation: WO {wo['wo_id']} → unknown equipment {wo['equipment_id']}")
                break

    # Hero anomalies present
    seeds = check(OUT_DIR / "seed_anomalies.json")
    if seeds:
        ids = {s["anomaly_id"] for s in seeds}
        required = {"ANOM-P3A-2026-04-22", "ANOM-EDG2-2026-04-23"}
        missing = required - ids
        if missing:
            errors.append(f"hero anomalies missing: {missing}")

    if errors:
        print("✗ FAIL")
        for e in errors:
            print(f"   • {e}")
        return 1
    print("✓ all validations passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="STP synthetic data generator")
    ap.add_argument("--force", action="store_true", help="regenerate even if output exists")
    ap.add_argument("--quick", action="store_true", help="smaller corpus (fast, for CI)")
    ap.add_argument("--validate", action="store_true", help="re-read every file and assert shape")
    args = ap.parse_args()

    if args.validate:
        return validate()

    summary = generate(force=args.force, quick=args.quick)
    print("\n📊 Summary:")
    for k, v in summary.items():
        print(f"   {k:30s} {v:>10,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
