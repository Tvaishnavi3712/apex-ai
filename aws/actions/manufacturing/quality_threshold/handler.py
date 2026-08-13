"""
Quality Threshold Action
Validate quality inspection results against thresholds and determine disposition
"""

import boto3
from boto3.dynamodb.conditions import Key
import os
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import SDK
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# AQL (Acceptable Quality Level) lookup table - simplified
# Based on ANSI/ASQ Z1.4 sampling plans
AQL_LIMITS = {
    "critical": {"aql": 0, "accept": 0, "reject": 1},  # Zero tolerance
    "major_1.0": {"aql": 1.0, "accept": 2, "reject": 3},
    "major_2.5": {"aql": 2.5, "accept": 5, "reject": 6},
    "minor_4.0": {"aql": 4.0, "accept": 7, "reject": 8},
}


# ============================================================================
# Decorator-based implementation
# ============================================================================

@apex_action(ApexActionSchema(
    name="quality_threshold",
    description="Validate quality inspection results against thresholds and determine lot disposition",
    category="quality",
    industry="manufacturing",
    input_schema=ActionInputSchema(description="Quality threshold parameters")
        .add_string("part_number", "Part number being inspected", required=True)
        .add_string("lot_number", "Lot or batch number", required=True)
        .add_number("sample_size", "Number of samples inspected", required=True)
        .add_number("lot_size", "Total lot size", required=True)
        .add_array("test_results", "Array of test results with pass/fail", required=True)
        .add_array("defects", "Array of defects found", required=False)
        .add_string("inspection_level", "Inspection level (I, II, III)", required=False),
    output_schema=ActionOutputSchema(description="Quality threshold result")
        .add_string("disposition", "Lot disposition: accept, reject, conditional, hold")
        .add_boolean("passed", "Overall pass/fail result")
        .add_number("pass_rate", "Percentage of samples that passed")
        .add_object("defect_summary", "Summary of defects by severity")
        .add_array("violations", "List of threshold violations")
        .add_boolean("car_required", "Corrective action request required")
        .add_string("car_reason", "Reason for CAR if required")
))
def quality_threshold(
    part_number: str,
    lot_number: str,
    sample_size: int,
    lot_size: int,
    test_results: List[Dict[str, Any]],
    defects: List[Dict[str, Any]] = None,
    inspection_level: str = "II"
) -> dict:
    """
    Validate quality inspection results against thresholds

    Args:
        part_number: Part number being inspected
        lot_number: Lot or batch number
        sample_size: Number of samples inspected
        lot_size: Total lot size
        test_results: Array of test results
        defects: Array of defects found
        inspection_level: Inspection level (I, II, III)

    Returns:
        Quality threshold validation result and disposition
    """
    defects = defects or []

    result = {
        "part_number": part_number,
        "lot_number": lot_number,
        "disposition": "pending",
        "passed": False,
        "pass_rate": 0.0,
        "defect_summary": {
            "critical": 0,
            "major": 0,
            "minor": 0,
            "total": 0
        },
        "violations": [],
        "car_required": False,
        "car_reason": None,
        "test_summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "marginal": 0
        },
        "aql_results": {}
    }

    try:
        # Get part-specific thresholds from database
        thresholds = _get_part_thresholds(part_number)

        # Analyze test results
        test_summary = _analyze_test_results(test_results, thresholds)
        result["test_summary"] = test_summary

        # Calculate pass rate
        if test_summary["total_tests"] > 0:
            result["pass_rate"] = round(
                (test_summary["passed"] / test_summary["total_tests"]) * 100, 2
            )

        # Analyze defects by severity
        defect_summary = _analyze_defects(defects)
        result["defect_summary"] = defect_summary

        # Check against AQL limits
        violations = []
        aql_results = {}

        # Critical defects - zero tolerance
        if defect_summary["critical"] > 0:
            violations.append({
                "type": "critical_defect",
                "severity": "critical",
                "message": f"Critical defects found: {defect_summary['critical']}",
                "threshold": 0,
                "actual": defect_summary["critical"]
            })
            aql_results["critical"] = "FAIL"
        else:
            aql_results["critical"] = "PASS"

        # Major defects - check against AQL
        major_limit = AQL_LIMITS["major_1.0"]
        if defect_summary["major"] > major_limit["accept"]:
            violations.append({
                "type": "major_defect_aql",
                "severity": "major",
                "message": f"Major defects ({defect_summary['major']}) exceed AQL limit ({major_limit['accept']})",
                "threshold": major_limit["accept"],
                "actual": defect_summary["major"]
            })
            aql_results["major"] = "FAIL"
        else:
            aql_results["major"] = "PASS"

        # Minor defects - check against AQL
        minor_limit = AQL_LIMITS["minor_4.0"]
        if defect_summary["minor"] > minor_limit["accept"]:
            violations.append({
                "type": "minor_defect_aql",
                "severity": "minor",
                "message": f"Minor defects ({defect_summary['minor']}) exceed AQL limit ({minor_limit['accept']})",
                "threshold": minor_limit["accept"],
                "actual": defect_summary["minor"]
            })
            aql_results["minor"] = "FAIL"
        else:
            aql_results["minor"] = "PASS"

        # Check for test failures
        if test_summary["failed"] > 0:
            violations.append({
                "type": "test_failure",
                "severity": "major" if test_summary["failed"] > 1 else "minor",
                "message": f"{test_summary['failed']} test(s) failed",
                "threshold": 0,
                "actual": test_summary["failed"]
            })

        result["violations"] = violations
        result["aql_results"] = aql_results

        # Determine disposition
        disposition = _determine_disposition(violations, defect_summary, test_summary)
        result["disposition"] = disposition
        result["passed"] = disposition == "accept"

        # Determine if CAR is required
        car_required, car_reason = _check_car_required(violations, defect_summary)
        result["car_required"] = car_required
        result["car_reason"] = car_reason

        return result

    except Exception as e:
        return {
            "part_number": part_number,
            "lot_number": lot_number,
            "disposition": "error",
            "passed": False,
            "error": str(e)
        }


