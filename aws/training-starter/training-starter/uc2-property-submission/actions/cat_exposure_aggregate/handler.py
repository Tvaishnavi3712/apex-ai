"""
Catastrophe Exposure Aggregation Action
Aggregate scheduled insured values by peril zone and test each aggregation
against remaining treaty capacity.

TRAINING USE CASE 2 — Insurance Underwriting.

Deploy location:  actions/insurance_underwriting/cat_exposure_aggregate/handler.py
Registry entry:   INDUSTRY_ACTIONS["insurance_underwriting"] += ["cat_exposure_aggregate"]
Resulting id:     insurance_underwriting.cat_exposure_aggregate

Why this is a separate action from appetite scoring: appetite is about whether
we want the risk. Capacity is about whether we are allowed to take it. An account
can be squarely in appetite and still be unwritable because the treaty in that
wind tier is full. Conflating the two produces declines that cite the wrong
reason, which is how brokers lose confidence in a carrier's underwriting.
"""

import os
import re
import sys
from decimal import Decimal
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import (  # noqa: E402
    apex_action,
    ApexActionSchema,
    ActionInputSchema,
    ActionOutputSchema,
    ApexActionBase,
)


DEFAULT_CAPACITY = {
    "tier_1_wind_max_usd": 40_000_000.0,
    "tier_2_wind_max_usd": 90_000_000.0,
    "flood_zone_ae_max_usd": 15_000_000.0,
    "flood_zone_v_max_usd": 0.0,
    "earthquake_zone_max_usd": 25_000_000.0,
    "single_zip_aggregate_max_usd": 30_000_000.0,
    "single_location_max_usd": 25_000_000.0,
}

# Tier 1 wind: first-tier coastal counties. Tier 2: second tier inland.
# A production deployment resolves these from a geocoding service; the static
# table keeps the training exercise runnable with no external dependency.
_TIER_1_WIND_STATES = {"FL", "LA", "TX", "MS", "AL", "SC", "NC", "GA", "HI"}
_TIER_2_WIND_STATES = {"VA", "MD", "DE", "NJ", "NY", "CT", "RI", "MA", "NH", "ME"}

# Coastal ZIP3 prefixes treated as tier 1 regardless of state.
_TIER_1_ZIP3 = {
    "770", "771", "772", "773", "774", "775",  # Houston / Galveston
    "780", "781", "782", "783", "784",          # Corpus Christi / South TX
    "700", "701", "703", "704", "705",          # New Orleans / South LA
    "330", "331", "332", "333", "334", "335",   # South FL
    "337", "338", "339", "341", "342",          # Tampa / SW FL
    "294", "295",                                # Charleston SC
    "284", "285",                                # Wilmington NC
    "395", "396",                                # Gulfport MS
}

# Earthquake zones by ZIP3 prefix — West Coast and New Madrid.
_EQ_ZIP3 = {
    "900", "901", "902", "903", "904", "905", "906", "907", "908",  # LA basin
    "910", "911", "912", "913", "914", "915", "916", "917", "918",
    "940", "941", "943", "944", "945", "946", "947", "948", "949",  # Bay Area
    "950", "951", "952", "953", "954", "955", "956", "957", "958",
    "970", "971", "972", "973",                                       # Portland
    "980", "981", "982", "983", "984", "985",                         # Seattle
    "380", "381", "382",                                              # New Madrid
}


