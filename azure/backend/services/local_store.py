"""
Local persisted store — the offline fallback for Apex on Azure.

Cosmos DB sits behind a private endpoint (ALZ policy `Deny-PublicPaaSEndpoints`)
and is not reachable from a laptop, so local development runs against this
store. It persists to disk, so seeded data survives a restart.
"""

from typing import Dict, Any, List, Optional
import json
from decimal import Decimal
import os



class DecimalEncoder(json.JSONEncoder):
    """Handle Decimal types from Cosmos DB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def convert_decimals(obj):
    """Convert Decimal types to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj


# In-memory storage for local development
_mock_storage: Dict[str, Dict[str, Any]] = {}

# ─────────────────────────────────────────────────────────────────────────────
# Local-mock disk persistence.
#
# Cosmos DB is private (ALZ policy `Deny-PublicPaaSEndpoints`) and therefore not
# reachable from a laptop, so local development runs against the in-memory mock.
# Persisting it to disk means seeded data survives a backend restart, which makes
# the local Azure build genuinely usable instead of resetting to empty.
# Set APEX_MOCK_PERSIST=false to opt out (pure in-memory).
# ─────────────────────────────────────────────────────────────────────────────
_MOCK_PERSIST = os.environ.get("APEX_MOCK_PERSIST", "true").lower() == "true"
_MOCK_FILE = os.environ.get("APEX_MOCK_FILE", "/tmp/apex-mock-store.json")


def _mock_load() -> None:
    """Hydrate the mock store from disk (best-effort)."""
    if not _MOCK_PERSIST or not os.path.exists(_MOCK_FILE):
        return
    try:
        with open(_MOCK_FILE, "r") as f:
            _mock_storage.update(json.load(f))
    except Exception:  # noqa: BLE001 — never block startup on a bad cache file
        pass


def _mock_save() -> None:
    """Flush the mock store to disk (best-effort)."""
    if not _MOCK_PERSIST:
        return
    try:
        tmp = f"{_MOCK_FILE}.tmp"
        with open(tmp, "w") as f:
            json.dump(_mock_storage, f, default=str)
        os.replace(tmp, _MOCK_FILE)
    except Exception:  # noqa: BLE001
        pass


_mock_load()


class LocalStore:
    """In-memory + disk-persisted store used when Cosmos is unreachable."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        if table_name not in _mock_storage:
            _mock_storage[table_name] = {}

    def _get_primary_key(self, item: Dict[str, Any]) -> str:
        """Get primary key from item - handles different table schemas"""
        key_fields = ['agent_id', 'work_item_id', 'action_id', 'playbook_id', 'blueprint_id', 'session_id', 'document_id', 'id']
        for field in key_fields:
            if field in item:
                return str(item[field])
        return str(hash(json.dumps(item, sort_keys=True, default=str)))

    async def get_item(self, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a single item by key"""
        pk = list(key.values())[0]
        return _mock_storage[self.table_name].get(str(pk))

    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Put an item into the table"""
        pk = self._get_primary_key(item)
        _mock_storage[self.table_name][pk] = item
        _mock_save()
        return item

    async def update_item(self, key: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item"""
        pk = list(key.values())[0]
        if str(pk) in _mock_storage[self.table_name]:
            _mock_storage[self.table_name][str(pk)].update(updates)
            _mock_save()
            return _mock_storage[self.table_name][str(pk)]
        return {}

    async def delete_item(self, key: Dict[str, Any]) -> None:
        """Delete an item"""
        pk = list(key.values())[0]
        if str(pk) in _mock_storage[self.table_name]:
            del _mock_storage[self.table_name][str(pk)]
            _mock_save()

    async def query(self, key_condition: Dict[str, Any], filter_expression: Optional[Dict[str, Any]] = None,
                    index_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Query items"""
        results = []
        for item in _mock_storage[self.table_name].values():
            match = True
            for field, value in key_condition.items():
                if item.get(field) != value:
                    match = False
                    break
            if match and filter_expression:
                for field, value in filter_expression.items():
                    if item.get(field) != value:
                        match = False
                        break
            if match:
                results.append(item)
                if len(results) >= limit:
                    break
        return results

    async def scan(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Scan table with optional filters"""
        results = []
        for item in _mock_storage[self.table_name].values():
            if filters:
                match = True
                for field, value in filters.items():
                    if item.get(field) != value:
                        match = False
                        break
                if match:
                    results.append(item)
            else:
                results.append(item)
            if len(results) >= limit:
                break
        return results

    async def batch_write(self, items: List[Dict[str, Any]]) -> None:
        """Batch write items"""
        for item in items:
            await self.put_item(item)




# Back-compat alias used internally by the Cosmos adapter.
MockCosmosService = LocalStore
