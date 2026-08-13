"""
EPROD AP Cycle orchestrator + SSE progress streaming.

Clone of telecommunications_cycle.py adapted for Enterprise Products Operating
(midstream AP). The pipeline routes an inbound document (invoice, PO, MSA,
quote, tariff sheet, JIB) through five stages:

  Stage 1  EXTRACT     parse document → structured-extract dict      ~2-4 s
  Stage 2  CLASSIFY    determine doc type, route to agent             ~1-2 s
  Stage 3  VALIDATE    rule pack per doc_type                          ~3-5 s
  (HITL gate — conditional)
  Stage 4  WRITE_BACK  queue ERP write-back                            ~1-2 s
  Stage 5  REPORT      emit AP Cycle Audit Report + PDF                ~2-3 s

Each stage emits SSE frames:
  event: cycle_start    data: {cycle_id, doc_path, started_at, trigger}
  event: stage_start    data: {stage_id, label, started_at}
  event: stage_done     data: {stage_id, ms, summary, output_keys[]}
  event: hitl_required  data: {request_id, severity, reason, …}
  event: hitl_decided   data: {request_id, decision, reviewer, comment, …}
  event: cycle_done     data: {cycle_id, report, write_back, …}
  event: cycle_halted   data: {cycle_id, reason, ended_at}
  event: error          data: {stage_id, error_message}
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, AsyncGenerator, Deque, Dict, List, Optional, Tuple

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from services.eprod_report_pdf import generate_ap_cycle_audit_report  # noqa: E402

router = APIRouter()
log = logging.getLogger(__name__)

REPORT_DIR = Path("/tmp/apex-eprod-reports")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_ROOT = ROOT / "synthetic-data" / "eprod"


# ─────────────────────── cycle history (in-memory) ───────────────────────
_CYCLE_HISTORY: Deque[Dict[str, Any]] = deque(maxlen=50)
_history_lock = asyncio.Lock()


async def _record_cycle(record: Dict[str, Any]) -> None:
    async with _history_lock:
        _CYCLE_HISTORY.appendleft(record)
        log.info("Recorded EPROD cycle %s (buffer size: %d)",
                 record.get("cycle_id"), len(_CYCLE_HISTORY))


# ─────────────────────── HITL ───────────────────────
_PENDING_HITL:   Dict[str, Dict[str, Any]] = {}
_HITL_EVENTS:    Dict[str, asyncio.Event] = {}
_HITL_DECISIONS: Dict[str, Dict[str, Any]] = {}
_HITL_LOCK = asyncio.Lock()
_HITL_TIMEOUT_SEC = 600


def _new_hitl_request(*, cycle_id: str, agent: str, gate: str, severity: str,
                       reason: str, data: Dict[str, Any]) -> str:
    request_id = f"HITL-{cycle_id}-{gate.upper()}"
    _PENDING_HITL[request_id] = {
        "request_id":  request_id,
        "cycle_id":    cycle_id,
        "agent":       agent,
        "gate":        gate,
        "severity":    severity,
        "reason":      reason,
        "data":        data,
        "created_at":  _now_ms(),
        "status":      "pending",
    }
    _HITL_EVENTS[request_id] = asyncio.Event()
    log.info("EPROD HITL created: %s · %s · agent=%s · gate=%s",
             request_id, severity, agent, gate)
    return request_id


async def _wait_for_hitl(request_id: str) -> Dict[str, Any]:
    event = _HITL_EVENTS.get(request_id)
    if event is None:
        return {"decision": "missing", "reason": "no event registered"}
    try:
        await asyncio.wait_for(event.wait(), timeout=_HITL_TIMEOUT_SEC)
        decision = _HITL_DECISIONS.get(request_id, {"decision": "missing"})
        log.info("EPROD HITL %s resolved: %s by %s",
                 request_id, decision.get("decision"), decision.get("reviewer"))
    except asyncio.TimeoutError:
        decision = {
            "decision":   "timeout",
            "reviewer":   "system",
            "decided_at": _now_ms(),
            "reason":     f"no human decision within {_HITL_TIMEOUT_SEC}s",
        }
        log.warning("EPROD HITL %s timed out — auto-reject", request_id)
    finally:
        pending = _PENDING_HITL.get(request_id)
        if pending is not None:
            pending["status"]      = decision.get("decision", "unknown")
            pending["resolved_at"] = _now_ms()
            pending["reviewer"]    = decision.get("reviewer", "system")
        asyncio.get_event_loop().call_later(8.0, _cleanup_hitl, request_id)
    return decision


def _cleanup_hitl(request_id: str) -> None:
    _PENDING_HITL.pop(request_id, None)
    _HITL_EVENTS.pop(request_id, None)
    _HITL_DECISIONS.pop(request_id, None)


# ─────────────────────── helpers ───────────────────────

def _sse(event: str, data: Dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _deterministic_seed(text: str) -> int:
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16)


def _confidence_scores(fields: List[str], seed: int) -> Dict[str, float]:
    rng = random.Random(seed)
    return {f: round(rng.uniform(0.85, 0.99), 3) for f in fields}


# ─────────────────────── doc-type classification ───────────────────────

_DOC_PATTERNS = [
    ("invoice",        re.compile(r"(invoice number|inv-|bill to|payment terms)", re.I)),
    ("purchase_order", re.compile(r"(purchase order|po-2026|po number)", re.I)),
    ("msa",            re.compile(r"(master service agreement|msa-)", re.I)),
    ("engineering_quote", re.compile(r"(quote-|engineering quote|proposal valid)", re.I)),
    ("tariff_sheet",   re.compile(r"(ferc tariff|tariff sheet|joint tariff)", re.I)),
    ("jib_statement",  re.compile(r"(joint interest billing|jib-|afe-)", re.I)),
]


def _classify_doc_text(text: str, hint: Optional[str] = None,
                        filename: Optional[str] = None) -> str:
    if hint and hint in {p[0] for p in _DOC_PATTERNS}:
        return hint
    # Filename may have a cycle_id prefix (e.g. "B8EA2A8B_INV-HAL-2026-...txt").
    # Match the doc-type tag anywhere in the filename, not just startswith.
    fn = (filename or "").upper()
    if "INV-" in fn:                          return "invoice"
    if "PO-2026" in fn or "_PO-" in fn:       return "purchase_order"
    if "MSA-" in fn:                          return "msa"
    if "QUOTE-" in fn:                        return "engineering_quote"
    if "FERC-" in fn or "TARIFF" in fn:       return "tariff_sheet"
    if "JIB-" in fn:                          return "jib_statement"
    for kind, rx in _DOC_PATTERNS:
        if rx.search(text):
            return kind
    return "invoice"


# ─────────────────────── extraction ───────────────────────

_RX_INV_NO     = re.compile(r"Invoice Number:\s*([A-Z0-9-]+)", re.I)
_RX_INV_DATE   = re.compile(r"Invoice Date:\s*([0-9/]+)", re.I)
_RX_PO_NO      = re.compile(r"PO Number:\s*([A-Z0-9-]+)", re.I)
_RX_MSA        = re.compile(r"MSA Reference:\s*([A-Z0-9-]+)", re.I)
_RX_TOTAL_LINE = re.compile(r"(?:Total Due|TOTAL DUE|Grand Total|Total Amount Due)[^\d]*\$?([\d,]+\.\d{2})", re.I)
_RX_SUBTOTAL   = re.compile(r"Subtotal[^\d]*\$?([\d,]+\.\d{2})", re.I)
_RX_TAX        = re.compile(r"(?:Sales Tax|Tax)[^\d]*\$?([\d,]+\.\d{2})", re.I)
_RX_AFE        = re.compile(r"AFE[:\s-]*([A-Z0-9-]+)", re.I)
_RX_QUOTE_NO   = re.compile(r"Quote (?:Number|#):\s*([A-Z0-9-]+)", re.I)
_RX_FERC_NO    = re.compile(r"FERC[\s-]*(?:Tariff|No\.?)[:\s]*([A-Z0-9.-]+)", re.I)


def _parse_money(s: Optional[str]) -> Optional[float]:
    if not s:
        return None
    try:
        return float(s.replace(",", ""))
    except Exception:
        return None


def _extract_vendor_from_top(text: str) -> Optional[str]:
    """Vendor name is usually one of the first non-empty lines after a banner."""
    for line in text.splitlines():
        stripped = line.strip().strip("=").strip()
        if not stripped:
            continue
        if any(k in stripped.upper() for k in ["INVOICE", "PURCHASE ORDER", "MASTER SERVICE",
                                                "ENGINEERING QUOTE", "JOINT INTEREST", "FERC TARIFF"]):
            continue
        if len(stripped) > 4 and not stripped.startswith(("Tax", "Phone", "P.O.", "3000")):
            return stripped[:80]
    return None


def _synthetic_extract(text: str, doc_type: str, filename: str) -> Dict[str, Any]:
    """Produce a realistic structured extract from the .txt sample."""
    seed = _deterministic_seed(filename + doc_type)
    rng = random.Random(seed)
    extracted: Dict[str, Any] = {"doc_type": doc_type}

    vendor = _extract_vendor_from_top(text)
    if vendor:
        extracted["vendor"] = vendor

    # invoice + JIB share many fields
    m = _RX_INV_NO.search(text);
    if m: extracted["invoice_number"] = m.group(1)
    m = _RX_INV_DATE.search(text);
    if m: extracted["invoice_date"] = m.group(1)
    m = _RX_PO_NO.search(text);
    if m: extracted["po_reference"] = m.group(1)
    m = _RX_MSA.search(text);
    if m: extracted["msa_reference"] = m.group(1)
    m = _RX_AFE.search(text);
    if m: extracted["afe_reference"] = m.group(1)
    m = _RX_TOTAL_LINE.search(text);
    if m: extracted["total"] = _parse_money(m.group(1))
    m = _RX_SUBTOTAL.search(text);
    if m: extracted["subtotal"] = _parse_money(m.group(1))
    m = _RX_TAX.search(text);
    if m: extracted["tax"] = _parse_money(m.group(1))
    m = _RX_QUOTE_NO.search(text);
    if m: extracted["quote_number"] = m.group(1)
    m = _RX_FERC_NO.search(text);
    if m: extracted["ferc_tariff_no"] = m.group(1)

    # doc-type-specific overlays
    if doc_type == "purchase_order":
        extracted.setdefault("po_reference", filename.replace(".txt", "").upper())
        extracted.setdefault("total", round(rng.uniform(15_000, 280_000), 2))
        extracted["scope"] = "Pipeline integrity inspection — Mont Belvieu lateral"
        extracted["asset_code"] = rng.choice(["EPD-PL-MB-04", "EPD-PL-SWY-12", "EPD-PL-HOU-22"])
    elif doc_type == "msa":
        extracted.setdefault("msa_reference", filename.replace(".txt", "").upper())
        extracted["effective_date"] = "2024-07-01"
        extracted["expiration_date"] = "2027-06-30"
        extracted["scope_summary"] = "Field services — well testing, slickline, integrity"
    elif doc_type == "engineering_quote":
        extracted.setdefault("total", round(rng.uniform(85_000, 410_000), 2))
        extracted["project"] = rng.choice(["Sweeny C2 expansion", "Mont Belvieu storage caverns",
                                            "Houston Ship Channel dock 12"])
    elif doc_type == "tariff_sheet":
        extracted.setdefault("ferc_tariff_no", "FERC-EPD-NGL-2026-001")
        extracted["effective_date"] = "2026-04-01"
        extracted["product"] = rng.choice(["NGL", "Crude", "Refined Products"])
        extracted["base_rate_per_bbl"] = round(rng.uniform(0.45, 1.85), 4)
        extracted["proposed_rate_per_bbl"] = round(extracted["base_rate_per_bbl"] *
                                                    rng.uniform(1.005, 1.028), 4)
    elif doc_type == "jib_statement":
        extracted.setdefault("afe_reference", "AFE-2026-EPC-1184")
        extracted.setdefault("total", round(rng.uniform(45_000, 350_000), 2))
        extracted["partner_share_pct"] = round(rng.choice([0.25, 0.3333, 0.50, 0.625]), 4)
        extracted["operator"] = "Enterprise Products Operating LLC"

    # asset code (commonly extracted)
    extracted.setdefault("asset_code", rng.choice([
        "EPD-PL-MB-04", "EPD-FT-SWY-08", "EPD-CN-HSC-12",
        "EPD-COMP-AGUA-03", "EPD-PROC-MTB-21",
    ]))

    # synthetic line items
    line_items: List[Dict[str, Any]] = []
    for i in range(rng.randint(2, 5)):
        qty = rng.randint(1, 12)
        unit = round(rng.uniform(450, 8500), 2)
        line_items.append({
            "description": rng.choice([
                "Pipeline integrity inspection — ILI run",
                "Slickline services — well intervention",
                "Cathodic protection survey",
                "Hydrotest — 6 mile lateral",
                "PHMSA Part 195 compliance review",
                "Compressor station maintenance — Q2",
                "Hot tap engineering review",
                "Valve actuator replacement",
            ]),
            "quantity":    qty,
            "unit_price":  unit,
            "total":       round(qty * unit, 2),
        })
    extracted["line_items"] = line_items

    # confidence per leaf field
    leaf_keys = [k for k, v in extracted.items()
                 if not isinstance(v, (list, dict)) and k != "doc_type"]
    extracted["_confidence"] = _confidence_scores(leaf_keys, seed)

    return extracted


# ─────────────────────── validation ───────────────────────

def _validate(doc_type: str, extracted: Dict[str, Any]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    seed = _deterministic_seed(json.dumps(extracted, default=str, sort_keys=True))
    rng = random.Random(seed)

    if doc_type == "invoice":
        if not extracted.get("po_reference"):
            findings.append({
                "rule":     "PO match required",
                "expected": "PO referenced on invoice",
                "actual":   "No PO reference",
                "severity": "high" if (extracted.get("total") or 0) > 25_000 else "medium",
                "action":   "Block payment until PO is attached",
            })
        else:
            findings.append({
                "rule":     "PO match required",
                "expected": "PO referenced on invoice",
                "actual":   f"Matched {extracted['po_reference']}",
                "severity": "pass",
                "action":   "Auto-link to PO record",
            })

        if not extracted.get("msa_reference"):
            findings.append({
                "rule":     "MSA scope check",
                "expected": "Active MSA on file",
                "actual":   "No MSA reference",
                "severity": "medium",
                "action":   "Route to Procurement to confirm MSA",
            })
        else:
            findings.append({
                "rule":     "MSA scope check",
                "expected": "Active MSA on file",
                "actual":   f"Matched {extracted['msa_reference']}",
                "severity": "pass",
                "action":   "Within MSA scope — proceed",
            })

        # duplicate check
        dup_flag = rng.random() < 0.12
        findings.append({
            "rule":     "Duplicate-invoice check",
            "expected": "No prior payment for invoice_number",
            "actual":   "Possible duplicate (90-day window)" if dup_flag else "No duplicate found",
            "severity": "high" if dup_flag else "pass",
            "action":   "Hold — manual review" if dup_flag else "Clear",
        })

        # tax code
        if extracted.get("tax") is None:
            findings.append({
                "rule":     "Tax code validation",
                "expected": "Sales tax present or exempt-cert on file",
                "actual":   "No tax line found",
                "severity": "low",
                "action":   "Verify exemption status",
            })
        else:
            findings.append({
                "rule":     "Tax code validation",
                "expected": "TX-77 rate applied (8.25%)",
                "actual":   f"${extracted['tax']:.2f} present",
                "severity": "pass",
                "action":   "Tax code OK",
            })

        # rate variance
        var_pct = round(rng.uniform(-2.5, 4.5), 2)
        findings.append({
            "rule":     "Rate variance vs MSA",
            "expected": "Within ±2% of MSA rate card",
            "actual":   f"{var_pct:+.2f}%",
            "severity": "high" if abs(var_pct) > 3.0 else ("medium" if abs(var_pct) > 2.0 else "pass"),
            "action":   "Escalate to Procurement" if abs(var_pct) > 3.0 else "Within tolerance",
        })

    elif doc_type == "purchase_order":
        outside_scope = rng.random() < 0.18
        findings.append({
            "rule":     "PO scope vs MSA",
            "expected": "PO line items inside MSA scope",
            "actual":   "Items outside MSA scope" if outside_scope else "All items within scope",
            "severity": "high" if outside_scope else "pass",
            "action":   "Block release — outside MSA scope" if outside_scope else "Approved for release",
        })
        threshold = 250_000
        amount = float(extracted.get("total") or 0)
        findings.append({
            "rule":     "Approval threshold",
            "expected": f"PO ≤ ${threshold:,} requires manager approval",
            "actual":   f"PO total ${amount:,.2f}",
            "severity": "medium" if amount > threshold else "pass",
            "action":   "Route to VP approval" if amount > threshold else "Within manager authority",
        })

    elif doc_type == "jib_statement":
        # For the demo, AFE balance is deterministically lower than the JIB
        # charge so the AFE-exceeded HITL gate reliably fires on every JIB
        # sample. This is the canonical "wow use case" trigger for the EPROD
        # discovery call. To exercise the pass-path, replace this with the
        # uniform range below.
        charge = float(extracted.get("total") or 0)
        afe_balance = round(charge * 0.62, 2)
        # Pass-path alternative (uncomment to demo the all-clear scenario):
        # afe_balance = round(rng.uniform(charge * 1.2, charge * 1.8), 2)
        if charge > afe_balance:
            findings.append({
                "rule":     "AFE balance check — AFE exceeded",
                "expected": f"Charge ≤ AFE remaining ${afe_balance:,.2f}",
                "actual":   f"Charge ${charge:,.2f}",
                "severity": "critical",
                "action":   "Halt write-back — escalate to Joint Venture Accounting",
                "detail":   f"JIB charge ${charge:,.2f} exceeds AFE remaining ${afe_balance:,.2f}",
            })
        else:
            findings.append({
                "rule":     "AFE balance check",
                "expected": f"Charge ≤ AFE remaining ${afe_balance:,.2f}",
                "actual":   f"Charge ${charge:,.2f}",
                "severity": "pass",
                "action":   "Within AFE balance",
            })

        share = float(extracted.get("partner_share_pct") or 0.25)
        computed_share = round(charge * share, 2)
        findings.append({
            "rule":     "Partner-share variance",
            "expected": f"Net charge = total × {share:.4f}",
            "actual":   f"${computed_share:,.2f}",
            "severity": "pass",
            "action":   "Variance within JOA terms",
        })

    elif doc_type == "tariff_sheet":
        base = float(extracted.get("base_rate_per_bbl") or 0)
        proposed = float(extracted.get("proposed_rate_per_bbl") or 0)
        var_pct = round(((proposed - base) / base * 100), 3) if base else 0
        findings.append({
            "rule":     "Tariff vs effective FERC rate",
            "expected": "Variance ≤ 1.5% from currently effective FERC rate",
            "actual":   f"{var_pct:+.3f}%",
            "severity": "high" if var_pct > 1.5 else "pass",
            "action":   "FERC re-filing required" if var_pct > 1.5 else "Within FERC index ceiling",
            "variance_pct": var_pct,
        })

    elif doc_type == "engineering_quote":
        hist_avg = round(float(extracted.get("total") or 100_000) * rng.uniform(0.85, 1.10), 2)
        delta_pct = round(((float(extracted.get("total") or 0) - hist_avg) / hist_avg * 100), 2)
        findings.append({
            "rule":     "Vendor historical rate comparison",
            "expected": f"Quote within ±10% of vendor 12-mo avg (${hist_avg:,.2f})",
            "actual":   f"{delta_pct:+.2f}%",
            "severity": "medium" if abs(delta_pct) > 10 else "pass",
            "action":   "Negotiate" if abs(delta_pct) > 10 else "Accept",
        })

    elif doc_type == "msa":
        findings.append({
            "rule":     "MSA ingestion",
            "expected": "MSA indexed for downstream PO/invoice matching",
            "actual":   f"Indexed {extracted.get('msa_reference','—')}",
            "severity": "pass",
            "action":   "Available to InvoiceAgent + POAgent",
        })

    return findings


# ─────────────────────── HITL gate ───────────────────────

def _needs_hitl(doc_type: str, extracted: Dict[str, Any],
                 validation_findings: List[Dict[str, Any]]) -> Optional[Tuple[str, str]]:
    if doc_type == "invoice":
        if (extracted.get("total") or 0) > 50_000 and not extracted.get("po_reference"):
            return ("high", "Invoice over $50K with no PO reference")
        if any(f["severity"] in ("high", "critical") for f in validation_findings):
            return ("high", "High-severity validation finding")
    if doc_type == "jib_statement":
        for f in validation_findings:
            if "AFE exceeded" in f.get("rule", ""):
                return ("critical", f.get("detail", "AFE balance exceeded"))
    if doc_type == "tariff_sheet":
        for f in validation_findings:
            if f.get("variance_pct", 0) > 1.5:
                return ("high", "Tariff variance > 1.5% vs effective FERC rate")
    if doc_type == "purchase_order":
        if any("outside MSA scope" in f.get("rule", "") or
                ("outside MSA scope" in str(f.get("action", "")).lower())
                for f in validation_findings):
            return ("high", "PO scope outside MSA")
        if any(f["severity"] == "high" for f in validation_findings):
            return ("high", "High-severity PO finding")
    return None


HITL_THRESHOLDS = [
    {"doc_type": "invoice",       "rule": "amount > $50,000 AND no PO reference",
     "severity": "high"},
    {"doc_type": "invoice",       "rule": "any high/critical validation finding",
     "severity": "high"},
    {"doc_type": "purchase_order","rule": "PO outside MSA scope",
     "severity": "high"},
    {"doc_type": "jib_statement", "rule": "JIB charge > AFE remaining balance",
     "severity": "critical"},
    {"doc_type": "tariff_sheet",  "rule": "tariff variance > 1.5% vs effective FERC rate",
     "severity": "high"},
]


# ─────────────────────── agents per doc type ───────────────────────

_AGENTS_FOR_DOC = {
    "invoice":           ["InvoiceAgent", "VendorAgent", "ApexSignal"],
    "purchase_order":    ["POAgent", "VendorAgent"],
    "msa":               ["ContractAgent"],
    "engineering_quote": ["VendorAgent", "EngineeringAgent"],
    "tariff_sheet":      ["TariffAgent", "PolicyAgent"],
    "jib_statement":     ["JIBAgent", "PartnerShareAgent"],
}


def _stage_done_summary(out: Dict[str, Any], stage_id: str) -> str:
    if stage_id == "extract":
        n = len(out.get("extracted", {})) - 2  # minus doc_type + _confidence
        return f"{n} fields extracted · vendor: {out.get('extracted', {}).get('vendor', '—')}"
    if stage_id == "classify":
        return f"doc_type: {out.get('doc_type')} → routed to {', '.join(out.get('agents', []))}"
    if stage_id == "validate":
        findings = out.get("findings", [])
        crit = sum(1 for f in findings if f["severity"] in ("high", "critical"))
        return f"{len(findings)} finding(s) · {crit} high/critical"
    if stage_id == "write_back":
        return f"queued ERP write-back · ref {out.get('write_back', {}).get('ref','—')}"
    if stage_id == "report":
        return f"AP Cycle Audit Report emitted · cycle {out.get('cycle_id','—')}"
    return ""


# ─────────────────────── orchestrator ───────────────────────

async def _run_pipeline(doc_path: str, cycle_id: str,
                         cycle_type: Optional[str] = None,
                         trigger: str = "ui_upload",
                         source_label: Optional[str] = None
                         ) -> AsyncGenerator[str, None]:
    pipeline_started_at = _now_ms()
    audit_trail: List[Dict[str, Any]] = []
    source_label = source_label or doc_path
    filename = Path(doc_path).name

    yield _sse("cycle_start", {
        "cycle_id":    cycle_id,
        "doc_path":    str(doc_path),
        "source":      source_label,
        "started_at":  pipeline_started_at,
        "trigger":     trigger,
    })

    # ─── Stage 1 · EXTRACT ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "extract", "label": "Extract Document",
                                "started_at": t0})
    try:
        text = Path(doc_path).read_text(encoding="utf-8", errors="ignore")
        await asyncio.sleep(random.uniform(2.0, 4.0))
        doc_type_hint = cycle_type
        # We need a doc_type to drive extraction; classify lightly upfront,
        # then re-classify in stage 2 for the explicit step.
        provisional_type = _classify_doc_text(text, hint=doc_type_hint, filename=filename)
        extracted = _synthetic_extract(text, provisional_type, filename)
    except Exception as e:
        log.exception("EPROD extract failed")
        yield _sse("error", {"stage_id": "extract", "error_message": str(e)})
        return
    elapsed = _now_ms() - t0
    audit_trail.append({"stage": "extract", "started_at": t0,
                        "duration_ms": elapsed, "outcome": "ok"})
    yield _sse("stage_done", {"stage_id": "extract", "ms": elapsed,
                               "summary": _stage_done_summary({"extracted": extracted}, "extract"),
                               "output_keys": list(extracted.keys()),
                               "extracted": extracted})

    # ─── Stage 2 · CLASSIFY ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "classify", "label": "Classify & Route",
                                "started_at": t0})
    await asyncio.sleep(random.uniform(1.0, 2.0))
    doc_type = _classify_doc_text(text, hint=doc_type_hint, filename=filename)
    extracted["doc_type"] = doc_type
    agents = _AGENTS_FOR_DOC.get(doc_type, ["InvoiceAgent"])
    elapsed = _now_ms() - t0
    audit_trail.append({"stage": "classify", "started_at": t0,
                        "duration_ms": elapsed, "outcome": f"doc_type={doc_type}"})
    yield _sse("stage_done", {"stage_id": "classify", "ms": elapsed,
                               "summary": _stage_done_summary({"doc_type": doc_type, "agents": agents}, "classify"),
                               "output_keys": ["doc_type", "agents"],
                               "doc_type": doc_type, "agents": agents})

    # ─── Stage 3 · VALIDATE ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "validate", "label": "Validate",
                                "started_at": t0})
    await asyncio.sleep(random.uniform(3.0, 5.0))
    findings = _validate(doc_type, extracted)
    elapsed = _now_ms() - t0
    audit_trail.append({"stage": "validate", "started_at": t0,
                        "duration_ms": elapsed,
                        "outcome": f"{len(findings)} finding(s)"})
    yield _sse("stage_done", {"stage_id": "validate", "ms": elapsed,
                               "summary": _stage_done_summary({"findings": findings}, "validate"),
                               "output_keys": ["findings"],
                               "findings": findings})

    # ─── HITL gate ───
    hitl_record: Optional[Dict[str, Any]] = None
    gate = _needs_hitl(doc_type, extracted, findings)
    if gate is not None:
        gate_severity, reason = gate
        request_id = _new_hitl_request(
            cycle_id=cycle_id,
            agent=agents[0] if agents else "InvoiceAgent",
            gate=f"{doc_type}-gate",
            severity=gate_severity,
            reason=reason,
            data={
                "doc_type":  doc_type,
                "vendor":    extracted.get("vendor"),
                "total":     extracted.get("total"),
                "po_ref":    extracted.get("po_reference"),
                "msa_ref":   extracted.get("msa_reference"),
                "afe_ref":   extracted.get("afe_reference"),
                "findings":  findings,
            },
        )
        yield _sse("hitl_required", {
            "request_id": request_id,
            "cycle_id":   cycle_id,
            "agent":      agents[0] if agents else "InvoiceAgent",
            "gate":       f"{doc_type}-gate",
            "severity":   gate_severity,
            "reason":     reason,
            "proposed_action": f"Hold {doc_type} pending human review.",
        })

        decision = await _wait_for_hitl(request_id)
        hitl_record = {
            "request_id":  request_id,
            "gate":        f"{doc_type}-gate",
            "severity":    gate_severity,
            "reason":      reason,
            "reviewer":    decision.get("reviewer"),
            "decision":    decision.get("decision"),
            "comment":     decision.get("comment", ""),
            "decided_at":  decision.get("decided_at"),
        }
        yield _sse("hitl_decided", {
            "request_id": request_id,
            "decision":   decision.get("decision"),
            "reviewer":   decision.get("reviewer"),
            "comment":    decision.get("comment", ""),
            "decided_at": decision.get("decided_at"),
        })

        if decision.get("decision") != "approve":
            ended_at = _now_ms()
            status_str = f"HALTED — HITL {decision.get('decision','?')}"
            audit_trail.append({"stage": "hitl", "started_at": ended_at,
                                "duration_ms": 0,
                                "outcome": f"{decision.get('decision')} by {decision.get('reviewer','—')}"})
            cycle = {
                "cycle_id":             cycle_id,
                "started_at":           pipeline_started_at,
                "ended_at":             ended_at,
                "duration_ms":          ended_at - pipeline_started_at,
                "trigger":              trigger,
                "source":               source_label,
                "doc_type":             doc_type,
                "extracted":            extracted,
                "validation_findings":  findings,
                "hitl":                 hitl_record,
                "audit_trail":          audit_trail,
                "status":               status_str,
                "agents":               agents,
                "vendor":               extracted.get("vendor"),
                "total":                extracted.get("total"),
                "write_back":           None,
                "report":               None,
            }
            # generate report for halted cycles too
            pdf_path = REPORT_DIR / f"{cycle_id}.pdf"
            try:
                generate_ap_cycle_audit_report(cycle, pdf_path)
                cycle["pdf_path"] = str(pdf_path)
            except Exception:
                log.exception("PDF generation failed for halted cycle %s", cycle_id)
            yield _sse("cycle_halted", {
                "cycle_id":  cycle_id,
                "reason":    f"halted by HITL: {decision.get('decision')} ({decision.get('reviewer','—')})",
                "ended_at":  ended_at,
                "pdf_url":   f"/api/v1/eprod/report/{cycle_id}",
            })
            await _record_cycle(cycle)
            return

    # ─── Stage 4 · WRITE_BACK ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "write_back", "label": "ERP Write-Back",
                                "started_at": t0})
    await asyncio.sleep(random.uniform(1.0, 2.0))
    write_back = {
        "ref":         f"ERP-{cycle_id}",
        "system":      "SAP S/4HANA (mock)",
        "doc_type":    doc_type,
        "amount":      extracted.get("total"),
        "vendor":      extracted.get("vendor"),
        "asset_code":  extracted.get("asset_code"),
        "queued_at":   _now_ms(),
        "status":      "queued",
    }
    elapsed = _now_ms() - t0
    audit_trail.append({"stage": "write_back", "started_at": t0,
                        "duration_ms": elapsed, "outcome": "queued"})
    yield _sse("stage_done", {"stage_id": "write_back", "ms": elapsed,
                               "summary": _stage_done_summary({"write_back": write_back}, "write_back"),
                               "output_keys": list(write_back.keys()),
                               "write_back": write_back})

    # ─── Stage 5 · REPORT ───
    t0 = _now_ms()
    yield _sse("stage_start", {"stage_id": "report", "label": "Emit Audit Report",
                                "started_at": t0})
    await asyncio.sleep(random.uniform(2.0, 3.0))
    status_str = "HITL APPROVED" if hitl_record else "PASS"
    report = {
        "report_id":            f"AP-{cycle_id}",
        "cycle_id":             cycle_id,
        "doc_type":             doc_type,
        "vendor":               extracted.get("vendor"),
        "amount":               extracted.get("total"),
        "asset_code":           extracted.get("asset_code"),
        "po_reference":         extracted.get("po_reference"),
        "msa_reference":        extracted.get("msa_reference"),
        "afe_reference":        extracted.get("afe_reference"),
        "agents":               agents,
        "validation_summary":   {
            "total":    len(findings),
            "high":     sum(1 for f in findings if f["severity"] == "high"),
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "medium":   sum(1 for f in findings if f["severity"] == "medium"),
            "pass":     sum(1 for f in findings if f["severity"] == "pass"),
        },
        "hitl":                 hitl_record,
        "audit_lens_event_id":  f"AUDIT-{cycle_id}",
    }
    elapsed = _now_ms() - t0
    audit_trail.append({"stage": "report", "started_at": t0,
                        "duration_ms": elapsed, "outcome": "emitted"})
    yield _sse("stage_done", {"stage_id": "report", "ms": elapsed,
                               "summary": _stage_done_summary({"cycle_id": cycle_id}, "report"),
                               "output_keys": list(report.keys()),
                               "report": report})

    # ─── Generate PDF ───
    ended_at = _now_ms()
    duration_ms = ended_at - pipeline_started_at
    cycle = {
        "cycle_id":            cycle_id,
        "started_at":          pipeline_started_at,
        "ended_at":            ended_at,
        "duration_ms":         duration_ms,
        "trigger":             trigger,
        "source":              source_label,
        "doc_type":            doc_type,
        "extracted":           extracted,
        "validation_findings": findings,
        "hitl":                hitl_record,
        "audit_trail":         audit_trail,
        "status":              status_str,
        "agents":              agents,
        "vendor":              extracted.get("vendor"),
        "total":               extracted.get("total"),
        "write_back":          write_back,
        "report":              report,
    }
    pdf_path = REPORT_DIR / f"{cycle_id}.pdf"
    try:
        generate_ap_cycle_audit_report(cycle, pdf_path)
        cycle["pdf_path"] = str(pdf_path)
    except Exception:
        log.exception("PDF generation failed for cycle %s", cycle_id)

    yield _sse("cycle_done", {
        "cycle_id":    cycle_id,
        "ended_at":    ended_at,
        "duration_ms": duration_ms,
        "trigger":     trigger,
        "doc_type":    doc_type,
        "status":      status_str,
        "report":      report,
        "write_back":  write_back,
        "agents":      agents,
        "pdf_url":     f"/api/v1/eprod/report/{cycle_id}",
    })

    await _record_cycle(cycle)


# ─────────────────────── routes ───────────────────────

async def _drain_pipeline_to_completion(doc_path: str, cycle_id: str,
                                         tmp_to_clean: Optional[Path],
                                         cycle_type: Optional[str],
                                         trigger: str = "s3_event",
                                         source_label: Optional[str] = None) -> None:
    try:
        async for _ in _run_pipeline(doc_path, cycle_id,
                                      cycle_type=cycle_type,
                                      trigger=trigger,
                                      source_label=source_label):
            pass
        log.info("EPROD Path-B pipeline complete: cycle=%s", cycle_id)
    except Exception:
        log.exception("EPROD Path-B pipeline raised: cycle=%s", cycle_id)
    finally:
        if tmp_to_clean is not None:
            try: tmp_to_clean.unlink(missing_ok=True)
            except Exception: pass


@router.post("/cycle-start")
async def cycle_start(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    cycle_type: Optional[str] = Form(None),
    s3_key: Optional[str] = Form(None),
    bucket: Optional[str] = Form(None),
):
    """Kick off an EPROD AP cycle. SSE stream (Path A) or background task (Path B)."""
    cycle_id = uuid.uuid4().hex[:12].upper()
    doc_path: Optional[Path] = None
    tmp_to_clean: Optional[Path] = None

    if file is not None:
        tmp_dir = Path("/tmp/apex-eprod-cycles")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        doc_path = tmp_dir / f"{cycle_id}_{file.filename}"
        contents = await file.read()
        doc_path.write_bytes(contents)
        tmp_to_clean = doc_path
    elif s3_key:
        try:
            import boto3
            s3 = boto3.client("s3")
            resolved_bucket = (
                bucket
                or request.headers.get("x-apex-bucket")
                or request.headers.get("X-Apex-Bucket")
                or os.environ.get("CONTAINER_DOCUMENTS_INCOMING", "")
            )
            if not resolved_bucket:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No bucket — pass `bucket` form field, "
                                           "X-Apex-Bucket header, or set CONTAINER_DOCUMENTS_INCOMING env.")
            tmp_dir = Path("/tmp/apex-eprod-cycles")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            doc_path = tmp_dir / f"{cycle_id}_{Path(s3_key).name}"
            log.info("EPROD Path-B S3 download: bucket=%s key=%s", resolved_bucket, s3_key)
            s3.download_file(resolved_bucket, s3_key, str(doc_path))
            tmp_to_clean = doc_path
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail=f"S3 download failed: {e}")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provide either `file` (multipart) or `s3_key` (form field).")

    if s3_key:
        background_tasks.add_task(
            _drain_pipeline_to_completion,
            str(doc_path), cycle_id, tmp_to_clean, cycle_type,
            "s3_event", s3_key,
        )
        return JSONResponse(
            status_code=202,
            content={
                "status":     "accepted",
                "cycle_id":   cycle_id,
                "trigger":    "s3-event",
                "s3_key":     s3_key,
                "message":    "EPROD pipeline running in background.",
            },
        )

    source_label = (file.filename if file else None) or str(doc_path)

    async def stream() -> AsyncGenerator[str, None]:
        try:
            async for frame in _run_pipeline(str(doc_path), cycle_id,
                                              cycle_type=cycle_type,
                                              trigger="ui_upload",
                                              source_label=source_label):
                yield frame
        finally:
            if tmp_to_clean is not None:
                try: tmp_to_clean.unlink(missing_ok=True)
                except Exception: pass

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":        "keep-alive",
        },
    )


@router.get("/cycle-status/{cycle_id}")
async def cycle_status(cycle_id: str):
    return {"cycle_id": cycle_id, "status": "ephemeral",
            "note": "cycle-start streams to completion"}


@router.get("/hitl/pending")
async def hitl_pending() -> Dict[str, Any]:
    items = sorted(
        list(_PENDING_HITL.values()),
        key=lambda r: r.get("created_at", 0),
        reverse=True,
    )
    return {"count": len(items), "items": items}


class _HitlDecisionPayload(BaseModel):
    reviewer: Optional[str] = "James Patchett"
    comment:  Optional[str] = None


@router.post("/hitl/{request_id}/approve")
async def hitl_approve(request_id: str, payload: _HitlDecisionPayload) -> Dict[str, Any]:
    if request_id not in _PENDING_HITL:
        raise HTTPException(status_code=404, detail=f"HITL request not found: {request_id}")
    if request_id not in _HITL_EVENTS:
        raise HTTPException(status_code=409, detail="Request already resolved")
    decision = {
        "request_id": request_id,
        "decision":   "approve",
        "reviewer":   payload.reviewer or "Unknown",
        "comment":    payload.comment or "",
        "decided_at": _now_ms(),
    }
    _HITL_DECISIONS[request_id] = decision
    _HITL_EVENTS[request_id].set()
    log.info("EPROD HITL approved: %s by %s", request_id, decision["reviewer"])
    return decision


@router.post("/hitl/{request_id}/reject")
async def hitl_reject(request_id: str, payload: _HitlDecisionPayload) -> Dict[str, Any]:
    if request_id not in _PENDING_HITL:
        raise HTTPException(status_code=404, detail=f"HITL request not found: {request_id}")
    if request_id not in _HITL_EVENTS:
        raise HTTPException(status_code=409, detail="Request already resolved")
    decision = {
        "request_id": request_id,
        "decision":   "reject",
        "reviewer":   payload.reviewer or "Unknown",
        "comment":    payload.comment or "",
        "decided_at": _now_ms(),
    }
    _HITL_DECISIONS[request_id] = decision
    _HITL_EVENTS[request_id].set()
    log.info("EPROD HITL rejected: %s by %s", request_id, decision["reviewer"])
    return decision


@router.get("/cycle-history")
async def cycle_history(limit: int = 50) -> Dict[str, Any]:
    limit = max(1, min(limit, 50))
    async with _history_lock:
        items = list(_CYCLE_HISTORY)[:limit]
    # don't ship the entire extracted blob in history
    slim_items = []
    for it in items:
        slim = {k: v for k, v in it.items()
                 if k not in {"extracted", "validation_findings", "audit_trail"}}
        slim["extracted_field_count"] = len(it.get("extracted", {}))
        slim["finding_count"] = len(it.get("validation_findings", []))
        slim_items.append(slim)
    return {"count": len(_CYCLE_HISTORY), "items": slim_items}


@router.get("/sample-files")
async def sample_files() -> Dict[str, Any]:
    """List bundled EPROD sample documents (invoices, POs, MSAs, quotes,
    tariff sheets, JIB statements). Frontend Run page uses these for the
    'drop one of these' picker."""
    files: List[Dict[str, Any]] = []
    if SAMPLE_ROOT.is_dir():
        # subfolder → doc_type mapping
        subdir_to_type = {
            "invoices":            "invoice",
            "purchase_orders":     "purchase_order",
            "msas":                "msa",
            "engineering_quotes":  "engineering_quote",
            "tariff_sheets":       "tariff_sheet",
            "jib_statements":      "jib_statement",
        }
        for subdir, doc_type in subdir_to_type.items():
            d = SAMPLE_ROOT / subdir
            if not d.is_dir():
                continue
            for p in sorted(d.glob("*.txt")):
                files.append({
                    "name":       p.name,
                    "label":      p.stem.replace("_", " "),
                    "doc_type":   doc_type,
                    "size_bytes": p.stat().st_size,
                    "demo_path":  str(p.relative_to(ROOT)),
                })
    return {"count": len(files), "files": files}


@router.get("/report/{cycle_id}")
async def report_download(cycle_id: str):
    """Download the AP Cycle Audit Report PDF for a completed cycle."""
    pdf_path = REPORT_DIR / f"{cycle_id}.pdf"
    if not pdf_path.is_file():
        raise HTTPException(status_code=404, detail=f"Report not found for {cycle_id}")
    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=f"EPROD-AP-Cycle-{cycle_id}.pdf",
    )


@router.get("/hitl-thresholds")
async def hitl_thresholds() -> Dict[str, Any]:
    """List the HITL trigger thresholds so the frontend can render them."""
    return {
        "thresholds": HITL_THRESHOLDS,
        "timeout_sec": _HITL_TIMEOUT_SEC,
    }


# ═══════════════════════════════════════════════════════════════════════
# GET /eprod/dashboard-state
# Single consolidated endpoint that hydrates the 3 EPROD pages
# (Dashboard, Command Center, Apex Signal). Replaces hardcoded UI values.
# ═══════════════════════════════════════════════════════════════════════
@router.get("/dashboard-state")
async def eprod_dashboard_state() -> Dict[str, Any]:
    """Consolidated data feed for EPROD demo pages.

    Returns a structured payload covering:
      • kpis              — 3 headline KPIs (review reduction, coverage, leakage)
      • agents            — 6-agent status with per-agent metrics
      • throughput        — 30-day daily docs + HITL routed counts
      • throughput_14d    — last-14-day subset for command-center chart
      • phases            — 6 POC phase tracker states
      • tariff_diff       — FERC vs invoice rate comparison (the wow viewer)
      • jib_reconciliation — 4 JV operator AFE-vs-JIB rows
      • processing_feed   — 15 seed terminal entries + ticker hints
      • generated_at      — server timestamp
    """
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    # ── 30-day throughput series ────────────────────────────────────
    # Anchored to a stable mean (159 docs/day, 13 HITL routed/day) with
    # day-of-week seasonality and small deterministic noise so the chart
    # looks lived-in. Use a date-based seed so reloads are stable.
    base = now.date()
    days = [(base - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    docs = []
    hitl = []
    for i, d in enumerate(days):
        dow = (i + 4) % 7   # Mon=0 .. Sun=6 (rough)
        seasonal = 1.0 if dow < 5 else 0.78   # weekends slower
        seed_val = (sum(ord(c) for c in d) * 13) % 50
        v = int(round(159 * seasonal + (seed_val - 25) * 0.6))
        h = int(round(v * 0.082 + ((seed_val % 7) - 3) * 0.3))
        docs.append({"date": d, "value": v})
        hitl.append({"date": d, "value": max(4, h)})

    throughput_30d = {"docs_processed": docs, "hitl_routed": hitl}
    throughput_14d = {
        "docs_processed": docs[-14:],
        "hitl_routed":    hitl[-14:],
    }
    docs_30d_total = sum(d["value"] for d in docs)

    # ── KPIs ────────────────────────────────────────────────────────
    kpis = {
        "review_reduction_pct":      75,
        "review_minutes_before":     45,
        "review_minutes_after":      11,
        "validation_coverage_pct":   100,
        "validation_before_text":    "10–30% spot-check sampling",
        "validation_segments":       ["Invoices", "POs", "FERC Tariffs"],
        "cost_leakage_caught_usd":   2_400_000,
        "leakage_breakdown": [
            {"label": "Rate errors",      "amount_usd": 1_100_000},
            {"label": "FERC drift",       "amount_usd":   800_000},
            {"label": "Tax errors",       "amount_usd":   500_000},
        ],
    }

    # ── 6-agent status with per-agent metrics ──────────────────────
    agents = [
        {"id": "invoice", "name": "Invoice Agent",     "use_case": "Invoice Intelligence · UC1",
         "accent": "#1a6db5", "badge": "Active", "badge_tone": "green", "doc_count": 1247,
         "starred": False,
         "metrics": [
             {"label": "Accuracy",       "value": "94.2%", "tone": "good"},
             {"label": "HITL Queue",     "value": "3 pending", "tone": "warn"},
             {"label": "Avg Confidence", "value": "91.8%", "tone": "neutral"},
         ]},
        {"id": "po", "name": "PO Agent",                "use_case": "PO-to-Contract Validation · UC2",
         "accent": "#7c3aed", "badge": "Active", "badge_tone": "green", "doc_count": 389,
         "starred": False,
         "metrics": [
             {"label": "Accuracy",         "value": "92.7%", "tone": "good"},
             {"label": "Mismatches Found", "value": "14 flagged", "tone": "bad"},
             {"label": "Cycle Time",       "value": "4.2 min", "tone": "neutral"},
         ]},
        {"id": "vendor", "name": "Vendor Agent",        "use_case": "Non-PO MSA Validation · UC3",
         "accent": "#059669", "badge": "Active", "badge_tone": "green", "doc_count": 203,
         "starred": False,
         "metrics": [
             {"label": "MSA Coverage",   "value": "100%", "tone": "good"},
             {"label": "HITL Queue",     "value": "1 pending", "tone": "warn"},
             {"label": "Audit Findings", "value": "0 this month", "tone": "good"},
         ]},
        {"id": "quote", "name": "Quote Agent",          "use_case": "Engineering Quote Processing · UC4",
         "accent": "#d97706", "badge": "Pilot", "badge_tone": "amber", "doc_count": 47,
         "starred": False,
         "metrics": [
             {"label": "Accuracy",        "value": "88.4%", "tone": "good"},
             {"label": "HITL Queue",      "value": "1 pending", "tone": "warn"},
             {"label": "Avg Decisioning", "value": "2.1 days", "tone": "neutral"},
         ]},
        {"id": "tariff", "name": "Tariff Agent",        "use_case": "Pipeline Tariff Sheet Intelligence · UC5",
         "accent": "#f59e0b", "badge": "Active", "badge_tone": "green", "doc_count": 312,
         "starred": True,
         "metrics": [
             {"label": "FERC Filings Indexed", "value": "18 pipelines", "tone": "good"},
             {"label": "Rate Drift Alerts",    "value": "3 active", "tone": "bad"},
             {"label": "Revenue Protected",    "value": "$840K MTD", "tone": "neutral"},
         ]},
        {"id": "jib", "name": "JIB Agent",              "use_case": "JIB Statement Reconciliation · UC6",
         "accent": "#2563eb", "badge": "Active", "badge_tone": "green", "doc_count": 28,
         "starred": True,
         "metrics": [
             {"label": "AFE Match Rate",  "value": "96.4%", "tone": "good"},
             {"label": "Overrun Flags",   "value": "2 active", "tone": "bad"},
             {"label": "JV Partners",     "value": "4 operators", "tone": "neutral"},
         ]},
    ]
    invoice_total = next(a["doc_count"] for a in agents if a["id"] == "invoice")
    po_total      = next(a["doc_count"] for a in agents if a["id"] == "po")
    other_total   = sum(a["doc_count"] for a in agents if a["id"] not in {"invoice", "po"})

    # ── POC Phase Tracker ───────────────────────────────────────────
    phases = [
        {"id": 1, "name": "Invoice Intel",  "use_case": "UC1", "status": "live",
         "gradient": "linear-gradient(135deg,#0f4c81,#1a6db5)"},
        {"id": 2, "name": "PO Validation",  "use_case": "UC2", "status": "live",
         "gradient": "linear-gradient(135deg,#5b21b6,#7c3aed)"},
        {"id": 3, "name": "Non-PO MSA",     "use_case": "UC3", "status": "live",
         "gradient": "linear-gradient(135deg,#065f46,#059669)"},
        {"id": 4, "name": "Eng. Quote",     "use_case": "UC4", "status": "live",
         "gradient": "linear-gradient(135deg,#92400e,#d97706)"},
        {"id": 5, "name": "Tariff",         "use_case": "UC5", "status": "live", "starred": True,
         "gradient": "linear-gradient(135deg,#b45309,#f59e0b)"},
        {"id": 6, "name": "JIB",            "use_case": "UC6", "status": "live", "starred": True,
         "gradient": "linear-gradient(135deg,#1e3a5f,#2563eb)"},
    ]

    # ── Tariff Diff Viewer (wow visual) ────────────────────────────
    tariff_diff = {
        "header": {
            "subtitle": "FERC filed rate vs. shipper billed rate · Texas Eastern",
            "chip":     "Drift Detected",
        },
        "ferc": {
            "label":         "FERC Filed Rate",
            "tariff_sheet":  "FERC-TETCO-2026-04",
            "effective":     "April 1, 2026",
            "zone":          "South-to-North",
            "rate_value":    0.2847,
            "rate_display":  "$0.2847",
            "unit":          "/Dth",
        },
        "invoice": {
            "label":         "Shipper Billed Rate",
            "invoice_id":    "INV-TETCO-2026-0412",
            "gas_day":       "May 15, 2026",
            "zone":          "South-to-North",
            "rate_value":    0.3012,
            "rate_display":  "$0.3012",
            "unit":          "/Dth",
        },
        "diff_lines": [
            {"kind": "context", "text": "--- FERC-TETCO-2026-04 (Effective Apr 1, 2026)"},
            {"kind": "context", "text": "+++ INV-TETCO-2026-0412 (Gas Day May 15, 2026)"},
            {"kind": "context", "text": "@@ Zone: South-to-North · Firm Transportation @@"},
            {"kind": "context", "text": " Commodity Charge:    $0.0000/Dth"},
            {"kind": "removed", "text": "- Reservation Charge: $0.2847/Dth"},
            {"kind": "added",   "text": "+ Reservation Charge: $0.3012/Dth  ← +5.8% OVER FERC FILED RATE"},
            {"kind": "context", "text": " Fuel Retention:      1.42%"},
            {"kind": "context", "text": " ACA Surcharge:       $0.0004/Dth"},
        ],
        "impact": {
            "lines_affected":  312,
            "avg_dth_per_day": 8400,
            "days":            30,
            "monthly_exposure_usd": 840_000,
        },
        "kpis": [
            {"label": "Rate Drift",       "value": "+5.8%",  "tone": "bad"},
            {"label": "Affected Lines",   "value": "312",    "tone": "warn"},
            {"label": "Monthly Exposure", "value": "$840K",  "tone": "bad"},
        ],
    }

    # ── JIB AFE Reconciliation table ───────────────────────────────
    jib_reconciliation = {
        "rows": [
            {"jv":            "Sweeny Hub JV",
             "operator":      "Phillips 66",
             "afe":           "AFE-2024-0882",
             "approved_usd":  1_850_000,
             "charged_usd":   2_100_000,
             "variance_usd":   250_000,
             "status":        "OVERRUN",
             "tone":          "bad",
             "pct_of_afe":    113},
            {"jv":            "Mont Belvieu JV",
             "operator":      "Targa Resources",
             "afe":           "AFE-2025-0341",
             "approved_usd":  4_200_000,
             "charged_usd":   4_618_000,
             "variance_usd":   418_000,
             "status":        "OVERRUN",
             "tone":          "bad",
             "pct_of_afe":    110},
            {"jv":            "Permian Basin Expansion",
             "operator":      "EPROD Operated",
             "afe":           "AFE-2025-1104",
             "approved_usd":  12_400_000,
             "charged_usd":   11_680_000,
             "variance_usd":  -720_000,
             "status":        "ON TRACK",
             "tone":          "good",
             "pct_of_afe":    94},
            {"jv":            "Midland Basin Pipeline",
             "operator":      "EPROD Operated",
             "afe":           "AFE-2026-0044",
             "approved_usd":  3_100_000,
             "charged_usd":   3_089_000,
             "variance_usd":   -11_000,
             "status":        "ON TRACK",
             "tone":          "good",
             "pct_of_afe":    99},
        ],
        "callout": {
            "tone": "bad",
            "text": "2 JV overruns totaling $668,000 require additional AFE approval or dispute resolution with operators",
        },
    }

    # ── Live processing feed (terminal-style) ──────────────────────
    feed = [
        {"time": "09:47:22", "agent": "Invoice Agent", "agent_tone": "blue",
         "doc_id": "INV-2026-04472", "detail": "Schlumberger · $98,400 · PDF native",
         "status": "EXTRACTED", "status_tone": "good", "trailer": "conf:96.2%"},
        {"time": "09:47:19", "agent": "Tariff Agent",  "agent_tone": "amber",
         "doc_id": "FERC-TETCO-2026-07", "detail": "Texas Eastern · Effective Jul 1",
         "status": "INDEXED", "status_tone": "warn", "trailer": "18 rate lines"},
        {"time": "09:47:15", "agent": "Invoice Agent", "agent_tone": "blue",
         "doc_id": "INV-2026-04471", "detail": "Halliburton · $184.50/hr billed vs $172.00/hr MSA",
         "status": "FLAGGED", "status_tone": "bad", "trailer": "HITL routed"},
        {"time": "09:47:08", "agent": "JIB Agent", "agent_tone": "cyan",
         "doc_id": "JIB-SWEENY-MAY26", "detail": "Phillips 66 Sweeny · $2.1M vs AFE $1.85M",
         "status": "OVERRUN", "status_tone": "bad", "trailer": "+$250K flagged"},
        {"time": "09:47:01", "agent": "PO Agent", "agent_tone": "purple",
         "doc_id": "PO-2026-08812", "detail": "Baker Hughes · Tax code TX-E vs TX-I",
         "status": "EXCEPTION", "status_tone": "warn", "trailer": "$12,400 diff"},
        {"time": "09:46:55", "agent": "Vendor Agent", "agent_tone": "green",
         "doc_id": "NON-PO-2026-0814", "detail": "Exterran Corp · MSA-2024-0441 validated",
         "status": "APPROVED", "status_tone": "good", "trailer": "conf:88.1%"},
        {"time": "09:46:48", "agent": "Tariff Agent", "agent_tone": "amber",
         "doc_id": "DRIFT-ALERT", "detail": "Texas Eastern · Billed $0.3012 vs FERC $0.2847",
         "status": "DRIFT +5.8%", "status_tone": "bad", "trailer": "HITL routed"},
        {"time": "09:46:41", "agent": "Invoice Agent", "agent_tone": "blue",
         "doc_id": "INV-2026-04470", "detail": "Weatherford · $56,200 · scanned PDF",
         "status": "APPROVED", "status_tone": "good", "trailer": "conf:91.4%"},
        {"time": "09:46:34", "agent": "PO Agent", "agent_tone": "purple",
         "doc_id": "PO-2026-08811", "detail": "Cameron Int'l · $204,000 · contract match",
         "status": "VALIDATED", "status_tone": "good", "trailer": "conf:94.8%"},
        {"time": "09:46:27", "agent": "JIB Agent", "agent_tone": "cyan",
         "doc_id": "JIB-TARGA-MAY26", "detail": "Targa Resources · Mont Belvieu JV · 4 AFEs matched",
         "status": "RECONCILED", "status_tone": "good", "trailer": ""},
        {"time": "09:46:20", "agent": "Invoice Agent", "agent_tone": "blue",
         "doc_id": "INV-2026-04469", "detail": "Archrock Services · $33,800 · XLSX format",
         "status": "APPROVED", "status_tone": "good", "trailer": "conf:89.7%"},
        {"time": "09:46:13", "agent": "Quote Agent", "agent_tone": "amber",
         "doc_id": "QUOTE-2026-0041", "detail": "Exterran Corp · scope language ambiguous",
         "status": "REVIEW", "status_tone": "warn", "trailer": "conf:74.2%"},
        {"time": "09:46:06", "agent": "Tariff Agent", "agent_tone": "amber",
         "doc_id": "FERC-PANHANDLE-2026-07", "detail": "Panhandle Eastern · PPI-FG index update",
         "status": "FORECAST", "status_tone": "warn", "trailer": "+3.2% projected"},
        {"time": "09:45:59", "agent": "Vendor Agent", "agent_tone": "green",
         "doc_id": "NON-PO-2026-0813", "detail": "SLB · Engineering services · MSA-2025-0112",
         "status": "APPROVED", "status_tone": "good", "trailer": ""},
        {"time": "09:45:52", "agent": "Invoice Agent", "agent_tone": "blue",
         "doc_id": "INV-2026-04468", "detail": "Schlumberger · $142,800 · rate validated against MSA",
         "status": "APPROVED", "status_tone": "good", "trailer": ""},
    ]

    # ── Signal hero stats (for Apex Signal page) ───────────────────
    signal_hero = {
        "active_alerts":      1,
        "forecasts":          2,
        "contracts_at_risk":  8,
        "protected_mtd_usd":  2_400_000,
    }

    return {
        "generated_at":   now.isoformat().replace("+00:00", "Z"),
        "kpis":           kpis,
        "agents":         agents,
        "agent_totals":   {
            "doc_count_total":   sum(a["doc_count"] for a in agents),
            "invoices_30d":      invoice_total,
            "pos_30d":           po_total,
            "other_30d":         other_total,
            "agents_live":       sum(1 for a in agents if a["badge"] == "Active"),
        },
        "throughput_30d":      throughput_30d,
        "throughput_14d":      throughput_14d,
        "throughput_summary": {
            "docs_30d_total":    docs_30d_total,
            "avg_docs_per_day":  159,
            "auto_approved_pct": 91.8,
            "hitl_routed_pct":   8.2,
            "vs_prior_pct":      23,
        },
        "phases":              phases,
        "tariff_diff":         tariff_diff,
        "jib_reconciliation":  jib_reconciliation,
        "processing_feed":     feed,
        "signal_hero":         signal_hero,
        "agent_impact": [
            {"agent_id": "invoice",
             "name":     "Invoice Agent",
             "metric":   "Review time per invoice",
             "before":   "45 min manual",
             "after":    "11 min · APEX-assisted",
             "delta":    "75% faster",
             "annual_savings_usd": 1_240_000,
             "context":  "Halliburton/Schlumberger/Baker Hughes invoices · 1,247 processed in May"},
            {"agent_id": "po",
             "name":     "PO Agent",
             "metric":   "Rate validation coverage",
             "before":   "10–30% spot-check sampling",
             "after":    "100% automated coverage",
             "delta":    "Pre-pay catch vs post-pay audit",
             "annual_savings_usd": 890_000,
             "context":  "MSA scope + rate variance + tax codes on 389 POs"},
            {"agent_id": "vendor",
             "name":     "Vendor Agent",
             "metric":   "Non-PO MSA validation",
             "before":   "Inconsistent / often skipped",
             "after":    "100% at-intake with audit evidence",
             "delta":    "Audit findings 0 this month",
             "annual_savings_usd": 410_000,
             "context":  "203 non-PO transactions validated against active MSAs"},
            {"agent_id": "quote",
             "name":     "Quote Agent",
             "metric":   "Quote decisioning cycle",
             "before":   "5–7 days manual",
             "after":    "2.1 days · APEX comparative report",
             "delta":    "62% faster procurement decisions",
             "annual_savings_usd": 320_000,
             "context":  "Fluor/Bechtel/Emerson engineering quotes vs 12-mo historical"},
            {"agent_id": "tariff",
             "name":     "Tariff Agent",
             "metric":   "FERC tariff variance detection",
             "before":   "Detected at audit · weeks-to-months",
             "after":    "Detected at invoice · minutes",
             "delta":    "$840K/month exposure prevented",
             "annual_savings_usd": 10_080_000,
             "context":  "18 FERC pipelines · 312 tariff lines · gas-day-effective rate enforcement",
             "starred":  True},
            {"agent_id": "jib",
             "name":     "JIB Agent",
             "metric":   "AFE overrun detection",
             "before":   "Manual reconcile · monthly close lag",
             "after":    "Daily flag · working-interest math + AFE bounds",
             "delta":    "$668K overruns surfaced pre-close (May 2026)",
             "annual_savings_usd": 8_400_000,
             "context":  "Phillips 66 Sweeny + Targa Mont Belvieu + 2 EPROD-operated AFEs",
             "starred":  True},
        ],
        "agent_impact_summary": {
            "total_annual_savings_usd": 21_340_000,
            "avg_cycle_time_reduction_pct": 68,
            "audit_findings_avoided":      0,
        },
    }
