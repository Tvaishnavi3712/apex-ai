"""
Three-Way Match Action
Compare an invoice against its purchase order and goods receipt, line by line,
and return every variance found.

TRAINING USE CASE 1 — Financial Services.

Deploy location:  actions/financial_services/three_way_match/handler.py
Registry entry:   backend/services/action_registry.py
                  INDUSTRY_ACTIONS["financial_services"] += ["three_way_match"]
Resulting id:     financial_services.three_way_match

The registry discovers this file by walking
actions/<industry>/<action_name>/handler.py for every (industry, action_name)
pair listed in INDUSTRY_ACTIONS. If the name is not in that dict this file is
never looked at, no matter that it exists on disk.
"""

import os
import sys
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, List, Optional

# The SDK lives two levels up from actions/<industry>/<action>/handler.py.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import (  # noqa: E402
    apex_action,
    ApexActionSchema,
    ActionInputSchema,
    ActionOutputSchema,
    ApexActionBase,
)


# Variance severity ranking. Used to decide which exception wins when an
# invoice carries several at once.
_SEVERITY_RANK = {
    "info": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@apex_action(ApexActionSchema(
    name="three_way_match",
    description=(
        "Compare an invoice against its purchase order and goods receipt line "
        "by line and return every price, quantity, freight and tax variance"
    ),
    category="matching",
    industry="financial_services",
    version="1.0",
    tags=["accounts_payable", "three_way_match", "exception_management"],
    input_schema=ActionInputSchema(description="Three-way match inputs")
        .add_string("invoice_number", "Invoice number being matched", required=True)
        .add_string("po_number", "Purchase order number to match against", required=True)
        .add_array("invoice_lines", "Invoice line items from the blueprint extraction", required=True)
        .add_array("po_lines", "Purchase order line items from the PO system", required=True)
        .add_array("receipt_lines", "Goods receipt line items, empty for a two-way match", required=False)
        .add_number("invoice_freight", "Freight charged on the invoice", required=False)
        .add_number("po_freight", "Freight allowed on the purchase order", required=False)
        .add_number("invoice_tax", "Tax charged on the invoice", required=False)
        .add_number("expected_tax_rate", "Expected tax rate as a decimal, e.g. 0.0825", required=False)
        .add_string("match_basis", "two_way or three_way. Defaults to three_way when receipt lines are supplied", required=False),
    output_schema=ActionOutputSchema(description="Three-way match result")
        .add_boolean("matched", "True when no variances were found at all")
        .add_string("match_basis", "The basis actually used: two_way or three_way")
        .add_array("variances", "Every variance found, one entry per finding")
        .add_string("worst_severity", "Highest severity across all variances")
        .add_number("total_variance_amount", "Net dollar impact of all variances combined")
        .add_number("lines_matched", "Count of invoice lines that matched cleanly")
        .add_number("lines_with_variance", "Count of invoice lines carrying at least one variance")
        .add_array("unmatched_invoice_lines", "Invoice lines with no corresponding PO line")
        .add_array("unbilled_po_lines", "PO lines with no corresponding invoice line")
))
def three_way_match(
    invoice_number: str,
    po_number: str,
    invoice_lines: List[Dict[str, Any]],
    po_lines: List[Dict[str, Any]],
    receipt_lines: Optional[List[Dict[str, Any]]] = None,
    invoice_freight: float = 0.0,
    po_freight: float = 0.0,
    invoice_tax: float = 0.0,
    expected_tax_rate: Optional[float] = None,
    match_basis: Optional[str] = None,
) -> dict:
    """
    Run a three-way (or two-way) match and report every variance.

    Args:
        invoice_number: Invoice number being matched
        po_number: Purchase order number to match against
        invoice_lines: Invoice line items from blueprint extraction
        po_lines: Purchase order line items from the PO system
        receipt_lines: Goods receipt line items; omit for a two-way match
        invoice_freight: Freight charged on the invoice
        po_freight: Freight allowed on the purchase order
        invoice_tax: Tax charged on the invoice
        expected_tax_rate: Expected tax rate as a decimal
        match_basis: Force two_way or three_way

    Returns:
        Match result with a variance list, severity and dollar impact
    """
    receipt_lines = receipt_lines or []

    basis = match_basis or ("three_way" if receipt_lines else "two_way")

    variances: List[Dict[str, Any]] = []
    lines_matched = 0
    lines_with_variance = 0
    unmatched_invoice_lines: List[Dict[str, Any]] = []

    po_index = _index_lines(po_lines)
    receipt_index = _index_lines(receipt_lines)
    consumed_po_keys = set()

    for inv_line in invoice_lines:
        key = _match_key(inv_line)
        po_line = po_index.get(key)

        if po_line is None:
            po_line = _fuzzy_find(inv_line, po_lines, consumed_po_keys)

        if po_line is None:
            unmatched_invoice_lines.append({
                "line_number": inv_line.get("line_number"),
                "description": inv_line.get("description"),
                "sku": inv_line.get("sku"),
                "amount": _f(inv_line.get("amount")),
            })
            variances.append(_variance(
                code="PRICE_VAR",
                line_number=inv_line.get("line_number"),
                field="line_existence",
                reason="Invoice line has no corresponding purchase order line",
                invoice_value=_f(inv_line.get("amount")),
                reference_value=0.0,
                variance_amount=_f(inv_line.get("amount")),
                variance_percent=100.0,
                severity="high",
            ))
            lines_with_variance += 1
            continue

        consumed_po_keys.add(_match_key(po_line))
        line_variances: List[Dict[str, Any]] = []

        # --- Price variance: invoice unit price vs PO unit price -------------
        inv_price = _f(inv_line.get("unit_price"))
        po_price = _f(po_line.get("unit_price"))
        if po_price > 0 and abs(inv_price - po_price) >= 0.01:
            delta = inv_price - po_price
            qty = _f(inv_line.get("quantity")) or 1.0
            line_variances.append(_variance(
                code="PRICE_VAR",
                line_number=inv_line.get("line_number"),
                field="unit_price",
                reason=(
                    "Invoice unit price is above the purchase order price"
                    if delta > 0 else
                    "Invoice unit price is below the purchase order price"
                ),
                invoice_value=inv_price,
                reference_value=po_price,
                variance_amount=round(delta * qty, 2),
                variance_percent=round((delta / po_price) * 100.0, 2),
                severity="medium" if delta > 0 else "low",
            ))

        # --- Quantity variance: billed vs received (three-way) or ordered ----
        inv_qty = _f(inv_line.get("quantity"))
        if basis == "three_way":
            receipt_line = receipt_index.get(key) or _fuzzy_find(inv_line, receipt_lines, set())
            ref_qty = _f(receipt_line.get("quantity")) if receipt_line else 0.0
            ref_label = "quantity_received"
            if receipt_line is None:
                line_variances.append(_variance(
                    code="QTY_VAR",
                    line_number=inv_line.get("line_number"),
                    field="quantity_received",
                    reason="No goods receipt line found for this invoice line",
                    invoice_value=inv_qty,
                    reference_value=0.0,
                    variance_amount=round(inv_qty * inv_price, 2),
                    variance_percent=100.0,
                    severity="high",
                ))
                ref_qty = None
        else:
            ref_qty = _f(po_line.get("quantity"))
            ref_label = "quantity_ordered"

        if ref_qty is not None and ref_qty > 0 and abs(inv_qty - ref_qty) >= 0.001:
            delta_qty = inv_qty - ref_qty
            line_variances.append(_variance(
                code="QTY_VAR",
                line_number=inv_line.get("line_number"),
                field=ref_label,
                reason=(
                    "Quantity billed exceeds quantity on record"
                    if delta_qty > 0 else
                    "Quantity billed is less than quantity on record"
                ),
                invoice_value=inv_qty,
                reference_value=ref_qty,
                variance_amount=round(delta_qty * (po_price or inv_price), 2),
                variance_percent=round((delta_qty / ref_qty) * 100.0, 2),
                severity="high" if delta_qty > 0 else "info",
            ))

        # --- Line extension: does qty * price actually equal the amount? -----
        stated_amount = _f(inv_line.get("amount"))
        computed_amount = round(inv_qty * inv_price, 2)
        if stated_amount and abs(stated_amount - computed_amount) >= 0.01:
            line_variances.append(_variance(
                code="MATH_ERROR",
                line_number=inv_line.get("line_number"),
                field="amount",
                reason="Line amount does not equal quantity multiplied by unit price",
                invoice_value=stated_amount,
                reference_value=computed_amount,
                variance_amount=round(stated_amount - computed_amount, 2),
                variance_percent=(
                    round(((stated_amount - computed_amount) / computed_amount) * 100.0, 2)
                    if computed_amount else 100.0
                ),
                severity="medium",
            ))

        if line_variances:
            variances.extend(line_variances)
            lines_with_variance += 1
        else:
            lines_matched += 1

    # --- Header level: freight -------------------------------------------
    inv_freight = _f(invoice_freight)
    allowed_freight = _f(po_freight)
    if inv_freight > 0 and abs(inv_freight - allowed_freight) >= 0.01:
        variances.append(_variance(
            code="FREIGHT_UNMATCHED",
            line_number=None,
            field="freight_amount",
            reason=(
                "Freight charged on the invoice is not present on the purchase order"
                if allowed_freight == 0 else
                "Freight charged differs from the amount allowed on the purchase order"
            ),
            invoice_value=inv_freight,
            reference_value=allowed_freight,
            variance_amount=round(inv_freight - allowed_freight, 2),
            variance_percent=(
                round(((inv_freight - allowed_freight) / allowed_freight) * 100.0, 2)
                if allowed_freight else 100.0
            ),
            severity="low",
        ))

    # --- Header level: tax ------------------------------------------------
    inv_tax = _f(invoice_tax)
    if expected_tax_rate is not None:
        taxable_base = sum(_f(l.get("amount")) for l in invoice_lines)
        expected_tax = round(taxable_base * _f(expected_tax_rate), 2)
        if abs(inv_tax - expected_tax) >= 0.01:
            variances.append(_variance(
                code="TAX_VAR",
                line_number=None,
                field="tax_amount",
                reason="Tax charged does not match the expected jurisdiction rate",
                invoice_value=inv_tax,
                reference_value=expected_tax,
                variance_amount=round(inv_tax - expected_tax, 2),
                variance_percent=(
                    round(((inv_tax - expected_tax) / expected_tax) * 100.0, 2)
                    if expected_tax else 100.0
                ),
                severity="low",
            ))

    # --- PO lines never billed -------------------------------------------
    unbilled_po_lines = [
        {
            "line_number": l.get("line_number"),
            "description": l.get("description"),
            "sku": l.get("sku"),
            "amount": _f(l.get("amount")),
        }
        for l in po_lines
        if _match_key(l) not in consumed_po_keys
    ]

    worst = "info"
    for v in variances:
        if _SEVERITY_RANK.get(v["severity"], 0) > _SEVERITY_RANK.get(worst, 0):
            worst = v["severity"]

    return {
        "invoice_number": invoice_number,
        "po_number": po_number,
        "matched": len(variances) == 0,
        "match_basis": basis,
        "variances": variances,
        "worst_severity": worst if variances else "none",
        "total_variance_amount": round(sum(v["variance_amount"] for v in variances), 2),
        "lines_matched": lines_matched,
        "lines_with_variance": lines_with_variance,
        "unmatched_invoice_lines": unmatched_invoice_lines,
        "unbilled_po_lines": unbilled_po_lines,
        "matched_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Helpers
# ============================================================================

def _f(value: Any) -> float:
    """Coerce anything DynamoDB or a blueprint might hand us into a float."""
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


def _match_key(line: Dict[str, Any]) -> str:
    """
    Preferred join key for a line: SKU when present, else the PO line
    reference, else a normalised description.
    """
    sku = (line.get("sku") or "").strip().upper()
    if sku:
        return f"sku:{sku}"
    ref = (line.get("po_line_reference") or "").strip().upper()
    if ref:
        return f"ref:{ref}"
    desc = (line.get("description") or "").strip().lower()
    return f"desc:{desc[:60]}"


def _index_lines(lines: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build a lookup of match key to line. First occurrence wins."""
    index: Dict[str, Dict[str, Any]] = {}
    for line in lines or []:
        key = _match_key(line)
        index.setdefault(key, line)
    return index


def _fuzzy_find(
    needle: Dict[str, Any],
    haystack: List[Dict[str, Any]],
    exclude_keys: set,
) -> Optional[Dict[str, Any]]:
    """
    Fall back to a token-overlap match on description when the SKU and PO line
    reference are both absent. Requires at least half the tokens to overlap so
    unrelated lines are not paired.
    """
    target = set((needle.get("description") or "").lower().split())
    if not target:
        return None

    best = None
    best_score = 0.0
    for candidate in haystack or []:
        if _match_key(candidate) in exclude_keys:
            continue
        tokens = set((candidate.get("description") or "").lower().split())
        if not tokens:
            continue
        overlap = len(target & tokens) / float(len(target | tokens))
        if overlap > best_score:
            best_score = overlap
            best = candidate

    return best if best_score >= 0.5 else None


def _variance(
    code: str,
    line_number: Optional[int],
    field: str,
    reason: str,
    invoice_value: float,
    reference_value: float,
    variance_amount: float,
    variance_percent: float,
    severity: str,
) -> Dict[str, Any]:
    """Uniform variance record. Every consumer downstream relies on this shape."""
    return {
        "exception_code": code,
        "line_number": line_number,
        "field": field,
        "reason": reason,
        "invoice_value": invoice_value,
        "reference_value": reference_value,
        "variance_amount": variance_amount,
        "variance_percent": variance_percent,
        "severity": severity,
    }


# ============================================================================
# Class-based implementation, for parity with the platform's other handlers
# ============================================================================

class ThreeWayMatchAction(ApexActionBase):
    """Three-Way Match Action (class-based)."""

    name = "three_way_match"
    description = "Compare invoice against purchase order and goods receipt"
    category = "matching"
    industry = "financial_services"

    def execute(self, **kwargs) -> dict:
        return three_way_match(**kwargs)


# ============================================================================
# Lambda entry point.
# The registry's invoke path looks for a function named after the action first
# (`three_way_match`), then falls back to a function literally named `handler`.
# ============================================================================

def handler(event, context):
    """Lambda entry point."""
    return three_way_match(**event)
