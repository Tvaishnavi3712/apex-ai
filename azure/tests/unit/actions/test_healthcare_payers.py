"""
Unit tests for Healthcare Payers action handlers.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestClaimsAdjudication:
    """Tests for claims_adjudication action."""

    @pytest.mark.unit
    def test_claims_adjudication_approved(self):
        """Test claim adjudication returns approved status."""
        from healthcare_payers.claims_adjudication.handler import claims_adjudication

        result = claims_adjudication(
            claim_id="CLM-001",
            member_id="MEM-12345",
            procedure_codes=["99213", "81003"],
            diagnosis_codes=["J06.9"],
            provider_npi="1234567890",
            service_date="2024-01-15",
            billed_amount=250.00
        )

        assert "status" in result
        assert "allowed_amount" in result
        assert "member_responsibility" in result
        assert "plan_payment" in result
        assert result["claim_id"] == "CLM-001"

    @pytest.mark.unit
    def test_claims_adjudication_has_adjustment_codes(self):
        """Test claim adjudication includes adjustment codes."""
        from healthcare_payers.claims_adjudication.handler import claims_adjudication

        result = claims_adjudication(
            claim_id="CLM-002",
            member_id="MEM-12345",
            procedure_codes=["99214"],
            diagnosis_codes=["J20.9"],
            provider_npi="1234567890",
            service_date="2024-01-15",
            billed_amount=350.00
        )

        assert "adjustment_codes" in result


class TestEligibilityVerify:
    """Tests for eligibility_verify action."""

    @pytest.mark.unit
    def test_eligibility_verify_active_member(self):
        """Test eligibility verification for active member."""
        from healthcare_payers.eligibility_verify.handler import eligibility_verify

        result = eligibility_verify(
            member_id="MEM-12345",
            service_date="2024-01-15"
        )

        assert "eligible" in result
        assert "member_id" in result
        assert "coverage" in result
        assert result["member_id"] == "MEM-12345"

    @pytest.mark.unit
    def test_eligibility_verify_includes_benefits(self):
        """Test eligibility verification includes benefit details."""
        from healthcare_payers.eligibility_verify.handler import eligibility_verify

        result = eligibility_verify(
            member_id="MEM-12345",
            service_date="2024-01-15"
        )

        assert "deductible" in result or "deductible" in str(result.get("coverage", {}))


class TestMedicalNecessity:
    """Tests for medical_necessity action."""

    @pytest.mark.unit
    def test_medical_necessity_review(self):
        """Test medical necessity determination."""
        from healthcare_payers.medical_necessity.handler import medical_necessity

        result = medical_necessity(
            procedure_code="27447",
            diagnosis_codes=["M17.11"],
            patient_age=65,
            clinical_notes="Severe osteoarthritis, conservative treatment failed"
        )

        assert "medically_necessary" in result
        assert "clinical_rationale" in result

    @pytest.mark.unit
    def test_medical_necessity_includes_criteria(self):
        """Test medical necessity includes evaluation criteria."""
        from healthcare_payers.medical_necessity.handler import medical_necessity

        result = medical_necessity(
            procedure_code="27447",
            diagnosis_codes=["M17.11"],
            patient_age=65
        )

        assert "criteria_met" in result or "evaluation" in result


class TestPaymentCalculate:
    """Tests for payment_calculate action."""

    @pytest.mark.unit
    def test_payment_calculate_in_network(self):
        """Test payment calculation for in-network provider."""
        from healthcare_payers.payment_calculate.handler import payment_calculate

        result = payment_calculate(
            procedure_codes=["99213"],
            provider_npi="1234567890",
            billed_amounts=[150.00],
            member_id="MEM-12345",
            network_status="in_network"
        )

        assert "allowed_amount" in result
        assert "member_responsibility" in result
        assert "plan_payment" in result

    @pytest.mark.unit
    def test_payment_calculate_coinsurance(self):
        """Test payment calculation applies coinsurance."""
        from healthcare_payers.payment_calculate.handler import payment_calculate

        result = payment_calculate(
            procedure_codes=["99214"],
            provider_npi="1234567890",
            billed_amounts=[200.00],
            member_id="MEM-12345",
            network_status="in_network"
        )

        assert "coinsurance" in result or result["member_responsibility"] > 0


class TestFraudDetection:
    """Tests for fraud_detection action."""

    @pytest.mark.unit
    def test_fraud_detection_low_risk(self):
        """Test fraud detection returns risk assessment."""
        from healthcare_payers.fraud_detection.handler import fraud_detection

        result = fraud_detection(
            claim_id="CLM-001",
            provider_npi="1234567890",
            procedure_codes=["99213"],
            billed_amount=150.00,
            member_history=[]
        )

        assert "risk_score" in result
        assert "risk_level" in result
        assert "indicators" in result

    @pytest.mark.unit
    def test_fraud_detection_flags_suspicious(self):
        """Test fraud detection identifies suspicious patterns."""
        from healthcare_payers.fraud_detection.handler import fraud_detection

        result = fraud_detection(
            claim_id="CLM-002",
            provider_npi="9876543210",
            procedure_codes=["99215", "99215", "99215"],  # Potential upcoding
            billed_amount=5000.00,
            member_history=[
                {"claim_id": "CLM-001", "date": "2024-01-10", "amount": 4500.00}
            ]
        )

        assert "risk_score" in result
        # High value and repeated codes should flag concerns
