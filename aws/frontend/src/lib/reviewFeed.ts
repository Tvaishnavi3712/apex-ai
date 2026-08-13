/**
 * Cross-page event bus for the Human Review → Agent Hub hand-off.
 *
 * When a reviewer approves/rejects/escalates an item on /review, we push a
 * compact entry into localStorage under `apex:review-feed` and dispatch a
 * same-tab custom event. Agent Hub reads the feed on mount and subscribes to
 * new entries so the relevant agent sees a system message land in its chat
 * the moment the decision is made (same tab OR another tab — both work).
 *
 * Keep the payload small: Agent Hub decides how to render it.
 */

export type ReviewDecision = 'approved' | 'rejected' | 'escalated';

export interface ReviewFeedEntry {
  id: string;                // review item id, e.g. 'CBB-ORD-1047'
  title: string;             // human-readable title
  decision: ReviewDecision;
  agent_id: string;          // target agent in Agent Hub (e.g. 'customerops')
  playbook_id: string;       // so we can deep-link back
  decided_by: string;        // reviewer name
  decided_at: string;        // ISO string
  next_step: string;         // short "what runs next" label
  comment?: string;
}

const KEY = 'apex:review-feed';
const EVENT = 'apex:review-feed';
const MAX = 50;

function safeParse(raw: string | null): ReviewFeedEntry[] {
  if (!raw) return [];
  try {
    const v = JSON.parse(raw);
    return Array.isArray(v) ? v : [];
  } catch {
    return [];
  }
}

/** Read the full feed (most-recent first). Returns `[]` during SSR. */
export function readReviewFeed(): ReviewFeedEntry[] {
  if (typeof window === 'undefined') return [];
  try { return safeParse(window.localStorage.getItem(KEY)); }
  catch { return []; }
}

/** Append a new entry and broadcast it to same-tab listeners. */
export function pushReviewFeedEntry(entry: ReviewFeedEntry): void {
  if (typeof window === 'undefined') return;
  try {
    const current = readReviewFeed();
    // de-duplicate by (id, decision) — guards against double-clicks
    const filtered = current.filter(e => !(e.id === entry.id && e.decision === entry.decision));
    const next = [entry, ...filtered].slice(0, MAX);
    window.localStorage.setItem(KEY, JSON.stringify(next));
    // storage events don't fire in the tab that wrote them — use a CustomEvent too
    window.dispatchEvent(new CustomEvent<ReviewFeedEntry>(EVENT, { detail: entry }));
  } catch {
    // localStorage can be disabled (private browsing, quota, etc.) — swallow
  }
}

/**
 * Subscribe to new feed entries from any tab. Returns an unsubscribe function.
 * The callback fires once per new entry (never for the full feed).
 */
export function subscribeToReviewFeed(
  cb: (entry: ReviewFeedEntry) => void,
): () => void {
  if (typeof window === 'undefined') return () => {};

  const onStorage = (e: StorageEvent) => {
    if (e.key !== KEY || !e.newValue || e.newValue === e.oldValue) return;
    const parsed = safeParse(e.newValue);
    const prev   = safeParse(e.oldValue);
    // Latest entry is first; fire only if it's actually new
    const latest = parsed[0];
    if (!latest) return;
    if (prev[0] && prev[0].id === latest.id && prev[0].decision === latest.decision) return;
    cb(latest);
  };

  const onCustom = (e: Event) => {
    const detail = (e as CustomEvent<ReviewFeedEntry>).detail;
    if (detail) cb(detail);
  };

  window.addEventListener('storage', onStorage);
  window.addEventListener(EVENT, onCustom as EventListener);
  return () => {
    window.removeEventListener('storage', onStorage);
    window.removeEventListener(EVENT, onCustom as EventListener);
  };
}
