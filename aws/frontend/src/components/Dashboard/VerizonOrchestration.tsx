/**
 * VerizonOrchestration — the demo centerpiece for Bob.
 *
 * Shows the OrchestratorAgent autonomously running a new-platform onboarding
 * cert (HPE EL140 Gen12 / iLO 7) through MULTIPLE ITERATIONS, and — the key
 * ask — clearly separating the platform's two tiers:
 *
 *   • REPORTING & CORRELATION  (blue)  — read-only intelligence, auto-runs.
 *   • DIRECT LAB ACTION        (red)   — executes on live lab hardware,
 *                                         every action gated by human approval.
 *
 * Client-animated from /signals/vz/orchestration/state (offline-safe) so the
 * run is 100% reliable in a live demo — no SSE/connection risk.
 */
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api/v1';

interface Iteration { n: number; label: string; result: string; metric: string }
interface Step {
  seq: number; agent: string; kind: 'correlate' | 'action' | 'gate';
  title: string; detail: string; evidence: string;
  requires_hitl: boolean; duration_ms: number;
  lab_target?: string; iterations?: Iteration[];
}
interface CampaignRef { id: string; label: string; platform: string }
interface OrchState {
  campaign_id?: string;
  campaign: string; platform: string; source: string;
  campaigns?: CampaignRef[];
  agents: Record<string, { code: string; name: string; color: string }>;
  tiers: Record<string, { label: string; sublabel: string; color: string }>;
  summary: {
    total_steps: number; correlate_steps: number; action_steps: number;
    hitl_gates: number; total_iterations: number;
    manual_baseline_hrs: number; orchestrated_min: number;
  };
  timeline: Step[];
}

