"""
APEX · Verizon Far Edge — Path B Lambda trigger.

Fires on every PutObject to s3://apex-vz-cycles-.../cycles/*.xml and
POSTs the object key to the APEX backend's /telecommunications/cycle-start
endpoint, which then runs the same Full Certification Cycle pipeline
that the UI upload path uses.

Why we send only the S3 key (not the file body):
  - 5-50 KB ROBOT XMLs would still fit in a Lambda payload, but routing
    the bucket+key into the backend lets the orchestrator pull the file
    server-side. That decouples the backend from Lambda transport limits
    and keeps the trigger code simple.

Environment:
  APEX_BACKEND_URL      e.g. https://apex.cbts.com/api/v1 (or your ngrok URL)
  KEY_PREFIX_FILTER     drops with other prefixes are ignored

The function is intentionally tiny — under 60 lines of real logic — so
there's nothing to break on stage. All the actual pipeline lives in the
APEX backend.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List

log = logging.getLogger()
log.setLevel(logging.INFO)


def _records_from_event(event: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract (bucket, key) tuples from every S3 record in the event."""
    out: List[Dict[str, str]] = []
    for r in event.get("Records", []) or []:
        s3 = r.get("s3") or {}
        bucket = (s3.get("bucket") or {}).get("name")
        key    = (s3.get("object") or {}).get("key")
        if bucket and key:
            # S3 URL-encodes spaces and unicode in the key — decode for the API
            out.append({"bucket": bucket, "key": urllib.parse.unquote_plus(key)})
    return out


def _post_cycle_start(backend_url: str, bucket: str, key: str) -> Dict[str, Any]:
    """Fire-and-forget POST to /telecommunications/cycle-start with s3_key.

    Lambda's HTTP client doesn't natively stream SSE — and we don't need
    to wait for the stream to finish (the orchestrator runs to completion
    server-side regardless). We just need the cycle to KICK OFF, then
    Lambda exits. The APEX UI reads progress directly from the backend
    if someone happens to be watching the Run page.
    """
    # Encode as multipart/form-data with the s3_key form field. urllib's
    # MIME builder is verbose; build the body by hand.
    boundary = "----ApexLambdaBoundary7d2c"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="s3_key"\r\n\r\n'
        f"{key}\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    url = backend_url.rstrip("/") + "/telecommunications/cycle-start"
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type":   f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
            "X-Apex-Source":  "s3-lambda-trigger",
            "X-Apex-Bucket":  bucket,
        },
    )

    try:
        # Short read timeout — we just want to confirm the server accepted
        # the request and started streaming. Don't drain the full SSE body.
        with urllib.request.urlopen(req, timeout=8) as r:
            head = r.read(256).decode("utf-8", errors="ignore")
            return {"status": r.status, "preview": head[:120]}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": e.reason}
    except Exception as e:
        return {"status": None, "error": f"{type(e).__name__}: {e}"}


def handler(event: Dict[str, Any], _ctx: Any) -> Dict[str, Any]:
    """Lambda entrypoint.

    event['Records'][n].s3.{bucket.name, object.key} → cycle-start POST.
    Returns a per-record result dict for CloudWatch + caller inspection.
    """
    backend_url = (os.environ.get("APEX_BACKEND_URL") or "").strip()
    key_filter  = (os.environ.get("KEY_PREFIX_FILTER") or "").strip()

    # When the backend URL is a placeholder (typical for an architecture-only
    # demo deploy without a public APEX backend), the Lambda intentionally
    # exits clean without dispatching — this is a safety check that prevents
    # data exfil to an unverified endpoint. In production the URL is wired
    # to the customer's internal load balancer over VPC.
    is_demo_mode = (not backend_url) or ("example.invalid" in backend_url)

    records = _records_from_event(event)
    if not records:
        log.info("No S3 records in event — exiting cleanly.")
        return {"status": "noop", "reason": "no s3 records in event"}

    results: List[Dict[str, Any]] = []
    for rec in records:
        log.info("S3 event received: bucket=%s key=%s", rec["bucket"], rec["key"])

        # Defensive: even though the S3 event filter pins prefix+suffix,
        # check again in case the filter is loosened later.
        if key_filter and not rec["key"].startswith(key_filter):
            log.info("  → skipped (outside key filter %s)", key_filter)
            results.append({**rec, "status": "skipped", "reason": "outside key filter"})
            continue
        if not rec["key"].lower().endswith(".xml"):
            log.info("  → skipped (not .xml)")
            results.append({**rec, "status": "skipped", "reason": "not .xml"})
            continue

        # Demo mode (placeholder URL): exit cleanly without calling backend.
        # In production this branch never executes — the URL points at the
        # customer's internal load balancer.
        if is_demo_mode:
            log.info("  → APEX_BACKEND_URL is a placeholder — Lambda exiting cleanly (production VPC link not wired in this demo)")
            log.info("  → in production this would POST to the APEX backend over a private VPC endpoint")
            results.append({**rec, "status": "demo_mode_exit",
                             "reason": "placeholder backend URL"})
            continue

        # Real call path
        log.info("  → dispatching cycle to APEX backend: %s", backend_url)
        post_result = _post_cycle_start(backend_url, rec["bucket"], rec["key"])
        results.append({**rec, **post_result})

    return {
        "status":  "ok",
        "records": len(records),
        "results": results,
    }


if __name__ == "__main__":
    # Local invocation for quick iteration: mock a minimal S3 event.
    import sys
    fake_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": "apex-vz-cycles-457795063704"},
                "object": {"key": "cycles/robot_output_caas_node_v2412_full.xml"},
            }
        }]
    }
    print(json.dumps(handler(fake_event, None), indent=2))
