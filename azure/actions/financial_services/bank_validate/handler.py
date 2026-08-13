"""
Bank Validate - Financial Services Action (Context-Driven)
Validate bank account information for payment processing

Context-Driven Architecture:
- Validation rules from playbook context.payment_config
- Bank requirements from context.vendor_validation.bank_requirements
"""

from typing import Dict, Any, Optional
from datetime import datetime
import structlog
import re

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


# Default bank validation configuration
DEFAULT_BANK_CONFIG = {
    "require_verification": True,
    "routing_number_length": 9,
    "account_number_min_length": 4,
    "account_number_max_length": 17,
    "verification_methods": ["micro_deposit", "instant_verify"]
}


@register_factory("bank_validate")
async def bank_validate(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate bank account information (context-driven).

    Context keys used:
        - payment_config: Payment configuration
        - vendor_validation: Vendor bank requirements

    Input:
        routing_number: Bank routing number
        account_number: Bank account number
        account_type: Account type (checking, savings)
        bank_name: Bank name (optional)
        vendor_id: Vendor ID

    Output:
        valid: Whether bank info is valid
        routing_valid: Routing number validation
        account_valid: Account number validation
        verification_status: Verification status
        bank_details: Looked up bank details
    """
    context = context or input_data.get('context', {})
    bank_config = context.get('payment_config', {}).get('bank_validation', DEFAULT_BANK_CONFIG)
    vendor_validation = context.get('vendor_validation', {})

    logger.info(
        "Bank validate invoked",
        context_driven=bool(context)
    )

    # Extract bank info
    routing_number = input_data.get('routing_number', '')
    account_number = input_data.get('account_number', '')
    account_type = input_data.get('account_type', 'checking')
    bank_name = input_data.get('bank_name', '')
    vendor_id = input_data.get('vendor_id', '')

    # Get from upstream if available
    vendor = input_data.get('vendor_match', {}) or input_data.get('vendor_lookup', {})
    if vendor and not routing_number:
        bank_info = vendor.get('bank_info', {})
        routing_number = bank_info.get('routing_number', '')
        account_number = bank_info.get('account_number', '')

    # Validate routing number
    routing_valid, routing_errors = _validate_routing_number(
        routing_number,
        bank_config.get('routing_number_length', 9)
    )

    # Validate account number
    account_valid, account_errors = _validate_account_number(
        account_number,
        bank_config.get('account_number_min_length', 4),
        bank_config.get('account_number_max_length', 17)
    )

    # Look up bank details
    bank_details = _lookup_bank(routing_number) if routing_valid else None

    # Determine verification status
    require_verification = bank_config.get('require_verification', True)
    verification_status = "not_required"
    if require_verification:
        verification_status = "pending"

    # Overall validity
    valid = routing_valid and account_valid

    return {
        "valid": valid,
        "routing_number": routing_number[:4] + "****" if routing_number else None,  # Partial mask
        "account_number_last4": account_number[-4:] if account_number else None,
        "account_type": account_type,
        "routing_valid": routing_valid,
        "routing_errors": routing_errors,
        "account_valid": account_valid,
        "account_errors": account_errors,
        "bank_name": bank_details.get('bank_name') if bank_details else bank_name,
        "bank_details": bank_details,
        "verification_status": verification_status,
        "verification_required": require_verification,
        "verification_methods": bank_config.get('verification_methods', []) if require_verification else [],
        "vendor_id": vendor_id,
        "validated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "bank_validate",
        "factory_version": "2.0.0",
        "context_keys_used": ["payment_config", "vendor_validation"]
    }


def _validate_routing_number(routing: str, expected_length: int) -> tuple:
    """Validate ABA routing number."""
    errors = []

    if not routing:
        return False, ["Routing number is required"]

    # Remove any formatting
    routing = re.sub(r'\D', '', routing)

    # Check length
    if len(routing) != expected_length:
        errors.append(f"Routing number must be {expected_length} digits")
        return False, errors

    # Validate checksum (ABA routing number algorithm)
    try:
        digits = [int(d) for d in routing]
        checksum = (
            3 * (digits[0] + digits[3] + digits[6]) +
            7 * (digits[1] + digits[4] + digits[7]) +
            1 * (digits[2] + digits[5] + digits[8])
        )
        if checksum % 10 != 0:
            errors.append("Invalid routing number checksum")
            return False, errors
    except (ValueError, IndexError):
        errors.append("Invalid routing number format")
        return False, errors

    return True, []


def _validate_account_number(account: str, min_length: int, max_length: int) -> tuple:
    """Validate bank account number."""
    errors = []

    if not account:
        return False, ["Account number is required"]

    # Remove any formatting
    account = re.sub(r'\D', '', account)

    # Check length
    if len(account) < min_length:
        errors.append(f"Account number must be at least {min_length} digits")
        return False, errors

    if len(account) > max_length:
        errors.append(f"Account number must be at most {max_length} digits")
        return False, errors

    return True, []


def _lookup_bank(routing: str) -> Optional[Dict[str, Any]]:
    """Look up bank details from routing number."""
    # Sample bank lookup data
    # In production, would use a banking API or database
    bank_lookup = {
        "021000021": {"bank_name": "JPMorgan Chase Bank", "city": "New York", "state": "NY"},
        "011000015": {"bank_name": "Federal Reserve Bank", "city": "Boston", "state": "MA"},
        "021000089": {"bank_name": "Citibank", "city": "New York", "state": "NY"},
        "026009593": {"bank_name": "Bank of America", "city": "New York", "state": "NY"},
        "071000013": {"bank_name": "JPMorgan Chase Bank", "city": "Chicago", "state": "IL"}
    }

    return bank_lookup.get(routing, {
        "bank_name": "Unknown Bank",
        "city": "Unknown",
        "state": "Unknown"
    })


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(bank_validate(event))
