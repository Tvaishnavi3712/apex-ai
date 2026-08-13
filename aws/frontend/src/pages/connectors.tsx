/**
 * Connectors — grid of external integrations grouped by section.
 *
 * CBB demo (spec §3.4) features a "Cornerstone Building Brands" section
 * first with the 6 connectors the CIO needs to see live: S3 Data Lake,
 * Athena, Azure Fabric One, Dynamics CRM, SAP S/4HANA, Global Supply Chain
 * Monitor. Each card has a Configure button that opens a right-slide panel
 * showing a (masked) endpoint, auth type, sync frequency, and a "Test
 * Connection" button that fires a green success toast.
 */

import React, { useMemo, useState } from 'react';
import Head from 'next/head';
import { CONNECTOR_CATALOG, type ConnectorEntry } from '@/lib/connectorCatalog';

type Status = 'connected' | 'warning' | 'available';

interface Connector {
  code: string;
  name: string;
  subtitle: string;
  status: Status;
  iconBg: string;
  iconColor: string;
  subtitleColor?: string;
  cardBorder?: string;
  /** CBB demos this connector powers, e.g. [1, 3]. Shown as a chip. */
  demos?: number[];
  /** Configure-panel content — present for CBB connectors. */
  config?: {
    endpoint: string;
    authType: 'AWS IAM Role' | 'OAuth 2.0' | 'API Key' | 'Service Principal' | 'Mutual TLS';
    syncFrequency: string;
    lastSync: string;
    region?: string;
    category: string;
  };
}

interface Section { title: string; connectors: Connector[] }

const SECTIONS: Section[] = [
  {
    title: 'Cornerstone Building Brands',
    connectors: [
      {
        code: 'S3', name: 'AWS S3 Data Lake',
        subtitle: 'CBB primary data lake · live',
        status: 'connected',
        iconBg: '#fff7ed', iconColor: '#ea580c',
        demos: [1, 3],
        config: {
          endpoint: 's3://cbb-datalake-prod-*******/',
          authType: 'AWS IAM Role',
          syncFrequency: 'Live — event-driven',
          lastSync: '12 seconds ago',
          region: 'us-east-1',
          category: 'Storage',
        },
      },
      {
        code: 'ATH', name: 'Amazon Athena',
        subtitle: 'Federated SQL over the data lake',
        status: 'connected',
        iconBg: '#eff6ff', iconColor: '#2563eb',
        demos: [1, 3],
        config: {
          endpoint: 'athena.us-east-1.amazonaws.com · workgroup: cbb-prod',
          authType: 'AWS IAM Role',
          syncFrequency: 'On-demand',
          lastSync: '4 minutes ago',
          region: 'us-east-1',
          category: 'Compute / Query',
        },
      },
      {
        code: 'FAB', name: 'Azure Fabric One Lakehouse',
        subtitle: 'Engineering tolerances + specs',
        status: 'connected',
        iconBg: '#eef2ff', iconColor: '#4338ca',
        demos: [2],
        config: {
          endpoint: 'fabric://cbb-manufacturing.lakehouse.fabric.microsoft.com',
          authType: 'Service Principal',
          syncFrequency: 'Every 15 minutes',
          lastSync: '2 minutes ago',
          category: 'Data Platform',
        },
      },
      {
        code: 'CRM', name: 'Microsoft Dynamics CRM',
        subtitle: 'Order + distributor records',
        status: 'connected',
        iconBg: '#e0f2fe', iconColor: '#0284c7',
        demos: [1],
        config: {
          endpoint: 'https://cbb.crm.dynamics.com/api/data/v9.2/',
          authType: 'OAuth 2.0',
          syncFrequency: 'Live — webhook',
          lastSync: '8 seconds ago',
          category: 'CRM / Application',
        },
      },
      {
        code: 'SAP', name: 'SAP S/4HANA ERP',
        subtitle: 'Inventory + PO holds',
        status: 'connected',
        iconBg: '#f0fdf4', iconColor: '#16a34a',
        demos: [2],
        config: {
          endpoint: 'https://s4.cbb.internal/sap/opu/odata/sap/API_*****',
          authType: 'Mutual TLS',
          syncFrequency: 'Live — event-driven',
          lastSync: '1 minute ago',
          category: 'ERP',
        },
      },
      {
        code: 'GSM', name: 'Global Supply Chain Monitor',
        subtitle: 'External disruption alerts',
        status: 'connected',
        iconBg: '#fef2f2', iconColor: '#dc2626',
        demos: [3],
        config: {
          endpoint: 'https://api.globalsupplymonitor.io/v2/alerts',
          authType: 'API Key',
          syncFrequency: 'Live — webhook',
          lastSync: '30 seconds ago',
          category: 'External API',
        },
      },
    ],
  },
  {
    title: 'AWS Services',
    connectors: [
      { code: 'BDA', name: 'Bedrock Data Automation', subtitle: 'Document extraction AI', status: 'connected', iconBg: '#fff7ed', iconColor: '#ea580c' },
      { code: 'BA',  name: 'Bedrock Agents',          subtitle: 'AI agent runtime',       status: 'connected', iconBg: '#f0fdf4', iconColor: '#16a34a' },
      { code: 'S3',  name: 'Amazon S3',               subtitle: 'Document storage',       status: 'connected', iconBg: '#eff6ff', iconColor: '#2563eb' },
      { code: 'DDB', name: 'DynamoDB',                subtitle: 'Work item store',        status: 'connected', iconBg: '#f5f3ff', iconColor: '#7c3aed' },
    ],
  },
  {
    title: 'Enterprise Systems',
    connectors: [
      { code: 'SF',  name: 'Salesforce',  subtitle: 'Rate limit: 82% used', status: 'warning',   iconBg: '#eff6ff', iconColor: '#00a1e0', subtitleColor: '#d97706', cardBorder: '#fde68a' },
      { code: 'SAP', name: 'SAP ERP',     subtitle: 'PO & vendor data',     status: 'connected', iconBg: '#f0fdf4', iconColor: '#16a34a' },
      { code: 'SLK', name: 'Slack',       subtitle: 'Notifications',        status: 'available', iconBg: '#f8fafc', iconColor: '#64748b' },
      { code: 'SVC', name: 'ServiceNow',  subtitle: 'ITSM integration',     status: 'available', iconBg: '#f8fafc', iconColor: '#64748b' },
    ],
  },
];

