/**
 * pb-tel-1 — Full Certification Cycle · LIVE RUN page.
 *
 * The wow-demo surface for Verizon Far Edge:
 *
 *   1. Drop a ROBOT XML into the dropzone (or click "Use sample") ────────────┐
 *   2. POST to /api/v1/telecommunications/cycle-start as multipart            │
 *   3. Browser opens an SSE stream and renders 5-stage live timeline          │
 *      ▸ parse  · classify · drift · jira (N tickets) · report                │
 *   4. As tickets are created, their cards appear one by one                  │
 *   5. Final result panel: clickable JIRA URLs, hours saved, status chip      │
 *
 * Mock vs Live: when `JIRA_URL` is unset in the backend .env, the pipeline
 * runs in mock mode — the UI shows a "MOCK" pill next to each ticket. The
 * moment JIRA creds are saved + the backend is restarted, the same page
 * starts producing live ticket URLs that open Atlassian.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ──────────────────────────── types ────────────────────────────

type StageId = 'parse' | 'classify' | 'drift' | 'jira' | 'report';

interface StageState {
  id:           StageId;
  label:        string;
  status:       'pending' | 'running' | 'done' | 'error';
  ms?:          number;
  summary?:     string;
  expectedCount?: number;
}

interface CreatedTicket {
  i:        number;
  of:       number;
  key:      string | null;
  url:      string | null;
  mock:     boolean;
  summary:  string;
  severity: string | null;
  category: string | null;
}

interface HitlRequired {
  request_id:      string;
  cycle_id:        string;
  agent:           string;
  gate:            string;
  severity:        'high' | 'medium' | 'low';
  reason:          string;
  proposed_action: string;
}

interface HitlDecided {
  request_id:  string;
  decision:    'approve' | 'reject' | 'timeout' | 'missing';
  reviewer:    string;
  comment:     string;
  decided_at:  number;
}

interface CycleReport {
  report_id:                 string;
  cycle_id:                  string;
  device_under_test?:        string;
  firmware_version?:         string;
  total_tests?:              number;
  pass_count?:               number;
  fail_count?:               number;
  warn_count?:               number;
  p1_count?:                 number;
  p2_count?:                 number;
  p3_count?:                 number;
  overall_status?:           string;
  schema_drift_events?:      number;
  scripts_impacted_by_drift?: number;
  jira_tickets_opened?:      string[];
  hours_saved_vs_manual?:    number;
  audit_lens_event_id?:      string;
}

interface SampleFile { name: string; label: string; size_bytes: number; demo_path: string }
interface JiraConfigProbe {
  config: { url: string; email: string; project_key: string; mock_mode: boolean; mock_reason: string; token_present: boolean };
  probe:  {
    ok: boolean;
    mock?: boolean;
    account_id?: string;
    email?: string;
    display?: string;
    error?: string;
    reason?: string;
    http_status?: number;
  };
}

// ──────────────────────────── stage scaffolding ────────────────────────────

const INITIAL_STAGES: StageState[] = [
  { id: 'parse',    label: 'Parse ROBOT XML',          status: 'pending' },
  { id: 'classify', label: 'Classify Failures',         status: 'pending' },
  { id: 'drift',    label: 'Schema Drift Check',        status: 'pending' },
  { id: 'jira',     label: 'Open JIRA Tickets',         status: 'pending' },
  { id: 'report',   label: 'Emit Certification Report', status: 'pending' },
];

// ──────────────────────────── main component ────────────────────────────

export default function RunCertificationCyclePage() {
  const [stages, setStages]            = useState<StageState[]>(INITIAL_STAGES);
  const [tickets, setTickets]          = useState<CreatedTicket[]>([]);
  const [cycleReport, setCycleReport]  = useState<CycleReport | null>(null);
  const [cycleId, setCycleId]          = useState<string | null>(null);
  const [running, setRunning]          = useState(false);
  const [errorMsg, setErrorMsg]        = useState<string | null>(null);
  const [samples, setSamples]          = useState<SampleFile[]>([]);
  const [jiraStatus, setJiraStatus]    = useState<JiraConfigProbe | null>(null);
  const [hitl, setHitl]                = useState<HitlRequired | null>(null);
  const [hitlDecision, setHitlDecision] = useState<HitlDecided | null>(null);
  const [hitlBusy, setHitlBusy]        = useState(false);
  const [halted, setHalted]            = useState<{ reason: string } | null>(null);
  const dropRef                        = useRef<HTMLDivElement | null>(null);
  const fileInputRef                   = useRef<HTMLInputElement | null>(null);

  // Load sample files + JIRA status once.
  useEffect(() => {
    (async () => {
      try {
        const [s, j] = await Promise.all([
          fetch(`${API_BASE_URL}/telecommunications/sample-files`).then(r => r.json()),
          fetch(`${API_BASE_URL}/telecommunications/jira-config`).then(r => r.json()),
        ]);
        setSamples(s.files || []);
        setJiraStatus(j);
      } catch (e) {
        // Backend not reachable yet — that's fine, the user can still see the page.
        console.warn('telecom run page init:', e);
      }
    })();
  }, []);

  // Reset for a new run.
  const reset = useCallback(() => {
    setStages(INITIAL_STAGES);
    setTickets([]);
    setCycleReport(null);
    setCycleId(null);
    setErrorMsg(null);
    setHitl(null);
    setHitlDecision(null);
    setHalted(null);
  }, []);

  // ──────────────────── SSE consumer ────────────────────
  // Browser EventSource doesn't support POST, so we use fetch + ReadableStream
  // and parse SSE frames manually. This is what Vercel docs recommend for
  // multipart-POST → text/event-stream flows.
  const consumeSse = useCallback(async (body: FormData) => {
    reset();
    setRunning(true);
    try {
      const r = await fetch(`${API_BASE_URL}/telecommunications/cycle-start`, {
        method: 'POST',
        body,
      });
      if (!r.ok || !r.body) {
        const text = await r.text().catch(() => `HTTP ${r.status}`);
        setErrorMsg(text || `HTTP ${r.status}`);
        setRunning(false);
        return;
      }

      const decoder = new TextDecoder();
      const reader  = r.body.getReader();
      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        // SSE frames are separated by double-newline.
        const frames = buffer.split('\n\n');
        buffer = frames.pop() || '';
        for (const frame of frames) {
          if (!frame.trim()) continue;
          const lines = frame.split('\n');
          let event = 'message';
          let dataStr = '';
          for (const line of lines) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            else if (line.startsWith('data:')) dataStr += line.slice(5).trim();
          }
          if (!dataStr) continue;
          let data: any; try { data = JSON.parse(dataStr); } catch { continue; }
          handleFrame(event, data);
        }
      }
      setRunning(false);
    } catch (e: any) {
      setErrorMsg(e?.message || String(e));
      setRunning(false);
    }
  }, [reset]);

  function handleFrame(event: string, data: any) {
    if (event === 'cycle_start') {
      setCycleId(data.cycle_id);
      return;
    }
    if (event === 'stage_start') {
      setStages((prev) => prev.map((s) =>
        s.id === data.stage_id
          ? { ...s, status: 'running', expectedCount: data.expected_count, label: data.label || s.label }
          : s));
      return;
    }
    if (event === 'stage_done') {
      setStages((prev) => prev.map((s) =>
        s.id === data.stage_id ? { ...s, status: 'done', ms: data.ms, summary: data.summary } : s));
      return;
    }
    if (event === 'ticket_created') {
      setTickets((prev) => [...prev, data as CreatedTicket]);
      return;
    }
    if (event === 'cycle_done') {
      setCycleReport(data.report as CycleReport);
      return;
    }
    if (event === 'hitl_required') {
      setHitl(data as HitlRequired);
      return;
    }
    if (event === 'hitl_decided') {
      setHitlDecision(data as HitlDecided);
      // Keep banner visible briefly so user sees the result, then collapse.
      setTimeout(() => { setHitl(null); }, 1500);
      return;
    }
    if (event === 'cycle_halted') {
      setHalted({ reason: data.reason || 'halted' });
      setRunning(false);
      return;
    }
    if (event === 'error') {
      setStages((prev) => prev.map((s) =>
        s.id === data.stage_id ? { ...s, status: 'error', summary: data.error_message } : s));
      setErrorMsg(data.error_message || 'unknown error');
      return;
    }
  }

  // ──────────────────── HITL actions ────────────────────
  const decideHitl = useCallback(async (request_id: string, decision: 'approve' | 'reject') => {
    setHitlBusy(true);
    try {
      const r = await fetch(`${API_BASE_URL}/telecommunications/hitl/${encodeURIComponent(request_id)}/${decision}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer: 'James Patchett' }),
      });
      if (!r.ok) {
        const t = await r.text().catch(() => `HTTP ${r.status}`);
        setErrorMsg(`HITL ${decision} failed: ${t}`);
      }
      // hitl_decided SSE will arrive and close the banner.
    } catch (e: any) {
      setErrorMsg(`HITL ${decision} error: ${e?.message || e}`);
    } finally {
      setHitlBusy(false);
    }
  }, []);

  // ──────────────────── upload + sample triggers ────────────────────

  const startWithFile = useCallback((file: File) => {
    const fd = new FormData(); fd.append('file', file);
    consumeSse(fd);
  }, [consumeSse]);

  const startWithSample = useCallback(async (sample: SampleFile) => {
    // Fetch the sample server-side via the demo-preview endpoint, then
    // re-POST it back as a synthetic File. Keeps the contract identical
    // between drop + sample-click paths.
    try {
      const r = await fetch(`${API_BASE_URL}/documents/demo-preview/verizon_far_edge/robot_outputs/${encodeURIComponent(sample.name)}`);
      if (!r.ok) {
        // Fall back to passing the path through as form field — the backend
        // will still resolve it via the synthetic-data folder.
        const fd = new FormData();
        // Read the local file via a fetch of the absolute path won't work
        // from the browser, so use the file-path passthrough instead.
        fd.append('file', new Blob([''], { type: 'application/xml' }), sample.name);
        return consumeSse(fd);
      }
      const text = await r.text();
      const blob = new Blob([text], { type: 'application/xml' });
      const file = new File([blob], sample.name, { type: 'application/xml' });
      startWithFile(file);
    } catch (e: any) {
      setErrorMsg(`Failed to load sample: ${e?.message || e}`);
    }
  }, [consumeSse, startWithFile]);

  // ──────────────────── DOM event handlers ────────────────────

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); e.stopPropagation();
    if (running) return;
    const f = e.dataTransfer.files?.[0];
    if (f) startWithFile(f);
  }, [running, startWithFile]);

  const onDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault(); e.stopPropagation();
  }, []);

  // ──────────────────── render ────────────────────

  return (
    <>
      <Head><title>Run · Full Certification Cycle · APEX</title></Head>
      <div style={{ padding: '24px 32px', maxWidth: 1240, margin: '0 auto' }}>

        {/* Breadcrumb + title */}
        <div style={{ marginBottom: 18, fontSize: 12, color: '#94a3b8' }}>
          <Link href="/canvas" style={{ color: '#94a3b8', textDecoration: 'none' }}>Canvas</Link>
          {' / '}
          <Link href="/canvas/playbook/pb-tel-1" style={{ color: '#94a3b8', textDecoration: 'none' }}>pb-tel-1</Link>
          {' / Run'}
        </div>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>
          Full Certification Cycle — live run
        </h1>
        <p style={{ fontSize: 13, color: '#64748b', marginBottom: 20 }}>
          Drop a ROBOT XML below. The CertificationAgent pipeline streams progress live, then writes real
          JIRA tickets at the end.
        </p>

        {/* JIRA status pill */}
        <JiraStatusPill probe={jiraStatus} />

        {/* Dropzone */}
        <div
          ref={dropRef}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onClick={() => fileInputRef.current?.click()}
          style={{
            marginTop: 16,
            border: '2px dashed #cbd5e1',
            borderRadius: 12,
            padding: '28px 24px',
            textAlign: 'center',
            cursor: running ? 'not-allowed' : 'pointer',
            background: running ? '#f8fafc' : '#fafbfc',
            transition: 'border-color .15s, background .15s',
          }}
          onMouseEnter={(e) => { if (!running) e.currentTarget.style.borderColor = '#3b82f6'; }}
          onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#cbd5e1'; }}
        >
          <div style={{ fontSize: 28, marginBottom: 4 }}>📥</div>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', marginBottom: 4 }}>
            Drop a ROBOT XML here
          </div>
          <div style={{ fontSize: 12, color: '#64748b' }}>
            …or click to browse. Don't have one? Pick a sample below.
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xml,application/xml,text/xml"
            style={{ display: 'none' }}
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) startWithFile(f);
              e.target.value = '';
            }}
          />
        </div>

        {/* Sample files */}
        {samples.length > 0 && (
          <div style={{ marginTop: 12, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11, color: '#94a3b8', alignSelf: 'center' }}>Use a sample:</span>
            {samples.map((s) => (
              <button key={s.name}
                onClick={() => !running && startWithSample(s)}
                disabled={running}
                title={`${(s.size_bytes / 1024).toFixed(1)} KB`}
                style={{
                  fontSize: 11,
                  padding: '6px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: 999,
                  background: '#fff',
                  color: '#475569',
                  cursor: running ? 'not-allowed' : 'pointer',
                  whiteSpace: 'nowrap',
                }}
              >
                {s.name.replace('robot_output_', '').replace('.xml', '')}
              </button>
            ))}
          </div>
        )}

        {/* Cycle id banner */}
        {cycleId && (
          <div style={{ marginTop: 18, padding: '10px 14px', background: '#eff6ff',
            border: '1px solid #bfdbfe', borderRadius: 10, display: 'flex',
            alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
            <div style={{ fontSize: 12, color: '#1e3a8a' }}>
              <span style={{ fontWeight: 600 }}>CYCLE</span>{' '}
              <span style={{ fontFamily: 'monospace' }}>{cycleId}</span>
              {running && <span style={{ marginLeft: 12, color: '#2563eb' }}>● running</span>}
              {!running && cycleReport && <span style={{ marginLeft: 12, color: '#16a34a' }}>✓ complete</span>}
            </div>
            <button onClick={reset} disabled={running}
              style={{ fontSize: 11, padding: '4px 10px', border: '1px solid #bfdbfe',
                       borderRadius: 6, background: '#fff', color: '#1e3a8a',
                       cursor: running ? 'not-allowed' : 'pointer' }}>
              ↺ reset
            </button>
          </div>
        )}

        {/* HITL banner — surfaces when pipeline pauses for human approval */}
        {hitl && (
          <HitlBanner
            req={hitl}
            decision={hitlDecision}
            busy={hitlBusy}
            onApprove={() => decideHitl(hitl.request_id, 'approve')}
            onReject={() => decideHitl(hitl.request_id, 'reject')}
          />
        )}

        {/* Halted banner — cycle was rejected at HITL gate */}
        {halted && (
          <div style={{ marginTop: 18, padding: 14, background: '#fef2f2',
            border: '1px solid #fecaca', borderRadius: 10, fontSize: 13, color: '#7f1d1d' }}>
            <strong>✗ Cycle halted.</strong> {halted.reason}. No JIRA tickets were created.
          </div>
        )}

        {/* Stage timeline */}
        {(running || cycleId) && (
          <div style={{ marginTop: 18 }}>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em',
                          textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>
              Pipeline progress
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {stages.map((s, i) => <StageRow key={s.id} stage={s} index={i + 1} />)}
            </div>
          </div>
        )}

        {/* Tickets stream */}
        {tickets.length > 0 && (
          <div style={{ marginTop: 22 }}>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em',
                          textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>
              JIRA tickets created — {tickets.length}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: 8 }}>
              {tickets.map((t) => <TicketCard key={`${t.i}-${t.key}`} ticket={t} />)}
            </div>
          </div>
        )}

        {/* Result summary */}
        {cycleReport && <ResultPanel report={cycleReport} ticketCount={tickets.length}
                                      allMock={tickets.length > 0 && tickets.every(t => t.mock)} />}

        {/* Error */}
        {errorMsg && (
          <div style={{ marginTop: 18, padding: 12, background: '#fef2f2',
            border: '1px solid #fecaca', borderRadius: 10, fontSize: 12, color: '#b91c1c' }}>
            ✗ {errorMsg}
          </div>
        )}

      </div>
    </>
  );
}

