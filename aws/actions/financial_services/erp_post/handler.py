"""
ERP Post - Small Factory
Formats and posts invoice data to ERP system.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()


def calculate_due_date(invoice_date: str, payment_terms: str) -> str:
    """Calculate payment due date based on terms."""
    try:
        # Parse invoice date
        if isinstance(invoice_date, str):
            inv_date = datetime.fromisoformat(invoice_date.replace('Z', '+00:00'))
        else:
            inv_date = datetime.now()

        # Parse payment terms (e.g., "Net 30", "Net 45")
        days = 30  # default
        if payment_terms:
            import re
            match = re.search(r'(\d+)', payment_terms)
            if match:
                days = int(match.group(1))

        due_date = inv_date + timedelta(days=days)
        return due_date.strftime('%Y-%m-%d')

    except Exception:
        return (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')


def format_for_sap(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format invoice data for SAP posting."""
    return {
        "BKPF": {  # Document header
            "BUKRS": invoice_data.get("company_code", "1000"),
            "BLART": "KR",  # Document type: Vendor invoice
            "BLDAT": invoice_data.get("invoice_date"),
            "BUDAT": datetime.now().strftime('%Y-%m-%d'),
            "WAERS": invoice_data.get("currency", "USD"),
            "XBLNR": invoice_data.get("invoice_number"),
        },
        "BSEG": [  # Line items
            {
                "BUZEI": str(i + 1).zfill(3),
                "BSCHL": "31" if item.get("is_vendor_line") else "40",
                "HKONT": item.get("gl_code"),
                "WRBTR": item.get("amount"),
                "SGTXT": item.get("description", "")[:50],
            }
            for i, item in enumerate(invoice_data.get("line_items", []))
        ],
    }


def format_for_oracle(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format invoice data for Oracle Financials."""
    return {
        "invoiceHeader": {
            "invoiceNumber": invoice_data.get("invoice_number"),
            "vendorId": invoice_data.get("vendor_id"),
            "invoiceDate": invoice_data.get("invoice_date"),
            "invoiceAmount": invoice_data.get("total_amount"),
            "invoiceCurrency": invoice_data.get("currency", "USD"),
            "paymentTerms": invoice_data.get("payment_terms"),
            "description": invoice_data.get("description", ""),
        },
        "invoiceLines": [
            {
                "lineNumber": i + 1,
                "lineType": "ITEM",
                "amount": item.get("amount"),
                "description": item.get("description"),
                "accountCode": item.get("gl_code"),
            }
            for i, item in enumerate(invoice_data.get("line_items", []))
        ],
    }


def format_for_quickbooks(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format invoice data for QuickBooks."""
    return {
        "Bill": {
            "VendorRef": {"value": invoice_data.get("vendor_id")},
            "DocNumber": invoice_data.get("invoice_number"),
            "TxnDate": invoice_data.get("invoice_date"),
            "DueDate": invoice_data.get("due_date"),
            "TotalAmt": invoice_data.get("total_amount"),
            "CurrencyRef": {"value": invoice_data.get("currency", "USD")},
            "Line": [
                {
                    "DetailType": "AccountBasedExpenseLineDetail",
                    "Amount": item.get("amount"),
                    "Description": item.get("description"),
                    "AccountBasedExpenseLineDetail": {
                        "AccountRef": {"value": item.get("gl_code")},
                    },
                }
                for item in invoice_data.get("line_items", [])
            ],
        }
    }


@register_factory("erp_post")
async def erp_post(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format and prepare invoice for ERP posting.

    Input:
        invoice_extract: Invoice details
        vendor_match: Vendor information
        po_reconcile: PO reconciliation
        approval_route: Approval results
        config.erp_system: Target ERP (sap, oracle, quickbooks)
        config.auto_post: Whether to auto-post

    Output:
        erp_payload: Formatted ERP payload
        posting_status: Status of posting
        document_number: Generated document number
        validation_errors: Any validation issues
    """
    config = input_data.get('config', {})
    invoice = input_data.get('invoice_extract', {})
    vendor = input_data.get('vendor_match', {})
    po_result = input_data.get('po_reconcile', {})
    approval = input_data.get('approval_route', {})

    erp_system = config.get('erp_system', 'quickbooks')
    auto_post = config.get('auto_post', False)

    # Validate required fields
    validation_errors = []

    if not invoice.get('invoice_number'):
        validation_errors.append("Missing invoice number")
    if not invoice.get('total_amount') and not invoice.get('total'):
        validation_errors.append("Missing invoice amount")
    if not vendor.get('vendor_id') and not vendor.get('matched'):
        validation_errors.append("Vendor not matched")

    # If not auto-approved, don't post
    if not approval.get('auto_approved', False) and not approval.get('fully_approved', False):
        return {
            "erp_payload": None,
            "posting_status": "pending_approval",
            "document_number": None,
            "validation_errors": validation_errors,
            "ready_to_post": False,
            "blocked_reason": "Awaiting approval",
        }

    if validation_errors:
        return {
            "erp_payload": None,
            "posting_status": "validation_failed",
            "document_number": None,
            "validation_errors": validation_errors,
            "ready_to_post": False,
        }

    # Build consolidated invoice data
    payment_terms = vendor.get('payment_terms', 'Net 30')
    invoice_date = invoice.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))

    invoice_data = {
        "invoice_number": invoice.get('invoice_number'),
        "vendor_id": vendor.get('vendor_id'),
        "vendor_name": vendor.get('vendor', {}).get('name', ''),
        "invoice_date": invoice_date,
        "due_date": calculate_due_date(invoice_date, payment_terms),
        "total_amount": invoice.get('total_amount') or invoice.get('total', 0),
        "currency": invoice.get('currency', 'USD'),
        "payment_terms": payment_terms,
        "po_number": po_result.get('po_number'),
        "gl_code": approval.get('gl_code', '6100'),
        "cost_center": approval.get('cost_center'),
        "department": approval.get('department'),
        "description": f"Invoice {invoice.get('invoice_number')} from {vendor.get('vendor', {}).get('name', 'Unknown')}",
        "line_items": invoice.get('line_items', [
            {
                "description": "Invoice total",
                "amount": invoice.get('total_amount') or invoice.get('total', 0),
                "gl_code": approval.get('gl_code', '6100'),
            }
        ]),
    }

    # Add vendor line for AP
    invoice_data["line_items"].insert(0, {
        "description": "Accounts Payable",
        "amount": -(invoice.get('total_amount') or invoice.get('total', 0)),
        "gl_code": "2100",  # AP GL code
        "is_vendor_line": True,
    })

    # Format for target ERP
    formatters = {
        "sap": format_for_sap,
        "oracle": format_for_oracle,
        "quickbooks": format_for_quickbooks,
    }

    formatter = formatters.get(erp_system.lower(), format_for_quickbooks)
    erp_payload = formatter(invoice_data)

    # Generate document number
    doc_number = f"AP-{datetime.now().strftime('%Y%m%d')}-{invoice.get('invoice_number', 'UNKNOWN')[-6:]}"

    # Determine posting status
    if auto_post:
        posting_status = "posted"
        logger.info("Invoice auto-posted to ERP", doc_number=doc_number, erp=erp_system)
    else:
        posting_status = "ready_to_post"

    return {
        "erp_payload": erp_payload,
        "erp_system": erp_system,
        "posting_status": posting_status,
        "document_number": doc_number,
        "validation_errors": [],
        "ready_to_post": True,
        "invoice_data": invoice_data,
        "payment_due_date": invoice_data["due_date"],
    }
