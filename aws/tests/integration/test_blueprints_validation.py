"""
Integration tests for validating all industry blueprints.
Tests JSON schema structure, required fields, and BDA compatibility.
"""
import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any, List


BLUEPRINTS_DIR = Path(__file__).parent.parent.parent / "blueprints"

INDUSTRIES = [
    "financial_services",
    "manufacturing",
    "hr",
    "healthcare_payers",
    "healthcare_providers",
    "healthcare_clinical",
    "retail",
    "cpg",
    "insurance_underwriting",
    "contact_center",
    "airlines",
    "supply_chain",
]

REQUIRED_TOP_LEVEL_FIELDS = [
    "blueprintName",
    "blueprintVersion",
    "description",
    "industry",
    "documentType",
    "bdaSchema",
]

REQUIRED_SCHEMA_FIELDS = ["class", "properties"]

VALID_PROPERTY_TYPES = ["string", "number", "boolean", "array", "object"]


def get_all_blueprints() -> List[tuple]:
    """Get all blueprint files across all industries."""
    blueprints = []
    for industry in INDUSTRIES:
        industry_dir = BLUEPRINTS_DIR / industry
        if industry_dir.exists():
            for bp_file in industry_dir.glob("*.json"):
                blueprints.append((industry, bp_file.name, bp_file))
    return blueprints


def load_blueprint(filepath: Path) -> Dict[str, Any]:
    """Load and parse blueprint JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)


class TestBlueprintStructure:
    """Tests for blueprint JSON structure validation."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_blueprint_has_required_fields(self, industry, filename, filepath):
        """Test that each blueprint has all required top-level fields."""
        blueprint = load_blueprint(filepath)

        for field in REQUIRED_TOP_LEVEL_FIELDS:
            assert field in blueprint, f"{filename}: Missing required field '{field}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_blueprint_has_valid_schema(self, industry, filename, filepath):
        """Test that bdaSchema has required fields."""
        blueprint = load_blueprint(filepath)
        schema = blueprint.get("bdaSchema", {})

        for field in REQUIRED_SCHEMA_FIELDS:
            assert field in schema, f"{filename}: bdaSchema missing '{field}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_blueprint_industry_matches_directory(self, industry, filename, filepath):
        """Test that blueprint industry field matches directory name."""
        blueprint = load_blueprint(filepath)
        assert blueprint["industry"] == industry, \
            f"{filename}: Industry mismatch - expected '{industry}', got '{blueprint['industry']}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_blueprint_version_format(self, industry, filename, filepath):
        """Test that blueprint version follows semver format."""
        blueprint = load_blueprint(filepath)
        version = blueprint.get("blueprintVersion", "")

        parts = version.split(".")
        assert len(parts) == 3, f"{filename}: Version '{version}' not in X.Y.Z format"
        for part in parts:
            assert part.isdigit(), f"{filename}: Version part '{part}' is not numeric"


