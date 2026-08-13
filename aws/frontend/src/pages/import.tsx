/**
 * Import — bring existing Robot Framework / Ansible automation into Apex.
 *
 * Three steps, all visible: pick a source, review what Apex made of it, commit.
 * The review step shows every source element and the action it mapped to, so
 * nothing lands without an engineer having seen the translation.
 *
 * Nothing is written until Commit is pressed.
 */

import React, { useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ─────────────────────────────────────────────────────────────────────────────
// types
// ─────────────────────────────────────────────────────────────────────────────

interface Sample {
  filename: string; path: string; format: string; size_bytes: number; description: string;
}

interface MappingRow {
  source: string; source_type: string; status: string; action_id: string; reason: string;
}

interface Analysis {
  detected_format: string;
  source_summary: Record<string, unknown>;
  proposed_playbook: Record<string, any>;
  mapping: MappingRow[];
  mapped_count: number;
  review_count: number;
  action_count: number;
  warnings: string[];
  yaml_preview: string;
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' }, ...init,
  });
  if (!r.ok) {
    let detail = `HTTP ${r.status}`;
    try { detail = (await r.json())?.detail || detail; } catch { /* keep status */ }
    throw new Error(detail);
  }
  return r.json();
}

// ─────────────────────────────────────────────────────────────────────────────
// page
// ─────────────────────────────────────────────────────────────────────────────

