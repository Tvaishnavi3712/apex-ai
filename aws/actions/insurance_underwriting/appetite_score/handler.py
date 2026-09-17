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

    guide = dict(DEFAULT_APPETITE)
    for key, value in (appetite_guide or {}).items():
        if key in guide and value is not None:
            guide[key] = value

    locations = locations or []
    prior_losses = prior_losses or []
    disqualifiers: List[Dict[str, Any]] = []
    concerns: List[Dict[str, Any]] = []
    positives: List[Dict[str, Any]] = []
    score = 60.0

    # -- Schedule roll-up ------------------------------------------------------
    tiv = 0.0
    frame_tiv = 0.0
    weighted_construction = 0.0
    for loc in locations:
        loc_tiv = _location_tiv(loc)
        tiv += loc_tiv
        cls = _construction_class(loc.get("construction_type") or loc.get("construction_class"))
        if cls == "frame":
            frame_tiv += loc_tiv
        weighted_construction += _CONSTRUCTION_SCORE.get(cls, 0) * loc_tiv
    frame_pct = (frame_tiv / tiv * 100.0) if tiv > 0 else 0.0
    construction_adj = (weighted_construction / tiv) if tiv > 0 else 0.0
    score += construction_adj

    # -- Occupancy: prohibited -> disqualifier, restricted -> concern, target -> positive
    mapped_primary = _map_occupancy(primary_occupancy or "")
    occ_by_class: Dict[str, List[str]] = {}
    for loc in locations:
        cls = _map_occupancy(loc.get("occupancy_description") or loc.get("occupancy") or "") or mapped_primary
        if cls:
            occ_by_class.setdefault(cls, []).append(str(loc.get("location_number") or "?"))
    if not occ_by_class and mapped_primary:
        occ_by_class[mapped_primary] = ["all"]
    for cls, locs in occ_by_class.items():
        if cls in guide["prohibited_occupancies"]:
            disqualifiers.append(_finding("PROHIBITED_OCCUPANCY",
                f"Prohibited occupancy '{cls}' at location(s) {', '.join(locs)}",
                locs, "appetite_guide.prohibited_occupancies", "hard"))
        elif cls in guide["restricted_occupancies"]:
            concerns.append(_finding("RESTRICTED_OCCUPANCY",
                f"Restricted occupancy '{cls}' at location(s) {', '.join(locs)} — underwriter judgement required",
                locs, "appetite_guide.restricted_occupancies", "soft"))
            score -= 6.0
        elif cls in guide["target_occupancies"]:
            positives.append(_finding("TARGET_OCCUPANCY",
                f"Target occupancy '{cls}' at location(s) {', '.join(locs)}",
                locs, "appetite_guide.target_occupancies", "info"))
            score += 10.0
    if not occ_by_class:
        concerns.append(_finding("UNMAPPED_OCCUPANCY",
            f"Occupancy '{primary_occupancy}' did not map to an appetite class — treated as marginal",
            [], "appetite_guide", "soft"))
        score -= 5.0

    # -- TIV: below minimum is a disqualifier; above maximum is a fac concern --
    if tiv < _f(guide["tiv_min_usd"]):
        disqualifiers.append(_finding("TIV_BELOW_MINIMUM",
            f"Total insured value ${tiv:,.0f} is below the programme minimum ${_f(guide['tiv_min_usd']):,.0f}",
            [], "appetite_guide.tiv_min_usd", "hard"))
    elif tiv > _f(guide["tiv_max_usd"]):
        concerns.append(_finding("TIV_EXCEEDS_SINGLE_RISK_AUTHORITY",
            f"Total insured value ${tiv:,.0f} exceeds single-risk authority ${_f(guide['tiv_max_usd']):,.0f} — facultative reinsurance review, not a decline",
            [], "appetite_guide.tiv_max_usd", "soft"))
        score -= 5.0

    # -- Construction: frame share ---------------------------------------------
    if frame_pct > _f(guide["max_frame_construction_percent"]):
        disqualifiers.append(_finding("FRAME_CONSTRUCTION_EXCEEDED",
            f"Frame construction is {frame_pct:.1f}% of TIV, above the {_f(guide['max_frame_construction_percent']):.0f}% maximum",
            [], "appetite_guide.max_frame_construction_percent", "hard"))

    # -- Per-location protection concerns (one finding per rule, all locations listed)
    this_year = datetime.utcnow().year
    old_build, old_roof, unsprinklered, poor_ppc = [], [], [], []
    for loc in locations:
        ln = str(loc.get("location_number") or "?")
        yb = _i(loc.get("year_built"))
        if yb and yb < int(_f(guide["min_year_built"])):
            old_build.append(ln)
        roof = _i(loc.get("roof_year_updated")) or yb
        if roof and (this_year - roof) > int(_f(guide["max_roof_age_years"])):
            old_roof.append(ln)
        if not _truthy(loc.get("sprinklered")):
            unsprinklered.append(ln)
        ppc = _protection_class(loc.get("protection_class"))
        if ppc is not None and ppc > int(_f(guide["min_protection_class"])):
            poor_ppc.append(ln)
    if old_build:
        concerns.append(_finding("YEAR_BUILT", f"Built before {guide['min_year_built']} at location(s) {', '.join(old_build)}", old_build, "appetite_guide.min_year_built", "soft")); score -= 4.0
    if old_roof:
        concerns.append(_finding("ROOF_AGE", f"Roof older than {guide['max_roof_age_years']} years at location(s) {', '.join(old_roof)}", old_roof, "appetite_guide.max_roof_age_years", "soft")); score -= 4.0
    if unsprinklered:
        concerns.append(_finding("UNSPRINKLERED", f"No automatic sprinklers at location(s) {', '.join(unsprinklered)}", unsprinklered, "protection", "soft")); score -= 6.0
    elif locations:
        positives.append(_finding("FULLY_SPRINKLERED", "Every scheduled location is sprinklered", [], "protection", "info")); score += 5.0
    if poor_ppc:
        concerns.append(_finding("PROTECTION_CLASS", f"Protection class worse than {guide['min_protection_class']} at location(s) {', '.join(poor_ppc)}", poor_ppc, "appetite_guide.min_protection_class", "soft")); score -= 4.0

    # -- Loss experience -------------------------------------------------------
    total_incurred = sum(_f(l.get("incurred_amount") or (_f(l.get("paid_amount")) + _f(l.get("reserve_amount")))) for l in prior_losses)
    cat_incurred = sum(_f(l.get("incurred_amount") or (_f(l.get("paid_amount")) + _f(l.get("reserve_amount")))) for l in prior_losses if _truthy(l.get("is_catastrophe")))
    years_supplied = _f(loss_run_years_provided)
    required_years = _f(guide["required_loss_run_years"])
    premium = _f(expiring_premium)
    loss_ratio = 0.0
    insufficient_history = False

    if years_supplied < required_years:
        insufficient_history = True
        missing = int(required_years - years_supplied)
        concerns.append(_finding("INSUFFICIENT_LOSS_HISTORY",
            f"Only {int(years_supplied)} of {int(required_years)} required loss-run years supplied — refer to broker for the missing {missing} year(s); do not decline on completeness",
            [], "appetite_guide.required_loss_run_years", "soft"))
    elif premium > 0:
        loss_ratio = total_incurred / (premium * required_years)
        if loss_ratio > _f(guide["max_three_year_loss_ratio"]):
            cat_share = (cat_incurred / total_incurred) if total_incurred > 0 else 0.0
            if cat_share >= 0.70:
                concerns.append(_finding("CAT_DRIVEN_LOSS_RATIO",
                    f"Three-year loss ratio {loss_ratio:.0%} exceeds {_f(guide['max_three_year_loss_ratio']):.0%} but {cat_share:.0%} of incurred is catastrophe-coded — one event does not describe the account",
                    [], "appetite_guide.max_three_year_loss_ratio", "soft"))
                score -= 5.0
            else:
                disqualifiers.append(_finding("ADVERSE_LOSS_HISTORY",
                    f"Three-year loss ratio {loss_ratio:.0%} exceeds {_f(guide['max_three_year_loss_ratio']):.0%} across separate non-catastrophe events",
                    [], "appetite_guide.max_three_year_loss_ratio", "hard"))
        elif loss_ratio <= 0.20:
            positives.append(_finding("CLEAN_LOSS_HISTORY", f"Three-year loss ratio {loss_ratio:.1%}", [], "loss_analysis", "info")); score += 10.0
        elif loss_ratio <= 0.40:
            score += 4.0

    open_reserves = [l for l in prior_losses if str(l.get("claim_status", "")).lower() == "open" and _f(l.get("reserve_amount")) >= 10_000]
    if open_reserves:
        ids = [str(l.get("claim_number") or "?") for l in open_reserves]
        concerns.append(_finding("OPEN_RESERVE",
            f"Open claim(s) {', '.join(ids)} carry material reserves totalling ${sum(_f(l.get('reserve_amount')) for l in open_reserves):,.0f} — may develop",
            [], "loss_analysis", "soft"))
        score -= 3.0

    # -- Account -----------------------------------------------------------------
    yib = _f(years_in_business)
    if yib and yib < 3:
        concerns.append(_finding("NEW_VENTURE", f"Only {yib:.0f} year(s) in business", [], "account", "soft")); score -= 5.0
    elif yib >= 10:
        positives.append(_finding("ESTABLISHED_ACCOUNT", f"{yib:.0f} years in business", [], "account", "info")); score += 5.0
    if _truthy(has_prior_declination):
        concerns.append(_finding("PRIOR_DECLINATION", "Prior declination or non-renewal disclosed — written explanation required before quoting", [], "account", "soft")); score -= 5.0

    # -- Band ----------------------------------------------------------------------
    score = max(0.0, min(100.0, score))
    if disqualifiers:
        band, recommendation = "out_of_appetite", "decline"
        score = min(score, 15.0)
    elif insufficient_history:
        band, recommendation = "marginal", "refer_to_broker"
    elif score >= 75:
        band, recommendation = "target", "route_to_underwriter"
    elif score >= 55:
        band, recommendation = "acceptable", "route_to_underwriter"
    else:
        band, recommendation = "marginal", "route_to_underwriter"

    return {
        "submission_id": submission_id,
        "appetite_score": round(score, 1),
        "appetite_band": band,
        "disqualifiers": disqualifiers,
        "concerns": concerns,
        "positives": positives,
        "total_insured_value": round(tiv, 2),
        "frame_construction_percent": round(frame_pct, 2),
        "three_year_loss_ratio": round(loss_ratio, 4),
        "loss_run_years_provided": years_supplied,
        "total_incurred": round(total_incurred, 2),
        "catastrophe_incurred": round(cat_incurred, 2),
        "mapped_primary_occupancy": mapped_primary or "",
        "recommendation": recommendation,
        "evaluated_at": datetime.utcnow().isoformat(),
    }


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