type TabKey = 'all' | 'connected' | 'available';

/* ───────────────────── Catalog-driven sections ─────────────────────
 * The bespoke SECTIONS above stay as-is so the CBB demo still renders the
 * way it always has. Everything else (the platform-wide 70+ connectors)
 * comes from CONNECTOR_CATALOG so we only have to maintain one source of
 * truth — also re-used by the playbook trigger picker.
 *
 * We DEDUPE by display name so a vendor doesn't show up twice (e.g. SAP
 * S/4HANA is already in the Cornerstone Building Brands section). */
const BESPOKE_NAMES = new Set(
  SECTIONS.flatMap((s) => s.connectors.map((c) => c.name)),
);

function catalogToConnectorCard(e: ConnectorEntry): Connector {
  return {
    code: e.code, name: e.name, subtitle: e.tagline,
    status: e.defaultStatus || 'available',
    iconBg: e.iconBg, iconColor: e.iconColor,
  };
}

const CATALOG_SECTIONS: Section[] = (() => {
  const grouped: Record<string, ConnectorEntry[]> = {};
  for (const c of CONNECTOR_CATALOG) {
    if (BESPOKE_NAMES.has(c.name)) continue;
    if (!grouped[c.category]) grouped[c.category] = [];
    grouped[c.category].push(c);
  }
  // Stable category order — most-asked-about first.
  const order = [
    'Object Storage', 'File Sharing', 'Streaming & Eventing',
    'Databases & CDC', 'Data Warehouses', 'Data Lakes & Lakehouses',
    'Email & Messaging', 'Webhooks & APIs', 'Schedule', 'File Transfer',
    'CRM', 'ERP', 'HRIS', 'ITSM & Ops', 'Document Repositories',
    'Identity & Auth', 'Voice & Contact Center', 'Industrial / OT',
    'Financial & Compliance', 'Observability',
    'AWS Services', 'Azure Services', 'GCP Services', 'AI / ML Services',
  ];
  return order
    .filter((cat) => grouped[cat]?.length > 0)
    .map((cat) => ({ title: cat, connectors: grouped[cat].map(catalogToConnectorCard) }));
})();

const ALL_SECTIONS: Section[] = [...SECTIONS, ...CATALOG_SECTIONS];

// Counts derived from the full merged sections list.
const ALL_COUNT       = ALL_SECTIONS.reduce((a, s) => a + s.connectors.length, 0);
const CONNECTED_COUNT = ALL_SECTIONS.reduce((a, s) => a + s.connectors.filter((c) => c.status === 'connected' || c.status === 'warning').length, 0);
const AVAILABLE_COUNT = ALL_SECTIONS.reduce((a, s) => a + s.connectors.filter((c) => c.status === 'available').length, 0);

