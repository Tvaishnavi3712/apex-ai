/**
 * Proactive alert banner — the demo's "killer moment".
 *
 * Mounts inside the Agent Hub. Starts polling /signals/stp/proactive-alert
 * every 10s right after mount. Backend returns 204 until session_age >=
 * reveal_offset_seconds (default 90), then returns the hero anomaly payload.
 * When the alert arrives, this component slides into view at the top of the
 * chat surface with a CRITICAL header and a CTA that fires the predictive
 * intent into the chat.
 *
 * Render strategy:
 *   • Only renders when demoMode is nuclear_operations / stp (otherwise null — no polling)
 *   • Self-contained polling — no parent state coupling
 *   • Dismissable via local state + backend POST so it never re-fires
 *   • Fully accessible: role="alert", aria-live="assertive", focus on mount
 *
 * UX:
 *   • Slides down from the top with a soft slate-blue → red gradient border
 *   • Pulsing red dot signals CRITICAL
 *   • Dismiss closes the banner; "Open Playbook →" fires onCta(query) so
 *     the Agent Hub can pre-fill the chat input with the predictive query
 */

import React, { useEffect, useState } from 'react';
import { useDemoMode } from '@/lib/demoMode';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface STPProactiveAlert {
  alert_id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM';
  equipment_id: string;
  title: string;
  body: string;
  detected_at: string;
  expected_failure_mode: string | null;
  days_until_impact: number;
  recommended_pm: string | null;
  estimated_avoidance_usd: number;
  audit_log_id: string;
  cta_label: string;
  cta_intent: string;
}

interface Props {
  /** Stable session id for this Agent Hub mount. Backend keys timing off this. */
  sessionId: string;
  /**
   * Override the default 90-second reveal offset. Use 0 for instant during
   * dry-runs, or 30 for shorter demos. Honored by the backend on every poll.
   */
  revealOffsetSeconds?: number;
  /**
   * Callback when user clicks the CTA — typically the Agent Hub pre-fills
   * the chat input with a predictive maintenance query for the cited asset.
   */
  onCta?: (suggestedQuery: string) => void;
}

const POLL_INTERVAL_MS = 10_000;

