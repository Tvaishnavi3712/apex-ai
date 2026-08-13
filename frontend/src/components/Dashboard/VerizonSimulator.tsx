/**
 * Verizon Far Edge — What-If Simulator.
 *
 * Agentic war-gaming for a risky firmware/field decision: inject a "what if",
 * watch the agent reason step-by-step (thought → tool call → observation →
 * recommendation), then approve the mitigation (HITL). Grounded in James
 * Patchett's real lab findings (MEAKV-1792 thermal, skip-level upgrade risk,
 * NEBS gap, Redfish schema drift).
 *
 * Self-contained + deterministic — streams an in-process reasoning trace, so
 * there is no Foundry Agent Service cold-start (same pattern as VerizonOrchestration).
 */
import React, { useEffect, useRef, useState } from 'react';
import Head from 'next/head';

type Tier = 'PREFERRED' | 'FALLBACK' | 'LAST_RESORT';
interface Option { tier: Tier; title: string; metricA: string; metricB: string; capacity: string; notes: string }
interface Step { kind: 'thought' | 'action' | 'observation' | 'answer'; text: string; tool?: string }
interface Stat { label: string; value: string; sub: string; tone: string }
interface Scenario {
  id: string; label: string; tagline: string; severity: 'HIGH' | 'CRITICAL';
  scope: string; headline: string; headlineLabel: string; headlineTone: string;
  stats: Stat[]; director: string; trace: Step[]; options: Option[];
}

