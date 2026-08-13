"""
Loss History Check Action
Check applicant loss history from reporting databases
"""

import boto3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="loss_history_check",
    description="Check applicant loss history from CLUE, A-PLUS, and other databases",
    category="underwriting",
    industry="insurance_underwriting",
    input_schema=ActionInputSchema(description="Loss history check parameters")
        .add_string("application_id", "Application identifier", required=True)
        .add_string("applicant_name", "Applicant full name", required=True)
        .add_string("date_of_birth", "Date of birth", required=False)
        .add_string("ssn_last4", "Last 4 of SSN for matching", required=False)
        .add_string("property_address", "Property address for home/property searches", required=False)
        .add_string("vin", "Vehicle VIN for auto searches", required=False)
        .add_string("line_of_business", "Insurance line for appropriate search", required=True),
    output_schema=ActionOutputSchema(description="Loss history check result")
        .add_array("losses", "List of losses found")
        .add_number("total_losses_5yr", "Total losses in last 5 years")
        .add_number("total_paid", "Total amount paid")
        .add_array("loss_summary", "Summary by loss type")
        .add_boolean("adverse_history", "Whether adverse history exists")
        .add_string("report_reference", "Report reference number")
))
def loss_history_check(
    application_id: str,
    applicant_name: str,
    line_of_business: str,
    date_of_birth: str = None,
    ssn_last4: str = None,
    property_address: str = None,
    vin: str = None
) -> dict:
    """
    Check loss history

    Args:
        application_id: Application ID
        applicant_name: Applicant name
        line_of_business: Line of business
        date_of_birth: Date of birth
        ssn_last4: Last 4 SSN
        property_address: Property address
        vin: Vehicle VIN

    Returns:
        Loss history results
    """
    report_reference = f"LH-{datetime.now().strftime('%Y%m%d%H%M%S')}-{application_id[:8]}"

    result = {
        "application_id": application_id,
        "applicant_name": applicant_name,
        "line_of_business": line_of_business,
        "losses": [],
        "total_losses_5yr": 0,
        "total_paid": 0,
        "loss_summary": [],
        "adverse_history": False,
        "report_reference": report_reference,
        "report_date": datetime.now().isoformat()
    }

    try:
        # This would call actual loss history services (CLUE, A-PLUS, etc.)
        # Simplified implementation returns mock data
        losses = _query_loss_database(applicant_name, property_address, vin, line_of_business)

        result["losses"] = losses
        result["total_losses_5yr"] = len(losses)
        result["total_paid"] = sum(l.get("amount_paid", 0) for l in losses)

        # Summarize by type
        loss_types = {}
        for loss in losses:
            loss_type = loss.get("loss_type", "Unknown")
            if loss_type not in loss_types:
                loss_types[loss_type] = {"count": 0, "total_paid": 0}
            loss_types[loss_type]["count"] += 1
            loss_types[loss_type]["total_paid"] += loss.get("amount_paid", 0)

        result["loss_summary"] = [
            {"loss_type": k, **v} for k, v in loss_types.items()
        ]

        # Determine if adverse
        if result["total_losses_5yr"] >= 3:
            result["adverse_history"] = True
        if result["total_paid"] > 50000:
            result["adverse_history"] = True

        # Check for specific adverse loss types
        for loss in losses:
            if loss.get("loss_type") in ["Fire", "Water - Pipe Burst", "Liability Claim"]:
                if loss.get("amount_paid", 0) > 10000:
                    result["adverse_history"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


def _query_loss_database(name: str, address: str, vin: str, lob: str) -> List[dict]:
    """Query loss history databases"""
    # Mock loss data for demonstration
    # In production, this would call CLUE, A-PLUS, ISO ClaimSearch, etc.

    if lob == "auto":
        return [
            {
                "loss_date": (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d'),
                "loss_type": "Collision",
                "description": "Rear-end collision",
                "amount_paid": 3500,
                "fault": "Other party at fault",
                "reporting_carrier": "Sample Insurance Co"
            }
        ]
    elif lob == "home":
        return [
            {
                "loss_date": (datetime.now() - timedelta(days=800)).strftime('%Y-%m-%d'),
                "loss_type": "Weather",
                "description": "Wind/hail damage to roof",
                "amount_paid": 8500,
                "reporting_carrier": "ABC Insurance"
            }
        ]
    else:
        return []


class LossHistoryAction(ApexActionBase):
    """Loss History Check Action (class-based)"""

    name = "loss_history_check"
    description = "Check applicant loss history"
    category = "underwriting"
    industry = "insurance_underwriting"

    def execute(self, **kwargs) -> dict:
        return loss_history_check(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return loss_history_check(**event)
