/**
 * Verizon Far Edge — Parallel New-Platform Onboarding (the hero).
 *
 * James's most-resonant use case, verbatim: "While it's being certified, you
 * automate the sub-cloud deploy — and automate the testing of that sub-cloud."
 * Three agents run CONCURRENTLY in swimlanes; the orchestrator (one operator)
 * only stops for HITL decisions. Maps to the real Jira board:
 *   • DEPLOY  → VZWFE-24 "Deploy Subcloud - ansible", VZWFE-27 "Install WRA on subclouds"
 *   • TEST    → WRCP 25.09.200 GNRD: Platform / HA / Monitoring / Performance
 *
 * Self-contained + deterministic (no backend / no Foundry Agent Service cold-start).
 */
import React, { useEffect, useRef, useState } from 'react';

type Kind = 'correlate' | 'action' | 'gate';
interface ReviewItem { label: string; diff?: string; reason: string; risk: 'low' | 'medium' | 'high' }
interface LaneStep { title: string; detail: string; kind: Kind; dur: number; jira?: string; review?: { heading: string; artifact: string; items: ReviewItem[] } }
interface Lane { key: string; agent: string; code: string; color: string; tint: string; sub: string; steps: LaneStep[] }

const LANES: Lane[] = [
  {
    key: 'certify', agent: 'CertificationAgent', code: 'CRT', color: '#dc2626', tint: '#fef2f2',
    sub: 'EL140 Gen12 · iLO7 — the gated track',
    steps: [
      { title: 'Detect blocked coverage', detail: 'MEAKV-1750 / 1793 blocked — iLO7 unsupported', kind: 'correlate', dur: 1200 },
      { title: 'Design PROPOSED-20→32', detail: '13 new cases drafted', kind: 'correlate', dur: 1600 },
      { title: 'HITL · authorize live-lab', detail: 'Run PROPOSED-20→28 on the live EL140', kind: 'gate', dur: 0,
        review: { heading: '9 PROPOSED tests will run on the live EL140', artifact: 'test-plan-EL140-PROPOSED-20-28.md · 2607:f160:10:90bf:ce:40a:0:e002', items: [
          { label: 'PROPOSED-20→23 · account/NTP/DNS', diff: 'Redfish GET/PATCH /Managers/1', reason: 'Read-mostly; one ilo-reset ~133s', risk: 'low' },
          { label: 'PROPOSED-24→26 · syslog/events/NIC', diff: 'PATCH /Managers/1/NetworkProtocol', reason: 'Config writes, no reboot', risk: 'low' },
          { label: 'PROPOSED-27→28 · hostname/secure-boot precheck', diff: 'GET /Systems/1/SecureBoot', reason: 'Read-only precheck', risk: 'low' },
        ] } },
      { title: 'Execute ×5 iterations', detail: '9 cases × 5 runs = 45 executions', kind: 'action', dur: 2400 },
      { title: 'Gap analysis → change-spec', detail: '7 CHANGE · 7 NO-CHANGE · 1 VERIFY', kind: 'correlate', dur: 1500 },
      { title: 'HITL · approve 7 playbook changes', detail: '7 Ansible changes across 15 role files', kind: 'gate', dur: 0,
        review: { heading: '7 Ansible role changes across 15 role files', artifact: 'playbook-change-spec-HPE-EL140-Gen12.md · branch el140-ilo7-support', items: [
          { label: 'group_vars/HPE', diff: '+ workload_profile_vRAN: vRAN', reason: 'iLO7 rejects other WorkloadProfile values', risk: 'low' },
          { label: 'roles/network-config/dns', diff: '~ cap DNS to 3 entries (was 6)', reason: 'iLO7 returns HTTP 400 on 6-entry DNS', risk: 'medium' },
          { label: 'roles/security-hardening (NEW)', diff: '+ KEK/DB cert install + SecureBoot', reason: 'No hardening role existed for iLO7', risk: 'high' },
          { label: '+4 more roles', diff: 'account index, syslog, events, hostname', reason: 'iLO7 path/schema deltas', risk: 'low' },
        ] } },
      { title: 'Apply changes · open PR', detail: 'branch el140-ilo7-support → PR (draft)', kind: 'action', dur: 1600 },
      { title: 'Certify + hash-chain audit', detail: 'PASS WITH DEVIATIONS · full lineage', kind: 'correlate', dur: 1200 },
    ],
  },
  {
    key: 'deploy', agent: 'DeployAgent', code: 'DEP', color: '#2563eb', tint: '#eff6ff',
    sub: 'Sub-cloud · Ansible — runs while cert runs',
    steps: [
      { title: 'Provision sub-cloud', detail: 'Ansible bootstrap · current CC version', kind: 'action', dur: 1500, jira: 'VZWFE-30' },
      { title: 'Deploy sub-cloud', detail: 'dcmanager subcloud add → ansible', kind: 'action', dur: 2000, jira: 'VZWFE-24' },
      { title: 'Install WRA on subclouds', detail: 'Wind River Analytics agent', kind: 'action', dur: 1800, jira: 'VZWFE-27' },
      { title: 'Prestaging + enroll', detail: 'subcloud enrolled · managed=true', kind: 'correlate', dur: 1400 },
      { title: 'Sub-cloud ready', detail: 'handed to TestAgent', kind: 'correlate', dur: 1000 },
    ],
  },
  {
    key: 'test', agent: 'TestAgent', code: 'TST', color: '#0891b2', tint: '#ecfeff',
    sub: 'WRCP 25.09.200 GNRD — auto-executed',
    steps: [
      { title: 'Platform suite', detail: 'Deployment · Prestaging · System-SC', kind: 'action', dur: 1700, jira: 'Platform' },
      { title: 'HA · switchover recovery', detail: 'Halt-induced swact + switchback', kind: 'action', dur: 2100, jira: 'HA 1–14' },
      { title: 'Monitoring', detail: 'Filebeat → Elasticsearch · Metricbeat', kind: 'correlate', dur: 1600, jira: 'Monitoring' },
      { title: 'Performance', detail: 'Network · Robustness · Storage-Ceph', kind: 'correlate', dur: 1800, jira: 'Performance' },
      { title: 'Results → Apex Signal', detail: 'pass/fail rolled up · regressions flagged', kind: 'correlate', dur: 1100 },
    ],
  },
];

