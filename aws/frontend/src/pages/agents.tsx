/**
 * Agents — deployed agent monitoring grid.
 * Ported from apex-prototype 2/agents.html.
 *
 * Data policy: try fetching from the API; fall back to sample data
 * from the HTML prototype if the fetch fails.
 */

import React, { useMemo, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Icon } from '@/components/AppShell/icons';
import { DataSourceBanner, type DataSource } from '@/components/AppShell/DataSourceBanner';
import { useDemoMode, isIndustryVisible } from '@/lib/demoMode';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type FilterTab = 'all' | 'active' | 'idle' | 'error';

interface AgentItem {
  id: string;
  name: string;
  industry?: string;
  code?: string;
  status: 'active' | 'busy' | 'idle' | 'error';
  docs_today?: number;
  accuracy?: number;
  avg_latency?: string;
  playbook?: string;
  last_run?: string;
  error_message?: string;
}

/** Real `Agent` shape returned by the backend (see backend/models/agent.py). */
interface ApiAgent {
  agent_id: string;
  name: string;
  description?: string;
  type?: string;
  status?: string;                // draft | deploying | active | failed | archived
  environment?: string;
  playbook_id?: string | null;
  model_id?: string;
  invocation_count?: number;
  last_invocation?: string | null;
  updated_at?: string | null;
}

/** Map backend Agent shape → UI AgentItem.
 *
 * The backend's Agent model doesn't carry an explicit industry field, so we
 * infer it from the agent's name. STP agents (ChatSTP, PolicyAgent, etc.)
 * always belong to nuclear_operations; other recognizable bots map to their
 * known industry. Falls through to undefined ("Other" theme) for unknowns.
 */
function inferIndustryFromName(name: string): string | undefined {
  const n = (name || '').toLowerCase();
  // STP agents
  if (n === 'chatstp' || n.endsWith('agent')) {
    if (n.startsWith('chatstp') || n.startsWith('policyagent') || n.startsWith('maintenanceagent')
        || n.startsWith('diagnosticsagent') || n.startsWith('reliabilityagent')) {
      return 'nuclear_operations';
    }
  }
  if (n.includes('invoice') || n.includes('vendor') || n.includes('kyc')) return 'financial_services';
  if (n.includes('claim') || n.includes('auth')) return 'healthcare_payers';
  if (n.includes('intake')) return 'healthcare_providers';
  if (n.includes('underwrite') || n.includes('cre')) return 'insurance_underwriting';
  if (n.includes('contract') || n.includes('rfp') || n.includes('cnc') || n.includes('workorder')) return 'aerospace_defense';
  if (n.includes('po') && n.length < 8) return 'manufacturing';
  if (n.includes('qc') || n.includes('shopper') || n.includes('logistics') || n.includes('customerops')) return 'supply_manufacturing';
  if (n.includes('talent')) return 'hr';
  return undefined;
}

function mapApiAgent(a: ApiAgent): AgentItem {
  const backendStatus = (a.status || '').toLowerCase();
  const uiStatus: AgentItem['status'] =
    backendStatus === 'active'               ? 'active'
  : backendStatus === 'failed'               ? 'error'
  : backendStatus === 'deploying'            ? 'busy'
  : backendStatus === 'archived' || backendStatus === 'draft' ? 'idle'
  :                                            'idle';

  return {
    id: a.agent_id,
    name: a.name,
    code: a.name.replace(/[^A-Za-z]/g, '').slice(0, 3).toUpperCase() || 'AGT',
    industry: inferIndustryFromName(a.name),
    status: uiStatus,
    docs_today: a.invocation_count ?? 0,
    playbook: a.playbook_id || undefined,
    last_run: a.last_invocation || a.updated_at || undefined,
    error_message: backendStatus === 'failed' ? (a.description || 'Agent failed to deploy') : undefined,
  };
}

interface IndustryTheme {
  label: string;
  color: string;
  bg: string;
}

