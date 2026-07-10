"""
APEX ShopperBot - Agent Commerce AI Shopping Assistant
Deployed on AWS Bedrock AgentCore Runtime
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta
import uuid

app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """You are ShopperBot, an intelligent AI shopping assistant for Agent Commerce.

Your capabilities:
1. Product Search - Find products by category, price, brand, ratings
2. Price Comparison - Compare same product across retailers
3. Cart Management - Add/remove items, view cart
4. Checkout - Process orders
5. Price Tracking - Set alerts for price drops

RESPONSE FORMAT - Use this clean, compact style:

For product listings, use this format:
```
┌─────────────────────────────────────────────────────┐
│  BEST BUY                              BEST PRICE  │
│  $649.99 (Save $150 - 19% off)                     │
│  ★ 4.5/5 (2,847 reviews) • In Stock                │
│  Samsung 65" Crystal UHD 4K Smart TV               │
│  Specs: 65" 4K UHD, HDR10+, Tizen Smart Platform   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  WALMART                                           │
│  $678.00 (Save $122 - 15% off)                     │
│  ★ 4.4/5 (892 reviews) • In Stock                  │
│  Samsung 65" Crystal UHD 4K Smart TV               │
│  Specs: 65" 4K UHD, HDR10+, Tizen Smart Platform   │
└─────────────────────────────────────────────────────┘
```

Key formatting rules:
- Put RETAILER NAME in caps at the top of each card
- Mark the lowest price with "BEST PRICE" label
- Show the dollar savings AND percentage
- Use ★ for ratings
- Keep it compact and scannable
- Always sort by price (lowest first)

