"""
AWS admin endpoints — provision the Cosmos DB tables action handlers expect,
and introspect what's already in the account.
"""

from fastapi import APIRouter, Query
from typing import Any, Dict

from services.azure_provisioner import provision_all, TABLE_SPECS

router = APIRouter()


@router.post("/provision")
async def provision_tables(region: str = Query("us-east-1")) -> Dict[str, Any]:
    """
    Create + seed every Cosmos DB table that action handlers expect.

    Idempotent: tables that already exist are skipped; rows that already
    exist (by primary key) are skipped.

    Returns a summary with created / existing / seeded counts.
    """
    return provision_all(region=region)


@router.get("/table-specs")
async def list_table_specs() -> Dict[str, Any]:
    """Return the list of tables the provisioner manages + their row fixtures."""
    return {
        "count": len(TABLE_SPECS),
        "tables": [
            {
                "name": name,
                "hash_key": hash_key,
                "hash_type": hash_type,
                "sample_row_count": len(items),
            }
            for name, hash_key, hash_type, items in TABLE_SPECS
        ],
    }
