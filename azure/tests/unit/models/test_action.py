"""
Unit tests for Action models.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError


class TestActionModels:
    """Tests for Action Pydantic models."""

    @pytest.mark.unit
    def test_action_base_valid(self):
        """Test creating valid ActionBase."""
        from backend.models.action import ActionBase

        action = ActionBase(
            name="vendor_lookup",
            description="Look up vendor information",
            type="lambda",
            category="data_lookup"
        )

        assert action.name == "vendor_lookup"
        assert action.type == "lambda"

    @pytest.mark.unit
    def test_action_types(self):
        """Test valid action types."""
        from backend.models.action import ActionBase

        valid_types = ["lambda", "gateway_prebuilt", "openapi", "mcp"]

        for action_type in valid_types:
            action = ActionBase(
                name="test_action",
                description="Test",
                type=action_type,
                category="general"
            )
            assert action.type == action_type

    @pytest.mark.unit
    def test_action_categories(self):
        """Test valid action categories."""
        from backend.models.action import ActionBase

        categories = [
            "document",
            "data_lookup",
            "business_logic",
            "notification",
            "integration",
            "human_in_loop"
        ]

        for category in categories:
            action = ActionBase(
                name="test_action",
                description="Test",
                type="lambda",
                category=category
            )
            assert action.category == category

    @pytest.mark.unit
    def test_action_with_schemas(self):
        """Test action with input/output schemas."""
        from backend.models.action import Action

        input_schema = {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string"},
                "vendor_id": {"type": "string"}
            },
            "required": ["vendor_name"]
        }

        output_schema = {
            "type": "object",
            "properties": {
                "vendor": {"type": "object"},
                "status": {"type": "string"}
            }
        }

        action = Action(
            action_id="action-001",
            name="vendor_lookup",
            description="Lookup vendor",
            type="lambda",
            category="data_lookup",
            input_schema=input_schema,
            output_schema=output_schema,
            status="active",
            created_at=datetime.utcnow()
        )

        assert "vendor_name" in action.input_schema["properties"]
        assert "status" in action.output_schema["properties"]

    @pytest.mark.unit
    def test_action_lambda_config(self):
        """Test action with Lambda configuration."""
        from backend.models.action import Action

        action = Action(
            action_id="action-002",
            name="invoice_extract",
            description="Extract invoice data",
            type="lambda",
            category="document",
            function_id="azure-resource-id",
            lambda_managed_identity="azure-resource-id",
            status="active",
            created_at=datetime.utcnow()
        )

        assert "lambda" in action.function_id
        assert action.type == "lambda"

    @pytest.mark.unit
    def test_action_metrics(self):
        """Test action with invocation metrics."""
        from backend.models.action import Action

        action = Action(
            action_id="action-003",
            name="metrics_action",
            description="Action with metrics",
            type="lambda",
            category="general",
            status="active",
            invocation_count=500,
            avg_latency_ms=125.5,
            error_rate=0.02,
            created_at=datetime.utcnow()
        )

        assert action.invocation_count == 500
        assert action.avg_latency_ms == 125.5
        assert action.error_rate == 0.02

    @pytest.mark.unit
    def test_action_status_values(self):
        """Test valid action status values."""
        from backend.models.action import Action

        statuses = ["active", "deprecated", "disabled"]

        for status in statuses:
            action = Action(
                action_id="status-action",
                name="test",
                description="test",
                type="lambda",
                category="general",
                status=status,
                created_at=datetime.utcnow()
            )
            assert action.status == status


class TestActionPackModels:
    """Tests for ActionPack models."""

    @pytest.mark.unit
    def test_action_pack_valid(self):
        """Test creating valid ActionPack."""
        from backend.models.action import ActionPack

        pack = ActionPack(
            pack_id="pack-001",
            name="Financial Services Pack",
            description="Actions for financial services",
            industry="financial_services",
            actions=["vendor_lookup", "po_match", "approval_route"],
            version="1.0.0"
        )

        assert pack.name == "Financial Services Pack"
        assert len(pack.actions) == 3

    @pytest.mark.unit
    def test_action_pack_industries(self):
        """Test action packs for different industries."""
        from backend.models.action import ActionPack

        industries = [
            "financial_services",
            "healthcare",
            "manufacturing",
            "hr",
            "legal"
        ]

        for industry in industries:
            pack = ActionPack(
                pack_id=f"pack-{industry}",
                name=f"{industry} Pack",
                description=f"Actions for {industry}",
                industry=industry,
                actions=["action1", "action2"],
                version="1.0.0"
            )
            assert pack.industry == industry


class TestActionSchemaValidation:
    """Tests for action schema validation."""

    @pytest.mark.unit
    def test_json_schema_format(self):
        """Test that schemas follow JSON Schema format."""
        from backend.models.action import Action

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "invoice_number": {
                    "type": "string",
                    "description": "Unique invoice ID"
                },
                "amount": {
                    "type": "number",
                    "minimum": 0
                }
            },
            "required": ["invoice_number"]
        }

        action = Action(
            action_id="schema-action",
            name="test",
            description="test",
            type="lambda",
            category="document",
            input_schema=schema,
            status="active",
            created_at=datetime.utcnow()
        )

        assert "$schema" in action.input_schema
        assert "required" in action.input_schema
