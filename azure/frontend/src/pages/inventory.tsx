/**
 * Inventory — the real hardware Apex manages.
 *
 * Every server, check and firmware row here comes from the backend, which
 * serves the artifacts captured by the Far Edge certification campaigns.
 * There is deliberately NO hardcoded fallback: an unknown id renders "not
 * found", and a failed fetch renders an error. Showing one server's
 * configuration under another server's name would be worse than showing
 * nothing at all.
 *
 * Select a server to open the detail panel; "Interrogate via Redfish" walks
 * its BMC live-style in the Redfish console.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { RedfishConsole } from '@/components/Inventory/RedfishConsole';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002/api/v1';

// ─────────────────────────────────────────────────────────────────────────────
// types
// ─────────────────────────────────────────────────────────────────────────────

export interface CheckGap {
  ref: string;
  title: string;
  summary: string | null;
  fields: { field: string; current: string; expected: string }[];
  action: string | null;
  remediation_command: string | null;
}

export interface Check {
  category: string;
  step: string;
  result: string;
  detail: string;
  gap: CheckGap | null;
  source_file: string;
}

export interface ServerRow {
  id: string;
  bmc_ip: string;
  hostname: string | null;
  vendor: string;
  platform: string | null;
  bmc_type: string | null;
  bmc_firmware: string | null;
  bios_version: string | null;
  status: string;
  last_seen: string | null;
  open_findings: number;
  evidence_count: number;
  firmware_count: number;
  check_summary: { total: number; pass: number; warn: number; drift: number; fail: number };
  test_summary: { total: number; pass: number; deviation: number; partial: number; fail: number };
}

interface ServerDetail extends ServerRow {
  checks: Check[];
  firmware: { component: string; version: string; minimum: string; result: string }[];
  artifacts: { id: string; title: string; result: string | null; date: string | null }[];
  tests: { test_id: string; title: string; result: string; date: string | null }[];
  evidence_files: string[];
  processor?: string | null;
  memory?: string | null;
  chassis_model?: string | null;
}

interface Summary {
  servers: number;
  by_status: Record<string, number>;
  by_platform: Record<string, number>;
  open_findings: number;
  tests_executed: number;
  campaigns: number;
  redfish_endpoints: number;
  generated_at: string;
  provenance: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// styling helpers
// ─────────────────────────────────────────────────────────────────────────────

/** Status colours run worst-first so a bad server never reads as calm. */
const STATUS_STYLE: Record<string, { bg: string; fg: string; dot: string }> = {
  FAIL:                  { bg: '#fef2f2', fg: '#b91c1c', dot: '#dc2626' },
  DRIFT:                 { bg: '#fff7ed', fg: '#c2410c', dot: '#ea580c' },
  'PASS WITH DEVIATION': { bg: '#fefce8', fg: '#a16207', dot: '#ca8a04' },
  PASS:                  { bg: '#f0fdf4', fg: '#15803d', dot: '#16a34a' },
  WARN:                  { bg: '#fefce8', fg: '#a16207', dot: '#ca8a04' },
  UNKNOWN:               { bg: '#f8fafc', fg: '#64748b', dot: '#94a3b8' },
};

function statusStyle(s: string) {
  return STATUS_STYLE[s?.toUpperCase()] || STATUS_STYLE.UNKNOWN;
}

const VENDOR_ACCENT: Record<string, string> = {
  HPE: '#00b388',    // HPE green
  Dell: '#0076ce',   // Dell blue
};

function Pill({ children, tone = 'slate' }: { children: React.ReactNode; tone?: string }) {
  const tones: Record<string, { bg: string; fg: string }> = {
    slate: { bg: '#f1f5f9', fg: '#475569' },
    red:   { bg: '#fef2f2', fg: '#b91c1c' },
    amber: { bg: '#fff7ed', fg: '#c2410c' },
    green: { bg: '#f0fdf4', fg: '#15803d' },
    blue:  { bg: '#eff6ff', fg: '#1d4ed8' },
  };
  const t = tones[tone] || tones.slate;
  return (
    <span style={{
      background: t.bg, color: t.fg, fontSize: 11, fontWeight: 600,
      padding: '2px 8px', borderRadius: 999, whiteSpace: 'nowrap',
    }}>{children}</span>
  );
}

function toneForResult(r: string): string {
  const u = (r || '').toUpperCase();
  if (u === 'FAIL') return 'red';
  if (u === 'DRIFT') return 'amber';
  if (u === 'WARN') return 'amber';
  if (u.startsWith('PASS')) return 'green';
  return 'slate';
}

