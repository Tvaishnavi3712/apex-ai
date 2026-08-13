/**
 * EPROD — Command Center.
 *
 * Wired to GET /api/v1/eprod/dashboard-state for all values. HITL queue keeps
 * the existing /eprod/hitl/pending poll. Feed continues to auto-ticker but
 * seeds from the dashboard-state response.
 *
 * Dark theme · EPROD blue gradient #0f4c81 → #1a6db5.
 */
import { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ──────────────────── API types ────────────────────
interface EprodHitlItem {
  request_id: string;
  agent:      string;
  severity:   'high' | 'medium' | 'low';
  title:      string;
  detail:     string;
  reviewer?:  string;
  created_at: number;
}

interface AgentMetric { label: string; value: string; tone: string }
interface AgentDto {
  id: string; name: string; accent: string;
  badge: string; badge_tone: string;
  doc_count: number; starred: boolean;
  metrics: AgentMetric[];
}

interface ThroughputPoint { date: string; value: number }
interface ThroughputSummary {
  docs_30d_total: number;
  avg_docs_per_day: number;
  auto_approved_pct: number;
  hitl_routed_pct: number;
  vs_prior_pct: number;
}

interface TariffDiff {
  header: { subtitle: string; chip: string };
  ferc:    { label: string; tariff_sheet: string; effective: string; zone: string; rate_value: number; rate_display: string; unit: string };
  invoice: { label: string; invoice_id: string;   gas_day: string;   zone: string; rate_value: number; rate_display: string; unit: string };
  diff_lines: Array<{ kind: 'context' | 'removed' | 'added'; text: string }>;
  impact: { lines_affected: number; avg_dth_per_day: number; days: number; monthly_exposure_usd: number };
  kpis: Array<{ label: string; value: string; tone: string }>;
}

interface JibRowDto {
  jv: string; operator: string; afe: string;
  approved_usd: number; charged_usd: number; variance_usd: number;
  status: string; tone: string; pct_of_afe: number;
}
interface JibReconciliation {
  rows: JibRowDto[];
  callout: { tone: string; text: string };
}

interface FeedEntry {
  time: string; agent: string; agent_tone: string;
  doc_id: string; detail: string;
  status: string; status_tone: string; trailer: string;
}

interface DashboardState {
  agents: AgentDto[];
  throughput_14d: { docs_processed: ThroughputPoint[]; hitl_routed: ThroughputPoint[] };
  throughput_summary: ThroughputSummary;
  tariff_diff: TariffDiff;
  jib_reconciliation: JibReconciliation;
  processing_feed: FeedEntry[];
}

// ──────────────────── helpers ────────────────────
function formatUsd(n: number, opts?: { full?: boolean }): string {
  if (opts?.full) {
    const sign = n < 0 ? '-' : '';
    return sign + '$' + Math.abs(n).toLocaleString();
  }
  const abs = Math.abs(n);
  const sign = n < 0 ? '-' : '';
  if (abs >= 1_000_000) return `${sign}$${(abs / 1_000_000).toFixed(2)}M`;
  if (abs >= 1_000)     return `${sign}$${(abs / 1_000).toFixed(0)}K`;
  return sign + '$' + abs.toLocaleString();
}

const AGENT_TONE_COLOR: Record<string, string> = {
  blue:   '#60a5fa',
  purple: '#c4b5fd',
  green:  '#4ade80',
  amber:  '#fbbf24',
  cyan:   '#22d3ee',
};
const STATUS_TONE_COLOR: Record<string, string> = {
  good:    '#4ade80',
  bad:     '#f87171',
  warn:    '#fbbf24',
  neutral: '#94a3b8',
};

// SVG icon paths keyed by agent id (kept from prior hardcoded design)
const AGENT_ICON_PATHS: Record<string, string> = {
  invoice: 'M9 2h6l5 5v15H4V2h5zm0 0v5h5',
  po:      'M3 4h18v6H3zM3 14h18v6H3z',
  vendor:  'M5 8h14l-1 12H6L5 8zm3-3h8v3H8z',
  quote:   'M6 4h12v16l-6-3-6 3z',
  tariff:  'M3 3v18h18M7 17l4-4 3 3 5-6',
  jib:     'M4 4h16v4H4zM4 12h16v4H4zM4 20h10v0',
};
function iconForAgentId(id: string): string {
  return AGENT_ICON_PATHS[id] || AGENT_ICON_PATHS.invoice;
}

// ──────────────────── styling helpers ────────────────────
const panel: React.CSSProperties = {
  background: '#0d1117', border: '1px solid rgba(255,255,255,.07)', borderRadius: 16,
};
const panelHeader: React.CSSProperties = {
  padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,.06)',
  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
};
const chip = (bg: string, fg: string, bd: string): React.CSSProperties => ({
  display: 'inline-flex', alignItems: 'center', gap: 5, borderRadius: 99,
  padding: '3px 10px', fontSize: 11, fontWeight: 600,
  background: bg, color: fg, border: `1px solid ${bd}`,
});
const dot = (bg: string): React.CSSProperties => ({
  width: 8, height: 8, borderRadius: '50%', flexShrink: 0, background: bg, display: 'inline-block',
});
const mono: React.CSSProperties = { fontFamily: "'JetBrains Mono', monospace" };
const heading: React.CSSProperties = { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 800, color: '#f9fafb', letterSpacing: '-.01em' };

