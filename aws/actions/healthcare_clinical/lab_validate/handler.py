"""
Lab Result Validation Action
Validate lab results against reference ranges and flag abnormal values
"""

import os
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Reference ranges for common lab tests
REFERENCE_RANGES = {
    "glucose": {"low": 70, "high": 100, "critical_low": 50, "critical_high": 400, "unit": "mg/dL"},
    "hemoglobin": {"low": 12.0, "high": 17.5, "critical_low": 7.0, "critical_high": 20.0, "unit": "g/dL"},
    "hematocrit": {"low": 36, "high": 50, "critical_low": 20, "critical_high": 60, "unit": "%"},
    "wbc": {"low": 4.5, "high": 11.0, "critical_low": 2.0, "critical_high": 30.0, "unit": "K/uL"},
    "platelet": {"low": 150, "high": 400, "critical_low": 50, "critical_high": 1000, "unit": "K/uL"},
    "sodium": {"low": 136, "high": 145, "critical_low": 120, "critical_high": 160, "unit": "mEq/L"},
    "potassium": {"low": 3.5, "high": 5.0, "critical_low": 2.5, "critical_high": 6.5, "unit": "mEq/L"},
    "creatinine": {"low": 0.7, "high": 1.3, "critical_low": 0.4, "critical_high": 10.0, "unit": "mg/dL"},
    "bun": {"low": 7, "high": 20, "critical_low": 2, "critical_high": 100, "unit": "mg/dL"},
    "troponin": {"low": 0, "high": 0.04, "critical_low": 0, "critical_high": 0.1, "unit": "ng/mL"},
    "inr": {"low": 0.8, "high": 1.2, "critical_low": 0.5, "critical_high": 5.0, "unit": "ratio"}
}


@apex_action(ApexActionSchema(
    name="lab_validate",
    description="Validate lab results against reference ranges and flag abnormal values",
    category="laboratory",
    industry="healthcare_clinical",
    input_schema=ActionInputSchema(description="Lab validation parameters")
        .add_string("patient_id", "Patient MRN", required=True)
        .add_string("order_id", "Lab order ID", required=True)
        .add_array("results", "Lab results with test name and value", required=True)
        .add_string("patient_age", "Patient age for age-adjusted ranges", required=False)
        .add_string("patient_gender", "Patient gender for gender-adjusted ranges", required=False),
    output_schema=ActionOutputSchema(description="Lab validation result")
        .add_boolean("all_normal", "Whether all results are within normal range")
        .add_boolean("has_critical", "Whether any critical values exist")
        .add_array("validated_results", "Validated results with flags")
        .add_array("critical_values", "Critical values requiring immediate attention")
        .add_array("abnormal_values", "Abnormal but non-critical values")
))
def lab_validate(
    patient_id: str,
    order_id: str,
    results: List[Dict],
    patient_age: str = None,
    patient_gender: str = None
) -> dict:
    """
    Validate lab results against reference ranges

    Args:
        patient_id: Patient MRN
        order_id: Lab order ID
        results: List of lab results
        patient_age: Patient age
        patient_gender: Patient gender

    Returns:
        Validated lab results with flags
    """
    result = {
        "patient_id": patient_id,
        "order_id": order_id,
        "all_normal": True,
        "has_critical": False,
        "validated_results": [],
        "critical_values": [],
        "abnormal_values": [],
        "validation_date": datetime.now().isoformat()
    }

    for lab_result in results:
        test_name = lab_result.get("test", "").lower().replace(" ", "_")
        value = lab_result.get("value")
        unit = lab_result.get("unit", "")

        # Get reference range
        ref_range = REFERENCE_RANGES.get(test_name, {})

        validated = {
            "test_name": lab_result.get("test"),
            "value": value,
            "unit": unit or ref_range.get("unit", ""),
            "reference_low": ref_range.get("low"),
            "reference_high": ref_range.get("high"),
            "status": "normal",
            "flag": None
        }

        if ref_range and isinstance(value, (int, float)):
            # Check critical values
            if value <= ref_range.get("critical_low", float('-inf')):
                validated["status"] = "critical"
                validated["flag"] = "critical_low"
                result["has_critical"] = True
                result["all_normal"] = False
                result["critical_values"].append({
                    "test": lab_result.get("test"),
                    "value": value,
                    "critical_threshold": ref_range.get("critical_low"),
                    "direction": "low"
                })
            elif value >= ref_range.get("critical_high", float('inf')):
                validated["status"] = "critical"
                validated["flag"] = "critical_high"
                result["has_critical"] = True
                result["all_normal"] = False
                result["critical_values"].append({
                    "test": lab_result.get("test"),
                    "value": value,
                    "critical_threshold": ref_range.get("critical_high"),
                    "direction": "high"
                })
            elif value < ref_range.get("low", float('-inf')):
                validated["status"] = "abnormal"
                validated["flag"] = "low"
                result["all_normal"] = False
                result["abnormal_values"].append({
                    "test": lab_result.get("test"),
                    "value": value,
                    "reference_low": ref_range.get("low"),
                    "direction": "low"
                })
            elif value > ref_range.get("high", float('inf')):
                validated["status"] = "abnormal"
                validated["flag"] = "high"
                result["all_normal"] = False
                result["abnormal_values"].append({
                    "test": lab_result.get("test"),
                    "value": value,
                    "reference_high": ref_range.get("high"),
                    "direction": "high"
                })

        result["validated_results"].append(validated)

    return result


class LabValidateAction(ApexActionBase):
    """Lab Validation Action (class-based)"""

    name = "lab_validate"
    description = "Validate lab results against reference ranges"
    category = "laboratory"
    industry = "healthcare_clinical"

    def execute(self, **kwargs) -> dict:
        return lab_validate(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return lab_validate(**event)