export default function Connectors() {
  const [tab, setTab] = useState<TabKey>('all');
  const [configuring, setConfiguring] = useState<Connector | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  };

  const q = search.trim().toLowerCase();
  const filterConnector = (c: Connector): boolean => {
    if (q && !(c.name.toLowerCase().includes(q) || c.subtitle.toLowerCase().includes(q) || c.code.toLowerCase().includes(q))) {
      return false;
    }
    if (tab === 'all') return true;
    if (tab === 'connected') return c.status === 'connected' || c.status === 'warning';
    return c.status === 'available';
  };

  const totalSearchHits = useMemo(() => {
    if (!q) return null;
    return ALL_SECTIONS.reduce((a, s) => a + s.connectors.filter(filterConnector).length, 0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, tab]);

  return (
    <>
      <Head><title>Connectors | APEX</title></Head>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Connectors</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>
            <strong style={{ color: '#0f172a' }}>{ALL_COUNT} integrations</strong> across {ALL_SECTIONS.length} categories.
            Apex integrates with your existing stack without moving data — no SaaS, no model training on your data.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => showToast('Coming soon — bring-your-own connector wizard')}>+ Add Connector</button>
      </div>

      <div style={{
        display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24,
        flexWrap: 'wrap',
      }}>
        <div className="tab-bar" style={{ width: 'fit-content' }}>
          <TabBtn active={tab === 'all'}       onClick={() => setTab('all')}>All ({ALL_COUNT})</TabBtn>
          <TabBtn active={tab === 'connected'} onClick={() => setTab('connected')}>Connected ({CONNECTED_COUNT})</TabBtn>
          <TabBtn active={tab === 'available'} onClick={() => setTab('available')}>Available ({AVAILABLE_COUNT})</TabBtn>
        </div>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search integrations (S3, Snowflake, ServiceNow, FinCEN…)"
          style={{
            flex: 1, minWidth: 240, padding: '8px 14px', borderRadius: 10,
            border: '1px solid #e2e8f0', fontSize: 13, color: '#0f172a',
            background: '#fff', outline: 'none',
          }}
        />
        {totalSearchHits !== null && (
          <span style={{ fontSize: 12, color: '#64748b' }}>
            {totalSearchHits} match{totalSearchHits === 1 ? '' : 'es'}
          </span>
        )}
      </div>

      {ALL_SECTIONS.map((section) => {
        const visible = section.connectors.filter(filterConnector);
        if (visible.length === 0) return null;
        return (
          <div key={section.title} style={{ marginBottom: 24 }}>
            <div style={{
              fontSize: 12, fontWeight: 600, textTransform: 'uppercase',
              letterSpacing: '.06em', color: '#94a3b8', marginBottom: 12,
            }}>
              {section.title}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
              {visible.map((c) => (
                <ConnectorCard
                  key={c.code + c.name}
                  c={c}
                  onConfigure={() => setConfiguring(c)}
                />
              ))}
            </div>
          </div>
        );
      })}

      {configuring && (
        <ConfigurePanel
          connector={configuring}
          onClose={() => setConfiguring(null)}
          onTest={() => showToast(`✓ ${configuring.name} — Connection Successful`)}
        />
      )}

      {toast && (
        <div
          style={{
            position: 'fixed', top: 80, right: 24, zIndex: 120,
            background: '#16a34a', color: '#fff',
            padding: '10px 16px', borderRadius: 10,
            fontSize: 13, fontWeight: 500,
            boxShadow: '0 10px 25px rgba(15,23,42,.2)',
          }}
        >
          {toast}
        </div>
      )}
    </>
  );
}

