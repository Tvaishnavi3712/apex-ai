"""
Appetite Score Action
Score a commercial property submission against the written appetite guide and
return the specific rules that fired.

TRAINING USE CASE 2 — Insurance Underwriting.

Deploy location:  actions/insurance_underwriting/appetite_score/handler.py
Registry entry:   INDUSTRY_ACTIONS["insurance_underwriting"] += ["appetite_score"]
Resulting id:     insurance_underwriting.appetite_score

Design note: this action separates DISQUALIFIERS from CONCERNS. A disqualifier
is a hard rule from the appetite guide and ends the submission. A concern is
judgement the underwriter should see but must not be auto-declined on. Collapsing
the two is the classic failure — you either auto-decline good accounts or you
push every marginal account to a human and save nobody any time.
"""

import os
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


DEFAULT_APPETITE = {
    "target_occupancies": [
        "warehouse_distribution", "light_manufacturing", "office",
        "strip_retail", "self_storage",
    ],
    "restricted_occupancies": [
        "cold_storage", "woodworking", "plastics_manufacturing",
        "recycling", "hospitality",
    ],
    "prohibited_occupancies": [
        "fireworks_manufacturing", "explosives", "refining",
        "waste_to_energy", "tire_storage",
    ],
    "tiv_min_usd": 2_000_000.0,
    "tiv_max_usd": 75_000_000.0,
    "min_year_built": 1955,
    "max_roof_age_years": 20,
    "min_protection_class": 6,
    "required_loss_run_years": 3,
    "max_three_year_loss_ratio": 0.60,
    "max_frame_construction_percent": 25.0,
}

# Free-text occupancy descriptions mapped onto appetite classes. Brokers write
# "cold storage warehouse", not "cold_storage".
_OCCUPANCY_KEYWORDS = {
    "tire_storage":            ["tire storage", "tire warehouse", "tire recycling"],
    "fireworks_manufacturing": ["fireworks", "pyrotechnic"],
    "explosives":              ["explosive", "ammunition", "ordnance"],
    "refining":                ["refinery", "refining", "petrochemical"],
    "waste_to_energy":         ["waste to energy", "waste-to-energy", "incinerat"],
    "cold_storage":            ["cold storage", "refrigerated warehouse", "freezer warehouse", "blast freez"],
    "woodworking":             ["woodworking", "cabinet", "sawmill", "lumber mill", "furniture manufactur"],
    "plastics_manufacturing":  ["plastic", "injection mold", "polymer"],
    "recycling":               ["recycling", "scrap", "salvage", "materials recovery"],
    "hospitality":             ["hotel", "motel", "restaurant", "banquet", "resort"],
    "warehouse_distribution":  ["warehouse", "distribution", "fulfillment", "logistics", "storage facility"],
    "light_manufacturing":     ["light manufactur", "assembly", "fabrication", "machine shop"],
    "office":                  ["office", "professional building", "medical office"],
    "strip_retail":            ["strip retail", "strip mall", "retail center", "shopping center", "retail strip"],
    "self_storage":            ["self storage", "self-storage", "mini storage"],
}

# ISO construction classes ordered worst to best.
_CONSTRUCTION_SCORE = {
    "frame": -20,
    "joisted masonry": -8,
    "non-combustible": 4,
    "noncombustible": 4,
    "masonry non-combustible": 10,
    "modified fire resistive": 14,
    "fire resistive": 18,
}


