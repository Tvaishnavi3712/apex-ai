/**
 * EPROD (Enterprise Products) Executive Dashboard.
 *
 * Renders when Settings → Demo Mode = "EPROD AP & Document Intelligence".
 * Port of the reference HTML at demo5-eprod/dashboard.html — six-agent AP
 * stack (Invoice, PO, Vendor, Quote, Tariff, JIB), HITL queue, APEX Signal
 * preview, Audit Lens activity, and POC phase tracker.
 *
 * KPIs, agent rows, processing volume chart, and phase tracker all read from
 * the single backend endpoint /api/v1/eprod/dashboard-state. HITL queue and
 * Audit Lens activity feed remain on their existing endpoints.
 */
import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface HitlItem {
  request_id: string;
  cycle_id:   string;
  agent:      string;
  gate:       string;
  severity:   'high' | 'medium' | 'low';
  reason:     string;
  data?:      Record<string, any>;
  created_at: number;
  status:     string;
}

interface CycleRow {
  cycle_id?:  string;
  doc_type?:  string;
  vendor?:    string;
  status?:    string;
  amount?:    string | number;
  timestamp?: number | string;
}

// ─── /eprod/dashboard-state response shape ───
interface DashKpis {
  review_reduction_pct: number;
  review_minutes_before: number;
  review_minutes_after: number;
  validation_coverage_pct: number;
  validation_before_text: string;
  validation_segments: string[];
  cost_leakage_caught_usd: number;
  leakage_breakdown: Array<{ label: string; amount_usd: number }>;
}
interface DashAgentMetric { label: string; value: string; tone: string }
interface DashAgent {
  id: string;
  name: string;
  use_case: string;
  accent: string;
  badge: string;
  badge_tone: string;
  doc_count: number;
  starred: boolean;
  metrics: DashAgentMetric[];
}
interface DashAgentTotals {
  doc_count_total: number;
  invoices_30d: number;
  pos_30d: number;
  other_30d: number;
  agents_live: number;
}
interface ThroughputPoint { date: string; value: number }
interface DashThroughput {
  docs_processed: ThroughputPoint[];
  hitl_routed:    ThroughputPoint[];
}
interface DashPhase {
  id: number;
  name: string;
  use_case: string;
  status: string;
  gradient: string;
  starred?: boolean;
}
interface DashState {
  generated_at: string;
  kpis: DashKpis;
  agents: DashAgent[];
  agent_totals: DashAgentTotals;
  throughput_30d: DashThroughput;
  throughput_14d: DashThroughput;
  throughput_summary: {
    docs_30d_total: number; avg_docs_per_day: number;
    auto_approved_pct: number; hitl_routed_pct: number; vs_prior_pct: number;
  };
  phases: DashPhase[];
  signal_hero: {
    active_alerts: number; forecasts: number;
    contracts_at_risk: number; protected_mtd_usd: number;
  };
  agent_impact: Array<{
    agent_id: string; name: string; metric: string;
    before: string; after: string; delta: string;
    annual_savings_usd: number;
    context: string;
    starred?: boolean;
  }>;
  agent_impact_summary: {
    total_annual_savings_usd: number;
    avg_cycle_time_reduction_pct: number;
    audit_findings_avoided: number;
  };
}

// ──────────────────────── inline-style helpers ────────────────────────
const card: React.CSSProperties = {
  background: '#fff', borderRadius: 18, border: '1px solid #e8edf2',
  boxShadow: '0 1px 4px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.03)',
};
const chip = (bg: string, fg: string, bd: string): React.CSSProperties => ({
  display: 'inline-flex', alignItems: 'center', gap: 5, borderRadius: 99,
  padding: '3px 10px', fontSize: 11, fontWeight: 600,
  background: bg, color: fg, border: `1px solid ${bd}`,
});
const badge = (bg: string, fg: string, bd: string): React.CSSProperties => ({
  display: 'inline-flex', alignItems: 'center', fontSize: 10, fontWeight: 700,
  letterSpacing: '.06em', textTransform: 'uppercase', padding: '3px 8px',
  borderRadius: 6, background: bg, color: fg, border: `1px solid ${bd}`,
});
const sectionLabel: React.CSSProperties = {
  fontSize: 10, fontWeight: 700, letterSpacing: '.12em',
  textTransform: 'uppercase', color: '#94a3b8', marginBottom: 14,
};
const monoFont = "'JetBrains Mono', monospace";
const grotesk  = "'Space Grotesk', sans-serif";

