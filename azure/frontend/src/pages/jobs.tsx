/**
 * Jobs — create, duplicate, schedule and run work against real hardware.
 *
 * This is the operator's home: a job binds a playbook to a set of servers and
 * a cadence. Running one walks each target's BMC over Redfish and reports a
 * per-server verdict.
 *
 * Handoffs (the demo chain):
 *   Inventory  → here, via ?server=<id>&name=… to pre-fill a remediation job
 *   here       → Redfish console, to show the evidence behind a verdict
 *   here       → Jira write-back, to turn findings into tickets
 *
 * Data comes from the API only — no hardcoded job fixtures. An empty list is
 * shown as empty, never backfilled with samples.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { RedfishConsole } from '@/components/Inventory/RedfishConsole';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';

// ─────────────────────────────────────────────────────────────────────────────
// types
// ─────────────────────────────────────────────────────────────────────────────

interface TargetDetail {
  id: string;
  hostname: string | null;
  platform: string | null;
  status: string | null;
  known: boolean;
}

interface Job {
  id: string;
  name: string;
  description: string;
  playbook_id: string;
  targets: string[];
  target_details: TargetDetail[];
  schedule: string;
  schedule_label: string;
  enabled: boolean;
  created_at: string;
  run_count: number;
  last_run_at: string | null;
  last_status: string | null;
  duplicated_from?: string;
}

interface Finding { step: string; result: string; detail: string; category: string }

interface RunTarget {
  server_id: string;
  hostname: string | null;
  platform?: string | null;
  bmc_ip?: string;
  status: string;
  requests: number;
  duration_ms?: number;
  findings: Finding[];
  error?: string;
}

interface Run {
  id: string;
  job_id: string;
  job_name: string;
  playbook_id: string;
  playbook_label?: string;
  /** "all", or the endpoint ids the playbook selected for this run. */
  endpoints_walked?: string[] | 'all';
  raises_tickets?: boolean;
  emits_report?: boolean;
  started_at: string;
  finished_at: string;
  status: string;
  targets: RunTarget[];
  target_count: number;
  total_requests: number;
  total_findings: number;
}

interface PlaybookOption {
  id: string;
  name: string;
  description: string;
  /** "all", or the number of Redfish endpoints this playbook walks. */
  endpoint_count: number | string;
  endpoints: string[] | null;
  emits_report: boolean;
  raises_tickets: boolean;
}

interface Options {
  servers: { id: string; hostname: string | null; platform: string | null; vendor: string; status: string }[];
  playbooks: PlaybookOption[];
  schedules: { value: string; label: string }[];
}

// ─────────────────────────────────────────────────────────────────────────────
// helpers
// ─────────────────────────────────────────────────────────────────────────────

const STATUS_TONE: Record<string, { bg: string; fg: string }> = {
  FAIL:  { bg: '#fef2f2', fg: '#b91c1c' },
  ERROR: { bg: '#fef2f2', fg: '#b91c1c' },
  DRIFT: { bg: '#fff7ed', fg: '#c2410c' },
  WARN:  { bg: '#fefce8', fg: '#a16207' },
  PASS:  { bg: '#f0fdf4', fg: '#15803d' },
};

function Chip({ children, tone = 'slate' }: { children: React.ReactNode; tone?: string }) {
  const tones: Record<string, { bg: string; fg: string }> = {
    slate: { bg: '#f1f5f9', fg: '#64748b' },
    blue:  { bg: '#eff6ff', fg: '#1d4ed8' },
    amber: { bg: '#fff7ed', fg: '#c2410c' },
    green: { bg: '#f0fdf4', fg: '#15803d' },
  };
  const t = tones[tone] || tones.slate;
  return (
    <span style={{
      background: t.bg, color: t.fg, fontSize: 10, fontWeight: 700,
      padding: '3px 8px', borderRadius: 999, whiteSpace: 'nowrap',
    }}>{children}</span>
  );
}

