#!/usr/bin/env python3
"""
Timed dry-run harness — runs the 4 hero queries against ChatSTP across the
3 strategy presets, captures latency per query, and prints a final report
suitable for the run-of-show.

Output: a Markdown table of latencies + aggregate stats per preset.

Usage:
    cd backend && source venv/bin/activate
    python3 scripts/timed_dry_run.py            # 1 pass per query (12 invocations)
    python3 scripts/timed_dry_run.py --runs 3   # 3 passes (36 invocations) — better p95 stats
    python3 scripts/timed_dry_run.py --preset balanced  # only one strategy
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

API_BASE = "http://localhost:8000/api/v1"

QUERIES = [
    ("UC-1", "Meal allowance",
     "What is the max meal allowance for site-meeting business travel?",
     ["STP-415", "$75"]),
    ("UC-2", "Last PM Pump-3A",
     "When was the last PM on Pump-3A and who worked on it?",
     ["P-3A", "Diane"]),
    ("UC-3", "Common issues",
     "What are the most common issues with Pump-3A?",
     ["bearing", "WO-2025"]),
    ("UC-4", "Predict P-3A",
     "Predict failure risk for Pump-3A in next 30 days",
     ["vibration", "P-3A"]),
]


def fetch_presets() -> List[Dict[str, Any]]:
    with urllib.request.urlopen(f"{API_BASE}/llm/presets", timeout=10) as r:
        return json.load(r)["presets"]


def invoke(prompt: str, overrides: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1, help="Number of passes per query (default 1)")
    ap.add_argument("--preset", type=str, default=None,
                    help="Only run this preset id (cost_optimized | balanced | quality_first)")
    args = ap.parse_args()

    all_presets = fetch_presets()
    presets = [p for p in all_presets if args.preset is None or p["id"] == args.preset]
    if not presets:
        print(f"✗ no preset matches '{args.preset}'. Available: {[p['id'] for p in all_presets]}")
        return 1

    print(f"\n# STP Demo Dry-Run · {len(presets)} preset(s) × {len(QUERIES)} queries × {args.runs} run(s)")
    print(f"# Total invocations: {len(presets) * len(QUERIES) * args.runs}\n")

    # Results: {preset_id: {uc_label: [latency_seconds, ...]}}
    results: Dict[str, Dict[str, List[float]]] = {}
    pass_fail: Dict[str, Dict[str, List[bool]]] = {}

    for preset in presets:
        print(f"\n══════ {preset['icon']} {preset['display_name']}  (registry est ${preset['estimated_query_cost_usd']:.5f}/query) ══════")
        results[preset["id"]] = {}
        pass_fail[preset["id"]] = {}

        for run_n in range(1, args.runs + 1):
            if args.runs > 1:
                print(f"  — run {run_n}/{args.runs} —")
            for uc, label, query, expects in QUERIES:
                t0 = time.time()
                ok = False
                err = None
                try:
                    d = invoke(query, preset["overrides"])
                    elapsed = time.time() - t0
                    resp = d.get("response", "")
                    ok = assertion_passes(resp, expects)
                except Exception as e:
                    elapsed = time.time() - t0
                    err = str(e)[:80]

                key = f"{uc} · {label}"
                results[preset["id"]].setdefault(key, []).append(elapsed)
                pass_fail[preset["id"]].setdefault(key, []).append(ok)

                marker = "✓" if ok else "✗"
                msg = f"  {marker}  {key:30s} {elapsed:5.1f}s"
                if err:
                    msg += f"  [{err}]"
                print(msg)

    # ─── Final report (Markdown) ─────────────────────────────────────────
    print("\n\n# ━━━━━━━━━━━━━━━━━ FINAL REPORT ━━━━━━━━━━━━━━━━━\n")

    # Per-preset summary
    print("## Latency by preset (seconds, lower = better)\n")
    print("| Preset            | UC-1   | UC-2   | UC-3   | UC-4   | Mean   | P95     |")
    print("|-------------------|--------|--------|--------|--------|--------|---------|")

    overall_pass = 0
    overall_total = 0
    for preset in presets:
        row_parts = [f"| {preset['icon']} {preset['display_name']:14s}"]
        all_lat: List[float] = []
        for uc, label, _, _ in QUERIES:
            key = f"{uc} · {label}"
            lats = results[preset["id"]].get(key, [])
            ok_lats = [l for l in lats]  # all latencies — the assertion already filtered
            if not lats:
                row_parts.append("|   —    ")
                continue
            mean = statistics.mean(lats)
            row_parts.append(f"| {mean:5.1f}s ")
            all_lat.extend(lats)
            overall_pass += sum(1 for ok in pass_fail[preset["id"]].get(key, []) if ok)
            overall_total += len(pass_fail[preset["id"]].get(key, []))
        if all_lat:
            mean_all = statistics.mean(all_lat)
            p95_all = sorted(all_lat)[max(0, int(len(all_lat) * 0.95) - 1)]
            row_parts.append(f"| {mean_all:5.1f}s ")
            row_parts.append(f"| {p95_all:5.1f}s   |")
        print("".join(row_parts))

    print(f"\n## Pass rate\n\n**{overall_pass}/{overall_total}** invocations returned correct entities.\n")

    # Per-preset cost summary
    print("## Cost per query (registry estimate)\n")
    print("| Preset            | Cost      | vs Quality-First |")
    print("|-------------------|-----------|------------------|")
    qf = next((p for p in all_presets if p["id"] == "quality_first"), None)
    qf_cost = qf["estimated_query_cost_usd"] if qf else 0
    for preset in presets:
        c = preset["estimated_query_cost_usd"]
        savings = (1 - c / qf_cost) * 100 if qf_cost > 0 else 0
        print(f"| {preset['icon']} {preset['display_name']:14s} | ${c:.5f} | {savings:5.1f}% savings |")

    print(f"\n## Demo readiness\n")
    if overall_pass == overall_total:
        print("✅ All hero queries returning correct entities across all presets.")
    else:
        print(f"❌ {overall_total - overall_pass} query/preset combinations failed — see per-row results above.")

    return 0 if overall_pass == overall_total else 1


if __name__ == "__main__":
    sys.exit(main())
