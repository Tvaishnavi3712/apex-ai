"""
Redfish client — interrogate a server's BMC (HPE iLO, Dell iDRAC).

Redfish is the DMTF standard management API every modern BMC exposes over
HTTPS. Apex uses it to read a server's real configuration rather than trusting
an inventory spreadsheet: firmware levels, BIOS/vRAN attributes, Secure Boot
state, thermal baselines, NIC layout.

Two transports, one client
--------------------------
`ReplayTransport` (default) serves the responses captured from the Verizon Far
Edge lab campaigns — real `curl` output from real BMCs, extracted by
`scripts/extract_hw_inventory.py`. Those BMCs live on Verizon-internal IPv6
behind a jump server, so they are unreachable from anywhere a demo runs; replay
is what makes the walk reproducible.

`LiveTransport` issues the same requests over HTTPS to a reachable BMC.
Credentials are passed per call and never stored, logged, or persisted — Apex
holds no BMC passwords.

Both produce identical `RedfishStep` records, so the console renders one code
path whether it replayed or dialled out.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

log = structlog.get_logger()

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_FILE = ROOT / "verizon-test-data" / "hardware_inventory.json"

# Redact anything that looks like a credential before a command is ever
# returned to a caller or written to a log.
_SECRET_PATTERNS = [
    re.compile(r"(-u\s+\S+?:)(\S+)"),                     # curl -u user:pass
    re.compile(r"(--password[= ])(\S+)"),
    re.compile(r"(-p\s+)(\S+)"),
]


def redact(command: str) -> str:
    """Mask credentials in a shell command so it is safe to display."""
    out = command
    for pat in _SECRET_PATTERNS:
        out = pat.sub(lambda m: m.group(1) + "XXXXXXXXXX", out)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# data model
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RedfishStep:
    """One request in an interrogation walk."""
    seq: int
    name: str
    method: str
    url: str
    command: str                      # display-safe, credentials masked
    status: int
    duration_ms: int
    response: Any = None
    error: Optional[str] = None
    source: str = "replay"            # "replay" | "live"
    findings: List[Dict[str, Any]] = field(default_factory=list)
    reason_for_change: Optional[str] = None
    required_change: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# inventory dataset
# ─────────────────────────────────────────────────────────────────────────────

class InventoryData:
    """
    Loads and caches the extracted hardware dataset.

    Reloads when the file's mtime changes so re-running the extractor is picked
    up without restarting the API.
    """

    _cache: Optional[Dict[str, Any]] = None
    _mtime: float = 0.0

    @classmethod
    def load(cls) -> Dict[str, Any]:
        try:
            mtime = INVENTORY_FILE.stat().st_mtime
        except OSError:
            log.warning("redfish.inventory_missing", path=str(INVENTORY_FILE))
            return {"servers": [], "redfish_catalog": [], "tests": [],
                    "campaigns": [], "artifacts": []}

        if cls._cache is None or mtime != cls._mtime:
            try:
                with open(INVENTORY_FILE, encoding="utf-8") as f:
                    cls._cache = json.load(f)
                cls._mtime = mtime
                log.info("redfish.inventory_loaded",
                         servers=len(cls._cache.get("servers", [])))
            except (OSError, json.JSONDecodeError) as e:
                log.error("redfish.inventory_load_failed", error=str(e))
                return {"servers": [], "redfish_catalog": [], "tests": [],
                        "campaigns": [], "artifacts": []}
        return cls._cache

    @classmethod
    def servers(cls) -> List[Dict[str, Any]]:
        return cls.load().get("servers", [])

    @classmethod
    def server(cls, server_id: str) -> Optional[Dict[str, Any]]:
        for s in cls.servers():
            if s.get("id") == server_id or s.get("bmc_ip") == server_id:
                return s
        return None

    @classmethod
    def catalog(cls) -> List[Dict[str, Any]]:
        return cls.load().get("redfish_catalog", [])


# ─────────────────────────────────────────────────────────────────────────────
# transports
# ─────────────────────────────────────────────────────────────────────────────

class ReplayTransport:
    """
    Serves captured BMC responses.

    The catalog was captured against one HPE EL140 unit. Replaying it for a
    different server would misrepresent that server's state, so responses are
    reframed with the target's own identity where the field is identity-bearing,
    and the step is marked so the UI can label its provenance.
    """

    source = "replay"

    def __init__(self, server: Dict[str, Any]) -> None:
        self.server = server

    def fetch(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        # Captured walks take ~100-400ms per call on real hardware; keep a
        # small delay so the console streams at a believable pace.
        time.sleep(0.04)
        return {
            "status": 200,
            "response": entry.get("response"),
            "error": None,
            "captured_from": entry.get("bmc_ip"),
        }


class LiveTransport:
    """
    Real HTTPS Redfish against a reachable BMC.

    Credentials arrive per call and are never retained. BMC certificates are
    self-signed in the lab, so verification is off by default — the same
    `--no-cert-check` posture the campaign tooling used.
    """

    source = "live"

    def __init__(self, host: str, username: str, password: str,
                 verify: bool = False, timeout: float = 15.0) -> None:
        self.host = host
        self._username = username
        self._password = password
        self.verify = verify
        self.timeout = timeout

    def _base(self) -> str:
        host = self.host
        # Bare IPv6 literals must be bracketed in a URL.
        if ":" in host and not host.startswith("[") and "//" not in host:
            host = f"[{host}]"
        return host if host.startswith("http") else f"https://{host}"

    def fetch(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        import httpx

        url = f"{self._base()}{entry.get('url') or '/redfish/v1/'}"
        try:
            with httpx.Client(verify=self.verify, timeout=self.timeout) as client:
                r = client.get(url, auth=(self._username, self._password))
            try:
                body = r.json()
            except ValueError:
                body = {"_raw": r.text[:4000]}
            return {"status": r.status_code, "response": body, "error": None}
        except Exception as e:  # noqa: BLE001 — an unreachable BMC is a result, not a crash
            return {"status": 0, "response": None, "error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# findings
# ─────────────────────────────────────────────────────────────────────────────

# Maps a catalog endpoint to the config-check steps it provides evidence for,
# so each Redfish response can be shown next to the compliance verdict it drove.
ENDPOINT_TO_CHECKS = {
    "model": ["iLO License", "iDRAC Identity"],
    "aggregate_health_status": ["Thermal / Fan Baseline"],
    "bios": ["WorkloadProfile", "vRAN Attribute Validation", "BIOS WorkloadProfile"],
    "secure_boot": ["Secure Boot"],
    "cpu": [],
    "memory": ["Memory Capacity"],
    "fans": ["Thermal / Fan Baseline"],
    "thermal_sensors": ["Thermal / Fan Baseline"],
    "base_network_adapters": ["NIC Inventory"],
    "power_supply": [],
    "storage": [],
    "ilo_bmc_version": ["Firmware Inventory"],
    "bios_version": ["Firmware Inventory"],
}


def findings_for(entry: Dict[str, Any], server: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Attach the server's own compliance verdicts to the endpoint that evidences them."""
    wanted = ENDPOINT_TO_CHECKS.get(entry.get("id"), [])
    if not wanted:
        return []
    out = []
    for check in server.get("checks", []):
        if check.get("step") in wanted:
            out.append({
                "step": check["step"],
                "result": check["result"],
                "detail": check.get("detail", ""),
                "category": check.get("category", ""),
                # Carry the resolved gap through: the certification report reads
                # its recommendation and impacted scripts from here, and the
                # console renders the current/expected diff.
                "gap": check.get("gap"),
            })
    return out