export function ProactiveAlertBanner({ sessionId, revealOffsetSeconds = 90, onCta }: Props) {
  const [demoMode] = useDemoMode();
  const [alert, setAlert] = useState<STPProactiveAlert | null>(null);
  const [dismissed, setDismissed] = useState(false);

  // Tell backend session has started (zeros the timer)
  useEffect(() => {
    if (demoMode !== 'nuclear_operations' && demoMode !== 'stp') return;
    const url = `${API_BASE_URL}/signals/stp/proactive-alert/start-session?session_id=${encodeURIComponent(sessionId)}`;
    fetch(url, { method: 'POST' }).catch(() => {/* best-effort */});
  }, [demoMode, sessionId]);

  // Poll the backend every 10s for the alert
  useEffect(() => {
    if (demoMode !== 'nuclear_operations' && demoMode !== 'stp') return;
    if (dismissed || alert) return;
    let cancelled = false;

    const poll = async () => {
      try {
        const url = `${API_BASE_URL}/signals/stp/proactive-alert?session_id=${encodeURIComponent(sessionId)}&reveal_offset_seconds=${revealOffsetSeconds}`;
        const r = await fetch(url);
        if (cancelled) return;
        if (r.status === 204) return;       // not ready yet, keep polling
        if (!r.ok) return;
        const data = (await r.json()) as STPProactiveAlert;
        if (!cancelled && data && data.alert_id) {
          setAlert(data);
        }
      } catch {
        // Network blip — next poll will retry
      }
    };

    // Fire one immediately + then on interval
    poll();
    const id = window.setInterval(poll, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, [demoMode, sessionId, revealOffsetSeconds, dismissed, alert]);

  const handleDismiss = () => {
    setDismissed(true);
    fetch(`${API_BASE_URL}/signals/stp/proactive-alert/dismiss?session_id=${encodeURIComponent(sessionId)}`, {
      method: 'POST',
    }).catch(() => {/* best-effort */});
  };

  const handleCta = () => {
    if (alert && onCta) {
      onCta(`Predict failure risk for ${alert.equipment_id} in next 30 days`);
    }
    handleDismiss();
  };

  if ((demoMode !== 'nuclear_operations' && demoMode !== 'stp') || !alert || dismissed) return null;

  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        position: 'relative',
        margin: '0 0 18px 0',
        borderRadius: 14,
        background: 'linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%)',
        border: '1.5px solid #dc2626',
        boxShadow: '0 8px 28px rgba(220, 38, 38, 0.18)',
        animation: 'apex-stp-banner-slide .35s cubic-bezier(.4, 0, .2, 1)',
        overflow: 'hidden',
      }}
    >
      {/* Top accent bar — slate-blue → red gradient */}
      <div
        aria-hidden
        style={{
          position: 'absolute', top: 0, left: 0, right: 0, height: 3,
          background: 'linear-gradient(90deg, #1e3a8a 0%, #dc2626 100%)',
        }}
      />
      <div style={{ padding: '18px 20px 16px', display: 'flex', gap: 14, alignItems: 'flex-start' }}>
        {/* Left — pulsing CRITICAL marker */}
        <div style={{ flexShrink: 0, paddingTop: 2 }}>
          <div
            style={{
              width: 40, height: 40, borderRadius: 12,
              background: '#dc2626',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#fff', fontWeight: 800, fontSize: 18,
              boxShadow: '0 0 0 4px rgba(220,38,38,0.18)',
              animation: 'apex-stp-banner-pulse 1.6s infinite ease-in-out',
            }}
          >
            !
          </div>
        </div>

        {/* Middle — content */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
            <span
              style={{
                fontSize: 10, fontWeight: 800, letterSpacing: '.1em', textTransform: 'uppercase',
                padding: '3px 8px', borderRadius: 4,
                background: '#dc2626', color: '#fff',
              }}
            >
              {alert.severity}
            </span>
            <span
              style={{
                fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase',
                padding: '3px 8px', borderRadius: 4,
                background: '#1e3a8a', color: '#fff',
              }}
            >
              ReliabilityAgent · proactive
            </span>
            <span style={{ fontSize: 11, color: '#94a3b8', fontWeight: 500 }}>
              {alert.equipment_id} · detected {fmtDetected(alert.detected_at)}
            </span>
          </div>
          <div style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55, marginBottom: 12 }}>
            {alert.body}
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button
              onClick={handleCta}
              className="btn btn-primary btn-sm"
              autoFocus
            >
              {alert.cta_label}
            </button>
            <button
              onClick={handleDismiss}
              className="btn btn-secondary btn-sm"
            >
              Dismiss
            </button>
            {alert.recommended_pm && (
              <span style={{
                fontSize: 11, color: '#475569', fontWeight: 500,
                padding: '7px 12px', borderRadius: 8,
                background: '#fff', border: '1px solid #e2e8f0',
              }}>
                Recommend PM: <span className="mono" style={{ color: '#0f172a' }}>{alert.recommended_pm}</span>
              </span>
            )}
            <span style={{
              fontSize: 11, color: '#16a34a', fontWeight: 700,
              padding: '7px 12px', borderRadius: 8,
              background: '#fff', border: '1px solid #bbf7d0',
            }}>
              ${alert.estimated_avoidance_usd.toLocaleString()} avoidance
            </span>
          </div>
        </div>

        {/* Right — close button */}
        <button
          onClick={handleDismiss}
          aria-label="Dismiss alert"
          style={{
            flexShrink: 0, padding: 6, background: 'transparent',
            border: 'none', cursor: 'pointer', color: '#94a3b8',
            borderRadius: 8,
          }}
          onMouseOver={(e) => (e.currentTarget.style.background = '#f1f5f9')}
          onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
        >
          <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Footer with audit-log id (compliance reassurance) */}
      <div style={{
        padding: '8px 20px', borderTop: '1px solid #fecaca',
        background: 'rgba(255, 255, 255, .55)',
        fontSize: 10, color: '#94a3b8', display: 'flex', justifyContent: 'space-between', gap: 8, flexWrap: 'wrap',
      }}>
        <span>Decision logged to <span className="mono">apex.audit_log</span>: {alert.audit_log_id}</span>
        <span>Session-bound · alert fires once per chat session</span>
      </div>

      {/* Animations */}
      <style>{`
        @keyframes apex-stp-banner-slide {
          from { transform: translateY(-12px); opacity: 0; }
          to   { transform: translateY(0); opacity: 1; }
        }
        @keyframes apex-stp-banner-pulse {
          0%, 100% { box-shadow: 0 0 0 4px rgba(220,38,38,0.18); }
          50%      { box-shadow: 0 0 0 8px rgba(220,38,38,0.10); }
        }
      `}</style>
    </div>
  );
}

function fmtDetected(iso: string): string {
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    const mins = Math.round((Date.now() - d.getTime()) / 60_000);
    if (mins < 60) return `${mins} min ago`;
    if (mins < 60 * 24) return `${Math.round(mins / 60)} hr ago`;
    return d.toLocaleString();
  } catch {
    return iso;
  }
}
