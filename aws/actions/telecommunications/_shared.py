"""
Shared helpers for the telecommunications industry action handlers.

The four telco-specific agents — CertificationAgent, SchemaWatchAgent,
UpgradeAdvisorAgent, MentorAgent — reuse small read-only helpers that
load synthetic data from `synthetic-data/<customer>/`. Today the only
customer demo is Verizon Far Edge (`synthetic-data/verizon_far_edge/`).
When additional carrier customers are onboarded (AT&T, T-Mobile, etc.),
the DATA_ROOT resolution becomes customer-aware via an env override.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Resolve the repo root so handlers don't care about their nesting.
REPO_ROOT = Path(__file__).resolve().parents[2]

# Customer-specific data root. Set APEX_TELCO_CUSTOMER=<name> to switch
# data folders when multiple customer demos coexist under telecommunications.
# Default: Verizon Far Edge (the launch customer).
_CUSTOMER = os.environ.get("APEX_TELCO_CUSTOMER", "verizon_far_edge")
DATA_ROOT = REPO_ROOT / "synthetic-data" / _CUSTOMER


def data_path(relative: str) -> Path:
    """Resolve a path inside the active telco customer's synthetic-data folder."""
    return DATA_ROOT / relative


def load_json(relative: str) -> Optional[Dict[str, Any]]:
    """Load a JSON file under the active telco customer data folder, or None if missing."""
    p = data_path(relative)
    if not p.is_file():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def load_csv(relative: str) -> List[Dict[str, str]]:
    """Load a CSV file under the active telco customer data folder as list[dict]."""
    p = data_path(relative)
    if not p.is_file():
        return []
    with p.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def missing_data_envelope(filename: str) -> Dict[str, Any]:
    """Standard error envelope when a seed file is missing."""
    return {
        "status": "error",
        "error_type": "missing_data",
        "message": f"Telco seed data file missing for customer {_CUSTOMER}: {filename}",
        "remediation": f"Regenerate via the synthetic-data scripts under synthetic-data/{_CUSTOMER}/.",
    }


def classify_failure_message(msg: str) -> Dict[str, str]:
    """Apply the canonical classification rules to a ROBOT failure message.

    Returns {category, severity}. The rules match those in the
    robot-framework-certification-output blueprint."""
    m = (msg or "").lower()
    if any(k in m for k in ("latency", "exceeds threshold", "threshold exceeded", "throughput", "packet loss")):
        if "latency" in m or "throughput" in m or "packet loss" in m:
            return {"category": "latency_threshold_breach", "severity": "P1"}
    if any(k in m for k in ("deprecated", "field missing", "schema changed", "endpoint moved", "field not found", "schema change")):
        return {"category": "schema_drift_failure", "severity": "P1"}
    if any(k in m for k in ("regression", "baseline not maintained", "previously passing")):
        return {"category": "regression_failure", "severity": "P2"}
    if any(k in m for k in ("borderline", "within tolerance", "monitor", "p99 approaching")):
        return {"category": "investigate", "severity": "P3"}
    return {"category": "investigate", "severity": "P3"}


def kb_lookup(failure_message: str) -> Optional[Dict[str, str]]:
    """Heuristic match a failure message to a customer KB entry. Demo-grade."""
    m = (failure_message or "").lower()
    if "powerstate" in m and ("not found" in m or "moved" in m):
        return {"id": "KB-WIND-RIVER-2412-S321", "title": "PowerState relocated to Status.PowerState",
                "workaround": "Update scripts: Systems/1.PowerState → Systems/1.Status.PowerState",
                "fix_version": "n/a (schema change, permanent in v1.16.0)"}
    if "fanspeeds" in m or "currentreading" in m:
        return {"id": "KB-WIND-RIVER-2412-S322", "title": "FanSpeeds renamed to Fans",
                "workaround": "Rename FanSpeeds[].CurrentReading to Fans[].Reading in 5 scripts",
                "fix_version": "n/a (schema change, permanent in v1.16.0)"}
    if "ipv6addresses" in m and ("missing" in m or "required" in m):
        return {"id": "KB-WIND-RIVER-2412-S323", "title": "IPv6Addresses now required",
                "workaround": "Populate IPv6Addresses: [] in interface payloads",
                "fix_version": "n/a (schema change, permanent in v1.16.0)"}
    if "rt-kernel" in m or ("p99" in m and "core" in m):
        return {"id": "KB-2026-0118", "title": "CU-UP latency degradation under default RT tuning",
                "workaround": "kernel.sched_rt_runtime_us=980000",
                "fix_version": "25.01"}
    return None