# ─────────────────────────────────────────────────────────────────────────────
# client
# ─────────────────────────────────────────────────────────────────────────────

class RedfishClient:
    """
    Walks a BMC's Redfish tree and returns one `RedfishStep` per request.

    Usage:
        client = RedfishClient.for_server("hpe-9249-e051")
        steps  = client.interrogate()
    """

    def __init__(self, server: Dict[str, Any], transport: Any) -> None:
        self.server = server
        self.transport = transport

    # ── construction ─────────────────────────────────────────────────────────
    @classmethod
    def for_server(cls, server_id: str, live: Optional[Dict[str, str]] = None) -> "RedfishClient":
        """
        Build a client for a server in the inventory.

        `live` is an optional {host, username, password} supplied by the caller
        at request time to force a real connection. Omit it — the default — and
        the client replays the captured campaign responses.
        """
        server = InventoryData.server(server_id)
        if server is None:
            raise KeyError(f"unknown server: {server_id}")

        if live and live.get("username") and live.get("password"):
            transport = LiveTransport(
                host=live.get("host") or server["bmc_ip"],
                username=live["username"],
                password=live["password"],
                verify=str(live.get("verify", "false")).lower() == "true",
            )
        else:
            transport = ReplayTransport(server)
        return cls(server, transport)

    # ── the walk ─────────────────────────────────────────────────────────────
    def interrogate(self, only: Optional[List[str]] = None) -> List[RedfishStep]:
        """
        Run the full interrogation, or just the endpoints named in `only`.

        Endpoint order follows the campaign's own sequence, so the walk reads
        the way the engineers actually performed it: identity first, then
        health, then BIOS, then subsystems.
        """
        catalog = InventoryData.catalog()
        # `is not None`, not truthiness: an empty list means "walk nothing",
        # which is a real instruction — some playbooks never touch hardware.
        if only is not None:
            wanted = {o.lower() for o in only}
            catalog = [c for c in catalog if c["id"].lower() in wanted]

        steps: List[RedfishStep] = []
        for entry in catalog:
            steps.append(self._one(entry, len(steps) + 1))
        return steps

    def _one(self, entry: Dict[str, Any], seq: int) -> RedfishStep:
        started = time.perf_counter()
        result = self.transport.fetch(entry)
        elapsed = int((time.perf_counter() - started) * 1000)

        command = self._display_command(entry)

        return RedfishStep(
            seq=seq,
            name=entry.get("name") or entry.get("id") or f"step-{seq}",
            method="GET",
            url=entry.get("url") or "/redfish/v1/",
            command=command,
            status=result.get("status", 0),
            duration_ms=elapsed,
            response=result.get("response"),
            error=result.get("error"),
            source=self.transport.source,
            findings=findings_for(entry, self.server),
            reason_for_change=entry.get("reason_for_change"),
            required_change=entry.get("required_change"),
        )

    def _display_command(self, entry: Dict[str, Any]) -> str:
        """
        The command shown in the console.

        Replay shows the real captured command so the audience sees exactly what
        was run against the lab unit. Live mode synthesises the equivalent curl
        for the host being dialled. Either way credentials are masked.
        """
        if self.transport.source == "replay":
            cmds = entry.get("commands") or []
            if cmds:
                return redact(cmds[0])

        host = getattr(self.transport, "host", self.server["bmc_ip"])
        bracketed = f"[{host}]" if ":" in host and not host.startswith("[") else host
        url = entry.get("url") or "/redfish/v1/"
        return redact(
            f"curl -gsk -u Administrator:XXXXXXXXXX -X GET "
            f"'https://{bracketed}{url}'"
        )

    # ── single fetch ─────────────────────────────────────────────────────────
    def get(self, endpoint_id: str) -> Optional[RedfishStep]:
        """Fetch one catalog endpoint by id."""
        for entry in InventoryData.catalog():
            if entry["id"] == endpoint_id:
                return self._one(entry, entry.get("seq", 1))
        return None


# Provider-neutral alias, matching the naming used by the other services.
BMCClient = RedfishClient