const SCENARIOS: Scenario[] = [
  {
    id: 'bmc45-pm9a3-wave',
    label: 'Push BMC .45 to all PM9A3 sites',
    tagline: 'Next wave would ship BMC 0.45 fleet-wide. Samsung PM9A3 drives present.',
    severity: 'CRITICAL', scope: 'Fleet-wide · Samsung PM9A3 · BMC 0.45',
    headline: '1,920', headlineLabel: 'Sites at risk', headlineTone: '#dc2626',
    stats: [
      { label: 'PM9A3 subclouds', value: '1,920', sub: 'MZQL21T9HCJR-00A07', tone: '#dc2626' },
      { label: 'Fan response', value: '100%', sub: 'thermal failsafe', tone: '#d97706' },
      { label: 'Power draw', value: '+14%', sub: 'sustained / site', tone: '#dc2626' },
    ],
    director: 'Firmware Automation Lead',
    trace: [
      { kind: 'thought', text: 'The pending wave pushes BMC 0.45 to every subcloud. First — which sites carry the Samsung PM9A3 drive?' },
      { kind: 'action', tool: 'query_fleet_inventory', text: 'query_fleet_inventory(drive="SAMSUNG PM9A3 / MZQL21T9HCJR-00A07")' },
      { kind: 'observation', text: '1,920 subclouds report ≥1 PM9A3 drive in the active inventory.' },
      { kind: 'thought', text: 'Cross-reference against the regression catalog — is BMC 0.45 known-bad on this drive?' },
      { kind: 'action', tool: 'lookup_regression', text: 'lookup_regression(meakv="MEAKV-1792")' },
      { kind: 'observation', text: 'MEAKV-1792 CONFIRMED in lab: BMC 0.45 cannot read PM9A3 temp → controller defaults fans to 100% → +14% power. Fixed in BMC 0.46.' },
      { kind: 'thought', text: 'Shipping 0.45 to 1,920 PM9A3 sites = fleet-wide thermal failsafe + a sustained power spike. The fix (0.46) already exists.' },
      { kind: 'answer', text: 'BLOCK BMC 0.45 for all PM9A3 sites and mandate 0.46. This is a direct field action — routing to human approval before any wave change.' },
    ],
    options: [
      { tier: 'PREFERRED', title: 'Block .45 → PM9A3, mandate .46', metricA: '0 cost', metricB: '0d delay', capacity: 'SUFFICIENT', notes: 'UpgradeAdvisor blocks .45 for PM9A3 sites; .46 already validated in lab (5/5 runs).' },
      { tier: 'FALLBACK', title: 'Stage .46 first, then resume', metricA: '0 cost', metricB: '2d delay', capacity: 'PARTIAL', notes: 'Push .46 to PM9A3 sites this wave; resume .45 only on non-PM9A3 hardware.' },
      { tier: 'LAST_RESORT', title: 'Proceed with manual thermal watch', metricA: '+14% power', metricB: '0d delay', capacity: 'RISKY', notes: 'Ship .45 anyway with hourly thermal monitoring. Only if .46 staging is blocked.' },
    ],
  },
  {
    id: 'skiplevel-23-24',
    label: 'Skip-level 23.06 → 24.01 on Type-B Northeast',
    tagline: 'Field team wants a direct jump. UpgradeAdvisor flagged it.',
    severity: 'CRITICAL', scope: 'CaaS-Node-Type-B · Northeast',
    headline: '78%', headlineLabel: 'Predicted fail rate', headlineTone: '#dc2626',
    stats: [
      { label: 'Nodes in scope', value: '3,240', sub: 'Type-B · Northeast', tone: '#dc2626' },
      { label: 'Version gap', value: 'Skip', tone: '#d97706', sub: '23.06 → 24.01 direct' },
      { label: 'Risk score', value: 'CRITICAL', sub: 'XGBoost wave-risk', tone: '#dc2626' },
    ],
    director: 'Distinguished Engineer (co-sign)',
    trace: [
      { kind: 'thought', text: 'A direct 23.06 → 24.01 is a skip-level jump. Validate the path against the upgrade matrix.' },
      { kind: 'action', tool: 'validate_upgrade_path', text: 'validate_upgrade_path(from="23.06", to="24.01", node="CaaS-Node-Type-B", region="NE")' },
      { kind: 'observation', text: 'Path is skip-level (24.06 release skipped). Breaking Redfish schema diff present (power.state → power.powerState).' },
      { kind: 'action', tool: 'score_wave_risk', text: 'score_wave_risk(node="Type-B", region="NE", path="23.06→24.01")' },
      { kind: 'observation', text: 'XGBoost wave-risk = CRITICAL · P(outage)=78%. Drivers: skip-level + breaking schema diff + Northeast thermal pattern.' },
      { kind: 'thought', text: 'A 78% predicted fail across 3,240 nodes is unacceptable. A stepped path defuses each driver individually.' },
      { kind: 'answer', text: 'BLOCK the direct path. Recommend the 3-step staged upgrade. Skip-level overrides require Distinguished-Engineer co-signature — routing to approval.' },
    ],
    options: [
      { tier: 'PREFERRED', title: '3-step staged path', metricA: '+0 risk', metricB: '+6d', capacity: 'SUFFICIENT', notes: '23.06 → 23.12 → 24.06 → 24.01, 7 pre-checks per hop. P(outage) drops to <5%.' },
      { tier: 'FALLBACK', title: 'Pause + canary 50 nodes', metricA: '+0 risk', metricB: '+3d', capacity: 'PARTIAL', notes: 'Canary the direct path on 50 nodes; promote only if fail rate < 5%.' },
      { tier: 'LAST_RESORT', title: 'Direct jump (DE co-sign)', metricA: '78% fail', metricB: '0d', capacity: 'BLOCKED', notes: 'Only with Distinguished-Engineer override + on-site rollback team staged.' },
    ],
  },
  {
    id: 'el140-nebs-skip',
    label: 'Certify EL140 without the NEBS threshold',
    tagline: 'Cert passes functionally — but the NEBS inlet caution is unset.',
    severity: 'HIGH', scope: 'HPE EL140 Gen12 · iLO7',
    headline: 'GAP', headlineLabel: 'NEBS compliance', headlineTone: '#d97706',
    stats: [
      { label: 'Functional tests', value: 'PASS', sub: '9/9 PROPOSED suite', tone: '#16a34a' },
      { label: 'NEBS threshold', value: 'UNSET', sub: '62°C inlet caution', tone: '#d97706' },
      { label: 'Field risk', value: 'Silent', sub: 'no thermal alarm', tone: '#dc2626' },
    ],
    director: 'Compliance Engineering',
    trace: [
      { kind: 'thought', text: 'Functional cert is green. But far-edge sites require NEBS GR-63 thermal compliance — check the inlet caution threshold.' },
      { kind: 'action', tool: 'read_bios_thresholds', text: 'read_bios_thresholds(platform="EL140 Gen12", sensor="inlet_ambient")' },
      { kind: 'observation', text: 'Inlet-ambient caution threshold = null. NEBS GR-63 requires a 62°C caution set point on far-edge nodes.' },
      { kind: 'thought', text: 'Certifying without it means a thermal excursion in the field raises NO alarm — a silent compliance + reliability gap.' },
      { kind: 'answer', text: 'Do NOT certify as-is. Set the 62°C inlet caution threshold, then re-run. Routing the threshold write to approval (direct config change).' },
    ],
    options: [
      { tier: 'PREFERRED', title: 'Set 62°C threshold + re-cert', metricA: '+1 step', metricB: '+15m', capacity: 'SUFFICIENT', notes: 'PATCH inlet caution = 62°C, re-run PROPOSED-30. Closes the NEBS gap before sign-off.' },
      { tier: 'FALLBACK', title: 'Conditional cert + tracked gap', metricA: '0', metricB: '0d', capacity: 'PARTIAL', notes: 'Certify with a documented NEBS exception; block far-edge deployment until threshold set.' },
      { tier: 'LAST_RESORT', title: 'Certify as-is', metricA: 'compliance risk', metricB: '0d', capacity: 'BLOCKED', notes: 'Not recommended — ships a silent thermal gap to NEBS-regulated sites.' },
    ],
  },
  {
    id: 'schema-drift-deploy',
    label: 'Deploy with the Redfish schema drift unpatched',
    tagline: 'power.state → power.powerState renamed. 6 playbooks still reference the old path.',
    severity: 'HIGH', scope: 'Wind River FW 3.2.1 · 6 Ansible playbooks',
    headline: '6', headlineLabel: 'Playbooks break', headlineTone: '#dc2626',
    stats: [
      { label: 'Scripts impacted', value: '6', sub: 'deprecated power.state', tone: '#dc2626' },
      { label: 'Lead time', value: '6d', sub: 'before next cert cycle', tone: '#16a34a' },
      { label: 'Detection', value: 'Auto', sub: 'SchemaWatchAgent', tone: '#0891b2' },
    ],
    director: 'Automation Team',
    trace: [
      { kind: 'thought', text: 'SchemaWatch flagged a Redfish field rename. Which automation references the deprecated path?' },
      { kind: 'action', tool: 'grep_playbooks', text: 'grep_playbooks(path="chassis.power.state")' },
      { kind: 'observation', text: '6 Ansible playbooks reference power.state (renamed to power.powerState in FW 3.2.1). They will silently read null at cert time.' },
      { kind: 'thought', text: 'Deploying now means 6 cert playbooks fail mid-cycle. We have 6 days lead time before the cycle — patch first.' },
      { kind: 'answer', text: 'BLOCK deploy until the 6 playbooks are patched. Draft the change-spec (read-only); apply is a direct action → routing to approval.' },
    ],
    options: [
      { tier: 'PREFERRED', title: 'Patch 6 playbooks + open PR', metricA: '0 cost', metricB: '+1d', capacity: 'SUFFICIENT', notes: 'Auto-draft the power.powerState change-spec; human approves the PR. 6-day lead time absorbs it.' },
      { tier: 'FALLBACK', title: 'Pin schema version', metricA: '0 cost', metricB: '0d', capacity: 'PARTIAL', notes: 'Pin the validator to the FW 3.1 schema for this cycle; patch playbooks next sprint.' },
      { tier: 'LAST_RESORT', title: 'Deploy + hotfix in cycle', metricA: 'cycle risk', metricB: '0d', capacity: 'RISKY', notes: 'Deploy now and hotfix when playbooks fail — burns cert-cycle time.' },
    ],
  },
];

