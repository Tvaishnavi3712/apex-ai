"""
Tolerance Policy Action
Apply the accounts-payable tolerance bands and routing matrix to a set of
variances and return a disposition: auto-resolve, route to a human, or reject.

TRAINING USE CASE 1 — Financial Services.

Deploy location:  actions/financial_services/tolerance_policy/handler.py
Registry entry:   INDUSTRY_ACTIONS["financial_services"] += ["tolerance_policy"]
Resulting id:     financial_services.tolerance_policy

This is the policy engine. The playbook's recipe explicitly tells the agent to
trust this action's disposition rather than reasoning about the bands itself.
That separation matters: policy lives in code where it is versioned, testable
and auditable, while the agent handles the judgement that policy cannot encode.
"""

import os
import sys
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import (  # noqa: E402
    apex_action,
    ApexActionSchema,
    ActionInputSchema,
    ActionOutputSchema,
    ApexActionBase,
)


# Default bands. Overridable per call so a tenant's playbook context block is
# the source of truth rather than this file.
DEFAULT_POLICY = {
    "price_variance_percent": 5.0,
    "price_variance_absolute_usd": 250.0,
    "quantity_variance_percent": 3.0,
    "freight_unmatched_max_usd": 250.0,
    "freight_unmatched_max_percent": 3.0,
    "tax_variance_max_usd": 500.0,
    "total_auto_resolve_ceiling_usd": 25000.0,
}

# Exception codes that can never auto-resolve, whatever the amount.
NEVER_AUTO_RESOLVE = {
    "DUP_SUSPECT",
    "REMIT_DRIFT",
    "VENDOR_UNKNOWN",
    "PO_CLOSED",
    "NO_PO",
    "NO_RECEIPT",
    "STALE_INVOICE",
}

# Who owns which exception, and how fast they must act.
ROUTING_MATRIX = {
    "PRICE_VAR":         {"role": "ap_specialist", "email": "ap-specialist@example.com",      "sla_hours": 8},
    "TAX_VAR":           {"role": "ap_specialist", "email": "ap-specialist@example.com",      "sla_hours": 8},
    "FREIGHT_UNMATCHED": {"role": "ap_specialist", "email": "ap-specialist@example.com",      "sla_hours": 8},
    "MATH_ERROR":        {"role": "ap_specialist", "email": "ap-specialist@example.com",      "sla_hours": 8},
    "QTY_VAR":           {"role": "buyer",         "email": "procurement@example.com",        "sla_hours": 24},
    "NO_PO":             {"role": "buyer",         "email": "procurement@example.com",        "sla_hours": 24},
    "PO_CLOSED":         {"role": "buyer",         "email": "procurement@example.com",        "sla_hours": 24},
    "NO_RECEIPT":        {"role": "buyer",         "email": "procurement@example.com",        "sla_hours": 24},
    "DUP_SUSPECT":       {"role": "ap_manager",    "email": "ap-manager@example.com",         "sla_hours": 4},
    "STALE_INVOICE":     {"role": "ap_manager",    "email": "ap-manager@example.com",         "sla_hours": 4},
    "REMIT_DRIFT":       {"role": "controls",      "email": "financial-controls@example.com", "sla_hours": 2},
    "VENDOR_UNKNOWN":    {"role": "controls",      "email": "financial-controls@example.com", "sla_hours": 2},
}

# GL accounts each auto-resolved variance type posts to.
VARIANCE_GL_ACCOUNTS = {
    "PRICE_VAR":         "6820-purchase-price-variance",
    "QTY_VAR":           "6825-quantity-variance",
    "FREIGHT_UNMATCHED": "6830-unplanned-freight",
    "TAX_VAR":           "2210-tax-accrual-adjustment",
}

_SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@apex_action(ApexActionSchema(
    name="tolerance_policy",
    description=(
        "Apply accounts-payable tolerance bands and the routing matrix to a set "
        "of variances and return a disposition of auto_resolve, route_to_human "
        "or reject, with the exact policy rule that drove the decision"
    ),
    category="policy_engine",
    industry="financial_services",
    version="1.0",
    tags=["accounts_payable", "tolerance", "policy", "routing", "auditability"],
    input_schema=ActionInputSchema(description="Tolerance policy inputs")
        .add_string("invoice_number", "Invoice number being dispositioned", required=True)
        .add_number("invoice_total", "Invoice grand total, used against the auto-resolve ceiling", required=True)
        .add_array("variances", "Variance records from three_way_match", required=True)
        .add_object("policy_overrides", "Tolerance band overrides from the playbook context block", required=False)
        .add_number("invoice_age_days", "Age of the invoice in days", required=False)
        .add_number("extraction_confidence", "Blueprint extraction confidence, 0.0 to 1.0", required=False)
        .add_number("duplicate_probability", "Duplicate probability from duplicate_fingerprint", required=False)
        .add_boolean("remit_drift_detected", "True when remit-to differs from the vendor master", required=False)
        .add_boolean("vendor_found", "False when the vendor is absent from the vendor master", required=False),
    output_schema=ActionOutputSchema(description="Disposition result")
        .add_string("disposition", "auto_resolve, route_to_human, or reject")
        .add_string("policy_rule_applied", "The named policy rule that produced this disposition")
        .add_string("primary_exception_code", "The exception code that drove routing")
        .add_string("assignee_role", "Role the exception is assigned to when human review is required")
        .add_string("assignee_email", "Email of the assignee")
        .add_number("sla_hours", "Hours allowed to resolve")
        .add_array("within_tolerance", "Variances that fell inside the bands")
        .add_array("outside_tolerance", "Variances that breached the bands")
        .add_array("gl_postings", "GL entries required to clear auto-resolved variances")
        .add_number("auto_resolved_amount", "Dollar value auto-resolved without human touch")
        .add_array("decision_trail", "Ordered list of every policy evaluation performed")
))
def tolerance_policy(
    invoice_number: str,
    invoice_total: float,
    variances: List[Dict[str, Any]],
    policy_overrides: Optional[Dict[str, Any]] = None,
    invoice_age_days: Optional[float] = None,
    extraction_confidence: Optional[float] = None,
    duplicate_probability: Optional[float] = None,
    remit_drift_detected: bool = False,
    vendor_found: bool = True,
) -> dict:
    """
    Decide the disposition for an invoice exception.

    Args:
        invoice_number: Invoice number being dispositioned
        invoice_total: Invoice grand total
        variances: Variance records from three_way_match
        policy_overrides: Tolerance band overrides from playbook context
        invoice_age_days: Age of the invoice in days
        extraction_confidence: Blueprint extraction confidence
        duplicate_probability: Probability from duplicate_fingerprint
        remit_drift_detected: True when remit-to differs from vendor master
        vendor_found: False when vendor is absent from the master

    Returns:
        Disposition, the policy rule applied, routing, GL postings and a
        full decision trail
    """
    policy = dict(DEFAULT_POLICY)
    if policy_overrides:
        for key, value in policy_overrides.items():
            if key in policy and value is not None:
                policy[key] = _f(value)

    total = _f(invoice_total)
    variances = variances or []
    trail: List[Dict[str, Any]] = []

    # ---------------------------------------------------------------------
    # Gate 1 — unconditional escalations, evaluated before any band maths.
    # These exist because the cost of a false negative is unbounded.
    # ---------------------------------------------------------------------
    if duplicate_probability is not None and _f(duplicate_probability) >= 0.80:
        trail.append(_step("hard_stop_duplicate", True,
                           f"duplicate_probability {_f(duplicate_probability):.2f} >= 0.80"))
        return _route(invoice_number, "DUP_SUSPECT", "hard_stop_duplicate",
                      variances, [], trail, total,
                      note="Suspected duplicate payment. Never auto-resolved.")

    if remit_drift_detected:
        trail.append(_step("hard_stop_remit_drift", True,
                           "remit-to party differs from the vendor master"))
        return _route(invoice_number, "REMIT_DRIFT", "hard_stop_remit_drift",
                      variances, [], trail, total,
                      note="Payment redirection risk. Financial Controls must clear.")

    if not vendor_found:
        trail.append(_step("hard_stop_vendor_unknown", True,
                           "vendor absent from the approved vendor master"))
        return _route(invoice_number, "VENDOR_UNKNOWN", "hard_stop_vendor_unknown",
                      variances, [], trail, total,
                      note="Vendor identity unverified. Never fail open on vendor identity.")

    if extraction_confidence is not None and _f(extraction_confidence) < 0.85:
        trail.append(_step("hard_stop_low_confidence", True,
                           f"extraction_confidence {_f(extraction_confidence):.2f} < 0.85"))
        return _route(invoice_number, "MATH_ERROR", "hard_stop_low_confidence",
                      variances, [], trail, total,
                      note="Extraction was not reliable enough to act on.")

    if invoice_age_days is not None and _f(invoice_age_days) > 120:
        trail.append(_step("hard_stop_stale_invoice", True,
                           f"invoice_age_days {_f(invoice_age_days):.0f} > 120"))
        return _route(invoice_number, "STALE_INVOICE", "hard_stop_stale_invoice",
                      variances, [], trail, total,
                      note="Invoices past 120 days require Controller approval.")

    trail.append(_step("hard_stops", False, "no unconditional escalation fired"))

    # ---------------------------------------------------------------------
    # Gate 2 — codes that structurally cannot auto-resolve.
    # ---------------------------------------------------------------------
    blocking = [v for v in variances if v.get("exception_code") in NEVER_AUTO_RESOLVE]
    if blocking:
        primary = _worst(blocking)
        code = primary.get("exception_code")
        trail.append(_step("non_resolvable_exception", True,
                           f"{code} cannot be auto-resolved by policy"))
        return _route(invoice_number, code, "non_resolvable_exception",
                      variances, blocking, trail, total)

    trail.append(_step("non_resolvable_exception", False,
                       "no structurally blocking exception present"))

    # ---------------------------------------------------------------------
    # Gate 3 — clean re-match. The original STP failure was transient.
    # ---------------------------------------------------------------------
    if not variances:
        trail.append(_step("clean_on_rematch", True, "match returned zero variances"))
        return {
            "invoice_number": invoice_number,
            "disposition": "auto_resolve",
            "policy_rule_applied": "clean_on_rematch",
            "primary_exception_code": None,
            "assignee_role": None,
            "assignee_email": None,
            "sla_hours": 0,
            "within_tolerance": [],
            "outside_tolerance": [],
            "gl_postings": [],
            "auto_resolved_amount": round(total, 2),
            "requires_human": False,
            "note": "No variance on re-match. Released to the payment run.",
            "decision_trail": trail,
            "policy_applied": policy,
            "evaluated_at": datetime.utcnow().isoformat(),
        }

    # ---------------------------------------------------------------------
    # Gate 4 — the auto-resolve ceiling. A 1% variance on a $900k invoice is
    # $9k, which nobody should auto-post.
    # ---------------------------------------------------------------------
    ceiling = policy["total_auto_resolve_ceiling_usd"]
    if total > ceiling:
        primary = _worst(variances)
        trail.append(_step("above_auto_resolve_ceiling", True,
                           f"invoice_total {total:.2f} > ceiling {ceiling:.2f}"))
        return _route(invoice_number, primary.get("exception_code"),
                      "above_auto_resolve_ceiling", variances, variances, trail, total,
                      note=f"Invoice exceeds the ${ceiling:,.0f} auto-resolve ceiling.")

    trail.append(_step("above_auto_resolve_ceiling", False,
                       f"invoice_total {total:.2f} within ceiling {ceiling:.2f}"))

    # ---------------------------------------------------------------------
    # Gate 5 — evaluate each variance against its band.
    # ---------------------------------------------------------------------
    within: List[Dict[str, Any]] = []
    outside: List[Dict[str, Any]] = []

    for v in variances:
        verdict, reason = _evaluate_band(v, policy, total)
        record = dict(v)
        record["band_verdict"] = verdict
        record["band_reason"] = reason
        trail.append(_step(
            f"band::{v.get('exception_code')}::line_{v.get('line_number')}",
            verdict == "outside",
            reason,
        ))
        (within if verdict == "within" else outside).append(record)

    if outside:
        primary = _worst(outside)
        return _route(invoice_number, primary.get("exception_code"),
                      "outside_tolerance_band", variances, outside, trail, total,
                      within=within)

    # ---------------------------------------------------------------------
    # Everything landed inside the bands. Auto-resolve with GL postings so the
    # entry is traceable back to this decision.
    # ---------------------------------------------------------------------
    gl_postings = []
    for v in within:
        code = v.get("exception_code")
        account = VARIANCE_GL_ACCOUNTS.get(code)
        amount = round(_f(v.get("variance_amount")), 2)
        if account and abs(amount) >= 0.01:
            gl_postings.append({
                "gl_account": account,
                "amount": amount,
                "exception_code": code,
                "line_number": v.get("line_number"),
                "memo": f"{code} auto-resolved within tolerance on {invoice_number}",
            })

    return {
        "invoice_number": invoice_number,
        "disposition": "auto_resolve",
        "policy_rule_applied": "all_variances_within_tolerance",
        "primary_exception_code": _worst(within).get("exception_code") if within else None,
        "assignee_role": None,
        "assignee_email": None,
        "sla_hours": 0,
        "within_tolerance": within,
        "outside_tolerance": [],
        "gl_postings": gl_postings,
        "auto_resolved_amount": round(total, 2),
        "requires_human": False,
        "note": (
            f"{len(within)} variance(s) inside tolerance. Auto-resolved and "
            f"posted across {len(gl_postings)} GL account(s)."
        ),
        "decision_trail": trail,
        "policy_applied": policy,
        "evaluated_at": datetime.utcnow().isoformat(),
    }


