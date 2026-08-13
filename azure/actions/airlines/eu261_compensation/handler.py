"""
EU261 Compensation Action
Calculate and process EU261 compensation for flight disruptions
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import uuid

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# EU261 compensation amounts
EU261_COMPENSATION = {
    "short_haul": {  # < 1500km
        "delay_2h": 0,
        "delay_3h": 250,
        "cancelled": 250
    },
    "medium_haul": {  # 1500-3500km
        "delay_3h": 400,
        "delay_4h": 400,
        "cancelled": 400
    },
    "long_haul": {  # > 3500km
        "delay_3h": 300,  # 50% if offered rerouting arriving within 4h
        "delay_4h": 600,
        "cancelled": 600
    }
}

# Extraordinary circumstances (exempt from compensation)
EXTRAORDINARY_CIRCUMSTANCES = [
    "severe_weather",
    "air_traffic_control",
    "security_threat",
    "political_instability",
    "hidden_manufacturing_defect",
    "strike_not_airline"
]


@apex_action(ApexActionSchema(
    name="eu261_compensation",
    description="Calculate and process EU261 compensation for flight disruptions",
    category="compensation",
    industry="airlines",
    input_schema=ActionInputSchema(description="EU261 compensation parameters")
        .add_string("pnr", "Passenger Name Record", required=True)
        .add_string("flight_number", "Flight number", required=True)
        .add_string("origin", "Origin airport (IATA)", required=True)
        .add_string("destination", "Destination airport (IATA)", required=True)
        .add_string("disruption_type", "Type: cancelled, delayed, denied_boarding", required=True)
        .add_number("delay_minutes", "Actual delay at destination in minutes", required=False)
        .add_number("distance_km", "Flight distance in kilometers", required=True)
        .add_string("disruption_reason", "Reason for disruption", required=False)
        .add_boolean("eu_departure", "Whether flight departed from EU", required=True)
        .add_boolean("eu_carrier", "Whether carrier is EU-based", required=True),
    output_schema=ActionOutputSchema(description="EU261 compensation result")
        .add_boolean("eligible", "Whether passenger is eligible for compensation")
        .add_number("compensation_amount", "Compensation amount in EUR")
        .add_string("currency", "Currency (EUR)")
        .add_string("eligibility_reason", "Reason for eligibility determination")
        .add_array("assistance_entitled", "Assistance passenger is entitled to")
        .add_object("payment_details", "Payment processing details")
))
def eu261_compensation(
    pnr: str,
    flight_number: str,
    origin: str,
    destination: str,
    disruption_type: str,
    distance_km: float,
    eu_departure: bool,
    eu_carrier: bool,
    delay_minutes: int = None,
    disruption_reason: str = None
) -> dict:
    """
    Calculate EU261 compensation

    Args:
        pnr: Passenger Name Record
        flight_number: Flight number
        origin: Origin airport
        destination: Destination airport
        disruption_type: Type of disruption
        distance_km: Flight distance
        eu_departure: EU departure
        eu_carrier: EU carrier
        delay_minutes: Delay in minutes
        disruption_reason: Disruption reason

    Returns:
        EU261 compensation calculation
    """
    result = {
        "pnr": pnr,
        "flight_number": flight_number,
        "eligible": False,
        "compensation_amount": 0,
        "currency": "EUR",
        "eligibility_reason": "",
        "assistance_entitled": [],
        "payment_details": {},
        "calculation_date": datetime.now().isoformat()
    }

    # Check if EU261 applies
    if not eu_departure and not eu_carrier:
        result["eligibility_reason"] = "EU261 does not apply - not EU departure and not EU carrier"
        return result

    # Check for extraordinary circumstances
    if disruption_reason and disruption_reason.lower() in EXTRAORDINARY_CIRCUMSTANCES:
        result["eligibility_reason"] = f"Extraordinary circumstances: {disruption_reason}"
        result["assistance_entitled"] = _get_assistance_entitlements(delay_minutes)
        return result

    # Determine distance category
    if distance_km < 1500:
        distance_category = "short_haul"
    elif distance_km <= 3500:
        distance_category = "medium_haul"
    else:
        distance_category = "long_haul"

    compensation_rates = EU261_COMPENSATION[distance_category]

    # Calculate compensation based on disruption type
    if disruption_type == "cancelled":
        # Cancelled flight
        result["eligible"] = True
        result["compensation_amount"] = compensation_rates["cancelled"]
        result["eligibility_reason"] = "Flight cancelled - EU261 compensation applies"

    elif disruption_type == "delayed":
        delay_hours = (delay_minutes or 0) / 60

        if distance_category == "short_haul" and delay_hours >= 3:
            result["eligible"] = True
            result["compensation_amount"] = compensation_rates["delay_3h"]
            result["eligibility_reason"] = f"Short-haul delay >= 3 hours ({delay_hours:.1f}h)"

        elif distance_category == "medium_haul" and delay_hours >= 3:
            result["eligible"] = True
            result["compensation_amount"] = compensation_rates["delay_3h"]
            result["eligibility_reason"] = f"Medium-haul delay >= 3 hours ({delay_hours:.1f}h)"

        elif distance_category == "long_haul":
            if delay_hours >= 4:
                result["eligible"] = True
                result["compensation_amount"] = compensation_rates["delay_4h"]
                result["eligibility_reason"] = f"Long-haul delay >= 4 hours ({delay_hours:.1f}h)"
            elif delay_hours >= 3:
                result["eligible"] = True
                result["compensation_amount"] = compensation_rates["delay_3h"]
                result["eligibility_reason"] = f"Long-haul delay 3-4 hours ({delay_hours:.1f}h) - 50% rate"

        else:
            result["eligibility_reason"] = f"Delay of {delay_hours:.1f}h does not meet compensation threshold"

    elif disruption_type == "denied_boarding":
        result["eligible"] = True
        result["compensation_amount"] = compensation_rates["cancelled"]
        result["eligibility_reason"] = "Denied boarding - EU261 compensation applies"

    # Add assistance entitlements
    result["assistance_entitled"] = _get_assistance_entitlements(delay_minutes)

    # Add payment details if eligible
    if result["eligible"]:
        result["payment_details"] = {
            "claim_reference": f"EU261-{uuid.uuid4().hex[:8].upper()}",
            "payment_method": "bank_transfer_or_voucher",
            "processing_time": "7-14 business days",
            "voucher_option": {
                "amount": result["compensation_amount"] * 1.2,
                "validity_years": 2
            }
        }

    return result


def _get_assistance_entitlements(delay_minutes: int) -> List[str]:
    """Get assistance entitlements based on delay"""
    entitlements = []
    delay_hours = (delay_minutes or 0) / 60

    if delay_hours >= 2:
        entitlements.append("Meals and refreshments")
        entitlements.append("Two phone calls, emails or faxes")

    if delay_hours >= 4 or delay_minutes is None:  # Cancelled
        entitlements.append("Hotel accommodation if overnight required")
        entitlements.append("Transport between airport and hotel")

    return entitlements


class EU261CompensationAction(ApexActionBase):
    """EU261 Compensation Action (class-based)"""

    name = "eu261_compensation"
    description = "Calculate EU261 compensation"
    category = "compensation"
    industry = "airlines"

    def execute(self, **kwargs) -> dict:
        return eu261_compensation(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return eu261_compensation(**event)
