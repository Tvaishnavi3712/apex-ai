"""
Azure Cosmos DB adapter — the Azure implementation of Apex's table store.

Drop-in replacement for the AWS `CosmosService`. It exposes the SAME async
interface (get_item / put_item / update_item / delete_item / query / scan /
batch_write) so none of the ~23 call sites in `api/` need to change.

Design notes
------------
* Auth is **Entra ID via DefaultAzureCredential** — no keys, no connection
  strings. Locally this uses your `az login` session; in Azure it uses the
  Container App's managed identity. The Cosmos account is created with
  `disableLocalAuth: true`, so key auth is not even possible.
* The account is **private** (ALZ policy `Deny-PublicPaaSEndpoints`), so it is
  only reachable from inside the VNet. For local development set
  `USE_LOCAL_MOCK=true` to fall back to the local persisted store.
* Logical table names (`apex-ai-platform-playbooks`) map to Cosmos containers
  (`playbooks`) by stripping the configured prefix.
* `scan()` paginates through ALL results — a page size is not a result limit.
  This is required for correct list endpoints.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


def _load_mock(table_name: str):
    """Lazy import of the shared in-memory mock (avoids a circular import)."""
    from services.local_store import LocalStore
    return LocalStore(table_name)


def convert_decimals(obj: Any) -> Any:
    """Lazy passthrough to the shared Decimal->native converter."""
    from services.local_store import convert_decimals as _cd
    return _cd(obj)

# Table-name prefix used on Azure; stripped to derive the Cosmos container name.
TABLE_PREFIX = os.environ.get("APEX_TABLE_PREFIX", "apex-ai-platform-")

# Containers whose partition key is NOT /id (must match infrastructure/azure/main.bicep).
PARTITION_KEYS: Dict[str, str] = {
    "playbooks": "industry",
    "blueprints": "industry",
    "simulator-scenarios": "scenario_id",
}


def container_name_for(table_name: str) -> str:
    """`apex-ai-platform-playbooks` -> `playbooks`."""
    return table_name[len(TABLE_PREFIX):] if table_name.startswith(TABLE_PREFIX) else table_name


class CosmosService:
    """Cosmos DB implementation of the Apex table-store port."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.container_name = container_name_for(table_name)
        self.partition_field = PARTITION_KEYS.get(self.container_name, "id")

        # Escape hatch for local dev without VNet access.
        self._use_mock = os.environ.get("USE_LOCAL_MOCK", "false").lower() == "true"
        self._mock_service = _load_mock(table_name) if self._use_mock else None

        self._container = None  # lazily created
        if not self._use_mock:
            logger.debug("cosmos.init", container=self.container_name)

    # ── connection ───────────────────────────────────────────────────────────
    def _get_container(self):
        """Lazily build the Cosmos client so import never triggers a network call."""
        if self._container is not None:
            return self._container

        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential

        endpoint = os.environ.get("AZURE_COSMOS_ENDPOINT")
        database = os.environ.get("AZURE_COSMOS_DATABASE", "apex")
        if not endpoint:
            raise RuntimeError(
                "AZURE_COSMOS_ENDPOINT is not set. Set it in backend/.env.azure, "
                "or set USE_LOCAL_MOCK=true for local development."
            )

        client = CosmosClient(endpoint, credential=DefaultAzureCredential())
        self._container = client.get_database_client(database).get_container_client(self.container_name)
        return self._container

    def _pk_of(self, item: Dict[str, Any]) -> Any:
        """Partition-key value for an item, defaulting to its id."""
        return item.get(self.partition_field, item.get("id"))

    @staticmethod
    def _strip_system_fields(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Remove Cosmos bookkeeping (_rid/_etag/…) so callers see clean records."""
        if not doc:
            return doc
        return {k: v for k, v in doc.items() if not k.startswith("_")}

    # ── CRUD ─────────────────────────────────────────────────────────────────
    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if self._use_mock:
            return await self._mock_service.get_item(key)

        from azure.cosmos import exceptions

        item_id = key.get("id") or next(iter(key.values()))
        try:
            doc = self._get_container().read_item(item=item_id, partition_key=key.get(self.partition_field, item_id))
            return self._strip_system_fields(doc)
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError:
            # Partition key unknown to the caller — fall back to a point query.
            rows = await self.scan(filters={"id": item_id}, limit=1)
            return rows[0] if rows else None

    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        if self._use_mock:
            return await self._mock_service.put_item(item)

        payload = convert_decimals(dict(item))
        # Cosmos requires a string `id`.
        if "id" not in payload:
            for candidate in ("playbook_id", "blueprint_id", "agent_id", "action_id",
                              "scenario_id", "request_id", "work_item_id"):
                if candidate in payload:
                    payload["id"] = str(payload[candidate])
                    break
        payload["id"] = str(payload.get("id", ""))
        if not payload["id"]:
            raise ValueError(f"Cannot write to {self.container_name}: item has no 'id'")

        self._get_container().upsert_item(payload)
        return payload

    async def update_item(self, key: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        if self._use_mock:
            return await self._mock_service.update_item(key, updates)

        current = await self.get_item(key) or dict(key)
        current.update(convert_decimals(updates))
        return await self.put_item(current)

    async def delete_item(self, key: Dict[str, Any]) -> None:
        if self._use_mock:
            return await self._mock_service.delete_item(key)

        from azure.cosmos import exceptions

        item_id = key.get("id") or next(iter(key.values()))
        try:
            self._get_container().delete_item(
                item=item_id, partition_key=key.get(self.partition_field, item_id)
            )
        except exceptions.CosmosResourceNotFoundError:
            pass

    # ── queries ──────────────────────────────────────────────────────────────
    async def query(
        self,
        key_condition: Dict[str, Any],
        filter_expression: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if self._use_mock:
            return await self._mock_service.query(key_condition, filter_expression, limit)

        filters = {**(key_condition or {}), **(filter_expression or {})}
        return await self.scan(filters=filters, limit=limit)

    async def scan(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Full scan with optional equality filters.

        Paginates through ALL pages — matching the AWS behaviour where a page
        limit must never be mistaken for a result limit.
        """
        if self._use_mock:
            return await self._mock_service.scan(filters, limit)

        where, params = "", []
        if filters:
            clauses = []
            for i, (field, value) in enumerate(filters.items()):
                clauses.append(f"c.{field} = @p{i}")
                params.append({"name": f"@p{i}", "value": value})
            where = " WHERE " + " AND ".join(clauses)

        sql = f"SELECT * FROM c{where}"

        results: List[Dict[str, Any]] = []
        try:
            pages = self._get_container().query_items(
                query=sql,
                parameters=params or None,
                enable_cross_partition_query=True,
                max_item_count=100,
            )
            for doc in pages:                      # SDK iterator handles continuation tokens
                clean = self._strip_system_fields(doc)
                if clean:
                    results.append(clean)
                if limit and len(results) >= limit:
                    break
        except Exception as e:                     # noqa: BLE001 — list endpoints must not 500
            logger.warning("cosmos.scan_failed", container=self.container_name, error=str(e))
            return []

        return results

    async def batch_write(self, items: List[Dict[str, Any]]) -> None:
        if self._use_mock:
            return await self._mock_service.batch_write(items)
        for item in items:
            await self.put_item(item)


# Backwards-compatible alias: existing code does `CosmosService(table)`.
# On Azure that now returns a Cosmos-backed store with the identical interface.
TableStore = CosmosService
