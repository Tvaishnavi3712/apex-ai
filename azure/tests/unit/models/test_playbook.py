"""
Unit tests for Playbook models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError


class TestPlaybookModels:
    """Tests for Playbook Pydantic models."""

    @pytest.mark.unit
    def test_playbook_base_valid(self):
        """Test creating valid PlaybookBase."""
        from backend.models.playbook import PlaybookBase

        playbook = PlaybookBase(
            name="Invoice Processing",
            description="Process vendor invoices",
            version="1.0.0",
            industry="financial_services",
            category="accounts_payable",
            intent="Automate invoice processing",
            recipe="1. Extract\n2. Validate\n3. Route"
        )

        assert playbook.name == "Invoice Processing"
        assert playbook.industry == "financial_services"

    @pytest.mark.unit
    def test_playbook_base_missing_required(self):
        """Test PlaybookBase fails without required fields."""
        from backend.models.playbook import PlaybookBase

        with pytest.raises(ValidationError):
            PlaybookBase(
                description="Missing name field"
            )

    @pytest.mark.unit
    def test_playbook_create_valid(self):
        """Test creating PlaybookCreate with all fields."""
        from backend.models.playbook import PlaybookCreate

        playbook = PlaybookCreate(
            name="Test Playbook",
            description="Test description",
            version="1.0.0",
            industry="financial_services",
            category="general",
            intent="Test intent",
            recipe="Test recipe",
            actions=["action1", "action2"],
            triggers=[{"type": "s3_event", "bucket": "test-bucket"}]
        )

        assert len(playbook.actions) == 2
        assert playbook.triggers[0]["type"] == "s3_event"

    @pytest.mark.unit
    def test_playbook_full_model(self):
        """Test full Playbook model with all fields."""
        from backend.models.playbook import Playbook

        playbook = Playbook(
            playbook_id="pb-001",
            name="Full Playbook",
            description="Complete playbook",
            version="2.0.0",
            status="active",
            industry="financial_services",
            category="accounts_payable",
            intent="Full intent",
            recipe="Full recipe",
            actions=["action1"],
            triggers=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by="test-user"
        )

        assert playbook.playbook_id == "pb-001"
        assert playbook.status == "active"

    @pytest.mark.unit
    def test_playbook_status_enum(self):
        """Test playbook status validation."""
        from backend.models.playbook import Playbook

        # Valid statuses
        for status in ["draft", "active", "archived", "deprecated"]:
            playbook = Playbook(
                playbook_id="pb-test",
                name="Test",
                description="Test",
                version="1.0.0",
                status=status,
                industry="test",
                category="test",
                intent="test",
                recipe="test",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert playbook.status == status

    @pytest.mark.unit
    def test_playbook_list_response(self):
        """Test PlaybookListResponse model."""
        from backend.models.playbook import Playbook, PlaybookListResponse

        playbooks = [
            Playbook(
                playbook_id=f"pb-{i}",
                name=f"Playbook {i}",
                description="Test",
                version="1.0.0",
                status="active",
                industry="test",
                category="test",
                intent="test",
                recipe="test",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            for i in range(3)
        ]

        response = PlaybookListResponse(
            playbooks=playbooks,
            total=3,
            page=1,
            page_size=10
        )

        assert response.total == 3
        assert len(response.playbooks) == 3

    @pytest.mark.unit
    def test_playbook_update_partial(self):
        """Test PlaybookUpdate allows partial updates."""
        from backend.models.playbook import PlaybookUpdate

        update = PlaybookUpdate(
            name="Updated Name"
        )

        assert update.name == "Updated Name"
        assert update.description is None

    @pytest.mark.unit
    def test_trigger_types(self):
        """Test different trigger type validations."""
        from backend.models.playbook import PlaybookCreate

        triggers = [
            {"type": "s3_event", "bucket": "test-bucket", "prefix": "invoices/"},
            {"type": "api", "method": "POST", "path": "/process"},
            {"type": "schedule", "cron": "0 9 * * *"},
        ]

        playbook = PlaybookCreate(
            name="Multi-trigger",
            description="Test",
            version="1.0.0",
            industry="test",
            category="test",
            intent="test",
            recipe="test",
            triggers=triggers
        )

        assert len(playbook.triggers) == 3


class TestDataSourceModel:
    """Tests for DataSource related models."""

    @pytest.mark.unit
    def test_data_source_s3(self):
        """Test Blob Storage data source configuration."""
        from backend.models.playbook import PlaybookCreate

        playbook = PlaybookCreate(
            name="Blob Storage Source",
            description="Test",
            version="1.0.0",
            industry="test",
            category="test",
            intent="test",
            recipe="test",
            data_sources=[{
                "type": "s3",
                "bucket": "documents",
                "prefix": "invoices/"
            }]
        )

        assert playbook.data_sources[0]["type"] == "s3"

    @pytest.mark.unit
    def test_data_source_cosmos_db(self):
        """Test Cosmos DB data source configuration."""
        from backend.models.playbook import PlaybookCreate

        playbook = PlaybookCreate(
            name="DDB Source",
            description="Test",
            version="1.0.0",
            industry="test",
            category="test",
            intent="test",
            recipe="test",
            data_sources=[{
                "type": "cosmos_db",
                "table": "vendors",
                "key_field": "vendor_id"
            }]
        )

        assert playbook.data_sources[0]["table"] == "vendors"