const INDUSTRY_THEMES: Record<string, IndustryTheme> = {
  financial_services:    { label: 'Financial Services',    color: '#1d4ed8', bg: '#dbeafe' },
  insurance_underwriting:{ label: 'Insurance',             color: '#7c3aed', bg: '#f5f3ff' },
  aerospace_defense:     { label: 'Aerospace & Defense',   color: '#ea580c', bg: '#fff7ed' },
  healthcare_payers:     { label: 'Healthcare Payers',     color: '#dc2626', bg: '#fee2e2' },
  healthcare_providers:  { label: 'Healthcare Providers',  color: '#dc2626', bg: '#fee2e2' },
  healthcare_clinical:   { label: 'Healthcare Clinical',   color: '#dc2626', bg: '#fee2e2' },
  manufacturing:         { label: 'Supply Chain & Manufacturing', color: '#16a34a', bg: '#f0fdf4' },
  supply_manufacturing:  { label: 'Supply Chain & Manufacturing', color: '#16a34a', bg: '#f0fdf4' },
  hr:                    { label: 'HR',                    color: '#7c3aed', bg: '#f5f3ff' },
  retail:                { label: 'Retail',                color: '#c026d3', bg: '#fdf4ff' },
  cpg:                   { label: 'CPG',                   color: '#0891b2', bg: '#ecfeff' },
  contact_center:        { label: 'Contact Center',        color: '#0d9488', bg: '#f0fdfa' },
  airlines:              { label: 'Airlines',              color: '#0284c7', bg: '#f0f9ff' },
  supply_chain:          { label: 'Supply Chain & Manufacturing', color: '#16a34a', bg: '#f0fdf4' },
  // Nuclear Operations & Reliability — STP Phase 2 demo domain.
  nuclear_operations:        { label: 'Nuclear Operations & Reliability', color: '#1e3a8a', bg: '#eef2ff' },
  agentic_enterprise:        { label: 'Agentic Enterprise',                color: '#475569', bg: '#f1f5f9' },
  supply_chain_orchestrator: { label: 'Supply Chain Orchestrator',         color: '#0f766e', bg: '#f0fdfa' },
  hospitality:               { label: 'Hospitality & Travel',              color: '#7c3aed', bg: '#f5f3ff' },
  commercial_real_estate:    { label: 'Commercial Real Estate',            color: '#0369a1', bg: '#f0f9ff' },
  other:                     { label: 'Other',                             color: '#475569', bg: '#f1f5f9' },
};

const SAMPLE_AGENTS: AgentItem[] = [
  { id: 'ag-1', name: 'InvoiceBot', code: 'INV', industry: 'financial_services',    status: 'active', docs_today: 142, accuracy: 97.2, avg_latency: '8.2s',  playbook: 'Invoice Processing v2' },
  { id: 'ag-2', name: 'ClaimsBot',  code: 'CLM', industry: 'insurance_underwriting',status: 'active', docs_today:  67, accuracy: 95.8, avg_latency: '11.4s', playbook: 'Claims Intake v3' },
  { id: 'ag-3', name: 'RFPBot',     code: 'RFP', industry: 'aerospace_defense',     status: 'busy',   docs_today:   4, accuracy: 88.4, avg_latency: '42s',   playbook: 'RFP Response v1' },
  { id: 'ag-4', name: 'KYCBot',     code: 'KYC', industry: 'financial_services',    status: 'error',  error_message: 'Connector error: Salesforce API rate limit exceeded' },
  { id: 'ag-5', name: 'CNCBot',     code: 'CNC', industry: 'manufacturing',         status: 'idle',   docs_today:   0, accuracy: 96.1, last_run: '2 days ago' },
  // STP Phase 2 — 5 specialist agents (router + 4 workstreams).
  { id: 'ag-stp-router',       name: 'ChatSTP',          code: 'STP', industry: 'nuclear_operations', status: 'active', docs_today:  61, accuracy: 96.1, avg_latency: '3.4s',  playbook: 'ChatSTP Router' },
  { id: 'ag-stp-policy',       name: 'PolicyAgent',       code: 'POL', industry: 'nuclear_operations', status: 'active', docs_today:  24, accuracy: 99.0, avg_latency: '2.1s',  playbook: 'Policy & Procedure Lookup' },
  { id: 'ag-stp-maintenance',  name: 'MaintenanceAgent',  code: 'MNT', industry: 'nuclear_operations', status: 'active', docs_today:  18, accuracy: 97.4, avg_latency: '4.8s',  playbook: 'Equipment PM History' },
  { id: 'ag-stp-diagnostics',  name: 'DiagnosticsAgent',  code: 'DGN', industry: 'nuclear_operations', status: 'active', docs_today:  12, accuracy: 94.2, avg_latency: '6.2s',  playbook: 'Equipment Issue Analysis' },
  { id: 'ag-stp-reliability',  name: 'ReliabilityAgent',  code: 'RLY', industry: 'nuclear_operations', status: 'busy',   docs_today:   7, accuracy: 91.8, avg_latency: '9.1s',  playbook: 'Predictive Maintenance' },
  // Agentic Enterprise — 3 vendor-neutral demos. Each agent is tagged with
  // its specific industry domain so picking that domain in the demoMode
  // dropdown shows ONLY this agent (the umbrella `agentic_enterprise` mode
  // catches all three via demoMode.ts MATCH_TABLE).
  { id: 'ag-ae-orchestrator',  name: 'OrchestratorAgent', code: 'ORC', industry: 'supply_chain_orchestrator', status: 'active', docs_today:   9, accuracy: 98.4, avg_latency: '1.8s',  playbook: 'Supply Chain Orchestrator' },
  { id: 'ag-ae-concierge',     name: 'ConciergeAgent',    code: 'CON', industry: 'hospitality',               status: 'active', docs_today:  47, accuracy: 96.7, avg_latency: '0.9s',  playbook: 'Cruise Concierge' },
  { id: 'ag-ae-lease',         name: 'LeaseAgent',        code: 'LSE', industry: 'commercial_real_estate',    status: 'active', docs_today:  14, accuracy: 94.8, avg_latency: '3.2s',  playbook: 'Lease Extraction' },
];

