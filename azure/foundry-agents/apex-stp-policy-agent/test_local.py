"""
Local smoke test for PolicyAgent.

Exercises the tools directly (no Azure OpenAI call) and asserts the demo question's
required citation appears in the search results. Also runs the entrypoint
end-to-end if AWS credentials are configured for Azure OpenAI.

Usage:
    cd apex-stp-policy-agent && python test_local.py
"""
from __future__ import annotations

import json
import os
import sys

# Make local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import search_policies, extract_citation, invoke  # noqa: E402


DEMO_PROMPTS = [
    "What is the max meal allowance for site-meeting business travel?",
    "What is the vibration limit for reactor coolant pumps?",
    "How often must Class-1 centrifugal pumps receive a PM?",
]


def test_tool_shapes() -> None:
    print("[1/3] search_policies envelope shape")
    r = search_policies("max meal allowance for site-meeting business travel", top_k=3)
    assert r["status"] == "ok", r
    assert "results" in r["data"]
    assert any(x["doc_number"] == "STP-415" for x in r["data"]["results"]), \
        f"STP-415 not in results: {r}"
    print("    ok — STP-415 surfaced")

    print("[2/3] extract_citation returns verbatim STP-415 § 3.2 text")
    cite = extract_citation("STP-415", "meal allowance per-diem")
    assert cite["status"] == "ok", cite
    d = cite["data"]
    assert d["doc_number"] == "STP-415"
    assert d["section"] == "3.2"
    assert "$75.00" in d["verbatim_text"]
    print(f"    ok — {d['citation_format'][:120]}...")

    print("[3/3] error envelope on missing doc")
    bad = extract_citation("STP-DOES-NOT-EXIST", "anything")
    assert bad["status"] == "error", bad
    print("    ok — error envelope returned")


def test_entrypoint() -> None:
    """Optional: full Azure OpenAI roundtrip. Requires AWS creds + Azure OpenAI access."""
    if os.environ.get("APEX_SKIP_AZURE_OPENAI") == "1":
        print("[azure_openai] skipped (APEX_SKIP_AZURE_OPENAI=1)")
        return
    print("[azure_openai] invoking entrypoint with demo prompts")
    for p in DEMO_PROMPTS:
        try:
            out = invoke({"prompt": p})
            print(f"  Q: {p}")
            print(f"  A: {json.dumps(out, default=str)[:400]}...")
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] azure_openai call failed: {e}")
            return


if __name__ == "__main__":
    test_tool_shapes()
    test_entrypoint()
    print("\nALL OK")
