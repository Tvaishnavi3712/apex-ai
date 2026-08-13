"""
Apex PO Bot - AgentCore Agent for purchase order processing
"""
import json
import boto3
from strands import Agent, tool
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

SYSTEM_PROMPT = """You are POBot, an AI assistant for purchase order processing in manufacturing operations.

Your capabilities:
1. Process incoming purchase orders
2. Validate product codes and quantities
3. Check inventory availability
4. Route orders for fulfillment
5. Generate shipping documents

When processing a PO:
- Extract order details: PO number, customer, items, quantities, ship dates
- Validate against product catalog
- Check inventory levels
- Calculate lead times
- Flag rush orders or exceptions

Be precise with quantities and dates. Prioritize accuracy."""


@tool
def extract_purchase_order(s3_uri: str) -> dict:
    """
    Extract data from a purchase order document using BDA.

    Args:
        s3_uri: S3 URI of the purchase order document

    Returns:
        Extracted PO data including items, quantities, dates
    """
    return {
        "status": "processing",
        "message": "Purchase order extraction started"
    }


@tool
def validate_product_codes(product_codes: list) -> dict:
    """
    Validate product codes against the product catalog.

    Args:
        product_codes: List of product codes/SKUs to validate

    Returns:
        Validation results for each product code
    """
    valid_products = {
        "SKU-001": {"name": "Widget A", "unit_price": 25.00},
        "SKU-002": {"name": "Widget B", "unit_price": 35.00},
        "SKU-003": {"name": "Component X", "unit_price": 15.00}
    }

    results = []
    all_valid = True
    for code in product_codes:
        if code in valid_products:
            results.append({"product_code": code, "valid": True, **valid_products[code]})
        else:
            results.append({"product_code": code, "valid": False})
            all_valid = False

    return {"validation_results": results, "all_valid": all_valid}


@tool
def check_inventory(items: list) -> dict:
    """
    Check inventory availability for order items.

    Args:
        items: List of items with product_code and quantity

    Returns:
        Inventory availability for each item
    """
    inventory = {"SKU-001": 500, "SKU-002": 250, "SKU-003": 1000}

    results = []
    all_available = True
    for item in items:
        code = item.get("product_code")
        qty = item.get("quantity", 0)
        available = inventory.get(code, 0)
        results.append({
            "product_code": code,
            "requested": qty,
            "available": available,
            "sufficient": available >= qty
        })
        if available < qty:
            all_available = False

    return {"inventory_results": results, "all_available": all_available}


@tool
def calculate_lead_time(items: list, ship_date: str) -> dict:
    """
    Calculate lead times and verify ship date feasibility.

    Args:
        items: List of order items
        ship_date: Requested ship date (YYYY-MM-DD)

    Returns:
        Lead time analysis and feasibility
    """
    from datetime import datetime, timedelta
    today = datetime.now()
    requested = datetime.strptime(ship_date, "%Y-%m-%d")
    days_until_ship = (requested - today).days
    standard_lead_time = 5

    return {
        "requested_ship_date": ship_date,
        "days_until_ship": days_until_ship,
        "standard_lead_time": standard_lead_time,
        "feasible": days_until_ship >= standard_lead_time,
        "is_rush_order": days_until_ship < standard_lead_time
    }


@tool
def route_for_fulfillment(po_number: str, customer_id: str, priority: str = "standard") -> dict:
    """
    Route a purchase order for fulfillment.

    Args:
        po_number: The purchase order number
        customer_id: Customer ID
        priority: Order priority (standard, expedite, rush)

    Returns:
        Fulfillment routing confirmation
    """
    import uuid
    return {
        "routed": True,
        "fulfillment_id": f"FUL{uuid.uuid4().hex[:8].upper()}",
        "po_number": po_number,
        "priority": priority,
        "warehouse": "WH-EAST-01"
    }


# Create the agent
model = BedrockModel(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        extract_purchase_order,
        validate_product_codes,
        check_inventory,
        calculate_lead_time,
        route_for_fulfillment
    ]
)

# Create the AgentCore app
app = BedrockAgentCoreApp(agent=agent)