// ──────────────────── feed ────────────────────
interface FeedLine { time: string; html: string }

function buildFeedHtml(e: FeedEntry): string {
  const agentColor = AGENT_TONE_COLOR[e.agent_tone] || '#94a3b8';
  const statusColor = STATUS_TONE_COLOR[e.status_tone] || '#94a3b8';
  return (
    `<span style="color:${agentColor}">[${e.agent}]</span> ` +
    `<span style="color:#f9fafb;font-weight:600">${e.doc_id}</span> ` +
    `<span style="color:#9ca3af">${e.detail}</span> ` +
    `<span style="color:${statusColor}">→ ${e.status}</span>` +
    (e.trailer ? ` <span style="color:#9ca3af">${e.trailer}</span>` : '')
  );
}

// templated random tickers (keep look-and-feel of live activity)
const LIVE_LINES = [
  () => {
    const n = 4473 + Math.floor(Math.random() * 80);
    const v = (20 + Math.floor(Math.random() * 180)).toLocaleString();
    return `<span style="color:#60a5fa">[Invoice Agent]</span> <span style="color:#f9fafb;font-weight:600">INV-2026-0${n}</span> <span style="color:#9ca3af">Schlumberger · $${v},000 · PDF native</span> <span style="color:#4ade80">→ EXTRACTED</span> <span style="color:#9ca3af">conf:${(92 + Math.random() * 6).toFixed(1)}%</span>`;
  },
  () => `<span style="color:#c4b5fd">[PO Agent]</span> <span style="color:#f9fafb;font-weight:600">PO-2026-0${8813 + Math.floor(Math.random() * 40)}</span> <span style="color:#9ca3af">${['Cameron','Baker Hughes','Weatherford','SLB'][Math.floor(Math.random()*4)]} · contract match</span> <span style="color:#4ade80">→ VALIDATED</span>`,
  () => `<span style="color:#4ade80">[Vendor Agent]</span> <span style="color:#f9fafb;font-weight:600">NON-PO-2026-0${815 + Math.floor(Math.random() * 30)}</span> <span style="color:#9ca3af">MSA validated</span> <span style="color:#4ade80">→ APPROVED</span>`,
  () => `<span style="color:#fbbf24">[Tariff Agent]</span> <span style="color:#f9fafb;font-weight:600">FERC-${['TETCO','PANHANDLE','ANR'][Math.floor(Math.random()*3)]}-2026-${7 + Math.floor(Math.random()*5)}</span> <span style="color:#9ca3af">rate sheet indexed</span> <span style="color:#fbbf24">→ INDEXED</span>`,
  () => `<span style="color:#22d3ee">[JIB Agent]</span> <span style="color:#f9fafb;font-weight:600">JIB-${['SWEENY','TARGA','PERMIAN'][Math.floor(Math.random()*3)]}-MAY26</span> <span style="color:#9ca3af">AFE match · ${1 + Math.floor(Math.random()*5)} lines</span> <span style="color:#4ade80">→ RECONCILED</span>`,
];

// ──────────────────── hardcoded HITL demo rows ────────────────────
interface HitlSeed {
  id:        string;
  title:     string;
  detail:    string;
  severity:  'high' | 'medium' | 'low';
  iconBg:    string;
  iconBd:    string;
  iconColor: string;
  agentChip: { bg: string; fg: string; bd: string; text: string };
  reviewer:  string;
  icon:      'warn' | 'tariff' | 'jib' | 'po' | 'quote';
}