// ─────────────────────────────────────────────────────────────────────────────
// page
// ─────────────────────────────────────────────────────────────────────────────

export default function InventoryPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [vendorFilter, setVendorFilter] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [consoleOpen, setConsoleOpen] = useState(false);

  const detailPanelRef = useRef<HTMLDivElement | null>(null);

  const summaryQuery = useQuery<Summary>({
    queryKey: ['inventory', 'summary'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/inventory/summary`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    retry: false,
    staleTime: 30_000,
  });

  const listQuery = useQuery<{ servers: ServerRow[]; count: number }>({
    queryKey: ['inventory', 'servers'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/inventory/servers`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    retry: false,
    staleTime: 30_000,
  });

  const detailQuery = useQuery<ServerDetail>({
    queryKey: ['inventory', 'server', selectedId],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/inventory/servers/${encodeURIComponent(selectedId!)}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    enabled: !!selectedId,
    retry: false,
    staleTime: 30_000,
  });

  // Sticky panels anchor inside their grid cell, so on a long list the panel
  // can sit below the fold and a click looks like it did nothing. Pull it
  // into view whenever the selection changes. (CLAUDE.md sticky-panel rule.)
  useEffect(() => {
    if (!selectedId) return;
    detailPanelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [selectedId]);

  const servers = listQuery.data?.servers ?? [];

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return servers.filter((s) => {
      if (vendorFilter !== 'all' && s.vendor !== vendorFilter) return false;
      if (!q) return true;
      return [s.id, s.hostname, s.bmc_ip, s.platform, s.bmc_firmware, s.bios_version]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q));
    });
  }, [servers, vendorFilter, search]);

  const vendors = useMemo(
    () => Array.from(new Set(servers.map((s) => s.vendor))).sort(),
    [servers],
  );

  return (
    <>
      <Head><title>Inventory | APEX</title></Head>

      {/* ── header ─────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18, gap: 16, flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Inventory</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4, maxWidth: 720 }}>
            The physical servers Apex manages. Configuration is read from each BMC over{' '}
            <strong style={{ color: '#0f172a' }}>Redfish</strong> — not from a spreadsheet — so
            drift is detected against what the hardware actually reports.
          </p>
        </div>
        {summaryQuery.data && (
          <div style={{ fontSize: 11, color: '#94a3b8', textAlign: 'right' }}>
            <div>{summaryQuery.data.provenance}</div>
            <div>captured {String(summaryQuery.data.generated_at).slice(0, 10)}</div>
          </div>
        )}
      </div>

      {/* ── summary tiles ──────────────────────────────────────────────── */}
      {summaryQuery.data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12, marginBottom: 22 }}>
          <Tile label="Servers"           value={summaryQuery.data.servers} />
          <Tile label="Open findings"     value={summaryQuery.data.open_findings}
                tone={summaryQuery.data.open_findings > 0 ? 'amber' : 'green'} />
          <Tile label="Tests executed"    value={summaryQuery.data.tests_executed} />
          <Tile label="Redfish endpoints" value={summaryQuery.data.redfish_endpoints} />
          <Tile label="Campaigns"         value={summaryQuery.data.campaigns} />
        </div>
      )}

      {/* ── filters ────────────────────────────────────────────────────── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18, flexWrap: 'wrap' }}>
        <div className="tab-bar" style={{ width: 'fit-content' }}>
          <FilterBtn active={vendorFilter === 'all'} onClick={() => setVendorFilter('all')}>
            All ({servers.length})
          </FilterBtn>
          {vendors.map((v) => (
            <FilterBtn key={v} active={vendorFilter === v} onClick={() => setVendorFilter(v)}>
              {v} ({servers.filter((s) => s.vendor === v).length})
            </FilterBtn>
          ))}
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search hostname, BMC address, platform, firmware…"
          style={{
            flex: 1, minWidth: 260, padding: '8px 14px', borderRadius: 10,
            border: '1px solid #e2e8f0', fontSize: 13, color: '#0f172a',
            background: '#fff', outline: 'none',
          }}
        />
      </div>

      {/* ── list + detail ──────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 20, alignItems: 'start' }}>
        <div>
          {listQuery.isLoading && <Skeleton rows={4} />}

          {listQuery.isError && (
            <ErrorBox
              title="Could not load the inventory"
              detail={String((listQuery.error as Error)?.message || '')}
              hint="Is the backend running on this port? Nothing is shown rather than risk showing the wrong hardware."
            />
          )}

          {listQuery.isSuccess && filtered.length === 0 && (
            <EmptyBox
              title={servers.length === 0 ? 'No servers in inventory' : 'No servers match this filter'}
              detail={
                servers.length === 0
                  ? 'Run scripts/extract_hw_inventory.py to ingest the lab campaign artifacts.'
                  : 'Try clearing the search or switching vendor.'
              }
            />
          )}

          <div style={{ display: 'grid', gap: 10 }}>
            {filtered.map((s) => (
              <ServerCard
                key={s.id}
                s={s}
                selected={s.id === selectedId}
                onSelect={() => setSelectedId(s.id)}
              />
            ))}
          </div>
        </div>

        {/* scrollMarginTop keeps the sticky topbar from covering the panel header */}
        <div ref={detailPanelRef} style={{ position: 'sticky', top: 80, scrollMarginTop: 80 }}>
          <DetailPanel
            selectedId={selectedId}
            query={detailQuery}
            onInterrogate={() => setConsoleOpen(true)}
          />
        </div>
      </div>

      {consoleOpen && selectedId && (
        <RedfishConsole
          serverId={selectedId}
          onClose={() => setConsoleOpen(false)}
        />
      )}
    </>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// pieces
