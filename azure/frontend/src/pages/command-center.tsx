/**
 * Command Center — KPIs, throughput, agent performance, activity & decisions.
 * Ported from apex-prototype 2/command-center.html.
 *
 * Data: attempts to fetch real metrics; falls back to HTML mock values.
 */

import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { useQuery } from '@tanstack/react-query';
import { useDemoMode } from '@/lib/demoMode';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
  AreaChart, Area,
} from 'recharts';
import { DataSourceBanner, type DataSource } from '@/components/AppShell/DataSourceBanner';
import { STPCommandCenter } from '@/components/Dashboard/STPCommandCenter';
import { VerizonCommandCenter } from '@/components/Dashboard/VerizonCommandCenter';
import { EprodCommandCenter }   from '@/components/Dashboard/EprodCommandCenter';
import { CwfcuCommandCenter }   from '@/components/Dashboard/CwfcuCommandCenter';
import { BolerCommandCenter }   from '@/components/Dashboard/BolerCommandCenter';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Heights (%) for the 24 throughput bars — from the HTML.
const BAR_HEIGHTS = [28, 32, 37, 33, 41, 45, 48, 53, 52, 56, 61, 64, 69, 75, 72, 79, 83, 87, 85, 91, 93, 92, 95, 100];

function barColor(i: number): string {
  if (i < 2)  return '#bfdbfe';
  if (i < 4)  return '#93c5fd';
  if (i < 6)  return '#60a5fa';
  if (i < 8)  return '#3b82f6';
  if (i < 10) return '#2563eb';
  if (i < 12) return '#1d4ed8';
  if (i < 14) return '#1e40af';
  return '#1e3a8a';
}

/** Response shape from GET /api/v1/metrics/summary (see backend/api/metrics.py). */
interface DecisionBreakdown {
  auto_approved: number;
  routed_for_approval: number;
  human_review: number;
  rejected_or_failed: number;
}

interface AgentPerformance {
  agent_id: string;
  name: string;
  accuracy: number | null;
  docs_today: number;
}

interface MetricsSummary {
  docs_today: number;
  docs_today_delta_pct: number | null;
  accuracy: number | null;                  // 0..1
  accuracy_delta_pct: number | null;
  avg_cost_per_doc: number;
  avg_cost_delta_pct: number | null;
  p95_latency_seconds: number | null;
  p95_latency_delta_seconds: number | null;
  active_agents: number;
  throughput_by_hour: number[];             // length 24
  decisions: DecisionBreakdown;
  agent_performance: AgentPerformance[];
}

const fmtDelta = (pct: number | null, invert = false, unit = '%'): string => {
  if (pct === null || pct === undefined) return '—';
  const up = pct >= 0;
  const arrow = up ? '↑' : '↓';
  const sign = up ? '+' : '';
  return `${arrow} ${sign}${pct.toFixed(1)}${unit}`;
};

const deltaColor = (pct: number | null, invert = false): string => {
  if (pct === null || pct === undefined) return '#64748b';
  const good = invert ? pct < 0 : pct >= 0;
  return good ? '#16a34a' : '#d97706';
};

export default function CommandCenter() {
  // STP demo mode → custom STPCommandCenter layout matching the prototype.
  // Other modes → original generic command center.
  // Branches are split so hook ordering is stable per branch (rules-of-hooks).
  const [demoMode] = useDemoMode();
  const isSTP  = demoMode === 'nuclear_operations' || demoMode === 'stp';
  const isVZ   = demoMode === 'verizon_far_edge';
  const isEprod = demoMode === 'eprod' || demoMode === 'oil_gas_midstream';
  const isCwfcu = demoMode === 'cwfcu' || demoMode === 'credit_union';
  const isBoler = demoMode === 'boler' || demoMode === 'manufacturing_multi_division';
  const title = isSTP   ? 'Command Center · STP Nuclear'
              : isVZ    ? 'Command Center · Verizon Far Edge'
              : isEprod ? 'Command Center · EPROD'
              : isCwfcu ? 'Command Center · CommunityWide FCU'
              : isBoler ? 'Command Center · The Boler Company'
              : 'Command Center';
  return (
    <>
      <Head><title>{title} | APEX</title></Head>
      {isSTP   ? <STPCommandCenter />
        : isVZ    ? <VerizonCommandCenter />
        : isEprod ? <EprodCommandCenter />
        : isCwfcu ? <CwfcuCommandCenter />
        : isBoler ? <BolerCommandCenter />
        : <GenericCommandCenter />}
    </>
  );
}

