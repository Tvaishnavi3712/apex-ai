/**
 * BolerHumanReview — HITL queue + approval surface for The Boler Company.
 *
 * Layout:
 *   • Left rail: REVIEW QUEUE — 7 exceptions + 1 CFO sign-off (stage 2 JE)
 *   • Center:    APPROVAL WINDOW for the currently selected item
 *                — full context, diff, evidence, signing chain
 *                — Approve / Override / Reject buttons wired to backend
 *   • Right rail: APPROVAL CHAIN (Sarah Mitchell → Ziggy Kravitz) + AUDIT
 *
 * Routing:
 *   /review                  → defaults to JE-2026-0031 (CFO sign-off — Stage 2)
 *   /review?item=EXC-2026-0441 → opens that specific exception
 *
 * All data from /api/v1/boler/dashboard-state.
 * Actions POST to /api/v1/boler/exceptions/{id}/* + /boler/je/{id}/distribute.
 */
import React, { useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useCwfcuToast, postCwfcuAction } from './cwfcuToast';
import { BOLER_DASHBOARD_FALLBACK } from './BolerDashboard';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

interface Exception {
  id: string; severity: string; title: string; description: string;
  employee?: string; employee_id?: string; agent: string; time: string;
  diff?: { before: string; after: string };
  amount_usd: number; status: string;
}

interface BolerState {
  cycle: string;
  exceptions: Array<Exception>;
  approval_queue: Array<{ stage: number; title: string; meta: string; status: string; status_color: string }>;
  je_preview: {
    division: string; period: string;
    lines: Array<{ side: string; account: string; description: string; amount_usd: number }>;
    balanced: boolean; total_usd: number;
  };
  audit_log: Array<{ time: string; date: string; action: string; detail: string; badge: string; badge_color: string }>;
}

const severityFill = (s: string) =>
  s === 'HIGH'     ? { bg: '#fef2f2', color: '#dc2626' }
: s === 'CRITICAL' ? { bg: '#fef2f2', color: '#dc2626' }
: s === 'MEDIUM'   ? { bg: '#fffbeb', color: '#d97706' }
: { bg: '#f0fdf4', color: '#16a34a' };

