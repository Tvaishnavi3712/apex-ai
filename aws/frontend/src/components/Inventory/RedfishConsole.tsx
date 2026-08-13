/**
 * Redfish Console — interrogate a server's BMC and watch it happen.
 *
 * Runs the walk Apex performs against iLO / iDRAC: each step shows the exact
 * request issued, the status and timing, the JSON the BMC returned, and any
 * compliance finding that response drove.
 *
 * Steps arrive from the API in one response; they are revealed progressively
 * so the walk reads as a sequence of requests rather than a wall of output.
 *
 * Credentials: the console never holds any. Replay mode needs none, and Live
 * mode passes what you type straight through to the single request and forgets
 * it — nothing is stored in state beyond the open dialog, logged, or persisted.
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ─────────────────────────────────────────────────────────────────────────────
// types
// ─────────────────────────────────────────────────────────────────────────────

interface Finding {
  step: string;
  result: string;
  detail: string;
  category: string;
}

interface Step {
  seq: number;
  name: string;
  method: string;
  url: string;
  command: string;
  status: number;
  duration_ms: number;
  response: unknown;
  error: string | null;
  source: string;
  findings: Finding[];
  reason_for_change: string | null;
  required_change: string | null;
}

interface WalkResult {
  server_id: string;
  bmc_ip: string;
  hostname: string | null;
  platform: string | null;
  mode: string;
  requests: number;
  succeeded: number;
  failed: number;
  total_duration_ms: number;
  steps: Step[];
}

type Phase = 'idle' | 'running' | 'done' | 'error';

// ─────────────────────────────────────────────────────────────────────────────
// component
// ─────────────────────────────────────────────────────────────────────────────

export function RedfishConsole({ serverId, onClose }: { serverId: string; onClose: () => void }) {
  const [phase, setPhase] = useState<Phase>('idle');
  const [result, setResult] = useState<WalkResult | null>(null);
  const [revealed, setRevealed] = useState(0);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

  const [liveMode, setLiveMode] = useState(false);
  const [liveHost, setLiveHost] = useState('');
  const [liveUser, setLiveUser] = useState('');
  const [livePass, setLivePass] = useState('');

  const scrollRef = useRef<HTMLDivElement | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);

  // Clear pending reveal timers on unmount so a closed dialog can't set state.
  useEffect(() => () => { timers.current.forEach(clearTimeout); }, []);

  // Esc closes, matching the rest of the app's panels.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const run = useCallback(async () => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    setPhase('running');
    setResult(null);
    setRevealed(0);
    setExpanded(new Set());
    setError(null);

    const body: Record<string, unknown> = {};
    if (liveMode && liveUser && livePass) {
      body.live = { host: liveHost || undefined, username: liveUser, password: livePass, verify: false };
    }

    try {
      const r = await fetch(
        `${API_BASE_URL}/inventory/servers/${encodeURIComponent(serverId)}/interrogate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        },
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data: WalkResult = await r.json();

      // Credentials were needed for exactly one request. Drop them now.
      setLivePass('');

      setResult(data);

      // Reveal one step at a time so the walk reads as a sequence.
      data.steps.forEach((_, i) => {
        timers.current.push(
          setTimeout(() => {
            setRevealed(i + 1);
            if (i === data.steps.length - 1) setPhase('done');
          }, i * 260),
        );
      });
      if (data.steps.length === 0) setPhase('done');
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setPhase('error');
    }
  }, [serverId, liveMode, liveHost, liveUser, livePass]);

  // Keep the newest step in view while the walk streams.
  useEffect(() => {
    if (phase === 'running' && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [revealed, phase]);

  const visible = useMemo(
    () => (result ? result.steps.slice(0, revealed) : []),
    [result, revealed],
  );

  const toggle = (seq: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(seq)) next.delete(seq); else next.add(seq);
      return next;
    });
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(15,23,42,.55)',
        zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#fff', borderRadius: 16, width: 'min(1000px, 100%)',
          maxHeight: 'calc(100vh - 48px)', display: 'flex', flexDirection: 'column',
          overflow: 'hidden', boxShadow: '0 24px 60px rgba(15,23,42,.3)',
        }}
      >
        {/* ── header ─────────────────────────────────────────────────── */}
        <div style={{
          padding: '16px 20px', borderBottom: '1px solid #e2e8f0',
          display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16,
        }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Redfish Console</div>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 3 }}>
              {result?.hostname || serverId}
              {result?.bmc_ip && (
                <span style={{ fontFamily: 'ui-monospace, monospace', color: '#94a3b8' }}> · {result.bmc_ip}</span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              border: '1px solid #e2e8f0', background: '#fff', borderRadius: 8,
              width: 30, height: 30, cursor: 'pointer', color: '#64748b', fontSize: 16, lineHeight: 1,
            }}
          >×</button>
        </div>

        {/* ── controls ───────────────────────────────────────────────── */}
        <div style={{ padding: '14px 20px', borderBottom: '1px solid #e2e8f0', background: '#f8fafc' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <button
              onClick={run}
              disabled={phase === 'running' || (liveMode && (!liveUser || !livePass))}
              className="btn btn-primary"
              style={{ opacity: phase === 'running' ? 0.6 : 1 }}
            >
              {phase === 'running' ? 'Interrogating…' : phase === 'done' ? 'Run again' : 'Run interrogation'}
            </button>

            <label style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, color: '#475569', cursor: 'pointer' }}>
              <input type="checkbox" checked={liveMode} onChange={(e) => setLiveMode(e.target.checked)} />
              Live BMC
            </label>

            {result && (
              <div style={{ marginLeft: 'auto', display: 'flex', gap: 14, fontSize: 12, color: '#475569' }}>
                <span><strong style={{ color: '#0f172a' }}>{result.requests}</strong> requests</span>
                <span style={{ color: '#15803d' }}><strong>{result.succeeded}</strong> ok</span>
                {result.failed > 0 && <span style={{ color: '#b91c1c' }}><strong>{result.failed}</strong> failed</span>}
                <span><strong style={{ color: '#0f172a' }}>{result.total_duration_ms}</strong> ms</span>
                <span style={{
                  background: result.mode === 'live' ? '#dcfce7' : '#eff6ff',
                  color: result.mode === 'live' ? '#15803d' : '#1d4ed8',
                  padding: '2px 8px', borderRadius: 999, fontWeight: 700, fontSize: 11,
                }}>{result.mode}</span>
              </div>
            )}
          </div>

          {liveMode && (
            <div style={{ marginTop: 12 }}>
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <input
                  value={liveHost} onChange={(e) => setLiveHost(e.target.value)}
                  placeholder="BMC host (blank = this server's address)"
                  style={inputStyle}
                />
                <input
                  value={liveUser} onChange={(e) => setLiveUser(e.target.value)}
                  placeholder="Username" autoComplete="off"
                  style={{ ...inputStyle, maxWidth: 170 }}
                />
                <input
                  value={livePass} onChange={(e) => setLivePass(e.target.value)}
                  placeholder="Password" type="password" autoComplete="new-password"
                  style={{ ...inputStyle, maxWidth: 170 }}
                />
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, lineHeight: 1.5 }}>
                Used for this one request, then discarded — Apex stores no BMC credentials.
                The lab BMCs sit on internal IPv6 behind a jump server, so leave this off
                unless the machine can actually reach the target.
              </div>
            </div>
          )}
        </div>

        {/* ── body ───────────────────────────────────────────────────── */}
        <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', background: '#fff' }}>
          {phase === 'idle' && (
            <div style={{ textAlign: 'center', padding: '48px 20px' }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#475569' }}>Ready to interrogate</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 8, lineHeight: 1.6, maxWidth: 520, margin: '8px auto 0' }}>
                Apex walks the BMC&apos;s Redfish tree — identity, health, BIOS and vRAN attributes,
                Secure Boot, thermal, NICs, storage, firmware — and compares what the hardware
                reports against the provisioning standard.
              </div>
            </div>
          )}

          {phase === 'error' && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 12, padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#b91c1c' }}>Interrogation failed</div>
              <div style={{ fontSize: 11, color: '#b91c1c', marginTop: 4, fontFamily: 'ui-monospace, monospace' }}>{error}</div>
            </div>
          )}

          <div style={{ display: 'grid', gap: 8 }}>
            {visible.map((s) => (
              <StepRow
                key={s.seq}
                step={s}
                open={expanded.has(s.seq)}
                onToggle={() => toggle(s.seq)}
              />
            ))}
          </div>

          {phase === 'running' && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 4px', color: '#64748b', fontSize: 12 }}>
              <Spinner />
              GET {result?.steps[revealed]?.url || '…'}
            </div>
          )}

          {phase === 'done' && result && (
            <Verdict result={result} />
          )}
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// pieces
// ─────────────────────────────────────────────────────────────────────────────

