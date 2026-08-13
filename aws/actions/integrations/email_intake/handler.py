"""
Email Intake Parser Action Handler
Parses incoming emails from AWS SES and routes documents to APEX playbooks.

Features:
- Parse emails received via AWS SES
- Extract document attachments (PDF, images)
- Route to appropriate playbook based on recipient address
- Send confirmation emails to senders
- Create work items for processing
"""

import os
import json
import logging
import email
import re
import uuid
from email import policy
from email.parser import BytesParser
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

# Import APEX SDK if available
try:
    from apex_sdk import apex_action, ActionContext, ActionResult
except ImportError:
    def apex_action(**kwargs):
        def decorator(func):
            func._apex_action = kwargs
            return func
        return decorator

    class ActionContext:
        def __init__(self, input_data: Dict[str, Any]):
            self.input = input_data

    class ActionResult:
        def __init__(self, success: bool, output: Dict = None, error: str = None):
            self.success = success
            self.output = output or {}
            self.error = error

logger = logging.getLogger(__name__)

# Initialize AWS clients
s3 = boto3.client("s3")
ses = boto3.client("ses")
dynamodb = boto3.resource("dynamodb")


# Email routing configuration
ROUTING_CONFIG = {
    "invoices": {
        "document_type": "invoice",
        "playbook": "invoice_processing",
        "agent": "InvoiceBot"
    },
    "claims": {
        "document_type": "healthcare_claim",
        "playbook": "claims_adjudication",
        "agent": "ClaimsBot"
    },
    "po": {
        "document_type": "purchase_order",
        "playbook": "po_processing",
        "agent": "POBot"
    },
    "hr": {
        "document_type": "resume",
        "playbook": "resume_screening",
        "agent": "TalentBot"
    },
    "expenses": {
        "document_type": "expense_report",
        "playbook": "expense_processing",
        "agent": "ExpenseBot"
    },
    "docs": {
        "document_type": "auto_detect",
        "playbook": "document_triage",
        "agent": "TriageBot"
    }
}

# Supported attachment types
SUPPORTED_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/tiff": ".tiff",
    "image/tif": ".tif"
}


@apex_action(
    action_id="email_intake",
    name="Email Intake Parser",
    description="Parse incoming emails and route documents to playbooks",
    category="integrations",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "bucket": {"type": "string", "description": "S3 bucket containing email"},
            "key": {"type": "string", "description": "S3 key for email object"}
        },
        "required": ["bucket", "key"]
    }
)
async def handler(context: ActionContext) -> ActionResult:
    """
    Parse email from S3 and create APEX work items.

    Args:
        context: ActionContext with S3 location of email

    Returns:
        ActionResult with created work items and documents
    """
    bucket = context.input["bucket"]
    key = context.input["key"]

    try:
        # Download email from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        raw_email = response["Body"].read()

        # Parse email
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
        email_data = extract_email_metadata(msg)

        logger.info(f"Processing email from {email_data['from_email']} to {email_data['to_email']}")

        # Determine routing based on recipient
        routing = determine_routing(email_data["to_email"])

        # Extract attachments
        attachments = extract_and_upload_attachments(msg, bucket, email_data)

        if not attachments:
            # No attachments found
            await send_no_attachment_reply(email_data)
            return ActionResult(
                success=False,
                error="No document attachments found in email",
                output={"email_from": email_data["from_email"]}
            )

        # Create work items for each attachment
        work_items = []
        for attachment in attachments:
            work_item = create_work_item(attachment, email_data, routing)
            work_items.append(work_item)

            logger.info(f"Created work item {work_item['document_id']} for {attachment['filename']}")

        # Send confirmation email
        await send_confirmation_email(email_data, work_items)

        return ActionResult(
            success=True,
            output={
                "work_items": work_items,
                "documents": attachments,
                "email_from": email_data["from_email"],
                "routing": routing,
                "sender_notified": True
            }
        )

    except Exception as e:
        logger.error(f"Error processing email: {e}")
        return ActionResult(success=False, error=str(e))


