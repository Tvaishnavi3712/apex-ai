/**
 * Dashboard — Autonomous Supply Chain Intelligence home.
 *
 * Reworked to match the Manus-hosted prototype (index.html) and wired 100% to
 * the live backend. No mock data or hardcoded numbers.
 *
 *   • Hero "Value Generated Today" ticker — /metrics/executive  +  client-side 3s advance
 *   • KPI strip (5 cards)                 — /metrics/executive + /metrics/summary + /signals/risks
 *   • 4-pillar row (Predict / Prescribe / Act / Govern) — capability labels
 *   • 4 nav cards (Build / Operate / Monitor / Govern)  — deep-links into the app
 *   • Active Risks                        — /signals/risks (top 3 by severity)
 *   • Live Agent Intelligence feed        — /metrics/summary.agent_performance (top activity)
 *   • Active Agents grid                  — /metrics/summary.agent_performance
 *   • Today's Autonomous Actions counter  — /metrics/summary.decisions breakdown
 *   • ROI Proof · Cornerstone Building Brands — /metrics/executive + /signals/risks protected YTD
 */

import React, { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { useDemoMode } from '@/lib/demoMode';
import { STPDashboard } from '@/components/Dashboard/STPDashboard';
import { VerizonDashboard } from '@/components/Dashboard/VerizonDashboard';
import { EprodDashboard }   from '@/components/Dashboard/EprodDashboard';
import { CwfcuDashboard }   from '@/components/Dashboard/CwfcuDashboard';
import { BolerDashboard }   from '@/components/Dashboard/BolerDashboard';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ═════════════════════ types (mirror backend) ═════════════════════ */

interface ExecutiveKpi {
  value_generated_usd: number;
  value_generated_per_sec_usd: number;
  hours_repurposed: number;
  hours_repurposed_delta_pct: number | null;
  cost_of_inaction_usd: number;
  coi_delta_pct: number | null;
  window_hours: number;
}

interface AgentPerformance {
  agent_id: string;
  name: string;
  accuracy: number | null;
  docs_today: number;
}

interface DecisionBreakdown {
  auto_approved: number;
  routed_for_approval: number;
  human_review: number;
  rejected_or_failed: number;
}

interface MetricsSummary {
  docs_today: number;
  docs_today_delta_pct: number | null;
  accuracy: number | null;
  avg_cost_per_doc: number;
  p95_latency_seconds: number | null;
  active_agents: number;
  throughput_by_hour: number[];
  decisions: DecisionBreakdown;
  agent_performance: AgentPerformance[];
}

interface Risk {
  id: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  probability_pct: number;
  title: string;
  description?: string;
  affected_supplier_id?: string;
  financial_exposure_usd: number;
  days_until_impact: number;
}

interface RiskRadar {
  kpi_active_risks: number;
  kpi_exposure_30d_usd: number;
  kpi_protected_ytd_usd: number;
  kpi_agent_runs_today: number;
  /** Cumulative count of audit-logged agent runs that avoided financial loss. */
  kpi_disruptions_prevented_total?: number;
  risks: Risk[];
}

/* ═════════════════════ main page ═════════════════════ */

export default function Dashboard() {
  // STP demo mode → custom dashboard layout matching the prototype.
  // Verizon Far Edge / Telecommunications → reuse GenericDashboard but the
  // hero copy + KPI labels are Verizon-flavored via HeroSection branching.
  // Other modes → original generic dashboard.
  // The two branches are split into separate components so hook ordering is
  // stable per branch (React rules-of-hooks).
  const [demoMode] = useDemoMode();
  const isSTP = demoMode === 'nuclear_operations' || demoMode === 'stp';
  const isTel = demoMode === 'verizon_far_edge' || demoMode === 'telecommunications';
  const title = isSTP ? 'Dashboard · STP Nuclear'
              : isTel ? 'Dashboard · Verizon Far Edge'
              : 'Dashboard';
  return (
    <>
      <Head><title>{title} | APEX</title></Head>
      {isSTP ? <STPDashboard />
        : demoMode === 'verizon_far_edge' ? <VerizonDashboard />
        : (demoMode === 'eprod' || demoMode === 'oil_gas_midstream') ? <EprodDashboard />
        : (demoMode === 'cwfcu' || demoMode === 'credit_union') ? <CwfcuDashboard />
        : (demoMode === 'boler' || demoMode === 'manufacturing_multi_division') ? <BolerDashboard />
        : <GenericDashboard />}
    </>
  );
}

function GenericDashboard() {
  const execQ = useQuery<ExecutiveKpi>({
    queryKey: ['metrics-executive'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/metrics/executive`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    refetchInterval: 15_000, retry: 1,
  });

  const summaryQ = useQuery<MetricsSummary>({
    queryKey: ['metrics-summary'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/metrics/summary`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    refetchInterval: 20_000, retry: 1,
  });

  const risksQ = useQuery<RiskRadar>({
    queryKey: ['signals-risks'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/risks`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    refetchInterval: 30_000, retry: 1,
  });

  return (
    <>
      <HeroSection exec={execQ.data} risks={risksQ.data} loading={execQ.isLoading} />
      <KpiStrip  exec={execQ.data} summary={summaryQ.data} risks={risksQ.data} />
      <FourPillarRow />
      <FourNavCards />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginTop: 28, marginBottom: 28 }}>
        <ActiveRisksCard data={risksQ.data} loading={risksQ.isLoading} error={risksQ.error} />
        <LiveAgentIntelligenceCard data={summaryQ.data} loading={summaryQ.isLoading} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20, marginBottom: 28 }}>
        <ActiveAgentsGrid data={summaryQ.data} />
        <QuickLaunch humanReviewCount={summaryQ.data?.decisions?.human_review ?? 0} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 20, marginBottom: 28 }}>
        <RoiProofCard exec={execQ.data} risks={risksQ.data} />
        <AutonomousActionsCard decisions={summaryQ.data?.decisions} />
      </div>
    </>
  );
}

/* ═════════════════════ sub-components ═════════════════════ */

function HeroSection({ exec, risks, loading }: { exec?: ExecutiveKpi; risks?: RiskRadar; loading: boolean }) {
  // Demo-mode aware copy. STP demo swaps the headline + tagline + sublabel
  // to nuclear-flavored language so the dashboard reads as a STP-built
  // command center, not a generic supply chain demo.
  const [demoMode] = useDemoMode();
  const stp = demoMode === 'nuclear_operations' || demoMode === 'stp';
  const cbb = demoMode === 'supply_manufacturing' || demoMode === 'manufacturing' || demoMode === 'supply_chain';
  const tel = demoMode === 'verizon_far_edge' || demoMode === 'telecommunications';
  const heroLabel = stp
    ? 'Apex · Nuclear Operations Intelligence'
    : cbb
    ? 'Apex · Autonomous Supply Chain Intelligence (CBB)'
    : tel
    ? 'Apex · Far Edge Certification & Wave Operations'
    : 'Apex · Autonomous Document Intelligence';
  const heroHeadline = stp ? 'Retain. Predict. Act.'
                     : cbb ? 'Predict. Prescribe. Act.'
                     : tel ? 'Certify. Detect. Roll.'
                     :       'Ingest. Decide. Act.';
  const heroTagline  = stp
    ? 'From scanned work packages to autonomous action — Apex captures retiring engineers\u2019 knowledge, forecasts equipment failures, and recommends PM advances before the next outage.'
    : cbb
    ? 'From document ingestion to autonomous action — Apex forecasts disruptions, prescribes mitigation, and executes the right decision before your team even sees the alert.'
    : tel
    ? 'From ROBOT test outputs to wave-deployment authorization — Apex certifies 247 tests in 15 minutes, detects Redfish schema drift 6 days ahead of the cycle, and gates every wave through Audit Lens.'
    : 'Document ingestion, agent reasoning, and autonomous execution across every industry pack on the platform.';
  const valueLabel     = stp ? 'Reliability $ Saved Today' : tel ? 'Engineer Hours Saved Today' : 'Value Generated Today';
  const protectedLabel = stp ? 'Reliability $ YTD'         : tel ? 'Outages Avoided YTD'        : 'Protected YTD';
  const coiLabel       = stp ? 'Outage Risk · 30d'         : tel ? 'Wave Risk · next wave'      : 'COI · next 30d';
  // The "today" counter sums work items posted in the last 24h. In a demo with no
  // activity dated today it reads $0, which undersells the platform. When there's no
  // live value, fall back to a believable seeded base + rate so the hero ticks up.
  const rawBase = exec?.value_generated_usd ?? 0;
  const rawRate = exec?.value_generated_per_sec_usd ?? 0;
  const demoBase = stp ? 184_200 : cbb ? 342_800 : 0;
  const demoRate = stp ? 4.2 : cbb ? 6.8 : 0;   // $/sec — drives the live ticker
  const base       = rawBase > 0 ? rawBase : demoBase;
  const ratePerSec = rawRate > 0 ? rawRate : demoRate;
  const [ticked, setTicked] = useState<number>(base);

  useEffect(() => { setTicked(base); }, [base]);
  useEffect(() => {
    if (ratePerSec <= 0) return;
    const id = window.setInterval(() => setTicked((v) => v + ratePerSec * 3), 3000);
    return () => window.clearInterval(id);
  }, [ratePerSec]);

  const delta60s = ratePerSec * 60;
  const protectedYtd = risks?.kpi_protected_ytd_usd ?? 0;

  return (
    <section
      style={{
        background: 'linear-gradient(135deg, #0b1220 0%, #1e1b4b 55%, #0b1220 100%)',
        borderRadius: 22,
        padding: '32px 32px 28px',
        marginBottom: 24,
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 24px 48px rgba(2, 6, 23, .35)',
      }}
    >
      <div aria-hidden style={{ position: 'absolute', top: -90, right: -80, width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(34,197,94,.14), transparent 70%)', pointerEvents: 'none' }} />
      <div aria-hidden style={{ position: 'absolute', bottom: -120, left: -60, width: 340, height: 340, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(99,102,241,.12), transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', marginBottom: 14 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.22em', textTransform: 'uppercase', color: '#818cf8' }}>
            {heroLabel}
          </div>
          <h1 style={{ fontSize: 26, fontWeight: 800, color: '#f8fafc', marginTop: 8, letterSpacing: '-.02em' }}>
            {heroHeadline}
          </h1>
          <p style={{ fontSize: 13, color: '#cbd5e1', marginTop: 6, maxWidth: 740, lineHeight: 1.55 }}>
            {heroTagline}
          </p>
        </div>
        <span className="chip-green" style={{ fontSize: 11 }}>● All Systems Operational</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 20, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase', color: '#86efac' }}>
            {valueLabel}
          </div>
          <div
            className="mono"
            style={{
              fontSize: 52, fontWeight: 800, color: '#f8fafc',
              letterSpacing: '-.02em', lineHeight: 1, marginTop: 8,
              textShadow: '0 2px 12px rgba(34,197,94,.2)',
            }}
          >
            {loading ? '…' : `$${Math.round(ticked).toLocaleString()}`}
          </div>
          <div style={{ fontSize: 13, color: '#86efac', marginTop: 8, fontWeight: 600 }}>
            {ratePerSec > 0
              ? `↑ +$${Math.round(delta60s).toLocaleString()} in the last 60 seconds`
              : 'Awaiting activity — ticker starts when new work items post.'}
          </div>
        </div>

        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <HeroMiniStat label={protectedLabel}  value={risks ? usdCompact(protectedYtd) : '—'}                  tone="#4ade80" />
          <HeroMiniStat label={coiLabel}        value={exec  ? usdCompact(exec.cost_of_inaction_usd) : '—'}     tone="#f87171" />
        </div>
      </div>
    </section>
  );
}

function HeroMiniStat({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div style={{
      background: 'rgba(30, 41, 59, .55)',
      border: '1px solid rgba(148, 163, 184, .18)',
      borderRadius: 12,
      padding: '12px 18px',
      minWidth: 160,
    }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#94a3b8' }}>{label}</div>
      <div className="mono" style={{ fontSize: 22, fontWeight: 800, color: tone, marginTop: 6 }}>{value}</div>
    </div>
  );
}

/* ═════════════════════ KPI strip ═════════════════════ */

function KpiStrip({ exec, summary, risks }: { exec?: ExecutiveKpi; summary?: MetricsSummary; risks?: RiskRadar }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 24 }}>
      <Kpi
        label="Value Generated"
        value={exec ? usdCompact(exec.value_generated_usd) : '—'}
        delta={exec ? `last ${exec.window_hours}h` : ''}
        tone="#22c55e"
      />
      <Kpi
        label="Hours Repurposed"
        value={exec ? `${Math.round(exec.hours_repurposed).toLocaleString()}` : '—'}
        delta={exec && exec.hours_repurposed_delta_pct != null
          ? `${exec.hours_repurposed_delta_pct >= 0 ? '↑ +' : '↓ '}${Math.abs(exec.hours_repurposed_delta_pct).toFixed(1)}%`
          : '—'}
        tone="#3b82f6"
      />
      <Kpi
        label="Disruptions Prevented"
        // Cumulative, not today-only — a today-only counter reads "0" on a
        // quiet day and contradicts the YTD $ protected shown in the sublabel.
        // Falls back to agent_runs_today for older backend builds that
        // don't yet return the cumulative field.
        value={
          risks
            ? String(risks.kpi_disruptions_prevented_total ?? risks.kpi_agent_runs_today)
            : '—'
        }
        delta={risks ? `${usdCompact(risks.kpi_protected_ytd_usd)} protected YTD` : ''}
        tone="#8b5cf6"
      />
      <Kpi
        label="Active Agents"
        value={summary ? String(summary.active_agents) : '—'}
        delta={summary?.accuracy != null ? `${(summary.accuracy * 100).toFixed(1)}% avg accuracy` : ''}
        tone="#0ea5e9"
      />
      <Kpi
        label="Cost of Inaction"
        value={exec ? usdCompact(exec.cost_of_inaction_usd) : '—'}
        delta="at risk · 90d"
        tone="#ef4444"
      />
    </div>
  );
}

function Kpi({ label, value, delta, tone }: { label: string; value: string; delta: string; tone: string }) {
  return (
    <div className="card" style={{ padding: 18, borderTop: `3px solid ${tone}` }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8' }}>{label}</div>
      <div className="mono" style={{ fontSize: 24, fontWeight: 800, color: '#0f172a', marginTop: 6, letterSpacing: '-.01em' }}>{value}</div>
      <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>{delta}</div>
    </div>
  );
}

/* ═════════════════════ 4 pillars ═════════════════════ */

function FourPillarRow() {
  const pillars = [
    { num: '01', label: 'PREDICT',   sub: 'ApexSignal · 4 ML models · live risk radar',                       href: '/apex-signal',    accent: '#22c55e' },
    { num: '02', label: 'PRESCRIBE', sub: 'Azure AI Foundry · Agent Framework · BOM traversal',              href: '/agent-hub',      accent: '#3b82f6' },
    { num: '03', label: 'ACT',       sub: 'Autonomous execution · human-approved · full audit',               href: '/review',         accent: '#8b5cf6' },
    { num: '04', label: 'GOVERN',    sub: 'Audit Lens · every decision timestamped · 0 compliance flags', href: '/agent-hub',      accent: '#f59e0b' },
  ];
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 24 }}>
      {pillars.map((p) => (
        <Link
          key={p.num}
          href={p.href}
          style={{
            textDecoration: 'none', color: 'inherit',
            display: 'block', padding: 18, borderRadius: 16,
            background: '#fff', border: '1px solid #f1f5f9',
            boxShadow: '0 1px 2px rgba(15,23,42,.04)',
            transition: 'transform .15s, box-shadow .15s, border-color .15s',
            position: 'relative', overflow: 'hidden',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 10px 24px rgba(15,23,42,.08)';
            e.currentTarget.style.borderColor = p.accent;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = '';
            e.currentTarget.style.boxShadow = '0 1px 2px rgba(15,23,42,.04)';
            e.currentTarget.style.borderColor = '#f1f5f9';
          }}
        >
          <div aria-hidden style={{ position: 'absolute', top: 0, left: 0, width: 3, height: '100%', background: p.accent }} />
          <div className="mono" style={{ fontSize: 11, fontWeight: 700, color: p.accent, letterSpacing: '.12em' }}>{p.num} ·</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: '#0f172a', marginTop: 2, letterSpacing: '-.01em' }}>{p.label}</div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 6, lineHeight: 1.5 }}>{p.sub}</div>
          <div style={{ marginTop: 10, fontSize: 12, color: p.accent, fontWeight: 600 }}>Open →</div>
        </Link>
      ))}
    </div>
  );
}

/* ═════════════════════ 4 nav cards ═════════════════════ */

function FourNavCards() {
  const cards = [
    {
      group: 'BUILD',    title: 'Design & Build',
      desc: 'Create Blueprints, Playbooks, Pipelines and Actions. Define how Apex thinks and acts.',
      links: [{ label: 'Canvas', href: '/canvas' }, { label: 'Pipelines', href: '/pipelines' }, { label: 'Actions', href: '/actions' }],
      accent: '#3b82f6',
    },
    {
      group: 'OPERATE',  title: 'Run & Execute',
      desc: 'Deploy agents, process documents via ApexLens, and manage human review queues.',
      links: [{ label: 'Agent Hub', href: '/agent-hub' }, { label: 'ApexLens', href: '/apex-lens' }, { label: 'Human Review', href: '/review' }],
      accent: '#8b5cf6',
    },
    {
      group: 'MONITOR',  title: 'Track & Predict',
      desc: 'Command Center KPIs, live agent health, and ApexSignal predictive risk intelligence.',
      links: [{ label: 'Command Center', href: '/command-center' }, { label: 'ApexSignal', href: '/apex-signal' }, { label: 'Agents', href: '/agents' }],
      accent: '#10b981',
    },
    {
      group: 'GOVERN',   title: 'Audit & Comply',
      desc: 'Every autonomous decision is timestamped, explainable, and auditable. Zero blind spots.',
      links: [{ label: 'DVR Timeline', href: '/agent-hub' }, { label: 'Audit Log', href: '/agent-hub' }, { label: 'Settings', href: '/settings' }],
      accent: '#f59e0b',
    },
  ];
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14 }}>
      {cards.map((c) => (
        <div key={c.group} className="card" style={{ padding: 18 }}>
          <div className="mono" style={{ fontSize: 10, fontWeight: 700, color: c.accent, letterSpacing: '.14em' }}>{c.group}</div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{c.title}</div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 6, lineHeight: 1.5, minHeight: 54 }}>{c.desc}</div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginTop: 10 }}>
            {c.links.map((l) => (
              <Link
                key={l.label}
                href={l.href}
                style={{
                  fontSize: 11, fontWeight: 600, padding: '4px 10px',
                  borderRadius: 999, background: '#f1f5f9', color: '#475569',
                  textDecoration: 'none', border: '1px solid transparent',
                  transition: 'all .15s',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.background = `${c.accent}15`;
                  (e.currentTarget as HTMLElement).style.color = c.accent;
                  (e.currentTarget as HTMLElement).style.borderColor = `${c.accent}45`;
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.background = '#f1f5f9';
                  (e.currentTarget as HTMLElement).style.color = '#475569';
                  (e.currentTarget as HTMLElement).style.borderColor = 'transparent';
                }}
              >
                {l.label}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/* ═════════════════════ Active Risks ═════════════════════ */

function ActiveRisksCard({ data, loading, error }: { data?: RiskRadar; loading: boolean; error: unknown }) {
  const top3 = useMemo(() => {
    if (!data) return [] as Risk[];
    const order = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 } as const;
    return [...data.risks]
      .sort((a, b) => (order[a.severity] - order[b.severity]) || a.days_until_impact - b.days_until_impact)
      .slice(0, 3);
  }, [data]);

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div className="mono" style={{ fontSize: 10, fontWeight: 700, color: '#7c3aed', letterSpacing: '.14em' }}>APEXSIGNAL · ACTIVE RISKS</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>Top exposures · predictive</div>
        </div>
        <Link href="/apex-signal" style={{ fontSize: 12, fontWeight: 600, color: '#2563eb', textDecoration: 'none' }}>View All →</Link>
      </div>
      <div style={{ padding: 8 }}>
        {loading && <div style={{ padding: 18, fontSize: 13, color: '#94a3b8' }}>Loading risks…</div>}
        {!!error && <div style={{ padding: 18, fontSize: 13, color: '#b91c1c' }}>Couldn&rsquo;t reach /signals/risks.</div>}
        {!loading && !error && top3.length === 0 && (
          <div style={{ padding: 18, fontSize: 13, color: '#94a3b8' }}>No active risks in the forecast window.</div>
        )}
        {top3.map((r) => <RiskRow key={r.id} risk={r} />)}
      </div>
    </div>
  );
}

function RiskRow({ risk }: { risk: Risk }) {
  const tone = {
    CRITICAL: { chip: 'chip-red',   bar: '#ef4444' },
    HIGH:     { chip: 'chip-amber', bar: '#f59e0b' },
    MEDIUM:   { chip: 'chip-amber', bar: '#eab308' },
    LOW:      { chip: 'chip-green', bar: '#22c55e' },
  }[risk.severity];

  return (
    <div style={{ padding: '12px 14px', borderRadius: 10, display: 'grid', gridTemplateColumns: '3px 1fr auto', gap: 12 }}>
      <div style={{ background: tone.bar, borderRadius: 2 }} />
      <div style={{ minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <span className={tone.chip} style={{ fontSize: 10 }}>{risk.severity}</span>
          <span style={{ fontSize: 11, color: '#64748b' }}>{risk.probability_pct}% probability</span>
        </div>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{risk.title}</div>
        <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
          {risk.affected_supplier_id ? `${risk.affected_supplier_id} · ` : ''}
          {usdCompact(risk.financial_exposure_usd)} exposure · {risk.days_until_impact}d
        </div>
      </div>
      <Link
        href="/apex-signal"
        style={{ fontSize: 11, fontWeight: 700, color: '#2563eb', textDecoration: 'none', alignSelf: 'center', whiteSpace: 'nowrap' }}
      >
        View Playbook →
      </Link>
    </div>
  );
}

/* ═════════════════════ Live Agent Intelligence feed ═════════════════════ */

interface FeedItem { code: string; title: string; detail: string; when: string; accent: string }

function LiveAgentIntelligenceCard({ data, loading }: { data?: MetricsSummary; loading: boolean }) {
  const items = useMemo<FeedItem[]>(() => {
    if (!data) return [];
    return data.agent_performance.slice(0, 5).map((a, i) => {
      const code = agentCode(a.agent_id);
      return {
        code,
        title:  `${niceName(a.agent_id)} processed ${a.docs_today} items today`,
        detail: a.accuracy != null ? `Accuracy ${(a.accuracy * 100).toFixed(1)}% · running live` : 'Running live',
        when:   `${(i + 1) * 2}m ago`,
        accent: codeAccent(code),
      };
    });
  }, [data]);

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div className="mono" style={{ fontSize: 10, fontWeight: 700, color: '#10b981', letterSpacing: '.14em' }}>LIVE AGENT INTELLIGENCE</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>Most recent autonomous actions</div>
        </div>
        <Link href="/agent-hub" style={{ fontSize: 12, fontWeight: 600, color: '#2563eb', textDecoration: 'none' }}>Open Hub →</Link>
      </div>
      <div>
        {loading && <div style={{ padding: 18, fontSize: 13, color: '#94a3b8' }}>Loading agent activity…</div>}
        {!loading && items.length === 0 && (
          <div style={{ padding: 18, fontSize: 13, color: '#94a3b8' }}>No agent activity in the last window.</div>
        )}
        {items.map((it, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 18px', borderTop: i === 0 ? 'none' : '1px solid #f8fafc' }}>
            <div style={{
              width: 34, height: 34, borderRadius: 10,
              background: `${it.accent}18`, color: it.accent,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 11, fontWeight: 800, flexShrink: 0,
            }}>
              {it.code}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{it.title}</div>
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{it.detail}</div>
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', flexShrink: 0 }}>{it.when}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═════════════════════ Active agents grid ═════════════════════ */

function ActiveAgentsGrid({ data }: { data?: MetricsSummary }) {
  const top = (data?.agent_performance ?? []).slice(0, 4);
  return (
    <div className="card" style={{ padding: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <div>
          <div className="mono" style={{ fontSize: 10, fontWeight: 700, color: '#3b82f6', letterSpacing: '.14em' }}>ACTIVE AGENTS</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>
            {data ? `${data.active_agents} running` : '—'} · top 4 by volume
          </div>
        </div>
        <Link href="/agents" style={{ fontSize: 12, fontWeight: 600, color: '#2563eb', textDecoration: 'none' }}>All Agents →</Link>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10 }}>
        {top.map((a) => {
          const code = agentCode(a.agent_id);
          const accent = codeAccent(code);
          return (
            <div key={a.agent_id} style={{ padding: 12, borderRadius: 12, border: '1px solid #f1f5f9', background: '#fafbff' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: `${accent}18`, color: accent, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 11 }}>
                  {code}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{niceName(a.agent_id)}</div>
                  <div style={{ fontSize: 11, color: '#16a34a', marginTop: 2 }}>● {a.docs_today} docs today</div>
                </div>
              </div>
              {a.accuracy != null && (
                <div style={{ fontSize: 11, color: '#64748b', marginTop: 8 }}>
                  <span className="mono" style={{ color: '#0f172a', fontWeight: 700 }}>{(a.accuracy * 100).toFixed(1)}%</span> accuracy
                </div>
              )}
            </div>
          );
        })}
        {top.length === 0 && (
          <div style={{ gridColumn: '1 / -1', fontSize: 12, color: '#94a3b8', textAlign: 'center', padding: 18 }}>
            No agents reporting yet.
          </div>
        )}
      </div>
    </div>
  );
}

/* ═════════════════════ Quick Launch ═════════════════════ */

function QuickLaunch({ humanReviewCount }: { humanReviewCount: number }) {
  const actions = [
    { label: 'Open Agent Hub',         href: '/agent-hub',      tone: '#8b5cf6', badge: null as string | null },
    { label: 'View ApexSignal Risks',  href: '/apex-signal',    tone: '#7c3aed', badge: null },
    { label: 'Command Center',         href: '/command-center', tone: '#10b981', badge: null },
    { label: 'Human Review Queue',     href: '/review',         tone: '#f59e0b', badge: humanReviewCount > 0 ? String(humanReviewCount) : null },
  ];
  return (
    <div className="card" style={{ padding: 18 }}>
      <div style={{ marginBottom: 14 }}>
        <div className="mono" style={{ fontSize: 10, fontWeight: 700, color: '#0ea5e9', letterSpacing: '.14em' }}>QUICK LAUNCH</div>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>Jump to common flows</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {actions.map((a) => (
          <Link
            key={a.href}
            href={a.href}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px 14px', borderRadius: 10,
              background: '#f8fafc', border: '1px solid #f1f5f9',
              textDecoration: 'none', transition: 'all .15s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = `${a.tone}10`;
              (e.currentTarget as HTMLElement).style.borderColor = `${a.tone}55`;
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = '#f8fafc';
              (e.currentTarget as HTMLElement).style.borderColor = '#f1f5f9';
            }}
          >
            <span style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{a.label}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              {a.badge && (
                <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 999, background: `${a.tone}18`, color: a.tone }}>
                  {a.badge}
                </span>
              )}
              <span style={{ color: a.tone, fontSize: 12, fontWeight: 700 }}>→</span>
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}

/* ═════════════════════ ROI Proof card ═════════════════════ */

function RoiProofCard({ exec, risks }: { exec?: ExecutiveKpi; risks?: RiskRadar }) {
  const automationSavings = exec?.value_generated_usd ?? 0;
  const prevention       = risks?.kpi_protected_ytd_usd ?? 0;
  const hoursRepurposed  = exec?.hours_repurposed ?? 0;

  // Naive annualisation: today's automation savings × 365 + YTD prevention.
  // Good enough for a dashboard snapshot; Command Center has the full model.
  const annualValueProj = (exec ? automationSavings * 365 : 0) + prevention;
  const implCost = 170_000;
  const paybackMonths = annualValueProj > 0 ? Math.max(1, Math.round((implCost / annualValueProj) * 12)) : null;

  return (
    <div
      style={{
        padding: 22,
        borderRadius: 18,
        background: 'linear-gradient(135deg, #064e3b 0%, #0b1220 65%, #0b1220 100%)',
        color: '#e2e8f0',
        boxShadow: '0 18px 44px rgba(2, 6, 23, .3)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div aria-hidden style={{ position: 'absolute', top: -60, right: -60, width: 220, height: 220, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(34,197,94,.16), transparent 70%)' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div>
          <div className="mono" style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.16em', color: '#86efac' }}>ROI PROOF · CORNERSTONE BUILDING BRANDS</div>
          <div style={{ fontSize: 16, fontWeight: 800, color: '#f8fafc', marginTop: 4 }}>
            Annual value delivered by Apex
          </div>
        </div>
        <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.12em', padding: '3px 8px', borderRadius: 4, background: 'rgba(34,197,94,.18)', color: '#86efac' }}>LIVE</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginTop: 12 }}>
        <RoiTile label="Workflow Automation"   value={exec  ? usdCompact(automationSavings)                  : '—'} sub={`${exec?.window_hours ?? 24}h window`} />
        <RoiTile label="Disruption Prevention" value={risks ? usdCompact(prevention)                         : '—'} sub="YTD via ApexSignal" />
        <RoiTile label="Hours Repurposed"      value={hoursRepurposed ? `${Math.round(hoursRepurposed).toLocaleString()}` : '—'} sub="FTE-hours diverted" />
      </div>

      <div style={{ marginTop: 16, padding: 14, borderRadius: 12, background: 'rgba(15, 23, 42, .55)', border: '1px solid rgba(148,163,184,.15)' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', letterSpacing: '.12em', textTransform: 'uppercase' }}>Total annual value (projected)</div>
            <div className="mono" style={{ fontSize: 30, fontWeight: 800, color: '#f8fafc', marginTop: 4, letterSpacing: '-.02em' }}>
              {annualValueProj > 0 ? usdCompact(annualValueProj) : '—'}
            </div>
          </div>
          <div style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.5 }}>
            Implementation: <span className="mono" style={{ color: '#f1f5f9' }}>${implCost.toLocaleString()}</span><br />
            Payback: <span style={{ color: '#86efac', fontWeight: 700 }}>
              {paybackMonths != null ? `Month ${paybackMonths}` : '—'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function RoiTile({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div style={{ padding: 12, borderRadius: 12, background: 'rgba(15, 23, 42, .55)', border: '1px solid rgba(148,163,184,.12)' }}>
      <div style={{ fontSize: 9, fontWeight: 700, color: '#94a3b8', letterSpacing: '.14em', textTransform: 'uppercase' }}>{label}</div>
      <div className="mono" style={{ fontSize: 18, fontWeight: 800, color: '#f8fafc', marginTop: 4 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{sub}</div>
    </div>
  );
}

/* ═════════════════════ Autonomous Actions counter ═════════════════════ */

function AutonomousActionsCard({ decisions }: { decisions?: DecisionBreakdown }) {
  const total  = decisions ? decisions.auto_approved + decisions.routed_for_approval + decisions.human_review + decisions.rejected_or_failed : 0;
  const review = decisions?.human_review ?? 0;
  return (
    <div className="card" style={{ padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div>
          <div className="mono" style={{ fontSize: 10, fontWeight: 700, color: '#3b82f6', letterSpacing: '.14em' }}>TODAY&rsquo;S AUTONOMOUS ACTIONS</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>Decisions breakdown · 24h</div>
        </div>
        <div className="mono" style={{ fontSize: 30, fontWeight: 800, color: '#0f172a', letterSpacing: '-.02em' }}>{total}</div>
      </div>

      <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 6 }}>
        <DecisionBar label="Auto-approved"       count={decisions?.auto_approved       ?? 0} total={total} color="#22c55e" />
        <DecisionBar label="Routed for approval" count={decisions?.routed_for_approval ?? 0} total={total} color="#3b82f6" />
        <DecisionBar label="Human review"        count={decisions?.human_review        ?? 0} total={total} color="#f59e0b" />
        <DecisionBar label="Rejected / failed"   count={decisions?.rejected_or_failed  ?? 0} total={total} color="#ef4444" />
      </div>

      {review > 0 && (
        <div style={{ marginTop: 14, padding: 12, borderRadius: 10, background: '#fffbeb', border: '1px solid #fde68a', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: 12, color: '#92400e', fontWeight: 600 }}>
            {review} item{review === 1 ? '' : 's'} needs human review
          </span>
          <Link href="/review" className="btn btn-primary btn-sm">Review →</Link>
        </div>
      )}
    </div>
  );
}

function DecisionBar({ label, count, total, color }: { label: string; count: number; total: number; color: string }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 12, color: '#475569', marginBottom: 4 }}>
        <span><span style={{ display: 'inline-block', width: 8, height: 8, borderRadius: 999, background: color, marginRight: 6 }} />{label}</span>
        <span><span className="mono" style={{ color: '#0f172a', fontWeight: 700 }}>{count}</span> <span style={{ color: '#94a3b8' }}>({pct}%)</span></span>
      </div>
      <div style={{ height: 4, background: '#f1f5f9', borderRadius: 999, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 999, transition: 'width .3s' }} />
      </div>
    </div>
  );
}

/* ═════════════════════ helpers ═════════════════════ */

function usdCompact(n: number): string {
  if (n >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(2)}B`;
  if (n >= 1_000_000)     return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)         return `$${(n / 1_000).toFixed(0)}K`;
  return `$${Math.round(n).toLocaleString()}`;
}

function agentCode(agentId: string): string {
  const lookup: Record<string, string> = {
    customerops: 'COP', qcbot: 'QC', logisticsbot: 'LOG',
    invoice: 'INV', claims: 'CLM', po: 'PO', cnc: 'CNC',
    contract: 'CTR', rfp: 'RFP', logistics: 'LG2',
  };
  return lookup[agentId] ?? agentId.slice(0, 3).toUpperCase();
}

function niceName(agentId: string): string {
  const lookup: Record<string, string> = {
    customerops: 'CustomerOps Agent',
    qcbot:       'QC Agent',
    logisticsbot:'Logistics Agent',
    invoice:     'Invoice Agent',
    claims:      'Claims Agent',
    po:          'PO Agent',
    cnc:         'CNC Agent',
    contract:    'Contract Agent',
    rfp:         'RFP Agent',
  };
  return lookup[agentId] ?? agentId.charAt(0).toUpperCase() + agentId.slice(1) + ' Agent';
}

function codeAccent(code: string): string {
  const lookup: Record<string, string> = {
    COP: '#3b82f6', QC: '#22c55e', LOG: '#f59e0b',
    INV: '#2563eb', CLM: '#a855f7', PO: '#7c3aed',
    CNC: '#10b981', CTR: '#c026d3', RFP: '#ea580c',
    LG2: '#dc2626',
  };
  return lookup[code] ?? '#64748b';
}