@apex_action(ApexActionSchema(
    name="cat_exposure_aggregate",
    description=(
        "Aggregate scheduled insured values by wind tier, flood zone, "
        "earthquake zone and postal code, then test each aggregation against "
        "remaining treaty capacity and report every breach"
    ),
    category="underwriting",
    industry="insurance_underwriting",
    version="1.0",
    tags=["catastrophe", "aggregation", "treaty_capacity", "commercial_property"],
    input_schema=ActionInputSchema(description="Catastrophe aggregation inputs")
        .add_string("submission_id", "Broker submission reference", required=True)
        .add_array("locations", "Full location schedule from the statement of values", required=True)
        .add_object("cat_capacity", "Remaining treaty capacity overrides from the playbook context block", required=False)
        .add_object("existing_aggregates", "Capacity already consumed by in-force business, keyed by zone", required=False),
    output_schema=ActionOutputSchema(description="Catastrophe exposure summary")
        .add_number("total_insured_value", "Total insured value across the whole schedule")
        .add_array("zone_aggregations", "Aggregated exposure per peril zone with capacity headroom")
        .add_array("capacity_breaches", "Every aggregation that exceeds remaining capacity")
        .add_boolean("has_breach", "True when any capacity limit is exceeded")
        .add_number("max_foreseeable_loss", "Largest single-event loss across all modelled zones")
        .add_string("max_foreseeable_loss_zone", "Zone driving the maximum foreseeable loss")
        .add_array("uncoded_locations", "Locations excluded from aggregation for missing a postal code")
        .add_number("tier_1_wind_tiv", "Total insured value in tier 1 wind")
        .add_number("flood_v_tiv", "Total insured value in flood zone V or VE")
        .add_string("recommendation", "decline, refer_facultative, or proceed")
))
def cat_exposure_aggregate(
    submission_id: str,
    locations: List[Dict[str, Any]],
    cat_capacity: Optional[Dict[str, Any]] = None,
    existing_aggregates: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Aggregate catastrophe exposure and test it against capacity.

    Args:
        submission_id: Broker submission reference
        locations: Full location schedule
        cat_capacity: Remaining treaty capacity overrides
        existing_aggregates: Capacity already consumed by in-force business

    Returns:
        Zone aggregations, capacity breaches, max foreseeable loss and a
        recommendation
    """

    # ---------------------------------------------------------------------------
    # TODO — YOUR IMPLEMENTATION GOES HERE
    #
    # Specification below. The verification harness is the acceptance test:
    #     python3 training/scripts/verify_training_setup.py --from-actions-dir
    #
    # Do not change the function signature or the @apex_action schema above — the
    # harness calls this signature, and the schema is the contract other actions
    # and the playbook recipe rely on.
    # ---------------------------------------------------------------------------

    # Aggregate insured values by peril zone and test each against capacity.

    # CRITICAL DESIGN POINT — this is deliberately NOT part of appetite scoring.
    # Appetite asks whether we WANT the risk. Capacity asks whether we are ALLOWED
    # to take it. An account can be squarely in appetite and unwritable because
    # the treaty in that wind tier is full. Conflating them produces declines that
    # cite the wrong reason, and brokers lose confidence in the underwriting.

    # Walk the schedule once, accumulating: total TIV, tier-1 and tier-2 wind,
    #   flood AE, flood V, earthquake, and a per-postal-code total.
    #   Tier 1: ZIP3 in _TIER_1_ZIP3, or a tier-1 state within 25 miles of coast.
    #   Flood:  zone starting V -> flood_v, starting A -> flood_ae.
    #   Quake:  ZIP3 in _EQ_ZIP3.
    # A location with no postal code is INCLUDED in TIV, EXCLUDED from postal-code
    #   aggregation, and reported in uncoded_locations. Silently dropping it
    #   understates exposure.
    # Flag any single location above single_location_max_usd.
    # Test every aggregation against its limit, adding existing_aggregates already
    #   consumed by in-force business. Anything over is a capacity_breach with the
    #   specific zone and the excess amount named.
    # Surface a postal-code row only when it breaches or is at 50%+ of its limit.
    # max_foreseeable_loss is the largest single modelled peril exposure.
    # Recommendation: a peril/concentration breach -> decline. A single oversized
    #   location with no other breach -> refer_facultative, NOT decline.

    raise NotImplementedError("cat_exposure_aggregate: see the TODO above")


# ============================================================================
# Helpers
# ============================================================================

def _location_tiv(loc: Dict[str, Any]) -> float:
    """Printed location total when present, otherwise the sum of components."""
    stated = _f(loc.get("total_insured_value"))
    if stated > 0:
        return stated
    return (
        _f(loc.get("building_value"))
        + _f(loc.get("contents_value"))
        + _f(loc.get("business_income_value"))
        + _f(loc.get("equipment_value"))
    )


def _address_of(loc: Dict[str, Any]) -> str:
    parts = [
        loc.get("street_address"),
        loc.get("city"),
        loc.get("state"),
        loc.get("postal_code"),
    ]
    return ", ".join(str(p) for p in parts if p)


def _f(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace("$", "").replace(",", "").replace("%", "").strip())
    except (TypeError, ValueError):
        return 0.0


# ============================================================================
# Class-based implementation
# ============================================================================

class CatExposureAggregateAction(ApexActionBase):
    """Catastrophe Exposure Aggregation Action (class-based)."""

    name = "cat_exposure_aggregate"
    description = "Aggregate insured values by peril zone and test against capacity"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return cat_exposure_aggregate(**kwargs)


def handler(event, context):
    """Lambda entry point."""
    return cat_exposure_aggregate(**event)
