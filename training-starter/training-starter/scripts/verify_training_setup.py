#!/usr/bin/env python3
"""
APEX Developer Training — self-checking verification harness.

Runs every sample fixture through the action handlers built in the two use cases
and asserts the result matches the `_training.expected_*` block in each fixture.

This is the graded exercise. A developer has completed the course when this
script prints ALL CHECKS PASSED against handlers they wrote themselves.

USAGE
    # Verify against the reference handlers shipped with the course
    python3 training/scripts/verify_training_setup.py

    # Verify against YOUR handlers once you have copied them into place
    python3 training/scripts/verify_training_setup.py --from-actions-dir

    # Verify one use case
    python3 training/scripts/verify_training_setup.py --use-case uc1

    # Show the full handler output for each fixture
    python3 training/scripts/verify_training_setup.py --verbose

EXIT CODES
    0  all checks passed
    1  one or more checks failed
    2  setup problem (handler missing, fixture unreadable)
"""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Resolve relative to THIS script, not to a hardcoded folder name, so the same
# harness works from `training/` (reference) and `training-starter/` (what the
# developers receive). Hardcoding "training" made the starter copy load the
# reference handlers and pass without a line of work being done.
PKG = Path(__file__).resolve().parents[1]           # the package root
UC1 = PKG / "uc1-invoice-exception"
UC2 = PKG / "uc2-property-submission"


def _find_repo_root(start: Path) -> Path:
    """Walk up until we find the tree containing actions/sdk."""
    for candidate in [start, *start.parents]:
        if (candidate / "actions" / "sdk").is_dir():
            return candidate
    raise SystemExit(
        "Could not locate the APEX repo root (a directory containing actions/sdk).\n"
        "  Run this from inside the apex-ai-platform/aws tree."
    )


REPO = _find_repo_root(PKG)

# The SDK lives under actions/, and every handler does `from sdk import ...`.
sys.path.insert(0, str(REPO / "actions"))

GREEN, RED, YELLOW, DIM, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = DIM = RESET = ""


# ============================================================================
# Handler loading
# ============================================================================

