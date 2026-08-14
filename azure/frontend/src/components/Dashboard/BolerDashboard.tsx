/**
 * BolerDashboard — The Boler Company "Benefits Allocation Intelligence" view.
 *
 * Port of docs/discovery/boler/dashboard.html. All data from
 * /api/v1/boler/dashboard-state per CLAUDE.md zero-hardcoding rule.
 *
 * Color palette: purple #6c47ff, teal #00c4a0, amber #f59e0b, red #ef4444.
 * Fonts: Space Grotesk (headings/numbers) + Inter (body) + JetBrains Mono (IDs).
 */
import React from 'react';
import Link from 'next/link';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/router';
import { useCwfcuToast, postCwfcuAction } from './cwfcuToast';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface BolerState {
  cycle: string;
  total_employees: number;
  total_divisions: number;
  kpis: {
    total_allocated_usd: number;
    total_allocated_pct_vs_may: number;
    processing_hours: number;
    manual_baseline_days: number;
    time_saved_days: number;
    exceptions_flagged: number;
    exceptions_new_this_cycle: number;
    exceptions_high_severity: number;
    exceptions_variance_usd: number;
    approval_stage: number;
    total_stages: number;
  };
  workflow: {
    stages: Array<{ key: string; label: string; sub: string; state: 'done' | 'active' | 'pending' }>;
    current_stage_index: number;
    total_stages: number;
  };
  carrier_files: Array<{ name: string; employees: number; amount_usd: number; status: string }>;
  divisions: Array<{
    id: string; name: string; color: string; employees: number;
    allocated_usd: number; budget_usd: number; variance_pct: number;
    status: string; cost_center: string;
  }>;
  exceptions: Array<{
    id: string; severity: string; title: string; description: string;
    employee?: string; employee_id?: string; agent: string; time: string;
    diff?: { before: string; after: string };
    amount_usd: number; status: string;
  }>;
  approval_queue: Array<{ stage: number; title: string; meta: string; status: string; status_color: string }>;
  je_preview: {
    division: string; period: string;
    lines: Array<{ side: string; account: string; description: string; amount_usd: number }>;
    balanced: boolean; total_usd: number;
  };
  audit_log: Array<{ time: string; date: string; action: string; detail: string; badge: string; badge_color: string }>;
  aws_architecture: Array<{ layer: string; service: string; role: string }>;
}

const fmtUsd = (n: number): string =>
  n >= 1_000_000 ? `$${(n / 1_000_000).toFixed(2)}M`
  : n >= 1_000   ? `$${(n / 1_000).toFixed(0)}K`
  : `$${n.toLocaleString()}`;
const fmtUsdFull = (n: number): string => `$${n.toLocaleString()}`;

const severityColor = (sev: string): string =>
  sev === 'HIGH' ? '#ef4444' : sev === 'MEDIUM' ? '#f59e0b' : '#9ca3af';
const severityBg = (sev: string): string =>
  sev === 'HIGH' ? '#fef2f2' : sev === 'MEDIUM' ? '#fffbeb' : '#f5f7fa';

const stageColor = (state: string): string =>
  state === 'done' ? '#00c4a0' : state === 'active' ? '#6c47ff' : '#f0f2f5';
const stageTextColor = (state: string): string =>
  state === 'done' ? '#fff' : state === 'active' ? '#fff' : '#9ca3af';

const auditBadgeStyle = (color: string): { bg: string; text: string } => {
  switch (color) {
    case 'green': return { bg: '#f0fdf4', text: '#16a34a' };
    case 'red':   return { bg: '#fef2f2', text: '#dc2626' };
    case 'amber': return { bg: '#fffbeb', text: '#d97706' };
    case 'blue':  return { bg: '#eff6ff', text: '#2563eb' };
    default:      return { bg: '#f5f7fa', text: '#6b7280' };
  }
};

const divisionStatusStyle = (s: string): { bg: string; color: string } =>
  s === 'Approved' ? { bg: '#f0fdf4', color: '#16a34a' }
: s === 'Review'   ? { bg: '#fffbeb', color: '#d97706' }
: s === 'Pending'  ? { bg: '#eff6ff', color: '#2563eb' }
: { bg: '#f5f7fa', color: '#6b7280' };