function StatusPill({ status }: { status: string | null }) {
  if (!status) return <span style={{ fontSize: 11, color: '#94a3b8' }}>never run</span>;
  const t = STATUS_TONE[status] || { bg: '#f1f5f9', fg: '#475569' };
  return (
    <span style={{
      background: t.bg, color: t.fg, fontSize: 11, fontWeight: 700,
      padding: '3px 9px', borderRadius: 999,
    }}>{status}</span>
  );
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
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

export default function JobsPage() {
  const router = useRouter();
  const qc = useQueryClient();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [duplicating, setDuplicating] = useState<Job | null>(null);
  const [activeRun, setActiveRun] = useState<Run | null>(null);
  const [consoleServer, setConsoleServer] = useState<string | null>(null);
  const [banner, setBanner] = useState<string | null>(null);

  const detailPanelRef = useRef<HTMLDivElement | null>(null);

  const jobsQuery = useQuery<{ jobs: Job[]; count: number }>({
    queryKey: ['jobs'],
    queryFn: () => api('/jobs/'),
    retry: false,
  });

  const optionsQuery = useQuery<Options>({
    queryKey: ['jobs', 'options'],
    queryFn: () => api('/jobs/meta/options'),
    retry: false,
    staleTime: 60_000,
  });

  // Handoff from Inventory: ?server=<id> opens the create form pre-filled.
  useEffect(() => {
    if (!router.isReady) return;
    const server = router.query.server;
    if (typeof server === 'string' && server) setCreating(true);
  }, [router.isReady, router.query.server]);

  // Sticky panel can sit below the fold on a long list — pull it into view.
  useEffect(() => {
    if (!selectedId) return;
    detailPanelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [selectedId]);

  const runMutation = useMutation({
    mutationFn: (jobId: string) => api<Run>(`/jobs/${jobId}/run`, { method: 'POST' }),
    onSuccess: (run) => {
      setActiveRun(run);
      qc.invalidateQueries({ queryKey: ['jobs'] });
    },
    onError: (e: Error) => setBanner(`Run failed: ${e.message}`),
  });

  const deleteMutation = useMutation({
    mutationFn: (jobId: string) => api(`/jobs/${jobId}`, { method: 'DELETE' }),
    onSuccess: () => {
      setSelectedId(null);
      qc.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  const scheduleMutation = useMutation({
    mutationFn: ({ id, schedule }: { id: string; schedule: string }) =>
      api<Job>(`/jobs/${id}`, { method: 'PATCH', body: JSON.stringify({ schedule }) }),
    onSuccess: (j) => {
      setBanner(`“${j.name}” now runs: ${j.schedule_label}`);
      qc.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  const jobs = jobsQuery.data?.jobs ?? [];
  const selected = useMemo(() => jobs.find((j) => j.id === selectedId) || null, [jobs, selectedId]);

  return (
    <>
      <Head><title>Jobs | APEX</title></Head>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18, gap: 16 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Jobs</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4, maxWidth: 720 }}>
            A job binds a playbook to a set of servers and a cadence. Run it once, or let it
            run nightly so drift is caught before it reaches a deployment wave.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setCreating(true)}>+ New Job</button>
      </div>

      {banner && (
        <div style={{
          background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 10,
          padding: '10px 14px', marginBottom: 16, fontSize: 13, color: '#1e40af',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12,
        }}>
          <span>{banner}</span>
          <button onClick={() => setBanner(null)} style={{
            border: 'none', background: 'transparent', cursor: 'pointer', color: '#1e40af', fontSize: 16,
          }}>×</button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: 20, alignItems: 'start' }}>
        <div>
          {jobsQuery.isLoading && (
            <div style={{ display: 'grid', gap: 10 }}>
              {[0, 1].map((i) => (
                <div key={i} style={{ height: 88, background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 12 }} />
              ))}
            </div>
          )}

          {jobsQuery.isError && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 12, padding: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#b91c1c' }}>Could not load jobs</div>
              <div style={{ fontSize: 11, color: '#b91c1c', marginTop: 4 }}>
                {String((jobsQuery.error as Error)?.message)}
              </div>
            </div>
          )}

          {jobsQuery.isSuccess && jobs.length === 0 && (
            <div style={{ background: '#f8fafc', border: '1px dashed #cbd5e1', borderRadius: 12, padding: 32, textAlign: 'center' }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#475569' }}>No jobs yet</div>
              <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 6, lineHeight: 1.6, maxWidth: 420, margin: '6px auto 14px' }}>
                Create one from a playbook and a set of servers — or start from a drift finding
                in Inventory and Apex will pre-fill the target for you.
              </div>
              <button className="btn btn-primary" onClick={() => setCreating(true)}>+ New Job</button>
            </div>
          )}

          <div style={{ display: 'grid', gap: 10 }}>
            {jobs.map((j) => (
              <JobCard
                key={j.id}
                job={j}
                selected={j.id === selectedId}
                busy={runMutation.isPending && runMutation.variables === j.id}
                onSelect={() => setSelectedId(j.id)}
                onRun={() => runMutation.mutate(j.id)}
                onDuplicate={() => setDuplicating(j)}
              />
            ))}
          </div>
        </div>

        <div ref={detailPanelRef} style={{ position: 'sticky', top: 80, scrollMarginTop: 80 }}>
          <JobDetail
            job={selected}
            schedules={optionsQuery.data?.schedules || []}
            onRun={() => selected && runMutation.mutate(selected.id)}
            onDuplicate={() => selected && setDuplicating(selected)}
            onDelete={() => selected && deleteMutation.mutate(selected.id)}
            onSchedule={(schedule) => selected && scheduleMutation.mutate({ id: selected.id, schedule })}
            onEvidence={(serverId) => setConsoleServer(serverId)}
          />
        </div>
      </div>

      {creating && optionsQuery.data && (
        <JobFormModal
          title="New Job"
          options={optionsQuery.data}
          initialTargets={typeof router.query.server === 'string' ? [router.query.server] : []}
          initialName={typeof router.query.name === 'string' ? router.query.name : ''}
          onClose={() => {
            setCreating(false);
            if (router.query.server) router.replace('/jobs', undefined, { shallow: true });
          }}
          onSubmit={async (payload) => {
            const job = await api<Job>('/jobs/', { method: 'POST', body: JSON.stringify(payload) });
            qc.invalidateQueries({ queryKey: ['jobs'] });
            setSelectedId(job.id);
            setBanner(`Created “${job.name}” — ${job.schedule_label}`);
            setCreating(false);
            if (router.query.server) router.replace('/jobs', undefined, { shallow: true });
          }}
        />
      )}

      {duplicating && optionsQuery.data && (
        <JobFormModal
          title={`Duplicate “${duplicating.name}”`}
          options={optionsQuery.data}
          initialName={`${duplicating.name} (copy)`}
          initialPlaybook={duplicating.playbook_id}
          initialTargets={duplicating.targets}
          initialSchedule={duplicating.schedule}
          lockPlaybook
          submitLabel="Duplicate"
          hint="Pick different servers to roll this proven job onto another platform. Run history is not copied."
          onClose={() => setDuplicating(null)}
          onSubmit={async (payload) => {
            const clone = await api<Job>(`/jobs/${duplicating.id}/duplicate`, {
              method: 'POST',
              body: JSON.stringify({ name: payload.name, targets: payload.targets, schedule: payload.schedule }),
            });
            qc.invalidateQueries({ queryKey: ['jobs'] });
            setSelectedId(clone.id);
            setBanner(`Duplicated to “${clone.name}”`);
            setDuplicating(null);
          }}
        />
      )}

      {activeRun && (
        <RunModal
          run={activeRun}
          onClose={() => setActiveRun(null)}
          onEvidence={(serverId) => { setActiveRun(null); setConsoleServer(serverId); }}
        />
      )}

      {consoleServer && (
        <RedfishConsole serverId={consoleServer} onClose={() => setConsoleServer(null)} />
      )}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// cards / panels
// ─────────────────────────────────────────────────────────────────────────────

function JobCard({
  job, selected, busy, onSelect, onRun, onDuplicate,
}: {
  job: Job; selected: boolean; busy: boolean;
  onSelect: () => void; onRun: () => void; onDuplicate: () => void;
}) {
  return (
    <div
      onClick={onSelect}
      style={{
        background: '#fff', cursor: 'pointer',
        border: '1px solid ' + (selected ? '#0f172a' : '#e2e8f0'),
        boxShadow: selected ? '0 0 0 3px rgba(15,23,42,.06)' : 'none',
        borderRadius: 12, padding: '14px 16px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{job.name}</div>
        <StatusPill status={job.last_status} />
      </div>

      {job.description && (
        <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{job.description}</div>
      )}

      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 8, fontFamily: 'ui-monospace, monospace' }}>
        {job.playbook_id}
      </div>

      <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        <span style={{ background: '#eff6ff', color: '#1d4ed8', fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 999 }}>
          {job.schedule_label}
        </span>
        <span style={{ background: '#f1f5f9', color: '#475569', fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 999 }}>
          {job.target_details.length} target{job.target_details.length === 1 ? '' : 's'}
        </span>
        <span style={{ background: '#f1f5f9', color: '#475569', fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 999 }}>
          {job.run_count} run{job.run_count === 1 ? '' : 's'}
        </span>

        <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
          <button
            onClick={(e) => { e.stopPropagation(); onDuplicate(); }}
            style={smallBtn}
          >Duplicate</button>
          <button
            onClick={(e) => { e.stopPropagation(); onRun(); }}
            disabled={busy}
            style={{ ...smallBtn, background: '#0f172a', color: '#fff', borderColor: '#0f172a', opacity: busy ? 0.6 : 1 }}
          >{busy ? 'Running…' : 'Run now'}</button>
        </div>
      </div>
    </div>
  );
}

const smallBtn: React.CSSProperties = {
  padding: '5px 11px', fontSize: 11, fontWeight: 600, borderRadius: 7,
  border: '1px solid #e2e8f0', background: '#fff', color: '#475569', cursor: 'pointer',
};

function JobDetail({
  job, schedules, onRun, onDuplicate, onDelete, onSchedule, onEvidence,
}: {
  job: Job | null;
  schedules: { value: string; label: string }[];
  onRun: () => void; onDuplicate: () => void; onDelete: () => void;
  onSchedule: (s: string) => void;
  onEvidence: (serverId: string) => void;
}) {
  const box: React.CSSProperties = { background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 18 };

  if (!job) {
    return (
      <div style={{ ...box, textAlign: 'center', padding: '40px 20px' }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Select a job</div>
        <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 6, lineHeight: 1.5 }}>
          Its targets, cadence and run history appear here.
        </div>
      </div>
    );
  }

  return (
    <div style={{ ...box, maxHeight: 'calc(100vh - 120px)', overflowY: 'auto' }}>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>{job.name}</div>
      {job.description && <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{job.description}</div>}

      <div style={{ display: 'flex', gap: 8, marginTop: 14 }}>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={onRun}>Run now</button>
        <button style={smallBtn} onClick={onDuplicate}>Duplicate</button>
      </div>

      <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e2e8f0' }}>
        <div style={sectionLabel}>Schedule</div>
        <select
          value={job.schedule}
          onChange={(e) => onSchedule(e.target.value)}
          style={{
            width: '100%', padding: '8px 10px', borderRadius: 8,
            border: '1px solid #cbd5e1', fontSize: 12, color: '#0f172a', background: '#fff',
          }}
        >
          {schedules.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 6 }}>
          Changing this takes effect immediately.
        </div>
      </div>

      <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e2e8f0' }}>
        <div style={sectionLabel}>Playbook</div>
        <div style={{ fontSize: 11, color: '#0f172a', fontFamily: 'ui-monospace, monospace', wordBreak: 'break-all' }}>
          {job.playbook_id}
        </div>
      </div>

      <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e2e8f0' }}>
        <div style={sectionLabel}>Targets ({job.target_details.length})</div>
        {job.target_details.map((t) => (
          <div key={t.id} style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '7px 0', borderBottom: '1px solid #f1f5f9',
          }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 11, fontWeight: 600, color: t.known ? '#0f172a' : '#b91c1c', fontFamily: 'ui-monospace, monospace' }}>
                {t.hostname || t.id}
              </div>
              <div style={{ fontSize: 10, color: '#94a3b8' }}>{t.platform || (t.known ? '' : 'not in inventory')}</div>
            </div>
            {t.known && (
              <button style={{ ...smallBtn, fontSize: 10, padding: '3px 8px' }} onClick={() => onEvidence(t.id)}>
                Evidence
              </button>
            )}
          </div>
        ))}
      </div>

      <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid #e2e8f0' }}>
        <div style={sectionLabel}>History</div>
        <Field label="Runs" value={String(job.run_count)} />
        <Field label="Last run" value={job.last_run_at ? job.last_run_at.replace('T', ' ').slice(0, 16) : '—'} />
        <Field label="Last status" value={job.last_status || '—'} />
        <Field label="Created" value={job.created_at.replace('T', ' ').slice(0, 16)} />
        {job.duplicated_from && <Field label="Duplicated from" value={job.duplicated_from} />}
      </div>

      <button
        onClick={onDelete}
        style={{ ...smallBtn, width: '100%', marginTop: 16, color: '#b91c1c', borderColor: '#fecaca' }}
      >Delete job</button>
    </div>
  );
}

