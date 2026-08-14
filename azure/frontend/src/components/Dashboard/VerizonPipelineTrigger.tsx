/**
 * Verizon Far Edge — End-to-End Pipeline: S3 drop → Apex → Jira write-back.
 *
 * Closes the loop James + Brent asked for: "drop the file in S3/GCS" (trigger)
 * and "use Apex as an action platform that writes back to our systems" (Jira).
 * A firmware report lands in S3 → an event fires the pipeline → agents run →
 * one HITL approval → Apex WRITES the results back into Jira (test executions,
 * the change-spec issue, linked PR, attachments) — mirroring the real
 * VZWFE / WRCP 25.09.200 GNRD board.
 *
 * Self-contained + deterministic (no real S3/Jira creds; demo-safe).
 */
import React, { useEffect, useRef, useState } from 'react';

type Kind = 'trigger' | 'extract' | 'correlate' | 'action' | 'gate' | 'jira';
interface Stage { kind: Kind; title: string; detail: string; mono?: string; dur: number }

const STAGES: Stage[] = [
  { kind: 'trigger',   title: 'S3 ObjectCreated event', detail: 'Apex trigger fires automatically — no one kicked this off.', mono: 's3://apex-far-edge-incoming/EL140/test-campaign-EL140-Gen12.md', dur: 1100 },
  { kind: 'extract',   title: 'BDA extracts the report', detail: 'Azure AI Document Intelligence parses frontmatter + per-MEAKV results into structured fields.', mono: 'platform=HPE EL140 Gen12 · iLO7 1.20.00 · 32 MEAKV rows', dur: 1600 },
  { kind: 'correlate', title: 'CertificationAgent · detect gaps', detail: 'MEAKV-1750 / 1793 blocked — iLO7 unsupported by the current BMC playbook.', mono: '2 blocked · 13 PROPOSED cases drafted', dur: 1500 },
  { kind: 'action',    title: 'Execute PROPOSED ×5 iterations', detail: 'Live Redfish calls against the lab EL140 for statistical confidence.', mono: '9 cases × 5 runs = 45 executions · 9/9 pass', dur: 2200 },
  { kind: 'correlate', title: 'PlaybookAgent · gap analysis', detail: 'Cross-reference vs the live Ansible playbook → change-spec (a proposal, nothing applied).', mono: '7 CHANGE · 7 NO-CHANGE · 1 VERIFY', dur: 1500 },
  { kind: 'gate',      title: 'HITL · approve write-back', detail: 'Apex is about to create/modify Jira issues + open a PR. Approve to let it write.', mono: 'creates 5 issues · updates 1 cycle · opens 1 PR', dur: 0 },
  { kind: 'jira',      title: 'Write results back to Jira', detail: 'Apex creates the test executions, the change-spec issue, links the PR, and attaches the reports.', mono: 'POST /rest/api/2/issue · /zephyr executions', dur: 1900 },
];

interface JiraRow { id: string; summary: string; type: string; status: string; op: 'created' | 'updated' }
const JIRA_ROWS: JiraRow[] = [
  { id: 'VZWFE-730', summary: 'EL140 iLO7 — PROPOSED-20→32 coverage', type: 'Story', status: 'Done', op: 'created' },
  { id: 'VZWFE-731', summary: 'Deployment 12 — provision EL140 sub-cloud', type: 'Test Exec', status: 'PASS', op: 'created' },
  { id: 'VZWFE-732', summary: 'Secure Boot + WorkloadProfile=vRAN', type: 'Test Exec', status: 'PASS', op: 'created' },
  { id: 'WRCP 25.09.200 GNRD', summary: 'Platform cycle — EL140 results rolled up', type: 'Cycle', status: '9/9 PASS', op: 'updated' },
  { id: 'VZWFE-735', summary: 'Playbook change-spec: 7 Ansible changes (iLO7)', type: 'Task', status: 'In Review', op: 'created' },
];

const KIND: Record<Kind, { color: string; bg: string; glyph: string; tag: string }> = {
  trigger:   { color: '#6c47ff', bg: '#f5f3ff', glyph: '⚡', tag: 'TRIGGER' },
  extract:   { color: '#0891b2', bg: '#ecfeff', glyph: '◇', tag: 'EXTRACT' },
  correlate: { color: '#2563eb', bg: '#eff6ff', glyph: '◇', tag: 'CORRELATE' },
  action:    { color: '#dc2626', bg: '#fef2f2', glyph: '⚡', tag: 'LAB ACTION' },
  gate:      { color: '#d97706', bg: '#fffbeb', glyph: '⏸', tag: 'HITL' },
  jira:      { color: '#16a34a', bg: '#f0fdf4', glyph: '✍', tag: 'WRITE-BACK' },
};
function btn(bg: string, color: string, bd?: string): React.CSSProperties {
  return { display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 13, fontWeight: 700, padding: '9px 18px', borderRadius: 9, cursor: 'pointer', border: `1px solid ${bd || bg}`, background: bg, color };
}

