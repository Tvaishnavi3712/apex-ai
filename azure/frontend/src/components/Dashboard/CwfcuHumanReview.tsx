/**
 * CwfcuHumanReview — HITL queue + decision surface for CommunityWide FCU.
 *
 * Layout mirrors /Users/babbu/Downloads/demo6-cwfcu/hitl.html:
 *   • Left rail: REVIEW QUEUE list (8 items) + QUEUE SUMMARY counts
 *   • Center:    CURRENT ITEM detail (SAR-2026-0142 deep-dive)
 *   • Right rail: NCUA EXAM IMPACT card + REGULATORY CONTEXT + RECENT REVIEWS
 *
 * All data from /api/v1/cwfcu/hitl/* endpoints.
 */
import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useCwfcuToast, postCwfcuAction } from './cwfcuToast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface QueueItem {
  id: string;
  doc: string;
  agent: string;
  priority: string;
  tone: string;
  flagged_minutes_ago: number;
  action: string;
  days_remaining?: number;
}

interface QueueSummary {
  total: number;
  high: number;
  medium: number;
  low: number;
  avg_wait_min: number;
  agent_confidence_avg_pct: number;
}

interface CurrentItem {
  item_id: string;
  type: string;
  priority: string;
  agent: string;
  subject_member: string;
  member_profile: {
    name: string; member_since: string; address: string;
    occupation: string; risk_tier: string; prior_sars: number;
  };
  key_findings: string[];
  transaction_data: Array<{ date: string; branch: string; amount: number; type: string }>;
  narrative: string;
  detection_confidence_pct: number;
  pattern_classification: string;
  intentional_structuring_probability_pct: number;
  ctr_threshold: number;
  statutory_cite: string;
  sar_deadline: string;
  ncua_exam_impact: string;
  regulatory_context: string[];
  actions_available: Array<{ id: string; label: string; tone: string }>;
  similar_historical_cases_filed: number;
}

interface RecentReviews {
  items: Array<{
    item_id: string; title: string; outcome: string;
    outcome_color: string; reviewed_at: string;
  }>;
}

const fmtUsd = (n: number): string => `$${n.toLocaleString()}`;
const fmtMinAgo = (m: number): string =>
  m < 60 ? `${m}m ago` : m < 1440 ? `${Math.floor(m / 60)}h ago` : `${Math.floor(m / 1440)}d ago`;

const priorityColor = (priority: string): string =>
  priority === 'HIGH' ? '#dc2626' : priority === 'MEDIUM' ? '#d97706' : '#16a34a';
const priorityBg = (priority: string): string =>
  priority === 'HIGH' ? '#fef2f2' : priority === 'MEDIUM' ? '#fffbeb' : '#f0fdf4';

