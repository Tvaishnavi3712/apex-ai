/**
 * CwfcuDashboard — CommunityWide Federal Credit Union demo dashboard.
 *
 * Renders the "One member · One exam · Five agents" story. All data sourced
 * from /api/v1/cwfcu/dashboard-state — zero hardcoded UI values per CLAUDE.md
 * ZERO-HARDCODING RULE.
 *
 * Layout (mirrors /Users/babbu/Downloads/demo6-cwfcu/dashboard.html):
 *   • 4 KPI cards: Docs Processed · Compliance Risk Caught · Loan Processing · NCUA Exam
 *   • Active Agents grid (6 cards — 5 agents + dark APEX Signal card)
 *   • HITL Review Queue + NCUA Exam Readiness folder bars (bottom row)
 *
 * Color palette pulled from the HTML mockup: purple #6c47ff (router/primary),
 * teal #00c4a0 (success/forecast), navy #0d1f35 (text), amber #d97706,
 * red #ef4444, green #16a34a. Fonts: Space Grotesk (display) + Inter (body).
 */
import React from 'react';
import Link from 'next/link';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useCwfcuToast, postCwfcuAction } from './cwfcuToast';
import { useProductBrand, brandLabel, brandWordmark } from '@/lib/productBrand';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface DashboardState {
  kpis: {
    docs_processed_mtd: number;
    docs_today_delta_pct: number;
    compliance_risk_caught_usd: number;
    loan_processing_days: number;
    loan_processing_baseline_days: number;
    ncua_exam_readiness_pct: number;
    ncua_exam_readiness_delta_pts: number;
  };
  exam_readiness: {
    overall_pct: number;
    target_pct: number;
    days_to_exam: number;
    folder_scores: Array<{ name: string; pct: number; tone: string }>;
    auto_assembled_pct: number;
    manual_categories_remaining: number;
    trajectory_msg: string;
  };
  agents: Array<{
    id: string;
    name: string;
    code: string;
    icon: string;
    icon_bg: string;
    accent: string;
    status: string;
    description: string;
    primary_metric: { label: string; value: string };
    secondary_metric: { label: string; value: string };
    fill_pct: number;
    fill_color: string;
  }>;
  apex_signal: {
    active_signals: number;
    critical_signals: number;
    fill_pct: number;
  };
  hitl_queue: Array<{
    id: string;
    doc: string;
    agent: string;
    priority: string;
    tone: string;
    flagged_minutes_ago: number;
    days_remaining?: number;
    action: string;
  }>;
  generated_at: string;
}

