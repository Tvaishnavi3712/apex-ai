"""
Payment Post - Healthcare Payers Action (Context-Driven)
Post payment to claim and generate payment records

Context-Driven Architecture:
- Payment settings from playbook context.payment_config
- GL mappings from context.gl_config
- Payment methods from context.payment_methods
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

try:
    from services.small_factory import register_factory
    SMALL_FACTORY_ENABLED = True
except ImportError:
    SMALL_FACTORY_ENABLED = False
    def register_factory(name):
        def decorator(func):
            return func
        return decorator

logger = structlog.get_logger()


# Default payment configuration
DEFAULT_PAYMENT_CONFIG = {
    "payment_methods": ["ach", "check", "wire"],
    "default_method": "ach",
    "batch_payments": True,
    "minimum_payment": 0.01,
    "payment_cycle": "weekly"
}

# Default GL mappings
DEFAULT_GL_CONFIG = {
    "claims_payable": "2100",
    "medical_expense": "5100",
    "pharmacy_expense": "5200",
    "provider_payable": "2110"
}


@register_factory("payment_post")
async def payment_post(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Post payment to claim (context-driven).

    Context keys used:
        - payment_config: Payment processing settings
        - gl_config: General ledger account mappings
        - payment_methods: Available payment methods

    Input:
        claim_extract: Extracted claim data
        benefits_apply: Benefits calculation result
        cob_calculate: COB calculation result (if applicable)

    Output:
        payment_posted: Whether payment was posted
        payment_amount: Amount to be paid
        payment_record: Payment record details
        gl_entries: GL posting entries
    """
    context = context or input_data.get('context', {})
    payment_config = context.get('payment_config', DEFAULT_PAYMENT_CONFIG)
    gl_config = context.get('gl_config', DEFAULT_GL_CONFIG)

    logger.info(
        "Payment post invoked",
        context_driven=bool(context)
    )

    # Get input data
    claim = input_data.get('claim_extract', {})
    benefits = input_data.get('benefits_apply', {})
    cob = input_data.get('cob_calculate', {})

    claim_number = claim.get('claim_number', '')

    # Determine payment amount
    if cob.get('cob_applies'):
        payment_amount = cob.get('plan_payment', 0)
    else:
        payment_amount = benefits.get('plan_payment', 0)

    # Check minimum payment threshold
    minimum_payment = payment_config.get('minimum_payment', 0.01)

    if payment_amount < minimum_payment:
        return {
            "claim_number": claim_number,
            "payment_posted": False,
            "payment_amount": 0,
            "reason": f"Below minimum payment threshold (${minimum_payment})",
            "status": "zero_pay",
            "posted_at": datetime.utcnow().isoformat(),
            "context_driven": bool(context),
            "factory_id": "payment_post",
            "factory_version": "2.0.0",
            "context_keys_used": ["payment_config"]
        }

    # Get provider info for payment
    provider_info = claim.get('claim_data', {}).get('provider_info', {})

    # Determine payment method
    preferred_method = provider_info.get('payment_method')
    available_methods = payment_config.get('payment_methods', ['ach', 'check'])

    if preferred_method and preferred_method in available_methods:
        payment_method = preferred_method
    else:
        payment_method = payment_config.get('default_method', 'ach')

    # Generate payment record
    payment_id = f"PAY{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    payment_record = {
        'payment_id': payment_id,
        'claim_number': claim_number,
        'payment_amount': round(payment_amount, 2),
        'payment_method': payment_method,
        'payee': {
            'name': provider_info.get('name', 'Unknown Provider'),
            'npi': provider_info.get('npi', ''),
            'tax_id': provider_info.get('tax_id', ''),
            'address': provider_info.get('address', {})
        },
        'payment_date': _calculate_payment_date(payment_config),
        'status': 'scheduled'
    }

    # Generate GL entries
    gl_entries = _generate_gl_entries(
        claim_number,
        payment_amount,
        benefits,
        gl_config
    )

    # Calculate batch info if batch payments enabled
    batch_info = None
    if payment_config.get('batch_payments', True):
        batch_info = {
            'batch_id': f"BATCH{datetime.utcnow().strftime('%Y%m%d')}",
            'payment_cycle': payment_config.get('payment_cycle', 'weekly'),
            'estimated_payment_date': payment_record['payment_date']
        }

    return {
        "claim_number": claim_number,
        "payment_posted": True,
        "payment_id": payment_id,
        "payment_amount": round(payment_amount, 2),
        "payment_method": payment_method,
        "payment_record": payment_record,
        "gl_entries": gl_entries,
        "gl_entry_count": len(gl_entries),
        "batch_info": batch_info,
        "status": "payment_scheduled",
        "amounts": {
            "billed": benefits.get('billed_amount', 0),
            "allowed": benefits.get('allowed_amount', 0),
            "plan_payment": round(payment_amount, 2),
            "member_responsibility": benefits.get('member_responsibility', 0),
            "provider_writeoff": benefits.get('provider_writeoff', 0)
        },
        "posted_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "payment_post",
        "factory_version": "2.0.0",
        "context_keys_used": ["payment_config", "gl_config", "payment_methods"]
    }


def _calculate_payment_date(payment_config: Dict) -> str:
    """Calculate payment date based on payment cycle."""
    from datetime import timedelta

    today = datetime.utcnow()
    cycle = payment_config.get('payment_cycle', 'weekly')

    if cycle == 'daily':
        payment_date = today + timedelta(days=1)
    elif cycle == 'weekly':
        # Next Friday
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        payment_date = today + timedelta(days=days_until_friday)
    elif cycle == 'biweekly':
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday < 7:
            days_until_friday += 7
        payment_date = today + timedelta(days=days_until_friday)
    else:  # monthly
        # First of next month
        if today.month == 12:
            payment_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            payment_date = today.replace(month=today.month + 1, day=1)

    return payment_date.strftime('%Y-%m-%d')


def _generate_gl_entries(claim_number: str, payment_amount: float,
                         benefits: Dict, gl_config: Dict) -> List[Dict]:
    """Generate GL posting entries."""
    entries = []

    # Debit medical expense
    entries.append({
        'account': gl_config.get('medical_expense', '5100'),
        'account_name': 'Medical Claims Expense',
        'debit': round(payment_amount, 2),
        'credit': 0,
        'reference': claim_number
    })

    # Credit provider payable
    entries.append({
        'account': gl_config.get('provider_payable', '2110'),
        'account_name': 'Provider Payable',
        'debit': 0,
        'credit': round(payment_amount, 2),
        'reference': claim_number
    })

    return entries


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(payment_post(event))