export default function ImportPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [committed, setCommitted] = useState<{ path: string; seed_command: string } | null>(null);
  const [tab, setTab] = useState<'mapping' | 'yaml'>('mapping');
  const fileRef = useRef<HTMLInputElement | null>(null);

  const samplesQuery = useQuery<{ samples: Sample[] }>({
    queryKey: ['import', 'samples'],
    queryFn: () => api('/import/samples'),
    retry: false,
  });

  const reset = () => { setAnalysis(null); setCommitted(null); setError(null); };

  const analyzeSample = async (s: Sample) => {
    reset(); setBusy(true);
    try {
      setAnalysis(await api<Analysis>('/import/analyze/sample', {
        method: 'POST',
        body: JSON.stringify({ filename: s.filename }),
      }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally { setBusy(false); }
  };

  const analyzeFile = async (file: File) => {
    reset(); setBusy(true);
    try {
      const content = await file.text();
      setAnalysis(await api<Analysis>('/import/analyze', {
        method: 'POST',
        body: JSON.stringify({ content, filename: file.name }),
      }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally { setBusy(false); }
  };

  const commit = async () => {
    if (!analysis) return;
    setBusy(true); setError(null);
    try {
      setCommitted(await api('/import/commit', {
        method: 'POST',
        body: JSON.stringify({ playbook: analysis.proposed_playbook, overwrite: false }),
      }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally { setBusy(false); }
  };

  const summaryPairs = useMemo(() => {
    if (!analysis) return [];
    return Object.entries(analysis.source_summary).map(([k, v]) => [
      k.replace(/_/g, ' '),
      typeof v === 'object' && v !== null
        ? Object.entries(v as Record<string, unknown>).map(([a, b]) => `${a}: ${b}`).join(' · ')
        : String(v),
    ]) as [string, string][];
  }, [analysis]);

  return (
    <>
      <Head><title>Import | APEX</title></Head>

      <div style={{ marginBottom: 18 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Import a workflow</h2>
        <p style={{ fontSize: 14, color: '#64748b', marginTop: 4, maxWidth: 760 }}>
          Apex ingests the automation your team already owns — Robot Framework certification
          suites and Ansible provisioning playbooks — and shows exactly how every element maps
          before anything is written.
        </p>
      </div>

      {/* ── step 1: source ─────────────────────────────────────────────── */}
      <StepHeader n={1} title="Choose a source" />

      <div style={{ display: 'grid', gap: 10, marginBottom: 8 }}>
        {samplesQuery.data?.samples.map((s) => (
          <button
            key={s.filename}
            onClick={() => analyzeSample(s)}
            disabled={busy}
            style={{
              textAlign: 'left', background: '#fff', border: '1px solid #e2e8f0',
              borderRadius: 12, padding: '13px 16px', cursor: busy ? 'default' : 'pointer',
              display: 'flex', alignItems: 'center', gap: 12,
            }}
          >
            <span style={{
              background: '#eff6ff', color: '#1d4ed8', fontSize: 10, fontWeight: 700,
              padding: '3px 8px', borderRadius: 6, whiteSpace: 'nowrap',
            }}>ROBOT XML</span>
            <span style={{ flex: 1, minWidth: 0 }}>
              <span style={{ display: 'block', fontSize: 13, fontWeight: 600, color: '#0f172a', fontFamily: 'ui-monospace, monospace' }}>
                {s.filename}
              </span>
              <span style={{ display: 'block', fontSize: 11, color: '#64748b', marginTop: 2 }}>
                {s.description}
              </span>
            </span>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>{Math.round(s.size_bytes / 1024)} KB</span>
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 26 }}>
        <input
          ref={fileRef} type="file" accept=".xml,.yml,.yaml" style={{ display: 'none' }}
          onChange={(e) => { const f = e.target.files?.[0]; if (f) analyzeFile(f); }}
        />
        <button style={secondaryBtn} onClick={() => fileRef.current?.click()} disabled={busy}>
          Upload your own file
        </button>
        <span style={{ fontSize: 11, color: '#94a3b8' }}>
          Robot Framework <code>output.xml</code> or an Ansible playbook <code>.yml</code>
        </span>
      </div>

      {busy && !analysis && (
        <div style={{ fontSize: 13, color: '#64748b', marginBottom: 20 }}>Analyzing…</div>
      )}

      {error && (
        <div style={{
          background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 12,
          padding: 14, marginBottom: 20,
        }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#b91c1c' }}>Import failed</div>
          <div style={{ fontSize: 12, color: '#b91c1c', marginTop: 4 }}>{error}</div>
        </div>
      )}

      {/* ── step 2: review ─────────────────────────────────────────────── */}
      {analysis && (
        <>
          <StepHeader n={2} title="Review the translation" />

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, marginBottom: 16 }}>
            <Tile label="Source elements" value={analysis.mapped_count} />
            <Tile label="Apex actions" value={analysis.action_count} />
            <Tile label="Need review" value={analysis.review_count}
                  tone={analysis.review_count > 0 ? 'amber' : 'green'} />
            <Tile label="Format" value={analysis.detected_format.replace(/_/g, ' ')} small />
          </div>

          <div style={{
            background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12,
            padding: 16, marginBottom: 16,
          }}>
            <div style={sectionLabel}>Source</div>
            {summaryPairs.map(([k, v]) => (
              <div key={k} style={{ display: 'flex', gap: 12, padding: '4px 0', fontSize: 12 }}>
                <span style={{ color: '#94a3b8', minWidth: 120, textTransform: 'capitalize' }}>{k}</span>
                <span style={{ color: '#0f172a', flex: 1, wordBreak: 'break-word' }}>{v}</span>
              </div>
            ))}
          </div>

          {analysis.warnings.length > 0 && (
            <div style={{
              background: '#fffbf5', border: '1px solid #fed7aa', borderRadius: 12,
              padding: 14, marginBottom: 16,
            }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: '#c2410c', marginBottom: 6 }}>
                Worth knowing
              </div>
              {analysis.warnings.map((w, i) => (
                <div key={i} style={{ fontSize: 11, color: '#9a3412', lineHeight: 1.6 }}>• {w}</div>
              ))}
            </div>
          )}

          <div className="tab-bar" style={{ width: 'fit-content', marginBottom: 12 }}>
            <TabBtn active={tab === 'mapping'} onClick={() => setTab('mapping')}>
              Mapping ({analysis.mapping.length})
            </TabBtn>
            <TabBtn active={tab === 'yaml'} onClick={() => setTab('yaml')}>Playbook YAML</TabBtn>
          </div>

          {tab === 'mapping' ? (
            <div style={{
              background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12,
              maxHeight: 420, overflowY: 'auto', marginBottom: 20,
            }}>
              {analysis.mapping.map((m, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 10, padding: '8px 14px',
                  borderBottom: '1px solid #f1f5f9',
                }}>
                  <span style={{
                    fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 999,
                    background: m.status === 'FAIL' ? '#fef2f2' : m.status === 'REVIEW' ? '#fff7ed' : '#f0fdf4',
                    color: m.status === 'FAIL' ? '#b91c1c' : m.status === 'REVIEW' ? '#c2410c' : '#15803d',
                    minWidth: 52, textAlign: 'center',
                  }}>{m.status}</span>
                  <span style={{ flex: 1, minWidth: 0, fontSize: 12, color: '#0f172a', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {m.source}
                  </span>
                  <span style={{ fontSize: 11, color: '#94a3b8' }}>→</span>
                  <span style={{ fontSize: 11, color: '#1d4ed8', fontFamily: 'ui-monospace, monospace', minWidth: 190 }}>
                    {m.action_id.split('.').pop()}
                  </span>
                  <span style={{ fontSize: 10, color: '#94a3b8', minWidth: 180, textAlign: 'right' }}>
                    {m.reason}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <pre style={{
              background: '#0f172a', color: '#e2e8f0', fontSize: 11, padding: 16,
              borderRadius: 12, overflowX: 'auto', maxHeight: 420, marginBottom: 20,
              fontFamily: 'ui-monospace, monospace', lineHeight: 1.6,
            }}>{analysis.yaml_preview}</pre>
          )}

          {/* ── step 3: commit ───────────────────────────────────────── */}
          <StepHeader n={3} title="Commit" />

          {committed ? (
            <div style={{
              background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 12, padding: 16,
            }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#15803d' }}>
                Playbook written
              </div>
              <div style={{ fontSize: 12, color: '#166534', marginTop: 6, fontFamily: 'ui-monospace, monospace' }}>
                {committed.path}
              </div>
              <div style={{ fontSize: 11, color: '#166534', marginTop: 10 }}>
                Seed it so it appears in Canvas and can be bound to a job:
              </div>
              <pre style={{
                background: '#0f172a', color: '#e2e8f0', fontSize: 10.5, padding: 10,
                borderRadius: 8, overflowX: 'auto', marginTop: 6,
                fontFamily: 'ui-monospace, monospace',
              }}>{committed.seed_command}</pre>
            </div>
          ) : (
            <div>
              <div style={{ fontSize: 12, color: '#64748b', marginBottom: 10, maxWidth: 620, lineHeight: 1.6 }}>
                This writes <code style={{ color: '#0f172a' }}>{analysis.proposed_playbook.name}.yaml</code>{' '}
                into <code style={{ color: '#0f172a' }}>playbooks/{analysis.proposed_playbook.industry}/</code>.
                Nothing has been written yet.
              </div>
              <button className="btn btn-primary" onClick={commit} disabled={busy}>
                {busy ? 'Writing…' : 'Commit playbook'}
              </button>
            </div>
          )}
        </>
      )}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// pieces
// ─────────────────────────────────────────────────────────────────────────────

function StepHeader({ n, title }: { n: number; title: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
      <span style={{
        width: 22, height: 22, borderRadius: 999, background: '#0f172a', color: '#fff',
        fontSize: 11, fontWeight: 700, display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      }}>{n}</span>
      <span style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{title}</span>
    </div>
  );
}

function Tile({ label, value, tone = 'slate', small }: {
  label: string; value: React.ReactNode; tone?: string; small?: boolean;
}) {
  const fg = tone === 'amber' ? '#c2410c' : tone === 'green' ? '#15803d' : '#0f172a';
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: '13px 15px' }}>
      <div style={{ fontSize: small ? 14 : 22, fontWeight: 700, color: fg, lineHeight: 1.2, textTransform: small ? 'capitalize' : undefined }}>
        {value}
      </div>
      <div style={{ fontSize: 10, color: '#64748b', marginTop: 4, textTransform: 'uppercase', letterSpacing: '.05em' }}>
        {label}
      </div>
    </div>
  );
}

function TabBtn({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button onClick={onClick} style={{
      padding: '7px 14px', fontSize: 12, fontWeight: 600, borderRadius: 8,
      border: '1px solid ' + (active ? '#0f172a' : '#e2e8f0'),
      background: active ? '#0f172a' : '#fff', color: active ? '#fff' : '#475569', cursor: 'pointer',
    }}>{children}</button>
  );
}

const secondaryBtn: React.CSSProperties = {
  padding: '8px 14px', fontSize: 12, fontWeight: 600, borderRadius: 8,
  border: '1px solid #cbd5e1', background: '#fff', color: '#475569', cursor: 'pointer',
};

const sectionLabel: React.CSSProperties = {
  fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
  letterSpacing: '.06em', color: '#475569', marginBottom: 9,
};
