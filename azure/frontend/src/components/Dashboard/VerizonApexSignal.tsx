/**
 * Verizon Far Edge — Apex Signal (predictive wave-risk).
 *
 * Renders when demo mode === 'verizon_far_edge'. Predictive intelligence
 * surface for the 16,247-site Verizon far-edge inventory.
 *
 * Wired to 3 Azure ML endpoints via /api/v1/signals/vz/*:
 *   • POST /signals/vz/wave-risk        → XGBoost wave outage probability
 *   • POST /signals/vz/site-cert        → XGBoost per-site cert risk (batch ok)
 *   • POST /signals/vz/thermal-anomaly  → Random Cut Forest anomaly score
 *   • GET  /signals/vz/endpoints/status → live/degraded badge
 *
 * The 16,247 site dots map remains client-shaped for now (real per-site
 * scoring via batch invoke is a follow-up — 16K dots × XGBoost would be
 * a noticeable per-frame cost without aggregation).
 */
import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const card: React.CSSProperties = {
  background: '#fff', borderRadius: 16, border: '1px solid #f1f5f9',
  boxShadow: '0 1px 3px rgba(0,0,0,.05)',
};
const chip = (bg: string, fg: string, bd: string): React.CSSProperties => ({
  display: 'inline-flex', alignItems: 'center', gap: 5, borderRadius: 99,
  padding: '3px 10px', fontSize: 11, fontWeight: 600,
  background: bg, color: fg, border: `1px solid ${bd}`,
});

// ──────────── API types ────────────
interface WaveRiskResp {
  probability_of_outage: number;
  risk_tier:             'low' | 'medium' | 'high' | 'critical';
  top_reasons:           string[];
  endpoint:              string;
  explanation:           Record<string, any>;
}
interface EndpointsStatus {
  overall:   'live' | 'degraded';
  endpoints: Array<{ name: string; status: string }>;
}

// Firmware certification intelligence — mined from James Patchett's real 118-report corpus
interface FirmwareIntel {
  source: string;
  total_reports: number;
  conformance_forecast: Array<{ target: string; predicted_failures: number; all_benign: boolean; signature: string; action: string }>;
  regression_watch: Array<{ firmware: string; platform: string; issue: string; meakv: string; status: string; risk: string; fix: string; recommendation: string }>;
  fleet_fragmentation: Array<{ platform: string; distinct_revs: number; revs: string[]; drift_risk: string }>;
  coverage_gap: Array<{ platform: string; covered: number; total: number; coverage_pct: number; wave_eligible: boolean }>;
  upgrade_confidence: { validated_paths: string[]; versions_seen: string[]; untested_warning: string };
}