export default function AgentsPage() {
  const [tab, setTab] = useState<FilterTab>('all');

  const agentsQuery = useQuery<{ items: AgentItem[]; source: DataSource }>({
    queryKey: ['agents'],
    queryFn: async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/agents`);
        if (r.ok) {
          const j = await r.json();
          const raw: ApiAgent[] = Array.isArray(j) ? j : (j.agents || j.items || []);
          if (raw.length > 0) return { items: raw.map(mapApiAgent), source: 'api' as DataSource };
        }
      } catch { /* fall through */ }
      return { items: [], source: 'mock' as DataSource };
    },
    retry: false,
  });

  const source: DataSource = agentsQuery.isLoading ? 'loading' : (agentsQuery.data?.source ?? 'mock');
  const apiAgents = agentsQuery.data?.items ?? [];
  // Always merge in the bespoke demo samples (STP + Agentic Enterprise) so
  // the demo always has the right agents even when the backend doesn't
  // return them yet (e.g., before seed_default_agents finishes). Dedup by
  // lowercased name.
  const guaranteedSamples = SAMPLE_AGENTS.filter(
    (a) => a.industry === 'nuclear_operations'
        || a.industry === 'supply_chain_orchestrator'
        || a.industry === 'hospitality'
        || a.industry === 'commercial_real_estate',
  );
  const apiNames = new Set(apiAgents.map((a) => (a.name || '').toLowerCase()));
  const sampleExtras = guaranteedSamples.filter((a) => !apiNames.has(a.name.toLowerCase()));
  const allAgents = apiAgents.length > 0 ? [...apiAgents, ...sampleExtras] : SAMPLE_AGENTS;

  // Demo mode: filters agents to the selected industry. 'all' shows every agent.
  const [demoMode] = useDemoMode();
  const agents = allAgents.filter((a) => isIndustryVisible(a.industry, demoMode));

  const counts = useMemo(() => ({
    all:    agents.length,
    active: agents.filter((a) => a.status === 'active' || a.status === 'busy').length,
    idle:   agents.filter((a) => a.status === 'idle').length,
    error:  agents.filter((a) => a.status === 'error').length,
  }), [agents]);

  const filtered = useMemo(() => {
    if (tab === 'all')    return agents;
    if (tab === 'active') return agents.filter((a) => a.status === 'active' || a.status === 'busy');
    if (tab === 'idle')   return agents.filter((a) => a.status === 'idle');
    if (tab === 'error')  return agents.filter((a) => a.status === 'error');
    return agents;
  }, [agents, tab]);

  return (
    <>
      <Head><title>Agents | APEX</title></Head>

      <DataSourceBanner
        source={source}
        entity="agents"
        hint={source === 'mock'
          ? 'Start backend: cd backend && uvicorn main:app --reload (default agents auto-seed on boot)'
          : undefined}
      />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className={`tab ${tab === 'all'    ? 'active' : ''}`} style={{ fontSize: 12, padding: '5px 12px' }} onClick={() => setTab('all')}>All ({counts.all})</button>
          <button className={`tab ${tab === 'active' ? 'active' : ''}`} style={{ fontSize: 12, padding: '5px 12px' }} onClick={() => setTab('active')}>Active ({counts.active})</button>
          <button className={`tab ${tab === 'idle'   ? 'active' : ''}`} style={{ fontSize: 12, padding: '5px 12px' }} onClick={() => setTab('idle')}>Idle ({counts.idle})</button>
          <button className={`tab ${tab === 'error'  ? 'active' : ''}`} style={{ fontSize: 12, padding: '5px 12px' }} onClick={() => setTab('error')}>Error ({counts.error})</button>
        </div>
        <Link href="/canvas/new-playbook" className="btn btn-primary btn-sm">+ Deploy New Agent</Link>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        {filtered.map((a) => <AgentCard key={a.id} a={a} />)}
        <DeployNewCard />
      </div>
    </>
  );
}

function AgentCard({ a }: { a: AgentItem }) {
  const theme = INDUSTRY_THEMES[a.industry || 'other'] || INDUSTRY_THEMES.other;
  const code = a.code || a.name.slice(0, 3).toUpperCase();

  const statusChip =
    a.status === 'active' ? 'chip-green' :
    a.status === 'busy'   ? 'chip-amber' :
    a.status === 'idle'   ? 'chip-gray'  :
                            'chip-red';
  const statusLabel =
    a.status === 'active' ? 'Active' :
    a.status === 'busy'   ? 'Busy'   :
    a.status === 'idle'   ? 'Idle'   :
                            'Error';

  if (a.status === 'error') {
    return (
      <div className="card" style={{ padding: 20, borderColor: '#fecaca' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 40, height: 40, borderRadius: 12, background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, color: theme.color }}>{code}</div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{a.name}</div>
              <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>{theme.label}</div>
            </div>
          </div>
          <span className="chip-red">Error</span>
        </div>
        <div style={{ background: '#fef2f2', borderRadius: 8, padding: 10, marginBottom: 14, fontSize: 12, color: '#dc2626' }}>
          {a.error_message || 'Agent encountered an error'}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-sm" style={{ flex: 1, justifyContent: 'center', background: '#fee2e2', color: '#dc2626', borderColor: '#fecaca' }}>View Error</button>
          <button className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Restart</button>
        </div>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: 20 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 40, height: 40, borderRadius: 12, background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, color: theme.color }}>{code}</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{a.name}</div>
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>{theme.label}</div>
          </div>
        </div>
        <span className={statusChip}>{statusLabel}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 14 }}>
        <StatRow label="Docs today" value={String(a.docs_today ?? 0)} />
        {a.accuracy !== undefined && (
          <StatRow
            label="Accuracy"
            value={`${a.accuracy.toFixed(1)}%`}
            valueColor={a.accuracy >= 95 ? '#16a34a' : a.accuracy >= 90 ? '#d97706' : '#dc2626'}
          />
        )}
        {a.avg_latency && <StatRow label="Avg latency" value={a.avg_latency} />}
        {a.last_run && <StatRow label="Last run" value={a.last_run} />}
        {a.playbook && <StatRow label="Playbook" value={a.playbook} valueColor="#2563eb" weight={500} />}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <Link href="/agent-hub" className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Chat</Link>
        {a.status === 'idle' ? (
          <button className="btn btn-primary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Activate</button>
        ) : (
          <button className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Configure</button>
        )}
      </div>
    </div>
  );
}

function StatRow({ label, value, valueColor, weight }: { label: string; value: string; valueColor?: string; weight?: number }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
      <span style={{ color: '#64748b' }}>{label}</span>
      <span style={{ fontWeight: weight ?? 600, color: valueColor || '#0f172a' }}>{value}</span>
    </div>
  );
}

function DeployNewCard() {
  return (
    <Link
      href="/canvas/new-playbook"
      className="card"
      style={{
        padding: 20,
        border: '2px dashed #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 200,
        cursor: 'pointer',
        textDecoration: 'none',
        boxShadow: 'none',
        gap: 8,
      }}
      onMouseOver={(e) => (e.currentTarget.style.borderColor = '#93c5fd')}
      onMouseOut={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
    >
      <div style={{ width: 44, height: 44, borderRadius: 12, background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon name="plus" style={{ width: 22, height: 22, color: '#94a3b8' }} />
      </div>
      <span style={{ fontSize: 13, fontWeight: 500, color: '#64748b' }}>Deploy New Agent</span>
    </Link>
  );
}