/* ── offline-safe fallback (mirrors /signals/vz/orchestration/state) ── */
const FALLBACK: OrchState = {
  campaign: 'HPE EL140 Gen12 · New-Platform Onboarding',
  platform: 'HPE ProLiant Compute EL140 Gen12 · iLO 7 v1.20.00 · BIOS v1.30',
  source: 'Real campaign · James Patchett · MTCE Lab · 2026-06-10',
  agents: {
    orchestrator: { code: 'ORC', name: 'OrchestratorAgent', color: '#6c47ff' },
    cert:         { code: 'CRT', name: 'CertificationAgent', color: '#1d4ed8' },
    playbook:     { code: 'PBK', name: 'PlaybookAgent',      color: '#0891b2' },
    signal:       { code: 'SIG', name: 'SignalAgent',        color: '#d97706' },
  },
  tiers: {
    correlate: { label: 'Reporting & Correlation', sublabel: 'Read-only intelligence · auto-runs · mutates nothing in the lab', color: '#2563eb' },
    action:    { label: 'Direct Lab Action', sublabel: 'Executes on live hardware · every action HITL-gated', color: '#dc2626' },
  },
  summary: { total_steps: 15, correlate_steps: 7, action_steps: 5, hitl_gates: 3, total_iterations: 10, manual_baseline_hrs: 40, orchestrated_min: 18 },
  timeline: [
    { seq: 1, agent: 'cert', kind: 'correlate', title: 'Detect blocked coverage', detail: 'Read EL140 Gen12 intake. MEAKV-1750 / MEAKV-1793 are BLOCKED — iLO 7 is a new server type the existing BMC playbook does not support.', evidence: 'iLO 7 v1.20.00 · BIOS v1.30 · 273-attr registry', requires_hitl: false, duration_ms: 1400 },
    { seq: 2, agent: 'orchestrator', kind: 'correlate', title: 'Design test coverage', detail: 'Propose PROPOSED-20→32: account mgmt, NTP, DNS, hostname, syslog, Redfish events, NIC/MAC discovery, BIOS WorkloadProfile, secure boot.', evidence: '13 new test cases drafted', requires_hitl: false, duration_ms: 2100 },
    { seq: 3, agent: 'orchestrator', kind: 'gate', title: 'HITL · authorize live-lab execution', detail: 'Running PROPOSED-20→28 against the live EL140 mutates lab hardware. Approve to proceed.', evidence: 'Target: live lab unit via vcpe-jumpserver2 SSH proxy', requires_hitl: true, duration_ms: 0 },
    { seq: 4, agent: 'cert', kind: 'action', title: 'Connect + capture baseline', detail: 'SSH proxy → Redfish GET live EL140 baseline.', evidence: 'GET /redfish/v1/Managers/1 · live unit', lab_target: 'EL140 · 2607:f160:10:90bf:ce:40a:0:e002', requires_hitl: false, duration_ms: 1800 },
    { seq: 5, agent: 'cert', kind: 'action', title: 'Execute PROPOSED-20→28 · 5 iterations each', detail: 'Run the provisioning + cert suite through 5 iterations for statistical confidence. Live Redfish calls.', evidence: '9 test cases × 5 runs = 45 executions', lab_target: 'EL140 · iLO 7 Redfish', requires_hitl: false, duration_ms: 5200, iterations: [
      { n: 1, label: 'run1', result: 'pass', metric: '9/9 pass · 133s ilo-reset' },
      { n: 2, label: 'run2', result: 'pass', metric: '9/9 pass · 131s' },
      { n: 3, label: 'run3', result: 'pass-dev', metric: '8/9 · DNS 6-entry → HTTP 400' },
      { n: 4, label: 'run4', result: 'pass', metric: '9/9 · DNS retried 3-entry' },
      { n: 5, label: 'run5', result: 'pass', metric: '9/9 pass · stable' },
    ] },
    { seq: 6, agent: 'signal', kind: 'correlate', title: 'Pull real reference values from live e930t', detail: 'Read production NTP/DNS/syslog from a live e930t (iLO 6) — real config, not placeholders.', evidence: 'syslog vcp-faredge-syslog.mon.vzwops.com:5140', requires_hitl: false, duration_ms: 1600 },
    { seq: 7, agent: 'signal', kind: 'correlate', title: 'Cross-platform correlation', detail: 'Several iLO 7 deviations are ALSO present on iLO 6 — broadening the playbook scope beyond EL140.', evidence: '3 deviations confirmed on iLO6 + iLO7', requires_hitl: false, duration_ms: 2000 },
    { seq: 8, agent: 'playbook', kind: 'correlate', title: 'Gap analysis → draft change-spec', detail: 'Cross-reference results against the live Ansible playbook. Produce a change spec — a PROPOSAL, nothing applied.', evidence: '7 CHANGE · 7 NO-CHANGE · 1 VERIFY · 15 role files', requires_hitl: false, duration_ms: 2600 },
    { seq: 9, agent: 'signal', kind: 'correlate', title: 'Compliance + drift scan', detail: 'NEBS 62°C inlet threshold unset on EL140. No security-hardening role. iDRAC thermal thresholds drifted across firmware.', evidence: '2 compliance gaps · 1 firmware drift', requires_hitl: false, duration_ms: 1800 },
    { seq: 10, agent: 'orchestrator', kind: 'gate', title: 'HITL · approve playbook changes', detail: '7 Ansible changes across 15 role files + new security-hardening role. Review before any commit.', evidence: 'playbook-change-spec-HPE-EL140-Gen12.md', requires_hitl: true, duration_ms: 0 },
    { seq: 11, agent: 'playbook', kind: 'action', title: 'Apply playbook changes · open PR', detail: 'Commit the 7 approved changes and open a PR for the automation team. Version-controlled + auditable.', evidence: 'branch: el140-ilo7-support → PR (draft)', lab_target: 'vcpe-jumpserver2:/home/patchja/bmc_playbook_EL140', requires_hitl: false, duration_ms: 2200 },
    { seq: 12, agent: 'orchestrator', kind: 'gate', title: 'HITL · approve BIOS + secure-boot config', detail: 'Set BIOS WorkloadProfile=vRAN and install Secure Boot certs on the live EL140 — requires a cold-boot cycle.', evidence: 'PROPOSED-30 · 9-step · ~8–10 min POST', requires_hitl: true, duration_ms: 0 },
    { seq: 13, agent: 'cert', kind: 'action', title: 'Configure BIOS + Secure Boot', detail: 'PATCH WorkloadProfile=vRAN, POST KEK+DB certs, enable SecureBoot, ForceRestart → cold boot → poll FinishedPost.', evidence: 'PATCH /Systems/1/Bios · cert count baseline+1', lab_target: 'EL140 · iLO 7 Redfish', requires_hitl: false, duration_ms: 4200 },
    { seq: 14, agent: 'cert', kind: 'action', title: 'Re-certify · 5 iterations', detail: 'Re-run the full PROPOSED suite post-config through 5 iterations to confirm green + stable.', evidence: '9 cases × 5 runs · all pass', lab_target: 'EL140 · iLO 7 Redfish', requires_hitl: false, duration_ms: 4800, iterations: [
      { n: 1, label: 'run1', result: 'pass', metric: '9/9 pass' },
      { n: 2, label: 'run2', result: 'pass', metric: '9/9 pass' },
      { n: 3, label: 'run3', result: 'pass', metric: '9/9 pass' },
      { n: 4, label: 'run4', result: 'pass', metric: '9/9 pass' },
      { n: 5, label: 'run5', result: 'pass', metric: '9/9 · SecureBoot ON · vRAN applied' },
    ] },
    { seq: 15, agent: 'orchestrator', kind: 'correlate', title: 'Certification report + audit trail', detail: 'EL140 Gen12 certified. New test cases added, playbook PR ready, every decision + action hash-chained to the audit log.', evidence: 'PASS WITH DEVIATIONS · 0 fails · full lineage', requires_hitl: false, duration_ms: 1500 },
  ],
};