// ─────────────────────────────────────────────────────────────────────────────

function Tile({ label, value, tone = 'slate' }: { label: string; value: React.ReactNode; tone?: string }) {
  const fg = tone === 'amber' ? '#c2410c' : tone === 'green' ? '#15803d' : '#0f172a';
  return (
    <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: '14px 16px' }}>
      <div style={{ fontSize: 24, fontWeight: 700, color: fg, lineHeight: 1.1 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, textTransform: 'uppercase', letterSpacing: '.05em' }}>{label}</div>
    </div>
  );
}

function FilterBtn({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '7px 14px', fontSize: 13, fontWeight: 600, borderRadius: 8,
        border: '1px solid ' + (active ? '#0f172a' : '#e2e8f0'),
        background: active ? '#0f172a' : '#fff',
        color: active ? '#fff' : '#475569',
        cursor: 'pointer',
      }}
    >{children}</button>
  );
}

function ServerCard({ s, selected, onSelect }: { s: ServerRow; selected: boolean; onSelect: () => void }) {
  const st = statusStyle(s.status);
  const accent = VENDOR_ACCENT[s.vendor] || '#94a3b8';

  return (
    <button
      onClick={onSelect}
      style={{
        textAlign: 'left', width: '100%', cursor: 'pointer',
        background: '#fff',
        border: '1px solid ' + (selected ? '#0f172a' : '#e2e8f0'),
        boxShadow: selected ? '0 0 0 3px rgba(15,23,42,.06)' : 'none',
        borderRadius: 12, padding: 0, overflow: 'hidden',
        display: 'grid', gridTemplateColumns: '4px 1fr',
      }}
    >
      <div style={{ background: accent }} />
      <div style={{ padding: '14px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', fontFamily: 'ui-monospace, monospace' }}>
            {s.hostname || s.id}
          </div>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: st.bg, color: st.fg, fontSize: 11, fontWeight: 700,
            padding: '3px 10px', borderRadius: 999,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: 999, background: st.dot }} />
            {s.status}
          </span>
        </div>

        <div style={{ fontSize: 12, color: '#64748b', marginTop: 5 }}>{s.platform}</div>

        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, fontFamily: 'ui-monospace, monospace' }}>
          {s.bmc_ip}
        </div>

        <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
          {s.bmc_type && <Pill tone="blue">{s.bmc_type} {s.bmc_firmware?.replace(/^iLO 7\s*/, '')}</Pill>}
          {s.bios_version && <Pill>BIOS {s.bios_version}</Pill>}
          {s.open_findings > 0
            ? <Pill tone="amber">{s.open_findings} finding{s.open_findings === 1 ? '' : 's'}</Pill>
            : <Pill tone="green">no findings</Pill>}
          {s.check_summary?.total > 0 && <Pill>{s.check_summary.total} checks</Pill>}
          {s.test_summary?.total > 0 && <Pill>{s.test_summary.total} tests</Pill>}
        </div>
      </div>
    </button>
  );
}