// ──────────────────────────── sub-components ────────────────────────────

function JiraStatusPill({ probe }: { probe: JiraConfigProbe | null }) {
  if (!probe) {
    return <span style={pillStyle('#f1f5f9', '#475569')}>● JIRA status: loading…</span>;
  }
  const { config, probe: p } = probe;
  if (config.mock_mode) {
    return (
      <span style={pillStyle('#fef9c3', '#92400e')}>
        ● JIRA: <strong style={{ marginLeft: 4 }}>MOCK</strong> ·
        <span style={{ marginLeft: 4 }}>{config.mock_reason}</span>
      </span>
    );
  }
  if (p.ok) {
    return (
      <span style={pillStyle('#dcfce7', '#166534')}>
        ● JIRA: <strong style={{ marginLeft: 4 }}>LIVE</strong> ·
        <span style={{ marginLeft: 4 }}>{config.url}</span> ·
        <span style={{ marginLeft: 4 }}>project {config.project_key}</span> ·
        <span style={{ marginLeft: 4 }}>auth as {p.display || p.email}</span>
      </span>
    );
  }
  return (
    <span style={pillStyle('#fee2e2', '#991b1b')}>
      ● JIRA: <strong style={{ marginLeft: 4 }}>ERROR</strong> ·
      <span style={{ marginLeft: 4 }}>{p.error || `HTTP ${p.http_status ?? '?'}`}</span>
    </span>
  );
}

