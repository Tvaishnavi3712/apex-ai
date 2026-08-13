"""
Integration tests for validating all industry action handlers.
Tests action module structure, imports, and handler patterns.
"""
import pytest
import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Tuple


ACTIONS_DIR = Path(__file__).parent.parent.parent / "actions"

INDUSTRIES = [
    "healthcare_payers",
    "healthcare_providers",
    "healthcare_clinical",
    "retail",
    "cpg",
    "insurance_underwriting",
    "contact_center",
    "airlines",
    "supply_chain",
    "manufacturing",
    "hr",
]


def get_all_action_handlers() -> List[Tuple[str, str, Path]]:
    """Get all action handler files across all industries."""
    handlers = []
    for industry in INDUSTRIES:
        industry_dir = ACTIONS_DIR / industry
        if industry_dir.exists():
            for action_dir in industry_dir.iterdir():
                if action_dir.is_dir() and not action_dir.name.startswith("__"):
                    handler_file = action_dir / "handler.py"
                    if handler_file.exists():
                        handlers.append((industry, action_dir.name, handler_file))
    return handlers


def load_handler_module(filepath: Path):
    """Load handler module for inspection."""
    spec = importlib.util.spec_from_file_location("handler", filepath)
    module = importlib.util.module_from_spec(spec)
    # Add parent to path for imports
    sys.path.insert(0, str(filepath.parent.parent.parent))
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        return None
    finally:
        if str(filepath.parent.parent.parent) in sys.path:
            sys.path.remove(str(filepath.parent.parent.parent))


class TestActionHandlerStructure:
    """Tests for action handler file structure."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_file_exists(self, industry, action_name, filepath):
        """Test that handler.py exists for each action."""
        assert filepath.exists(), f"{industry}/{action_name}: handler.py missing"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_docstring(self, industry, action_name, filepath):
        """Test that handler has module docstring."""
        content = filepath.read_text()
        # Check for module docstring (triple quotes at start)
        assert '"""' in content[:500] or "'''" in content[:500], \
            f"{industry}/{action_name}: handler.py missing module docstring"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_imports_sdk(self, industry, action_name, filepath):
        """Test that handler imports the action SDK."""
        content = filepath.read_text()
        assert "from sdk import" in content or "import sdk" in content, \
            f"{industry}/{action_name}: handler.py should import sdk"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_decorator(self, industry, action_name, filepath):
        """Test that handler uses @apex_action decorator."""
        content = filepath.read_text()
        assert "@apex_action" in content, \
            f"{industry}/{action_name}: handler.py missing @apex_action decorator"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_lambda_entry(self, industry, action_name, filepath):
        """Test that handler has Lambda entry point."""
        content = filepath.read_text()
        assert "def handler(event, context)" in content or \
               "def handler(event," in content, \
            f"{industry}/{action_name}: handler.py missing Lambda handler function"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_class_implementation(self, industry, action_name, filepath):
        """Test that handler has class-based implementation."""
        content = filepath.read_text()
        assert "ApexActionBase" in content, \
            f"{industry}/{action_name}: handler.py missing ApexActionBase class"


class TestActionSchemaDefinitions:
    """Tests for action schema definitions."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_input_schema(self, industry, action_name, filepath):
        """Test that handler defines input schema."""
        content = filepath.read_text()
        assert "ActionInputSchema" in content or "input_schema" in content, \
            f"{industry}/{action_name}: handler.py missing input schema definition"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_output_schema(self, industry, action_name, filepath):
        """Test that handler defines output schema."""
        content = filepath.read_text()
        assert "ActionOutputSchema" in content or "output_schema" in content, \
            f"{industry}/{action_name}: handler.py missing output schema definition"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_action_has_name(self, industry, action_name, filepath):
        """Test that action defines a name."""
        content = filepath.read_text()
        assert 'name=' in content or 'name =' in content, \
            f"{industry}/{action_name}: handler.py missing action name"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_action_has_description(self, industry, action_name, filepath):
        """Test that action defines a description."""
        content = filepath.read_text()
        assert 'description=' in content or 'description =' in content, \
            f"{industry}/{action_name}: handler.py missing action description"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_action_has_category(self, industry, action_name, filepath):
        """Test that action defines a category."""
        content = filepath.read_text()
        assert 'category=' in content or 'category =' in content, \
            f"{industry}/{action_name}: handler.py missing action category"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_action_has_industry(self, industry, action_name, filepath):
        """Test that action defines an industry."""
        content = filepath.read_text()
        assert 'industry=' in content or 'industry =' in content, \
            f"{industry}/{action_name}: handler.py missing action industry"


class TestActionInitFiles:
    """Tests for action __init__.py files."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry", INDUSTRIES)
    def test_industry_has_init(self, industry):
        """Test that industry directory has __init__.py."""
        industry_dir = ACTIONS_DIR / industry
        if industry_dir.exists():
            init_file = industry_dir / "__init__.py"
            assert init_file.exists(), f"{industry}: missing __init__.py"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_action_dir_has_init(self, industry, action_name, filepath):
        """Test that each action directory has __init__.py."""
        action_dir = filepath.parent
        init_file = action_dir / "__init__.py"
        assert init_file.exists(), f"{industry}/{action_name}: missing __init__.py"


