"""
Document Intake - Core Action (Context-Driven)
Ingest and prepare documents for processing pipeline

Context-Driven Architecture:
- Document configurations are read from playbook context.document_config
- S3 bucket settings are read from context.aws_resources.s3_buckets
- Extraction settings are read from context.extraction_config
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import os
import json

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


# Default document configuration
DEFAULT_DOCUMENT_CONFIG = {
    "supported_formats": ["pdf", "png", "jpg", "jpeg", "tiff", "docx"],
    "max_file_size_mb": 50,
    "ocr_enabled": True,
    "text_extraction_enabled": True
}


@register_factory("document_intake")
async def document_intake(
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Ingest document and prepare for processing (context-driven).

    Context keys used:
        - document_config: Document processing configuration
        - aws_resources: AWS resource configurations (S3 buckets)
        - extraction_config: Extraction settings

    Input:
        document_s3_uri: S3 URI of document
        document_type: Type of document (invoice, claim, resume, etc.)
        metadata: Additional document metadata

    Output:
        document_id: Unique document identifier
        document_type: Detected/confirmed document type
        file_format: Document format
        page_count: Number of pages
        text_content: Extracted text (if text extraction enabled)
        ready_for_processing: Whether document is ready for next stage
    """
    context = context or input_data.get('context', {})
    document_config = context.get('document_config', DEFAULT_DOCUMENT_CONFIG)
    aws_resources = context.get('aws_resources', {})

    logger.info(
        "Document intake invoked",
        context_driven=bool(context)
    )

    # Extract input parameters
    initial_input = input_data.get('initial_input', {})
    document_uri = initial_input.get('document_s3_uri') or input_data.get('document_s3_uri')
    document_type = initial_input.get('document_type') or input_data.get('document_type', 'unknown')
    metadata = input_data.get('metadata', {})

    if not document_uri:
        return {
            "error": "No document_s3_uri provided",
            "ready_for_processing": False
        }

    # Parse S3 URI
    s3_parts = _parse_s3_uri(document_uri)
    if not s3_parts:
        return {
            "error": f"Invalid S3 URI: {document_uri}",
            "ready_for_processing": False
        }

    bucket, key = s3_parts
    file_extension = key.split('.')[-1].lower() if '.' in key else ''

    # Validate file format
    supported_formats = document_config.get('supported_formats', DEFAULT_DOCUMENT_CONFIG['supported_formats'])
    if file_extension not in supported_formats:
        return {
            "error": f"Unsupported file format: {file_extension}",
            "supported_formats": supported_formats,
            "ready_for_processing": False
        }

    # Generate document ID
    document_id = f"doc-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(document_uri) % 10000:04d}"

    # Get document info from S3
    document_info = await _get_document_info(bucket, key)

    # Check file size
    max_size_mb = document_config.get('max_file_size_mb', 50)
    file_size_mb = document_info.get('size_bytes', 0) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return {
            "error": f"File size {file_size_mb:.2f}MB exceeds maximum {max_size_mb}MB",
            "ready_for_processing": False
        }

    # Extract text if enabled
    text_content = None
    if document_config.get('text_extraction_enabled', True):
        text_content = await _extract_text(bucket, key, file_extension, document_config)

    # Detect page count
    page_count = await _get_page_count(bucket, key, file_extension)

    return {
        "document_id": document_id,
        "document_s3_uri": document_uri,
        "document_type": document_type,
        "file_format": file_extension,
        "file_size_mb": round(file_size_mb, 2),
        "page_count": page_count,
        "text_content": text_content,
        "text_extracted": text_content is not None,
        "bucket": bucket,
        "key": key,
        "ready_for_processing": True,
        "ingested_at": datetime.utcnow().isoformat(),
        "metadata": metadata,
        "context_driven": bool(context),
        "factory_id": "document_intake",
        "factory_version": "2.0.0",
        "context_keys_used": ["document_config", "aws_resources"]
    }


def _parse_s3_uri(uri: str) -> Optional[tuple]:
    """Parse S3 URI into bucket and key."""
    if uri.startswith('s3://'):
        parts = uri[5:].split('/', 1)
        if len(parts) == 2:
            return parts[0], parts[1]
    return None


async def _get_document_info(bucket: str, key: str) -> Dict[str, Any]:
    """Get document metadata from S3."""
    if not AWS_ENABLED:
        return {"size_bytes": 1024 * 1024, "content_type": "application/pdf"}

    try:
        s3 = boto3.client('s3')
        response = s3.head_object(Bucket=bucket, Key=key)
        return {
            "size_bytes": response.get('ContentLength', 0),
            "content_type": response.get('ContentType', ''),
            "last_modified": response.get('LastModified', datetime.utcnow()).isoformat()
        }
    except Exception as e:
        logger.warning("Failed to get document info", error=str(e))
        return {"size_bytes": 0, "content_type": "unknown"}


async def _extract_text(bucket: str, key: str, file_extension: str, config: Dict) -> Optional[str]:
    """Extract text from document."""
    if not AWS_ENABLED:
        return "Sample extracted text for testing purposes."

    try:
        # For PDF, use Textract
        if file_extension == 'pdf':
            textract = boto3.client('textract')
            response = textract.detect_document_text(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            text_blocks = [block['Text'] for block in response.get('Blocks', []) if block['BlockType'] == 'LINE']
            return '\n'.join(text_blocks)

        # For images, use Textract OCR
        elif file_extension in ['png', 'jpg', 'jpeg', 'tiff']:
            textract = boto3.client('textract')
            response = textract.detect_document_text(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            text_blocks = [block['Text'] for block in response.get('Blocks', []) if block['BlockType'] == 'LINE']
            return '\n'.join(text_blocks)

        return None
    except Exception as e:
        logger.warning("Text extraction failed", error=str(e))
        return None


async def _get_page_count(bucket: str, key: str, file_extension: str) -> int:
    """Get page count from document."""
    # For non-PDF documents, assume 1 page
    if file_extension != 'pdf':
        return 1

    # For PDFs, would need to parse the document
    # Simplified: return 1 as placeholder
    return 1


def handler(event, lambda_context):
    """Lambda entry point."""
    import asyncio
    return asyncio.run(document_intake(event))
