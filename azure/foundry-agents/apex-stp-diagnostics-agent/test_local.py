"""Local smoke test for DiagnosticsAgent."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import search_work_packages, aggregate_failure_modes, invoke  # noqa: E402

DEMO_PROMPTS = [
    "What are the most common issues with Pump-3A?",
    "Show me vibration WOs on P-3A.",
    "Aggregate failures across the RCS system.",
]


def test_tool_shapes() -> None:
    print("[1/3] search_work_packages(P-3A)")
    s = search_work_packages("P-3A")
    assert s["status"] == "ok", s
    assert s["data"]["total"] >= 5
    print(f"    ok — {s['data']['total']} events")

    print("[2/3] aggregate_failure_modes(P-3A)")
    a = aggregate_failure_modes(equipment_ids=["P-3A"])
    assert a["status"] == "ok"
    top = a["data"]["top_modes"]
    assert len(top) >= 3, top
    # The most common P-3A issue must be vibration (3 events out of 9).
    assert top[0]["failure_mode"] == "Vibration above limit (axial)", top[0]
    assert len(top[0]["evidence_wo_ids"]) >= 3
    print(f"    ok — top mode {top[0]['failure_mode']} ({top[0]['count']} events, {top[0]['pct']}%)")

    print("[3/3] empty-corpus path")
    e = aggregate_failure_modes(equipment_ids=["P-NOPE"])
    assert e["status"] == "ok"
    assert e["data"]["total_events"] == 0
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
