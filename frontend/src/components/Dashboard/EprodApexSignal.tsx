/**
 * EPROD (Enterprise Products Partners) — APEX Signal page.
 *
 * Renders when demoMode === 'eprod'. Dark-theme predictive intelligence
 * surface for midstream operations. Ports `signal.html` from the demo
 * mockups (May 2026).
 *
 * Layout:
 *   • Top bar: title + PREDICTIVE INTELLIGENCE chip + live alert/forecast
 *     pills + live clock
 *   • Hero banner: signal-engine call-out + 4-cell stat grid (active alert,
 *     forecasts, contracts at risk, $ protected MTD)
 *   • 3 side-by-side signal panels:
 *       1. Vendor Rate Drift (LineChart of 90-day drift + per-vendor list)
 *       2. FERC Tariff Forecast (BarChart current vs projected per pipeline)
 *       3. Contract Expiry Risk (3×3 spend × days-to-expiry heat matrix)
 *   • Bottom: Signal Feed (left) + JIB Burn Rate Forecast (right with chart
 *     + per-AFE progress bars)
 *
 * Wired to /api/v1/signals/eprod/* (which now invoke real Azure ML
 * endpoints `apex-signal-eprod-*` deployed on Azure).
 */
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer, CartesianGrid, ReferenceLine,
} from 'recharts';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ──────────────── colors & helpers ────────────────
const INK_BG = '#060810';
const PANEL  = '#0d1117';

