/**
 * Verizon Far Edge Executive Dashboard.
 *
 * Renders when Settings → Demo Mode = "Verizon Far Edge Operations" (or the
 * generic "Telecommunications" industry). Port of the reference HTML at
 * apex-verizon-demo/dashboard.html — exec-level program outcomes, wave 47
 * status, 4-agent status grid, HITL queue, Governance DVR timeline.
 *
 * Numbers are display-only for the demo. The /telecommunications/cycle-history
 * endpoint feeds Wave-47 throughput when the pipeline has run.
 */
import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useQuery, useQueryClient } from '@tanstack/react-query';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface HitlItem {
  request_id:    string;
  cycle_id:      string;
  agent:         string;
  gate:          string;
  severity:      'high' | 'medium' | 'low';
  reason:        string;
  data?:         Record<string, any>;
  created_at:    number;
  status:        'pending' | 'approve' | 'reject' | 'timeout' | string;
  reviewer?:     string;
  resolved_at?:  number;
}

// ──────────────────────── tiny inline-style helpers ────────────────────────
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

// Golden-config offline fallback (mirrors /signals/vz/firmware-intelligence)
const GOLDEN_FALLBACK = {
  golden_config: [
    { platform: 'HPE EL140 Gen12', controller: 'iLO7', lab_certified: '1.20.00', production: 'onboarding', drift_sites: 0, status: 'CERTIFYING', risk: 'medium', note: 'New current-gen server type — 7 playbook changes proposed, NEBS 62°C threshold unset' },
    { platform: 'Dell XR8720t', controller: 'iDRAC 10', lab_certified: '1.30.33.10', production: '1.30.10.51 / 1.30.33.10 mix', drift_sites: 64, status: 'DRIFT', risk: 'medium', note: 'Inlet-temp warning thresholds null on 1.30.10.51, populated on 1.30.33.10 — roll forward' },
    { platform: 'ZT Proteus', controller: 'BMC', lab_certified: '0.46', production: '0.45 / 0.46 mix', drift_sites: 312, status: 'DRIFT', risk: 'critical', note: 'BMC .45 still in field on Samsung PM9A3 sites — MEAKV-1792 thermal regression' },
    { platform: 'HPE E930t', controller: 'iLO6', lab_certified: '1.60', production: '1.57 / 1.60 mix', drift_sites: 88, status: 'DRIFT', risk: 'medium', note: 'Field running 1.57; golden is 1.60 — schedule rolling update' },
    { platform: 'ZT Triton', controller: 'BMC', lab_certified: '2.31', production: '2.31', drift_sites: 0, status: 'ALIGNED', risk: 'low', note: 'Production matches lab-certified golden' },
  ],
  golden_config_gaps: [
    { component: 'SSD firmware (Samsung PM9A3)', tracked: false, impact: 'Not in the golden-config baseline yet — the .45 thermal regression is invisible to drift checks until added', recommendation: 'Add SSD firmware to the golden-config schema (MEAKV-1792 makes this urgent)' },
    { component: 'CPLD firmware (ZT PDB)', tracked: false, impact: 'PDB-CPLD revs not baselined', recommendation: 'Extend golden-config to CPLD components' },
  ],
};

// ──────────────────────── component ────────────────────────

