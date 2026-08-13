"""
Fraud Score Action
Calculate fraud risk score for returns and transactions
"""

import boto3
from boto3.dynamodb.conditions import Key
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


@apex_action(ApexActionSchema(
    name="fraud_score",
    description="Calculate fraud risk score for returns and transactions",
    category="fraud",
    industry="retail",
    input_schema=ActionInputSchema(description="Fraud scoring parameters")
        .add_string("customer_id", "Customer identifier", required=False)
        .add_string("transaction_id", "Transaction being evaluated", required=True)
        .add_string("action_type", "Type of action: return, exchange, purchase", required=True)
        .add_number("amount", "Transaction amount", required=True)
        .add_string("payment_method", "Payment method used", required=False)
        .add_boolean("has_receipt", "Whether receipt is present", required=False),
    output_schema=ActionOutputSchema(description="Fraud score result")
        .add_number("fraud_score", "Fraud risk score 0-100")
        .add_string("risk_level", "Risk level: low, medium, high, critical")
        .add_boolean("requires_review", "Whether manual review is required")
        .add_array("risk_factors", "Identified risk factors")
        .add_array("recommendations", "Recommended actions")
))
def fraud_score(
    transaction_id: str,
    action_type: str,
    amount: float,
    customer_id: str = None,
    payment_method: str = None,
    has_receipt: bool = True
) -> dict:
    """
    Calculate fraud risk score

    Args:
        transaction_id: Transaction ID
        action_type: Action type (return, exchange, purchase)
        amount: Transaction amount
        customer_id: Customer ID
        payment_method: Payment method
        has_receipt: Has receipt

    Returns:
        Fraud score and risk assessment
    """
    result = {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "fraud_score": 0,
        "risk_level": "low",
        "requires_review": False,
        "risk_factors": [],
        "recommendations": [],
        "scoring_date": datetime.now().isoformat()
    }

    score = 0

    # Check customer history if available
    if customer_id:
        history = _get_customer_history(customer_id)

        # High return rate
        if history.get("return_rate", 0) > 0.3:
            score += 20
            result["risk_factors"].append({
                "factor": "high_return_rate",
                "description": f"Return rate {history['return_rate']*100:.1f}% exceeds threshold",
                "weight": 20
            })

        # Frequent returns
        if history.get("returns_30_days", 0) > 5:
            score += 15
            result["risk_factors"].append({
                "factor": "frequent_returns",
                "description": f"{history['returns_30_days']} returns in last 30 days",
                "weight": 15
            })

        # New customer with high value return
        if history.get("account_age_days", 365) < 30 and amount > 100:
            score += 15
            result["risk_factors"].append({
                "factor": "new_account_high_value",
                "description": "New account with high-value return",
                "weight": 15
            })
    else:
        # No customer ID - higher risk
        score += 10
        result["risk_factors"].append({
            "factor": "unidentified_customer",
            "description": "No customer identification provided",
            "weight": 10
        })

    # No receipt penalty
    if not has_receipt:
        score += 20
        result["risk_factors"].append({
            "factor": "no_receipt",
            "description": "No receipt provided for return",
            "weight": 20
        })

    # High value threshold
    if amount > 500:
        score += 15
        result["risk_factors"].append({
            "factor": "high_value",
            "description": f"High-value transaction: ${amount:.2f}",
            "weight": 15
        })
    elif amount > 200:
        score += 5
        result["risk_factors"].append({
            "factor": "elevated_value",
            "description": f"Elevated value transaction: ${amount:.2f}",
            "weight": 5
        })

    # Cash refund request
    if payment_method and "cash" in payment_method.lower():
        if amount > 50:
            score += 10
            result["risk_factors"].append({
                "factor": "cash_refund_request",
                "description": "Cash refund requested for significant amount",
                "weight": 10
            })

    # Calculate final score (cap at 100)
    result["fraud_score"] = min(score, 100)

    # Determine risk level
    if result["fraud_score"] >= 70:
        result["risk_level"] = "critical"
        result["requires_review"] = True
        result["recommendations"].append("Manager approval required")
        result["recommendations"].append("Verify customer identity")
    elif result["fraud_score"] >= 50:
        result["risk_level"] = "high"
        result["requires_review"] = True
        result["recommendations"].append("Supervisor review recommended")
    elif result["fraud_score"] >= 25:
        result["risk_level"] = "medium"
        result["recommendations"].append("Standard processing with monitoring")
    else:
        result["risk_level"] = "low"
        result["recommendations"].append("Proceed with standard processing")

    return result


def _get_customer_history(customer_id: str) -> dict:
    """Get customer return history"""
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('CUSTOMER_TABLE', 'apex-retail-customers'))

        response = table.get_item(Key={"customer_id": customer_id})
        if 'Item' in response:
            return response['Item']
    except Exception:
        pass

    # Return mock history
    return {
        "customer_id": customer_id,
        "return_rate": 0.15,
        "returns_30_days": 2,
        "total_purchases": 20,
        "total_returns": 3,
        "account_age_days": 180,
        "lifetime_value": 1500
    }


class FraudScoreAction(ApexActionBase):
    """Fraud Score Action (class-based)"""

    name = "fraud_score"
    description = "Calculate fraud risk score"
    category = "fraud"
    industry = "retail"

    def execute(self, **kwargs) -> dict:
        return fraud_score(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return fraud_score(**event)