@apex_action(ApexActionSchema(
    name="appetite_score",
    description=(
        "Score a commercial property submission against the written appetite "
        "guide and return hard disqualifiers separately from underwriting "
        "concerns, with the specific rule and location behind each"
    ),
    category="underwriting",
    industry="insurance_underwriting",
    version="1.0",
    tags=["appetite", "commercial_property", "triage", "underwriting_guide"],
    input_schema=ActionInputSchema(description="Appetite scoring inputs")
        .add_string("submission_id", "Broker submission reference", required=True)
        .add_array("locations", "Full location schedule from the statement of values", required=True)
        .add_string("primary_occupancy", "Dominant occupancy across the schedule", required=False)
        .add_array("prior_losses", "Prior claims from the loss runs", required=False)
        .add_number("loss_run_years_provided", "Years of loss experience supplied", required=False)
        .add_number("expiring_premium", "Expiring annual premium, used for the loss ratio", required=False)
        .add_number("years_in_business", "Years the insured has operated", required=False)
        .add_boolean("has_prior_declination", "True when a prior declination is disclosed", required=False)
        .add_object("appetite_guide", "Appetite guide overrides from the playbook context block", required=False),
    output_schema=ActionOutputSchema(description="Appetite assessment")
        .add_number("appetite_score", "Composite score from 0 to 100, higher is better")
        .add_string("appetite_band", "target, acceptable, marginal, or out_of_appetite")
        .add_array("disqualifiers", "Hard appetite-guide breaches. Any entry means decline")
        .add_array("concerns", "Judgement items the underwriter should see but must not auto-decline on")
        .add_array("positives", "Factors improving the account")
        .add_number("total_insured_value", "Computed total insured value across the schedule")
        .add_number("frame_construction_percent", "Share of total insured value in frame construction")
        .add_number("three_year_loss_ratio", "Incurred losses divided by expiring premium over the period")
        .add_string("mapped_primary_occupancy", "Appetite class the free-text occupancy mapped to")
        .add_string("recommendation", "decline, refer_to_broker, or route_to_underwriter")
))
def appetite_score(
    submission_id: str,
    locations: List[Dict[str, Any]],
    primary_occupancy: Optional[str] = None,
    prior_losses: Optional[List[Dict[str, Any]]] = None,
    loss_run_years_provided: Optional[float] = None,
    expiring_premium: Optional[float] = None,
    years_in_business: Optional[float] = None,
    has_prior_declination: bool = False,
    appetite_guide: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Score a submission against the appetite guide.

    Args:
        submission_id: Broker submission reference
        locations: Full location schedule
        primary_occupancy: Dominant occupancy across the schedule
        prior_losses: Prior claims from the loss runs
        loss_run_years_provided: Years of loss experience supplied
        expiring_premium: Expiring annual premium
        years_in_business: Years the insured has operated
        has_prior_declination: True when a prior declination is disclosed
        appetite_guide: Appetite guide overrides

    Returns:
        Appetite score, band, disqualifiers, concerns and a recommendation
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

    # Score the submission against the appetite guide. Start at 60 and adjust.

    # CRITICAL DESIGN POINT — keep disqualifiers and concerns strictly separate:
    #   disqualifiers  hard appetite-guide breaches. Any entry means decline.
    #   concerns       judgement the underwriter must SEE but must never be
    #                  auto-declined on.
    # Collapsing the two means you either auto-decline good accounts or push every
    # marginal account to a human and save nobody any time.

    # Roll up the schedule: total insured value via _location_tiv(), and the share
    #   of TIV in frame construction.
    # Occupancy: map each location with _map_occupancy().
    #   prohibited -> disqualifier. restricted -> concern. target -> positive.
    # TIV: below the minimum is a disqualifier. ABOVE the maximum is NOT — it is a
    #   facultative-reinsurance concern. Think about why.
    # Construction: frame above max_frame_construction_percent is a disqualifier.
    # Per location, raise concerns for: built before min_year_built, roof older
    #   than max_roof_age_years, unsprinklered, protection class worse than the
    #   minimum. Score construction quality from _CONSTRUCTION_SCORE.
    # Loss experience — the subtle one:
    #   Only judge the loss ratio when years_supplied >= required_loss_run_years.
    #   Computing a three-year ratio from one year of data manufactures a
    #   disqualifier out of a completeness gap. Raise a referral concern instead.
    #   When it IS judgeable and above the threshold: if 70%+ of incurred is
    #   catastrophe-coded, that is a concern (one hurricane does not describe an
    #   account); otherwise it is an ADVERSE_LOSS_HISTORY disqualifier.
    # Flag open claims carrying material reserves.
    # Account: under 3 years in business is a concern, 10+ is a positive, a
    #   disclosed prior declination is a concern.
    # Band: any disqualifier -> out_of_appetite (cap the score at 15).
    #   An insufficient-loss-history concern -> marginal + refer_to_broker.
    #   Otherwise >=75 target, >=55 acceptable, else marginal.

    raise NotImplementedError("appetite_score: see the TODO above")


# ============================================================================
# Helpers
# ============================================================================

def _finding(
    code: str,
    detail: str,
    locations: Optional[List[str]] = None,
    rule: Optional[str] = None,
    severity: str = "hard",
) -> Dict[str, Any]:
    """Uniform finding record so the broker response can quote it directly."""
    return {
        "code": code,
        "detail": detail,
        "locations": locations or [],
        "rule": rule,
        "severity": severity,
    }


def _map_occupancy(text: str) -> str:
    """
    Map a free-text occupancy description onto an appetite class.
    Prohibited and restricted classes are tested first so a description like
    "tire storage warehouse" maps to tire_storage, not warehouse_distribution.
    """
    if not text:
        return ""
    lowered = str(text).lower()

    ordered = (
        DEFAULT_APPETITE["prohibited_occupancies"]
        + DEFAULT_APPETITE["restricted_occupancies"]
        + DEFAULT_APPETITE["target_occupancies"]
    )
    for occ_class in ordered:
        for keyword in _OCCUPANCY_KEYWORDS.get(occ_class, []):
            if keyword in lowered:
                return occ_class
    return ""


def _construction_class(value: Any) -> str:
    """Normalise an ISO construction description to a comparable key."""
    if not value:
        return ""
    s = str(value).strip().lower().replace("_", " ")
    if "fire resistive" in s:
        return "modified fire resistive" if "modified" in s else "fire resistive"
    if "masonry non" in s or "mnc" in s:
        return "masonry non-combustible"
    if "joisted" in s or "jm" in s:
        return "joisted masonry"
    if "non-combustible" in s or "noncombustible" in s:
        return "non-combustible"
    if "frame" in s:
        return "frame"
    return s


def _protection_class(value: Any) -> Optional[int]:
    """Pull the numeric grade out of 'PPC 3', 'Class 4', or '3'."""
    if value is None or value == "":
        return None
    import re as _re
    match = _re.search(r"(\d+)", str(value))
    return int(match.group(1)) if match else None


def _location_tiv(loc: Dict[str, Any]) -> float:
    """
    Use the printed location total when present, otherwise sum the components.
    Trusting the printed figure matters — a schedule that prints a total the
    components do not sum to is a data-quality signal, not a maths error to fix.
    """
    stated = _f(loc.get("total_insured_value"))
    if stated > 0:
        return stated
    return (
        _f(loc.get("building_value"))
        + _f(loc.get("contents_value"))
        + _f(loc.get("business_income_value"))
        + _f(loc.get("equipment_value"))
    )


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ("true", "yes", "y", "1")


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


def _i(value: Any) -> Optional[int]:
    f = _f(value)
    return int(f) if f else None


# ============================================================================
# Class-based implementation
# ============================================================================

class AppetiteScoreAction(ApexActionBase):
    """Appetite Score Action (class-based)."""

    name = "appetite_score"
    description = "Score a submission against the written appetite guide"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return appetite_score(**kwargs)


def handler(event, context):
    """Lambda entry point."""
    return appetite_score(**event)
