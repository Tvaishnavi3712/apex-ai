"""
anomaly_detect — surface seeded anomaly windows for an equipment item.

Reads `seed_anomalies.json` and returns any anomaly attached to the given
equipment, formatted as the agent expects. Tomorrow morning this gets
swapped for live `apex-signal-stp-anomaly` (Random Cut Forest) endpoint —
the response shape already matches.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_seed_anomalies, missing_data_envelope, parse_date,
)

MODEL_VERSION = "apex-signal-stp-anomaly-v1-cached"


def _severity_for_z(z: float) -> str:
    """Map z-score → severity tier."""
    if z >= 3.5:
        return "CRITICAL"
    if z >= 3.0:
        return "HIGH"
    if z >= 2.0:
        return "MODERATE"
    return "LOW"


@apex_action(ApexActionSchema(
    name="anomaly_detect",
    description="Detect anomaly windows on an equipment's sensor streams within a recent time window.",
    category="ml_inference",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="Anomaly detection request")
        .add_string("equipment_id", "Equipment id, e.g. P-3A", required=True)
        .add_number("lookback_days", "How many days to scan (default 14)", required=False),
    output_schema=ActionOutputSchema(description="Anomaly report envelope")
        .add_string("status", "ok | error")
        .add_string("anomalies_detected", "List of {channel, drift_type, magnitude, started_at, current_value, baseline_value, severity, scripted_message}")
        .add_number("overall_anomaly_score", "0-100 aggregate")
        .add_string("first_detected_at", "ISO-8601 of earliest anomaly")
        .add_string("model_version", "Model identifier"),
))
def anomaly_detect(equipment_id: str, lookback_days: int = 14) -> dict:
    """Return seeded anomalies that target `equipment_id` within `lookback_days`."""
    if not equipment_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "equipment_id is required"}

    anomalies = load_seed_anomalies()
    if anomalies is None:
        return missing_data_envelope("seed_anomalies.json")

    cutoff = datetime.now(timezone.utc) - timedelta(days=int(lookback_days or 14))
    detected: List[Dict[str, Any]] = []
    earliest: datetime = datetime.max.replace(tzinfo=timezone.utc)

    for an in anomalies:
        if an.get("equipment_id") != equipment_id:
            continue
        started = parse_date(an.get("started_at") or an.get("detected_at"))
        if started and started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        if started and started < cutoff:
            continue
        z = float(an.get("z_score", 0))
        detected.append({
            "anomaly_id": an.get("anomaly_id"),
            "channel": an.get("channel") or an.get("sensor"),
            "drift_type": an.get("drift_type"),
            "magnitude": an.get("magnitude"),
            "started_at": an.get("started_at"),
            "detected_at": an.get("detected_at"),
            "current_value": an.get("value"),
            "limit_value": an.get("limit"),
            "z_score": z,
            "trend": an.get("trend"),
            "severity": _severity_for_z(z),
            "scripted_message": an.get("scripted_message"),
            "expected_failure_mode": an.get("expected_failure_mode"),
        })
        if started and started < earliest:
            earliest = started

    overall = 0
    if detected:
        # Worst severity drives the overall score
        z_scores = [d["z_score"] for d in detected if d.get("z_score") is not None]
        overall = int(min(100, max(0, max(z_scores) * 25))) if z_scores else 0

    return {
        "status": "ok",
        "equipment_id": equipment_id,
        "anomalies_detected": detected,
        "overall_anomaly_score": overall,
        "first_detected_at": earliest.isoformat() if detected else None,
        "model_version": MODEL_VERSION,
        "lookback_days": int(lookback_days or 14),
    }


def handler(event, context=None):
    return anomaly_detect(
        equipment_id=event.get("equipment_id", ""),
        lookback_days=int(event.get("lookback_days", 14)),
    )
