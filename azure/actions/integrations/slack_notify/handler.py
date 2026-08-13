"""
Slack Notification Action Handler
Sends rich notifications to Slack channels/users with interactive components.

Features:
- Document status notifications
- Approval request cards with buttons
- Exception alerts with action buttons
- Thread replies for conversation context
- Channel routing based on document type
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.signature import SignatureVerifier

# Import APEX SDK if available, otherwise define minimal interface
try:
    from apex_sdk import apex_action, ActionContext, ActionResult
except ImportError:
    # Standalone mode - define minimal interfaces
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

# Initialize Slack client
def get_slack_client() -> WebClient:
    """Get Slack WebClient with bot token from environment or Secrets Manager."""
    token = os.environ.get("SLACK_BOT_TOKEN")

    if not token:
        # Try Azure Key Vault
        try:
            secrets = boto3.client("secretsmanager")
            secret = secrets.get_secret_value(SecretId="apex/slack")
            token = json.loads(secret["SecretString"])["bot_token"]
        except Exception as e:
            logger.error(f"Failed to get Slack token: {e}")
            raise ValueError("SLACK_BOT_TOKEN not configured")

    return WebClient(token=token)


@apex_action(
    action_id="slack_notify",
    name="Slack Notification",
    description="Send rich notifications to Slack channels or users",
    category="integrations",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "channel": {"type": "string", "description": "Channel ID or user ID"},
            "notification_type": {"type": "string", "enum": ["status", "approval", "exception", "custom"]},
            "document_id": {"type": "string"},
            "title": {"type": "string"},
            "message": {"type": "string"},
            "fields": {"type": "array", "items": {"type": "object"}},
            "actions": {"type": "array", "items": {"type": "object"}},
            "thread_ts": {"type": "string"},
            "metadata": {"type": "object"}
        },
        "required": ["channel", "notification_type", "title"]
    }
)
async def handler(context: ActionContext) -> ActionResult:
    """
    Send a Slack notification with optional interactive buttons.

    Args:
        context: ActionContext with input parameters

    Returns:
        ActionResult with message timestamp and channel
    """
    try:
        client = get_slack_client()

        # Build Block Kit message
        blocks = build_notification_blocks(
            notification_type=context.input.get("notification_type", "status"),
            title=context.input.get("title", "APEX Notification"),
            message=context.input.get("message", ""),
            fields=context.input.get("fields", []),
            actions=context.input.get("actions", []),
            document_id=context.input.get("document_id", ""),
            metadata=context.input.get("metadata", {})
        )

        # Send message
        response = client.chat_postMessage(
            channel=context.input["channel"],
            blocks=blocks,
            text=context.input.get("title", "APEX Notification"),  # Fallback for notifications
            thread_ts=context.input.get("thread_ts"),
            unfurl_links=False,
            unfurl_media=False
        )

        logger.info(f"Slack message sent: {response['ts']} to {response['channel']}")

        return ActionResult(
            success=True,
            output={
                "message_ts": response["ts"],
                "channel": response["channel"],
                "permalink": response.get("permalink", "")
            }
        )

    except SlackApiError as e:
        logger.error(f"Slack API error: {e.response['error']}")
        return ActionResult(
            success=False,
            error=f"Slack API error: {e.response['error']}"
        )
    except Exception as e:
        logger.error(f"Error sending Slack notification: {e}")
        return ActionResult(
            success=False,
            error=str(e)
        )


def build_notification_blocks(
    notification_type: str,
    title: str,
    message: str,
    fields: List[Dict],
    actions: List[Dict],
    document_id: str,
    metadata: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Build Slack Block Kit blocks for notification."""

    # Emoji mapping by notification type
    emoji_map = {
        "status": ":white_check_mark:",
        "approval": ":bell:",
        "exception": ":warning:",
        "error": ":x:",
        "custom": ":page_facing_up:"
    }

    # Color mapping (for attachments if needed)
    color_map = {
        "status": "#36a64f",      # Green
        "approval": "#2196F3",    # Blue
        "exception": "#ff9800",   # Orange
        "error": "#f44336",       # Red
        "custom": "#9c27b0"       # Purple
    }

    blocks = []

    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"{emoji_map.get(notification_type, ':robot_face:')} {title}",
            "emoji": True
        }
    })

    # Main message
    if message:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        })

    # Fields (displayed in two columns)
    if fields:
        field_blocks = []
        for field in fields[:10]:  # Slack limit
            field_blocks.append({
                "type": "mrkdwn",
                "text": f"*{field.get('label', 'Field')}*\n{field.get('value', 'N/A')}"
            })

        # Split into sections of 2 fields each (Slack's preferred layout)
        for i in range(0, len(field_blocks), 2):
            section = {
                "type": "section",
                "fields": field_blocks[i:i+2]
            }
            blocks.append(section)

    # Divider before actions
    if actions:
        blocks.append({"type": "divider"})

        # Action buttons
        action_elements = []
        for action in actions[:5]:  # Slack limit
            button = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": action.get("label", "Action"),
                    "emoji": True
                },
                "action_id": action.get("action_id", f"action_{len(action_elements)}"),
                "value": json.dumps({
                    "document_id": document_id,
                    "action": action.get("value", ""),
                    "metadata": metadata
                })
            }

            # Style (primary = green, danger = red)
            if action.get("style") in ["primary", "danger"]:
                button["style"] = action["style"]

            # URL button
            if action.get("url"):
                button["url"] = action["url"]
                button["type"] = "button"

            action_elements.append(button)

        blocks.append({
            "type": "actions",
            "elements": action_elements
        })

    # Context footer
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    context_parts = [f":robot_face: APEX AI Platform"]

    if document_id:
        context_parts.append(f"Document: `{document_id}`")

    context_parts.append(timestamp)

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": " | ".join(context_parts)
            }
        ]
    })

    return blocks


