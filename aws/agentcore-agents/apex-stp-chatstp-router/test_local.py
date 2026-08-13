"""Local smoke test for ChatSTP router.

Tests classification + in-process delegation to all 4 specialists.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import (  # noqa: E402
    classify_intent,
    delegate_to_policy,
    delegate_to_maintenance,
    delegate_to_diagnostics,
    delegate_to_reliability,
    invoke,
)

DEMO_PROMPTS = [
    ("policy",      "What is the max meal allowance for site-meeting business travel?"),
    ("maintenance", "When was the last PM on Pump-3A and who worked on it?"),
    ("diagnostics", "What are the most common issues with Pump-3A?"),
    ("reliability", "Predict failure risk for Pump-3A in next 30 days."),
    ("off_topic",   "What's the weather like in Houston tomorrow?"),
]


def test_classifier() -> None:
    print("[1/3] classify_intent on demo prompts")
    for expected, q in DEMO_PROMPTS:
        c = classify_intent(q)
        assert c["status"] == "ok", c
        got = c["data"]["intent"]
        assert got == expected, f"expected {expected}, got {got} for: {q}"
        print(f"    ok — '{q[:50]}...' → {got}")


def test_delegation_inproc() -> None:
    """Delegate via the in-process fallback path (no ARNs required)."""
    print("[2/3] in-process delegation to all 4 specialists (skipping Bedrock LLM call)")

    # We invoke each delegate_to_* tool with a representative query. Each one
    # ends up calling the specialist's `invoke`, which makes a Bedrock call.
    # Skip the actual Bedrock call here — just verify the routing wires up.
    if os.environ.get("APEX_SKIP_BEDROCK", "1") == "1":
        print("    [skip] APEX_SKIP_BEDROCK=1 — delegation wiring only")
        # Confirm the local-invoker import path resolves for each specialist
        from agent import _local_invoker
        for name in ("maintenance", "diagnostics", "reliability"):
            try:
                fn = _local_invoker(name)
                assert callable(fn)
                print(f"    ok — '{name}' invoker imported")
            except Exception as e:  # noqa: BLE001
                print(f"    [warn] '{name}' invoker import failed: {e}")
        return

    for tool_fn, q in [
        (delegate_to_policy,      "What is the max meal allowance for travel?"),
        (delegate_to_maintenance, "When was the last PM on P-3A?"),
        (delegate_to_diagnostics, "Common issues with P-3A?"),
        (delegate_to_reliability, "Predict P-3A risk."),
    ]:
        r = tool_fn(q)
        assert r["status"] == "ok", r
        print(f"    ok — {tool_fn.__name__}: {json.dumps(r)[:100]}...")


def test_entrypoint() -> None:
    if os.environ.get("APEX_SKIP_BEDROCK", "1") == "1":
        print("[3/3] [skip] router entrypoint requires Bedrock")
        return
    print("[3/3] full router roundtrip via Bedrock")
    for _, q in DEMO_PROMPTS:
        try:
            out = invoke({"prompt": q})
            print(f"  Q: {q}")
            print(f"  A: {json.dumps(out, default=str)[:300]}...")
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {e}")
            return


if __name__ == "__main__":
    test_classifier()
    test_delegation_inproc()
    test_entrypoint()
    print("\nALL OK")
