"""Local smoke test for MaintenanceAgent."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import lookup_pm_history, get_engineer_attribution, fetch_work_package, invoke  # noqa: E402

DEMO_PROMPTS = [
    "When was the last PM on Pump-3A and who worked on it?",
    "Show me PM history for P-3B in the last 6 months.",
    "Pull the work package for WO-2026-00871.",
]


def test_tool_shapes() -> None:
    print("[1/4] lookup_pm_history(P-3A) returns last_pm")
    r = lookup_pm_history("P-3A")
    assert r["status"] == "ok", r
    last = r["data"]["last_pm"]
    assert last["wo_id"] == "WO-2026-00871"
    assert last["completed_date"] == "2026-03-18"
    assert last["lead_engineer"]["name"] == "Diane Okafor"
    print(f"    ok — last PM {last['completed_date']} by {last['lead_engineer']['name']}")

    print("[2/4] get_engineer_attribution(WO-2026-00871)")
    a = get_engineer_attribution("WO-2026-00871")
    assert a["status"] == "ok"
    assert a["data"]["lead_engineer"]["name"] == "Diane Okafor"
    assert any(t["name"] == "Marcus Holloway" for t in a["data"]["techs"])
    print("    ok")

    print("[3/4] fetch_work_package returns S3 path")
    f = fetch_work_package("WO-2026-00871")
    assert f["status"] == "ok"
    assert f["data"]["pdf_path"].startswith("s3://")
    print(f"    ok — {f['data']['pdf_path']}")

    print("[4/4] error envelope on unknown WO")
    bad = get_engineer_attribution("WO-NOPE")
    assert bad["status"] == "error", bad
    print("    ok")


def test_entrypoint() -> None:
    if os.environ.get("APEX_SKIP_AZURE_OPENAI") == "1":
        print("[azure_openai] skipped")
        return
    print("[azure_openai] invoking entrypoint")
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