const TIER_STYLE: Record<Tier, { label: string; color: string; bg: string; bd: string }> = {
  PREFERRED:   { label: 'PREFERRED',   color: '#16a34a', bg: '#f0fdf4', bd: '#bbf7d0' },
  FALLBACK:    { label: 'FALLBACK',    color: '#2563eb', bg: '#eff6ff', bd: '#bfdbfe' },
  LAST_RESORT: { label: 'LAST_RESORT', color: '#dc2626', bg: '#fef2f2', bd: '#fecaca' },
};
const KIND_STYLE: Record<Step['kind'], { label: string; color: string }> = {
  thought:     { label: 'THINKING',    color: '#6c47ff' },
  action:      { label: 'TOOL CALL',   color: '#0891b2' },
  observation: { label: 'OBSERVATION', color: '#d97706' },
  answer:      { label: 'DECISION',    color: '#16a34a' },
};

export function VerizonSimulator() {
  const [selId, setSelId] = useState<string>(SCENARIOS[0].id);
  const sel = SCENARIOS.find((s) => s.id === selId)!;

  const [phase, setPhase] = useState<'idle' | 'running' | 'done'>('idle');
  const [shown, setShown] = useState<number>(0);     // # trace steps revealed
  const [approved, setApproved] = useState<boolean>(false);
  const timers = useRef<number[]>([]);

  const clearTimers = () => { timers.current.forEach((t) => clearTimeout(t)); timers.current = []; };
  useEffect(() => () => clearTimers(), []);
  // switching scenarios resets the run
  useEffect(() => { clearTimers(); setPhase('idle'); setShown(0); setApproved(false); }, [selId]);

  const run = () => {
    clearTimers(); setShown(0); setApproved(false); setPhase('running');
    sel.trace.forEach((_, i) => {
      const t = window.setTimeout(() => {
        setShown(i + 1);
        if (i === sel.trace.length - 1) setPhase('done');
      }, 650 * (i + 1));
      timers.current.push(t);
    });
  };

  const card: React.CSSProperties = { background: '#fff', border: '1px solid #e8edf2', borderRadius: 16, boxShadow: '0 1px 2px rgba(15,23,42,.04)' };
  const sevChip = (sev: string) => sev === 'CRITICAL'
    ? { bg: '#fef2f2', fg: '#dc2626', bd: '#fecaca' }
    : { bg: '#fffbeb', fg: '#d97706', bd: '#fde68a' };

  return (
    <>
      <Head><title>Simulator · Verizon Far Edge | APEX</title></Head>
      <div style={{ fontFamily: 'Inter, sans-serif', color: '#1e293b', background: '#f0f4f8', minHeight: '100vh', padding: '28px 32px', maxWidth: 1600, margin: '0 auto' }}>

        {/* Hero */}
        <div style={{ ...card, padding: '22px 26px', marginBottom: 18, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase', color: '#6c47ff' }}>What-If Simulator</div>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 24, fontWeight: 800, color: '#0f172a', marginTop: 4, letterSpacing: '-.02em' }}>
              Rehearse the risky call. Watch the agent reason.
            </div>
            <div style={{ fontSize: 12.5, color: '#64748b', marginTop: 4 }}>
              Agentic war-gaming for a firmware/field decision — read-only reasoning &amp; correlation, then a human approves any direct action.
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            {phase === 'idle' || phase === 'done'
              ? <button onClick={run} style={btn('#6c47ff', '#fff')}>{phase === 'done' ? '↻ Re-run' : '▶ Run Simulation'}</button>
              : <button onClick={() => { clearTimers(); setPhase('idle'); setShown(0); }} style={btn('#fff', '#475569', '#cbd5e1')}>■ Stop</button>}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 360px', gap: 16, alignItems: 'start' }}>

          {/* ── Inject crisis (scenario list) ── */}
          <div style={{ ...card, padding: 18 }}>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 4 }}>Inject What-If</div>
            <div style={{ fontSize: 11.5, color: '#94a3b8', marginBottom: 14 }}>{SCENARIOS.length} scenarios · grounded in MTCE lab findings</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {SCENARIOS.map((s) => {
                const active = s.id === selId;
                const sc = sevChip(s.severity);
                return (
                  <button key={s.id} onClick={() => setSelId(s.id)} style={{
                    textAlign: 'left', cursor: 'pointer', padding: '13px 14px', borderRadius: 12,
                    background: active ? '#f5f3ff' : '#fff',
                    border: `1px solid ${active ? '#6c47ff' : '#e8edf2'}`,
                    boxShadow: active ? '0 4px 14px rgba(108,71,255,.12)' : 'none', transition: 'all .2s',
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', lineHeight: 1.3 }}>{s.label}</span>
                      <span style={{ flexShrink: 0, fontSize: 9, fontWeight: 800, padding: '2px 7px', borderRadius: 99, background: sc.bg, color: sc.fg, border: `1px solid ${sc.bd}` }}>{s.severity}</span>
                    </div>
                    <div style={{ fontSize: 11.5, color: '#64748b', marginTop: 5, lineHeight: 1.45 }}>{s.tagline}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* ── Live agent reasoning ── */}
          <div style={{ ...card, padding: 22 }}>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#16a34a', marginBottom: 6 }}>Live Agent Reasoning</div>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 19, fontWeight: 800, color: '#0f172a' }}>{sel.label}</div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 3 }}>{sel.scope}</div>

            {/* headline metric */}
            <div style={{ marginTop: 16, paddingBottom: 16, borderBottom: '1px solid #f1f5f9' }}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8' }}>{sel.headlineLabel}</div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 44, fontWeight: 800, color: sel.headlineTone, lineHeight: 1.05 }}>{sel.headline}</div>
            </div>

            {/* sub-stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginTop: 16 }}>
              {sel.stats.map((st) => (
                <div key={st.label} style={{ background: '#f8fafc', border: '1px solid #e8edf2', borderRadius: 10, padding: '11px 13px' }}>
                  <div style={{ fontSize: 18, fontWeight: 800, color: st.tone, fontFamily: "'Space Grotesk', sans-serif" }}>{st.value}</div>
                  <div style={{ fontSize: 11, fontWeight: 600, color: '#334155', marginTop: 3 }}>{st.label}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 1 }}>{st.sub}</div>
                </div>
              ))}
            </div>

            {/* reasoning trace */}
            <div style={{ marginTop: 18, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {phase === 'idle' && (
                <div style={{ padding: '20px 16px', borderRadius: 10, border: '1px dashed #cbd5e1', background: '#f8fafc', fontSize: 12.5, color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>
                  &gt; standing by · click <strong style={{ color: '#6c47ff' }}>▶ Run Simulation</strong> to stream the agent&apos;s reasoning trace.
                </div>
              )}
              {sel.trace.slice(0, shown).map((step, i) => {
                const ks = KIND_STYLE[step.kind];
                return (
                  <div key={i} style={{
                    display: 'flex', gap: 12, padding: '12px 14px', borderRadius: 11,
                    background: step.kind === 'answer' ? '#f0fdf4' : '#fff',
                    border: `1px solid ${step.kind === 'answer' ? '#bbf7d0' : '#e8edf2'}`,
                    animation: 'vzfade .3s ease',
                  }}>
                    <span style={{ flexShrink: 0, fontSize: 9, fontWeight: 800, letterSpacing: '.06em', color: ks.color, background: `${ks.color}14`, border: `1px solid ${ks.color}33`, borderRadius: 6, padding: '3px 7px', height: 'fit-content' }}>{ks.label}</span>
                    <div style={{ minWidth: 0 }}>
                      {step.tool && <div style={{ fontSize: 11.5, fontWeight: 700, color: '#0891b2', fontFamily: "'JetBrains Mono', monospace", marginBottom: 3 }}>{step.text}</div>}
                      {!step.tool && <div style={{ fontSize: 13, color: step.kind === 'answer' ? '#15803d' : '#334155', lineHeight: 1.5, fontWeight: step.kind === 'answer' ? 600 : 400 }}>{step.text}</div>}
                    </div>
                  </div>
                );
              })}
              {phase === 'running' && (
                <div style={{ fontSize: 11.5, color: '#6c47ff', fontFamily: "'JetBrains Mono', monospace", paddingLeft: 4 }}>▌ reasoning…</div>
              )}
            </div>
          </div>

          {/* ── Recommended actions ── */}
          <div style={{ ...card, padding: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#d97706', marginBottom: 4 }}>Recommended Actions</div>
            <div style={{ fontSize: 12, color: '#64748b', marginBottom: 14 }}>3 ranked options · escalates to <strong style={{ color: '#0f172a' }}>{sel.director}</strong></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, opacity: phase === 'done' ? 1 : 0.5, transition: 'opacity .3s' }}>
              {sel.options.map((o) => {
                const ts = TIER_STYLE[o.tier];
                return (
                  <div key={o.tier} style={{ background: ts.bg, border: `1px solid ${ts.bd}`, borderRadius: 12, padding: '13px 15px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: 10, fontWeight: 800, letterSpacing: '.06em', color: ts.color }}>{ts.label}</span>
                      <span style={{ fontSize: 10, fontWeight: 700, color: '#64748b' }}>capacity {o.capacity}</span>
                    </div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginTop: 6 }}>{o.title}</div>
                    <div style={{ display: 'flex', gap: 14, marginTop: 5 }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: ts.color }}>{o.metricA}</span>
                      <span style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>{o.metricB}</span>
                    </div>
                    <div style={{ fontSize: 11.5, color: '#64748b', marginTop: 6, lineHeight: 1.45 }}>{o.notes}</div>
                  </div>
                );
              })}
            </div>
            <div style={{ marginTop: 14 }}>
              {phase !== 'done' ? (
                <div style={{ padding: '12px', borderRadius: 10, background: '#f8fafc', border: '1px dashed #cbd5e1', textAlign: 'center', fontSize: 12, fontWeight: 600, color: '#94a3b8' }}>
                  Run the simulation to enable approval
                </div>
              ) : approved ? (
                <div style={{ padding: '12px', borderRadius: 10, background: '#f0fdf4', border: '1px solid #bbf7d0', textAlign: 'center', fontSize: 12.5, fontWeight: 700, color: '#15803d' }}>
                  ✓ {sel.options[0].title} approved · routed to {sel.director} · logged to Audit Lens
                </div>
              ) : (
                <button onClick={() => setApproved(true)} style={{ ...btn('#16a34a', '#fff'), width: '100%', justifyContent: 'center' }}>
                  ✓ Approve preferred option (HITL)
                </button>
              )}
            </div>
          </div>
        </div>
        <style>{`@keyframes vzfade{from{opacity:0;transform:translateY(-3px)}to{opacity:1;transform:translateY(0)}}`}</style>
      </div>
    </>
  );
}

function btn(bg: string, color: string, bd?: string): React.CSSProperties {
  return { display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 700, padding: '10px 20px', borderRadius: 9, cursor: 'pointer', border: `1px solid ${bd || bg}`, background: bg, color };
}