const fmtUsd = (n: number): string =>
  n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(2)}M`
: n >= 1_000     ? `$${(n / 1_000).toFixed(0)}K`
: `$${n.toLocaleString()}`;

const fmtUsdFull = (n: number): string => `$${n.toLocaleString()}`;

export function BolerHumanReview() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { Toast, push } = useCwfcuToast();
  const itemParam = (router.query.item as string | undefined) || undefined;

  const q = useQuery<BolerState>({
    queryKey: ['boler-dashboard-state'],
    queryFn: async () => {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 3000);
      try {
        const r = await fetch(`${API_BASE_URL}/boler/dashboard-state`, { signal: ctl.signal });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      } finally { clearTimeout(t); }
    },
    refetchInterval: 30_000,
    retry: 0,
    placeholderData: BOLER_DASHBOARD_FALLBACK as any,
  });

  const d: BolerState = (q.data as BolerState) ?? (BOLER_DASHBOARD_FALLBACK as any);

  // Build the unified queue: 7 exceptions + 1 JE awaiting CFO sign-off
  type QueueItem =
    | { kind: 'exception'; id: string; severity: string; title: string; amount: number; assignee: string; description: string; employee?: string; diff?: { before: string; after: string } }
    | { kind: 'je'; id: string; severity: string; title: string; amount: number; assignee: string; description: string };

  const queue: QueueItem[] = useMemo(() => {
    const items: QueueItem[] = d.exceptions.map((e) => ({
      kind: 'exception' as const,
      id: e.id,
      severity: e.severity,
      title: e.title,
      amount: e.amount_usd,
      assignee: e.status.includes('CFO') ? 'Ziggy Kravitz (CFO)'
              : e.status.includes('Benefits') ? 'Sarah Mitchell (Benefits Dir)'
              : 'APEX Auto',
      description: e.description,
      employee: e.employee,
      diff: e.diff,
    }));
    items.push({
      kind: 'je' as const,
      id: 'JE-2026-0031',
      severity: 'HIGH',
      title: `Stage 2 — Hendrickson Intl JE · ${fmtUsdFull(d.je_preview.total_usd)} · CFO sign-off`,
      amount: d.je_preview.total_usd,
      assignee: 'Ziggy Kravitz (CFO)',
      description: `Consolidated journal entry for ${d.je_preview.division} · ${d.je_preview.period}. Debits=Credits balanced. Sarah Mitchell signed stage 1 at 09:22 AM. Auto-distributes to division S3 inbox upon CFO sign-off.`,
    });
    return items;
  }, [d]);

  // Select item — from ?item= or default to JE-2026-0031 (the headline CFO ask)
  const [selectedId, setSelectedId] = useState<string>(itemParam || 'JE-2026-0031');
  const selected = queue.find((q) => q.id === selectedId) || queue[queue.length - 1];

  // ── action handlers ──
  const handleApply = (id: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/exceptions/${encodeURIComponent(id)}/apply-reclassification`, push)
      .then((r) => { if (r?.ok) queryClient.invalidateQueries({ queryKey: ['boler-dashboard-state'] }); });
  const handleOverride = (id: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/exceptions/${encodeURIComponent(id)}/override?note=demo-override`, push);
  const handleRemove = (id: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/exceptions/${encodeURIComponent(id)}/remove-allocation`, push)
      .then((r) => { if (r?.ok) queryClient.invalidateQueries({ queryKey: ['boler-dashboard-state'] }); });
  const handleDismiss = (id: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/exceptions/${encodeURIComponent(id)}/dismiss`, push)
      .then((r) => { if (r?.ok) queryClient.invalidateQueries({ queryKey: ['boler-dashboard-state'] }); });
  const handleDistributeJE = (id: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/je/${encodeURIComponent(id)}/distribute`, push)
      .then((r) => { if (r?.ok) queryClient.invalidateQueries({ queryKey: ['boler-dashboard-state'] }); });

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1120', padding: 24 }}>
      <Toast />

      {/* Page header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 24, fontWeight: 800, color: '#0d1120' }}>
          Human Review — Benefits Allocation HITL
        </div>
        <div style={{ fontSize: 13, color: '#7a8fa6', marginTop: 4 }}>
          {queue.length} items in queue · {d.cycle} cycle · Two-stage approval (Benefits → CFO) · SLA 24h
        </div>
      </div>

      {/* 3-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 320px', gap: 20 }}>

        {/* ── LEFT: Queue ── */}
        <div style={{
          background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12,
          padding: 18, height: 'fit-content',
        }}>
          <div style={{
            fontSize: 11, fontWeight: 700, color: '#6c47ff', letterSpacing: '.08em',
            textTransform: 'uppercase', marginBottom: 12,
          }}>
            Review Queue · {queue.length}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {queue.map((it) => {
              const sev = severityFill(it.severity);
              const isSel = it.id === selectedId;
              return (
                <button
                  key={it.id}
                  onClick={() => {
                    setSelectedId(it.id);
                    router.replace({ pathname: '/review', query: { item: it.id } }, undefined, { shallow: true });
                  }}
                  style={{
                    textAlign: 'left', cursor: 'pointer', padding: '10px 12px',
                    borderRadius: 8, border: '1px solid',
                    borderColor: isSel ? '#6c47ff' : '#e8ecf0',
                    background:  isSel ? '#f4f1ff' : '#fff',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{
                      fontSize: 9, fontWeight: 700, padding: '2px 6px', borderRadius: 3,
                      background: sev.bg, color: sev.color,
                    }}>{it.severity}</span>
                    <span style={{ fontSize: 11, color: '#7a8fa6' }}>{it.id}</span>
                  </div>
                  <div style={{ fontSize: 12.5, fontWeight: 600, color: '#0d1120', lineHeight: 1.35 }}>
                    {it.title}
                  </div>
                  <div style={{ fontSize: 11, color: '#7a8fa6', marginTop: 4 }}>
                    {fmtUsd(it.amount)} · {it.assignee}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Queue summary */}
          <div style={{
            marginTop: 18, paddingTop: 14, borderTop: '1px solid #f0f2f5',
            display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10,
          }}>
            <Stat label="HIGH" value={queue.filter((q) => q.severity === 'HIGH' || q.severity === 'CRITICAL').length} tone="#dc2626" />
            <Stat label="MEDIUM" value={queue.filter((q) => q.severity === 'MEDIUM').length} tone="#d97706" />
            <Stat label="With Sarah" value={queue.filter((q) => q.assignee.includes('Sarah')).length} tone="#6c47ff" />
            <Stat label="With Ziggy" value={queue.filter((q) => q.assignee.includes('Ziggy')).length} tone="#2563eb" />
          </div>
        </div>

        {/* ── CENTER: Approval Window ── */}
        <div style={{
          background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 24,
        }}>
          {selected.kind === 'je' ? (
            <ApprovalWindowJE item={selected} jePreview={d.je_preview}
                              onApprove={() => handleDistributeJE(selected.id)}
                              onOverride={() => handleOverride(selected.id)} />
          ) : (
            <ApprovalWindowException item={selected}
                                      onApply={() => handleApply(selected.id)}
                                      onOverride={() => handleOverride(selected.id)}
                                      onRemove={() => handleRemove(selected.id)}
                                      onDismiss={() => handleDismiss(selected.id)} />
          )}
        </div>

        {/* ── RIGHT: Approval Chain + Audit ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Approval Chain */}
          <div style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 18 }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: '#6c47ff', letterSpacing: '.08em',
              textTransform: 'uppercase', marginBottom: 12,
            }}>
              Approval Chain
            </div>
            {d.approval_queue.map((s) => (
              <div key={s.stage} style={{
                display: 'flex', alignItems: 'flex-start', gap: 10, padding: '8px 0',
                borderBottom: '1px solid #f5f7fa',
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: 8,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: s.status === 'COMPLETE' ? '#f0fdf4'
                            : s.status === 'REVIEW'   ? '#eff6ff'
                            : '#f5f7fa',
                  color: s.status_color, fontSize: 12, fontWeight: 700, flexShrink: 0,
                }}>
                  {s.status === 'COMPLETE' ? '✓' : s.stage}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 11.5, fontWeight: 600, color: '#0d1120', lineHeight: 1.3 }}>
                    {s.title}
                  </div>
                  <div style={{ fontSize: 10.5, color: '#7a8fa6', marginTop: 2, lineHeight: 1.4 }}>
                    {s.meta}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Audit Trail */}
          <div style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 18 }}>
            <div style={{
              fontSize: 11, fontWeight: 700, color: '#6c47ff', letterSpacing: '.08em',
              textTransform: 'uppercase', marginBottom: 12,
            }}>
              Recent Audit Events
            </div>
            {d.audit_log.slice(0, 5).map((a, i) => (
              <div key={i} style={{ padding: '8px 0', borderBottom: i < 4 ? '1px solid #f5f7fa' : 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                  <span style={{ fontSize: 10.5, fontWeight: 700, color: a.badge_color === 'red' ? '#dc2626'
                                                                : a.badge_color === 'green' ? '#16a34a'
                                                                : a.badge_color === 'amber' ? '#d97706'
                                                                : '#2563eb' }}>
                    {a.badge}
                  </span>
                  <span style={{ fontSize: 10, color: '#9ca3af' }}>{a.time}</span>
                </div>
                <div style={{ fontSize: 11.5, fontWeight: 600, color: '#0d1120', lineHeight: 1.3 }}>
                  {a.action}
                </div>
                <div style={{ fontSize: 10.5, color: '#7a8fa6', marginTop: 2, lineHeight: 1.4 }}>
                  {a.detail}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ───────────────────────── center panels ───────────────────────── */

function ApprovalWindowException({ item, onApply, onOverride, onRemove, onDismiss }: {
  item: any;
  onApply: () => Promise<any>;
  onOverride: () => Promise<any>;
  onRemove: () => Promise<any>;
  onDismiss: () => Promise<any>;
}) {
  const sev = severityFill(item.severity);
  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
        <span style={{
          fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 4,
          background: sev.bg, color: sev.color,
        }}>
          {item.severity}
        </span>
        <span style={{ fontSize: 13, fontWeight: 700, color: '#0d1120' }}>{item.id}</span>
        <span style={{ fontSize: 11.5, color: '#7a8fa6', marginLeft: 'auto' }}>
          Assigned: <strong style={{ color: '#0d1120' }}>{item.assignee}</strong>
        </span>
      </div>

      <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0d1120', margin: '4px 0 6px' }}>
        {item.title}
      </h2>
      {item.employee && (
        <div style={{ fontSize: 12, color: '#475569', marginBottom: 12 }}>
          Subject: <strong>{item.employee}</strong>
        </div>
      )}

      {/* Description */}
      <div style={{
        background: '#f8f9fc', border: '1px solid #e8ecf0', borderRadius: 8,
        padding: 14, marginBottom: 16, fontSize: 12.5, color: '#0d1120', lineHeight: 1.55,
      }}>
        {item.description}
      </div>

      {/* Diff block */}
      {item.diff && (
        <div style={{ marginBottom: 16 }}>
          <div style={{
            fontSize: 10.5, fontWeight: 700, color: '#6c47ff', letterSpacing: '.08em',
            textTransform: 'uppercase', marginBottom: 6,
          }}>
            Proposed Resolution
          </div>
          <div style={{
            background: '#0d1f35', borderRadius: 8, padding: 14,
            fontFamily: 'JetBrains Mono, ui-monospace, monospace', fontSize: 12, lineHeight: 1.7,
          }}>
            <div style={{ color: '#ef4444' }}>{item.diff.before}</div>
            <div style={{ color: '#22c55e' }}>{item.diff.after}</div>
          </div>
        </div>
      )}

      {/* Variance */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 18,
      }}>
        <KV label="$ Variance" value={fmtUsdFull(item.amount)} />
        <KV label="Agent" value="APEX Benefits" />
        <KV label="Cycle" value="June 2026" />
      </div>

      {/* Action buttons */}
      <div style={{
        paddingTop: 16, borderTop: '1px solid #e8ecf0',
        display: 'flex', gap: 10, flexWrap: 'wrap',
      }}>
        <ActionBtn label="✓ Approve & Apply" tone="primary" onClick={onApply} />
        <ActionBtn label="Override with Note" tone="warning" onClick={onOverride} />
        <ActionBtn label="Remove Allocation" tone="danger" onClick={onRemove} />
        <ActionBtn label="Dismiss" tone="neutral" onClick={onDismiss} />
      </div>

      <div style={{
        marginTop: 12, fontSize: 10.5, color: '#9ca3af', fontStyle: 'italic',
      }}>
        Decision will be hash-chained into Cosmos DB audit log · IAM role: BenefitsHITLApprover
      </div>
    </div>
  );
}

function ApprovalWindowJE({ item, jePreview, onApprove, onOverride }: {
  item: any;
  jePreview: BolerState['je_preview'];
  onApprove: () => Promise<any>;
  onOverride: () => Promise<any>;
}) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
        <span style={{
          fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 4,
          background: '#eff6ff', color: '#2563eb',
        }}>
          STAGE 2 · CFO
        </span>
        <span style={{ fontSize: 13, fontWeight: 700, color: '#0d1120' }}>{item.id}</span>
        <span style={{ fontSize: 11.5, color: '#7a8fa6', marginLeft: 'auto' }}>
          Awaiting: <strong style={{ color: '#0d1120' }}>{item.assignee}</strong>
        </span>
      </div>

      <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0d1120', margin: '4px 0 12px' }}>
        Consolidated JE · {jePreview.division} · {jePreview.period}
      </h2>

      <div style={{
        background: '#f8f9fc', border: '1px solid #e8ecf0', borderRadius: 8,
        padding: 14, marginBottom: 16, fontSize: 12.5, color: '#0d1120', lineHeight: 1.55,
      }}>
        {item.description}
      </div>

      {/* JE Lines */}
      <div style={{ marginBottom: 16 }}>
        <div style={{
          fontSize: 10.5, fontWeight: 700, color: '#6c47ff', letterSpacing: '.08em',
          textTransform: 'uppercase', marginBottom: 6,
        }}>
          Journal Entry Lines
        </div>
        <div style={{
          background: '#0d1f35', borderRadius: 8, padding: 14,
          fontFamily: 'JetBrains Mono, ui-monospace, monospace', fontSize: 11.5, lineHeight: 1.8,
        }}>
          {jePreview.lines.map((l, i) => (
            <div key={i} style={{ display: 'flex', color: l.side === 'DR' ? '#cbd5e1' : '#fcd34d' }}>
              <span style={{ width: 32, color: l.side === 'DR' ? '#22c55e' : '#fcd34d' }}>{l.side}</span>
              <span style={{ width: 80 }}>{l.account}</span>
              <span style={{ flex: 1 }}>{l.description}</span>
              <span style={{ width: 110, textAlign: 'right' }}>{fmtUsdFull(l.amount_usd)}</span>
            </div>
          ))}
          <div style={{ marginTop: 6, paddingTop: 6, borderTop: '1px solid #1e293b',
                        color: '#22c55e', display: 'flex' }}>
            <span style={{ flex: 1 }}>BALANCE CHECK</span>
            <span>{jePreview.balanced ? '✓ BALANCED · $0.00' : '✗ UNBALANCED'}</span>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 18,
      }}>
        <KV label="Total JE" value={fmtUsdFull(jePreview.total_usd)} />
        <KV label="Stage 1" value="Sarah Mitchell ✓" tone="#16a34a" />
        <KV label="Stage 2" value="Ziggy Kravitz ⧗" tone="#2563eb" />
      </div>

      <div style={{
        paddingTop: 16, borderTop: '1px solid #e8ecf0',
        display: 'flex', gap: 10, flexWrap: 'wrap',
      }}>
        <ActionBtn label="✓ Sign & Distribute to S3" tone="primary" onClick={onApprove} />
        <ActionBtn label="Hold — Request Revision" tone="warning" onClick={onOverride} />
      </div>

      <div style={{
        marginTop: 12, fontSize: 10.5, color: '#9ca3af', fontStyle: 'italic',
      }}>
        Sign-off triggers Azure Logic Apps distribution to 5 division S3 inboxes (KMS per-division keys) + SES notification to division controllers · ~18s end-to-end
      </div>
    </div>
  );
}

