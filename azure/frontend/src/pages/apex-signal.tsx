/**
 * ApexSignal — Proactive Supply Chain Intelligence (Killer Feature 6).
 *
 * Four tabs per spec (ApexSignal_ClaudeCode_Spec.docx §2):
 *   • Risk Radar       — GET /signals/risks (Cosmos DB predictive_events + Azure ML lead-time refresh)
 *   • Demand Sensing   — GET /signals/demand (Azure ML DeepAR)
 *   • Stockout Forecast— GET /signals/stockout (Azure ML Linear Learner per inventory row)
 *   • Supplier Health  — GET /signals/suppliers (Azure ML XGBoost multi-class)
 *
 * "View Playbook →" on a risk card → POST /signals/risks/{id}/playbook which
 * invokes the real Logistics Foundry Agent Service runtime (same pattern as Simulator).
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  LineChart, Line, Area, AreaChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { useDemoMode, isIndustryVisible } from '@/lib/demoMode';
import { VerizonApexSignal } from '@/components/Dashboard/VerizonApexSignal';
import { EprodApexSignal }   from '@/components/Dashboard/EprodApexSignal';
import { CwfcuApexSignal }   from '@/components/Dashboard/CwfcuApexSignal';
import { BolerApexSignal }   from '@/components/Dashboard/BolerApexSignal';
import { useProductBrand, brandLabel, brandWordmark } from '@/lib/productBrand';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ═════════════════════ types (mirror backend models) ═════════════════════ */

interface Risk {
  id: string;
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  probability_pct: number;
  title: string;
  description?: string;
  affected_material_id?: string;
  affected_supplier_id?: string;
  affected_plants: string[];
  financial_exposure_usd: number;
  days_until_impact: number;
  agent_playbook_ready: boolean;
}

interface RiskRadar {
  kpi_active_risks: number;
  kpi_exposure_30d_usd: number;
  kpi_protected_ytd_usd: number;
  kpi_agent_runs_today: number;
  risks: Risk[];
}

interface DemandSensing {
  product_id: string;
  product_name: string;
  weeks_historical: string[];
  weeks_forecast:   string[];
  historical:       number[];
  forecast:         number[];
  confidence_lower: number[];
  confidence_upper: number[];
  external_signals: Array<{ type: string; description: string }>;
  agent_actions:    Array<{ title: string; detail: string }>;
}

interface StockoutRow {
  material_id: string;
  material_name: string;
  plant: string;
  days_until_stockout: number;
  pct_of_safety_stock: number;
  status: 'Critical' | 'At Risk' | 'Healthy';
}

interface StockoutReport {
  critical_material: string | null;
  critical_stockout_date: string | null;
  rows: StockoutRow[];
}

interface SupplierHealth {
  supplier_id: string;
  name: string;
  role: string;
  material_ids: string[];
  on_time_pct: number;
  qc_pass_pct: number;
  risk_score: string;
  risk_trend: string;
  predictive_alert?: string;
}

interface SupplierHealthReport {
  suppliers: SupplierHealth[];
}

interface PlaybookResponse {
  event_id: string;
  status: 'complete' | 'foundry_agent_offline';
  agent_id: string;
  final_answer: string;
  reasoning_steps: number;
  latency_ms: number;
}

type TabKey = 'risks' | 'demand' | 'stockout' | 'suppliers' | 'stp_reliability';

interface STPAssetRisk {
  equipment_id: string;
  system_id: string;
  risk_score: number;
  risk_tier: 'low' | 'moderate' | 'high' | 'critical';
  days_until_failure: number;
  confidence_lower_80: number;
  confidence_upper_80: number;
  active_anomaly: string | null;
  expected_failure_mode: string | null;
  scripted_message: string | null;
  recommended_pm: string | null;
  estimated_avoidance_usd: number;
  estimated_avoidance_hours: number;
}

interface STPPlantReliability {
  kpi_critical_assets: number;
  kpi_high_risk_assets: number;
  kpi_protected_ytd_usd: number;
  kpi_engineers_retiring_24mo: number;
  kpi_work_packages_indexed: number;
  kpi_active_anomalies: number;
  assets_at_risk: STPAssetRisk[];
  last_updated: string;
  model_versions: Record<string, string>;
}

/* ═════════════════════ component ═════════════════════ */

