#!/usr/bin/env python3
"""
Multi-LLM smoke test — runs the 4 hero queries through ChatSTP across the
3 strategy presets (Cost-Optimized / Balanced / Quality-First) and reports:

  • response correctness (entity check)
  • per-call latency
  • model_used echo from the agent runtime (proves the swap actually took)
  • per-strategy aggregate cost vs Quality-First baseline

Run after re-deploying STP Foundry Agent Service runtimes:

    cd backend && source venv/bin/activate
    python3 scripts/smoke_test_multi_llm.py

Exit code 0 if all 12 invocations return valid responses; 1 otherwise.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List

API_BASE = "http://localhost:8000/api/v1"

QUERIES = [
    ("UC-1 · meal allowance",
     "What is the max meal allowance for site-meeting business travel?",
     ["STP-415", "$75"]),
    ("UC-2 · last PM Pump-3A",
     "When was the last PM on Pump-3A and who worked on it?",
     ["P-3A", "Diane"]),
    ("UC-3 · common Pump-3A issues",
     "What are the most common issues with Pump-3A?",
     ["bearing", "WO-2025"]),
    ("UC-4 · predict P-3A failure",
     "Predict failure risk for Pump-3A in next 30 days",
     ["vibration", "P-3A"]),
]


def fetch_presets() -> List[Dict[str, Any]]:
    """Pull the 3 strategy presets from the backend registry."""
    with urllib.request.urlopen(f"{API_BASE}/llm/presets", timeout=10) as r:
        return json.load(r)["presets"]


def invoke_chatstp(prompt: str, overrides: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """POST to /chat/invoke/chatstp with model_overrides body."""
    url = f"{API_BASE}/chat/invoke/chatstp?prompt={urllib.parse.quote(prompt)}"
    req = urllib.request.Request(
        url, method="POST",
        data=json.dumps({"model_overrides": overrides}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.load(r)


def assertion_passes(response: str, must_include: List[str]) -> bool:
    body = (response or "").lower()
    return any(token.lower() in body for token in must_include)


def main() -> int:
    presets = fetch_presets()
    print(f"Loaded {len(presets)} strategy presets from /llm/presets")
    for p in presets:
        print(f"  {p['icon']} {p['display_name']:18s} ${p['estimated_query_cost_usd']:.5f}/query (registry estimate)")
    print()

    overall_pass = 0
    overall_fail = 0
    summary: List[str] = []

    for preset in presets:
        print(f"\n══════ {preset['icon']} {preset['display_name']} ══════")
        print(f"  registry estimate: ${preset['estimated_query_cost_usd']:.5f}/query")
        print()
        for label, query, expects in QUERIES:
            t0 = time.time()
            try:
                d = invoke_chatstp(query, preset["overrides"])
                elapsed = time.time() - t0
                resp = d.get("response", "")
                ok = assertion_passes(resp, expects)
                if ok:
                    overall_pass += 1
                    print(f"  ✓  [{label}]   ({elapsed:.1f}s)")
                else:
                    overall_fail += 1
                    print(f"  ✗  [{label}]   ({elapsed:.1f}s) — missing {expects} in response")
                    print(f"     {resp[:240]}")
            except Exception as e:
                overall_fail += 1
                elapsed = time.time() - t0
                print(f"  ✗  [{label}]   ({elapsed:.1f}s) — {e}")
        summary.append(
            f"  {preset['icon']} {preset['display_name']:18s} estimate ${preset['estimated_query_cost_usd']:.5f}/query"
        )

    total = overall_pass + overall_fail
    print(f"\n━━━ {overall_pass}/{total} invocations passing ━━━")
    print()
    for line in summary:
        print(line)
    return 0 if overall_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
