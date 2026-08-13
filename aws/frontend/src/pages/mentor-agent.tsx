/**
 * MentorAgent — Verizon Far Edge knowledge Q&A.
 *
 * Port of apex-verizon-demo/mentor-agent.html. Renders the chat interface
 * for engineers to ask citation-grounded questions over the Apex Lens KB.
 *
 * Visible from the AppShell sidebar only when demo mode === 'verizon_far_edge'.
 * If a user navigates here in any other demo mode they see a "switch demo mode"
 * prompt rather than the full UI.
 */
import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useDemoMode } from '@/lib/demoMode';

const card: React.CSSProperties = {
  background: '#fff', borderRadius: 18, border: '1px solid #e8edf2',
  boxShadow: '0 1px 4px rgba(0,0,0,.04), 0 4px 16px rgba(0,0,0,.03)',
};
const chip = (bg: string, fg: string, bd: string): React.CSSProperties => ({
  display: 'inline-flex', alignItems: 'center', gap: 5, borderRadius: 99,
  padding: '3px 10px', fontSize: 11, fontWeight: 600,
  background: bg, color: fg, border: `1px solid ${bd}`,
});

interface KbDoc { id: string; title: string; meta: string; content: string }

const KB_DOCS: Record<string, KbDoc> = {
  'rb-1': {
    id: 'rb-1', title: 'Upgrade Procedure · Type-B', meta: 'Runbook §4.2 · Last updated: Jan 15, 2026',
    content: `<strong>§4.2 Upgrade Procedure — CaaS-Node-Type-B</strong><br/><br/>
<strong>Pre-conditions:</strong><br/>
• Minimum disk space: 8GB free on /var<br/>
• Ansible version: 2.14.0 or higher<br/>
• Redfish baseline snapshot: required<br/>
• HITL approval: required if failure rate &gt; 15%<br/><br/>
<strong>Supported paths:</strong><br/>
• 22.12 → 23.06 (direct, 2.1% fail rate)<br/>
• 23.06 → 23.12 (direct, 1.8% fail rate)<br/>
• 23.12 → 24.06 (direct, 3.2% fail rate)<br/>
• 23.06 → 24.01 (BLOCKED — skip-level)<br/><br/>
<strong>⚠ Warning:</strong> Direct upgrade from 23.06 to 24.01 is a skip-level upgrade and is not supported. Historical failure rate: 78%.`,
  },
  'rb-2': { id: 'rb-2', title: 'Pre-Check Checklist', meta: 'Runbook §2.1 · Last updated: Feb 3, 2026',
    content: `<strong>§2.1 Pre-Check Checklist — All Device Types</strong><br/><br/>
1. Verify disk space ≥ 8GB on /var<br/>
2. Confirm Ansible ≥ 2.14.0<br/>
3. Take Redfish baseline snapshot<br/>
4. Verify network connectivity to all target nodes<br/>
5. Confirm backup of current configuration<br/>
6. Check compatibility matrix for target firmware<br/>
7. Review historical failure rate for upgrade path` },
  'rb-3': { id: 'rb-3', title: 'Rollback Procedure', meta: 'Runbook §6.3 · Last updated: Jan 28, 2026',
    content: `<strong>§6.3 Emergency Rollback Procedure</strong><br/><br/>
Trigger conditions: Upgrade failure rate &gt; 20% in first batch, or critical service unavailability.<br/><br/>
1. Halt the upgrade wave immediately<br/>
2. Notify J. Patchett and certification team lead<br/>
3. Execute rollback playbook: ansible-playbook rollback.yml<br/>
4. Verify Redfish endpoint responds on all rolled-back nodes<br/>
5. Document in Audit Lens with timestamp and approver` },
  'rb-4': { id: 'rb-4', title: 'Thermal Anomaly Response', meta: 'Runbook §8.1 · Last updated: Mar 12, 2026',
    content: `<strong>§8.1 Thermal Anomaly Response</strong><br/><br/>
Threshold: Chassis temperature &gt; 75°C sustained for &gt; 5 minutes.<br/><br/>
Immediate actions:<br/>
1. Flag site in CertificationAgent for manual review<br/>
2. Check ambient temperature at site<br/>
3. Verify cooling system status via Redfish thermal endpoint<br/>
4. If pattern appears across 3+ sites in same region: escalate to regional ops` },
  'ir-1': { id: 'ir-1', title: 'INC-2026-0001 · Type-B Northeast High-Risk Pattern RCA', meta: 'Incident Report · Closed Q1 2026',
    content: `<strong>Root Cause Analysis — Type-B Northeast High-Risk Pattern</strong><br/><br/>
Three contributing factors, all knowable in advance:<br/><br/>
1. Skip-level upgrade (23.06→24.01) attempted on Type-B NE — 78% historical failure rate not surfaced<br/>
2. Redfish schema drift (power.state renamed) not detected before cycle — 14 scripts failed silently<br/>
3. Thermal anomaly pattern from prior wave not correlated — geographic-scale failure predictable<br/><br/>
<strong>Mitigation:</strong> APEX agents (UpgradeAdvisorAgent, SchemaWatchAgent, CertificationAgent) surface all three signals before wave authorization via real-time predictive intelligence.` },
  'ir-2': { id: 'ir-2', title: 'INC-2025-0847 · Type-B Failure', meta: 'Incident Report · Closed: Nov 18, 2025',
    content: `<strong>INC-2025-0847 — CaaS-Node-Type-B Skip-Level Failure</strong><br/><br/>
Date: November 2025. Attempted direct upgrade 23.06→24.01 on 200 Type-B nodes in Midwest region. 156 nodes (78%) failed mid-upgrade. Recovery time: 4 days.<br/><br/>
Root cause: Skip-level upgrade not validated against compatibility matrix. Engineer relied on memory rather than documented procedure.<br/><br/>
This incident data is now indexed in the Apex Lens KB and is surfaced automatically by UpgradeAdvisorAgent for all Type-B 23.06→24.01 requests.` },
  'cm-1': { id: 'cm-1', title: 'Firmware Compatibility Matrix', meta: 'Compatibility Matrix · Q1 2026 · Version 3.2',
    content: `<strong>Firmware Compatibility Matrix — Q1 2026</strong><br/><br/>
CaaS-Node-Type-A:<br/>
• All sequential upgrades: supported<br/>
• Skip-level (2+ versions): not supported<br/><br/>
CaaS-Node-Type-B:<br/>
• 22.12→23.06: supported (2.1% fail)<br/>
• 23.06→23.12: supported (1.8% fail)<br/>
• 23.06→24.01: BLOCKED (skip-level, 78% fail)<br/>
• 23.12→24.06: supported (3.2% fail)<br/><br/>
CaaS-Node-Type-C:<br/>
• All sequential upgrades: supported<br/>
• Skip-level: requires VP approval` },
  'vd-1': { id: 'vd-1', title: 'Wind River FW 3.2.1 Release Notes', meta: 'Vendor Documentation · Released: May 1, 2026',
    content: `<strong>Wind River Titanium Cloud 3.2.1 Release Notes</strong><br/><br/>
Breaking changes:<br/>
• Redfish API: power.state field renamed to power.powerState (§3.4.2)<br/>
• Redfish API: new required field chassis.thermalStatus added (§3.4.5)<br/><br/>
Known issues:<br/>
• Upgrade from 3.1.x to 3.2.1 on Type-B hardware: verify disk space before upgrade<br/><br/>
Ansible playbooks referencing power.state must be updated before using FW 3.2.1.` },
};

