"""
Product Search Action Handler
Searches product catalog based on criteria for Agent Commerce
"""
from typing import Dict, Any, List, Optional
import json


# Simulated product database for demo
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
        "specifications": [
            {"spec_name": "Screen Size", "spec_value": "65 inches"},
            {"spec_name": "Resolution", "spec_value": "4K UHD (3840 x 2160)"},
            {"spec_name": "HDR", "spec_value": "HDR10+"},
            {"spec_name": "Smart Platform", "spec_value": "Tizen"}
        ]
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
        "specifications": [
            {"spec_name": "Screen Size", "spec_value": "65 inches"},
            {"spec_name": "Resolution", "spec_value": "4K UHD (3840 x 2160)"},
            {"spec_name": "Display Type", "spec_value": "OLED"},
            {"spec_name": "Smart Platform", "spec_value": "webOS 23"}
        ]
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
        "specifications": [
            {"spec_name": "Screen Size", "spec_value": "65 inches"},
            {"spec_name": "Resolution", "spec_value": "4K UHD (3840 x 2160)"},
            {"spec_name": "Display Type", "spec_value": "LED"},
            {"spec_name": "Smart Platform", "spec_value": "Google TV"}
        ]
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
        "specifications": [
            {"spec_name": "Screen Size", "spec_value": "65 inches"},
            {"spec_name": "Resolution", "spec_value": "4K UHD (3840 x 2160)"},
            {"spec_name": "Display Type", "spec_value": "OLED"},
            {"spec_name": "Processor", "spec_value": "Cognitive Processor XR"}
        ]
    },
    {
        "product_id": "HP-DY-15-001",
        "product_name": "HP 15.6\" Laptop - Intel Core i5, 16GB RAM, 512GB SSD",
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
        "tags": ["laptop", "hp", "intel", "i5", "16gb", "512gb", "windows"],
        "specifications": [
            {"spec_name": "Screen Size", "spec_value": "15.6 inches"},
            {"spec_name": "Processor", "spec_value": "Intel Core i5-1235U"},
            {"spec_name": "RAM", "spec_value": "16GB DDR4"},
            {"spec_name": "Storage", "spec_value": "512GB SSD"}
        ]
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
        "specifications": [
            {"spec_name": "Material", "spec_value": "Leather"},
            {"spec_name": "Closure", "spec_value": "Lace-up"},
            {"spec_name": "Sole", "spec_value": "Rubber"}
        ]
    }
]


def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    in_stock_only: bool = True,
    sort_by: str = "relevance",
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search products based on various criteria.
    """
    results = PRODUCT_CATALOG.copy()

    # Filter by query (search in name, tags, description)
    if query:
        query_lower = query.lower()
        results = [
            p for p in results
            if query_lower in p["product_name"].lower()
            or any(query_lower in tag for tag in p.get("tags", []))
            or query_lower in p.get("brand", "").lower()
            or query_lower in p.get("category", "").lower()
        ]

    # Filter by category
    if category:
        results = [p for p in results if category.lower() in p.get("category", "").lower()]

    # Filter by brand
    if brand:
        results = [p for p in results if brand.lower() in p.get("brand", "").lower()]

    # Filter by price range
    if min_price is not None:
        results = [p for p in results if p.get("sale_price", p.get("base_price", 0)) >= min_price]
    if max_price is not None:
        results = [p for p in results if p.get("sale_price", p.get("base_price", 0)) <= max_price]

    # Filter by rating
    if min_rating is not None:
        results = [p for p in results if p.get("rating", 0) >= min_rating]

    # Filter by stock
    if in_stock_only:
        results = [p for p in results if p.get("in_stock", False)]

    # Sort results
    if sort_by == "price_low":
        results.sort(key=lambda x: x.get("sale_price", x.get("base_price", 0)))
    elif sort_by == "price_high":
        results.sort(key=lambda x: x.get("sale_price", x.get("base_price", 0)), reverse=True)
    elif sort_by == "rating":
        results.sort(key=lambda x: x.get("rating", 0), reverse=True)
    elif sort_by == "reviews":
        results.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    elif sort_by == "discount":
        results.sort(key=lambda x: x.get("discount_percentage", 0), reverse=True)

    return results[:limit]


def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Product Search Action Handler

    Input:
        query: Search query string
        category: Product category filter
        brand: Brand filter
        min_price: Minimum price
        max_price: Maximum price
        min_rating: Minimum rating (1-5)
        in_stock_only: Only show in-stock items
        sort_by: Sort order (relevance, price_low, price_high, rating, reviews, discount)
        limit: Max results to return

    Output:
        products: List of matching products
        total_count: Number of matches
        filters_applied: Summary of applied filters
    """
    # Extract parameters
    query = event.get("query")
    category = event.get("category")
    brand = event.get("brand")
    min_price = event.get("min_price")
    max_price = event.get("max_price")
    min_rating = event.get("min_rating")
    in_stock_only = event.get("in_stock_only", True)
    sort_by = event.get("sort_by", "relevance")
    limit = event.get("limit", 10)

    # Search products
    products = search_products(
        query=query,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        limit=limit
    )

    # Build filters summary
    filters_applied = {}
    if query:
        filters_applied["query"] = query
    if category:
        filters_applied["category"] = category
    if brand:
        filters_applied["brand"] = brand
    if min_price:
        filters_applied["min_price"] = min_price
    if max_price:
        filters_applied["max_price"] = max_price
    if min_rating:
        filters_applied["min_rating"] = min_rating
    filters_applied["in_stock_only"] = in_stock_only
    filters_applied["sort_by"] = sort_by

    return {
        "success": True,
        "products": products,
        "total_count": len(products),
        "filters_applied": filters_applied
    }


if __name__ == "__main__":
    # Test the handler
    test_event = {
        "query": "65 inch tv",
        "max_price": 800,
        "min_rating": 4.0,
        "sort_by": "rating"
    }
    result = handler(test_event)
    print(json.dumps(result, indent=2))
