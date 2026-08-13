"""
Price Tracking Action Handler
Tracks prices and triggers alerts for Agent Commerce
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import uuid

# In-memory price tracking storage
PRICE_WATCHES: Dict[str, List[Dict[str, Any]]] = {}
PRICE_HISTORY: Dict[str, List[Dict[str, Any]]] = {
    "TV-SAM-65-001": [
        {"date": "2024-01-01", "price": 799.99},
        {"date": "2024-01-15", "price": 749.99},
        {"date": "2024-02-01", "price": 699.99},
        {"date": "2024-02-15", "price": 649.99},
    ],
    "TV-LG-65-002": [
        {"date": "2024-01-01", "price": 1599.99},
        {"date": "2024-01-15", "price": 1499.99},
        {"date": "2024-02-01", "price": 1399.99},
        {"date": "2024-02-15", "price": 1299.99},
    ],
    "TV-TCL-65-003": [
        {"date": "2024-01-01", "price": 449.99},
        {"date": "2024-01-15", "price": 399.99},
        {"date": "2024-02-01", "price": 379.99},
        {"date": "2024-02-15", "price": 349.99},
    ]
}


def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Price Tracking Action Handler

    Operations:
        - watch: Set up price watch for a product
        - check: Check current price against target
        - history: Get price history for a product
        - list: List all active price watches
        - remove: Remove a price watch

    Input:
        user_id: User identifier
        operation: watch|check|history|list|remove
        product_id: Product ID
        target_price: Target price for alerts
        product_name: Product name (for watch)
        current_price: Current price (for watch)
    """
    user_id = event.get("user_id", "default_user")
    operation = event.get("operation", "list")
    product_id = event.get("product_id")

    if user_id not in PRICE_WATCHES:
        PRICE_WATCHES[user_id] = []

    if operation == "watch":
        target_price = event.get("target_price")
        product_name = event.get("product_name", "Unknown Product")
        current_price = event.get("current_price", 0)

        if not target_price or not product_id:
            return {
                "success": False,
                "error": "product_id and target_price are required"
            }

        # Check if already watching
        existing = next(
            (w for w in PRICE_WATCHES[user_id] if w["product_id"] == product_id),
            None
        )

        if existing:
            existing["target_price"] = target_price
            existing["updated_at"] = datetime.utcnow().isoformat()
            message = f"Updated price watch for {product_name}"
        else:
            watch = {
                "watch_id": str(uuid.uuid4()),
                "product_id": product_id,
                "product_name": product_name,
                "current_price": current_price,
                "target_price": target_price,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            PRICE_WATCHES[user_id].append(watch)
            message = f"Now watching {product_name} for price drop to ${target_price}"

        return {
            "success": True,
            "operation": "watch",
            "message": message,
            "watches": PRICE_WATCHES[user_id]
        }

    elif operation == "check":
        current_price = event.get("current_price", 0)

        watch = next(
            (w for w in PRICE_WATCHES[user_id] if w["product_id"] == product_id),
            None
        )

        if not watch:
            return {
                "success": False,
                "error": f"No price watch found for product {product_id}"
            }

        target_met = current_price <= watch["target_price"]

        return {
            "success": True,
            "operation": "check",
            "product_id": product_id,
            "product_name": watch["product_name"],
            "current_price": current_price,
            "target_price": watch["target_price"],
            "target_met": target_met,
            "price_difference": round(current_price - watch["target_price"], 2),
            "recommendation": "BUY NOW!" if target_met else f"Wait - ${round(current_price - watch['target_price'], 2)} above target"
        }

    elif operation == "history":
        history = PRICE_HISTORY.get(product_id, [])

        if not history:
            return {
                "success": True,
                "operation": "history",
                "product_id": product_id,
                "history": [],
                "message": "No price history available"
            }

        # Calculate trends
        if len(history) >= 2:
            price_change = history[-1]["price"] - history[0]["price"]
            trend = "decreasing" if price_change < 0 else "increasing" if price_change > 0 else "stable"
            lowest = min(h["price"] for h in history)
            highest = max(h["price"] for h in history)
        else:
            trend = "unknown"
            lowest = highest = history[0]["price"] if history else 0

        return {
            "success": True,
            "operation": "history",
            "product_id": product_id,
            "history": history,
            "analysis": {
                "trend": trend,
                "lowest_price": lowest,
                "highest_price": highest,
                "current_price": history[-1]["price"] if history else 0,
                "recommendation": "Good time to buy - near lowest price" if history and history[-1]["price"] <= lowest * 1.1 else "Consider waiting for better deal"
            }
        }

    elif operation == "remove":
        PRICE_WATCHES[user_id] = [
            w for w in PRICE_WATCHES[user_id] if w["product_id"] != product_id
        ]

        return {
            "success": True,
            "operation": "remove",
            "message": f"Removed price watch for {product_id}",
            "watches": PRICE_WATCHES[user_id]
        }

    else:  # list
        return {
            "success": True,
            "operation": "list",
            "watches": PRICE_WATCHES[user_id],
            "count": len(PRICE_WATCHES[user_id])
        }
