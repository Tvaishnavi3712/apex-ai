"""
Compensation Validation Action
Validate compensation against salary bands, equity guidelines, and budget
"""

import boto3
try:  # AZURE BUILD: Cosmos DB resource -> Cosmos DB shim
    from sdk.azure_data import get_table_resource
except ImportError:
    from ...sdk.azure_data import get_table_resource

try:  # AZURE BUILD: native key-condition builder
    from sdk.azure_data import Key
except ImportError:
    from ...sdk.azure_data import Key
import os
from decimal import Decimal
from typing import Dict, Any, Optional, List

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# ============================================================================
# Decorator-based implementation
# ============================================================================

@apex_action(ApexActionSchema(
    name="compensation_validation",
    description="Validate compensation package against salary bands, equity guidelines, and budget",
    category="compensation",
    industry="hr",
    input_schema=ActionInputSchema(description="Compensation validation parameters")
        .add_string("job_level", "Job level/grade (e.g., L5, Senior, Director)", required=True)
        .add_string("location", "Work location for geo-differential", required=True)
        .add_number("base_salary", "Proposed base salary", required=True)
        .add_number("signing_bonus", "Signing bonus amount", required=False)
        .add_number("target_bonus_percent", "Target bonus percentage", required=False)
        .add_string("equity_grant", "Equity grant value or shares", required=False)
        .add_string("job_id", "Job requisition ID for budget check", required=False)
        .add_string("currency", "Currency code (default USD)", required=False),
    output_schema=ActionOutputSchema(description="Compensation validation result")
        .add_boolean("within_band", "Whether salary is within approved band")
        .add_string("band_position", "Position in band: below, min, lower, mid, upper, max, above")
        .add_number("band_percentile", "Percentile within band (0-100)")
        .add_object("band_details", "Salary band min, mid, max")
        .add_array("exceptions_required", "List of exceptions needed")
        .add_array("approvals_required", "Additional approvals needed")
        .add_boolean("within_budget", "Whether within job requisition budget")
))
def compensation_validation(
    job_level: str,
    location: str,
    base_salary: float,
    signing_bonus: float = 0,
    target_bonus_percent: float = 0,
    equity_grant: str = None,
    job_id: str = None,
    currency: str = "USD"
) -> dict:
    """
    Validate compensation against bands and guidelines

    Args:
        job_level: Job level/grade
        location: Work location
        base_salary: Proposed base salary
        signing_bonus: One-time signing bonus
        target_bonus_percent: Annual target bonus %
        equity_grant: Equity grant details
        job_id: Job requisition ID
        currency: Currency code

    Returns:
        Validation result with band analysis and required approvals
    """
    result = {
        "job_level": job_level,
        "location": location,
        "base_salary": base_salary,
        "currency": currency,
        "within_band": False,
        "band_position": "unknown",
        "band_percentile": 0,
        "band_details": {},
        "exceptions_required": [],
        "approvals_required": [],
        "within_budget": True,
        "total_compensation": 0,
        "compensation_breakdown": {},
        "warnings": []
    }

    try:
        # Get salary band for job level and location
        band = _get_salary_band(job_level, location, currency)
        if not band:
            return {**result, "error": f"No salary band found for {job_level} in {location}"}

        result["band_details"] = {
            "minimum": band["min"],
            "midpoint": band["mid"],
            "maximum": band["max"],
            "currency": currency
        }

        # Analyze base salary position
        band_analysis = _analyze_band_position(base_salary, band)
        result.update(band_analysis)

        # Calculate total compensation
        total_comp = _calculate_total_compensation(
            base_salary, signing_bonus, target_bonus_percent, equity_grant
        )
        result["total_compensation"] = total_comp["total"]
        result["compensation_breakdown"] = total_comp

        # Check for required exceptions
        exceptions = _check_exceptions(
            base_salary, band, signing_bonus, equity_grant
        )
        result["exceptions_required"] = exceptions

        # Determine required approvals
        approvals = _determine_approvals(
            base_salary, band, signing_bonus, equity_grant, exceptions
        )
        result["approvals_required"] = approvals

        # Check budget if job_id provided
        if job_id:
            budget_check = _check_budget(job_id, total_comp["total"])
            result["within_budget"] = budget_check["within_budget"]
            if not budget_check["within_budget"]:
                result["warnings"].append(
                    f"Total compensation exceeds job budget by ${budget_check.get('overage', 0):,.2f}"
                )
                result["approvals_required"].append("finance_approval")

        # Add warnings for edge cases
        if band_analysis["band_percentile"] > 90:
            result["warnings"].append(
                "Salary is in top 10% of band - limited future growth potential"
            )

        return result

    except Exception as e:
        return {**result, "error": str(e)}


