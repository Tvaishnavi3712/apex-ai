"""
Receipt Generator
Generate synthetic receipt documents for testing BDA extraction
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import os

# Sample merchant data
MERCHANTS = {
    "restaurants": [
        {"name": "The Capital Grille", "category": "Restaurant"},
        {"name": "Morton's Steakhouse", "category": "Restaurant"},
        {"name": "Olive Garden", "category": "Restaurant"},
        {"name": "Chipotle Mexican Grill", "category": "Restaurant"},
        {"name": "Panera Bread", "category": "Restaurant"},
        {"name": "Starbucks", "category": "Restaurant"},
    ],
    "hotels": [
        {"name": "Marriott Hotel", "category": "Hotel"},
        {"name": "Hilton Garden Inn", "category": "Hotel"},
        {"name": "Hyatt Regency", "category": "Hotel"},
        {"name": "Holiday Inn Express", "category": "Hotel"},
    ],
    "office_supplies": [
        {"name": "Staples", "category": "Office Supplies"},
        {"name": "Office Depot", "category": "Office Supplies"},
        {"name": "Best Buy", "category": "Retail"},
    ],
    "transportation": [
        {"name": "Uber", "category": "Ground Transportation"},
        {"name": "Lyft", "category": "Ground Transportation"},
        {"name": "Enterprise Rent-A-Car", "category": "Ground Transportation"},
        {"name": "Airport Parking", "category": "Parking"},
    ],
    "gas": [
        {"name": "Shell", "category": "Gas Station"},
        {"name": "Chevron", "category": "Gas Station"},
        {"name": "BP", "category": "Gas Station"},
    ]
}

ADDRESSES = [
    {"street": "100 Congress Ave", "city": "Austin", "state": "TX", "zip": "78701"},
    {"street": "200 Pike St", "city": "Seattle", "state": "WA", "zip": "98101"},
    {"street": "300 Michigan Ave", "city": "Chicago", "state": "IL", "zip": "60601"},
    {"street": "400 Market St", "city": "San Francisco", "state": "CA", "zip": "94102"},
    {"street": "500 Peachtree St", "city": "Atlanta", "state": "GA", "zip": "30308"},
]

MENU_ITEMS = {
    "restaurant": [
        ("Appetizer - Calamari", 14.99),
        ("Caesar Salad", 12.99),
        ("Grilled Salmon", 28.99),
        ("Filet Mignon", 45.99),
        ("Chicken Parmesan", 22.99),
        ("Pasta Primavera", 18.99),
        ("Dessert - Cheesecake", 9.99),
        ("Coffee", 3.99),
        ("Soft Drink", 2.99),
        ("Iced Tea", 2.99),
    ],
    "coffee": [
        ("Latte - Grande", 5.75),
        ("Cappuccino", 4.95),
        ("Drip Coffee - Large", 2.95),
        ("Espresso", 3.25),
        ("Muffin", 3.45),
        ("Croissant", 3.95),
    ],
    "office": [
        ("Copy Paper - Case", 49.99),
        ("Ink Cartridge - Black", 34.99),
        ("Ink Cartridge - Color", 44.99),
        ("Pens - 12 Pack", 12.99),
        ("Notebooks - 3 Pack", 15.99),
        ("Stapler", 18.99),
        ("Folders - 25 Pack", 8.99),
    ]
}


@dataclass
class ReceiptItem:
    description: str
    quantity: int
    unit_price: float
    amount: float


@dataclass
class Receipt:
    merchant_name: str
    merchant_category: str
    merchant_address: Dict[str, str]
    merchant_phone: str
    transaction_date: str
    transaction_time: str
    receipt_number: str
    items: List[ReceiptItem]
    subtotal: float
    tax_rate: float
    tax_amount: float
    tip: float
    total: float
    payment_method: str
    card_type: str
    last_four: str


def generate_phone() -> str:
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def generate_receipt_number() -> str:
    return f"{random.randint(1000, 9999)}-{random.randint(100000, 999999)}"


def generate_receipt_items(category: str) -> List[ReceiptItem]:
    """Generate items based on merchant category"""

    if category == "Restaurant":
        menu = MENU_ITEMS["restaurant"]
        count = random.randint(2, 6)
    elif category in ["Office Supplies", "Retail"]:
        menu = MENU_ITEMS["office"]
        count = random.randint(1, 5)
    else:
        menu = MENU_ITEMS["coffee"]
        count = random.randint(1, 3)

    items = []
    selected = random.sample(menu, min(count, len(menu)))

    for desc, price in selected:
        qty = random.randint(1, 3) if "Coffee" in desc or "Drink" in desc else 1
        amount = round(price * qty, 2)
        items.append(ReceiptItem(
            description=desc,
            quantity=qty,
            unit_price=price,
            amount=amount
        ))

    return items


def generate_receipt(
    merchant_type: str = None,
    transaction_date: datetime = None
) -> Receipt:
    """Generate a complete synthetic receipt"""

    # Select merchant
    if merchant_type is None:
        merchant_type = random.choice(list(MERCHANTS.keys()))

    merchant = random.choice(MERCHANTS[merchant_type])
    address = random.choice(ADDRESSES)

    # Date/time
    if transaction_date is None:
        transaction_date = datetime.now() - timedelta(days=random.randint(0, 30))

    tx_time = f"{random.randint(7, 21):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"

    # Items
    items = generate_receipt_items(merchant["category"])

    # Totals
    subtotal = sum(item.amount for item in items)
    tax_rate = random.choice([0.0625, 0.07, 0.0825])
    tax_amount = round(subtotal * tax_rate, 2)

    # Tip for restaurants
    tip = 0
    if merchant["category"] == "Restaurant" and random.random() > 0.2:
        tip_rate = random.choice([0.15, 0.18, 0.20, 0.22])
        tip = round(subtotal * tip_rate, 2)

    total = round(subtotal + tax_amount + tip, 2)

    # Payment
    payment_method = random.choice(["Credit Card", "Debit Card"])
    card_type = random.choice(["Visa", "MasterCard", "Amex"])
    last_four = f"{random.randint(1000, 9999)}"

    return Receipt(
        merchant_name=merchant["name"],
        merchant_category=merchant["category"],
        merchant_address=address,
        merchant_phone=generate_phone(),
        transaction_date=transaction_date.strftime("%Y-%m-%d"),
        transaction_time=tx_time,
        receipt_number=generate_receipt_number(),
        items=items,
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        tip=tip,
        total=total,
        payment_method=payment_method,
        card_type=card_type,
        last_four=last_four
    )


def receipt_to_html(receipt: Receipt) -> str:
    """Convert receipt to HTML (thermal receipt style)"""

    items_html = ""
    for item in receipt.items:
        items_html += f"""
        <tr>
            <td>{item.description}</td>
            <td class="qty">{item.quantity}</td>
            <td class="amount">${item.amount:.2f}</td>
        </tr>
        """

    tip_row = ""
    if receipt.tip > 0:
        tip_row = f"""
        <tr>
            <td colspan="2">Tip:</td>
            <td class="amount">${receipt.tip:.2f}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Receipt - {receipt.receipt_number}</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            width: 300px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ccc;
        }}
        .header {{
            text-align: center;
            border-bottom: 1px dashed #333;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }}
        .merchant-name {{
            font-size: 18px;
            font-weight: bold;
        }}
        .address {{
            font-size: 12px;
            color: #666;
        }}
        table {{
            width: 100%;
            font-size: 12px;
        }}
        td {{
            padding: 3px 0;
        }}
        .qty {{
            text-align: center;
            width: 30px;
        }}
        .amount {{
            text-align: right;
            width: 60px;
        }}
        .divider {{
            border-top: 1px dashed #333;
            margin: 10px 0;
        }}
        .totals td {{
            font-size: 14px;
        }}
        .total-row {{
            font-weight: bold;
            font-size: 16px;
        }}
        .payment-info {{
            margin-top: 15px;
            font-size: 12px;
            text-align: center;
        }}
        .footer {{
            margin-top: 20px;
            text-align: center;
            font-size: 11px;
            color: #666;
        }}
        .barcode {{
            text-align: center;
            font-family: 'Libre Barcode 39', cursive;
            font-size: 40px;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="merchant-name">{receipt.merchant_name}</div>
        <div class="address">
            {receipt.merchant_address['street']}<br>
            {receipt.merchant_address['city']}, {receipt.merchant_address['state']} {receipt.merchant_address['zip']}<br>
            {receipt.merchant_phone}
        </div>
    </div>

    <div style="font-size: 12px; margin-bottom: 10px;">
        Date: {receipt.transaction_date}<br>
        Time: {receipt.transaction_time}<br>
        Receipt #: {receipt.receipt_number}
    </div>

    <div class="divider"></div>

    <table>
        <thead>
            <tr>
                <td>Item</td>
                <td class="qty">Qty</td>
                <td class="amount">Price</td>
            </tr>
        </thead>
        <tbody>
            {items_html}
        </tbody>
    </table>

    <div class="divider"></div>

    <table class="totals">
        <tr>
            <td colspan="2">Subtotal:</td>
            <td class="amount">${receipt.subtotal:.2f}</td>
        </tr>
        <tr>
            <td colspan="2">Tax ({receipt.tax_rate * 100:.2f}%):</td>
            <td class="amount">${receipt.tax_amount:.2f}</td>
        </tr>
        {tip_row}
        <tr class="total-row">
            <td colspan="2">TOTAL:</td>
            <td class="amount">${receipt.total:.2f}</td>
        </tr>
    </table>

    <div class="payment-info">
        <strong>{receipt.payment_method}</strong><br>
        {receipt.card_type} ****{receipt.last_four}<br>
        APPROVED
    </div>

    <div class="footer">
        Thank you for your business!<br>
        Please retain for your records
    </div>

    <div class="barcode">
        *{receipt.receipt_number}*
    </div>
</body>
</html>
    """
    return html


def receipt_to_json(receipt: Receipt) -> Dict[str, Any]:
    """Convert receipt to JSON (ground truth)"""
    return {
        "merchant": {
            "name": receipt.merchant_name,
            "category": receipt.merchant_category,
            "address": receipt.merchant_address,
            "phone": receipt.merchant_phone
        },
        "transaction": {
            "date": receipt.transaction_date,
            "time": receipt.transaction_time,
            "receipt_number": receipt.receipt_number
        },
        "line_items": [asdict(item) for item in receipt.items],
        "totals": {
            "subtotal": receipt.subtotal,
            "tax_rate": receipt.tax_rate,
            "tax_amount": receipt.tax_amount,
            "tip": receipt.tip,
            "total": receipt.total
        },
        "payment": {
            "method": receipt.payment_method,
            "card_type": receipt.card_type,
            "last_four": receipt.last_four
        }
    }


def generate_receipt_batch(count: int, output_dir: str) -> List[Dict[str, Any]]:
    """Generate a batch of receipts"""

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)

    manifest = []

    for i in range(count):
        receipt = generate_receipt()
        receipt_id = receipt.receipt_number.replace("-", "_")

        # Save HTML
        html_path = os.path.join(output_dir, "html", f"{receipt_id}.html")
        with open(html_path, "w") as f:
            f.write(receipt_to_html(receipt))

        # Save JSON
        json_path = os.path.join(output_dir, "json", f"{receipt_id}.json")
        with open(json_path, "w") as f:
            json.dump(receipt_to_json(receipt), f, indent=2)

        manifest.append({
            "receipt_number": receipt.receipt_number,
            "html_file": f"html/{receipt_id}.html",
            "json_file": f"json/{receipt_id}.json",
            "total": receipt.total,
            "merchant": receipt.merchant_name,
            "category": receipt.merchant_category
        })

        print(f"Generated receipt {i + 1}/{count}: {receipt.receipt_number}")

    # Save manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "../output/receipts"

    print(f"Generating {count} synthetic receipts...")
    manifest = generate_receipt_batch(count, output_dir)
    print(f"Generated {len(manifest)} receipts to {output_dir}")
