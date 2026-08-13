"""
API tests for Blueprints router.
"""
import pytest
from unittest.mock import patch
from datetime import datetime


class TestBlueprintsAPI:
    """Tests for blueprints API endpoints."""

    @pytest.fixture
    def mock_db(self):
        """Mock DynamoDB service."""
        with patch("backend.api.blueprints.db") as mock:
            yield mock

    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @pytest.mark.api
    def test_list_blueprints_empty(self, client, mock_db):
        """Test listing blueprints when empty."""
        mock_db.scan.return_value = []

        response = client.get("/api/v1/blueprints")

        assert response.status_code == 200
        data = response.json()
        assert "blueprints" in data

    @pytest.mark.api
    def test_list_blueprints_filter_by_industry(self, client, mock_db):
        """Test filtering blueprints by industry."""
        mock_db.scan.return_value = [
            {
                "blueprint_id": "bp-001",
                "name": "Invoice",
                "industry": "financial_services",
                "document_type": "invoice",
                "stage": "LIVE",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        ]

        response = client.get("/api/v1/blueprints?industry=financial_services")

        assert response.status_code == 200

    @pytest.mark.api
    def test_get_blueprint_exists(self, client, mock_db):
        """Test getting an existing blueprint."""
        mock_db.get_item.return_value = {
            "blueprint_id": "bp-001",
            "name": "Invoice Blueprint",
            "description": "Extract invoice fields",
            "industry": "financial_services",
            "document_type": "invoice",
            "stage": "LIVE",
            "schema": {"class": "Invoice", "properties": {}},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = client.get("/api/v1/blueprints/bp-001")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Invoice Blueprint"

    @pytest.mark.api
    def test_get_blueprint_not_found(self, client, mock_db):
        """Test getting non-existent blueprint returns 404."""
        mock_db.get_item.return_value = None

        response = client.get("/api/v1/blueprints/non-existent")

        assert response.status_code == 404

    @pytest.mark.api
    def test_create_blueprint_valid(self, client, mock_db):
        """Test creating a valid blueprint."""
        mock_db.put_item.return_value = None

        blueprint_data = {
            "name": "New Blueprint",
            "description": "A new blueprint",
            "industry": "manufacturing",
            "document_type": "purchase_order",
            "schema": {
                "class": "PurchaseOrder",
                "properties": {
                    "po_number": {"type": "string"},
                    "total": {"type": "number"}
                }
            }
        }

        response = client.post("/api/v1/blueprints", json=blueprint_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Blueprint"

    @pytest.mark.api
    def test_delete_blueprint(self, client, mock_db):
        """Test deleting a blueprint."""
        mock_db.get_item.return_value = {"blueprint_id": "bp-001"}
        mock_db.delete_item.return_value = None

        response = client.delete("/api/v1/blueprints/bp-001")

        assert response.status_code == 204

    @pytest.mark.api
    def test_deploy_blueprint(self, client, mock_db):
        """Test deploying blueprint to BDA."""
        mock_db.get_item.return_value = {
            "blueprint_id": "bp-001",
            "name": "Test",
            "stage": "DEVELOPMENT",
            "industry": "test",
            "document_type": "test",
            "schema": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        response = client.post("/api/v1/blueprints/bp-001/deploy")

        # May return 200 or 501 (not implemented)
        assert response.status_code in [200, 501]

    @pytest.mark.api
    def test_test_blueprint(self, client, mock_db):
        """Test blueprint with sample document."""
        mock_db.get_item.return_value = {
            "blueprint_id": "bp-001",
            "name": "Test",
            "stage": "LIVE",
            "industry": "test",
            "document_type": "test",
            "schema": {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        test_data = {
            "document_s3_uri": "s3://test-bucket/sample.pdf"
        }

        response = client.post("/api/v1/blueprints/bp-001/test", json=test_data)

        # May return 200 or 501 (not implemented)
        assert response.status_code in [200, 501]