function formatUsd(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `$${(n / 1_000).toFixed(0)}K`;
  return `$${n.toLocaleString()}`;
}

// Per-agent icon gradient (from accent) + header-metric unit. Accent is a
// single hex; we lighten it for the gradient stop.
function gradientFromAccent(accent: string): string {
  // Hand-tuned matches for known agent accents so existing visuals stay close.
  const map: Record<string, string> = {
    '#1a6db5': 'linear-gradient(135deg,#0f4c81,#1a6db5)',
    '#7c3aed': 'linear-gradient(135deg,#5b21b6,#7c3aed)',
    '#059669': 'linear-gradient(135deg,#065f46,#059669)',
    '#d97706': 'linear-gradient(135deg,#92400e,#d97706)',
    '#f59e0b': 'linear-gradient(135deg,#b45309,#f59e0b)',
    '#2563eb': 'linear-gradient(135deg,#1e3a5f,#2563eb)',
  };
  return map[accent] || `linear-gradient(135deg,${accent},${accent})`;
}

const AGENT_UNIT: Record<string, (n: number) => string> = {
  invoice: (n) => `${n.toLocaleString()} docs`,
  po:      (n) => `${n.toLocaleString()} POs`,
  vendor:  (n) => `${n.toLocaleString()} txns`,
  quote:   (n) => `${n.toLocaleString()} quotes`,
  tariff:  (n) => `${n.toLocaleString()} tariff lines`,
  jib:     (n) => `${n.toLocaleString()} JIB stmts`,
};
function headerMetricFor(agent: DashAgent): string {
  const f = AGENT_UNIT[agent.id];
  return f ? f(agent.doc_count) : `${agent.doc_count.toLocaleString()} docs`;
}

// Per-metric tone → text color
const TONE_COLOR: Record<string, string> = {
  good:    '#059669',
  warn:    '#d97706',
  bad:     '#dc2626',
  neutral: '#0f172a',
};

// Agent badge tone → badge styling
function agentBadgeStyle(tone: string): React.CSSProperties {
  if (tone === 'amber') return badge('rgba(245,158,11,.1)', '#d97706', 'rgba(245,158,11,.2)');
  return badge('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.2)');
}

const SEV_PALETTE: Record<string, { rowBg: string; rowBd: string; dot: string; badge: React.CSSProperties; label: string }> = {
  high:   { rowBg: '#fef2f2', rowBd: '#fecaca', dot: '#ef4444',
            badge: badge('rgba(220,38,38,.1)',  '#dc2626', 'rgba(220,38,38,.2)'),
            label: 'High' },
  medium: { rowBg: '#fffbeb', rowBd: '#fde68a', dot: '#f59e0b',
            badge: badge('rgba(245,158,11,.1)', '#d97706', 'rgba(245,158,11,.2)'),
            label: 'Medium' },
  low:    { rowBg: '#f0fdf4', rowBd: '#bbf7d0', dot: '#22c55e',
            badge: badge('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.2)'),
            label: 'Low' },
};

const HITL_FALLBACK: Array<{ title: string; detail: string; severity: 'high' | 'medium' | 'low' }> = [
  { title: 'INV-2026-04471 · Halliburton Energy',  detail: 'Rate mismatch: billed $184.50/hr vs. MSA $172.00/hr · $3,840 variance',  severity: 'high' },
  { title: 'TARIFF-DRIFT · Texas Eastern Pipeline', detail: 'FERC filed rate $0.2847/Dth · Billed $0.3012/Dth · 5.8% over',           severity: 'high' },
  { title: 'JIB-2026-MAY · Sweeny Hub JV',          detail: 'AFE-2024-0882 overrun: $2.1M charged vs. $1.85M approved',               severity: 'medium' },
  { title: 'PO-2026-08812 · Baker Hughes',          detail: 'Tax code mismatch: TX-E vs. TX-I · $12,400 tax differential',            severity: 'medium' },
  { title: 'QUOTE-2026-0041 · Exterran Corp',       detail: 'Confidence 74% — scope language ambiguous · Needs procurement review',   severity: 'low' },
];

