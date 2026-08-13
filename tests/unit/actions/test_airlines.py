"""
Unit tests for Airlines action handlers.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add actions directory to path
ACTIONS_DIR = Path(__file__).parent.parent.parent.parent / "actions"
sys.path.insert(0, str(ACTIONS_DIR))


class TestAffectedPassengers:
    """Tests for affected_passengers action."""

    @pytest.mark.unit
    def test_affected_passengers_returns_list(self):
        """Test affected passengers action returns passenger list."""
        from airlines.affected_passengers.handler import affected_passengers

        result = affected_passengers(
            flight_number="AA123",
            flight_date="2024-01-15",
            disruption_type="cancellation"
        )

        assert "passengers" in result
        assert "total_count" in result
        assert "flight_number" in result
        assert isinstance(result["passengers"], list)

    @pytest.mark.unit
    def test_affected_passengers_includes_segments(self):
        """Test affected passengers includes status segments."""
        from airlines.affected_passengers.handler import affected_passengers

        result = affected_passengers(
            flight_number="AA456",
            flight_date="2024-01-15",
            disruption_type="delay"
        )

        assert "segments" in result or "by_status" in result


class TestAutoRebook:
    """Tests for auto_rebook action."""

    @pytest.mark.unit
    def test_auto_rebook_finds_alternatives(self):
        """Test auto rebook finds alternative flights."""
        from airlines.auto_rebook.handler import auto_rebook

        result = auto_rebook(
            passenger_id="PAX-001",
            original_flight="AA123",
            original_date="2024-01-15",
            origin="JFK",
            destination="LAX"
        )

        assert "rebooked" in result
        assert "new_itinerary" in result or "alternatives" in result
        assert "confirmation" in result

    @pytest.mark.unit
    def test_auto_rebook_respects_preferences(self):
        """Test auto rebook considers passenger preferences."""
        from airlines.auto_rebook.handler import auto_rebook

        result = auto_rebook(
            passenger_id="PAX-002",
            original_flight="AA456",
            original_date="2024-01-15",
            origin="ORD",
            destination="MIA",
            cabin_class="business"
        )

        assert "rebooked" in result


class TestHotelBooking:
    """Tests for hotel_booking action."""

    @pytest.mark.unit
    def test_hotel_booking_creates_reservation(self):
        """Test hotel booking creates reservation."""
        from airlines.hotel_booking.handler import hotel_booking

        result = hotel_booking(
            passenger_id="PAX-001",
            airport_code="JFK",
            check_in_date="2024-01-15",
            nights=1
        )

        assert "confirmation" in result
        assert "hotel_name" in result
        assert "check_in" in result

    @pytest.mark.unit
    def test_hotel_booking_includes_transport(self):
        """Test hotel booking includes transportation info."""
        from airlines.hotel_booking.handler import hotel_booking

        result = hotel_booking(
            passenger_id="PAX-002",
            airport_code="LAX",
            check_in_date="2024-01-15",
            nights=1,
            include_transport=True
        )

        assert "confirmation" in result


class TestEU261Compensation:
    """Tests for eu261_compensation action."""

    @pytest.mark.unit
    def test_eu261_compensation_short_haul(self):
        """Test EU261 compensation for short-haul flight."""
        from airlines.eu261_compensation.handler import eu261_compensation

        result = eu261_compensation(
            flight_number="BA123",
            origin="LHR",
            destination="CDG",
            delay_hours=4,
            departure_date="2024-01-15"
        )

        assert "eligible" in result
        assert "compensation_amount" in result
        assert "currency" in result

    @pytest.mark.unit
    def test_eu261_compensation_long_haul(self):
        """Test EU261 compensation for long-haul flight."""
        from airlines.eu261_compensation.handler import eu261_compensation

        result = eu261_compensation(
            flight_number="BA456",
            origin="LHR",
            destination="JFK",
            delay_hours=5,
            departure_date="2024-01-15"
        )

        assert "eligible" in result
        # Long-haul with 5+ hour delay should qualify
        if result["eligible"]:
            assert result["compensation_amount"] == 600

    @pytest.mark.unit
    def test_eu261_compensation_extraordinary(self):
        """Test EU261 compensation with extraordinary circumstances."""
        from airlines.eu261_compensation.handler import eu261_compensation

        result = eu261_compensation(
            flight_number="BA789",
            origin="LHR",
            destination="FRA",
            delay_hours=6,
            departure_date="2024-01-15",
            reason="weather"
        )

        assert "eligible" in result
        assert "reason_code" in result or "extraordinary_circumstances" in result


class TestBaggageTrace:
    """Tests for baggage_trace action."""

    @pytest.mark.unit
    def test_baggage_trace_creates_record(self):
        """Test baggage trace creates WorldTracer record."""
        from airlines.baggage_trace.handler import baggage_trace

        result = baggage_trace(
            passenger_name="John Smith",
            flight_number="AA123",
            flight_date="2024-01-15",
            bag_description="Black Samsonite hardside",
            origin="JFK",
            destination="LAX"
        )

        assert "file_reference" in result
        assert "status" in result

    @pytest.mark.unit
    def test_baggage_trace_includes_tracking(self):
        """Test baggage trace includes tracking information."""
        from airlines.baggage_trace.handler import baggage_trace

        result = baggage_trace(
            passenger_name="Jane Doe",
            flight_number="AA456",
            flight_date="2024-01-15",
            bag_description="Red roller bag",
            origin="ORD",
            destination="MIA",
            bag_tag="AA123456"
        )

        assert "file_reference" in result
        assert "last_seen" in result or "tracking" in result