# ============================================================================
# Band evaluation
# ============================================================================

def _evaluate_band(
    variance: Dict[str, Any],
    policy: Dict[str, float],
    invoice_total: float,
) -> tuple:
    """Return ('within'|'outside', human-readable reason) for one variance."""
    code = variance.get("exception_code")
    amount = abs(_f(variance.get("variance_amount")))
    percent = abs(_f(variance.get("variance_percent")))

    if code == "PRICE_VAR":
        pct_cap = policy["price_variance_percent"]
        abs_cap = policy["price_variance_absolute_usd"]
        # Both tests must pass. A small percentage of a large line is still a
        # large dollar amount, and a small dollar amount at a huge percentage
        # signals a data problem rather than a rounding difference.
        if percent <= pct_cap and amount <= abs_cap:
            return "within", (
                f"PRICE_VAR {percent:.2f}% / ${amount:,.2f} within "
                f"{pct_cap:.0f}% and ${abs_cap:,.0f}"
            )
        return "outside", (
            f"PRICE_VAR {percent:.2f}% / ${amount:,.2f} breaches "
            f"{pct_cap:.0f}% or ${abs_cap:,.0f}"
        )

    if code == "QTY_VAR":
        pct_cap = policy["quantity_variance_percent"]
        # Under-delivery is not an exposure — we simply pay for less.
        if _f(variance.get("invoice_value")) < _f(variance.get("reference_value")):
            return "within", "QTY_VAR is an under-billing, no exposure"
        if percent <= pct_cap:
            return "within", f"QTY_VAR {percent:.2f}% within {pct_cap:.0f}%"
        return "outside", f"QTY_VAR {percent:.2f}% breaches {pct_cap:.0f}%"

    if code == "FREIGHT_UNMATCHED":
        usd_cap = policy["freight_unmatched_max_usd"]
        pct_cap = policy["freight_unmatched_max_percent"]
        effective_cap = min(usd_cap, invoice_total * (pct_cap / 100.0)) if invoice_total else usd_cap
        if amount <= effective_cap:
            return "within", (
                f"FREIGHT ${amount:,.2f} within the lower of ${usd_cap:,.0f} "
                f"and {pct_cap:.0f}% (${effective_cap:,.2f})"
            )
        return "outside", f"FREIGHT ${amount:,.2f} breaches ${effective_cap:,.2f}"

    if code == "TAX_VAR":
        usd_cap = policy["tax_variance_max_usd"]
        if amount <= usd_cap:
            return "within", f"TAX_VAR ${amount:,.2f} within ${usd_cap:,.0f}"
        return "outside", f"TAX_VAR ${amount:,.2f} breaches ${usd_cap:,.0f}"

    if code == "MATH_ERROR":
        # An invoice that does not foot is always a human decision. Auto-posting
        # a plug entry to make arithmetic work is exactly the control failure
        # auditors look for.
        return "outside", "MATH_ERROR never auto-resolves — the invoice does not foot"

    return "outside", f"{code} has no tolerance band defined; defaulting to human review"