const inputStyle: React.CSSProperties = {
  flex: 1, minWidth: 150, padding: '7px 12px', borderRadius: 8,
  border: '1px solid #cbd5e1', fontSize: 12, color: '#0f172a',
  background: '#fff', outline: 'none',
};

function StepRow({ step, open, onToggle }: { step: Step; open: boolean; onToggle: () => void }) {
  const ok = step.status >= 200 && step.status < 300;
  const worst = worstFinding(step.findings);

  return (
    <div style={{ border: '1px solid #e2e8f0', borderRadius: 10, overflow: 'hidden' }}>
      <button
        onClick={onToggle}
        style={{
          width: '100%', textAlign: 'left', cursor: 'pointer', background: '#fff',
          border: 'none', padding: '10px 12px', display: 'flex', alignItems: 'center', gap: 10,
        }}
      >
        <span style={{ fontSize: 11, color: '#94a3b8', width: 20, fontFamily: 'ui-monospace, monospace' }}>
          {String(step.seq).padStart(2, '0')}
        </span>
        <span style={{
          fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 5,
          background: ok ? '#f0fdf4' : '#fef2f2', color: ok ? '#15803d' : '#b91c1c',
        }}>{step.status || 'ERR'}</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#475569', width: 34 }}>{step.method}</span>
        <span style={{
          flex: 1, minWidth: 0, fontSize: 11, color: '#0f172a',
          fontFamily: 'ui-monospace, monospace', overflow: 'hidden',
          textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>{step.url}</span>

        {worst && (
          <span style={{
            fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 999,
            background: worst === 'DRIFT' || worst === 'WARN' ? '#fff7ed' : worst === 'FAIL' ? '#fef2f2' : '#f0fdf4',
            color: worst === 'DRIFT' || worst === 'WARN' ? '#c2410c' : worst === 'FAIL' ? '#b91c1c' : '#15803d',
          }}>{worst}</span>
        )}

        <span style={{ fontSize: 10, color: '#94a3b8', width: 46, textAlign: 'right' }}>{step.duration_ms}ms</span>
        <span style={{ fontSize: 10, color: '#cbd5e1' }}>{open ? '▾' : '▸'}</span>
      </button>

      {open && (
        <div style={{ borderTop: '1px solid #f1f5f9', padding: 12, background: '#fafbfc' }}>
          <Label>Request</Label>
          <pre style={preStyle}>{step.command}</pre>

          {step.error && (
            <>
              <Label>Error</Label>
              <pre style={{ ...preStyle, background: '#7f1d1d' }}>{step.error}</pre>
            </>
          )}

          {step.response != null && (
            <>
              <Label>Response</Label>
              <pre style={{ ...preStyle, maxHeight: 300 }}>
                {JSON.stringify(step.response, null, 2)}
              </pre>
            </>
          )}

          {step.findings.length > 0 && (
            <>
              <Label>Compliance</Label>
              {step.findings.map((f, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 8, alignItems: 'flex-start',
                  padding: '6px 0', borderBottom: '1px solid #f1f5f9',
                }}>
                  <span style={{
                    fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 999,
                    background: f.result.startsWith('PASS') ? '#f0fdf4' : '#fff7ed',
                    color: f.result.startsWith('PASS') ? '#15803d' : '#c2410c',
                  }}>{f.result}</span>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: '#0f172a' }}>{f.step}</div>
                    <div style={{ fontSize: 10, color: '#64748b', lineHeight: 1.5 }}>{f.detail}</div>
                  </div>
                </div>
              ))}
            </>
          )}

          {step.required_change && (
            <div style={{
              marginTop: 10, background: '#eff6ff', border: '1px solid #bfdbfe',
              borderRadius: 8, padding: 10, fontSize: 11, color: '#1e40af', lineHeight: 1.5,
            }}>
              <strong>Monitoring change required: </strong>{step.required_change}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Verdict({ result }: { result: WalkResult }) {
  const findings = result.steps.flatMap((s) => s.findings);
  const drift = findings.filter((f) => ['DRIFT', 'WARN', 'FAIL'].includes(f.result));
  const unique = Array.from(new Map(drift.map((f) => [f.step, f])).values());

  return (
    <div style={{
      marginTop: 16, padding: 14, borderRadius: 12,
      background: unique.length ? '#fffbf5' : '#f0fdf4',
      border: '1px solid ' + (unique.length ? '#fed7aa' : '#bbf7d0'),
    }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: unique.length ? '#c2410c' : '#15803d' }}>
        {unique.length
          ? `Interrogation complete — ${unique.length} item${unique.length === 1 ? '' : 's'} need attention`
          : 'Interrogation complete — server matches the provisioning standard'}
      </div>
      {unique.length > 0 && (
        <div style={{ marginTop: 8, display: 'grid', gap: 4 }}>
          {unique.map((f, i) => (
            <div key={i} style={{ fontSize: 11, color: '#7c2d12' }}>
              <strong>{f.result}</strong> · {f.step}
            </div>
          ))}
          <div style={{ fontSize: 11, color: '#9a3412', marginTop: 6, lineHeight: 1.5 }}>
            Create a remediation job from the Inventory panel to fix these, or schedule the
            check to run nightly so drift is caught before it reaches a wave.
          </div>
        </div>
      )}
      <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 10 }}>
        {result.requests} Redfish requests · {result.total_duration_ms}ms · mode: {result.mode}
      </div>
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
      letterSpacing: '.06em', color: '#94a3b8', margin: '10px 0 5px',
    }}>{children}</div>
  );
}

const preStyle: React.CSSProperties = {
  background: '#0f172a', color: '#e2e8f0', fontSize: 10.5, padding: 10,
  borderRadius: 8, overflowX: 'auto', fontFamily: 'ui-monospace, monospace',
  lineHeight: 1.6, margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word',
};

function worstFinding(findings: Finding[]): string | null {
  if (!findings.length) return null;
  const order = ['FAIL', 'DRIFT', 'WARN'];
  for (const level of order) {
    if (findings.some((f) => f.result === level)) return level;
  }
  return 'PASS';
}

function Spinner() {
  return (
    <span
      style={{
        width: 12, height: 12, borderRadius: 999,
        border: '2px solid #cbd5e1', borderTopColor: '#0f172a',
        display: 'inline-block', animation: 'apex-spin .7s linear infinite',
      }}
    >
      <style>{`@keyframes apex-spin { to { transform: rotate(360deg) } }`}</style>
    </span>
  );
}