function pillStyle(bg: string, color: string): React.CSSProperties {
  return {
    display: 'inline-flex', alignItems: 'center',
    fontSize: 11, padding: '4px 10px', borderRadius: 999,
    background: bg, color: color,
    fontFamily: 'inherit',
  };
}

function StageRow({ stage, index }: { stage: StageState; index: number }) {
  const dot =
    stage.status === 'done'    ? '#16a34a' :
    stage.status === 'running' ? '#2563eb' :
    stage.status === 'error'   ? '#dc2626' : '#cbd5e1';
  const bg =
    stage.status === 'done'    ? '#f0fdf4' :
    stage.status === 'running' ? '#eff6ff' :
    stage.status === 'error'   ? '#fef2f2' : '#fafbfc';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px',
                  background: bg, border: '1px solid #f1f5f9', borderRadius: 10 }}>
      <span style={{ width: 22, height: 22, borderRadius: '50%', background: dot, color: '#fff',
                     display: 'flex', alignItems: 'center', justifyContent: 'center',
                     fontSize: 11, fontWeight: 700 }}>{index}</span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{stage.label}</div>
        {stage.summary && (
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{stage.summary}</div>
        )}
      </div>
      <div style={{ fontSize: 11, color: '#94a3b8', whiteSpace: 'nowrap' }}>
        {stage.status === 'running' && <span>● running…</span>}
        {stage.status === 'done'    && <span>{stage.ms} ms</span>}
        {stage.status === 'pending' && <span>—</span>}
        {stage.status === 'error'   && <span style={{ color: '#dc2626' }}>error</span>}
      </div>
    </div>
  );
}