def extract_email_metadata(msg: email.message.Message) -> Dict[str, Any]:
    """Extract metadata from parsed email message."""

    from_header = msg.get("From", "")
    to_header = msg.get("To", "")

    return {
        "message_id": msg.get("Message-ID", ""),
        "from": from_header,
        "from_email": extract_email_address(from_header),
        "from_name": extract_name_from_header(from_header),
        "to": to_header,
        "to_email": extract_email_address(to_header),
        "subject": msg.get("Subject", "(No Subject)"),
        "date": msg.get("Date", ""),
        "body": get_email_body(msg),
        "reply_to": msg.get("Reply-To") or from_header,
        "references": msg.get("References", ""),
        "in_reply_to": msg.get("In-Reply-To", "")
    }


def extract_email_address(header: str) -> str:
    """Extract email address from header string."""
    match = re.search(r"[\w\.\-\+]+@[\w\.\-]+\.\w+", header)
    return match.group(0).lower() if match else header.lower()


def extract_name_from_header(header: str) -> str:
    """Extract name from email header."""
    # Try to get name from "Name <email@example.com>" format
    match = re.match(r'^"?([^"<]+)"?\s*<', header)
    if match:
        return match.group(1).strip()
    return ""


def get_email_body(msg: email.message.Message) -> str:
    """Extract plain text body from email."""

    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            # Skip attachments
            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain":
                try:
                    body = part.get_content()
                    break
                except Exception:
                    pass
            elif content_type == "text/html" and not body:
                # Fallback to HTML if no plain text
                try:
                    html_content = part.get_content()
                    # Simple HTML stripping
                    body = re.sub(r"<[^>]+>", "", html_content)
                except Exception:
                    pass
    else:
        try:
            body = msg.get_content()
        except Exception:
            pass

    return body.strip() if body else ""


def determine_routing(to_address: str) -> Dict[str, str]:
    """Determine playbook routing based on recipient email address."""

    # Extract local part (before @)
    local_part = to_address.split("@")[0].lower()

    # Remove any plus addressing (e.g., invoices+vendor123@)
    local_part = local_part.split("+")[0]

    if local_part in ROUTING_CONFIG:
        return ROUTING_CONFIG[local_part]

    # Default routing
    return ROUTING_CONFIG.get("docs", {
        "document_type": "auto_detect",
        "playbook": "document_triage",
        "agent": "TriageBot"
    })


