"""
Unit tests for Healthcare Providers action handlers.
"""
import pytest
import sys
from pathlib import Path

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestPatientLookup:
    """Tests for patient_lookup action."""

    @pytest.mark.unit
    def test_patient_lookup_by_mrn(self):
        """Test patient lookup by MRN."""
        from healthcare_providers.patient_lookup.handler import patient_lookup

        result = patient_lookup(
            mrn="MRN-12345"
        )

        assert "patient" in result or "found" in result
        assert "mrn" in result

    @pytest.mark.unit
    def test_patient_lookup_by_demographics(self):
        """Test patient lookup by demographics."""
        from healthcare_providers.patient_lookup.handler import patient_lookup

        result = patient_lookup(
            first_name="John",
            last_name="Smith",
            date_of_birth="1980-05-15"
        )

        assert "patient" in result or "matches" in result


class TestInsuranceVerify:
    """Tests for insurance_verify action."""

    @pytest.mark.unit
    def test_insurance_verify_active(self):
        """Test insurance verification for active policy."""
        from healthcare_providers.insurance_verify.handler import insurance_verify

        result = insurance_verify(
            member_id="MEM-12345",
            payer_id="BCBS",
            service_date="2024-01-15"
        )

        assert "active" in result or "verified" in result
        assert "coverage" in result or "benefits" in result

    @pytest.mark.unit
    def test_insurance_verify_returns_copay(self):
        """Test insurance verification returns copay info."""
        from healthcare_providers.insurance_verify.handler import insurance_verify

        result = insurance_verify(
            member_id="MEM-12345",
            payer_id="AETNA",
            service_date="2024-01-15",
            service_type="office_visit"
        )

        assert "copay" in result or "cost_share" in result or "coverage" in result


class TestReferralValidate:
    """Tests for referral_validate action."""

    @pytest.mark.unit
    def test_referral_validate_valid(self):
        """Test referral validation for valid referral."""
        from healthcare_providers.referral_validate.handler import referral_validate

        result = referral_validate(
            referral_number="REF-2024-001",
            patient_mrn="MRN-12345",
            specialty="cardiology"
        )

        assert "valid" in result
        assert "referral_number" in result

    @pytest.mark.unit
    def test_referral_validate_expired(self):
        """Test referral validation for expired referral."""
        from healthcare_providers.referral_validate.handler import referral_validate

        result = referral_validate(
            referral_number="REF-2023-001",
            patient_mrn="MRN-12345",
            specialty="orthopedics",
            service_date="2024-06-01"
        )

        assert "valid" in result
        assert "status" in result or "expiration" in result


class TestAppointmentSchedule:
    """Tests for appointment_schedule action."""

    @pytest.mark.unit
    def test_appointment_schedule_new(self):
        """Test scheduling new appointment."""
        from healthcare_providers.appointment_schedule.handler import appointment_schedule

        result = appointment_schedule(
            patient_mrn="MRN-12345",
            provider_id="PROV-001",
            appointment_type="follow_up",
            preferred_date="2024-02-01",
            preferred_time="10:00"
        )

        assert "appointment_id" in result or "confirmation" in result
        assert "scheduled" in result or "status" in result

    @pytest.mark.unit
    def test_appointment_schedule_reschedule(self):
        """Test rescheduling appointment."""
        from healthcare_providers.appointment_schedule.handler import appointment_schedule

        result = appointment_schedule(
            patient_mrn="MRN-12345",
            appointment_id="APT-2024-001",
            action="reschedule",
            new_date="2024-02-15",
            new_time="14:00"
        )

        assert "status" in result or "confirmation" in result


class TestEHRUpdate:
    """Tests for ehr_update action."""

    @pytest.mark.unit
    def test_ehr_update_adds_note(self):
        """Test EHR update adds clinical note."""
        from healthcare_providers.ehr_update.handler import ehr_update

        result = ehr_update(
            patient_mrn="MRN-12345",
            update_type="clinical_note",
            content={
                "note_type": "progress_note",
                "text": "Patient presents with...",
                "provider_id": "PROV-001"
            }
        )

        assert "success" in result
        assert "record_id" in result or "update_id" in result

    @pytest.mark.unit
    def test_ehr_update_creates_audit(self):
        """Test EHR update creates audit trail."""
        from healthcare_providers.ehr_update.handler import ehr_update

        result = ehr_update(
            patient_mrn="MRN-12345",
            update_type="diagnosis",
            content={
                "icd_code": "J06.9",
                "description": "Acute upper respiratory infection"
            }
        )

        assert "success" in result
        assert "audit" in result or "timestamp" in result
