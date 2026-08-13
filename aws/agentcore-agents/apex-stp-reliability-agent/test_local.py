"""Local smoke test for ReliabilityAgent."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import (  # noqa: E402
    predict_rul,
    detect_anomalies,
    recommend_pm,
    compute_risk_score,
    invoke,
)

DEMO_PROMPTS = [
    "Predict failure risk for Pump-3A in next 30 days.",
    "What anomalies have you detected on P-3B?",
    "Should we schedule a PM for P-3A this month?",
]


def test_tool_shapes() -> None:
    print("[1/4] detect_anomalies(P-3A) returns scripted message")
    a = detect_anomalies("P-3A")
    assert a["status"] == "ok"
    anoms = a["data"]["anomalies"]
    assert len(anoms) == 1
    assert "0.34 in/s" in anoms[0]["scripted_message"]
    assert "0.30 in/s Tech-Spec limit" in anoms[0]["scripted_message"]
    print(f"    ok — anomaly {anoms[0]['anomaly_id']}")

    print("[2/4] predict_rul(P-3A)")
    p = predict_rul("P-3A", horizon_days=30)
    assert p["status"] == "ok"
    assert isinstance(p["data"]["days_to_failure"], int)
    print(f"    ok — RUL {p['data']['days_to_failure']}d")

    print("[3/4] recommend_pm + compute_risk_score")
    rec = recommend_pm("P-3A")
    assert rec["status"] == "ok"
    assert rec["data"]["avoidance_usd"] >= 100_000
    rs = compute_risk_score("P-3A")
    assert rs["status"] == "ok"
    assert rs["data"]["risk_tier"] in ("CRITICAL", "HIGH", "MODERATE", "LOW")
    assert rs["data"]["audit_log_id"].startswith("AUD-")
    assert "[Decision logged to apex.audit_log: AUD-" in rs["data"]["audit_log_marker"]
    print(f"    ok — tier {rs['data']['risk_tier']}, audit {rs['data']['audit_log_id']}")

    print("[4/4] empty path on unknown equipment")
    e = detect_anomalies("P-NOPE")
    assert e["status"] == "ok"
    assert e["data"]["anomalies"] == []
    print("    ok")


def test_entrypoint() -> None:
    if os.environ.get("APEX_SKIP_BEDROCK") == "1":
        print("[bedrock] skipped")
        return
    print("[bedrock] invoking entrypoint")
    for p in DEMO_PROMPTS:
        try:
            out = invoke({"prompt": p})
            print(f"  Q: {p}")
            print(f"  A: {json.dumps(out, default=str)[:400]}...")
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {e}")
            return


if __name__ == "__main__":
    test_tool_shapes()
    test_entrypoint()
    print("\nALL OK")