const AUDIT_FALLBACK: Array<{ time: string; kind: 'approved' | 'flagged' | 'routed' | 'indexed'; text: string }> = [
  { time: '09:47:22', kind: 'approved', text: 'INV-2026-04468 · Schlumberger · $142,800' },
  { time: '09:44:15', kind: 'flagged',  text: 'TARIFF · Texas Eastern · Rate drift +5.8%' },
  { time: '09:41:03', kind: 'approved', text: 'PO-2026-08809 · Baker Hughes · $87,400' },
  { time: '09:38:50', kind: 'routed',   text: 'JIB · Sweeny Hub JV · AFE overrun $250K' },
  { time: '09:35:12', kind: 'approved', text: 'NON-PO · Exterran Corp · MSA validated' },
  { time: '09:31:44', kind: 'approved', text: 'INV-2026-04465 · Weatherford · $56,200' },
  { time: '09:28:09', kind: 'flagged',  text: 'INV-2026-04471 · Halliburton · Rate mismatch' },
  { time: '09:24:33', kind: 'indexed',  text: 'FERC · Panhandle Eastern · Tariff update filed' },
];

const AUDIT_BADGE: Record<string, React.CSSProperties> = {
  approved: badge('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.2)'),
  flagged:  badge('rgba(220,38,38,.1)',  '#dc2626', 'rgba(220,38,38,.2)'),
  routed:   badge('rgba(245,158,11,.1)', '#d97706', 'rgba(245,158,11,.2)'),
  indexed:  badge('rgba(59,130,246,.1)', '#2563eb', 'rgba(59,130,246,.2)'),
};

// ──────────────────────── component ────────────────────────

