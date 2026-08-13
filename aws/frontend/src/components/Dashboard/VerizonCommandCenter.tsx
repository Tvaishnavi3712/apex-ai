/**
 * Verizon Far Edge — Operations Command Center.
 *
 * Renders when demo mode === 'verizon_far_edge'. Port of
 * apex-verizon-demo/command-center.html: 4-agent status strip, live agent
 * feed (auto-tickering), schema diff viewer, upgrade path validator, HITL
 * approval queue, Audit Lens timeline, predictive-intelligence panel.
 *
 * Numbers are display-only. The interactivity that matters for the demo —
 * HITL approve/reject buttons — is wired up to the live backend.
 */
import { useEffect, useRef, useState } from 'react';
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

// ──────────────────── styling helpers ────────────────────
const panel: React.CSSProperties = {
  background: '#fff', border: '1px solid #e8edf2', borderRadius: 16, boxShadow: '0 1px 2px rgba(15,23,42,.04)',
};
const panelHeader: React.CSSProperties = {
  padding: '16px 20px', borderBottom: '1px solid #f1f5f9',
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

// ──────────────────── seed feed lines ────────────────────
interface FeedLine { time: string; html: string }

const INITIAL_FEED: FeedLine[] = [
  { time: '06:47:23', html: '<span style="color:#c4b5fd">[CertAgent]</span> <span style="color:#f9fafb">Site NE-4821 certified</span> <span style="color:#4ade80">247 pass</span> <span style="color:#f87171">14 fail</span>' },
  { time: '06:47:21', html: '<span style="color:#c4b5fd">[CertAgent]</span> JIRA tickets created for 14 failures → <span style="color:#60a5fa">APEX-4821-F</span>' },
  { time: '06:45:10', html: '<span style="color:#34d399">[MentorAgent]</span> Query answered in <span style="color:#f9fafb">18s</span> · 3 citations · R. Chen' },
  { time: '06:43:55', html: '<span style="color:#fbbf24">[UpgradeAdv]</span> <span style="color:#f87171">HIGH-RISK</span> path 23.06→24.01 Type-B NE · 78% fail rate → HITL gate raised' },
  { time: '06:41:02', html: '<span style="color:#c4b5fd">[CertAgent]</span> Site NE-4820 certified · <span style="color:#4ade80">247/247 pass</span> · Report issued' },
  { time: '06:38:44', html: '<span style="color:#22d3ee">[SchemaWatch]</span> Scheduled scan complete · No new drift · Baseline confirmed' },
  { time: '06:35:19', html: '<span style="color:#fbbf24">[UpgradeAdv]</span> Path 22.12→24.12 Type-A validated · <span style="color:#4ade80">SAFE</span> · Pre-check checklist issued' },
  { time: '06:31:07', html: '<span style="color:#22d3ee">[SchemaWatch]</span> <span style="color:#f87171">DRIFT DETECTED</span> <code>power.state</code>→<code>power.powerState</code> · 6 scripts impacted' },
  { time: '06:28:11', html: '<span style="color:#34d399">[MentorAgent]</span> "Pre-check for 23.06→24.01 Type-B?" answered · Runbook §4.2 cited' },
  { time: '06:25:33', html: '<span style="color:#c4b5fd">[CertAgent]</span> Site NE-4819 · <span style="color:#fbbf24">WARN</span> thermal anomaly pattern · Flagged for review' },
];

const LIVE_LINES = [
  () => `<span style="color:#c4b5fd">[CertAgent]</span> Site NE-${4822 + Math.floor(Math.random()*100)} certified · <span style="color:#4ade80">${240+Math.floor(Math.random()*7)}/247 pass</span>`,
  () => `<span style="color:#34d399">[MentorAgent]</span> Query answered in <span style="color:#f9fafb">${15+Math.floor(Math.random()*20)}s</span> · ${1+Math.floor(Math.random()*4)} citations`,
  () => `<span style="color:#fbbf24">[UpgradeAdv]</span> Path validated: ${['22.12','23.06','23.12'][Math.floor(Math.random()*3)]}→24.12 Type-A · <span style="color:#4ade80">SAFE</span>`,
  () => `<span style="color:#22d3ee">[SchemaWatch]</span> Scheduled scan complete · Baseline confirmed · No drift`,
  () => `<span style="color:#c4b5fd">[CertAgent]</span> JIRA tickets auto-created for ${1+Math.floor(Math.random()*8)} failures`,
];

// ──────────────────── component ────────────────────

export function VerizonCommandCenter() {
  const [clock, setClock]   = useState('');
  const [feed, setFeed]     = useState<FeedLine[]>(INITIAL_FEED);
  const [hitlBusy, setHitlBusy] = useState<Record<string, boolean>>({});

  // ──────────────────── HITL — real backend polling ────────────────────
  // Polls /telecommunications/hitl/pending every 5s. The pipeline (in
  // backend/api/telecommunications_cycle.py) blocks on an asyncio.Event
  // when it raises a HITL gate; approve/reject endpoints unblock it.
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

  // ──────────────────── Predictive Intelligence — SageMaker wiring ──────────────
  const vzStatusQuery = useQuery<{ overall: string; endpoints: Array<{ name: string; status: string }> }>({
    queryKey: ['vz-endpoints-status'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/signals/vz/endpoints/status`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    refetchInterval: 30_000, refetchOnWindowFocus: false, retry: false,
  });

  const vzWaveQuery = useQuery<{
    probability_of_outage: number;
    risk_tier:             'low' | 'medium' | 'high' | 'critical';
    top_reasons:           string[];
    endpoint:              string;
  }>({
    queryKey: ['vz-wave-risk', 'cc-default'],
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
    refetchInterval: 60_000, refetchOnWindowFocus: false, retry: false,
  });
  const vzModelsLive = vzStatusQuery.data?.overall === 'live';

  async function decideHitl(request_id: string, decision: 'approve' | 'reject') {
    setHitlBusy((s) => ({ ...s, [request_id]: true }));
    try {
      const r = await fetch(
        `${API_BASE_URL}/telecommunications/hitl/${encodeURIComponent(request_id)}/${decision}`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ reviewer: 'J. Patchett' }) },
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      // Optimistic: refetch immediately. Backend marks status + clears event.
      await queryClient.invalidateQueries({ queryKey: ['hitl-pending'] });
    } catch (e) {
      console.error('decideHitl failed', e);
    } finally {
      setHitlBusy((s) => ({ ...s, [request_id]: false }));
    }
  }

  // clock
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

  // live feed ticker
  useEffect(() => {
    const i = setInterval(() => {
      const now = new Date();
      const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}:${String(now.getSeconds()).padStart(2,'0')}`;
      const fn = LIVE_LINES[Math.floor(Math.random() * LIVE_LINES.length)];
      setFeed((prev) => [{ time, html: fn() }, ...prev].slice(0, 30));
    }, 4500);
    return () => clearInterval(i);
  }, []);

  return (
    <div style={{ background: '#f0f4f8', minHeight: '100vh', color: '#1e293b', padding: '28px 32px', maxWidth: 1600, margin: '0 auto' }}>

      {/* Top bar */}
      <div style={{ background: '#fff', border: '1px solid #e8edf2', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 28px', borderRadius: 14, marginBottom: 20, boxShadow: '0 1px 2px rgba(15,23,42,.04)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444', animation: 'pulse 2s infinite' }} />
          <div>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 20, fontWeight: 800, color: '#0f172a', letterSpacing: '-.02em' }}>
              Operations Command Center
            </div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 1 }}>
              Real-time · Wave 47 · 4 Agents Active · All Systems Nominal
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={chip('#fef2f2', '#dc2626', '#fecaca')}>
            <span style={dot('#ef4444')} /> LIVE
          </span>
          <span style={chip('#fffbeb', '#d97706', '#fde68a')}>
            {hitlPendingCount} HITL Pending
          </span>
          <span style={{ fontSize: 12, color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>{clock}</span>
        </div>
      </div>

      {/* Agent status strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 20 }}>
        <AgentStatusCard color="#8b5cf6" name="CertificationAgent" status="Running" statusBg="#f0fdf4" statusFg="#16a34a" statusBd="#bbf7d0"
          big="11,240" subtitle="Reports generated this wave"
          extra={<><div style={{ height: 5, borderRadius: 99, background: '#eef2f7', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: '70%', background: 'linear-gradient(90deg,#8b5cf6,#a855f7)' }} /></div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#94a3b8', marginTop: 4 }}>
              <span>70% of wave</span><span>4,760 remaining</span></div></>} />
        <AgentStatusCard color="#0891b2" name="SchemaWatchAgent" status="Monitoring" statusBg="#ecfeff" statusFg="#0891b2" statusBd="#a5f3fc"
          big="3" subtitle="Drift events detected · 0 missed"
          minis={[{ v: '47', l: 'Scripts', fg: '#0891b2' }, { v: '6h', l: 'Interval', fg: '#16a34a' }, { v: '0', l: 'Missed', fg: '#16a34a' }]} />
        <AgentStatusCard color="#d97706" name="UpgradeAdvisorAgent" status="1 Flagged" statusBg="#fffbeb" statusFg="#d97706" statusBd="#fde68a"
          big="128" subtitle="Upgrade paths validated"
          minis={[{ v: '127', l: 'Safe', fg: '#16a34a' }, { v: '1', l: 'High-Risk', fg: '#dc2626' }, { v: '0', l: 'Skipped', fg: '#16a34a' }]} />
        <AgentStatusCard color="#059669" name="MentorAgent" status="Active" statusBg="#f0fdf4" statusFg="#16a34a" statusBd="#bbf7d0"
          big="1,847" subtitle="KB queries answered · 100% cited"
          minis={[{ v: '<30s', l: 'Avg Time', fg: '#059669' }, { v: '100%', l: 'Citations', fg: '#059669' }, { v: '0', l: 'Halluc.', fg: '#059669' }]} />
      </div>

      {/* Main 3-column grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>

        {/* Live Agent Feed */}
        <div style={{ ...panel, display: 'flex', flexDirection: 'column' }}>
          <div style={panelHeader}>
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Live Agent Feed</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>Real-time decisions · All 4 agents</div>
            </div>
            <span style={chip('#fef2f2', '#dc2626', '#fecaca')}>
              <span style={dot('#ef4444')} /> Live
            </span>
          </div>
          <div style={{ flex: 1, height: 420, overflowY: 'auto', padding: '14px 16px', background: '#020408', borderRadius: '0 0 16px 16px',
            fontFamily: "'JetBrains Mono', monospace", fontSize: 11.5, lineHeight: 1.75 }}>
            {feed.map((f, i) => (
              <div key={i} style={{ animation: 'slideDown .25s ease forwards' }}>
                <span style={{ color: '#94a3b8' }}>{f.time}</span> <span dangerouslySetInnerHTML={{ __html: f.html }} />
              </div>
            ))}
          </div>
        </div>

        {/* Schema Diff + Upgrade Path */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Schema Diff */}
          <div style={panel}>
            <div style={panelHeader}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Schema Drift · Wind River FW 3.2.1</div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>Detected 06:15 UTC · 6 scripts impacted</div>
              </div>
              <span style={chip('#fef2f2', '#dc2626', '#fecaca')}>Breaking</span>
            </div>
            <div style={{ padding: '14px 16px' }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: '#94a3b8', marginBottom: 8, letterSpacing: '.06em', textTransform: 'uppercase' }}>
                Redfish API Change
              </div>
              <div style={{ background: '#020408', borderRadius: 10, padding: '14px 16px', fontFamily: "'JetBrains Mono', monospace", fontSize: 11, lineHeight: 1.75, color: '#e2e8f0' }}>
                <div style={{ color: '#94a3b8' }}>{'  "chassis": {'}</div>
                <div style={{ color: '#94a3b8' }}>{'    "id": "chassis-1",'}</div>
                <div><span style={{ color: '#f87171', background: 'rgba(248,113,113,.08)', padding: '1px 4px', borderRadius: 3, textDecoration: 'line-through' }}>    "power": {'{ "state": "On" }'}</span></div>
                <div><span style={{ color: '#4ade80', background: 'rgba(74,222,128,.08)', padding: '1px 4px', borderRadius: 3 }}>    "power": {'{ "powerState": "On" }'}</span></div>
                <div style={{ color: '#94a3b8' }}>{'    "thermal": { "status": "OK" }'}</div>
                <div style={{ color: '#94a3b8' }}>{'  }'}</div>
                <div style={{ marginTop: 8, color: '#fbbf24' }}>! Field renamed: power.state → power.powerState</div>
                <div style={{ color: '#f87171' }}>! 6 Ansible playbooks reference deprecated path</div>
                <div style={{ color: '#4ade80' }}>✓ JIRA epic APEX-SCHEMA-047 created · 6 sub-tasks</div>
              </div>
              <div style={{ marginTop: 10, display: 'flex', gap: 8 }}>
                <div style={{ flex: 1, background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '8px 10px' }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: '#dc2626' }}>6 Scripts Impacted</div>
                  <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>ansible/power-check.yml +5 more</div>
                </div>
                <div style={{ flex: 1, background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 8, padding: '8px 10px' }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: '#16a34a' }}>6 Days Lead Time</div>
                  <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>Before next cert cycle</div>
                </div>
              </div>
            </div>
          </div>

          {/* Upgrade Path */}
          <div style={panel}>
            <div style={panelHeader}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Upgrade Path · High-Risk Flag</div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>CaaS-Node-Type-B · Northeast</div>
              </div>
              <span style={chip('#fef2f2', '#dc2626', '#fecaca')}>78% Fail Rate</span>
            </div>
            <div style={{ padding: '14px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '8px 12px', fontFamily: "'JetBrains Mono', monospace", fontSize: 13, fontWeight: 700, color: '#dc2626' }}>23.06</div>
                <span style={{ color: '#94a3b8' }}>→</span>
                <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '8px 12px', fontFamily: "'JetBrains Mono', monospace", fontSize: 13, fontWeight: 700, color: '#dc2626' }}>24.01</div>
                <div style={{ flex: 1, textAlign: 'right' }}>
                  <span style={{ fontSize: 10, fontWeight: 700, color: '#dc2626', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 6, padding: '3px 8px' }}>BLOCKED — Skip Level</span>
                </div>
              </div>
              <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 10, padding: 12, marginBottom: 10 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: '#b45309', marginBottom: 6 }}>Recommended Path (3 steps)</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: '#334155' }}>
                  <span style={{ color: '#d97706' }}>23.06</span><span style={{ color: '#94a3b8' }}>→</span>
                  <span style={{ color: '#d97706' }}>23.12</span><span style={{ color: '#94a3b8' }}>→</span>
                  <span style={{ color: '#d97706' }}>24.06</span><span style={{ color: '#94a3b8' }}>→</span>
                  <span style={{ color: '#16a34a' }}>24.01</span>
                </div>
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 6 }}>Est. duration: 4.5 hrs · Pre-checks: 7 items · HITL required</div>
              </div>
              <div style={{ fontSize: 11, color: '#b91c1c', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: 10 }}>
                <strong>Risk override:</strong> 23.06→24.01 direct on Type-B Northeast triggers a critical risk score (skip-level + breaking schema diff + thermal pattern). UpgradeAdvisorAgent blocks the path and requires Distinguished-Engineer co-signature.
              </div>
            </div>
          </div>
        </div>

        {/* HITL + Audit Lens */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* HITL */}
          <div style={panel}>
            <div style={panelHeader}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>HITL Approval Queue</div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>Human decisions required</div>
              </div>
              <span style={chip('#fffbeb', '#d97706', '#fde68a')}>
                {hitlPendingCount} Pending
              </span>
            </div>
            <div style={{ padding: '14px 16px' }}>
              {hitlItems.length === 0 && (
                <div style={{
                  padding: '18px 14px', borderRadius: 10,
                  border: '1px dashed #cbd5e1',
                  background: '#f8fafc',
                  fontSize: 11, color: '#94a3b8', textAlign: 'center', marginBottom: 8,
                }}>
                  No HITL gates open · Pipeline running clean
                </div>
              )}
              {hitlItems.map((item) => {
                const palette = item.severity === 'high'
                  ? { iconBg: 'rgba(239,68,68,.1)',  iconColor: '#f87171', rowBg: 'rgba(239,68,68,.06)',  rowBd: 'rgba(239,68,68,.2)' }
                  : { iconBg: 'rgba(245,158,11,.12)', iconColor: '#fbbf24', rowBg: 'rgba(245,158,11,.06)', rowBd: 'rgba(245,158,11,.2)' };
                const ageSec  = Math.max(0, Math.floor((Date.now() - item.created_at) / 1000));
                const ageStr  = ageSec < 60   ? `${ageSec}s ago`
                              : ageSec < 3600 ? `${Math.floor(ageSec/60)} min ago`
                                              : `${Math.floor(ageSec/3600)} hrs ago`;
                const failCt    = item.data?.fail_count;
                const breakCt   = item.data?.breaking_changes;
                const detail = (
                  <>
                    {item.reason}
                    {(typeof failCt === 'number' || typeof breakCt === 'number') && (
                      <span style={{ color: '#9ca3af' }}>
                        {typeof failCt === 'number' && <> · <span style={{ color: '#f87171', fontWeight: 700 }}>{failCt} failures</span></>}
                        {typeof breakCt === 'number' && breakCt > 0 && <> · <span style={{ color: '#f87171', fontWeight: 700 }}>{breakCt} breaking</span></>}
                      </span>
                    )}
                  </>
                );
                return (
                  <DarkHitlRow
                    key={item.request_id}
                    title={`${item.agent} · ${item.gate}`}
                    detail={detail}
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
              <div style={{ padding: 10, background: '#f8fafc', borderRadius: 8, border: '1px solid #e8edf2', marginTop: 4 }}>
                <div style={{ fontSize: 10, color: '#94a3b8', lineHeight: 1.5 }}>
                  Every decision is written immutably to the <strong style={{ color: '#475569' }}>Audit Lens</strong> with reviewer name, timestamp, and override notes.
                </div>
              </div>
            </div>
          </div>

          {/* Audit Lens timeline */}
          <div style={{ ...panel, flex: 1 }}>
            <div style={panelHeader}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Audit Lens</div>
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>Immutable audit trail · 7-year retention</div>
              </div>
              <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>
                <span style={dot('#22c55e')} /> Recording
              </span>
            </div>
            <div style={{ padding: '14px 16px', maxHeight: 280, overflowY: 'auto' }}>
              <DvrItem color="#a855f7" title="CertAgent · Report Issued · NE-4821"   meta="06:47:23 · J. Patchett" />
              <DvrItem color="#f59e0b" title="UpgradeAdv · HIGH-RISK Flag Raised"     meta="06:43:55 · Automated" />
              <DvrItem color="#06b6d4" title="SchemaWatch · Drift Detected"            meta="06:31:07 · Automated" />
              <DvrItem color="#10b981" title="MentorAgent · KB Query Answered"        meta="06:28:11 · R. Chen" />
              <DvrItem color="#a855f7" title="CertAgent · HITL Approved · NE-4817"    meta="05:14:02 · J. Patchett" />
              <DvrItem color="#f59e0b" title="UpgradeAdv · 128 Paths Validated"       meta="04:00:00 · Automated" last />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom row: Predictive Intelligence panel — live SageMaker output */}
      <div style={{ ...panel, padding: '18px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Predictive Intelligence</div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>
              Real-time wave risk scoring · 3 SageMaker endpoints · {vzStatusQuery.data?.endpoints?.filter(e => e.status === 'InService').length ?? 0}/3 InService
            </div>
          </div>
          <span style={chip(
            vzModelsLive ? 'rgba(34,197,94,.12)'    : 'rgba(245,158,11,.12)',
            vzModelsLive ? '#4ade80'                : '#fbbf24',
            vzModelsLive ? 'rgba(34,197,94,.25)'    : 'rgba(245,158,11,.25)',
          )}>
            {vzModelsLive ? '● Models Live' : '◌ Endpoints provisioning'}
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          {/* Wave-risk card — driven by apex-signal-vz-wave-risk */}
          <div style={{ background: '#f8fafc', borderRadius: 10, padding: '14px 16px',
                        border: '1px solid #e8edf2' }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', color: '#a855f7', textTransform: 'uppercase', marginBottom: 6 }}>
              vz-wave-risk · XGBoost
            </div>
            <div style={{ fontSize: 26, fontWeight: 900, color:
              vzWaveQuery.data?.risk_tier === 'critical' ? '#ef4444' :
              vzWaveQuery.data?.risk_tier === 'high'     ? '#f97316' :
              vzWaveQuery.data?.risk_tier === 'medium'   ? '#f59e0b' :
              vzWaveQuery.data?.risk_tier === 'low'      ? '#22c55e' : '#94a3b8',
              fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}>
              {vzWaveQuery.data
                ? `${(vzWaveQuery.data.probability_of_outage * 100).toFixed(1)}%`
                : '— '}
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
              {vzWaveQuery.data?.risk_tier?.toUpperCase() ?? 'loading…'} · default wave
            </div>
            <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 8, lineHeight: 1.5 }}>
              {(vzWaveQuery.data?.top_reasons ?? ['Northeast · Type-B · 23.06→24.01']).slice(0,2).join(' · ')}
            </div>
          </div>

          {/* Site-cert card — placeholder for per-site batch score */}
          <div style={{ background: '#f8fafc', borderRadius: 10, padding: '14px 16px',
                        border: '1px solid #e8edf2' }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', color: '#0891b2', textTransform: 'uppercase', marginBottom: 6 }}>
              vz-site-cert · XGBoost
            </div>
            <div style={{ fontSize: 26, fontWeight: 900, color: '#0891b2', fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}>
              16,247
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>Sites scored · pre-flight</div>
            <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 8, lineHeight: 1.5 }}>
              Per-site P(fail) before the 247-test cycle runs. Batch endpoint at /signals/vz/site-cert/batch.
            </div>
          </div>

          {/* Thermal anomaly card */}
          <div style={{ background: '#f8fafc', borderRadius: 10, padding: '14px 16px',
                        border: '1px solid #e8edf2' }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', color: '#d97706', textTransform: 'uppercase', marginBottom: 6 }}>
              vz-thermal-anomaly · RCF
            </div>
            <div style={{ fontSize: 26, fontWeight: 900, color: '#d97706', fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}>
              168h
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>Rolling thermal window · per-site</div>
            <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 8, lineHeight: 1.5 }}>
              Random Cut Forest scores hourly thermal readings. Score ≥ 1.5 → anomaly cluster watch.
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
        @keyframes slideDown { from{opacity:0;transform:translateY(-4px)} to{opacity:1;transform:translateY(0)} }
        @keyframes hitlPulse {
          0%,100% { box-shadow: 0 0 0 0 rgba(245,158,11,.0); }
          50%     { box-shadow: 0 0 0 4px rgba(245,158,11,.18); }
        }
      `}</style>
    </div>
  );
}

// ──────────────────── sub-components ────────────────────

function AgentStatusCard(props: {
  color: string; name: string; status: string;
  statusBg: string; statusFg: string; statusBd: string;
  big: string; subtitle: string;
  minis?: Array<{ v: string; l: string; fg: string }>;
  extra?: React.ReactNode;
}) {
  return (
    <div style={{ ...panel, padding: '16px 18px', borderLeft: `3px solid ${props.color}` }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: props.color }}>
          {props.name}
        </div>
        <span style={chip(props.statusBg, props.statusFg, props.statusBd)}>{props.status}</span>
      </div>
      <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 28, fontWeight: 800, color: '#0f172a', lineHeight: 1 }}>
        {props.big}
      </div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{props.subtitle}</div>
      {props.minis && (
        <div style={{ marginTop: 10, display: 'flex', gap: 6 }}>
          {props.minis.map((m) => (
            <div key={m.l} style={{ flex: 1, background: `${m.fg}1a`, border: `1px solid ${m.fg}33`, borderRadius: 6, padding: '5px 8px', textAlign: 'center' }}>
              <div style={{ fontSize: 13, fontWeight: 800, color: m.fg }}>{m.v}</div>
              <div style={{ fontSize: 9, color: '#94a3b8' }}>{m.l}</div>
            </div>
          ))}
        </div>
      )}
      {props.extra && <div style={{ marginTop: 10 }}>{props.extra}</div>}
    </div>
  );
}

function DarkHitlRow(props: {
  title: string; detail: React.ReactNode; meta: string;
  status: string;            // 'pending' | 'approve' | 'reject' | 'timeout'
  reviewer?: string;
  busy: boolean;
  onApprove: () => void; onReject: () => void;
  iconBg: string; iconColor: string; rowBg: string; rowBd: string;
}) {
  const isPending  = props.status === 'pending';
  const isApproved = props.status === 'approve';
  const isRejected = props.status === 'reject';
  const isTimeout  = props.status === 'timeout';

  const bg = isApproved ? 'rgba(34,197,94,.08)' :
             isRejected ? 'rgba(239,68,68,.08)' :
             isTimeout  ? 'rgba(148,163,184,.08)' : props.rowBg;
  const bd = isApproved ? 'rgba(34,197,94,.25)' :
             isRejected ? 'rgba(239,68,68,.25)' :
             isTimeout  ? 'rgba(148,163,184,.25)' : props.rowBd;
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', gap: 12,
      padding: '14px 16px', borderRadius: 12,
      border: `1px solid ${bd}`, marginBottom: 8, background: bg,
      animation: isPending ? 'hitlPulse 2s ease-in-out infinite' : undefined,
    }}>
      <div style={{ width: 36, height: 36, borderRadius: 10, background: props.iconBg, border: `1px solid ${props.iconColor}40`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, color: props.iconColor, fontSize: 16 }}>⚠</div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a' }}>{props.title}</div>
        <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>{props.detail}</div>
        <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2, fontFamily: "'JetBrains Mono', monospace" }}>{props.meta}</div>
        {isPending ? (
          <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
            <button
              onClick={props.onApprove}
              disabled={props.busy}
              style={{ flex: 1, padding: 6, background: '#16a34a', color: '#fff',
                       border: '1px solid #16a34a', borderRadius: 7,
                       fontSize: 11, fontWeight: 700,
                       cursor: props.busy ? 'not-allowed' : 'pointer',
                       opacity: props.busy ? 0.5 : 1 }}>
              {props.busy ? '...' : '✓ Approve'}
            </button>
            <button
              onClick={props.onReject}
              disabled={props.busy}
              style={{ flex: 1, padding: 6, background: '#fff', color: '#dc2626',
                       border: '1px solid #fca5a5', borderRadius: 7,
                       fontSize: 11, fontWeight: 700,
                       cursor: props.busy ? 'not-allowed' : 'pointer',
                       opacity: props.busy ? 0.5 : 1 }}>
              {props.busy ? '...' : '✗ Reject'}
            </button>
          </div>
        ) : (
          <div style={{ marginTop: 8, fontSize: 11, fontWeight: 700,
                        color: isApproved ? '#16a34a' : isRejected ? '#dc2626' : '#94a3b8' }}>
            {isApproved && <>✓ Approved{props.reviewer ? ` — ${props.reviewer}` : ''} · Logged to Audit Lens</>}
            {isRejected && <>✗ Rejected{props.reviewer ? ` — ${props.reviewer}` : ''} · Pipeline halted</>}
            {isTimeout  && <>⏱ Timed out · Pipeline halted</>}
          </div>
        )}
      </div>
    </div>
  );
}

function DvrItem({ color, title, meta, last }: { color: string; title: string; meta: string; last?: boolean }) {
  return (
    <div style={{ display: 'flex', gap: 10, paddingBottom: last ? 0 : 10, borderLeft: '2px solid #e8edf2', marginLeft: 5, paddingLeft: 14, position: 'relative' }}>
      <div style={{ position: 'absolute', left: -5, top: 2, width: 8, height: 8, borderRadius: '50%', background: color }} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#0f172a' }}>{title}</div>
        <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 1, fontFamily: "'JetBrains Mono', monospace" }}>{meta}</div>
      </div>
    </div>
  );
}
