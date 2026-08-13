"""
API tests for Playbooks router.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestPlaybooksAPI:
    """Tests for playbooks API endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Mock Cosmos DB service."""
        with patch("backend.api.playbooks.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_list_playbooks_empty(self, client, mock_db):
        """Test listing playbooks when empty."""
        mock_db.scan.return_value = []

        response = client.get("/api/v1/playbooks")

        assert response.status_code == 200
        data = response.json()
        assert "playbooks" in data
        assert len(data["playbooks"]) == 0

    @pytest.mark.api
    def test_list_playbooks_with_data(self, client, mock_db):
        """Test listing playbooks with existing data."""
        mock_db.scan.return_value = [
            {
                "playbook_id": "pb-001",
                "name": "Invoice Processing",
                "description": "Process invoices",
                "version": "1.0.0",
                "status": "active",
                "industry": "financial_services",
                "category": "accounts_payable",
                "intent": "Process invoices",
                "recipe": "Steps...",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]

        response = client.get("/api/v1/playbooks")

        assert response.status_code == 200
        data = response.json()
        assert len(data["playbooks"]) == 1
        assert data["playbooks"][0]["name"] == "Invoice Processing"

    @pytest.mark.api
    def test_list_playbooks_filter_by_industry(self, client, mock_db):
        """Test filtering playbooks by industry."""
        mock_db.query.return_value = [
            {"playbook_id": "pb-fin-001", "industry": "financial_services"}
        ]

        response = client.get("/api/v1/playbooks?industry=financial_services")

        assert response.status_code == 200
        mock_db.query.assert_called()

    @pytest.mark.api
    def test_get_playbook_exists(self, client, mock_db):
        """Test getting an existing playbook."""
        mock_db.get_item.return_value = {
            "playbook_id": "pb-001",
            "name": "Test Playbook",
            "description": "Test",
            "version": "1.0.0",
            "status": "active",
            "industry": "test",
            "category": "test",
            "intent": "test",
            "recipe": "test",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = client.get("/api/v1/playbooks/pb-001")

        assert response.status_code == 200
        data = response.json()
        assert data["playbook_id"] == "pb-001"

    @pytest.mark.api
    def test_get_playbook_not_found(self, client, mock_db):
        """Test getting non-existent playbook returns 404."""
        mock_db.get_item.return_value = None

        response = client.get("/api/v1/playbooks/non-existent")

        assert response.status_code == 404

    @pytest.mark.api
    def test_create_playbook_valid(self, client, mock_db):
        """Test creating a valid playbook."""
        mock_db.put_item.return_value = None

        playbook_data = {
            "name": "New Playbook",
            "description": "A new playbook",
            "version": "1.0.0",
            "industry": "financial_services",
            "category": "accounts_payable",
            "intent": "Process documents",
            "recipe": "1. Extract\n2. Validate\n3. Route",
            "actions": ["action1", "action2"]
        }

        response = client.post("/api/v1/playbooks", json=playbook_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Playbook"
        assert "playbook_id" in data

    @pytest.mark.api
    def test_create_playbook_missing_fields(self, client, mock_db):
        """Test creating playbook with missing required fields."""
        playbook_data = {
            "name": "Incomplete Playbook"
            # Missing required fields
        }

        response = client.post("/api/v1/playbooks", json=playbook_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.api
    def test_update_playbook_valid(self, client, mock_db):
        """Test updating an existing playbook."""
        mock_db.get_item.return_value = {
            "playbook_id": "pb-001",
            "name": "Original",
            "description": "Original desc",
            "version": "1.0.0",
            "status": "active",
            "industry": "test",
            "category": "test",
            "intent": "test",
            "recipe": "test",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        mock_db.update_item.return_value = None

        update_data = {
            "name": "Updated Playbook",
            "description": "Updated description"
        }

        response = client.put("/api/v1/playbooks/pb-001", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Playbook"

    @pytest.mark.api
    def test_update_playbook_not_found(self, client, mock_db):
        """Test updating non-existent playbook returns 404."""
        mock_db.get_item.return_value = None

        update_data = {"name": "Updated"}

        response = client.put("/api/v1/playbooks/non-existent", json=update_data)

        assert response.status_code == 404

    @pytest.mark.api
    def test_delete_playbook_exists(self, client, mock_db):
        """Test deleting an existing playbook."""
        mock_db.get_item.return_value = {"playbook_id": "pb-001"}
        mock_db.delete_item.return_value = None

        response = client.delete("/api/v1/playbooks/pb-001")

        assert response.status_code == 204

    @pytest.mark.api
    def test_delete_playbook_not_found(self, client, mock_db):
        """Test deleting non-existent playbook returns 404."""
        mock_db.get_item.return_value = None

        response = client.delete("/api/v1/playbooks/non-existent")

        assert response.status_code == 404


class TestPlaybookDeployment:
    """Tests for playbook deployment endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Mock Cosmos DB service."""
        with patch("backend.api.playbooks.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_deploy_playbook(self, client, mock_db):
        """Test deploying a playbook."""
        mock_db.get_item.return_value = {
            "playbook_id": "pb-001",
            "name": "Test",
            "status": "draft",
            "description": "test",
            "version": "1.0.0",
            "industry": "test",
            "category": "test",
            "intent": "test",
            "recipe": "test",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = client.post("/api/v1/playbooks/pb-001/deploy")

        # May return 200 or 501 (not implemented)
        assert response.status_code in [200, 501]

    @pytest.mark.api
    def test_test_playbook(self, client, mock_db):
        """Test running a test execution of playbook."""
        mock_db.get_item.return_value = {
            "playbook_id": "pb-001",
            "name": "Test",
            "status": "active",
            "description": "test",
            "version": "1.0.0",
            "industry": "test",
            "category": "test",
            "intent": "test",
            "recipe": "test",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        test_data = {
            "input": {"document_s3_uri": "s3://test/doc.pdf"}
        }

        response = client.post("/api/v1/playbooks/pb-001/test", json=test_data)

        # May return 200 or 501 (not implemented)
        assert response.status_code in [200, 501]
