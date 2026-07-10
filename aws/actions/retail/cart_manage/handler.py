"""
Cart Management Action Handler
Manages shopping cart operations for Agent Commerce
"""
from typing import Dict, Any, List
import uuid
from datetime import datetime

# In-memory cart storage (would be DynamoDB in production)
CARTS: Dict[str, Dict[str, Any]] = {}


def get_or_create_cart(user_id: str) -> Dict[str, Any]:
    """Get existing cart or create new one for user."""
    if user_id not in CARTS:
        CARTS[user_id] = {
            "cart_id": str(uuid.uuid4()),
            "user_id": user_id,
            "items": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    return CARTS[user_id]


def calculate_cart_totals(cart: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate cart totals."""
    subtotal = sum(item["price"] * item["quantity"] for item in cart["items"])
    discount_total = sum(
        (item.get("original_price", item["price"]) - item["price"]) * item["quantity"]
        for item in cart["items"]
    )
    tax_rate = 0.08  # 8% tax
    tax = subtotal * tax_rate
    total = subtotal + tax

    return {
        "subtotal": round(subtotal, 2),
        "discount_total": round(discount_total, 2),
        "tax_rate": tax_rate,
        "tax": round(tax, 2),
        "total": round(total, 2),
        "item_count": sum(item["quantity"] for item in cart["items"])
    }


def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Cart Management Action Handler

    Operations:
        - add: Add item to cart
        - remove: Remove item from cart
        - update: Update item quantity
        - get: Get cart contents
        - clear: Clear entire cart

    Input:
        user_id: User identifier
        operation: add|remove|update|get|clear
        product_id: Product ID (for add/remove/update)
        quantity: Quantity (for add/update)
        product_name: Product name (for add)
        price: Product price (for add)
        original_price: Original price before discount (for add)
    """
    user_id = event.get("user_id", "default_user")
    operation = event.get("operation", "get")

    cart = get_or_create_cart(user_id)

    if operation == "add":
        product_id = event.get("product_id")
        quantity = event.get("quantity", 1)
        product_name = event.get("product_name", "Unknown Product")
        price = event.get("price", 0)
        original_price = event.get("original_price", price)

        # Check if product already in cart
        existing_item = next(
            (item for item in cart["items"] if item["product_id"] == product_id),
            None
        )

        if existing_item:
            existing_item["quantity"] += quantity
        else:
            cart["items"].append({
                "product_id": product_id,
                "product_name": product_name,
                "price": price,
                "original_price": original_price,
                "quantity": quantity,
                "added_at": datetime.utcnow().isoformat()
            })

        cart["updated_at"] = datetime.utcnow().isoformat()

        return {
            "success": True,
            "operation": "add",
            "message": f"Added {quantity}x {product_name} to cart",
            "cart": cart,
            "totals": calculate_cart_totals(cart)
        }

    elif operation == "remove":
        product_id = event.get("product_id")
        cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
        cart["updated_at"] = datetime.utcnow().isoformat()

        return {
            "success": True,
            "operation": "remove",
            "message": f"Removed product {product_id} from cart",
            "cart": cart,
            "totals": calculate_cart_totals(cart)
        }

    elif operation == "update":
        product_id = event.get("product_id")
        quantity = event.get("quantity", 1)

        for item in cart["items"]:
            if item["product_id"] == product_id:
                if quantity <= 0:
                    cart["items"].remove(item)
                else:
                    item["quantity"] = quantity
                break

        cart["updated_at"] = datetime.utcnow().isoformat()

        return {
            "success": True,
            "operation": "update",
            "message": f"Updated quantity for {product_id}",
            "cart": cart,
            "totals": calculate_cart_totals(cart)
        }

    elif operation == "clear":
        cart["items"] = []
        cart["updated_at"] = datetime.utcnow().isoformat()

        return {
            "success": True,
            "operation": "clear",
            "message": "Cart cleared",
            "cart": cart,
            "totals": calculate_cart_totals(cart)
        }

    else:  # get
        return {
            "success": True,
            "operation": "get",
            "cart": cart,
            "totals": calculate_cart_totals(cart)
        }
