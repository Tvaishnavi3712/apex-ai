/**
 * CwfcuCommandCenter — real-time ops view for CommunityWide FCU.
 *
 * Layout mirrors /Users/babbu/Downloads/demo6-cwfcu/command-center.html:
 *   • 4 KPI cards
 *   • Top row: SAR Intelligence Viewer + Live Agent Activity Feed
 *   • Bottom row: Active Loan Pipeline + Agent Accuracy + NCUA Exam Countdown
 *
 * All data sourced from /api/v1/cwfcu/dashboard-state per CLAUDE.md.
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useCwfcuToast, postCwfcuAction } from './cwfcuToast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface DashboardState {
  kpis: {
    docs_processed_today: number;
    docs_today_delta_pct: number;
    hitl_queue_pending: number;
    hitl_avg_wait_min: number;
    sars_auto_drafted_today: number;
    sars_pending_review: number;
    loan_packets_cleared_today: number;
  };
  sar_viewer: Array<{
    sar_id: string;
    subject_member: string;
    summary: string;
    amount_usd: number;
    narrative: string | null;
    description: string;
    actions: string[];
    priority: string;
  }>;
  processing_feed: Array<{
    time: string; agent: string; color: string; message: string;
    tag: string; tag_tone: string;
  }>;
  loan_pipeline: Array<{
    member: string; type: string; amount_usd: number;
    progress_pct: number; progress_color: string; progress_label: string;
    status: string; status_color: string;
  }>;
  agent_accuracy: Array<{ name: string; accuracy_pct: number; color: string }>;
  exam_readiness: {
    overall_pct: number; target_pct: number; days_to_exam: number;
    trajectory_msg: string;
  };
}

const fmtUsd = (n: number): string => `$${n.toLocaleString()}`;

const tagTone = (tone: string): { bg: string; color: string } => ({
  bg:
    tone === 'red'   ? 'rgba(239,68,68,0.1)'
  : tone === 'amber' ? 'rgba(245,158,11,0.1)'
  : tone === 'green' ? 'rgba(22,163,74,0.1)'
  : tone === 'teal'  ? 'rgba(0,196,160,0.1)'
  : 'rgba(108,71,255,0.1)',
  color:
    tone === 'red'   ? '#ef4444'
  : tone === 'amber' ? '#d97706'
  : tone === 'green' ? '#16a34a'
  : tone === 'teal'  ? '#00c4a0'
  : '#6c47ff',
});

export function CwfcuCommandCenter() {
  const router = useRouter();
  const { Toast, push } = useCwfcuToast();
  const [editOpen, setEditOpen] = useState<string | null>(null);
  const [editText, setEditText] = useState('');

  const q = useQuery<DashboardState>({
    queryKey: ['cwfcu-dashboard-state'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/cwfcu/dashboard-state`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 15_000,
    retry: 1,
  });

  if (q.isLoading || !q.data) {
    return <div style={{ padding: 32, color: '#7a8fa6' }}>Loading Command Center…</div>;
  }
  if (q.isError) {
    return <div style={{ padding: 32, color: '#dc2626' }}>Failed to load Command Center.</div>;
  }
  const d = q.data;

  const handleApprove = (sarId: string) =>
    postCwfcuAction(`${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(sarId)}/file-sar`, push);

  const handleDismiss = (sarId: string) =>
    postCwfcuAction(`${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(sarId)}/dismiss`, push);

  const handleEditOpen = (sarId: string, currentNarrative?: string) => {
    setEditOpen(sarId);
    setEditText(currentNarrative || '');
  };

  const handleEditSave = async () => {
    if (!editOpen) return;
    const r = await fetch(
      `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(editOpen)}/edit-narrative?narrative=${encodeURIComponent(editText)}`,
      { method: 'POST' },
    );
    const j = await r.json();
    if (j?.toast) {
      push({ tone: j.toast.tone === 'info' ? 'info' : 'success', title: j.toast.title, detail: j.toast.detail });
    }
    setEditOpen(null);
  };

  const handleOpenReview = (sarId: string) => {
    router.push(`/review?item=${encodeURIComponent(sarId)}`);
  };

  const handleLoanClick = (member: string) => {
    push({ tone: 'info', title: `Opening packet for ${member}`, detail: 'Routing to Loan Document Agent in Agent Hub…' });
    setTimeout(() => router.push(`/agent-hub?agent=cwfcu-loan-agent`), 600);
  };

  const handleFeedClick = (agent: string) => {
    const agentMap: Record<string, string> = {
      Compliance:  'cwfcu-compliance-agent',
      'Loan Doc':  'cwfcu-loan-agent',
      Onboarding:  'cwfcu-onboarding-agent',
      Vendor:      'cwfcu-vendor-agent',
      Policy:      'cwfcu-policy-agent',
    };
    const aid = agentMap[agent] || 'cwfcu-compliance-agent';
    router.push(`/agent-hub?agent=${aid}`);
  };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1f35' }}>
      <Toast />

      {/* KPI STRIP — every card is clickable */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <Kpi label="Docs Processed Today" value={`${d.kpis.docs_processed_today}`} delta={`↑ ${d.kpis.docs_today_delta_pct}% vs. yesterday`} deltaColor="#16a34a"
             onClick={() => router.push('/agent-hub?agent=cwfcu-compliance-agent')} />
        <Kpi label="HITL Queue" value={`${d.kpis.hitl_queue_pending}`} valueColor="#f59e0b" sub={`Avg. wait: ${d.kpis.hitl_avg_wait_min} min`}
             onClick={() => router.push('/review')} />
        <Kpi label="SARs Auto-Drafted" value={`${d.kpis.sars_auto_drafted_today}`} valueColor="#6c47ff" sub={`Today · ${d.kpis.sars_pending_review} pending review`}
             onClick={() => router.push('/review')} />
        <Kpi label="Loan Packets Cleared" value={`${d.kpis.loan_packets_cleared_today}`} valueColor="#00c4a0" sub="Avg. 1.4 days to decision"
             onClick={() => router.push('/agent-hub?agent=cwfcu-loan-agent')} />
      </div>

      {/* TOP ROW */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <SarViewer
          sars={d.sar_viewer}
          onApprove={handleApprove}
          onEdit={handleEditOpen}
          onDismiss={handleDismiss}
          onOpenReview={handleOpenReview}
        />
        <ActivityFeed feed={d.processing_feed} onFeedClick={handleFeedClick} />
      </div>

      {/* BOTTOM ROW */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 16 }}>
        <LoanPipelinePanel
          pipeline={d.loan_pipeline}
          clearedToday={d.kpis.loan_packets_cleared_today}
          onLoanClick={handleLoanClick}
        />
        <AgentAccuracyPanel agents={d.agent_accuracy} onAgentClick={(name) => {
          const m: Record<string, string> = {
            'Compliance Agent': 'cwfcu-compliance-agent',
            'Loan Document Agent': 'cwfcu-loan-agent',
            'Member Onboarding Agent': 'cwfcu-onboarding-agent',
            'Vendor & Contract Agent': 'cwfcu-vendor-agent',
            'Policy & HR Agent': 'cwfcu-policy-agent',
          };
          const aid = m[name] || 'cwfcu-compliance-agent';
          router.push(`/agent-hub?agent=${aid}`);
        }} />
        <ExamCountdownPanel exam={d.exam_readiness} onClick={() => router.push('/apex-signal')} />
      </div>

      {/* Edit narrative modal */}
      {editOpen && (
        <div onClick={() => setEditOpen(null)} style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,.5)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', zIndex: 200,
        }}>
          <div onClick={(e) => e.stopPropagation()} style={{
            background: '#fff', borderRadius: 12, padding: 24, width: 640,
            maxHeight: '80vh', boxShadow: '0 12px 48px rgba(0,0,0,.2)',
            display: 'flex', flexDirection: 'column',
          }}>
            <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
              Edit SAR Narrative · {editOpen}
            </div>
            <div style={{ fontSize: 12, color: '#6b7280', marginBottom: 12 }}>
              Edits stay in draft state. BSA Officer still owns the final file decision.
            </div>
            <textarea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              style={{
                flex: 1, minHeight: 220, padding: 12, fontSize: 13,
                border: '1px solid #e8ecf0', borderRadius: 8, fontFamily: 'Inter, sans-serif',
                resize: 'vertical', marginBottom: 16, lineHeight: 1.5,
              }}
            />
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button onClick={() => setEditOpen(null)} style={btnSecondary}>Cancel</button>
              <button onClick={handleEditSave} style={btnPrimaryDark}>Save draft</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

