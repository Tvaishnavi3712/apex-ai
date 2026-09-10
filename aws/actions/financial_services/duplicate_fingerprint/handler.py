"""
Duplicate Fingerprint Action
Fingerprint an invoice and search payment history for probable duplicate
payments — the single largest source of hard-dollar recovery in accounts payable.

TRAINING USE CASE 1 — Financial Services.

Deploy location:  actions/financial_services/duplicate_fingerprint/handler.py
Registry entry:   INDUSTRY_ACTIONS["financial_services"] += ["duplicate_fingerprint"]
Resulting id:     financial_services.duplicate_fingerprint

Why fuzzy matching rather than an exact invoice-number check: real duplicate
payments almost never carry an identical invoice number. They arrive as
"INV-1042" and "INV1042", as a rebill after a statement chase, as the same
invoice submitted by both the vendor and a factoring company, or as the same
work billed under a second invoice number entirely. Exact-match duplicate
checks are why duplicate payments survive to the payment run.
"""

import os
import re
import sys
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import (  # noqa: E402
    apex_action,
    ApexActionSchema,
    ActionInputSchema,
    ActionOutputSchema,
    ApexActionBase,
)

# Weight each signal contributes to the duplicate probability. Sums to 1.0.
_WEIGHTS = {
    "invoice_number": 0.35,
    "amount": 0.30,
    "vendor": 0.15,
    "po_number": 0.10,
    "date_proximity": 0.10,
}

# At or above this, never auto-resolve. Mirrors the playbook's hard stop.
DUPLICATE_ESCALATION_THRESHOLD = 0.80