/* ───────────────────────── building blocks ───────────────────────── */

function Stat({ label, value, tone }: { label: string; value: number | string; tone: string }) {
  return (
    <div style={{ background: '#f8f9fc', borderRadius: 6, padding: '8px 10px' }}>
      <div style={{ fontSize: 9.5, fontWeight: 700, color: '#9ca3af', letterSpacing: '.08em', textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ fontSize: 16, fontWeight: 700, color: tone, marginTop: 2 }}>
        {value}
      </div>
    </div>
  );
}

function KV({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div style={{ background: '#f8f9fc', border: '1px solid #e8ecf0', borderRadius: 6, padding: '8px 12px' }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#9ca3af', letterSpacing: '.08em', textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: tone || '#0d1120', marginTop: 3 }}>
        {value}
      </div>
    </div>
  );
}

function ActionBtn({ label, tone, onClick }: {
  label: string; tone: 'primary' | 'warning' | 'danger' | 'neutral';
  onClick: () => Promise<any>;
}) {
  const palette: Record<string, { bg: string; color: string; border: string }> = {
    primary: { bg: '#6c47ff', color: '#fff',    border: '#6c47ff' },
    warning: { bg: '#fff7ed', color: '#ea580c', border: '#fed7aa' },
    danger:  { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
    neutral: { bg: '#f8f9fc', color: '#475569', border: '#e8ecf0' },
  };
  const p = palette[tone];
  const [busy, setBusy] = useState(false);
  return (
    <button
      onClick={async () => { setBusy(true); try { await onClick(); } finally { setBusy(false); } }}
      disabled={busy}
      style={{
        fontSize: 12.5, fontWeight: 600, padding: '9px 16px',
        borderRadius: 8, cursor: busy ? 'wait' : 'pointer',
        border: `1px solid ${p.border}`, background: p.bg, color: p.color,
        opacity: busy ? 0.6 : 1,
      }}
    >
      {busy ? '…' : label}
    </button>
  );
}
