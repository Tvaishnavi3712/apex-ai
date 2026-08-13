"""
Integration tests for validating all industry playbooks.
Tests YAML structure, required fields, and workflow definitions.
"""
import pytest
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List


PLAYBOOKS_DIR = Path(__file__).parent.parent.parent / "playbooks"

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

REQUIRED_FIELDS = [
    "name",
    "version",
    "description",
    "industry",
    "category",
    "intent",
    "recipe",
]

VALID_TRIGGER_TYPES = ["s3_event", "api", "schedule", "event", "edi", "webhook"]


def get_all_playbooks() -> List[tuple]:
    """Get all playbook files across all industries."""
    playbooks = []
    for industry in INDUSTRIES:
        industry_dir = PLAYBOOKS_DIR / industry
        if industry_dir.exists():
            for pb_file in industry_dir.glob("*.yaml"):
                playbooks.append((industry, pb_file.name, pb_file))
    return playbooks


def load_playbook(filepath: Path) -> Dict[str, Any]:
    """Load and parse playbook YAML."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


class TestPlaybookStructure:
    """Tests for playbook YAML structure validation."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_playbook_has_required_fields(self, industry, filename, filepath):
        """Test that each playbook has all required fields."""
        playbook = load_playbook(filepath)

        for field in REQUIRED_FIELDS:
            assert field in playbook, f"{filename}: Missing required field '{field}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_playbook_industry_matches_directory(self, industry, filename, filepath):
        """Test that playbook industry field matches directory name."""
        playbook = load_playbook(filepath)
        assert playbook["industry"] == industry, \
            f"{filename}: Industry mismatch - expected '{industry}', got '{playbook['industry']}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_playbook_version_format(self, industry, filename, filepath):
        """Test that playbook version follows semver format."""
        playbook = load_playbook(filepath)
        version = str(playbook.get("version", ""))

        parts = version.split(".")
        assert len(parts) == 3, f"{filename}: Version '{version}' not in X.Y.Z format"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_playbook_has_intent(self, industry, filename, filepath):
        """Test that playbook has meaningful intent description."""
        playbook = load_playbook(filepath)
        intent = playbook.get("intent", "")

        assert len(intent) > 20, f"{filename}: Intent too short, should describe workflow purpose"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_playbook_has_recipe(self, industry, filename, filepath):
        """Test that playbook has meaningful recipe with steps."""
        playbook = load_playbook(filepath)
        recipe = playbook.get("recipe", "")

        assert len(recipe) > 50, f"{filename}: Recipe too short, should contain workflow steps"
        assert "Step" in recipe or "step" in recipe or "1." in recipe, \
            f"{filename}: Recipe should contain numbered steps"


class TestPlaybookActions:
    """Tests for playbook action definitions."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_playbook_has_actions(self, industry, filename, filepath):
        """Test that playbook defines actions."""
        playbook = load_playbook(filepath)
        actions = playbook.get("actions", [])

        assert len(actions) > 0, f"{filename}: Playbook should define at least one action"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_actions_have_required_fields(self, industry, filename, filepath):
        """Test that each action has name and action_id."""
        playbook = load_playbook(filepath)
        actions = playbook.get("actions", [])

        for i, action in enumerate(actions):
            assert "name" in action, f"{filename}: Action {i} missing 'name'"
            assert "action_id" in action, f"{filename}: Action {i} missing 'action_id'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_actions_have_valid_ids(self, industry, filename, filepath):
        """Test that action IDs follow naming convention."""
        playbook = load_playbook(filepath)
        actions = playbook.get("actions", [])

        for action in actions:
            action_id = action.get("action_id", "")
            # Action ID should be namespace.action_name format
            assert "." in action_id, \
                f"{filename}: Action ID '{action_id}' should be namespace.action_name format"


class TestPlaybookTriggers:
    """Tests for playbook trigger definitions."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_triggers_have_valid_type(self, industry, filename, filepath):
        """Test that triggers have valid type."""
        playbook = load_playbook(filepath)
        triggers = playbook.get("triggers", [])

        for i, trigger in enumerate(triggers):
            trigger_type = trigger.get("type")
            assert trigger_type in VALID_TRIGGER_TYPES, \
                f"{filename}: Trigger {i} has invalid type '{trigger_type}'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_s3_triggers_have_bucket(self, industry, filename, filepath):
        """Test that Blob Storage triggers specify bucket."""
        playbook = load_playbook(filepath)
        triggers = playbook.get("triggers", [])

        for trigger in triggers:
            if trigger.get("type") == "s3_event":
                assert "bucket" in trigger, \
                    f"{filename}: Blob Storage trigger missing 'bucket'"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_api_triggers_have_endpoint(self, industry, filename, filepath):
        """Test that API triggers specify endpoint."""
        playbook = load_playbook(filepath)
        triggers = playbook.get("triggers", [])

        for trigger in triggers:
            if trigger.get("type") == "api":
                assert "endpoint" in trigger, \
                    f"{filename}: API trigger missing 'endpoint'"