Be conversational but concise. Focus on helping users find the best deal quickly.
"""

# Simulated product database with retailer information
PRODUCT_CATALOG = [
    {
        "product_id": "TV-SAM-65-001",
        "product_name": "Samsung 65\" Crystal UHD 4K Smart TV",
        "brand": "Samsung",
        "category": "Electronics",
        "subcategory": "Televisions",
        "base_price": 799.99,
        "sale_price": 649.99,
        "discount_percentage": 19,
        "rating": 4.5,
        "review_count": 2847,
        "in_stock": True,
        "quantity_available": 45,
        "tags": ["4k", "smart tv", "65 inch", "samsung", "uhd"],
        "specs": "65\" 4K UHD, HDR10+, Tizen Smart Platform",
        "retailer": "Best Buy",
        "retailer_url": "https://www.bestbuy.com/samsung-65-crystal-uhd"
    },
    {
        "product_id": "TV-SAM-65-002",
        "product_name": "Samsung 65\" Crystal UHD 4K Smart TV",
        "brand": "Samsung",
        "category": "Electronics",
        "subcategory": "Televisions",
        "base_price": 799.99,
        "sale_price": 697.99,
        "discount_percentage": 13,
        "rating": 4.5,
        "review_count": 15234,
        "in_stock": True,
        "quantity_available": 120,
        "tags": ["4k", "smart tv", "65 inch", "samsung", "uhd"],
        "specs": "65\" 4K UHD, HDR10+, Tizen Smart Platform",
        "retailer": "Amazon",
        "retailer_url": "https://www.amazon.com/dp/B0SAMSUNG65"
    },
    {
        "product_id": "TV-SAM-65-003",
        "product_name": "Samsung 65\" Crystal UHD 4K Smart TV",
        "brand": "Samsung",
        "category": "Electronics",
        "subcategory": "Televisions",
        "base_price": 799.99,
        "sale_price": 678.00,
        "discount_percentage": 15,
        "rating": 4.4,
        "review_count": 892,
        "in_stock": True,
        "quantity_available": 35,
        "tags": ["4k", "smart tv", "65 inch", "samsung", "uhd"],
        "specs": "65\" 4K UHD, HDR10+, Tizen Smart Platform",
        "retailer": "Walmart",
        "retailer_url": "https://www.walmart.com/ip/samsung-65-4k-tv"
    },
    {
        "product_id": "TV-LG-65-002",
        "product_name": "LG 65\" OLED evo C3 Series 4K Smart TV",
        "brand": "LG",
        "category": "Electronics",
        "subcategory": "Televisions",
        "base_price": 1499.99,
        "sale_price": 1299.99,
        "discount_percentage": 13,
        "rating": 4.8,
        "review_count": 1523,
        "in_stock": True,
        "quantity_available": 12,
        "tags": ["4k", "oled", "smart tv", "65 inch", "lg", "premium"],
        "specs": "65\" OLED 4K, Dolby Vision, webOS 23",
        "retailer": "Best Buy",
        "retailer_url": "https://www.bestbuy.com/lg-65-oled-c3"
    },
    {
        "product_id": "TV-TCL-65-003",
        "product_name": "TCL 65\" Class S4 4K LED Smart TV",
        "brand": "TCL",
        "category": "Electronics",
        "subcategory": "Televisions",
        "base_price": 399.99,
        "sale_price": 349.99,
        "discount_percentage": 12,
        "rating": 4.2,
        "review_count": 5621,
        "in_stock": True,
        "quantity_available": 128,
        "tags": ["4k", "smart tv", "65 inch", "tcl", "budget", "led"],
        "specs": "65\" LED 4K, Google TV, HDR",
        "retailer": "Amazon",
        "retailer_url": "https://www.amazon.com/dp/B0TCL65S4"
    },
    {
        "product_id": "TV-SONY-65-004",
        "product_name": "Sony 65\" BRAVIA XR A80L OLED 4K TV",
        "brand": "Sony",
        "category": "Electronics",
        "subcategory": "Televisions",
        "base_price": 1999.99,
        "sale_price": 1799.99,
        "discount_percentage": 10,
        "rating": 4.9,
        "review_count": 892,
        "in_stock": True,
        "quantity_available": 8,
        "tags": ["4k", "oled", "smart tv", "65 inch", "sony", "premium", "bravia"],
        "specs": "65\" OLED 4K, Cognitive Processor XR, Google TV",
        "retailer": "Best Buy",
        "retailer_url": "https://www.bestbuy.com/sony-65-bravia-a80l"
    },
    {
        "product_id": "HP-LAP-15-001",
        "product_name": "HP 15.6\" Laptop - Intel Core i5",
        "brand": "HP",
        "category": "Electronics",
        "subcategory": "Laptops",
        "base_price": 699.99,
        "sale_price": 599.99,
        "discount_percentage": 14,
        "rating": 4.3,
        "review_count": 1245,
        "in_stock": True,
        "quantity_available": 67,
        "tags": ["laptop", "hp", "intel", "i5", "windows"],
        "specs": "15.6\" FHD, Intel i5, 16GB RAM, 512GB SSD",
        "retailer": "Amazon",
        "retailer_url": "https://www.amazon.com/dp/B0HP15LAPTOP"
    },
    {
        "product_id": "NIKE-AF1-001",
        "product_name": "Nike Air Force 1 '07",
        "brand": "Nike",
        "category": "Footwear",
        "subcategory": "Sneakers",
        "base_price": 115.00,
        "sale_price": 115.00,
        "discount_percentage": 0,
        "rating": 4.7,
        "review_count": 12453,
        "in_stock": True,
        "quantity_available": 234,
        "tags": ["nike", "sneakers", "air force 1", "white", "casual"],
        "specs": "Leather upper, rubber sole, classic design",
        "retailer": "Nike.com",
        "retailer_url": "https://www.nike.com/air-force-1-07"
    },
    {
        "product_id": "NIKE-AF1-002",
        "product_name": "Nike Air Force 1 '07",
        "brand": "Nike",
        "category": "Footwear",
        "subcategory": "Sneakers",
        "base_price": 115.00,
        "sale_price": 99.99,
        "discount_percentage": 13,
        "rating": 4.6,
        "review_count": 3421,
        "in_stock": True,
        "quantity_available": 45,
        "tags": ["nike", "sneakers", "air force 1", "white", "casual"],
        "specs": "Leather upper, rubber sole, classic design",
        "retailer": "Foot Locker",
        "retailer_url": "https://www.footlocker.com/nike-air-force-1"
    },
    {
        "product_id": "DYSON-V15-001",
        "product_name": "Dyson V15 Detect Cordless Vacuum",
        "brand": "Dyson",
        "category": "Home",
        "subcategory": "Vacuums",
        "base_price": 749.99,
        "sale_price": 649.99,
        "discount_percentage": 13,
        "rating": 4.6,
        "review_count": 3421,
        "in_stock": True,
        "quantity_available": 23,
        "tags": ["vacuum", "cordless", "dyson", "home"],
        "specs": "Laser detect, 60min runtime, LCD screen",
        "retailer": "Dyson.com",
        "retailer_url": "https://www.dyson.com/v15-detect"
    },
    {
        "product_id": "DYSON-V15-002",
        "product_name": "Dyson V15 Detect Cordless Vacuum",
        "brand": "Dyson",
        "category": "Home",
        "subcategory": "Vacuums",
        "base_price": 749.99,
        "sale_price": 599.99,
        "discount_percentage": 20,
        "rating": 4.5,
        "review_count": 8923,
        "in_stock": True,
        "quantity_available": 67,
        "tags": ["vacuum", "cordless", "dyson", "home"],
        "specs": "Laser detect, 60min runtime, LCD screen",
        "retailer": "Amazon",
        "retailer_url": "https://www.amazon.com/dp/B0DYSONV15"
    }
]

# Session storage for cart
USER_CARTS: Dict[str, Dict[str, Any]] = {}
PRICE_WATCHES: Dict[str, List[Dict[str, Any]]] = {}


@tool
def search_products(
    query: str,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None
) -> dict:
    """
    Search for products based on criteria.

    Args:
        query: Search terms (e.g., "65 inch tv", "laptop", "sneakers")
        max_price: Maximum price filter
        min_rating: Minimum rating filter (1-5)
        category: Category filter (Electronics, Footwear, Home)
        brand: Brand filter

    Returns:
        List of matching products with details
    """
    results = PRODUCT_CATALOG.copy()
    query_lower = query.lower()

    # Split query into words for flexible matching
    query_words = query_lower.split()

    # Search by query - match if ANY word matches
    def matches_product(p):
        searchable = (
            p["product_name"].lower() + " " +
            p.get("brand", "").lower() + " " +
            p.get("subcategory", "").lower() + " " +
            " ".join(p.get("tags", []))
        )
        return any(word in searchable for word in query_words)

    results = [p for p in results if matches_product(p)]

    # Apply filters
    if max_price:
        results = [p for p in results if p["sale_price"] <= max_price]
    if min_rating:
        results = [p for p in results if p["rating"] >= min_rating]
    if category:
        results = [p for p in results if category.lower() in p.get("category", "").lower()]
    if brand:
        results = [p for p in results if brand.lower() in p.get("brand", "").lower()]

    # Sort by price (lowest first) for best deals
    results.sort(key=lambda x: x["sale_price"])

    if not results:
        return {"found": 0, "message": "No products found matching your criteria", "products": []}

    # Format results with retailer info
    formatted = []
    for p in results[:5]:  # Top 5 results
        discount_text = f" (SAVE {p['discount_percentage']}%!)" if p['discount_percentage'] > 0 else ""
        formatted.append({
            "id": p["product_id"],
            "name": p["product_name"],
            "retailer": p.get("retailer", "Unknown"),
            "retailer_url": p.get("retailer_url", ""),
            "price": f"${p['sale_price']:.2f}{discount_text}",
            "original_price": f"${p['base_price']:.2f}" if p['discount_percentage'] > 0 else None,
            "rating": f"{p['rating']}/5 ({p['review_count']} reviews)",
            "specs": p["specs"],
            "in_stock": p["in_stock"]
        })

    return {
        "found": len(results),
        "showing": len(formatted),
        "products": formatted,
        "note": "Products sorted by lowest price first"
    }


@tool
def compare_products(product_ids: str) -> dict:
    """
    Compare multiple products side by side.

    Args:
        product_ids: Comma-separated product IDs to compare

    Returns:
        Comparison table with recommendation
    """
    ids = [pid.strip() for pid in product_ids.split(",")]
    products = [p for p in PRODUCT_CATALOG if p["product_id"] in ids]

    if not products:
        return {"error": "No products found with those IDs"}

    comparison = []
    for p in products:
        comparison.append({
            "name": p["product_name"],
            "price": p["sale_price"],
            "original_price": p["base_price"],
            "savings": p["base_price"] - p["sale_price"],
            "rating": p["rating"],
            "reviews": p["review_count"],
            "specs": p["specs"]
        })

    # Determine best value
    best_value = min(products, key=lambda x: x["sale_price"] / x["rating"])
    best_rated = max(products, key=lambda x: x["rating"])
    best_price = min(products, key=lambda x: x["sale_price"])

    return {
        "comparison": comparison,
        "recommendations": {
            "best_value": f"{best_value['product_name']} - Best price-to-rating ratio",
            "highest_rated": f"{best_rated['product_name']} - {best_rated['rating']}/5 stars",
            "lowest_price": f"{best_price['product_name']} - ${best_price['sale_price']:.2f}"
        }
    }


@tool
def add_to_cart(product_id: str, quantity: int = 1) -> dict:
    """
    Add a product to the shopping cart.

    Args:
        product_id: The product ID to add
        quantity: Number of items to add (default 1)

    Returns:
        Updated cart summary
    """
    user_id = "default_user"
    product = next((p for p in PRODUCT_CATALOG if p["product_id"] == product_id), None)

    if not product:
        return {"error": f"Product {product_id} not found"}

    if not product["in_stock"]:
        return {"error": f"{product['product_name']} is out of stock"}

    if user_id not in USER_CARTS:
        USER_CARTS[user_id] = {"items": [], "created_at": datetime.utcnow().isoformat()}

    cart = USER_CARTS[user_id]

    # Check if already in cart
    existing = next((item for item in cart["items"] if item["product_id"] == product_id), None)
    if existing:
        existing["quantity"] += quantity
    else:
        cart["items"].append({
            "product_id": product_id,
            "name": product["product_name"],
            "price": product["sale_price"],
            "quantity": quantity
        })

    # Calculate totals
    subtotal = sum(item["price"] * item["quantity"] for item in cart["items"])
    tax = subtotal * 0.08
    total = subtotal + tax

    return {
        "message": f"Added {quantity}x {product['product_name']} to cart",
        "cart_summary": {
            "items": len(cart["items"]),
            "total_quantity": sum(item["quantity"] for item in cart["items"]),
            "subtotal": f"${subtotal:.2f}",
            "tax": f"${tax:.2f}",
            "total": f"${total:.2f}"
        }
    }


@tool
def view_cart() -> dict:
    """
    View current shopping cart contents.

    Returns:
        Cart contents with totals
    """
    user_id = "default_user"
    cart = USER_CARTS.get(user_id, {"items": []})

    if not cart["items"]:
        return {"message": "Your cart is empty", "items": [], "total": "$0.00"}

    items = []
    subtotal = 0
    for item in cart["items"]:
        line_total = item["price"] * item["quantity"]
        subtotal += line_total
        items.append({
            "product": item["name"],
            "quantity": item["quantity"],
            "unit_price": f"${item['price']:.2f}",
            "line_total": f"${line_total:.2f}"
        })

    tax = subtotal * 0.08
    total = subtotal + tax

    return {
        "items": items,
        "subtotal": f"${subtotal:.2f}",
        "tax": f"${tax:.2f}",
        "total": f"${total:.2f}",
        "item_count": sum(item["quantity"] for item in cart["items"])
    }


@tool
def checkout(shipping_method: str = "standard") -> dict:
    """
    Process checkout and place order.

    Args:
        shipping_method: standard, express, or overnight

    Returns:
        Order confirmation
    """
    user_id = "default_user"
    cart = USER_CARTS.get(user_id, {"items": []})

    if not cart["items"]:
        return {"error": "Cart is empty. Add items before checkout."}

    # Calculate totals
    subtotal = sum(item["price"] * item["quantity"] for item in cart["items"])
    tax = subtotal * 0.08

    shipping_costs = {"standard": 5.99, "express": 14.99, "overnight": 29.99}
    shipping = shipping_costs.get(shipping_method, 5.99)

    delivery_days = {"standard": 5, "express": 2, "overnight": 1}
    est_delivery = (datetime.utcnow() + timedelta(days=delivery_days.get(shipping_method, 5))).strftime("%B %d, %Y")

    total = subtotal + tax + shipping

    # Generate order
    order_id = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Clear cart
    USER_CARTS[user_id] = {"items": []}

    return {
        "success": True,
        "order_id": order_id,
        "message": f"Order {order_id} placed successfully!",
        "order_summary": {
            "subtotal": f"${subtotal:.2f}",
            "tax": f"${tax:.2f}",
            "shipping": f"${shipping:.2f} ({shipping_method})",
            "total": f"${total:.2f}",
            "estimated_delivery": est_delivery
        },
        "next_steps": "You will receive a confirmation email shortly."
    }


@tool
def set_price_alert(product_id: str, target_price: float) -> dict:
    """
    Set a price alert for a product.

    Args:
        product_id: Product to watch
        target_price: Alert when price drops to this level

    Returns:
        Confirmation of price watch
    """
    user_id = "default_user"
    product = next((p for p in PRODUCT_CATALOG if p["product_id"] == product_id), None)

    if not product:
        return {"error": f"Product {product_id} not found"}

    if user_id not in PRICE_WATCHES:
        PRICE_WATCHES[user_id] = []

    watch = {
        "product_id": product_id,
        "product_name": product["product_name"],
        "current_price": product["sale_price"],
        "target_price": target_price,
        "created_at": datetime.utcnow().isoformat()
    }

    PRICE_WATCHES[user_id].append(watch)

    if product["sale_price"] <= target_price:
        return {
            "message": f"Great news! {product['product_name']} is already at ${product['sale_price']:.2f} - below your target of ${target_price:.2f}!",
            "recommendation": "Buy now to lock in this price!"
        }

    return {
        "message": f"Price alert set for {product['product_name']}",
        "current_price": f"${product['sale_price']:.2f}",
        "target_price": f"${target_price:.2f}",
        "difference": f"${product['sale_price'] - target_price:.2f} above target"
    }


@tool
def get_recommendations(category: str = "Electronics") -> dict:
    """
    Get product recommendations.

    Args:
        category: Category to get recommendations for

    Returns:
        Top recommended products
    """
    products = [p for p in PRODUCT_CATALOG if p["category"].lower() == category.lower()]

    if not products:
        products = PRODUCT_CATALOG

    # Sort by discount then rating
    deals = sorted(products, key=lambda x: x["discount_percentage"], reverse=True)[:3]
    top_rated = sorted(products, key=lambda x: x["rating"], reverse=True)[:3]

    return {
        "top_deals": [
            {
                "name": p["product_name"],
                "price": f"${p['sale_price']:.2f}",
                "discount": f"{p['discount_percentage']}% off"
            } for p in deals if p["discount_percentage"] > 0
        ],
        "top_rated": [
            {
                "name": p["product_name"],
                "rating": f"{p['rating']}/5",
                "price": f"${p['sale_price']:.2f}"
            } for p in top_rated
        ]
    }


# Initialize the model - using Amazon Nova Pro (works with AgentCore)
model = BedrockModel(
    model_id="us.amazon.nova-pro-v1:0",
    region_name="us-east-1"
)

# Create the agent with all tools
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        search_products,
        compare_products,
        add_to_cart,
        view_cart,
        checkout,
        set_price_alert,
        get_recommendations
    ]
)


def clean_response(response) -> str:
    """Extract clean text from agent response, removing thinking tags."""
    import re

    # Handle different response formats
    if hasattr(response, 'message'):
        msg = response.message
    else:
        msg = response

    # If it's a dict with content
    if isinstance(msg, dict):
        if 'content' in msg:
            content = msg['content']
            if isinstance(content, list):
                # Extract text from content blocks
                texts = []
                for block in content:
                    if isinstance(block, dict) and 'text' in block:
                        texts.append(block['text'])
                    elif isinstance(block, str):
                        texts.append(block)
                text = '\n'.join(texts)
            else:
                text = str(content)
        else:
            text = str(msg)
    elif isinstance(msg, str):
        text = msg
    else:
        text = str(msg)

    # Remove <thinking>...</thinking> blocks
    text = re.sub(r'<thinking>.*?</thinking>\s*', '', text, flags=re.DOTALL)

    # Clean up extra whitespace
    text = text.strip()

    return text


@app.entrypoint
def invoke(payload):
    """AgentCore entrypoint for ShopperBot."""
    user_message = payload.get("prompt", "Hello")
    result = agent(user_message)

    # Clean the response to remove thinking tags and format nicely
    clean_text = clean_response(result)

    return {"response": clean_text}


if __name__ == "__main__":
    app.run()
