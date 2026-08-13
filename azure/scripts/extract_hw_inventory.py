#!/usr/bin/env python3
"""
Extract the real Verizon Far Edge hardware artifacts into an Apex inventory dataset.

Source: the lab result folders produced by the certification campaigns —

    HPE-EL140-ilo_1.20.00-BIOS_v1.30/     HPE ProLiant Compute EL140 Gen12 / iLO 7
    Dell-XR8720-1.1.3_BIOS-1.30.10.51_iDRAC/  Dell XR8720t / iDRAC 10

Everything emitted here comes out of those files. Nothing is invented: BMC
addresses, firmware levels, check outcomes, Redfish URLs and the JSON bodies
are all lifted verbatim so the Inventory page and the Redfish console can
replay a genuine interrogation.

Output: verizon-test-data/hardware_inventory.json

Usage:
    python3 scripts/extract_hw_inventory.py [--src DIR ...] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_SOURCES = [
    os.path.expanduser("~/Downloads/HPE-EL140-ilo_1.20.00-BIOS_v1.30 copy"),
    os.path.expanduser("~/Downloads/Dell-XR8720-1.1.3_BIOS-1.30.10.51_iDRAC copy"),
]

DEFAULT_OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "verizon-test-data",
    "hardware_inventory.json",
)

# ─────────────────────────────────────────────────────────────────────────────
# generic parsing helpers
# ─────────────────────────────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HASH_HEADER_RE = re.compile(r"\A((?:#[^\n]*\n)+)", re.MULTILINE)
FENCE_RE = re.compile(r"```(\w+)?\s*\n(.*?)```", re.DOTALL)


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def parse_frontmatter(text: str) -> Dict[str, str]:
    """YAML-ish `--- key: value ---` block at the top of a file."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def parse_hash_header(text: str) -> Dict[str, str]:
    """`# Key: value` comment header (used by the HPE campaign summary)."""
    m = HASH_HEADER_RE.match(text)
    if not m:
        return {}
    out: Dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.lstrip("#").strip()
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip().lower().replace(" ", "_")] = v.strip()
    return out


def parse_bold_fields(text: str) -> Dict[str, str]:
    """`**Host:** \\`value\\`` style fields (Dell configure-run files)."""
    out: Dict[str, str] = {}
    for k, v in re.findall(r"\*\*([A-Za-z /()]+):\*\*\s*`?([^`\n]+)`?", text):
        out[k.strip().lower().replace(" ", "_")] = v.strip().rstrip("*").strip()
    return out


def parse_md_tables_with_pos(text: str) -> List[Tuple[int, List[List[str]]]]:
    """
    Every pipe table in the document as (character offset, rows), header first.

    The offset is what lets a table be attributed to the `###` section it sits
    under; matching on header text alone would map every table to the first one
    that shares a header.
    """
    tables: List[Tuple[int, List[List[str]]]] = []
    current: List[List[str]] = []
    start = 0
    offset = 0
    for line in text.splitlines(keepends=True):
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not all(set(c) <= set("-: ") and c for c in cells):  # skip separator
                if not current:
                    start = offset
                current.append(cells)
        else:
            if len(current) > 1:
                tables.append((start, current))
            current = []
        offset += len(line)
    if len(current) > 1:
        tables.append((start, current))
    return tables


def parse_md_tables(text: str) -> List[List[List[str]]]:
    """Every pipe table in the document, as a list of row-lists (header first)."""
    return [rows for _, rows in parse_md_tables_with_pos(text)]


def clean(cell: str) -> str:
    """Strip markdown emphasis and backticks from a table cell."""
    return re.sub(r"[*`]", "", cell).strip()


def slug_from_ip(ip: str) -> str:
    """
    Short, stable, readable id from the BMC address.

    Two hextets, not one: the lab reuses `e001` as the last hextet on different
    subnets, so a single-hextet slug collides across servers.
    """
    parts = [p for p in ip.lower().split(":") if p]
    if len(parts) >= 8:
        return f"{parts[3]}-{parts[-1]}"   # subnet hextet + host hextet
    return "-".join(parts[-2:]) if len(parts) >= 2 else ip.lower()