function DetailPanel({
  selectedId, query, onInterrogate,
}: {
  selectedId: string | null;
  query: { data?: ServerDetail; isLoading: boolean; isError: boolean; error: unknown };
  onInterrogate: () => void;
}) {
  const box: React.CSSProperties = {
    background: '#fff', border: '1px solid #e2e8f0', borderRadius: 12, padding: 18,
  };

  if (!selectedId) {
    return (
      <div style={{ ...box, textAlign: 'center', padding: '40px 20px' }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>Select a server</div>
        <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 6, lineHeight: 1.5 }}>
          Its configuration, compliance checks and firmware inventory appear here.
        </div>
      </div>
    );
  }

  if (query.isLoading) return <div style={box}><Skeleton rows={3} /></div>;

  if (query.isError) {
    return (
      <div style={box}>
        <ErrorBox
          title="Could not load this server"
          detail={String((query.error as Error)?.message || '')}
          hint="Nothing is substituted — a different server's data here would be misleading."
        />
      </div>
    );
  }

  const s = query.data;
  if (!s) return null;

  const st = statusStyle(s.status);
  const findings = (s.checks || []).filter((c) => ['DRIFT', 'WARN', 'FAIL'].includes(c.result));

  const byCategory = (s.checks || []).reduce<Record<string, Check[]>>((acc, c) => {
    (acc[c.category] ||= []).push(c);
    return acc;
  }, {});

  return (
    <div style={{ ...box, maxHeight: 'calc(100vh - 120px)', overflowY: 'auto' }}>
      {/* identity */}
      <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', fontFamily: 'ui-monospace, monospace', wordBreak: 'break-all' }}>
        {s.hostname || s.id}
      </div>
      <div style={{ fontSize: 12, color: '#64748b', marginTop: 3 }}>{s.platform}</div>

      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 6, marginTop: 10,
        background: st.bg, color: st.fg, fontSize: 11, fontWeight: 700,
        padding: '4px 10px', borderRadius: 999,
      }}>
        <span style={{ width: 6, height: 6, borderRadius: 999, background: st.dot }} />
        {s.status}
      </div>

      <button
        onClick={onInterrogate}
        className="btn btn-primary"
        style={{ width: '100%', marginTop: 14, marginBottom: 4 }}
      >
        Interrogate via Redfish
      </button>

      <Field label="BMC address" value={s.bmc_ip} mono />
      <Field label="BMC firmware" value={s.bmc_firmware} />
      <Field label="BIOS" value={s.bios_version} />
      {s.processor && <Field label="Processor" value={s.processor} />}
      {s.memory && <Field label="Memory" value={s.memory} />}
      {s.chassis_model && <Field label="Chassis" value={s.chassis_model} />}
      <Field label="Last verified" value={s.last_seen} />

      {/* findings first — this is what an operator acts on */}
      {findings.length > 0 && (
        <Section title={`Needs action (${findings.length})`}>
          {/* Handoff: turn what we just found into scheduled work, with the
              target and a descriptive name already filled in. */}
          <Link
            href={{
              pathname: '/jobs',
              query: {
                server: s.id,
                name: `Remediate ${s.hostname || s.id}`,
              },
            }}
            style={{
              display: 'block', textAlign: 'center', textDecoration: 'none',
              background: '#c2410c', color: '#fff', fontSize: 12, fontWeight: 700,
              padding: '9px 12px', borderRadius: 8, marginBottom: 12,
            }}
          >
            Create job from findings →
          </Link>

          {findings.map((c, i) => (
            <div key={i} style={{
              border: '1px solid #fed7aa', background: '#fffbf5',
              borderRadius: 10, padding: 12, marginBottom: 8,
            }}>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
                <Pill tone={toneForResult(c.result)}>{c.result}</Pill>
                <span style={{ fontSize: 12, fontWeight: 700, color: '#0f172a' }}>{c.step}</span>
              </div>
              <div style={{ fontSize: 11, color: '#475569', lineHeight: 1.5 }}>{c.detail}</div>

              {c.gap?.fields?.length ? (
                <div style={{ marginTop: 8, display: 'grid', gap: 4 }}>
                  {c.gap.fields.map((f, j) => (
                    <div key={j} style={{ fontSize: 10, fontFamily: 'ui-monospace, monospace' }}>
                      <div style={{ color: '#64748b' }}>{f.field}</div>
                      <div style={{ color: '#b91c1c' }}>− {f.current}</div>
                      <div style={{ color: '#15803d' }}>+ {f.expected}</div>
                    </div>
                  ))}
                </div>
              ) : null}

              {c.gap?.action && (
                <div style={{ fontSize: 11, color: '#0f172a', marginTop: 8, lineHeight: 1.5 }}>
                  <strong>Action: </strong>{c.gap.action}
                </div>
              )}
              {c.gap?.remediation_command && (
                <pre style={{
                  marginTop: 8, background: '#0f172a', color: '#e2e8f0',
                  fontSize: 10, padding: 10, borderRadius: 8, overflowX: 'auto',
                  fontFamily: 'ui-monospace, monospace', lineHeight: 1.5,
                }}>{c.gap.remediation_command}</pre>
              )}
            </div>
          ))}
        </Section>
      )}

      {/* all checks, grouped as the engineers grouped them */}
      {Object.keys(byCategory).length > 0 && (
        <Section title={`Compliance checks (${s.checks.length})`}>
          {Object.entries(byCategory).map(([cat, checks]) => (
            <div key={cat} style={{ marginBottom: 10 }}>
              <div style={{
                fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                letterSpacing: '.06em', color: '#94a3b8', marginBottom: 5,
              }}>{cat}</div>
              {checks.map((c, i) => (
                <div key={i} style={{
                  display: 'flex', gap: 8, alignItems: 'flex-start',
                  padding: '5px 0', borderBottom: '1px solid #f1f5f9',
                }}>
                  <Pill tone={toneForResult(c.result)}>{c.result}</Pill>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 11, fontWeight: 600, color: '#0f172a' }}>{c.step}</div>
                    <div style={{ fontSize: 10, color: '#94a3b8', lineHeight: 1.4 }}>{c.detail}</div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </Section>
      )}

      {s.firmware?.length > 0 && (
        <Section title={`Firmware inventory (${s.firmware.length})`}>
          {s.firmware.map((f, i) => (
            <div key={i} style={{
              display: 'flex', justifyContent: 'space-between', gap: 8,
              padding: '4px 0', borderBottom: '1px solid #f1f5f9', fontSize: 11,
            }}>
              <span style={{ color: '#475569' }}>{f.component}</span>
              <span style={{ color: '#0f172a', fontFamily: 'ui-monospace, monospace' }}>{f.version}</span>
            </div>
          ))}
        </Section>
      )}

      {s.tests?.length > 0 && (
        <Section title={`Certification tests (${s.tests.length})`}>
          {s.tests.slice(0, 12).map((t, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '4px 0' }}>
              <Pill tone={toneForResult(t.result)}>{t.result}</Pill>
              <span style={{ fontSize: 11, color: '#475569', fontFamily: 'ui-monospace, monospace' }}>{t.test_id}</span>
            </div>
          ))}
          {s.tests.length > 12 && (
            <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 6 }}>
              + {s.tests.length - 12} more
            </div>
          )}
        </Section>
      )}

      {s.evidence_files?.length > 0 && (
        <Section title={`Evidence (${s.evidence_files.length} files)`}>
          <div style={{ fontSize: 10, color: '#94a3b8', lineHeight: 1.6, fontFamily: 'ui-monospace, monospace' }}>
            {s.evidence_files.slice(0, 8).join(', ')}
            {s.evidence_files.length > 8 && ` … +${s.evidence_files.length - 8}`}
          </div>
        </Section>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginTop: 18, paddingTop: 14, borderTop: '1px solid #e2e8f0' }}>
      <div style={{
        fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
        letterSpacing: '.06em', color: '#475569', marginBottom: 10,
      }}>{title}</div>
      {children}
    </div>
  );
}

