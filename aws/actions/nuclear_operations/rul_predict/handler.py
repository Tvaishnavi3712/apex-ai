"""
rul_predict — Remaining Useful Life prediction for an equipment item.

For demo night this reads the deterministic seed_anomalies corpus: if the
equipment has a seeded anomaly, return its expected_lead_days as the
prediction with realistic confidence bands. Otherwise return a healthy
90+ day forecast. Tomorrow morning the live SageMaker DeepAR endpoint
(`apex-signal-stp-rul`) will replace this body — the response shape is
already aligned to what that endpoint emits.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.append(str(Path(__file__).resolve().parents[3]))

from actions.sdk import apex_action, ApexActionSchema, ActionInputSchema, ActionOutputSchema  # noqa: E402
from actions.nuclear_operations._shared import (  # noqa: E402
    load_seed_anomalies, missing_data_envelope, index_by,
)

MODEL_VERSION = "apex-signal-stp-rul-v1-cached"


def _make_curve(days_until_failure: int, horizon_days: int) -> List[Dict[str, Any]]:
    """Build a per-day forecast curve with rising failure probability."""
    today = datetime.now(timezone.utc).date()
    out: List[Dict[str, Any]] = []
    for i in range(horizon_days + 1):
        days_left = max(0, days_until_failure - i)
        # Probability rises sigmoidally as we approach failure
        if days_until_failure > 0:
            x = (i - days_until_failure / 2) / max(1, days_until_failure / 4)
            prob = 1.0 / (1.0 + 2.71828 ** (-x))
        else:
            prob = 1.0
        out.append({
            "date": (today + timedelta(days=i)).isoformat(),
            "days_remaining": days_left,
            "prob_failure_pct": round(prob * 100, 1),
        })
    return out


@apex_action(ApexActionSchema(
    name="rul_predict",
    description="Predict Remaining Useful Life (days until failure) for an equipment, with 80% and 95% confidence bands.",
    category="ml_inference",
    industry="nuclear_operations",
    input_schema=ActionInputSchema(description="RUL prediction request")
        .add_string("equipment_id", "Equipment id, e.g. P-3A", required=True)
        .add_number("horizon_days", "Forecast horizon in days (default 30)", required=False),
    output_schema=ActionOutputSchema(description="RUL forecast envelope")
        .add_string("status", "ok | error")
        .add_number("days_until_failure", "Most likely days until failure")
        .add_number("confidence_lower_80", "80% lower bound")
        .add_number("confidence_upper_80", "80% upper bound")
        .add_number("confidence_lower_95", "95% lower bound")
        .add_number("confidence_upper_95", "95% upper bound")
        .add_string("forecast_curve", "Per-day {date, days_remaining, prob_failure_pct}")
        .add_string("model_version", "Model identifier"),
))
def rul_predict(equipment_id: str, horizon_days: int = 30) -> dict:
    """Predict RUL for `equipment_id`. Reads cached anomaly data tonight; SageMaker tomorrow."""
    if not equipment_id:
        return {"status": "error", "error_type": "bad_arguments", "message": "equipment_id is required"}

    anomalies = load_seed_anomalies()
    if anomalies is None:
        return missing_data_envelope("seed_anomalies.json")

    eq_anomaly = next((a for a in anomalies if a.get("equipment_id") == equipment_id), None)
    horizon_days = max(1, int(horizon_days or 30))

    if eq_anomaly:
        d = int(eq_anomaly.get("expected_lead_days", 21))
        return {
            "status": "ok",
            "equipment_id": equipment_id,
            "days_until_failure": d,
            "confidence_lower_80": max(1, int(d * 0.7)),
            "confidence_upper_80": int(d * 1.3),
            "confidence_lower_95": max(1, int(d * 0.5)),
            "confidence_upper_95": int(d * 1.6),
            "forecast_curve": _make_curve(d, horizon_days),
            "model_version": MODEL_VERSION,
            "based_on_anomaly": eq_anomaly.get("anomaly_id"),
            "expected_failure_mode": eq_anomaly.get("expected_failure_mode"),
            "scripted_message": eq_anomaly.get("scripted_message"),
        }

    # Healthy asset — return long-horizon forecast
    return {
        "status": "ok",
        "equipment_id": equipment_id,
        "days_until_failure": 180,
        "confidence_lower_80": 130,
        "confidence_upper_80": 240,
        "confidence_lower_95": 90,
        "confidence_upper_95": 365,
        "forecast_curve": _make_curve(180, horizon_days),
        "model_version": MODEL_VERSION,
        "based_on_anomaly": None,
        "expected_failure_mode": None,
        "scripted_message": None,
        "health_status": "nominal",
    }


def handler(event, context=None):
    return rul_predict(
        equipment_id=event.get("equipment_id", ""),
        horizon_days=int(event.get("horizon_days", 30)),
    )