const sectionLabel: React.CSSProperties = {
  fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
  letterSpacing: '.06em', color: '#475569', marginBottom: 9,
};

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, padding: '5px 0' }}>
      <span style={{ fontSize: 11, color: '#94a3b8' }}>{label}</span>
      <span style={{ fontSize: 11, color: '#0f172a', textAlign: 'right' }}>{value}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// modals
// ─────────────────────────────────────────────────────────────────────────────

function Modal({ title, onClose, children, width = 620 }: {
  title: string; onClose: () => void; children: React.ReactNode; width?: number;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, background: 'rgba(15,23,42,.55)', zIndex: 1000,
        display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#fff', borderRadius: 16, width: `min(${width}px, 100%)`,
          maxHeight: 'calc(100vh - 48px)', display: 'flex', flexDirection: 'column',
          overflow: 'hidden', boxShadow: '0 24px 60px rgba(15,23,42,.3)',
        }}
      >
        <div style={{
          padding: '16px 20px', borderBottom: '1px solid #e2e8f0',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12,
        }}>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>{title}</div>
          <button onClick={onClose} aria-label="Close" style={{
            border: '1px solid #e2e8f0', background: '#fff', borderRadius: 8,
            width: 30, height: 30, cursor: 'pointer', color: '#64748b', fontSize: 16, lineHeight: 1,
          }}>×</button>
        </div>
        <div style={{ overflowY: 'auto', padding: 20 }}>{children}</div>
      </div>
    </div>
  );
}

