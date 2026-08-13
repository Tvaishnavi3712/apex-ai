"""
Generate Payment - Financial Services Action (Context-Driven)
Generate payment files (NACHA, wire instructions, checks)

Context-Driven Architecture:
- Payment formats from playbook context.payment_config
- Bank details from context.payment_config.bank_accounts
- File settings from context.payment_config.file_settings
"""

from typing import Dict, Any, List, Optional
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


# Default payment file configuration
DEFAULT_FILE_CONFIG = {
    "nacha": {
        "immediate_origin": "1234567890",
        "immediate_destination": "0987654321",
        "company_name": "APEX PLATFORM",
        "company_id": "1234567890"
    },
    "wire": {
        "template": "standard",
        "include_purpose": True
    }
}


@register_factory("generate_payment")
async def generate_payment(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate payment file (context-driven).

    Context keys used:
        - payment_config: Payment file configuration
        - aws_resources: S3 bucket for file storage

    Input:
        payments: List of payments to include
        payment_method: Payment method (ach, wire, check)
        batch_date: Batch effective date

    Output:
        file_id: Generated file identifier
        file_type: Type of file generated
        file_location: S3 location of generated file
        payment_count: Number of payments included
        total_amount: Total payment amount
    """
    context = context or input_data.get('context', {})
    payment_config = context.get('payment_config', {})
    file_config = payment_config.get('file_settings', DEFAULT_FILE_CONFIG)
    aws_resources = context.get('aws_resources', {})

    logger.info(
        "Generate payment invoked",
        context_driven=bool(context)
    )

    # Get payments
    payments = input_data.get('payments', [])
    payment_method = input_data.get('payment_method', 'ach')
    batch_date = input_data.get('batch_date', datetime.utcnow().strftime('%Y-%m-%d'))

    # If single payment from upstream
    if not payments:
        payment_process = input_data.get('payment_process', {})
        if payment_process:
            payments = [{
                'payment_id': payment_process.get('payment_id'),
                'amount': payment_process.get('amount'),
                'vendor_name': payment_process.get('vendor_name'),
                'vendor_id': payment_process.get('vendor_id'),
                'bank_reference': payment_process.get('bank_reference')
            }]
            payment_method = payment_process.get('payment_method', payment_method)

    if not payments:
        return {
            "error": "No payments to process",
            "file_id": None,
            "context_driven": bool(context),
            "factory_id": "generate_payment",
            "factory_version": "2.0.0"
        }

    # Generate file based on payment method
    file_id = f"PAY-FILE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    if payment_method == 'ach':
        file_content, file_type = _generate_nacha_file(payments, batch_date, file_config.get('nacha', {}))
    elif payment_method == 'wire':
        file_content, file_type = _generate_wire_instructions(payments, file_config.get('wire', {}))
    else:
        file_content, file_type = _generate_check_register(payments)

    # Calculate totals
    total_amount = sum(p.get('amount', 0) for p in payments)

    # Store file to S3
    file_location = None
    s3_buckets = aws_resources.get('s3_buckets', {})
    payments_bucket = s3_buckets.get('payments') or s3_buckets.get('documents')

    if payments_bucket and AWS_ENABLED:
        file_location = await _store_payment_file(
            file_id=file_id,
            file_content=file_content,
            file_type=file_type,
            bucket=payments_bucket
        )

    return {
        "file_id": file_id,
        "file_type": file_type,
        "payment_method": payment_method,
        "file_location": file_location or f"local://{file_id}.{file_type}",
        "payment_count": len(payments),
        "total_amount": round(total_amount, 2),
        "batch_date": batch_date,
        "payments_included": [p.get('payment_id') for p in payments],
        "generated_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "generate_payment",
        "factory_version": "2.0.0",
        "context_keys_used": ["payment_config", "aws_resources"]
    }


def _generate_nacha_file(payments: List[Dict], batch_date: str, config: Dict) -> tuple:
    """Generate NACHA ACH file."""
    lines = []

    # File Header Record (1)
    file_creation_date = datetime.utcnow().strftime('%y%m%d')
    file_creation_time = datetime.utcnow().strftime('%H%M')

    lines.append(
        f"101 {config.get('immediate_destination', '0987654321'):>9}"
        f" {config.get('immediate_origin', '1234567890'):>10}"
        f"{file_creation_date}{file_creation_time}"
        f"A094101{'DEST BANK NAME':<23}{'ORIGIN BANK':<23}{'REF':>8}"
    )

    # Batch Header Record (5)
    batch_number = 1
    lines.append(
        f"5200{config.get('company_name', 'COMPANY'):<16}"
        f"{'':20}{config.get('company_id', '1234567890'):>10}"
        f"PPD{'PAYROLL':<10}{batch_date.replace('-', '')}"
        f"{batch_date.replace('-', '')}   1"
        f"{config.get('immediate_destination', '0987654321')[:8]:>8}"
        f"{batch_number:07d}"
    )

    # Entry Detail Records (6)
    entry_hash = 0
    total_debit = 0
    total_credit = 0

    for i, payment in enumerate(payments):
        amount_cents = int(payment.get('amount', 0) * 100)
        total_credit += amount_cents

        routing = payment.get('routing_number', '021000021')
        account = payment.get('account_number', '123456789')
        entry_hash += int(routing[:8])

        lines.append(
            f"622{routing:>9}{account:<17}{amount_cents:010d}"
            f"{payment.get('vendor_id', ''):<15}"
            f"{payment.get('vendor_name', '')[:22]:<22}"
            f"  {config.get('immediate_origin', '1234567890')[:8]:>8}"
            f"{i+1:07d}"
        )

    # Batch Control Record (8)
    lines.append(
        f"8200{len(payments):06d}{entry_hash % 10000000000:010d}"
        f"{total_debit:012d}{total_credit:012d}"
        f"{config.get('company_id', '1234567890'):>10}{'':25}"
        f"{config.get('immediate_destination', '0987654321')[:8]:>8}"
        f"{batch_number:07d}"
    )

    # File Control Record (9)
    lines.append(
        f"9{1:06d}{1:06d}{len(payments):08d}"
        f"{entry_hash % 10000000000:010d}"
        f"{total_debit:012d}{total_credit:012d}{'':39}"
    )

    # Pad to multiple of 10 lines
    while len(lines) % 10 != 0:
        lines.append('9' * 94)

    return '\n'.join(lines), 'ach'


def _generate_wire_instructions(payments: List[Dict], config: Dict) -> tuple:
    """Generate wire transfer instructions."""
    instructions = []

    for payment in payments:
        instruction = {
            "wire_id": f"WIRE-{uuid.uuid4().hex[:8].upper()}",
            "beneficiary_name": payment.get('vendor_name', ''),
            "beneficiary_account": payment.get('account_number', ''),
            "beneficiary_bank": payment.get('bank_name', ''),
            "beneficiary_bank_routing": payment.get('routing_number', ''),
            "amount": payment.get('amount', 0),
            "currency": "USD",
            "purpose": f"Payment for {payment.get('payment_id', 'invoice')}",
            "reference": payment.get('payment_id', '')
        }
        instructions.append(instruction)

    import json
    return json.dumps(instructions, indent=2), 'json'


def _generate_check_register(payments: List[Dict]) -> tuple:
    """Generate check register."""
    lines = ["Check Number,Date,Payee,Amount,Memo"]

    check_number = 10001
    for payment in payments:
        lines.append(
            f"{check_number},"
            f"{datetime.utcnow().strftime('%Y-%m-%d')},"
            f"\"{payment.get('vendor_name', '')}\","
            f"{payment.get('amount', 0):.2f},"
            f"\"{payment.get('payment_id', '')}\""
        )
        check_number += 1

    return '\n'.join(lines), 'csv'


async def _store_payment_file(file_id: str, file_content: str, file_type: str, bucket: str) -> Optional[str]:
    """Store payment file to S3."""
    try:
        s3 = boto3.client('s3')
        key = f"payment-files/{datetime.utcnow().strftime('%Y/%m/%d')}/{file_id}.{file_type}"

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_content,
            ContentType='text/plain' if file_type in ['ach', 'csv'] else 'application/json'
        )

        return f"s3://{bucket}/{key}"
    except Exception as e:
        logger.warning("Failed to store payment file", error=str(e))
        return None


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(generate_payment(event))
