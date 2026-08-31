#!/usr/bin/env python3
"""
APEX Developer Training — DynamoDB seed data.

Creates and seeds every table the two training use cases depend on. Idempotent:
existing tables are reused and existing rows are overwritten with the canonical
values, so re-running is always safe.

Follows the same shape as backend/services/aws_provisioner.py — a TABLE_SPECS
list of (table_name, hash_key, hash_key_type, items) tuples — so anything you
learn here transfers directly to the platform's own provisioner.

USAGE
    # Seed everything against real AWS (uses your default credentials/region)
    python3 training/scripts/seed_training_data.py

    # Seed only one use case
    python3 training/scripts/seed_training_data.py --use-case uc1
    python3 training/scripts/seed_training_data.py --use-case uc2

    # See exactly what would be written without touching AWS
    python3 training/scripts/seed_training_data.py --dry-run

    # Write the rows to local JSON instead of DynamoDB (offline exercise)
    python3 training/scripts/seed_training_data.py --emit-json training/seed-output

    # Point at a different region or table prefix
    python3 training/scripts/seed_training_data.py --region us-west-2 --prefix apex-dev

WHY THESE TABLES
    UC1 (financial_services.*) needs purchase orders, goods receipts, the vendor
    master and payment history — without payment history the duplicate detector
    has nothing to compare against and every invoice looks unique.

    UC2 (insurance_underwriting.*) needs a policy register and an open-submission
    pipeline — without them clearance always returns "clear" and the broker
    conflict scenario cannot be demonstrated.

    Note that backend/services/aws_provisioner.py currently seeds NOTHING for
    insurance_underwriting. The two UC2 tables below are the first seed data that
    industry has had.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Tuple

DEFAULT_REGION = os.environ.get("AWS_REGION", "us-east-1")
DEFAULT_PREFIX = "apex-ai-platform"

# Anchor every relative date to a fixed day so the fixtures stay reproducible.
TODAY = datetime(2026, 5, 14)


def _d(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).strftime("%Y-%m-%d")


# ============================================================================
# Row builders — one per entity, mirroring aws_provisioner.py's _po()/_vendor()
# ============================================================================

def _vendor(
    vendor_id: str,
    name: str,
    tax_id: str,
    status: str = "active",
    category: str = "supplies",
    remit_to_name: str = None,
    country: str = "US",
) -> Dict[str, Any]:
    """Approved vendor master row. remit_to_name defaults to the vendor name —
    a row where they differ is what REMIT_DRIFT detects."""
    return {
        "vendor_id": vendor_id,
        "vendor_name": name,
        "vendor_name_lower": name.lower(),
        "status": status,
        "payment_terms": "NET30",
        "category": category,
        "tax_id": tax_id,
        "country": country,
        "remit_to_name": remit_to_name or name,
        "contact_email": f"ar@{name.split()[0].lower()}.example.com",
        "approved_date": _d(900),
        "credit_limit": Decimal("250000"),
        "w9_on_file": True,
    }


def _po(
    po_number: str,
    vendor_id: str,
    vendor_name: str,
    lines: List[Dict[str, Any]],
    po_type: str = "stock",
    status: str = "open",
    freight_allowed: float = 0.0,
) -> Dict[str, Any]:
    """Purchase order header plus line detail. po_type drives whether the
    playbook requires a three-way or two-way match."""
    subtotal = sum(float(l["quantity"]) * float(l["unit_price"]) for l in lines)
    return {
        "po_number": po_number,
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "po_type": po_type,
        "status": status,
        "currency": "USD",
        "freight_allowed": Decimal(str(round(freight_allowed, 2))),
        "total_amount": Decimal(str(round(subtotal + freight_allowed, 2))),
        "remaining_balance": Decimal(str(round(subtotal + freight_allowed, 2))) if status == "open" else Decimal("0"),
        "issued_date": _d(60),
        "buyer_email": "procurement@example.com",
        "lines": [
            {
                "line_number": l["line_number"],
                "sku": l["sku"],
                "description": l["description"],
                "quantity": Decimal(str(l["quantity"])),
                "uom": l.get("uom", "EA"),
                "unit_price": Decimal(str(l["unit_price"])),
                "amount": Decimal(str(round(float(l["quantity"]) * float(l["unit_price"]), 2))),
            }
            for l in lines
        ],
    }


def _receipt(
    receipt_number: str,
    po_number: str,
    lines: List[Dict[str, Any]],
    received_date_days_ago: int = 20,
) -> Dict[str, Any]:
    """Goods receipt. The quantity here — not the PO quantity — is what a
    three-way match compares the invoice against."""
    return {
        "receipt_number": receipt_number,
        "po_number": po_number,
        "received_date": _d(received_date_days_ago),
        "received_by": "warehouse@example.com",
        "status": "posted",
        "lines": [
            {
                "line_number": l["line_number"],
                "sku": l["sku"],
                "quantity": Decimal(str(l["quantity"])),
                "uom": l.get("uom", "EA"),
            }
            for l in lines
        ],
    }


def _payment(
    payment_id: str,
    invoice_number: str,
    vendor_id: str,
    vendor_name: str,
    amount: float,
    invoice_date_days_ago: int,
    paid_date_days_ago: int,
    po_number: str = None,
) -> Dict[str, Any]:
    """A previously paid invoice. This is the corpus duplicate_fingerprint
    searches — it is the single most important table in UC1."""
    return {
        "payment_id": payment_id,
        "invoice_number": invoice_number,
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "total_amount": Decimal(str(round(amount, 2))),
        "currency": "USD",
        "invoice_date": _d(invoice_date_days_ago),
        "paid_date": _d(paid_date_days_ago),
        "po_number": po_number,
        "payment_method": "ACH",
        "status": "paid",
    }


def _policy(
    policy_number: str,
    named_insured: str,
    fein: str,
    broker: str,
    effective_days_ago: int,
    address: str,
    postal_code: str,
    tiv: float,
    additional_named: List[str] = None,
) -> Dict[str, Any]:
    """In-force policy. A submission matching one of these by FEIN is a renewal,
    not new business."""
    return {
        "policy_number": policy_number,
        "named_insured": named_insured,
        "additional_named_insureds": additional_named or [],
        "fein": fein,
        "broker_agency_name": broker,
        "line_of_business": "commercial_property",
        "status": "in_force",
        "effective_date": _d(effective_days_ago),
        "expiration_date": _d(effective_days_ago - 365),
        "first_location_address": address,
        "first_location_postal_code": postal_code,
        "total_insured_value": Decimal(str(round(tiv, 2))),
        "annual_premium": Decimal(str(round(tiv * 0.0052, 2))),
    }


def _open_submission(
    submission_id: str,
    named_insured: str,
    fein: str,
    broker: str,
    received_days_ago: int,
    address: str,
    postal_code: str,
    tiv: float,
    status: str = "open",
    additional_named: List[str] = None,
) -> Dict[str, Any]:
    """A submission already in the pipeline. Matching one of these from a
    DIFFERENT broker is the broker-of-record conflict UC2 demonstrates."""
    return {
        "submission_id": submission_id,
        "named_insured": named_insured,
        "additional_named_insureds": additional_named or [],
        "fein": fein,
        "broker_agency_name": broker,
        "line_of_business": "commercial_property",
        "status": status,
        "received_date": _d(received_days_ago),
        "requested_effective_date": _d(received_days_ago - 45),
        "first_location_address": address,
        "first_location_postal_code": postal_code,
        "total_insured_value": Decimal(str(round(tiv, 2))),
        "assigned_underwriter": "underwriting@example.com",
    }


# ============================================================================
# UC1 — Financial Services: AP Invoice Exception Triage
# ============================================================================

# Vendor names and tax IDs match the sample invoices in
# training/uc1-invoice-exception/sample-files/ exactly. If you change one, change
# the other — vendor_lookup joins on the name printed on the document.
UC1_VENDORS = [
    _vendor("VEN-001", "Acme Corp", "74-2091883", category="packaging"),
    # Globex remits to itself. inv_06 names "Meridian Capital Funding LLC" as the
    # payee, which is what REMIT_DRIFT detects.
    _vendor("VEN-002", "Globex Corp", "31-1774502", category="industrial"),
    _vendor("VEN-003", "Initech LLC", "74-3010556", category="it_hardware"),
    _vendor("VEN-004", "Hooli Inc.", "94-2404110", category="it_hardware"),
    _vendor("VEN-005", "Umbrella Corporation", "38-1665521", category="chemicals"),
]

# Every PO below is the baseline for one sample invoice. The PO unit price is
# what three_way_match compares the invoice price against, so these numbers ARE
# the test: change a unit price here and the expected disposition changes.
UC1_PURCHASE_ORDERS = [
    # inv_01 (clean) and inv_05 (duplicate) both reference PO-5000.
    # Prices match the invoices exactly, so inv_01 produces zero variances.
    _po("PO-5000", "VEN-001", "Acme Corp", [
        {"line_number": 1, "sku": "ACM-TAPE-24",      "description": "Packing tape, 24-roll case", "quantity": 100, "unit_price": 42.50},
        {"line_number": 2, "sku": "ACM-STRAP-12",     "description": "Poly strapping, 12mm coil",  "quantity": 50,  "unit_price": 15.00},
        {"line_number": 3, "sku": "ACM-BUBBLE-WRAP",  "description": "Bubble wrap, 50m roll",      "quantity": 40,  "unit_price": 24.00},
    ]),
    # inv_02 — PRICE_VAR *within* tolerance. Invoice bills $515.00 against this
    # $500.00 PO price: a 3.0% variance, inside the 5% / $250 band.
    _po("PO-6112", "VEN-003", "Initech LLC", [
        {"line_number": 1, "sku": "INI-SW24",      "description": "24-port managed switch", "quantity": 8, "unit_price": 500.00},
        {"line_number": 2, "sku": "INI-CBL-CAT6",  "description": "Cat6 patch cable, 3m",   "quantity": 8, "unit_price": 45.00},
    ]),
    # inv_03 — PRICE_VAR *outside* tolerance. Invoice bills $201.60 against this
    # $180.00 PO price: a 12.0% variance, breaching the 5% band.
    _po("PO-7231", "VEN-004", "Hooli Inc.", [
        {"line_number": 1, "sku": "HLI-MON27",        "description": "27in monitor",     "quantity": 10, "unit_price": 180.00},
        {"line_number": 2, "sku": "HLI-DOC-STATION",  "description": "Docking station",  "quantity": 10, "unit_price": 89.00},
    ]),
    # inv_04 — QTY_VAR. PO and receipt both say 100; the invoice bills 120.
    _po("PO-8340", "VEN-005", "Umbrella Corporation", [
        {"line_number": 1, "sku": "UMB-CLN-5G",         "description": "Industrial cleaner, 5 gal", "quantity": 100, "unit_price": 38.75},
        {"line_number": 2, "sku": "UMB-DEGREASE-CS",    "description": "Degreaser, case of 12",     "quantity": 15,  "unit_price": 32.00},
    ]),
    # inv_06 — everything matches. The ONLY problem is the remit-to party, which
    # is exactly why a naive matcher would auto-resolve and pay a fraudster.
    _po("PO-6650", "VEN-002", "Globex Corp", [
        {"line_number": 1, "sku": "GLX-PSU-24V",   "description": "24V power supply unit",   "quantity": 25, "unit_price": 68.00},
        {"line_number": 2, "sku": "GLX-CTRL-PLC",  "description": "PLC controller module",   "quantity": 5,  "unit_price": 312.00},
    ]),
    # Extra fixtures for the exercises in Module 3.
    _po("PO-6200", "VEN-003", "Initech LLC", [
        {"line_number": 1, "sku": "SVC-CONSULT", "description": "Systems consulting, hours", "quantity": 80, "unit_price": 175.00},
    ], po_type="services"),          # services PO — two-way match, NO_RECEIPT must NOT fire
    _po("PO-4400", "VEN-005", "Umbrella Corporation", [
        {"line_number": 1, "sku": "CH-99", "description": "Reagent, 5L", "quantity": 10, "unit_price": 220.00},
    ], status="closed"),             # exercises PO_CLOSED
    _po("PO-7700", "VEN-001", "Acme Corp", [
        {"line_number": 1, "sku": "ACM-TAPE-24", "description": "Packing tape, 24-roll case", "quantity": 200, "unit_price": 42.50},
    ], freight_allowed=180.00),      # exercises FREIGHT_UNMATCHED
]

# The receipt quantity — not the PO quantity — is what a three-way match
# compares the invoice against. GRN-63390 is the QTY_VAR fixture.
UC1_GOODS_RECEIPTS = [
    _receipt("GRN-77201", "PO-5000", [
        {"line_number": 1, "sku": "ACM-TAPE-24",  "quantity": 20},
        {"line_number": 2, "sku": "ACM-STRAP-12", "quantity": 10},
    ]),
    _receipt("GRN-77088", "PO-5000", [
        {"line_number": 1, "sku": "ACM-TAPE-24",     "quantity": 80},
        {"line_number": 2, "sku": "ACM-STRAP-12",    "quantity": 40},
        {"line_number": 3, "sku": "ACM-BUBBLE-WRAP", "quantity": 20},
    ], received_date_days_ago=70),
    _receipt("GRN-55210", "PO-6112", [
        {"line_number": 1, "sku": "INI-SW24",     "quantity": 8},
        {"line_number": 2, "sku": "INI-CBL-CAT6", "quantity": 8},
    ]),
    _receipt("GRN-91004", "PO-7231", [
        {"line_number": 1, "sku": "HLI-MON27",       "quantity": 10},
        {"line_number": 2, "sku": "HLI-DOC-STATION", "quantity": 10},
    ]),
    # Only 100 received. The invoice bills 120. This is the QTY_VAR fixture.
    _receipt("GRN-63390", "PO-8340", [
        {"line_number": 1, "sku": "UMB-CLN-5G",      "quantity": 100},
        {"line_number": 2, "sku": "UMB-DEGREASE-CS", "quantity": 15},
    ]),
    _receipt("GRN-40217", "PO-6650", [
        {"line_number": 1, "sku": "GLX-PSU-24V",  "quantity": 25},
        {"line_number": 2, "sku": "GLX-CTRL-PLC", "quantity": 5},
    ]),
    _receipt("GRN-88010", "PO-7700", [
        {"line_number": 1, "sku": "ACM-TAPE-24", "quantity": 200},
    ]),
    # NOTE: PO-6200 deliberately has NO receipt. It is a services PO, so a
    # two-way match is correct and NO_RECEIPT must not fire.
]

UC1_PAYMENT_HISTORY = [
    # THE duplicate fixture. inv_05 arrives as "INV-001042" / Acme Corp /
    # $4,850.00 / PO-5000. This row is "inv 1042" — different formatting, same
    # invoice, already paid. An exact-match duplicate check misses it entirely;
    # the fuzzy fingerprint scores it 0.97 and blocks the payment.
    _payment("PMT-9001", "inv 1042", "VEN-001", "ACME CORPORATION", 4850.00,
             invoice_date_days_ago=88, paid_date_days_ago=81, po_number="PO-5000"),
    # Near-miss controls. These must NOT trip the duplicate detector — they are
    # how you prove the matcher is discriminating rather than just permissive.
    _payment("PMT-9002", "INV-001043", "VEN-001", "Acme Corp", 4850.00,
             invoice_date_days_ago=87, paid_date_days_ago=80, po_number="PO-5001"),
    _payment("PMT-9003", "INV-001042", "VEN-005", "Umbrella Corporation", 4850.00,
             invoice_date_days_ago=300, paid_date_days_ago=293, po_number="PO-9999"),
    _payment("PMT-9004", "INI-20440", "VEN-003", "Initech LLC", 4720.00,
             invoice_date_days_ago=120, paid_date_days_ago=112, po_number="PO-6090"),
    _payment("PMT-9005", "GLX-77020", "VEN-002", "Globex Corp", 2500.00,
             invoice_date_days_ago=45, paid_date_days_ago=38, po_number="PO-6640"),
    _payment("PMT-9006", "HLI-330870", "VEN-004", "Hooli Inc.", 2890.00,
             invoice_date_days_ago=95, paid_date_days_ago=88, po_number="PO-7200"),
]


# ============================================================================
# UC2 — Insurance Underwriting: CP Submission Clearance
# ============================================================================

UC2_POLICY_REGISTER = [
    # Renewal fixture: a submission for this FEIN is a renewal, not new business.
    _policy("CP-2024-118840", "Ironwood Millworks Inc", "74-2298031",
            "Harborline Risk Advisors", effective_days_ago=300,
            address="9 Tannery Row", postal_code="03060", tiv=11_200_000,
            additional_named=["Ironwood Millworks Holdings LLC"]),
    _policy("CP-2024-119002", "Sunblaze Self Storage LP", "31-0994412",
            "Keystone Commercial Brokers", effective_days_ago=210,
            address="4501 Grand River Ave", postal_code="48906", tiv=6_800_000),
    _policy("CP-2025-120441", "Northgate Office Trust", "20-7761204",
            "Harborline Risk Advisors", effective_days_ago=120,
            address="2200 Northgate Plaza", postal_code="55432", tiv=24_500_000),
]

UC2_OPEN_SUBMISSIONS = [
    # THE broker-conflict fixture. sub_02 arrives for the same FEIN through a
    # different (wholesale) broker 9 days later. Clearance must catch it.
    _open_submission("SUB-2026-0417", "Cedar Ridge Logistics LLC", "47-3319008",
                     "Harborline Risk Advisors", received_days_ago=12,
                     address="1420 N Industrial Blvd", postal_code="76106",
                     tiv=18_440_000,
                     additional_named=["Cedar Ridge Transport LLC"]),
    _open_submission("SUB-2026-0431", "Brightwater Retail Partners LP", "82-4471905",
                     "Vantage Point Insurance Group", received_days_ago=5,
                     address="775 Waterview Pkwy", postal_code="75080",
                     tiv=29_100_000),
    _open_submission("SUB-2026-0402", "Pinnacle Fabrication Co", "45-6612870",
                     "Keystone Commercial Brokers", received_days_ago=25,
                     address="1201 Foundry St", postal_code="44113",
                     tiv=9_750_000, status="quoted"),
]


# ============================================================================
# TABLE_SPECS — (table_suffix, hash_key, hash_key_type, items, use_case)
# ============================================================================

TABLE_SPECS: List[Tuple[str, str, str, List[Dict[str, Any]], str]] = [
    ("approved-vendors",  "vendor_id",       "S", UC1_VENDORS,          "uc1"),
    ("purchase-orders",   "po_number",       "S", UC1_PURCHASE_ORDERS,  "uc1"),
    ("goods-receipts",    "receipt_number",  "S", UC1_GOODS_RECEIPTS,   "uc1"),
    ("payment-history",   "payment_id",      "S", UC1_PAYMENT_HISTORY,  "uc1"),
    ("policy-register",   "policy_number",   "S", UC2_POLICY_REGISTER,  "uc2"),
    ("open-submissions",  "submission_id",   "S", UC2_OPEN_SUBMISSIONS, "uc2"),
]


# ============================================================================
# DynamoDB plumbing
# ============================================================================

def _to_dynamo(obj: Any) -> Any:
    """
    DynamoDB rejects Python floats. Convert every float to Decimal recursively.

    This is the single most common seeding failure in this platform — a nested
    float inside a list of line items raises
    `TypeError: Float types are not supported. Use Decimal types instead`
    and the traceback points at put_item rather than at the offending field.
    """
    if isinstance(obj, float):
        return Decimal(str(round(obj, 4)))
    if isinstance(obj, dict):
        return {k: _to_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_dynamo(v) for v in obj]
    return obj


def _from_dynamo(obj: Any) -> Any:
    """Inverse of _to_dynamo, for JSON emission."""
    if isinstance(obj, Decimal):
        f = float(obj)
        return int(f) if f.is_integer() else f
    if isinstance(obj, dict):
        return {k: _from_dynamo(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_from_dynamo(v) for v in obj]
    return obj


def _table_exists(client, name: str) -> bool:
    try:
        client.describe_table(TableName=name)
        return True
    except client.exceptions.ResourceNotFoundException:
        return False


def _create_table(client, name: str, hash_key: str, hash_type: str) -> None:
    client.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": hash_key, "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": hash_key, "AttributeType": hash_type}],
        BillingMode="PAY_PER_REQUEST",
        Tags=[
            {"Key": "Project", "Value": "APEX"},
            {"Key": "Purpose", "Value": "developer-training"},
        ],
    )
    client.get_waiter("table_exists").wait(TableName=name)


# ============================================================================
# Cloud writers — one per target. Each takes (table_name, hash_key, rows) and
# returns the number of rows written.
# ============================================================================

def _write_aws(table_name: str, hash_key: str, hash_type: str,
               rows: List[Dict[str, Any]], region: str) -> int:
    """DynamoDB. Requires Decimal, not float — see _to_dynamo()."""
    import boto3
    client = boto3.client("dynamodb", region_name=region)
    resource = boto3.resource("dynamodb", region_name=region)

    if not _table_exists(client, table_name):
        print(f"        creating table {table_name}...")
        _create_table(client, table_name, hash_key, hash_type)

    table = resource.Table(table_name)
    written = 0
    with table.batch_writer(overwrite_by_pkeys=[hash_key]) as batch:
        for row in rows:
            batch.put_item(Item=row)
            written += 1
    return written


def _write_azure(table_name: str, hash_key: str, hash_type: str,
                 rows: List[Dict[str, Any]], region: str) -> int:
    """
    Cosmos DB, via the platform's own `actions/sdk/azure_data.py` shim.

    Two differences from DynamoDB that matter:

    1. Cosmos is JSON-native and accepts floats happily. It is Decimal it does
       NOT understand — so the conversion runs in the OPPOSITE direction from
       AWS. We hand it plain floats via _from_dynamo().
    2. Cosmos needs an `id` on every document. We derive it from the hash key.

    Containers are provisioned by infrastructure/azure/main.bicep, not here —
    unlike DynamoDB, this writer does not create them. Note also that the Azure
    build's own backend/services/azure_provisioner.py is BROKEN (it calls
    boto3.client("cosmos_db"), which is not a real service). Use this script.
    """
    sys.path.insert(0, str(_azure_actions_path()))
    from sdk.azure_data import get_table_resource  # noqa: E402

    table = get_table_resource().Table(table_name)
    written = 0
    for row in _from_dynamo(rows):
        item = dict(row)
        item.setdefault("id", str(item[hash_key]))
        table.put_item(Item=item)
        written += 1
    return written


def _azure_actions_path():
    """Locate the Azure build's actions/ directory, which holds the Cosmos shim."""
    from pathlib import Path
    here = Path(__file__).resolve()
    azure_actions = here.parents[3] / "azure" / "actions"
    if not azure_actions.exists():
        raise SystemExit(
            f"ERROR: Azure build not found at {azure_actions}.\n"
            f"  --cloud azure needs the sibling azure/ tree for sdk/azure_data.py.\n"
            f"  Use --cloud local to seed the offline mock store instead."
        )
    return azure_actions