async def send_notification(
    channel: str,
    document_id: str,
    title: str,
    message: str,
    fields: List[Dict] = None,
    status: str = "success"
) -> ActionResult:
    """
    Convenience function to send a document status notification.

    Args:
        channel: Slack channel or user ID
        document_id: Document reference
        title: Notification title
        message: Main message body
        fields: Optional list of {label, value} fields
        status: Status type for styling (success, warning, error)
    """
    context = ActionContext({
        "channel": channel,
        "notification_type": "status" if status == "success" else "exception",
        "document_id": document_id,
        "title": title,
        "message": message,
        "fields": fields or []
    })

    return await handler(context)


async def send_approval_request(
    channel: str,
    document_id: str,
    document_type: str,
    amount: str,
    reason: str,
    requester: str,
    callback_id: str
) -> ActionResult:
    """
    Send an approval request with Approve/Reject buttons.

    Args:
        channel: Slack channel or user ID
        document_id: Document reference
        document_type: Type of document (Invoice, PO, etc.)
        amount: Amount requiring approval
        reason: Reason approval is needed
        requester: Who requested the approval
        callback_id: Callback ID for button handling
    """
    context = ActionContext({
        "channel": channel,
        "notification_type": "approval",
        "document_id": document_id,
        "title": f"Approval Required: {document_type}",
        "message": f"*{reason}*\nRequested by: {requester}",
        "fields": [
            {"label": "Document", "value": document_id},
            {"label": "Type", "value": document_type},
            {"label": "Amount", "value": amount},
            {"label": "Reason", "value": reason}
        ],
        "actions": [
            {
                "label": "Approve",
                "action_id": f"approve_{callback_id}",
                "value": "approve",
                "style": "primary"
            },
            {
                "label": "Reject",
                "action_id": f"reject_{callback_id}",
                "value": "reject",
                "style": "danger"
            },
            {
                "label": "View Document",
                "action_id": f"view_{callback_id}",
                "value": "view",
                "url": f"https://apex.company.com/documents/{document_id}"
            }
        ],
        "metadata": {
            "callback_id": callback_id,
            "document_type": document_type
        }
    })

    return await handler(context)


async def send_exception_alert(
    channel: str,
    document_id: str,
    exception_type: str,
    exception_reason: str,
    confidence_score: float = None,
    problem_fields: List[Dict] = None
) -> ActionResult:
    """
    Send an exception alert for documents requiring attention.

    Args:
        channel: Slack channel or user ID
        document_id: Document reference
        exception_type: Type of exception
        exception_reason: Human-readable reason
        confidence_score: Overall confidence score
        problem_fields: List of fields with issues
    """
    fields = [
        {"label": "Document", "value": document_id},
        {"label": "Exception Type", "value": exception_type},
        {"label": "Reason", "value": exception_reason}
    ]

    if confidence_score is not None:
        fields.append({
            "label": "Confidence",
            "value": f"{confidence_score * 100:.1f}%"
        })

    message = f":warning: *{exception_reason}*"

    if problem_fields:
        message += "\n\n*Problem Fields:*"
        for field in problem_fields[:5]:
            message += f"\n• `{field.get('name', 'Unknown')}`: {field.get('issue', 'Low confidence')}"

    context = ActionContext({
        "channel": channel,
        "notification_type": "exception",
        "document_id": document_id,
        "title": f"Processing Exception: {document_id}",
        "message": message,
        "fields": fields,
        "actions": [
            {
                "label": "Review",
                "action_id": f"review_{document_id}",
                "value": "review",
                "style": "primary"
            },
            {
                "label": "Override",
                "action_id": f"override_{document_id}",
                "value": "override"
            },
            {
                "label": "Reject",
                "action_id": f"reject_{document_id}",
                "value": "reject",
                "style": "danger"
            }
        ]
    })

    return await handler(context)


