"""
Vendor Create - Financial Services Action (Context-Driven)
Create new vendor records in the system

Context-Driven Architecture:
- Vendor requirements from playbook context.vendor_validation
- Required documents from context.vendor_validation.required_documents
- Approval rules from context.approval_workflow
"""

from typing import Dict, Any, Optional
from datetime import datetime
import structlog
import uuid

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:
    import boto3

    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default vendor validation configuration
DEFAULT_VENDOR_CONFIG = {
    "required_documents": {
        "w9": {"required": True, "expires": False},
        "tax_id": {"required": True, "expires": False},
        "insurance": {"required": False, "expires": True, "expiry_days": 365}
    },
    "auto_approve_domestic": True,
    "require_bank_verification": True
}


@register_factory("vendor_create")
async def vendor_create(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create new vendor record (context-driven).

    Context keys used:
        - vendor_validation: Vendor requirements
        - approval_workflow: Approval settings

    Input:
        vendor_name: Vendor legal name
        vendor_type: Vendor type (supplier, contractor, etc.)
        tax_id: Tax identification number
        address: Vendor address
        bank_info: Banking information
        contact: Contact information

    Output:
        vendor_id: New vendor identifier
        status: Vendor status (pending, active)
        missing_documents: List of missing required documents
        requires_approval: Whether approval is needed
    """
    context = context or input_data.get('context', {})
    vendor_config = context.get('vendor_validation', DEFAULT_VENDOR_CONFIG)
    approval_config = context.get('approval_workflow', {})

    logger.info(
        "Vendor create invoked",
        context_driven=bool(context)
    )

    # Extract vendor data
    vendor_name = input_data.get('vendor_name', '')
    vendor_type = input_data.get('vendor_type', 'supplier')
    tax_id = input_data.get('tax_id', '')
    address = input_data.get('address', {})
    bank_info = input_data.get('bank_info', {})
    contact = input_data.get('contact', {})

    # Extract from invoice if available
    invoice = input_data.get('invoice_extract', {})
    if not vendor_name and invoice:
        vendor_name = invoice.get('vendor_name', '')

    # Generate vendor ID
    vendor_id = f"VEN-{uuid.uuid4().hex[:8].upper()}"

    # Check required documents
    required_docs = vendor_config.get('required_documents', {})
    provided_docs = input_data.get('documents', {})
    missing_documents = []

    for doc_type, doc_config in required_docs.items():
        if doc_config.get('required', False):
            if doc_type not in provided_docs and not input_data.get(f'has_{doc_type}', False):
                missing_documents.append({
                    "document": doc_type,
                    "required": True,
                    "expires": doc_config.get('expires', False)
                })

    # Check if tax ID provided
    has_tax_id = bool(tax_id) or input_data.get('has_tax_id', False)
    if required_docs.get('tax_id', {}).get('required', True) and not has_tax_id:
        if not any(d['document'] == 'tax_id' for d in missing_documents):
            missing_documents.append({"document": "tax_id", "required": True})

    # Determine if domestic
    country = address.get('country', 'US')
    is_domestic = country.upper() in ['US', 'USA', 'UNITED STATES']

    # Determine approval requirement
    auto_approve = (
        vendor_config.get('auto_approve_domestic', True) and
        is_domestic and
        len(missing_documents) == 0
    )

    # Determine status
    if missing_documents:
        status = "incomplete"
    elif auto_approve:
        status = "active"
    else:
        status = "pending_approval"

    # Create vendor record
    vendor_record = {
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "vendor_type": vendor_type,
        "tax_id": tax_id if tax_id else None,
        "address": address,
        "country": country,
        "is_domestic": is_domestic,
        "contact": contact,
        "bank_info": {k: v for k, v in bank_info.items() if k not in ['account_number', 'routing_number']},  # Redact sensitive
        "has_bank_info": bool(bank_info.get('account_number')),
        "status": status,
        "missing_documents": missing_documents,
        "requires_approval": not auto_approve and status != "incomplete",
        "auto_approved": auto_approve,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": input_data.get('created_by', 'system'),
        "context_driven": bool(context),
        "factory_id": "vendor_create",
        "factory_version": "2.0.0",
        "context_keys_used": ["vendor_validation", "approval_workflow"]
    }

    # Store vendor record
    await _store_vendor(vendor_record, context.get('aws_resources', {}))

    return vendor_record


async def _store_vendor(vendor: Dict[str, Any], aws_resources: Dict[str, Any]) -> bool:
    """Store vendor record to Cosmos DB."""
    if not AWS_ENABLED:
        return True

    try:
        cosmos_containers = aws_resources.get('cosmos_containers', {})
        vendors_table = cosmos_containers.get('vendors')

        if vendors_table:
            tables = get_table_resource()
            table = cosmos_db.Table(vendors_table)
            table.put_item(Item={
                'vendor_id': vendor['vendor_id'],
                'vendor_name': vendor['vendor_name'],
                'status': vendor['status'],
                'created_at': vendor['created_at']
            })
            return True
    except Exception as e:
        logger.warning("Failed to store vendor", error=str(e))

    return False


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(vendor_create(event))
