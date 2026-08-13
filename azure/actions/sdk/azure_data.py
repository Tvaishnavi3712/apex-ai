"""
Table-resource compatibility shim backed by Azure Cosmos DB.

Action handlers were written against the AWS Cosmos DB resource API:

    cosmos_db = boto3.resource("cosmos_db")
    table    = cosmos_db.Table("apex-ai-platform-suppliers")
    table.get_item(Key={"id": "S-1"})["Item"]
    table.put_item(Item={...})
    table.query(KeyConditionExpression=...)

This module exposes the same surface over Cosmos DB, so handler bodies work
unchanged on Azure — only the resource construction differs:

    # AWS build
    cosmos_db = boto3.resource("cosmos_db")
    # Azure build
    tables = get_table_resource()

Logical table names (`apex-ai-platform-suppliers`) map to Cosmos containers
(`suppliers`) by stripping `APEX_TABLE_PREFIX`.

Auth is Entra ID (DefaultAzureCredential) — no keys. When Cosmos is unreachable
(it sits behind a private endpoint) set `USE_LOCAL_MOCK=true` to use the same
on-disk store the backend uses locally.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

TABLE_PREFIX = os.environ.get("APEX_TABLE_PREFIX", "apex-ai-platform-")

# Containers whose partition key is not /id (mirrors infrastructure/azure/main.bicep).
PARTITION_KEYS: Dict[str, str] = {
    "playbooks": "industry",
    "blueprints": "industry",
    "simulator-scenarios": "scenario_id",
}


def _container_name(table_name: str) -> str:
    return table_name[len(TABLE_PREFIX):] if table_name.startswith(TABLE_PREFIX) else table_name


def _use_mock() -> bool:
    return os.environ.get("USE_LOCAL_MOCK", "false").lower() == "true"


def _mock_path() -> str:
    return os.environ.get("APEX_MOCK_FILE", "/tmp/apex-mock-store.json")


def _load_mock() -> Dict[str, Dict[str, Any]]:
    try:
        with open(_mock_path()) as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return {}


def _save_mock(store: Dict[str, Dict[str, Any]]) -> None:
    try:
        tmp = _mock_path() + ".tmp"
        with open(tmp, "w") as f:
            json.dump(store, f, default=str)
        os.replace(tmp, _mock_path())
    except Exception:  # noqa: BLE001
        pass


class _Table:
    """Mimics a boto3 Cosmos DB Table over a Cosmos container."""

    def __init__(self, table_name: str) -> None:
        self.name = table_name
        self.container_name = _container_name(table_name)
        self.partition_field = PARTITION_KEYS.get(self.container_name, "id")
        self._container = None

    # ── connection ───────────────────────────────────────────────────────────
    def _get(self):
        if self._container is not None:
            return self._container
        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential

        endpoint = os.environ.get("AZURE_COSMOS_ENDPOINT")
        if not endpoint:
            raise RuntimeError("AZURE_COSMOS_ENDPOINT is not set")
        client = CosmosClient(endpoint, credential=DefaultAzureCredential())
        db = client.get_database_client(os.environ.get("AZURE_COSMOS_DATABASE", "apex"))
        self._container = db.get_container_client(self.container_name)
        return self._container

    # ── Cosmos DB-shaped API ──────────────────────────────────────────────────
    def get_item(self, Key: Optional[Dict[str, Any]] = None, **_: Any) -> Dict[str, Any]:  # noqa: N803
        key = Key or {}
        item_id = str(key.get("id") or (next(iter(key.values())) if key else ""))

        if _use_mock():
            rows = _load_mock().get(self.name, {})
            item = rows.get(item_id)
            return {"Item": item} if item else {}

        from azure.cosmos import exceptions
        try:
            doc = self._get().read_item(item=item_id, partition_key=key.get(self.partition_field, item_id))
            return {"Item": {k: v for k, v in doc.items() if not k.startswith("_")}}
        except exceptions.CosmosResourceNotFoundError:
            return {}
        except Exception:  # noqa: BLE001 — fall back to a filtered scan
            rows = self.scan(Limit=1, _filters={"id": item_id}).get("Items", [])
            return {"Item": rows[0]} if rows else {}

    def put_item(self, Item: Optional[Dict[str, Any]] = None, **_: Any) -> Dict[str, Any]:  # noqa: N803
        item = dict(Item or {})
        if "id" not in item:
            for c in ("playbook_id", "blueprint_id", "agent_id", "action_id",
                      "scenario_id", "request_id", "work_item_id", "supplier_id"):
                if c in item:
                    item["id"] = str(item[c])
                    break
        item["id"] = str(item.get("id", ""))

        if _use_mock():
            store = _load_mock()
            store.setdefault(self.name, {})[item["id"]] = item
            _save_mock(store)
            return {"Attributes": item}

        self._get().upsert_item(item)
        return {"Attributes": item}

    def update_item(
        self,
        Key: Optional[Dict[str, Any]] = None,          # noqa: N803
        AttributeUpdates: Optional[Dict[str, Any]] = None,  # noqa: N803
        **kwargs: Any,
    ) -> Dict[str, Any]:
        current = self.get_item(Key=Key).get("Item") or dict(Key or {})
        if AttributeUpdates:
            for k, v in AttributeUpdates.items():
                current[k] = v.get("Value", v) if isinstance(v, dict) else v
        # Minimal UpdateExpression support: "SET a = :x, b = :y"
        expr = kwargs.get("UpdateExpression", "")
        vals = kwargs.get("ExpressionAttributeValues", {}) or {}
        if expr.upper().startswith("SET"):
            for part in expr[3:].split(","):
                if "=" not in part:
                    continue
                field, placeholder = (x.strip() for x in part.split("=", 1))
                if placeholder in vals:
                    current[field.lstrip("#")] = vals[placeholder]
        self.put_item(Item=current)
        return {"Attributes": current}

    def delete_item(self, Key: Optional[Dict[str, Any]] = None, **_: Any) -> Dict[str, Any]:  # noqa: N803
        key = Key or {}
        item_id = str(key.get("id") or (next(iter(key.values())) if key else ""))
        if _use_mock():
            store = _load_mock()
            store.get(self.name, {}).pop(item_id, None)
            _save_mock(store)
            return {}
        from azure.cosmos import exceptions
        try:
            self._get().delete_item(item=item_id, partition_key=key.get(self.partition_field, item_id))
        except exceptions.CosmosResourceNotFoundError:
            pass
        return {}

    def scan(self, Limit: int = 500, _filters: Optional[Dict[str, Any]] = None, **_: Any) -> Dict[str, Any]:  # noqa: N803
        if _use_mock():
            rows = list(_load_mock().get(self.name, {}).values())
            if _filters:
                rows = [r for r in rows if all(r.get(k) == v for k, v in _filters.items())]
            rows = rows[:Limit]
            return {"Items": rows, "Count": len(rows)}

        where, params = "", []
        if _filters:
            clauses = []
            for i, (k, v) in enumerate(_filters.items()):
                clauses.append(f"c.{k} = @p{i}")
                params.append({"name": f"@p{i}", "value": v})
            where = " WHERE " + " AND ".join(clauses)
        try:
            docs = self._get().query_items(
                query=f"SELECT * FROM c{where}",
                parameters=params or None,
                enable_cross_partition_query=True,
            )
            items: List[Dict[str, Any]] = []
            for d in docs:
                items.append({k: v for k, v in d.items() if not k.startswith("_")})
                if len(items) >= Limit:
                    break
            return {"Items": items, "Count": len(items)}
        except Exception:  # noqa: BLE001 — handlers must not hard-fail
            return {"Items": [], "Count": 0}

    def query(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Equality-only query support.

        Accepts `_filters={...}` directly, or a boto3 `KeyConditionExpression`
        built from `Key('field').eq(value)`, from which the field/value pair is
        extracted best-effort.
        """
        filters = kwargs.get("_filters") or {}
        kce = kwargs.get("KeyConditionExpression")
        if kce is not None and not filters:
            if hasattr(kce, "as_filter"):                 # native Key
                filters.update(kce.as_filter())
            else:                                          # tolerate other shapes
                try:
                    name = getattr(getattr(kce, "_values", [None])[0], "name", None)
                    value = getattr(kce, "_values", [None, None])[1]
                    if name is not None:
                        filters[name] = value
                except Exception:  # noqa: BLE001
                    pass
        return self.scan(Limit=kwargs.get("Limit", 500), _filters=filters or None)

    # batch_writer() context manager parity
    def batch_writer(self):
        table = self

        class _Batch:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def put_item(self, Item=None, **_):  # noqa: N803
                return table.put_item(Item=Item)

            def delete_item(self, Key=None, **_):  # noqa: N803
                return table.delete_item(Key=Key)

        return _Batch()


class AzureTableResource:
    """Mimics `get_table_resource()`."""

    def Table(self, name: str) -> _Table:  # noqa: N802 — boto3 casing kept deliberately
        return _Table(name)


_resource: Optional[AzureTableResource] = None


def get_table_resource(*_: Any, **__: Any) -> AzureTableResource:
    """Process-wide Cosmos DB-compatible resource backed by Cosmos DB."""
    global _resource
    if _resource is None:
        _resource = AzureTableResource()
    return _resource


class Key:
    """
    Native key-condition builder (replaces the AWS `conditions.Key` helper).

    Supports the equality form used across Apex handlers:

        Key("supplier_id").eq("S-1")

    `_Table.query()` reads `.field` / `.value` off the result, so no AWS SDK
    dependency is needed.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.field = name
        self.value: Any = None
        self.op = "eq"

    def eq(self, value: Any) -> "Key":
        self.value = value
        self.op = "eq"
        return self

    def begins_with(self, value: Any) -> "Key":
        self.value = value
        self.op = "begins_with"
        return self

    def as_filter(self) -> Dict[str, Any]:
        return {self.field: self.value}

    def __repr__(self) -> str:  # pragma: no cover
        return f"Key({self.field}{self.op}{self.value!r})"
