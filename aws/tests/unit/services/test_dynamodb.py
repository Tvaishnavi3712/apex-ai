"""
Unit tests for DynamoDB Service.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from moto import mock_dynamodb
import boto3


class TestDynamoDBService:
    """Tests for DynamoDBService class."""

    @pytest.fixture
    def mock_table(self):
        """Create a mock DynamoDB table."""
        with mock_dynamodb():
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            table = dynamodb.create_table(
                TableName="test-table",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table.meta.client.get_waiter("table_exists").wait(TableName="test-table")
            yield table

    @pytest.fixture
    def service(self, mock_table):
        """Create DynamoDBService instance with mocked table."""
        from backend.services.dynamodb import DynamoDBService

        with patch.object(DynamoDBService, "__init__", lambda self, table_name: None):
            svc = DynamoDBService.__new__(DynamoDBService)
            svc.table_name = "test-table"
            svc.table = mock_table
            svc.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            yield svc

    @pytest.mark.unit
    def test_put_item_success(self, service, mock_table):
        """Test successful item insertion."""
        item = {"id": "test-001", "name": "Test Item", "value": 100}

        service.put_item(item)

        response = mock_table.get_item(Key={"id": "test-001"})
        assert "Item" in response
        assert response["Item"]["name"] == "Test Item"
        assert response["Item"]["value"] == Decimal("100")

    @pytest.mark.unit
    def test_get_item_existing(self, service, mock_table):
        """Test retrieving an existing item."""
        mock_table.put_item(Item={"id": "test-002", "name": "Existing"})

        result = service.get_item({"id": "test-002"})

        assert result is not None
        assert result["name"] == "Existing"

    @pytest.mark.unit
    def test_get_item_not_found(self, service):
        """Test retrieving non-existent item returns None."""
        result = service.get_item({"id": "non-existent"})

        assert result is None

    @pytest.mark.unit
    def test_update_item(self, service, mock_table):
        """Test updating an existing item."""
        mock_table.put_item(Item={"id": "test-003", "name": "Original", "count": 1})

        service.update_item(
            key={"id": "test-003"},
            updates={"name": "Updated", "count": 5}
        )

        response = mock_table.get_item(Key={"id": "test-003"})
        assert response["Item"]["name"] == "Updated"
        assert response["Item"]["count"] == Decimal("5")

    @pytest.mark.unit
    def test_delete_item(self, service, mock_table):
        """Test deleting an item."""
        mock_table.put_item(Item={"id": "test-004", "name": "To Delete"})

        service.delete_item({"id": "test-004"})

        response = mock_table.get_item(Key={"id": "test-004"})
        assert "Item" not in response

    @pytest.mark.unit
    def test_query_with_key_condition(self, service, mock_table):
        """Test querying items with key condition."""
        # Add test items
        mock_table.put_item(Item={"id": "query-001", "status": "active"})
        mock_table.put_item(Item={"id": "query-002", "status": "active"})

        # Note: Basic query on partition key
        result = service.query(
            key_condition="id = :id",
            expression_values={":id": "query-001"}
        )

        assert len(result) == 1
        assert result[0]["id"] == "query-001"

    @pytest.mark.unit
    def test_scan_all_items(self, service, mock_table):
        """Test scanning all items in table."""
        mock_table.put_item(Item={"id": "scan-001", "type": "A"})
        mock_table.put_item(Item={"id": "scan-002", "type": "B"})
        mock_table.put_item(Item={"id": "scan-003", "type": "A"})

        result = service.scan()

        assert len(result) == 3

    @pytest.mark.unit
    def test_scan_with_filter(self, service, mock_table):
        """Test scanning with filter expression."""
        mock_table.put_item(Item={"id": "filter-001", "type": "A"})
        mock_table.put_item(Item={"id": "filter-002", "type": "B"})
        mock_table.put_item(Item={"id": "filter-003", "type": "A"})

        result = service.scan(
            filters={"type": "A"}
        )

        # Filter is applied after scan
        assert all(item["type"] == "A" for item in result)

    @pytest.mark.unit
    def test_batch_write_items(self, service, mock_table):
        """Test batch writing multiple items."""
        items = [
            {"id": "batch-001", "name": "Item 1"},
            {"id": "batch-002", "name": "Item 2"},
            {"id": "batch-003", "name": "Item 3"},
        ]

        service.batch_write(items)

        # Verify all items exist
        for item in items:
            response = mock_table.get_item(Key={"id": item["id"]})
            assert "Item" in response

    @pytest.mark.unit
    def test_decimal_conversion(self, service, mock_table):
        """Test that Decimal types are properly handled."""
        mock_table.put_item(Item={
            "id": "decimal-001",
            "price": Decimal("19.99"),
            "quantity": Decimal("5"),
        })

        result = service.get_item({"id": "decimal-001"})

        # Service should convert Decimals to floats
        assert isinstance(result["price"], (int, float, Decimal))
        assert float(result["price"]) == 19.99


class TestDynamoDBServiceErrors:
    """Test error handling in DynamoDBService."""

    @pytest.mark.unit
    def test_put_item_with_invalid_data(self):
        """Test that invalid data raises appropriate error."""
        from backend.services.dynamodb import DynamoDBService

        with patch.object(DynamoDBService, "__init__", lambda self, table_name: None):
            svc = DynamoDBService.__new__(DynamoDBService)
            svc.table = MagicMock()
            svc.table.put_item.side_effect = Exception("Invalid data format")

            with pytest.raises(Exception) as exc_info:
                svc.put_item({"invalid": object()})

            assert "Invalid data" in str(exc_info.value) or "Failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_connection_error_handling(self):
        """Test handling of connection errors."""
        from backend.services.dynamodb import DynamoDBService

        with patch.object(DynamoDBService, "__init__", lambda self, table_name: None):
            svc = DynamoDBService.__new__(DynamoDBService)
            svc.table = MagicMock()
            svc.table.get_item.side_effect = Exception("Connection refused")

            with pytest.raises(Exception):
                svc.get_item({"id": "test"})