const btnPrimaryDark: React.CSSProperties = {
  background: '#6c47ff', color: '#fff', border: 'none', borderRadius: 8,
  padding: '8px 16px', fontSize: 12, fontWeight: 700, cursor: 'pointer',
};

/* ──────────────────────── KPI ──────────────────────── */
function Kpi({ label, value, valueColor, delta, deltaColor, sub, onClick }: {
  label: string; value: string; valueColor?: string;
  delta?: string; deltaColor?: string; sub?: string;
  onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        background: '#fff', borderRadius: 12, padding: '20px 22px',
        border: '1px solid #e8ecf0',
        cursor: onClick ? 'pointer' : 'default', transition: 'box-shadow .15s',
      }}
      onMouseEnter={(e) => { if (onClick) (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 14px rgba(108,71,255,0.08)'; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.boxShadow = 'none'; }}
    >
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#7a8fa6', marginBottom: 8 }}>
        {label}
      </div>
      <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 32, fontWeight: 800, color: valueColor || '#0d1f35', lineHeight: 1 }}>
        {value}
      </div>
      {delta && <div style={{ fontSize: 12, marginTop: 6, color: deltaColor || '#16a34a' }}>{delta}</div>}
      {sub && <div style={{ fontSize: 12, color: '#7a8fa6', marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

/* ──────────────────────── SAR Intelligence Viewer ──────────────────────── */
function SarViewer({ sars, onApprove, onEdit, onDismiss, onOpenReview }: {
  sars: DashboardState['sar_viewer'];
  onApprove:     (sarId: string) => void;
  onEdit:        (sarId: string, narrative?: string) => void;
  onDismiss:     (sarId: string) => void;
  onOpenReview:  (sarId: string) => void;
}) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0' }}>
      <div style={{
        fontSize: 13, fontWeight: 700, color: '#0d1f35', marginBottom: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        SAR Intelligence Viewer — Compliance Agent
        <span style={{ fontSize: 11, fontWeight: 600, background: '#fffbeb', color: '#d97706', padding: '2px 8px', borderRadius: 4 }}>
          {sars.filter((s) => !!s.narrative || s.actions.includes('open_for_review')).length} Pending Review
        </span>
      </div>

      {sars.map((s, i) => {
        const isPrimary = i === 0;
        return (
          <div key={s.sar_id} style={{
            border: isPrimary ? '1px solid #fde68a' : '1px solid #e8ecf0',
            borderRadius: 10,
            padding: 14,
            marginBottom: i < sars.length - 1 ? 10 : 0,
            background: isPrimary ? '#fffbeb' : '#f8fafc',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
              <div>
                <div style={{
                  fontSize: 11, fontWeight: 700, color: isPrimary ? '#92400e' : '#374151',
                  fontFamily: 'Space Grotesk, sans-serif',
                }}>
                  {s.sar_id} · Member {s.subject_member}
                </div>
                <div style={{ fontSize: 11, color: isPrimary ? '#78716c' : '#9ca3af', marginTop: 1 }}>
                  {s.summary}
                </div>
              </div>
              <div style={{
                fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 800,
                color: isPrimary ? '#d97706' : '#6b7280',
              }}>
                {fmtUsd(s.amount_usd)}
              </div>
            </div>
            <div style={{
              fontSize: 12, color: isPrimary ? '#57534e' : '#6b7280',
              lineHeight: 1.5, marginBottom: 10,
            }}>
              {s.description}
            </div>
            {s.narrative && (
              <>
                <div style={{
                  fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', color: '#92400e',
                  textTransform: 'uppercase', marginBottom: 6,
                }}>
                  Auto-Generated SAR Narrative
                </div>
                <div style={{
                  fontSize: 11, color: '#44403c', background: '#fff', border: '1px solid #e7e5e4',
                  borderRadius: 6, padding: 10, lineHeight: 1.6, fontStyle: 'italic', marginBottom: 10,
                }}>
                  {s.narrative}
                </div>
              </>
            )}
            <div style={{ display: 'flex', gap: 8 }}>
              {s.actions.map((a) => {
                if (a === 'approve_and_file') {
                  return <button key={a} style={btnPrimary}
                    onClick={() => onApprove(s.sar_id)}>✓ Approve &amp; File</button>;
                }
                if (a === 'edit_narrative') {
                  return <button key={a} style={btnSecondary}
                    onClick={() => onEdit(s.sar_id, s.narrative || '')}>✎ Edit Narrative</button>;
                }
                if (a === 'dismiss') {
                  return <button key={a} style={btnDanger}
                    onClick={() => onDismiss(s.sar_id)}>✗ Dismiss</button>;
                }
                if (a === 'open_for_review') {
                  return <button key={a} style={btnDark}
                    onClick={() => onOpenReview(s.sar_id)}>Open for Review</button>;
                }
                return null;
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

const btnPrimary: React.CSSProperties = {
  background: '#16a34a', color: '#fff', border: 'none', borderRadius: 6,
  padding: '6px 12px', fontSize: 11, fontWeight: 700, cursor: 'pointer',
};
const btnSecondary: React.CSSProperties = {
  background: '#f5f6fa', color: '#374151', border: '1px solid #e8ecf0', borderRadius: 6,
  padding: '6px 12px', fontSize: 11, fontWeight: 600, cursor: 'pointer',
};
const btnDanger: React.CSSProperties = {
  background: '#fef2f2', color: '#ef4444', border: '1px solid #fecaca', borderRadius: 6,
  padding: '6px 12px', fontSize: 11, fontWeight: 600, cursor: 'pointer',
};
const btnDark: React.CSSProperties = {
  background: '#0d1f35', color: '#00c4a0', border: 'none', borderRadius: 6,
  padding: '6px 14px', fontSize: 11, fontWeight: 700, cursor: 'pointer',
};

/* ──────────────────────── Live Activity Feed ──────────────────────── */
function ActivityFeed({ feed, onFeedClick }: {
  feed: DashboardState['processing_feed'];
  onFeedClick: (agent: string) => void;
}) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0' }}>
      <div style={{
        fontSize: 13, fontWeight: 700, color: '#0d1f35', marginBottom: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        Live Agent Activity Feed
        <span style={{ fontSize: 11, fontWeight: 600, background: '#f0fdf4', color: '#16a34a', padding: '2px 8px', borderRadius: 4 }}>
          ● Live
        </span>
      </div>
      <div>
        {feed.map((f, i) => {
          const t = tagTone(f.tag_tone);
          return (
            <div key={i}
              onClick={() => onFeedClick(f.agent)}
              style={{
                display: 'grid', gridTemplateColumns: '42px 70px 1fr 60px',
                alignItems: 'center', gap: 8, padding: '8px 0',
                borderBottom: i < feed.length - 1 ? '1px solid #f5f7fa' : 'none',
                fontSize: 12, cursor: 'pointer',
              }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = '#fafbfd'; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
            >
              <span style={{ color: '#9ca3af' }}>{f.time}</span>
              <span style={{ color: f.color, fontWeight: 600 }}>{f.agent}</span>
              <span style={{ color: '#374151' }}>{f.message}</span>
              <span style={{
                background: t.bg, color: t.color, fontSize: 10, fontWeight: 700,
                padding: '2px 6px', borderRadius: 3, textAlign: 'center',
              }}>
                {f.tag}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ──────────────────────── Loan Pipeline Panel ──────────────────────── */
function LoanPipelinePanel({ pipeline, clearedToday, onLoanClick }: {
  pipeline: DashboardState['loan_pipeline']; clearedToday: number;
  onLoanClick: (member: string) => void;
}) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0' }}>
      <div style={{
        fontSize: 13, fontWeight: 700, color: '#0d1f35', marginBottom: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        Active Loan Pipeline — Loan Document Agent
        <span style={{ fontSize: 11, fontWeight: 600, background: '#f0fdf4', color: '#16a34a', padding: '2px 8px', borderRadius: 4 }}>
          {clearedToday} Cleared Today
        </span>
      </div>
      <div style={{
        display: 'grid', gridTemplateColumns: '1fr 80px 80px 1fr 80px', gap: 8,
        fontSize: 11, fontWeight: 700, color: '#9ca3af',
        textTransform: 'uppercase', letterSpacing: '0.08em',
        paddingBottom: 8, borderBottom: '1px solid #f0f2f5', marginBottom: 6,
      }}>
        <span>Member</span><span>Type</span><span>Amount</span><span>Progress</span><span>Status</span>
      </div>
      {pipeline.map((l, i) => (
        <div key={i}
          onClick={() => onLoanClick(l.member)}
          style={{
            display: 'grid', gridTemplateColumns: '1fr 80px 80px 1fr 80px',
            gap: 8, alignItems: 'center', padding: '8px 0',
            borderBottom: i < pipeline.length - 1 ? '1px solid #f5f7fa' : 'none',
            fontSize: 12, cursor: 'pointer',
          }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = '#fafbfd'; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
        >
          <span style={{ fontWeight: 600, color: '#0d1f35' }}>{l.member}</span>
          <span style={{ color: '#6b7280' }}>{l.type}</span>
          <span style={{ fontWeight: 700, color: '#0d1f35' }}>{fmtUsd(l.amount_usd)}</span>
          <div>
            <div style={{ fontSize: 10, color: '#9ca3af', marginBottom: 3 }}>
              {l.progress_label} — {l.progress_pct}%
            </div>
            <div style={{ height: 4, background: '#f0f2f5', borderRadius: 2 }}>
              <div style={{ width: `${l.progress_pct}%`, height: 4, background: l.progress_color, borderRadius: 2 }} />
            </div>
          </div>
          <span style={{
            background:
              l.status === 'READY'   ? '#f0fdf4'
            : l.status === 'PENDING' ? '#fffbeb'
            : l.status === 'REVIEW'  ? '#eff6ff'
            : l.status === 'APPROVED'? '#f0fdf4'
            : '#faf5ff',
            color: l.status_color,
            fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 4, textAlign: 'center',
          }}>
            {l.status}
          </span>
        </div>
      ))}
    </div>
  );
}

/* ──────────────────────── Agent Accuracy ──────────────────────── */
function AgentAccuracyPanel({ agents, onAgentClick }: {
  agents: DashboardState['agent_accuracy'];
  onAgentClick: (name: string) => void;
}) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0' }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35', marginBottom: 14 }}>
        Agent Accuracy — June 2026
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {agents.map((a) => (
          <div key={a.name}
            onClick={() => onAgentClick(a.name)}
            style={{ cursor: 'pointer' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
              <span style={{ fontWeight: 600, color: '#0d1f35' }}>{a.name}</span>
              <span style={{ fontWeight: 700, color: a.color }}>{a.accuracy_pct.toFixed(1)}%</span>
            </div>
            <div style={{ height: 6, background: '#f0f2f5', borderRadius: 3 }}>
              <div style={{ width: `${a.accuracy_pct}%`, height: 6, background: a.color, borderRadius: 3 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ──────────────────────── Exam Countdown ──────────────────────── */
function ExamCountdownPanel({ exam, onClick }: {
  exam: DashboardState['exam_readiness'];
  onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0',
        textAlign: 'center', cursor: onClick ? 'pointer' : 'default',
      }}
    >
      <div style={{
        fontSize: 13, fontWeight: 700, color: '#0d1f35', marginBottom: 14,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        NCUA Exam Countdown
      </div>
      <div style={{
        fontFamily: 'Space Grotesk, sans-serif', fontSize: 64, fontWeight: 800,
        color: '#0d1f35', lineHeight: 1, margin: '16px 0 4px',
      }}>
        {exam.days_to_exam}
      </div>
      <div style={{ fontSize: 12, color: '#7a8fa6', marginBottom: 16 }}>days until exam window</div>
      <div style={{ background: '#f5f6fa', borderRadius: 8, padding: 12, textAlign: 'left' }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#0d1f35', marginBottom: 6 }}>
          Current readiness: <span style={{ color: '#d97706' }}>{exam.overall_pct}%</span> · Target:{' '}
          <span style={{ color: '#16a34a' }}>{exam.target_pct}%</span>
        </div>
        <div style={{ height: 8, background: '#e8ecf0', borderRadius: 4 }}>
          <div style={{
            width: `${exam.overall_pct}%`, height: 8,
            background: 'linear-gradient(90deg, #6c47ff, #00c4a0)', borderRadius: 4,
          }} />
        </div>
        <div style={{ fontSize: 11, color: '#16a34a', marginTop: 6, fontWeight: 600 }}>
          ✓ On track at current pace
        </div>
      </div>
    </div>
  );
}