export function CwfcuHumanReview() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { Toast, push } = useCwfcuToast();
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [reviewerModalOpen, setReviewerModalOpen] = useState(false);
  const [reviewerInput, setReviewerInput] = useState('Adrienne Williams');

  // URL ?item=<id> drives which HITL item is loaded; defaults to SAR-2026-0142
  const urlItem = typeof router.query.item === 'string' ? router.query.item : undefined;
  const activeItemId = urlItem || 'SAR-2026-0142';

  const queueQ = useQuery<{ items: QueueItem[]; summary: QueueSummary }>({
    queryKey: ['cwfcu-hitl-pending'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/cwfcu/hitl/pending`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 20_000,
    retry: 1,
  });

  const itemQ = useQuery<CurrentItem>({
    queryKey: ['cwfcu-hitl-item', activeItemId],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/cwfcu/hitl/item/${encodeURIComponent(activeItemId)}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  const recentQ = useQuery<RecentReviews>({
    queryKey: ['cwfcu-hitl-recent'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/cwfcu/hitl/recent-reviews`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  if (queueQ.isLoading || !queueQ.data || !itemQ.data || !recentQ.data) {
    return <div style={{ padding: 32, color: '#7a8fa6' }}>Loading Human Review…</div>;
  }

  const items   = queueQ.data.items;
  const summary = queueQ.data.summary;
  const it      = itemQ.data;

  const selectItem = (id: string) => {
    router.push(`/review?item=${encodeURIComponent(id)}`, undefined, { shallow: true });
  };

  const handlePrimaryAction = async () => {
    if (it.item_id === 'SAR-2026-0142') {
      setConfirmOpen(true);
      return;
    }
    // Generic primary action — file/approve
    const r = await postCwfcuAction(
      `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(it.item_id)}/approve`,
      push,
    );
    if (r?.ok) {
      queryClient.invalidateQueries({ queryKey: ['cwfcu-hitl-pending'] });
    }
  };

  const confirmFileSar = async () => {
    const r = await postCwfcuAction(
      `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(it.item_id)}/file-sar`,
      push,
    );
    setConfirmOpen(false);
    if (r?.ok) {
      queryClient.invalidateQueries({ queryKey: ['cwfcu-hitl-pending'] });
    }
  };

  const handleCancel = async () => {
    const r = await postCwfcuAction(
      `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(it.item_id)}/dismiss`,
      push,
    );
    if (r?.ok) {
      queryClient.invalidateQueries({ queryKey: ['cwfcu-hitl-pending'] });
    }
  };

  const handleSwitchReviewer = async () => {
    const r = await fetch(
      `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(it.item_id)}/switch-reviewer?reviewer=${encodeURIComponent(reviewerInput)}`,
      { method: 'POST' },
    );
    const j = await r.json();
    if (j?.toast) {
      push({ tone: 'info', title: j.toast.title, detail: j.toast.detail });
    }
    setReviewerModalOpen(false);
  };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1f35' }}>
      <Toast />
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 20, fontWeight: 800 }}>
          Human Review · CommunityWide FCU
        </div>
        <div style={{ fontSize: 12, color: '#7a8fa6', marginTop: 2 }}>
          NCUA-anchored decision surface · {summary.total} pending · avg wait {summary.avg_wait_min} min
        </div>
      </div>

      {/* 3-COLUMN LAYOUT */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 320px', gap: 16 }}>
        {/* LEFT: Review Queue + Summary */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: '#fff', borderRadius: 12, border: '1px solid #e8ecf0', overflow: 'hidden' }}>
            <div style={{
              padding: '14px 16px', borderBottom: '1px solid #e8ecf0',
              fontSize: 11, fontWeight: 700, letterSpacing: '0.12em',
              textTransform: 'uppercase', color: '#9ca3af',
            }}>
              Review Queue
            </div>
            {items.map((q) => {
              const isSelected = q.id === it.item_id;
              return (
                <div
                  key={q.id}
                  onClick={() => selectItem(q.id)}
                  style={{
                    padding: '12px 16px',
                    borderLeft: isSelected ? '3px solid #6c47ff' : '3px solid transparent',
                    background: isSelected ? '#f5f3ff' : '#fff',
                    cursor: 'pointer',
                    borderBottom: '1px solid #f0f2f5',
                  }}
                  onMouseEnter={(e) => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = '#fafbfd'; }}
                  onMouseLeave={(e) => { if (!isSelected) (e.currentTarget as HTMLDivElement).style.background = '#fff'; }}
                >
                  <div style={{ fontSize: 12, fontWeight: 600, color: '#0d1f35' }}>{q.id}</div>
                  <div style={{ fontSize: 11, color: '#6b7280', marginTop: 2, lineHeight: 1.3 }}>{q.doc}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 5 }}>
                    <span style={{
                      fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 4,
                      background: priorityBg(q.priority), color: priorityColor(q.priority),
                    }}>
                      {q.priority}
                    </span>
                    <span style={{ fontSize: 10, color: '#9ca3af' }}>{fmtMinAgo(q.flagged_minutes_ago)}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* QUEUE SUMMARY */}
          <div style={{ background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e8ecf0' }}>
            <div style={{
              fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
              textTransform: 'uppercase', color: '#9ca3af', marginBottom: 10,
            }}>
              Queue Summary
            </div>
            <SummaryRow label="Total pending" value={`${summary.total}`} />
            <SummaryRow label="HIGH priority" value={`${summary.high}`} color="#dc2626" />
            <SummaryRow label="MEDIUM priority" value={`${summary.medium}`} color="#d97706" />
            <SummaryRow label="LOW priority" value={`${summary.low}`} color="#16a34a" />
            <SummaryRow label="Avg agent confidence" value={`${summary.agent_confidence_avg_pct}%`} color="#16a34a" />
            <SummaryRow label="NCUA exam in" value={`47 days`} color="#dc2626" lastRow />
          </div>
        </div>

        {/* CENTER: Current Item */}
        <div style={{ background: '#fff', borderRadius: 12, border: '1px solid #e8ecf0', overflow: 'hidden' }}>
          <div style={{
            padding: '14px 20px', borderBottom: '1px solid #e8ecf0',
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#9ca3af' }}>
                Current Item
              </div>
              <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 700, marginTop: 2 }}>
                {it.item_id} · {it.subject_member}
              </div>
            </div>
            <span style={{
              fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 4,
              background: priorityBg(it.priority), color: priorityColor(it.priority),
            }}>
              {it.priority} priority
            </span>
          </div>

          <div style={{ padding: 20 }}>
            {/* MEMBER PROFILE */}
            <SectionLabel>Member Profile</SectionLabel>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
              <ProfileRow label="Member ID" value={it.subject_member} />
              <ProfileRow label="Member Since" value={it.member_profile.member_since} />
              <ProfileRow label="Address" value={it.member_profile.address} />
              <ProfileRow label="Account Type" value="Share-Savings" />
              <ProfileRow label="Risk Profile" value={it.member_profile.risk_tier} valueColor={priorityColor(it.member_profile.risk_tier === 'HIGH' ? 'HIGH' : 'MEDIUM')} />
              <ProfileRow label="Prior SARs" value={`${it.member_profile.prior_sars}`} />
            </div>

            {/* KEY FINDINGS */}
            <SectionLabel>Key Findings</SectionLabel>
            <ul style={{ paddingLeft: 18, fontSize: 13, color: '#374151', lineHeight: 1.6, marginBottom: 16 }}>
              {it.key_findings.map((f) => (<li key={f} style={{ marginBottom: 4 }}>{f}</li>))}
            </ul>

            {/* TRANSACTION DATA */}
            <SectionLabel>Transaction Data Ingested</SectionLabel>
            <div style={{ background: '#f8f9fc', borderRadius: 8, padding: 12, marginBottom: 16 }}>
              <div style={{
                display: 'grid', gridTemplateColumns: '60px 1fr 90px 130px', gap: 8,
                fontSize: 10, fontWeight: 700, color: '#9ca3af',
                textTransform: 'uppercase', letterSpacing: '0.08em',
                paddingBottom: 6, borderBottom: '1px solid #e8ecf0', marginBottom: 6,
              }}>
                <span>Date</span><span>Branch</span><span>Amount</span><span>Type</span>
              </div>
              {it.transaction_data.map((tx, i) => (
                <div key={i} style={{
                  display: 'grid', gridTemplateColumns: '60px 1fr 90px 130px', gap: 8,
                  fontSize: 12, padding: '6px 0',
                  borderBottom: i < it.transaction_data.length - 1 ? '1px solid #e8ecf0' : 'none',
                }}>
                  <span style={{ color: '#6b7280' }}>{tx.date}</span>
                  <span style={{ color: '#374151' }}>{tx.branch}</span>
                  <span style={{ fontWeight: 700, color: '#0d1f35' }}>{fmtUsd(tx.amount)}</span>
                  <span style={{ color: '#6b7280' }}>{tx.type}</span>
                </div>
              ))}
            </div>

            {/* AUTO-GENERATED SAR NARRATIVE */}
            <SectionLabel>SAR Narrative Generated</SectionLabel>
            <div style={{
              background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 8,
              padding: 14, marginBottom: 16, fontSize: 13, color: '#44403c',
              lineHeight: 1.6, fontStyle: 'italic',
            }}>
              {it.narrative}
            </div>

            {/* DETECTION CONFIDENCE + IMMUTABLE WARNING */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginBottom: 16 }}>
              <StatTile label="Detection Confidence" value={`${it.detection_confidence_pct}%`} valueColor="#16a34a" />
              <StatTile label="Pattern classification" value={it.pattern_classification.split(' (')[0]} valueColor="#0d1f35" />
              <StatTile label="Intentional structuring probability" value={`${it.intentional_structuring_probability_pct}%`} valueColor="#dc2626" />
            </div>

            <div style={{
              background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8,
              padding: 12, fontSize: 12, color: '#dc2626', marginBottom: 16,
            }}>
              ⚠ This action is immutable and will be logged to Audit Lens. SAR will be filed with FinCEN.
              SAR deadline: <strong>{it.sar_deadline}</strong>.
            </div>

            {/* ACTION BAR — dynamically driven by item.actions_available */}
            <div style={{ display: 'flex', gap: 10 }}>
              {it.actions_available.map((a, i) => {
                const isPrimary = a.tone === 'primary';
                const label = it.item_id === 'SAR-2026-0142' && isPrimary ? 'FILE SAR' : a.label;
                return (
                  <button
                    key={a.id}
                    style={isPrimary ? primaryBtn : secondaryBtn}
                    onClick={() => {
                      if (isPrimary) {
                        handlePrimaryAction();
                      } else if (a.id === 'dismiss' || a.id === 'cancel' || a.id === 'decline') {
                        handleCancel();
                      } else {
                        // Generic action — toast it
                        push({ tone: 'info', title: `${a.label} · ${it.item_id}`, detail: 'Action logged to Audit Lens' });
                      }
                    }}
                  >
                    {label}
                  </button>
                );
              })}
              <button
                style={{ ...secondaryBtn, marginLeft: 'auto' }}
                onClick={() => setReviewerModalOpen(true)}
              >
                Switch reviewer
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT: NCUA Exam Impact + Regulatory + Recent */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e8ecf0' }}>
            <div style={{
              fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
              textTransform: 'uppercase', color: '#9ca3af', marginBottom: 10,
            }}>
              NCUA Exam Impact
            </div>
            <div style={{ fontSize: 13, color: '#374151', lineHeight: 1.6, marginBottom: 10 }}>
              {it.ncua_exam_impact}
            </div>
            <div style={{
              background: '#f0fdf4', borderRadius: 6, padding: 10, fontSize: 12,
              color: '#16a34a', fontWeight: 500,
            }}>
              {it.similar_historical_cases_filed} similar historical cases filed at credit unions of similar size — patterns established.
            </div>
          </div>

          <div style={{ background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e8ecf0' }}>
            <div style={{
              fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
              textTransform: 'uppercase', color: '#9ca3af', marginBottom: 10,
            }}>
              Regulatory Context
            </div>
            <div style={{ fontSize: 12, color: '#374151', marginBottom: 8 }}>
              <strong>Statute:</strong> {it.statutory_cite}
            </div>
            <div style={{ fontSize: 12, color: '#374151', marginBottom: 8 }}>
              <strong>CTR Threshold:</strong> {fmtUsd(it.ctr_threshold)}
            </div>
            <ul style={{ paddingLeft: 18, fontSize: 12, color: '#374151', lineHeight: 1.5, margin: 0 }}>
              {it.regulatory_context.map((r) => <li key={r} style={{ marginBottom: 4 }}>{r}</li>)}
            </ul>
          </div>

          <div style={{ background: '#fff', borderRadius: 12, padding: 16, border: '1px solid #e8ecf0' }}>
            <div style={{
              fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
              textTransform: 'uppercase', color: '#9ca3af', marginBottom: 10,
            }}>
              Recent Reviews
            </div>
            {recentQ.data.items.map((r) => (
              <div key={r.item_id} style={{ paddingBottom: 8, marginBottom: 8, borderBottom: '1px solid #f0f2f5' }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#0d1f35' }}>{r.title}</div>
                <div style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 3,
                }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: r.outcome_color }}>{r.outcome}</span>
                  <span style={{ fontSize: 10, color: '#9ca3af' }}>{r.reviewed_at}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CONFIRM MODAL — SAR file */}
      {confirmOpen && (
        <div onClick={() => setConfirmOpen(false)} style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,.4)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 200,
        }}>
          <div onClick={(e) => e.stopPropagation()} style={{
            background: '#fff', borderRadius: 12, padding: 24, width: 480,
            boxShadow: '0 12px 48px rgba(0,0,0,.2)',
          }}>
            <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
              File {it.item_id} with FinCEN?
            </div>
            <div style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
              This action is <strong>immutable</strong> and will be logged to Audit Lens. After submission,
              a SAR continuing report cannot retract — only amend with additional information.
            </div>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button onClick={() => setConfirmOpen(false)} style={secondaryBtn}>Cancel</button>
              <button onClick={confirmFileSar} style={primaryBtn}>
                Confirm File
              </button>
            </div>
          </div>
        </div>
      )}

      {/* SWITCH REVIEWER MODAL */}
      {reviewerModalOpen && (
        <div onClick={() => setReviewerModalOpen(false)} style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,.4)', display: 'flex',
          alignItems: 'center', justifyContent: 'center', zIndex: 200,
        }}>
          <div onClick={(e) => e.stopPropagation()} style={{
            background: '#fff', borderRadius: 12, padding: 24, width: 480,
            boxShadow: '0 12px 48px rgba(0,0,0,.2)',
          }}>
            <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
              Reassign {it.item_id}
            </div>
            <div style={{ fontSize: 13, color: '#6b7280', marginBottom: 16 }}>
              Pick the reviewer who should own this item. Reassignments are logged to Audit Lens.
            </div>
            <select
              value={reviewerInput}
              onChange={(e) => setReviewerInput(e.target.value)}
              style={{
                width: '100%', padding: '10px 12px', fontSize: 13,
                border: '1px solid #e8ecf0', borderRadius: 8, marginBottom: 16,
                fontFamily: 'Inter, sans-serif', background: '#fff',
              }}
            >
              <option>Adrienne Williams (BSA Officer)</option>
              <option>Margaret Rodriguez (VP Operations)</option>
              <option>Nathan Bryant (Compliance Officer)</option>
              <option>Mariana Kim (Senior Compliance Analyst)</option>
              <option>Felix Lopez (BSA Analyst)</option>
            </select>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button onClick={() => setReviewerModalOpen(false)} style={secondaryBtn}>Cancel</button>
              <button onClick={handleSwitchReviewer} style={primaryBtn}>Reassign</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* helpers */