function JobFormModal({
  title, options, onClose, onSubmit,
  initialName = '', initialPlaybook = '', initialTargets = [], initialSchedule = 'manual',
  lockPlaybook = false, submitLabel = 'Create job', hint,
}: {
  title: string;
  options: Options;
  onClose: () => void;
  onSubmit: (payload: { name: string; playbook_id: string; targets: string[]; schedule: string; description: string }) => Promise<void>;
  initialName?: string; initialPlaybook?: string; initialTargets?: string[]; initialSchedule?: string;
  lockPlaybook?: boolean; submitLabel?: string; hint?: string;
}) {
  const [name, setName] = useState(initialName);
  const [playbook, setPlaybook] = useState(initialPlaybook || options.playbooks[0]?.id || '');
  const [targets, setTargets] = useState<string[]>(initialTargets);
  const [schedule, setSchedule] = useState(initialSchedule);
  const [description, setDescription] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Order once, on mount: servers arriving pre-selected (e.g. handed off from a
  // finding in Inventory) sort to the top so the selection is visible without
  // scrolling. Deliberately not recomputed — rows jumping as you tick would be
  // worse than a little scrolling.
  const [orderedServers] = useState(() => {
    const pre = new Set(initialTargets);
    return [...options.servers].sort(
      (a, b) => Number(pre.has(b.id)) - Number(pre.has(a.id)),
    );
  });

  const toggle = (id: string) =>
    setTargets((prev) => (prev.includes(id) ? prev.filter((t) => t !== id) : [...prev, id]));

  const submit = async () => {
    setError(null);
    if (!name.trim()) { setError('Give the job a name.'); return; }
    if (!targets.length) { setError('Select at least one target server.'); return; }
    setBusy(true);
    try {
      await onSubmit({ name: name.trim(), playbook_id: playbook, targets, schedule, description });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Modal title={title} onClose={onClose}>
      {hint && (
        <div style={{
          background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 10,
          padding: '9px 12px', marginBottom: 16, fontSize: 12, color: '#1e40af', lineHeight: 1.5,
        }}>{hint}</div>
      )}

      <FormLabel>Name</FormLabel>
      <input value={name} onChange={(e) => setName(e.target.value)} style={fieldStyle}
             placeholder="e.g. EL140 nightly compliance" />

      <FormLabel>Description</FormLabel>
      <input value={description} onChange={(e) => setDescription(e.target.value)} style={fieldStyle}
             placeholder="Optional — what this job is for" />

      <FormLabel>Playbook</FormLabel>
      <select value={playbook} onChange={(e) => setPlaybook(e.target.value)}
              disabled={lockPlaybook} style={{ ...fieldStyle, background: lockPlaybook ? '#f8fafc' : '#fff' }}>
        {options.playbooks.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
      </select>
      {/* Spell out what choosing this playbook actually changes about a run —
          otherwise the dropdown reads as cosmetic. */}
      {(() => {
        const p = options.playbooks.find((x) => x.id === playbook);
        if (!p) return null;
        return (
          <div style={{
            marginTop: -8, marginBottom: 14, padding: '10px 12px',
            background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 8,
          }}>
            <div style={{ fontSize: 11, color: '#475569', lineHeight: 1.5 }}>{p.description}</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
              <Chip tone="blue">
                {p.endpoint_count === 'all'
                  ? 'walks all Redfish endpoints'
                  : `walks ${p.endpoint_count} Redfish endpoint${p.endpoint_count === 1 ? '' : 's'}`}
              </Chip>
              <Chip tone={p.raises_tickets ? 'amber' : 'slate'}>
                {p.raises_tickets ? 'raises tickets' : 'no tickets'}
              </Chip>
              <Chip tone={p.emits_report ? 'green' : 'slate'}>
                {p.emits_report ? 'certification report' : 'no report'}
              </Chip>
            </div>
          </div>
        );
      })()}

      <FormLabel>Target servers ({targets.length} selected)</FormLabel>
      <div style={{ border: '1px solid #e2e8f0', borderRadius: 10, maxHeight: 220, overflowY: 'auto', marginBottom: 14 }}>
        {orderedServers.map((s) => {
          const on = targets.includes(s.id);
          return (
            <label key={s.id} style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '9px 12px',
              borderBottom: '1px solid #f1f5f9', cursor: 'pointer',
              background: on ? '#f8fafc' : '#fff',
            }}>
              <input type="checkbox" checked={on} onChange={() => toggle(s.id)} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a', fontFamily: 'ui-monospace, monospace' }}>
                  {s.hostname || s.id}
                </div>
                <div style={{ fontSize: 10, color: '#94a3b8' }}>{s.platform}</div>
              </div>
              <StatusPill status={s.status} />
            </label>
          );
        })}
      </div>

      <FormLabel>Schedule</FormLabel>
      <select value={schedule} onChange={(e) => setSchedule(e.target.value)} style={fieldStyle}>
        {options.schedules.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
      </select>

      {error && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: 10, fontSize: 12, color: '#b91c1c', marginBottom: 12 }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 6 }}>
        <button style={smallBtn} onClick={onClose}>Cancel</button>
        <button className="btn btn-primary" onClick={submit} disabled={busy}>
          {busy ? 'Working…' : submitLabel}
        </button>
      </div>
    </Modal>
  );
}

