/**
 * Shared toast notification system for the CWFCU demo screens.
 *
 * useCwfcuToast() returns a `{ Toast, push, pushFromBackend }` triple:
 *   • <Toast /> renders the floating notification (call once per screen)
 *   • push({ tone, title, detail }) shows a manual toast
 *   • pushFromBackend(response) reads the canonical `{ ok, toast: {...} }`
 *     shape returned by every CWFCU mutation endpoint and shows it
 *
 * Tones: 'success' (green) · 'info' (blue) · 'warn' (amber) · 'error' (red)
 * Auto-dismiss after 4.5 seconds, but a sticky toast stays until clicked.
 */
import React, { useCallback, useEffect, useState } from 'react';

export type ToastTone = 'success' | 'info' | 'warn' | 'error';

export interface ToastPayload {
  tone: ToastTone;
  title: string;
  detail?: string;
  sticky?: boolean;
}

interface ToastEntry extends ToastPayload {
  id: number;
}

const toneStyle: Record<ToastTone, { bg: string; border: string; color: string; iconBg: string; icon: string }> = {
  success: { bg: '#f0fdf4', border: '#bbf7d0', color: '#166534', iconBg: '#dcfce7', icon: '✓' },
  info:    { bg: '#eff6ff', border: '#bfdbfe', color: '#1e40af', iconBg: '#dbeafe', icon: 'i' },
  warn:    { bg: '#fffbeb', border: '#fde68a', color: '#92400e', iconBg: '#fef3c7', icon: '!' },
  error:   { bg: '#fef2f2', border: '#fecaca', color: '#991b1b', iconBg: '#fee2e2', icon: '×' },
};

export function useCwfcuToast() {
  const [entries, setEntries] = useState<ToastEntry[]>([]);
  const [counter, setCounter] = useState(1);

  const push = useCallback((payload: ToastPayload) => {
    const id = counter;
    setCounter((c) => c + 1);
    setEntries((prev) => [...prev, { ...payload, id }]);
    if (!payload.sticky) {
      setTimeout(() => {
        setEntries((prev) => prev.filter((e) => e.id !== id));
      }, 4500);
    }
  }, [counter]);

  /** Read a backend mutation response `{ ok, toast: {...} }` and show it. */
  const pushFromBackend = useCallback((response: any) => {
    if (response?.toast) {
      const t = response.toast;
      const tone: ToastTone =
        t.tone === 'success' ? 'success'
      : t.tone === 'warn'    ? 'warn'
      : t.tone === 'error'   ? 'error'
      : 'info';
      push({ tone, title: t.title, detail: t.detail });
    } else if (response?.error) {
      push({ tone: 'error', title: 'Action failed', detail: String(response.error) });
    } else {
      push({ tone: 'success', title: 'Done' });
    }
  }, [push]);

  const dismiss = useCallback((id: number) => {
    setEntries((prev) => prev.filter((e) => e.id !== id));
  }, []);

  const Toast: React.FC = () => (
    <div
      style={{
        position: 'fixed', bottom: 24, right: 24, zIndex: 220,
        display: 'flex', flexDirection: 'column-reverse', gap: 10,
        pointerEvents: 'none',
      }}
    >
      {entries.map((e) => {
        const s = toneStyle[e.tone];
        return (
          <div
            key={e.id}
            onClick={() => dismiss(e.id)}
            style={{
              pointerEvents: 'auto',
              background: s.bg, border: `1px solid ${s.border}`,
              borderRadius: 10, padding: '14px 18px',
              boxShadow: '0 8px 24px rgba(0,0,0,.08)',
              minWidth: 280, maxWidth: 460, cursor: 'pointer',
              display: 'flex', gap: 12, alignItems: 'flex-start',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            <div style={{
              width: 24, height: 24, borderRadius: '50%', background: s.iconBg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 14, fontWeight: 700, color: s.color, flexShrink: 0,
            }}>
              {s.icon}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: s.color }}>{e.title}</div>
              {e.detail && (
                <div style={{ fontSize: 12, color: s.color, marginTop: 3, opacity: 0.86, lineHeight: 1.4 }}>
                  {e.detail}
                </div>
              )}
            </div>
            <div style={{ fontSize: 18, color: s.color, opacity: 0.5, fontWeight: 700, lineHeight: 1 }}>
              ×
            </div>
          </div>
        );
      })}
    </div>
  );

  return { Toast, push, pushFromBackend };
}

/** Convenience: POST to a CWFCU mutation endpoint and show the toast. */
export async function postCwfcuAction(
  url: string,
  push: (payload: ToastPayload) => void,
): Promise<any> {
  try {
    const r = await fetch(url, { method: 'POST' });
    const json = await r.json();
    if (json?.toast) {
      const tone: ToastTone =
        json.toast.tone === 'success' ? 'success'
      : json.toast.tone === 'warn'    ? 'warn'
      : json.toast.tone === 'error'   ? 'error'
      : 'info';
      push({ tone, title: json.toast.title, detail: json.toast.detail });
    } else if (!r.ok) {
      push({ tone: 'error', title: 'Action failed', detail: `HTTP ${r.status}` });
    }
    return json;
  } catch (e) {
    push({ tone: 'error', title: 'Action failed', detail: String(e) });
    return null;
  }
}