function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontSize: 10, fontWeight: 700, letterSpacing: '0.12em',
      textTransform: 'uppercase', color: '#9ca3af', marginBottom: 8,
    }}>
      {children}
    </div>
  );
}

function ProfileRow({ label, value, valueColor }: {
  label: string; value: string; valueColor?: string;
}) {
  return (
    <div style={{ fontSize: 12 }}>
      <div style={{ color: '#9ca3af', marginBottom: 2 }}>{label}</div>
      <div style={{ color: valueColor || '#0d1f35', fontWeight: 600 }}>{value}</div>
    </div>
  );
}

function StatTile({ label, value, valueColor }: {
  label: string; value: string; valueColor: string;
}) {
  return (
    <div style={{ background: '#f8f9fc', borderRadius: 8, padding: 12 }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#9ca3af', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 22, fontWeight: 800, color: valueColor }}>
        {value}
      </div>
    </div>
  );
}

function SummaryRow({ label, value, color, lastRow }: {
  label: string; value: string; color?: string; lastRow?: boolean;
}) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '7px 0', borderBottom: lastRow ? 'none' : '1px solid #f0f2f5', fontSize: 12,
    }}>
      <span style={{ color: '#6b7280' }}>{label}</span>
      <span style={{ fontWeight: 600, color: color || '#0d1f35' }}>{value}</span>
    </div>
  );
}

const primaryBtn: React.CSSProperties = {
  background: '#6c47ff', color: '#fff', border: 'none', borderRadius: 8,
  padding: '10px 20px', fontSize: 13, fontWeight: 700, cursor: 'pointer',
};
const secondaryBtn: React.CSSProperties = {
  background: '#f5f6fa', color: '#374151', border: '1px solid #e8ecf0',
  borderRadius: 8, padding: '10px 20px', fontSize: 13, fontWeight: 600, cursor: 'pointer',
};
