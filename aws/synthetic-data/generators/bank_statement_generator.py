"""
Bank Statement Generator
Generate synthetic bank statements for testing BDA extraction
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import os

BANKS = [
    {"name": "First National Bank", "routing": "021000089"},
    {"name": "Chase Bank", "routing": "021000021"},
    {"name": "Bank of America", "routing": "026009593"},
    {"name": "Wells Fargo", "routing": "121000248"},
    {"name": "Citibank", "routing": "021000089"},
]

ACCOUNT_HOLDERS = [
    "Contoso Industries LLC",
    "Fabrikam Corporation",
    "Northwind Traders Inc",
    "Adventure Works Ltd",
    "Wide World Importers Co"
]

TRANSACTION_DESCRIPTIONS = {
    "deposits": [
        "ACH DEPOSIT - CUSTOMER PAYMENT",
        "WIRE TRANSFER - VENDOR REFUND",
        "CHECK DEPOSIT",
        "ACH CREDIT - ACCOUNTS RECEIVABLE",
        "MERCHANT SERVICES DEPOSIT",
        "WIRE TRANSFER IN",
    ],
    "withdrawals": [
        "ACH DEBIT - PAYROLL",
        "WIRE TRANSFER - VENDOR PAYMENT",
        "CHECK #",
        "ACH DEBIT - UTILITY PAYMENT",
        "ACH DEBIT - INSURANCE PREMIUM",
        "WIRE TRANSFER OUT",
        "DEBIT CARD PURCHASE",
    ],
    "fees": [
        "MONTHLY SERVICE FEE",
        "WIRE TRANSFER FEE",
        "OVERDRAFT FEE",
        "STOP PAYMENT FEE",
    ]
}


@dataclass
class Transaction:
    date: str
    description: str
    type: str
    debit: float
    credit: float
    balance: float
    reference: str


@dataclass
class BankStatement:
    bank_name: str
    bank_routing: str
    account_holder: str
    account_number: str
    account_type: str
    statement_start: str
    statement_end: str
    beginning_balance: float
    ending_balance: float
    total_deposits: float
    total_withdrawals: float
    total_fees: float
    transactions: List[Transaction]


def generate_account_number() -> str:
    return f"****{random.randint(1000, 9999)}"


def generate_reference() -> str:
    return f"REF{random.randint(100000000, 999999999)}"


def generate_transactions(
    start_date: datetime,
    end_date: datetime,
    beginning_balance: float
) -> List[Transaction]:
    """Generate realistic bank transactions for the period"""

    transactions = []
    current_balance = beginning_balance
    current_date = start_date

    # Generate 15-40 transactions per month
    num_transactions = random.randint(15, 40)

    for _ in range(num_transactions):
        # Random date within period
        days_in_period = (end_date - start_date).days
        tx_date = start_date + timedelta(days=random.randint(0, days_in_period))

        # Determine transaction type
        tx_type_roll = random.random()

        if tx_type_roll < 0.35:  # 35% deposits
            tx_type = "Deposit"
            description = random.choice(TRANSACTION_DESCRIPTIONS["deposits"])
            amount = round(random.uniform(500, 50000), 2)
            debit = 0
            credit = amount
            current_balance += amount

        elif tx_type_roll < 0.90:  # 55% withdrawals
            tx_type = "Withdrawal"
            description = random.choice(TRANSACTION_DESCRIPTIONS["withdrawals"])
            if "CHECK #" in description:
                description = f"CHECK #{random.randint(1000, 9999)}"
            amount = round(random.uniform(100, 25000), 2)
            debit = amount
            credit = 0
            current_balance -= amount

        else:  # 10% fees
            tx_type = "Fee"
            description = random.choice(TRANSACTION_DESCRIPTIONS["fees"])
            amount = round(random.uniform(15, 50), 2)
            debit = amount
            credit = 0
            current_balance -= amount

        transactions.append(Transaction(
            date=tx_date.strftime("%Y-%m-%d"),
            description=description,
            type=tx_type,
            debit=debit,
            credit=credit,
            balance=round(current_balance, 2),
            reference=generate_reference()
        ))

    # Sort by date
    transactions.sort(key=lambda x: x.date)

    # Recalculate running balance
    current_balance = beginning_balance
    for tx in transactions:
        current_balance = current_balance - tx.debit + tx.credit
        tx.balance = round(current_balance, 2)

    return transactions


def generate_bank_statement(
    statement_month: datetime = None
) -> BankStatement:
    """Generate a complete synthetic bank statement"""

    bank = random.choice(BANKS)
    holder = random.choice(ACCOUNT_HOLDERS)

    # Statement period (full month)
    if statement_month is None:
        statement_month = datetime.now().replace(day=1) - timedelta(days=1)

    start_date = statement_month.replace(day=1)
    if start_date.month == 12:
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)

    # Balances
    beginning_balance = round(random.uniform(50000, 500000), 2)

    # Generate transactions
    transactions = generate_transactions(start_date, end_date, beginning_balance)

    # Calculate totals
    total_deposits = sum(tx.credit for tx in transactions)
    total_withdrawals = sum(tx.debit for tx in transactions if tx.type != "Fee")
    total_fees = sum(tx.debit for tx in transactions if tx.type == "Fee")
    ending_balance = beginning_balance + total_deposits - total_withdrawals - total_fees

    return BankStatement(
        bank_name=bank["name"],
        bank_routing=bank["routing"],
        account_holder=holder,
        account_number=generate_account_number(),
        account_type=random.choice(["Business Checking", "Operating Account"]),
        statement_start=start_date.strftime("%Y-%m-%d"),
        statement_end=end_date.strftime("%Y-%m-%d"),
        beginning_balance=beginning_balance,
        ending_balance=round(ending_balance, 2),
        total_deposits=round(total_deposits, 2),
        total_withdrawals=round(total_withdrawals, 2),
        total_fees=round(total_fees, 2),
        transactions=transactions
    )


def statement_to_html(statement: BankStatement) -> str:
    """Convert bank statement to HTML"""

    transactions_html = ""
    for tx in statement.transactions:
        debit_str = f"${tx.debit:,.2f}" if tx.debit > 0 else ""
        credit_str = f"${tx.credit:,.2f}" if tx.credit > 0 else ""

        transactions_html += f"""
        <tr>
            <td>{tx.date}</td>
            <td>{tx.description}</td>
            <td>{tx.reference}</td>
            <td class="debit">{debit_str}</td>
            <td class="credit">{credit_str}</td>
            <td class="balance">${tx.balance:,.2f}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bank Statement - {statement.account_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            color: #333;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            border-bottom: 3px solid #1a365d;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .bank-info {{
            color: #1a365d;
        }}
        .bank-name {{
            font-size: 24px;
            font-weight: bold;
        }}
        .statement-title {{
            font-size: 20px;
            color: #1a365d;
            text-align: right;
        }}
        .account-info {{
            background-color: #f5f5f5;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
        }}
        .summary-box {{
            background-color: #e8f4f8;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #1a365d;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }}
        .summary-item {{
            text-align: center;
        }}
        .summary-label {{
            font-size: 12px;
            color: #666;
        }}
        .summary-value {{
            font-size: 20px;
            font-weight: bold;
            color: #1a365d;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}
        th {{
            background-color: #1a365d;
            color: white;
            padding: 12px 8px;
            text-align: left;
        }}
        td {{
            padding: 8px;
            border-bottom: 1px solid #ddd;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .debit {{
            color: #c53030;
            text-align: right;
        }}
        .credit {{
            color: #2f855a;
            text-align: right;
        }}
        .balance {{
            text-align: right;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            font-size: 11px;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="bank-info">
            <div class="bank-name">{statement.bank_name}</div>
            <div>Routing Number: {statement.bank_routing}</div>
        </div>
        <div class="statement-title">
            ACCOUNT STATEMENT<br>
            <span style="font-size: 14px;">
                {statement.statement_start} to {statement.statement_end}
            </span>
        </div>
    </div>

    <div class="account-info">
        <div>
            <strong>Account Holder:</strong><br>
            {statement.account_holder}
        </div>
        <div>
            <strong>Account Number:</strong><br>
            {statement.account_number}
        </div>
        <div>
            <strong>Account Type:</strong><br>
            {statement.account_type}
        </div>
    </div>

    <div class="summary-box">
        <h3 style="margin-top: 0;">Account Summary</h3>
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label">Beginning Balance</div>
                <div class="summary-value">${statement.beginning_balance:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Deposits</div>
                <div class="summary-value" style="color: #2f855a;">+${statement.total_deposits:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Withdrawals</div>
                <div class="summary-value" style="color: #c53030;">-${statement.total_withdrawals:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Total Fees</div>
                <div class="summary-value" style="color: #c53030;">-${statement.total_fees:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Ending Balance</div>
                <div class="summary-value">${statement.ending_balance:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Transaction Count</div>
                <div class="summary-value">{len(statement.transactions)}</div>
            </div>
        </div>
    </div>

    <h3>Transaction Detail</h3>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Reference</th>
                <th style="text-align: right;">Debit</th>
                <th style="text-align: right;">Credit</th>
                <th style="text-align: right;">Balance</th>
            </tr>
        </thead>
        <tbody>
            {transactions_html}
        </tbody>
    </table>

    <div class="footer">
        This statement is provided for informational purposes. Please review all transactions and report any discrepancies within 60 days.
        <br><br>
        {statement.bank_name} | Member FDIC | Equal Housing Lender
    </div>
</body>
</html>
    """
    return html


def statement_to_json(statement: BankStatement) -> Dict[str, Any]:
    """Convert statement to JSON (ground truth)"""
    return {
        "bank": {
            "name": statement.bank_name,
            "routing_number": statement.bank_routing
        },
        "account": {
            "holder_name": statement.account_holder,
            "account_number": statement.account_number,
            "account_type": statement.account_type
        },
        "statement_period": {
            "start_date": statement.statement_start,
            "end_date": statement.statement_end
        },
        "balances": {
            "beginning_balance": statement.beginning_balance,
            "ending_balance": statement.ending_balance
        },
        "summary": {
            "total_deposits": statement.total_deposits,
            "total_withdrawals": statement.total_withdrawals,
            "total_fees": statement.total_fees,
            "transaction_count": len(statement.transactions)
        },
        "transactions": [asdict(tx) for tx in statement.transactions]
    }


def generate_statement_batch(count: int, output_dir: str) -> List[Dict[str, Any]]:
    """Generate a batch of bank statements"""

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)

    manifest = []

    for i in range(count):
        # Generate for different months
        months_ago = i % 12
        statement_date = datetime.now() - timedelta(days=30 * months_ago)
        statement = generate_bank_statement(statement_date)

        statement_id = f"stmt_{statement.statement_start.replace('-', '')}_{statement.account_number.replace('*', 'X')}"

        # Save HTML
        html_path = os.path.join(output_dir, "html", f"{statement_id}.html")
        with open(html_path, "w") as f:
            f.write(statement_to_html(statement))

        # Save JSON
        json_path = os.path.join(output_dir, "json", f"{statement_id}.json")
        with open(json_path, "w") as f:
            json.dump(statement_to_json(statement), f, indent=2)

        manifest.append({
            "statement_id": statement_id,
            "html_file": f"html/{statement_id}.html",
            "json_file": f"json/{statement_id}.json",
            "period": f"{statement.statement_start} to {statement.statement_end}",
            "ending_balance": statement.ending_balance,
            "account_holder": statement.account_holder
        })

        print(f"Generated statement {i + 1}/{count}: {statement_id}")

    # Save manifest
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    return manifest


if __name__ == "__main__":
    import sys

    count = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "../output/statements"

    print(f"Generating {count} synthetic bank statements...")
    manifest = generate_statement_batch(count, output_dir)
    print(f"Generated {len(manifest)} statements to {output_dir}")
