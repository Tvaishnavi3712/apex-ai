"""
Formulary Check Action
Check medication formulary coverage and suggest alternatives
"""

import boto3
import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Formulary tiers and coverage
FORMULARY_DATA = {
    "lisinopril": {"tier": 1, "covered": True, "copay": 10, "prior_auth": False},
    "metformin": {"tier": 1, "covered": True, "copay": 10, "prior_auth": False},
    "atorvastatin": {"tier": 1, "covered": True, "copay": 10, "prior_auth": False},
    "amlodipine": {"tier": 1, "covered": True, "copay": 10, "prior_auth": False},
    "omeprazole": {"tier": 1, "covered": True, "copay": 10, "prior_auth": False},
    "metoprolol": {"tier": 1, "covered": True, "copay": 10, "prior_auth": False},
    "losartan": {"tier": 2, "covered": True, "copay": 30, "prior_auth": False},
    "rosuvastatin": {"tier": 2, "covered": True, "copay": 30, "prior_auth": False},
    "pantoprazole": {"tier": 2, "covered": True, "copay": 30, "prior_auth": False},
    "eliquis": {"tier": 3, "covered": True, "copay": 75, "prior_auth": True},
    "jardiance": {"tier": 3, "covered": True, "copay": 75, "prior_auth": True},
    "ozempic": {"tier": 3, "covered": True, "copay": 100, "prior_auth": True},
    "humira": {"tier": 4, "covered": True, "copay": 150, "prior_auth": True, "specialty": True},
    "keytruda": {"tier": 4, "covered": True, "copay": 200, "prior_auth": True, "specialty": True}
}

# Therapeutic alternatives
THERAPEUTIC_ALTERNATIVES = {
    "rosuvastatin": ["atorvastatin", "simvastatin", "pravastatin"],
    "pantoprazole": ["omeprazole", "lansoprazole"],
    "losartan": ["lisinopril", "enalapril"],
    "eliquis": ["warfarin", "xarelto"],
    "jardiance": ["metformin", "glipizide"],
    "ozempic": ["trulicity", "victoza", "metformin"]
}


@apex_action(ApexActionSchema(
    name="formulary_check",
    description="Check medication formulary coverage and suggest alternatives",
    category="pharmacy",
    industry="healthcare_clinical",
    input_schema=ActionInputSchema(description="Formulary check parameters")
        .add_string("medication", "Medication name to check", required=True)
        .add_string("member_id", "Insurance member ID", required=False)
        .add_string("plan_id", "Insurance plan ID", required=False)
        .add_boolean("include_alternatives", "Include therapeutic alternatives", required=False),
    output_schema=ActionOutputSchema(description="Formulary check result")
        .add_boolean("on_formulary", "Whether medication is on formulary")
        .add_number("tier", "Formulary tier (1-4)")
        .add_number("estimated_copay", "Estimated member copay")
        .add_boolean("prior_auth_required", "Whether prior authorization is required")
        .add_boolean("specialty_drug", "Whether it is a specialty drug")
        .add_array("alternatives", "Lower-tier alternatives if available")
        .add_object("quantity_limits", "Quantity limit information if applicable")
))
def formulary_check(
    medication: str,
    member_id: str = None,
    plan_id: str = None,
    include_alternatives: bool = True
) -> dict:
    """
    Check formulary coverage for a medication

    Args:
        medication: Medication name
        member_id: Insurance member ID
        plan_id: Insurance plan ID
        include_alternatives: Include alternatives

    Returns:
        Formulary coverage details
    """
    med_lower = medication.lower().strip()

    result = {
        "medication": medication,
        "on_formulary": False,
        "tier": None,
        "estimated_copay": None,
        "prior_auth_required": False,
        "specialty_drug": False,
        "alternatives": [],
        "quantity_limits": None,
        "step_therapy_required": False,
        "check_date": datetime.now().isoformat()
    }

    # Check formulary
    formulary_info = FORMULARY_DATA.get(med_lower)

    if formulary_info:
        result["on_formulary"] = formulary_info.get("covered", False)
        result["tier"] = formulary_info.get("tier")
        result["estimated_copay"] = formulary_info.get("copay")
        result["prior_auth_required"] = formulary_info.get("prior_auth", False)
        result["specialty_drug"] = formulary_info.get("specialty", False)

        # Add quantity limits for certain drugs
        if formulary_info.get("tier", 0) >= 3:
            result["quantity_limits"] = {
                "max_quantity": 30,
                "days_supply": 30,
                "refills_allowed": 11
            }

        # Check step therapy
        if med_lower in ["eliquis", "jardiance", "ozempic"]:
            result["step_therapy_required"] = True
            result["step_therapy_drugs"] = THERAPEUTIC_ALTERNATIVES.get(med_lower, [])[:2]

    # Find alternatives
    if include_alternatives:
        alternatives = THERAPEUTIC_ALTERNATIVES.get(med_lower, [])
        for alt in alternatives:
            alt_info = FORMULARY_DATA.get(alt)
            if alt_info and alt_info.get("tier", 5) < formulary_info.get("tier", 1) if formulary_info else True:
                result["alternatives"].append({
                    "medication": alt.title(),
                    "tier": alt_info.get("tier"),
                    "estimated_copay": alt_info.get("copay"),
                    "prior_auth_required": alt_info.get("prior_auth", False),
                    "savings": (formulary_info.get("copay", 0) - alt_info.get("copay", 0)) if formulary_info else 0
                })

    # Sort alternatives by tier
    result["alternatives"].sort(key=lambda x: (x["tier"], x["estimated_copay"]))

    # Add coverage notes
    if not result["on_formulary"]:
        result["coverage_notes"] = "Medication not on formulary. Prior authorization may be required for coverage."
    elif result["prior_auth_required"]:
        result["coverage_notes"] = "Prior authorization required. Contact pharmacy benefits for approval process."
    elif result["tier"] >= 3:
        result["coverage_notes"] = "Specialty tier medication. Consider tier 1/2 alternatives for lower cost."

    return result


class FormularyCheckAction(ApexActionBase):
    """Formulary Check Action (class-based)"""

    name = "formulary_check"
    description = "Check medication formulary coverage"
    category = "pharmacy"
    industry = "healthcare_clinical"

    def execute(self, **kwargs) -> dict:
        return formulary_check(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return formulary_check(**event)