const SOURCES = {
  s3:  { label: 'Azure Blob Storage',            short: 'S3',  event: 'S3 ObjectCreated event',      path: 's3://apex-far-edge-incoming/EL140/test-campaign-EL140-Gen12.md' },
  gcs: { label: 'Google Cloud Storage', short: 'GCS', event: 'GCS object.finalize event',   path: 'gs://apex-far-edge-incoming/EL140/test-campaign-EL140-Gen12.md' },
} as const;
type SourceKey = keyof typeof SOURCES;

export function VerizonPipelineTrigger() {
  const [source, setSource] = useState<SourceKey>('s3');
  const [phase, setPhase] = useState<'idle' | 'running' | 'awaiting' | 'done'>('idle');
  const [shown, setShown] = useState(0);       // stages revealed (done)
  const timers = useRef<number[]>([]);
  const clear = () => { timers.current.forEach((t) => clearTimeout(t)); timers.current = []; };
  useEffect(() => () => clear(), []);

  const reset = () => { clear(); setPhase('idle'); setShown(0); };

  const advance = (idx: number) => {
    if (idx >= STAGES.length) { setPhase('done'); return; }
    const st = STAGES[idx];
    if (st.kind === 'gate') { setPhase('awaiting'); return; }
    const t = window.setTimeout(() => { setShown(idx + 1); advance(idx + 1); }, st.dur);
    timers.current.push(t);
  };
  const drop = () => { clear(); setShown(0); setPhase('running'); const t = window.setTimeout(() => advance(0), 300); timers.current.push(t); };
  const approve = () => {
    const gi = STAGES.findIndex((s) => s.kind === 'gate');
    setShown(gi + 1); setPhase('running');
    const t = window.setTimeout(() => advance(gi + 1), 250); timers.current.push(t);
  };

  const gateIdx = STAGES.findIndex((s) => s.kind === 'gate');
  const atGate = phase === 'awaiting';
  const card: React.CSSProperties = { background: '#fff', border: '1px solid #e8edf2', borderRadius: 16, boxShadow: '0 1px 2px rgba(15,23,42,.04)' };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#1e293b', background: '#f0f4f8', minHeight: '100vh', padding: '24px 32px 36px', maxWidth: 1600, margin: '0 auto' }}>
      {/* header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 14, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.16em', textTransform: 'uppercase', color: '#ee0000' }}>End-to-End Pipeline · {SOURCES[source].short} → Apex → Jira</div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontSize: 23, fontWeight: 800, color: '#0f172a', marginTop: 4, letterSpacing: '-.02em' }}>Drop a file. Apex does the rest — and writes it back to Jira.</div>
          <div style={{ fontSize: 12.5, color: '#475569', marginTop: 5, maxWidth: 880, lineHeight: 1.45 }}>
            A firmware report lands in {SOURCES[source].label} → an event fires the pipeline → agents run and certify → you approve once →
            <strong style={{ color: '#0f172a' }}> Apex writes the results straight into your Jira board.</strong> Not just chat — an action platform.
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
          {/* trigger-source selector — S3 or Google Cloud Storage */}
          <div style={{ display: 'flex', gap: 4, background: '#fff', border: '1px solid #e8edf2', borderRadius: 10, padding: 3 }}>
            {(Object.keys(SOURCES) as SourceKey[]).map((k) => (
              <button key={k} onClick={() => { setSource(k); reset(); }} disabled={phase === 'running' || phase === 'awaiting'}
                style={{
                  fontSize: 12, fontWeight: 700, padding: '6px 12px', borderRadius: 7, cursor: (phase === 'running' || phase === 'awaiting') ? 'not-allowed' : 'pointer',
                  border: 'none', background: source === k ? '#eef2ff' : 'transparent', color: source === k ? '#4338ca' : '#94a3b8',
                }}>{SOURCES[k].label}</button>
            ))}
          </div>
          {phase === 'idle' || phase === 'done'
            ? <button onClick={drop} style={btn('#6c47ff', '#fff')}>{phase === 'done' ? '↻ Drop Again' : `📥 Drop file to ${SOURCES[source].short}`}</button>
            : <button onClick={reset} style={btn('#fff', '#475569', '#cbd5e1')}>■ Reset</button>}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.15fr 1fr', gap: 18, alignItems: 'start' }}>
        {/* ── pipeline column ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {STAGES.map((st, i) => {
            const k = KIND[st.kind];
            const title = st.kind === 'trigger' ? SOURCES[source].event : st.title;
            const mono = st.kind === 'trigger' ? SOURCES[source].path : st.mono;
            const isDone = i < shown;
            const isActive = i === shown && phase === 'running';
            const pendingGate = st.kind === 'gate' && atGate && i === gateIdx;
            const visible = isDone || isActive || pendingGate;
            return (
              <div key={i} style={{
                ...card, padding: '13px 15px',
                border: `1px solid ${pendingGate ? '#fbbf24' : isActive ? k.color : '#e8edf2'}`,
                background: pendingGate ? '#fffdf5' : '#fff',
                opacity: visible ? 1 : 0.4, transition: 'all .3s',
              }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                  <span style={{ flexShrink: 0, width: 30, height: 30, borderRadius: 8, marginTop: 1, background: isDone ? '#16a34a' : k.bg, color: isDone ? '#fff' : k.color, display: 'inline-flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 800 }}>{isDone ? '✓' : k.glyph}</span>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: 9, fontWeight: 800, letterSpacing: '.05em', color: k.color, background: k.bg, border: `1px solid ${k.color}33`, borderRadius: 5, padding: '2px 7px' }}>{k.tag}</span>
                      <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{title}</span>
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 4, lineHeight: 1.45 }}>{st.detail}</div>
                    {mono && <div style={{ fontSize: 10.5, color: st.kind === 'action' ? '#dc2626' : '#0891b2', fontFamily: "'JetBrains Mono', monospace", marginTop: 4, wordBreak: 'break-all' }}>{mono}</div>}

                    {pendingGate && (
                      <div style={{ marginTop: 12 }}>
                        {/* exactly what will be written — shown BEFORE approve */}
                        <div style={{ background: '#fff', border: '1px solid #fde68a', borderRadius: 9, padding: '11px 13px', marginBottom: 12 }}>
                          <div style={{ fontSize: 12, fontWeight: 800, color: '#0f172a', marginBottom: 8 }}>🔍 Review — exactly what Apex will write to Jira</div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
                            {JIRA_ROWS.map((r, k) => (
                              <div key={k} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', paddingBottom: 7, borderBottom: k < JIRA_ROWS.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                                <span style={{ flexShrink: 0, marginTop: 1, fontSize: 8.5, fontWeight: 800, color: r.op === 'created' ? '#16a34a' : '#2563eb', background: r.op === 'created' ? '#f0fdf4' : '#eff6ff', border: `1px solid ${r.op === 'created' ? '#bbf7d0' : '#bfdbfe'}`, borderRadius: 5, padding: '2px 6px', width: 56, textAlign: 'center' }}>{r.op === 'created' ? 'NEW' : 'UPDATE'}</span>
                                <div style={{ minWidth: 0, flex: 1 }}>
                                  <div style={{ display: 'flex', gap: 7, alignItems: 'center', flexWrap: 'wrap' }}>
                                    <span style={{ fontSize: 11.5, fontWeight: 700, color: '#1d4ed8', fontFamily: "'JetBrains Mono', monospace" }}>{r.id}</span>
                                    <span style={{ fontSize: 8.5, color: '#64748b', background: '#f1f5f9', borderRadius: 4, padding: '1px 6px' }}>{r.type}</span>
                                    <span style={{ fontSize: 8.5, fontWeight: 700, color: /PASS|Done/.test(r.status) ? '#16a34a' : '#d97706' }}>{r.status}</span>
                                  </div>
                                  <div style={{ fontSize: 11.5, color: '#334155', marginTop: 1 }}>{r.summary}</div>
                                </div>
                              </div>
                            ))}
                          </div>
                          <div style={{ fontSize: 10.5, color: '#64748b', marginTop: 8, paddingTop: 8, borderTop: '1px solid #f1f5f9' }}>
                            📎 will attach <strong style={{ color: '#0f172a' }}>test-campaign-summary-EL140.md</strong> + <strong style={{ color: '#0f172a' }}>playbook-change-spec.md</strong> · 🔗 will link PR <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>el140-ilo7-support</span>
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                          <button onClick={approve} style={btn('#16a34a', '#fff')}>✓ Approve — write 5 issues to Jira</button>
                          <button onClick={reset} style={btn('#fff', '#dc2626', '#fca5a5')}>Reject</button>
                          <span style={{ fontSize: 11, color: '#94a3b8' }}>Nothing is written until you approve · hash-chained to Audit Lens.</span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Jira board column ── */}
        <div style={{ ...card, padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '14px 16px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 14, fontWeight: 800, color: '#0f172a' }}>Your Jira · ME VCP-FE Engineering</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>Project VZWFE · Apex writes via REST API — your board, not a replacement</div>
            </div>
            <span style={{ fontSize: 10.5, fontWeight: 700, color: phase === 'done' ? '#16a34a' : '#94a3b8', background: phase === 'done' ? '#f0fdf4' : '#f8fafc', border: `1px solid ${phase === 'done' ? '#bbf7d0' : '#e8edf2'}`, borderRadius: 99, padding: '4px 11px' }}>
              {phase === 'done' ? '● 5 issues written' : 'awaiting pipeline'}
            </span>
          </div>
          {phase !== 'done' ? (
            <div style={{ padding: '40px 20px', textAlign: 'center', fontSize: 12.5, color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>
              {phase === 'idle' ? '> drop a file to S3 to start the pipeline' : phase === 'awaiting' ? '> approve the write-back to populate Jira' : '> pipeline running… Apex will write here'}
            </div>
          ) : (
            <div>
              {JIRA_ROWS.map((r, i) => (
                <div key={i} style={{ padding: '11px 16px', borderBottom: i < JIRA_ROWS.length - 1 ? '1px solid #f1f5f9' : 'none', display: 'flex', gap: 12, alignItems: 'flex-start', animation: `vzj .35s ease ${i * 90}ms both` }}>
                  <span style={{ flexShrink: 0, fontSize: 9, fontWeight: 800, color: r.op === 'created' ? '#16a34a' : '#2563eb', background: r.op === 'created' ? '#f0fdf4' : '#eff6ff', border: `1px solid ${r.op === 'created' ? '#bbf7d0' : '#bfdbfe'}`, borderRadius: 5, padding: '2px 6px', width: 56, textAlign: 'center', marginTop: 2 }}>{r.op === 'created' ? 'NEW' : 'UPDATED'}</span>
                  <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ display: 'flex', gap: 7, alignItems: 'center', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: 12, fontWeight: 700, color: '#1d4ed8', fontFamily: "'JetBrains Mono', monospace" }}>{r.id}</span>
                      <span style={{ fontSize: 9, color: '#64748b', background: '#f1f5f9', borderRadius: 4, padding: '1px 6px' }}>{r.type}</span>
                      <span style={{ fontSize: 9, fontWeight: 700, color: /PASS|Done/.test(r.status) ? '#16a34a' : '#d97706' }}>{r.status}</span>
                    </div>
                    <div style={{ fontSize: 12, color: '#334155', marginTop: 2 }}>{r.summary}</div>
                  </div>
                </div>
              ))}
              <div style={{ padding: '12px 16px', background: '#f8fafc', fontSize: 11, color: '#64748b', lineHeight: 1.5 }}>
                📎 Attached <strong style={{ color: '#0f172a' }}>test-campaign-summary-EL140.md</strong> + <strong style={{ color: '#0f172a' }}>playbook-change-spec.md</strong> · 🔗 linked PR <span style={{ fontFamily: "'JetBrains Mono', monospace" }}>el140-ilo7-support</span>. Every write hash-chained to the Audit Lens.
              </div>
            </div>
          )}
        </div>
      </div>

      {phase === 'done' && (
        <div style={{ ...card, border: '1px solid #bbf7d0', background: '#f0fdf4', padding: '15px 18px', marginTop: 16 }}>
          <div style={{ fontSize: 14, fontWeight: 800, color: '#15803d' }}>✓ Loop closed — file in, certified, written back to Jira</div>
          <div style={{ fontSize: 12.5, color: '#166534', marginTop: 4, lineHeight: 1.5 }}>
            One file drop triggered the whole chain. Apex extracted it, ran the cert, and wrote 5 issues + 1 cycle update + a linked PR back into your board —
            with a single human approval. <strong>This is the "action platform" — it doesn't just answer, it does the work in your systems.</strong>
          </div>
        </div>
      )}
      <div style={{ fontSize: 11.5, color: '#94a3b8', marginTop: 14 }}>
        Trigger sources are pluggable — S3, Google Cloud Storage, or FTP drop. Write-back targets are pluggable via MCP — Jira today; ServiceNow, monitoring, or inventory next.
      </div>
      <style>{`@keyframes vzj{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:translateY(0)}}`}</style>
    </div>
  );
}