// Hardcoded answer set for the suggested-question hot path
const ANSWERS: Record<string, { text: string; citations: string[]; time: string }> = {
  'upgrade path from 23.06 to 24.01 on type-b': {
    text: `The direct upgrade from <strong>23.06 to 24.01</strong> on CaaS-Node-Type-B is <strong style="color:#dc2626;">blocked</strong> — it is a skip-level upgrade with a <strong>78% historical failure rate</strong>.<br/><br/>
The correct path is a <strong>3-step upgrade</strong>:<br/>
1. 23.06 → 23.12 (1.8% fail rate, ~1.5 hrs)<br/>
2. 23.12 → 24.06 (3.2% fail rate, ~1.5 hrs)<br/>
3. 24.06 → 24.01 (2.1% fail rate, ~1.5 hrs)<br/><br/>
Total estimated duration: <strong>4.5 hours</strong>. HITL approval is required before starting.<br/><br/>
<strong style="color:#dc2626;">⚠ Safety-critical procedure — human review required before execution.</strong>`,
    citations: ['Runbook §4.2', 'INC-2025-0847', 'Compat. Matrix Q1-2026'], time: '22s',
  },
  'pre-checks are required before a type-b upgrade': {
    text: `Before any CaaS-Node-Type-B upgrade, the following <strong>7 pre-checks</strong> are required:<br/><br/>
1. <strong>Disk space:</strong> ≥ 8GB free on /var<br/>
2. <strong>Ansible version:</strong> ≥ 2.14.0<br/>
3. <strong>Redfish baseline snapshot:</strong> must be taken before upgrade<br/>
4. <strong>Network connectivity:</strong> verify all target nodes reachable<br/>
5. <strong>Configuration backup:</strong> confirm backup completed<br/>
6. <strong>Compatibility matrix check:</strong> verify path is supported<br/>
7. <strong>Historical failure rate review:</strong> if &gt; 15%, HITL approval required<br/><br/>
Skipping pre-check #3 (Redfish baseline) was a contributing factor in INC-2025-0847.`,
    citations: ['Runbook §2.1', 'INC-2025-0847'], time: '18s',
  },
  'high-risk type-b northeast pattern': {
    text: `The Type-B Northeast high-risk pattern has <strong>three root causes</strong>, all knowable in advance:<br/><br/>
<strong>1. Skip-level upgrade (UpgradeAdvisorAgent)</strong><br/>
A direct 23.06→24.01 upgrade on Type-B nodes in the Northeast carries a 78% historical failure rate. The signal is in the database and surfaced before wave authorization.<br/><br/>
<strong>2. Redfish schema drift (SchemaWatchAgent)</strong><br/>
Wind River firmware updates that rename power.state to power.powerState cause silent failures in 14 Ansible scripts unless detected pre-wave.<br/><br/>
<strong>3. Thermal anomaly correlation (CertificationAgent)</strong><br/>
A failure pattern across NE sites in one wave predicts geographic-scale failure in the next.<br/><br/>
APEX agents surface all three signals before wave authorization via real-time predictive intelligence.`,
    citations: ['INC-2026-0001', 'Runbook §4.2', 'Wind River 3.2.1 Notes'], time: '27s',
  },
  'rollback procedure for a failed type-a upgrade': {
    text: `The emergency rollback procedure for a failed Type-A upgrade:<br/><br/>
<strong>Trigger conditions:</strong> Upgrade failure rate &gt; 20% in first batch, OR critical service unavailability.<br/><br/>
<strong>Steps:</strong><br/>
1. Halt the upgrade wave immediately<br/>
2. Notify James Patchett and the certification team lead<br/>
3. Execute rollback playbook: <code style="background:#f1f5f9;padding:2px 5px;border-radius:4px;font-family:'JetBrains Mono',monospace;">ansible-playbook rollback.yml --limit failed_nodes</code><br/>
4. Verify Redfish endpoint responds correctly on all rolled-back nodes<br/>
5. Document the incident in the Audit Lens with timestamp, approver name, and override notes<br/><br/>
<strong style="color:#dc2626;">⚠ Safety-critical procedure — human review required before execution.</strong>`,
    citations: ['Runbook §6.3'], time: '19s',
  },
};