const fmtUsdM = (n: number): string => {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(0)}K`;
  return `$${n.toLocaleString()}`;
};

const fmtMinAgo = (m: number): string => {
  if (m < 60) return `${m} min ago`;
  const hrs = Math.floor(m / 60);
  return hrs < 24 ? `${hrs} hrs ago` : `${Math.floor(hrs / 24)}d ago`;
};

const toneColor: Record<string, string> = {
  red:   '#ef4444',
  amber: '#d97706',
  green: '#16a34a',
  teal:  '#00c4a0',
  blue:  '#2563eb',
};

const folderToneColor = (tone: string): string =>
  tone === 'good' ? '#16a34a' : tone === 'warn' ? '#d97706' : '#ef4444';

const priorityBadge = (priority: string, tone: string): { bg: string; color: string } => ({
  bg:    tone === 'red'  ? '#fef2f2' : tone === 'amber' ? '#fffbeb' : '#f0fdf4',
  color: tone === 'red'  ? '#dc2626' : tone === 'amber' ? '#d97706' : '#16a34a',
});

export function CwfcuDashboard() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { Toast, push } = useCwfcuToast();
  const [brand] = useProductBrand();
  const signalName = brandLabel('Apex Signal', brand);
  const productWordmark = brandWordmark(brand);  // 'APEX' or 'REGULUS LENS'
  const q = useQuery<DashboardState>({
    queryKey: ['cwfcu-dashboard-state'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/cwfcu/dashboard-state`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30_000,
    retry: 1,
    staleTime: 15_000,
  });

  if (q.isLoading || !q.data) {
    return (
      <div style={{ padding: 32, color: '#7a8fa6', fontFamily: 'Inter, sans-serif' }}>
        Loading CommunityWide FCU dashboard…
      </div>
    );
  }
  if (q.isError) {
    return (
      <div style={{ padding: 32, color: '#dc2626', fontFamily: 'Inter, sans-serif' }}>
        Failed to load CWFCU dashboard. Check that backend /cwfcu/dashboard-state is up.
      </div>
    );
  }

  const d = q.data;

  const handleHitlAction = async (item: DashboardState['hitl_queue'][0]) => {
    const endpoint = item.action === 'approve' ? 'approve' : 'file-sar';
    // For non-SAR items, use approve. For SAR items, use file-sar via Human Review's confirm flow.
    const url = item.id.startsWith('SAR')
      ? `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(item.id)}/file-sar`
      : `${API_BASE_URL}/cwfcu/hitl/${encodeURIComponent(item.id)}/${endpoint}`;
    const r = await postCwfcuAction(url, push);
    if (r?.ok) {
      queryClient.invalidateQueries({ queryKey: ['cwfcu-dashboard-state'] });
    }
  };

  const handleHitlOpen = (id: string) => router.push(`/review?item=${encodeURIComponent(id)}`);

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1f35' }}>
      <Toast />

      {/* HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 24, fontWeight: 800, color: '#0d1f35' }}>
            Executive Dashboard
          </div>
          <div style={{ fontSize: 12, color: '#7a8fa6', marginTop: 2 }}>
            CommunityWide Federal Credit Union · {d.agents.length} agents live · NCUA exam in {d.exam_readiness.days_to_exam} days
          </div>
        </div>
        <div style={{
          background: '#fef3c7', border: '1px solid #fcd34d', borderRadius: 20,
          padding: '6px 14px', fontSize: 12, fontWeight: 700, color: '#92400e',
        }}>
          NCUA exam · {d.exam_readiness.days_to_exam}d
        </div>
      </div>

      {/* KPI STRIP — 4 cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <KpiCard
          label="Documents Processed"
          value={d.kpis.docs_processed_mtd.toLocaleString()}
          valueColor="#00c4a0"
          delta={`↑ ${d.kpis.docs_today_delta_pct}% vs. last month`}
          sub="Across all 5 agents"
        />
        <KpiCard
          label="Compliance Risk Caught"
          value={fmtUsdM(d.kpis.compliance_risk_caught_usd)}
          delta="↑ Potential regulatory exposure avoided"
          sub="SAR + BSA exceptions flagged"
        />
        <KpiCard
          label="Loan Processing Time"
          value={`${d.kpis.loan_processing_days} `}
          valueColor="#00c4a0"
          valueSuffix="days"
          delta={`↓ From ${d.kpis.loan_processing_baseline_days} days manual baseline`}
          sub="Avg. doc-to-decision cycle"
        />
        <KpiCard
          label="NCUA Exam Readiness"
          value={`${d.kpis.ncua_exam_readiness_pct}`}
          valueSuffix="%"
          delta={`↑ ${d.kpis.ncua_exam_readiness_delta_pts} pts in 30 days`}
          sub="Document completeness score"
        />
      </div>

      {/* ACTIVE AGENTS */}
      <div style={{
        fontFamily: 'Space Grotesk, sans-serif', fontSize: 16, fontWeight: 700,
        color: '#0d1f35', marginBottom: 14,
      }}>
        Active Agents
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
        {d.agents.map((a) => (
          <AgentCard key={a.id} agent={a} />
        ))}
        {/* Dark Signal card — brand-aware label */}
        <ApexSignalCard signal={d.apex_signal} signalName={signalName} />
      </div>

      {/* BOTTOM GRID — HITL Queue + NCUA Exam Readiness */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <HitlQueuePanel items={d.hitl_queue} onAction={handleHitlAction} onOpen={handleHitlOpen} />
        <NcuaExamPanel
          exam={d.exam_readiness}
          productWordmark={productWordmark}
          onClick={() => router.push('/apex-signal')}
        />
      </div>
    </div>
  );
}

/* ──────────────────────── KPI Card ──────────────────────── */
function KpiCard({
  label, value, valueSuffix, valueColor, delta, sub,
}: {
  label: string; value: string; valueSuffix?: string; valueColor?: string;
  delta?: string; sub?: string;
}) {
  return (
    <div style={{
      background: '#fff', borderRadius: 12, padding: '20px 22px', border: '1px solid #e8ecf0',
    }}>
      <div style={{
        fontSize: 11, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase',
        color: '#7a8fa6', marginBottom: 8,
      }}>
        {label}
      </div>
      <div style={{
        fontFamily: 'Space Grotesk, sans-serif', fontSize: 36, fontWeight: 800,
        color: valueColor || '#0d1f35', lineHeight: 1,
      }}>
        {value}
        {valueSuffix && (
          <span style={{ fontSize: 18, fontWeight: 600 }}>{valueSuffix}</span>
        )}
      </div>
      {delta && (
        <div style={{ fontSize: 12, marginTop: 6, color: '#16a34a' }}>{delta}</div>
      )}
      {sub && (
        <div style={{ fontSize: 12, color: '#7a8fa6', marginTop: 4 }}>{sub}</div>
      )}
    </div>
  );
}