function TicketCard({ ticket }: { ticket: CreatedTicket }) {
  const sev = ticket.severity || '—';
  const sevColor =
    sev === 'P1' ? '#dc2626' :
    sev === 'P2' ? '#d97706' :
    sev === 'P3' ? '#475569' : '#94a3b8';
  return (
    <div style={{ padding: '10px 12px', background: '#fff',
                  border: '1px solid #e2e8f0', borderRadius: 10,
                  display: 'flex', flexDirection: 'column', gap: 6 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <span style={{ fontFamily: 'monospace', fontSize: 12, fontWeight: 600, color: '#0f172a' }}>
          {ticket.key || '…'}
        </span>
        <span style={{ display: 'inline-flex', gap: 4 }}>
          <span style={{ fontSize: 10, fontWeight: 700, color: sevColor, background: '#fff',
                          border: `1px solid ${sevColor}33`, padding: '2px 6px', borderRadius: 999 }}>
            {sev}
          </span>
          {ticket.mock && (
            <span style={{ fontSize: 10, fontWeight: 700, color: '#92400e', background: '#fef9c3',
                            border: '1px solid #fde68a', padding: '2px 6px', borderRadius: 999 }}>
              MOCK
            </span>
          )}
        </span>
      </div>
      <div style={{ fontSize: 11, color: '#475569', lineHeight: 1.4 }}>{ticket.summary}</div>
      {ticket.url && (
        <a href={ticket.url} target="_blank" rel="noreferrer"
           style={{ fontSize: 11, color: '#2563eb', textDecoration: 'none' }}>
          Open in JIRA →
        </a>
      )}
    </div>
  );
}

function HitlBanner({ req, decision, busy, onApprove, onReject }: {
  req: HitlRequired;
  decision: HitlDecided | null;
  busy: boolean;
  onApprove: () => void;
  onReject:  () => void;
}) {
  // Once the decision lands, render the resolution state instead of the buttons.
  if (decision) {
    const ok    = decision.decision === 'approve';
    const color = ok ? '#16a34a' : '#dc2626';
    const bg    = ok ? '#f0fdf4' : '#fef2f2';
    const bd    = ok ? '#bbf7d0' : '#fecaca';
    return (
      <div style={{ marginTop: 18, padding: '14px 18px', background: bg,
        border: `1px solid ${bd}`, borderRadius: 12, display: 'flex',
        alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 22 }}>{ok ? '✓' : '✗'}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color }}>
            HITL {ok ? 'approved' : 'rejected'} by {decision.reviewer || '—'}
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
            Request <span style={{ fontFamily: 'monospace' }}>{req.request_id}</span> ·
            Logged immutably to the Audit Lens
            {decision.comment && <> · <em>"{decision.comment}"</em></>}
          </div>
        </div>
      </div>
    );
  }

  const palette = req.severity === 'high'
    ? { bg: '#fef2f2', bd: '#fecaca', accent: '#dc2626' }
    : { bg: '#fffbeb', bd: '#fde68a', accent: '#d97706' };

  return (
    <div style={{
      marginTop: 18, padding: '16px 20px', background: palette.bg,
      border: `2px solid ${palette.bd}`, borderRadius: 12,
      display: 'flex', flexDirection: 'column', gap: 12,
      animation: 'hitlPulse 2s ease-in-out infinite',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <span style={{ fontSize: 22, color: palette.accent, lineHeight: 1 }}>⚠</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em',
            textTransform: 'uppercase', color: palette.accent, marginBottom: 4 }}>
            Human-in-the-loop · {req.severity} severity · {req.agent}
          </div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
            Pipeline paused for approval — request <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{req.request_id}</span>
          </div>
          <div style={{ fontSize: 12, color: '#374151', lineHeight: 1.6 }}>
            {req.reason}
          </div>
          <div style={{ marginTop: 8, padding: '8px 10px', background: '#fff',
            border: '1px solid #e2e8f0', borderRadius: 8, fontSize: 11, color: '#475569' }}>
            <strong>Proposed action:</strong> {req.proposed_action}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8, marginLeft: 34 }}>
        <button
          onClick={onApprove} disabled={busy}
          style={{
            padding: '8px 18px', borderRadius: 8, fontSize: 12, fontWeight: 700,
            background: '#16a34a', color: '#fff', border: 'none',
            cursor: busy ? 'not-allowed' : 'pointer', opacity: busy ? 0.6 : 1,
          }}
        >
          ✓ Approve — proceed with JIRA writes
        </button>
        <button
          onClick={onReject} disabled={busy}
          style={{
            padding: '8px 18px', borderRadius: 8, fontSize: 12, fontWeight: 700,
            background: '#dc2626', color: '#fff', border: 'none',
            cursor: busy ? 'not-allowed' : 'pointer', opacity: busy ? 0.6 : 1,
          }}
        >
          ✗ Reject — halt pipeline
        </button>
        <span style={{ fontSize: 10, color: '#94a3b8', alignSelf: 'center', marginLeft: 8 }}>
          Decision logged to Audit Lens. Pipeline auto-rejects after 10 min.
        </span>
      </div>
      <style>{`
        @keyframes hitlPulse {
          0%,100% { box-shadow: 0 0 0 0 ${palette.accent}33; }
          50%     { box-shadow: 0 0 0 8px ${palette.accent}00; }
        }
      `}</style>
    </div>
  );
}