def _get_part_thresholds(part_number: str) -> Dict[str, Any]:
    """Get part-specific quality thresholds from database"""
    try:
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('SPECS_TABLE', 'apex-ai-platform-specifications')
        table = dynamodb.Table(table_name)

        response = table.get_item(Key={"part_number": part_number})
        if 'Item' in response:
            return response['Item'].get('quality_thresholds', {})
    except Exception:
        pass

    # Return default thresholds
    return {
        "critical_aql": 0,
        "major_aql": 1.0,
        "minor_aql": 2.5,
        "min_pass_rate": 95.0
    }


def _analyze_test_results(test_results: List[Dict], thresholds: Dict) -> Dict[str, int]:
    """Analyze test results and count pass/fail/marginal"""
    summary = {
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "marginal": 0
    }

    for test in test_results:
        summary["total_tests"] += 1
        result = str(test.get("result", "")).lower()

        if result in ["pass", "passed", "ok", "accept"]:
            summary["passed"] += 1
        elif result in ["fail", "failed", "reject", "ng"]:
            summary["failed"] += 1
        elif result in ["marginal", "warning", "borderline"]:
            summary["marginal"] += 1
        else:
            # Try to evaluate against specification
            actual = test.get("actual_value")
            spec_min = test.get("spec_min")
            spec_max = test.get("spec_max")

            if actual is not None and (spec_min is not None or spec_max is not None):
                try:
                    actual = float(actual)
                    if spec_min is not None and actual < float(spec_min):
                        summary["failed"] += 1
                    elif spec_max is not None and actual > float(spec_max):
                        summary["failed"] += 1
                    else:
                        summary["passed"] += 1
                except (ValueError, TypeError):
                    summary["failed"] += 1

    return summary


def _analyze_defects(defects: List[Dict]) -> Dict[str, int]:
    """Analyze defects by severity"""
    summary = {
        "critical": 0,
        "major": 0,
        "minor": 0,
        "total": 0
    }

    for defect in defects:
        severity = str(defect.get("severity", "minor")).lower()
        quantity = int(defect.get("quantity_affected", 1))

        summary["total"] += quantity

        if severity in ["critical", "crit", "c"]:
            summary["critical"] += quantity
        elif severity in ["major", "maj", "a", "b"]:
            summary["major"] += quantity
        else:
            summary["minor"] += quantity

    return summary


def _determine_disposition(
    violations: List[Dict],
    defect_summary: Dict,
    test_summary: Dict
) -> str:
    """Determine lot disposition based on findings"""

    # Critical defects = automatic reject
    if defect_summary["critical"] > 0:
        return "reject"

    # Check for critical violations
    critical_violations = [v for v in violations if v.get("severity") == "critical"]
    if critical_violations:
        return "reject"

    # Check for major violations
    major_violations = [v for v in violations if v.get("severity") == "major"]
    if major_violations:
        # Could be reject or conditional based on quantity
        if len(major_violations) > 1 or defect_summary["major"] > 5:
            return "reject"
        return "conditional"

    # Minor violations only
    if violations:
        return "conditional"

    # All tests passed, no violations
    if test_summary["failed"] == 0 and not violations:
        return "accept"

    return "hold"


def _check_car_required(violations: List[Dict], defect_summary: Dict) -> tuple:
    """Check if corrective action request is required"""

    # Critical defects always require CAR
    if defect_summary["critical"] > 0:
        return True, "Critical defect(s) found - immediate corrective action required"

    # Major defects above threshold require CAR
    if defect_summary["major"] >= 3:
        return True, f"Multiple major defects ({defect_summary['major']}) indicate systematic issue"

    # Critical violations require CAR
    critical_violations = [v for v in violations if v.get("severity") == "critical"]
    if critical_violations:
        return True, critical_violations[0].get("message")

    return False, None


# ============================================================================
# Class-based implementation
# ============================================================================

class QualityThresholdAction(ApexActionBase):
    """
    Quality Threshold Action (class-based implementation)
    """

    name = "quality_threshold"
    description = "Validate quality inspection results against thresholds"
    category = "quality"
    industry = "manufacturing"

    def __init__(self, specs_table: str = None):
        super().__init__()
        self.specs_table = specs_table or os.environ.get(
            'SPECS_TABLE',
            'apex-ai-platform-specifications'
        )

    def execute(
        self,
        part_number: str,
        lot_number: str,
        sample_size: int,
        lot_size: int,
        test_results: List[Dict[str, Any]],
        defects: List[Dict[str, Any]] = None,
        inspection_level: str = "II",
        **kwargs
    ) -> dict:
        """Execute the quality threshold validation"""
        return quality_threshold(
            part_number=part_number,
            lot_number=lot_number,
            sample_size=sample_size,
            lot_size=lot_size,
            test_results=test_results,
            defects=defects,
            inspection_level=inspection_level
        )


# Lambda handler
def handler(event, context):
    """Lambda entry point"""
    return quality_threshold(**event)
