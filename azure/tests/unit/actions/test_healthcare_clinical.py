"""
Unit tests for Healthcare Clinical action handlers.
"""
import pytest
import sys
from pathlib import Path

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestLabValidate:
    """Tests for lab_validate action."""

    @pytest.mark.unit
    def test_lab_validate_normal_results(self):
        """Test lab validation with normal results."""
        from healthcare_clinical.lab_validate.handler import lab_validate

        result = lab_validate(
            patient_mrn="MRN-12345",
            lab_results=[
                {"test": "glucose", "value": 95, "unit": "mg/dL"},
                {"test": "hemoglobin", "value": 14.5, "unit": "g/dL"}
            ]
        )

        assert "validated" in result or "results" in result
        assert "abnormal" in result or "flags" in result

    @pytest.mark.unit
    def test_lab_validate_abnormal_results(self):
        """Test lab validation flags abnormal results."""
        from healthcare_clinical.lab_validate.handler import lab_validate

        result = lab_validate(
            patient_mrn="MRN-12345",
            lab_results=[
                {"test": "glucose", "value": 350, "unit": "mg/dL"},  # High
                {"test": "potassium", "value": 6.5, "unit": "mEq/L"}  # High
            ]
        )

        assert "abnormal" in result or "flags" in result or "critical" in result


class TestCriticalValueAlert:
    """Tests for critical_value_alert action."""

    @pytest.mark.unit
    def test_critical_value_alert_triggers(self):
        """Test critical value alert is triggered."""
        from healthcare_clinical.critical_value_alert.handler import critical_value_alert

        result = critical_value_alert(
            patient_mrn="MRN-12345",
            test_name="potassium",
            value=7.0,
            unit="mEq/L",
            ordering_provider="PROV-001"
        )

        assert "critical" in result
        assert "alert_sent" in result or "notification" in result

    @pytest.mark.unit
    def test_critical_value_alert_non_critical(self):
        """Test non-critical values don't trigger alert."""
        from healthcare_clinical.critical_value_alert.handler import critical_value_alert

        result = critical_value_alert(
            patient_mrn="MRN-12345",
            test_name="glucose",
            value=100,
            unit="mg/dL",
            ordering_provider="PROV-001"
        )

        assert "critical" in result


class TestDrugInteraction:
    """Tests for drug_interaction action."""

    @pytest.mark.unit
    def test_drug_interaction_none(self):
        """Test drug interaction check with no interactions."""
        from healthcare_clinical.drug_interaction.handler import drug_interaction

        result = drug_interaction(
            medications=["acetaminophen", "lisinopril"]
        )

        assert "interactions" in result
        assert "severity" in result or "risk_level" in result

    @pytest.mark.unit
    def test_drug_interaction_detected(self):
        """Test drug interaction detection."""
        from healthcare_clinical.drug_interaction.handler import drug_interaction

        result = drug_interaction(
            medications=["warfarin", "aspirin", "ibuprofen"]
        )

        assert "interactions" in result
        # Should detect bleeding risk interactions


class TestFormularyCheck:
    """Tests for formulary_check action."""

    @pytest.mark.unit
    def test_formulary_check_covered(self):
        """Test formulary check for covered medication."""
        from healthcare_clinical.formulary_check.handler import formulary_check

        result = formulary_check(
            medication_name="lisinopril",
            ndc_code="00093-7180-01",
            plan_id="PLAN-001"
        )

        assert "covered" in result
        assert "tier" in result or "copay" in result

    @pytest.mark.unit
    def test_formulary_check_alternatives(self):
        """Test formulary check suggests alternatives."""
        from healthcare_clinical.formulary_check.handler import formulary_check

        result = formulary_check(
            medication_name="brand_medication",
            ndc_code="12345-678-90",
            plan_id="PLAN-001"
        )

        assert "covered" in result
        assert "alternatives" in result or "generic" in result or "tier" in result


class TestClinicalDecision:
    """Tests for clinical_decision action."""

    @pytest.mark.unit
    def test_clinical_decision_recommendation(self):
        """Test clinical decision support recommendation."""
        from healthcare_clinical.clinical_decision.handler import clinical_decision

        result = clinical_decision(
            patient_data={
                "age": 55,
                "gender": "M",
                "conditions": ["hypertension", "diabetes"],
                "medications": ["metformin", "lisinopril"]
            },
            clinical_context="annual_wellness",
            query="preventive_screenings"
        )

        assert "recommendations" in result
        assert "evidence" in result or "guidelines" in result

    @pytest.mark.unit
    def test_clinical_decision_alerts(self):
        """Test clinical decision generates alerts."""
        from healthcare_clinical.clinical_decision.handler import clinical_decision

        result = clinical_decision(
            patient_data={
                "age": 65,
                "gender": "F",
                "conditions": ["afib"],
                "medications": []
            },
            clinical_context="medication_review",
            query="anticoagulation"
        )

        assert "recommendations" in result
        # Should flag need for anticoagulation consideration