type StepStatus = 'pending' | 'running' | 'done';

const resultColor = (r: string) =>
  r === 'pass' ? '#16a34a' : r === 'pass-dev' ? '#d97706' : r === 'fail' ? '#dc2626' : '#64748b';

/* Brent's ask: every HITL gate must show WHAT a human is approving — the exact
   change set / diff — before Approve. Keyed by gate title keyword so it resolves
   for both live-API and offline-fallback timelines. */
interface ReviewItem { label: string; diff?: string; reason: string; risk: 'low' | 'medium' | 'high' }
function gateReview(title: string): { heading: string; artifact: string; items: ReviewItem[] } | null {
  const t = title.toLowerCase();
  if (t.includes('live-lab') || t.includes('authorize')) {
    return {
      heading: '9 PROPOSED test cases will execute on the live EL140',
      artifact: 'test-plan-EL140-PROPOSED-20-28.md · target 2607:f160:10:90bf:ce:40a:0:e002',
      items: [
        { label: 'PROPOSED-20→23 · Account mgmt + NTP + DNS', diff: 'Redfish GET/PATCH · /Managers/1', reason: 'Read-mostly; one ilo-reset (~133s)', risk: 'low' },
        { label: 'PROPOSED-24→26 · syslog + Redfish events + NIC/MAC', diff: 'PATCH /Managers/1/NetworkProtocol', reason: 'Config writes, no reboot', risk: 'low' },
        { label: 'PROPOSED-27→28 · hostname + secure-boot precheck', diff: 'GET /Systems/1/SecureBoot', reason: 'Read-only precheck', risk: 'low' },
      ],
    };
  }
  if (t.includes('playbook change')) {
    return {
      heading: '7 Ansible role changes across 15 role files',
      artifact: 'playbook-change-spec-HPE-EL140-Gen12.md · branch el140-ilo7-support',
      items: [
        { label: 'group_vars/HPE', diff: '+ bios_attribute_value_workload_profile_vRAN: vRAN', reason: 'iLO 7 rejects other WorkloadProfile values', risk: 'low' },
        { label: 'roles/bmc-account/tasks', diff: '~ account index 65536 (iLO7) vs 1 (iLO6)', reason: 'iLO 7 reserves admin account index', risk: 'medium' },
        { label: 'roles/network-config/dns', diff: '~ cap DNS to 3 entries (was 6)', reason: 'iLO7 returns HTTP 400 on 6-entry DNS', risk: 'medium' },
        { label: 'roles/security-hardening (NEW)', diff: '+ new role · KEK/DB cert install + SecureBoot', reason: 'No hardening role existed for iLO7', risk: 'high' },
        { label: '+3 more roles', diff: 'syslog port, Redfish event subscription, hostname', reason: 'iLO7 path/schema deltas', risk: 'low' },
      ],
    };
  }
  if (t.includes('bios') || t.includes('secure-boot')) {
    return {
      heading: 'BIOS + Secure Boot config on the live EL140 (cold-boot required)',
      artifact: 'PROPOSED-30 · 9-step · ~8–10 min POST',
      items: [
        { label: 'BIOS WorkloadProfile', diff: 'PATCH /Systems/1/Bios → vRAN', reason: 'Required far-edge RAN profile', risk: 'medium' },
        { label: 'Secure Boot certificates', diff: 'POST KEK + DB certs · enable SecureBoot', reason: 'Cert count baseline+1', risk: 'high' },
        { label: 'Cold reboot + re-cert', diff: 'ForceRestart → poll FinishedPost', reason: '~8–10 min POST window', risk: 'high' },
      ],
    };
  }
  return null;
}
const riskTone = (r: string) => r === 'high' ? '#dc2626' : r === 'medium' ? '#d97706' : '#16a34a';