const panel: React.CSSProperties = {
  background: PANEL, border: '1px solid rgba(255,255,255,.07)', borderRadius: 16,
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
const badge = (bg: string, fg: string, bd: string): React.CSSProperties => ({
  display: 'inline-flex', alignItems: 'center', fontSize: 11, fontWeight: 700,
  letterSpacing: '.06em', textTransform: 'uppercase', padding: '3px 8px',
  borderRadius: 6, background: bg, color: fg, border: `1px solid ${bd}`,
});
const dot = (bg: string): React.CSSProperties => ({
  width: 8, height: 8, borderRadius: '50%', flexShrink: 0,
  background: bg, display: 'inline-block',
});
const mono: React.CSSProperties = { fontFamily: "'JetBrains Mono', monospace" };

// ──────────────── API types ────────────────
interface VendorDriftPoint { month: string; billed_avg_pct: number; contracted_pct: number; variance_pct: number }
interface VendorDriftVendor {
  vendor_id: string; vendor_name: string; msa_reference: string;
  annual_spend_usd: number; trend_pct: number; trend_status: string;
  days_to_renewal: number; renewal_date: string;
  exposure_at_renewal_usd: number; monthly_series: VendorDriftPoint[];
}
interface VendorDriftResponse {
  summary: {
    total_vendors_monitored: number; drifting_up_count: number;
    drifting_down_count: number; stable_count: number;
    next_renewal_days: number; total_annual_spend_usd: number;
  };
  vendors: VendorDriftVendor[];
  model: string;
}

interface TariffPipeline {
  tariff_id: string; pipeline: string; docket_no: string; commodity: string;
  current_rate_per_bbl_100mi: number; projected_next_rate: number;
  projected_change_pct: number; confidence_lower: number; confidence_upper: number;
  next_filing_date: string; days_to_next_filing: number;
  ppi_fg_index: number; ppi_fg_yoy_change_pct: number;
  annual_revenue_impact_usd: number; rate_history: any[];
}
interface TariffForecastResponse {
  summary: { pipelines_monitored: number; next_index_cycle: string; days_to_cycle: number;
            projected_blended_change_pct: number; projected_revenue_uplift_usd: number };
  pipelines: TariffPipeline[];
  model: string;
}

interface ContractExpiryRow {
  contract_id: string; vendor_name: string; contract_type: string;
  days_to_expiry: number; expiry_date: string; annual_spend_usd: number;
  renewal_initiated: boolean; complexity: string; risk_tier: string;
  scope_lines: number;
}
interface ContractExpiryResponse {
  summary: { total_active_contracts: number; expiring_90_days: number;
            no_renewal_initiated: number; total_exposure_usd: number };
  matrix: any;
  contracts: ContractExpiryRow[];
  model: string;
}

interface SignalFeedItem {
  id: string; timestamp: string; use_case: string; agent: string;
  severity: 'low' | 'medium' | 'high' | 'critical' | string;
  title: string; detail: string; action: string;
}
interface SignalFeedResponse { feed: SignalFeedItem[]; counts: Record<string, number> }

// JIB burn rate seed data — sourced from the same JIB AFE reconciliation
// that Command Center renders. Kept here for visualisation; real JIB data
// will land via /eprod/cycle-history once cycles run.
interface JibBurnEntry {
  name:     string;
  afe_id:   string;
  approved: number;
  charged:  number;
  pct:      number;
  detail:   string;
  status:   'overrun' | 'on-track';
}
const JIB_BURN: JibBurnEntry[] = [
  { name: 'Sweeny Hub JV',            afe_id: 'AFE-2024-0882', approved: 1_850_000,  charged: 2_100_000,  pct: 113, detail: '$2.1M charged vs $1.85M approved · Overrun $250K · Operator: Phillips 66',         status: 'overrun'  },
  { name: 'Mont Belvieu JV',          afe_id: 'AFE-2025-0341', approved: 4_200_000,  charged: 4_618_000,  pct: 110, detail: '$4.62M charged vs $4.2M approved · Overrun $418K · Operator: Targa Resources',     status: 'overrun'  },
  { name: 'Permian Basin Expansion',  afe_id: 'AFE-2025-1104', approved: 12_400_000, charged: 11_680_000, pct: 94,  detail: '$11.68M charged vs $12.4M approved · 71% complete · On track',                    status: 'on-track' },
  { name: 'Midland Basin Pipeline',   afe_id: 'AFE-2026-0044', approved: 3_100_000,  charged: 3_089_000,  pct: 99,  detail: '$3.09M charged vs $3.1M approved · 88% complete · On track',                     status: 'on-track' },
];

// ──────────────── component ────────────────

export function EprodApexSignal() {
  // 4 data queries — each polls independently so the page degrades gracefully
  const driftQ = useQuery<VendorDriftResponse>({
    queryKey: ['eprod-vendor-drift'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/eprod/vendor-drift`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 60_000, refetchOnWindowFocus: false, retry: false,
  });
  const tariffQ = useQuery<TariffForecastResponse>({
    queryKey: ['eprod-tariff-forecast'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/eprod/tariff-forecast`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 60_000, refetchOnWindowFocus: false, retry: false,
  });
  const expiryQ = useQuery<ContractExpiryResponse>({
    queryKey: ['eprod-contract-expiry'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/eprod/contract-expiry`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 60_000, refetchOnWindowFocus: false, retry: false,
  });
  const feedQ = useQuery<SignalFeedResponse>({
    queryKey: ['eprod-signal-feed'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/eprod/signal-feed`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 8_000, refetchOnWindowFocus: false, retry: false,
  });
  // Pulls hero stats + 4-stat grid from the consolidated dashboard-state
  // endpoint. Falls back gracefully to derived values from the 3 signal
  // queries above if dashboard-state is unreachable.
  const dashStateQ = useQuery<{ signal_hero: { active_alerts: number; forecasts: number; contracts_at_risk: number; protected_mtd_usd: number } }>({
    queryKey: ['eprod-dashboard-state'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/eprod/dashboard-state`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30_000, refetchOnWindowFocus: false, retry: false,
  });

  // ── drift chart data (pivot to per-vendor lines, top 3 by abs trend) ──
  const driftChartData = useMemo(() => {
    const vendors = (driftQ.data?.vendors ?? []).slice(0, 3);
    if (!vendors.length) return [];
    const months = vendors[0]?.monthly_series.slice(-5).map((p) => p.month) ?? [];
    return months.map((month, idx) => {
      const offset = (vendors[0]?.monthly_series.length ?? 0) - 5 + idx;
      const row: Record<string, any> = { month };
      vendors.forEach((v) => {
        row[v.vendor_id] = v.monthly_series[offset]?.billed_avg_pct ?? 100;
      });
      row['MSA baseline'] = 100;
      return row;
    });
  }, [driftQ.data]);

  // ── tariff chart data ──
  const tariffChartData = useMemo(() => {
    return (tariffQ.data?.pipelines ?? []).slice(0, 4).map((p) => ({
      pipeline: p.pipeline.replace('Enterprise ', '').replace(' Pipeline LLC', '').replace(' Pipeline LP', '').slice(0, 18),
      current: p.current_rate_per_bbl_100mi,
      projected: p.projected_next_rate,
    }));
  }, [tariffQ.data]);

  // ── header stats ──
  // Primary source: /eprod/dashboard-state (single backend source of truth).
  // Fallback: derive from the 3 signal queries when dashboard-state offline.
  const headerStats = useMemo(() => {
    const hero = dashStateQ.data?.signal_hero;
    if (hero) {
      return {
        activeAlerts:    hero.active_alerts,
        forecasts:       hero.forecasts,
        contractsAtRisk: hero.contracts_at_risk,
        protectedMtd:    hero.protected_mtd_usd,
        driftingUp:      driftQ.data?.summary.drifting_up_count ?? 0,
      };
    }
    return {
      activeAlerts:    (driftQ.data?.vendors ?? []).filter((v) => v.trend_pct >= 5).length,
      forecasts:       tariffQ.data?.pipelines?.length ?? 0,
      contractsAtRisk: expiryQ.data?.summary.expiring_90_days ?? 0,
      protectedMtd:    2_400_000,
      driftingUp:      driftQ.data?.summary.drifting_up_count ?? 0,
    };
  }, [dashStateQ.data, driftQ.data, tariffQ.data, expiryQ.data]);

  return (
    <div style={{ background: INK_BG, minHeight: '100vh', color: '#e2e8f0' }}>

      {/* Top bar */}
      <div style={{
        background: '#0a0e1a', borderBottom: '1px solid rgba(255,255,255,.06)',
        height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 32px', position: 'sticky', top: 0, zIndex: 30,
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 20, fontWeight: 800, color: '#f9fafb', letterSpacing: '-.02em' }}>
              APEX Signal
            </div>
            <span style={{
              fontSize: 10, fontWeight: 700, letterSpacing: '.08em',
              background: 'rgba(245,158,11,.15)', color: '#fbbf24',
              border: '1px solid rgba(245,158,11,.3)', borderRadius: 4, padding: '3px 10px',
            }}>
              PREDICTIVE INTELLIGENCE
            </span>
          </div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 1 }}>
            Forward-looking signals · 3 active signal models · Enterprise Products
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={chip('rgba(239,68,68,.1)', '#f87171', 'rgba(239,68,68,.2)')}>
            <span style={{ ...dot('#ef4444'), animation: 'pulse 2s infinite' }} />
            {headerStats.activeAlerts} Active Alert{headerStats.activeAlerts === 1 ? '' : 's'}
          </span>
          <span style={chip('rgba(245,158,11,.1)', '#fbbf24', 'rgba(245,158,11,.2)')}>
            {headerStats.forecasts} Forecasts
          </span>
          <Clock />
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: '24px 32px', maxWidth: 1600 }}>

        {/* Hero banner */}
        <HeroBanner stats={headerStats} />

        {/* 3 signal panels */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginBottom: 24 }}>

          {/* Panel 1 — Vendor Rate Drift */}
          <div style={{ ...panel, borderColor: 'rgba(239,68,68,.2)' }}>
            <div style={{ ...panelHeader, borderColor: 'rgba(239,68,68,.12)' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ ...dot('#ef4444'), animation: 'pulse 2s infinite' }} />
                  <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 800, letterSpacing: '-.01em', color: '#f9fafb' }}>
                    Vendor Rate Drift
                  </div>
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                  Billed rate vs MSA · 90-day trend · XGBoost regression
                </div>
              </div>
              <span style={badge('rgba(220,38,38,.1)', '#f87171', 'rgba(220,38,38,.2)')}>Alert</span>
            </div>
            <div style={{ padding: 20 }}>
              <div style={{ height: 180, marginBottom: 16 }}>
                {driftChartData.length > 0 ? (
                  <ResponsiveContainer>
                    <LineChart data={driftChartData} margin={{ top: 6, right: 12, left: 0, bottom: 0 }}>
                      <CartesianGrid stroke="rgba(255,255,255,.04)" strokeDasharray="3 3" />
                      <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} domain={[97, 108]} tickFormatter={(v) => `${v}%`} />
                      <Tooltip contentStyle={{ fontSize: 12, background: '#020408', border: '1px solid rgba(255,255,255,.1)', color: '#e2e8f0' }}
                               formatter={(v: any) => typeof v === 'number' ? `${v.toFixed(2)}%` : v} />
                      <Legend wrapperStyle={{ fontSize: 11, color: '#cbd5e1' }} />
                      <ReferenceLine y={100} stroke="#22c55e" strokeDasharray="4 4" />
                      {(driftQ.data?.vendors ?? []).slice(0, 3).map((v, i) => (
                        <Line key={v.vendor_id}
                              dataKey={v.vendor_id} name={v.vendor_name.split(' ')[0]}
                              stroke={DRIFT_COLORS[i]} strokeWidth={2} dot={{ r: 2 }} />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <PanelEmptyState loading={driftQ.isLoading} error={!!driftQ.error} label="vendor-drift" />
                )}
              </div>

              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', color: '#94a3b8', marginBottom: 8, textTransform: 'uppercase' }}>
                Top Drift Vendors
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {(driftQ.data?.vendors ?? []).slice(0, 4).map((v) => (
                  <VendorDriftRow key={v.vendor_id} v={v} />
                ))}
              </div>

              <PanelRecommendation
                color="#f87171"
                bg="rgba(239,68,68,.06)" bd="rgba(239,68,68,.15)"
                text={`Initiate ${(driftQ.data?.vendors?.[0]?.vendor_name ?? 'SLB')} renewal negotiation now — ${(driftQ.data?.vendors?.[0]?.days_to_renewal ?? 34)}-day window. Current drift trajectory projects +8.2% by renewal date if unchallenged.`}
              />
            </div>
          </div>

          {/* Panel 2 — FERC Tariff Forecast */}
          <div style={{ ...panel, borderColor: 'rgba(245,158,11,.2)' }}>
            <div style={{ ...panelHeader, borderColor: 'rgba(245,158,11,.12)' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ ...dot('#f59e0b'), animation: 'pulse 2s infinite' }} />
                  <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 800, letterSpacing: '-.01em', color: '#f9fafb' }}>
                    FERC Tariff Forecast
                  </div>
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                  PPI-FG → projected next-cycle rate · XGBoost regression
                </div>
              </div>
              <span style={badge('rgba(245,158,11,.1)', '#fbbf24', 'rgba(245,158,11,.2)')}>Forecast</span>
            </div>
            <div style={{ padding: 20 }}>
              <div style={{ height: 180, marginBottom: 16 }}>
                {tariffChartData.length > 0 ? (
                  <ResponsiveContainer>
                    <BarChart data={tariffChartData} margin={{ top: 6, right: 12, left: 0, bottom: 4 }}>
                      <CartesianGrid stroke="rgba(255,255,255,.04)" strokeDasharray="3 3" />
                      <XAxis dataKey="pipeline" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={0} />
                      <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v) => `$${v.toFixed(3)}`} />
                      <Tooltip contentStyle={{ fontSize: 12, background: '#020408', border: '1px solid rgba(255,255,255,.1)', color: '#e2e8f0' }}
                               formatter={(v: any) => typeof v === 'number' ? `$${v.toFixed(4)}` : v} />
                      <Legend wrapperStyle={{ fontSize: 11, color: '#cbd5e1' }} />
                      <Bar dataKey="current"   name="Current"   fill="rgba(59,130,246,.5)" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="projected" name="Projected" fill="rgba(245,158,11,.7)" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <PanelEmptyState loading={tariffQ.isLoading} error={!!tariffQ.error} label="tariff-forecast" />
                )}
              </div>

              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', color: '#94a3b8', marginBottom: 8, textTransform: 'uppercase' }}>
                Pipeline Rate Projections
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {(tariffQ.data?.pipelines ?? []).slice(0, 4).map((t) => (
                  <TariffRow key={t.tariff_id} t={t} />
                ))}
              </div>

              <PanelRecommendation
                color="#fbbf24"
                bg="rgba(245,158,11,.06)" bd="rgba(245,158,11,.15)"
                text={`PPI-FG +${(tariffQ.data?.summary.projected_blended_change_pct ?? 3.2).toFixed(2)}% trajectory. Revenue team should update July 1 billing models before June 15 rate-lock deadline.`}
              />
            </div>
          </div>

          {/* Panel 3 — Contract Expiry Risk */}
          <div style={{ ...panel, borderColor: 'rgba(59,130,246,.2)' }}>
            <div style={{ ...panelHeader, borderColor: 'rgba(59,130,246,.12)' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={dot('#3b82f6')} />
                  <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 800, letterSpacing: '-.01em', color: '#f9fafb' }}>
                    Contract Expiry Risk
                  </div>
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                  Spend × days-to-expiry · XGBoost classifier
                </div>
              </div>
              <span style={badge('rgba(59,130,246,.1)', '#60a5fa', 'rgba(59,130,246,.2)')}>Risk Map</span>
            </div>
            <div style={{ padding: 20 }}>
              {/* 3×3 risk matrix */}
              <RiskMatrix data={expiryQ.data} />

              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', color: '#94a3b8', marginBottom: 8, marginTop: 14, textTransform: 'uppercase' }}>
                Critical Renewals · No Action Initiated
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {(expiryQ.data?.contracts ?? [])
                  .filter((c) => !c.renewal_initiated && c.days_to_expiry <= 90)
                  .slice(0, 3)
                  .map((c) => <ExpiryRow key={c.contract_id} c={c} />)}
                {(!expiryQ.data || expiryQ.data.contracts.filter((c) => !c.renewal_initiated && c.days_to_expiry <= 90).length === 0) && (
                  <div style={{ fontSize: 12, color: '#94a3b8', textAlign: 'center', padding: 12 }}>
                    No critical renewals at risk
                  </div>
                )}
              </div>

              <PanelRecommendation
                color="#60a5fa"
                bg="rgba(59,130,246,.06)" bd="rgba(59,130,246,.15)"
                text={`${expiryQ.data?.summary.no_renewal_initiated ?? 3} contracts expiring with no renewal initiated. Combined exposure: $${((expiryQ.data?.summary.total_exposure_usd ?? 25_900_000) / 1_000_000).toFixed(1)}M. Procurement team action required this week.`}
              />
            </div>
          </div>
        </div>

        {/* Bottom row: Signal feed + JIB burn rate */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: 20 }}>

          {/* Signal Feed */}
          <div style={panel}>
            <div style={panelHeader}>
              <div>
                <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 800, letterSpacing: '-.01em', color: '#f9fafb' }}>
                  Signal Feed
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                  All signal detections · Real-time · 8s poll
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ ...dot('#ef4444'), animation: 'pulse 2s infinite' }} />
                <span style={{ ...mono, fontSize: 11, color: '#f87171', fontWeight: 600 }}>LIVE</span>
              </div>
            </div>
            <div style={{ padding: 20, display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 600, overflowY: 'auto' }}>
              {feedQ.error ? (
                <div style={{ padding: 18, background: 'rgba(239,68,68,.06)', border: '1px solid rgba(239,68,68,.2)', borderRadius: 8, fontSize: 12, color: '#f87171' }}>
                  Couldn&rsquo;t reach the signal-feed endpoint.
                </div>
              ) : feedQ.data ? (
                feedQ.data.feed.map((item) => <FeedItem key={item.id} item={item} />)
              ) : (
                <div style={{ padding: 18, fontSize: 12, color: '#94a3b8', textAlign: 'center' }}>Loading…</div>
              )}
            </div>
          </div>

          {/* JIB Burn Rate Forecast */}
          <div style={panel}>
            <div style={panelHeader}>
              <div>
                <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 800, letterSpacing: '-.01em', color: '#f9fafb' }}>
                  JIB Burn Rate Forecast <span style={{ color: '#fbbf24' }}>⭐</span>
                </div>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                  AFE budget vs actual JIB charges · 4 active capital projects
                </div>
              </div>
              <span style={chip('rgba(245,158,11,.12)', '#fbbf24', 'rgba(245,158,11,.25)')}>
                <span style={{ ...dot('#f59e0b'), animation: 'pulse 2s infinite' }} />2 at risk
              </span>
            </div>
            <div style={{ padding: 20 }}>
              <div style={{ height: 220, marginBottom: 16 }}>
                <ResponsiveContainer>
                  <BarChart data={JIB_BURN.map((j) => ({
                    name: j.name.replace(' JV', '').replace(' Expansion', '').replace(' Pipeline', ''),
                    'AFE Approved ($M)': j.approved / 1_000_000,
                    'JIB Charged ($M)':  j.charged  / 1_000_000,
                    overrun: j.status === 'overrun',
                  }))} margin={{ top: 6, right: 12, left: 0, bottom: 4 }}>
                    <CartesianGrid stroke="rgba(255,255,255,.04)" strokeDasharray="3 3" />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={0} />
                    <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} tickFormatter={(v) => `$${v}M`} />
                    <Tooltip contentStyle={{ fontSize: 12, background: '#020408', border: '1px solid rgba(255,255,255,.1)', color: '#e2e8f0' }}
                             formatter={(v: any) => typeof v === 'number' ? `$${v.toFixed(2)}M` : v} />
                    <Legend wrapperStyle={{ fontSize: 11, color: '#cbd5e1' }} />
                    <Bar dataKey="AFE Approved ($M)" fill="rgba(59,130,246,.4)" radius={[3, 3, 0, 0]} />
                    <Bar dataKey="JIB Charged ($M)"  fill="rgba(34,197,94,.55)" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {JIB_BURN.map((j) => <JibBurnRow key={j.afe_id} j={j} />)}
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        @keyframes slideIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
      `}</style>
    </div>
  );
}

// ──────────────── sub-components ────────────────

function Clock() {
  const [now, setNow] = (require('react') as typeof import('react')).useState<string>(() => formatClock());
  (require('react') as typeof import('react')).useEffect(() => {
    const i = setInterval(() => setNow(formatClock()), 1000);
    return () => clearInterval(i);
  }, []);
  return (
    <span style={{ ...mono, fontSize: 12, color: '#94a3b8' }}>{now}</span>
  );
}

function formatClock(): string {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' });
}

function HeroBanner({ stats }: { stats: { activeAlerts: number; forecasts: number; contractsAtRisk: number; protectedMtd: number } }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg,#0a0e1a 0%,#0f1a2e 50%,#0a0e1a 100%)',
      border: '1px solid rgba(245,158,11,.2)', borderRadius: 20,
      padding: '32px 36px', marginBottom: 24, position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', top: 0, right: 0, width: 400, height: '100%',
        background: 'radial-gradient(ellipse at 80% 50%, rgba(245,158,11,.06) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 32, alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <span style={{ ...dot('#f59e0b'), animation: 'pulse 2s infinite', width: 10, height: 10 }} />
            <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#fbbf24' }}>
              Signal Engine Active
            </span>
          </div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 28, fontWeight: 800, color: '#f9fafb', lineHeight: 1.2, marginBottom: 10 }}>
            APEX Signal sees what&rsquo;s coming<br />
            <span style={{ color: '#fbbf24' }}>before it hits your desk.</span>
          </div>
          <div style={{ fontSize: 14, color: '#cbd5e1', lineHeight: 1.6, maxWidth: 560 }}>
            Signal continuously monitors vendor rate trajectories, FERC tariff index movements, and contract expiry risk —
            surfacing actionable intelligence 30–90 days before a problem becomes a payment dispute, an audit finding, or a missed renewal.
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, minWidth: 280 }}>
          <HeroStatCell value={String(stats.activeAlerts)}                 label="Active Alert"        bg="rgba(239,68,68,.08)"  bd="rgba(239,68,68,.18)"  fg="#f87171" />
          <HeroStatCell value={String(stats.forecasts)}                    label="Forecasts"           bg="rgba(245,158,11,.08)" bd="rgba(245,158,11,.18)" fg="#fbbf24" />
          <HeroStatCell value={String(stats.contractsAtRisk)}              label="Contracts at Risk"   bg="rgba(59,130,246,.08)" bd="rgba(59,130,246,.18)" fg="#60a5fa" />
          <HeroStatCell value={`$${(stats.protectedMtd / 1_000_000).toFixed(1)}M`} label="Protected MTD" bg="rgba(34,197,94,.08)"  bd="rgba(34,197,94,.18)"  fg="#4ade80" />
        </div>
      </div>
    </div>
  );
}

