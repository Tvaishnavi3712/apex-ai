#!/usr/bin/env python3
"""
JIRA status — quick health check before / during / after a demo.

Reports:
  · auth probe (200 = creds work, 401/403 = creds bad)
  · project exists + allowed issue types
  · ticket count by label
  · 5 most-recent APEX-generated tickets

Usage:
    python3 scripts/jira_status.py
    python3 scripts/jira_status.py --label live-probe
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    sys.stderr.write("httpx required.  pip install httpx\n"); sys.exit(1)


def _load_env(path: Path) -> None:
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", default="apex-auto-generated")
    parser.add_argument("--env",   default="backend/.env")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    _load_env(repo_root / args.env)

    url   = os.environ.get("JIRA_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_TOKEN", "")
    pkey  = os.environ.get("JIRA_PROJECT_KEY", "APEXVZ")
    if not (url and email and token):
        print("✗ JIRA creds missing in .env (URL / EMAIL / TOKEN)")
        return 2

    print(f"━━━ JIRA  status ━━━")
    print(f"  URL  : {url}")
    print(f"  Proj : {pkey}")
    print(f"  User : {email}")
    print()

    with httpx.Client(auth=(email, token), timeout=15.0,
                      headers={"Accept": "application/json"}) as c:
        # Auth
        r = c.get(f"{url}/rest/api/3/myself")
        if r.status_code == 200:
            j = r.json()
            print(f"  ✓ auth      {j.get('displayName')}  ({j.get('emailAddress')})")
        else:
            print(f"  ✗ auth      status={r.status_code}  body={r.text[:200]}")
            return 1

        # Project
        r = c.get(f"{url}/rest/api/3/project/{pkey}")
        if r.status_code == 200:
            j = r.json()
            types = [t["name"] for t in j.get("issueTypes", [])]
            print(f"  ✓ project   {j['name']!r}  id={j['id']}  types={types}")
        else:
            print(f"  ✗ project   status={r.status_code}  body={r.text[:200]}")
            return 1

        # Ticket count by label. The new /search/jql endpoint dropped the
        # `total` field — count via len(issues) and walk pages while !isLast.
        count = 0
        next_token = None
        while True:
            payload = {
                "jql":        f'project = {pkey} AND labels = "{args.label}"',
                "fields":     ["summary"],
                "maxResults": 100,
            }
            if next_token:
                payload["nextPageToken"] = next_token
            r = c.post(f"{url}/rest/api/3/search/jql", json=payload,
                       headers={"Content-Type": "application/json", "Accept": "application/json"})
            if r.status_code != 200:
                print(f"  ✗ search    status={r.status_code}  body={r.text[:200]}")
                break
            body = r.json()
            count += len(body.get("issues", []))
            if body.get("isLast", True) or not body.get("nextPageToken"):
                break
            next_token = body["nextPageToken"]
        print(f"  ✓ tickets   labelled '{args.label}': {count}")

        # 5 most recent
        r = c.post(
            f"{url}/rest/api/3/search/jql",
            json={
                "jql":        f'project = {pkey} AND labels = "{args.label}" ORDER BY created DESC',
                "fields":     ["summary", "status", "created"],
                "maxResults": 5,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if r.status_code == 200:
            issues = r.json().get("issues", [])
            if issues:
                print()
                print("  Recent:")
                for i in issues:
                    s = i["fields"]["summary"][:80]
                    st = i["fields"]["status"]["name"]
                    print(f"    {i['key']:<12}  {st:<8} {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
