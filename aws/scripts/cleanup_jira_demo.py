#!/usr/bin/env python3
"""
Cleanup utility — delete every JIRA ticket created by the APEX
CertificationAgent demo (identified by the `apex-auto-generated` label).

Useful before a customer demo so the JIRA board starts at a clean state.
Idempotent — running on an empty project is a no-op.

Reads JIRA creds from backend/.env. Pass --dry-run to preview without
deleting. Pass --label foo to filter by a different label.

Usage:
    python3 scripts/cleanup_jira_demo.py             # delete all apex-auto-generated
    python3 scripts/cleanup_jira_demo.py --dry-run   # preview only
    python3 scripts/cleanup_jira_demo.py --label live-probe
    python3 scripts/cleanup_jira_demo.py --keep-epic # delete tickets but leave epics
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    sys.stderr.write("httpx required. Run:  pip install httpx\n")
    sys.exit(1)


def _load_env(path: Path) -> None:
    if not path.exists():
        sys.stderr.write(f"missing env file: {path}\n")
        sys.exit(1)
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Delete APEX-tagged JIRA tickets.")
    parser.add_argument("--label",     default="apex-auto-generated",
                        help="JQL label filter (default: apex-auto-generated)")
    parser.add_argument("--dry-run",   action="store_true",
                        help="List target tickets but don't delete")
    parser.add_argument("--keep-epic", action="store_true",
                        help="Skip Epic-type tickets — only delete child issues")
    parser.add_argument("--env",       default="backend/.env",
                        help="Path to .env (default: backend/.env)")
    parser.add_argument("--max",       type=int, default=200,
                        help="Max tickets per batch (default: 200)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    _load_env(repo_root / args.env)

    url   = os.environ.get("JIRA_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_TOKEN", "")
    if not (url and email and token):
        sys.stderr.write("JIRA_URL / JIRA_EMAIL / JIRA_TOKEN missing in .env\n")
        return 2

    auth = (email, token)
    headers = {"Accept": "application/json"}
    jql = f'labels = "{args.label}" ORDER BY created DESC'

    print(f"JIRA  : {url}")
    print(f"Label : {args.label}")
    print(f"Dry-run: {args.dry_run}")
    if args.keep_epic:
        print("Keep-epic: enabled (Epic-type tickets will NOT be deleted)")
    print()

    with httpx.Client(auth=auth, timeout=20.0, headers=headers) as c:
        # Find tickets. Atlassian deprecated /rest/api/3/search in early 2026 —
        # use /rest/api/3/search/jql (POST body) instead.
        r = c.post(
            f"{url}/rest/api/3/search/jql",
            json={
                "jql":          jql,
                "fields":       ["summary", "issuetype"],
                "maxResults":   args.max,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        if r.status_code != 200:
            sys.stderr.write(f"search failed: {r.status_code} {r.text[:200]}\n")
            return 1
        issues = r.json().get("issues", [])
        if not issues:
            print("No matching tickets — nothing to delete.")
            return 0

        print(f"Found {len(issues)} matching ticket(s):")
        to_delete = []
        for i in issues:
            t = i["fields"]["issuetype"]["name"]
            s = i["fields"]["summary"][:70]
            skip = args.keep_epic and t.lower() == "epic"
            tag = "[skip Epic]" if skip else "[delete]   "
            print(f"  {tag} {i['key']:<14} {t:8s} {s}")
            if not skip:
                to_delete.append(i["key"])

        if args.dry_run:
            print(f"\nDRY RUN — would delete {len(to_delete)} ticket(s).")
            return 0

        if not to_delete:
            print("\nNothing left to delete after filters.")
            return 0

        print(f"\nDeleting {len(to_delete)} ticket(s)...")
        deleted, errors = 0, 0
        for key in to_delete:
            d = c.delete(f"{url}/rest/api/3/issue/{key}",
                          params={"deleteSubtasks": "true"})
            if d.status_code in (204, 200):
                deleted += 1
                print(f"  ✓ {key}")
            else:
                errors += 1
                print(f"  ✗ {key}  status={d.status_code}  {d.text[:120]}")
            # Free-tier rate-limit safety
            time.sleep(0.08)

        print(f"\nDeleted {deleted}/{len(to_delete)} · errors {errors}")
        return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