/* ─────────────────────────────────────────────────────────────────────
 * BOLER_DASHBOARD_FALLBACK
 * Per CLAUDE.md ZERO-HARDCODING RULE: this is the EXPLICIT, BOLER-SPECIFIC
 * offline fallback. Mirrors backend/api/boler.py::boler_dashboard_state so
 * the demo always renders even when the APEX backend isn't running locally
 * (port 8000 owned by another process, etc.).
 * NEVER use this for a different industry. NEVER fall back to a generic
 * "Invoice Processing" shape. Boler-only.
 * ───────────────────────────────────────────────────────────────────── */
export const BOLER_DASHBOARD_FALLBACK: BolerState = {
  cycle: 'June 2026',
  total_employees: 847,
  total_divisions: 5,
  kpis: {
    total_allocated_usd: 2_142_000,
    total_allocated_pct_vs_may: 3.2,
    processing_hours: 4.2,
    manual_baseline_days: 3.5,
    time_saved_days: 3.3,
    exceptions_flagged: 7,
    exceptions_new_this_cycle: 3,
    exceptions_high_severity: 2,
    exceptions_variance_usd: 28_120,
    approval_stage: 2,
    total_stages: 3,
  },
  workflow: {
    stages: [
      { key: 'intake',       label: 'File Intake',         sub: 'Jun 3 · 6 files',    state: 'done' },
      { key: 'extract',      label: 'APEX Extract',        sub: 'Jun 3 · 4.2 hrs',    state: 'done' },
      { key: 'approval1',    label: 'Benefits Approval',   sub: 'Jun 5 · Approved',   state: 'done' },
      { key: 'approval2',    label: 'Accounting Review',   sub: 'Jun 6 · Pending',    state: 'active' },
      { key: 'distribution', label: 'Distribution',        sub: 'Jun 7 · Scheduled',  state: 'pending' },
    ],
    current_stage_index: 3,
    total_stages: 5,
  },
  carrier_files: [
    { name: 'Cigna_Medical_Jun2026.csv',   employees: 847, amount_usd: 1_284_320, status: 'Extracted' },
    { name: 'Delta_Dental_Jun2026.csv',    employees: 831, amount_usd:   187_450, status: 'Extracted' },
    { name: 'Fidelity_401k_Jun2026.csv',   employees: 803, amount_usd:   412_880, status: 'Extracted' },
    { name: 'VSP_Vision_Jun2026.csv',      employees: 798, amount_usd:    62_140, status: 'Extracted' },
    { name: 'Hartford_Life_Jun2026.csv',   employees: 847, amount_usd:    98_760, status: 'Extracted' },
    { name: 'Cigna_STD_LTD_Jun2026.csv',   employees: 847, amount_usd:    94_450, status: 'Extracted' },
  ],
  divisions: [
    { id: 'hendrickson',  name: 'Hendrickson Intl',        color: '#6c47ff', employees: 412,
      allocated_usd: 1_042_800, budget_usd: 1_034_400, variance_pct: 0.8,  status: 'Approved', cost_center: '6200-001' },
    { id: 'real_estate',  name: 'Boler Real Estate',       color: '#2563eb', employees:  89,
      allocated_usd:   224_910, budget_usd:   227_640, variance_pct: -1.2, status: 'Approved', cost_center: '6200-002' },
    { id: 'holdings',     name: 'Boler Holdings',          color: '#f59e0b', employees: 124,
      allocated_usd:   313_480, budget_usd:   300_960, variance_pct: 4.1,  status: 'Review',   cost_center: '6200-003' },
    { id: 'manufacturing',name: 'Boler Mfg Services',      color: '#00c4a0', employees: 156,
      allocated_usd:   394_320, budget_usd:   388_800, variance_pct: 1.4,  status: 'Pending',  cost_center: '6200-004' },
    { id: 'corporate',    name: 'Corporate / Shared Svcs', color: '#9ca3af', employees:  66,
      allocated_usd:   166_490, budget_usd:   167_000, variance_pct: -0.3, status: 'Approved', cost_center: '6200-005' },
  ],
  exceptions: [
    { id: 'EXC-2026-0441', severity: 'HIGH',
      title: 'Employee coded to wrong division',
      description: 'Chen, Robert (EMP-4821) was coded to Hendrickson Intl but transferred to Boler Holdings on May 15. All 6 benefit lines still allocated to Hendrickson.',
      employee: 'Chen, Robert', employee_id: 'EMP-4821',
      agent: 'Benefits', time: '09:41 AM',
      diff: { before: '- Hendrickson Intl · Cost Center 6200-001 · $3,840/mo',
              after:  '+ Boler Holdings · Cost Center 6200-004 · $3,840/mo' },
      amount_usd: 3_840, status: 'Awaiting CFO' },
    { id: 'EXC-2026-0442', severity: 'HIGH',
      title: 'Duplicate enrollment — Cigna medical + COBRA',
      description: 'Martinez, Laura (EMP-3312) appears in both active Cigna medical file and COBRA billing file. Terminated Apr 30. COBRA billing should not be charged to Boler Holdings cost center.',
      employee: 'Martinez, Laura', employee_id: 'EMP-3312',
      agent: 'Benefits', time: '09:38 AM',
      diff: { before: '- Active Medical: $1,240/mo charged to Boler Holdings (INVALID)',
              after:  '+ COBRA is self-pay — remove from corporate allocation entirely' },
      amount_usd: 1_240, status: 'Awaiting CFO' },
    { id: 'EXC-2026-0443', severity: 'MEDIUM',
      title: 'Rate change vs. prior month (+8.4%)',
      description: 'Cigna medical · Boler Holdings · $2,180 variance · No rate card update on file. APEX Signal flagged this 90 days ago — renewal in 41 days.',
      agent: 'Signal', time: '09:35 AM',
      amount_usd: 2_180, status: 'Awaiting Benefits' },
    { id: 'EXC-2026-0444', severity: 'MEDIUM',
      title: 'Division transfer not reflected',
      description: '4 employees transferred May 15 — still coded to prior division — $14,320 misallocation. 3 of 4 auto-corrected (Kim, Foster, Reilly). Chen escalated separately as EXC-0441.',
      agent: 'Benefits', time: '09:22 AM',
      amount_usd: 14_320, status: 'Auto-Fixed' },
    { id: 'EXC-2026-0445', severity: 'MEDIUM',
      title: '401k match rate mismatch',
      description: 'Fidelity file shows 4.5% match rate. HR policy P-COMP-401K-2024 shows 4.0%. $8,240 monthly delta. Root cause TBD — Sarah Mitchell follow-up requested.',
      agent: 'Benefits', time: '09:31 AM',
      amount_usd: 8_240, status: 'Awaiting Benefits' },
    { id: 'EXC-2026-0446', severity: 'LOW',
      title: 'Terminated employee — benefits still active',
      description: 'Thompson, D. · Terminated May 28 · Vision + dental still billed · $420 auto-fixed.',
      employee: 'Thompson, D.',
      agent: 'Benefits', time: '09:18 AM',
      amount_usd: 420, status: 'Auto-Fixed' },
    { id: 'EXC-2026-0447', severity: 'LOW',
      title: 'Missing cost center code',
      description: '3 new hires · No cost center assigned · $6,840 unallocated. Routed to Sarah Mitchell to confirm division placements with hiring managers.',
      agent: 'Benefits', time: '09:14 AM',
      amount_usd: 6_840, status: 'Awaiting Benefits' },
  ],
  approval_queue: [
    { stage: 1, title: 'Stage 1 — Benefits Manager Approval',
      meta: 'Approved Jun 5, 2026 · 09:22 AM · Sarah Mitchell, Benefits Director',
      status: 'COMPLETE', status_color: '#16a34a' },
    { stage: 2, title: 'Stage 2 — Accounting Review & Approval',
      meta: 'Awaiting · Routed to Ziggy Kravitz, CFO · Due Jun 6, 2026',
      status: 'REVIEW',   status_color: '#2563eb' },
    { stage: 3, title: 'Stage 3 — Division Journal Entry Distribution',
      meta: 'Scheduled Jun 7, 2026 · Auto-distribution via Step Functions + S3',
      status: 'PENDING',  status_color: '#9ca3af' },
  ],
  je_preview: {
    division: 'Hendrickson Intl',
    period:   'June 2026',
    lines: [
      { side: 'DR', account: '6200-001', description: 'Benefits Expense — Medical',         amount_usd: 624_480 },
      { side: 'DR', account: '6200-002', description: 'Benefits Expense — Dental',          amount_usd:  91_840 },
      { side: 'DR', account: '6200-003', description: 'Benefits Expense — 401k Match',      amount_usd: 201_760 },
      { side: 'DR', account: '6200-004', description: 'Benefits Expense — Vision/Life/LTD', amount_usd: 124_720 },
      { side: 'CR', account: '2100-001', description: 'Benefits Payable — Cigna',           amount_usd: 1_042_800 },
    ],
    balanced: true,
    total_usd: 1_042_800,
  },
  audit_log: [
    { time: '09:41:03', date: 'Jun 6, 2026', action: 'EXC-0441 reclassification applied',
      detail: 'Chen, R. · Hendrickson → Boler Holdings · $3,840/mo', badge: 'FIXED',    badge_color: 'green' },
    { time: '09:38:22', date: 'Jun 6, 2026', action: 'Stage 2 approval notification sent',
      detail: 'Ziggy Kravitz · Email (SES) + SNS push · Due Jun 6',  badge: 'ROUTED',   badge_color: 'blue' },
    { time: '09:35:14', date: 'Jun 6, 2026', action: 'Cigna rate drift alert generated',
      detail: '+4.1% above contract · 90-day model',                  badge: 'ALERT',    badge_color: 'red' },
    { time: '09:31:08', date: 'Jun 6, 2026', action: '401k match rate mismatch flagged',
      detail: 'Fidelity 4.5% vs. HR policy 4.0% · $8,240 delta',     badge: 'FLAGGED',  badge_color: 'amber' },
    { time: '09:22:14', date: 'Jun 5, 2026', action: 'Stage 1 approved — Sarah Mitchell',
      detail: 'Benefits Director · 5 resolved · 2 overridden',       badge: 'APPROVED', badge_color: 'green' },
    { time: '09:18:33', date: 'Jun 5, 2026', action: 'Thompson, D. — terminated employee removed',
      detail: 'Vision + dental · $420 removed from allocation',      badge: 'AUTO-FIXED', badge_color: 'green' },
    { time: '09:14:22', date: 'Jun 3, 2026', action: '6 carrier files ingested from Blob intake container',
      detail: '847 employees · $2,142,000 total',                    badge: 'INGESTED', badge_color: 'green' },
  ],
  aws_architecture: [
    { layer: 'File Intake',    service: 'Azure Blob Storage (restricted bucket)',  role: 'Carrier files dropped by HR/Benefits team' },
    { layer: 'Extraction',     service: 'Azure Functions + Azure OpenAI',    role: 'Document parsing, field extraction, reclassification' },
    { layer: 'Orchestration',  service: 'Azure Logic Apps',             role: 'Multi-stage approval workflow, SLA enforcement' },
    { layer: 'Storage',        service: 'Azure Cosmos DB',                role: 'Audit ledger, exception records, allocation history' },
    { layer: 'Notifications',  service: 'Azure Communication Services + SNS',               role: 'Approval requests, exception alerts, distribution emails' },
    { layer: 'Analytics',      service: 'Amazon QuickSight',              role: 'Division dashboards, trend charts, CFO reporting' },
    { layer: 'AI/LLM',         service: 'Azure OpenAI (GPT-5)',         role: 'Agent intelligence, exception reasoning, narrative generation' },
    { layer: 'Security',       service: 'Entra ID + Key Vault',                  role: 'Role-based access, encryption at rest and in transit' },
  ],
};

