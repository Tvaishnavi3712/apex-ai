"""
Unit tests for Blueprint models.
"""
import pytest
from datetime import datetime


class TestBlueprintModels:
    """Tests for Blueprint Pydantic models."""

    @pytest.mark.unit
    def test_blueprint_base_valid(self):
        """Test creating valid BlueprintBase."""
        from backend.models.blueprint import BlueprintBase

        blueprint = BlueprintBase(
            name="Invoice Blueprint",
            description="Extract invoice fields",
            document_type="invoice",
            industry="financial_services"
        )

        assert blueprint.name == "Invoice Blueprint"
        assert blueprint.document_type == "invoice"

    @pytest.mark.unit
    def test_blueprint_with_schema(self):
        """Test blueprint with extraction schema."""
        from backend.models.blueprint import Blueprint

        schema = {
            "class": "Invoice",
            "description": "Invoice extraction",
            "properties": {
                "invoice_number": {
                    "type": "string",
                    "inferenceType": "explicit",
                    "instruction": "Extract invoice number"
                },
                "total_amount": {
                    "type": "number",
                    "inferenceType": "explicit",
                    "instruction": "Extract total amount"
                }
            }
        }

        blueprint = Blueprint(
            blueprint_id="bp-001",
            name="Invoice Blueprint",
            description="Extract invoice",
            document_type="invoice",
            industry="financial_services",
            stage="LIVE",
            schema=schema,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert "properties" in blueprint.schema
        assert "invoice_number" in blueprint.schema["properties"]

    @pytest.mark.unit
    def test_blueprint_stages(self):
        """Test valid blueprint stages."""
        from backend.models.blueprint import Blueprint

        stages = ["DEVELOPMENT", "LIVE"]

        for stage in stages:
            blueprint = Blueprint(
                blueprint_id="bp-stage",
                name="Test",
                description="Test",
                document_type="test",
                industry="test",
                stage=stage,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert blueprint.stage == stage

    @pytest.mark.unit
    def test_blueprint_with_bda_arn(self):
        """Test blueprint with BDA ARN."""
        from backend.models.blueprint import Blueprint

        blueprint = Blueprint(
            blueprint_id="bp-002",
            name="Deployed Blueprint",
            description="Deployed to BDA",
            document_type="invoice",
            industry="financial_services",
            stage="LIVE",
            docintel_blueprint_id="azure-resource-id",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert "azure-resource-id" in blueprint.docintel_blueprint_id

    @pytest.mark.unit
    def test_blueprint_field_types(self):
        """Test blueprint with various field types."""
        from backend.models.blueprint import Blueprint

        schema = {
            "class": "TestDoc",
            "properties": {
                "text_field": {"type": "string"},
                "number_field": {"type": "number"},
                "date_field": {"type": "string", "format": "date"},
                "boolean_field": {"type": "boolean"},
                "array_field": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }

        blueprint = Blueprint(
            blueprint_id="bp-types",
            name="Type Test",
            description="Test field types",
            document_type="test",
            industry="test",
            stage="DEVELOPMENT",
            schema=schema,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        props = blueprint.schema["properties"]
        assert props["text_field"]["type"] == "string"
        assert props["number_field"]["type"] == "number"
        assert props["array_field"]["type"] == "array"

    @pytest.mark.unit
    def test_blueprint_nested_definitions(self):
        """Test blueprint with nested type definitions."""
        from backend.models.blueprint import Blueprint

        schema = {
            "class": "Invoice",
            "definitions": {
                "LineItem": {
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "amount": {"type": "number"}
                    }
                }
            },
            "properties": {
                "line_items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/LineItem"}
                }
            }
        }

        blueprint = Blueprint(
            blueprint_id="bp-nested",
            name="Nested Blueprint",
            description="Has nested types",
            document_type="invoice",
            industry="financial_services",
            stage="LIVE",
            schema=schema,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        assert "definitions" in blueprint.schema
        assert "LineItem" in blueprint.schema["definitions"]


class TestBlueprintDocumentTypes:
    """Tests for blueprint document type configurations."""

    @pytest.mark.unit
    def test_financial_document_types(self):
        """Test financial services document types."""
        from backend.models.blueprint import Blueprint

        doc_types = ["invoice", "receipt", "bank_statement", "w9", "contract"]

        for doc_type in doc_types:
            blueprint = Blueprint(
                blueprint_id=f"bp-{doc_type}",
                name=f"{doc_type} Blueprint",
                description=f"Extract {doc_type}",
                document_type=doc_type,
                industry="financial_services",
                stage="DEVELOPMENT",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert blueprint.document_type == doc_type

    @pytest.mark.unit
    def test_manufacturing_document_types(self):
        """Test manufacturing document types."""
        from backend.models.blueprint import Blueprint

        doc_types = ["purchase_order", "bill_of_lading", "packing_slip", "quality_report"]

        for doc_type in doc_types:
            blueprint = Blueprint(
                blueprint_id=f"bp-mfg-{doc_type}",
                name=f"{doc_type} Blueprint",
                description=f"Extract {doc_type}",
                document_type=doc_type,
                industry="manufacturing",
                stage="DEVELOPMENT",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert blueprint.industry == "manufacturing"

    @pytest.mark.unit
    def test_hr_document_types(self):
        """Test HR document types."""
        from backend.models.blueprint import Blueprint

        doc_types = ["resume", "offer_letter", "i9_form", "w4_form"]

        for doc_type in doc_types:
            blueprint = Blueprint(
                blueprint_id=f"bp-hr-{doc_type}",
                name=f"{doc_type} Blueprint",
                description=f"Extract {doc_type}",
                document_type=doc_type,
                industry="hr",
                stage="DEVELOPMENT",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            assert blueprint.industry == "hr"
