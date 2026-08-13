"""
parse_robot_output — read a ROBOT Framework XML test output and return a
structured summary (suite metadata + per-test results) for
CertificationAgent to classify.

Reads the synthetic ROBOT XML under
`synthetic-data/verizon_far_edge/robot_outputs/` when no explicit path is
supplied — so the agent has a working demo input out of the box.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.telecommunications._shared import data_path, missing_data_envelope  # noqa: E402

DEFAULT_XML = "robot_outputs/robot_output_caas_node_v2412_full.xml"


def _first_fail_msg(elem: ET.Element) -> Optional[str]:
    """Return the first <msg level='FAIL'> text under elem, if any."""
    for m in elem.iter("msg"):
        if m.attrib.get("level") in ("FAIL", "ERROR"):
            return (m.text or "").strip()
    return None


def _first_warn_msg(elem: ET.Element) -> Optional[str]:
    for m in elem.iter("msg"):
        if m.attrib.get("level") == "WARN":
            return (m.text or "").strip()
    return None


def _library_for(elem: ET.Element) -> Optional[str]:
    kw = elem.find(".//kw")
    return kw.attrib.get("library") if kw is not None else None


def _redfish_endpoint_for(elem: ET.Element, msg: Optional[str]) -> Optional[str]:
    """Pull a /redfish/... endpoint reference from kw args or msg text."""
    kw = elem.find(".//kw")
    if kw is not None:
        for arg in kw.findall("arg"):
            t = (arg.text or "").strip()
            if t.startswith("/redfish/"):
                return t
    if msg and "/redfish/" in msg:
        i = msg.find("/redfish/")
        return msg[i:].split()[0].rstrip(".,")
    return None


@apex_action(ApexActionSchema(
    name="parse_robot_output",
    description="Parse a ROBOT Framework XML test output into structured test results + suite metadata.",
    category="document_parsing",
    industry="telecommunications",
    input_schema=ActionInputSchema(description="ROBOT output parse request")
        .add_string("file_path", "Absolute or repo-relative path to the XML. Defaults to the bundled demo XML.", required=False),
    output_schema=ActionOutputSchema(description="Structured parse result")
        .add_string("status",              "ok | error")
        .add_string("test_suite_name",     "Suite name attribute")
        .add_string("device_under_test",   "Device metadata")
        .add_string("firmware_version",    "Firmware under test")
        .add_string("cycle_id",            "Cycle identifier")
        .add_string("region",              "Region metadata")
        .add_number("total_tests",         "Total test count")
        .add_number("passed_tests",        "Passed count")
        .add_number("failed_tests",        "Failed count")
        .add_number("warn_tests",          "Tests with WARN-level messages")
        .add_string("test_results",        "List of per-test records: {test_id, name, status, library, failure_message, redfish_endpoint}")
        .add_string("categories",          "Tag-grouped statistics if present"),
))
def parse_robot_output(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Parse the ROBOT XML — returns a structured summary that downstream
    actions (classify_failures, build_jira_tickets) can consume directly."""
    p = Path(file_path) if file_path else data_path(DEFAULT_XML)
    if not p.is_file():
        return missing_data_envelope(p.name)

    try:
        tree = ET.parse(p)
    except ET.ParseError as e:
        return {"status": "error", "error_type": "parse_error",
                "message": f"Could not parse ROBOT XML: {e}"}

    root = tree.getroot()
    suite = root.find("suite")
    if suite is None:
        return {"status": "error", "error_type": "schema_error",
                "message": "No <suite> element found in ROBOT XML"}

    meta = {item.attrib.get("name"): (item.text or "")
            for item in suite.findall("metadata/item")}

    tests: List[Dict[str, Any]] = []
    for t in suite.iter("test"):
        status_elem = None
        for child in t:
            if child.tag == "status":
                status_elem = child
        status_attr = (status_elem.attrib.get("status") if status_elem is not None else "PASS") or "PASS"
        fail_msg = _first_fail_msg(t)
        warn_msg = _first_warn_msg(t) if status_attr == "PASS" else None
        record = {
            "test_id":          t.attrib.get("id"),
            "name":             t.attrib.get("name"),
            "status":           "WARN" if (warn_msg and status_attr == "PASS") else status_attr,
            "library":          _library_for(t),
            "failure_message":  fail_msg or warn_msg,
            "redfish_endpoint": _redfish_endpoint_for(t, fail_msg or warn_msg),
            "starttime":        status_elem.attrib.get("starttime") if status_elem is not None else None,
            "endtime":          status_elem.attrib.get("endtime")   if status_elem is not None else None,
        }
        tests.append(record)

    passed = sum(1 for r in tests if r["status"] == "PASS")
    failed = sum(1 for r in tests if r["status"] == "FAIL")
    warned = sum(1 for r in tests if r["status"] == "WARN")

    # Pull tag-level statistics if present
    categories = []
    for stat in root.findall(".//statistics/tag/stat"):
        categories.append({
            "tag":  (stat.text or "").strip(),
            "pass": int(stat.attrib.get("pass", 0)),
            "fail": int(stat.attrib.get("fail", 0)),
        })

    return {
        "status":            "ok",
        "test_suite_name":   suite.attrib.get("name", ""),
        "device_under_test": meta.get("device_under_test", ""),
        "firmware_version":  meta.get("firmware_version", ""),
        "cycle_id":          meta.get("cycle_id", ""),
        "region":            meta.get("region", ""),
        "total_tests":       len(tests),
        "passed_tests":      passed,
        "failed_tests":      failed,
        "warn_tests":        warned,
        "test_results":      tests,
        "categories":        categories,
        "source_file":       str(p),
    }
