"""
Compliance Check Action (Context-Driven)
Verify transactions against compliance rules and policies

Context-Driven Architecture:
- Compliance rules are read from playbook context.compliance
- Blocked countries are read from context.compliance.blocked_countries
- Transaction limits are read from context.compliance.transaction_limits
"""

import boto3
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase

# Small Factory registration
try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

import structlog
logger = structlog.get_logger()


@apex_action(ApexActionSchema(
    name="compliance_check",
    description="Check transaction against compliance rules and flag violations",
    category="business_logic",
    industry="financial_services",
    input_schema=ActionInputSchema(description="Compliance check parameters")
        .add_number("amount", "Transaction amount", required=True)
        .add_string("vendor_id", "Vendor ID", required=True)
        .add_string("vendor_country", "Vendor country code", required=False)
        .add_boolean("has_tax_id", "Whether vendor has tax ID on file", required=False)
        .add_boolean("has_w9", "Whether W9 is on file", required=False)
        .add_boolean("has_po", "Whether PO exists", required=False)
        .add_boolean("has_invoice", "Whether invoice is attached", required=False)
        .add_boolean("has_receipt", "Whether receipt is attached", required=False)
        .add_boolean("has_contract", "Whether contract exists", required=False)
        .add_string("invoice_date", "Invoice date (ISO format)", required=False)
        .add_number("daily_vendor_total", "Total paid to vendor today", required=False)
        .add_object("context", "Playbook context with compliance rules", required=False),
    output_schema=ActionOutputSchema(description="Compliance check result")
        .add_boolean("compliant", "Whether transaction is compliant")
        .add_string("compliance_status", "PASS | FAIL | WARNING")
        .add_boolean("requires_review", "Whether manual review is needed")
))
def compliance_check(
    amount: float,
    vendor_id: str,
    vendor_country: str = None,
    has_tax_id: bool = True,
    has_w9: bool = True,
    has_po: bool = True,
    has_invoice: bool = True,
    has_receipt: bool = True,
    has_contract: bool = False,
    invoice_date: str = None,
    daily_vendor_total: float = 0,
    context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    Check transaction against compliance rules using context-driven configuration.

    Args:
        amount: Transaction amount
        vendor_id: Vendor identifier
        vendor_country: Vendor's country code
        has_tax_id: Whether vendor tax ID is on file
        has_w9: Whether W9 is on file
        has_po: Whether a PO exists
        has_invoice: Whether invoice is attached
        has_receipt: Whether receipt is attached
        has_contract: Whether contract exists for this vendor
        invoice_date: Date of invoice
        daily_vendor_total: Total already paid to vendor today
        context: Playbook context containing compliance rules

    Returns:
        Compliance status with any violations
    """
    context = context or {}
    compliance_config = context.get("compliance", {})

    violations = []
    warnings = []

    # =========================================================================
    # Vendor Rules (from context)
    # =========================================================================
    vendor_validation = context.get("vendor_validation", {})
    required_docs = vendor_validation.get("required_documents", {})

    # Tax ID check
    if required_docs.get("tax_id", {}).get("required", True) and not has_tax_id:
        violations.append({
            "rule": "require_tax_id",
            "message": "Vendor tax ID is required but not on file",
            "severity": "high",
            "source": "context.vendor_validation.required_documents"
        })

    # W9 check
    w9_config = required_docs.get("w9", {})
    if w9_config.get("required", True) and not has_w9:
        violations.append({
            "rule": "require_w9",
            "message": "W9 form is required but not on file",
            "severity": "high",
            "source": "context.vendor_validation.required_documents"
        })

    # =========================================================================
    # Blocked Countries (from context)
    # =========================================================================
    blocked_countries = compliance_config.get("blocked_countries", [])

    if vendor_country:
        vendor_country_upper = vendor_country.upper()
        for blocked in blocked_countries:
            blocked_code = blocked.get("code", blocked) if isinstance(blocked, dict) else blocked
            if vendor_country_upper == blocked_code.upper():
                reason = blocked.get("reason", "Sanctioned country") if isinstance(blocked, dict) else "Blocked country"
                violations.append({
                    "rule": "blocked_country",
                    "message": f"Transactions with vendors in {vendor_country} are prohibited: {reason}",
                    "severity": "critical",
                    "source": "context.compliance.blocked_countries"
                })
                break

    # =========================================================================
    # Transaction Limits (from context)
    # =========================================================================
    transaction_limits = compliance_config.get("transaction_limits", {})

    # Max single invoice
    max_single = transaction_limits.get("max_single_invoice", 1000000)
    if amount > max_single:
        violations.append({
            "rule": "max_single_transaction",
            "message": f"Amount ${amount:,.2f} exceeds maximum single transaction of ${max_single:,.2f}",
            "severity": "high",
            "source": "context.compliance.transaction_limits"
        })

    # Max daily vendor total
    max_daily = transaction_limits.get("max_vendor_daily", 2000000)
    total_with_this = daily_vendor_total + amount
    if total_with_this > max_daily:
        violations.append({
            "rule": "max_daily_vendor_total",
            "message": f"Daily vendor total ${total_with_this:,.2f} exceeds limit of ${max_daily:,.2f}",
            "severity": "high",
            "source": "context.compliance.transaction_limits"
        })

    # Wire required threshold
    wire_threshold = transaction_limits.get("require_wire_above", 100000)
    if amount > wire_threshold:
        warnings.append({
            "rule": "wire_required",
            "message": f"Amount ${amount:,.2f} requires wire transfer",
            "severity": "info",
            "source": "context.compliance.transaction_limits"
        })

    # =========================================================================
    # PO Matching (from context)
    # =========================================================================
    po_matching = context.get("po_matching", {})
    po_required_threshold = po_matching.get("required_threshold", 1000)

    if amount > po_required_threshold and not has_po:
        violations.append({
            "rule": "require_po",
            "message": f"PO required for amounts over ${po_required_threshold:,.2f}",
            "severity": "medium",
            "source": "context.po_matching.required_threshold"
        })

    # =========================================================================
    # Invoice Age (from context)
    # =========================================================================
    invoice_age_config = compliance_config.get("invoice_age", {})
    max_age_days = invoice_age_config.get("max_days", 90)
    warning_age_days = invoice_age_config.get("warning_days", 60)

    if invoice_date:
        try:
            if 'T' in invoice_date:
                invoice_dt = datetime.fromisoformat(invoice_date.replace('Z', '+00:00'))
            else:
                invoice_dt = datetime.strptime(invoice_date, "%Y-%m-%d")

            now = datetime.now(invoice_dt.tzinfo) if invoice_dt.tzinfo else datetime.now()
            age_days = (now - invoice_dt).days

            if age_days > max_age_days:
                violations.append({
                    "rule": "invoice_age",
                    "message": f"Invoice is {age_days} days old, exceeds {max_age_days} day limit",
                    "severity": "medium",
                    "source": "context.compliance.invoice_age"
                })
            elif age_days > warning_age_days:
                warnings.append({
                    "rule": "invoice_age_warning",
                    "message": f"Invoice is {age_days} days old, approaching {max_age_days} day limit",
                    "severity": "low",
                    "source": "context.compliance.invoice_age"
                })
        except (ValueError, TypeError):
            warnings.append({
                "rule": "invalid_date",
                "message": "Could not parse invoice date",
                "severity": "low"
            })

    # =========================================================================
    # Duplicate Detection (from context)
    # =========================================================================
    duplicate_config = compliance_config.get("duplicate_detection", {})
    if duplicate_config.get("enabled", True):
        if not duplicate_config.get("allow_same_vendor_same_day", False):
            if daily_vendor_total > 0:
                warnings.append({
                    "rule": "same_day_vendor_payment",
                    "message": f"Another payment to this vendor exists today (${daily_vendor_total:,.2f})",
                    "severity": "info",
                    "source": "context.compliance.duplicate_detection"
                })

    # =========================================================================
    # Audit Requirements (from context)
    # =========================================================================
    audit_config = compliance_config.get("audit", {})
    if audit_config.get("log_all_decisions", True):
        # Log compliance check for audit trail
        logger.info(
            "Compliance check completed",
            amount=amount,
            vendor_id=vendor_id,
            violations=len(violations),
            warnings=len(warnings)
        )

    # =========================================================================
    # Sanctions Screening (from context)
    # =========================================================================
    sanctions_config = compliance_config.get("sanctions", {})
    if sanctions_config.get("enabled", False):
        # In production, this would call a sanctions screening service
        sanctions_lists = sanctions_config.get("lists", ["OFAC_SDN"])
        warnings.append({
            "rule": "sanctions_screening",
            "message": f"Sanctions screening should be performed against: {', '.join(sanctions_lists)}",
            "severity": "info",
            "source": "context.compliance.sanctions"
        })

    # =========================================================================
    # Determine Overall Status
    # =========================================================================
    critical_violations = [v for v in violations if v["severity"] == "critical"]
    high_violations = [v for v in violations if v["severity"] == "high"]
    medium_violations = [v for v in violations if v["severity"] == "medium"]

    if critical_violations:
        compliance_status = "FAIL"
        compliant = False
        requires_review = True
    elif high_violations:
        compliance_status = "FAIL"
        compliant = False
        requires_review = True
    elif medium_violations:
        compliance_status = "WARNING"
        compliant = False
        requires_review = True
    elif warnings:
        compliance_status = "WARNING"
        compliant = True
        requires_review = False
    else:
        compliance_status = "PASS"
        compliant = True
        requires_review = False

    return {
        "compliant": compliant,
        "compliance_status": compliance_status,
        "requires_review": requires_review,
        "violations": violations,
        "warnings": warnings,
        "violation_count": len(violations),
        "warning_count": len(warnings),
        "checked_at": datetime.utcnow().isoformat(),
        "amount": amount,
        "vendor_id": vendor_id,
        "context_driven": bool(context),
        "rules_checked": [
            "vendor_validation",
            "blocked_countries",
            "transaction_limits",
            "po_matching",
            "invoice_age",
            "duplicate_detection",
            "sanctions"
        ]
    }


@register_factory("compliance_check")
async def compliance_check_factory(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Small Factory handler for compliance check (context-driven).

    Context keys used:
        - compliance: Compliance rules (blocked_countries, transaction_limits, etc.)
        - vendor_validation: Vendor documentation requirements
        - po_matching: PO requirements

    Returns:
        Compliance check results with violations and warnings
    """
    effective_context = context or input_data.get("context", {})

    # Extract invoice data from previous factory
    invoice = input_data.get("invoice_extract", {}) or input_data.get("data_extraction", {})
    vendor = input_data.get("vendor_match", {}) or input_data.get("vendor_validation", {})

    logger.info(
        "Compliance check factory invoked",
        context_driven=bool(effective_context)
    )

    result = compliance_check(
        amount=float(invoice.get("total_amount", 0) or invoice.get("total", 0) or input_data.get("amount", 0)),
        vendor_id=vendor.get("vendor_id", "") or input_data.get("vendor_id", ""),
        vendor_country=vendor.get("country", input_data.get("vendor_country")),
        has_tax_id=vendor.get("has_tax_id", True),
        has_w9=vendor.get("has_w9", True),
        has_po=input_data.get("has_po", True),
        has_invoice=True,
        has_receipt=input_data.get("has_receipt", True),
        has_contract=input_data.get("has_contract", False),
        invoice_date=invoice.get("invoice_date"),
        daily_vendor_total=float(input_data.get("daily_vendor_total", 0)),
        context=effective_context
    )

    result["factory_id"] = "compliance_check"
    result["factory_version"] = "2.0.0"
    result["context_keys_used"] = ["compliance", "vendor_validation", "po_matching"]

    return result


class ComplianceCheckAction(ApexActionBase):
    """Compliance Check Action (class-based)"""

    name = "compliance_check"
    description = "Check transaction against compliance rules"
    category = "business_logic"
    industry = "financial_services"

    def __init__(self, context: Dict[str, Any] = None):
        super().__init__()
        self.context = context or {}

    def execute(self, amount: float, vendor_id: str, **kwargs) -> dict:
        return compliance_check(
            amount=amount,
            vendor_id=vendor_id,
            context=self.context,
            **kwargs
        )


def handler(event, context):
    """Lambda entry point"""
    return compliance_check(**event)
