"""
List-endpoint helpers — dedupe and short-lived caching.

Why this exists
---------------
The playbook and blueprint tables accumulated duplicates: re-seeding an
industry mints a fresh row when the by-name lookup misses, so after many
re-seeds across many demo modes the playbooks table held 396 rows for 77
distinct playbooks. The gallery pages then paid to scan, validate and
serialize five copies of everything.

Rather than mutate anyone's data, the list endpoints collapse duplicates on
the way out and cache the result briefly. Two effects:

* the response carries one row per logical record, not five;
* a cold DynamoDB scan is paid once per TTL instead of on every page load.

The underlying rows are untouched — this is a read-path fix. Removing the
duplicates for real is a separate, deliberate cleanup.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Dict, Iterable, List, Optional

import structlog

log = structlog.get_logger()

# Every write path invalidates explicitly, so freshness does not depend on this
# expiring. It is only a backstop for changes made outside the API (a direct
# table edit, a seeder run elsewhere). Hence: long.
#
# A short TTL was actively harmful — pause for a minute mid-demo and the next
# page load paid the full ~5s scan again. Combined with stale-while-revalidate
# below, expiry is now never visible to a caller.
DEFAULT_TTL_SECONDS = 900.0  # 15 minutes


# ─────────────────────────────────────────────────────────────────────────────
# dedupe
# ─────────────────────────────────────────────────────────────────────────────

def dedupe_by(
    rows: Iterable[Dict[str, Any]],
    key: str,
    prefer: str = "updated_at",
) -> List[Dict[str, Any]]:
    """
    Collapse rows sharing the same `key`, keeping the freshest.

    "Freshest" is the greatest `prefer` timestamp; rows without one lose to
    rows with one, so a fully-populated record always beats a stub. Rows with
    no key at all are passed through untouched rather than silently merged —
    they're not duplicates, they're unidentifiable.
    """
    best: Dict[Any, Dict[str, Any]] = {}
    passthrough: List[Dict[str, Any]] = []
    order: List[Any] = []

    for row in rows:
        k = row.get(key)
        if not k:
            passthrough.append(row)
            continue

        current = best.get(k)
        if current is None:
            best[k] = row
            order.append(k)
            continue

        if str(row.get(prefer) or "") > str(current.get(prefer) or ""):
            best[k] = row

    return [best[k] for k in order] + passthrough


# ─────────────────────────────────────────────────────────────────────────────
# projection
# ─────────────────────────────────────────────────────────────────────────────

def project(rows: Iterable[Dict[str, Any]], keep: Iterable[str]) -> List[Dict[str, Any]]:
    """
    Reduce each row to `keep`, dropping absent fields rather than nulling them.

    Used to strip long prose (a playbook's `intent` and `recipe`, a blueprint's
    `schema_fields`) from list responses. Detail endpoints still return
    everything.
    """
    keep = set(keep)
    return [{k: v for k, v in row.items() if k in keep} for row in rows]


# ─────────────────────────────────────────────────────────────────────────────
# cache
# ─────────────────────────────────────────────────────────────────────────────

class TTLCache:
    """
    Tiny in-process cache with stale-while-revalidate.

    Safe for the single-worker API this runs behind. Deliberately not an LRU —
    the keyspace is a handful of filter combinations.

    The important property: **once a key has been populated, no caller ever
    waits on the backing scan again.** When an entry goes stale it is still
    returned immediately and refreshed in the background. Only the very first
    request for a key can block, and `warm()` exists so that request is the
    server's own at startup rather than a user's.
    """

    def __init__(self, ttl: float = DEFAULT_TTL_SECONDS) -> None:
        self.ttl = ttl
        self._lock = threading.Lock()
        self._store: Dict[str, tuple] = {}
        # Keys with a background refresh in flight, so a burst of requests
        # triggers one refresh rather than one per request.
        self._refreshing: set = set()

    # ── raw access ───────────────────────────────────────────────────────────
    def _peek(self, key: str) -> Optional[tuple]:
        with self._lock:
            return self._store.get(key)

    def get(self, key: str) -> Optional[Any]:
        """Fresh value only — returns None once the entry is stale."""
        hit = self._peek(key)
        if not hit:
            return None
        value, expires_at = hit
        return value if time.monotonic() <= expires_at else None

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = (value, time.monotonic() + self.ttl)

    def invalidate(self, key: Optional[str] = None) -> None:
        """Drop one key, or everything when key is None (after a write/seed)."""
        with self._lock:
            if key is None:
                self._store.clear()
            else:
                self._store.pop(key, None)

    # ── main entry point ─────────────────────────────────────────────────────
    async def get_or_set(self, key: str, producer: Callable[[], Any]) -> Any:
        """
        Return the cached value if present — fresh or stale.

        Stale values are returned immediately and refreshed in the background,
        so a lapsed TTL never shows up as latency. Only a cold key awaits the
        producer.
        """
        hit = self._peek(key)

        if hit is not None:
            value, expires_at = hit
            if time.monotonic() > expires_at:
                self._schedule_refresh(key, producer)
            return value

        value = await producer()
        self.set(key, value)
        return value

    def _schedule_refresh(self, key: str, producer: Callable[[], Any]) -> None:
        """Kick off one background refresh for a stale key."""
        import asyncio

        with self._lock:
            if key in self._refreshing:
                return
            self._refreshing.add(key)

        async def _refresh() -> None:
            try:
                self.set(key, await producer())
            except Exception as e:  # noqa: BLE001 — keep serving the stale value
                log.warning("list_cache.refresh_failed", key=key, error=str(e))
            finally:
                with self._lock:
                    self._refreshing.discard(key)

        try:
            asyncio.get_running_loop().create_task(_refresh())
        except RuntimeError:
            # No loop (e.g. called from sync context) — drop the marker so a
            # later request can retry rather than being wedged as "refreshing".
            with self._lock:
                self._refreshing.discard(key)

    # ── startup priming ──────────────────────────────────────────────────────
    async def warm(self, key: str, producer: Callable[[], Any], label: str = "") -> None:
        """
        Populate a key before anyone asks for it.

        Called during app startup so the first page load is served from cache
        instead of paying the cold scan. Failure is non-fatal: the key stays
        empty and the first real request populates it as before.
        """
        if self.get(key) is not None:
            return
        started = time.monotonic()
        try:
            self.set(key, await producer())
            log.info("list_cache.warmed", key=label or key,
                     seconds=round(time.monotonic() - started, 2))
        except Exception as e:  # noqa: BLE001 — never block startup
            log.warning("list_cache.warm_failed", key=label or key, error=str(e))