# ─────────────────────────────────────────────────────────────────────────────
# server identity
# ─────────────────────────────────────────────────────────────────────────────

VENDOR_BY_PLATFORM = [
    ("EL140", "HPE"),
    ("ProLiant", "HPE"),
    ("Edgeline", "HPE"),
    ("XR8720", "Dell"),
    ("Dell", "Dell"),
]


def vendor_for(platform: str) -> str:
    for needle, vendor in VENDOR_BY_PLATFORM:
        if needle.lower() in platform.lower():
            return vendor
    return "Unknown"


# The lab writes the same box several ways ("HPE EL140 Gen12" in test
# frontmatter, the full marketing name in campaign summaries). Collapse them so
# one physical server doesn't look like two models in the inventory.
PLATFORM_CANONICAL = {
    "hpe el140 gen12": "HPE ProLiant Compute EL140 Gen12",
    "hpe proliant compute el140 gen12": "HPE ProLiant Compute EL140 Gen12",
    "el140 gen12": "HPE ProLiant Compute EL140 Gen12",
    "dell xr8720t": "Dell XR8720t",
    "xr8720t": "Dell XR8720t",
}


def canonical_platform(platform: Optional[str]) -> Optional[str]:
    if not platform:
        return None
    return PLATFORM_CANONICAL.get(platform.strip().lower(), platform.strip())


def infer_platform(text: str, filename: str) -> Optional[str]:
    """
    Recover the platform when a file never states it outright.

    The Dell configure-run logs, for instance, only reveal the model through
    their title ("XR8720t Configure Run") and the script they invoke
    (`xr8720t_configure_r1.py`).
    """
    haystack = f"{filename}\n{text[:2000]}".lower()
    for needle, canon in (
        ("xr8720t", "Dell XR8720t"),
        ("el140", "HPE ProLiant Compute EL140 Gen12"),
        ("e930t", "HPE Edgeline e930t"),
        ("e920t", "HPE Edgeline e920t"),
        ("e910t", "HPE ProLiant e910t"),
    ):
        if needle in haystack:
            return canon
    return None


def bmc_kind(vendor: str, fw: str) -> str:
    if vendor == "HPE":
        return "iLO 7" if fw.startswith("iLO 7") or "1.20" in fw else "iLO"
    if vendor == "Dell":
        return "iDRAC 10"
    return "BMC"