const HITL_SEEDS: HitlSeed[] = [
  {
    id: 'INV-2026-04471',
    title: 'INV-2026-04471 · Halliburton Energy',
    detail: 'Rate mismatch: billed $184.50/hr vs. MSA $172.00/hr · 20.8 hrs · $3,840 variance',
    severity: 'high',
    iconBg: 'rgba(239,68,68,.15)', iconBd: 'rgba(239,68,68,.3)', iconColor: '#f87171',
    agentChip: { bg: 'rgba(239,68,68,.1)', fg: '#f87171', bd: 'rgba(239,68,68,.2)', text: 'Invoice Agent · conf 82.1%' },
    reviewer: 'Awaiting AP review',
    icon: 'warn',
  },
  {
    id: 'TARIFF-DRIFT',
    title: 'TARIFF-DRIFT · Texas Eastern Pipeline',
    detail: 'FERC filed rate $0.2847/Dth · Billed $0.3012/Dth · 5.8% over · 312 affected shipper lines',
    severity: 'high',
    iconBg: 'rgba(245,158,11,.15)', iconBd: 'rgba(245,158,11,.3)', iconColor: '#fbbf24',
    agentChip: { bg: 'rgba(245,158,11,.1)', fg: '#fbbf24', bd: 'rgba(245,158,11,.2)', text: 'Tariff Agent ⭐' },
    reviewer: 'Revenue team review',
    icon: 'tariff',
  },
  {
    id: 'JIB-2026-MAY',
    title: 'JIB-2026-MAY · Sweeny Hub JV',
    detail: 'AFE-2024-0882 overrun: $2.1M charged vs. $1.85M approved · $250K excess',
    severity: 'medium',
    iconBg: 'rgba(59,130,246,.15)', iconBd: 'rgba(59,130,246,.3)', iconColor: '#60a5fa',
    agentChip: { bg: 'rgba(59,130,246,.1)', fg: '#60a5fa', bd: 'rgba(59,130,246,.2)', text: 'JIB Agent ⭐' },
    reviewer: 'JV finance review',
    icon: 'jib',
  },
  {
    id: 'PO-2026-08812',
    title: 'PO-2026-08812 · Baker Hughes',
    detail: 'Tax code mismatch: TX-E (exempt) vs. TX-I (industrial) · $12,400 tax differential',
    severity: 'medium',
    iconBg: 'rgba(168,85,247,.15)', iconBd: 'rgba(168,85,247,.3)', iconColor: '#c4b5fd',
    agentChip: { bg: 'rgba(168,85,247,.1)', fg: '#c4b5fd', bd: 'rgba(168,85,247,.2)', text: 'PO Agent · conf 79.3%' },
    reviewer: 'Tax team review',
    icon: 'po',
  },
  {
    id: 'QUOTE-2026-0041',
    title: 'QUOTE-2026-0041 · Exterran Corp',
    detail: 'Confidence 74.2% — scope language ambiguous in section 3.2 · Procurement review needed',
    severity: 'low',
    iconBg: 'rgba(245,158,11,.15)', iconBd: 'rgba(245,158,11,.3)', iconColor: '#fbbf24',
    agentChip: { bg: 'rgba(245,158,11,.1)', fg: '#fbbf24', bd: 'rgba(245,158,11,.2)', text: 'Quote Agent · conf 74.2%' },
    reviewer: 'Procurement review',
    icon: 'quote',
  },
];