function GenericCommandCenter() {
  const [demoMode] = useDemoMode();
  const isSTP = demoMode === 'nuclear_operations' || demoMode === 'stp';
  const isCBB = demoMode === 'supply_manufacturing' || demoMode === 'manufacturing' || demoMode === 'supply_chain';

  const q = useQuery<{ data: MetricsSummary | null; source: DataSource }>({
    queryKey: ['metrics-summary'],
    queryFn: async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/metrics/summary`);
        if (r.ok) {
          const j: MetricsSummary = await r.json();
          // Only count as live data if there's at least some activity to show.
          const hasData = j.docs_today > 0 || j.active_agents > 0 || j.throughput_by_hour.some((v) => v > 0);
          return { data: j, source: (hasData ? 'api' : 'mock') as DataSource };
        }
      } catch { /* fall through */ }
      return { data: null, source: 'mock' as DataSource };
    },
    retry: 0,
  });

  const data = q.data?.data ?? null;
  const source: DataSource = q.isLoading ? 'loading' : (q.data?.source ?? 'mock');

  // CBB demo KPI values per execution plan §3.7. When a live /metrics/summary
  // API is wired up, the data?.* branches still win; otherwise the CBB numbers
  // drive the executive dashboard during the meeting.
  const totalActions     = data ? data.docs_today.toLocaleString() : '14,204';
  const actionsDelta     = data ? fmtDelta(data.docs_today_delta_pct) + ' vs yesterday' : '↑ +12% this week';
  const actionsColor     = data ? deltaColor(data.docs_today_delta_pct) : '#16a34a';

  const accuracyKpi      = data?.accuracy != null ? `${(data.accuracy * 100).toFixed(1)}%` : '99.4%';
  const accDelta         = data ? fmtDelta(data.accuracy_delta_pct, false, 'pt') + ' (7-day avg)' : '↑ +0.2% this week';
  const accColor         = data ? deltaColor(data.accuracy_delta_pct) : '#16a34a';

  const hoursSavedKpi    = data?.p95_latency_seconds != null ? `${data.p95_latency_seconds.toFixed(1)}s` : '4,102 hrs';
  const hoursSavedLabel  = data?.p95_latency_seconds != null ? 'P95 Latency' : 'Human Hours Saved';
  const hoursSavedDelta  = data?.p95_latency_delta_seconds != null
    ? `${data.p95_latency_delta_seconds >= 0 ? '↑ +' : '↓ '}${data.p95_latency_delta_seconds.toFixed(1)}s (watch)`
    : '↑ +8% this week';
  const hoursSavedColor  = data?.p95_latency_delta_seconds != null && data.p95_latency_delta_seconds > 0 ? '#d97706' : '#16a34a';

  const costSavingsKpi   = data ? `$${data.avg_cost_per_doc.toFixed(2)}` : '$314,500';
  const costSavingsLabel = data ? 'Avg Cost / Doc' : 'Est. Cost Savings';
  const costSavingsDelta = data ? fmtDelta(data.avg_cost_delta_pct, true) + ' vs last week' : '↑ +18% this month';
  const costSavingsColor = data ? deltaColor(data.avg_cost_delta_pct, true) : '#16a34a';

  return (
    <>
      <DataSourceBanner
        source={source}
        entity="metrics"
        hint={source === 'mock'
          ? 'Metrics are computed from work_items. Post a work item or seed playbooks to see live numbers.'
          : undefined}
      />

      {/* FEATURE 1 — ROI Command Center (dark exec block) */}
      <RoiCommandCenter />

      {/* KPI strip — CBB demo defaults per spec §3.7; live API data overrides when present */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        <Kpi topColor="#3b82f6" label="Total Automated Actions" value={totalActions}   delta={actionsDelta}     deltaColor={actionsColor}     icon="chart"        iconColor="#3b82f6" />
        <Kpi topColor="#22c55e" label={hoursSavedLabel}         value={hoursSavedKpi}  delta={hoursSavedDelta}  deltaColor={hoursSavedColor}  icon="refresh"      iconColor="#22c55e" />
        <Kpi topColor="#8b5cf6" label="Accuracy Rate"           value={accuracyKpi}    delta={accDelta}         deltaColor={accColor}         icon="check_circle" iconColor="#8b5cf6" />
        <Kpi topColor="#f59e0b" label={costSavingsLabel}        value={costSavingsKpi} delta={costSavingsDelta} deltaColor={costSavingsColor} icon="info"         iconColor="#f59e0b" />
      </div>

      {/* Charts row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 20, marginBottom: 20 }}>
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Throughput · docs/hr</div>
              <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 2 }}>Last 24 hours</div>
            </div>
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="tab active" style={{ fontSize: 11, padding: '4px 10px' }}>24h</button>
              <button className="tab" style={{ fontSize: 11, padding: '4px 10px' }}>7d</button>
              <button className="tab" style={{ fontSize: 11, padding: '4px 10px' }}>30d</button>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 100 }}>
            {(() => {
              const series = data?.throughput_by_hour?.length === 24 ? data.throughput_by_hour : null;
              const max = series ? Math.max(1, ...series) : 100;
              const heights = series ? series.map((v) => Math.max(4, Math.round((v / max) * 100))) : BAR_HEIGHTS;
              return heights.map((h, i) => (
                <div key={i} className="sparkline-bar" style={{ flex: 1, background: barColor(i), height: `${h}%` }} />
              ));
            })()}
          </div>
          <div className="mono" style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6, fontSize: 11, color: '#94a3b8' }}>
            <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>now</span>
          </div>
        </div>

        <div className="card" style={{ padding: 24 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Agent Performance</div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 20 }}>Accuracy by agent</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {(() => {
              // Demo-mode aware: filter live agent_performance to the active
              // domain when possible. Falls back to demo-aware sample rows.
              const allPerf = data?.agent_performance ?? [];
              const inDomain = (name: string): boolean => {
                const n = (name || '').toLowerCase();
                if (isSTP) return n.includes('chatstp') || n.endsWith('agent');
                if (isCBB) return /customer|qc|logistic|po|cnc|workorder|contract|rfp/.test(n);
                return true;
              };
              const filtered = allPerf
                .filter((a) => a.accuracy !== null)
                .filter((a) => inDomain(a.name))
                .slice(0, 4);
              if (filtered.length > 0) {
                return filtered.map((a) => {
                  const pct = (a.accuracy ?? 0) * 100;
                  const warn = pct < 95;
                  return (
                    <PerfRow
                      key={a.agent_id}
                      name={a.name}
                      pct={pct}
                      color={warn ? '#f59e0b' : '#22c55e'}
                      deltaColor={warn ? '#d97706' : undefined}
                    />
                  );
                });
              }
              // No live data → demo-aware fallback rows.
              if (isSTP) {
                return (
                  <>
                    <PerfRow name="ChatSTP"            pct={96.1} color="#22c55e" />
                    <PerfRow name="PolicyAgent"        pct={99.0} color="#22c55e" />
                    <PerfRow name="MaintenanceAgent"   pct={97.4} color="#22c55e" />
                    <PerfRow name="ReliabilityAgent"   pct={91.8} color="#f59e0b" deltaColor="#d97706" />
                  </>
                );
              }
              if (isCBB) {
                return (
                  <>
                    <PerfRow name="CustomerOps"   pct={97.4} color="#22c55e" />
                    <PerfRow name="QC Agent"      pct={96.7} color="#22c55e" />
                    <PerfRow name="Logistics"     pct={95.4} color="#22c55e" />
                    <PerfRow name="POBot"         pct={94.2} color="#f59e0b" deltaColor="#d97706" />
                  </>
                );
              }
              return (
                <>
                  <PerfRow name="InvoiceBot"  pct={97.2} color="#22c55e" />
                  <PerfRow name="ClaimsBot"   pct={95.8} color="#22c55e" />
                  <PerfRow name="RFPBot"      pct={88.4} color="#f59e0b" deltaColor="#d97706" />
                  <PerfRow name="CNCBot"      pct={96.1} color="#22c55e" />
                </>
              );
            })()}
          </div>
        </div>
      </div>

      {/* CBB Executive Charts — spec §3.7 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* 1 — Actions by Workflow (horizontal bar) */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Actions by Workflow</div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 16 }}>30-day totals · CBB production</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={[
                { name: 'Order Mods',         value: 4821, fill: '#3b82f6' },
                { name: 'QC Checks',          value: 6102, fill: '#8b5cf6' },
                { name: 'BOM Traversals',     value: 1204, fill: '#f59e0b' },
                { name: 'Sentiment Triage',   value: 2077, fill: '#22c55e' },
              ]}
              layout="vertical"
              margin={{ top: 4, right: 24, bottom: 4, left: 16 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: '#334155' }} width={120} />
              <Tooltip
                formatter={(v: number) => v.toLocaleString()}
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={22} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 2 — Escalation Rate Trend (line) */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Escalation Rate Trend</div>
            <span className="chip-green" style={{ fontSize: 11 }}>▼ 11pt · 8 weeks</span>
          </div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 16 }}>% of actions escalated to humans</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart
              data={[
                { week: 'W1', rate: 15 },
                { week: 'W2', rate: 13 },
                { week: 'W3', rate: 12 },
                { week: 'W4', rate: 10 },
                { week: 'W5', rate: 8 },
                { week: 'W6', rate: 6 },
                { week: 'W7', rate: 5 },
                { week: 'W8', rate: 4 },
              ]}
              margin={{ top: 8, right: 16, bottom: 4, left: -8 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit="%" domain={[0, 16]} />
              <Tooltip
                formatter={(v: number) => `${v}%`}
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
              />
              <Line
                type="monotone"
                dataKey="rate"
                stroke="#16a34a"
                strokeWidth={2.5}
                dot={{ r: 4, fill: '#16a34a' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* 3 — Processing Volume by Plant (doughnut) */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Processing Volume by Plant</div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 16 }}>Share of documents processed</div>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Ohio',    value: 34, fill: '#3b82f6' },
                  { name: 'Texas',   value: 28, fill: '#8b5cf6' },
                  { name: 'Georgia', value: 18, fill: '#f59e0b' },
                  { name: 'Other',   value: 20, fill: '#94a3b8' },
                ]}
                dataKey="value"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={2}
                label={(entry: { name: string; value: number }) => `${entry.name} ${entry.value}%`}
                labelLine={false}
              >
                {[0, 1, 2, 3].map((i) => (
                  <Cell key={i} />
                ))}
              </Pie>
              <Tooltip
                formatter={(v: number) => `${v}%`}
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* 4 — Agent Uptime (progress bars as gauge) */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Agent Uptime</div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 20 }}>Rolling 30-day availability</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            <UptimeRow name="CustomerOps" pct={99.9} />
            <UptimeRow name="QCBot"       pct={99.7} />
            <UptimeRow name="LogisticsBot" pct={99.8} />
          </div>
          <div style={{ marginTop: 24, padding: 12, background: '#f0fdf4', borderRadius: 8, border: '1px solid #bbf7d0', fontSize: 12, color: '#166534' }}>
            ● All agents within SLA (≥99.5% target)
          </div>
        </div>
      </div>

      {/* FEATURE 5 — Workforce Intelligence (3 charts: Cognitive Offload, HITL Velocity, Skill Shift) */}
      <WorkforceIntelligence />

      {/* Activity + Decisions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>Live Activity</span>
            <span className="chip-green animate-pulse">● Live</span>
          </div>
          <div>
            {/* CBB demo activity — headlines the 3 hero demos at the top for the live deck */}
            <ActivityItem dot="green" text="CustomerOps processed Order Mod CBB-ORD-1044 · AUTO_APPROVED"       time="09:14:32" />
            <ActivityItem dot="amber" text="QCBot · QC Batch Ohio Plant 7 · 50 certs · 2 HOLDS PLACED"          time="09:12:18" />
            <ActivityItem dot="red"   text="LogisticsBot · Vinyl Resin port strike · $1.09M · ESCALATED"        time="09:10:44" />
            <ActivityItem dot="amber" text="SentimentBot triaged DIST-4421 · HIGH PRIORITY flagged"             time="09:08:21" />
            <ActivityItem dot="green" text="CustomerOps · Order Mod CBB-ORD-1039 · AUTO_APPROVED"               time="09:06:55" last />
          </div>
        </div>

        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #f8fafc' }}>
            <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>Decision Summary · Today</span>
          </div>
          <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 12 }}>
            {(() => {
              const d = data?.decisions;
              if (d) {
                const total = d.auto_approved + d.routed_for_approval + d.human_review + d.rejected_or_failed;
                const pct = (n: number) => (total > 0 ? Math.round((n / total) * 100) : 0);
                const fmt = (n: number) => n.toLocaleString();
                return (
                  <>
                    <DecisionRow color="#22c55e" label="Auto-approved"       count={fmt(d.auto_approved)}       pct={pct(d.auto_approved)} />
                    <DecisionRow color="#3b82f6" label="Routed for approval" count={fmt(d.routed_for_approval)} pct={pct(d.routed_for_approval)} />
                    <DecisionRow color="#f59e0b" label="Human review"        count={fmt(d.human_review)}        pct={pct(d.human_review)} />
                    <DecisionRow color="#ef4444" label="Rejected / Failed"   count={fmt(d.rejected_or_failed)}  pct={pct(d.rejected_or_failed)} />
                  </>
                );
              }
              return (
                <>
                  <DecisionRow color="#22c55e" label="Auto-approved"       count="14,361" pct={78} />
                  <DecisionRow color="#3b82f6" label="Routed for approval" count="3,385"  pct={18} />
                  <DecisionRow color="#f59e0b" label="Human review"        count="666"    pct={4} />
                  <DecisionRow color="#ef4444" label="Rejected / Failed"   count="0"      pct={0} />
                </>
              );
            })()}
          </div>
        </div>
      </div>
    </>
  );
}

/* ─────────── sub-components ─────────── */

function Kpi({ topColor, label, value, delta, deltaColor, icon, iconColor }: {
  topColor: string; label: string; value: string; delta: string; deltaColor: string; icon: string; iconColor: string;
}) {
  const iconPath: Record<string, string> = {
    chart:        'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    check_circle: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
    info:         'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    refresh:      'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  };
  return (
    <div className="kpi-card" style={{ borderTop: `3px solid ${topColor}` }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>{label}</span>
        <svg style={{ width: 18, height: 18, color: iconColor }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={iconPath[icon]} />
        </svg>
      </div>
      <div className="kpi-value" style={{ color: '#0f172a' }}>{value}</div>
      <div className="kpi-delta" style={{ color: deltaColor }}>{delta}</div>
    </div>
  );
}

function PerfRow({ name, pct, color, deltaColor }: { name: string; pct: number; color: string; deltaColor?: string }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
        <span style={{ fontWeight: 500, color: '#0f172a' }}>{name}</span>
        <span style={{ fontWeight: 600, color: deltaColor || '#16a34a' }}>{pct.toFixed(1)}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

function ActivityItem({ dot, text, time, last }: { dot: 'green' | 'amber' | 'red'; text: string; time: string; last?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', borderBottom: last ? 'none' : '1px solid #f8fafc' }}>
      <span className={`dot-${dot}`} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{text}</div>
        <div style={{ fontSize: 11, color: '#94a3b8' }}>{time}</div>
      </div>
    </div>
  );
}

function UptimeRow({ name, pct }: { name: string; pct: number }) {
  // Scale: visualise the last 0.5% above 99.5 so differences are readable at a glance.
  const barPct = Math.max(0, Math.min(100, ((pct - 99.5) / 0.5) * 100));
  const color = pct >= 99.9 ? '#16a34a' : pct >= 99.7 ? '#22c55e' : '#f59e0b';
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
        <span style={{ fontWeight: 600, color: '#0f172a' }}>{name}</span>
        <span className="mono" style={{ fontWeight: 700, color }}>{pct.toFixed(1)}%</span>
      </div>
      <div style={{ height: 10, background: '#f1f5f9', borderRadius: 999, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${barPct}%`, background: color, borderRadius: 999, transition: 'width .3s' }} />
      </div>
      <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>SLA 99.5% · scale 99.5–100%</div>
    </div>
  );
}