def _get_salary_band(
    job_level: str,
    location: str,
    currency: str
) -> Optional[Dict[str, float]]:
    """Retrieve salary band from database"""
    try:
        tables = get_table_resource()
        table_name = os.environ.get('SALARY_BANDS_TABLE', 'apex-ai-platform-salary-bands')
        table = cosmos_db.Table(table_name)

        # Try location-specific band first
        response = table.get_item(
            Key={
                "job_level": job_level,
                "location": location
            }
        )
        if 'Item' in response:
            item = response['Item']
            return {
                "min": float(item.get('band_min', 0)),
                "mid": float(item.get('band_mid', 0)),
                "max": float(item.get('band_max', 0))
            }

        # Fall back to default location
        response = table.get_item(
            Key={
                "job_level": job_level,
                "location": "default"
            }
        )
        if 'Item' in response:
            item = response['Item']
            geo_factor = _get_geo_factor(location)
            return {
                "min": float(item.get('band_min', 0)) * geo_factor,
                "mid": float(item.get('band_mid', 0)) * geo_factor,
                "max": float(item.get('band_max', 0)) * geo_factor
            }
    except Exception:
        pass

    # Return mock bands for testing
    mock_bands = {
        "L3": {"min": 80000, "mid": 100000, "max": 120000},
        "L4": {"min": 100000, "mid": 125000, "max": 150000},
        "L5": {"min": 130000, "mid": 160000, "max": 190000},
        "L6": {"min": 170000, "mid": 210000, "max": 250000},
        "L7": {"min": 220000, "mid": 275000, "max": 330000},
        "senior": {"min": 130000, "mid": 160000, "max": 190000},
        "staff": {"min": 170000, "mid": 210000, "max": 250000},
        "director": {"min": 200000, "mid": 250000, "max": 300000},
    }

    level_key = job_level.lower()
    if level_key in mock_bands:
        geo_factor = _get_geo_factor(location)
        band = mock_bands[level_key]
        return {
            "min": band["min"] * geo_factor,
            "mid": band["mid"] * geo_factor,
            "max": band["max"] * geo_factor
        }

    return None


def _get_geo_factor(location: str) -> float:
    """Get geographic cost-of-living factor"""
    geo_factors = {
        "san francisco": 1.15,
        "new york": 1.12,
        "seattle": 1.10,
        "boston": 1.08,
        "los angeles": 1.05,
        "denver": 0.95,
        "austin": 0.92,
        "remote": 0.90,
        "default": 1.0
    }
    return geo_factors.get(location.lower(), 1.0)


def _analyze_band_position(
    salary: float,
    band: Dict[str, float]
) -> Dict[str, Any]:
    """Analyze where salary falls within band"""
    band_min = band["min"]
    band_mid = band["mid"]
    band_max = band["max"]
    band_range = band_max - band_min

    if salary < band_min:
        percentile = 0
        position = "below_minimum"
        within_band = False
    elif salary > band_max:
        percentile = 100
        position = "above_maximum"
        within_band = False
    else:
        percentile = ((salary - band_min) / band_range) * 100
        within_band = True

        if salary < band_min + (band_range * 0.25):
            position = "lower_quartile"
        elif salary < band_mid:
            position = "below_midpoint"
        elif salary == band_mid:
            position = "at_midpoint"
        elif salary < band_min + (band_range * 0.75):
            position = "above_midpoint"
        else:
            position = "upper_quartile"

    return {
        "within_band": within_band,
        "band_position": position,
        "band_percentile": round(percentile, 1)
    }