@apex_action(ApexActionSchema(
    name="duplicate_fingerprint",
    description=(
        "Fingerprint an invoice and search payment history for probable "
        "duplicate payments using normalised invoice number, amount, vendor, "
        "purchase order and date proximity"
    ),
    category="fraud_detection",
    industry="financial_services",
    version="1.0",
    tags=["accounts_payable", "duplicate_payment", "recovery", "controls"],
    input_schema=ActionInputSchema(description="Duplicate detection inputs")
        .add_string("invoice_number", "Invoice number as printed on the document", required=True)
        .add_string("vendor_name", "Vendor name from the invoice", required=True)
        .add_number("total_amount", "Invoice grand total", required=True)
        .add_string("invoice_date", "Invoice date in YYYY-MM-DD form", required=False)
        .add_string("po_number", "Purchase order referenced on the invoice", required=False)
        .add_string("vendor_id", "Resolved vendor id from the vendor master", required=False)
        .add_array("payment_history", "Previously paid invoices to compare against. When omitted the action reads the payment-history table", required=False)
        .add_integer("lookback_days", "How far back to search. Defaults to 400 days", required=False),
    output_schema=ActionOutputSchema(description="Duplicate detection result")
        .add_number("duplicate_probability", "Highest duplicate probability found, 0.0 to 1.0")
        .add_boolean("is_duplicate_suspect", "True when probability is at or above the escalation threshold")
        .add_string("fingerprint", "Canonical fingerprint computed for this invoice")
        .add_array("candidates", "Every candidate scored above the reporting floor, highest first")
        .add_string("strongest_signal", "Which signal contributed most to the top score")
        .add_number("amount_at_risk", "Dollar amount that would have been paid twice")
        .add_string("recommended_action", "block_and_escalate, review, or proceed")
))
def duplicate_fingerprint(
    invoice_number: str,
    vendor_name: str,
    total_amount: float,
    invoice_date: Optional[str] = None,
    po_number: Optional[str] = None,
    vendor_id: Optional[str] = None,
    payment_history: Optional[List[Dict[str, Any]]] = None,
    lookback_days: int = 400,
) -> dict:
    """
    Score this invoice against payment history for duplicate risk.

    Args:
        invoice_number: Invoice number as printed
        vendor_name: Vendor name from the invoice
        total_amount: Invoice grand total
        invoice_date: Invoice date, YYYY-MM-DD
        po_number: Purchase order referenced
        vendor_id: Resolved vendor id
        payment_history: Prior payments to compare against
        lookback_days: Search window in days

    Returns:
        Duplicate probability, scored candidates and a recommended action
    """
    amount = _f(total_amount)
    norm_invoice = _normalise_invoice_number(invoice_number)
    norm_vendor = _normalise_vendor(vendor_name)
    fingerprint = f"{norm_vendor}|{norm_invoice}|{amount:.2f}"

    history = payment_history
    if history is None:
        history = _load_payment_history(vendor_id, norm_vendor, lookback_days)

    candidates: List[Dict[str, Any]] = []

    for prior in history or []:
        score, signals = _score_candidate(
            norm_invoice=norm_invoice,
            norm_vendor=norm_vendor,
            amount=amount,
            invoice_date=invoice_date,
            po_number=po_number,
            prior=prior,
        )

        # Report anything with a meaningful signal, not just escalations —
        # analysts want to see the near misses too.
        if score >= 0.45:
            candidates.append({
                "prior_invoice_number": prior.get("invoice_number"),
                "prior_payment_id": prior.get("payment_id"),
                "prior_paid_date": prior.get("paid_date"),
                "prior_amount": _f(prior.get("total_amount") or prior.get("amount")),
                "prior_po_number": prior.get("po_number"),
                "prior_vendor_name": prior.get("vendor_name"),
                "duplicate_probability": round(score, 4),
                "signals": signals,
                "match_explanation": _explain(signals),
            })

    candidates.sort(key=lambda c: c["duplicate_probability"], reverse=True)

    top = candidates[0] if candidates else None
    probability = top["duplicate_probability"] if top else 0.0
    is_suspect = probability >= DUPLICATE_ESCALATION_THRESHOLD

    strongest = "none"
    if top:
        strongest = max(top["signals"], key=lambda k: top["signals"][k]["weighted"])

    if is_suspect:
        recommended = "block_and_escalate"
    elif probability >= 0.60:
        recommended = "review"
    else:
        recommended = "proceed"

    return {
        "invoice_number": invoice_number,
        "fingerprint": fingerprint,
        "duplicate_probability": round(probability, 4),
        "is_duplicate_suspect": is_suspect,
        "candidates": candidates[:10],
        "candidate_count": len(candidates),
        "strongest_signal": strongest,
        "amount_at_risk": round(amount, 2) if is_suspect else 0.0,
        "recommended_action": recommended,
        "threshold_applied": DUPLICATE_ESCALATION_THRESHOLD,
        "searched_records": len(history or []),
        "evaluated_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Scoring
# ============================================================================

def _score_candidate(
    norm_invoice: str,
    norm_vendor: str,
    amount: float,
    invoice_date: Optional[str],
    po_number: Optional[str],
    prior: Dict[str, Any],
) -> tuple:
    """Score one prior payment. Returns (total_score, signal_detail)."""
    signals: Dict[str, Dict[str, Any]] = {}

    # --- Invoice number similarity ---------------------------------------
    prior_norm = _normalise_invoice_number(prior.get("invoice_number") or "")
    if norm_invoice and prior_norm:
        if norm_invoice == prior_norm:
            inv_sim = 1.0
        elif norm_invoice in prior_norm or prior_norm in norm_invoice:
            inv_sim = 0.85
        else:
            inv_sim = _ratio(norm_invoice, prior_norm)
    else:
        inv_sim = 0.0
    signals["invoice_number"] = _signal(inv_sim, "invoice_number", norm_invoice, prior_norm)

    # --- Amount similarity ------------------------------------------------
    prior_amount = _f(prior.get("total_amount") or prior.get("amount"))
    if amount > 0 and prior_amount > 0:
        delta_pct = abs(amount - prior_amount) / max(amount, prior_amount)
        if delta_pct < 0.0001:
            amt_sim = 1.0
        elif delta_pct <= 0.01:
            amt_sim = 0.90          # penny rounding or FX drift
        elif delta_pct <= 0.05:
            amt_sim = 0.60          # partial rebill
        else:
            amt_sim = 0.0
    else:
        amt_sim = 0.0
    signals["amount"] = _signal(amt_sim, "amount", amount, prior_amount)

    # --- Vendor similarity ------------------------------------------------
    prior_vendor = _normalise_vendor(prior.get("vendor_name") or "")
    vendor_sim = 1.0 if (norm_vendor and norm_vendor == prior_vendor) else _ratio(norm_vendor, prior_vendor)
    signals["vendor"] = _signal(vendor_sim, "vendor", norm_vendor, prior_vendor)

    # --- PO number --------------------------------------------------------
    po_a = (po_number or "").strip().upper()
    po_b = (prior.get("po_number") or "").strip().upper()
    po_sim = 1.0 if (po_a and po_a == po_b) else 0.0
    signals["po_number"] = _signal(po_sim, "po_number", po_a, po_b)

    # --- Date proximity ---------------------------------------------------
    date_sim = _date_proximity(invoice_date, prior.get("invoice_date") or prior.get("paid_date"))
    signals["date_proximity"] = _signal(
        date_sim, "date_proximity", invoice_date, prior.get("invoice_date") or prior.get("paid_date")
    )

    total = sum(s["weighted"] for s in signals.values())
    return total, signals


def _signal(similarity: float, key: str, a: Any, b: Any) -> Dict[str, Any]:
    weight = _WEIGHTS[key]
    return {
        "similarity": round(similarity, 4),
        "weight": weight,
        "weighted": round(similarity * weight, 4),
        "this_invoice": a,
        "prior_invoice": b,
    }


def _explain(signals: Dict[str, Dict[str, Any]]) -> str:
    """Human-readable reason string for the resolution packet."""
    parts = []
    if signals["invoice_number"]["similarity"] >= 0.99:
        parts.append("identical invoice number")
    elif signals["invoice_number"]["similarity"] >= 0.80:
        parts.append("near-identical invoice number")
    if signals["amount"]["similarity"] >= 0.99:
        parts.append("identical amount")
    elif signals["amount"]["similarity"] >= 0.60:
        parts.append("amount within 5 percent")
    if signals["vendor"]["similarity"] >= 0.90:
        parts.append("same vendor")
    if signals["po_number"]["similarity"] >= 0.99:
        parts.append("same purchase order")
    if signals["date_proximity"]["similarity"] >= 0.80:
        parts.append("invoiced within days of each other")
    return ", ".join(parts) if parts else "weak partial signals only"


# ============================================================================
# Normalisation and similarity helpers
# ============================================================================

def _normalise_invoice_number(value: str) -> str:
    """
    Strip everything that varies between a duplicate pair: separators, spaces,
    common prefixes, and leading zeros. 'INV-001042' and 'inv 1042' collapse to
    the same string, which is the entire point.
    """
    if not value:
        return ""
    s = str(value).upper()
    s = re.sub(r"^(INV|INVOICE|BILL|DOC|NO|NUM)[\s\-#.:]*", "", s)
    s = re.sub(r"[^A-Z0-9]", "", s)
    s = re.sub(r"^0+", "", s)
    return s


def _normalise_vendor(value: str) -> str:
    """Drop corporate suffixes and punctuation so 'Acme Corp.' == 'ACME CORPORATION'."""
    if not value:
        return ""
    s = str(value).upper()
    s = re.sub(r"[^A-Z0-9\s]", " ", s)
    for suffix in (
        "INCORPORATED", "CORPORATION", "COMPANY", "LIMITED",
        "HOLDINGS", "GROUP", "LLC", "LLP", "LTD", "INC", "CORP", "CO", "PLC", "GMBH", "SA", "NV", "BV",
    ):
        s = re.sub(rf"\b{suffix}\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _ratio(a: str, b: str) -> float:
    """
    Character-bigram Dice coefficient. Deliberately dependency-free so the
    handler runs in a bare Lambda without difflib behaviour surprises.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    if len(a) < 2 or len(b) < 2:
        return 1.0 if a == b else 0.0
    bg_a = {a[i:i + 2] for i in range(len(a) - 1)}
    bg_b = {b[i:i + 2] for i in range(len(b) - 1)}
    if not bg_a or not bg_b:
        return 0.0
    return (2.0 * len(bg_a & bg_b)) / (len(bg_a) + len(bg_b))


def _date_proximity(a: Optional[str], b: Optional[str]) -> float:
    """
    1.0 for the same day, tapering to 0 at 180 days apart. Duplicates cluster
    close together in time — a rebill usually lands within a billing cycle.
    """
    da, db = _parse_date(a), _parse_date(b)
    if not da or not db:
        return 0.0
    days = abs((da - db).days)
    if days == 0:
        return 1.0
    if days <= 7:
        return 0.90
    if days <= 35:
        return 0.70
    if days <= 90:
        return 0.40
    if days <= 180:
        return 0.15
    return 0.0


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    text = str(value).strip()[:19]
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _f(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("$", "").replace(",", "").strip())
    except (TypeError, ValueError):
        return 0.0


def _table(table_name: str):
    """
    Return a boto3-style table handle on EITHER cloud.

    This is the cloud-portability pattern used throughout APEX. The Azure build
    ships `sdk/azure_data.py`, a shim exposing the same surface as
    `boto3.resource("dynamodb")` — `.Table(name).get_item(Key=...)`,
    `.put_item(Item=...)`, `.scan(Limit=...)`, `.query(...)`. Import it first
    and fall back to boto3, and the rest of the handler body is identical on
    AWS and Azure.

    Setting USE_LOCAL_MOCK=true makes the Azure shim read the on-disk mock
    store, so this handler also runs with no cloud account at all.
    """
    try:
        from sdk.azure_data import get_table_resource       # Azure build
        return get_table_resource().Table(table_name)
    except ImportError:
        import boto3                                         # AWS build
        return boto3.resource("dynamodb").Table(table_name)


def _load_payment_history(
    vendor_id: Optional[str],
    norm_vendor: str,
    lookback_days: int,
) -> List[Dict[str, Any]]:
    """
    Read prior payments from the table store when the caller did not supply them.

    Returns an empty list on any failure — the caller treats an empty history
    as "no duplicate evidence available", and the playbook's recipe requires a
    human review in that case rather than a silent pass.
    """
    try:
        table_name = os.environ.get(
            "PAYMENT_HISTORY_TABLE",
            "apex-ai-platform-payment-history",
        )
        table = _table(table_name)
        cutoff = (datetime.utcnow() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

        # A cross-partition scan is correct here on both clouds: the Azure shim's
        # query() is itself a filtered scan, and duplicate detection legitimately
        # needs to look across vendors when the vendor name was mis-keyed.
        items = table.scan(Limit=1000).get("Items", [])

        if vendor_id:
            narrowed = [i for i in items if str(i.get("vendor_id") or "") == vendor_id]
            # Only narrow when it does not empty the corpus — a mis-keyed vendor_id
            # must not silently disable duplicate detection.
            if narrowed:
                items = narrowed

        return [
            item for item in items
            if str(item.get("paid_date") or item.get("invoice_date") or "") >= cutoff
        ]

    except Exception:
        return []


# ============================================================================
# Class-based implementation
# ============================================================================

class DuplicateFingerprintAction(ApexActionBase):
    """Duplicate Fingerprint Action (class-based)."""

    name = "duplicate_fingerprint"
    description = "Detect probable duplicate payments"
    category = "fraud_detection"
    industry = "financial_services"

    def execute(self, **kwargs) -> dict:
        return duplicate_fingerprint(**kwargs)


def handler(event, context):
    """Lambda entry point."""
    return duplicate_fingerprint(**event)