function FormLabel({ children }: { children: React.ReactNode }) {
  return <div style={{ ...sectionLabel, marginTop: 4 }}>{children}</div>;
}

const fieldStyle: React.CSSProperties = {
  width: '100%', padding: '9px 12px', borderRadius: 8, border: '1px solid #cbd5e1',
  fontSize: 13, color: '#0f172a', background: '#fff', outline: 'none', marginBottom: 14,
};

function RunModal({ run, onClose, onEvidence }: {
  run: Run; onClose: () => void; onEvidence: (serverId: string) => void;
}) {
  const t = STATUS_TONE[run.status] || { bg: '#f1f5f9', fg: '#475569' };
  const allFindings = run.targets.flatMap((tg) =>
    tg.findings.map((f) => ({ ...f, hostname: tg.hostname || tg.server_id })));

  return (
    <Modal title={`Run · ${run.job_name}`} onClose={onClose} width={720}>
      <div style={{
        background: t.bg, border: `1px solid ${t.fg}22`, borderRadius: 12,
        padding: 14, marginBottom: 18,
      }}>
        <div style={{ fontSize: 15, fontWeight: 700, color: t.fg }}>{run.status}</div>
        <div style={{ fontSize: 12, color: '#475569', marginTop: 5 }}>
          {run.target_count} target{run.target_count === 1 ? '' : 's'} ·{' '}
          {run.total_requests} Redfish requests ·{' '}
          {run.total_findings} finding{run.total_findings === 1 ? '' : 's'}
        </div>
        {/* Make the playbook's effect legible: which endpoints it chose to walk. */}
        {run.playbook_label && (
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 7, lineHeight: 1.5 }}>
            <strong style={{ color: '#0f172a' }}>{run.playbook_label}</strong>
            {run.endpoints_walked === 'all'
              ? ' walked every Redfish endpoint.'
              : Array.isArray(run.endpoints_walked) && run.endpoints_walked.length === 0
                ? ' answers from the knowledge base and does not contact hardware.'
                : Array.isArray(run.endpoints_walked)
                  ? ` selected ${run.endpoints_walked.length} endpoint${run.endpoints_walked.length === 1 ? '' : 's'}: ${run.endpoints_walked.join(', ')}`
                  : ''}
          </div>
        )}
      </div>

      {run.targets.map((tg) => (
        <div key={tg.server_id} style={{
          border: '1px solid #e2e8f0', borderRadius: 10, padding: 14, marginBottom: 10,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, justifyContent: 'space-between' }}>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', fontFamily: 'ui-monospace, monospace' }}>
                {tg.hostname || tg.server_id}
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8' }}>
                {tg.platform} · {tg.requests} requests{tg.duration_ms ? ` · ${tg.duration_ms}ms` : ''}
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <StatusPill status={tg.status} />
              <button style={smallBtn} onClick={() => onEvidence(tg.server_id)}>Evidence</button>
            </div>
          </div>

          {tg.error && (
            <div style={{ fontSize: 11, color: '#b91c1c', marginTop: 8 }}>{tg.error}</div>
          )}

          {tg.findings.length > 0 && (
            <div style={{ marginTop: 10 }}>
              {tg.findings.map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start', padding: '5px 0' }}>
                  <StatusPill status={f.result} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: '#0f172a' }}>{f.step}</div>
                    <div style={{ fontSize: 10, color: '#64748b', lineHeight: 1.5 }}>{f.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {tg.findings.length === 0 && !tg.error && (
            <div style={{ fontSize: 11, color: '#15803d', marginTop: 8 }}>
              Matches the provisioning standard — nothing to remediate.
            </div>
          )}
        </div>
      ))}

      {run.emits_report && <CertificationReport runId={run.id} />}

      {allFindings.length > 0 && run.raises_tickets !== false && <JiraWriteBack runId={run.id} />}

      {allFindings.length > 0 && run.raises_tickets === false && (
        <div style={{
          marginTop: 6, padding: 14, borderRadius: 12,
          background: '#f8fafc', border: '1px solid #e2e8f0',
        }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#475569' }}>No tickets raised</div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 5, lineHeight: 1.5 }}>
            The <strong>{run.playbook_label}</strong> playbook reports findings for scoring only —
            a wave gate scores readiness rather than opening a backlog.
          </div>
          {/* Name the servers that actually have findings, so the next step is
              unambiguous — "this server" was wrong on a multi-target run. */}
          {(() => {
            const affected = run.targets
              .filter((t) => t.findings.length > 0)
              .map((t) => t.hostname || t.server_id);
            if (!affected.length) return null;
            return (
              <div style={{ fontSize: 11, color: '#475569', marginTop: 8, lineHeight: 1.6 }}>
                To raise tickets, run a <strong>Full certification cycle</strong> job against{' '}
                {affected.length === 1 ? 'this server' : `these ${affected.length} servers`}:
                <div style={{ marginTop: 4, fontFamily: 'ui-monospace, monospace', fontSize: 10, color: '#0f172a' }}>
                  {affected.map((h, i) => <div key={i}>· {h}</div>)}
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </Modal>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// certification report — shaped by the blueprint, not by this component
// ─────────────────────────────────────────────────────────────────────────────

interface ReportEnvelope {
  report: {
    header: Record<string, string | number>;
    executive_summary: Record<string, number>;
    failure_analysis: {
      test_id: string; category: string; severity: string;
      root_cause: string; recommendation: string; jira_ticket: string;
    }[];
    schema_drift_summary: {
      endpoint: string; change_type: string; scripts_impacted: string[];
      remediation_steps: string;
      observed: { field: string; current: string; expected: string }[];
    }[];
    deployment_recommendation: {
      overall_recommendation: string;
      conditions_to_proceed: string[];
      estimated_remediation_days: number;
    };
    governance_trail: Record<string, string[]>;
  };
  blueprint: { blueprint_name: string; blueprint_version: string; class: string; formats: string[] };
  conforms: boolean;
  missing_properties: string[];
}

function CertificationReport({ runId }: { runId: string }) {
  const [open, setOpen] = useState(false);

  const q = useQuery<ReportEnvelope>({
    queryKey: ['cert-report', runId],
    queryFn: () => api(`/jobs/runs/${runId}/report`),
    retry: false,
    enabled: open,
  });

  const REC_TONE: Record<string, { bg: string; fg: string }> = {
    proceed:     { bg: '#f0fdf4', fg: '#15803d' },
    conditional: { bg: '#fffbf5', fg: '#c2410c' },
    hold:        { bg: '#fef2f2', fg: '#b91c1c' },
  };

  return (
    <div style={{
      marginTop: 6, marginBottom: 10, padding: 14, borderRadius: 12,
      background: '#f8fafc', border: '1px solid #e2e8f0',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
        <div>
          <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a' }}>Certification report</div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 3, lineHeight: 1.5 }}>
            The canonical artifact shared with HQ Planning, shaped by the{' '}
            <code style={{ color: '#1d4ed8' }}>certification_report</code> blueprint.
          </div>
        </div>
        <button style={smallBtn} onClick={() => setOpen((v) => !v)}>
          {open ? 'Hide' : 'Generate'}
        </button>
      </div>

      {open && q.isLoading && (
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 10 }}>Rendering…</div>
      )}

      {open && q.isError && (
        <div style={{ fontSize: 11, color: '#b91c1c', marginTop: 10 }}>
          {String((q.error as Error)?.message)}
        </div>
      )}

      {open && q.data && (() => {
        const { report: r, blueprint, conforms, missing_properties } = q.data;
        const rec = r.deployment_recommendation;
        const tone = REC_TONE[rec.overall_recommendation] || REC_TONE.conditional;

        return (
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 10, color: '#94a3b8', marginBottom: 10 }}>
              {blueprint.blueprint_name} v{blueprint.blueprint_version} · {blueprint.class} ·{' '}
              <span style={{ color: conforms ? '#15803d' : '#c2410c', fontWeight: 700 }}>
                {conforms ? 'conforms to blueprint' : `missing: ${missing_properties.join(', ')}`}
              </span>
            </div>

            <ReportSection title="Header">
              {Object.entries(r.header).map(([k, v]) => (
                <KV key={k} k={k.replace(/_/g, ' ')} v={String(v)} />
              ))}
            </ReportSection>

            <ReportSection title="Executive summary">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(96px,1fr))', gap: 8 }}>
                {Object.entries(r.executive_summary).map(([k, v]) => (
                  <div key={k} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: '8px 10px' }}>
                    <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>{v}</div>
                    <div style={{ fontSize: 9, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.04em' }}>
                      {k.replace(/_/g, ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </ReportSection>

            {r.failure_analysis.length > 0 && (
              <ReportSection title={`Failure analysis (${r.failure_analysis.length})`}>
                {r.failure_analysis.map((f, i) => (
                  <div key={i} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 10, marginBottom: 6 }}>
                    <div style={{ display: 'flex', gap: 7, alignItems: 'center', flexWrap: 'wrap' }}>
                      <Chip tone={f.severity === 'P1' ? 'amber' : 'slate'}>{f.severity}</Chip>
                      <Chip>{f.category}</Chip>
                      {f.jira_ticket && <Chip tone="green">{f.jira_ticket}</Chip>}
                    </div>
                    <div style={{ fontSize: 10, color: '#475569', marginTop: 6, lineHeight: 1.5 }}>{f.root_cause}</div>
                    {f.recommendation && (
                      <div style={{ fontSize: 10, color: '#15803d', marginTop: 4, lineHeight: 1.5 }}>
                        <strong>Fix: </strong>{f.recommendation}
                      </div>
                    )}
                  </div>
                ))}
              </ReportSection>
            )}

            {r.schema_drift_summary.length > 0 && (
              <ReportSection title={`Schema drift (${r.schema_drift_summary.length})`}>
                {r.schema_drift_summary.map((s, i) => (
                  <div key={i} style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8, padding: 10, marginBottom: 6 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#0f172a' }}>{s.endpoint}</div>
                    {s.observed?.map((o, j) => (
                      <div key={j} style={{ fontSize: 10, fontFamily: 'ui-monospace, monospace', marginTop: 5 }}>
                        <div style={{ color: '#64748b' }}>{o.field}</div>
                        <div style={{ color: '#b91c1c' }}>− {o.current}</div>
                        <div style={{ color: '#15803d' }}>+ {o.expected}</div>
                      </div>
                    ))}
                    {s.scripts_impacted?.length > 0 && (
                      <div style={{ fontSize: 10, color: '#1d4ed8', marginTop: 6, fontFamily: 'ui-monospace, monospace' }}>
                        impacted: {s.scripts_impacted.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </ReportSection>
            )}

            <ReportSection title="Deployment recommendation">
              <div style={{ background: tone.bg, borderRadius: 8, padding: 10 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: tone.fg, textTransform: 'uppercase' }}>
                  {rec.overall_recommendation}
                </div>
                {rec.conditions_to_proceed.map((c, i) => (
                  <div key={i} style={{ fontSize: 10, color: '#475569', marginTop: 4 }}>• {c}</div>
                ))}
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 6 }}>
                  Estimated remediation: {rec.estimated_remediation_days} day(s)
                </div>
              </div>
            </ReportSection>

            <ReportSection title="Governance trail">
              {Object.entries(r.governance_trail).map(([k, v]) => (
                <div key={k} style={{ marginBottom: 6 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '.04em' }}>
                    {k.replace(/_/g, ' ')}
                  </div>
                  {(v as string[]).length === 0
                    ? <div style={{ fontSize: 10, color: '#cbd5e1' }}>—</div>
                    : (v as string[]).map((line, i) => (
                        <div key={i} style={{ fontSize: 10, color: '#475569', lineHeight: 1.5 }}>• {line}</div>
                      ))}
                </div>
              ))}
            </ReportSection>
          </div>
        );
      })()}
    </div>
  );
}

function ReportSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid #e2e8f0' }}>
      <div style={{
        fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
        letterSpacing: '.06em', color: '#475569', marginBottom: 7,
      }}>{title}</div>
      {children}
    </div>
  );
}

function KV({ k, v }: { k: string; v: string }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, padding: '3px 0' }}>
      <span style={{ fontSize: 10, color: '#94a3b8', textTransform: 'capitalize' }}>{k}</span>
      <span style={{ fontSize: 10, color: '#0f172a', textAlign: 'right', wordBreak: 'break-word' }}>{v}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Jira write-back — preview, approve, create
// ─────────────────────────────────────────────────────────────────────────────

interface JiraIssue {
  summary: string; severity: string; category: string;
  hostname: string; result: string; root_cause: string; recommendation: string;
}

interface JiraPreview {
  run_id: string;
  count: number;
  issues: JiraIssue[];
  jira: { project_key?: string; mock_mode?: boolean; url?: string };
  already_created: { key: string; url: string; summary: string }[];
}

/**
 * The approval gate. The preview is fetched from the same composer the create
 * call uses, so the list an operator approves is exactly the list that gets
 * written — it cannot drift.
 */
function JiraWriteBack({ runId }: { runId: string }) {
  const [created, setCreated] = useState<{ key: string; url: string; summary: string }[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const preview = useQuery<JiraPreview>({
    queryKey: ['jira-preview', runId],
    queryFn: () => api(`/jobs/runs/${runId}/jira/preview`),
    retry: false,
  });

  const approve = async () => {
    setBusy(true);
    setError(null);
    try {
      const res = await api<{ created: { key: string; url: string; summary: string }[] }>(
        `/jobs/runs/${runId}/jira/create`, { method: 'POST' },
      );
      setCreated(res.created);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  if (preview.isLoading) {
    return <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 10 }}>Composing tickets…</div>;
  }
  if (preview.isError || !preview.data) {
    return (
      <div style={{ marginTop: 6, padding: 12, borderRadius: 10, background: '#fef2f2', border: '1px solid #fecaca', fontSize: 12, color: '#b91c1c' }}>
        Could not compose the ticket preview: {String((preview.error as Error)?.message || '')}
      </div>
    );
  }

  const p = preview.data;
  const done = created ?? p.already_created;

  if (done.length > 0) {
    return (
      <div style={{ marginTop: 6, padding: 14, borderRadius: 12, background: '#f0fdf4', border: '1px solid #bbf7d0' }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: '#15803d' }}>
          {done.length} ticket{done.length === 1 ? '' : 's'} raised
        </div>
        <div style={{ marginTop: 8, display: 'grid', gap: 5 }}>
          {done.map((t, i) => (
            <div key={i} style={{ fontSize: 11, color: '#166534' }}>
              <span style={{ fontWeight: 700, fontFamily: 'ui-monospace, monospace' }}>{t.key}</span>
              {' — '}{t.summary}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div style={{ marginTop: 6, padding: 14, borderRadius: 12, background: '#fffbf5', border: '1px solid #fed7aa' }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: '#c2410c' }}>
        {p.count} ticket{p.count === 1 ? '' : 's'} will be created in{' '}
        {p.jira.project_key || 'APEXVZ'}
        {p.jira.mock_mode && (
          <span style={{ marginLeft: 8, background: '#fef3c7', color: '#92400e', fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 999 }}>
            MOCK MODE
          </span>
        )}
      </div>
      <div style={{ fontSize: 11, color: '#9a3412', marginTop: 6, lineHeight: 1.5 }}>
        This is exactly what will be written. Nothing is raised until you approve.
      </div>

      <div style={{ marginTop: 10, display: 'grid', gap: 8 }}>
        {p.issues.map((it, i) => (
          <div key={i} style={{ background: '#fff', border: '1px solid #fed7aa', borderRadius: 8, padding: 10 }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <span style={{ background: '#fef2f2', color: '#b91c1c', fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 999 }}>
                {it.severity}
              </span>
              <span style={{ fontSize: 11, fontWeight: 700, color: '#0f172a' }}>{it.summary}</span>
            </div>
            {it.root_cause && (
              <div style={{ fontSize: 10, color: '#64748b', marginTop: 5, lineHeight: 1.5 }}>{it.root_cause}</div>
            )}
            {it.recommendation && (
              <div style={{ fontSize: 10, color: '#15803d', marginTop: 4, lineHeight: 1.5 }}>
                <strong>Fix: </strong>{it.recommendation}
              </div>
            )}
          </div>
        ))}
      </div>

      {error && (
        <div style={{ marginTop: 10, fontSize: 11, color: '#b91c1c' }}>{error}</div>
      )}

      <button
        onClick={approve}
        disabled={busy}
        className="btn btn-primary"
        style={{ width: '100%', marginTop: 12, opacity: busy ? 0.6 : 1 }}
      >
        {busy ? 'Creating…' : `Approve & write ${p.count} ticket${p.count === 1 ? '' : 's'} to Jira`}
      </button>
    </div>
  );
}
