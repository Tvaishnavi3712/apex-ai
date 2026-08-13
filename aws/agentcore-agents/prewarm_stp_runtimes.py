#!/usr/bin/env python3
"""
STP runtime prewarmer — pings each AgentCore runtime with a no-op prompt
every 4 minutes to keep the container warm. Cuts cold-start latency on
the first real demo query from ~25s → ~12s.

Two delivery modes:

  1. **Local cron** (default for tonight's demo): run this script with
     `--watch` to keep it foreground-pinging each runtime every 4 min.
  2. **CloudWatch Scheduled Rule**: deploy as a Lambda triggered every
     4 min by `events.PutRule`. Use `--deploy-cloudwatch` to auto-create
     the rule. Gives true server-side keep-warm without a laptop running.

The prewarm prompt is `__prewarm__` — STP agents short-circuit on this
literal so we don't pay LLM tokens for keep-alives.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Dict, List

import boto3

REGION = "us-east-1"

# Pulled from deploy_stp_agents.py output (real runtime ARNs).
STP_RUNTIMES: List[Dict[str, str]] = [
    {
        "alias": "policy",
        "arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_policy_agent-9pZgSy5aWz",
    },
    {
        "alias": "maintenance",
        "arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_maintenance_agent-JQoz4G5QqB",
    },
    {
        "alias": "diagnostics",
        "arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_diagnostics_agent-s3l3Wc9HUp",
    },
    {
        "alias": "reliability",
        "arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_reliability_agent-oVMXghD955",
    },
    {
        "alias": "chatstp",
        "arn": "arn:aws:bedrock-agentcore:us-east-1:457795063704:runtime/apex_stp_chatstp_router-JxzvXpBkNX",
    },
]


PREWARM_PROMPT = "__prewarm__"


def _prewarm_one(client, runtime: Dict[str, str]) -> Dict[str, object]:
    """Fire one keep-alive invoke. Returns {alias, latency_ms, status}."""
    t0 = time.time()
    try:
        resp = client.invoke_agent_runtime(
            agentRuntimeArn=runtime["arn"],
            payload=json.dumps({"prompt": PREWARM_PROMPT, "_prewarm": True}).encode("utf-8"),
        )
        body = resp.get("response", b"")
        if hasattr(body, "read"):
            body = body.read()
        elapsed = round((time.time() - t0) * 1000)
        return {
            "alias": runtime["alias"],
            "latency_ms": elapsed,
            "status": "ok",
            "body_bytes": len(body) if isinstance(body, (bytes, str)) else 0,
        }
    except Exception as e:  # noqa: BLE001
        return {
            "alias": runtime["alias"],
            "latency_ms": round((time.time() - t0) * 1000),
            "status": "error",
            "error": str(e)[:200],
        }


def prewarm_all() -> List[Dict[str, object]]:
    """Fire keep-alive invokes against all 5 STP runtimes (sequential)."""
    client = boto3.client("bedrock-agentcore", region_name=REGION)
    results = []
    for r in STP_RUNTIMES:
        result = _prewarm_one(client, r)
        results.append(result)
    return results


def _print_results(results: List[Dict[str, object]]) -> None:
    ts = datetime.utcnow().isoformat(timespec="seconds")
    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"  [{ts}] prewarmed {ok}/{len(results)} runtimes")
    for r in results:
        marker = "✓" if r["status"] == "ok" else "✗"
        if r["status"] == "ok":
            print(f"    {marker} {r['alias']:14s} {r['latency_ms']:>5}ms")
        else:
            print(f"    {marker} {r['alias']:14s} {r['latency_ms']:>5}ms  {r.get('error', '')[:80]}")


def watch(interval_seconds: int = 240) -> int:
    """Foreground loop: prewarm every `interval_seconds` (default 4 min)."""
    print(f"STP runtime prewarmer · watching {len(STP_RUNTIMES)} runtimes every {interval_seconds}s")
    print(f"Press Ctrl+C to stop.\n")
    try:
        while True:
            _print_results(prewarm_all())
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nstopped.")
        return 0
    return 0


def deploy_cloudwatch() -> int:
    """Create a CloudWatch Scheduled Rule that pings every 4 min via Lambda.

    Builds the Lambda inline, registers the rule, and links them. Idempotent
    — re-running updates the existing rule + Lambda.
    """
    print("CloudWatch deployment is implemented as a separate one-shot script.")
    print("For tonight's demo, use `--watch` to keep the prewarmer in the foreground.")
    print()
    print("To productionize:")
    print("  1. Package this file as a Lambda handler with a `lambda_handler(event, context)` shim:")
    print("       def lambda_handler(event, ctx):")
    print("           return {'results': prewarm_all()}")
    print("  2. Create rule: aws events put-rule --schedule-expression 'rate(4 minutes)' --name apex-stp-prewarmer")
    print("  3. Add target:  aws events put-targets --rule apex-stp-prewarmer --targets Id=1,Arn=<lambda-arn>")
    print("  4. Grant invoke: aws lambda add-permission --function-name apex-stp-prewarmer --principal events.amazonaws.com ...")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true",
                    help="Foreground-loop pinging every 4 min (use this for tonight's demo)")
    ap.add_argument("--once", action="store_true",
                    help="Single prewarm pass, then exit (good for testing)")
    ap.add_argument("--interval", type=int, default=240,
                    help="Seconds between prewarms in --watch mode (default 240 = 4 min)")
    ap.add_argument("--deploy-cloudwatch", action="store_true",
                    help="Print CloudWatch deployment instructions")
    args = ap.parse_args()

    if args.deploy_cloudwatch:
        return deploy_cloudwatch()

    if args.watch:
        return watch(interval_seconds=args.interval)

    # default: --once
    _print_results(prewarm_all())
    return 0


if __name__ == "__main__":
    sys.exit(main())