export function VerizonDashboard() {
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

  // Optional live data from the telecom cycle history. Updates Wave 47 numbers
  // once a real cycle runs.
  const historyQ = useQuery<{ items: any[] }>({
    queryKey: ['vz-dash-cycle-history'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/telecommunications/cycle-history?limit=10`);
      if (!r.ok) return { items: [] };
      return r.json();
    },
    retry: false, staleTime: 15_000, refetchInterval: 15_000,
  });
  const latestCycle = historyQ.data?.items?.[0];

  // ── Golden Configuration drift — lab-certified vs production firmware ──
  // Directly addresses James's in-flight "golden config dashboard" (meeting
  // notes). Real-corpus driven; offline-safe fallback so it always renders.
  const goldenQ = useQuery<any>({
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
    retry: 0, staleTime: 60_000, refetchInterval: 60_000,
    placeholderData: GOLDEN_FALLBACK,
  });
  const golden = goldenQ.data ?? GOLDEN_FALLBACK;
  const goldenRows: any[] = golden.golden_config ?? [];
  const goldenGaps: any[] = golden.golden_config_gaps ?? [];
  const driftSites = goldenRows.reduce((a: number, r: any) => a + (r.drift_sites || 0), 0);

  // ──────────────────── HITL polling ────────────────────
  const queryClient = useQueryClient();
  const hitlQuery = useQuery<{ count: number; items: HitlItem[] }>({
    queryKey: ['hitl-pending'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/telecommunications/hitl/pending`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 5000,
    refetchOnWindowFocus: false,
    retry: false,
  });
  const hitlItems = hitlQuery.data?.items ?? [];
  const hitlPendingCount = hitlItems.filter((it) => it.status === 'pending').length;
  const [hitlBusy, setHitlBusy] = useState<Record<string, boolean>>({});

  async function decideHitl(request_id: string, decision: 'approve' | 'reject') {
    setHitlBusy((s) => ({ ...s, [request_id]: true }));
    try {
      const r = await fetch(
        `${API_BASE_URL}/telecommunications/hitl/${encodeURIComponent(request_id)}/${decision}`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reviewer: 'J. Patchett' }) },
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      await queryClient.invalidateQueries({ queryKey: ['hitl-pending'] });
    } catch (e) {
      console.error('decideHitl failed', e);
    } finally {
      setHitlBusy((s) => ({ ...s, [request_id]: false }));
    }
  }

  return (
    <div style={{ background: '#f0f4f8', minHeight: '100vh', padding: '28px 32px', maxWidth: 1600, margin: '0 auto' }}>

      {/* Top bar substitute (live + HITL pills) */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 800, color: '#0f172a', letterSpacing: '-.02em' }}>
            Executive Dashboard
          </div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
            CAS Platform · Far Edge Certification Operations · Wind River + OpenShift
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ ...chip('#f0fdf4', '#16a34a', '#bbf7d0') }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', display: 'inline-block' }} />
            6 Agents Live
          </span>
          <span style={chip(
            hitlPendingCount > 0 ? '#fffbeb' : '#f0fdf4',
            hitlPendingCount > 0 ? '#d97706' : '#16a34a',
            hitlPendingCount > 0 ? '#fde68a' : '#bbf7d0',
          )}>
            {hitlPendingCount > 0 ? `⚠ ${hitlPendingCount} HITL Pending` : '✓ 0 HITL Pending'}
          </span>
          <span style={{ fontSize: 12, color: '#64748b' }}>{clock}</span>
        </div>
      </div>

      {/* Headline KPIs */}
      <div style={sectionLabel}>Program Outcomes · Wave 47</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20, marginBottom: 28 }}>
        <HeadlineKpi
          label="Time to Market" value="40%" detail="Cert cycle 1–2 months → compressed by automating triage, docs + drift checks"
          progressLabel={['1–2 mo', '~3 wks']} progressWidth={60}
          bgGradient="linear-gradient(135deg,#1e1b4b 0%,#312e81 100%)"
          accent="#a78bfa" accentBg="rgba(139,92,246,.2)" accentBd="rgba(139,92,246,.3)"
          progressBg="rgba(139,92,246,.2)" progressFill="linear-gradient(90deg,#8b5cf6,#a78bfa)"
        />
        <HeadlineKpi
          label="Documentation Effort Reduction" value="70%" detail="~40 hrs manual write-up per firmware → ~12 hrs (exit reports, MOPs, JIRA)"
          progressLabel={['40 hrs', '12 hrs']} progressWidth={70}
          bgGradient="linear-gradient(135deg,#052e16 0%,#14532d 100%)"
          accent="#4ade80" accentBg="rgba(34,197,94,.15)" accentBd="rgba(34,197,94,.25)"
          progressBg="rgba(34,197,94,.15)" progressFill="linear-gradient(90deg,#22c55e,#4ade80)"
        />
        <HeadlineKpi
          label="Missed Anomalies" value="Zero" detail="Schema drift, high-risk paths, and test-failure patterns surfaced before wave authorization"
          chips={['Schema drift: 0 missed', 'High-risk paths: 0 missed', 'Test failures: 0 missed']}
          bgGradient="linear-gradient(135deg,#431407 0%,#7c2d12 100%)"
          accent="#fb923c" accentBg="rgba(251,146,60,.15)" accentBd="rgba(251,146,60,.25)"
        />
      </div>

      {/* Current-Gen Autonomous Onboarding — orchestration metrics strip */}
      <div style={sectionLabel}>Autonomous Onboarding · Current-Gen Fleet</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 14, marginBottom: 28 }}>
        {[
          { v: '2', l: 'New platforms certifying', s: 'EL140 Gen12 · XR8720t', c: '#6c47ff' },
          { v: '13', l: 'PROPOSED tests designed', s: 'AI-authored coverage', c: '#2563eb' },
          { v: '90', l: 'Test iterations run', s: '9 cases × 5 × 2 platforms', c: '#0891b2' },
          { v: '7', l: 'Playbook changes', s: 'Ansible · evidence-linked', c: '#d97706' },
          { v: '3', l: 'HITL gates', s: 'Human-approved actions', c: '#16a34a' },
          { v: '40h→18m', l: 'Per new platform', s: '>95% time reduction', c: '#dc2626' },
        ].map((m) => (
          <div key={m.l} style={{ ...card, padding: 16, borderLeft: `4px solid ${m.c}` }}>
            <div style={{ fontSize: 26, fontWeight: 800, color: m.c, fontFamily: "'Space Grotesk', sans-serif" }}>{m.v}</div>
            <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a', marginTop: 4 }}>{m.l}</div>
            <div style={{ fontSize: 10.5, color: '#94a3b8', marginTop: 2 }}>{m.s}</div>
          </div>
        ))}
      </div>

      {/* Wave 47 + Agent Status */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        {/* Wave 47 */}
        <div style={{ ...card, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 700, color: '#0f172a' }}>
                Wave 47 — Active Deployment
              </div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                16,000 sites · Northeast + Midwest regions
              </div>
            </div>
            <span style={chip('#fffbeb', '#d97706', '#fde68a')}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#f59e0b' }} />
              In Progress
            </span>
          </div>

          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>Sites Certified</span>
              <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, fontWeight: 600, color: '#0f172a' }}>
                11,240 / 16,000
              </span>
            </div>
            <ProgressBar pct={70} fill="linear-gradient(90deg,#cd0000,#ff6b6b)" />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#94a3b8', marginTop: 5 }}>
              <span>70.25% complete</span>
              <span>4,760 remaining</span>
            </div>
          </div>

          <WaveRow label="CaaS-Node-Type-A" pct={92} num="6,440/7,000" chipBg="#f0fdf4" chipFg="#16a34a" chipBd="#bbf7d0" fill="#22c55e" />
          <WaveRow label="CaaS-Node-Type-B" pct={54} num="3,240/6,000" chipBg="#fffbeb" chipFg="#d97706" chipBd="#fde68a" fill="#f59e0b" />
          <WaveRow label="CaaS-Node-Type-C" pct={18} num="540/3,000"   chipBg="#eff6ff" chipFg="#2563eb" chipBd="#bfdbfe" fill="#3b82f6" />

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginTop: 20, paddingTop: 16, borderTop: '1px solid #f1f5f9' }}>
            <FooterMetric value="247" label="Tests / Cycle" color="#0f172a" />
            <FooterMetric value={latestCycle ? `${((latestCycle.passed / latestCycle.total) * 100).toFixed(1)}%` : '94.3%'} label="Pass Rate" color="#22c55e" />
            <FooterMetric value={latestCycle ? String(latestCycle.failed ?? 14) : '14'} label="Failures" color="#f59e0b" />
            <FooterMetric value="8.4d" label="Avg Cycle" color="#a855f7" />
          </div>
        </div>

        {/* Agent Status */}
        <div style={{ ...card, padding: 24 }}>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 20 }}>
            Agent Status · All 6 Active
          </div>
          <AgentCard
            name="CertificationAgent" sub="Test Report Intelligence" status="Running"
            accent="#8b5cf6"
            metrics={[
              { v: '11,240', l: 'Reports Generated', bg: '#faf5ff', fg: '#7c3aed' },
              { v: '70%',    l: 'Doc Time Saved',    bg: '#f0fdf4', fg: '#16a34a' },
              { v: String(hitlPendingCount), l: 'HITL Pending',
                bg: hitlPendingCount > 0 ? '#fffbeb' : '#f0fdf4',
                fg: hitlPendingCount > 0 ? '#d97706' : '#16a34a' },
            ]}
            href="/canvas/playbook/pb-tel-1"
          />
          <AgentCard
            name="SchemaWatchAgent" sub="Redfish Schema Drift Detection" status="Monitoring"
            accent="#06b6d4"
            metrics={[
              { v: '3',  l: 'Drift Events',    bg: '#ecfeff', fg: '#0891b2' },
              { v: '47', l: 'Scripts Scanned', bg: '#f0fdf4', fg: '#16a34a' },
              { v: '0',  l: 'Missed Breaks',   bg: '#f0fdf4', fg: '#16a34a' },
            ]}
            href="/canvas/playbook/pb-tel-3"
          />
          <AgentCard
            name="UpgradeAdvisorAgent" sub="Upgrade Path Validation" status="Active"
            accent="#f59e0b"
            metrics={[
              { v: '128', l: 'Paths Validated',    bg: '#fffbeb', fg: '#d97706' },
              { v: '1',   l: 'High-Risk Flagged',  bg: '#fef2f2', fg: '#dc2626' },
              { v: '0',   l: 'Skip-Level Missed',  bg: '#f0fdf4', fg: '#16a34a' },
            ]}
            href="/canvas/playbook/pb-tel-2"
          />
          <AgentCard
            name="MentorAgent" sub="Knowledge Preservation" status="Active"
            accent="#10b981"
            metrics={[
              { v: '1,847', l: 'KB Queries',       bg: '#f0fdf4', fg: '#16a34a' },
              { v: '<30s',  l: 'Avg Answer Time',  bg: '#f0fdf4', fg: '#16a34a' },
              { v: '100%',  l: 'Citation Rate',    bg: '#f0fdf4', fg: '#16a34a' },
            ]}
            href="/mentor-agent"
            last
          />
        </div>
      </div>

      {/* ════════ GOLDEN CONFIGURATION DRIFT (lab-certified vs production) ════════ */}
      <div style={sectionLabel}>Golden Configuration · Lab-Certified vs Production</div>
      <div style={{ ...card, padding: 24, marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18 }}>
          <div>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 700, color: '#0f172a' }}>
              Golden Configuration Drift
            </div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
              Production firmware (data lake) vs the lab-certified golden baseline · automated drift detection
            </div>
          </div>
          <span style={chip(driftSites > 0 ? '#fef2f2' : '#f0fdf4', driftSites > 0 ? '#dc2626' : '#16a34a', driftSites > 0 ? '#fecaca' : '#bbf7d0')}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: driftSites > 0 ? '#ef4444' : '#22c55e' }} />
            {driftSites.toLocaleString()} sites drifted
          </span>
        </div>

        {/* drift table */}
        <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1.2fr 0.8fr 0.9fr', gap: 0, fontSize: 12 }}>
          {['Platform · Controller', 'Lab-Certified (Golden)', 'In Production', 'Drift Sites', 'Status'].map((h, i) => (
            <div key={i} style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
                                  color: '#94a3b8', padding: '0 8px 8px', borderBottom: '1px solid #e8edf2' }}>{h}</div>
          ))}
          {goldenRows.map((r: any, idx: number) => {
            const sc = r.status === 'DRIFT' ? (r.risk === 'critical' ? '#dc2626' : '#d97706')
                     : r.status === 'PENDING' ? '#2563eb' : '#16a34a';
            const sbg = r.status === 'DRIFT' ? (r.risk === 'critical' ? '#fef2f2' : '#fffbeb')
                      : r.status === 'PENDING' ? '#eff6ff' : '#f0fdf4';
            return (
              <React.Fragment key={r.platform + r.controller}>
                <div style={{ padding: '11px 8px', borderBottom: idx < goldenRows.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                  <div style={{ fontWeight: 600, color: '#0f172a' }}>{r.platform}</div>
                  <div style={{ fontSize: 10.5, color: '#94a3b8' }}>{r.controller}</div>
                </div>
                <div style={{ padding: '11px 8px', fontFamily: "'JetBrains Mono', monospace", color: '#16a34a', fontWeight: 600, borderBottom: idx < goldenRows.length - 1 ? '1px solid #f1f5f9' : 'none' }}>{r.lab_certified}</div>
                <div style={{ padding: '11px 8px', fontFamily: "'JetBrains Mono', monospace", color: r.status === 'DRIFT' ? '#dc2626' : '#475569', borderBottom: idx < goldenRows.length - 1 ? '1px solid #f1f5f9' : 'none' }}>{r.production}</div>
                <div style={{ padding: '11px 8px', fontWeight: 700, color: r.drift_sites > 0 ? '#dc2626' : '#94a3b8', borderBottom: idx < goldenRows.length - 1 ? '1px solid #f1f5f9' : 'none' }}>{r.drift_sites > 0 ? r.drift_sites.toLocaleString() : '—'}</div>
                <div style={{ padding: '11px 8px', borderBottom: idx < goldenRows.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                  <span style={{ fontSize: 9.5, fontWeight: 700, padding: '2px 7px', borderRadius: 4, background: sbg, color: sc }}>{r.status}</span>
                </div>
              </React.Fragment>
            );
          })}
        </div>

        {/* the SSD-firmware tracking gap James flagged */}
        <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #f1f5f9' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#d97706', letterSpacing: '.06em', textTransform: 'uppercase', marginBottom: 8 }}>
            Coverage Gaps · components not yet in the golden baseline
          </div>
          {goldenGaps.map((g: any, i: number) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', padding: '7px 10px', marginBottom: 6,
                                  borderRadius: 8, background: '#fffbeb', border: '1px solid #fde68a' }}>
              <span style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px', borderRadius: 3, background: '#d97706', color: '#fff', whiteSpace: 'nowrap' }}>NOT TRACKED</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <span style={{ fontSize: 12.5, fontWeight: 600, color: '#0f172a' }}>{g.component}</span>
                <span style={{ fontSize: 11.5, color: '#92400e' }}> — {g.recommendation}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* HITL Queue + Governance DVR (Audit Lens) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 20 }}>
        <div style={{ ...card, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
            <div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 700, color: '#0f172a' }}>
                HITL Approval Queue
              </div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                Human-in-the-loop decisions pending
              </div>
            </div>
            <span style={{
              background: hitlPendingCount > 0 ? '#fef2f2' : '#f0fdf4',
              border: hitlPendingCount > 0 ? '1px solid #fecaca' : '1px solid #bbf7d0',
              borderRadius: 99, padding: '5px 12px', fontSize: 12, fontWeight: 700,
              color: hitlPendingCount > 0 ? '#dc2626' : '#16a34a',
            }}>
              {hitlPendingCount} Pending
            </span>
          </div>
          {hitlItems.length === 0 && (
            <div style={{
              padding: '20px 16px', borderRadius: 12, border: '1px dashed #e2e8f0',
              background: '#f8fafc', textAlign: 'center', marginBottom: 8,
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#16a34a' }}>✓ No HITL gates open</div>
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>
                Pipeline is running clean · All agents auto-proceeding
              </div>
            </div>
          )}
          {hitlItems.map((item) => {
            const palette = item.severity === 'high'
              ? { bg: '#fef2f2', bd: '#fecaca', iconBg: 'rgba(239,68,68,.1)',  iconColor: '#ef4444' }
              : { bg: '#fffbeb', bd: '#fde68a', iconBg: 'rgba(245,158,11,.15)', iconColor: '#f59e0b' };
            const ageSec = Math.max(0, Math.floor((Date.now() - item.created_at) / 1000));
            const ageStr = ageSec < 60   ? `${ageSec}s ago`
                         : ageSec < 3600 ? `${Math.floor(ageSec / 60)} min ago`
                                         : `${Math.floor(ageSec / 3600)} hrs ago`;
            return (
              <HitlRow
                key={item.request_id}
                title={`${item.agent} · ${item.gate}`}
                detail={item.reason}
                meta={`${item.request_id} · ${ageStr}`}
                status={item.status}
                reviewer={item.reviewer}
                busy={!!hitlBusy[item.request_id]}
                onApprove={() => decideHitl(item.request_id, 'approve')}
                onReject={()  => decideHitl(item.request_id, 'reject')}
                {...palette}
              />
            );
          })}
          <div style={{ padding: 10, background: '#f8fafc', borderRadius: 8, border: '1px solid #e2e8f0', marginTop: 8 }}>
            <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.5 }}>
              Every decision is written immutably to the <strong style={{ color: '#475569' }}>Audit Lens</strong> with reviewer name, timestamp, and override notes.
            </div>
          </div>
        </div>

        <div style={{ ...card, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
            <div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Governance Audit Lens</div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>Immutable audit trail · 7-year retention</div>
            </div>
            <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
              Recording
            </span>
          </div>
          <DvrEntry color="#8b5cf6" title="CertAgent · Report Issued · NE-4821" meta="06:47:23 · J. Patchett" />
          <DvrEntry color="#f59e0b" title="UpgradeAdv · HIGH-RISK Flag Raised"   meta="06:43:55 · Automated" />
          <DvrEntry color="#06b6d4" title="SchemaWatch · Drift Detected"          meta="06:31:07 · Automated" />
          <DvrEntry color="#10b981" title="MentorAgent · KB Query Answered"      meta="06:28:11 · R. Chen" />
          <DvrEntry color="#8b5cf6" title="CertAgent · HITL Approved · NE-4817"  meta="05:14:02 · J. Patchett" />
          <DvrEntry color="#f59e0b" title="UpgradeAdv · 128 Paths Validated"     meta="04:00:00 · Automated" last />
        </div>
      </div>

      {/* Quick links */}
      <div style={{ ...card, padding: 24 }}>
        <div style={{ ...sectionLabel, marginBottom: 16 }}>Quick Actions</div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
          <QuickLink href="/canvas/playbook/pb-tel-1-run" emoji="▶" title="Run Cert Cycle"      sub="Drop ROBOT XML → 17 JIRA tickets in 15s" />
          <QuickLink href="/command-center"               emoji="📡" title="Command Center"     sub="Live agent feed · drift · HITL queue" />
          <QuickLink href="/apex-signal"                  emoji="📊" title="Apex Signal"        sub="16,247-site risk · wave overview" />
          <QuickLink href="/mentor-agent"                 emoji="📚" title="Ask MentorAgent"    sub="Citation-grounded KB · &lt;30s answers" />
        </div>
      </div>

      <style>{`
        @keyframes hitlPulseLight {
          0%,100% { box-shadow: 0 0 0 0 rgba(245,158,11,0); }
          50%     { box-shadow: 0 0 0 4px rgba(245,158,11,.18); }
        }
      `}</style>
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
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 52, fontWeight: 800, color: '#fff', lineHeight: 1, letterSpacing: '-.03em' }}>
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
      {props.chips && (
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

function ProgressBar({ pct, fill }: { pct: number; fill: string }) {
  return (
    <div style={{ height: 6, borderRadius: 99, background: '#f1f5f9', overflow: 'hidden' }}>
      <div style={{ height: '100%', borderRadius: 99, width: `${pct}%`, background: fill, transition: 'width 1.4s' }} />
    </div>
  );
}

function WaveRow({ label, pct, num, chipBg, chipFg, chipBd, fill }: {
  label: string; pct: number; num: string; chipBg: string; chipFg: string; chipBd: string; fill: string;
}) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid #f1f5f9' }}>
      <div style={{ width: 140, fontSize: 12, fontWeight: 600, color: '#374151' }}>{label}</div>
      <div style={{ flex: 1, padding: '0 16px' }}>
        <ProgressBar pct={pct} fill={fill} />
      </div>
      <div style={{ width: 90, textAlign: 'right', fontSize: 11, fontFamily: "'JetBrains Mono', monospace", color: chipFg, fontWeight: 600 }}>
        {num}
      </div>
      <div style={{ width: 70, textAlign: 'right' }}>
        <span style={chip(chipBg, chipFg, chipBd)}>{pct}%</span>
      </div>
    </div>
  );
}

function FooterMetric({ value, label, color }: { value: string; label: string; color: string }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 800, color }}>{value}</div>
      <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', marginTop: 2 }}>{label}</div>
    </div>
  );
}

