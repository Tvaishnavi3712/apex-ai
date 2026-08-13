"""
Clinical Decision Support Action
Provide evidence-based clinical recommendations
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Clinical guidelines database (simplified)
CLINICAL_GUIDELINES = {
    "diabetes_screening": {
        "condition": "diabetes",
        "criteria": {"age_min": 45, "bmi_min": 25},
        "recommendations": [
            "Screen with fasting glucose or HbA1c",
            "Repeat every 3 years if normal",
            "Screen earlier if BMI >= 25 with risk factors"
        ],
        "evidence_level": "A"
    },
    "statin_therapy": {
        "condition": "cardiovascular",
        "criteria": {"ldl_min": 190, "ascvd_risk_min": 7.5},
        "recommendations": [
            "High-intensity statin for LDL >= 190",
            "Moderate-intensity statin for 10-year ASCVD risk >= 7.5%",
            "Consider statin for diabetes ages 40-75"
        ],
        "evidence_level": "A"
    },
    "hypertension_management": {
        "condition": "hypertension",
        "criteria": {"systolic_min": 130, "diastolic_min": 80},
        "recommendations": [
            "Target BP < 130/80 for most patients",
            "First-line: ACE inhibitor, ARB, CCB, or thiazide",
            "Lifestyle modifications for all patients"
        ],
        "evidence_level": "A"
    }
}


@apex_action(ApexActionSchema(
    name="clinical_decision_support",
    description="Provide evidence-based clinical recommendations based on patient data",
    category="clinical",
    industry="healthcare_clinical",
    input_schema=ActionInputSchema(description="Clinical decision support parameters")
        .add_string("patient_id", "Patient MRN", required=True)
        .add_array("diagnoses", "Current diagnoses (ICD-10 or description)", required=True)
        .add_array("medications", "Current medications", required=False)
        .add_object("vitals", "Current vital signs", required=False)
        .add_object("labs", "Recent lab results", required=False)
        .add_number("age", "Patient age", required=False)
        .add_string("query", "Specific clinical question", required=False),
    output_schema=ActionOutputSchema(description="Clinical decision support result")
        .add_array("recommendations", "Clinical recommendations")
        .add_array("alerts", "Clinical alerts requiring attention")
        .add_array("quality_measures", "Applicable quality measures")
        .add_array("care_gaps", "Identified care gaps")
))
def clinical_decision_support(
    patient_id: str,
    diagnoses: List[str],
    medications: List[str] = None,
    vitals: Dict[str, Any] = None,
    labs: Dict[str, Any] = None,
    age: int = None,
    query: str = None
) -> dict:
    """
    Provide clinical decision support

    Args:
        patient_id: Patient MRN
        diagnoses: Current diagnoses
        medications: Current medications
        vitals: Current vitals
        labs: Recent labs
        age: Patient age
        query: Specific question

    Returns:
        Clinical recommendations and alerts
    """
    medications = medications or []
    vitals = vitals or {}
    labs = labs or {}

    result = {
        "patient_id": patient_id,
        "recommendations": [],
        "alerts": [],
        "quality_measures": [],
        "care_gaps": [],
        "analysis_date": datetime.now().isoformat()
    }

    # Analyze based on diagnoses
    diagnoses_lower = [d.lower() for d in diagnoses]

    # Diabetes checks
    if any("diabetes" in d or "e11" in d.lower() for d in diagnoses_lower):
        _add_diabetes_recommendations(result, medications, labs, vitals)

    # Hypertension checks
    if any("hypertension" in d or "i10" in d.lower() for d in diagnoses_lower):
        _add_hypertension_recommendations(result, medications, vitals)

    # Cardiovascular risk checks
    if any("cardiovascular" in d or "coronary" in d for d in diagnoses_lower):
        _add_cardiovascular_recommendations(result, medications, labs)

    # Check for preventive care gaps
    if age:
        _check_preventive_care(result, age, diagnoses_lower)

    # Generate alerts from vitals
    if vitals:
        _check_vital_alerts(result, vitals)

    # Generate alerts from labs
    if labs:
        _check_lab_alerts(result, labs)

    return result


def _add_diabetes_recommendations(result: dict, medications: List, labs: dict, vitals: dict):
    """Add diabetes-specific recommendations"""
    result["quality_measures"].append({
        "measure": "Diabetes: HbA1c Control",
        "target": "HbA1c < 7% for most adults",
        "code": "NQF0059"
    })

    hba1c = labs.get("hba1c", labs.get("a1c"))
    if hba1c:
        if hba1c > 9:
            result["alerts"].append({
                "type": "poor_control",
                "message": f"HbA1c {hba1c}% indicates poor glycemic control",
                "recommendation": "Consider treatment intensification"
            })
            result["care_gaps"].append("HbA1c > 9% - medication adjustment needed")

    # Check for statin therapy
    meds_lower = [m.lower() for m in medications]
    has_statin = any("statin" in m or "atorvastatin" in m or "simvastatin" in m or "rosuvastatin" in m for m in meds_lower)

    if not has_statin:
        result["care_gaps"].append("Diabetes without statin therapy - consider adding statin")
        result["recommendations"].append({
            "type": "medication",
            "recommendation": "Add moderate-intensity statin for cardiovascular protection",
            "evidence": "ADA Guidelines 2024"
        })


def _add_hypertension_recommendations(result: dict, medications: List, vitals: dict):
    """Add hypertension-specific recommendations"""
    result["quality_measures"].append({
        "measure": "Hypertension: BP Control",
        "target": "BP < 130/80 mmHg",
        "code": "NQF0018"
    })

    systolic = vitals.get("systolic", vitals.get("sbp"))
    diastolic = vitals.get("diastolic", vitals.get("dbp"))

    if systolic and diastolic:
        if systolic >= 140 or diastolic >= 90:
            result["alerts"].append({
                "type": "uncontrolled_bp",
                "message": f"Blood pressure {systolic}/{diastolic} is uncontrolled",
                "recommendation": "Consider medication adjustment"
            })
            result["care_gaps"].append(f"Uncontrolled hypertension: {systolic}/{diastolic}")


def _add_cardiovascular_recommendations(result: dict, medications: List, labs: dict):
    """Add cardiovascular recommendations"""
    ldl = labs.get("ldl")

    if ldl and ldl > 100:
        result["recommendations"].append({
            "type": "lipid_management",
            "recommendation": f"LDL {ldl} mg/dL - target < 70 mg/dL for high-risk patients",
            "evidence": "ACC/AHA Guidelines"
        })


def _check_preventive_care(result: dict, age: int, diagnoses: List):
    """Check for preventive care gaps"""
    if age >= 50:
        result["quality_measures"].append({
            "measure": "Colorectal Cancer Screening",
            "target": "Colonoscopy every 10 years or alternative screening",
            "code": "NQF0034"
        })

    if age >= 65:
        result["quality_measures"].append({
            "measure": "Pneumococcal Vaccination",
            "target": "PCV15 or PCV20 vaccination",
            "code": "NQF0043"
        })


def _check_vital_alerts(result: dict, vitals: dict):
    """Generate alerts from vital signs"""
    hr = vitals.get("heart_rate", vitals.get("hr"))
    if hr:
        if hr < 50:
            result["alerts"].append({
                "type": "bradycardia",
                "message": f"Heart rate {hr} bpm - bradycardia",
                "severity": "warning"
            })
        elif hr > 100:
            result["alerts"].append({
                "type": "tachycardia",
                "message": f"Heart rate {hr} bpm - tachycardia",
                "severity": "warning"
            })


def _check_lab_alerts(result: dict, labs: dict):
    """Generate alerts from lab values"""
    egfr = labs.get("egfr")
    if egfr and egfr < 60:
        result["alerts"].append({
            "type": "ckd",
            "message": f"eGFR {egfr} indicates chronic kidney disease",
            "recommendation": "Adjust renally-excreted medications; avoid NSAIDs"
        })


class ClinicalDecisionAction(ApexActionBase):
    """Clinical Decision Support Action (class-based)"""

    name = "clinical_decision_support"
    description = "Provide evidence-based clinical recommendations"
    category = "clinical"
    industry = "healthcare_clinical"

    def execute(self, **kwargs) -> dict:
        return clinical_decision_support(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return clinical_decision_support(**event)
