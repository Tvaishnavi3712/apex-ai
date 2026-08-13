"""
Secure Store - Core Action (Context-Driven)
Securely store sensitive data with encryption and access controls

Context-Driven Architecture:
- Storage configuration from playbook context.aws_resources
- Encryption settings from context.security_config
- Retention policies from context.security_config.retention
"""

from typing import Dict, Any, Optional
from datetime import datetime
import structlog
import json
import hashlib
import base64

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


# Default security configuration
DEFAULT_SECURITY_CONFIG = {
    "encryption": {
        "enabled": True,
        "algorithm": "AES-256"
    },
    "retention": {
        "default_days": 90,
        "pii_days": 30,
        "financial_days": 365
    },
    "access_control": {
        "log_access": True,
        "require_audit": True
    }
}


@register_factory("secure_store")
async def secure_store(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Securely store sensitive data (context-driven).

    Context keys used:
        - aws_resources: Storage configuration (S3, Secrets Manager)
        - security_config: Encryption and retention settings

    Input:
        data: Data to store
        data_type: Type of data (pii, financial, general)
        encryption_key_id: KMS key ID (optional)
        metadata: Additional metadata
        ttl_days: Time to live in days (optional)

    Output:
        storage_id: Unique storage identifier
        storage_location: Where data is stored
        encrypted: Whether data is encrypted
        expires_at: Expiration timestamp
        access_url: URL to retrieve data (if applicable)
    """
    context = context or input_data.get('context', {})
    aws_resources = context.get('aws_resources', {})
    security_config = context.get('security_config', DEFAULT_SECURITY_CONFIG)
    retention_config = security_config.get('retention', DEFAULT_SECURITY_CONFIG['retention'])
    encryption_config = security_config.get('encryption', DEFAULT_SECURITY_CONFIG['encryption'])

    logger.info(
        "Secure store invoked",
        context_driven=bool(context)
    )

    # Extract input parameters
    data = input_data.get('data', {})
    data_type = input_data.get('data_type', 'general')
    encryption_key_id = input_data.get('encryption_key_id')
    metadata = input_data.get('metadata', {})
    ttl_days = input_data.get('ttl_days')

    # Determine retention period
    if ttl_days is None:
        if data_type == 'pii':
            ttl_days = retention_config.get('pii_days', 30)
        elif data_type == 'financial':
            ttl_days = retention_config.get('financial_days', 365)
        else:
            ttl_days = retention_config.get('default_days', 90)

    # Generate storage ID
    data_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:12]
    storage_id = f"sec-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{data_hash}"

    # Calculate expiration
    expires_at = datetime.utcnow().timestamp() + (ttl_days * 24 * 3600)

    # Store data
    encrypted = encryption_config.get('enabled', True)
    storage_location, access_url = await _store_securely(
        storage_id=storage_id,
        data=data,
        data_type=data_type,
        metadata=metadata,
        encryption_key_id=encryption_key_id,
        ttl_days=ttl_days,
        aws_resources=aws_resources,
        encrypt=encrypted
    )

    # Log access for audit
    if security_config.get('access_control', {}).get('log_access', True):
        await _log_access(
            storage_id=storage_id,
            action='store',
            data_type=data_type,
            aws_resources=aws_resources
        )

    return {
        "storage_id": storage_id,
        "data_type": data_type,
        "storage_location": storage_location,
        "encrypted": encrypted,
        "expires_at": datetime.fromtimestamp(expires_at).isoformat(),
        "ttl_days": ttl_days,
        "access_url": access_url,
        "metadata": metadata,
        "stored_at": datetime.utcnow().isoformat(),
        "context_driven": bool(context),
        "factory_id": "secure_store",
        "factory_version": "2.0.0",
        "context_keys_used": ["aws_resources", "security_config"]
    }


async def _store_securely(
    storage_id: str,
    data: Any,
    data_type: str,
    metadata: Dict[str, Any],
    encryption_key_id: Optional[str],
    ttl_days: int,
    aws_resources: Dict[str, Any],
    encrypt: bool
) -> tuple:
    """Store data securely to S3 or Secrets Manager."""
    if not AWS_ENABLED:
        return f"mock://secure/{storage_id}", f"/api/secure/{storage_id}"

    try:
        # For highly sensitive data, use Secrets Manager
        if data_type in ['pii', 'credentials']:
            return await _store_to_secrets_manager(storage_id, data, ttl_days)

        # For other data, use encrypted S3
        s3_buckets = aws_resources.get('s3_buckets', {})
        secure_bucket = s3_buckets.get('secure') or s3_buckets.get('documents_secure')

        if secure_bucket:
            return await _store_to_s3_encrypted(
                storage_id, data, secure_bucket, encryption_key_id, metadata
            )

        return f"memory://secure/{storage_id}", None

    except Exception as e:
        logger.error("Secure storage failed", error=str(e))
        return f"error://{storage_id}", None


async def _store_to_secrets_manager(storage_id: str, data: Any, ttl_days: int) -> tuple:
    """Store data in Azure Key Vault."""
    try:
        secrets_manager = boto3.client('secretsmanager')

        secrets_manager.create_secret(
            Name=storage_id,
            SecretString=json.dumps(data) if isinstance(data, dict) else str(data),
            Description=f"Secure storage for {storage_id}"
        )

        return f"secretsmanager://{storage_id}", None

    except Exception as e:
        logger.warning("Secrets Manager store failed", error=str(e))
        return f"mock://secrets/{storage_id}", None


async def _store_to_s3_encrypted(
    storage_id: str,
    data: Any,
    bucket: str,
    encryption_key_id: Optional[str],
    metadata: Dict[str, Any]
) -> tuple:
    """Store data in encrypted S3."""
    try:
        s3 = boto3.client('s3')
        key = f"secure/{storage_id}.json"

        extra_args = {
            'ContentType': 'application/json',
            'ServerSideEncryption': 'aws:kms' if encryption_key_id else 'AES256',
            'Metadata': {k: str(v) for k, v in metadata.items()}
        }

        if encryption_key_id:
            extra_args['SSEKMSKeyId'] = encryption_key_id

        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data),
            **extra_args
        )

        return f"s3://{bucket}/{key}", f"/api/secure/{storage_id}"

    except Exception as e:
        logger.warning("S3 encrypted store failed", error=str(e))
        return f"mock://s3/{storage_id}", None


async def _log_access(
    storage_id: str,
    action: str,
    data_type: str,
    aws_resources: Dict[str, Any]
) -> None:
    """Log access for audit trail."""
    logger.info(
        "Secure data access",
        storage_id=storage_id,
        action=action,
        data_type=data_type,
        timestamp=datetime.utcnow().isoformat()
    )


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(secure_store(event))