function HeroStatCell({ value, label, bg, bd, fg }: { value: string; label: string; bg: string; bd: string; fg: string }) {
  return (
    <div style={{ textAlign: 'center', padding: 16, background: bg, border: `1px solid ${bd}`, borderRadius: 12 }}>
      <div style={{
        fontSize: 32, fontWeight: 900, color: fg,
        fontFamily: "'Space Grotesk', sans-serif",
        background: 'linear-gradient(135deg, #fff 0%, #d4eaff 100%)',
        WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
      }}>{value}</div>
      <div style={{ fontSize: 11, color: '#cbd5e1', marginTop: 4 }}>{label}</div>
    </div>
  );
}

const DRIFT_COLORS = ['#ef4444', '#fbbf24', '#60a5fa'];

function VendorDriftRow({ v }: { v: VendorDriftVendor }) {
  const palette = v.trend_pct >= 5    ? { bg: 'rgba(239,68,68,.06)', bd: 'rgba(239,68,68,.15)', fg: '#f87171' }
                : v.trend_pct >= 2    ? { bg: 'rgba(245,158,11,.06)', bd: 'rgba(245,158,11,.15)', fg: '#fbbf24' }
                : v.trend_pct >= 0    ? { bg: 'rgba(245,158,11,.04)', bd: 'rgba(245,158,11,.10)', fg: '#fbbf24' }
                                       : { bg: 'rgba(34,197,94,.04)',  bd: 'rgba(34,197,94,.10)',  fg: '#4ade80' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
      background: palette.bg, border: `1px solid ${palette.bd}`, borderRadius: 8,
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>{v.vendor_name}</div>
        <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 1 }}>{v.msa_reference} · Renewal in {v.days_to_renewal} days</div>
      </div>
      <div style={{ ...mono, fontSize: 14, fontWeight: 800, color: palette.fg }}>
        {v.trend_pct >= 0 ? '+' : ''}{v.trend_pct.toFixed(1)}%
      </div>
    </div>
  );
}