function ConnectorCard({ c, onConfigure }: { c: Connector; onConfigure: () => void }) {
  const cardClass = c.status === 'available' ? 'connector-card' : 'connector-card connected';
  const cardStyle: React.CSSProperties = c.cardBorder ? { borderColor: c.cardBorder } : {};

  const chip =
    c.status === 'connected' ? <span className="chip-green">Connected</span> :
    c.status === 'warning'   ? <span className="chip-amber">Warning</span> :
    <span className="chip-gray">Available</span>;

  return (
    <div className={cardClass} style={cardStyle}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: c.iconBg, color: c.iconColor,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 11, fontWeight: 700,
        }}>
          {c.code}
        </div>
        {chip}
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{c.name}</div>
      <div style={{ fontSize: 11, color: c.subtitleColor || '#94a3b8', marginTop: 3 }}>{c.subtitle}</div>

      {c.demos && c.demos.length > 0 && (
        <div style={{ marginTop: 10 }}>
          <span
            style={{
              fontSize: 9, fontWeight: 700, letterSpacing: '.08em',
              padding: '2px 6px', borderRadius: 4,
              background: '#0f172a', color: '#f8fafc',
            }}
          >
            CBB DEMO{c.demos.length > 1 ? 'S' : ''} · {c.demos.join(', ')}
          </span>
        </div>
      )}

      <div style={{ marginTop: 12, display: 'flex', gap: 6 }}>
        {c.status === 'available' ? (
          <button className="btn btn-primary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
            Connect
          </button>
        ) : c.config ? (
          <button
            className="btn btn-secondary btn-sm"
            style={{ flex: 1, justifyContent: 'center' }}
            onClick={onConfigure}
          >
            Configure
          </button>
        ) : (
          <button className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
            Manage
          </button>
        )}
      </div>
    </div>
  );
}

function ConfigurePanel({ connector, onClose, onTest }: {
  connector: Connector;
  onClose: () => void;
  onTest: () => void;
}) {
  const [testing, setTesting] = useState(false);
  const cfg = connector.config!;

  const runTest = () => {
    setTesting(true);
    setTimeout(() => {
      setTesting(false);
      onTest();
    }, 900);
  };

  return (
    <>
      <div
        onClick={onClose}
        style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.25)', zIndex: 95 }}
      />
      <aside
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0, width: 460,
          background: '#fff', zIndex: 96,
          boxShadow: '-12px 0 32px rgba(15,23,42,.08)',
          display: 'flex', flexDirection: 'column',
        }}
      >
        {/* Header */}
        <div style={{ padding: '18px 22px', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 12,
                background: connector.iconBg, color: connector.iconColor,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, fontWeight: 700,
              }}>
                {connector.code}
              </div>
              <div>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>{connector.name}</h3>
                <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>{cfg.category}</div>
              </div>
            </div>
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#9ca3af' }}
            >
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <span className="chip-green">Connected</span>
            <span style={{ fontSize: 11, color: '#64748b' }}>Last sync: {cfg.lastSync}</span>
          </div>
        </div>

        {/* Body */}
        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 22, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Field label="Endpoint URL (masked)">
            <div
              className="mono"
              style={{
                fontSize: 11, padding: '9px 12px', background: '#f8fafc',
                border: '1px solid #e2e8f0', borderRadius: 8,
                color: '#0f172a', wordBreak: 'break-all',
              }}
            >
              {cfg.endpoint}
            </div>
          </Field>

          <Field label="Authentication type">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontSize: 11, fontWeight: 600,
                padding: '4px 10px', borderRadius: 99,
                background: '#eff6ff', color: '#2563eb',
                border: '1px solid #bfdbfe',
              }}>
                {cfg.authType}
              </span>
              <span style={{ fontSize: 11, color: '#16a34a', fontWeight: 600 }}>✓ Credentials valid</span>
            </div>
          </Field>

          <Field label="Sync frequency">
            <select className="select" defaultValue={cfg.syncFrequency}>
              <option>{cfg.syncFrequency}</option>
              <option>Every 5 minutes</option>
              <option>Every 15 minutes</option>
              <option>Every hour</option>
              <option>Daily at 00:00</option>
            </select>
          </Field>

          {cfg.region && (
            <Field label="Region">
              <input className="input mono" defaultValue={cfg.region} readOnly />
            </Field>
          )}

          {connector.demos && (
            <Field label="Powers CBB demos">
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                {connector.demos.map((d) => (
                  <span
                    key={d}
                    style={{
                      fontSize: 10, fontWeight: 700, letterSpacing: '.06em',
                      padding: '3px 8px', borderRadius: 4,
                      background: '#0f172a', color: '#f8fafc',
                    }}
                  >
                    DEMO {d}
                  </span>
                ))}
              </div>
            </Field>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 22px', borderTop: '1px solid #f1f5f9',
          display: 'flex', gap: 8, justifyContent: 'space-between',
        }}>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>Close</button>
          <button
            className="btn btn-success"
            onClick={runTest}
            disabled={testing}
            style={testing ? { opacity: 0.7, cursor: 'not-allowed' } : undefined}
          >
            {testing ? '⟳ Testing…' : 'Test Connection'}
          </button>
        </div>
      </aside>
    </>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  );
}

function TabBtn({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button className={active ? 'tab active' : 'tab'} onClick={onClick}>
      {children}
    </button>
  );
}