def load_handler(name: str, use_case_dir: Path, industry: str, from_actions: bool):
    """
    Load a handler module either from the training folder (reference
    implementation) or from actions/<industry>/<name>/handler.py (the
    developer's own copy, once deployed).
    """
    if from_actions:
        path = REPO / "actions" / industry / name / "handler.py"
    else:
        path = use_case_dir / "actions" / name / "handler.py"

    if not path.exists():
        raise FileNotFoundError(
            f"{path}\n"
            f"  If you used --from-actions-dir, copy your handler there first:\n"
            f"    cp -r {use_case_dir / 'actions' / name} {REPO / 'actions' / industry}/"
        )

    spec = importlib.util.spec_from_file_location(f"apex_{industry}_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ============================================================================
# Seed data — mirrors training/scripts/seed_training_data.py so the harness
# runs with no AWS dependency.
# ============================================================================

PO_LINES = {
    # inv_01 clean / inv_05 duplicate — prices equal the invoice, so zero variance.
    "PO-5000": [
        {"line_number": 1, "sku": "ACM-TAPE-24",     "description": "Packing tape, 24-roll case", "quantity": 100, "unit_price": 42.50, "amount": 4250.00},
        {"line_number": 2, "sku": "ACM-STRAP-12",    "description": "Poly strapping, 12mm coil",  "quantity": 50,  "unit_price": 15.00, "amount": 750.00},
        {"line_number": 3, "sku": "ACM-BUBBLE-WRAP", "description": "Bubble wrap, 50m roll",      "quantity": 40,  "unit_price": 24.00, "amount": 960.00},
    ],
    # inv_02 — invoice bills 515.00 against 500.00 = 3.0%, inside the band.
    "PO-6112": [
        {"line_number": 1, "sku": "INI-SW24",     "description": "24-port managed switch", "quantity": 8, "unit_price": 500.00, "amount": 4000.00},
        {"line_number": 2, "sku": "INI-CBL-CAT6", "description": "Cat6 patch cable, 3m",   "quantity": 8, "unit_price": 45.00,  "amount": 360.00},
    ],
    # inv_03 — invoice bills 201.60 against 180.00 = 12.0%, breaching the band.
    "PO-7231": [
        {"line_number": 1, "sku": "HLI-MON27",       "description": "27in monitor",    "quantity": 10, "unit_price": 180.00, "amount": 1800.00},
        {"line_number": 2, "sku": "HLI-DOC-STATION", "description": "Docking station", "quantity": 10, "unit_price": 89.00,  "amount": 890.00},
    ],
    # inv_04 — quantity fixture.
    "PO-8340": [
        {"line_number": 1, "sku": "UMB-CLN-5G",      "description": "Industrial cleaner, 5 gal", "quantity": 100, "unit_price": 38.75, "amount": 3875.00},
        {"line_number": 2, "sku": "UMB-DEGREASE-CS", "description": "Degreaser, case of 12",     "quantity": 15,  "unit_price": 32.00, "amount": 480.00},
    ],
    # inv_06 — everything matches; only the remit-to party is wrong.
    "PO-6650": [
        {"line_number": 1, "sku": "GLX-PSU-24V",  "description": "24V power supply unit", "quantity": 25, "unit_price": 68.00,  "amount": 1700.00},
        {"line_number": 2, "sku": "GLX-CTRL-PLC", "description": "PLC controller module", "quantity": 5,  "unit_price": 312.00, "amount": 1560.00},
    ],
}

RECEIPT_LINES = {
    "PO-5000": [{"line_number": 1, "sku": "ACM-TAPE-24",  "quantity": 20},
                {"line_number": 2, "sku": "ACM-STRAP-12", "quantity": 10}],
    "PO-6112": [{"line_number": 1, "sku": "INI-SW24",     "quantity": 8},
                {"line_number": 2, "sku": "INI-CBL-CAT6", "quantity": 8}],
    "PO-7231": [{"line_number": 1, "sku": "HLI-MON27",       "quantity": 10},
                {"line_number": 2, "sku": "HLI-DOC-STATION", "quantity": 10}],
    # Only 100 received against the 120 billed — the QTY_VAR fixture.
    "PO-8340": [{"line_number": 1, "sku": "UMB-CLN-5G",      "quantity": 100},
                {"line_number": 2, "sku": "UMB-DEGREASE-CS", "quantity": 15}],
    "PO-6650": [{"line_number": 1, "sku": "GLX-PSU-24V",  "quantity": 25},
                {"line_number": 2, "sku": "GLX-CTRL-PLC", "quantity": 5}],
}

PAYMENT_HISTORY = [
    # The duplicate of inv_05, stored under a different invoice-number format.
    {"payment_id": "PMT-9001", "invoice_number": "inv 1042", "vendor_id": "VEN-001",
     "vendor_name": "ACME CORPORATION", "total_amount": 4850.00,
     "invoice_date": "2026-02-15", "paid_date": "2026-02-22", "po_number": "PO-5000"},
    # Near-miss controls — these must NOT trip the detector.
    {"payment_id": "PMT-9002", "invoice_number": "INV-001043", "vendor_id": "VEN-001",
     "vendor_name": "Acme Corp", "total_amount": 4850.00,
     "invoice_date": "2026-02-16", "paid_date": "2026-02-23", "po_number": "PO-5001"},
    {"payment_id": "PMT-9003", "invoice_number": "INV-001042", "vendor_id": "VEN-005",
     "vendor_name": "Umbrella Corporation", "total_amount": 4850.00,
     "invoice_date": "2025-07-18", "paid_date": "2025-07-25", "po_number": "PO-9999"},
    {"payment_id": "PMT-9005", "invoice_number": "GLX-77020", "vendor_id": "VEN-002",
     "vendor_name": "Globex Corp", "total_amount": 2500.00,
     "invoice_date": "2026-03-30", "paid_date": "2026-04-06", "po_number": "PO-6640"},
]

VENDOR_MASTER = {
    "acme corp":            {"vendor_id": "VEN-001", "remit_to_name": "Acme Corp"},
    "globex corp":          {"vendor_id": "VEN-002", "remit_to_name": "Globex Corp"},
    "initech llc":          {"vendor_id": "VEN-003", "remit_to_name": "Initech LLC"},
    "hooli inc.":           {"vendor_id": "VEN-004", "remit_to_name": "Hooli Inc."},
    "umbrella corporation": {"vendor_id": "VEN-005", "remit_to_name": "Umbrella Corporation"},
}

OPEN_SUBMISSIONS = [
    {"submission_id": "SUB-2026-0417", "named_insured": "Cedar Ridge Logistics LLC",
     "fein": "47-3319008", "broker_agency_name": "Harborline Risk Advisors",
     "received_date": "2026-05-02", "status": "open",
     "first_location_address": "1420 N Industrial Blvd", "first_location_postal_code": "76106"},
]

POLICY_REGISTER = [
    {"policy_number": "CP-2024-118840", "named_insured": "Ironwood Millworks Inc",
     "fein": "74-2298031", "broker_agency_name": "Harborline Risk Advisors",
     "effective_date": "2025-07-18", "first_location_address": "9 Tannery Row",
     "first_location_postal_code": "03060"},
]


# ============================================================================
# Result reporting
# ============================================================================

class Results:
    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[tuple] = []
        self.skipped: List[tuple] = []

    def check(self, fixture: str, label: str, actual: Any, expected: Any) -> bool:
        if _equivalent(actual, expected):
            self.passed.append(f"{fixture} :: {label}")
            print(f"    {GREEN}PASS{RESET}  {label:<26} {_fmt(actual)}")
            return True
        self.failed.append((fixture, label, actual, expected))
        print(f"    {RED}FAIL{RESET}  {label:<26} got {_fmt(actual)}, expected {_fmt(expected)}")
        return False

    def skip(self, fixture: str, reason: str):
        self.skipped.append((fixture, reason))
        print(f"    {YELLOW}SKIP{RESET}  {reason}")


def _equivalent(actual: Any, expected: Any) -> bool:
    if isinstance(expected, (list, set)) and isinstance(actual, (list, set)):
        return sorted(str(x) for x in actual) == sorted(str(x) for x in expected)
    if expected is None:
        return actual in (None, "", [], 0)
    return str(actual).lower() == str(expected).lower()


def _fmt(value: Any) -> str:
    if isinstance(value, (list, set)):
        return "[" + ", ".join(str(v) for v in value) + "]"
    return str(value)


# ============================================================================
# Use case 1 — AP invoice exception triage
# ============================================================================

def run_uc1(from_actions: bool, verbose: bool, results: Results) -> None:
    print(f"\n{'=' * 78}")
    print("USE CASE 1 — Financial Services: AP Invoice Exception Triage")
    print("=" * 78)

    twm = load_handler("three_way_match", UC1, "financial_services", from_actions)
    dfp = load_handler("duplicate_fingerprint", UC1, "financial_services", from_actions)
    tol = load_handler("tolerance_policy", UC1, "financial_services", from_actions)

    fixtures = sorted((UC1 / "sample-files").glob("*.expected.json"))
    if not fixtures:
        results.skip("uc1", "no fixtures found in sample-files/")
        return

    for path in fixtures:
        doc = json.loads(path.read_text())
        meta = doc.get("_training", {})
        name = path.name.replace(".expected.json", "")
        print(f"\n  {DIM}{name}{RESET} — {meta.get('scenario_name', '')}")

        po_number = doc.get("po_number")
        vendor_name = doc.get("vendor_name", "")
        total = float(doc.get("total_amount") or 0)

        # --- Step 1: duplicate fingerprint (hard stop) --------------------
        dup = dfp.duplicate_fingerprint(
            invoice_number=doc.get("invoice_number", ""),
            vendor_name=vendor_name,
            total_amount=total,
            invoice_date=doc.get("invoice_date"),
            po_number=po_number,
            payment_history=PAYMENT_HISTORY,
        )

        # --- Step 2: vendor / remit-to check ------------------------------
        vendor_row = VENDOR_MASTER.get(vendor_name.strip().lower())
        vendor_found = vendor_row is not None
        remit_on_doc = (doc.get("remit_to_name") or "").strip().lower()
        remit_of_record = (vendor_row or {}).get("remit_to_name", "").strip().lower()
        remit_drift = bool(remit_on_doc and remit_of_record and remit_on_doc != remit_of_record)

        # --- Step 3: three-way match --------------------------------------
        variances: List[Dict[str, Any]] = []
        if po_number in PO_LINES:
            match = twm.three_way_match(
                invoice_number=doc.get("invoice_number", ""),
                po_number=po_number,
                invoice_lines=doc.get("line_items", []),
                po_lines=PO_LINES[po_number],
                receipt_lines=RECEIPT_LINES.get(po_number, []),
                invoice_freight=float(doc.get("freight_amount") or 0),
                invoice_tax=float(doc.get("tax_amount") or 0),
            )
            variances = match["variances"]
            if verbose:
                print(f"      {DIM}match: {len(variances)} variance(s), "
                      f"worst={match['worst_severity']}, "
                      f"impact=${match['total_variance_amount']:,.2f}{RESET}")

        # --- Step 4: tolerance policy -------------------------------------
        decision = tol.tolerance_policy(
            invoice_number=doc.get("invoice_number", ""),
            invoice_total=total,
            variances=variances,
            extraction_confidence=0.95,
            duplicate_probability=dup["duplicate_probability"],
            remit_drift_detected=remit_drift,
            vendor_found=vendor_found,
        )

        if verbose:
            print(f"      {DIM}policy: {json.dumps({k: decision[k] for k in ('disposition','policy_rule_applied','assignee_role','sla_hours')})}{RESET}")

        # --- Assertions ----------------------------------------------------
        results.check(name, "disposition",
                      decision["disposition"], meta.get("expected_disposition"))
        results.check(name, "assignee_role",
                      decision["assignee_role"], meta.get("expected_assignee_role"))

        expected_codes = meta.get("expected_exception_codes") or []
        if expected_codes:
            observed = {v.get("exception_code") for v in variances}
            if decision.get("primary_exception_code"):
                observed.add(decision["primary_exception_code"])
            missing = [c for c in expected_codes if c not in observed]
            results.check(name, "exception_codes",
                          "all present" if not missing else f"missing {missing}",
                          "all present")

        if meta.get("teaching_point"):
            print(f"    {DIM}↳ {meta['teaching_point'][:96]}{RESET}")


# ============================================================================
# Use case 2 — CP submission clearance
# ============================================================================

def run_uc2(from_actions: bool, verbose: bool, results: Results) -> None:
    print(f"\n{'=' * 78}")
    print("USE CASE 2 — Insurance Underwriting: CP Submission Clearance")
    print("=" * 78)

    clr = load_handler("submission_clear", UC2, "insurance_underwriting", from_actions)
    apt = load_handler("appetite_score", UC2, "insurance_underwriting", from_actions)
    cat = load_handler("cat_exposure_aggregate", UC2, "insurance_underwriting", from_actions)

    fixtures = sorted((UC2 / "sample-files").glob("*.expected.json"))
    if not fixtures:
        results.skip("uc2", "no fixtures found in sample-files/ — "
                            "generate them before running this use case")
        return

    for path in fixtures:
        doc = json.loads(path.read_text())
        meta = doc.get("_training", {})
        name = path.name.replace(".expected.json", "")
        print(f"\n  {DIM}{name}{RESET} — {meta.get('scenario_name', '')}")

        locations = doc.get("locations", [])
        first = locations[0] if locations else {}

        # --- Step 1: clearance ---------------------------------------------
        clearance = clr.submission_clear(
            submission_id=doc.get("submission_id", name),
            named_insured=doc.get("named_insured", ""),
            fein=doc.get("fein"),
            additional_named_insureds=doc.get("additional_named_insureds", []),
            dba_names=doc.get("dba_names", []),
            first_location_address=first.get("street_address"),
            first_location_postal_code=first.get("postal_code"),
            broker_agency_name=doc.get("broker_agency_name"),
            policy_register=POLICY_REGISTER,
            open_submissions=OPEN_SUBMISSIONS,
        )

        # --- Step 2: appetite ----------------------------------------------
        appetite = apt.appetite_score(
            submission_id=doc.get("submission_id", name),
            locations=locations,
            primary_occupancy=doc.get("primary_occupancy"),
            prior_losses=doc.get("prior_losses", []),
            loss_run_years_provided=doc.get("loss_run_years_provided"),
            expiring_premium=doc.get("expiring_premium"),
            years_in_business=doc.get("years_in_business"),
            has_prior_declination=bool(doc.get("has_prior_declination")),
        )

        # --- Step 3: catastrophe aggregation --------------------------------
        catagg = cat.cat_exposure_aggregate(
            submission_id=doc.get("submission_id", name),
            locations=locations,
        )

        if verbose:
            print(f"      {DIM}clearance={clearance['clearance_status']} "
                  f"appetite={appetite['appetite_band']}/{appetite['appetite_score']} "
                  f"cat_breaches={catagg['breach_count']}{RESET}")

        # --- Derive the overall disposition, mirroring the recipe -----------
        if doc.get("submission_completeness") in ("missing_sov", "missing_both"):
            disposition = "refer_to_broker"
        elif float(doc.get("loss_run_years_provided") or 0) < 3:
            disposition = "refer_to_broker"
        elif clearance["blocking_conflict"]:
            disposition = {"renewal": "route_renewal",
                           "broker_conflict": "route_bor",
                           "same_broker_resubmission": "merge"}[clearance["clearance_status"]]
        elif appetite["disqualifiers"]:
            disposition = "decline"
        elif catagg["recommendation"] == "decline":
            disposition = "decline"
        elif catagg["recommendation"] == "refer_facultative":
            disposition = "refer_facultative"
        else:
            disposition = "route_to_underwriter"

        results.check(name, "disposition", disposition, meta.get("expected_disposition"))

        if meta.get("expected_clearance_status"):
            results.check(name, "clearance_status",
                          clearance["clearance_status"], meta["expected_clearance_status"])

        if meta.get("expected_appetite_band"):
            results.check(name, "appetite_band",
                          appetite["appetite_band"], meta["expected_appetite_band"])

        expected_tiv = doc.get("schedule_total_insured_value")
        if expected_tiv:
            drift = abs(appetite["total_insured_value"] - float(expected_tiv))
            results.check(name, "tiv_reconciles",
                          "yes" if drift < 1.0 else f"off by ${drift:,.2f}", "yes")

        if meta.get("teaching_point"):
            print(f"    {DIM}↳ {meta['teaching_point'][:96]}{RESET}")


# ============================================================================
# Entry point
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the APEX training build.")
    parser.add_argument("--use-case", default="all", choices=["all", "uc1", "uc2"])
    parser.add_argument("--from-actions-dir", action="store_true",
                        help="Load handlers from actions/<industry>/ instead of the "
                             "training reference copies")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    source = "actions/<industry>/" if args.from_actions_dir else "training reference copies"
    print(f"APEX training verification — handlers loaded from: {source}")

    results = Results()
    for label, runner in (("uc1", run_uc1), ("uc2", run_uc2)):
        if args.use_case not in ("all", label):
            continue
        try:
            runner(args.from_actions_dir, args.verbose, results)
        except FileNotFoundError as exc:
            print(f"\n{RED}SETUP ERROR{RESET}: handler not found\n  {exc}")
            return 2
        except NotImplementedError as exc:
            # Expected in the starter package — a body has not been written yet.
            # Report it as work outstanding, not as a crash.
            print(f"\n  {YELLOW}NOT IMPLEMENTED{RESET}  {exc}")
            print(f"  {DIM}Write the body, then run this again.{RESET}")
            results.failed.append((label, "implementation", "NotImplementedError", "a return value"))

    print(f"\n{'=' * 78}")
    total = len(results.passed) + len(results.failed)
    if results.failed:
        print(f"{RED}{len(results.failed)} of {total} checks FAILED{RESET}")
        for fixture, label, actual, expected in results.failed:
            print(f"  {fixture} :: {label} — got {_fmt(actual)}, expected {_fmt(expected)}")
        return 1

    print(f"{GREEN}ALL CHECKS PASSED{RESET} — {len(results.passed)} of {total}")
    if results.skipped:
        for fixture, reason in results.skipped:
            print(f"{YELLOW}  skipped: {fixture} — {reason}{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
