"""
PO Reconcile - Small Factory
Reconciles invoice against purchase orders.
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

# Sample PO database (in production, this would be ERP/Cosmos DB)
PO_DATABASE = {
    "PO-2024-001": {
        "po_number": "PO-2024-001",
        "vendor_id": "VND-001",
        "status": "open",
        "total_amount": 5000.00,
        "received_amount": 0.00,
        "line_items": [
            {"item": "Office Supplies", "quantity": 100, "unit_price": 25.00, "total": 2500.00},
            {"item": "Printer Paper", "quantity": 50, "unit_price": 50.00, "total": 2500.00},
        ],
        "created_date": "2024-01-15",
        "expected_delivery": "2024-02-15",
    },
    "PO-2024-002": {
        "po_number": "PO-2024-002",
        "vendor_id": "VND-002",
        "status": "partial",
        "total_amount": 15000.00,
        "received_amount": 7500.00,
        "line_items": [
            {"item": "Laptop Computers", "quantity": 5, "unit_price": 1500.00, "total": 7500.00},
            {"item": "Monitors", "quantity": 10, "unit_price": 750.00, "total": 7500.00},
        ],
        "created_date": "2024-01-20",
        "expected_delivery": "2024-02-20",
    },
}


def find_po_by_number(po_number: str) -> Optional[Dict[str, Any]]:
    """Find PO by exact number."""
    # Normalize PO number
    po_number = po_number.upper().strip()
    return PO_DATABASE.get(po_number)


def find_po_by_vendor(vendor_id: str, amount: float, tolerance: float = 0.05) -> List[Dict[str, Any]]:
    """Find POs by vendor and approximate amount."""
    matches = []

    for po in PO_DATABASE.values():
        if po["vendor_id"] != vendor_id:
            continue
        if po["status"] == "closed":
            continue

        # Check amount within tolerance
        remaining = po["total_amount"] - po["received_amount"]
        if abs(remaining - amount) / max(remaining, 1) <= tolerance:
            matches.append(po)

    return matches


def calculate_variance(po: Dict[str, Any], invoice_amount: float) -> Dict[str, Any]:
    """Calculate variance between PO and invoice."""
    remaining = po["total_amount"] - po["received_amount"]
    variance = invoice_amount - remaining
    variance_pct = (variance / max(remaining, 1)) * 100

    return {
        "po_remaining": remaining,
        "invoice_amount": invoice_amount,
        "variance": round(variance, 2),
        "variance_percent": round(variance_pct, 2),
        "within_tolerance": abs(variance_pct) <= 5,  # 5% tolerance
    }


def reconcile_line_items(po_items: List[Dict], invoice_items: List[Dict]) -> Dict[str, Any]:
    """Reconcile line items between PO and invoice."""
    matched_items = []
    unmatched_po_items = []
    unmatched_invoice_items = list(invoice_items)

    for po_item in po_items:
        matched = False
        for i, inv_item in enumerate(unmatched_invoice_items):
            # Simple matching by description similarity
            po_desc = po_item.get("item", "").lower()
            inv_desc = inv_item.get("description", "").lower()

            if po_desc in inv_desc or inv_desc in po_desc:
                matched_items.append({
                    "po_item": po_item,
                    "invoice_item": inv_item,
                    "quantity_match": po_item.get("quantity") == inv_item.get("quantity"),
                    "price_match": abs(po_item.get("unit_price", 0) - inv_item.get("unit_price", 0)) < 0.01,
                })
                unmatched_invoice_items.pop(i)
                matched = True
                break

        if not matched:
            unmatched_po_items.append(po_item)

    return {
        "matched_items": matched_items,
        "unmatched_po_items": unmatched_po_items,
        "unmatched_invoice_items": unmatched_invoice_items,
        "full_match": len(unmatched_po_items) == 0 and len(unmatched_invoice_items) == 0,
    }


@register_factory("po_reconcile")
async def po_reconcile(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconcile invoice against purchase orders.

    Input:
        invoice_extract: Extracted invoice data
        vendor_match.vendor_id: Matched vendor ID
        config.tolerance: Amount variance tolerance
        config.require_po: Whether PO is required

    Output:
        reconciled: Whether invoice reconciled to PO
        po: Matched purchase order
        variance: Amount variance details
        line_item_match: Line item reconciliation
        approval_required: Whether manual approval needed
    """
    config = input_data.get('config', {})
    invoice = input_data.get('invoice_extract', {})
    vendor = input_data.get('vendor_match', {})

    tolerance = config.get('tolerance', 0.05)  # 5% default
    require_po = config.get('require_po', True)

    # Get invoice details
    invoice_amount = invoice.get('total_amount', 0) or invoice.get('total', 0)
    po_number = invoice.get('po_number', '') or invoice.get('purchase_order', '')
    invoice_items = invoice.get('line_items', [])
    vendor_id = vendor.get('vendor_id', '')

    matched_po = None
    match_method = None

    # Try to find PO
    if po_number:
        matched_po = find_po_by_number(po_number)
        if matched_po:
            match_method = "po_number"

    if not matched_po and vendor_id:
        candidates = find_po_by_vendor(vendor_id, invoice_amount, tolerance)
        if len(candidates) == 1:
            matched_po = candidates[0]
            match_method = "vendor_amount"
        elif len(candidates) > 1:
            # Multiple matches - need manual review
            return {
                "reconciled": False,
                "po": None,
                "match_candidates": [po["po_number"] for po in candidates],
                "variance": None,
                "approval_required": True,
                "reason": "multiple_po_matches",
                "action_required": "select_po",
            }

    if not matched_po:
        if require_po:
            return {
                "reconciled": False,
                "po": None,
                "variance": None,
                "approval_required": True,
                "reason": "no_po_found",
                "action_required": "create_po_or_approve",
                "invoice_amount": invoice_amount,
            }
        else:
            # Non-PO invoice - route for approval
            return {
                "reconciled": True,
                "po": None,
                "is_non_po_invoice": True,
                "variance": None,
                "approval_required": True,
                "reason": "non_po_invoice",
                "action_required": "manager_approval",
                "invoice_amount": invoice_amount,
            }

    # Calculate variance
    variance = calculate_variance(matched_po, invoice_amount)

    # Reconcile line items
    line_item_match = reconcile_line_items(matched_po.get("line_items", []), invoice_items)

    # Determine if approval required
    approval_required = (
        not variance["within_tolerance"] or
        not line_item_match["full_match"]
    )

    return {
        "reconciled": True,
        "po": matched_po,
        "po_number": matched_po["po_number"],
        "match_method": match_method,
        "variance": variance,
        "line_item_match": line_item_match,
        "approval_required": approval_required,
        "reason": None if not approval_required else "variance_or_mismatch",
        "action_required": "auto_approve" if not approval_required else "review_variance",
    }