export function EprodDashboard() {
  const [clock, setClock] = useState('');
  useEffect(() => {
    const tick = () => {
      const n = new Date();
      const d = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][n.getDay()];
      const mo = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][n.getMonth()];
      let h = n.getHours(); const m = n.getMinutes(); const s = n.getSeconds();
      const ap = h >= 12 ? 'PM' : 'AM'; h = h % 12 || 12;
      setClock(`${d} ${mo} ${n.getDate()} · ${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')} ${ap}`);
    };
    tick(); const i = setInterval(tick, 1000); return () => clearInterval(i);
  }, []);

  // Single backend payload feeding KPIs, agents, volume chart, and phases.
  const dashStateQ = useQuery<DashState>({
    queryKey: ['eprod-dashboard-state'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/eprod/dashboard-state`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30000, refetchOnWindowFocus: false, retry: false,
  });
  const ds = dashStateQ.data;
  const dsLoading = dashStateQ.isLoading;
  const dsError   = dashStateQ.isError;

  // Live HITL queue (graceful fallback on error)
  const hitlQuery = useQuery<{ count: number; items: HitlItem[] }>({
    queryKey: ['eprod-hitl-pending'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/eprod/hitl/pending`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 8000, refetchOnWindowFocus: false, retry: false,
  });

  const hitlRows = useMemo(() => {
    const items = hitlQuery.data?.items;
    if (items && items.length > 0) {
      return items.slice(0, 5).map((it) => ({
        title:    `${it.gate || it.agent} · ${it.cycle_id || it.request_id}`,
        detail:   it.reason,
        severity: (it.severity || 'medium') as 'high' | 'medium' | 'low',
      }));
    }
    return HITL_FALLBACK;
  }, [hitlQuery.data]);

  const hitlPendingCount = hitlRows.length;

  // Live cycle-history → Audit Lens activity feed (graceful fallback)
  const cycleQuery = useQuery<{ items: CycleRow[] }>({
    queryKey: ['eprod-cycle-history'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/eprod/cycle-history?limit=8`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 10000, refetchOnWindowFocus: false, retry: false,
  });

  const auditRows = useMemo(() => {
    const items = cycleQuery.data?.items;
    if (!items || items.length === 0) return AUDIT_FALLBACK;
    return items.slice(0, 8).map((c): { time: string; kind: 'approved' | 'flagged' | 'routed' | 'indexed'; text: string } => {
      const ts = c.timestamp ? new Date(typeof c.timestamp === 'number' ? c.timestamp * 1000 : c.timestamp) : new Date();
      const time = `${String(ts.getHours()).padStart(2,'0')}:${String(ts.getMinutes()).padStart(2,'0')}:${String(ts.getSeconds()).padStart(2,'0')}`;
      const s = (c.status || '').toLowerCase();
      const kind: 'approved' | 'flagged' | 'routed' | 'indexed' =
        s.includes('flag')   ? 'flagged'  :
        s.includes('rout')   ? 'routed'   :
        s.includes('index')  ? 'indexed'  : 'approved';
      const text = [c.cycle_id, c.vendor, c.amount].filter(Boolean).join(' · ') || c.doc_type || 'Activity';
      return { time, kind, text };
    });
  }, [cycleQuery.data]);

  // ─── derived display values from dashboard-state ───
  const kpis = ds?.kpis;
  const dash = (v: string | number | undefined, fmt?: (n: number) => string): string => {
    if (v === undefined || v === null) return '—';
    if (typeof v === 'number' && fmt) return fmt(v);
    return String(v);
  };

  const reviewReductionValue = kpis ? `${kpis.review_reduction_pct}%` : '—';
  const reviewDetailHtml = kpis
    ? `Invoice review: <strong style="color:#93c5fd;">${kpis.review_minutes_before} min → ${kpis.review_minutes_after} min</strong> per document`
    : 'Invoice review reduction · loading…';
  const reviewProgressLabel: [string, string] = kpis
    ? [`${kpis.review_minutes_before} min`, `${kpis.review_minutes_after} min`]
    : ['—', '—'];
  const reviewProgressWidth = kpis?.review_reduction_pct ?? 0;

  const coverageValue = kpis ? `${kpis.validation_coverage_pct}%` : '—';
  const coverageDetailHtml = kpis
    ? `Up from <strong style="color:#86efac;">${kpis.validation_before_text}</strong> sampling to full automated coverage`
    : 'Validation coverage · loading…';
  const coverageChips = kpis ? kpis.validation_segments.map((s) => `${s} ✓`) : [];

  const leakageValue = kpis ? formatUsd(kpis.cost_leakage_caught_usd) : '—';
  const leakageChips = kpis
    ? kpis.leakage_breakdown.map((b) => `${formatUsd(b.amount_usd)} ${b.label.toLowerCase()}`)
    : [];

  const agents = ds?.agents ?? [];
  const agentTotals = ds?.agent_totals;
  const phases = ds?.phases ?? [];
  const agentImpact = ds?.agent_impact ?? [];
  const agentImpactSummary = ds?.agent_impact_summary;

  // Build volume-chart data from throughput_30d. The chart historically
  // showed three categories (Invoices/POs/Other); the new payload provides
  // total `docs_processed` and `hitl_routed`. Render both as two lines.
  const volumeSeries = useMemo(() => {
    const docs = ds?.throughput_30d?.docs_processed ?? [];
    const hitl = ds?.throughput_30d?.hitl_routed ?? [];
    return docs.map((d, i) => ({
      day: d.date.slice(5),                       // "MM-DD" tick
      docs: d.value,
      hitl: hitl[i]?.value ?? 0,
    }));
  }, [ds]);

  const docs30dTotal = ds?.throughput_summary?.docs_30d_total ?? agentTotals?.doc_count_total ?? 0;
  const agentsLive = agentTotals?.agents_live ?? 0;

  return (
    <div style={{ background: '#f0f4f8', minHeight: '100vh', padding: '28px 32px', maxWidth: 1600, margin: '0 auto' }}>

      {/* Top bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: grotesk, fontSize: 22, fontWeight: 800, color: '#0f172a', letterSpacing: '-.02em' }}>
            Executive Dashboard
          </div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
            AP & Document Intelligence · {agents.length || 6} Active Use Cases · May 2026
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
            {agentsLive || agents.length || 6} Agents Live
          </span>
          <span style={chip('#fffbeb', '#d97706', '#fde68a')}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }} />
            {hitlPendingCount} HITL Pending
          </span>
          <span style={{ fontSize: 12, color: '#64748b' }}>{clock}</span>
          <span style={chip('#f8fafc', '#475569', '#e2e8f0')}>Live · 30s refresh</span>
        </div>
      </div>

      {dsError && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fecaca', color: '#b91c1c',
          padding: '8px 14px', borderRadius: 10, fontSize: 12, marginBottom: 14,
        }}>
          Couldn&apos;t reach /eprod/dashboard-state · using defaults
        </div>
      )}

      {/* Headline KPIs */}
      <div style={sectionLabel}>Program Outcomes · POC Phase 1–2</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginBottom: 28 }}>
        <HeadlineKpi
          label="Manual Review Reduction" value={reviewReductionValue}
          detail={reviewDetailHtml}
          progressLabel={reviewProgressLabel} progressWidth={reviewProgressWidth}
          bgGradient="linear-gradient(135deg,#0f2d4a 0%,#0f4c81 100%)"
          accent="#93c5fd" accentBg="rgba(26,109,181,.25)" accentBd="rgba(26,109,181,.4)"
          progressBg="rgba(26,109,181,.2)" progressFill="linear-gradient(90deg,#1a6db5,#60a5fa)"
        />
        <HeadlineKpi
          label="Rate Validation Coverage" value={coverageValue}
          detail={coverageDetailHtml}
          chips={coverageChips}
          bgGradient="linear-gradient(135deg,#052e16 0%,#14532d 100%)"
          accent="#86efac" accentBg="rgba(34,197,94,.12)" accentBd="rgba(34,197,94,.22)"
        />
        <HeadlineKpi
          label="Cost Leakage Caught (MTD)" value={leakageValue}
          detail="Rate mismatches, tax errors, and FERC tariff drift caught pre-payment"
          chips={leakageChips}
          bgGradient="linear-gradient(135deg,#431407 0%,#7c2d12 100%)"
          accent="#fdba74" accentBg="rgba(251,146,60,.12)" accentBd="rgba(251,146,60,.22)"
        />
      </div>

      {/* Active Agents (left) + Right column */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>

        {/* Active Agents */}
        <div style={{ ...card, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Active Agents</div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                {agents.length || 6} agents deployed · EPROD Azure tenant
              </div>
            </div>
            <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
              All Systems Nominal
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {dsLoading && agents.length === 0 && (
              <div style={{ fontSize: 12, color: '#94a3b8', padding: '12px 4px' }}>Loading agents…</div>
            )}
            {agents.map((a) => (
              <AgentRow
                key={a.id}
                name={`${a.name}`}
                sub={a.use_case}
                iconBg={gradientFromAccent(a.accent)}
                headerMetric={headerMetricFor(a)}
                statusBadge={agentBadgeStyle(a.badge_tone)}
                statusLabel={a.badge}
                highlight={a.starred}
                isNew={a.starred}
                stats={a.metrics.map((m) => ({
                  label: m.label,
                  value: m.value,
                  color: TONE_COLOR[m.tone] || '#0f172a',
                }))}
              />
            ))}
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Document Processing Volume */}
          <div style={{ ...card, padding: 24, flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <div>
                <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Document Processing Volume</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>Last 30 days · All agents</div>
              </div>
              <span style={chip('#eff6ff', '#2563eb', '#bfdbfe')}>{docs30dTotal.toLocaleString()} total</span>
            </div>
            <div style={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={volumeSeries} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
                  <XAxis dataKey="day" tick={{ fontSize: 10, fill: '#94a3b8' }} interval={4} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} axisLine={false} tickLine={false} width={28} />
                  <Tooltip
                    contentStyle={{ fontSize: 11, borderRadius: 8, border: '1px solid #e2e8f0', boxShadow: '0 4px 12px rgba(0,0,0,.08)' }}
                    labelStyle={{ fontWeight: 700, color: '#0f172a' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 11 }} iconSize={8} />
                  <Line type="monotone" dataKey="docs" stroke="#1a6db5" strokeWidth={2} dot={false} name="Docs Processed" />
                  <Line type="monotone" dataKey="hitl" stroke="#d97706" strokeWidth={2} dot={false} name="HITL Routed" />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginTop: 16 }}>
              <VolumeStat value={dash(agentTotals?.invoices_30d, (n) => n.toLocaleString())} label="Invoices" />
              <VolumeStat value={dash(agentTotals?.pos_30d,      (n) => n.toLocaleString())} label="POs" />
              <VolumeStat value={dash(agentTotals?.other_30d,    (n) => n.toLocaleString())} label="Other Docs" />
            </div>
          </div>

          {/* HITL Review Queue */}
          <div style={{ ...card, padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div>
                <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#0f172a' }}>HITL Review Queue</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>Human-in-the-loop · Awaiting sign-off</div>
              </div>
              <span style={chip('#fffbeb', '#d97706', '#fde68a')}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }} />
                {hitlPendingCount} pending
              </span>
            </div>

            {hitlRows.map((row, i) => {
              const p = SEV_PALETTE[row.severity] || SEV_PALETTE.medium;
              return (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '14px 16px', borderRadius: 12,
                  border: `1px solid ${p.rowBd}`, marginBottom: 8, background: p.rowBg,
                }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.dot, flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {row.title}
                    </div>
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{row.detail}</div>
                  </div>
                  <div style={{ flexShrink: 0 }}>
                    <span style={p.badge}>{p.label}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* APEX Signal Preview + Audit Lens */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>

        {/* APEX Signal — representative summaries, kept hardcoded for now */}
        <div style={{
          ...card, padding: 24,
          background: 'linear-gradient(135deg,#0f172a 0%,#1e293b 100%)',
          border: '1px solid rgba(245,158,11,.2)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }} />
                <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#f9fafb' }}>APEX Signal</div>
                <div style={{ fontSize: 10, background: 'rgba(245,158,11,.15)', color: '#fbbf24', border: '1px solid rgba(245,158,11,.3)', borderRadius: 4, padding: '2px 8px', fontWeight: 700, letterSpacing: '.06em' }}>
                  PREDICTIVE
                </div>
              </div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>Forward-looking intelligence · Live signal feed</div>
            </div>
            <Link href="/apex-signal" style={{ fontSize: 12, fontWeight: 600, color: '#fbbf24', textDecoration: 'none' }}>
              Full Signal View →
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <SignalRow color="#ef4444" titleColor="#fca5a5"
              title="Vendor Rate Drift · Schlumberger"
              detail="Billed rates trending +6.1% above MSA over 90 days · Renewal in 34 days"
              tag="ALERT" bg="rgba(239,68,68,.1)" bd="rgba(239,68,68,.25)" />
            <SignalRow color="#f59e0b" titleColor="#fcd34d"
              title="FERC Tariff Forecast · Panhandle Eastern"
              detail="PPI-FG index trending +3.2% · Projected July 1 rate: $0.2941/Dth (+$0.0094)"
              tag="FORECAST" bg="rgba(245,158,11,.1)" bd="rgba(245,158,11,.25)" />
            <SignalRow color="#3b82f6" titleColor="#93c5fd"
              title="Contract Expiry Risk · 8 MSAs"
              detail="8 contracts expire within 90 days · Combined spend $47M · 3 renewals not initiated"
              tag="RISK" bg="rgba(59,130,246,.1)" bd="rgba(59,130,246,.25)" />
            <SignalRow color="#22c55e" titleColor="#86efac"
              title="JIB Burn Rate · Permian Basin Expansion"
              detail="AFE-2025-1104 tracking 94% of budget at 71% completion · On track"
              tag="NORMAL" bg="rgba(34,197,94,.08)" bd="rgba(34,197,94,.2)" />
          </div>
        </div>

        {/* Audit Lens */}
        <div style={{ ...card, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Audit Lens · Recent Activity</div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>Every decision captured · Full traceability</div>
            </div>
            <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>100% coverage</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {auditRows.map((row, i) => (
              <div key={i} style={{
                display: 'flex', gap: 12, padding: '10px 0',
                borderBottom: i === auditRows.length - 1 ? 'none' : '1px solid #f1f5f9',
              }}>
                <div style={{ fontSize: 11, fontFamily: monoFont, color: '#94a3b8', flexShrink: 0, width: 80 }}>{row.time}</div>
                <div style={{ flex: 1 }}>
                  <span style={{ ...AUDIT_BADGE[row.kind], marginRight: 6 }}>{row.kind.toUpperCase()}</span>
                  <span style={{ fontSize: 12, color: '#0f172a' }}>{row.text}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Agent Impact · Before vs After APEX */}
      {agentImpact.length > 0 && (
        <div style={{ ...card, padding: 24, marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20, gap: 16, flexWrap: 'wrap' }}>
            <div>
              <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#0f172a' }}>
                Agent Impact · Before vs After APEX
              </div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                Manual cycle vs APEX-assisted · annual savings projected from May 2026 throughput
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
              <span style={chip('#eff6ff', '#0f4c81', '#bfdbfe')}>
                Total annual savings: {agentImpactSummary ? formatUsd(agentImpactSummary.total_annual_savings_usd) : '—'}
              </span>
              <span style={chip('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.2)')}>
                Audit findings avoided: {agentImpactSummary?.audit_findings_avoided ?? 0}
              </span>
              {agentImpactSummary && (
                <span style={chip('#fff7ed', '#d97706', '#fed7aa')}>
                  Avg cycle time -{agentImpactSummary.avg_cycle_time_reduction_pct}%
                </span>
              )}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
            {agentImpact.map((a) => {
              const starred = !!a.starred;
              const borderColor = starred ? '#f59e0b' : '#e8edf2';
              const borderWidth = starred ? 2 : 1;
              const accentBg = starred ? '#fffbeb' : '#f8fafc';
              const deltaPillStyle = starred
                ? chip('rgba(245,158,11,.12)', '#b45309', 'rgba(245,158,11,.28)')
                : chip('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.22)');
              return (
                <div key={a.agent_id} style={{
                  background: '#fff', borderRadius: 14,
                  border: `${borderWidth}px solid ${borderColor}`,
                  padding: 16, display: 'flex', flexDirection: 'column', gap: 10,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                    <div style={{ fontFamily: grotesk, fontSize: 14, fontWeight: 700, color: '#0f172a' }}>
                      {a.name}{starred ? ' ⭐' : ''}
                    </div>
                    <div style={{ fontFamily: grotesk, fontSize: 20, fontWeight: 800, color: '#0f4c81', letterSpacing: '-.02em' }}>
                      {formatUsd(a.annual_savings_usd)}
                    </div>
                  </div>

                  <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8' }}>
                    {a.metric}
                  </div>

                  <div style={{ background: accentBg, borderRadius: 10, padding: 10, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', width: 50, flexShrink: 0 }}>BEFORE</div>
                      <div style={{ fontSize: 12, color: '#94a3b8', textDecoration: 'line-through' }}>{a.before}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                      <div style={{ fontSize: 10, fontWeight: 700, color: '#059669', width: 50, flexShrink: 0 }}>AFTER</div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: '#065f46' }}>{a.after}</div>
                    </div>
                  </div>

                  <div>
                    <span style={deltaPillStyle}>{a.delta}</span>
                  </div>

                  <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.5, marginTop: 'auto' }}>
                    {a.context}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* POC Phase Tracker */}
      <div style={{ ...card, padding: 24, marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <div style={{ fontFamily: grotesk, fontSize: 16, fontWeight: 700, color: '#0f172a' }}>POC Phase Tracker</div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
              {phases.length || 6} use cases · Phased deployment · EPROD Azure tenant
            </div>
          </div>
          <span style={chip('#eff6ff', '#2563eb', '#bfdbfe')}>Phase 1–{phases.length || 2} Active</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.max(phases.length, 6)}, 1fr)`, gap: 12 }}>
          {phases.map((p) => {
            // Pick a sensible shadow color derived from the gradient end-stop.
            const m = /,(#[0-9a-fA-F]{3,8})\)\s*$/.exec(p.gradient);
            const shadow = m ? `${m[1]}4D` : 'rgba(15,76,129,.3)';
            const statusLabel = (p.status || 'live').toLowerCase() === 'live'
              ? (p.starred ? 'Live ⭐' : 'Live')
              : p.status;
            return (
              <PhaseBadge
                key={p.id}
                num={p.id}
                label={p.name}
                bg={p.gradient}
                shadow={shadow}
                status={statusLabel}
                statusColor="#059669"
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ──────────────────────── sub-components ────────────────────────

function HeadlineKpi(props: {
  label: string; value: string; detail: string;
  progressLabel?: [string, string]; progressWidth?: number;
  chips?: string[];
  bgGradient: string; accent: string; accentBg: string; accentBd: string;
  progressBg?: string; progressFill?: string;
}) {
  return (
    <div style={{ background: props.bgGradient, borderRadius: 20, padding: '28px 32px', position: 'relative', overflow: 'hidden', border: `1px solid ${props.accentBd}` }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: `${props.accent}b3`, marginBottom: 6 }}>
            {props.label}
          </div>
          <div style={{ fontFamily: grotesk, fontSize: 52, fontWeight: 800, color: '#fff', lineHeight: 1, letterSpacing: '-.03em' }}>
            {props.value}
          </div>
        </div>
        <div style={{ width: 52, height: 52, borderRadius: 16, background: props.accentBg, border: `1px solid ${props.accentBd}` }} />
      </div>
      <div style={{ fontSize: 13, color: `${props.accent}cc`, lineHeight: 1.5 }} dangerouslySetInnerHTML={{ __html: props.detail }} />
      {props.progressLabel && (
        <div style={{ marginTop: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: `${props.accent}99`, marginBottom: 6 }}>
            <span>Before APEX</span><span>With APEX</span>
          </div>
          <div style={{ height: 6, borderRadius: 99, background: props.progressBg, overflow: 'hidden' }}>
            <div style={{ height: '100%', borderRadius: 99, width: `${props.progressWidth}%`, background: props.progressFill, transition: 'width 1.4s' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: `${props.accent}b3`, marginTop: 5 }}>
            <span>{props.progressLabel[0]}</span><span>{props.progressLabel[1]}</span>
          </div>
        </div>
      )}
      {props.chips && props.chips.length > 0 && (
        <div style={{ marginTop: 14, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {props.chips.map((c) => (
            <div key={c} style={{ background: props.accentBg, border: `1px solid ${props.accentBd}`, borderRadius: 8, padding: '6px 12px', fontSize: 11, fontWeight: 600, color: props.accent }}>
              {c}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AgentRow(props: {
  name: string; sub: string;
  iconBg: string; headerMetric: string;
  statusBadge: React.CSSProperties; statusLabel: string;
  stats: Array<{ label: string; value: string; color: string }>;
  highlight?: boolean; isNew?: boolean; last?: boolean;
}) {
  return (
    <div style={{
      borderRadius: 16,
      border: props.highlight ? '1px solid #fde68a' : '1px solid #e8edf2',
      background: props.highlight ? '#fffdf5' : '#fff',
      padding: '20px 22px',
      marginBottom: props.last ? 0 : 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 36, height: 36, borderRadius: 10, background: props.iconBg, flexShrink: 0 }} />
          <div>
            <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>
              {props.name}
              {props.isNew && (
                <span style={{ fontSize: 10, background: '#fef3c7', color: '#d97706', border: '1px solid #fde68a', borderRadius: 4, padding: '1px 6px', marginLeft: 6, fontWeight: 700 }}>
                  ⭐ NEW
                </span>
              )}
            </div>
            <div style={{ fontSize: 11, color: '#64748b' }}>{props.sub}</div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={props.statusBadge}>{props.statusLabel}</span>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a', fontFamily: monoFont }}>{props.headerMetric}</div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 12 }}>
        {props.stats.map((s) => (
          <div key={s.label} style={{ flex: 1 }}>
            <div style={{ fontSize: 10, color: '#94a3b8', marginBottom: 4 }}>{s.label}</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: s.color }}>{s.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function VolumeStat({ value, label }: { value: string; label: string }) {
  return (
    <div style={{ textAlign: 'center', padding: 10, background: '#f8fafc', borderRadius: 10 }}>
      <div style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', fontFamily: grotesk }}>{value}</div>
      <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>{label}</div>
    </div>
  );
}

function SignalRow(props: {
  color: string; titleColor: string;
  title: string; detail: string; tag: string;
  bg: string; bd: string;
}) {
  return (
    <div style={{
      padding: '12px 14px', background: props.bg, border: `1px solid ${props.bd}`,
      borderRadius: 10, display: 'flex', alignItems: 'center', gap: 10,
    }}>
      <div style={{ width: 6, height: 6, borderRadius: '50%', background: props.color, flexShrink: 0 }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: props.titleColor }}>{props.title}</div>
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>{props.detail}</div>
      </div>
      <div style={{ fontSize: 10, fontWeight: 700, color: props.color, fontFamily: monoFont }}>{props.tag}</div>
    </div>
  );
}

function PhaseBadge(props: {
  num: number; label: string; bg: string; shadow: string;
  status: string; statusColor: string;
}) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: 48, height: 48, borderRadius: '50%', background: props.bg,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        margin: '0 auto 8px', boxShadow: `0 4px 12px ${props.shadow}`,
      }}>
        <span style={{ fontSize: 16, fontWeight: 800, color: '#fff' }}>{props.num}</span>
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{props.label}</div>
      <div style={{ fontSize: 10, color: props.statusColor, marginTop: 2, fontWeight: 600 }}>● {props.status}</div>
    </div>
  );
}
