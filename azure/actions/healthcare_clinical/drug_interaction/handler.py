"""
Drug Interaction Check Action
Check for drug-drug interactions and contraindications
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Drug interaction database (simplified)
DRUG_INTERACTIONS = {
    ("warfarin", "aspirin"): {
        "severity": "major",
        "effect": "Increased risk of bleeding",
        "recommendation": "Monitor INR closely; consider alternative antiplatelet"
    },
    ("warfarin", "ibuprofen"): {
        "severity": "major",
        "effect": "Increased anticoagulant effect and GI bleeding risk",
        "recommendation": "Avoid combination; use acetaminophen if analgesia needed"
    },
    ("metformin", "contrast"): {
        "severity": "major",
        "effect": "Risk of lactic acidosis with IV contrast",
        "recommendation": "Hold metformin 48 hours before and after contrast administration"
    },
    ("lisinopril", "potassium"): {
        "severity": "moderate",
        "effect": "Risk of hyperkalemia",
        "recommendation": "Monitor potassium levels regularly"
    },
    ("simvastatin", "amiodarone"): {
        "severity": "major",
        "effect": "Increased risk of myopathy/rhabdomyolysis",
        "recommendation": "Limit simvastatin to 20mg daily or use alternative statin"
    },
    ("ssri", "tramadol"): {
        "severity": "major",
        "effect": "Increased risk of serotonin syndrome",
        "recommendation": "Monitor for serotonin syndrome symptoms; consider alternative"
    },
    ("methotrexate", "nsaid"): {
        "severity": "major",
        "effect": "Increased methotrexate toxicity",
        "recommendation": "Avoid NSAIDs or monitor methotrexate levels closely"
    }
}

# Drug class mappings
DRUG_CLASSES = {
    "sertraline": "ssri",
    "fluoxetine": "ssri",
    "paroxetine": "ssri",
    "escitalopram": "ssri",
    "ibuprofen": "nsaid",
    "naproxen": "nsaid",
    "diclofenac": "nsaid",
    "meloxicam": "nsaid"
}


@apex_action(ApexActionSchema(
    name="drug_interaction_check",
    description="Check for drug-drug interactions and contraindications",
    category="pharmacy",
    industry="healthcare_clinical",
    input_schema=ActionInputSchema(description="Drug interaction check parameters")
        .add_string("patient_id", "Patient MRN", required=True)
        .add_array("current_medications", "Patient's current medications", required=True)
        .add_array("new_medications", "New medications being prescribed", required=True)
        .add_array("allergies", "Patient allergies", required=False),
    output_schema=ActionOutputSchema(description="Drug interaction check result")
        .add_boolean("safe_to_prescribe", "Whether new medications are safe")
        .add_boolean("has_major_interactions", "Whether major interactions exist")
        .add_array("interactions", "List of drug interactions found")
        .add_array("allergy_alerts", "Allergy-related alerts")
        .add_array("recommendations", "Clinical recommendations")
))
def drug_interaction_check(
    patient_id: str,
    current_medications: List[str],
    new_medications: List[str],
    allergies: List[str] = None
) -> dict:
    """
    Check for drug interactions

    Args:
        patient_id: Patient MRN
        current_medications: Current medications
        new_medications: New medications
        allergies: Patient allergies

    Returns:
        Interaction check results
    """
    allergies = allergies or []

    result = {
        "patient_id": patient_id,
        "safe_to_prescribe": True,
        "has_major_interactions": False,
        "interactions": [],
        "allergy_alerts": [],
        "recommendations": [],
        "check_date": datetime.now().isoformat()
    }

    # Normalize drug names
    all_current = [_normalize_drug(d) for d in current_medications]
    all_new = [_normalize_drug(d) for d in new_medications]

    # Check interactions between new drugs and current drugs
    for new_drug in all_new:
        for current_drug in all_current:
            interaction = _check_interaction(new_drug, current_drug)
            if interaction:
                result["interactions"].append({
                    "drug1": new_drug,
                    "drug2": current_drug,
                    **interaction
                })
                if interaction["severity"] == "major":
                    result["has_major_interactions"] = True
                    result["safe_to_prescribe"] = False

        # Check interactions between new drugs
        for other_new in all_new:
            if new_drug != other_new:
                interaction = _check_interaction(new_drug, other_new)
                if interaction:
                    # Avoid duplicates
                    if not any(
                        i["drug1"] == other_new and i["drug2"] == new_drug
                        for i in result["interactions"]
                    ):
                        result["interactions"].append({
                            "drug1": new_drug,
                            "drug2": other_new,
                            **interaction
                        })
                        if interaction["severity"] == "major":
                            result["has_major_interactions"] = True
                            result["safe_to_prescribe"] = False

    # Check allergies
    for new_drug in new_medications:
        allergy_check = _check_allergy(new_drug, allergies)
        if allergy_check:
            result["allergy_alerts"].append(allergy_check)
            result["safe_to_prescribe"] = False

    # Generate recommendations
    if result["has_major_interactions"]:
        result["recommendations"].append(
            "Major drug interactions detected. Review and consider alternatives."
        )
    if result["allergy_alerts"]:
        result["recommendations"].append(
            "Potential allergy cross-reactivity detected. Verify with patient."
        )
    if result["safe_to_prescribe"]:
        result["recommendations"].append(
            "No significant interactions detected. Safe to prescribe with standard monitoring."
        )

    return result


def _normalize_drug(drug_name: str) -> str:
    """Normalize drug name for matching"""
    normalized = drug_name.lower().strip()
    # Remove common suffixes
    for suffix in [" hcl", " sodium", " er", " xr", " cr", " sr"]:
        normalized = normalized.replace(suffix, "")
    return normalized


def _check_interaction(drug1: str, drug2: str) -> dict:
    """Check for interaction between two drugs"""
    # Direct lookup
    key1 = (drug1, drug2)
    key2 = (drug2, drug1)

    if key1 in DRUG_INTERACTIONS:
        return DRUG_INTERACTIONS[key1]
    if key2 in DRUG_INTERACTIONS:
        return DRUG_INTERACTIONS[key2]

    # Check by drug class
    class1 = DRUG_CLASSES.get(drug1, drug1)
    class2 = DRUG_CLASSES.get(drug2, drug2)

    key1 = (class1, drug2)
    key2 = (drug1, class2)
    key3 = (class1, class2)

    for key in [key1, key2, key3]:
        if key in DRUG_INTERACTIONS:
            return DRUG_INTERACTIONS[key]

    return None


def _check_allergy(drug: str, allergies: List[str]) -> dict:
    """Check for drug-allergy conflicts"""
    drug_lower = drug.lower()
    allergy_lower = [a.lower() for a in allergies]

    # Cross-reactivity mappings
    cross_reactivity = {
        "penicillin": ["amoxicillin", "ampicillin", "augmentin", "piperacillin"],
        "sulfa": ["sulfamethoxazole", "bactrim", "septra", "sulfasalazine"],
        "cephalosporin": ["cefazolin", "ceftriaxone", "cephalexin", "keflex"],
        "nsaid": ["ibuprofen", "naproxen", "aspirin", "meloxicam", "diclofenac"]
    }

    for allergy in allergy_lower:
        if allergy in drug_lower or drug_lower in allergy:
            return {
                "drug": drug,
                "allergy": allergy,
                "alert_type": "direct_match",
                "severity": "contraindicated"
            }

        # Check cross-reactivity
        for allergen_class, drugs in cross_reactivity.items():
            if allergy in allergen_class or allergen_class in allergy:
                if drug_lower in drugs:
                    return {
                        "drug": drug,
                        "allergy": allergy,
                        "alert_type": "cross_reactivity",
                        "class": allergen_class,
                        "severity": "caution"
                    }

    return None


class DrugInteractionAction(ApexActionBase):
    """Drug Interaction Check Action (class-based)"""

    name = "drug_interaction_check"
    description = "Check for drug-drug interactions"
    category = "pharmacy"
    industry = "healthcare_clinical"

    def execute(self, **kwargs) -> dict:
        return drug_interaction_check(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return drug_interaction_check(**event)