export function VerizonOrchestration() {
  const [campaignId, setCampaignId] = useState<string>('el140');

  const q = useQuery<OrchState>({
    queryKey: ['vz-orchestration-state', campaignId],
    queryFn: async () => {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 3000);
      try {
        const r = await fetch(`${API_BASE_URL}/signals/vz/orchestration/state?campaign=${campaignId}`, { signal: ctl.signal });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      } finally { clearTimeout(t); }
    },
    retry: 0, staleTime: 60_000, placeholderData: campaignId === 'el140' ? FALLBACK : undefined,
  });
  const data: OrchState = q.data ?? FALLBACK;
  const timeline = data.timeline;
  const campaigns: CampaignRef[] = data.campaigns ?? [{ id: 'el140', label: data.campaign, platform: data.platform }];

  const [phase, setPhase] = useState<'idle' | 'running' | 'awaiting' | 'done'>('idle');
  const [status, setStatus] = useState<Record<number, StepStatus>>({});
  const [iterShown, setIterShown] = useState<Record<number, number>>({});
  const [gateSeq, setGateSeq] = useState<number | null>(null);
  const timers = useRef<number[]>([]);

  const clearTimers = () => { timers.current.forEach((t) => clearTimeout(t)); timers.current = []; };
  useEffect(() => () => clearTimers(), []);

  const reset = () => {
    clearTimers();
    setPhase('idle'); setStatus({}); setIterShown({}); setGateSeq(null);
  };

  // Switching campaigns resets the run.
  useEffect(() => {
    clearTimers();
    setPhase('idle'); setStatus({}); setIterShown({}); setGateSeq(null);
  }, [campaignId]);

  const SCALE = 0.42;     // compress wall-clock for the demo
  const ITER_MS = 520;

  const runFrom = (idx: number) => {
    if (idx >= timeline.length) { setPhase('done'); return; }
    const step = timeline[idx];

    if (step.kind === 'gate') {
      setStatus((s) => ({ ...s, [step.seq]: 'running' }));
      setGateSeq(step.seq);
      setPhase('awaiting');
      return; // wait for approve
    }

    setStatus((s) => ({ ...s, [step.seq]: 'running' }));

    if (step.iterations && step.iterations.length) {
      setIterShown((m) => ({ ...m, [step.seq]: 0 }));
      step.iterations.forEach((_, i) => {
        const t = window.setTimeout(() => setIterShown((m) => ({ ...m, [step.seq]: i + 1 })), ITER_MS * (i + 1));
        timers.current.push(t);
      });
      const done = window.setTimeout(() => {
        setStatus((s) => ({ ...s, [step.seq]: 'done' }));
        runFrom(idx + 1);
      }, ITER_MS * (step.iterations.length + 1));
      timers.current.push(done);
    } else {
      const t = window.setTimeout(() => {
        setStatus((s) => ({ ...s, [step.seq]: 'done' }));
        runFrom(idx + 1);
      }, Math.max(700, step.duration_ms * SCALE));
      timers.current.push(t);
    }
  };

  const start = () => { reset(); setPhase('running'); const t = window.setTimeout(() => runFrom(0), 250); timers.current.push(t); };

  const approveGate = () => {
    if (gateSeq == null) return;
    const idx = timeline.findIndex((s) => s.seq === gateSeq);
    setStatus((s) => ({ ...s, [gateSeq]: 'done' }));
    setGateSeq(null); setPhase('running');
    const t = window.setTimeout(() => runFrom(idx + 1), 200);
    timers.current.push(t);
  };

  const doneCount = useMemo(() => Object.values(status).filter((s) => s === 'done').length, [status]);
  const progressPct = Math.round((doneCount / timeline.length) * 100);

  const tierOf = (k: Step['kind']) =>
    k === 'gate' ? { label: 'HITL Gate', color: '#d97706', bg: '#fffbeb', bd: '#fde68a' }
    : k === 'action' ? { label: data.tiers.action.label, color: data.tiers.action.color, bg: '#fef2f2', bd: '#fecaca' }
    : { label: data.tiers.correlate.label, color: data.tiers.correlate.color, bg: '#eff6ff', bd: '#bfdbfe' };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#1e293b', background: '#f0f4f8', minHeight: '100vh', padding: '28px 32px', maxWidth: 1600, margin: '0 auto' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20, flexWrap: 'wrap', gap: 14 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase', color: '#ee0000' }}>
            Mission Control · One operator runs the whole campaign
          </div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 22, fontWeight: 800, color: '#0f172a', marginTop: 4, letterSpacing: '-.02em' }}>
            {data.campaign}
          </div>
          <div style={{ fontSize: 12.5, color: '#64748b', marginTop: 4 }}>{data.platform}</div>
          <div style={{ fontSize: 12, color: '#475569', marginTop: 6, maxWidth: 760, lineHeight: 1.45 }}>
            The manager you asked for — Apex drives the agents through every step and only stops for the
            decisions that matter. <strong style={{ color: '#0f172a' }}>You don&apos;t babysit sessions; you approve actions.</strong>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Campaign picker */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span style={{ fontSize: 9.5, fontWeight: 700, color: '#94a3b8', letterSpacing: '.1em', textTransform: 'uppercase' }}>Campaign</span>
            <select
              value={campaignId}
              onChange={(e) => setCampaignId(e.target.value)}
              disabled={phase === 'running' || phase === 'awaiting'}
              style={{
                fontSize: 13, fontWeight: 600, padding: '8px 12px', borderRadius: 9,
                background: '#fff', color: '#0f172a', border: '1px solid #ee0000',
                cursor: (phase === 'running' || phase === 'awaiting') ? 'not-allowed' : 'pointer',
                minWidth: 280, opacity: (phase === 'running' || phase === 'awaiting') ? 0.5 : 1,
              }}
            >
              {campaigns.map((c) => (
                <option key={c.id} value={c.id} style={{ background: '#fff' }}>{c.label}</option>
              ))}
            </select>
          </div>
          {phase === 'idle' || phase === 'done' ? (
            <button onClick={start} style={{ ...btn('#ee0000', '#fff'), alignSelf: 'flex-end' }}>
              {phase === 'done' ? '↻ Run Again' : '▶ Run Campaign'}
            </button>
          ) : (
            <button onClick={reset} style={{ ...btn('#fff', '#475569', '#cbd5e1'), alignSelf: 'flex-end' }}>■ Reset</button>
          )}
        </div>
      </div>

      {/* THE differentiation — two-tier legend (Bob's key area) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 16 }}>
        <TierCard color={data.tiers.correlate.color} icon="◇"
          label={data.tiers.correlate.label} sub={data.tiers.correlate.sublabel}
          count={`${data.summary.correlate_steps} steps`} />
        <TierCard color={data.tiers.action.color} icon="⚡"
          label={data.tiers.action.label} sub={data.tiers.action.sublabel}
          count={`${data.summary.action_steps} steps · ${data.summary.hitl_gates} HITL gates`} />
      </div>

      {/* Summary strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 18 }}>
        <Stat label="Steps" value={`${doneCount}/${data.summary.total_steps}`} tone="#0f172a" />
        <Stat label="Iterations" value={String(data.summary.total_iterations)} tone="#0891b2" />
        <Stat label="HITL Gates" value={String(data.summary.hitl_gates)} tone="#d97706" />
        <Stat label="Lab Actions" value={String(data.summary.action_steps)} tone="#dc2626" />
        <Stat label="Manual → Auto" value={`${data.summary.manual_baseline_hrs}h → ${data.summary.orchestrated_min}m`} tone="#6c47ff" />
      </div>

      {/* progress bar */}
      <div style={{ height: 6, background: '#e2e8f0', borderRadius: 3, overflow: 'hidden', marginBottom: 20 }}>
        <div style={{ width: `${progressPct}%`, height: '100%', background: 'linear-gradient(90deg,#ee0000,#ff6b6b)', transition: 'width .4s' }} />
      </div>

      {/* Timeline */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {timeline.map((step) => {
          const st = status[step.seq] || 'pending';
          const tier = tierOf(step.kind);
          const agent = data.agents[step.agent];
          const active = st === 'running';
          const done = st === 'done';
          const isPendingGate = step.kind === 'gate' && gateSeq === step.seq;
          return (
            <div key={step.seq} style={{
              display: 'flex', gap: 14, padding: '14px 16px', borderRadius: 14,
              background: '#fff',
              border: `1px solid ${active || isPendingGate ? tier.color : '#e8edf2'}`,
              boxShadow: active || isPendingGate ? `0 4px 16px ${tier.color}22` : '0 1px 2px rgba(15,23,42,.04)',
              opacity: (phase !== 'idle' && st === 'pending') ? 0.7 : 1, transition: 'all .3s',
            }}>
              {/* tier rail + seq */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, minWidth: 40 }}>
                <div style={{
                  width: 30, height: 30, borderRadius: 8, background: tier.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 13, fontWeight: 800, color: '#fff',
                  boxShadow: active ? `0 0 0 4px ${tier.color}33` : 'none',
                }}>
                  {done ? '✓' : step.seq}
                </div>
                <span style={{ fontSize: 9, fontWeight: 700, color: agent?.color }}>{agent?.code}</span>
              </div>

              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                  <span style={{
                    fontSize: 9, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase',
                    padding: '2px 8px', borderRadius: 4, color: tier.color,
                    background: `${tier.color}1a`, border: `1px solid ${tier.color}44`,
                  }}>
                    {step.kind === 'gate' ? '⏸ ' : step.kind === 'action' ? '⚡ ' : '◇ '}{tier.label}
                  </span>
                  <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{step.title}</span>
                  {active && step.kind !== 'gate' && <Spinner color={tier.color} />}
                </div>
                <div style={{ fontSize: 13, color: '#334155', lineHeight: 1.55 }}>{step.detail}</div>

                {step.lab_target && (
                  <div style={{ fontSize: 11.5, color: '#dc2626', marginTop: 5, fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>
                    ▸ live target: {step.lab_target}
                  </div>
                )}
                <div style={{ fontSize: 11.5, color: '#64748b', marginTop: 5, fontFamily: "'JetBrains Mono', monospace" }}>
                  {step.evidence}
                </div>

                {/* multi-iteration runs */}
                {step.iterations && (
                  <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
                    {step.iterations.map((it, i) => {
                      const shown = (iterShown[step.seq] || 0) > i || done;
                      return (
                        <div key={it.n} style={{
                          opacity: shown ? 1 : 0.35, transition: 'opacity .3s',
                          background: shown ? `${resultColor(it.result)}0d` : '#f8fafc',
                          border: `1px solid ${shown ? resultColor(it.result) + '66' : '#e8edf2'}`,
                          borderRadius: 7, padding: '6px 9px', minWidth: 120,
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: 10, fontWeight: 700, color: '#475569', fontFamily: "'JetBrains Mono', monospace" }}>{it.label}</span>
                            <span style={{ fontSize: 9, fontWeight: 700, color: resultColor(it.result), textTransform: 'uppercase' }}>
                              {shown ? it.result : '…'}
                            </span>
                          </div>
                          <div style={{ fontSize: 9.5, color: '#64748b', marginTop: 3 }}>{shown ? it.metric : ''}</div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* HITL gate approve */}
                {isPendingGate && (() => {
                  const review = gateReview(step.title);
                  return (
                  <div style={{ marginTop: 12, padding: 12, borderRadius: 10, background: '#fffbeb', border: '1px solid #fde68a' }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#b45309', marginBottom: 10 }}>
                      ⏸ Awaiting human approval — no lab action runs until you approve.
                    </div>

                    {/* What you're approving — the actual change set (Brent's ask) */}
                    {review && (
                      <div style={{ background: '#fff', border: '1px solid #fde68a', borderRadius: 9, padding: '11px 13px', marginBottom: 12 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                          <span style={{ fontSize: 12, fontWeight: 800, color: '#0f172a' }}>🔍 Review — {review.heading}</span>
                          <span style={{ fontSize: 10, color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>{review.artifact}</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
                          {review.items.map((it, k) => (
                            <div key={k} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', paddingBottom: 7, borderBottom: k < review.items.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                              <span style={{ flexShrink: 0, marginTop: 1, fontSize: 8.5, fontWeight: 800, letterSpacing: '.04em', color: riskTone(it.risk), background: `${riskTone(it.risk)}14`, border: `1px solid ${riskTone(it.risk)}40`, borderRadius: 5, padding: '2px 6px', width: 52, textAlign: 'center' }}>{it.risk.toUpperCase()}</span>
                              <div style={{ minWidth: 0, flex: 1 }}>
                                <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a' }}>{it.label}</div>
                                {it.diff && <div style={{ fontSize: 10.5, color: '#0891b2', fontFamily: "'JetBrains Mono', monospace", marginTop: 1 }}>{it.diff}</div>}
                                <div style={{ fontSize: 11, color: '#64748b', marginTop: 1 }}>{it.reason}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                      <button onClick={approveGate} style={btn('#16a34a', '#fff')}>✓ Approve {review ? `${review.items.length} change${review.items.length > 1 ? 's' : ''}` : ''} &amp; continue</button>
                      <button onClick={reset} style={btn('#fff', '#dc2626', '#fca5a5')}>Reject</button>
                      <span style={{ fontSize: 11, color: '#94a3b8' }}>Approval is hash-chained to the Audit Lens with your name + timestamp.</span>
                    </div>
                  </div>
                  );
                })()}
              </div>
            </div>
          );
        })}
      </div>

      {phase === 'done' && (
        <div style={{ marginTop: 18, padding: 16, borderRadius: 14, background: '#f0fdf4', border: '1px solid #bbf7d0' }}>
          <div style={{ fontSize: 14, fontWeight: 800, color: '#15803d' }}>✓ Campaign complete — {data.campaign.split('·')[0].trim()} certified</div>
          <div style={{ fontSize: 12.5, color: '#166534', marginTop: 4, lineHeight: 1.5 }}>
            {data.summary.correlate_steps} correlation/reporting steps (read-only) · {data.summary.action_steps} direct lab actions ·
            {' '}{data.summary.hitl_gates} human approvals · {data.summary.total_iterations} test iterations.
            Every direct action was human-approved and hash-chained to the audit log.
            Manual baseline ~{data.summary.manual_baseline_hrs}h → orchestrated ~{data.summary.orchestrated_min}m.
          </div>
        </div>
      )}
    </div>
  );
}

/* ── building blocks ── */
function btn(bg: string, color: string, bd?: string): React.CSSProperties {
  return { fontSize: 13, fontWeight: 700, padding: '9px 18px', borderRadius: 9, cursor: 'pointer',
    border: `1px solid ${bd || bg}`, background: bg, color };
}
function TierCard({ color, icon, label, sub, count }: { color: string; icon: string; label: string; sub: string; count: string }) {
  return (
    <div style={{ background: '#fff', border: `1px solid ${color}44`, borderRadius: 14, padding: 16, borderLeft: `4px solid ${color}`, boxShadow: '0 1px 2px rgba(15,23,42,.04)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ width: 28, height: 28, borderRadius: 8, background: `${color}1a`, color, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, fontWeight: 800 }}>{icon}</span>
        <span style={{ fontSize: 15, fontWeight: 800, color: '#0f172a' }}>{label}</span>
        <span style={{ marginLeft: 'auto', fontSize: 11, fontWeight: 700, color, background: `${color}14`, padding: '3px 9px', borderRadius: 99 }}>{count}</span>
      </div>
      <div style={{ fontSize: 12, color: '#64748b', marginTop: 8, lineHeight: 1.45 }}>{sub}</div>
    </div>
  );
}
function Stat({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div style={{ background: '#fff', border: '1px solid #e8edf2', borderRadius: 14, padding: '12px 14px', boxShadow: '0 1px 2px rgba(15,23,42,.04)' }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.06em' }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color: tone, marginTop: 3, fontFamily: "'Space Grotesk', sans-serif" }}>{value}</div>
    </div>
  );
}
function Spinner({ color }: { color: string }) {
  return (
    <span style={{
      width: 12, height: 12, borderRadius: '50%', border: `2px solid ${color}44`, borderTopColor: color,
      display: 'inline-block', animation: 'vzspin 0.7s linear infinite',
    }}>
      <style>{`@keyframes vzspin{to{transform:rotate(360deg)}}`}</style>
    </span>
  );
}
