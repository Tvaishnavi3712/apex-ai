"""
Apex Action Test Script Generator
=================================

Produces `Apex_Action_Test_Script.docx` in this folder — a complete manual
test plan covering every action currently registered in the Apex backend.

How it discovers actions:
  • Imports `services.action_registry.get_registry()` (same path the backend
    uses) and reads `.get_all_actions()`.
  • Schemas come from the registry's on-disk extractor, so `input_schema` /
    `output_schema` reflect what the handler file actually declares via
    `@apex_action(ApexActionSchema(...))` or its docstring.

When to re-run:
  • Any time a new action handler is added under `actions/<industry>/` and
    registered in `services/action_registry.INDUSTRY_ACTIONS`.
  • Any time an existing handler's `ApexActionSchema` changes.
  • Any time `backend/services/aws_provisioner.py` gets new sample data
    that should show up under "Sample Test Values".

Usage:
    cd aws/backend && source venv/bin/activate
    python ../test-scripts/generate_test_script.py

The script writes to `aws/test-scripts/Apex_Action_Test_Script.docx` and
prints a short summary.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure the backend package is importable no matter where this is run from.
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from services.action_registry import get_registry, reload_registry  # noqa: E402

from docx import Document  # noqa: E402
from docx.shared import Inches, Pt, RGBColor  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.enum.table import WD_ALIGN_VERTICAL  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402


OUTPUT_PATH = _SCRIPT_DIR / "Apex_Action_Test_Script.docx"

# ─────────────────── Known sample inputs / expectations ───────────────────
#
# Keyed by action_id. Each entry describes one "happy path" scenario that
# a tester can drop into the Test Runner. The provisioner (see
# backend/services/aws_provisioner.py) seeds DynamoDB with these exact
# values, so if the reader uses them they should see real successful output.
#
# Add new entries here whenever the provisioner gets new fixture data.

SCENARIO: Dict[str, List[Dict[str, Any]]] = {
    "financial_services.po_match": [
        {
            "name": "Exact-amount match",
            "input": {"po_number": "PO-123", "invoice_amount": 500},
            "expect": "matched=true, match_status=EXACT_MATCH, po_amount=500",
        },
        {
            "name": "Within 5% tolerance",
            "input": {"po_number": "PO-123", "invoice_amount": 525},
            "expect": "matched=true, match_status=WITHIN_TOLERANCE",
        },
        {
            "name": "Over tolerance",
            "input": {"po_number": "PO-123", "invoice_amount": 600},
            "expect": "matched=false, match_status=OVER_TOLERANCE, variance_percent=20.0",
        },
        {
            "name": "PO not in system",
            "input": {"po_number": "PO-DOES-NOT-EXIST", "invoice_amount": 100},
            "expect": "matched=false, match_status=NOT_FOUND",
        },
    ],
    "financial_services.vendor_lookup": [
        {
            "name": "Approved vendor by name",
            "input": {"vendor_name": "Acme Corp"},
            "expect": "found=true, vendor_id=VEN-001, status=active",
        },
        {
            "name": "Unknown vendor",
            "input": {"vendor_name": "Nonexistent Ltd"},
            "expect": "found=false",
        },
    ],
    "healthcare_payers.eligibility_verify": [
        {
            "name": "Active member",
            "input": {"member_id": "MEM-1001", "npi": "1234567890"},
            "expect": "eligible=true, plan=PPO-GOLD",
        },
    ],
    "healthcare_payers.claims_adjudication": [
        {
            "name": "Standard claim",
            "input": {
                "claim_id": "CLM-001",
                "member_id": "MEM-1001",
                "provider_npi": "1234567890",
                "service_date": "2026-03-15",
                "procedure_codes": ["99213"],
                "diagnosis_codes": ["E11.9"],
                "billed_amount": 1200,
            },
            "expect": "claim adjudication envelope; allowed_amount + status",
        },
    ],
    "healthcare_providers.patient_lookup": [
        {
            "name": "Seeded patient",
            "input": {"patient_id": "PAT-1001"},
            "expect": "name=Jane Doe, active=true",
        },
    ],
    "healthcare_providers.referral_validate": [
        {
            "name": "Approved referral",
            "input": {"patient_id": "PAT-1001", "referral_number": "REF-001"},
            "expect": "status=approved, specialty=Cardiology",
        },
    ],
    "retail.receipt_validate": [
        {
            "name": "Valid transaction",
            "input": {"transaction_id": "TXN-001"},
            "expect": "valid=true, amount=125.00",
        },
    ],
    "retail.refund_process": [
        {
            "name": "Approved refund",
            "input": {"transaction_id": "TXN-001", "amount": 25},
            "expect": "status=approved",
        },
    ],
    "manufacturing.carrier_validation": [
        {
            "name": "Approved carrier",
            "input": {"carrier_scac": "UPSN"},
            "expect": "valid=true, on_time_pct present",
        },
    ],
    "manufacturing.inventory_lookup": [
        {
            "name": "Seeded SKU",
            "input": {"sku": "SKU-MFG-1"},
            "expect": "on_hand=1000",
        },
    ],
    "hr.job_requirement_match": [
        {
            "name": "Open requisition",
            "input": {"job_id": "REQ-001"},
            "expect": "level=L5, open=true",
        },
    ],
    "hr.compensation_validation": [
        {
            "name": "In-band offer",
            "input": {"job_id": "REQ-001", "proposed_salary": 170000},
            "expect": "in_band=true",
        },
    ],
}

# Industry display order (nice groupings first, then anything else).
INDUSTRY_ORDER = [
    "financial_services",
    "healthcare_payers",
    "healthcare_providers",
    "healthcare_clinical",
    "insurance_underwriting",
    "retail",
    "cpg",
    "manufacturing",
    "hr",
    "contact_center",
    "airlines",
    "supply_chain",
    "aerospace_defense",
    "core",
    "integrations",
]

INDUSTRY_LABEL = {
    "financial_services":     "Financial Services",
    "healthcare_payers":      "Healthcare — Payers",
    "healthcare_providers":   "Healthcare — Providers",
    "healthcare_clinical":    "Healthcare — Clinical",
    "insurance_underwriting": "Insurance Underwriting",
    "retail":                 "Retail",
    "cpg":                    "CPG",
    "manufacturing":          "Manufacturing",
    "hr":                     "HR",
    "contact_center":         "Contact Center",
    "airlines":               "Airlines",
    "supply_chain":           "Supply Chain",
    "aerospace_defense":      "Aerospace & Defense",
    "core":                   "Core (cross-industry)",
    "integrations":           "Integrations",
}


# ─────────────────── docx helpers ───────────────────

def _set_font(run, *, size: int = 11, bold: bool = False, color: Tuple[int, int, int] = None,
              name: str = None, mono: bool = False):
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor(*color)
    if mono:
        run.font.name = "Courier New"
    elif name:
        run.font.name = name


def _set_cell_shading(cell, color_hex: str):
    """Apply fill color to a table cell (e.g. 'E8EEF7')."""
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def _add_heading(doc: Document, text: str, level: int):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        if level == 0:
            _set_font(run, size=22, bold=True, color=(15, 23, 42))
        elif level == 1:
            _set_font(run, size=16, bold=True, color=(37, 99, 235))
        elif level == 2:
            _set_font(run, size=13, bold=True, color=(15, 23, 42))
        else:
            _set_font(run, size=11, bold=True, color=(71, 85, 105))


def _add_para(doc: Document, text: str, *, size: int = 11, bold: bool = False,
              italic: bool = False, color: Tuple[int, int, int] = None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    _set_font(run, size=size, bold=bold, color=color)
    run.italic = italic
    return p


def _add_code_para(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    run = p.add_run(text)
    _set_font(run, size=10, mono=True, color=(15, 23, 42))


def _add_bulleted(doc: Document, items: List[str]):
    for item in items:
        p = doc.add_paragraph(item, style="List Bullet")
        for r in p.runs:
            _set_font(r, size=11)


def _schema_table(doc: Document, title: str, schema: Dict[str, Any], columns: List[str]):
    """Render a schema (dict of field → spec) as a 4-column table."""
    _add_para(doc, title, size=11, bold=True, color=(71, 85, 105))

    if not schema:
        p = doc.add_paragraph()
        run = p.add_run("No schema declared.")
        _set_font(run, size=10, color=(148, 163, 184))
        run.italic = True
        return

    tbl = doc.add_table(rows=1, cols=len(columns))
    tbl.autofit = True
    hdr = tbl.rows[0].cells
    for i, col in enumerate(columns):
        hdr[i].text = col
        _set_cell_shading(hdr[i], "E8EEF7")
        for p in hdr[i].paragraphs:
            for r in p.runs:
                _set_font(r, size=10, bold=True, color=(30, 58, 138))

    for name, spec in schema.items():
        if isinstance(spec, dict):
            t = spec.get("type", "any")
            desc = spec.get("description", "")
            req = "Yes" if spec.get("required") else ""
        else:
            t, desc, req = str(spec), "", ""
        row = tbl.add_row().cells
        vals = {"Field": name, "Type": t, "Required": req, "Description": desc}
        for i, col in enumerate(columns):
            row[i].text = vals.get(col, "")
            for p in row[i].paragraphs:
                for r in p.runs:
                    if col == "Field":
                        _set_font(r, size=10, mono=True, color=(15, 23, 42))
                    elif col == "Type":
                        _set_font(r, size=10, bold=True, color=(37, 99, 235))
                    elif col == "Required":
                        _set_font(r, size=10, bold=True,
                                  color=(185, 28, 28) if req == "Yes" else (148, 163, 184))
                    else:
                        _set_font(r, size=10, color=(51, 65, 85))


def _scenario_table(doc: Document, action_id: str):
    scenarios = SCENARIO.get(action_id)
    if not scenarios:
        return

    _add_para(doc, "Sample test values", size=11, bold=True, color=(71, 85, 105))

    for scenario in scenarios:
        # Scenario name
        p = doc.add_paragraph()
        run = p.add_run("● " + scenario["name"])
        _set_font(run, size=10, bold=True, color=(21, 128, 61))

        # Input as JSON
        import json
        _add_code_para(doc, json.dumps(scenario["input"], indent=2))

        # Expected outcome
        p = doc.add_paragraph()
        r1 = p.add_run("Expect: ")
        _set_font(r1, size=10, bold=True, color=(71, 85, 105))
        r2 = p.add_run(scenario["expect"])
        _set_font(r2, size=10, color=(51, 65, 85))
        r2.italic = True


# ─────────────────── document sections ───────────────────

def _write_cover(doc: Document, actions):
    _add_heading(doc, "Apex Action Test Script", level=0)
    _add_para(
        doc,
        f"Auto-generated manual test plan covering every registered action. "
        f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} local time "
        f"from {len(actions)} action handlers across "
        f"{len({a.industry for a in actions})} industries.",
        size=11, italic=True, color=(100, 116, 139),
    )
    _add_para(doc, "")  # spacer


def _write_overview(doc: Document):
    _add_heading(doc, "Overview", level=1)
    _add_para(
        doc,
        "This document describes how to execute the Apex Action Test Runner against every "
        "registered action handler and verify its behavior end-to-end. Every sample input "
        "referenced here is also seeded into the target AWS account by the provisioner, "
        "so the happy-path scenarios should return real successful responses.",
    )
    _add_para(doc, "")

    _add_heading(doc, "How to re-generate this document", level=2)
    _add_para(doc, "Whenever a new action handler is added, or an existing handler's schema changes:")
    _add_code_para(
        doc,
        "cd aws/backend && source venv/bin/activate\n"
        "python ../test-scripts/generate_test_script.py"
    )
    _add_para(
        doc,
        "The generator reads directly from the action registry, so the new action will be "
        "picked up automatically. Check in the updated .docx alongside your handler change.",
        italic=True, color=(100, 116, 139),
    )


def _write_prereqs(doc: Document):
    _add_heading(doc, "Prerequisites", level=1)
    _add_bulleted(doc, [
        "AWS CLI configured with a valid profile (us-east-1 region). "
        "Run `aws sts get-caller-identity` to confirm.",
        "DynamoDB tables provisioned. Run: "
        "`curl -X POST 'http://localhost:8000/api/v1/aws/provision?region=us-east-1'` "
        "or: `python -m services.aws_provisioner us-east-1` from `backend/`.",
        "Backend running: `cd backend && source venv/bin/activate && "
        "uvicorn main:app --reload --port 8000`",
        "Frontend running: `cd frontend && npm run dev`, then open http://localhost:3000/actions",
        "Registry reloaded after any handler change: "
        "`curl -X POST http://localhost:8000/api/v1/actions/registry/reload`",
    ])


def _write_testing_methodology(doc: Document):
    _add_heading(doc, "Testing methodology", level=1)
    _add_para(
        doc,
        "For each action below, perform both a UI test and a CLI test. Both paths hit the "
        "same backend endpoint, so they should produce identical results.",
    )

    _add_heading(doc, "UI test (preferred for screenshots)", level=2)
    _add_bulleted(doc, [
        "Open http://localhost:3000/actions",
        "Filter by industry or type if needed; click the action card to open the detail panel.",
        "Schema tab: confirm the fields listed here match what the document shows.",
        "Test Runner tab: pick a scenario below, fill its inputs in Form or JSON mode, click Run Test.",
        "Confirm the status badge (SUCCESS / RUNTIME / BAD ARGUMENTS / NOT FOUND), duration, "
        "and the output matches the 'Expect' line from the scenario.",
    ])

    _add_heading(doc, "CLI test (preferred for CI)", level=2)
    _add_para(doc, "Template:")
    _add_code_para(
        doc,
        "curl -s -X POST \\\n"
        "  'http://localhost:8000/api/v1/actions/registry/invoke/<ACTION_ID>' \\\n"
        "  -H 'Content-Type: application/json' \\\n"
        "  -d '<JSON_PAYLOAD>' | python3 -m json.tool"
    )

    _add_heading(doc, "What counts as a pass?", level=2)
    _add_bulleted(doc, [
        "SUCCESS: the response has ok=true and the result matches the Expect line.",
        "Clean NOT_FOUND/VENDOR_MISMATCH/OVER_TOLERANCE responses also count as passes when the "
        "scenario explicitly expects them — they prove the handler's branch coverage works.",
        "RUNTIME errors that reference a missing DynamoDB table indicate the provisioner hasn't "
        "run — this is environmental, not a handler bug.",
    ])


def _write_action_entry(doc: Document, action):
    _add_heading(doc, action.name, level=2)

    # Meta table: action_id, industry, category, handler
    tbl = doc.add_table(rows=4, cols=2)
    tbl.autofit = True
    rows = [
        ("Action ID",    action.action_id),
        ("Industry",     action.industry),
        ("Category",     action.category),
        ("Handler",      os.path.relpath(action.handler_path, _BACKEND_DIR.parent)),
    ]
    for i, (k, v) in enumerate(rows):
        c_k, c_v = tbl.rows[i].cells
        c_k.text = k
        c_v.text = v
        _set_cell_shading(c_k, "F1F5F9")
        for p in c_k.paragraphs:
            for r in p.runs:
                _set_font(r, size=10, bold=True, color=(71, 85, 105))
        for p in c_v.paragraphs:
            for r in p.runs:
                _set_font(r, size=10, mono=(k in ("Action ID", "Handler")), color=(15, 23, 42))

    _add_para(doc, "")  # spacer

    # Schemas
    _schema_table(doc, "Input parameters",
                  action.input_schema or {},
                  columns=["Field", "Type", "Required", "Description"])
    _add_para(doc, "")
    _schema_table(doc, "Output fields",
                  action.output_schema or {},
                  columns=["Field", "Type", "Description"])
    _add_para(doc, "")

    # Scenarios
    _scenario_table(doc, action.action_id)
    _add_para(doc, "")


def _write_troubleshooting(doc: Document):
    _add_heading(doc, "Troubleshooting", level=1)

    _add_heading(doc, "RUNTIME: ResourceNotFoundException", level=2)
    _add_para(doc, "The handler hit DynamoDB but the table doesn't exist yet. Run the provisioner:")
    _add_code_para(doc, "curl -X POST 'http://localhost:8000/api/v1/aws/provision?region=us-east-1'")

    _add_heading(doc, "NOT_FOUND: 'Action <id> is not registered'", level=2)
    _add_para(doc, "The handler file exists but isn't listed in INDUSTRY_ACTIONS. Add it to:")
    _add_code_para(doc, "aws/backend/services/action_registry.py → INDUSTRY_ACTIONS")
    _add_para(doc, "Then hot-reload the registry:")
    _add_code_para(doc, "curl -X POST http://localhost:8000/api/v1/actions/registry/reload")

    _add_heading(doc, "BAD ARGUMENTS", level=2)
    _add_para(
        doc,
        "The JSON payload field names don't match the handler's function parameters. "
        "Check the handler file's function signature — it's the source of truth. "
        "When in doubt, use Form mode in the Test Runner: it labels inputs exactly "
        "as the handler expects them.",
    )

    _add_heading(doc, "LOAD_FAILED: 'Handler failed to load'", level=2)
    _add_para(
        doc,
        "The handler file has a Python import error. Typical causes are a missing pip "
        "dependency in the backend venv (boto3, structlog, etc.) or a syntax error in the "
        "handler itself. Check the backend logs for the full traceback.",
    )


# ─────────────────── main ───────────────────

def main():
    # Force fresh discovery so we pick up any handler changes since backend start.
    registry = reload_registry()
    actions = registry.get_all_actions()

    # Group by industry.
    by_industry: Dict[str, List[Any]] = {}
    for a in actions:
        by_industry.setdefault(a.industry, []).append(a)

    # Sort actions within each industry by name.
    for lst in by_industry.values():
        lst.sort(key=lambda a: a.name)

    # Build ordered industry list: known order first, then anything unexpected.
    ordered = [i for i in INDUSTRY_ORDER if i in by_industry]
    ordered += sorted(k for k in by_industry if k not in INDUSTRY_ORDER)

    doc = Document()

    _write_cover(doc, actions)
    _write_overview(doc)
    _write_prereqs(doc)
    _write_testing_methodology(doc)

    _add_heading(doc, f"Action catalog ({len(actions)} total)", level=1)

    for industry in ordered:
        label = INDUSTRY_LABEL.get(industry, industry.replace("_", " ").title())
        entries = by_industry[industry]
        _add_heading(doc, f"{label} ({len(entries)})", level=1)
        for action in entries:
            _write_action_entry(doc, action)

    _write_troubleshooting(doc)

    # Footer paragraph
    _add_para(doc, "")
    _add_para(
        doc,
        f"— End of document. Regenerate with "
        f"`python test-scripts/generate_test_script.py` after any action change.",
        size=9, italic=True, color=(148, 163, 184),
    )

    doc.save(str(OUTPUT_PATH))

    print(f"✓ Generated {OUTPUT_PATH.name}")
    print(f"  Actions documented:  {len(actions)}")
    print(f"  Industries:          {len(ordered)} ({', '.join(ordered)})")
    print(f"  Scenarios covered:   {sum(len(SCENARIO.get(a.action_id, [])) for a in actions)}")
    print(f"  Output:              {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