function Field({ label, value, mono }: { label: string; value?: string | null; mono?: boolean }) {
  if (!value) return null;
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, padding: '6px 0', borderBottom: '1px solid #f1f5f9' }}>
      <span style={{ fontSize: 11, color: '#94a3b8' }}>{label}</span>
      <span style={{
        fontSize: 11, color: '#0f172a', textAlign: 'right', wordBreak: 'break-all',
        fontFamily: mono ? 'ui-monospace, monospace' : undefined,
      }}>{value}</span>
    </div>
  );
}

function Skeleton({ rows }: { rows: number }) {
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} style={{
          height: 92, background: 'linear-gradient(90deg,#f8fafc,#f1f5f9,#f8fafc)',
          borderRadius: 12, border: '1px solid #e2e8f0',
        }} />
      ))}
    </div>
  );
}

function ErrorBox({ title, detail, hint }: { title: string; detail?: string; hint?: string }) {
  return (
    <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 12, padding: 16 }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: '#b91c1c' }}>{title}</div>
      {detail && <div style={{ fontSize: 11, color: '#b91c1c', marginTop: 4, fontFamily: 'ui-monospace, monospace' }}>{detail}</div>}
      {hint && <div style={{ fontSize: 11, color: '#7f1d1d', marginTop: 8, lineHeight: 1.5 }}>{hint}</div>}
    </div>
  );
}

function EmptyBox({ title, detail }: { title: string; detail: string }) {
  return (
    <div style={{ background: '#f8fafc', border: '1px dashed #cbd5e1', borderRadius: 12, padding: 28, textAlign: 'center' }}>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#475569' }}>{title}</div>
      <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 6 }}>{detail}</div>
    </div>
  );
}