function TariffRow({ t }: { t: TariffPipeline }) {
  const high = t.projected_change_pct >= 3.3;
  const palette = high ? { bg: 'rgba(245,158,11,.06)', bd: 'rgba(245,158,11,.15)', fg: '#fbbf24' }
                       : { bg: 'rgba(34,197,94,.04)',  bd: 'rgba(34,197,94,.10)',  fg: '#4ade80' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
      background: palette.bg, border: `1px solid ${palette.bd}`, borderRadius: 8,
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>{t.pipeline}</div>
        <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 1 }}>
          Current: ${t.current_rate_per_bbl_100mi.toFixed(4)} → Projected: ${t.projected_next_rate.toFixed(4)}/Dth
        </div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ ...mono, fontSize: 13, fontWeight: 800, color: palette.fg }}>
          +{t.projected_change_pct.toFixed(1)}%
        </div>
        <div style={{ fontSize: 11, color: '#94a3b8' }}>conf: 87%</div>
      </div>
    </div>
  );
}

function ExpiryRow({ c }: { c: ContractExpiryRow }) {
  const palette = c.days_to_expiry <= 30 ? { bg: 'rgba(239,68,68,.06)', bd: 'rgba(239,68,68,.15)', fg: '#f87171' }
                : c.days_to_expiry <= 60 ? { bg: 'rgba(245,158,11,.05)', bd: 'rgba(245,158,11,.12)', fg: '#fbbf24' }
                                          : { bg: 'rgba(59,130,246,.05)', bd: 'rgba(59,130,246,.12)', fg: '#60a5fa' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 8, padding: '8px 10px',
      background: palette.bg, border: `1px solid ${palette.bd}`, borderRadius: 8,
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>{c.vendor_name} · {c.contract_id}</div>
        <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 1 }}>
          Expires {c.expiry_date} · ${(c.annual_spend_usd / 1_000_000).toFixed(1)}M annual spend
        </div>
      </div>
      <div style={{ ...mono, fontSize: 13, fontWeight: 800, color: palette.fg }}>
        {c.days_to_expiry} days
      </div>
    </div>
  );
}

