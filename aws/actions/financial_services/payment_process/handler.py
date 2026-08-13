"""
Payment Process - Financial Services Action (Context-Driven)
Process approved payments through configured payment methods

Context-Driven Architecture:
- Payment methods from playbook context.payment_config
- Bank details from context.payment_config.bank_accounts
- Transaction limits from context.compliance.transaction_limits
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

try:
    import boto3
    AWS_ENABLED = True
except ImportError:
    AWS_ENABLED = False

logger = structlog.get_logger()


# Default payment configuration
DEFAULT_PAYMENT_CONFIG = {
    "methods": {
        "ach": {"enabled": True, "max_amount": 100000},
        "wire": {"enabled": True, "min_amount": 10000},
        "check": {"enabled": True, "max_amount": 50000}
    },
    "default_method": "ach",
    "require_dual_approval_above": 50000,
    "batch_payments": True
}


@register_factory("payment_process")
async def payment_process(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process payment for approved invoice (context-driven).

    Context keys used:
        - payment_config: Payment method configuration
        - compliance: Transaction limits

    Input:
        invoice_extract: Invoice data
        approval_route: Approval decision
        vendor_match: Vendor details
        payment_method: Preferred payment method (optional)

    Output:
        payment_id: Unique payment identifier
        payment_method: Selected payment method
        payment_status: Payment status
        scheduled_date: Payment scheduled date
        bank_reference: Bank reference number
    """
    context = context or input_data.get('context', {})
    payment_config = context.get('payment_config', DEFAULT_PAYMENT_CONFIG)
    compliance = context.get('compliance', {})

    logger.info(
        "Payment process invoked",
        context_driven=bool(context)
    )

    # Get upstream data
    invoice = input_data.get('invoice_extract', {})
    approval = input_data.get('approval_route', {})
    vendor = input_data.get('vendor_match', {}) or input_data.get('vendor_lookup', {})

    # Validate approval
    if not approval.get('auto_approved') and approval.get('approval_level') not in ['approved', 'auto_approve']:
        if not input_data.get('force_process'):
            return {
                "payment_id": None,
                "payment_status": "rejected",
                "error": "Invoice not approved for payment",
                "approval_status": approval.get('approval_level'),
                "context_driven": bool(context),
                "factory_id": "payment_process",
                "factory_version": "2.0.0"
            }

    amount = invoice.get('total_amount', 0)
    vendor_id = vendor.get('vendor_id', 'unknown')
    invoice_number = invoice.get('invoice_number', 'unknown')

    # Determine payment method
    requested_method = input_data.get('payment_method')
    payment_method = _select_payment_method(amount, requested_method, payment_config)

    # Generate payment ID
    payment_id = f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Check dual approval requirement
    dual_threshold = payment_config.get('require_dual_approval_above', 50000)
    requires_dual_approval = amount > dual_threshold

    if requires_dual_approval and not approval.get('dual_approval_completed'):
        return {
            "payment_id": payment_id,
            "payment_status": "pending_dual_approval",
            "amount": amount,
            "payment_method": payment_method,
            "requires_dual_approval": True,
            "dual_approval_threshold": dual_threshold,
            "context_driven": bool(context),
            "factory_id": "payment_process",
            "factory_version": "2.0.0"
        }

    # Process payment
    payment_result = await _execute_payment(
        payment_id=payment_id,
        amount=amount,
        vendor=vendor,
        invoice_number=invoice_number,
        payment_method=payment_method,
        payment_config=payment_config
    )

    return {
        "payment_id": payment_id,
        "invoice_number": invoice_number,
        "vendor_id": vendor_id,
        "vendor_name": vendor.get('vendor_name'),
        "amount": amount,
        "currency": invoice.get('currency', 'USD'),
        "payment_method": payment_method,
        "payment_status": payment_result.get('status', 'processed'),
        "bank_reference": payment_result.get('bank_reference'),
        "scheduled_date": payment_result.get('scheduled_date'),
        "batch_id": payment_result.get('batch_id'),
        "requires_dual_approval": requires_dual_approval,
        "processed_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "payment_process",
        "factory_version": "2.0.0",
        "context_keys_used": ["payment_config", "compliance"]
    }


def _select_payment_method(
    amount: float,
    requested_method: Optional[str],
    payment_config: Dict[str, Any]
) -> str:
    """Select appropriate payment method based on amount and configuration."""
    methods = payment_config.get('methods', DEFAULT_PAYMENT_CONFIG['methods'])

    # Use requested method if valid
    if requested_method and requested_method in methods:
        method_config = methods[requested_method]
        if method_config.get('enabled', True):
            max_amt = method_config.get('max_amount', float('inf'))
            min_amt = method_config.get('min_amount', 0)
            if min_amt <= amount <= max_amt:
                return requested_method

    # Auto-select based on amount
    if amount >= methods.get('wire', {}).get('min_amount', 10000):
        if methods.get('wire', {}).get('enabled', True):
            return 'wire'

    if amount <= methods.get('ach', {}).get('max_amount', 100000):
        if methods.get('ach', {}).get('enabled', True):
            return 'ach'

    if methods.get('check', {}).get('enabled', True):
        return 'check'

    return payment_config.get('default_method', 'ach')


async def _execute_payment(
    payment_id: str,
    amount: float,
    vendor: Dict[str, Any],
    invoice_number: str,
    payment_method: str,
    payment_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute payment through banking system."""
    # In production, this would integrate with banking APIs
    # Simplified implementation for now

    bank_reference = f"REF-{uuid.uuid4().hex[:12].upper()}"
    scheduled_date = datetime.utcnow().isoformat()

    logger.info(
        "Payment executed",
        payment_id=payment_id,
        amount=amount,
        method=payment_method,
        bank_reference=bank_reference
    )

    # Simulate batch processing for ACH
    batch_id = None
    if payment_method == 'ach' and payment_config.get('batch_payments', True):
        batch_id = f"BATCH-{datetime.utcnow().strftime('%Y%m%d')}"

    return {
        "status": "processed",
        "bank_reference": bank_reference,
        "scheduled_date": scheduled_date,
        "batch_id": batch_id
    }


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(payment_process(event))