class TestBDASchemaProperties:
    """Tests for BDA schema property validation."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_properties_have_valid_types(self, industry, filename, filepath):
        """Test that all properties have valid types."""
        blueprint = load_blueprint(filepath)
        properties = blueprint.get("bdaSchema", {}).get("properties", {})

        for prop_name, prop_def in properties.items():
            prop_type = prop_def.get("type")
            assert prop_type in VALID_PROPERTY_TYPES, \
                f"{filename}: Property '{prop_name}' has invalid type '{prop_type}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_array_properties_have_items(self, industry, filename, filepath):
        """Test that array properties define items schema."""
        blueprint = load_blueprint(filepath)
        properties = blueprint.get("bdaSchema", {}).get("properties", {})

        for prop_name, prop_def in properties.items():
            if prop_def.get("type") == "array":
                has_items = "items" in prop_def or "$ref" in prop_def.get("items", {})
                assert "items" in prop_def, \
                    f"{filename}: Array property '{prop_name}' missing 'items' definition"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_definitions_referenced_correctly(self, industry, filename, filepath):
        """Test that $ref references point to valid definitions."""
        blueprint = load_blueprint(filepath)
        schema = blueprint.get("bdaSchema", {})
        definitions = schema.get("definitions", {})
        properties = schema.get("properties", {})

        def check_refs(obj, path=""):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref = obj["$ref"]
                    if ref.startswith("#/definitions/"):
                        def_name = ref.replace("#/definitions/", "")
                        assert def_name in definitions, \
                            f"{filename}: Reference '{ref}' at {path} not found in definitions"
                for key, value in obj.items():
                    check_refs(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_refs(item, f"{path}[{i}]")

        check_refs(properties)


class TestIndustrySpecificBlueprints:
    """Tests for industry-specific blueprint requirements."""

    @pytest.mark.integration
    def test_healthcare_payers_blueprints_exist(self):
        """Test healthcare payers has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "healthcare_payers"
        assert industry_dir.exists(), "healthcare_payers directory missing"

        expected = ["medical_claim.json", "eob.json", "prior_authorization.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_healthcare_providers_blueprints_exist(self):
        """Test healthcare providers has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "healthcare_providers"
        assert industry_dir.exists(), "healthcare_providers directory missing"

        expected = ["patient_intake.json", "referral.json", "discharge_summary.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_healthcare_clinical_blueprints_exist(self):
        """Test healthcare clinical has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "healthcare_clinical"
        assert industry_dir.exists(), "healthcare_clinical directory missing"

        expected = ["lab_results.json", "prescription.json", "clinical_notes.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_retail_blueprints_exist(self):
        """Test retail has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "retail"
        assert industry_dir.exists(), "retail directory missing"

        expected = ["receipt.json", "return_form.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_cpg_blueprints_exist(self):
        """Test CPG has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "cpg"
        assert industry_dir.exists(), "cpg directory missing"

        expected = ["product_specification.json", "compliance_certificate.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_insurance_underwriting_blueprints_exist(self):
        """Test insurance underwriting has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "insurance_underwriting"
        assert industry_dir.exists(), "insurance_underwriting directory missing"

        expected = ["insurance_application.json", "risk_assessment.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_contact_center_blueprints_exist(self):
        """Test contact center has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "contact_center"
        assert industry_dir.exists(), "contact_center directory missing"

        expected = ["call_transcript.json", "case_notes.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_airlines_blueprints_exist(self):
        """Test airlines has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "airlines"
        assert industry_dir.exists(), "airlines directory missing"

        expected = ["boarding_pass.json", "baggage_claim.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_supply_chain_blueprints_exist(self):
        """Test supply chain has required blueprints."""
        industry_dir = BLUEPRINTS_DIR / "supply_chain"
        assert industry_dir.exists(), "supply_chain directory missing"

        expected = ["demand_forecast.json", "replenishment_order.json"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"


class TestBlueprintExtractionRules:
    """Tests for blueprint extraction rules configuration."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_extraction_rules_valid(self, industry, filename, filepath):
        """Test that extraction rules have valid configuration."""
        blueprint = load_blueprint(filepath)
        rules = blueprint.get("extractionRules", {})

        if "confidenceThreshold" in rules:
            threshold = rules["confidenceThreshold"]
            assert 0 <= threshold <= 1, \
                f"{filename}: confidenceThreshold {threshold} not in range 0-1"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_output_configuration_valid(self, industry, filename, filepath):
        """Test that output configuration has valid settings."""
        blueprint = load_blueprint(filepath)
        output = blueprint.get("outputConfiguration", {})

        for field in ["includeConfidenceScores", "includeBoundingBoxes", "includeRawText"]:
            if field in output:
                assert isinstance(output[field], bool), \
                    f"{filename}: {field} should be boolean"


class TestBlueprintValidationRules:
    """Tests for blueprint validation rules."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_blueprints())
    def test_validation_rules_structure(self, industry, filename, filepath):
        """Test that validation rules have required structure."""
        blueprint = load_blueprint(filepath)
        rules = blueprint.get("validationRules", [])

        for i, rule in enumerate(rules):
            assert "name" in rule, f"{filename}: Validation rule {i} missing 'name'"
            assert "expression" in rule, f"{filename}: Validation rule {i} missing 'expression'"