def extract_and_upload_attachments(
    msg: email.message.Message,
    bucket: str,
    email_data: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Extract attachments from email and upload to S3."""

    attachments = []
    document_bucket = os.environ.get("DOCUMENT_BUCKET", bucket)

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))

        if "attachment" not in content_disposition:
            continue

        filename = part.get_filename()
        if not filename:
            continue

        content_type = part.get_content_type()

        # Check if supported type
        if content_type not in SUPPORTED_TYPES:
            logger.info(f"Skipping unsupported attachment type: {content_type}")
            continue

        # Generate document ID
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8].upper()
        doc_id = f"EMAIL-{timestamp}-{unique_id}"

        # Clean filename
        safe_filename = re.sub(r"[^\w\.\-]", "_", filename)

        # S3 key
        s3_key = f"inbox/{doc_id}/{safe_filename}"

        try:
            # Get content
            content = part.get_payload(decode=True)

            if not content:
                continue

            # Upload to S3
            s3.put_object(
                Bucket=document_bucket,
                Key=s3_key,
                Body=content,
                ContentType=content_type,
                Metadata={
                    "document_id": doc_id,
                    "original_filename": filename,
                    "source": "email",
                    "from_email": email_data["from_email"],
                    "subject": email_data["subject"][:256]  # Metadata limit
                }
            )

            attachments.append({
                "document_id": doc_id,
                "filename": filename,
                "safe_filename": safe_filename,
                "s3_bucket": document_bucket,
                "s3_key": s3_key,
                "content_type": content_type,
                "size_bytes": len(content)
            })

            logger.info(f"Uploaded attachment: {doc_id} - {filename}")

        except Exception as e:
            logger.error(f"Error uploading attachment {filename}: {e}")

    return attachments


def create_work_item(
    attachment: Dict[str, Any],
    email_data: Dict[str, Any],
    routing: Dict[str, str]
) -> Dict[str, Any]:
    """Create APEX work item for document."""

    work_items_table = os.environ.get("WORK_ITEMS_TABLE", "apex-work-items")
    table = dynamodb.Table(work_items_table)

    work_item = {
        "document_id": attachment["document_id"],
        "document_type": routing["document_type"],
        "playbook": routing["playbook"],
        "assigned_agent": routing["agent"],
        "status": "pending",
        "source": "email",
        "source_details": {
            "from_email": email_data["from_email"],
            "from_name": email_data["from_name"],
            "subject": email_data["subject"],
            "message_id": email_data["message_id"],
            "received_date": email_data["date"]
        },
        "s3_location": {
            "bucket": attachment["s3_bucket"],
            "key": attachment["s3_key"]
        },
        "original_filename": attachment["filename"],
        "content_type": attachment["content_type"],
        "size_bytes": attachment["size_bytes"],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        table.put_item(Item=work_item)
    except Exception as e:
        logger.error(f"Error creating work item: {e}")

    return work_item


async def send_confirmation_email(
    email_data: Dict[str, Any],
    work_items: List[Dict[str, Any]]
) -> None:
    """Send confirmation email to sender."""

    from_address = os.environ.get("NOTIFICATION_FROM_EMAIL", "noreply@apex.company.com")
    apex_url = os.environ.get("APEX_URL", "https://apex.company.com")

    # Format document list
    doc_list = "\n".join([
        f"  - {item['document_id']}: {item.get('original_filename', 'document')}"
        for item in work_items
    ])

    # Primary reference ID
    primary_ref = work_items[0]["document_id"] if work_items else "N/A"

    body_text = f"""
Thank you for your submission to APEX AI Platform.

We have received the following document(s) for processing:

{doc_list}

Document Type: {work_items[0].get('document_type', 'Auto-detect').replace('_', ' ').title()}
Processing Agent: {work_items[0].get('assigned_agent', 'Auto-assigned')}

You can track the status of your documents at:
{apex_url}/status?ref={primary_ref}

Reference Number: {primary_ref}

If you have any questions, please contact support@company.com.

---
This is an automated message from APEX AI Platform.
Please do not reply directly to this email.

CBTS - Transforming Documents into Decisions
""".strip()

    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
        .document-list {{ background: white; padding: 15px; border-radius: 4px; margin: 15px 0; }}
        .document-item {{ padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
        .document-item:last-child {{ border-bottom: none; }}
        .btn {{ display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
        .footer {{ text-align: center; padding: 15px; color: #6b7280; font-size: 12px; }}
        .ref {{ font-family: monospace; background: #e5e7eb; padding: 2px 6px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">Document Received</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">APEX AI Platform</p>
        </div>
        <div class="content">
            <p>Thank you for your submission. We have received the following document(s) for processing:</p>

            <div class="document-list">
                {''.join([f'<div class="document-item"><strong>{item["document_id"]}</strong><br/><small>{item.get("original_filename", "document")}</small></div>' for item in work_items])}
            </div>

            <p>
                <strong>Document Type:</strong> {work_items[0].get('document_type', 'Auto-detect').replace('_', ' ').title()}<br/>
                <strong>Processing Agent:</strong> {work_items[0].get('assigned_agent', 'Auto-assigned')}<br/>
                <strong>Reference:</strong> <span class="ref">{primary_ref}</span>
            </p>

            <a href="{apex_url}/status?ref={primary_ref}" class="btn">Track Status</a>
        </div>
        <div class="footer">
            <p>This is an automated message from APEX AI Platform.<br/>
            Please do not reply directly to this email.</p>
            <p><strong>CBTS</strong> - Transforming Documents into Decisions</p>
        </div>
    </div>
</body>
</html>
"""

    try:
        ses.send_email(
            Source=from_address,
            Destination={
                "ToAddresses": [email_data["from_email"]]
            },
            Message={
                "Subject": {
                    "Data": f"Document Received: {email_data['subject'][:50]}",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": body_text,
                        "Charset": "UTF-8"
                    },
                    "Html": {
                        "Data": body_html,
                        "Charset": "UTF-8"
                    }
                }
            },
            ReplyToAddresses=[os.environ.get("SUPPORT_EMAIL", "support@company.com")]
        )

        logger.info(f"Confirmation email sent to {email_data['from_email']}")

    except ClientError as e:
        logger.error(f"Error sending confirmation email: {e}")