// Top-level dispatcher — picks Verizon vs Generic based on demo mode.
// We split components so hook ordering is stable per branch (rules-of-hooks).
export default function ApexSignalPage() {
  const [demoMode] = useDemoMode();
  const [brand] = useProductBrand();
  const signalName = brandLabel('Apex Signal', brand);     // "Regulus Signal" when active
  const wordmark   = brandWordmark(brand);                  // "APEX" / "REGULUS LENS"
  if (demoMode === 'verizon_far_edge' || demoMode === 'telecommunications') {
    return (
      <>
        <Head><title>{signalName} · Verizon Far Edge | {wordmark}</title></Head>
        <VerizonApexSignal />
      </>
    );
  }
  if (demoMode === 'eprod' || demoMode === 'oil_gas_midstream') {
    return (
      <>
        <Head><title>{signalName} · EPROD | {wordmark}</title></Head>
        <EprodApexSignal />
      </>
    );
  }
  if (demoMode === 'cwfcu' || demoMode === 'credit_union') {
    return (
      <>
        <Head><title>{signalName} · CommunityWide FCU | {wordmark}</title></Head>
        <CwfcuApexSignal />
      </>
    );
  }
  if (demoMode === 'boler' || demoMode === 'manufacturing_multi_division') {
    return (
      <>
        <Head><title>{signalName} · The Boler Company | {wordmark}</title></Head>
        <BolerApexSignal />
      </>
    );
  }
  return <GenericApexSignal />;
}