def _calculate_total_compensation(
    base_salary: float,
    signing_bonus: float,
    target_bonus_percent: float,
    equity_grant: str
) -> Dict[str, float]:
    """Calculate total first-year compensation"""
    target_bonus = base_salary * (target_bonus_percent / 100) if target_bonus_percent else 0

    # Parse equity value (simplified)
    equity_value = 0
    if equity_grant:
        try:
            # Try to extract numeric value
            import re
            numbers = re.findall(r'[\d,]+', equity_grant.replace(',', ''))
            if numbers:
                equity_value = float(numbers[0])
                # If it looks like shares, estimate value
                if 'share' in equity_grant.lower() and equity_value > 1000:
                    equity_value = equity_value * 50  # Assume $50/share
        except Exception:
            pass

    # First year equity (typically 25% vests)
    first_year_equity = equity_value * 0.25

    total = base_salary + signing_bonus + target_bonus + first_year_equity

    return {
        "base_salary": base_salary,
        "signing_bonus": signing_bonus,
        "target_bonus": round(target_bonus, 2),
        "first_year_equity": round(first_year_equity, 2),
        "total_equity_grant": equity_value,
        "total": round(total, 2)
    }


def _check_exceptions(
    base_salary: float,
    band: Dict[str, float],
    signing_bonus: float,
    equity_grant: str
) -> List[str]:
    """Check for required exceptions"""
    exceptions = []

    if base_salary > band["max"]:
        exceptions.append("above_band_exception")

    if base_salary > band["mid"] * 1.1:
        exceptions.append("above_midpoint_justification")

    if signing_bonus > 25000:
        exceptions.append("signing_bonus_exception")

    if signing_bonus > 50000:
        exceptions.append("large_signing_bonus_exception")

    return exceptions


def _determine_approvals(
    base_salary: float,
    band: Dict[str, float],
    signing_bonus: float,
    equity_grant: str,
    exceptions: List[str]
) -> List[str]:
    """Determine required approvals based on offer details"""
    approvals = []

    # Standard hiring manager approval
    approvals.append("hiring_manager")

    # HR review for above midpoint
    if base_salary > band["mid"]:
        approvals.append("hr_compensation_review")

    # VP approval for above band
    if "above_band_exception" in exceptions:
        approvals.append("vp_approval")

    # CFO approval for large signing bonus
    if signing_bonus > 50000:
        approvals.append("cfo_approval")

    return approvals


def _check_budget(job_id: str, total_compensation: float) -> Dict[str, Any]:
    """Check if compensation is within job requisition budget"""
    try:
        tables = get_table_resource()
        table_name = os.environ.get('JOBS_TABLE', 'apex-ai-platform-job-requisitions')
        table = cosmos_db.Table(table_name)

        response = table.get_item(Key={"job_id": job_id})
        if 'Item' in response:
            budget = float(response['Item'].get('compensation_budget', 0))
            within = total_compensation <= budget
            return {
                "within_budget": within,
                "budget": budget,
                "overage": max(0, total_compensation - budget) if not within else 0
            }
    except Exception:
        pass

    return {"within_budget": True}


# ============================================================================
# Class-based implementation
# ============================================================================

class CompensationValidationAction(ApexActionBase):
    """
    Compensation Validation Action (class-based implementation)
    """

    name = "compensation_validation"
    description = "Validate compensation against bands and guidelines"
    category = "compensation"
    industry = "hr"

    def execute(
        self,
        job_level: str,
        location: str,
        base_salary: float,
        signing_bonus: float = 0,
        target_bonus_percent: float = 0,
        equity_grant: str = None,
        job_id: str = None,
        currency: str = "USD",
        **kwargs
    ) -> dict:
        """Execute the compensation validation"""
        return compensation_validation(
            job_level=job_level,
            location=location,
            base_salary=base_salary,
            signing_bonus=signing_bonus,
            target_bonus_percent=target_bonus_percent,
            equity_grant=equity_grant,
            job_id=job_id,
            currency=currency
        )


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return compensation_validation(**event)