// ──────────────────── component ────────────────────
export function EprodCommandCenter() {
  const [clock, setClock] = useState('');
  const [feed, setFeed]   = useState<FeedLine[]>([]);
  const [feedSeeded, setFeedSeeded] = useState(false);

  // Dashboard state (single endpoint for everything below)
  const dashStateQ = useQuery<DashboardState>({
    queryKey: ['eprod-dashboard-state'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/eprod/dashboard-state`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30000, refetchOnWindowFocus: false, retry: false,
  });
  const state = dashStateQ.data;

  // HITL queue — poll backend; prepend to demo rows
  const hitlQuery = useQuery<{ count: number; items: EprodHitlItem[] }>({
    queryKey: ['eprod-hitl-pending'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/eprod/hitl/pending`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 8000, refetchOnWindowFocus: false, retry: false,
  });
  const liveHitl = hitlQuery.data?.items ?? [];
  const hitlPendingCount = liveHitl.length + HITL_SEEDS.length;

  // Seed feed once after first dashboard response
  useEffect(() => {
    if (feedSeeded) return;
    if (!state?.processing_feed) return;
    setFeed(state.processing_feed.map((e) => ({ time: e.time, html: buildFeedHtml(e) })));
    setFeedSeeded(true);
  }, [state, feedSeeded]);

  // clock
  useEffect(() => {
    const tick = () => {
      const n = new Date();
      const h = String(n.getHours()).padStart(2,'0');
      const m = String(n.getMinutes()).padStart(2,'0');
      const s = String(n.getSeconds()).padStart(2,'0');
      setClock(`${h}:${m}:${s}`);
    };
    tick(); const i = setInterval(tick, 1000); return () => clearInterval(i);
  }, []);

  // feed ticker
  useEffect(() => {
    const i = setInterval(() => {
      const now = new Date();
      const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
      const fn = LIVE_LINES[Math.floor(Math.random() * LIVE_LINES.length)];
      setFeed((prev) => [{ time, html: fn() }, ...prev].slice(0, 40));
    }, 4500);
    return () => clearInterval(i);
  }, []);

  // Derived chart data — merge docs_processed + hitl_routed onto shared day axis
  const chartData = useMemo(() => {
    if (!state?.throughput_14d) return [];
    const docs = state.throughput_14d.docs_processed;
    const hitl = state.throughput_14d.hitl_routed;
    const hitlByDate: Record<string, number> = {};
    for (const p of hitl) hitlByDate[p.date] = p.value;
    return docs.map((p, idx) => {
      // friendly label: first + last show full "May 14"; middle shows just day
      let day = p.date.slice(-2); // "DD"
      if (idx === 0 || idx === docs.length - 1) {
        const month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][parseInt(p.date.slice(5,7), 10) - 1] || '';
        day = `${month} ${day}`;
      } else {
        day = String(parseInt(day, 10));
      }
      return { day, docs: p.value, hitl: hitlByDate[p.date] ?? 0 };
    });
  }, [state]);

  return (
    <div style={{ background: '#060810', minHeight: '100vh', color: '#e2e8f0', padding: '20px 24px' }}>

      {dashStateQ.isError && (
        <div style={{
          background: 'rgba(239,68,68,.08)', border: '1px solid rgba(239,68,68,.25)',
          color: '#fca5a5', borderRadius: 10, padding: '8px 14px', fontSize: 12, marginBottom: 12,
        }}>
          Couldn’t reach /eprod/dashboard-state — using cached values
        </div>
      )}

      {/* Top bar */}
      <div style={{ background: '#0a0e1a', border: '1px solid rgba(255,255,255,.06)', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 28px', borderRadius: 12, marginBottom: 20 }}>
        <div>
          <div style={{ ...heading, fontSize: 20, fontWeight: 800, letterSpacing: '-.02em' }}>Command Center</div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 1 }}>
            Real-time document processing ops · {state?.agents?.length ?? '—'} agents active
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ ...chip('rgba(34,197,94,.1)', '#4ade80', 'rgba(34,197,94,.2)'), padding: '6px 14px', fontSize: 12 }}>
            <span style={{ ...dot('#22c55e'), animation: 'pulse 2s infinite' }} /> All Systems Nominal
          </span>
          <span style={{ ...chip('rgba(245,158,11,.1)', '#fbbf24', 'rgba(245,158,11,.2)'), padding: '6px 14px', fontSize: 12 }}>
            {hitlPendingCount} HITL Pending
          </span>
          <span style={{ ...mono, fontSize: 12, color: '#94a3b8' }}>{clock}</span>
        </div>
      </div>

      {/* Row 1: Agent Status + Live Feed */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: 20, marginBottom: 20 }}>

        {/* Agent Status */}
        <div style={panel}>
          <div style={panelHeader}>
            <div>
              <div style={{ ...heading, fontSize: 16 }}>Agent Status</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                {state?.agents?.length ?? '—'} agents · EPROD Azure tenant
              </div>
            </div>
            <span style={chip('rgba(34,197,94,.12)', '#4ade80', 'rgba(34,197,94,.25)')}>
              <span style={{ ...dot('#22c55e'), animation: 'pulse 2s infinite' }} /> All Live
            </span>
          </div>
          <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 8 }}>
            {(state?.agents ?? []).map((a) => {
              const primary = a.metrics?.[0];
              const metricStr = primary?.value ?? '—';
              const parsed = primary ? parseFloat(primary.value) : NaN;
              const pct = Number.isFinite(parsed) && parsed > 0 ? Math.min(100, parsed) : 95;
              const accent = a.accent || '#1a6db5';
              return (
                <AgentStatusBar
                  key={a.id}
                  gradient={`linear-gradient(135deg, ${accent}, ${accent})`}
                  iconPath={iconForAgentId(a.id)}
                  name={a.name + (a.starred ? ' ⭐' : '')}
                  metric={metricStr}
                  metricColor={STATUS_TONE_COLOR[primary?.tone || 'neutral'] || '#94a3b8'}
                  pct={pct}
                  fillGradient={`linear-gradient(90deg, ${accent}, ${accent}aa)`}
                  badge={(a.badge || 'LIVE').toUpperCase()}
                  badgeColor={a.badge_tone === 'amber' ? 'amber' : 'green'}
                  highlight={a.starred}
                />
              );
            })}
            {!state && [0,1,2,3,4,5].map((i) => (
              <div key={i} style={{
                height: 56, borderRadius: 10, border: '1px dashed rgba(255,255,255,.06)',
                background: 'rgba(255,255,255,.02)',
              }} />
            ))}
          </div>
        </div>

        {/* Live Processing Feed */}
        <div style={panel}>
          <div style={panelHeader}>
            <div>
              <div style={{ ...heading, fontSize: 16 }}>Live Processing Feed</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>Real-time agent activity · All document types</div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span style={{ ...dot('#ef4444'), width: 6, height: 6, animation: 'pulse 2s infinite' }} />
              <span style={{ ...mono, fontSize: 11, fontWeight: 600, color: '#f87171' }}>LIVE</span>
            </div>
          </div>
          <div style={{
            margin: 12, height: 340, overflowY: 'auto', padding: '14px 16px',
            background: '#020408', borderRadius: 10, border: '1px solid rgba(255,255,255,.05)',
            ...mono, fontSize: 13, lineHeight: 1.9,
          }}>
            {feed.map((f, i) => (
              <div key={`${f.time}-${i}`} style={{ animation: 'slideDown .25s ease forwards' }}>
                <span style={{ color: '#9ca3af' }}>{f.time}</span> <span dangerouslySetInnerHTML={{ __html: f.html }} />
              </div>
            ))}
            {feed.length === 0 && (
              <div style={{ color: '#475569' }}>Waiting for feed…</div>
            )}
          </div>
        </div>
      </div>

      {/* Row 2: HITL Queue + Tariff Diff Viewer */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>

        {/* HITL Queue */}
        <div style={panel}>
          <div style={panelHeader}>
            <div>
              <div style={{ ...heading, fontSize: 16 }}>HITL Review Queue</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>Human-in-the-loop · No autonomous write-back</div>
            </div>
            <span style={chip('rgba(245,158,11,.12)', '#fbbf24', 'rgba(245,158,11,.25)')}>
              <span style={{ ...dot('#f59e0b'), animation: 'pulse 2s infinite' }} /> {hitlPendingCount} pending
            </span>
          </div>
          <div style={{ padding: 20 }}>
            {liveHitl.map((it) => (
              <HitlRow
                key={it.request_id}
                title={it.title}
                detail={it.detail}
                severity={it.severity}
                iconBg="rgba(59,130,246,.15)" iconBd="rgba(59,130,246,.3)" iconColor="#60a5fa"
                agentChipBg="rgba(59,130,246,.1)" agentChipFg="#60a5fa" agentChipBd="rgba(59,130,246,.2)"
                agentText={it.agent}
                reviewer={it.reviewer ?? 'Awaiting review'}
                icon="warn"
              />
            ))}
            {HITL_SEEDS.map((it) => (
              <HitlRow
                key={it.id}
                title={it.title} detail={it.detail} severity={it.severity}
                iconBg={it.iconBg} iconBd={it.iconBd} iconColor={it.iconColor}
                agentChipBg={it.agentChip.bg} agentChipFg={it.agentChip.fg} agentChipBd={it.agentChip.bd}
                agentText={it.agentChip.text} reviewer={it.reviewer} icon={it.icon}
              />
            ))}
          </div>
        </div>

        {/* Tariff Rate Diff Viewer */}
        <div style={panel}>
          <div style={panelHeader}>
            <div>
              <div style={{ ...heading, fontSize: 16 }}>Tariff Rate Diff Viewer</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                {state?.tariff_diff?.header?.subtitle ?? '—'}
              </div>
            </div>
            <span style={chip('rgba(239,68,68,.12)', '#f87171', 'rgba(239,68,68,.25)')}>
              <span style={{ ...dot('#ef4444'), animation: 'pulse 2s infinite' }} />
              {' '}{state?.tariff_diff?.header?.chip ?? 'Drift Detected'}
            </span>
          </div>
          <div style={{ padding: 20 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
              <RateCard
                accentColor="#4ade80" bg="rgba(34,197,94,.06)" bd="rgba(34,197,94,.15)"
                label={state?.tariff_diff?.ferc?.label ?? 'FERC Filed Rate'}
                lines={state?.tariff_diff?.ferc ? [
                  `Tariff Sheet: ${state.tariff_diff.ferc.tariff_sheet}`,
                  `Effective: ${state.tariff_diff.ferc.effective}`,
                  `Zone: ${state.tariff_diff.ferc.zone}`,
                ] : ['—', '—', '—']}
                rate={state?.tariff_diff?.ferc?.rate_display ?? '—'}
                unit={state?.tariff_diff?.ferc?.unit ?? ''}
              />
              <RateCard
                accentColor="#f87171" bg="rgba(239,68,68,.06)" bd="rgba(239,68,68,.2)"
                label={state?.tariff_diff?.invoice?.label ?? 'Shipper Billed Rate'}
                lines={state?.tariff_diff?.invoice ? [
                  `Invoice: ${state.tariff_diff.invoice.invoice_id}`,
                  `Gas Day: ${state.tariff_diff.invoice.gas_day}`,
                  `Zone: ${state.tariff_diff.invoice.zone}`,
                ] : ['—', '—', '—']}
                rate={state?.tariff_diff?.invoice?.rate_display ?? '—'}
                unit={state?.tariff_diff?.invoice?.unit ?? ''}
              />
            </div>

            <div style={{
              background: '#020408', borderRadius: 10, padding: 14,
              border: '1px solid rgba(255,255,255,.05)',
              ...mono, fontSize: 13, lineHeight: 1.9,
            }}>
              {(state?.tariff_diff?.diff_lines ?? []).map((ln, i) => {
                if (ln.kind === 'removed') {
                  return (
                    <div key={i} style={{ background: 'rgba(239,68,68,.13)', padding: '1px 4px', borderRadius: 3, color: '#f87171', textDecoration: 'line-through' }}>
                      {ln.text}
                    </div>
                  );
                }
                if (ln.kind === 'added') {
                  return (
                    <div key={i} style={{ background: 'rgba(239,68,68,.13)', padding: '1px 4px', borderRadius: 3, color: '#f87171' }}>
                      {ln.text}
                    </div>
                  );
                }
                return <div key={i} style={{ color: '#9ca3af' }}>{ln.text}</div>;
              })}
              {state?.tariff_diff?.impact && (
                <>
                  <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid rgba(255,255,255,.06)' }}>
                    <span style={{ color: '#fbbf24' }}>
                      ⚠ IMPACT: {state.tariff_diff.impact.lines_affected} shipper lines × avg{' '}
                      {state.tariff_diff.impact.avg_dth_per_day.toLocaleString()} Dth/day ×{' '}
                      {state.tariff_diff.impact.days} days
                    </span>
                  </div>
                  <div style={{ color: '#f87171', fontWeight: 600 }}>
                    {'  '}Estimated overbilling: {formatUsd(state.tariff_diff.impact.monthly_exposure_usd)}/month if uncorrected
                  </div>
                </>
              )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 10, marginTop: 14 }}>
              {(state?.tariff_diff?.kpis ?? [
                { label: 'Rate Drift', value: '—', tone: 'bad' },
                { label: 'Affected Lines', value: '—', tone: 'warn' },
                { label: 'Monthly Exposure', value: '—', tone: 'bad' },
              ]).map((k, i) => (
                <StatBox key={i} value={k.value} label={k.label} color={STATUS_TONE_COLOR[k.tone] || '#94a3b8'} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: JIB Reconciliation + Throughput */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20 }}>

        {/* JIB Reconciliation */}
        <div style={panel}>
          <div style={panelHeader}>
            <div>
              <div style={{ ...heading, fontSize: 16 }}>JIB Statement Reconciliation ⭐</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                JIB Agent · AFE match · {state?.jib_reconciliation?.rows?.length ?? '—'} JV operators · May 2026
              </div>
            </div>
            <span style={chip('rgba(245,158,11,.12)', '#fbbf24', 'rgba(245,158,11,.25)')}>
              <span style={{ ...dot('#f59e0b'), animation: 'pulse 2s infinite' }} />
              {' '}{(state?.jib_reconciliation?.rows ?? []).filter((r) => r.tone === 'bad').length} overruns
            </span>
          </div>
          <div style={{ padding: 20 }}>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,.06)' }}>
                    <Th align="left">JV / Operator</Th>
                    <Th align="right">AFE Approved</Th>
                    <Th align="right">JIB Charged</Th>
                    <Th align="right">Variance</Th>
                    <Th align="center">Status</Th>
                  </tr>
                </thead>
                <tbody>
                  {(state?.jib_reconciliation?.rows ?? []).map((r, idx, arr) => {
                    const isBad = r.tone === 'bad';
                    const varianceSigned = (r.variance_usd >= 0 ? '+' : '') + formatUsd(r.variance_usd, { full: true });
                    return (
                      <JibRow
                        key={`${r.jv}-${idx}`}
                        jv={r.jv}
                        operator={`${r.operator} · ${r.afe}`}
                        afe={formatUsd(r.approved_usd, { full: true })}
                        charged={formatUsd(r.charged_usd, { full: true })}
                        chargedColor={isBad ? '#f87171' : '#4ade80'}
                        variance={varianceSigned}
                        varianceColor={isBad ? '#f87171' : '#4ade80'}
                        status={r.status}
                        statusColor={isBad ? 'red' : 'green'}
                        last={idx === arr.length - 1}
                      />
                    );
                  })}
                </tbody>
              </table>
            </div>
            {state?.jib_reconciliation?.callout && (
              <div style={{
                marginTop: 12, padding: '10px 14px',
                background: 'rgba(239,68,68,.06)', border: '1px solid rgba(239,68,68,.15)', borderRadius: 8,
                display: 'flex', alignItems: 'center', gap: 10,
              }}>
                <span style={{ color: '#f87171', fontSize: 16, flexShrink: 0 }}>⚠</span>
                <span style={{ fontSize: 13, color: '#f87171', fontWeight: 600 }}>
                  {state.jib_reconciliation.callout.text}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Throughput */}
        <div style={panel}>
          <div style={panelHeader}>
            <div>
              <div style={{ ...heading, fontSize: 16 }}>Processing Throughput</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>Docs processed per day · Last 14 days</div>
            </div>
            <span style={chip('rgba(6,182,212,.12)', '#22d3ee', 'rgba(6,182,212,.25)')}>
              ↑ {state?.throughput_summary?.vs_prior_pct ?? '—'}% vs prior period
            </span>
          </div>
          <div style={{ padding: 20 }}>
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 12, left: -10, bottom: 0 }}>
                  <CartesianGrid stroke="rgba(255,255,255,.04)" />
                  <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#94a3b8' }} stroke="rgba(255,255,255,.08)" />
                  <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} stroke="rgba(255,255,255,.08)" />
                  <Tooltip
                    contentStyle={{ background: '#0a0e1a', border: '1px solid rgba(255,255,255,.1)', borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: '#f9fafb' }}
                  />
                  <Legend wrapperStyle={{ fontSize: 12, color: '#cbd5e1' }} iconSize={10} />
                  <Line type="monotone" dataKey="docs" name="Docs Processed" stroke="#1a6db5" strokeWidth={2} dot={{ r: 3, fill: '#1a6db5' }} />
                  <Line type="monotone" dataKey="hitl" name="HITL Routed" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3, fill: '#f59e0b' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, marginTop: 16 }}>
              <StatBox value={state?.throughput_summary ? String(state.throughput_summary.avg_docs_per_day) : '—'} label="Docs/day avg" color="#f9fafb" big />
              <StatBox value={state?.throughput_summary ? `${state.throughput_summary.auto_approved_pct}%` : '—'} label="Auto-approved" color="#4ade80" big />
              <StatBox value={state?.throughput_summary ? `${state.throughput_summary.hitl_routed_pct}%` : '—'} label="HITL routed" color="#fbbf24" big />
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        @keyframes slideDown { from{opacity:0;transform:translateY(-4px)} to{opacity:1;transform:translateY(0)} }
      `}</style>
    </div>
  );
}

// ──────────────────── sub-components ────────────────────

function AgentStatusBar(props: {
  gradient: string; iconPath?: string;
  name: string; metric: string; metricColor: string;
  pct: number; fillGradient: string;
  badge: string; badgeColor: 'green' | 'amber';
  highlight?: boolean;
}) {
  const badgePalette = props.badgeColor === 'green'
    ? { bg: 'rgba(16,185,129,.1)', fg: '#34d399', bd: 'rgba(16,185,129,.2)' }
    : { bg: 'rgba(245,158,11,.1)', fg: '#fbbf24', bd: 'rgba(245,158,11,.2)' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '10px 14px', borderRadius: 10,
      border: `1px solid ${props.highlight ? 'rgba(245,158,11,.2)' : 'rgba(255,255,255,.06)'}`,
      background: props.highlight ? 'rgba(245,158,11,.04)' : 'rgba(255,255,255,.02)',
    }}>
      <div style={{
        width: 32, height: 32, borderRadius: 8, background: props.gradient,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        color: '#fff',
      }}>
        {props.iconPath ? (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d={props.iconPath} />
          </svg>
        ) : (
          <span style={{ fontSize: 14, fontWeight: 700 }}>{props.name.charAt(0)}</span>
        )}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>{props.name}</span>
          <span style={{ ...mono, fontSize: 12, color: props.metricColor }}>{props.metric}</span>
        </div>
        <div style={{ height: 5, borderRadius: 99, background: 'rgba(255,255,255,.06)', overflow: 'hidden', marginTop: 6 }}>
          <div style={{ height: '100%', width: `${props.pct}%`, background: props.fillGradient, borderRadius: 99 }} />
        </div>
      </div>
      <div style={{
        display: 'inline-flex', alignItems: 'center',
        fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
        padding: '3px 8px', borderRadius: 6,
        background: badgePalette.bg, color: badgePalette.fg, border: `1px solid ${badgePalette.bd}`,
      }}>
        {props.badge}
      </div>
    </div>
  );
}

function HitlRow(props: {
  title: string; detail: string;
  severity: 'high' | 'medium' | 'low';
  iconBg: string; iconBd: string; iconColor: string;
  agentChipBg: string; agentChipFg: string; agentChipBd: string;
  agentText: string; reviewer: string;
  icon: 'warn' | 'tariff' | 'jib' | 'po' | 'quote';
}) {
  const rowPalette = props.severity === 'high'
    ? { bg: 'rgba(239,68,68,.06)', bd: 'rgba(239,68,68,.2)' }
    : props.severity === 'medium'
    ? { bg: 'rgba(245,158,11,.05)', bd: 'rgba(245,158,11,.18)' }
    : { bg: 'rgba(34,197,94,.04)', bd: 'rgba(34,197,94,.15)' };
  const badge = props.severity === 'high'
    ? { bg: 'rgba(220,38,38,.1)', fg: '#f87171', bd: 'rgba(220,38,38,.2)', label: 'HIGH' }
    : props.severity === 'medium'
    ? { bg: 'rgba(245,158,11,.1)', fg: '#fbbf24', bd: 'rgba(245,158,11,.2)', label: 'MEDIUM' }
    : { bg: 'rgba(16,185,129,.1)', fg: '#34d399', bd: 'rgba(16,185,129,.2)', label: 'LOW' };
  const iconChar = props.icon === 'warn' ? '⚠'
                 : props.icon === 'tariff' ? '$'
                 : props.icon === 'jib' ? '◆'
                 : props.icon === 'po' ? '☰'
                 : '?';
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12,
      padding: '14px 16px', borderRadius: 12, marginBottom: 8,
      background: rowPalette.bg, border: `1px solid ${rowPalette.bd}`,
    }}>
      <div style={{
        width: 36, height: 36, borderRadius: 10,
        background: props.iconBg, border: `1px solid ${props.iconBd}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        color: props.iconColor, fontSize: 18, fontWeight: 700,
      }}>
        {iconChar}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>{props.title}</span>
          <span style={{
            display: 'inline-flex', alignItems: 'center',
            fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
            padding: '3px 8px', borderRadius: 6,
            background: badge.bg, color: badge.fg, border: `1px solid ${badge.bd}`,
          }}>{badge.label}</span>
        </div>
        <div style={{ fontSize: 12, color: '#cbd5e1', marginBottom: 6 }}>{props.detail}</div>
        <div style={{ display: 'flex', gap: 6 }}>
          <span style={{
            fontSize: 11, padding: '2px 8px', borderRadius: 4, fontWeight: 600,
            background: props.agentChipBg, color: props.agentChipFg, border: `1px solid ${props.agentChipBd}`,
          }}>{props.agentText}</span>
          <span style={{
            fontSize: 11, padding: '2px 8px', borderRadius: 4,
            background: 'rgba(255,255,255,.05)', color: '#cbd5e1', border: '1px solid rgba(255,255,255,.08)',
          }}>{props.reviewer}</span>
        </div>
      </div>
    </div>
  );
}

