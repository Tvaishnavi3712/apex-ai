"""
DynamoDB service for data persistence
Includes mock implementation for local development without AWS
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, Any, List, Optional
import json
from decimal import Decimal
import os

from core.config import settings


class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def convert_decimals(obj):
    """Convert Decimal types to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj


# In-memory storage for local development
_mock_storage: Dict[str, Dict[str, Any]] = {}


class MockDynamoDBService:
    """Mock DynamoDB service for local development without AWS"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        if table_name not in _mock_storage:
            _mock_storage[table_name] = {}

    def _get_primary_key(self, item: Dict[str, Any]) -> str:
        """Get primary key from item - handles different table schemas"""
        key_fields = ['agent_id', 'work_item_id', 'action_id', 'playbook_id', 'blueprint_id', 'session_id', 'document_id', 'id']
        for field in key_fields:
            if field in item:
                return str(item[field])
        return str(hash(json.dumps(item, sort_keys=True, default=str)))

    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single item by key"""
        pk = list(key.values())[0]
        return _mock_storage[self.table_name].get(str(pk))

    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put an item into the table"""
        pk = self._get_primary_key(item)
        _mock_storage[self.table_name][pk] = item
        return item

    async def update_item(self, key: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item"""
        pk = list(key.values())[0]
        if str(pk) in _mock_storage[self.table_name]:
            _mock_storage[self.table_name][str(pk)].update(updates)
            return _mock_storage[self.table_name][str(pk)]
        return {}

    async def delete_item(self, key: Dict[str, Any]) -> None:
        """Delete an item"""
        pk = list(key.values())[0]
        if str(pk) in _mock_storage[self.table_name]:
            del _mock_storage[self.table_name][str(pk)]

    async def query(self, key_condition: Dict[str, Any], filter_expression: Optional[Dict[str, Any]] = None,
                    index_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query items"""
        results = []
        for item in _mock_storage[self.table_name].values():
            match = True
            for field, value in key_condition.items():
                if item.get(field) != value:
                    match = False
                    break
            if match and filter_expression:
                for field, value in filter_expression.items():
                    if item.get(field) != value:
                        match = False
                        break
            if match:
                results.append(item)
                if len(results) >= limit:
                    break
        return results

    async def scan(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Scan table with optional filters"""
        results = []
        for item in _mock_storage[self.table_name].values():
            if filters:
                match = True
                for field, value in filters.items():
                    if item.get(field) != value:
                        match = False
                        break
                if match:
                    results.append(item)
            else:
                results.append(item)
            if len(results) >= limit:
                break
        return results

    async def batch_write(self, items: List[Dict[str, Any]]) -> None:
        """Batch write items"""
        for item in items:
            await self.put_item(item)


class DynamoDBService:
    """DynamoDB operations - falls back to mock for local development"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self._mock_service = None
        self._use_mock = False

        # Check if we should use mock (for local development)
        use_local = os.environ.get('USE_LOCAL_MOCK', 'false').lower() == 'true'

        if use_local:
            self._use_mock = True
            self._mock_service = MockDynamoDBService(table_name)
        else:
            try:
                self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
                self.table = self.dynamodb.Table(table_name)
                # Try a simple operation to verify connection
                self.table.table_status
            except Exception as e:
                # Fall back to mock if DynamoDB is not available
                print(f"DynamoDB not available for {table_name}, using mock: {e}")
                self._use_mock = True
                self._mock_service = MockDynamoDBService(table_name)

    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single item by key"""
        if self._use_mock:
            return await self._mock_service.get_item(key)
        try:
            response = self.table.get_item(Key=key)
            item = response.get('Item')
            return convert_decimals(item) if item else None
        except Exception as e:
            raise Exception(f"Failed to get item from {self.table_name}: {str(e)}")

    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put an item into the table"""
        if self._use_mock:
            return await self._mock_service.put_item(item)
        try:
            self.table.put_item(Item=item)
            return item
        except Exception as e:
            raise Exception(f"Failed to put item to {self.table_name}: {str(e)}")

    async def update_item(
        self,
        key: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an item"""
        if self._use_mock:
            return await self._mock_service.update_item(key, updates)
        try:
            update_expression_parts = []
            expression_values = {}
            expression_names = {}

            for i, (field, value) in enumerate(updates.items()):
                placeholder = f":val{i}"
                name_placeholder = f"#field{i}"
                update_expression_parts.append(f"{name_placeholder} = {placeholder}")
                expression_values[placeholder] = value
                expression_names[name_placeholder] = field

            update_expression = "SET " + ", ".join(update_expression_parts)

            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames=expression_names,
                ReturnValues="ALL_NEW"
            )

            return convert_decimals(response.get('Attributes', {}))
        except Exception as e:
            raise Exception(f"Failed to update item in {self.table_name}: {str(e)}")

    async def delete_item(self, key: Dict[str, Any]) -> None:
        """Delete an item"""
        if self._use_mock:
            return await self._mock_service.delete_item(key)
        try:
            self.table.delete_item(Key=key)
        except Exception as e:
            raise Exception(f"Failed to delete item from {self.table_name}: {str(e)}")

    async def query(
        self,
        key_condition: Dict[str, Any],
        filter_expression: Optional[Dict[str, Any]] = None,
        index_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query items with key condition"""
        if self._use_mock:
            return await self._mock_service.query(key_condition, filter_expression, index_name, limit)
        try:
            # Build key condition expression
            key_conditions = []
            expression_values = {}

            for i, (field, value) in enumerate(key_condition.items()):
                key_conditions.append(Key(field).eq(value))

            combined_condition = key_conditions[0]
            for condition in key_conditions[1:]:
                combined_condition = combined_condition & condition

            kwargs = {
                'KeyConditionExpression': combined_condition,
                'Limit': limit
            }

            if index_name:
                kwargs['IndexName'] = index_name

            if filter_expression:
                filters = []
                for field, value in filter_expression.items():
                    filters.append(Attr(field).eq(value))
                combined_filter = filters[0]
                for f in filters[1:]:
                    combined_filter = combined_filter & f
                kwargs['FilterExpression'] = combined_filter

            response = self.table.query(**kwargs)
            return [convert_decimals(item) for item in response.get('Items', [])]

        except Exception as e:
            raise Exception(f"Failed to query {self.table_name}: {str(e)}")

    async def scan(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Scan table with optional filters.

        Paginates through all results to ensure we get up to 'limit' matching items.
        """
        if self._use_mock:
            return await self._mock_service.scan(filters, limit)
        try:
            kwargs = {}

            if filters:
                # Build filter expression
                filter_conditions = []
                for field, value in filters.items():
                    filter_conditions.append(Attr(field).eq(value))

                combined_filter = filter_conditions[0]
                for f in filter_conditions[1:]:
                    combined_filter = combined_filter & f
                kwargs['FilterExpression'] = combined_filter

            # Paginate through all results to get up to 'limit' items
            results = []
            while True:
                response = self.table.scan(**kwargs)
                items = response.get('Items', [])
                results.extend([convert_decimals(item) for item in items])

                # Stop if we have enough or no more pages
                if len(results) >= limit or 'LastEvaluatedKey' not in response:
                    break
                kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

            return results[:limit]

        except Exception as e:
            raise Exception(f"Failed to scan {self.table_name}: {str(e)}")

    async def batch_write(self, items: List[Dict[str, Any]]) -> None:
        """Batch write items"""
        if self._use_mock:
            return await self._mock_service.batch_write(items)
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
        except Exception as e:
            raise Exception(f"Failed to batch write to {self.table_name}: {str(e)}")