class TestIndustrySpecificActions:
    """Tests for industry-specific action requirements."""

    @pytest.mark.integration
    def test_healthcare_payers_actions_exist(self):
        """Test healthcare payers has required actions."""
        industry_dir = ACTIONS_DIR / "healthcare_payers"
        assert industry_dir.exists(), "healthcare_payers actions directory missing"

        expected = [
            "claims_adjudication",
            "eligibility_verify",
            "medical_necessity",
            "payment_calculate",
            "fraud_detection",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_healthcare_providers_actions_exist(self):
        """Test healthcare providers has required actions."""
        industry_dir = ACTIONS_DIR / "healthcare_providers"
        assert industry_dir.exists(), "healthcare_providers actions directory missing"

        expected = [
            "patient_lookup",
            "insurance_verify",
            "referral_validate",
            "appointment_schedule",
            "ehr_update",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_healthcare_clinical_actions_exist(self):
        """Test healthcare clinical has required actions."""
        industry_dir = ACTIONS_DIR / "healthcare_clinical"
        assert industry_dir.exists(), "healthcare_clinical actions directory missing"

        expected = [
            "lab_validate",
            "critical_value_alert",
            "drug_interaction",
            "formulary_check",
            "clinical_decision",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_retail_actions_exist(self):
        """Test retail has required actions."""
        industry_dir = ACTIONS_DIR / "retail"
        assert industry_dir.exists(), "retail actions directory missing"

        expected = [
            "receipt_validate",
            "return_policy",
            "fraud_score",
            "inventory_update",
            "refund_process",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_cpg_actions_exist(self):
        """Test CPG has required actions."""
        industry_dir = ACTIONS_DIR / "cpg"
        assert industry_dir.exists(), "cpg actions directory missing"

        expected = [
            "ingredient_validate",
            "regulatory_check",
            "label_compliance",
            "nutrition_validate",
            "allergen_check",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_insurance_underwriting_actions_exist(self):
        """Test insurance underwriting has required actions."""
        industry_dir = ACTIONS_DIR / "insurance_underwriting"
        assert industry_dir.exists(), "insurance_underwriting actions directory missing"

        expected = [
            "risk_score",
            "premium_calculate",
            "coverage_validate",
            "loss_history",
            "auto_decision",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_contact_center_actions_exist(self):
        """Test contact center has required actions."""
        industry_dir = ACTIONS_DIR / "contact_center"
        assert industry_dir.exists(), "contact_center actions directory missing"

        expected = [
            "sentiment_analyze",
            "compliance_check",
            "quality_score",
            "coaching_recommend",
            "escalation_detect",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_airlines_actions_exist(self):
        """Test airlines has required actions."""
        industry_dir = ACTIONS_DIR / "airlines"
        assert industry_dir.exists(), "airlines actions directory missing"

        expected = [
            "affected_passengers",
            "auto_rebook",
            "hotel_booking",
            "eu261_compensation",
            "baggage_trace",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"

    @pytest.mark.integration
    def test_supply_chain_actions_exist(self):
        """Test supply chain has required actions."""
        industry_dir = ACTIONS_DIR / "supply_chain"
        assert industry_dir.exists(), "supply_chain actions directory missing"

        expected = [
            "forecast_analyze",
            "inventory_analyze",
            "eoq_calculate",
            "reorder_point",
            "quality_metrics",
            "delivery_metrics",
            "scorecard_generate",
        ]
        for action in expected:
            action_handler = industry_dir / action / "handler.py"
            assert action_handler.exists(), f"Missing {action}/handler.py"


class TestActionReturnTypes:
    """Tests for action return type patterns."""

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_returns_dict(self, industry, action_name, filepath):
        """Test that handler function returns dict type hint."""
        content = filepath.read_text()
        # Check for return type annotation
        assert "-> dict" in content or "-> Dict" in content, \
            f"{industry}/{action_name}: handler function should return dict"

    @pytest.mark.integration
    @pytest.mark.parametrize("industry,action_name,filepath", get_all_action_handlers())
    def test_handler_has_try_except(self, industry, action_name, filepath):
        """Test that handler has error handling."""
        content = filepath.read_text()
        # Most handlers should have try/except for robustness
        assert "try:" in content and "except" in content, \
            f"{industry}/{action_name}: handler should have error handling"