class ServerAccumulator:
    """Collects fragments about each BMC across many files into one record."""

    def __init__(self) -> None:
        self.by_ip: Dict[str, Dict[str, Any]] = {}

    def touch(self, ip: str) -> Dict[str, Any]:
        if ip not in self.by_ip:
            self.by_ip[ip] = {
                "id": "",
                "bmc_ip": ip,
                "hostname": None,
                "vendor": None,
                "platform": None,
                "bmc_type": None,
                "bmc_firmware": None,
                "bios_version": None,
                "chassis_model": None,
                "processor": None,
                "memory": None,
                "nics": [],
                "last_seen": None,
                "evidence_files": [],
                "checks": [],
                "tests": [],
            }
        return self.by_ip[ip]

    def merge(self, ip: str, fields: Dict[str, Any], source: str) -> None:
        rec = self.touch(ip)
        for k, v in fields.items():
            if v in (None, "", []):
                continue
            if rec.get(k) in (None, "", []):
                rec[k] = v
        if source and source not in rec["evidence_files"]:
            rec["evidence_files"].append(source)

    def finalize(self, artifacts: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        artifacts = artifacts or []
        out = []
        for ip, rec in self.by_ip.items():
            rec["platform"] = canonical_platform(rec.get("platform"))
            platform = rec.get("platform") or ""
            vendor = rec.get("vendor") or vendor_for(platform)
            rec["vendor"] = vendor
            rec["id"] = f"{vendor.lower()}-{slug_from_ip(ip)}"
            if not rec.get("bmc_type"):
                rec["bmc_type"] = bmc_kind(vendor, rec.get("bmc_firmware") or "")

            checks = rec["checks"]
            rec["check_summary"] = {
                "total": len(checks),
                "pass": sum(1 for c in checks if c["result"] == "PASS"),
                "warn": sum(1 for c in checks if c["result"] == "WARN"),
                "drift": sum(1 for c in checks if c["result"] == "DRIFT"),
                "fail": sum(1 for c in checks if c["result"] == "FAIL"),
            }
            tests = rec["tests"]
            counted = {"PASS", "FAIL"}
            rec["test_summary"] = {
                "total": len(tests),
                "pass": sum(1 for t in tests if t["result"] == "PASS"),
                "deviation": sum(1 for t in tests if "DEVIATION" in t["result"]),
                "partial": sum(1 for t in tests if "PARTIAL" in t["result"]),
                "fail": sum(1 for t in tests if t["result"] == "FAIL"),
                # SKIP / REFERENCE-ARTIFACT / COMPLETE are real campaign outcomes;
                # bucket them so the counts still reconcile to `total`.
                "other": sum(1 for t in tests
                             if t["result"] not in counted
                             and "DEVIATION" not in t["result"]
                             and "PARTIAL" not in t["result"]),
            }
            rec["status"] = derive_status(rec, [a for a in artifacts if a["bmc_ip"] == ip])
            out.append(rec)
        out.sort(key=lambda r: (r["vendor"], r["bmc_ip"]))
        return out


def derive_status(rec: Dict[str, Any], artifacts: List[Dict[str, Any]]) -> str:
    """
    Roll a server's evidence up to one headline status.

    Ordered worst-first so the inventory never flatters a box: a single FAIL
    outranks any number of passes. Servers evidenced only by lab artifacts
    (Secure Boot installs, playbook replication runs) still get a real status
    rather than falling through to UNKNOWN.
    """
    cs, ts = rec["check_summary"], rec["test_summary"]
    outcomes = [a["result"] for a in artifacts if a.get("result")]

    if cs["fail"] or ts["fail"] or "FAIL" in outcomes:
        return "FAIL"
    if cs["drift"]:
        return "DRIFT"
    if cs["warn"] or ts["deviation"] or ts["partial"] \
            or any("DEVIATION" in o for o in outcomes):
        return "PASS WITH DEVIATION"
    if cs["total"] or ts["total"] or outcomes:
        return "PASS"
    return "UNKNOWN"


# ─────────────────────────────────────────────────────────────────────────────
# per-file extractors
# ─────────────────────────────────────────────────────────────────────────────

RESULT_TOKENS = ("PASS WITH DEVIATION", "PARTIAL-PASS", "PARTIAL PASS",
                 "PASS", "DRIFT", "WARN", "FAIL", "BLOCKED", "SKIP", "INFO")


def normalize_result(raw: str) -> str:
    up = clean(raw).upper()
    for token in RESULT_TOKENS:
        if up.startswith(token):
            return token
    return up or "UNKNOWN"


def extract_test_result(path: str, text: str, acc: ServerAccumulator,
                        tests: List[Dict[str, Any]]) -> None:
    """MEAKV-*/PROPOSED-*-result.md — one executed certification test."""
    fm = parse_frontmatter(text)
    if not fm.get("bmc_ip"):
        return
    ip = fm["bmc_ip"]
    title_m = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else fm.get("test", "")
    title = re.sub(r"^[A-Z]+-\d+\s*[—-]\s*", "", title)

    record = {
        "test_id": fm.get("test") or os.path.basename(path).split("-result")[0],
        "title": title,
        "result": normalize_result(fm.get("result", "")),
        "bmc_ip": ip,
        "platform": fm.get("platform"),
        "date": fm.get("date"),
        "source_file": os.path.basename(path),
    }
    tests.append(record)

    acc.merge(ip, {
        "platform": canonical_platform(fm.get("platform")) or infer_platform(text, path),
        "bmc_firmware": fm.get("bmc_fw"),
        "bios_version": fm.get("bios_version"),
        "hostname": fm.get("hostname"),
        "last_seen": fm.get("date"),
    }, os.path.basename(path))
    acc.touch(ip)["tests"].append(
        {k: record[k] for k in ("test_id", "title", "result", "date")}
    )


CHECK_CATEGORY_RE = re.compile(r"^###\s+(.*)$", re.MULTILINE)

GAP_RE = re.compile(r"^###\s+(Gap\s+(\d+)|Warning)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)
GAP_REF_RE = re.compile(r"See\s+(Gap\s+\d+)\s+below", re.IGNORECASE)
ACTION_RE = re.compile(r"\*\*Action[^:*]*:\*\*\s*(.+?)(?=\n\s*\n|\Z)", re.DOTALL)


def extract_gaps(text: str) -> Dict[str, Dict[str, Any]]:
    """
    Parse the `### Gap N — ...` sections of a config-check report.

    The step tables only say "See Gap 1 below", which is meaningless once the
    row is lifted out of the document. These sections hold what an operator
    actually needs: what drifted, what it should be, and the remediation
    command. Keyed by ref ("Gap 1") so checks can be joined back to them.
    """
    gaps: Dict[str, Dict[str, Any]] = {}
    matches = list(GAP_RE.finditer(text))

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        # Stop at the next `##` section so we don't absorb the whole tail.
        nxt = re.search(r"^##\s+", body, re.MULTILINE)
        if nxt:
            body = body[: nxt.start()]

        ref = m.group(1).strip()
        action_m = ACTION_RE.search(body)
        # The command itself is captured separately as `remediation_command`;
        # keep the action prose free of the fence so it reads as a sentence.
        action = " ".join(FENCE_RE.sub("", action_m.group(1)).split()) if action_m else None

        # A current/expected table is the clearest statement of the drift.
        fields = []
        for table in parse_md_tables(body):
            header = [clean(c).lower() for c in table[0]]
            if "current" in header[1:2] + header[1:3] or "current count" in header:
                i_cur = next((j for j, h in enumerate(header) if h.startswith("current")), 1)
                i_exp = next((j for j, h in enumerate(header)
                              if h.startswith(("expected", "required"))), None)
                for row in table[1:]:
                    if len(row) <= i_cur:
                        continue
                    fields.append({
                        "field": clean(row[0]),
                        "current": clean(row[i_cur]),
                        "expected": clean(row[i_exp]) if i_exp is not None and len(row) > i_exp else "",
                    })

        # Leading prose, fences and tables removed, as the human-readable summary.
        prose = FENCE_RE.sub("", body)
        prose = "\n".join(l for l in prose.splitlines()
                          if not l.strip().startswith("|"))
        prose = re.sub(r"\*\*Action[^:*]*:\*\*.*", "", prose, flags=re.DOTALL)
        summary = " ".join(prose.split())

        remediation = None
        for lang, code in FENCE_RE.findall(body):
            if (lang or "").lower() in ("bash", "sh", ""):
                remediation = redact_secrets(code.strip())
                break

        gaps[ref] = {
            "ref": ref,
            "title": m.group(3).strip(),
            "summary": summary[:900] or None,
            "fields": fields,
            "action": action,
            "remediation_command": remediation,
        }

    return gaps


_SECRET_RE = [
    re.compile(r"(--password[= ]\s*)(\S+)"),
    re.compile(r"(-u\s+\S+?:)(\S+)"),
    re.compile(r"(-p\s+)(\S+)"),
]


def redact_secrets(cmd: str) -> str:
    """Mask anything credential-shaped before it leaves this script."""
    for pat in _SECRET_RE:
        cmd = pat.sub(lambda m: m.group(1) + "XXXXXXXXXX", cmd)
    return cmd


def extract_config_check(path: str, text: str, acc: ServerAccumulator) -> None:
    """
    ilo-config-check-*.md and configure-run-*.md — a provisioning compliance
    sweep. Each row of the step tables becomes one inventory check.
    """
    fm = parse_frontmatter(text)
    bold = parse_bold_fields(text)
    ip = fm.get("bmc_ip") or bold.get("host")
    if not ip:
        m = re.search(r"(2607:[0-9a-f:]+)", text)
        ip = m.group(1) if m else None
    if not ip:
        return

    # Section headings let us group checks the way the engineers grouped them.
    categories: List[Tuple[int, str]] = [
        (m.start(), m.group(1).strip()) for m in CHECK_CATEGORY_RE.finditer(text)
    ]

    def category_at(pos: int) -> str:
        name = "Checks"
        for start, label in categories:
            if start < pos:
                name = label
            else:
                break
        return name

    gaps = extract_gaps(text)

    added = 0
    for pos, table in parse_md_tables_with_pos(text):
        header = [clean(c).lower() for c in table[0]]
        if "step" not in header or "result" not in header:
            continue
        i_step, i_res = header.index("step"), header.index("result")
        i_det = header.index("detail") if "detail" in header else None
        for row in table[1:]:
            if len(row) <= max(i_step, i_res):
                continue
            detail = clean(row[i_det]) if i_det is not None and len(row) > i_det else ""

            # "See Gap 1 below" is a pointer, not information — resolve it.
            gap = None
            ref_m = GAP_REF_RE.search(detail)
            if ref_m:
                gap = gaps.get(ref_m.group(1))
                if gap and gap.get("summary"):
                    detail = gap["summary"][:300]

            acc.touch(ip)["checks"].append({
                "category": category_at(pos),
                "step": clean(row[i_step]),
                "result": normalize_result(row[i_res]),
                "detail": detail,
                "gap": gap,
                "source_file": os.path.basename(path),
            })
            added += 1

    if added:
        acc.merge(ip, {
            "platform": canonical_platform(fm.get("platform")) or infer_platform(text, path),
            "bmc_firmware": fm.get("bmc_fw"),
            "bios_version": fm.get("bios_version"),
            "hostname": fm.get("hostname") or bold.get("hostname"),
            "last_seen": fm.get("date"),
        }, os.path.basename(path))


IDENTITY_KEYS = {
    "platform": "platform",
    "chassis model": "chassis_model",
    "bios version": "bios_version",
    "bmc firmware": "bmc_firmware",
    "bmc ipv6": "bmc_ip",
    "bmc hostname": "hostname",
    "processor": "processor",
    "memory": "memory",
}


def extract_campaign(path: str, text: str, acc: ServerAccumulator,
                     campaigns: List[Dict[str, Any]]) -> None:
    """test-campaign-summary-*.md — the roll-up for a whole certification run."""
    fm = parse_frontmatter(text) or parse_hash_header(text)
    ip = fm.get("bmc_ip") or fm.get("bmc_ip".replace("_", " "))
    if not ip:
        m = re.search(r"(2607:[0-9a-f:]+)", text)
        ip = m.group(1) if m else None

    identity: Dict[str, Any] = {}
    for table in parse_md_tables(text):
        header = [clean(c).lower() for c in table[0]]
        if header[:2] == ["field", "value"]:
            for row in table[1:]:
                key = IDENTITY_KEYS.get(clean(row[0]).lower())
                if key and len(row) > 1:
                    identity[key] = clean(row[1])

    campaigns.append({
        "id": os.path.basename(path).replace("test-campaign-summary-", "").replace(".md", ""),
        "platform": fm.get("platform") or identity.get("platform"),
        "bmc_ip": identity.get("bmc_ip") or ip,
        "date_start": fm.get("date_start") or fm.get("date"),
        "date_end": fm.get("date_end") or fm.get("date"),
        "totals": {
            k: int(fm[k]) for k in
            ("total_tests", "pass", "pass_with_deviation", "partial_pass", "blocked", "fail")
            if fm.get(k, "").isdigit()
        },
        "source_file": os.path.basename(path),
    })

    if ip or identity.get("bmc_ip"):
        acc.merge(identity.get("bmc_ip") or ip, {
            "platform": canonical_platform(fm.get("platform") or identity.get("platform"))
                        or infer_platform(text, path),
            "bmc_firmware": fm.get("bmc_fw") or identity.get("bmc_firmware"),
            "bios_version": fm.get("bios_version") or identity.get("bios_version"),
            "hostname": identity.get("hostname"),
            "chassis_model": identity.get("chassis_model"),
            "processor": identity.get("processor"),
            "memory": identity.get("memory"),
            "last_seen": fm.get("date_end") or fm.get("date"),
        }, os.path.basename(path))


SECTION_RE = re.compile(r"^##\s+(\d+)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)


def extract_redfish_catalog(path: str, text: str) -> List[Dict[str, Any]]:
    """
    icinga-*-redfish-endpoints.md — the interrogation catalog.

    Each `## N — name` section pairs a real curl against the BMC with the real
    JSON it returned. That pairing is what lets the console replay a genuine
    Redfish walk instead of rendering a mock.
    """
    fm = parse_frontmatter(text)
    matches = list(SECTION_RE.finditer(text))
    catalog: List[Dict[str, Any]] = []

    # The document's own Summary Table is the authoritative statement of which
    # checks need a monitoring change. The per-section prose says things like
    # "**No change required.**", which is not reliably machine-readable.
    changes = parse_change_summary(text)

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]

        commands, responses = [], []
        for lang, code in FENCE_RE.findall(body):
            code = code.strip()
            if (lang or "").lower() == "bash":
                commands.append(code)
            elif (lang or "").lower() == "json":
                try:
                    responses.append(json.loads(code))
                except json.JSONDecodeError:
                    responses.append({"_raw": code})

        urls = sorted(set(re.findall(r"/redfish/v1[A-Za-z0-9/_.\-]*", body)))
        # The URL actually fetched is the one inside the curl, not the yaml config.
        fetched = None
        for cmd in commands:
            u = re.search(r"/redfish/v1[A-Za-z0-9/_.\-]*", cmd)
            if u:
                fetched = u.group(0)
                break

        reason = section_text(body, "Reason for change")
        change = section_text(body, "Required config change")

        endpoint_id = re.sub(r"[^a-z0-9]+", "_", m.group(2).lower()).strip("_")
        needed = lookup_changes(changes, endpoint_id)

        catalog.append({
            "seq": int(m.group(1)),
            "id": endpoint_id,
            "name": m.group(2),
            "requires_change": bool(needed),
            "changes_required": needed,
            "url": fetched or (urls[0] if urls else None),
            "urls_referenced": urls,
            "commands": commands,
            "response": responses[0] if responses else None,
            "responses": responses,
            "reason_for_change": reason,
            "required_change": change,
            "bmc_ip": fm.get("bmc_ip"),
            "platform": fm.get("platform"),
            "bmc_fw": fm.get("bmc_fw"),
            "source_file": os.path.basename(path),
        })

    return catalog


def parse_change_summary(text: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Read the `## Summary Table` at the end of the endpoint document.

    Rows look like:

        | model                  | No — wrong product string | Add `HPE …EL140 Gen12` |
        | aggregate_health_status| Yes — same path, works    | None (…confirmed)      |
        | bios — LlcPrefetch     | Yes — attribute exists    | None                   |

    A check can appear several times with a ` — sub-check` suffix, so rows are
    grouped by the endpoint prefix. Only rows whose "Change Required" cell is
    something other than "None" are kept — those are the endpoints where
    monitoring genuinely has to change.
    """
    out: Dict[str, List[Dict[str, str]]] = {}

    for table in parse_md_tables(text):
        header = [clean(c).lower() for c in table[0]]
        if not header or "check" not in header[0]:
            continue
        i_change = next((j for j, h in enumerate(header) if "change" in h and "required" in h), None)
        if i_change is None:
            continue

        for row in table[1:]:
            if len(row) <= i_change:
                continue
            check = clean(row[0])
            change = clean(row[i_change])
            # "None", "None (…)" and empty all mean no change is needed.
            if not change or change.lower().startswith("none"):
                continue

            endpoint = re.split(r"\s+[—–-]\s+", check)[0].strip()
            key = re.sub(r"[^a-z0-9]+", "_", endpoint.lower()).strip("_")
            out.setdefault(key, []).append({
                "check": check,
                "change": change,
                "applies": clean(row[1]) if len(row) > 1 else "",
            })

    return out


def lookup_changes(changes: Dict[str, List[Dict[str, str]]],
                   endpoint_id: str) -> List[Dict[str, str]]:
    """
    Join a section id to its summary-table rows.

    The two don't always spell a check the same way — the section heading is
    `base_network_adapters` while the summary table says "network adapters", and
    `ilo (BMC version)` appears there as just "ilo". Fall back to containment in
    either direction, longest match first so `bios_version` doesn't get claimed
    by `bios`.
    """
    if endpoint_id in changes:
        return changes[endpoint_id]

    for key in sorted(changes, key=len, reverse=True):
        if key == endpoint_id:
            return changes[key]
        # The summary key must be a whole-token prefix or suffix of the section
        # id — never the reverse, or `bios` would claim `bios_version`'s rows.
        ktoks, etoks = key.split("_"), endpoint_id.split("_")
        if len(ktoks) > len(etoks):
            continue
        if ktoks == etoks[: len(ktoks)] or ktoks == etoks[-len(ktoks):]:
            return changes[key]

    return []


def section_text(body: str, heading: str) -> Optional[str]:
    """Prose under a `### heading`, fences stripped."""
    m = re.search(rf"^###\s+{re.escape(heading)}\s*$", body, re.MULTILINE)
    if not m:
        return None
    rest = body[m.end():]
    nxt = re.search(r"^###\s+", rest, re.MULTILINE)
    chunk = rest[: nxt.start()] if nxt else rest
    chunk = FENCE_RE.sub("", chunk)
    return " ".join(chunk.split()) or None


def extract_lab_artifact(path: str, text: str, acc: ServerAccumulator,
                         artifacts: List[Dict[str, Any]]) -> None:
    """
    Any remaining lab document that names a BMC — Secure Boot cert installs,
    playbook-function replication runs, BIOS comparisons, change specs.

    These aren't numbered test cases, but they are real evidence against a real
    server, so they hang off the inventory record as attached artifacts.
    """
    fm = parse_frontmatter(text)
    ip = fm.get("bmc_ip")
    if not ip:
        return

    title_m = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
    result = fm.get("result") or fm.get("overall_result") or ""

    artifacts.append({
        "id": os.path.basename(path).replace(".md", ""),
        "title": (title_m.group(1).strip() if title_m else os.path.basename(path)),
        "objective": fm.get("test_objective"),
        "result": normalize_result(result) if result else None,
        "bmc_ip": ip,
        "date": fm.get("date"),
        "source_file": os.path.basename(path),
    })

    acc.merge(ip, {
        "platform": canonical_platform(fm.get("platform")) or infer_platform(text, path),
        "bmc_firmware": fm.get("bmc_fw") or fm.get("ilo_version"),
        "bios_version": fm.get("bios_version"),
        # `ilo_hostname` sometimes carries an annotated pair; keep the first name.
        "hostname": (fm.get("hostname") or fm.get("ilo_hostname") or "").split(" (")[0] or None,
        "last_seen": fm.get("date"),
    }, os.path.basename(path))


def extract_firmware(text: str) -> List[Dict[str, str]]:
    """Firmware inventory rows, wherever a component/version table appears."""
    rows = []
    for table in parse_md_tables(text):
        header = [clean(c).lower() for c in table[0]]
        if "component" not in header:
            continue
        i_c = header.index("component")
        i_v = next((header.index(h) for h in ("version", "installed", "current") if h in header), None)
        i_m = next((header.index(h) for h in ("minimum", "recipe minimum", "required") if h in header), None)
        i_r = header.index("result") if "result" in header else None
        for row in table[1:]:
            if len(row) <= i_c:
                continue
            rows.append({
                "component": clean(row[i_c]),
                "version": clean(row[i_v]) if i_v is not None and len(row) > i_v else "",
                "minimum": clean(row[i_m]) if i_m is not None and len(row) > i_m else "",
                "result": normalize_result(row[i_r]) if i_r is not None and len(row) > i_r else "",
            })
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# driver
# ─────────────────────────────────────────────────────────────────────────────

def build(sources: List[str]) -> Dict[str, Any]:
    acc = ServerAccumulator()
    tests: List[Dict[str, Any]] = []
    campaigns: List[Dict[str, Any]] = []
    catalog: List[Dict[str, Any]] = []
    artifacts: List[Dict[str, Any]] = []
    firmware: Dict[str, List[Dict[str, str]]] = {}
    skipped: List[str] = []

    for src in sources:
        if not os.path.isdir(src):
            print(f"  ! source not found, skipping: {src}", file=sys.stderr)
            continue
        for fname in sorted(os.listdir(src)):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(src, fname)
            try:
                text = read(path)
            except OSError as e:
                skipped.append(f"{fname}: {e}")
                continue

            if fname.endswith("-result.md"):
                extract_test_result(path, text, acc, tests)
            elif fname.startswith("test-campaign-summary"):
                extract_campaign(path, text, acc, campaigns)
            elif fname.startswith("ilo-config-check") or fname.startswith("configure-run"):
                extract_config_check(path, text, acc)
            elif "redfish-endpoints" in fname:
                catalog.extend(extract_redfish_catalog(path, text))
            else:
                extract_lab_artifact(path, text, acc, artifacts)

            fw = extract_firmware(text)
            if fw:
                fm = parse_frontmatter(text)
                ip = fm.get("bmc_ip")
                if ip:
                    firmware.setdefault(ip, [])
                    have = {r["component"] for r in firmware[ip]}
                    firmware[ip].extend(r for r in fw if r["component"] not in have)

    servers = acc.finalize(artifacts)
    for s in servers:
        s["firmware"] = firmware.get(s["bmc_ip"], [])
        s["artifacts"] = [a for a in artifacts if a["bmc_ip"] == s["bmc_ip"]]

    catalog.sort(key=lambda c: c["seq"])

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "scripts/extract_hw_inventory.py",
        "provenance": "Verizon Far Edge lab certification campaigns, June 2026",
        "sources": [os.path.basename(s.rstrip("/")) for s in sources if os.path.isdir(s)],
        "servers": servers,
        "redfish_catalog": catalog,
        "tests": tests,
        "campaigns": campaigns,
        "artifacts": artifacts,
        "skipped": skipped,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", action="append", default=None,
                    help="source folder (repeatable); defaults to the two lab result folders")
    ap.add_argument("--out", default=DEFAULT_OUT, help=f"output JSON (default: {DEFAULT_OUT})")
    args = ap.parse_args()

    sources = args.src or DEFAULT_SOURCES
    print("Extracting hardware inventory")
    for s in sources:
        print(f"  src  {s}  {'ok' if os.path.isdir(s) else 'MISSING'}")

    data = build(sources)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n  out  {args.out}")
    print(f"\n  servers          {len(data['servers'])}")
    for s in data["servers"]:
        cs = s["check_summary"]
        print(f"    {s['id']:<16} {s['platform'] or '?':<36} "
              f"{s['status']:<21} checks={cs['total']:>2} tests={s['test_summary']['total']:>2}")
    print(f"  redfish endpoints {len(data['redfish_catalog'])}")
    print(f"  tests             {len(data['tests'])}")
    print(f"  campaigns         {len(data['campaigns'])}")
    print(f"  lab artifacts     {len(data['artifacts'])}")
    if data["skipped"]:
        print(f"  skipped           {len(data['skipped'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
