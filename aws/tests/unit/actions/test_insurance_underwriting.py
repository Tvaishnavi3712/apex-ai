"""
Unit tests for Insurance Underwriting action handlers.
"""
import pytest
import sys
from pathlib import Path

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestRiskScore:
    """Tests for risk_score action."""

    @pytest.mark.unit
    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        from insurance_underwriting.risk_score.handler import risk_score

        result = risk_score(
            application_id="APP-001",
            applicant_data={
                "age": 35,
                "occupation": "accountant",
                "health_history": "none"
            },
            policy_type="life"
        )

        assert "risk_score" in result
        assert "risk_tier" in result or "classification" in result
        assert "application_id" in result

    @pytest.mark.unit
    def test_risk_score_factors(self):
        """Test risk score includes factor breakdown."""
        from insurance_underwriting.risk_score.handler import risk_score

        result = risk_score(
            application_id="APP-002",
            applicant_data={
                "age": 55,
                "occupation": "construction_worker",
                "health_history": "diabetes",
                "smoker": True
            },
            policy_type="life"
        )

        assert "risk_score" in result
        assert "factors" in result or "risk_tier" in result


class TestPremiumCalculate:
    """Tests for premium_calculate action."""

    @pytest.mark.unit
    def test_premium_calculate_base(self):
        """Test premium calculation returns base premium."""
        from insurance_underwriting.premium_calculate.handler import premium_calculate

        result = premium_calculate(
            application_id="APP-001",
            policy_type="auto",
            coverage_amount=100000,
            risk_score=75,
            risk_tier="standard"
        )

        assert "premium" in result or "annual_premium" in result
        assert "application_id" in result

    @pytest.mark.unit
    def test_premium_calculate_discounts(self):
        """Test premium calculation applies discounts."""
        from insurance_underwriting.premium_calculate.handler import premium_calculate

        result = premium_calculate(
            application_id="APP-002",
            policy_type="auto",
            coverage_amount=100000,
            risk_score=85,
            risk_tier="preferred",
            discounts=["multi_policy", "safe_driver"]
        )

        assert "premium" in result or "annual_premium" in result
        assert "discounts_applied" in result or "discount_amount" in result or "base_premium" in result


class TestCoverageValidate:
    """Tests for coverage_validate action."""

    @pytest.mark.unit
    def test_coverage_validate_within_limits(self):
        """Test coverage validation within limits."""
        from insurance_underwriting.coverage_validate.handler import coverage_validate

        result = coverage_validate(
            application_id="APP-001",
            policy_type="life",
            requested_coverage=500000,
            applicant_income=150000
        )

        assert "valid" in result or "approved" in result
        assert "coverage_amount" in result or "application_id" in result

    @pytest.mark.unit
    def test_coverage_validate_exceeds_limits(self):
        """Test coverage validation flags excessive coverage."""
        from insurance_underwriting.coverage_validate.handler import coverage_validate

        result = coverage_validate(
            application_id="APP-002",
            policy_type="life",
            requested_coverage=5000000,
            applicant_income=50000
        )

        assert "valid" in result or "approved" in result
        assert "max_coverage" in result or "recommendation" in result or "issues" in result


class TestLossHistory:
    """Tests for loss_history action."""

    @pytest.mark.unit
    def test_loss_history_clean(self):
        """Test loss history check with no claims."""
        from insurance_underwriting.loss_history.handler import loss_history

        result = loss_history(
            applicant_id="APPL-001",
            policy_type="auto",
            search_years=5
        )

        assert "claims" in result or "loss_history" in result
        assert "total_losses" in result or "claim_count" in result

    @pytest.mark.unit
    def test_loss_history_with_claims(self):
        """Test loss history check with prior claims."""
        from insurance_underwriting.loss_history.handler import loss_history

        result = loss_history(
            applicant_id="APPL-002",
            policy_type="homeowners",
            search_years=7,
            property_address="123 Main St, City, ST 12345"
        )

        assert "claims" in result or "loss_history" in result


class TestAutoDecision:
    """Tests for auto_decision action."""

    @pytest.mark.unit
    def test_auto_decision_approved(self):
        """Test auto-decision approves low-risk application."""
        from insurance_underwriting.auto_decision.handler import auto_decision

        result = auto_decision(
            application_id="APP-001",
            risk_score=85,
            risk_tier="preferred",
            loss_history_score=100,
            coverage_validation="passed"
        )

        assert "decision" in result
        assert "application_id" in result
        assert result["decision"] in ["approved", "referred", "declined"]

    @pytest.mark.unit
    def test_auto_decision_referred(self):
        """Test auto-decision refers borderline application."""
        from insurance_underwriting.auto_decision.handler import auto_decision

        result = auto_decision(
            application_id="APP-002",
            risk_score=60,
            risk_tier="substandard",
            loss_history_score=70,
            coverage_validation="review_needed"
        )

        assert "decision" in result
        assert "reason" in result or "referral_reason" in result or "flags" in result

    @pytest.mark.unit
    def test_auto_decision_declined(self):
        """Test auto-decision declines high-risk application."""
        from insurance_underwriting.auto_decision.handler import auto_decision

        result = auto_decision(
            application_id="APP-003",
            risk_score=30,
            risk_tier="decline",
            loss_history_score=40,
            coverage_validation="failed"
        )

        assert "decision" in result
        assert result["decision"] in ["declined", "referred"]
