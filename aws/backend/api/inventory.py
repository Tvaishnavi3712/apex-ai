"""
Hardware Inventory API — the real servers Apex manages.

Backs the Inventory page and the Redfish console. Every record traces to a
lab artifact produced by the Verizon Far Edge certification campaigns; nothing
here is synthesised. Re-run `scripts/extract_hw_inventory.py` to refresh.

Endpoints
---------
    GET  /servers                     fleet list (light projection)
    GET  /servers/{id}                one server, full evidence
    GET  /servers/{id}/checks         compliance checks, grouped
    GET  /servers/{id}/drift          only what needs action
    POST /servers/{id}/interrogate    run a Redfish walk
    GET  /redfish/catalog             the interrogation endpoint catalog
    GET  /summary                     fleet roll-up

List endpoints skip malformed rows rather than failing the whole response —
one bad record must never cascade into the frontend's error fallback.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.redfish import InventoryData, RedfishClient

log = structlog.get_logger()
router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# models
# ─────────────────────────────────────────────────────────────────────────────

class LiveCredentials(BaseModel):
    """
    Supplied per request to force a real BMC connection.

    Never stored, never logged, never written to disk. Omit entirely and the
    interrogation replays the captured campaign responses.
    """
    host: Optional[str] = Field(None, description="BMC host; defaults to the server's own address")
    username: Optional[str] = None
    password: Optional[str] = None
    verify: bool = Field(False, description="Verify the BMC's TLS certificate (lab certs are self-signed)")


class InterrogateRequest(BaseModel):
    endpoints: Optional[List[str]] = Field(
        None, description="Catalog endpoint ids to fetch; omit for the full walk"
    )
    live: Optional[LiveCredentials] = None


# ─────────────────────────────────────────────────────────────────────────────
# projections
# ─────────────────────────────────────────────────────────────────────────────

LIST_FIELDS = (
    "id", "bmc_ip", "hostname", "vendor", "platform", "bmc_type",
    "bmc_firmware", "bios_version", "status", "last_seen",
    "check_summary", "test_summary",
)


def _to_list_row(server: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Light projection for the fleet list.

    Full records carry every check, test and captured artifact — far more than
    a list needs. Returning None lets the caller skip a row it can't read
    instead of failing the whole request.
    """
    try:
        row = {k: server.get(k) for k in LIST_FIELDS}
        row["evidence_count"] = len(server.get("evidence_files") or [])
        row["firmware_count"] = len(server.get("firmware") or [])
        row["open_findings"] = sum(
            1 for c in (server.get("checks") or [])
            if c.get("result") in ("DRIFT", "WARN", "FAIL")
        )
        return row
    except Exception as e:  # noqa: BLE001 — skip the row, keep the list
        log.warning("inventory.row_skipped", server=server.get("id"), error=str(e))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/servers")
async def list_servers(
    vendor: Optional[str] = Query(None, description="Filter by vendor, e.g. HPE or Dell"),
    status: Optional[str] = Query(None, description="Filter by status, e.g. DRIFT"),
) -> Dict[str, Any]:
    """The managed fleet."""
    rows: List[Dict[str, Any]] = []
    for server in InventoryData.servers():
        row = _to_list_row(server)
        if row is None:
            continue
        if vendor and (row.get("vendor") or "").lower() != vendor.lower():
            continue
        if status and (row.get("status") or "").upper() != status.upper():
            continue
        rows.append(row)

    return {"servers": rows, "count": len(rows)}


@router.get("/summary")
async def fleet_summary() -> Dict[str, Any]:
    """Roll-up for the inventory header tiles."""
    servers = InventoryData.servers()

    by_status: Dict[str, int] = {}
    by_platform: Dict[str, int] = {}
    findings = 0
    for s in servers:
        by_status[s.get("status") or "UNKNOWN"] = by_status.get(s.get("status") or "UNKNOWN", 0) + 1
        plat = s.get("platform") or "Unknown"
        by_platform[plat] = by_platform.get(plat, 0) + 1
        findings += sum(1 for c in (s.get("checks") or [])
                        if c.get("result") in ("DRIFT", "WARN", "FAIL"))

    data = InventoryData.load()
    return {
        "servers": len(servers),
        "by_status": by_status,
        "by_platform": by_platform,
        "open_findings": findings,
        "tests_executed": len(data.get("tests") or []),
        "campaigns": len(data.get("campaigns") or []),
        "redfish_endpoints": len(data.get("redfish_catalog") or []),
        "generated_at": data.get("generated_at"),
        "provenance": data.get("provenance"),
    }


