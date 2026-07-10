"""
Hotel Booking Action
Book hotel accommodations for stranded passengers
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="hotel_booking",
    description="Book hotel accommodations for stranded passengers",
    category="passenger_services",
    industry="airlines",
    input_schema=ActionInputSchema(description="Hotel booking parameters")
        .add_string("pnr", "Passenger Name Record", required=True)
        .add_string("passenger_name", "Passenger name", required=True)
        .add_string("airport_code", "Airport code for hotel search", required=True)
        .add_string("checkin_date", "Check-in date (YYYY-MM-DD)", required=True)
        .add_string("checkout_date", "Check-out date (YYYY-MM-DD)", required=True)
        .add_string("passenger_tier", "Passenger loyalty tier", required=False)
        .add_number("party_size", "Number of guests", required=False)
        .add_boolean("include_meals", "Include meal vouchers", required=False),
    output_schema=ActionOutputSchema(description="Hotel booking result")
        .add_boolean("booked", "Whether hotel was booked")
        .add_string("hotel_name", "Hotel name")
        .add_string("confirmation_number", "Hotel confirmation number")
        .add_string("address", "Hotel address")
        .add_string("phone", "Hotel phone number")
        .add_object("room_details", "Room details")
        .add_object("transportation", "Transportation arrangements")
        .add_object("meal_vouchers", "Meal voucher details if included")
))
def hotel_booking(
    pnr: str,
    passenger_name: str,
    airport_code: str,
    checkin_date: str,
    checkout_date: str,
    passenger_tier: str = "general",
    party_size: int = 1,
    include_meals: bool = True
) -> dict:
    """
    Book hotel for stranded passenger

    Args:
        pnr: Passenger Name Record
        passenger_name: Passenger name
        airport_code: Airport code
        checkin_date: Check-in date
        checkout_date: Check-out date
        passenger_tier: Loyalty tier
        party_size: Party size
        include_meals: Include meals

    Returns:
        Hotel booking result
    """
    confirmation = f"HTL{uuid.uuid4().hex[:8].upper()}"

    result = {
        "pnr": pnr,
        "passenger_name": passenger_name,
        "booked": False,
        "hotel_name": None,
        "confirmation_number": None,
        "address": None,
        "phone": None,
        "room_details": {},
        "transportation": {},
        "meal_vouchers": {},
        "booking_date": datetime.now().isoformat()
    }

    # Get hotel preferences based on tier
    hotel_tier = _get_hotel_tier(passenger_tier)

    # Search and book hotel
    hotels = _search_hotels(airport_code, checkin_date, checkout_date, hotel_tier)

    if hotels:
        selected_hotel = hotels[0]

        booking_result = _book_hotel(selected_hotel, passenger_name, party_size, checkin_date, checkout_date)

        if booking_result.get("success"):
            result["booked"] = True
            result["hotel_name"] = selected_hotel["name"]
            result["confirmation_number"] = booking_result["confirmation"]
            result["address"] = selected_hotel["address"]
            result["phone"] = selected_hotel["phone"]
            result["room_details"] = {
                "room_type": _get_room_type(passenger_tier, party_size),
                "beds": "1 King" if party_size <= 2 else "2 Queen",
                "amenities": selected_hotel.get("amenities", []),
                "wifi_included": True
            }

            # Arrange transportation
            result["transportation"] = {
                "type": "shuttle",
                "pickup_location": f"{airport_code} Terminal",
                "schedule": "Every 30 minutes",
                "hotel_shuttle_phone": selected_hotel.get("shuttle_phone")
            }

            # Add meal vouchers if requested
            if include_meals:
                meal_amount = 50 if passenger_tier in ["diamond", "platinum"] else 30
                result["meal_vouchers"] = {
                    "amount_per_person": meal_amount,
                    "total_amount": meal_amount * party_size,
                    "valid_at": "Hotel restaurant and room service",
                    "voucher_code": f"MEAL{uuid.uuid4().hex[:6].upper()}"
                }

            return result

    # Return mock booking for testing
    return {
        "pnr": pnr,
        "passenger_name": passenger_name,
        "booked": True,
        "hotel_name": "Airport Marriott",
        "confirmation_number": confirmation,
        "address": f"123 Airport Blvd, {airport_code}",
        "phone": "555-123-4567",
        "room_details": {
            "room_type": "Deluxe King" if passenger_tier in ["diamond", "platinum", "gold"] else "Standard",
            "beds": "1 King" if party_size <= 2 else "2 Queen",
            "floor": "Executive Floor" if passenger_tier in ["diamond", "platinum"] else "Standard",
            "amenities": ["WiFi", "Breakfast", "Gym Access"],
            "wifi_included": True
        },
        "transportation": {
            "type": "complimentary_shuttle",
            "pickup_location": f"{airport_code} Terminal - Ground Transportation",
            "schedule": "Runs every 20 minutes",
            "first_pickup": "05:00",
            "last_pickup": "23:00"
        },
        "meal_vouchers": {
            "amount_per_person": 50 if passenger_tier in ["diamond", "platinum"] else 30,
            "total_amount": (50 if passenger_tier in ["diamond", "platinum"] else 30) * party_size,
            "valid_at": "Hotel restaurant, room service, and airport food court",
            "voucher_code": f"MEAL{uuid.uuid4().hex[:6].upper()}",
            "expiration": checkout_date
        } if include_meals else None,
        "checkin_time": "15:00",
        "checkout_time": "12:00",
        "booking_date": datetime.now().isoformat()
    }


def _get_hotel_tier(passenger_tier: str) -> str:
    """Map passenger tier to hotel tier"""
    tier_mapping = {
        "diamond": "luxury",
        "platinum": "premium",
        "gold": "premium",
        "silver": "standard",
        "general": "standard"
    }
    return tier_mapping.get(passenger_tier, "standard")


def _get_room_type(passenger_tier: str, party_size: int) -> str:
    """Get room type based on tier and party size"""
    if passenger_tier in ["diamond", "platinum"]:
        return "Suite" if party_size > 2 else "Executive King"
    elif passenger_tier == "gold":
        return "Deluxe King" if party_size <= 2 else "Family Room"
    else:
        return "Standard King" if party_size <= 2 else "Standard Double"


def _search_hotels(airport: str, checkin: str, checkout: str, tier: str) -> List[dict]:
    """Search for available hotels"""
    # Would integrate with hotel booking system
    return [
        {
            "name": "Airport Marriott",
            "tier": tier,
            "address": f"123 Airport Blvd, {airport}",
            "phone": "555-123-4567",
            "amenities": ["WiFi", "Breakfast", "Gym", "Pool"],
            "shuttle_phone": "555-123-4568"
        }
    ]


def _book_hotel(hotel: dict, name: str, party: int, checkin: str, checkout: str) -> dict:
    """Book hotel room"""
    return {
        "success": True,
        "confirmation": f"HTL{uuid.uuid4().hex[:8].upper()}"
    }


class HotelBookingAction(ApexActionBase):
    """Hotel Booking Action (class-based)"""

    name = "hotel_booking"
    description = "Book hotel for stranded passengers"
    category = "passenger_services"
    industry = "airlines"

    def execute(self, **kwargs) -> dict:
        return hotel_booking(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return hotel_booking(**event)