# ============================================================================
# Helpers
# ============================================================================

def _route(
    invoice_number: str,
    code: Optional[str],
    rule: str,
    all_variances: List[Dict[str, Any]],
    breaching: List[Dict[str, Any]],
    trail: List[Dict[str, Any]],
    invoice_total: float,
    within: Optional[List[Dict[str, Any]]] = None,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a route_to_human disposition."""
    routing = ROUTING_MATRIX.get(code or "", {
        "role": "ap_specialist",
        "email": "ap-specialist@example.com",
        "sla_hours": 8,
    })
    return {
        "invoice_number": invoice_number,
        "disposition": "route_to_human",
        "policy_rule_applied": rule,
        "primary_exception_code": code,
        "assignee_role": routing["role"],
        "assignee_email": routing["email"],
        "sla_hours": routing["sla_hours"],
        "within_tolerance": within or [],
        "outside_tolerance": breaching,
        "gl_postings": [],
        "auto_resolved_amount": 0.0,
        "requires_human": True,
        "note": note or (
            f"{len(breaching)} variance(s) require {routing['role']} review "
            f"within {routing['sla_hours']}h."
        ),
        "dollar_impact": round(
            sum(abs(_f(v.get("variance_amount"))) for v in breaching), 2
        ) or round(invoice_total, 2),
        "decision_trail": trail,
        "evaluated_at": datetime.utcnow().isoformat(),
    }


def _worst(variances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Highest-severity variance, breaking ties on the larger dollar amount. This
    is what decides who the exception routes to.
    """
    if not variances:
        return {}
    return sorted(
        variances,
        key=lambda v: (
            _SEVERITY_RANK.get(v.get("severity", "info"), 0),
            abs(_f(v.get("variance_amount"))),
        ),
        reverse=True,
    )[0]


def _step(rule: str, fired: bool, detail: str) -> Dict[str, Any]:
    """One entry in the decision trail. This is the audit artefact."""
    return {"rule": rule, "fired": fired, "detail": detail}


def _f(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return 0.0


# ============================================================================
# Class-based implementation
# ============================================================================

class TolerancePolicyAction(ApexActionBase):
    """Tolerance Policy Action (class-based)."""

    name = "tolerance_policy"
    description = "Apply AP tolerance bands and routing matrix"
    category = "policy_engine"
    industry = "financial_services"

    def execute(self, **kwargs) -> dict:
        return tolerance_policy(**kwargs)


def handler(event, context):
    """Lambda entry point."""
    return tolerance_policy(**event)
