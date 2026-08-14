"""
Base class for Apex Actions
Provides common functionality for action implementations
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: azure-openai -> Azure OpenAI shim
    from sdk.azure_llm import get_bedrock_runtime
except ImportError:
    from ...sdk.azure_llm import get_bedrock_runtime
import json
import logging

logger = logging.getLogger(__name__)


class ApexActionBase(ABC):
    """
    Base class for implementing Apex Actions as classes

    Use this when you need more complex action logic with state,
    multiple helper methods, or dependency injection.

    Example:
        class VendorLookupAction(ApexActionBase):
            name = "vendor_lookup"
            description = "Check if vendor exists in approved vendor list"

            def __init__(self):
                super().__init__()
                self.table_name = "approved_vendors"

            def execute(self, vendor_name: str) -> dict:
                result = self.cosmos_db_get(self.table_name, {"vendor_name": vendor_name})
                return {
                    "exists": result is not None,
                    "vendor_id": result.get("vendor_id") if result else None
                }
    """

    # Override these in subclasses
    name: str = "base_action"
    description: str = "Base action"
    category: str = "business_logic"
    industry: str = "general"

    def __init__(self):
        self._tables = None
        self._s3 = None
        self._azure_openai = None
        self._ses = None

    @property
    def cosmos_db(self):
        """Lazy-loaded Cosmos DB resource"""
        if self._tables is None:
            self._tables = get_table_resource()
        return self._tables

    @property
    def s3(self):
        """Lazy-loaded S3 client"""
        if self._s3 is None:
            self._s3 = boto3.client('s3')
        return self._s3

    @property
    def azure_openai(self):
        """Lazy-loaded Azure OpenAI client"""
        if self._azure_openai is None:
            self._azure_openai = get_bedrock_runtime()
        return self._azure_openai

    @property
    def ses(self):
        """Lazy-loaded SES client"""
        if self._ses is None:
            self._ses = boto3.client('ses')
        return self._ses

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the action logic

        Override this method in subclasses to implement the action.

        Args:
            **kwargs: Action input parameters

        Returns:
            Dict with action results
        """
        pass

    def __call__(self, event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
        """
        Lambda handler entry point

        This allows the action to be used directly as a Lambda handler:
            handler = VendorLookupAction()
        """
        try:
            logger.info(f"Executing action: {self.name}")
            logger.debug(f"Input: {json.dumps(event)}")

            result = self.execute(**event)

            logger.info(f"Action {self.name} completed successfully")
            return result

        except Exception as e:
            logger.error(f"Action {self.name} failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "action": self.name
            }

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def cosmos_db_get(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get an item from Cosmos DB"""
        table = self.tables.Table(table_name)
        response = table.get_item(Key=key)
        return response.get('Item')

    def cosmos_db_put(self, table_name: str, item: Dict[str, Any]) -> None:
        """Put an item to Cosmos DB"""
        table = self.tables.Table(table_name)
        table.put_item(Item=item)

    def cosmos_db_query(
        self,
        table_name: str,
        key_condition,
        index_name: Optional[str] = None
    ) -> list:
        """Query Cosmos DB"""
        table = self.tables.Table(table_name)
        kwargs = {'KeyConditionExpression': key_condition}
        if index_name:
            kwargs['IndexName'] = index_name
        response = table.query(**kwargs)
        return response.get('Items', [])

    def s3_get(self, bucket: str, key: str) -> bytes:
        """Get an object from S3"""
        response = self.s3.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()

    def s3_get_json(self, bucket: str, key: str) -> Dict[str, Any]:
        """Get and parse a JSON object from S3"""
        content = self.s3_get(bucket, key)
        return json.loads(content.decode('utf-8'))

    def s3_put(self, bucket: str, key: str, body: bytes, content_type: str = None) -> str:
        """Put an object to S3"""
        kwargs = {'Bucket': bucket, 'Key': key, 'Body': body}
        if content_type:
            kwargs['ContentType'] = content_type
        self.s3.put_object(**kwargs)
        return f"s3://{bucket}/{key}"

    def s3_put_json(self, bucket: str, key: str, data: Dict[str, Any]) -> str:
        """Put a JSON object to S3"""
        body = json.dumps(data, indent=2).encode('utf-8')
        return self.s3_put(bucket, key, body, 'application/json')

    def invoke_claude(
        self,
        prompt: str,
        system: str = None,
        max_tokens: int = 1000,
        model_id: str = "anthropic.claude-opus-4-5-20251101-v1:0"
    ) -> str:
        """Invoke Claude via Azure OpenAI"""
        messages = [{"role": "user", "content": prompt}]

        body = {
                        "max_tokens": max_tokens,
            "messages": messages
        }

        if system:
            body["system"] = system

        response = self.llm.invoke_model(
            modelId=model_id,
            body=json.dumps(body)
        )

        result = json.loads(response['body'].read())
        return result['content'][0]['text']

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        sender: str = "noreply@apex-ai.cbts.com"
    ) -> str:
        """Send an email via SES"""
        response = self.ses.send_email(
            Source=sender,
            Destination={'ToAddresses': [to]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        return response['MessageId']

    def log(self, message: str, level: str = "info", **kwargs):
        """Structured logging"""
        log_data = {
            "action": self.name,
            "message": message,
            **kwargs
        }

        if level == "debug":
            logger.debug(json.dumps(log_data))
        elif level == "warning":
            logger.warning(json.dumps(log_data))
        elif level == "error":
            logger.error(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