const KIND: Record<Kind, { label: string; color: string; bg: string; glyph: string }> = {
  correlate: { label: 'Reporting & Correlation', color: '#2563eb', bg: '#eff6ff', glyph: '◇' },
  action:    { label: 'Direct Lab Action',       color: '#dc2626', bg: '#fef2f2', glyph: '⚡' },
  gate:      { label: 'HITL Gate',               color: '#d97706', bg: '#fffbeb', glyph: '⏸' },
};
const riskTone = (r: string) => r === 'high' ? '#dc2626' : r === 'medium' ? '#d97706' : '#16a34a';
function btn(bg: string, color: string, bd?: string): React.CSSProperties {
  return { display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 700, padding: '9px 18px', borderRadius: 9, cursor: 'pointer', border: `1px solid ${bd || bg}`, background: bg, color };
}

export function VerizonParallelOnboarding() {
  const [phase, setPhase] = useState<'idle' | 'running' | 'awaiting' | 'done'>('idle');
  const [prog, setProg] = useState<Record<string, number>>({ certify: 0, deploy: 0, test: 0 });
  const [gate, setGate] = useState<{ lane: string; idx: number } | null>(null);
  const [approvals, setApprovals] = useState(0);
  const timers = useRef<number[]>([]);
  const doneLanes = useRef<Set<string>>(new Set());

  const clear = () => { timers.current.forEach((t) => clearTimeout(t)); timers.current = []; };
  useEffect(() => () => clear(), []);

  const reset = () => { clear(); doneLanes.current = new Set(); setPhase('idle'); setProg({ certify: 0, deploy: 0, test: 0 }); setGate(null); setApprovals(0); };

  const advance = (laneKey: string, idx: number) => {
    const lane = LANES.find((l) => l.key === laneKey)!;
    if (idx >= lane.steps.length) {
      doneLanes.current.add(laneKey);
      if (doneLanes.current.size === LANES.length) setPhase('done');
      return;
    }
    const step = lane.steps[idx];
    if (step.kind === 'gate') {
      setGate({ lane: laneKey, idx });
      setPhase('awaiting');
      return; // pause THIS lane; others keep running
    }
    const t = window.setTimeout(() => {
      setProg((p) => ({ ...p, [laneKey]: idx + 1 }));
      advance(laneKey, idx + 1);
    }, step.dur);
    timers.current.push(t);
  };

  const start = () => {
    reset();
    setPhase('running');
    // staggered concurrent kick-off — lanes visibly move together
    LANES.forEach((l, i) => {
      const t = window.setTimeout(() => advance(l.key, 0), 250 + i * 180);
      timers.current.push(t);
    });
  };

  const approve = () => {
    if (!gate) return;
    const { lane, idx } = gate;
    setProg((p) => ({ ...p, [lane]: idx + 1 }));
    setApprovals((n) => n + 1);
    setGate(null);
    setPhase('running');
    const t = window.setTimeout(() => advance(lane, idx + 1), 200);
    timers.current.push(t);
  };

  const gateStep = gate ? LANES.find((l) => l.key === gate.lane)!.steps[gate.idx] : null;
  const totalSteps = LANES.reduce((n, l) => n + l.steps.length, 0);
  const doneSteps = Object.values(prog).reduce((a, b) => a + b, 0);
  const actionsCount = LANES.reduce((n, l) => n + l.steps.filter((s) => s.kind === 'action').length, 0);
  const gateCount = LANES.reduce((n, l) => n + l.steps.filter((s) => s.kind === 'gate').length, 0);

  const card: React.CSSProperties = { background: '#fff', border: '1px solid #e8edf2', borderRadius: 16, boxShadow: '0 1px 2px rgba(15,23,42,.04)' };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#1e293b', background: '#f0f4f8', minHeight: '100vh', padding: '24px 32px 36px', maxWidth: 1600, margin: '0 auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase', color: '#ee0000' }}>
            Mission Control · Parallel Onboarding
          </div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 23, fontWeight: 800, color: '#0f172a', marginTop: 4, letterSpacing: '-.02em' }}>
            One server in. Three agents working at once.
          </div>
          <div style={{ fontSize: 12.5, color: '#475569', marginTop: 5, maxWidth: 860, lineHeight: 1.45 }}>
            “While it’s being certified, you automate the sub-cloud deploy — and the testing of that sub-cloud.” One operator
            runs all three; <strong style={{ color: '#0f172a' }}>Apex only stops for the decisions that matter.</strong>
          </div>
        </div>
        <div>
          {phase === 'idle' || phase === 'done'
            ? <button onClick={start} style={btn('#ee0000', '#fff')}>{phase === 'done' ? '↻ Run Again' : '▶ Run Onboarding'}</button>
            : <button onClick={reset} style={btn('#fff', '#475569', '#cbd5e1')}>■ Reset</button>}
        </div>
      </div>

      {/* tier legend + live counters */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 16, alignItems: 'center' }}>
        <Legend color="#2563eb" glyph="◇" text="Reporting & Correlation · read-only · auto" />
        <Legend color="#dc2626" glyph="⚡" text="Direct Lab Action · HITL-gated" />
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <Mini v={`${doneSteps}/${totalSteps}`} l="steps" />
          <Mini v={String(approvals)} l="approvals" tone="#16a34a" />
          <Mini v="3" l="agents · 1 operator" tone="#6c47ff" />
        </div>
      </div>

      {/* GATE BANNER — full width, shows WHAT you're approving (Brent's ask) */}
      {phase === 'awaiting' && gateStep && (
        <div style={{ ...card, border: '1px solid #fbbf24', background: '#fffdf5', padding: '16px 18px', marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 8 }}>
            <span style={{ fontSize: 14, fontWeight: 800, color: '#b45309' }}>⏸ Approval required — CertificationAgent paused. Deploy &amp; Test keep running.</span>
            <span style={{ fontSize: 10.5, color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>{gateStep.review?.artifact}</span>
          </div>
          <div style={{ fontSize: 12.5, fontWeight: 700, color: '#0f172a', margin: '8px 0 10px' }}>🔍 Review — {gateStep.review?.heading}</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 22px', marginBottom: 14 }}>
            {gateStep.review?.items.map((it, k) => (
              <div key={k} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                <span style={{ flexShrink: 0, marginTop: 1, fontSize: 8.5, fontWeight: 800, color: riskTone(it.risk), background: `${riskTone(it.risk)}14`, border: `1px solid ${riskTone(it.risk)}40`, borderRadius: 5, padding: '2px 6px', width: 52, textAlign: 'center' }}>{it.risk.toUpperCase()}</span>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 700, color: '#0f172a' }}>{it.label}</div>
                  {it.diff && <div style={{ fontSize: 10.5, color: '#0891b2', fontFamily: "'JetBrains Mono', monospace" }}>{it.diff}</div>}
                  <div style={{ fontSize: 11, color: '#64748b' }}>{it.reason}</div>
                </div>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
            <button onClick={approve} style={btn('#16a34a', '#fff')}>✓ Approve {gateStep.review?.items.length} change{(gateStep.review?.items.length ?? 0) > 1 ? 's' : ''} &amp; continue</button>
            <button onClick={reset} style={btn('#fff', '#dc2626', '#fca5a5')}>Reject</button>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>Hash-chained to the Audit Lens with your name + timestamp.</span>
          </div>
        </div>
      )}

      {/* SWIMLANES */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, alignItems: 'start' }}>
        {LANES.map((lane) => {
          const done = prog[lane.key];
          const laneComplete = done >= lane.steps.length;
          const isGatedHere = gate?.lane === lane.key;
          return (
            <div key={lane.key} style={{ ...card, padding: 16 }}>
              {/* lane header */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                <span style={{ width: 30, height: 30, borderRadius: 8, background: lane.tint, color: lane.color, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 800 }}>{lane.code}</span>
                <div>
                  <div style={{ fontSize: 14.5, fontWeight: 800, color: '#0f172a' }}>{lane.agent}</div>
                  <div style={{ fontSize: 10.5, color: '#94a3b8' }}>{lane.sub}</div>
                </div>
                {phase !== 'idle' && (
                  <span style={{ marginLeft: 'auto', fontSize: 10, fontWeight: 700, color: laneComplete ? '#16a34a' : isGatedHere ? '#d97706' : lane.color }}>
                    {laneComplete ? '✓ done' : isGatedHere ? '⏸ paused' : '● running'}
                  </span>
                )}
              </div>
              {/* lane progress bar */}
              <div style={{ height: 4, background: '#eef2f7', borderRadius: 2, overflow: 'hidden', margin: '8px 0 12px' }}>
                <div style={{ width: `${(done / lane.steps.length) * 100}%`, height: '100%', background: lane.color, transition: 'width .5s' }} />
              </div>
              {/* steps */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {lane.steps.map((st, i) => {
                  const isDone = i < done;
                  const isActive = i === done && phase === 'running' && !laneComplete;
                  const isGate = st.kind === 'gate';
                  const pendingGateHere = isGate && isGatedHere && gate?.idx === i;
                  const k = KIND[st.kind];
                  const shown = isDone || isActive || pendingGateHere;
                  return (
                    <div key={i} style={{
                      display: 'flex', gap: 9, padding: '8px 10px', borderRadius: 9,
                      background: pendingGateHere ? '#fffbeb' : isActive ? `${lane.color}0a` : '#fff',
                      border: `1px solid ${pendingGateHere ? '#fde68a' : isActive ? lane.color : '#eef2f7'}`,
                      opacity: shown ? 1 : 0.4, transition: 'all .3s',
                    }}>
                      <span style={{ flexShrink: 0, width: 18, height: 18, borderRadius: 5, marginTop: 1, background: isDone ? '#16a34a' : k.bg, color: isDone ? '#fff' : k.color, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 800 }}>
                        {isDone ? '✓' : k.glyph}
                      </span>
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
                          <span style={{ fontSize: 12.5, fontWeight: 700, color: '#0f172a' }}>{st.title}</span>
                          {st.jira && <span style={{ fontSize: 8.5, fontWeight: 700, color: '#475569', background: '#f1f5f9', borderRadius: 4, padding: '1px 5px', fontFamily: "'JetBrains Mono', monospace" }}>{st.jira}</span>}
                        </div>
                        <div style={{ fontSize: 11, color: '#64748b', marginTop: 1 }}>{st.detail}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* completion banner */}
      {phase === 'done' && (
        <div style={{ ...card, border: '1px solid #bbf7d0', background: '#f0fdf4', padding: '16px 18px', marginTop: 16 }}>
          <div style={{ fontSize: 14.5, fontWeight: 800, color: '#15803d' }}>✓ Platform onboarded — certified, deployed, and tested in one run</div>
          <div style={{ fontSize: 12.5, color: '#166534', marginTop: 5, lineHeight: 1.5 }}>
            3 agents ran <strong>concurrently</strong> · {totalSteps} steps · {actionsCount} direct lab actions · {gateCount} human approvals.
            One operator drove the whole campaign — every lab action reviewed, approved, and hash-chained to the audit log.
            <strong> Manual baseline ~40 h → orchestrated ~18 min.</strong>
          </div>
        </div>
      )}

      {/* footer note */}
      <div style={{ fontSize: 11.5, color: '#94a3b8', marginTop: 14 }}>
        Grounded in your real test taxonomy — WRCP 25.09.200 GNRD (Platform · HA · Monitoring · Performance) and sub-cloud deploy tickets VZWFE-24 / VZWFE-27.
      </div>
    </div>
  );
}

function Legend({ color, glyph, text }: { color: string; glyph: string; text: string }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, fontSize: 11.5, fontWeight: 600, color: '#475569', background: '#fff', border: '1px solid #e8edf2', borderRadius: 99, padding: '5px 12px' }}>
      <span style={{ color, fontWeight: 800 }}>{glyph}</span>{text}
    </span>
  );
}
function Mini({ v, l, tone }: { v: string; l: string; tone?: string }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'baseline', gap: 5, background: '#fff', border: '1px solid #e8edf2', borderRadius: 9, padding: '5px 11px' }}>
      <span style={{ fontSize: 15, fontWeight: 800, color: tone || '#0f172a', fontFamily: "'Space Grotesk', sans-serif" }}>{v}</span>
      <span style={{ fontSize: 10.5, color: '#94a3b8' }}>{l}</span>
    </span>
  );
}
