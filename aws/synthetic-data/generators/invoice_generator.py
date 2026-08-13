"""
Invoice Generator
Generate synthetic invoice documents for testing BDA extraction
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
import os

# Sample data pools
VENDOR_NAMES = [
    "Acme Corporation", "TechPro Solutions", "Global Supply Co.",
    "Premier Services Inc.", "Industrial Partners LLC", "DataSystems Corp",
    "Quality Products Ltd", "Apex Manufacturing", "Summit Enterprises",
    "Precision Tools Inc.", "CloudTech Services", "Elite Consulting Group"
]

VENDOR_ADDRESSES = [
    {"street": "123 Business Park Dr", "city": "Austin", "state": "TX", "zip": "78701"},
    {"street": "456 Commerce Blvd", "city": "Seattle", "state": "WA", "zip": "98101"},
    {"street": "789 Industrial Way", "city": "Chicago", "state": "IL", "zip": "60601"},
    {"street": "321 Tech Center Ln", "city": "San Jose", "state": "CA", "zip": "95110"},
    {"street": "555 Enterprise Ave", "city": "Denver", "state": "CO", "zip": "80202"},
    {"street": "999 Corporate Plaza", "city": "Atlanta", "state": "GA", "zip": "30301"},
]

CUSTOMER_NAMES = [
    "Contoso Industries", "Fabrikam Corp", "Northwind Traders",
    "Adventure Works", "Wide World Importers", "Tailspin Toys"
]

PRODUCT_CATALOG = [
    {"desc": "Professional Software License - Annual", "unit": "each", "price_range": (500, 5000)},
    {"desc": "Cloud Hosting Services - Monthly", "unit": "month", "price_range": (100, 1000)},
    {"desc": "Technical Consulting - Hourly", "unit": "hour", "price_range": (150, 300)},
    {"desc": "Hardware Components - Server Grade", "unit": "each", "price_range": (200, 2000)},
    {"desc": "Network Equipment - Enterprise", "unit": "each", "price_range": (500, 3000)},
    {"desc": "Maintenance Support - Annual", "unit": "year", "price_range": (1000, 10000)},
    {"desc": "Training Services - Per Person", "unit": "person", "price_range": (200, 500)},
    {"desc": "Data Migration Services", "unit": "project", "price_range": (5000, 25000)},
    {"desc": "Security Audit Services", "unit": "audit", "price_range": (2000, 10000)},
    {"desc": "Office Supplies - Bulk Order", "unit": "box", "price_range": (25, 150)},
]

PAYMENT_TERMS = ["NET30", "NET15", "NET45", "NET60", "Due on Receipt", "2/10 NET30"]


@dataclass
class LineItem:
    description: str
    quantity: int
    unit_price: float
    amount: float
    item_code: str = ""


@dataclass
class Invoice:
    vendor_name: str
    vendor_address: Dict[str, str]
    vendor_tax_id: str
    vendor_phone: str
    vendor_email: str
    customer_name: str
    customer_address: Dict[str, str]
    invoice_number: str
    invoice_date: str
    due_date: str
    po_number: str
    terms: str
    line_items: List[LineItem]
    subtotal: float
    tax_rate: float
    tax_amount: float
    shipping: float
    total: float
    bank_name: str = "First National Bank"
    account_number: str = "****1234"
    routing_number: str = "021000089"


def generate_tax_id() -> str:
    """Generate random EIN format tax ID"""
    return f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"


def generate_phone() -> str:
    """Generate random phone number"""
    return f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def generate_invoice_number() -> str:
    """Generate invoice number"""
    prefix = random.choice(["INV", "SI", "IV", ""])
    year = datetime.now().year
    seq = random.randint(10000, 99999)
    return f"{prefix}{year}-{seq}" if prefix else f"{year}{seq}"


def generate_po_number() -> str:
    """Generate PO number"""
    return f"PO-{random.randint(100000, 999999)}"


def generate_item_code() -> str:
    """Generate item/SKU code"""
    letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
    numbers = random.randint(1000, 9999)
    return f"{letters}-{numbers}"


def generate_line_items(count: int = None) -> List[LineItem]:
    """Generate random line items"""
    if count is None:
        count = random.randint(1, 8)

    items = []
    for _ in range(count):
        product = random.choice(PRODUCT_CATALOG)
        qty = random.randint(1, 20)
        unit_price = round(random.uniform(*product["price_range"]), 2)
        amount = round(qty * unit_price, 2)

        items.append(LineItem(
            description=product["desc"],
            quantity=qty,
            unit_price=unit_price,
            amount=amount,
            item_code=generate_item_code()
        ))

    return items


def generate_invoice(
    vendor_name: str = None,
    invoice_date: datetime = None,
    total_range: tuple = None
) -> Invoice:
    """Generate a complete synthetic invoice"""

    # Vendor info
    vendor = vendor_name or random.choice(VENDOR_NAMES)
    vendor_addr = random.choice(VENDOR_ADDRESSES)

    # Customer info
    customer = random.choice(CUSTOMER_NAMES)
    customer_addr = random.choice(VENDOR_ADDRESSES)

    # Dates
    if invoice_date is None:
        invoice_date = datetime.now() - timedelta(days=random.randint(0, 30))

    terms = random.choice(PAYMENT_TERMS)
    if "NET" in terms:
        days = int("".join(filter(str.isdigit, terms.split()[0])))
        due_date = invoice_date + timedelta(days=days)
    else:
        due_date = invoice_date + timedelta(days=30)

    # Line items
    line_items = generate_line_items()

    # Totals
    subtotal = sum(item.amount for item in line_items)
    tax_rate = random.choice([0, 0.0625, 0.07, 0.0825, 0.10])
    tax_amount = round(subtotal * tax_rate, 2)
    shipping = round(random.uniform(0, 50), 2) if random.random() > 0.5 else 0
    total = round(subtotal + tax_amount + shipping, 2)

    return Invoice(
        vendor_name=vendor,
        vendor_address=vendor_addr,
        vendor_tax_id=generate_tax_id(),
        vendor_phone=generate_phone(),
        vendor_email=f"billing@{vendor.lower().replace(' ', '').replace('.', '')[:10]}.com",
        customer_name=customer,
        customer_address=customer_addr,
        invoice_number=generate_invoice_number(),
        invoice_date=invoice_date.strftime("%Y-%m-%d"),
        due_date=due_date.strftime("%Y-%m-%d"),
        po_number=generate_po_number(),
        terms=terms,
        line_items=line_items,
        subtotal=subtotal,
        tax_rate=tax_rate,
        tax_amount=tax_amount,
        shipping=shipping,
        total=total
    )


def invoice_to_html(invoice: Invoice, template: str = "standard") -> str:
    """Convert invoice to HTML for PDF generation"""

    line_items_html = ""
    for i, item in enumerate(invoice.line_items, 1):
        line_items_html += f"""
        <tr>
            <td>{i}</td>
            <td>{item.item_code}</td>
            <td>{item.description}</td>
            <td>{item.quantity}</td>
            <td>${item.unit_price:,.2f}</td>
            <td>${item.amount:,.2f}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice {invoice.invoice_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #333;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
        }}
        .vendor-info {{
            max-width: 300px;
        }}
        .invoice-info {{
            text-align: right;
        }}
        .invoice-title {{
            font-size: 32px;
            color: #2c3e50;
            font-weight: bold;
        }}
        .invoice-number {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        .addresses {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }}
        .address-block {{
            width: 45%;
        }}
        .address-label {{
            font-weight: bold;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
            margin-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .totals {{
            width: 300px;
            margin-left: auto;
        }}
        .totals table {{
            margin-bottom: 0;
        }}
        .totals td {{
            padding: 8px;
        }}
        .totals .total-row {{
            font-weight: bold;
            font-size: 18px;
            background-color: #2c3e50;
            color: white;
        }}
        .payment-info {{
            margin-top: 40px;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="vendor-info">
            <h2 style="margin: 0; color: #2c3e50;">{invoice.vendor_name}</h2>
            <p>
                {invoice.vendor_address['street']}<br>
                {invoice.vendor_address['city']}, {invoice.vendor_address['state']} {invoice.vendor_address['zip']}<br>
                Phone: {invoice.vendor_phone}<br>
                Email: {invoice.vendor_email}<br>
                Tax ID: {invoice.vendor_tax_id}
            </p>
        </div>
        <div class="invoice-info">
            <div class="invoice-title">INVOICE</div>
            <div class="invoice-number">
                Invoice #: {invoice.invoice_number}<br>
                Date: {invoice.invoice_date}<br>
                Due Date: {invoice.due_date}<br>
                PO #: {invoice.po_number}<br>
                Terms: {invoice.terms}
            </div>
        </div>
    </div>

    <div class="addresses">
        <div class="address-block">
            <div class="address-label">Bill To:</div>
            <div>
                {invoice.customer_name}<br>
                {invoice.customer_address['street']}<br>
                {invoice.customer_address['city']}, {invoice.customer_address['state']} {invoice.customer_address['zip']}
            </div>
        </div>
        <div class="address-block">
            <div class="address-label">Ship To:</div>
            <div>
                {invoice.customer_name}<br>
                {invoice.customer_address['street']}<br>
                {invoice.customer_address['city']}, {invoice.customer_address['state']} {invoice.customer_address['zip']}
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Item Code</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {line_items_html}
        </tbody>
    </table>

    <div class="totals">
        <table>
            <tr>
                <td>Subtotal:</td>
                <td style="text-align: right;">${invoice.subtotal:,.2f}</td>
            </tr>
            <tr>
                <td>Tax ({invoice.tax_rate * 100:.2f}%):</td>
                <td style="text-align: right;">${invoice.tax_amount:,.2f}</td>
            </tr>
            <tr>
                <td>Shipping:</td>
                <td style="text-align: right;">${invoice.shipping:,.2f}</td>
            </tr>
            <tr class="total-row">
                <td>Total Due:</td>
                <td style="text-align: right;">${invoice.total:,.2f}</td>
            </tr>
        </table>
    </div>

    <div class="payment-info">
        <strong>Payment Information:</strong><br>
        Bank: {invoice.bank_name}<br>
        Account: {invoice.account_number}<br>
        Routing: {invoice.routing_number}<br>
        <br>
        Please include invoice number {invoice.invoice_number} with your payment.
    </div>

    <div class="footer">
        Thank you for your business!<br>
        Questions? Contact {invoice.vendor_email}
    </div>
</body>
</html>
    """
    return html


def invoice_to_json(invoice: Invoice) -> Dict[str, Any]:
    """Convert invoice to JSON format (ground truth)"""
    return {
        "vendor": {
            "name": invoice.vendor_name,
            "address": invoice.vendor_address,
            "tax_id": invoice.vendor_tax_id,
            "phone": invoice.vendor_phone,
            "email": invoice.vendor_email
        },
        "invoice": {
            "number": invoice.invoice_number,
            "date": invoice.invoice_date,
            "due_date": invoice.due_date,
            "po_number": invoice.po_number,
            "terms": invoice.terms
        },
        "bill_to": {
            "company_name": invoice.customer_name,
            "address": invoice.customer_address
        },
        "line_items": [asdict(item) for item in invoice.line_items],
        "totals": {
            "subtotal": invoice.subtotal,
            "tax_rate": invoice.tax_rate,
            "tax_amount": invoice.tax_amount,
            "shipping": invoice.shipping,
            "total": invoice.total
        },
        "payment": {
            "bank_name": invoice.bank_name,
            "account_number": invoice.account_number,
            "routing_number": invoice.routing_number
        }
    }


def generate_invoice_batch(count: int, output_dir: str) -> List[Dict[str, Any]]:
    """Generate a batch of invoices with HTML and JSON files"""

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)

    manifest = []

    for i in range(count):
        invoice = generate_invoice()
        invoice_id = invoice.invoice_number.replace("-", "_")

        # Save HTML
        html_path = os.path.join(output_dir, "html", f"{invoice_id}.html")
        with open(html_path, "w") as f:
            f.write(invoice_to_html(invoice))

        # Save JSON (ground truth)
        json_path = os.path.join(output_dir, "json", f"{invoice_id}.json")
        json_data = invoice_to_json(invoice)
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)

        manifest.append({
            "invoice_number": invoice.invoice_number,
            "html_file": f"html/{invoice_id}.html",
            "json_file": f"json/{invoice_id}.json",
            "total": invoice.total,
            "vendor": invoice.vendor_name
        })

        print(f"Generated invoice {i + 1}/{count}: {invoice.invoice_number}")

    # Save manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "../output/invoices"

    print(f"Generating {count} synthetic invoices...")
    manifest = generate_invoice_batch(count, output_dir)
    print(f"Generated {len(manifest)} invoices to {output_dir}")