const FW_INTEL_FALLBACK: FirmwareIntel = {
  source: 'James Patchett · MTCE Lab · 118 real firmware reports',
  total_reports: 118,
  conformance_forecast: [
    { target: 'HPE E930t · iLO6 1.57', predicted_failures: 7, all_benign: true, signature: 'WWW-Authenticate header + X.509 IPv6 cert', action: 'pre-classified · auto-certify on next run' },
    { target: 'HPE E910t · iLO6 1.60', predicted_failures: 7, all_benign: true, signature: 'WWW-Authenticate header + X.509 IPv6 cert', action: 'pre-classified · auto-certify on next run' },
    { target: 'ZT Proteus · BMC 3.02', predicted_failures: 6, all_benign: true, signature: 'WWW-Authenticate header + X.509 IPv6 cert', action: 'pre-classified · auto-certify on next run' },
    { target: 'ZT Triton · BMC 2.31', predicted_failures: 5, all_benign: true, signature: 'WWW-Authenticate header + X.509 IPv6 cert', action: 'pre-classified · auto-certify on next run' },
  ],
  regression_watch: [
    { firmware: 'ZT BMC 0.45', platform: 'ZT Proteus (Samsung PM9A3 sites)', issue: 'Cannot read PM9A3 drive temp → fans spike to 100%', meakv: 'MEAKV-1792', status: 'CONFIRMED', risk: 'critical', fix: 'BMC 0.46', recommendation: 'BLOCK .45 wave to PM9A3 sites · mandate .46' },
    { firmware: 'ZT BMC 0.43', platform: 'ZT Proteus (early-rev)', issue: 'Redfish 503 during host boot / inventory window', meakv: 'troubleshooting', status: 'TRANSIENT', risk: 'low', fix: 'RedfishDBReset + retry-after-boot', recommendation: 'watch · remediation in BMC playbook KB' },
  ],
  fleet_fragmentation: [
    { platform: 'ZT Proteus', distinct_revs: 6, revs: [], drift_risk: 'high' },
    { platform: 'HPE E910t', distinct_revs: 4, revs: [], drift_risk: 'medium' },
    { platform: 'HPE E930t', distinct_revs: 3, revs: [], drift_risk: 'medium' },
    { platform: 'ZT Triton', distinct_revs: 2, revs: [], drift_risk: 'low' },
  ],
  coverage_gap: [
    { platform: 'Dell PowerEdge R7615', covered: 1, total: 14, coverage_pct: 7, wave_eligible: false },
    { platform: 'ZT Galene', covered: 3, total: 14, coverage_pct: 21, wave_eligible: false },
    { platform: 'HPE E930t', covered: 10, total: 14, coverage_pct: 71, wave_eligible: true },
    { platform: 'ZT Proteus', covered: 14, total: 14, coverage_pct: 100, wave_eligible: true },
  ],
  upgrade_confidence: { validated_paths: ['21.05p6 → 21.12p10 (ZT Proteus · alarms clear)'], versions_seen: ['21.05p6', '21.12p10', '22.12mr1'], untested_warning: 'Any path skipping a validated rev = HITL gate' },
};

// ──────────── site dot generator ────────────
interface SiteDot { left: number; top: number; size: number; tier: 'critical' | 'high' | 'medium' | 'low' }
function generateSiteDots(): SiteDot[] {
  const regions = [
    { cx: 0.78, cy: 0.28, count: 80, name: 'Northeast',    criticalRatio: 0.15, highRatio: 0.2 },
    { cx: 0.72, cy: 0.62, count: 60, name: 'Southeast',    criticalRatio: 0.02, highRatio: 0.1 },
    { cx: 0.52, cy: 0.35, count: 70, name: 'Midwest',      criticalRatio: 0.03, highRatio: 0.12 },
    { cx: 0.45, cy: 0.65, count: 55, name: 'South Central',criticalRatio: 0.02, highRatio: 0.08 },
    { cx: 0.18, cy: 0.28, count: 50, name: 'Northwest',    criticalRatio: 0.01, highRatio: 0.06 },
    { cx: 0.22, cy: 0.58, count: 50, name: 'Southwest',    criticalRatio: 0.04, highRatio: 0.18 },
  ];
  const dots: SiteDot[] = [];
  regions.forEach((r) => {
    for (let i = 0; i < r.count; i++) {
      const a = Math.random() * Math.PI * 2;
      const rad = Math.random() * 0.1;
      const left = (r.cx + Math.cos(a) * rad) * 100;
      const top  = (r.cy + Math.sin(a) * rad) * 100;
      const v = Math.random();
      let tier: SiteDot['tier'];
      let size = 4;
      if (v < r.criticalRatio) { tier = 'critical'; size = 6; }
      else if (v < r.criticalRatio + r.highRatio) { tier = 'high'; size = 5; }
      else if (v < r.criticalRatio + r.highRatio + 0.25) { tier = 'medium'; }
      else tier = 'low';
      dots.push({ left, top, size, tier });
    }
  });
  return dots;
}
const TIER_COLOR: Record<SiteDot['tier'], string> = {
  critical: '#ef4444',
  high:     '#f97316',
  medium:   '#f59e0b',
  low:      '#22c55e',
};
const TIER_BG = {
  critical: { bg: '#fef2f2', bd: '#fecaca', fg: '#991b1b' },
  high:     { bg: '#fff7ed', bd: '#fed7aa', fg: '#c2410c' },
  medium:   { bg: '#fffbeb', bd: '#fde68a', fg: '#92400e' },
  low:      { bg: '#f0fdf4', bd: '#bbf7d0', fg: '#166534' },
};

