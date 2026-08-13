"""
ServiceNow Integration Handler
Bidirectional integration with ServiceNow ITSM for document processing.

Features:
- Receive documents from ServiceNow tickets
- Process attachments through APEX playbooks
- Update ServiceNow records with results
- Add work notes and populate fields
- Support for multiple record types (incidents, requests, cases)
"""

import os
import json
import logging
import base64
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

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

logger = logging.getLogger(__name__)

# Initialize AWS clients
s3 = boto3.client("s3")
tables = get_table_resource()
secrets = boto3.client("secretsmanager")


class ServiceNowClient:
    """Client for ServiceNow REST API."""

    def __init__(self, instance_url: str = None, username: str = None, password: str = None):
        self.instance_url = instance_url or os.environ.get("SERVICENOW_INSTANCE")
        self.username = username or os.environ.get("SERVICENOW_USERNAME")
        self.password = password

        if not self.password:
            self.password = self._get_password_from_secrets()

        if not all([self.instance_url, self.username, self.password]):
            raise ValueError("ServiceNow credentials not configured")

    def _get_password_from_secrets(self) -> str:
        """Get password from Azure Key Vault."""
        try:
            secret = secrets.get_secret_value(SecretId="apex/servicenow")
            return json.loads(secret["SecretString"])["password"]
        except Exception as e:
            logger.error(f"Failed to get ServiceNow password: {e}")
            return os.environ.get("SERVICENOW_PASSWORD", "")

    async def get_record(self, table: str, sys_id: str) -> Optional[Dict]:
        """Get a record from ServiceNow."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.instance_url}/api/now/table/{table}/{sys_id}",
                auth=(self.username, self.password),
                headers={"Accept": "application/json"}
            )

            if response.status_code == 200:
                return response.json().get("result")
            return None

    async def update_record(
        self,
        table: str,
        sys_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a ServiceNow record."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.instance_url}/api/now/table/{table}/{sys_id}",
                auth=(self.username, self.password),
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                json=data
            )

            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "result": response.json().get("result") if response.status_code == 200 else None,
                "error": response.text if response.status_code != 200 else None
            }

    async def add_work_note(
        self,
        table: str,
        sys_id: str,
        note: str
    ) -> Dict[str, Any]:
        """Add a work note to a ServiceNow record."""
        return await self.update_record(table, sys_id, {"work_notes": note})

    async def add_comment(
        self,
        table: str,
        sys_id: str,
        comment: str
    ) -> Dict[str, Any]:
        """Add a customer-visible comment to a record."""
        return await self.update_record(table, sys_id, {"comments": comment})

    async def get_attachment(self, attachment_sys_id: str) -> Optional[bytes]:
        """Download attachment content from ServiceNow."""
        async with httpx.AsyncClient() as client:
            # Get attachment metadata
            meta_response = await client.get(
                f"{self.instance_url}/api/now/attachment/{attachment_sys_id}",
                auth=(self.username, self.password),
                headers={"Accept": "application/json"}
            )

            if meta_response.status_code != 200:
                return None

            # Download file content
            file_response = await client.get(
                f"{self.instance_url}/api/now/attachment/{attachment_sys_id}/file",
                auth=(self.username, self.password)
            )

            if file_response.status_code == 200:
                return file_response.content
            return None

    async def add_attachment(
        self,
        table: str,
        sys_id: str,
        filename: str,
        content: bytes,
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """Add an attachment to a ServiceNow record."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.instance_url}/api/now/attachment/file",
                auth=(self.username, self.password),
                params={
                    "table_name": table,
                    "table_sys_id": sys_id,
                    "file_name": filename
                },
                headers={"Content-Type": content_type},
                content=content
            )

            return {
                "success": response.status_code == 201,
                "result": response.json() if response.status_code == 201 else None,
                "error": response.text if response.status_code != 201 else None
            }