@router.get("/redfish/catalog")
async def redfish_catalog() -> Dict[str, Any]:
    """
    The interrogation catalog: which Redfish endpoints Apex walks, and why.

    Response bodies are omitted here — they can be large. Run an interrogation
    to get them.
    """
    entries = []
    for c in InventoryData.catalog():
        entries.append({
            "seq": c.get("seq"),
            "id": c.get("id"),
            "name": c.get("name"),
            "url": c.get("url"),
            "reason_for_change": c.get("reason_for_change"),
            "required_change": c.get("required_change"),
            "has_response": c.get("response") is not None,
        })
    return {"endpoints": entries, "count": len(entries)}


@router.get("/servers/{server_id}")
async def get_server(server_id: str) -> Dict[str, Any]:
    """
    One server with its full evidence chain.

    404s on an unknown id rather than falling back to another server's record —
    showing the wrong box's configuration would be worse than showing nothing.
    """
    server = InventoryData.server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")
    return server


@router.get("/servers/{server_id}/checks")
async def get_checks(server_id: str) -> Dict[str, Any]:
    """Compliance checks grouped the way the engineers grouped them."""
    server = InventoryData.server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")

    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for check in server.get("checks") or []:
        grouped.setdefault(check.get("category") or "Checks", []).append(check)

    return {
        "server_id": server["id"],
        "bmc_ip": server.get("bmc_ip"),
        "summary": server.get("check_summary"),
        "categories": [{"name": k, "checks": v} for k, v in grouped.items()],
    }


@router.get("/servers/{server_id}/drift")
async def get_drift(server_id: str) -> Dict[str, Any]:
    """
    Only what needs action — the DRIFT / WARN / FAIL checks with their
    remediation, ordered worst first. This is what a job would remediate.
    """
    server = InventoryData.server(server_id)
    if server is None:
        raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")

    severity = {"FAIL": 0, "DRIFT": 1, "WARN": 2}
    items = [c for c in (server.get("checks") or []) if c.get("result") in severity]
    items.sort(key=lambda c: severity.get(c.get("result"), 9))

    return {
        "server_id": server["id"],
        "bmc_ip": server.get("bmc_ip"),
        "hostname": server.get("hostname"),
        "count": len(items),
        "findings": items,
    }


@router.post("/servers/{server_id}/interrogate")
async def interrogate(server_id: str, body: Optional[InterrogateRequest] = None) -> Dict[str, Any]:
    """
    Walk the server's Redfish tree and return every request with its response.

    Replays captured campaign responses by default. Pass `live` credentials to
    dial a reachable BMC instead; those credentials are used for the request
    and discarded.
    """
    body = body or InterrogateRequest()

    live_cfg = None
    if body.live and body.live.username and body.live.password:
        live_cfg = {
            "host": body.live.host or "",
            "username": body.live.username,
            "password": body.live.password,
            "verify": str(body.live.verify).lower(),
        }

    try:
        client = RedfishClient.for_server(server_id, live=live_cfg)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Server not found: {server_id}")

    steps = client.interrogate(only=body.endpoints)

    ok = sum(1 for s in steps if 200 <= s.status < 300)
    return {
        "server_id": client.server["id"],
        "bmc_ip": client.server.get("bmc_ip"),
        "hostname": client.server.get("hostname"),
        "platform": client.server.get("platform"),
        "mode": steps[0].source if steps else ("live" if live_cfg else "replay"),
        "requests": len(steps),
        "succeeded": ok,
        "failed": len(steps) - ok,
        "total_duration_ms": sum(s.duration_ms for s in steps),
        "steps": [s.to_dict() for s in steps],
    }