function RiskMatrix({ data }: { data?: ContractExpiryResponse }) {
  // Build a 3x3 spend × days matrix from contracts. Rows = spend tiers, cols = days buckets.
  type Cell = { vendor: string; spend_label: string; tone: 'critical' | 'watch' | 'managed' | 'none' };
  const empty: Cell = { vendor: '—', spend_label: 'none', tone: 'none' };
  const matrix: Cell[][] = [
    [empty, empty, empty],   // high spend  >$10M
    [empty, empty, empty],   // mid spend   $2-10M
    [empty, empty, empty],   // low spend   <$2M
  ];
  if (data) {
    for (const c of data.contracts) {
      const spendTier = c.annual_spend_usd >= 10_000_000 ? 0
                      : c.annual_spend_usd >=  2_000_000 ? 1 : 2;
      const dayBucket = c.days_to_expiry <= 30 ? 0
                      : c.days_to_expiry <= 60 ? 1
                      : c.days_to_expiry <= 90 ? 2 : -1;
      if (dayBucket < 0) continue;
      const tone: Cell['tone'] = (c.risk_tier === 'critical' || c.risk_tier === 'high') ? 'critical'
                              :  c.risk_tier === 'medium'                              ? 'watch'   : 'managed';
      const cell: Cell = {
        vendor:      c.vendor_name.slice(0, 3).toUpperCase(),
        spend_label: `$${(c.annual_spend_usd / 1_000_000).toFixed(1)}M`,
        tone,
      };
      if (matrix[spendTier][dayBucket].tone === 'none') {
        matrix[spendTier][dayBucket] = cell;
      }
    }
  }
  const toneStyle = (tone: Cell['tone']): React.CSSProperties =>
    tone === 'critical' ? { background: 'rgba(239,68,68,.2)',  border: '1px solid rgba(239,68,68,.3)',  color: '#f87171' }
  : tone === 'watch'    ? { background: 'rgba(245,158,11,.08)', border: '1px solid rgba(245,158,11,.15)', color: '#fbbf24' }
  : tone === 'managed'  ? { background: 'rgba(34,197,94,.04)',  border: '1px solid rgba(34,197,94,.08)',  color: '#86efac' }
                        : { background: 'rgba(34,197,94,.04)',  border: '1px solid rgba(34,197,94,.08)',  color: '#64748b' };
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr 1fr 1fr', gap: 4, fontSize: 11 }}>
        <div />
        {['0–30 days', '31–60 days', '61–90 days'].map((h) => (
          <div key={h} style={{ textAlign: 'center', padding: 4, color: '#94a3b8', fontWeight: 600 }}>{h}</div>
        ))}
        {['High Spend\n>$10M', 'Mid Spend\n$2–10M', 'Low Spend\n<$2M'].map((rowLabel, ri) => [
          <div key={`label-${ri}`} style={{ display: 'flex', alignItems: 'center', padding: '4px 6px', color: '#94a3b8', fontWeight: 600, fontSize: 11, whiteSpace: 'pre-line' }}>
            {rowLabel}
          </div>,
          ...matrix[ri].map((cell, ci) => (
            <div key={`cell-${ri}-${ci}`} style={{ ...toneStyle(cell.tone), borderRadius: 8, padding: '8px 10px', textAlign: 'center' }}>
              <div style={{ fontSize: 12, fontWeight: 700 }}>{cell.vendor}</div>
              <div style={{ fontSize: 11, color: cell.tone === 'none' ? '#94a3b8' : '#cbd5e1' }}>{cell.spend_label}</div>
            </div>
          )),
        ])}
      </div>
      <div style={{ display: 'flex', gap: 12, marginTop: 8, fontSize: 11 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <div style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(239,68,68,.3)' }} /><span style={{ color: '#cbd5e1' }}>Critical</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <div style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(245,158,11,.2)' }} /><span style={{ color: '#cbd5e1' }}>Watch</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <div style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(34,197,94,.15)' }} /><span style={{ color: '#cbd5e1' }}>Managed</span>
        </div>
      </div>
    </div>
  );
}

function PanelRecommendation({ color, bg, bd, text }: { color: string; bg: string; bd: string; text: string }) {
  return (
    <div style={{ marginTop: 12, padding: '10px 12px', background: bg, border: `1px solid ${bd}`, borderRadius: 8 }}>
      <div style={{ fontSize: 12, color, fontWeight: 600 }}>⚡ Signal Recommendation</div>
      <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 4 }}>{text}</div>
    </div>
  );
}