function RateCard(props: {
  accentColor: string; bg: string; bd: string;
  label: string; lines: string[];
  rate: string; unit: string;
}) {
  return (
    <div style={{ background: props.bg, border: `1px solid ${props.bd}`, borderRadius: 10, padding: 14 }}>
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: props.accentColor, marginBottom: 8 }}>
        {props.label}
      </div>
      {props.lines.map((l) => (
        <div key={l} style={{ ...mono, fontSize: 12, color: '#cbd5e1', marginBottom: 4 }}>{l}</div>
      ))}
      <div style={{ ...heading, fontSize: 24, fontWeight: 800, color: props.accentColor, marginTop: 8 }}>
        {props.rate}<span style={{ fontSize: 13, fontWeight: 500, color: '#cbd5e1' }}>{props.unit}</span>
      </div>
    </div>
  );
}

function StatBox({ value, label, color, big }: { value: string; label: string; color: string; big?: boolean }) {
  return (
    <div style={{
      textAlign: 'center', padding: 10,
      background: 'rgba(255,255,255,.03)', border: '1px solid rgba(255,255,255,.06)', borderRadius: 8,
    }}>
      <div style={{
        ...heading, fontSize: big ? 32 : 16, fontWeight: 900, color,
        ...(big ? {
          background: 'linear-gradient(135deg, #fff 0%, #d4eaff 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        } : {}),
      }}>{value}</div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{label}</div>
    </div>
  );
}

function Th({ children, align }: { children: React.ReactNode; align: 'left' | 'right' | 'center' }) {
  return (
    <th style={{
      textAlign: align, padding: '12px 14px',
      fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8',
    }}>{children}</th>
  );
}

function JibRow(props: {
  jv: string; operator: string;
  afe: string; charged: string; chargedColor: string;
  variance: string; varianceColor: string;
  status: string; statusColor: 'red' | 'green';
  last?: boolean;
}) {
  const badge = props.statusColor === 'red'
    ? { bg: 'rgba(220,38,38,.1)', fg: '#f87171', bd: 'rgba(220,38,38,.2)' }
    : { bg: 'rgba(16,185,129,.1)', fg: '#34d399', bd: 'rgba(16,185,129,.2)' };
  return (
    <tr style={{ borderBottom: props.last ? undefined : '1px solid rgba(255,255,255,.04)' }}>
      <td style={{ padding: '12px 14px', color: '#f9fafb', fontWeight: 500 }}>
        {props.jv}<br /><span style={{ fontSize: 11, color: '#94a3b8' }}>{props.operator}</span>
      </td>
      <td style={{ padding: '12px 14px', textAlign: 'right', ...mono, color: '#cbd5e1' }}>{props.afe}</td>
      <td style={{ padding: '12px 14px', textAlign: 'right', ...mono, color: props.chargedColor, fontWeight: 600 }}>{props.charged}</td>
      <td style={{ padding: '12px 14px', textAlign: 'right', ...mono, color: props.varianceColor, fontWeight: 700 }}>{props.variance}</td>
      <td style={{ padding: '12px 14px', textAlign: 'center' }}>
        <span style={{
          display: 'inline-flex', alignItems: 'center',
          fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
          padding: '3px 8px', borderRadius: 6,
          background: badge.bg, color: badge.fg, border: `1px solid ${badge.bd}`,
        }}>{props.status}</span>
      </td>
    </tr>
  );
}