function getAnswer(q: string) {
  const lower = q.toLowerCase();
  for (const key of Object.keys(ANSWERS)) {
    if (lower.includes(key)) return ANSWERS[key];
  }
  return {
    text: `I searched the Apex Lens knowledge base for "<strong>${q}</strong>" but did not find a high-confidence match in the indexed documents. I only provide citation-grounded answers — I will not speculate beyond what is in the knowledge base.<br/><br/>Please rephrase, or browse the knowledge base on the left.`,
    citations: [] as string[],
    time: '12s',
  };
}

interface ChatMessage { role: 'user' | 'agent'; html: string; citations?: string[]; time?: string }

const KB_GROUPS: Array<{ label: string; items: Array<{ id: string; title: string; meta: string }> }> = [
  { label: 'Runbooks (12)', items: [
    { id: 'rb-1', title: 'Upgrade Procedure · Type-B',    meta: 'Runbook §4.2 · 23.06→24.01' },
    { id: 'rb-2', title: 'Pre-Check Checklist',            meta: 'Runbook §2.1 · All device types' },
    { id: 'rb-3', title: 'Rollback Procedure',             meta: 'Runbook §6.3 · Emergency' },
    { id: 'rb-4', title: 'Thermal Anomaly Response',       meta: 'Runbook §8.1 · Escalation path' },
  ]},
  { label: 'Incident Reports (8)', items: [
    { id: 'ir-1', title: 'INC-2026-0001 · Jan Outage',     meta: 'Root cause · Lessons learned' },
    { id: 'ir-2', title: 'INC-2025-0847 · Type-B Fail',    meta: '23.06→24.01 skip-level' },
  ]},
  { label: 'Compatibility Matrix (3)', items: [
    { id: 'cm-1', title: 'Firmware Compatibility Matrix',  meta: 'All device types · Q1 2026' },
  ]},
  { label: 'Vendor Docs (6)', items: [
    { id: 'vd-1', title: 'Wind River FW 3.2.1 Release Notes', meta: 'Schema changes · Known issues' },
  ]},
];