# Lambda handler for webhook events from Slack
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Azure Functions handler for Slack webhook events.
    Handles button clicks and interactive component callbacks.
    """
    # Verify Slack signature
    signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
    if signing_secret:
        verifier = SignatureVerifier(signing_secret)
        if not verifier.is_valid_request(event.get("body", ""), event.get("headers", {})):
            return {"statusCode": 401, "body": "Invalid signature"}

    # Parse body
    body = event.get("body", "{}")
    if isinstance(body, str):
        # Check if it's URL-encoded
        if body.startswith("payload="):
            import urllib.parse
            body = urllib.parse.unquote(body.replace("payload=", ""))
        body = json.loads(body)

    # Handle URL verification challenge
    if body.get("type") == "url_verification":
        return {
            "statusCode": 200,
            "body": json.dumps({"challenge": body.get("challenge")})
        }

    # Handle interactive components (button clicks)
    if body.get("type") == "block_actions":
        return handle_block_actions(body)

    # Handle view submissions (modals)
    if body.get("type") == "view_submission":
        return handle_view_submission(body)

    return {"statusCode": 200, "body": "OK"}


def handle_block_actions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle button clicks from Slack messages."""

    actions = payload.get("actions", [])
    user = payload.get("user", {})
    channel = payload.get("channel", {})
    message_ts = payload.get("message", {}).get("ts")

    for action in actions:
        action_id = action.get("action_id", "")
        value = action.get("value", "{}")

        try:
            value_data = json.loads(value)
        except json.JSONDecodeError:
            value_data = {"action": value}

        document_id = value_data.get("document_id", "")
        action_type = value_data.get("action", action_id.split("_")[0])

        logger.info(f"Slack action: {action_type} on {document_id} by {user.get('id')}")

        # Process the action
        if action_type == "approve":
            process_approval(document_id, user, True, channel.get("id"), message_ts)
        elif action_type == "reject":
            process_approval(document_id, user, False, channel.get("id"), message_ts)
        elif action_type == "review":
            # Open review modal or redirect
            pass
        elif action_type == "override":
            process_override(document_id, user, channel.get("id"), message_ts)

    return {"statusCode": 200, "body": ""}


def handle_view_submission(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle modal form submissions."""

    view = payload.get("view", {})
    user = payload.get("user", {})

    callback_id = view.get("callback_id", "")
    values = view.get("state", {}).get("values", {})

    logger.info(f"View submission: {callback_id} by {user.get('id')}")

    # Process based on callback_id
    # Implementation depends on specific modals defined

    return {"statusCode": 200, "body": ""}


def process_approval(
    document_id: str,
    user: Dict,
    approved: bool,
    channel_id: str,
    message_ts: str
):
    """Process an approval/rejection from Slack."""

    # Update the document status in APEX
    # This would call the APEX API or directly update Cosmos DB

    tables = get_table_resource()
    table = cosmos_db.Table(os.environ.get("WORK_ITEMS_TABLE", "apex-work-items"))

    try:
        table.update_item(
            Key={"document_id": document_id},
            UpdateExpression="SET #status = :status, approved_by = :user, approved_at = :time, approval_channel = :channel",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "approved" if approved else "rejected",
                ":user": user.get("id"),
                ":time": datetime.utcnow().isoformat(),
                ":channel": "slack"
            }
        )

        # Update the original message to show the action taken
        client = get_slack_client()
        action_text = "approved" if approved else "rejected"

        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=f"Document {document_id} was {action_text} by <@{user.get('id')}>",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":{'white_check_mark' if approved else 'x'}: Document `{document_id}` was *{action_text}* by <@{user.get('id')}>"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Processed at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
        )

    except Exception as e:
        logger.error(f"Error processing approval: {e}")


def process_override(document_id: str, user: Dict, channel_id: str, message_ts: str):
    """Process an override action from Slack."""

    # Mark document for manual override
    tables = get_table_resource()
    table = cosmos_db.Table(os.environ.get("WORK_ITEMS_TABLE", "apex-work-items"))

    try:
        table.update_item(
            Key={"document_id": document_id},
            UpdateExpression="SET #status = :status, overridden_by = :user, overridden_at = :time",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":status": "manual_override",
                ":user": user.get("id"),
                ":time": datetime.utcnow().isoformat()
            }
        )

        # Update message
        client = get_slack_client()
        client.chat_update(
            channel=channel_id,
            ts=message_ts,
            text=f"Document {document_id} marked for manual override by <@{user.get('id')}>",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":construction: Document `{document_id}` marked for *manual override* by <@{user.get('id')}>"
                    }
                }
            ]
        )

    except Exception as e:
        logger.error(f"Error processing override: {e}")
