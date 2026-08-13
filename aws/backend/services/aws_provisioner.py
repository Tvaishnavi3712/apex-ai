"""
AWS Provisioner — create and seed the DynamoDB tables every action handler
expects, against the user's real AWS account.

All tables use on-demand (PAY_PER_REQUEST) billing so there's no provisioned-
capacity cost. Creation + seeding is idempotent: if a table already exists
we skip create; if a row already exists we skip put.

One-shot entry points:

  • `provision_all(region="us-east-1") -> dict`
    Creates every table. Seeds sample data where present.

  • `/api/v1/aws/provision` (added in api/aws_admin.py)
    Same thing over HTTP so the frontend can trigger it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Tuple

import boto3
from botocore.exceptions import ClientError


def _to_ddb(obj: Any) -> Any:
    """Recursively convert floats → Decimal for DynamoDB compatibility."""
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: _to_ddb(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_ddb(v) for v in obj]
    return obj


# ─────────────────── table specs ───────────────────

# Each spec: (table_name, hash_key_name, hash_key_type, sample_items[])
# Sort keys aren't required by any handler we scanned (all use get_item with
# single-hash-key lookups). If a handler later needs a sort key we can extend.
TableSpec = Tuple[str, str, str, List[Dict[str, Any]]]


def _po(po_number: str, amount: float, vendor_id: str, status: str = "open") -> Dict[str, Any]:
    return {
        "po_number": po_number,
        "total_amount": amount,
        "vendor_id": vendor_id,
        "vendor_name": f"Vendor {vendor_id}",
        "status": status,
        "currency": "USD",
    }


def _vendor(vid: str, name: str, status: str = "active", category: str = "supplies") -> Dict[str, Any]:
    return {
        "vendor_id": vid,
        "vendor_name": name,
        "status": status,
        "payment_terms": "NET30",
        "category": category,
        "tax_id": f"12-345{vid[-4:]}",
    }


def _patient(pid: str, name: str) -> Dict[str, Any]:
    return {
        "patient_id": pid,
        "name": name,
        "dob": "1975-04-12",
        "insurance_id": "INS-001",
        "active": True,
    }


def _member(mid: str, plan: str = "PPO-GOLD") -> Dict[str, Any]:
    return {
        "member_id": mid,
        "status": "active",
        "plan": plan,
        "effective_date": "2025-01-01",
        "termination_date": None,
        "coverage_level": "family",
    }


def _provider(npi: str, name: str) -> Dict[str, Any]:
    return {
        "npi": npi,
        "provider_name": name,
        "specialty": "Internal Medicine",
        "network_tier": "in_network",
        "active": True,
        "taxonomy": "207R00000X",
    }


def _claim(cid: str, amount: float) -> Dict[str, Any]:
    return {
        "claim_id": cid,
        "member_id": "MEM-1001",
        "provider_npi": "1234567890",
        "billed_amount": amount,
        "status": "pending",
        "service_date": "2026-03-15",
    }


TABLE_SPECS: List[TableSpec] = [
    # ── Financial Services ──
    ("apex-ai-platform-purchase-orders", "po_number", "S", [
        # First row is the demo the user asked for.
        _po("PO-123", 500.00, "VEN-001"),
        _po("PO-124", 1250.50, "VEN-002"),
        _po("PO-2024-0891", 87400.00, "VEN-003"),
        _po("PO-5000", 1000.00, "VEN-001"),
        _po("PO-CLOSED-1", 200.00, "VEN-004", status="closed"),
    ]),
    ("apex-ai-platform-approved-vendors", "vendor_id", "S", [
        _vendor("VEN-001", "Acme Corp"),
        _vendor("VEN-002", "Globex Corp"),
        _vendor("VEN-003", "Initech"),
        _vendor("VEN-004", "Hooli",     status="inactive"),
        _vendor("VEN-005", "Umbrella",  category="chemicals"),
    ]),

    # ── Healthcare Payers ──
    ("apex-claims", "claim_id", "S", [
        _claim("CLM-001", 1200.00),
        _claim("CLM-002", 450.75),
        _claim("CL-8821", 3200.00),
    ]),
    ("apex-eligibility", "member_id", "S", [
        _member("MEM-1001"),
        _member("MEM-1002", plan="HMO-SILVER"),
    ]),
    ("apex-provider-network", "npi", "S", [
        _provider("1234567890", "Dr. Smith"),
        _provider("9876543210", "Dr. Jones"),
    ]),
    ("apex-providers", "npi", "S", [
        _provider("1234567890", "Dr. Smith"),
        _provider("9876543210", "Dr. Jones"),
    ]),
    ("apex-ai-platform-substitutes", "drug_id", "S", [
        {"drug_id": "DRUG-001", "substitute_ids": ["DRUG-002", "DRUG-003"], "reason": "formulary"},
    ]),

    # ── Healthcare Providers ──
    ("apex-patients", "patient_id", "S", [
        _patient("PAT-1001", "Jane Doe"),
        _patient("PAT-1002", "John Roe"),
    ]),
    ("apex-appointments", "appointment_id", "S", [
        {"appointment_id": "APT-001", "patient_id": "PAT-1001", "provider_npi": "1234567890",
         "scheduled_at": "2026-05-01T10:00:00Z", "status": "booked"},
    ]),
    ("apex-referrals", "referral_number", "S", [
        {"referral_number": "REF-001", "patient_id": "PAT-1001", "specialty": "Cardiology",
         "status": "approved"},
    ]),

    # ── Retail ──
    ("apex-retail-transactions", "transaction_id", "S", [
        {"transaction_id": "TXN-001", "customer_id": "CUS-001", "amount": 125.00,
         "currency": "USD", "store_id": "STO-1", "status": "completed"},
    ]),
    ("apex-retail-customers", "customer_id", "S", [
        {"customer_id": "CUS-001", "name": "Alice Buyer", "loyalty_tier": "gold",
         "lifetime_value": 4200.00, "risk_score": 0.1},
    ]),
    ("apex-retail-inventory", "sku", "S", [
        {"sku": "SKU-ABC-001", "name": "Widget A", "on_hand": 150, "reorder_point": 30},
    ]),
    ("apex-retail-refunds", "transaction_id", "S", [
        {"transaction_id": "TXN-001", "refund_amount": 25.00, "status": "approved"},
    ]),
    ("apex-store-credits", "customer_id", "S", [
        {"customer_id": "CUS-001", "balance": 50.00, "currency": "USD"},
    ]),
    ("apex-inventory", "sku", "S", [
        {"sku": "SKU-ABC-001", "on_hand": 150, "reserved": 5, "location": "WHSE-1"},
    ]),

    # ── Manufacturing ──
    ("apex-ai-platform-inventory", "sku", "S", [
        {"sku": "SKU-MFG-1", "on_hand": 1000, "reorder_point": 100, "lead_time_days": 14},
    ]),
    ("apex-ai-platform-carriers", "carrier_scac", "S", [
        {"carrier_scac": "UPSN", "name": "UPS",    "on_time_pct": 96.5},
        {"carrier_scac": "FDEG", "name": "FedEx",  "on_time_pct": 95.1},
    ]),
    ("apex-ai-platform-specifications", "part_number", "S", [
        {"part_number": "P-1001", "material": "aluminum", "tolerance_mm": 0.05, "revision": "B"},
    ]),
    ("apex-quality", "part_number", "S", [
        {"part_number": "P-1001", "defect_rate": 0.002, "last_inspection": "2026-04-10"},
    ]),

    # ── HR ──
    ("apex-ai-platform-job-requisitions", "job_id", "S", [
        {"job_id": "REQ-001", "title": "Senior Engineer", "department": "Platform",
         "level": "L5", "open": True},
    ]),
    ("apex-ai-platform-salary-bands", "level", "S", [
        {"level": "L4", "min": 120000, "mid": 140000, "max": 160000},
        {"level": "L5", "min": 150000, "mid": 175000, "max": 200000},
    ]),

    # ── Airlines / Supply Chain ──
    ("apex-airline-reservations", "reservation_id", "S", [
        {"reservation_id": "RES-001", "passenger": "Alice Flyer", "flight_number": "AA100",
         "status": "confirmed"},
    ]),
    ("apex-shipments", "shipment_id", "S", [
        {"shipment_id": "SHP-001", "carrier_scac": "UPSN", "origin": "JFK", "destination": "SFO",
         "status": "in_transit"},
    ]),

    # ── Platform infrastructure ──
    ("apex-blueprints", "blueprint_id", "S", []),
    ("apex-work-items", "work_item_id", "S", []),
    ("apex-audit", "log_id", "S", []),
    ("apex-inventory-audit", "audit_id", "S", []),
    ("apex-alerts", "alert_id", "S", []),
    ("apex-cars", "car_id", "S", []),
]


# ─────────────────── provisioner ───────────────────

def _table_exists(client, name: str) -> bool:
    try:
        client.describe_table(TableName=name)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise


def _create_table(client, name: str, hash_key: str, hash_type: str) -> str:
    try:
        client.create_table(
            TableName=name,
            KeySchema=[{"AttributeName": hash_key, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": hash_key, "AttributeType": hash_type}],
            BillingMode="PAY_PER_REQUEST",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            return "already-exists"
        raise
    # Wait until ACTIVE (typically 5–10s with on-demand).
    client.get_waiter("table_exists").wait(TableName=name, WaiterConfig={"Delay": 2, "MaxAttempts": 40})
    return "created"


def _seed_items(resource, name: str, hash_key: str, items: List[Dict[str, Any]]) -> int:
    """Put items, skipping ones whose hash-key value already exists."""
    if not items:
        return 0
    table = resource.Table(name)
    seeded = 0
    for item in items:
        key_val = item.get(hash_key)
        if key_val is None:
            continue
        # ConditionExpression ensures we don't overwrite existing rows
        try:
            table.put_item(
                Item=_to_ddb(item),
                ConditionExpression=f"attribute_not_exists(#k)",
                ExpressionAttributeNames={"#k": hash_key},
            )
            seeded += 1
        except ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            # row exists already, keep going
    return seeded


def provision_all(region: str = "us-east-1", specs: List[TableSpec] | None = None) -> Dict[str, Any]:
    """Create every expected table and seed sample rows. Idempotent."""
    client = boto3.client("dynamodb", region_name=region)
    resource = boto3.resource("dynamodb", region_name=region)

    use_specs = specs if specs is not None else TABLE_SPECS

    created: List[str] = []
    already: List[str] = []
    seeded_counts: Dict[str, int] = {}
    errors: List[Dict[str, str]] = []

    for name, hash_key, hash_type, items in use_specs:
        try:
            if _table_exists(client, name):
                already.append(name)
            else:
                status = _create_table(client, name, hash_key, hash_type)
                (created if status == "created" else already).append(name)

            seeded_counts[name] = _seed_items(resource, name, hash_key, items)
        except Exception as e:  # noqa: BLE001
            errors.append({"table": name, "error": str(e)})

    return {
        "region": region,
        "created_tables": created,
        "already_existing_tables": already,
        "seeded_row_counts": seeded_counts,
        "total_rows_seeded": sum(seeded_counts.values()),
        "errors": errors,
    }


if __name__ == "__main__":
    import json
    import sys
    region = sys.argv[1] if len(sys.argv) > 1 else "us-east-1"
    result = provision_all(region=region)
    print(json.dumps(result, indent=2, default=str))
