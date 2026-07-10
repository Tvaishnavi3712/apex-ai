"""
Microsoft Teams Bot Handler
Conversational bot for document status, approvals, and notifications.

Features:
- Natural language commands (status, pending, approve, reject)
- Adaptive Card responses
- Proactive notifications
- File upload handling
- Integration with APEX workflows
"""

import os
import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

import boto3
import httpx

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

from .cards import (
    build_status_card,
    build_approval_card,
    build_pending_list_card,
    build_help_card,
    build_error_card,
    build_success_card
)

logger = logging.getLogger(__name__)


class TeamsBot:
    """Microsoft Teams Bot for APEX AI Platform."""

    def __init__(self):
        self.app_id = os.environ.get("MICROSOFT_APP_ID")
        self.app_password = os.environ.get("MICROSOFT_APP_PASSWORD")
        self.tenant_id = os.environ.get("TEAMS_TENANT_ID")
        self.apex_api_url = os.environ.get("APEX_API_URL", "http://localhost:8000")

        # Command patterns
        self.commands = {
            r"^status\s+(.+)$": self.handle_status,
            r"^pending(\s+.*)?$": self.handle_pending,
            r"^approve\s+(.+)$": self.handle_approve,
            r"^reject\s+(.+?)(?:\s+(.+))?$": self.handle_reject,
            r"^search\s+(.+)$": self.handle_search,
            r"^help$": self.handle_help,
        }

    async def get_access_token(self) -> str:
        """Get Azure AD access token for Bot Framework."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.app_id,
                    "client_secret": self.app_password,
                    "scope": "https://api.botframework.com/.default"
                }
            )
            response.raise_for_status()
            return response.json()["access_token"]

    async def process_activity(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming activity from Teams."""

        activity_type = activity.get("type")

        if activity_type == "message":
            return await self.handle_message(activity)
        elif activity_type == "invoke":
            return await self.handle_invoke(activity)
        elif activity_type == "conversationUpdate":
            return await self.handle_conversation_update(activity)

        return {"type": "message", "text": "Activity type not supported"}

    async def handle_message(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming message from user."""

        text = activity.get("text", "").strip()
        user_id = activity.get("from", {}).get("id")

        # Remove bot mention if present
        text = re.sub(r"<at>.*?</at>\s*", "", text).strip().lower()

        # Check for file attachments
        attachments = activity.get("attachments", [])
        if attachments:
            return await self.handle_file_upload(activity, attachments)

        # Match command patterns
        for pattern, handler in self.commands.items():
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return await handler(activity, match.groups(), user_id)

        # No command matched - try natural language understanding
        return await self.handle_natural_language(activity, text, user_id)

    async def handle_status(
        self,
        activity: Dict,
        args: tuple,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle status command."""

        doc_id = args[0].strip().upper() if args[0] else ""

        if not doc_id:
            return {
                "type": "message",
                "text": "Please provide a document ID. Example: `status INV-2024-0892`"
            }

        # Query APEX API for document
        doc = await self.get_document(doc_id)

        if not doc:
            return {
                "type": "message",
                "text": f"Document `{doc_id}` not found. Please check the ID and try again."
            }

        # Build status card
        card = build_status_card(doc)

        return {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        }

    async def handle_pending(
        self,
        activity: Dict,
        args: tuple,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle pending approvals command."""

        # Get pending approvals for user
        pending = await self.get_pending_approvals(user_id)

        if not pending:
            return {
                "type": "message",
                "text": ":tada: You have no pending approvals!"
            }

        # Build pending list card
        card = build_pending_list_card(pending)

        return {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        }

    async def handle_approve(
        self,
        activity: Dict,
        args: tuple,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle approve command."""

        doc_id = args[0].strip().upper() if args[0] else ""

        if not doc_id:
            return {
                "type": "message",
                "text": "Please provide a document ID. Example: `approve INV-2024-0892`"
            }

        # Process approval
        result = await self.process_approval(doc_id, user_id, True)

        if result.get("success"):
            card = build_success_card(
                f"Document `{doc_id}` Approved",
                f"Successfully approved by you at {datetime.utcnow().strftime('%H:%M UTC')}"
            )
        else:
            card = build_error_card(
                "Approval Failed",
                result.get("error", "Unknown error occurred")
            )

        return {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        }

    async def handle_reject(
        self,
        activity: Dict,
        args: tuple,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle reject command."""

        doc_id = args[0].strip().upper() if args[0] else ""
        reason = args[1].strip() if len(args) > 1 and args[1] else "No reason provided"

        if not doc_id:
            return {
                "type": "message",
                "text": "Please provide a document ID. Example: `reject INV-2024-0892 duplicate invoice`"
            }

        # Process rejection
        result = await self.process_approval(doc_id, user_id, False, reason)

        if result.get("success"):
            return {
                "type": "message",
                "text": f":x: Document `{doc_id}` has been rejected.\nReason: {reason}"
            }
        else:
            return {
                "type": "message",
                "text": f":warning: Could not reject `{doc_id}`: {result.get('error')}"
            }

    async def handle_search(
        self,
        activity: Dict,
        args: tuple,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle search command."""

        query = args[0].strip() if args[0] else ""

        if not query:
            return {
                "type": "message",
                "text": "Please provide a search query. Example: `search invoices from Acme`"
            }

        # Search documents
        results = await self.search_documents(query)

        if not results:
            return {
                "type": "message",
                "text": f"No documents found matching: {query}"
            }

        # Format results
        text = f"**Found {len(results)} document(s):**\n\n"
        for doc in results[:10]:
            text += f"- `{doc['document_id']}` | {doc.get('document_type', 'Unknown')} | {doc.get('status', 'Unknown')}\n"

        return {"type": "message", "text": text}

    async def handle_help(
        self,
        activity: Dict,
        args: tuple,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle help command."""

        card = build_help_card()

        return {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": card
            }]
        }

    async def handle_natural_language(
        self,
        activity: Dict,
        text: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Handle natural language queries using intent classification."""

        # Simple keyword-based intent detection
        text_lower = text.lower()

        if any(word in text_lower for word in ["status", "where", "check", "find"]):
            # Try to extract document ID
            doc_match = re.search(r"([A-Z]{2,4}-\d{4}-\d{4})", text.upper())
            if doc_match:
                return await self.handle_status(activity, (doc_match.group(1),), user_id)

        if any(word in text_lower for word in ["pending", "approval", "waiting", "queue"]):
            return await self.handle_pending(activity, (None,), user_id)

        if any(word in text_lower for word in ["approve", "accept", "confirm"]):
            doc_match = re.search(r"([A-Z]{2,4}-\d{4}-\d{4})", text.upper())
            if doc_match:
                return await self.handle_approve(activity, (doc_match.group(1),), user_id)

        # Default to help
        return await self.handle_help(activity, (), user_id)

    async def handle_file_upload(
        self,
        activity: Dict,
        attachments: List[Dict]
    ) -> Dict[str, Any]:
        """Handle file uploads from Teams."""

        processed = []

        for attachment in attachments:
            content_type = attachment.get("contentType", "")

            # Check if it's a supported document type
            if content_type in ["application/pdf", "image/png", "image/jpeg"]:
                # Download and process
                result = await self.process_uploaded_file(
                    attachment,
                    activity.get("from", {}).get("id")
                )
                processed.append(result)

        if processed:
            return {
                "type": "message",
                "text": f":white_check_mark: Received {len(processed)} document(s) for processing.\n" +
                        "\n".join([f"- `{p['document_id']}`: {p['status']}" for p in processed])
            }

        return {
            "type": "message",
            "text": ":warning: No supported documents found. Please upload PDF, PNG, or JPEG files."
        }

    async def handle_invoke(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Handle invoke activities (button clicks, card actions)."""

        invoke_name = activity.get("name", "")
        value = activity.get("value", {})

        if invoke_name == "adaptiveCard/action":
            action = value.get("action", {})
            action_type = action.get("type", "")
            data = action.get("data", {})

            if action_type == "Action.Submit":
                return await self.handle_card_action(data, activity)

        return {"status": 200}

    async def handle_card_action(
        self,
        data: Dict[str, Any],
        activity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle adaptive card action submissions."""

        action = data.get("action", "")
        doc_id = data.get("document_id", "")
        user_id = activity.get("from", {}).get("id")

        if action == "approve":
            result = await self.process_approval(doc_id, user_id, True)
            return {"status": 200, "body": {"message": "Approved"}}

        elif action == "reject":
            result = await self.process_approval(doc_id, user_id, False)
            return {"status": 200, "body": {"message": "Rejected"}}

        elif action == "view":
            # Return URL to open in browser
            return {
                "status": 200,
                "body": {
                    "type": "openUrl",
                    "value": f"https://apex.company.com/documents/{doc_id}"
                }
            }

        return {"status": 200}

    async def handle_conversation_update(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Handle conversation update (bot added to conversation)."""

        members_added = activity.get("membersAdded", [])
        bot_id = activity.get("recipient", {}).get("id")

        for member in members_added:
            if member.get("id") == bot_id:
                # Bot was added - send welcome message
                return {
                    "type": "message",
                    "text": (
                        ":wave: **Welcome to APEX AI!**\n\n"
                        "I can help you with document processing. Try these commands:\n\n"
                        "- `status INV-2024-0892` - Check document status\n"
                        "- `pending` - View your pending approvals\n"
                        "- `approve INV-2024-0892` - Approve a document\n"
                        "- `help` - See all commands\n\n"
                        "You can also upload documents directly to this chat!"
                    )
                }

        return {}

    # API helper methods
    async def get_document(self, doc_id: str) -> Optional[Dict]:
        """Get document from APEX API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.apex_api_url}/api/documents/{doc_id}"
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Error getting document: {e}")
        return None

    async def get_pending_approvals(self, user_id: str) -> List[Dict]:
        """Get pending approvals for user."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.apex_api_url}/api/work-items",
                    params={
                        "status": "pending_approval",
                        "assigned_to": user_id,
                        "limit": 10
                    }
                )
                if response.status_code == 200:
                    return response.json().get("items", [])
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
        return []

    async def process_approval(
        self,
        doc_id: str,
        user_id: str,
        approved: bool,
        reason: str = None
    ) -> Dict:
        """Process document approval/rejection."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.apex_api_url}/api/work-items/{doc_id}/approve",
                    json={
                        "approved": approved,
                        "approved_by": user_id,
                        "reason": reason,
                        "channel": "teams"
                    }
                )
                return response.json()
        except Exception as e:
            logger.error(f"Error processing approval: {e}")
            return {"success": False, "error": str(e)}

    async def search_documents(self, query: str) -> List[Dict]:
        """Search documents."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.apex_api_url}/api/documents/search",
                    params={"q": query, "limit": 10}
                )
                if response.status_code == 200:
                    return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
        return []

    async def process_uploaded_file(
        self,
        attachment: Dict,
        user_id: str
    ) -> Dict:
        """Process an uploaded file."""

        from datetime import datetime
        import uuid

        doc_id = f"TEAMS-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

        # In production, download file and upload to S3
        # For now, create work item reference

        return {
            "document_id": doc_id,
            "status": "processing",
            "filename": attachment.get("name", "unknown")
        }

    async def send_proactive_message(
        self,
        conversation_reference: Dict,
        message: str = None,
        card: Dict = None
    ) -> bool:
        """Send a proactive message to a user."""

        try:
            token = await self.get_access_token()
            service_url = conversation_reference.get("serviceUrl", "")
            conversation_id = conversation_reference.get("conversation", {}).get("id", "")

            async with httpx.AsyncClient() as client:
                payload = {"type": "message"}

                if card:
                    payload["attachments"] = [{
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card
                    }]
                else:
                    payload["text"] = message

                response = await client.post(
                    f"{service_url}/v3/conversations/{conversation_id}/activities",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"Error sending proactive message: {e}")
            return False


# Global bot instance
bot = TeamsBot()


@apex_action(
    action_id="teams_message",
    name="Teams Message",
    description="Send message or card to Microsoft Teams",
    category="integrations",
    version="1.0.0"
)
async def handler(context: ActionContext) -> ActionResult:
    """
    Send a message to Microsoft Teams.

    Input:
        conversation_reference: Dict - Teams conversation reference
        message: str - Text message (optional)
        card: Dict - Adaptive card (optional)

    Output:
        success: bool
        message_id: str
    """
    try:
        result = await bot.send_proactive_message(
            conversation_reference=context.input["conversation_reference"],
            message=context.input.get("message"),
            card=context.input.get("card")
        )

        return ActionResult(success=result)

    except Exception as e:
        return ActionResult(success=False, error=str(e))


async def send_adaptive_card(
    conversation_reference: Dict,
    card: Dict
) -> bool:
    """Convenience function to send an adaptive card."""
    return await bot.send_proactive_message(conversation_reference, card=card)


# Lambda handler
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for Teams webhook."""

    # Parse body
    body = event.get("body", "{}")
    if isinstance(body, str):
        body = json.loads(body)

    # Process activity
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        response = loop.run_until_complete(bot.process_activity(body))

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response)
        }

    except Exception as e:
        logger.error(f"Error processing Teams activity: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    finally:
        loop.close()
