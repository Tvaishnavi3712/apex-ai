"""
Email Parse - Small Factory
Extracts attachments and metadata from emails for document processing.
"""

from typing import Dict, Any, List
import re
import structlog
from services.small_factory import register_factory

logger = structlog.get_logger()

# Common attachment patterns
DOCUMENT_EXTENSIONS = {
    "invoice": [".pdf", ".png", ".jpg", ".jpeg"],
    "spreadsheet": [".xlsx", ".xls", ".csv"],
    "document": [".docx", ".doc", ".pdf"],
}


def extract_email_metadata(email_content: Dict[str, Any]) -> Dict[str, Any]:
    """Extract metadata from email."""
    return {
        "from": email_content.get("from", ""),
        "to": email_content.get("to", []),
        "cc": email_content.get("cc", []),
        "subject": email_content.get("subject", ""),
        "date": email_content.get("date", ""),
        "message_id": email_content.get("message_id", ""),
    }


def classify_attachment(filename: str) -> str:
    """Classify attachment by filename."""
    filename_lower = filename.lower()

    # Check for invoice indicators
    if any(word in filename_lower for word in ["invoice", "inv", "bill", "receipt"]):
        return "invoice"
    if any(word in filename_lower for word in ["po", "purchase", "order"]):
        return "purchase_order"
    if any(word in filename_lower for word in ["contract", "agreement", "terms"]):
        return "contract"
    if any(word in filename_lower for word in ["statement", "report"]):
        return "statement"

    # Default based on extension
    for ext in DOCUMENT_EXTENSIONS["invoice"]:
        if filename_lower.endswith(ext):
            return "document"

    return "unknown"


@register_factory("email_parse")
async def email_parse(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse email and extract attachments for processing.

    Input:
        email: Raw email content or parsed email object
        config.extract_body: Whether to extract email body
        config.classify_attachments: Auto-classify attachments

    Output:
        metadata: Email metadata (from, to, subject, date)
        body: Email body text (if extracted)
        attachments: List of attachments with classification
        primary_document: Main document to process
    """
    config = input_data.get('config', {})
    email = input_data.get('email', {})
    state = input_data.get('state', {})

    # Can also receive from state
    if not email:
        email = state.get('input', {}).get('email', {})

    extract_body = config.get('extract_body', True)
    classify_attachments = config.get('classify_attachments', True)

    # Extract metadata
    metadata = extract_email_metadata(email)

    # Extract body
    body = ""
    if extract_body:
        body = email.get('body', '')
        if isinstance(body, dict):
            body = body.get('text', '') or body.get('html', '')

    # Process attachments
    raw_attachments = email.get('attachments', [])
    attachments = []
    primary_document = None

    for i, att in enumerate(raw_attachments):
        filename = att.get('filename', f'attachment_{i}')
        content_type = att.get('content_type', 'application/octet-stream')
        size = att.get('size', 0)
        s3_uri = att.get('s3_uri', '')

        attachment_info = {
            "index": i,
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "s3_uri": s3_uri,
        }

        if classify_attachments:
            attachment_info["classification"] = classify_attachment(filename)

        attachments.append(attachment_info)

        # Select primary document (first invoice or PDF)
        if not primary_document:
            if attachment_info.get("classification") == "invoice":
                primary_document = attachment_info
            elif content_type == "application/pdf":
                primary_document = attachment_info

    # If no primary document, use first attachment
    if not primary_document and attachments:
        primary_document = attachments[0]

    # Extract sender domain for vendor matching
    sender_email = metadata.get("from", "")
    sender_domain = ""
    if "@" in sender_email:
        sender_domain = sender_email.split("@")[-1].strip(">").lower()

    return {
        "metadata": metadata,
        "body": body if extract_body else None,
        "attachments": attachments,
        "attachment_count": len(attachments),
        "primary_document": primary_document,
        "sender_domain": sender_domain,
        "has_invoice": any(a.get("classification") == "invoice" for a in attachments),
    }