function GenericApexSignal() {
  const [demoMode] = useDemoMode();
  const [brand] = useProductBrand();
  const wordmark = brandWordmark(brand);

  // Each tab declares which industry it belongs to. The filter then collapses
  // the visible tab set to whichever the current demo mode shows. In 'all'
  // mode all 5 tabs are visible.
  const allTabs = [
    { k: 'risks',           label: 'Risk Radar',          industry: 'supply_manufacturing' },
    { k: 'demand',          label: 'Demand Sensing',      industry: 'supply_manufacturing' },
    { k: 'stockout',        label: 'Stockout Forecast',   industry: 'supply_manufacturing' },
    { k: 'suppliers',       label: 'Supplier Health',     industry: 'supply_manufacturing' },
    { k: 'stp_reliability', label: 'Plant Reliability',   industry: 'nuclear_operations' },
  ] as const;
  const visibleTabs = allTabs.filter((t) => isIndustryVisible(t.industry, demoMode));

  const isSTP = demoMode === 'nuclear_operations' || demoMode === 'stp';

  // Default tab depends on which tabs are visible.
  const initialTab: TabKey = visibleTabs[0]?.k ?? 'risks';
  const [tab, setTab] = useState<TabKey>(initialTab);
  const [openPlaybookFor, setOpenPlaybookFor] = useState<string | null>(null);

  // If demo mode flips at runtime, auto-switch to a still-visible tab.
  useEffect(() => {
    const stillVisible = visibleTabs.some((t) => t.k === tab);
    if (!stillVisible && visibleTabs[0]) setTab(visibleTabs[0].k);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoMode]);

  const risksQ = useQuery<RiskRadar>({
    queryKey: ['signals-risks'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/risks`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    // Skip the network call in STP mode — none of the surfaces that consume
    // /risks are visible. Keeps the page responsive and avoids polluting the
    // dashboard cost ticker with non-STP data.
    enabled: !isSTP,
    retry: 1, refetchInterval: 30_000,
  });

  // STP-specific page header copy.
  const eyebrow = isSTP
    ? 'ApexSignal · Plant Reliability · STP Nuclear'
    : 'ApexSignal · Predictive Intelligence · Live';
  const headline = isSTP
    ? 'Proactive Plant Reliability Intelligence'
    : 'Proactive Supply Chain Intelligence';
  const tagline = isSTP
    ? 'DeepAR + Random Cut Forest + XGBoost over plant sensor streams. ReliabilityAgent sees bearing degradation 11 days before failure.'
    : 'Azure ML forecasts + Azure AI Foundry Agent Service mitigation. Agents see the storm before it hits.';

  return (
    <>
      <Head><title>{brandLabel('ApexSignal', brand)} | {wordmark}</title></Head>

      {/* Page header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16, gap: 10, flexWrap: 'wrap' }}>
        <div>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.18em', textTransform: 'uppercase', color: isSTP ? '#1e3a8a' : '#7c3aed' }}>
            {eyebrow}
          </div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{headline}</h2>
          <p style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>{tagline}</p>
        </div>
        <span className="chip-green" style={{ fontSize: 11 }}>● All Systems Operational</span>
      </div>

      {/* KPI strip — generic CBB strip suppressed in STP mode (Plant Reliability tab has its own STP-specific KPIs) */}
      {!isSTP && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
          <SignalKpi label="Active Risks"          value={risksQ.data?.kpi_active_risks ?? '—'} tone="red" />
          <SignalKpi label="$ At Risk (30d)"       value={risksQ.data ? usdCompact(risksQ.data.kpi_exposure_30d_usd)  : '—'} tone="amber" />
          <SignalKpi label="$ Protected YTD"       value={risksQ.data ? usdCompact(risksQ.data.kpi_protected_ytd_usd) : '—'} tone="green" />
          <SignalKpi label="Agent Runs Today"      value={risksQ.data?.kpi_agent_runs_today ?? '—'} tone="blue" />
        </div>
      )}

      {/* Tab bar — collapses to a single Plant Reliability tab in STP mode */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {visibleTabs.map((t) => (
          <button
            key={t.k}
            onClick={() => setTab(t.k)}
            style={{
              padding: '8px 16px',
              fontSize: 13,
              fontWeight: 600,
              border: `1px solid ${tab === t.k ? '#7c3aed' : '#e2e8f0'}`,
              background: tab === t.k ? '#7c3aed' : '#fff',
              color: tab === t.k ? '#fff' : '#475569',
              borderRadius: 99,
              cursor: 'pointer',
              transition: 'all .15s',
            }}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'risks'           && <RiskRadarTab data={risksQ.data} loading={risksQ.isLoading} error={risksQ.error} onOpenPlaybook={setOpenPlaybookFor} />}
      {tab === 'demand'          && <DemandSensingTab />}
      {tab === 'stockout'        && <StockoutTab />}
      {tab === 'suppliers'       && <SupplierHealthTab />}
      {tab === 'stp_reliability' && <STPPlantReliabilityTab />}

      {openPlaybookFor && (
        <PlaybookModal
          eventId={openPlaybookFor}
          risk={risksQ.data?.risks?.find((r) => r.id === openPlaybookFor)}
          onClose={() => setOpenPlaybookFor(null)}
        />
      )}
    </>
  );
}

/* ═════════════════════ Tab: Risk Radar ═════════════════════ */

function RiskRadarTab({
  data, loading, error, onOpenPlaybook,
}: {
  data: RiskRadar | undefined;
  loading: boolean;
  error: unknown;
  onOpenPlaybook: (id: string) => void;
}) {
  if (loading) return <div className="card" style={{ padding: 24, color: '#94a3b8' }}>Loading active risks…</div>;
  if (error || !data) return <div className="card" style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' }}>Couldn&rsquo;t load risks from the backend.</div>;

  return (
    <>
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10 }}>
        Predicted disruptions · next 30 days
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {data.risks.map((r) => <RiskCard key={r.id} risk={r} onView={() => onOpenPlaybook(r.id)} />)}
        {data.risks.length === 0 && (
          <div className="card" style={{ padding: 32, textAlign: 'center', color: '#94a3b8' }}>No active risks in the forecast window.</div>
        )}
      </div>
    </>
  );
}

function RiskCard({ risk, onView }: { risk: Risk; onView: () => void }) {
  const tone = {
    CRITICAL: { border: '#fecaca', bg: '#fef2f2', chip: 'chip-red',    text: '#991b1b' },
    HIGH:     { border: '#fed7aa', bg: '#fff7ed', chip: 'chip-amber',  text: '#9a3412' },
    MEDIUM:   { border: '#fde68a', bg: '#fffbeb', chip: 'chip-amber',  text: '#92400e' },
    LOW:      { border: '#bbf7d0', bg: '#f0fdf4', chip: 'chip-green',  text: '#166534' },
  }[risk.severity];

  return (
    <div className="card" style={{ padding: '16px 20px', borderLeft: `4px solid ${tone.text}`, background: '#fff' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 260 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span className={tone.chip} style={{ fontSize: 10 }}>{risk.severity}</span>
            <span style={{ fontSize: 12, color: '#64748b' }}>· {risk.probability_pct}% Probability</span>
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>{risk.title}</div>
          <div style={{ fontSize: 13, color: '#475569', marginTop: 6, lineHeight: 1.45 }}>{risk.description}</div>
          <div style={{ display: 'flex', gap: 14, marginTop: 8, fontSize: 12, color: '#64748b', flexWrap: 'wrap' }}>
            {risk.affected_supplier_id && <span>Supplier <span className="mono" style={{ color: '#0f172a' }}>{risk.affected_supplier_id}</span></span>}
            {risk.affected_material_id && <span>Material <span className="mono" style={{ color: '#0f172a' }}>{risk.affected_material_id}</span></span>}
            {risk.affected_plants.length > 0 && <span>{risk.affected_plants.length} plants affected</span>}
          </div>
        </div>
        <div style={{ textAlign: 'right', minWidth: 180 }}>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8' }}>Financial Exposure</div>
          <div className="mono" style={{ fontSize: 22, fontWeight: 800, color: tone.text }}>${risk.financial_exposure_usd.toLocaleString()}</div>
          <div style={{ fontSize: 11, color: '#64748b' }}>{risk.days_until_impact} days until impact</div>
          <button
            onClick={onView}
            disabled={!risk.agent_playbook_ready}
            style={{
              marginTop: 10, padding: '6px 14px', fontSize: 12, fontWeight: 700,
              background: risk.agent_playbook_ready ? 'linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%)' : '#e2e8f0',
              color: risk.agent_playbook_ready ? '#fff' : '#94a3b8',
              border: 'none', borderRadius: 8,
              cursor: risk.agent_playbook_ready ? 'pointer' : 'not-allowed',
            }}
          >View Playbook →</button>
        </div>
      </div>
    </div>
  );
}

/* ═════════════════════ Tab: Demand Sensing ═════════════════════ */

function DemandSensingTab() {
  const q = useQuery<DemandSensing>({
    queryKey: ['signals-demand'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/demand`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  // IMPORTANT: every hook must run on every render, so useMemo sits BEFORE
  // any conditional return. When q.data is undefined we return [].
  const chartData = useMemo(() => {
    const d = q.data;
    if (!d) return [] as Array<{ week: string; historical?: number; forecast?: number; lower?: number; upper?: number }>;
    const all: Array<{ week: string; historical?: number; forecast?: number; lower?: number; upper?: number }> = [];
    d.historical.forEach((v, i) => all.push({ week: fmtWeek(d.weeks_historical[i]), historical: v }));
    // duplicate the last historical point into forecast to join the lines
    if (d.historical.length > 0 && d.forecast.length > 0) {
      all.push({
        week: fmtWeek(d.weeks_forecast[0]),
        historical: d.historical[d.historical.length - 1],
        forecast:   d.forecast[0],
        lower:      d.confidence_lower[0],
        upper:      d.confidence_upper[0],
      });
    }
    d.forecast.forEach((v, i) => {
      if (i === 0) return;
      all.push({
        week:     fmtWeek(d.weeks_forecast[i]),
        forecast: v,
        lower:    d.confidence_lower[i],
        upper:    d.confidence_upper[i],
      });
    });
    return all;
  }, [q.data]);

  if (q.isLoading) return <div className="card" style={{ padding: 24, color: '#94a3b8' }}>Loading DeepAR forecast…</div>;
  if (q.error || !q.data) return <div className="card" style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' }}>Couldn&rsquo;t reach the demand endpoint.</div>;

  const d = q.data;
  return (
    <>
      <div className="card" style={{ padding: 20, marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10, marginBottom: 12, flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Demand Forecast · {d.product_name} (next 12 weeks)</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>DeepAR time-series · trained on 36 months of sales data · updated daily</div>
          </div>
          <span className="chip-purple" style={{ fontSize: 11 }}>apex-signal-demand</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData} margin={{ top: 8, right: 16, bottom: 4, left: -8 }}>
            <defs>
              <linearGradient id="bandFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#22c55e" stopOpacity={0.20} />
                <stop offset="100%" stopColor="#22c55e" stopOpacity={0.04} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="week" tick={{ fontSize: 11, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} width={44} />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e2e8f0' }} formatter={(v: number) => v.toLocaleString()} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Area   dataKey="upper"     stroke="transparent" fill="url(#bandFill)" name="Forecast range" />
            <Line   dataKey="historical" stroke="#94a3b8" strokeWidth={2}   dot={{ r: 3 }} name="Historical" />
            <Line   dataKey="forecast"   stroke="#16a34a" strokeWidth={2.5} strokeDasharray="4 4" dot={{ r: 3 }} name="Forecast" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 12, marginBottom: 16 }}>
        {d.external_signals.map((s, i) => <SignalRowCard key={i} kind={s.type} text={s.description} />)}
      </div>

      <div className="card" style={{ padding: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>Recommended Agent Actions</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {d.agent_actions.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, padding: '12px 14px', borderRadius: 10, background: '#f8fafc', border: '1px solid #f1f5f9' }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{a.title}</div>
                <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{a.detail}</div>
              </div>
              <button className="btn btn-primary btn-sm">Execute</button>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function SignalRowCard({ kind, text }: { kind: string; text: string }) {
  const tone = {
    positive:   { icon: '↑', color: '#16a34a', bg: '#f0fdf4', label: 'Positive' },
    risk:       { icon: '↓', color: '#dc2626', bg: '#fef2f2', label: 'Risk' },
    competitor: { icon: '◆', color: '#7c3aed', bg: '#faf5ff', label: 'Competitor' },
    macro:      { icon: '▲', color: '#2563eb', bg: '#eff6ff', label: 'Macro' },
  }[kind] ?? { icon: '•', color: '#64748b', bg: '#f8fafc', label: 'Signal' };
  return (
    <div className="card" style={{ padding: 14, background: tone.bg, borderLeft: `3px solid ${tone.color}` }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: tone.color }}>
        {tone.icon} {tone.label}
      </div>
      <div style={{ fontSize: 12, color: '#334155', marginTop: 4, lineHeight: 1.5 }}>{text}</div>
    </div>
  );
}

/* ═════════════════════ Tab: Stockout Forecast ═════════════════════ */

function StockoutTab() {
  const q = useQuery<StockoutReport>({
    queryKey: ['signals-stockout'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/stockout`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  if (q.isLoading) return <div className="card" style={{ padding: 24, color: '#94a3b8' }}>Loading Linear Learner stockout forecast…</div>;
  if (q.error || !q.data) return <div className="card" style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' }}>Couldn&rsquo;t reach the stockout endpoint.</div>;

  const d = q.data;
  const chartData = d.rows.slice(0, 4).map((r, i) => ({
    day: `d+${r.days_until_stockout}`,
    inventory: 100 - i * 8,
  }));

  return (
    <>
      <div className="card" style={{ padding: 20, marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Inventory Burn Rate vs. Inbound Supply</div>
          <span className="chip-purple" style={{ fontSize: 11 }}>apex-signal-stockout</span>
        </div>
        {d.critical_material && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '10px 14px', borderRadius: 10, fontSize: 13, fontWeight: 600 }}>
            Projected stockout: <span className="mono">{d.critical_material}</span> · <span>{d.critical_stockout_date}</span>
          </div>
        )}
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData} margin={{ top: 12, right: 16, bottom: 4, left: -8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#64748b' }} />
            <YAxis tick={{ fontSize: 11, fill: '#64748b' }} unit="%" />
            <Tooltip contentStyle={{ fontSize: 12, borderRadius: 6 }} />
            <Line type="monotone" dataKey="inventory" stroke="#dc2626" strokeWidth={2.5} dot={{ r: 4 }} name="Inventory level (%)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '14px 20px', borderBottom: '1px solid #f1f5f9', fontSize: 13, fontWeight: 700, color: '#0f172a' }}>
          Critical Stock Levels · {d.rows.length} materials
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#f8fafc', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: '10px 16px', fontWeight: 600 }}>Material</th>
              <th style={{ padding: '10px 8px', fontWeight: 600 }}>Plant</th>
              <th style={{ padding: '10px 8px', fontWeight: 600, textAlign: 'right' }}>Days to Stockout</th>
              <th style={{ padding: '10px 8px', fontWeight: 600, textAlign: 'right' }}>Safety Stock %</th>
              <th style={{ padding: '10px 16px', fontWeight: 600 }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {d.rows.map((r) => {
              const tone = r.status === 'Critical' ? 'chip-red' : r.status === 'At Risk' ? 'chip-amber' : 'chip-green';
              return (
                <tr key={`${r.material_id}-${r.plant}`} style={{ borderTop: '1px solid #f1f5f9' }}>
                  <td className="mono" style={{ padding: '10px 16px', color: '#0f172a' }}>{r.material_name}</td>
                  <td style={{ padding: '10px 8px', color: '#475569' }}>{r.plant}</td>
                  <td className="mono" style={{ padding: '10px 8px', textAlign: 'right', color: '#0f172a', fontWeight: 600 }}>{r.days_until_stockout}</td>
                  <td style={{ padding: '10px 8px', textAlign: 'right', color: '#475569' }}>{r.pct_of_safety_stock}%</td>
                  <td style={{ padding: '10px 16px' }}><span className={tone} style={{ fontSize: 10 }}>{r.status}</span></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}

/* ═════════════════════ Tab: Supplier Health ═════════════════════ */

function SupplierHealthTab() {
  const q = useQuery<SupplierHealthReport>({
    queryKey: ['signals-suppliers'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/suppliers`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  if (q.isLoading) return <div className="card" style={{ padding: 24, color: '#94a3b8' }}>Loading XGBoost supplier risk scores…</div>;
  if (q.error || !q.data) return <div className="card" style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' }}>Couldn&rsquo;t reach the supplier endpoint.</div>;

  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Supplier Risk Scores · Predictive Model (updated weekly)</div>
        <span className="chip-purple" style={{ fontSize: 11 }}>apex-signal-supplier</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 12 }}>
        {q.data.suppliers.map((s) => <SupplierCard key={s.supplier_id} supplier={s} />)}
      </div>
    </>
  );
}

function SupplierCard({ supplier }: { supplier: SupplierHealth }) {
  const tone = {
    'Very Low': { chip: 'chip-green', border: '#bbf7d0', label: 'Healthy'  },
    'Low':      { chip: 'chip-green', border: '#bbf7d0', label: 'Healthy'  },
    'Medium':   { chip: 'chip-amber', border: '#fde68a', label: 'Watch'    },
    'High':     { chip: 'chip-red',   border: '#fecaca', label: 'At Risk'  },
    'Critical': { chip: 'chip-red',   border: '#fecaca', label: 'Critical' },
  }[supplier.risk_score] ?? { chip: 'chip-gray', border: '#e2e8f0', label: supplier.risk_score };

  return (
    <div className="card" style={{ padding: 16, borderLeft: `4px solid ${tone.border}` }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 4 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{supplier.name}</div>
          <div style={{ fontSize: 11, color: '#64748b' }}>{supplier.material_ids.join(' · ')} · {supplier.role}</div>
        </div>
        <span className={tone.chip} style={{ fontSize: 10 }}>{tone.label}</span>
      </div>
      <div style={{ display: 'flex', gap: 12, marginTop: 10, fontSize: 12, color: '#475569' }}>
        <span><strong style={{ color: '#0f172a' }}>{supplier.on_time_pct.toFixed(0)}%</strong> on-time</span>
        <span><strong style={{ color: '#0f172a' }}>{supplier.qc_pass_pct.toFixed(1)}%</strong> QC pass</span>
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10, fontSize: 11, color: '#64748b' }}>
        <span>Risk: <strong style={{ color: '#0f172a' }}>{supplier.risk_score}</strong></span>
        <span>Trend: {supplier.risk_trend === 'declining' ? '↓' : supplier.risk_trend === 'improving' ? '↑' : '→'} {supplier.risk_trend}</span>
      </div>
      {supplier.predictive_alert && (
        <div style={{ marginTop: 10, padding: 10, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, color: '#991b1b', fontSize: 11, lineHeight: 1.5 }}>
          {supplier.predictive_alert}
        </div>
      )}
    </div>
  );
}

/* ═════════════════════ Playbook modal ═════════════════════ */

function PlaybookModal({ eventId, risk, onClose }: { eventId: string; risk?: Risk; onClose: () => void }) {
  const mutation = useMutation({
    mutationFn: async (): Promise<PlaybookResponse> => {
      const r = await fetch(`${API_BASE_URL}/signals/risks/${encodeURIComponent(eventId)}/playbook`, { method: 'POST' });
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
  });
  // Auto-dispatch exactly once when the modal opens for a given risk.
  // Side-effects during render violate React's rules; useEffect is the right home.
  const mutateRef = useRef(mutation.mutate);
  mutateRef.current = mutation.mutate;
  useEffect(() => { mutateRef.current(); }, [eventId]);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 200,
        background: 'rgba(2,6,23,.55)',
        display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
        padding: 36, overflowY: 'auto',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 720, maxWidth: '96vw',
          background: '#0b1220', color: '#e2e8f0',
          borderRadius: 18, border: '1px solid rgba(148,163,184,.18)',
          boxShadow: '0 20px 60px rgba(2,6,23,.5)',
          padding: 24,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14, gap: 10 }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.18em', textTransform: 'uppercase', color: '#a78bfa' }}>
              Agent Mitigation Playbook
            </div>
            <h3 style={{ fontSize: 17, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>{risk?.title ?? eventId}</h3>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
              Logistics Foundry Agent Service runtime · GPT-5.4 via Azure AI Foundry Agent Service
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: 22, cursor: 'pointer', padding: 0, lineHeight: 1 }}>×</button>
        </div>

        {risk && (
          <div style={{ padding: 12, borderRadius: 10, background: 'rgba(30,41,59,.55)', border: '1px solid rgba(148,163,184,.12)', marginBottom: 14 }}>
            <div style={{ display: 'flex', gap: 18, fontSize: 12, color: '#cbd5e1', flexWrap: 'wrap' }}>
              <span>Severity <strong style={{ color: '#f1f5f9' }}>{risk.severity}</strong></span>
              <span>Probability <strong style={{ color: '#f1f5f9' }}>{risk.probability_pct}%</strong></span>
              <span>Exposure <strong style={{ color: '#f1f5f9' }}>${risk.financial_exposure_usd.toLocaleString()}</strong></span>
              <span>Days <strong style={{ color: '#f1f5f9' }}>{risk.days_until_impact}</strong></span>
            </div>
          </div>
        )}

        {mutation.isPending && (
          <div style={{ padding: 30, textAlign: 'center', color: '#94a3b8' }}>
            <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 13 }}>
              Dispatching to Logistics Foundry Agent Service…
            </div>
            <div style={{ marginTop: 10 }}><Dots /></div>
          </div>
        )}

        {mutation.error != null && (
          <div style={{ padding: 16, borderRadius: 10, background: 'rgba(239,68,68,.12)', border: '1px solid rgba(239,68,68,.4)', color: '#fca5a5', fontSize: 13 }}>
            Playbook dispatch failed. <span className="mono">{mutation.error instanceof Error ? mutation.error.message : String(mutation.error)}</span>
          </div>
        )}

        {mutation.data && (
          <>
            <div style={{ display: 'flex', gap: 12, fontSize: 11, color: '#94a3b8', marginBottom: 10 }}>
              <span>Status · <strong style={{ color: mutation.data.status === 'complete' ? '#86efac' : '#fca5a5' }}>{mutation.data.status}</strong></span>
              <span>Reasoning steps · {mutation.data.reasoning_steps}</span>
              <span>Latency · {mutation.data.latency_ms} ms</span>
            </div>
            <pre
              className="mono"
              style={{
                background: 'rgba(30,41,59,.45)',
                border: '1px solid rgba(148,163,184,.12)',
                borderRadius: 10,
                padding: 14,
                color: '#e2e8f0',
                fontSize: 12,
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
                maxHeight: '50vh',
                overflowY: 'auto',
                margin: 0,
              }}
            >{mutation.data.final_answer}</pre>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 16 }}>
              <button onClick={onClose}
                style={{ padding: '8px 14px', fontSize: 13, fontWeight: 600, borderRadius: 10, background: 'rgba(148,163,184,.12)', color: '#e2e8f0', border: '1px solid rgba(148,163,184,.22)', cursor: 'pointer' }}>Close</button>
              <button
                style={{ padding: '8px 18px', fontSize: 13, fontWeight: 700, borderRadius: 10, background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)', color: '#fff', border: 'none', cursor: 'pointer', boxShadow: '0 10px 24px rgba(22,163,74,.3)' }}>
                Approve &amp; Execute
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ═════════════════════ small helpers ═════════════════════ */

function SignalKpi({ label, value, tone }: { label: string; value: string | number; tone: 'red' | 'amber' | 'green' | 'blue' }) {
  const c = { red: '#dc2626', amber: '#f59e0b', green: '#16a34a', blue: '#2563eb' }[tone];
  return (
    <div className="card" style={{ padding: 14, borderTop: `3px solid ${c}` }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8' }}>{label}</div>
      <div className="mono" style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', marginTop: 6 }}>{value}</div>
    </div>
  );
}

function Dots() {
  return (
    <span style={{ display: 'inline-flex', gap: 5 }}>
      {[0, 1, 2].map((i) => (
        <span key={i} style={{
          width: 6, height: 6, borderRadius: '50%', background: '#60a5fa',
          animation: `sigdot 1.1s ${i * 0.15}s infinite ease-in-out`, opacity: 0.35,
        }} />
      ))}
      <style>{`
        @keyframes sigdot {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </span>
  );
}

function usdCompact(n: number): string {
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `$${(n / 1_000).toFixed(0)}K`;
  return `$${Math.round(n).toLocaleString()}`;
}

function fmtWeek(iso: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  if (!m) return iso;
  return `${parseInt(m[2], 10)}/${parseInt(m[3], 10)}`;
}


/* ═════════════════════ Tab: Plant Reliability (STP Phase 2) ═════════════════════
 *
 * Backed by GET /api/v1/signals/stp/plant-reliability — reads the same
 * synthetic-data corpus the STP action handlers + Foundry Agent Service agents use.
 * Once the live Azure ML endpoints (apex-signal-stp-rul / -anomaly /
 * -failure-class) are deployed, the backend swaps to live inference and
 * this tab updates transparently.
 */

const STP_TIER_COLORS: Record<STPAssetRisk['risk_tier'], { bg: string; chip: string; text: string }> = {
  critical: { bg: '#fef2f2', chip: '#dc2626', text: '#991b1b' },
  high:     { bg: '#fff7ed', chip: '#ea580c', text: '#9a3412' },
  moderate: { bg: '#fffbeb', chip: '#f59e0b', text: '#92400e' },
  low:      { bg: '#f0fdf4', chip: '#16a34a', text: '#14532d' },
};

function STPPlantReliabilityTab() {
  const q = useQuery<STPPlantReliability>({
    queryKey: ['signals-stp-plant-reliability'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/stp/plant-reliability`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  if (q.isLoading) return <div className="card" style={{ padding: 24, color: '#94a3b8' }}>Loading STP plant reliability data…</div>;
  if (q.error || !q.data) {
    return (
      <div className="card" style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b' }}>
        Couldn&rsquo;t reach the STP plant-reliability endpoint. Make sure the backend is running and synthetic data has been generated:
        <br /><br />
        <code className="mono" style={{ fontSize: 12 }}>cd synthetic-data/nuclear_operations &amp;&amp; python3 generate.py</code>
      </div>
    );
  }

  const d = q.data;
  return (
    <>
      {/* STP-specific KPI strip — overlays the generic ApexSignal KPIs above */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 12, marginBottom: 20,
        padding: 16, borderRadius: 14,
        background: 'linear-gradient(135deg, rgba(30,58,138,.05), rgba(30,58,138,.02))',
        border: '1px solid #e0e7ff',
      }}>
        <STPKpi label="Critical Assets"       value={d.kpi_critical_assets} tone="critical" />
        <STPKpi label="High-Risk Assets"      value={d.kpi_high_risk_assets} tone="high" />
        <STPKpi label="Active Anomalies"      value={d.kpi_active_anomalies} tone="moderate" />
        <STPKpi label="Reliability $ YTD"     value={`$${(d.kpi_protected_ytd_usd / 1000).toFixed(0)}K`} tone="low" />
        <STPKpi label="Engineers Retiring 24mo" value={d.kpi_engineers_retiring_24mo} tone="moderate" />
        <STPKpi label="Work Packages Indexed" value={d.kpi_work_packages_indexed.toLocaleString()} tone="low" />
      </div>

      {/* At-risk asset table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 16 }}>
        <div style={{ padding: '14px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>
            Assets at Risk · {d.assets_at_risk.length} active
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            <span className="chip-purple" style={{ fontSize: 10 }}>{d.model_versions.rul}</span>
            <span className="chip-purple" style={{ fontSize: 10 }}>{d.model_versions.anomaly}</span>
            <span className="chip-purple" style={{ fontSize: 10 }}>{d.model_versions.failure_class}</span>
          </div>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#f8fafc', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: '10px 16px', fontWeight: 600 }}>Equipment</th>
              <th style={{ padding: '10px 8px', fontWeight: 600 }}>System</th>
              <th style={{ padding: '10px 8px', fontWeight: 600 }}>Risk</th>
              <th style={{ padding: '10px 8px', fontWeight: 600, textAlign: 'right' }}>Days to Failure</th>
              <th style={{ padding: '10px 8px', fontWeight: 600, textAlign: 'right' }}>Recommend</th>
              <th style={{ padding: '10px 8px', fontWeight: 600, textAlign: 'right' }}>Avoidance ($)</th>
            </tr>
          </thead>
          <tbody>
            {d.assets_at_risk.map((a) => {
              const tone = STP_TIER_COLORS[a.risk_tier];
              return (
                <tr key={a.equipment_id} style={{ borderTop: '1px solid #f1f5f9', background: tone.bg }}>
                  <td className="mono" style={{ padding: '10px 16px', color: '#0f172a', fontWeight: 600 }}>{a.equipment_id}</td>
                  <td className="mono" style={{ padding: '10px 8px', color: '#475569' }}>{a.system_id}</td>
                  <td style={{ padding: '10px 8px' }}>
                    <span style={{
                      fontSize: 10, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
                      padding: '3px 8px', borderRadius: 4, background: tone.chip, color: '#fff',
                    }}>
                      {a.risk_tier} · {a.risk_score}
                    </span>
                  </td>
                  <td className="mono" style={{ padding: '10px 8px', color: tone.text, textAlign: 'right' }}>
                    {a.days_until_failure}d
                    <span style={{ color: '#94a3b8', fontSize: 10, marginLeft: 4 }}>
                      ({a.confidence_lower_80}–{a.confidence_upper_80})
                    </span>
                  </td>
                  <td className="mono" style={{ padding: '10px 8px', color: '#0f172a', textAlign: 'right' }}>{a.recommended_pm || '—'}</td>
                  <td className="mono" style={{ padding: '10px 8px', color: '#16a34a', textAlign: 'right', fontWeight: 600 }}>
                    ${(a.estimated_avoidance_usd / 1000).toFixed(0)}K
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Hero card — top critical asset highlights its scripted_message */}
      {d.assets_at_risk[0] && d.assets_at_risk[0].scripted_message && (
        <div className="card" style={{ padding: 20, background: '#fef2f2', border: '1.5px solid #fecaca' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10, flexShrink: 0,
              background: '#dc2626', color: '#fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18, fontWeight: 800,
            }}>!</div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#991b1b', marginBottom: 4 }}>
                ReliabilityAgent · {d.assets_at_risk[0].risk_tier.toUpperCase()} alert
              </div>
              <div style={{ fontSize: 13, color: '#0f172a', lineHeight: 1.6 }}>
                {d.assets_at_risk[0].scripted_message}
              </div>
              <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                <button className="btn btn-primary btn-sm">Open Playbook →</button>
                <button className="btn btn-secondary btn-sm">Add to Outage Window</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function STPKpi({ label, value, tone }: { label: string; value: string | number; tone: STPAssetRisk['risk_tier'] }) {
  const c = STP_TIER_COLORS[tone];
  return (
    <div className="card" style={{ padding: 12, borderTop: `3px solid ${c.chip}`, background: '#fff' }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8' }}>{label}</div>
      <div className="mono" style={{ fontSize: 20, fontWeight: 800, color: '#0f172a', marginTop: 4 }}>{value}</div>
    </div>
  );
}
