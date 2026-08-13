"""
Return Policy Check Action
Check return policies and eligibility for items
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema, ApexActionBase


# Return policies by category
RETURN_POLICIES = {
    "electronics": {
        "return_window_days": 15,
        "restocking_fee_pct": 15,
        "condition_required": "unopened_or_like_new",
        "receipt_required": True,
        "exceptions": ["software", "memory_cards"]
    },
    "clothing": {
        "return_window_days": 30,
        "restocking_fee_pct": 0,
        "condition_required": "unworn_with_tags",
        "receipt_required": True,
        "exceptions": ["swimwear", "undergarments"]
    },
    "furniture": {
        "return_window_days": 7,
        "restocking_fee_pct": 20,
        "condition_required": "unassembled",
        "receipt_required": True,
        "exceptions": ["custom_orders"]
    },
    "perishable": {
        "return_window_days": 1,
        "restocking_fee_pct": 0,
        "condition_required": "quality_issue_only",
        "receipt_required": True,
        "exceptions": []
    },
    "default": {
        "return_window_days": 30,
        "restocking_fee_pct": 0,
        "condition_required": "original_condition",
        "receipt_required": True,
        "exceptions": []
    }
}


@apex_action(ApexActionSchema(
    name="return_policy_check",
    description="Check return policies and eligibility for items",
    category="returns",
    industry="retail",
    input_schema=ActionInputSchema(description="Return policy check parameters")
        .add_string("sku", "Item SKU", required=True)
        .add_string("category", "Item category", required=False)
        .add_string("purchase_date", "Purchase date (YYYY-MM-DD)", required=True)
        .add_string("item_condition", "Current item condition", required=False)
        .add_boolean("has_receipt", "Whether customer has receipt", required=False)
        .add_boolean("is_member", "Whether customer is loyalty member", required=False),
    output_schema=ActionOutputSchema(description="Return policy check result")
        .add_boolean("returnable", "Whether item can be returned")
        .add_number("return_window_days", "Return window in days")
        .add_number("days_remaining", "Days remaining in return window")
        .add_number("restocking_fee_pct", "Restocking fee percentage")
        .add_string("refund_method", "How refund will be issued")
        .add_array("requirements", "Requirements for return")
        .add_array("exceptions", "Applicable exceptions or restrictions")
))
def return_policy_check(
    sku: str,
    purchase_date: str,
    category: str = None,
    item_condition: str = None,
    has_receipt: bool = True,
    is_member: bool = False
) -> dict:
    """
    Check return policy for an item

    Args:
        sku: Item SKU
        purchase_date: Purchase date
        category: Item category
        item_condition: Current condition
        has_receipt: Has receipt
        is_member: Loyalty member

    Returns:
        Return policy details
    """
    # Get policy for category
    policy = RETURN_POLICIES.get(category.lower() if category else "default", RETURN_POLICIES["default"])

    # Extended return window for members
    return_window = policy["return_window_days"]
    if is_member:
        return_window = int(return_window * 1.5)  # 50% longer for members

    # Calculate days since purchase
    try:
        purchase = datetime.strptime(purchase_date, '%Y-%m-%d')
        days_since = (datetime.now() - purchase).days
        days_remaining = max(0, return_window - days_since)
    except Exception:
        days_since = 0
        days_remaining = return_window

    # Determine if returnable
    returnable = True
    requirements = []
    exceptions = []

    # Check return window
    if days_since > return_window:
        returnable = False
        exceptions.append(f"Return window of {return_window} days has expired")

    # Check receipt requirement
    if policy["receipt_required"] and not has_receipt:
        if is_member:
            requirements.append("Receipt not required for members - purchase can be looked up")
        else:
            returnable = False
            exceptions.append("Receipt required for non-members")

    # Check condition
    if item_condition:
        condition_lower = item_condition.lower()
        if "damaged" in condition_lower:
            returnable = False
            exceptions.append("Item damaged by customer - not eligible for return")
        elif "opened" in condition_lower and policy["condition_required"] == "unopened_or_like_new":
            policy["restocking_fee_pct"] = max(policy["restocking_fee_pct"], 15)
            requirements.append("Opened items subject to restocking fee")

    # Add standard requirements
    if policy["condition_required"]:
        requirements.append(f"Item must be in {policy['condition_required'].replace('_', ' ')} condition")
    requirements.append("Original packaging preferred")
    requirements.append("All accessories and manuals must be included")

    # Determine refund method
    if has_receipt:
        refund_method = "original_payment"
    elif is_member:
        refund_method = "store_credit"
    else:
        refund_method = "store_credit_lowest_price"

    return {
        "sku": sku,
        "category": category or "general",
        "returnable": returnable,
        "return_window_days": return_window,
        "days_since_purchase": days_since,
        "days_remaining": days_remaining,
        "restocking_fee_pct": policy["restocking_fee_pct"],
        "restocking_fee_waived": is_member and policy["restocking_fee_pct"] > 0,
        "refund_method": refund_method,
        "requirements": requirements,
        "exceptions": exceptions,
        "member_benefits_applied": is_member,
        "policy_version": "2024.1",
        "check_date": datetime.now().isoformat()
    }


class ReturnPolicyAction(ApexActionBase):
    """Return Policy Check Action (class-based)"""

    name = "return_policy_check"
    description = "Check return policies and eligibility"
    category = "returns"
    industry = "retail"

    def execute(self, **kwargs) -> dict:
        return return_policy_check(**kwargs)


def handler(event, context):
    """Lambda entry point"""
    return return_policy_check(**event)