const SUGGESTED = [
  { text: 'What is the upgrade path from 23.06 to 24.01 on Type-B?', bg: '#f0fdf4', fg: '#16a34a', bd: '#bbf7d0' },
  { text: 'What pre-checks are required before a Type-B upgrade?',    bg: '#eff6ff', fg: '#2563eb', bd: '#bfdbfe' },
  { text: 'What is the high-risk Type-B Northeast pattern?',         bg: '#faf5ff', fg: '#7c3aed', bd: '#ddd6fe' },
  { text: 'What is the rollback procedure for a failed Type-A upgrade?', bg: '#fffbeb', fg: '#d97706', bd: '#fde68a' },
];

export default function MentorAgentPage() {
  const [demoMode] = useDemoMode();
  const [input, setInput] = useState('');
  const [activeKb, setActiveKb] = useState('rb-1');
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'agent', html: 'Hello, R. Chen. I have access to the complete Far Edge certification knowledge base — runbooks, incident reports, compatibility matrices, and vendor documentation. Every answer I give includes the exact source passage so you can verify it in 30 seconds. What would you like to know?' },
  ]);
  const [thinking, setThinking] = useState(false);

  // Gate: only available in Verizon Far Edge demo mode.
  if (demoMode !== 'verizon_far_edge') {
    return (
      <>
        <Head><title>MentorAgent | APEX</title></Head>
        <div style={{ padding: '60px 40px', textAlign: 'center', maxWidth: 600, margin: '0 auto' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📚</div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: '#0f172a', marginBottom: 10 }}>MentorAgent</h1>
          <p style={{ fontSize: 14, color: '#64748b', lineHeight: 1.6, marginBottom: 20 }}>
            MentorAgent is the Verizon Far Edge knowledge Q&A agent. It's available only when the demo mode is set to <strong>Verizon Far Edge Operations</strong>.
          </p>
          <Link href="/settings" style={{ display: 'inline-block', padding: '10px 20px', background: '#2563eb', color: '#fff', borderRadius: 8, textDecoration: 'none', fontWeight: 600, fontSize: 13 }}>
            → Switch demo mode in Settings
          </Link>
        </div>
      </>
    );
  }

  function sendMessage(q?: string) {
    const text = (q || input).trim();
    if (!text) return;
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', html: text }]);
    setThinking(true);
    setTimeout(() => {
      const ans = getAnswer(text);
      setMessages((prev) => [...prev, { role: 'agent', html: ans.text, citations: ans.citations, time: ans.time }]);
      setThinking(false);
    }, 1200 + Math.random() * 600);
  }

  function clearChat() {
    setMessages([{ role: 'agent', html: 'Chat cleared. Ask me anything about Far Edge certification procedures.' }]);
  }

  const activeDoc = KB_DOCS[activeKb] || KB_DOCS['rb-1'];

  return (
    <>
      <Head><title>MentorAgent · Verizon Far Edge | APEX</title></Head>
      <div style={{ background: '#f0f4f8', minHeight: '100vh' }}>

        {/* Top bar */}
        <div style={{ background: '#fff', borderBottom: '1px solid #e8edf2', height: 64, display: 'flex',
          alignItems: 'center', justifyContent: 'space-between', padding: '0 32px', position: 'sticky', top: 0, zIndex: 30 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: 'linear-gradient(135deg,#10b981,#059669)',
              display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontSize: 18, color: '#fff' }}>📚</span>
            </div>
            <div>
              <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 20, fontWeight: 800, color: '#0f172a', letterSpacing: '-.02em' }}>
                MentorAgent
              </div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 1 }}>
                Knowledge preservation · Apex Lens KB · Citation-grounded
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#22c55e', display: 'inline-block', animation: 'pulse 2s infinite' }} />
              Active
            </span>
            <span style={chip('#f0fdf4', '#16a34a', '#bbf7d0')}>1,847 Queries Answered</span>
            <span style={chip('#eff6ff', '#2563eb', '#bfdbfe')}>100% Citation Rate</span>
          </div>
        </div>

        <div style={{ padding: '24px 32px', maxWidth: 1600 }}>

          {/* KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 14, marginBottom: 24 }}>
            <KpiCard label="Answer Time"      value="<30s"  sub="vs. minutes–hours manual" pill="~99% faster" pillBg="#f0fdf4" pillFg="#16a34a" pillBd="#bbf7d0" valueColor="#10b981" />
            <KpiCard label="Citation Rate"    value="100%"  sub="Every answer has a source" pill="Zero hallucination" pillBg="#eff6ff" pillFg="#2563eb" pillBd="#bfdbfe" valueColor="#2563eb" />
            <KpiCard label="KB Queries"       value="1,847" sub="This wave · All engineers" pill="Consistent answers" pillBg="#faf5ff" pillFg="#7c3aed" pillBd="#ddd6fe" valueColor="#0f172a" />
            <KpiCard label="Onboarding Time"  value="Weeks" sub="vs. months apprenticeship" pill="Significant reduction" pillBg="#fffbeb" pillFg="#d97706" pillBd="#fde68a" valueColor="#d97706" />
            <KpiCard label="Knowledge Retained" value="100%" sub="When engineers leave" pill="Permanent" pillBg="#f0fdf4" pillFg="#16a34a" pillBd="#bbf7d0" valueColor="#16a34a" />
          </div>

          {/* 3-column layout */}
          <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 300px', gap: 20 }}>

            {/* KB Browser */}
            <div>
              <div style={{ ...card, padding: 18 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 14 }}>Knowledge Base</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {KB_GROUPS.map((g) => (
                    <div key={g.label}>
                      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8', padding: '10px 4px 4px' }}>
                        {g.label}
                      </div>
                      {g.items.map((it) => {
                        const active = activeKb === it.id;
                        return (
                          <button key={it.id} onClick={() => setActiveKb(it.id)}
                            style={{
                              textAlign: 'left',
                              padding: '12px 14px', borderRadius: 10, cursor: 'pointer',
                              background: active ? '#f0fdf4' : '#fff',
                              border: `1px solid ${active ? '#10b981' : '#f1f5f9'}`,
                              marginBottom: 6, width: '100%',
                              fontFamily: 'inherit',
                            }}>
                            <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{it.title}</div>
                            <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>{it.meta}</div>
                          </button>
                        );
                      })}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Chat */}
            <div style={{ ...card, display: 'flex', flexDirection: 'column', height: 'calc(100vh - 220px)', minHeight: 600 }}>
              {/* Chat header */}
              <div style={{ padding: '18px 22px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,#10b981,#059669)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontSize: 16, color: '#fff' }}>📚</span>
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>MentorAgent</div>
                    <div style={{ fontSize: 11, color: '#64748b' }}>Citation-grounded · Apex Lens KB · Zero hallucination</div>
                  </div>
                </div>
                <button onClick={clearChat} style={{ padding: '6px 14px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 11, fontWeight: 600, color: '#64748b', cursor: 'pointer' }}>
                  Clear Chat
                </button>
              </div>

              {/* Suggested */}
              <div style={{ padding: '14px 22px', borderBottom: '1px solid #f8fafc', flexShrink: 0 }}>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>
                  Suggested Questions
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {SUGGESTED.map((s) => (
                    <button key={s.text} onClick={() => sendMessage(s.text)}
                      style={{
                        padding: '6px 12px', background: s.bg, border: `1px solid ${s.bd}`, borderRadius: 99,
                        fontSize: 11, fontWeight: 600, color: s.fg, cursor: 'pointer',
                      }}>
                      {s.text}
                    </button>
                  ))}
                </div>
              </div>

              {/* Messages */}
              <div style={{ flex: 1, overflowY: 'auto', padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 14 }}>
                {messages.map((m, i) => (
                  m.role === 'user' ? (
                    <div key={i} style={{
                      background: 'linear-gradient(135deg,#10b981,#059669)', color: '#fff',
                      borderRadius: '16px 16px 4px 16px', padding: '12px 16px', maxWidth: '75%',
                      alignSelf: 'flex-end', fontSize: 13, lineHeight: 1.5,
                    }}>{m.html}</div>
                  ) : (
                    <div key={i} style={{
                      background: '#fff', border: '1px solid #e8edf2', borderRadius: '16px 16px 16px 4px',
                      padding: '14px 16px', maxWidth: '85%', alignSelf: 'flex-start',
                      fontSize: 13, lineHeight: 1.6, boxShadow: '0 1px 4px rgba(0,0,0,.04)',
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                        <div style={{ width: 24, height: 24, borderRadius: 6, background: 'linear-gradient(135deg,#10b981,#059669)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, color: '#fff' }}>
                          📚
                        </div>
                        <span style={{ fontSize: 11, fontWeight: 700, color: '#10b981' }}>MentorAgent</span>
                        {m.time && <span style={{ fontSize: 10, color: '#94a3b8' }}>Answered in {m.time} · {m.citations?.length ?? 0} source{(m.citations?.length ?? 0) !== 1 ? 's' : ''}</span>}
                      </div>
                      <div style={{ color: '#374151', lineHeight: 1.6 }} dangerouslySetInnerHTML={{ __html: m.html }} />
                      {m.citations && m.citations.length > 0 && (
                        <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
                          <span style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', marginRight: 4 }}>SOURCES:</span>
                          {m.citations.map((c) => (
                            <span key={c} style={{
                              display: 'inline-flex', alignItems: 'center', gap: 4,
                              background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 6,
                              padding: '2px 8px', fontSize: 10, fontWeight: 700, color: '#2563eb',
                            }}>{c}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  )
                ))}
                {thinking && (
                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 16, padding: '12px 16px', alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <Dot delay={0} /><Dot delay={160} /><Dot delay={320} />
                    <span style={{ fontSize: 11, color: '#94a3b8', marginLeft: 4 }}>Searching Apex Lens KB...</span>
                  </div>
                )}
              </div>

              {/* Input */}
              <div style={{ padding: '16px 22px', borderTop: '1px solid #f1f5f9', flexShrink: 0 }}>
                <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder="Ask anything about Far Edge certification procedures..."
                    rows={1}
                    style={{
                      flex: 1, padding: '12px 14px', border: '1px solid #e2e8f0', borderRadius: 12,
                      fontSize: 13, color: '#374151', outline: 'none', resize: 'none',
                      fontFamily: 'inherit', lineHeight: 1.5, minHeight: 44, maxHeight: 120, background: '#f8fafc',
                    }}
                  />
                  <button onClick={() => sendMessage()} style={{
                    padding: '12px 20px', background: 'linear-gradient(135deg,#10b981,#059669)',
                    color: '#fff', border: 'none', borderRadius: 12, fontSize: 13, fontWeight: 700,
                    cursor: 'pointer', flexShrink: 0, boxShadow: '0 4px 12px rgba(16,185,129,.3)',
                  }}>
                    Send
                  </button>
                </div>
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 6 }}>
                  Press Enter to send · Shift+Enter for new line · All answers are citation-grounded
                </div>
              </div>
            </div>

            {/* Active KB doc + stats */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div style={{ ...card, padding: 18 }}>
                <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10 }}>Active Document</div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>{activeDoc.title}</div>
                <div style={{ fontSize: 11, color: '#64748b', marginBottom: 12 }}>{activeDoc.meta}</div>
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 10, padding: 12, fontSize: 11, lineHeight: 1.7, color: '#374151', maxHeight: 280, overflowY: 'auto' }}
                  dangerouslySetInnerHTML={{ __html: activeDoc.content }} />
              </div>

              <div style={{ ...card, padding: 18, background: 'linear-gradient(135deg,#f0fdf4,#dcfce7)', borderColor: '#bbf7d0' }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#15803d', marginBottom: 12 }}>The Onboarding Multiplier</div>
                <div style={{ fontSize: 12, color: '#374151', lineHeight: 1.6, marginBottom: 12 }}>
                  R. Chen (new hire, 3 weeks) has asked <strong>47 questions</strong> this wave — each answered in under 30 seconds with citations.
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                  <div style={{ background: '#fff', border: '1px solid #bbf7d0', borderRadius: 8, padding: 10, textAlign: 'center' }}>
                    <div style={{ fontSize: 20, fontWeight: 800, color: '#16a34a' }}>47</div>
                    <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>Questions asked</div>
                  </div>
                  <div style={{ background: '#fff', border: '1px solid #bbf7d0', borderRadius: 8, padding: 10, textAlign: 'center' }}>
                    <div style={{ fontSize: 20, fontWeight: 800, color: '#16a34a' }}>~6h</div>
                    <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>Senior eng time saved</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <style>{`
          @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
          @keyframes thinking { 0%,80%,100%{transform:scale(0)} 40%{transform:scale(1)} }
        `}</style>
      </div>
    </>
  );
}

function KpiCard({ label, value, sub, pill, pillBg, pillFg, pillBd, valueColor }: {
  label: string; value: string; sub: string; pill: string;
  pillBg: string; pillFg: string; pillBd: string; valueColor: string;
}) {
  return (
    <div style={{ ...card, padding: '18px 20px' }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>{label}</div>
      <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 32, fontWeight: 800, color: valueColor, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>{sub}</div>
      <div style={{ marginTop: 8, fontSize: 10, fontWeight: 700, color: pillFg, background: pillBg, border: `1px solid ${pillBd}`, borderRadius: 6, padding: '3px 8px', display: 'inline-block' }}>
        {pill}
      </div>
    </div>
  );
}

function Dot({ delay }: { delay: number }) {
  return (
    <div style={{
      width: 7, height: 7, borderRadius: '50%', background: '#94a3b8',
      animation: `thinking 1.4s ${delay}ms infinite ease-in-out`,
    }} />
  );
}
