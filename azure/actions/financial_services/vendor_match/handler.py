"""
Vendor Match - Small Factory
Matches invoice data to vendor database records.
"""

from typing import Dict, Any, List, Optional
import re
import structlog
from services.small_factory import register_factory

# Claude integration (optional)
try:
    from services.azure_openai import get_model_router
    CLAUDE_ENABLED = True
except ImportError:
    CLAUDE_ENABLED = False

logger = structlog.get_logger()

# Sample vendor database (in production, this would be Cosmos DB/API)
VENDOR_DATABASE = {
    "acme": {
        "vendor_id": "VND-001",
        "name": "ACME Corporation",
        "domains": ["acme.com", "acmecorp.com"],
        "tax_id": "12-3456789",
        "payment_terms": "Net 30",
        "default_gl_code": "6100",
        "category": "supplies",
    },
    "techsupply": {
        "vendor_id": "VND-002",
        "name": "TechSupply Inc",
        "domains": ["techsupply.com", "techsupply.io"],
        "tax_id": "98-7654321",
        "payment_terms": "Net 45",
        "default_gl_code": "6200",
        "category": "technology",
    },
    "officemax": {
        "vendor_id": "VND-003",
        "name": "OfficeMax Pro",
        "domains": ["officemax.com", "officemaxpro.com"],
        "tax_id": "55-1234567",
        "payment_terms": "Net 30",
        "default_gl_code": "6150",
        "category": "office_supplies",
    },
}


def normalize_vendor_name(name: str) -> str:
    """Normalize vendor name for matching."""
    # Remove common suffixes
    name = re.sub(r'\b(inc|llc|corp|corporation|ltd|limited|co|company)\b', '', name.lower())
    # Remove punctuation and extra spaces
    name = re.sub(r'[^\w\s]', '', name)
    name = ' '.join(name.split())
    return name.strip()


def match_by_domain(domain: str) -> Optional[Dict[str, Any]]:
    """Match vendor by email domain."""
    domain = domain.lower().strip()
    for key, vendor in VENDOR_DATABASE.items():
        if domain in vendor.get("domains", []):
            return vendor
    return None


def match_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Match vendor by name similarity."""
    normalized = normalize_vendor_name(name)

    for key, vendor in VENDOR_DATABASE.items():
        vendor_normalized = normalize_vendor_name(vendor["name"])
        # Exact match
        if normalized == vendor_normalized:
            return vendor
        # Partial match
        if normalized in vendor_normalized or vendor_normalized in normalized:
            return vendor
        # Key match
        if key in normalized:
            return vendor

    return None


def match_by_tax_id(tax_id: str) -> Optional[Dict[str, Any]]:
    """Match vendor by tax ID."""
    # Normalize tax ID (remove dashes)
    tax_id = re.sub(r'[^\d]', '', tax_id)

    for vendor in VENDOR_DATABASE.values():
        vendor_tax = re.sub(r'[^\d]', '', vendor.get("tax_id", ""))
        if tax_id == vendor_tax:
            return vendor

    return None


@register_factory("vendor_match")
async def vendor_match(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Match invoice to vendor in database.

    Input:
        email_parse.sender_domain: Email sender domain
        invoice_extract.vendor_name: Extracted vendor name
        invoice_extract.vendor_tax_id: Extracted tax ID
        config.create_if_missing: Auto-create new vendor
        config.confidence_threshold: Minimum match confidence

    Output:
        matched: Whether vendor was matched
        vendor: Matched vendor details
        match_method: How match was found
        confidence: Match confidence score
        new_vendor: If vendor is new/unmatched
    """
    config = input_data.get('config', {})
    email_output = input_data.get('email_parse', {})
    invoice_output = input_data.get('invoice_extract', {})
    document_output = input_data.get('document_classify', {})

    confidence_threshold = config.get('confidence_threshold', 0.7)
    create_if_missing = config.get('create_if_missing', False)

    # Get matching criteria
    sender_domain = email_output.get('sender_domain', '')
    vendor_name = invoice_output.get('vendor_name', '') or invoice_output.get('vendor', {}).get('name', '')
    vendor_tax_id = invoice_output.get('vendor_tax_id', '') or invoice_output.get('vendor', {}).get('tax_id', '')

    matched_vendor = None
    match_method = None
    confidence = 0.0

    # Try matching methods in order of reliability

    # 1. Tax ID match (highest confidence)
    if vendor_tax_id:
        matched_vendor = match_by_tax_id(vendor_tax_id)
        if matched_vendor:
            match_method = "tax_id"
            confidence = 0.99

    # 2. Domain match
    if not matched_vendor and sender_domain:
        matched_vendor = match_by_domain(sender_domain)
        if matched_vendor:
            match_method = "email_domain"
            confidence = 0.95

    # 3. Name match
    if not matched_vendor and vendor_name:
        matched_vendor = match_by_name(vendor_name)
        if matched_vendor:
            match_method = "name_similarity"
            confidence = 0.85

    # Build result
    if matched_vendor and confidence >= confidence_threshold:
        return {
            "matched": True,
            "vendor": matched_vendor,
            "vendor_id": matched_vendor["vendor_id"],
            "match_method": match_method,
            "confidence": confidence,
            "new_vendor": False,
            "payment_terms": matched_vendor.get("payment_terms"),
            "default_gl_code": matched_vendor.get("default_gl_code"),
        }
    else:
        # New or unmatched vendor
        new_vendor_info = {
            "name": vendor_name,
            "domain": sender_domain,
            "tax_id": vendor_tax_id,
            "status": "pending_review",
        }

        return {
            "matched": False,
            "vendor": None,
            "vendor_id": None,
            "match_method": None,
            "confidence": confidence,
            "new_vendor": True,
            "new_vendor_info": new_vendor_info,
            "requires_manual_review": True,
            "suggested_action": "create_vendor" if create_if_missing else "manual_match",
        }