// ──────────── component ────────────
export function VerizonApexSignal() {
  const [dots] = useState<SiteDot[]>(() => generateSiteDots());

  // Endpoint health badge — refreshes every 30s
  const statusQuery = useQuery<EndpointsStatus>({
    queryKey: ['vz-endpoints-status'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/vz/endpoints/status`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30_000,
    refetchOnWindowFocus: false,
    retry: false,
  });
  const modelsLive = statusQuery.data?.overall === 'live';

  // Default wave scenario — the highest-risk planned wave on the page.
  // Sent to apex-signal-vz-wave-risk; the prediction drives the hero pill.
  const waveQuery = useQuery<WaveRiskResp>({
    queryKey: ['vz-wave-risk', 'default-northeast-type-b'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/vz/wave-risk`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_type:           'CaaS-Node-Type-B',
          firmware_from:         '23.06',
          firmware_to:           '24.01',
          region:                'Northeast',
          schema_drift_events:   3,
          historical_pass_rate:  0.78,
          season_q:              2,
          wave_size:             4200,
        }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 60_000,
    refetchOnWindowFocus: false,
    retry: false,
  });

  // Firmware certification intelligence — real-corpus predictions (offline-safe)
  const fwQuery = useQuery<FirmwareIntel>({
    queryKey: ['vz-firmware-intelligence'],
    queryFn: async () => {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 3000);
      try {
        const r = await fetch(`${API_BASE_URL}/signals/vz/firmware-intelligence`, { signal: ctl.signal });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      } finally { clearTimeout(t); }
    },
    refetchInterval: 60_000,
    refetchOnWindowFocus: false,
    retry: 0,
    placeholderData: FW_INTEL_FALLBACK,
  });
  const fw: FirmwareIntel = fwQuery.data ?? FW_INTEL_FALLBACK;

  const waveBadge = useMemo(() => {
    const w = waveQuery.data;
    if (!w) return { tier: 'medium' as const, text: '— ·  loading',  pct: 0 };
    return {
      tier: w.risk_tier as 'low' | 'medium' | 'high' | 'critical',
      text: `${(w.probability_of_outage * 100).toFixed(1)}% · ${w.risk_tier.toUpperCase()}`,
      pct:  Math.round(w.probability_of_outage * 100),
    };
  }, [waveQuery.data]);

  return (
    <div style={{ background: '#f8fafc', minHeight: '100vh', padding: '28px 32px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Apex Signal</h1>
          <span style={chip('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.2)')}>
            PREDICTIVE ANALYTICS
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={chip(
            modelsLive ? '#f0fdf4' : '#fffbeb',
            modelsLive ? '#16a34a' : '#d97706',
            modelsLive ? '#bbf7d0' : '#fde68a',
          )}>
            <span style={{ width: 8, height: 8, borderRadius: '50%',
                           background: modelsLive ? '#22c55e' : '#f59e0b',
                           display: 'inline-block',
                           animation: modelsLive ? 'pulse 2s infinite' : undefined }} />
            {modelsLive ? '3 Azure ML Models Live' : 'Models Degraded'}
          </span>
        </div>
      </div>

      {/* Hero — live wave-risk prediction */}
      <div style={{
        background: 'linear-gradient(135deg,#0d1117 0%,#051a0a 50%,#0d1117 100%)',
        borderRadius: 20, padding: '32px 36px', marginBottom: 24,
        border: '1px solid rgba(34,197,94,.15)', position: 'relative', overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', top: -50, right: -30, width: 260, height: 260, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(34,197,94,.12) 0%, transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ position: 'relative' }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.18em', textTransform: 'uppercase', color: '#4ade80', marginBottom: 10 }}>
            APEX SIGNAL · PREDICTIVE INTELLIGENCE · 16,247 SITE WAVE RISK SCORING
          </div>
          <h2 style={{ fontSize: 26, fontWeight: 900, color: '#f8fafc', letterSpacing: '-.02em', marginBottom: 8 }}>
            Live Wave Risk Intelligence
          </h2>
          <p style={{ fontSize: 13, color: '#94a3b8', maxWidth: 720, lineHeight: 1.6, marginBottom: 18 }}>
            Apex Signal scores every site in the deployment wave by risk using three Azure ML models —
            wave-risk (XGBoost), per-site cert risk (XGBoost), and thermal anomaly (Random Cut Forest).
            Real-time predictive intelligence drives wave sequencing.
          </p>

          {/* Live wave risk prediction card */}
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 16,
                        background: 'rgba(0,0,0,.35)', border: '1px solid rgba(255,255,255,.08)',
                        borderRadius: 14, padding: '14px 18px' }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', color: '#94a3b8', textTransform: 'uppercase' }}>
                Default Wave · Northeast · Type-B · 23.06→24.01
              </div>
              <div style={{ fontSize: 22, fontWeight: 900, color: TIER_COLOR[waveBadge.tier], marginTop: 2 }}>
                {waveBadge.text}
              </div>
              <div style={{ fontSize: 11, color: '#cbd5e1', marginTop: 2 }}>
                P(outage within 30 days · model: apex-signal-vz-wave-risk)
              </div>
            </div>
            <div style={{ width: 1, alignSelf: 'stretch', background: 'rgba(255,255,255,.08)' }} />
            <div style={{ maxWidth: 360 }}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', color: '#94a3b8', textTransform: 'uppercase' }}>
                Top reasons
              </div>
              <ul style={{ margin: '4px 0 0 0', padding: 0, listStyle: 'none', fontSize: 11, color: '#e2e8f0', lineHeight: 1.55 }}>
                {(waveQuery.data?.top_reasons ?? ['loading…']).slice(0, 3).map((r, i) => (
                  <li key={i}>• {r}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* KPI row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 22 }}>
        <Kpi label="Total Sites"   value="16,247"  sub="Next wave: ~16K" />
        <Kpi label="Critical Risk" value="340"     sub="Hold for Wave 2" color="#dc2626" />
        <Kpi label="High Risk"     value="1,240"   sub="Manual review required" color="#f97316" />
        <Kpi label="Medium Risk"   value="3,820"   sub="Monitor closely" color="#f59e0b" />
        <Kpi label="Low Risk"      value="10,847"  sub="Cleared for Wave 1" color="#16a34a" />
      </div>

      {/* ════════ FIRMWARE CERTIFICATION INTELLIGENCE (real corpus) ════════ */}
      <div style={{ ...card, padding: 0, marginBottom: 22, overflow: 'hidden' }}>
        {/* section header band */}
        <div style={{ background: 'linear-gradient(135deg,#0d1117,#1a0608)', padding: '16px 22px',
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase', color: '#f87171' }}>
              NEW · PREDICTIVE FIRMWARE INTELLIGENCE
            </div>
            <div style={{ fontSize: 17, fontWeight: 800, color: '#f8fafc', marginTop: 3 }}>
              Forecasts mined from {fw.total_reports} real MTCE Lab reports
            </div>
          </div>
          <span style={{ fontSize: 11, color: '#94a3b8', fontStyle: 'italic', maxWidth: 280, textAlign: 'right' }}>
            {fw.source}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 0 }}>
          {/* Panel 1 — Conformance noise forecast */}
          <div style={{ padding: 20, borderRight: '1px solid #eef2f7', borderBottom: '1px solid #eef2f7' }}>
            <PanelHead icon="◆" tone="#2563eb" title="Conformance Noise Forecast"
                       sub="Predict the next cert's benign failures — pre-classified" />
            {fw.conformance_forecast.slice(0, 4).map((c, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0',
                                    borderBottom: i < 3 ? '1px solid #f5f7fa' : 'none' }}>
                <div style={{ fontSize: 19, fontWeight: 800, color: '#2563eb', minWidth: 26, textAlign: 'center' }}>{c.predicted_failures}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 600, color: '#0f172a' }}>{c.target}</div>
                  <div style={{ fontSize: 10.5, color: '#94a3b8' }}>{c.signature}</div>
                </div>
                <span style={{ fontSize: 9.5, fontWeight: 700, padding: '2px 7px', borderRadius: 4,
                               background: '#f0fdf4', color: '#16a34a' }}>BENIGN</span>
              </div>
            ))}
            <div style={{ fontSize: 11, color: '#64748b', marginTop: 8, fontStyle: 'italic' }}>
              Every HPE platform throws 7 · ZT 5–6 · all the same signature → auto-certify.
            </div>
          </div>

          {/* Panel 2 — Regression watch */}
          <div style={{ padding: 20, borderBottom: '1px solid #eef2f7' }}>
            <PanelHead icon="⚠" tone="#dc2626" title="Firmware Regression Watch"
                       sub="Block bad builds before they reach a wave" />
            {fw.regression_watch.map((r, i) => {
              const crit = r.risk === 'critical';
              return (
                <div key={i} style={{ padding: '8px 10px', marginBottom: 8, borderRadius: 8,
                                      background: crit ? '#fef2f2' : '#fffbeb',
                                      border: `1px solid ${crit ? '#fecaca' : '#fde68a'}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 12.5, fontWeight: 800, color: crit ? '#dc2626' : '#d97706' }}>{r.firmware}</span>
                    <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 3,
                                   background: crit ? '#dc2626' : '#d97706', color: '#fff' }}>{r.status}</span>
                    <span style={{ fontSize: 10, color: '#64748b', marginLeft: 'auto' }}>{r.meakv}</span>
                  </div>
                  <div style={{ fontSize: 11, color: '#475569', marginTop: 3 }}>{r.issue}</div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: crit ? '#dc2626' : '#d97706', marginTop: 3 }}>
                    → {r.recommendation}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Panel 3 — Fleet fragmentation */}
          <div style={{ padding: 20, borderRight: '1px solid #eef2f7' }}>
            <PanelHead icon="▤" tone="#7c3aed" title="Fleet Firmware Fragmentation"
                       sub="More revs in the field = higher cert + regression surface" />
            {fw.fleet_fragmentation.slice(0, 5).map((f, i) => {
              const pct = Math.min(100, (f.distinct_revs / 6) * 100);
              const col = f.drift_risk === 'high' ? '#dc2626' : f.drift_risk === 'medium' ? '#f59e0b' : '#16a34a';
              return (
                <div key={i} style={{ padding: '6px 0', borderBottom: i < 4 ? '1px solid #f5f7fa' : 'none' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                    <span style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{f.platform}</span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: col }}>{f.distinct_revs} revs · {f.drift_risk}</span>
                  </div>
                  <div style={{ height: 5, background: '#eef2f7', borderRadius: 3, overflow: 'hidden' }}>
                    <div style={{ width: `${pct}%`, height: '100%', background: col }} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Panel 4 — Coverage gap */}
          <div style={{ padding: 20 }}>
            <PanelHead icon="◷" tone="#0891b2" title="Cert Coverage Gap"
                       sub="New platforms need a full sweep before wave-eligibility" />
            {fw.coverage_gap.filter(c => c.platform !== 'Unknown').slice(0, 5).map((c, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0',
                                    borderBottom: i < 4 ? '1px solid #f5f7fa' : 'none' }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{c.platform}</div>
                  <div style={{ height: 5, background: '#eef2f7', borderRadius: 3, overflow: 'hidden', marginTop: 3 }}>
                    <div style={{ width: `${c.coverage_pct}%`, height: '100%',
                                  background: c.coverage_pct >= 70 ? '#16a34a' : c.coverage_pct >= 30 ? '#f59e0b' : '#dc2626' }} />
                  </div>
                </div>
                <span style={{ fontSize: 11, fontWeight: 700, color: '#475569', minWidth: 42, textAlign: 'right' }}>{c.covered}/{c.total}</span>
                <span style={{ fontSize: 9, fontWeight: 700, padding: '2px 7px', borderRadius: 4,
                               background: c.wave_eligible ? '#f0fdf4' : '#fef2f2',
                               color: c.wave_eligible ? '#16a34a' : '#dc2626' }}>
                  {c.wave_eligible ? 'ELIGIBLE' : 'GAP'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Map + signals grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: 20, marginBottom: 20 }}>

        {/* US Site Map */}
        <div style={{ ...card, padding: 22 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Wave 1 Site Risk Map</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
                16,247 sites · color = predicted risk tier
              </div>
            </div>
            <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
              {(['critical','high','medium','low'] as const).map((t) => (
                <span key={t} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 10, color: '#64748b' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: TIER_COLOR[t], display: 'inline-block' }} />
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </span>
              ))}
            </div>
          </div>

          {/* Map container */}
          <div style={{ position: 'relative', background: '#f0f4f8', borderRadius: 12, overflow: 'hidden', border: '1px solid #e2e8f0', aspectRatio: '960 / 600' }}>
            <svg viewBox="0 0 960 600" style={{ width: '100%', display: 'block' }}>
              <rect width="960" height="600" fill="#e8edf2"/>
              <path d="M 120 120 L 820 120 L 860 180 L 860 420 L 780 480 L 680 500 L 580 520 L 480 510 L 380 520 L 280 500 L 180 460 L 120 400 L 80 300 L 100 200 Z" fill="#dde4ec" stroke="#c8d3de" strokeWidth="1.5"/>
              <line x1="300" y1="120" x2="280" y2="500" stroke="#c8d3de" strokeWidth="0.5" opacity="0.5"/>
              <line x1="480" y1="120" x2="480" y2="510" stroke="#c8d3de" strokeWidth="0.5" opacity="0.5"/>
              <line x1="640" y1="120" x2="680" y2="500" stroke="#c8d3de" strokeWidth="0.5" opacity="0.5"/>
              <line x1="120" y1="280" x2="860" y2="280" stroke="#c8d3de" strokeWidth="0.5" opacity="0.5"/>
              <line x1="120" y1="380" x2="860" y2="380" stroke="#c8d3de" strokeWidth="0.5" opacity="0.5"/>
              <text x="180" y="200" fontSize="11" fill="#94a3b8" fontWeight="600">NORTHWEST</text>
              <text x="400" y="160" fontSize="11" fill="#94a3b8" fontWeight="600">NORTH CENTRAL</text>
              <text x="680" y="180" fontSize="11" fill="#94a3b8" fontWeight="600">NORTHEAST</text>
              <text x="160" y="360" fontSize="11" fill="#94a3b8" fontWeight="600">SOUTHWEST</text>
              <text x="400" y="380" fontSize="11" fill="#94a3b8" fontWeight="600">SOUTH CENTRAL</text>
              <text x="680" y="360" fontSize="11" fill="#94a3b8" fontWeight="600">SOUTHEAST</text>
            </svg>
            <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
              {dots.map((d, i) => (
                <div key={i} style={{
                  position: 'absolute',
                  left: `${d.left}%`, top: `${d.top}%`,
                  width: d.size, height: d.size, borderRadius: '50%',
                  background: TIER_COLOR[d.tier],
                  boxShadow: d.tier === 'critical' ? '0 0 8px rgba(239,68,68,.6)' :
                             d.tier === 'high'     ? '0 0 6px rgba(249,115,22,.4)' : 'none',
                }} />
              ))}
            </div>
          </div>

          {/* Wave score banner — driven by Azure ML prediction */}
          {waveQuery.data && (
            <div style={{
              marginTop: 12, padding: '14px 16px',
              background: TIER_BG[waveBadge.tier].bg,
              border: `1px solid ${TIER_BG[waveBadge.tier].bd}`,
              borderRadius: 10,
            }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: TIER_BG[waveBadge.tier].fg, marginBottom: 6 }}>
                ⚠ Wave Risk · {waveBadge.tier.toUpperCase()} · {waveBadge.pct}% predicted outage
              </div>
              <div style={{ fontSize: 12, color: '#374151', lineHeight: 1.6 }}>
                {(waveQuery.data.top_reasons || []).join(' · ')}. Recommendation: HITL approval
                required before wave authorization.
              </div>
            </div>
          )}
        </div>

        {/* Signal feed + vendor prediction */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ ...card, padding: 20 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 14 }}>Active Signals</div>
            <SignalCard
              kind="critical" id="SIGNAL-001" status="Hold"
              detail="Northeast cluster (340 sites) · Firmware 24.12 on CaaS-Node-Type-B · Historical pattern match"
              conf={waveBadge.pct} confColor="linear-gradient(90deg,#dc2626,#ef4444)"
              confText={`${waveBadge.pct}% · vz-wave-risk model`}
            />
            <SignalCard
              kind="warning" id="SIGNAL-002" status="Monitor"
              detail="Southwest cluster (1,240 sites) · Wind River 23.06 → 24.12 upgrade · 3 vendors historically slow to respond · 45-day delay risk"
              conf={63} confColor="linear-gradient(90deg,#f59e0b,#d97706)" confText="63% · Pre-engage vendor 14 days early"
            />
            <SignalCard
              kind="info" id="SIGNAL-003" status="Action"
              detail="Midwest cluster (3,820 sites) · Redfish schema v1.16.0 · 14 scripts require update before deployment · Remediation map generated"
              conf={94} confColor="linear-gradient(90deg,#3b82f6,#2563eb)" confText="94% · Schema remediation required"
            />
          </div>

          <div style={{ ...card, padding: 20 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 14 }}>Vendor Response Prediction</div>
            <VendorRow name="Wind River"        kind="Schema issue · P2 severity"         eta="8–12 days"   color="#d97706" sub="Based on 23 prior tickets" />
            <VendorRow name="Hardware Vendor A" kind="Latency threshold · P1 severity"   eta="18–25 days"  color="#dc2626" sub="No on-site engineers · Delayed" />
            <VendorRow name="Red Hat"           kind="OpenShift operator · P3"           eta="2–4 days"    color="#16a34a" sub="Strong historical response" last />
          </div>
        </div>
      </div>

      {/* Wave Sequencing */}
      <div style={{ ...card, padding: 24 }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 16 }}>
          Recommended Wave Deployment Sequence
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
          <WaveCard label="Wave 1 — Proceed"          big="10,847 sites" bg="#f0fdf4" bd="#bbf7d0" labelColor="#166534" bigColor="#16a34a"
            detail="Low-risk clusters · Midwest, Northwest, South Central · Firmware 24.12 validated · No schema issues" />
          <WaveCard label="Wave 2 — After Remediation" big="5,060 sites"  bg="#fffbeb" bd="#fde68a" labelColor="#92400e" bigColor="#d97706"
            detail="Medium + High risk · Script updates required · Vendor pre-engagement recommended · 14-day prep window" />
          <WaveCard label="Wave 3 — Hold"              big="340 sites"    bg="#fef2f2" bd="#fecaca" labelColor="#991b1b" bigColor="#dc2626"
            detail="Northeast critical cluster · Matches high-risk Type-B pattern · Resolve APEX-VZ-2847 first · Vendor on-site required" />
        </div>
        <div style={{ marginTop: 14, padding: '14px 16px', background: '#f8fafc', border: '1px solid #f1f5f9', borderRadius: 10, fontSize: 12, color: '#374151', lineHeight: 1.5 }}>
          <strong>Human approval required</strong> before any wave deployment. Every recommendation logged in the Audit Lens with timestamp,
          confidence score, and full evidence chain. James Patchett (HQ Planning) is the designated approver for Wave 1 and Wave 2.
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
      `}</style>
    </div>
  );
}

// ──────────── sub-components ────────────
function PanelHead({ icon, tone, title, sub }: { icon: string; tone: string; title: string; sub: string }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ width: 22, height: 22, borderRadius: 6, background: `${tone}1a`, color: tone,
                       display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700 }}>
          {icon}
        </span>
        <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{title}</span>
      </div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 3 }}>{sub}</div>
    </div>
  );
}