/* ──────────────────────── Agent Card ──────────────────────── */
function AgentCard({ agent }: { agent: DashboardState['agents'][0] }) {
  return (
    <Link href={`/agent-hub?agent=${encodeURIComponent(agent.id)}`} style={{ textDecoration: 'none' }}>
      <div style={{
        background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0',
        cursor: 'pointer', transition: 'box-shadow .15s',
      }}
      onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 14px rgba(108,71,255,0.08)'; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.boxShadow = 'none'; }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <div style={{
              width: 38, height: 38, borderRadius: 9, background: agent.icon_bg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 16, fontWeight: 800, color: agent.accent,
            }}>
              {agent.code}
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>{agent.name}</div>
              <div style={{ fontSize: 11, color: '#7a8fa6', lineHeight: 1.4, marginTop: 2 }}>
                {agent.description}
              </div>
            </div>
          </div>
          <span style={{
            fontSize: 11, fontWeight: 700, padding: '3px 9px', borderRadius: 4,
            background: agent.status === 'live' ? '#f0fdf4' : '#eff6ff',
            color:      agent.status === 'live' ? '#16a34a' : '#2563eb',
          }}>
            {agent.status.toUpperCase()}
          </span>
        </div>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f2f5',
        }}>
          <div>
            <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 22, fontWeight: 800, color: '#0d1f35' }}>
              {agent.primary_metric.value}
            </div>
            <div style={{ fontSize: 11, color: '#7a8fa6' }}>{agent.primary_metric.label}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: agent.fill_color }}>
              {agent.secondary_metric.value}
            </div>
            <div style={{ fontSize: 11, color: '#7a8fa6' }}>{agent.secondary_metric.label}</div>
          </div>
        </div>
        <div style={{ height: 4, borderRadius: 2, background: '#f0f2f5', marginTop: 8 }}>
          <div style={{ height: 4, borderRadius: 2, background: agent.fill_color, width: `${agent.fill_pct}%` }} />
        </div>
      </div>
    </Link>
  );
}

/* ──────────────────────── APEX/Regulus Signal Card (dark) ──────────────────────── */
function ApexSignalCard({ signal, signalName }: {
  signal: DashboardState['apex_signal'];
  signalName: string;
}) {
  return (
    <Link href="/apex-signal" style={{ textDecoration: 'none' }}>
      <div style={{
        background: '#0d1f35', borderRadius: 12, padding: 20, border: '1px solid #0d1f35',
        cursor: 'pointer',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
            <div style={{
              width: 38, height: 38, borderRadius: 9, background: 'rgba(0,196,160,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
            }}>
              📡
            </div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>{signalName}</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.55)', lineHeight: 1.4, marginTop: 2 }}>
                Predictive intelligence · Early warning · Exam readiness
              </div>
            </div>
          </div>
          <span style={{
            fontSize: 11, fontWeight: 700, padding: '3px 9px', borderRadius: 4,
            background: 'rgba(0,196,160,0.15)', color: '#00c4a0',
          }}>
            SIGNAL
          </span>
        </div>
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginTop: 12, paddingTop: 12, borderTop: '1px solid rgba(255,255,255,0.1)',
        }}>
          <div>
            <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 22, fontWeight: 800, color: '#00c4a0' }}>
              {signal.active_signals}
            </div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)' }}>Active signals firing</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#f59e0b' }}>{signal.critical_signals} Critical</div>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)' }}>Require action</div>
          </div>
        </div>
        <div style={{ height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.1)', marginTop: 8 }}>
          <div style={{ height: 4, borderRadius: 2, background: '#00c4a0', width: `${signal.fill_pct}%` }} />
        </div>
      </div>
    </Link>
  );
}

