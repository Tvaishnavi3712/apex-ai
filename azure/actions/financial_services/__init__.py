"""
Financial Services Action Pack
Pre-built actions for invoice processing, vendor validation, approval routing, etc.
"""

from .vendor_lookup import vendor_lookup, VendorLookupAction
from .po_match import po_match, POMatchAction
from .approval_route import approval_route, ApprovalRouteAction
from .compliance_check import compliance_check, ComplianceCheckAction
from .invoice_extract import invoice_extract

__all__ = [
    'vendor_lookup',
    'VendorLookupAction',
    'po_match',
    'POMatchAction',
    'approval_route',
    'ApprovalRouteAction',
    'compliance_check',
    'ComplianceCheckAction',
    'invoice_extract'
]

# Action Pack metadata
PACK_INFO = {
    "name": "Financial Services Action Pack",
    "version": "1.0.0",
    "industry": "financial_services",
    "description": "Pre-built actions for invoice processing, vendor validation, PO matching, and approval routing",
    "actions": [
        "vendor_lookup",
        "po_match",
        "approval_route",
        "compliance_check",
        "invoice_extract"
    ]
}