def _write_local(table_name: str, hash_key: str, hash_type: str,
                 rows: List[Dict[str, Any]], region: str) -> int:
    """
    The offline mock store the Azure build reads when USE_LOCAL_MOCK=true.

    This is the fastest way to run the whole course with no cloud account at
    all: seed here, export USE_LOCAL_MOCK=true, and every handler that reads a
    table finds this data.
    """
    path = os.environ.get("APEX_MOCK_FILE", "/tmp/apex-mock-store.json")
    try:
        with open(path) as fh:
            store = json.load(fh)
    except Exception:
        store = {}

    container = table_name
    prefix = os.environ.get("APEX_TABLE_PREFIX", "apex-ai-platform-")
    if container.startswith(prefix):
        container = container[len(prefix):]

    bucket = store.setdefault(container, {})
    for row in _from_dynamo(rows):
        item = dict(row)
        item.setdefault("id", str(item[hash_key]))
        bucket[item["id"]] = item

    with open(path, "w") as fh:
        json.dump(store, fh, indent=2)
    return len(rows)


WRITERS = {"aws": _write_aws, "azure": _write_azure, "local": _write_local}


def seed(cloud: str, region: str, prefix: str, use_case: str,
         dry_run: bool, emit_json: str) -> int:
    specs = [s for s in TABLE_SPECS if use_case in ("all", s[4])]

    if emit_json:
        os.makedirs(emit_json, exist_ok=True)

    total_rows = 0
    print(f"APEX training seed — cloud: {cloud}, use case: {use_case}, prefix: {prefix}"
          + (f", region: {region}" if cloud == "aws" else ""))
    print("=" * 78)

    for suffix, hash_key, hash_type, items, uc in specs:
        table_name = f"{prefix}-{suffix}"
        rows = _to_dynamo(items)

        if emit_json:
            path = os.path.join(emit_json, f"{table_name}.json")
            with open(path, "w") as fh:
                json.dump({"table": table_name, "hash_key": hash_key,
                           "items": _from_dynamo(rows)}, fh, indent=2)
            print(f"  [{uc}] {table_name:<44} {len(rows):>3} rows -> {path}")
            total_rows += len(rows)
            continue

        if dry_run:
            print(f"  [{uc}] {table_name:<44} {len(rows):>3} rows (dry run, key={hash_key})")
            for row in rows[:2]:
                print(f"          {json.dumps(_from_dynamo(row))[:96]}...")
            total_rows += len(rows)
            continue

        try:
            written = WRITERS[cloud](table_name, hash_key, hash_type, rows, region)
        except ImportError as exc:
            need = {"aws": "boto3", "azure": "azure-cosmos azure-identity", "local": "-"}[cloud]
            print(f"ERROR: missing dependency for --cloud {cloud} ({exc}).\n"
                  f"  Install: pip install {need}\n"
                  f"  Or use --cloud local / --dry-run / --emit-json to work offline.",
                  file=sys.stderr)
            return 1

        print(f"  [{uc}] {table_name:<44} {written:>3} rows written")
        total_rows += written

    print("=" * 78)
    mode = "emitted" if emit_json else ("planned" if dry_run else "written")
    print(f"{len(specs)} table(s), {total_rows} row(s) {mode}.")

    if not dry_run and not emit_json:
        print()
        print("Verify with:")
        if cloud == "aws":
            print(f"  aws dynamodb scan --table-name {prefix}-payment-history "
                  f"--region {region} --max-items 3")
        elif cloud == "azure":
            print(f"  az cosmosdb sql container show -a $AZURE_COSMOS_ACCOUNT "
                  f"-d $AZURE_COSMOS_DATABASE -n payment-history -g $AZURE_RESOURCE_GROUP")
        else:
            path = os.environ.get("APEX_MOCK_FILE", "/tmp/apex-mock-store.json")
            print(f"  python3 -c \"import json;print(list(json.load(open('{path}')).keys()))\"")
            print()
            print("Then run the backend with the mock store active:")
            print("  export USE_LOCAL_MOCK=true")
        print()
        print("Then reload the action registry so the new actions pick the data up:")
        port = 8002 if cloud == "azure" else 8000
        print(f"  curl -X POST http://localhost:{port}/api/v1/actions/registry/reload")
        print(f"  curl -X POST http://localhost:{port}/api/v1/actions/registry/register-all")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seed APEX developer-training data on AWS, Azure, or offline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--cloud", default="aws", choices=["aws", "azure", "local"],
                        help="aws = DynamoDB, azure = Cosmos DB, "
                             "local = offline mock store (default: aws)")
    parser.add_argument("--region", default=DEFAULT_REGION,
                        help=f"AWS region, ignored for azure/local (default: {DEFAULT_REGION})")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX,
                        help=f"Table name prefix (default: {DEFAULT_PREFIX})")
    parser.add_argument("--use-case", default="all", choices=["all", "uc1", "uc2"],
                        help="Which use case's tables to seed (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be written without calling any cloud")
    parser.add_argument("--emit-json", metavar="DIR", default=None,
                        help="Write rows to JSON files in DIR instead of a cloud")
    args = parser.parse_args()

    return seed(args.cloud, args.region, args.prefix, args.use_case,
                args.dry_run, args.emit_json)


if __name__ == "__main__":
    sys.exit(main())