async def send_no_attachment_reply(email_data: Dict[str, Any]) -> None:
    """Send reply when no supported attachments found."""

    from_address = os.environ.get("NOTIFICATION_FROM_EMAIL", "noreply@apex.company.com")

    body_text = f"""
Thank you for contacting APEX AI Platform.

Unfortunately, we could not find any supported document attachments in your email.

Supported formats:
  - PDF documents (.pdf)
  - Images: PNG (.png), JPEG (.jpg, .jpeg), TIFF (.tiff, .tif)

Please ensure:
  - Documents are attached to the email (not embedded in the body)
  - Each document is under 25MB
  - Files are in a supported format

If you believe this is an error, please contact support@company.com.

---
This is an automated message from APEX AI Platform.

CBTS - Transforming Documents into Decisions
""".strip()

    try:
        ses.send_email(
            Source=from_address,
            Destination={
                "ToAddresses": [email_data["from_email"]]
            },
            Message={
                "Subject": {
                    "Data": f"Re: {email_data['subject'][:50]} - No Documents Found",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": body_text,
                        "Charset": "UTF-8"
                    }
                }
            }
        )

        logger.info(f"No-attachment reply sent to {email_data['from_email']}")

    except ClientError as e:
        logger.error(f"Error sending no-attachment reply: {e}")


def parse_email(raw_email: bytes) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Parse raw email bytes and extract metadata and attachment info.

    Returns:
        Tuple of (email_metadata, attachment_info_list)
    """
    msg = BytesParser(policy=policy.default).parsebytes(raw_email)
    email_data = extract_email_metadata(msg)

    attachments = []
    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition", ""))

        if "attachment" in content_disposition:
            filename = part.get_filename()
            content_type = part.get_content_type()

            if filename and content_type in SUPPORTED_TYPES:
                attachments.append({
                    "filename": filename,
                    "content_type": content_type,
                    "size_bytes": len(part.get_payload(decode=True) or b"")
                })

    return email_data, attachments


# Lambda handler for SES events
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for SES email receipts.

    Triggered by SES when email is received and stored in S3.
    """
    import asyncio

    logger.info(f"Email intake Lambda triggered")

    # Handle SES notification format
    records = event.get("Records", [])

    results = []

    for record in records:
        # SES stores email in S3
        ses_notification = record.get("ses", {})
        mail = ses_notification.get("mail", {})

        # Get S3 location from action (S3 action stores the email)
        receipt = ses_notification.get("receipt", {})
        action = receipt.get("action", {})

        bucket = action.get("bucketName") or os.environ.get("EMAIL_BUCKET")
        key = action.get("objectKey") or mail.get("messageId")

        if not bucket or not key:
            logger.error("Missing S3 bucket or key in SES notification")
            continue

        # Process the email
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            action_context = ActionContext({"bucket": bucket, "key": key})
            result = loop.run_until_complete(handler(action_context))
            results.append({
                "message_id": mail.get("messageId"),
                "success": result.success,
                "output": result.output if result.success else {"error": result.error}
            })

        except Exception as e:
            logger.error(f"Error processing email: {e}")
            results.append({
                "message_id": mail.get("messageId"),
                "success": False,
                "error": str(e)
            })

        finally:
            loop.close()

    return {
        "statusCode": 200,
        "body": json.dumps({
            "processed": len(results),
            "results": results
        })
    }