@apex_action(
    action_id="servicenow_update",
    name="ServiceNow Update",
    description="Update ServiceNow record with APEX processing results",
    category="integrations",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "instance": {"type": "string"},
            "table": {"type": "string"},
            "sys_id": {"type": "string"},
            "update_type": {"type": "string", "enum": ["work_note", "fields", "attachment", "comment"]},
            "data": {"type": "object"}
        },
        "required": ["table", "sys_id", "update_type", "data"]
    }
)
async def handler(context: ActionContext) -> ActionResult:
    """
    Update ServiceNow record with extraction results.

    Args:
        context: ActionContext with update parameters

    Returns:
        ActionResult with update status
    """
    try:
        client = ServiceNowClient(
            instance_url=context.input.get("instance")
        )

        table = context.input["table"]
        sys_id = context.input["sys_id"]
        update_type = context.input["update_type"]
        data = context.input["data"]

        if update_type == "work_note":
            result = await client.add_work_note(table, sys_id, data["note"])

        elif update_type == "comment":
            result = await client.add_comment(table, sys_id, data["comment"])

        elif update_type == "fields":
            result = await client.update_record(table, sys_id, data["fields"])

        elif update_type == "attachment":
            content = data.get("content")
            if isinstance(content, str):
                content = base64.b64decode(content)

            result = await client.add_attachment(
                table, sys_id,
                data["filename"],
                content,
                data.get("content_type", "application/octet-stream")
            )

        else:
            return ActionResult(
                success=False,
                error=f"Unknown update type: {update_type}"
            )

        if result.get("success"):
            return ActionResult(
                success=True,
                output={
                    "record_url": f"{client.instance_url}/{table}.do?sys_id={sys_id}",
                    "update_type": update_type
                }
            )
        else:
            return ActionResult(
                success=False,
                error=result.get("error", "Unknown error")
            )

    except Exception as e:
        logger.error(f"Error updating ServiceNow: {e}")
        return ActionResult(success=False, error=str(e))