function DecisionRow({ color, label, count, pct }: { color: string; label: string; count: string; pct: number }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ width: 12, height: 12, borderRadius: 3, background: color }} />
        <span style={{ fontSize: 13, color: '#374151' }}>{label}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div className="progress-bar" style={{ width: 120 }}>
          <div className="progress-fill" style={{ width: `${pct}%`, background: color }} />
        </div>
        <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{count}</span>
      </div>
    </div>
  );
}

/* ══════════════════════════ FEATURE 1 — ROI Command Center ══════════════════════════ */

interface ExecutiveKpi {
  value_generated_usd: number;
  value_generated_per_sec_usd: number;
  hours_repurposed: number;
  hours_repurposed_delta_pct: number | null;
  cost_of_inaction_usd: number;
  coi_delta_pct: number | null;
  window_hours: number;
}

/**
 * Executive-impact strip shown above the operational KPIs.
 *
 * Three visceral metrics (spec §3), all pulled live from
 * GET /api/v1/metrics/executive — aggregated server-side from work_items:
 *   • Value Generated  (sum of value_usd · last 24h) + live ticker at the
 *     rate the backend reports (avg $/sec over the last 60s of data)
 *   • Hours Repurposed (sum of manual_hours_saved · last 24h) + MoM delta
 *   • Cost of Inaction (sum of avoided_loss_usd · last 90d) + QoQ delta
 */