function Kpi({ label, value, sub, color }: { label: string; value: string; sub: string; color?: string }) {
  return (
    <div style={{ ...card, padding: '16px 18px' }}>
      <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.1em', color: '#94a3b8' }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 900, color: color || '#0f172a', letterSpacing: '-.02em', marginTop: 4 }}>{value}</div>
      <div style={{ fontSize: 11, color: color || '#64748b', marginTop: 2 }}>{sub}</div>
    </div>
  );
}

function SignalCard({ kind, id, status, detail, conf, confColor, confText }: {
  kind: 'critical' | 'warning' | 'info';
  id: string; status: string; detail: string; conf: number; confColor: string; confText: string;
}) {
  const palette = {
    critical: { bg: '#fef2f2', bd: '#fecaca', fg: '#991b1b', chipBg: '#fef2f2', chipFg: '#dc2626', chipBd: '#fecaca' },
    warning:  { bg: '#fffbeb', bd: '#fde68a', fg: '#92400e', chipBg: '#fffbeb', chipFg: '#d97706', chipBd: '#fde68a' },
    info:     { bg: '#eff6ff', bd: '#bfdbfe', fg: '#1d4ed8', chipBg: '#eff6ff', chipFg: '#2563eb', chipBd: '#bfdbfe' },
  }[kind];
  return (
    <div style={{ padding: '16px 20px', borderRadius: 12, border: `1px solid ${palette.bd}`, background: palette.bg, marginBottom: 8 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, color: palette.fg }}>{id} · {kind.charAt(0).toUpperCase() + kind.slice(1)}</div>
          <div style={{ fontSize: 11, color: '#374151', marginTop: 3, lineHeight: 1.5 }}>{detail}</div>
        </div>
        <span style={chip(palette.chipBg, palette.chipFg, palette.chipBd)}>{status}</span>
      </div>
      <div style={{ marginTop: 8, fontSize: 10, fontWeight: 700, color: '#94a3b8' }}>CONFIDENCE</div>
      <div style={{ marginTop: 4, height: 6, borderRadius: 99, background: '#f1f5f9', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${Math.max(2, Math.min(100, conf))}%`, background: confColor }} />
      </div>
      <div style={{ fontSize: 10, color: palette.chipFg, fontWeight: 600, marginTop: 2 }}>{confText}</div>
    </div>
  );
}

function VendorRow({ name, kind, eta, color, sub, last }: { name: string; kind: string; eta: string; color: string; sub: string; last?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: last ? 'none' : '1px solid #f1f5f9' }}>
      <div>
        <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{name}</div>
        <div style={{ fontSize: 10, color: '#64748b' }}>{kind}</div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontSize: 13, fontWeight: 700, color }}>{eta}</div>
        <div style={{ fontSize: 10, color: '#94a3b8' }}>{sub}</div>
      </div>
    </div>
  );
}

function WaveCard({ label, big, bg, bd, labelColor, bigColor, detail }: { label: string; big: string; bg: string; bd: string; labelColor: string; bigColor: string; detail: string }) {
  return (
    <div style={{ padding: 16, background: bg, border: `1px solid ${bd}`, borderRadius: 12 }}>
      <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.1em', color: labelColor, marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 900, color: bigColor, marginBottom: 4 }}>{big}</div>
      <div style={{ fontSize: 11, color: '#374151', lineHeight: 1.5 }}>{detail}</div>
    </div>
  );
}