function PanelEmptyState({ loading, error, label }: { loading: boolean; error: boolean; label: string }) {
  if (error) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: 'rgba(239,68,68,.06)', border: '1px solid rgba(239,68,68,.15)', borderRadius: 8 }}>
        <div style={{ fontSize: 12, color: '#f87171', textAlign: 'center', padding: 16 }}>
          {label} endpoint unavailable
        </div>
      </div>
    );
  }
  return (
    <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <span style={{ fontSize: 12, color: '#94a3b8' }}>{loading ? 'Loading…' : 'No data yet'}</span>
    </div>
  );
}

function FeedItem({ item }: { item: SignalFeedItem }) {
  const palette =
    item.severity === 'critical' ? { bg: 'rgba(239,68,68,.06)',  bd: 'rgba(239,68,68,.2)',  dotC: '#ef4444', fg: '#f87171', label: 'ALERT'    } :
    item.severity === 'high'     ? { bg: 'rgba(239,68,68,.06)',  bd: 'rgba(239,68,68,.2)',  dotC: '#ef4444', fg: '#f87171', label: 'ALERT'    } :
    item.severity === 'medium'   ? { bg: 'rgba(245,158,11,.06)', bd: 'rgba(245,158,11,.2)', dotC: '#f59e0b', fg: '#fbbf24', label: 'FORECAST' } :
                                   { bg: 'rgba(59,130,246,.06)', bd: 'rgba(59,130,246,.2)', dotC: '#3b82f6', fg: '#60a5fa', label: 'INFO'    };
  return (
    <div style={{
      padding: '14px 16px', borderRadius: 10,
      background: palette.bg, border: `1px solid ${palette.bd}`,
      animation: 'slideIn .4s ease both',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ ...dot(palette.dotC), width: 6, height: 6, animation: 'pulse 2s infinite' }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>{item.title}</span>
        </div>
        <span style={{ ...mono, fontSize: 11, fontWeight: 700, color: palette.dotC }}>{palette.label}</span>
      </div>
      <div style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.55 }}>{item.detail}</div>
      <div style={{ ...mono, fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
        {formatHHMM(item.timestamp)} · Signal Model: {modelTagFor(item.use_case)} · {item.agent}
      </div>
    </div>
  );
}

function JibBurnRow({ j }: { j: JibBurnEntry }) {
  const palette = j.status === 'overrun'
    ? { bg: 'rgba(239,68,68,.06)', bd: 'rgba(239,68,68,.15)', fg: '#f87171', barFrom: '#ef4444', barTo: '#f87171' }
    : { bg: 'rgba(34,197,94,.04)', bd: 'rgba(34,197,94,.10)', fg: '#4ade80', barFrom: '#22c55e', barTo: '#4ade80' };
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '10px 12px', background: palette.bg, border: `1px solid ${palette.bd}`, borderRadius: 8,
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: '#f9fafb' }}>
            {j.name} · {j.afe_id}
          </span>
          <span style={{ fontSize: 12, fontWeight: 700, color: palette.fg }}>{j.pct}% of AFE</span>
        </div>
        <div style={{ height: 5, borderRadius: 99, background: 'rgba(255,255,255,.06)', overflow: 'hidden' }}>
          <div style={{
            height: '100%', borderRadius: 99,
            width: `${Math.min(100, j.pct)}%`,
            background: `linear-gradient(90deg, ${palette.barFrom}, ${palette.barTo})`,
          }} />
        </div>
        <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 4 }}>{j.detail}</div>
      </div>
    </div>
  );
}

function formatHHMM(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  } catch {
    return iso;
  }
}

function modelTagFor(useCase: string): string {
  if (useCase.includes('tariff'))   return 'FERCForecast-v1.4';
  if (useCase.includes('jib'))      return 'JIBBurnRate-v1.0';
  if (useCase.includes('invoice'))  return 'VendorDrift-v2.1';
  if (useCase === 'po_contract' || useCase === 'non_po_msa')  return 'ContractRisk-v1.2';
  return 'Signal-v1.0';
}