function AgentCard(props: {
  name: string; sub: string; status: string; accent: string;
  metrics: Array<{ v: string; l: string; bg: string; fg: string }>;
  href: string; last?: boolean;
}) {
  return (
    <div style={{
      borderRadius: 16, border: '1px solid #e8edf2', background: '#fff', padding: '20px 22px',
      marginBottom: props.last ? 0 : 10, borderLeft: `3px solid ${props.accent}`, transition: 'all .2s',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{props.name}</div>
          <div style={{ fontSize: 11, color: '#64748b' }}>{props.sub}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={badge('rgba(16,185,129,.1)', '#059669', 'rgba(16,185,129,.2)')}>{props.status}</span>
          <Link href={props.href} style={{ fontSize: 11, color: props.accent, fontWeight: 600, textDecoration: 'none' }}>View →</Link>
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
        {props.metrics.map((m) => (
          <div key={m.l} style={{ background: m.bg, borderRadius: 8, padding: '8px 10px', textAlign: 'center' }}>
            <div style={{ fontSize: 16, fontWeight: 800, color: m.fg, fontFamily: "'Space Grotesk', sans-serif" }}>{m.v}</div>
            <div style={{ fontSize: 10, color: '#94a3b8', fontWeight: 600, marginTop: 1 }}>{m.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function HitlRow(props: {
  title: string; detail: string; meta: string;
  bg: string; bd: string; iconBg: string; iconColor: string;
  status: string;          // 'pending' | 'approve' | 'reject' | 'timeout'
  reviewer?: string;
  busy: boolean;
  onApprove: () => void; onReject: () => void;
}) {
  const isPending  = props.status === 'pending';
  const isApproved = props.status === 'approve';
  const isRejected = props.status === 'reject';
  const isTimeout  = props.status === 'timeout';

  const rowBg = isApproved ? '#f0fdf4' : isRejected ? '#fef2f2' : isTimeout ? '#f8fafc' : props.bg;
  const rowBd = isApproved ? '#bbf7d0' : isRejected ? '#fecaca' : isTimeout ? '#e2e8f0' : props.bd;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 12,
      padding: '14px 16px', borderRadius: 12,
      border: `1px solid ${rowBd}`, marginBottom: 8, background: rowBg,
      animation: isPending ? 'hitlPulseLight 2s ease-in-out infinite' : undefined,
    }}>
      <div style={{ width: 40, height: 40, borderRadius: 12, background: props.iconBg, border: `1px solid ${props.iconColor}40`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: props.iconColor, fontSize: 18 }}>⚠</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>{props.title}</div>
        <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{props.detail}</div>
        <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>{props.meta}</div>
        {!isPending && (
          <div style={{ marginTop: 6, fontSize: 11, fontWeight: 700,
                        color: isApproved ? '#15803d' : isRejected ? '#b91c1c' : '#64748b' }}>
            {isApproved && <>✓ Approved{props.reviewer ? ` — ${props.reviewer}` : ''} · Logged to Audit Lens</>}
            {isRejected && <>✗ Rejected{props.reviewer ? ` — ${props.reviewer}` : ''} · Pipeline halted</>}
            {isTimeout  && <>⏱ Timed out · Pipeline halted</>}
          </div>
        )}
      </div>
      {isPending && (
        <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
          <button onClick={props.onApprove} disabled={props.busy}
            style={{ padding: '6px 12px', background: '#dcfce7', color: '#15803d',
                     border: '1px solid #bbf7d0', borderRadius: 7,
                     fontSize: 11, fontWeight: 700,
                     cursor: props.busy ? 'not-allowed' : 'pointer',
                     opacity: props.busy ? 0.5 : 1 }}>
            {props.busy ? '...' : 'Approve'}
          </button>
          <button onClick={props.onReject} disabled={props.busy}
            style={{ padding: '6px 12px', background: '#fef2f2', color: '#b91c1c',
                     border: '1px solid #fecaca', borderRadius: 7,
                     fontSize: 11, fontWeight: 700,
                     cursor: props.busy ? 'not-allowed' : 'pointer',
                     opacity: props.busy ? 0.5 : 1 }}>
            {props.busy ? '...' : 'Reject'}
          </button>
        </div>
      )}
    </div>
  );
}

function DvrEntry({ color, title, meta, last }: { color: string; title: string; meta: string; last?: boolean }) {
  return (
    <div style={{ display: 'flex', gap: 10, paddingBottom: last ? 0 : 10, borderLeft: '2px solid #f1f5f9', marginLeft: 5, paddingLeft: 14, position: 'relative' }}>
      <div style={{ position: 'absolute', left: -5, top: 2, width: 8, height: 8, borderRadius: '50%', background: color }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#0f172a' }}>{title}</div>
        <div style={{ fontSize: 10, color: '#64748b', marginTop: 1, fontFamily: "'JetBrains Mono', monospace" }}>{meta}</div>
      </div>
    </div>
  );
}

function QuickLink({ href, emoji, title, sub }: { href: string; emoji: string; title: string; sub: string }) {
  return (
    <Link href={href} style={{ textDecoration: 'none', padding: 14, borderRadius: 12, border: '1px solid #e8edf2', background: '#fafbfc', display: 'block', transition: 'all .15s' }}>
      <div style={{ fontSize: 22, marginBottom: 6 }}>{emoji}</div>
      <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>{title}</div>
      <div style={{ fontSize: 11, color: '#64748b' }} dangerouslySetInnerHTML={{ __html: sub }} />
    </Link>
  );
}