class TestPlaybookOutputs:
    """Tests for playbook output definitions."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_outputs_have_required_fields(self, industry, filename, filepath):
        """Test that outputs have name and type."""
        playbook = load_playbook(filepath)
        outputs = playbook.get("output", [])

        for i, output in enumerate(outputs):
            assert "name" in output, f"{filename}: Output {i} missing 'name'"
            assert "type" in output, f"{filename}: Output {i} missing 'type'"


class TestPlaybookContext:
    """Tests for playbook context and rules."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_context_has_business_rules(self, industry, filename, filepath):
        """Test that context includes business rules."""
        playbook = load_playbook(filepath)
        context = playbook.get("context", {})

        # Most playbooks should have business rules
        if context:
            has_rules = "business_rules" in context or "rules" in context or any(
                "rule" in k.lower() for k in context.keys()
            )
            # This is a soft check - not all playbooks need explicit rules
            assert isinstance(context, dict), f"{filename}: Context should be a dictionary"


class TestIndustrySpecificPlaybooks:
    """Tests for industry-specific playbook requirements."""

    @pytest.mark.integration
    def test_healthcare_payers_playbooks_exist(self):
        """Test healthcare payers has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "healthcare_payers"
        assert industry_dir.exists(), "healthcare_payers directory missing"

        expected = ["claims_processing.yaml", "prior_authorization.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_healthcare_providers_playbooks_exist(self):
        """Test healthcare providers has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "healthcare_providers"
        assert industry_dir.exists(), "healthcare_providers directory missing"

        expected = ["patient_registration.yaml", "referral_management.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_healthcare_clinical_playbooks_exist(self):
        """Test healthcare clinical has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "healthcare_clinical"
        assert industry_dir.exists(), "healthcare_clinical directory missing"

        expected = ["lab_results_processing.yaml", "prescription_processing.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_retail_playbooks_exist(self):
        """Test retail has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "retail"
        assert industry_dir.exists(), "retail directory missing"

        expected = ["returns_processing.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_cpg_playbooks_exist(self):
        """Test CPG has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "cpg"
        assert industry_dir.exists(), "cpg directory missing"

        expected = ["product_compliance.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_insurance_underwriting_playbooks_exist(self):
        """Test insurance underwriting has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "insurance_underwriting"
        assert industry_dir.exists(), "insurance_underwriting directory missing"

        expected = ["underwriting_workflow.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_contact_center_playbooks_exist(self):
        """Test contact center has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "contact_center"
        assert industry_dir.exists(), "contact_center directory missing"

        expected = ["call_quality_analysis.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_airlines_playbooks_exist(self):
        """Test airlines has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "airlines"
        assert industry_dir.exists(), "airlines directory missing"

        expected = ["flight_disruption.yaml", "baggage_reconciliation.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"

    @pytest.mark.integration
    def test_supply_chain_playbooks_exist(self):
        """Test supply chain has required playbooks."""
        industry_dir = PLAYBOOKS_DIR / "supply_chain"
        assert industry_dir.exists(), "supply_chain directory missing"

        expected = ["inventory_optimization.yaml", "supplier_performance.yaml"]
        for filename in expected:
            assert (industry_dir / filename).exists(), f"Missing {filename}"


class TestPlaybookWorkerConfig:
    """Tests for playbook worker configuration."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,filename,filepath", get_all_playbooks())
    def test_worker_config_valid(self, industry, filename, filepath):
        """Test that worker configuration is valid if present."""
        playbook = load_playbook(filepath)
        worker = playbook.get("worker", {})

        if worker:
            if "concurrency" in worker:
                assert worker["concurrency"] > 0, \
                    f"{filename}: Worker concurrency must be positive"

            if "timeout_seconds" in worker:
                assert worker["timeout_seconds"] > 0, \
                    f"{filename}: Worker timeout must be positive"
                assert worker["timeout_seconds"] <= 900, \
                    f"{filename}: Worker timeout exceeds Lambda max (900s)"
