/**
 * CwfcuApexSignal — predictive intelligence + forward-looking forecast view.
 *
 * Layout mirrors /Users/babbu/Downloads/demo6-cwfcu/signal.html:
 *   • Header: "APEX Signal — Forward-Looking Intelligence"
 *   • 3-panel grid: Vendor Rate Drift · NCUA Regulatory Monitor · Exam Readiness Forecast
 *   • Live Signal Feed grid (6 tiles)
 *
 * Charts use Recharts (already in the platform — no extra deps).
 * All data from /api/v1/cwfcu/dashboard-state.
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import { useCwfcuToast, postCwfcuAction } from './cwfcuToast';
import { useProductBrand, brandLabel } from '@/lib/productBrand';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface DashboardState {
  signal_hero: {
    days_to_exam: number;
    exam_date: string;
    readiness_pct: number;
    active_signals: number;
    critical_signals: number;
    updated_minutes_ago: number;
  };
  vendor_drift: {
    chart_labels: string[];
    vendors: Array<{
      name: string; series: number[]; color: string;
      current_drift_pct: number; renewal_days: number; alert_tone: string;
    }>;
    contract_limit_pct: number;
    alert_count: number;
  };
  regulatory: Array<{
    severity: string; effective: string; title: string; description: string;
    action_required: string | null; tone: string;
  }>;
  exam_trajectory: {
    chart_labels: string[];
    actual_series: (number | null)[];
    projected_series: (number | null)[];
    target_series: number[];
    folder_bars: Array<{ name: string; pct: number; color: string }>;
    on_track: boolean;
  };
  signal_feed: Array<{
    tone: string; agent: string; title: string; detail: string;
  }>;
}

const fmtUsd = (n: number): string =>
  n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(1)}M`
  : n >= 1_000   ? `$${(n / 1_000).toFixed(0)}K`
  : `$${n.toLocaleString()}`;

const driftAlertBg = (tone: string): string =>
  tone === 'red' ? '#fef2f2' : tone === 'amber' ? '#fffbeb' : '#f0fdf4';
const driftAlertColor = (tone: string): string =>
  tone === 'red' ? '#ef4444' : tone === 'amber' ? '#d97706' : '#16a34a';

const regTileBg = (tone: string): string =>
  tone === 'red' ? '#fef2f2' : tone === 'amber' ? '#fffbeb' : '#f0fdf4';
const regTileBorder = (tone: string): string =>
  tone === 'red' ? '#fecaca' : tone === 'amber' ? '#fde68a' : '#bbf7d0';
const regTileTextColor = (tone: string): string =>
  tone === 'red' ? '#ef4444' : tone === 'amber' ? '#d97706' : '#16a34a';

const feedToneBg = (tone: string): string =>
  tone === 'alert'    ? '#fef2f2'
: tone === 'warning'  ? '#fffbeb'
: tone === 'clear'    ? '#f0fdf4'
: tone === 'approved' ? '#f0fdf4'
: '#faf5ff';
const feedToneBorder = (tone: string): string =>
  tone === 'alert'    ? '#fecaca'
: tone === 'warning'  ? '#fde68a'
: tone === 'clear'    ? '#bbf7d0'
: tone === 'approved' ? '#bbf7d0'
: '#e9d5ff';
const feedToneLabel = (tone: string): string =>
  tone === 'alert'    ? 'ALERT'
: tone === 'warning'  ? 'WARNING'
: tone === 'clear'    ? 'CLEAR'
: tone === 'approved' ? 'APPROVED'
: 'FORECAST';
const feedToneTextColor = (tone: string): string =>
  tone === 'alert'    ? '#ef4444'
: tone === 'warning'  ? '#d97706'
: tone === 'clear'    ? '#16a34a'
: tone === 'approved' ? '#16a34a'
: '#7c3aed';

export function CwfcuApexSignal() {
  const router = useRouter();
  const { Toast, push } = useCwfcuToast();
  const [brand] = useProductBrand();
  const signalName = brandLabel('Apex Signal', brand);   // → "Regulus Signal" when Regulus mode

  const q = useQuery<DashboardState>({
    queryKey: ['cwfcu-dashboard-state'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/cwfcu/dashboard-state`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30_000,
    retry: 1,
  });

  if (q.isLoading || !q.data) {
    return <div style={{ padding: 32, color: '#7a8fa6' }}>Loading {signalName}…</div>;
  }
  if (q.isError) {
    return <div style={{ padding: 32, color: '#dc2626' }}>Failed to load {signalName}.</div>;
  }
  const d = q.data;

  const onVendorClick = (vendorName: string) =>
    postCwfcuAction(`${API_BASE_URL}/cwfcu/vendors/${encodeURIComponent(vendorName.toLowerCase())}/renewal-brief`, push);

  const onRegulatoryClick = (title: string) =>
    postCwfcuAction(`${API_BASE_URL}/cwfcu/regulatory/${encodeURIComponent(title.replace(/\s+/g,'-').slice(0,40))}/open-gap-analysis`, push);

  const onSignalFeedClick = (tile: DashboardState['signal_feed'][0]) => {
    const tone = tile.tone;
    if (tone === 'alert' || tone === 'warning') {
      router.push('/review');
    } else if (tone === 'clear' || tone === 'approved') {
      router.push(`/agent-hub?agent=cwfcu-${tile.agent.split(' ')[0].toLowerCase()}-agent`);
    } else {
      router.push('/');
    }
  };

  // Build chart data
  const vendorChartData = d.vendor_drift.chart_labels.map((label, i) => {
    const row: Record<string, number | string> = { label, limit: d.vendor_drift.contract_limit_pct };
    d.vendor_drift.vendors.forEach((v) => { row[v.name] = v.series[i]; });
    return row;
  });
  const examChartData = d.exam_trajectory.chart_labels.map((label, i) => ({
    label,
    actual:    d.exam_trajectory.actual_series[i] ?? null,
    projected: d.exam_trajectory.projected_series[i] ?? null,
    target:    d.exam_trajectory.target_series[i],
  }));

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1f35' }}>
      <Toast />

      {/* HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div>
          <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 20, fontWeight: 800, color: '#0d1f35' }}>
            {signalName} — Forward-Looking Intelligence
          </div>
          <div style={{ fontSize: 12, color: '#7a8fa6', marginTop: 2 }}>
            Predictive alerts · Trend detection · Exam readiness forecasting · CommunityWide FCU
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            fontSize: 11, fontWeight: 700, background: '#faf5ff', color: '#7c3aed',
            border: '1px solid #e9d5ff', padding: '4px 12px', borderRadius: 20,
          }}>
            ● PREDICTIVE
          </span>
          <span style={{ fontSize: 11, color: '#9ca3af' }}>
            Updated {d.signal_hero.updated_minutes_ago} min ago
          </span>
        </div>
      </div>

      {/* THREE SIGNAL PANELS */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
        {/* Vendor Rate Drift */}
        <div style={panelStyle}>
          <div style={panelTitleRow}>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>Vendor Rate Drift</div>
            <span style={{ fontSize: 10, fontWeight: 700, background: '#fef2f2', color: '#ef4444', padding: '2px 8px', borderRadius: 4 }}>
              {d.vendor_drift.alert_count} ALERTS
            </span>
          </div>
          <div style={{ fontSize: 11, color: '#7a8fa6', marginBottom: 12 }}>
            Billed rates vs. contracted rate card — trailing 90 days
          </div>
          <div style={{ height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={vendorChartData} margin={{ top: 4, right: 10, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f2f5" />
                <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#9ca3af' }} />
                <YAxis tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={(v) => `${v}%`} />
                <Tooltip />
                {d.vendor_drift.vendors.map((v) => (
                  <Line key={v.name} type="monotone" dataKey={v.name} stroke={v.color} strokeWidth={2} dot={{ r: 2 }} />
                ))}
                <Line type="monotone" dataKey="limit" stroke="#e8ecf0" strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 12 }}>
            {d.vendor_drift.vendors.map((v) => (
              <div
                key={v.name}
                onClick={() => onVendorClick(v.name)}
                style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '6px 10px', background: driftAlertBg(v.alert_tone),
                  borderRadius: 6, borderLeft: `3px solid ${driftAlertColor(v.alert_tone)}`,
                  cursor: 'pointer', transition: 'transform .12s',
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateX(2px)'; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateX(0)'; }}
              >
                <span style={{ fontSize: 12, fontWeight: 600, color: '#0d1f35' }}>{v.name}</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: driftAlertColor(v.alert_tone) }}>
                  +{v.current_drift_pct.toFixed(1)}% drift
                </span>
                <span style={{ fontSize: 10, color: '#9ca3af' }}>Renewal in {v.renewal_days}d</span>
              </div>
            ))}
          </div>
        </div>

        {/* NCUA Regulatory Monitor */}
        <div style={panelStyle}>
          <div style={panelTitleRow}>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>NCUA Regulatory Monitor</div>
            <span style={{ fontSize: 10, fontWeight: 700, background: '#fffbeb', color: '#d97706', padding: '2px 8px', borderRadius: 4 }}>
              {d.regulatory.filter((r) => r.action_required).length} CHANGES
            </span>
          </div>
          <div style={{ fontSize: 11, color: '#7a8fa6', marginBottom: 12 }}>
            Live monitoring of NCUA, FinCEN, CFPB rule changes affecting CW FCU
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {d.regulatory.map((reg) => (
              <div
                key={reg.title}
                onClick={() => onRegulatoryClick(reg.title)}
                style={{
                  padding: 10, background: regTileBg(reg.tone), borderRadius: 8,
                  border: `1px solid ${regTileBorder(reg.tone)}`,
                  cursor: 'pointer', transition: 'transform .12s',
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-1px)'; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'; }}
              >
                <div style={{
                  fontSize: 11, fontWeight: 700, color: regTileTextColor(reg.tone), marginBottom: 3,
                }}>
                  {reg.severity} · Effective {reg.effective}
                </div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#0d1f35', marginBottom: 3 }}>
                  {reg.title}
                </div>
                <div style={{ fontSize: 11, color: '#6b7280', lineHeight: 1.4 }}>
                  {reg.description}
                </div>
                {reg.action_required && (
                  <div style={{ marginTop: 6, fontSize: 10, fontWeight: 700, color: regTileTextColor(reg.tone) }}>
                    {reg.action_required}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Exam Readiness Forecast */}
        <div style={panelStyle}>
          <div style={panelTitleRow}>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>Exam Readiness Forecast</div>
            <span style={{ fontSize: 10, fontWeight: 700, background: '#f0fdf4', color: '#16a34a', padding: '2px 8px', borderRadius: 4 }}>
              ON TRACK
            </span>
          </div>
          <div style={{ fontSize: 11, color: '#7a8fa6', marginBottom: 12 }}>
            NCUA exam window: {d.signal_hero.exam_date} · {d.signal_hero.days_to_exam} days · Signal projects 97% readiness
          </div>
          <div style={{ height: 160 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={examChartData} margin={{ top: 4, right: 10, left: -16, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f2f5" />
                <XAxis dataKey="label" tick={{ fontSize: 9, fill: '#9ca3af' }} />
                <YAxis domain={[65, 100]} tick={{ fontSize: 10, fill: '#9ca3af' }} tickFormatter={(v) => `${v}%`} />
                <Tooltip />
                <Line type="monotone" dataKey="actual" stroke="#6c47ff" strokeWidth={2} dot={{ r: 3 }} connectNulls={false} />
                <Line type="monotone" dataKey="projected" stroke="#00c4a0" strokeWidth={2} strokeDasharray="5 4" dot={{ r: 2 }} connectNulls={false} />
                <Line type="monotone" dataKey="target" stroke="#e8ecf0" strokeDasharray="3 3" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 12 }}>
            {d.exam_trajectory.folder_bars.map((b) => (
              <div key={b.name} style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0',
                borderBottom: '1px solid #f5f7fa',
              }}>
                <div style={{ flex: 1, fontSize: 12, fontWeight: 600, color: '#0d1f35' }}>{b.name}</div>
                <div style={{ width: 80, height: 5, background: '#f0f2f5', borderRadius: 3 }}>
                  <div style={{ width: `${b.pct}%`, height: 5, background: b.color, borderRadius: 3 }} />
                </div>
                <div style={{ fontSize: 11, fontWeight: 700, color: b.color, width: 32, textAlign: 'right' }}>
                  {b.pct}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* LIVE SIGNAL FEED */}
      <div style={panelStyle}>
        <div style={{
          fontSize: 13, fontWeight: 700, color: '#0d1f35', marginBottom: 14,
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          Live Signal Feed
          <span style={{ fontSize: 11, color: '#9ca3af' }}>All agents · Real-time anomaly detection</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
          {d.signal_feed.map((tile) => (
            <div
              key={tile.title}
              onClick={() => onSignalFeedClick(tile)}
              style={{
                padding: 10, background: feedToneBg(tile.tone), borderRadius: 8,
                border: `1px solid ${feedToneBorder(tile.tone)}`,
                cursor: 'pointer', transition: 'transform .12s',
              }}
              onMouseEnter={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-1px)'; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'; }}
            >
              <div style={{
                fontSize: 10, fontWeight: 700, color: feedToneTextColor(tile.tone),
                textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 4,
              }}>
                {feedToneLabel(tile.tone)} · {tile.agent}
              </div>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#0d1f35', marginBottom: 3 }}>
                {tile.title}
              </div>
              <div style={{ fontSize: 11, color: '#6b7280' }}>
                {tile.detail}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0',
};
const panelTitleRow: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12,
};