function RoiCommandCenter() {
  const q = useQuery<ExecutiveKpi>({
    queryKey: ['metrics-executive'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/metrics/executive`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    refetchInterval: 15_000,  // keep the KPIs warm; ticker handles sub-second feel
    retry: 1,
  });

  const data = q.data;
  const baseValue = data?.value_generated_usd ?? 0;
  const ratePerSec = data?.value_generated_per_sec_usd ?? 0;
  const [tickedValue, setTickedValue] = useState<number>(baseValue);

  // Reset ticker when the baseline refetches.
  useEffect(() => { setTickedValue(baseValue); }, [baseValue]);

  // Ticker: advance every 3s by 3 * ratePerSec (backend-reported dollars/sec).
  // If ratePerSec is 0 (no recent activity), we don't tick — no fake motion.
  useEffect(() => {
    if (ratePerSec <= 0) return;
    const id = window.setInterval(() => {
      setTickedValue((v) => v + ratePerSec * 3);
    }, 3000);
    return () => window.clearInterval(id);
  }, [ratePerSec]);

  const fmtUsd = (n: number) => `$${Math.round(n).toLocaleString()}`;
  const fmtDelta = (pct: number | null) => pct == null ? '—' : `${pct >= 0 ? '↑ +' : '↓ '}${Math.abs(pct).toFixed(1)}%`;
  const deltaTone = (pct: number | null) => pct == null ? undefined : (pct >= 0 ? '#86efac' : '#fca5a5');

  return (
    <section style={{
      background: 'linear-gradient(135deg, #0b1220 0%, #111827 60%, #0b1220 100%)',
      borderRadius: 20,
      padding: '28px 28px 24px',
      marginBottom: 24,
      position: 'relative',
      overflow: 'hidden',
      boxShadow: '0 20px 48px rgba(2, 6, 23, .35)',
    }}>
      {/* subtle glow accents */}
      <div aria-hidden style={{ position: 'absolute', top: -80, right: -80, width: 260, height: 260, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(34,197,94,.12), transparent 70%)', pointerEvents: 'none' }} />
      <div aria-hidden style={{ position: 'absolute', bottom: -120, left: -80, width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(59,130,246,.10), transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 18 }}>
        <div>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.18em', textTransform: 'uppercase', color: '#60a5fa' }}>
            ROI Command Center
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>Executive Impact · Today</div>
        </div>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 600, color: '#86efac' }}>
          <span className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 0 4px rgba(34,197,94,.25)' }} />
          LIVE · auto-refreshing every 3s
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        <ExecTile
          label="Value Generated"
          value={q.isLoading ? '…' : fmtUsd(tickedValue)}
          sub={ratePerSec > 0
            ? `Revenue protected · last 24h · ticker $${ratePerSec.toFixed(2)}/s`
            : 'Revenue protected · last 24h'}
          accent="#22c55e"
          pulse={ratePerSec > 0}
        />
        <ExecTile
          label="Hours Repurposed"
          value={q.isLoading ? '…' : `${Math.round(data?.hours_repurposed ?? 0).toLocaleString()} hrs`}
          sub={`${fmtDelta(data?.hours_repurposed_delta_pct ?? null)} vs prior ${data?.window_hours ?? 24}h · diverted from manual tasks`}
          accent="#60a5fa"
          subColor={deltaTone(data?.hours_repurposed_delta_pct ?? null)}
        />
        <ExecTile
          label="Cost of Inaction (COI)"
          value={q.isLoading ? '…' : fmtUsd(data?.cost_of_inaction_usd ?? 0)}
          sub={`${fmtDelta(data?.coi_delta_pct ?? null)} vs prior quarter · avoided losses last 90d`}
          accent="#f59e0b"
          subColor={deltaTone(data?.coi_delta_pct ?? null)}
        />
      </div>
    </section>
  );
}

function ExecTile({ label, value, sub, accent, pulse, subColor }: { label: string; value: string; sub: string; accent: string; pulse?: boolean; subColor?: string }) {
  return (
    <div style={{
      background: 'rgba(30, 41, 59, .55)',
      border: '1px solid rgba(148, 163, 184, .12)',
      borderRadius: 14,
      padding: '18px 20px',
      backdropFilter: 'blur(6px)',
      position: 'relative',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: accent, boxShadow: `0 0 12px ${accent}aa` }} />
        <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#94a3b8' }}>{label}</span>
      </div>
      <div
        className={pulse ? 'animate-pulse' : ''}
        style={{
          fontFamily: "'JetBrains Mono', ui-monospace, monospace",
          fontSize: 30,
          fontWeight: 800,
          color: '#f8fafc',
          letterSpacing: '-.02em',
          lineHeight: 1.05,
        }}
      >
        {value}
      </div>
      <div style={{ fontSize: 12, color: subColor || '#cbd5e1', marginTop: 6 }}>{sub}</div>
    </div>
  );
}

/* ══════════════════════════ FEATURE 5 — Workforce Intelligence ══════════════════════════ */

/**
 * Human-impact dashboard block (spec §7):
 *   • Cognitive Offload — area chart, repetitive-task volume over time
 *   • HITL Velocity     — line chart, human approval time (hours → minutes)
 *   • Skill Shift Index — bar chart, strategic review % vs data entry %
 */
interface WorkforceReport {
  cognitive_offload:       Array<{ week: string; value: number }>;
  hitl_velocity_minutes:   Array<{ week: string; value: number }>;
  skill_shift:             Array<{ month: string; strategic_pct: number; manual_pct: number }>;
}

function WorkforceIntelligence() {
  const q = useQuery<WorkforceReport>({
    queryKey: ['metrics-workforce'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/metrics/workforce?weeks=8`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    refetchInterval: 60_000,
    retry: 1,
  });

  const offloadData   = (q.data?.cognitive_offload ?? []).map((p) => ({ week: shortWeek(p.week), volume: p.value }));
  const hitlData      = (q.data?.hitl_velocity_minutes ?? []).map((p) => ({ week: shortWeek(p.week), minutes: p.value }));
  const skillShiftData = (q.data?.skill_shift ?? []).map((p) => ({
    month:     shortMonth(p.month),
    strategic: p.strategic_pct,
    manual:    p.manual_pct,
  }));

  const offloadGrowth = offloadData.length >= 2
    ? (offloadData[offloadData.length - 1].volume / Math.max(1, offloadData[0].volume)).toFixed(1)
    : '—';
  const hitlFirst = hitlData[0]?.minutes;
  const hitlLast  = hitlData[hitlData.length - 1]?.minutes;
  const skillFirst = skillShiftData[0]?.strategic ?? 0;
  const skillLast  = skillShiftData[skillShiftData.length - 1]?.strategic ?? 0;

  return (
    <section style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#64748b' }}>
            Workforce Intelligence
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginTop: 2 }}>Human × Agent collaboration health</div>
        </div>
        <span className="chip-green" style={{ fontSize: 11 }}>Trust ↑ · Toil ↓</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {/* Cognitive Offload — area */}
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Cognitive Offload</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 10 }}>Repetitive tasks handled by agents · weekly</div>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={offloadData} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
              <defs>
                <linearGradient id="offloadFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%"   stopColor="#22c55e" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="week" tick={{ fontSize: 10, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} width={36} />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }} formatter={(v: number) => [v.toLocaleString(), 'tasks']} />
              <Area type="monotone" dataKey="volume" stroke="#16a34a" strokeWidth={2} fill="url(#offloadFill)" />
            </AreaChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#16a34a', fontWeight: 600, marginTop: 6 }}>
            {offloadData.length >= 2
              ? `↑ ${offloadGrowth}× growth over ${offloadData.length} weeks`
              : (q.isLoading ? 'Loading…' : 'Awaiting first week of data')}
          </div>
        </div>

        {/* HITL Velocity — line */}
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Human-in-the-Loop Velocity</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 10 }}>Avg minutes to approve an agent decision</div>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={hitlData} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="week" tick={{ fontSize: 10, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} width={36} unit="m" />
              <Tooltip
                contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }}
                formatter={(v: number) => [`${v} min`, 'approval']}
              />
              <Line type="monotone" dataKey="minutes" stroke="#3b82f6" strokeWidth={2.5} dot={{ r: 3, fill: '#3b82f6' }} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#2563eb', fontWeight: 600, marginTop: 6 }}>
            {hitlFirst != null && hitlLast != null && hitlData.length >= 2
              ? `▼ ${Math.round(hitlFirst)} min → ${Math.round(hitlLast)} min · trust in agents rising`
              : (q.isLoading ? 'Loading…' : 'Awaiting review decisions')}
          </div>
        </div>

        {/* Skill Shift Index — stacked bar */}
        <div className="card" style={{ padding: 20 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Skill Shift Index</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 10 }}>% of human time · strategic vs manual</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={skillShiftData} margin={{ top: 6, right: 8, bottom: 0, left: -12 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 10, fill: '#94a3b8' }} />
              <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} width={36} unit="%" />
              <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }} formatter={(v: number) => `${v}%`} />
              <Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="strategic" stackId="x" fill="#8b5cf6" name="Strategic review" radius={[4, 4, 0, 0]} />
              <Bar dataKey="manual"    stackId="x" fill="#cbd5e1" name="Manual data entry" />
            </BarChart>
          </ResponsiveContainer>
          <div style={{ fontSize: 11, color: '#7c3aed', fontWeight: 600, marginTop: 6 }}>
            {skillShiftData.length >= 2
              ? `Strategic work up to ${Math.round(skillLast)}% (from ${Math.round(skillFirst)}%)`
              : (q.isLoading ? 'Loading…' : 'Awaiting activity data')}
          </div>
        </div>
      </div>
    </section>
  );
}

/** 'YYYY-Www' → 'Www' for compact chart ticks. */
function shortWeek(iso: string): string {
  const m = iso.match(/W(\d{2})$/);
  return m ? `W${m[1]}` : iso;
}
/** 'YYYY-MM' → 'Jan' etc. */
function shortMonth(iso: string): string {
  const m = /^\d{4}-(\d{2})$/.exec(iso);
  if (!m) return iso;
  const idx = parseInt(m[1], 10) - 1;
  const labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  return labels[idx] ?? iso;
}