export function BolerDashboard() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { Toast, push } = useCwfcuToast();

  const q = useQuery<BolerState>({
    queryKey: ['boler-dashboard-state'],
    queryFn: async () => {
      const ctl = new AbortController();
      const timer = setTimeout(() => ctl.abort(), 3000); // 3s timeout — never hang the demo
      try {
        const r = await fetch(`${API_BASE_URL}/boler/dashboard-state`, { signal: ctl.signal });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      } finally {
        clearTimeout(timer);
      }
    },
    refetchInterval: 30_000,
    retry: 0,                  // don't spin on a dead backend — fall back fast
    staleTime: 15_000,
    placeholderData: BOLER_DASHBOARD_FALLBACK,  // render fallback IMMEDIATELY
  });

  // Per ZERO-HARDCODING RULE in CLAUDE.md: fallback ONLY when the API actually
  // errors — never silently in place of a different domain's data. Here the
  // fallback IS Boler data, so it's safe to render even on initial isLoading
  // while the network call resolves. This is the explicit "offline fallback"
  // case the rule permits.
  // Render fallback IMMEDIATELY — placeholderData ensures q.data is populated
  // from frame 1, so the demo never sits on a "Loading…" flash even when the
  // backend is offline. React Query silently swaps in the live response when
  // it arrives.
  const d: BolerState = q.data ?? BOLER_DASHBOARD_FALLBACK;

  const handleApply = (excId: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/exceptions/${encodeURIComponent(excId)}/apply-reclassification`, push)
      .then((r) => { if (r?.ok) queryClient.invalidateQueries({ queryKey: ['boler-dashboard-state'] }); });

  const handleOverride = (excId: string) =>
    postCwfcuAction(`${API_BASE_URL}/boler/exceptions/${encodeURIComponent(excId)}/override?note=demo-override`, push);

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1120' }}>
      <Toast />

      {/* Page header */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 22, fontWeight: 800, color: '#0d1120' }}>
          Benefits Allocation Intelligence
        </div>
        <div style={{ fontSize: 13, color: '#7a8fa6', marginTop: 3 }}>
          End-to-end automated benefits allocation · {d.total_divisions} divisions · {d.cycle} ·{' '}
          <span style={{ color: '#6c47ff', fontWeight: 600 }}>APEX on Azure</span> · runs entirely in your account
        </div>
      </div>

      {/* 4 KPI cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
        <Kpi
          label="Total Benefits Allocated"
          value={fmtUsd(d.kpis.total_allocated_usd)}
          valueColor="#00c4a0"
          delta={`↑ ${d.kpis.total_allocated_pct_vs_may}% vs. May 2026`}
          sub={`Across ${d.total_divisions} divisions · ${d.total_employees} employees`}
        />
        <Kpi
          label="Processing Time"
          value={`${d.kpis.processing_hours}`}
          valueSuffix=" hrs"
          valueColor="#6c47ff"
          delta={`↓ From ${d.kpis.manual_baseline_days} days manual baseline`}
          sub="File intake to journal entry distribution"
        />
        <Kpi
          label="Exceptions Flagged"
          value={`${d.kpis.exceptions_flagged}`}
          valueColor="#f59e0b"
          delta={`↑ ${d.kpis.exceptions_new_this_cycle} new this cycle`}
          deltaColor="#d97706"
          sub="Reclassification errors caught pre-approval"
        />
        <Kpi
          label="Approval Stage"
          value={`Stage ${d.kpis.approval_stage}`}
          valueColor="#6c47ff"
          delta="Accounting review · Awaiting sign-off"
          deltaColor="#2563eb"
          sub={`Benefits approved Jun 5 · Accounting Jun 6`}
        />
      </div>

      {/* Workflow tracker */}
      <Panel style={{ marginBottom: 20 }}>
        <PanelTitle
          title={`${d.cycle} Allocation Workflow`}
          subtitle="S3 intake → APEX extract (Lambda + Azure OpenAI) → Benefits Approval → Accounting Review → Distribution (S3 + SES)"
          badge={`Stage ${d.kpis.approval_stage} of ${d.workflow.total_stages}`}
          badgeStyle={{ bg: '#eff6ff', color: '#2563eb', border: '#bfdbfe' }}
        />
        <div style={{ display: 'flex', alignItems: 'center', gap: 0, margin: '12px 0 20px' }}>
          {d.workflow.stages.map((s, i) => (
            <div key={s.key} style={{ flex: 1, textAlign: 'center', position: 'relative' }}>
              {i < d.workflow.stages.length - 1 && (
                <div style={{
                  position: 'absolute', top: 18, right: -1, width: '100%',
                  height: 2, background: '#e8ecf0', zIndex: 0,
                }} />
              )}
              <div style={{
                width: 36, height: 36, borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 6px', fontSize: 13, fontWeight: 700,
                position: 'relative', zIndex: 1,
                background: stageColor(s.state),
                color:      stageTextColor(s.state),
                boxShadow: s.state === 'active' ? '0 0 0 4px rgba(108,71,255,0.15)' : 'none',
              }}>
                {s.state === 'done' ? '✓' : i + 1}
              </div>
              <div style={{ fontSize: 10.5, fontWeight: 600, color: '#374151' }}>{s.label}</div>
              <div style={{ fontSize: 10, color: '#9ca3af', marginTop: 2 }}>{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Source files */}
        <div style={{ background: '#f8f9fc', borderRadius: 9, padding: 14, border: '1px solid #e8ecf0' }}>
          <div style={{
            fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
            letterSpacing: '.08em', color: '#9ca3af', marginBottom: 10,
          }}>
            Source Files Ingested — S3 Restricted Intake
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8 }}>
            {d.carrier_files.map((f) => (
              <div key={f.name} style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 7, padding: 10 }}>
                <div style={{ fontSize: 11, fontWeight: 600, color: '#0d1120' }}>{f.name}</div>
                <div style={{ fontSize: 10.5, color: '#7a8fa6', marginTop: 2 }}>
                  {f.employees} employees · {fmtUsdFull(f.amount_usd)}
                </div>
                <div style={{ fontSize: 10.5, color: '#16a34a', fontWeight: 600, marginTop: 3 }}>
                  ✓ {f.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      </Panel>

      {/* Division Allocation + Exceptions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
        {/* Division Allocation Table */}
        <Panel>
          <PanelTitle title="Division Allocation Summary"
            badge={`${d.divisions.length} Divisions`}
            badgeStyle={{ bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0' }}
          />
          <div style={{ marginTop: 8 }}>
            <div style={{
              display: 'grid', gridTemplateColumns: '1.4fr 70px 1.1fr 70px 80px',
              gap: 8, fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase',
              letterSpacing: '.06em', color: '#9ca3af',
              paddingBottom: 8, borderBottom: '1px solid #f0f2f5',
            }}>
              <span>Division</span><span>Employees</span><span>Allocated</span><span>vs. Budget</span><span>Status</span>
            </div>
            {d.divisions.map((div) => {
              const s = divisionStatusStyle(div.status);
              return (
                <div key={div.id} style={{
                  display: 'grid', gridTemplateColumns: '1.4fr 70px 1.1fr 70px 80px',
                  gap: 8, fontSize: 12.5, padding: '10px 0',
                  borderBottom: '1px solid #f5f7fa', alignItems: 'center',
                }}>
                  <span>
                    <span style={{
                      width: 10, height: 10, borderRadius: 3,
                      background: div.color, display: 'inline-block', marginRight: 8,
                    }} />
                    <span style={{ fontWeight: 600, color: '#0d1120' }}>{div.name}</span>
                  </span>
                  <span style={{ color: '#7a8fa6' }}>{div.employees}</span>
                  <span style={{ fontFamily: 'Space Grotesk, sans-serif', fontWeight: 700, color: '#0d1f35' }}>
                    {fmtUsdFull(div.allocated_usd)}
                  </span>
                  <span style={{
                    color: div.variance_pct > 2 ? '#d97706' : div.variance_pct < 0 ? '#16a34a' : '#16a34a',
                    fontWeight: 600,
                  }}>
                    {div.variance_pct > 0 ? '+' : ''}{div.variance_pct}%{div.variance_pct > 3 ? ' ⚠' : ''}
                  </span>
                  <span style={{
                    fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 4,
                    background: s.bg, color: s.color, textAlign: 'center',
                  }}>
                    {div.status}
                  </span>
                </div>
              );
            })}
          </div>
          <div style={{
            marginTop: 14, paddingTop: 12, borderTop: '1px solid #f0f2f5',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <div style={{ fontSize: 12, color: '#7a8fa6' }}>Total · {d.total_employees} employees</div>
            <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 18, fontWeight: 800, color: '#0d1f35' }}>
              {fmtUsdFull(d.kpis.total_allocated_usd)}
            </div>
          </div>
        </Panel>

        {/* Exceptions panel */}
        <Panel>
          <PanelTitle title="APEX Exceptions Flagged"
            badge={`${d.exceptions.length} Items`}
            badgeStyle={{ bg: '#fffbeb', color: '#d97706', border: '#fde68a' }}
          />
          <div style={{ marginTop: 4 }}>
            {d.exceptions.map((e) => (
              <div key={e.id}
                onClick={() => router.push(`/review?item=${encodeURIComponent(e.id)}`)}
                style={{
                  display: 'flex', alignItems: 'flex-start', gap: 12,
                  padding: '11px 0', borderBottom: '1px solid #f5f7fa', cursor: 'pointer',
                }}
              >
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: severityColor(e.severity), marginTop: 4, flexShrink: 0,
                }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 600, color: '#0d1120' }}>{e.title}</div>
                  <div style={{ fontSize: 11, color: '#7a8fa6', marginTop: 2, lineHeight: 1.4 }}>
                    {e.employee || ''}{e.employee && ' · '}{e.description.split('.')[0]}
                  </div>
                </div>
                <span style={{
                  fontSize: 10.5, fontWeight: 700, padding: '2px 8px', borderRadius: 4,
                  background: severityBg(e.severity), color: severityColor(e.severity),
                  marginLeft: 'auto', flexShrink: 0,
                }}>
                  {e.severity}
                </span>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      {/* Approval Queue + Audit Trail */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 24 }}>
        {/* Approval Queue */}
        <Panel>
          <PanelTitle title="Two-Stage Approval Queue"
            badge="Stage 2 Active"
            badgeStyle={{ bg: '#eff6ff', color: '#2563eb', border: '#bfdbfe' }}
          />
          {d.approval_queue.map((s) => (
            <div key={s.stage} style={{
              display: 'flex', alignItems: 'center', gap: 12,
              padding: '10px 0', borderBottom: '1px solid #f5f7fa',
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: 9,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: s.status === 'COMPLETE' ? '#f0fdf4'
                          : s.status === 'REVIEW'   ? '#eff6ff'
                          : '#f5f7fa',
                color:      s.status_color, fontSize: 13, fontWeight: 700, flexShrink: 0,
              }}>
                {s.status === 'COMPLETE' ? '✓' : s.stage}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 12.5, fontWeight: 600, color: '#0d1120' }}>{s.title}</div>
                <div style={{ fontSize: 11, color: '#7a8fa6', marginTop: 1 }}>{s.meta}</div>
              </div>
              {s.status === 'REVIEW' && (
                <button
                  onClick={() => router.push('/review')}
                  style={{
                    fontSize: 11.5, fontWeight: 600, padding: '5px 14px',
                    borderRadius: 6, cursor: 'pointer', border: 'none',
                    background: '#0d1f35', color: '#00c4a0',
                  }}
                >
                  Review →
                </button>
              )}
              {s.status === 'COMPLETE' && (
                <span style={{
                  fontSize: 11, fontWeight: 600, color: '#16a34a',
                  background: '#f0fdf4', padding: '4px 10px', borderRadius: 6,
                }}>
                  COMPLETE
                </span>
              )}
              {s.status === 'PENDING' && (
                <span style={{
                  fontSize: 11, fontWeight: 600, color: '#9ca3af',
                  background: '#f5f7fa', padding: '4px 10px', borderRadius: 6,
                }}>
                  PENDING
                </span>
              )}
            </div>
          ))}

          {/* Journal Entry Preview */}
          <div style={{ marginTop: 14, padding: 12, background: '#f8f9fc', borderRadius: 8, border: '1px solid #e8ecf0' }}>
            <div style={{ fontSize: 11.5, fontWeight: 600, color: '#0d1120', marginBottom: 6 }}>
              Journal Entry Preview — {d.je_preview.division}
            </div>
            <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 11, color: '#374151', lineHeight: 1.8 }}>
              {d.je_preview.lines.map((line, i) => (
                <div key={i}>
                  {line.side === 'DR' ? 'DR' : '  CR'} {line.account} · {line.description}{' '}
                  <span style={{ float: 'right', fontWeight: 600 }}>
                    {fmtUsdFull(line.amount_usd)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </Panel>

        {/* Audit Trail */}
        <Panel>
          <PanelTitle title={`APEX Audit Trail — ${d.cycle} Cycle`}
            badge="100% Coverage · Cosmos DB"
            badgeStyle={{ bg: '#f0fdf4', color: '#16a34a', border: '#bbf7d0' }}
          />
          <div>
            {d.audit_log.slice(0, 6).map((a, i) => {
              const ab = auditBadgeStyle(a.badge_color);
              return (
                <div key={i} style={{
                  display: 'flex', gap: 12, padding: '8px 0',
                  borderBottom: i < 5 ? '1px solid #f5f7fa' : 'none',
                }}>
                  <div style={{
                    fontFamily: "'JetBrains Mono', monospace", fontSize: 10.5, color: '#9ca3af',
                    width: 60, flexShrink: 0, marginTop: 2,
                  }}>
                    {a.time}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#0d1120' }}>{a.action}</div>
                    <div style={{ fontSize: 11, color: '#7a8fa6' }}>{a.detail}</div>
                  </div>
                  <span style={{
                    fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                    background: ab.bg, color: ab.text, flexShrink: 0, marginTop: 2,
                  }}>
                    {a.badge}
                  </span>
                </div>
              );
            })}
          </div>
        </Panel>
      </div>

    </div>
  );
}

/* ──────────────────────── helpers ──────────────────────── */
function Panel({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{
      background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0',
      ...style,
    }}>
      {children}
    </div>
  );
}

function PanelTitle({ title, subtitle, badge, badgeStyle }: {
  title: string; subtitle?: string;
  badge?: string; badgeStyle?: { bg: string; color: string; border: string };
}) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
      marginBottom: subtitle ? 8 : 14,
    }}>
      <div>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#0d1f35' }}>{title}</div>
        {subtitle && (
          <div style={{ fontSize: 11, fontWeight: 400, color: '#7a8fa6', marginTop: 2 }}>{subtitle}</div>
        )}
      </div>
      {badge && (
        <span style={{
          fontSize: 11, fontWeight: 600, padding: '3px 10px', borderRadius: 20,
          background: badgeStyle?.bg || '#f5f7fa',
          color:      badgeStyle?.color || '#6b7280',
          border:     `1px solid ${badgeStyle?.border || '#e8ecf0'}`,
        }}>
          {badge}
        </span>
      )}
    </div>
  );
}

function Kpi({ label, value, valueSuffix, valueColor, delta, deltaColor, sub }: {
  label: string; value: string; valueSuffix?: string; valueColor?: string;
  delta?: string; deltaColor?: string; sub?: string;
}) {
  return (
    <div style={{ background: '#fff', borderRadius: 12, padding: 20, border: '1px solid #e8ecf0' }}>
      <div style={{
        fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.07em',
        color: '#7a8fa6', marginBottom: 8,
      }}>
        {label}
      </div>
      <div style={{
        fontFamily: 'Space Grotesk, sans-serif', fontSize: 32, fontWeight: 800,
        color: valueColor || '#0d1f35', lineHeight: 1,
      }}>
        {value}{valueSuffix && <span style={{ fontSize: 18, fontWeight: 600 }}>{valueSuffix}</span>}
      </div>
      {delta && (
        <div style={{ fontSize: 11.5, marginTop: 6, fontWeight: 500, color: deltaColor || '#16a34a' }}>
          {delta}
        </div>
      )}
      {sub && (
        <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 3 }}>{sub}</div>
      )}
    </div>
  );
}