@apex_action(
    action_id="servicenow_receive",
    name="ServiceNow Receive",
    description="Receive document from ServiceNow for processing",
    category="integrations",
    version="1.0.0",
    input_schema={
        "type": "object",
        "properties": {
            "source_reference": {"type": "object"},
            "filename": {"type": "string"},
            "content_type": {"type": "string"},
            "content_base64": {"type": "string"},
            "document_type": {"type": "string"},
            "playbook": {"type": "string"},
            "callback_url": {"type": "string"}
        },
        "required": ["source_reference", "filename", "content_base64"]
    }
)
async def receive_handler(context: ActionContext) -> ActionResult:
    """
    Receive document from ServiceNow and create work item.

    Called by ServiceNow when a document attachment needs processing.
    """
    try:
        # Decode document
        content = base64.b64decode(context.input["content_base64"])

        # Generate document ID
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8].upper()
        doc_id = f"SNOW-{timestamp}-{unique_id}"

        # Get configuration
        document_bucket = os.environ.get("DOCUMENT_BUCKET", "apex-documents")
        work_items_table = os.environ.get("WORK_ITEMS_TABLE", "apex-work-items")

        # Upload to S3
        filename = context.input["filename"]
        s3_key = f"servicenow/{doc_id}/{filename}"

        s3.put_object(
            Bucket=document_bucket,
            Key=s3_key,
            Body=content,
            ContentType=context.input.get("content_type", "application/octet-stream"),
            Metadata={
                "document_id": doc_id,
                "source": "servicenow",
                "source_table": context.input["source_reference"].get("table", ""),
                "source_sys_id": context.input["source_reference"].get("sys_id", "")
            }
        )

        # Determine routing
        document_type = context.input.get("document_type", "auto_detect")
        playbook = context.input.get("playbook", "document_triage")

        # Create work item
        table = cosmos_db.Table(work_items_table)

        work_item = {
            "document_id": doc_id,
            "document_type": document_type,
            "playbook": playbook,
            "status": "pending",
            "source": "servicenow",
            "source_details": {
                "table": context.input["source_reference"].get("table"),
                "sys_id": context.input["source_reference"].get("sys_id"),
                "attachment_sys_id": context.input["source_reference"].get("attachment_sys_id"),
                "callback_url": context.input.get("callback_url")
            },
            "s3_location": {
                "bucket": document_bucket,
                "key": s3_key
            },
            "original_filename": filename,
            "content_type": context.input.get("content_type"),
            "size_bytes": len(content),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        table.put_item(Item=work_item)

        logger.info(f"Created work item {doc_id} from ServiceNow")

        return ActionResult(
            success=True,
            output={
                "document_id": doc_id,
                "work_item_id": doc_id,
                "status": "processing"
            }
        )

    except Exception as e:
        logger.error(f"Error receiving from ServiceNow: {e}")
        return ActionResult(success=False, error=str(e))


async def update_record(
    table: str,
    sys_id: str,
    fields: Dict[str, Any],
    instance_url: str = None
) -> ActionResult:
    """Convenience function to update ServiceNow record fields."""
    context = ActionContext({
        "instance": instance_url,
        "table": table,
        "sys_id": sys_id,
        "update_type": "fields",
        "data": {"fields": fields}
    })
    return await handler(context)


async def add_work_note(
    table: str,
    sys_id: str,
    note: str,
    instance_url: str = None
) -> ActionResult:
    """Convenience function to add work note to ServiceNow record."""
    context = ActionContext({
        "instance": instance_url,
        "table": table,
        "sys_id": sys_id,
        "update_type": "work_note",
        "data": {"note": note}
    })
    return await handler(context)


def format_extraction_work_note(
    document_id: str,
    extracted_data: Dict[str, Any],
    confidence: float,
    processing_time: str
) -> str:
    """Format extraction results as a ServiceNow work note."""

    note = f"""
=== APEX AI Extraction Results ===
Document ID: {document_id}
Confidence: {confidence * 100:.1f}%
Processing Time: {processing_time}

Extracted Data:
"""

    for key, value in extracted_data.items():
        # Clean up field names
        display_key = key.replace("_", " ").title()
        note += f"  {display_key}: {value}\n"

    note += f"""
---
Processed by APEX AI Platform
{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
"""

    return note.strip()


async def send_callback(
    callback_url: str,
    document_id: str,
    status: str,
    extracted_data: Dict[str, Any] = None,
    confidence: float = None,
    processing_time: str = None,
    error: str = None
) -> bool:
    """Send processing results back to ServiceNow callback URL."""

    payload = {
        "document_id": document_id,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    if extracted_data:
        payload["extracted_data"] = extracted_data
    if confidence is not None:
        payload["confidence"] = confidence
    if processing_time:
        payload["processing_time"] = processing_time
    if error:
        payload["error"] = error

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                callback_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )
            return response.status_code in [200, 201, 202]

    except Exception as e:
        logger.error(f"Error sending callback to ServiceNow: {e}")
        return False


# Lambda handler for webhook from ServiceNow
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Azure Functions handler for ServiceNow webhook requests.

    Receives document processing requests from ServiceNow.
    """
    import asyncio

    # Parse body
    body = event.get("body", "{}")
    if isinstance(body, str):
        body = json.loads(body)

    # Determine action based on path or payload
    path = event.get("path", "")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        if "/receive" in path or body.get("action") == "process_document":
            # Receive document for processing
            action_context = ActionContext(body)
            result = loop.run_until_complete(receive_handler(action_context))

            return {
                "statusCode": 200 if result.success else 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "success": result.success,
                    "document_id": result.output.get("document_id") if result.success else None,
                    "status": result.output.get("status") if result.success else None,
                    "error": result.error if not result.success else None
                })
            }

        elif "/update" in path or body.get("action") == "update_record":
            # Update ServiceNow record
            action_context = ActionContext(body)
            result = loop.run_until_complete(handler(action_context))

            return {
                "statusCode": 200 if result.success else 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "success": result.success,
                    "record_url": result.output.get("record_url") if result.success else None,
                    "error": result.error if not result.success else None
                })
            }

        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Unknown action"})
            }

    except Exception as e:
        logger.error(f"Error in ServiceNow Lambda handler: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    finally:
        loop.close()
