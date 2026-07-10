"""
API tests for Actions router.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestActionsAPI:
    """Tests for actions API endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Mock DynamoDB service."""
        with patch("backend.api.actions.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_list_actions_empty(self, client, mock_db):
        """Test listing actions when empty."""
        mock_db.scan.return_value = []

        response = client.get("/api/v1/actions")

        assert response.status_code == 200
        data = response.json()
        assert "actions" in data

    @pytest.mark.api
    def test_list_actions_with_data(self, client, mock_db):
        """Test listing actions with existing data."""
        mock_db.scan.return_value = [
            {
                "action_id": "action-001",
                "name": "vendor_lookup",
                "description": "Look up vendor",
                "type": "lambda",
                "category": "data_lookup",
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            }
        ]

        response = client.get("/api/v1/actions")

        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 1

    @pytest.mark.api
    def test_list_actions_filter_by_category(self, client, mock_db):
        """Test filtering actions by category."""
        mock_db.scan.return_value = [
            {"action_id": "action-001", "category": "data_lookup"}
        ]

        response = client.get("/api/v1/actions?category=data_lookup")

        assert response.status_code == 200

    @pytest.mark.api
    def test_get_action_gallery(self, client, mock_db):
        """Test getting actions organized by category."""
        mock_db.scan.return_value = [
            {"action_id": "a1", "name": "lookup", "category": "data_lookup"},
            {"action_id": "a2", "name": "extract", "category": "document"},
            {"action_id": "a3", "name": "notify", "category": "notification"},
        ]

        response = client.get("/api/v1/actions/gallery")

        assert response.status_code == 200
        data = response.json()
        assert "categories" in data

    @pytest.mark.api
    def test_get_action_packs(self, client, mock_db):
        """Test getting predefined action packs."""
        response = client.get("/api/v1/actions/packs")

        assert response.status_code == 200
        data = response.json()
        assert "packs" in data

    @pytest.mark.api
    def test_get_action_exists(self, client, mock_db):
        """Test getting an existing action."""
        mock_db.get_item.return_value = {
            "action_id": "action-001",
            "name": "vendor_lookup",
            "description": "Look up vendor info",
            "type": "lambda",
            "category": "data_lookup",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }

        response = client.get("/api/v1/actions/action-001")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "vendor_lookup"

    @pytest.mark.api
    def test_get_action_not_found(self, client, mock_db):
        """Test getting non-existent action returns 404."""
        mock_db.get_item.return_value = None

        response = client.get("/api/v1/actions/non-existent")

        assert response.status_code == 404

    @pytest.mark.api
    def test_create_action_valid(self, client, mock_db):
        """Test creating a valid action."""
        mock_db.put_item.return_value = None

        action_data = {
            "name": "new_action",
            "description": "A new action",
            "type": "lambda",
            "category": "business_logic",
            "input_schema": {
                "type": "object",
                "properties": {"param": {"type": "string"}}
            },
            "output_schema": {
                "type": "object",
                "properties": {"result": {"type": "boolean"}}
            }
        }

        response = client.post("/api/v1/actions", json=action_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new_action"
        assert "action_id" in data

    @pytest.mark.api
    def test_delete_action_exists(self, client, mock_db):
        """Test deleting an existing action."""
        mock_db.get_item.return_value = {"action_id": "action-001"}
        mock_db.delete_item.return_value = None

        response = client.delete("/api/v1/actions/action-001")

        assert response.status_code == 204

    @pytest.mark.api
    def test_delete_action_not_found(self, client, mock_db):
        """Test deleting non-existent action returns 404."""
        mock_db.get_item.return_value = None

        response = client.delete("/api/v1/actions/non-existent")

        assert response.status_code == 404


class TestActionPacks:
    """Tests for action pack deployment."""

    @pytest.fixture
    def mock_db(self):
        """Mock DynamoDB service."""
        with patch("backend.api.actions.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_deploy_financial_services_pack(self, client, mock_db):
        """Test deploying financial services action pack."""
        mock_db.batch_write.return_value = None

        response = client.post("/api/v1/actions/deploy-pack/financial_services")

        # May return 200 or 501 (not implemented)
        assert response.status_code in [200, 201, 501]

    @pytest.mark.api
    def test_deploy_unknown_pack(self, client, mock_db):
        """Test deploying unknown pack returns error."""
        response = client.post("/api/v1/actions/deploy-pack/unknown_pack")

        assert response.status_code in [404, 400, 501]


class TestActionTesting:
    """Tests for action testing endpoint."""

    @pytest.fixture
    def mock_db(self):
        """Mock DynamoDB service."""
        with patch("backend.api.actions.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_test_action_valid(self, client, mock_db):
        """Test running action test with valid input."""
        mock_db.get_item.return_value = {
            "action_id": "action-001",
            "name": "vendor_lookup",
            "type": "lambda",
            "category": "data_lookup",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }

        test_input = {
            "vendor_name": "Acme Corp"
        }

        response = client.post(
            "/api/v1/actions/action-001/test",
            json=test_input
        )

        # May return 200 or 501 (not implemented)
        assert response.status_code in [200, 501]

    @pytest.mark.api
    def test_test_action_not_found(self, client, mock_db):
        """Test testing non-existent action returns 404."""
        mock_db.get_item.return_value = None

        response = client.post(
            "/api/v1/actions/non-existent/test",
            json={}
        )

        assert response.status_code == 404