function ResultPanel({ report, ticketCount, allMock }: { report: CycleReport; ticketCount: number; allMock: boolean }) {
  const status = report.overall_status || '—';
  const statusBg = status.startsWith('PROCEED') ? '#dcfce7' :
                   status.startsWith('CONDITIONAL') ? '#fef9c3' :
                   '#fee2e2';
  const statusColor = status.startsWith('PROCEED') ? '#166534' :
                      status.startsWith('CONDITIONAL') ? '#92400e' :
                      '#991b1b';
  return (
    <div style={{ marginTop: 22, padding: 18, border: '1px solid #e2e8f0',
                  borderRadius: 12, background: '#fff' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 8 }}>
        <div>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Cycle result</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
            {report.device_under_test} · {report.firmware_version} · cycle <span style={{ fontFamily: 'monospace' }}>{report.cycle_id}</span>
          </div>
        </div>
        <span style={{ fontSize: 11, fontWeight: 700, color: statusColor, background: statusBg,
                       padding: '4px 10px', borderRadius: 999 }}>
          {status}
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: 12 }}>
        <Metric label="Total tests"     value={report.total_tests} />
        <Metric label="Passed"          value={report.pass_count}      color="#16a34a" />
        <Metric label="Failed"          value={report.fail_count}      color="#dc2626" />
        <Metric label="Warn"            value={report.warn_count}      color="#d97706" />
        <Metric label="P1 / P2 / P3"    value={`${report.p1_count ?? '—'} / ${report.p2_count ?? '—'} / ${report.p3_count ?? '—'}`} />
        <Metric label="Schema drift"    value={report.schema_drift_events} />
        <Metric label="Scripts impacted" value={report.scripts_impacted_by_drift} />
        <Metric label="JIRA tickets"    value={ticketCount} color="#2563eb" />
        <Metric label="Hours saved"     value={report.hours_saved_vs_manual} />
      </div>
      <div style={{ marginTop: 14, fontSize: 11, color: '#94a3b8',
                     padding: '8px 12px', background: '#f8fafc', borderRadius: 8 }}>
        Audit Lens event: <span style={{ fontFamily: 'monospace' }}>{report.audit_lens_event_id}</span>
        {allMock && (
          <span style={{ marginLeft: 12, color: '#92400e', fontWeight: 600 }}>
            ● all tickets mock — paste your JIRA URL into backend/.env to write live
          </span>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value, color }: { label: string; value?: string | number | null; color?: string }) {
  return (
    <div>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.06em',
                     textTransform: 'uppercase', color: '#94a3b8' }}>{label}</div>
      <div style={{ fontSize: 18, fontWeight: 700, color: color || '#0f172a', marginTop: 2 }}>
        {value ?? '—'}
      </div>
    </div>
  );
}
