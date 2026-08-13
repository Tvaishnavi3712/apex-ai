"""
API tests for Work Items router.
"""
import pytest
from unittest.mock import patch
from datetime import datetime


class TestWorkItemsAPI:
    """Tests for work items API endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Mock DynamoDB service."""
        with patch("backend.api.work_items.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_list_work_items_empty(self, client, mock_db):
        """Test listing work items when empty."""
        mock_db.scan.return_value = []

        response = client.get("/api/v1/work-items")

        assert response.status_code == 200
        data = response.json()
        assert "work_items" in data

    @pytest.mark.api
    def test_list_work_items_with_filters(self, client, mock_db):
        """Test listing work items with filters."""
        mock_db.scan.return_value = [
            {
                "work_item_id": "wi-001",
                "type": "invoice_review",
                "status": "pending",
                "priority": "high",
                "payload": {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]

        response = client.get("/api/v1/work-items?status=pending&priority=high")

        assert response.status_code == 200

    @pytest.mark.api
    def test_get_work_item_queue(self, client, mock_db):
        """Test getting pending queue for agent."""
        mock_db.query.return_value = [
            {"work_item_id": "wi-001", "status": "pending"},
            {"work_item_id": "wi-002", "status": "pending"}
        ]

        response = client.get("/api/v1/work-items/queue/agent-001")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    @pytest.mark.api
    def test_get_work_item_exists(self, client, mock_db):
        """Test getting an existing work item."""
        mock_db.get_item.return_value = {
            "work_item_id": "wi-001",
            "type": "invoice_review",
            "status": "pending",
            "priority": "high",
            "payload": {"invoice_id": "inv-123"},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = client.get("/api/v1/work-items/wi-001")

        assert response.status_code == 200
        data = response.json()
        assert data["work_item_id"] == "wi-001"

    @pytest.mark.api
    def test_get_work_item_not_found(self, client, mock_db):
        """Test getting non-existent work item returns 404."""
        mock_db.get_item.return_value = None

        response = client.get("/api/v1/work-items/non-existent")

        assert response.status_code == 404

    @pytest.mark.api
    def test_create_work_item_valid(self, client, mock_db):
        """Test creating a valid work item."""
        mock_db.put_item.return_value = None

        item_data = {
            "type": "document_review",
            "priority": "high",
            "payload": {"document_id": "doc-123"}
        }

        response = client.post("/api/v1/work-items", json=item_data)

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "document_review"
        assert "work_item_id" in data

    @pytest.mark.api
    def test_create_work_items_batch(self, client, mock_db):
        """Test creating multiple work items."""
        mock_db.batch_write.return_value = None

        items_data = {
            "items": [
                {"type": "review", "priority": "normal", "payload": {}},
                {"type": "review", "priority": "high", "payload": {}}
            ]
        }

        response = client.post("/api/v1/work-items/batch", json=items_data)

        assert response.status_code == 201

    @pytest.mark.api
    def test_update_work_item_status(self, client, mock_db):
        """Test updating work item status."""
        mock_db.get_item.return_value = {
            "work_item_id": "wi-001",
            "status": "pending",
            "type": "review",
            "priority": "normal",
            "payload": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        mock_db.update_item.return_value = None

        status_update = {"status": "executing"}

        response = client.put("/api/v1/work-items/wi-001/status", json=status_update)

        assert response.status_code == 200

    @pytest.mark.api
    def test_set_work_item_result(self, client, mock_db):
        """Test setting work item result."""
        mock_db.get_item.return_value = {
            "work_item_id": "wi-001",
            "status": "executing",
            "type": "review",
            "priority": "normal",
            "payload": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        mock_db.update_item.return_value = None

        result_data = {
            "status": "success",
            "output": {"approved": True},
            "confidence": 0.95
        }

        response = client.put("/api/v1/work-items/wi-001/result", json=result_data)

        assert response.status_code == 200

    @pytest.mark.api
    def test_retry_failed_work_item(self, client, mock_db):
        """Test retrying a failed work item."""
        mock_db.get_item.return_value = {
            "work_item_id": "wi-001",
            "status": "failed",
            "type": "review",
            "priority": "normal",
            "payload": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        mock_db.update_item.return_value = None

        response = client.post("/api/v1/work-items/wi-001/retry")

        assert response.status_code == 200

    @pytest.mark.api
    def test_delete_work_item(self, client, mock_db):
        """Test deleting a work item."""
        mock_db.get_item.return_value = {"work_item_id": "wi-001"}
        mock_db.delete_item.return_value = None

        response = client.delete("/api/v1/work-items/wi-001")

        assert response.status_code == 204