/* ──────────────────────── HITL Queue Panel ──────────────────────── */
function HitlQueuePanel({ items, onAction, onOpen }: {
  items: DashboardState['hitl_queue'];
  onAction: (item: DashboardState['hitl_queue'][0]) => void;
  onOpen:   (id: string) => void;
}) {
  const top5 = items.slice(0, 5);
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0' }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14,
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>HITL Review Queue</div>
        <Link href="/review" style={{ textDecoration: 'none' }}>
          <span style={{
            fontSize: 11, fontWeight: 600, background: '#fef2f2', color: '#ef4444',
            padding: '2px 8px', borderRadius: 4, cursor: 'pointer',
          }}>
            {items.length} Pending →
          </span>
        </Link>
      </div>
      {top5.map((it) => (
        <div
          key={it.id}
          onClick={() => onOpen(it.id)}
          style={{
            display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0',
            borderBottom: '1px solid #f5f7fa', cursor: 'pointer',
          }}
          onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.background = '#fafbfd'; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.background = 'transparent'; }}
        >
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: toneColor[it.tone] }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: '#0d1f35' }}>{it.doc}</div>
            <div style={{ fontSize: 11, color: '#7a8fa6', marginTop: 1 }}>
              {it.agent} · Flagged {fmtMinAgo(it.flagged_minutes_ago)} · {it.priority}
              {it.days_remaining !== undefined && ` · ${it.days_remaining}d remaining`}
            </div>
          </div>
          <button
            onClick={(e) => { e.stopPropagation(); onAction(it); }}
            style={{
              fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 5,
              background: it.action === 'approve' ? '#f0fdf4' : '#0d1f35',
              color:      it.action === 'approve' ? '#16a34a' : '#00c4a0',
              cursor: 'pointer', border: 'none',
            }}
          >
            {it.action === 'approve' ? 'Approve' : 'Review'}
          </button>
        </div>
      ))}
    </div>
  );
}

/* ──────────────────────── NCUA Exam Panel ──────────────────────── */
function NcuaExamPanel({ exam, productWordmark, onClick }: {
  exam: DashboardState['exam_readiness'];
  productWordmark: string;
  onClick?: () => void;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0',
        cursor: onClick ? 'pointer' : 'default', transition: 'box-shadow .15s',
      }}
      onMouseEnter={(e) => { if (onClick) (e.currentTarget as HTMLDivElement).style.boxShadow = '0 4px 14px rgba(108,71,255,0.08)'; }}
      onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.boxShadow = 'none'; }}
    >
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14,
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>NCUA Exam Readiness — 2026</div>
        <span style={{
          fontSize: 11, fontWeight: 600, background: '#fffbeb', color: '#d97706',
          padding: '2px 8px', borderRadius: 4,
        }}>
          {exam.days_to_exam} Days
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 18 }}>
        <div style={{ textAlign: 'center', minWidth: 120 }}>
          <div style={{
            fontFamily: 'Space Grotesk, sans-serif', fontSize: 52, fontWeight: 800,
            color: '#0d1f35', lineHeight: 1,
          }}>
            {exam.overall_pct}<span style={{ fontSize: 24 }}>%</span>
          </div>
          <div style={{ fontSize: 11, color: '#7a8fa6', marginTop: 2 }}>Overall Score</div>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, color: '#4a6080', lineHeight: 1.6 }}>
            {productWordmark} has assembled <strong>{exam.auto_assembled_pct}% of NCUA&apos;s standard exam request list</strong>{' '}
            automatically. {exam.manual_categories_remaining} document categories still require manual input from your team.
          </div>
        </div>
      </div>

      {exam.folder_scores.map((f) => (
        <div key={f.name} style={{
          display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderBottom: '1px solid #f5f7fa',
        }}>
          <div style={{ flex: 1, fontSize: 12, fontWeight: 600, color: '#0d1f35' }}>{f.name}</div>
          <div style={{ width: 120 }}>
            <div style={{ height: 6, borderRadius: 3, background: '#f0f2f5' }}>
              <div style={{
                height: 6, borderRadius: 3, background: folderToneColor(f.tone), width: `${f.pct}%`,
              }} />
            </div>
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, width: 36, textAlign: 'right', color: folderToneColor(f.tone) }}>
            {f.pct}%
          </div>
        </div>
      ))}

      <div style={{
        marginTop: 14, background: '#f0fdf4', borderRadius: 7, padding: '10px 14px',
        fontSize: 12, color: '#166534', fontWeight: 500,
      }}>
        ✓ {exam.trajectory_msg}
      </div>
    </div>
  );
}
