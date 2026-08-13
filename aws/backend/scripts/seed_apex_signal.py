#!/usr/bin/env python3
"""
Seed ApexSignal DynamoDB tables from the supply-chain synthetic-data files.

Tables:
  apex-ai-platform-predictive-events   ← predictive_events.json
  apex-ai-platform-suppliers           ← suppliers.json
  apex-ai-platform-agent-audit-log     ← agent_audit_log.json
  apex-ai-platform-inventory-bom       ← inventory_bom.json
  apex-ai-platform-purchase-orders     ← purchase_orders.json

Tables are created on demand (on-demand billing) — safe to re-run.
"""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REGION = os.environ.get("AWS_REGION", "us-east-1")
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "synthetic-data" / "supply-chain"

TABLES = [
    # table_name,                                     pk,                       source_file,                    row_factory
    ("apex-ai-platform-predictive-events",           "event_id",               "predictive_events.json",        lambda rows: rows),
    ("apex-ai-platform-suppliers",                   "supplier_id",            "suppliers.json",                lambda rows: rows),
    ("apex-ai-platform-agent-audit-log",             "run_id",                 "agent_audit_log.json",          lambda rows: rows),
    ("apex-ai-platform-purchase-orders",             "po_number",              "purchase_orders.json",          lambda rows: rows),
    # inventory_bom is a composite doc (materials + plants + products + bom + inventory)
    # — flatten as one row per logical entity with a type-discriminator PK.
    ("apex-ai-platform-inventory-bom",               "entity_id",              "inventory_bom.json",            "bom_flatten"),
]


def _flatten_bom(doc: dict) -> list[dict]:
    rows: list[dict] = []
    for m in doc.get("materials", []):
        rows.append({"entity_id": f"MATERIAL#{m['material_id']}", "kind": "material", **m})
    for p in doc.get("plants", []):
        rows.append({"entity_id": f"PLANT#{p['plant_id']}", "kind": "plant", **p})
    for p in doc.get("products", []):
        rows.append({"entity_id": f"PRODUCT#{p['product_id']}", "kind": "product", **p})
    for b in doc.get("bom", []):
        rows.append({"entity_id": f"BOM#{b['product_id']}#{b['material_id']}", "kind": "bom", **b})
    for i in doc.get("inventory", []):
        rows.append({"entity_id": f"INV#{i['material_id']}#{i['plant_id']}", "kind": "inventory", **i})
    return rows


def _to_ddb(v):
    if isinstance(v, float):  return Decimal(str(round(v, 6)))
    if isinstance(v, dict):   return {k: _to_ddb(x) for k, x in v.items()}
    if isinstance(v, list):   return [_to_ddb(x) for x in v]
    return v


def ensure_table(client, name: str, pk: str) -> None:
    try:
        client.describe_table(TableName=name)
        print(f"  [ddb] {name} exists")
        return
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
    print(f"  [ddb] creating {name} ...")
    client.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": pk, "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": pk, "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    client.get_waiter("table_exists").wait(TableName=name, WaiterConfig={"Delay": 5, "MaxAttempts": 40})
    print(f"  [ddb] {name} READY")


def batch_put(table, items: list[dict]) -> None:
    with table.batch_writer() as bw:
        for it in items:
            bw.put_item(Item=_to_ddb(it))


def main() -> int:
    client = boto3.client("dynamodb", region_name=REGION)
    ddb    = boto3.resource("dynamodb", region_name=REGION)

    print(f"\n{'=' * 60}\nSEEDING ApexSignal · {REGION}\n{'=' * 60}")
    for tbl_name, pk, src, factory in TABLES:
        ensure_table(client, tbl_name, pk)
        doc = json.loads((DATA_DIR / src).read_text())
        if factory == "bom_flatten":
            rows = _flatten_bom(doc)
        else:
            rows = factory(doc)
        if not isinstance(rows, list):
            rows = [rows]
        if not rows:
            print(f"  [skip] {tbl_name}: no rows from {src}")
            continue
        batch_put(ddb.Table(tbl_name), rows)
        print(f"  [ddb] {tbl_name:40s}  {len(rows):>4d} rows  ({src})")

    print(f"\n{'=' * 60}\nDone.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
