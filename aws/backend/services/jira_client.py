"""
Atlassian JIRA Cloud REST API v3 client for Apex.

Used by:
  - actions.core.jira_create_ticket  (one ticket per failure)
  - actions.core.jira_create_epic    (bundle epic with sub-tasks)

Configuration (env, read at module import):
  JIRA_URL          e.g. https://myworkspace.atlassian.net
  JIRA_EMAIL        atlassian account email
  JIRA_TOKEN        atlassian API token (from id.atlassian.com)
  JIRA_PROJECT_KEY  e.g. APEXVZ  (default)
  JIRA_MOCK_MODE    when 'true' (or any required env var missing), returns
                    realistic mock responses instead of calling JIRA.

Why a hand-rolled client instead of `jira-python`:
  - We only need 2 endpoints (create_issue + link parent).
  - SDK adds 4 dependencies + 800 LOC for no benefit at this scale.
  - httpx is already in the dep tree.

Safety:
  - Token is read from env ONLY — never logged, never echoed in errors.
  - When the client fails, error messages redact the auth header.
  - Mock mode is the default until credentials are present — so the demo
    works the moment the page loads, with or without JIRA configured.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

log = logging.getLogger(__name__)


# ─────────────────────────── .env loader ───────────────────────────
# Pydantic-settings reads `.env` into the Settings object but does NOT
# pollute os.environ. The JiraConfig below reads os.environ directly so
# Settings → Save Changes can be re-read at runtime without redeploy.
# Bridge the two by loading the .env file into os.environ once, the first
# time this module is imported. Safe to call multiple times — won't
# overwrite values that already exist in os.environ.

def _ensure_env_loaded() -> None:
    """Load backend/.env into os.environ if not already populated."""
    if os.environ.get("_APEX_JIRA_ENV_LOADED") == "1":
        return
    try:
        from dotenv import load_dotenv
        # Walk up from this file to find backend/.env. This file lives at
        # backend/services/jira_client.py, so backend/.env is one level up.
        here = Path(__file__).resolve()
        env_path = here.parent.parent / ".env"
        if env_path.is_file():
            load_dotenv(dotenv_path=env_path, override=False)
            os.environ["_APEX_JIRA_ENV_LOADED"] = "1"
            log.debug("Loaded JIRA env from %s", env_path)
    except ImportError:
        # python-dotenv not installed — fall through and trust whatever
        # got into os.environ via shell/uvicorn startup.
        pass


_ensure_env_loaded()


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


# ─────────────────────────── config ───────────────────────────

class JiraConfig:
    """Immutable snapshot of JIRA-related env vars at instantiation time."""

    def __init__(self) -> None:
        self.url:         str  = _env("JIRA_URL").rstrip("/")
        self.email:       str  = _env("JIRA_EMAIL")
        self.token:       str  = _env("JIRA_TOKEN")
        self.project_key: str  = _env("JIRA_PROJECT_KEY", "APEXVZ")
        explicit_mock:    bool = _env("JIRA_MOCK_MODE", "false").lower() == "true"
        creds_missing:    bool = not (self.url and self.email and self.token)
        self.mock_mode:   bool = explicit_mock or creds_missing
        # Reason surfacing is useful for the Settings UI status pill.
        if explicit_mock:
            self.mock_reason = "JIRA_MOCK_MODE=true in .env"
        elif creds_missing:
            missing = [k for k, v in (("JIRA_URL", self.url),
                                       ("JIRA_EMAIL", self.email),
                                       ("JIRA_TOKEN", self.token)) if not v]
            self.mock_reason = f"Missing env: {', '.join(missing)}"
        else:
            self.mock_reason = ""

    def public(self) -> Dict[str, Any]:
        """Safe-to-render config — never includes the token."""
        return {
            "url":          self.url,
            "email":        self.email,
            "project_key":  self.project_key,
            "mock_mode":    self.mock_mode,
            "mock_reason":  self.mock_reason,
            "token_present": bool(self.token),
        }


# ─────────────────────────── client ───────────────────────────

class JiraClient:
    """Thin sync httpx client around JIRA Cloud REST v3.

    Construct ONE instance per request flow and close() when done. Or use
    the module-level get_client() helper which returns a singleton.
    """

    def __init__(self, config: Optional[JiraConfig] = None) -> None:
        self.config = config or JiraConfig()
        self._client = httpx.Client(
            auth=(self.config.email, self.config.token) if not self.config.mock_mode else None,
            timeout=20.0,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )

    # Context manager support
    def __enter__(self) -> "JiraClient": return self
    def __exit__(self, *a) -> None: self.close()
    def close(self) -> None: self._client.close()

    # ───── public methods ─────

    def create_issue(
        self,
        *,
        summary: str,
        description: str,
        issue_type: str = "Bug",
        labels: Optional[List[str]] = None,
        parent_epic_key: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a single JIRA issue. Returns
            {key, url, mock: bool, http_status: int|None, raw_error: str|None}
        """
        labels = list(labels or []) + ["apex-auto-generated"]

        if self.config.mock_mode:
            return self._mock_issue(summary, issue_type, labels, parent_epic_key)

        payload: Dict[str, Any] = {
            "fields": {
                "project":    {"key": self.config.project_key},
                "summary":    summary[:240],     # JIRA caps summary at 255 chars
                "description": self._to_adf(description),
                "issuetype":  {"name": issue_type},
                "labels":     [self._sanitize_label(l) for l in labels],
            }
        }
        if parent_epic_key:
            # JIRA Cloud "next-gen" projects expose parent on every issue type.
            payload["fields"]["parent"] = {"key": parent_epic_key}
        if extra_fields:
            payload["fields"].update(extra_fields)

        try:
            r = self._client.post(f"{self.config.url}/rest/api/3/issue", json=payload)
            if r.status_code >= 400:
                # Don't dump the auth header. Log status + redacted body.
                log.error(
                    "JIRA create_issue %s — status=%d body=%s",
                    summary[:60], r.status_code, r.text[:400],
                )
                return {
                    "key":         None,
                    "url":         None,
                    "mock":        False,
                    "http_status": r.status_code,
                    "raw_error":   r.text[:400],
                }
            j = r.json()
            return {
                "key":         j["key"],
                "url":         f"{self.config.url}/browse/{j['key']}",
                "mock":        False,
                "http_status": r.status_code,
                "raw_error":   None,
            }
        except httpx.RequestError as e:
            # Network-level failure (timeout, DNS, refused). Don't reveal token.
            log.error("JIRA create_issue network error: %s", type(e).__name__)
            return {
                "key":         None,
                "url":         None,
                "mock":        False,
                "http_status": None,
                "raw_error":   f"network: {type(e).__name__}",
            }

    def myself(self) -> Dict[str, Any]:
        """Validate creds. Returns {ok, account_id, email, mock} or
        {ok: False, error: ...}. Used by the Settings UI status pill."""
        if self.config.mock_mode:
            return {"ok": True, "mock": True, "reason": self.config.mock_reason}
        try:
            r = self._client.get(f"{self.config.url}/rest/api/3/myself")
            if r.status_code == 200:
                j = r.json()
                return {
                    "ok":         True,
                    "mock":       False,
                    "account_id": j.get("accountId"),
                    "email":      j.get("emailAddress"),
                    "display":    j.get("displayName"),
                }
            return {"ok": False, "mock": False, "http_status": r.status_code,
                    "error": r.text[:200]}
        except httpx.RequestError as e:
            return {"ok": False, "mock": False, "error": type(e).__name__}

    # ───── helpers ─────

    @staticmethod
    def _sanitize_label(label: str) -> str:
        """JIRA labels can't contain whitespace."""
        return label.strip().replace(" ", "-").lower()

    @staticmethod
    def _to_adf(text: str) -> Dict[str, Any]:
        """JIRA v3 REST requires description in Atlassian Document Format.
        Convert markdown-ish text to ADF — paragraphs separated by blank lines."""
        paragraphs = [p.strip() for p in (text or "").split("\n\n") if p.strip()]
        nodes = [
            {"type": "paragraph", "content": [{"type": "text", "text": p}]}
            for p in paragraphs
        ] or [{"type": "paragraph", "content": []}]
        return {"type": "doc", "version": 1, "content": nodes}

    def _mock_issue(
        self, summary: str, issue_type: str, labels: List[str],
        parent_epic_key: Optional[str],
    ) -> Dict[str, Any]:
        """Realistic mock response. Ticket key resembles the live JIRA format
        so the UI doesn't have to special-case mock URLs."""
        # Stable sequence based on summary so the same summary yields the
        # same key across runs (looks intentional, not random).
        seq = (abs(hash(summary)) % 9000) + 1000
        if issue_type.lower() == "epic":
            seq += 5000
        key = f"{self.config.project_key}-{seq}"
        host = self.config.url or "https://mock.atlassian.net"
        return {
            "key":         key,
            "url":         f"{host}/browse/{key}",
            "mock":        True,
            "http_status": None,
            "raw_error":   None,
            "_labels":     labels,
            "_parent":     parent_epic_key,
        }


# ─────────────────────────── module-level singleton ───────────────────────────

_singleton_lock = threading.Lock()
_singleton: Optional[JiraClient] = None


def get_client() -> JiraClient:
    """Cached client. Cheap to call repeatedly."""
    global _singleton
    if _singleton is None:
        with _singleton_lock:
            if _singleton is None:
                _singleton = JiraClient()
    return _singleton


def reset_client() -> None:
    """Force re-read of env vars next call (used by Settings → Save Changes)."""
    global _singleton
    with _singleton_lock:
        if _singleton is not None:
            try:
                _singleton.close()
            except Exception:
                pass
        _singleton = None
