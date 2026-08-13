/**
 * Canvas — Playbooks & Blueprints browser.
 * Ported from apex-prototype 2/canvas.html.
 *
 * Data policy: if the API returns real data, we display it grouped by
 * industry; otherwise we fall back to the HTML sample grouping.
 */

import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Icon } from '@/components/AppShell/icons';
import { DataSourceBanner, type DataSource } from '@/components/AppShell/DataSourceBanner';
import { useDemoMode, isIndustryVisible } from '@/lib/demoMode';
import { humanizeName } from '@/lib/humanize';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type Tab = 'playbooks' | 'blueprints';

interface PlaybookItem {
  id: string;
  name: string;
  description?: string;
  industry?: string;
  status?: string;
  actions_count?: number;
  last_run?: string;
}

interface BlueprintItem {
  id: string;
  name: string;
  industry?: string;
  field_count?: number;
  status?: string;
  arn?: string;
}

export default function CanvasPage() {
  const [tab, setTab] = useState<Tab>('playbooks');
  const [openSchema, setOpenSchema]   = useState<string | null>(null);
  // Collapse state is stored per industry, scoped per tab so the two views
  // don't fight each other. Default: everything expanded.
  const [collapsedPb, setCollapsedPb] = useState<Set<string>>(new Set());
  const [collapsedBp, setCollapsedBp] = useState<Set<string>>(new Set());

  const collapsed = tab === 'playbooks' ? collapsedPb : collapsedBp;
  const setCollapsed = tab === 'playbooks' ? setCollapsedPb : setCollapsedBp;

  const toggleGroup = (industry: string) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(industry)) next.delete(industry);
      else next.add(industry);
      return next;
    });
  };

  const pbQuery = useQuery<{ items: PlaybookItem[]; source: DataSource }>({
    queryKey: ['playbooks'],
    queryFn: async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/playbooks?limit=500`);
        if (r.ok) {
          const j = await r.json();
          const raw: any[] = Array.isArray(j) ? j : (j.playbooks || j.items || []);
          // CRITICAL: backend returns `playbook_id`, frontend list type uses `id`.
          // Without this map, every Link href becomes /canvas/playbook/undefined
          // → 404 on the detail page → silent invoice fallback. (see CLAUDE.md
          // "Zero-hardcoding rule")
          const items: PlaybookItem[] = raw.map((p) => ({
            id:            p.playbook_id || p.id,
            // Title-case the snake_case backend name (`policy_procedure_lookup`
            // → `Policy Procedure Lookup`). See lib/humanize.ts for acronym
            // handling (HR, RCS, etc).
            name:          humanizeName(p.name) || p.name || '',
            description:   p.description,
            industry:      p.industry,
            status:        p.status,
            actions_count: Array.isArray(p.actions) ? p.actions.length : p.actions_count,
            last_run:      p.last_run,
          }));
          if (items.length > 0) return { items, source: 'api' as DataSource };
        }
      } catch { /* fall through */ }
      return { items: [], source: 'mock' as DataSource };
    },
    retry: false,
  });

  const bpQuery = useQuery<{ items: BlueprintItem[]; source: DataSource }>({
    queryKey: ['blueprints'],
    queryFn: async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/blueprints?limit=500`);
        if (r.ok) {
          const j = await r.json();
          const raw: any[] = Array.isArray(j) ? j : (j.blueprints || j.items || []);
          // Same id-mapping bug as playbooks above — backend returns
          // `blueprint_id`, frontend type uses `id`. Map it explicitly.
          const items: BlueprintItem[] = raw.map((b) => ({
            id:          b.blueprint_id || b.id,
            name:        humanizeName(b.name) || b.name || '',
            industry:    b.industry,
            field_count: Array.isArray(b.schema_fields) ? b.schema_fields.length : b.field_count,
            status:      b.status,
            arn:         b.bda_blueprint_arn || b.arn,
          }));
          if (items.length > 0) return { items, source: 'api' as DataSource };
        }
      } catch { /* fall through */ }
      return { items: [], source: 'mock' as DataSource };
    },
    retry: false,
  });

  // Banner follows whichever tab is currently visible.
  const activeQuery = tab === 'playbooks' ? pbQuery : bpQuery;
  const source: DataSource = activeQuery.isLoading
    ? 'loading'
    : (activeQuery.data?.source ?? 'mock');
  const bannerEntity = tab === 'playbooks' ? 'playbooks' : 'blueprints';
  const bannerHint = source === 'mock'
    ? `curl -X POST 'http://localhost:8000/api/v1/${bannerEntity}/seed?force=true'`
    : undefined;

  // Merge API data with the CBB demo cards + generic samples.
  //
  // Why: (1) CBB demo cards must always appear — they power the 3 hero demos
  // and don't live in DynamoDB. (2) The seeder has a habit of inserting the
  // same playbook twice, so we dedupe on (industry, normalized name).
  // (3) Generic pb-*/bp-* samples are only used when the API returned nothing,
  // otherwise they double-up with real rows that have the same name.
  const allPlaybooks  = useDedupedList(pbQuery.data?.items,  CBB_PLAYBOOKS,  GENERIC_SAMPLE_PLAYBOOKS);
  const allBlueprints = useDedupedList(bpQuery.data?.items,  CBB_BLUEPRINTS, GENERIC_SAMPLE_BLUEPRINTS);

  // Demo-mode filter: collapses Canvas to the selected industry. 'all' shows
  // every industry. Backend data unchanged — UI-only filter.
  const [demoMode] = useDemoMode();
  const playbooks  = allPlaybooks.filter((p) => isIndustryVisible(canonIndustry(p.industry), demoMode));
  const blueprints = allBlueprints.filter((b) => isIndustryVisible(canonIndustry(b.industry), demoMode));

  // group playbooks by industry — canonIndustry() merges manufacturing +
  // supply_chain into a single "Supply Chain & Manufacturing" domain.
  const grouped = playbooks.reduce<Record<string, PlaybookItem[]>>((acc, p) => {
    const k = canonIndustry(p.industry);
    (acc[k] = acc[k] || []).push(p);
    return acc;
  }, {});

  // group blueprints by industry (same shape as playbooks so the expand/collapse
  // control works identically across both tabs)
  const groupedBp = blueprints.reduce<Record<string, BlueprintItem[]>>((acc, b) => {
    const k = canonIndustry(b.industry);
    (acc[k] = acc[k] || []).push(b);
    return acc;
  }, {});

  const activeIndustryKeys = tab === 'playbooks' ? Object.keys(grouped) : Object.keys(groupedBp);
  const allCollapsed = activeIndustryKeys.length > 0 && activeIndustryKeys.every((k) => collapsed.has(k));
  const expandAll   = () => setCollapsed(new Set());
  const collapseAll = () => setCollapsed(new Set(activeIndustryKeys));

  return (
    <>
      <Head><title>Canvas | APEX</title></Head>

      <DataSourceBanner source={source} entity={bannerEntity} hint={bannerHint} />

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Canvas</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>Design playbooks and extraction blueprints by industry domain</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <Link href="/canvas/new-blueprint" className="btn btn-secondary">
            <Icon name="doc" className="" style={{ width: 16, height: 16 }} /> New Blueprint
          </Link>
          <Link href="/canvas/new-playbook" className="btn btn-primary">
            <Icon name="plus" className="" style={{ width: 16, height: 16 }} /> New Playbook
          </Link>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, gap: 12, flexWrap: 'wrap' }}>
        <div className="tab-bar" style={{ width: 'fit-content' }}>
          <button className={`tab ${tab === 'playbooks' ? 'active' : ''}`} onClick={() => setTab('playbooks')}>
            Playbooks ({playbooks.length})
          </button>
          <button className={`tab ${tab === 'blueprints' ? 'active' : ''}`} onClick={() => setTab('blueprints')}>
            Blueprints ({blueprints.length})
          </button>
        </div>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', fontSize: 12 }}>
          <span style={{ color: '#94a3b8', marginRight: 4 }}>
            {activeIndustryKeys.length} domain{activeIndustryKeys.length === 1 ? '' : 's'}
          </span>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={allCollapsed ? expandAll : collapseAll}
            disabled={activeIndustryKeys.length === 0}
            title={allCollapsed ? 'Expand all domains' : 'Collapse all domains'}
          >
            {allCollapsed ? '▸ Expand All' : '▾ Collapse All'}
          </button>
        </div>
      </div>

      {tab === 'playbooks' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {Object.entries(grouped).map(([industry, items]) => (
            <IndustryGroup
              key={industry}
              industry={industry}
              items={items}
              collapsed={collapsed.has(industry)}
              onToggle={() => toggleGroup(industry)}
            />
          ))}
        </div>
      )}

      {tab === 'blueprints' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {Object.entries(groupedBp).map(([industry, items]) => (
            <BlueprintIndustryGroup
              key={industry}
              industry={industry}
              items={items}
              collapsed={collapsed.has(industry)}
              onToggle={() => toggleGroup(industry)}
              onViewSchema={(id) => CBB_BLUEPRINT_SCHEMAS[id] && setOpenSchema(id)}
            />
          ))}
          <NewBlueprintCard />
        </div>
      )}

      {openSchema && CBB_BLUEPRINT_SCHEMAS[openSchema] && (
        <SchemaPanel
          blueprint={CBB_BLUEPRINT_SCHEMAS[openSchema]}
          onClose={() => setOpenSchema(null)}
        />
      )}
    </>
  );
}

function IndustryGroup({
  industry, items, collapsed, onToggle,
}: {
  industry: string;
  items: PlaybookItem[];
  collapsed: boolean;
  onToggle: () => void;
}) {
  const theme = INDUSTRY_THEME[canonIndustry(industry)] || DEFAULT_THEME;
  const activeCount = items.filter((p) => p.status === 'deployed' || p.status === 'active').length;

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={!collapsed}
        aria-controls={`pb-group-${industry}`}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          width: '100%', padding: '16px 20px',
          borderBottom: collapsed ? 'none' : '1px solid #f8fafc',
          background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left',
          transition: 'background .12s',
        }}
        onMouseOver={(e) => (e.currentTarget.style.background = '#f8fafc')}
        onMouseOut={(e)  => (e.currentTarget.style.background = 'transparent')}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Chevron collapsed={collapsed} />
          <div style={{ width: 36, height: 36, borderRadius: 10, background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg style={{ width: 18, height: 18, color: theme.color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.iconPath} />
            </svg>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15, color: '#0f172a' }}>{theme.label}</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 1 }}>{items.length} playbook{items.length === 1 ? '' : 's'}</div>
          </div>
        </div>
        {activeCount > 0 && <span className={theme.chipCls}>{activeCount} Active</span>}
      </button>
      {!collapsed && (
        <div id={`pb-group-${industry}`}>
          {items.map((p, i) => <PlaybookRow key={p.id} p={p} last={i === items.length - 1} />)}
        </div>
      )}
    </div>
  );
}

function BlueprintIndustryGroup({
  industry, items, collapsed, onToggle, onViewSchema,
}: {
  industry: string;
  items: BlueprintItem[];
  collapsed: boolean;
  onToggle: () => void;
  onViewSchema: (id: string) => void;
}) {
  const theme = INDUSTRY_THEME[canonIndustry(industry)] || DEFAULT_THEME;
  const deployedCount = items.filter((b) => b.status === 'deployed' || !!b.arn).length;

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={!collapsed}
        aria-controls={`bp-group-${industry}`}
        style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          width: '100%', padding: '16px 20px',
          borderBottom: collapsed ? 'none' : '1px solid #f8fafc',
          background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left',
          transition: 'background .12s',
        }}
        onMouseOver={(e) => (e.currentTarget.style.background = '#f8fafc')}
        onMouseOut={(e)  => (e.currentTarget.style.background = 'transparent')}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Chevron collapsed={collapsed} />
          <div style={{ width: 36, height: 36, borderRadius: 10, background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg style={{ width: 18, height: 18, color: theme.color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.iconPath} />
            </svg>
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15, color: '#0f172a' }}>{theme.label}</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 1 }}>
              {items.length} blueprint{items.length === 1 ? '' : 's'}
            </div>
          </div>
        </div>
        {deployedCount > 0 && <span className={theme.chipCls}>{deployedCount} Deployed</span>}
      </button>
      {!collapsed && (
        <div
          id={`bp-group-${industry}`}
          style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, padding: 20 }}
        >
          {items.map((bp) => (
            <BlueprintCard
              key={bp.id}
              bp={bp}
              onViewSchema={CBB_BLUEPRINT_SCHEMAS[bp.id] ? () => onViewSchema(bp.id) : undefined}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function Chevron({ collapsed }: { collapsed: boolean }) {
  return (
    <svg
      style={{
        width: 16, height: 16, color: '#94a3b8',
        transform: collapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
        transition: 'transform .15s ease',
      }}
      fill="none" viewBox="0 0 24 24" stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
    </svg>
  );
}

function PlaybookRow({ p, last }: { p: PlaybookItem; last?: boolean }) {
  const s = STATUS_MAP[p.status || 'draft'] || STATUS_MAP.draft;
  return (
    <Link
      href={`/canvas/playbook/${p.id}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '14px 20px',
        borderBottom: last ? 'none' : '1px solid #f8fafc',
        cursor: 'pointer',
        textDecoration: 'none',
      } as React.CSSProperties}
      onMouseOver={(e) => (e.currentTarget.style.background = '#f8fafc')}
      onMouseOut={(e)  => (e.currentTarget.style.background = '')}
    >
      {playbookRowInner(p, s)}
    </Link>
  );
}

function playbookRowInner(p: PlaybookItem, s: { dot: 'green' | 'amber' | 'gray' | 'red'; chip: string; chipText: string }) {
  return (
    <>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span className={`dot-${s.dot}`} />
        <div>
          <div style={{ fontSize: 14, fontWeight: 500, color: '#0f172a' }}>{p.name}</div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
            {p.description || `${p.actions_count || 0} actions · ${p.last_run ? `Last run ${p.last_run}` : 'Never run'}`}
          </div>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span className={s.chip}>{s.chipText}</span>
        <span className="btn btn-secondary btn-sm">Open Editor</span>
      </div>
    </>
  );
}

function BlueprintCard({ bp, onViewSchema }: { bp: BlueprintItem; onViewSchema?: () => void }) {
  const theme = INDUSTRY_THEME[canonIndustry(bp.industry)] || DEFAULT_THEME;
  const deployed = bp.status === 'deployed' || !!bp.arn;
  const code = theme.blueprint?.code || (bp.name || '?').slice(0, 3).toUpperCase();

  return (
    <div
      className="card"
      style={{ padding: 20, cursor: 'pointer' }}
      onClick={onViewSchema}
      onMouseOver={(e) => (e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,.08)')}
      onMouseOut={(e) => (e.currentTarget.style.boxShadow = '')}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: theme.color }}>
          {code}
        </div>
        <span className={deployed ? 'chip-green' : 'chip-amber'}>{deployed ? 'Deployed' : 'Draft'}</span>
      </div>
      <div style={{ fontWeight: 600, fontSize: 14, color: '#0f172a' }}>{bp.name}</div>
      <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>
        {theme.label} · {bp.field_count || 0} fields
      </div>
      <div
        className="mono"
        style={{
          fontSize: 11,
          color: '#64748b',
          marginTop: 8,
          background: '#f8fafc',
          padding: '6px 10px',
          borderRadius: 8,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {bp.arn || 'Not yet deployed'}
      </div>
      <div style={{ display: 'flex', gap: 8, marginTop: 12 }} onClick={(e) => e.stopPropagation()}>
        {onViewSchema ? (
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            style={{ flex: 1, justifyContent: 'center' }}
            onClick={onViewSchema}
          >
            View Schema
          </button>
        ) : (
          <Link href={`/canvas/blueprint/${bp.id}`} className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Edit</Link>
        )}
        <Link href={deployed ? '/testing' : '/canvas/new-blueprint'} className="btn btn-primary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
          {deployed ? 'Test' : 'Deploy'}
        </Link>
      </div>
    </div>
  );
}

function NewBlueprintCard() {
  return (
    <Link
      href="/canvas/new-blueprint"
      className="card"
      style={{
        padding: 20,
        border: '2px dashed #e2e8f0',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 160,
        cursor: 'pointer',
        textDecoration: 'none',
        boxShadow: 'none',
        gap: 8,
      }}
      onMouseOver={(e) => (e.currentTarget.style.borderColor = '#93c5fd')}
      onMouseOut={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
    >
      <div style={{ width: 40, height: 40, borderRadius: 10, background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Icon name="plus" className="" style={{ width: 20, height: 20, color: '#94a3b8' }} />
      </div>
      <span style={{ fontSize: 13, fontWeight: 500, color: '#64748b' }}>New Blueprint</span>
    </Link>
  );
}

/* ─────────── theme maps ─────────── */

interface IndustryTheme {
  label: string; color: string; bg: string; iconPath: string; chipCls: string;
  blueprint?: { color: string; bg: string; code: string };
}

const INDUSTRY_THEME: Record<string, IndustryTheme> = {
  financial_services: {
    label: 'Financial Services', color: '#2563eb', bg: '#eff6ff', chipCls: 'chip-blue',
    iconPath: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    blueprint: { color: '#2563eb', bg: '#eff6ff', code: 'INV' },
  },
  insurance_underwriting: {
    label: 'Insurance', color: '#7c3aed', bg: '#f5f3ff', chipCls: 'chip-purple',
    iconPath: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
    blueprint: { color: '#7c3aed', bg: '#f5f3ff', code: 'CLM' },
  },
  aerospace_defense: {
    label: 'Aerospace & Defense', color: '#ea580c', bg: '#fff7ed', chipCls: 'chip-amber',
    iconPath: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
    blueprint: { color: '#ea580c', bg: '#fff7ed', code: 'RFP' },
  },
  healthcare_payers:    { label: 'Healthcare Payers',    color: '#dc2626', bg: '#fef2f2', chipCls: 'chip-red',    iconPath: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  healthcare_providers: { label: 'Healthcare Providers', color: '#dc2626', bg: '#fef2f2', chipCls: 'chip-red',    iconPath: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  healthcare_clinical:  { label: 'Healthcare Clinical',  color: '#dc2626', bg: '#fef2f2', chipCls: 'chip-red',    iconPath: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  supply_manufacturing: { label: 'Supply Chain & Manufacturing', color: '#0f766e', bg: '#f0fdfa', chipCls: 'chip-green', iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
  hr:                   { label: 'HR',                   color: '#7c3aed', bg: '#f5f3ff', chipCls: 'chip-purple', iconPath: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
  retail:               { label: 'Retail',               color: '#c026d3', bg: '#fdf4ff', chipCls: 'chip-purple', iconPath: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z' },
  cpg:                  { label: 'CPG',                  color: '#0891b2', bg: '#ecfeff', chipCls: 'chip-blue',   iconPath: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z' },
  contact_center:       { label: 'Contact Center',       color: '#0d9488', bg: '#f0fdfa', chipCls: 'chip-green',  iconPath: 'M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z' },
  airlines:             { label: 'Airlines',             color: '#0284c7', bg: '#f0f9ff', chipCls: 'chip-blue',   iconPath: 'M3 19l9 2-9-18-9 18 9-2zm0 0v-8' },
  // Nuclear Operations & Reliability — STP demo (Phase 2). Slate-blue accent
  // signals "regulated / engineered / serious"; the orbit + nucleus iconPath
  // is the universal "atomic" cue.
  nuclear_operations:   {
    label: 'Nuclear Operations & Reliability', color: '#1e3a8a', bg: '#eef2ff', chipCls: 'chip-blue',
    iconPath: 'M12 2a10 10 0 100 20 10 10 0 000-20zm-7.5 7.5l15 5m0-5l-15 5M12 12m-3 0a3 3 0 106 0 3 3 0 10-6 0',
    blueprint: { color: '#1e3a8a', bg: '#eef2ff', code: 'WP' },
  },
  // Telecommunications — carrier far-edge / RAN / network deployment.
  // Red accent + signal-tower icon (matches the actions.tsx theme).
  telecommunications:   {
    label: 'Telecommunications', color: '#b91c1c', bg: '#fef2f2', chipCls: 'chip-red',
    iconPath: 'M8.111 16.404a5.5 5.5 0 010-7.778m7.778 0a5.5 5.5 0 010 7.778m-9.9 2.121a8.5 8.5 0 010-12.02m12.02 0a8.5 8.5 0 010 12.02M12 14a2 2 0 100-4 2 2 0 000 4z',
    blueprint: { color: '#b91c1c', bg: '#fef2f2', code: 'TEL' },
  },
  // Oil & Gas Midstream — deep green accent (EPROD demo).
  oil_gas_midstream: {
    label: 'Oil & Gas — Midstream', color: '#047857', bg: '#ecfdf5', chipCls: 'chip-green',
    iconPath: 'M5 12h14m-7-7l7 7-7 7',
    blueprint: { color: '#047857', bg: '#ecfdf5', code: 'OGM' },
  },
  // ─── Agentic Enterprise (66 Degrees vendor-neutral) — 3 specific industry domains ───
  supply_chain_orchestrator: {
    label: 'Supply Chain Orchestrator', color: '#0f766e', bg: '#f0fdfa', chipCls: 'chip-green',
    iconPath: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    blueprint: { color: '#0f766e', bg: '#f0fdfa', code: 'SCO' },
  },
  hospitality:               {
    label: 'Hospitality & Travel', color: '#7c3aed', bg: '#f5f3ff', chipCls: 'chip-purple',
    iconPath: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    blueprint: { color: '#7c3aed', bg: '#f5f3ff', code: 'HOS' },
  },
  commercial_real_estate:    {
    label: 'Commercial Real Estate', color: '#0369a1', bg: '#f0f9ff', chipCls: 'chip-blue',
    iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    blueprint: { color: '#0369a1', bg: '#f0f9ff', code: 'CRE' },
  },
  other:                { label: 'Other',                color: '#475569', bg: '#f1f5f9', chipCls: 'chip-gray',   iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
};

const DEFAULT_THEME: IndustryTheme = INDUSTRY_THEME.other;

/** Canonicalise an industry string so manufacturing + supply_chain merge into
 *  the unified "Supply Chain & Manufacturing" domain. Leaves other industries
 *  (financial_services, healthcare_*, etc.) untouched. */
function canonIndustry(s: string | undefined | null): string {
  const k = (s || 'other').toLowerCase();
  if (k === 'manufacturing' || k === 'supply_chain' || k === 'supply' || k === 'supply_manufacturing') {
    return 'supply_manufacturing';
  }
  return k;
}

const STATUS_MAP: Record<string, { dot: 'green' | 'amber' | 'gray' | 'red'; chip: string; chipText: string }> = {
  deployed: { dot: 'green', chip: 'chip-green', chipText: 'Active' },
  active:   { dot: 'green', chip: 'chip-green', chipText: 'Active' },
  draft:    { dot: 'gray',  chip: 'chip-gray',  chipText: 'Draft' },
  idle:     { dot: 'amber', chip: 'chip-amber', chipText: 'Idle' },
  archived: { dot: 'red',   chip: 'chip-red',   chipText: 'Archived' },
};

/* ─────────── Sample data ─────────── */
/** CBB demo cards — always rendered, they drive the 3 hero demos. */
const CBB_PLAYBOOKS: PlaybookItem[] = [
  { id: 'pb-cbb-1', name: 'Zero-Touch Order Modification',   industry: 'supply_manufacturing',   status: 'deployed', description: 'CBB · Supply Chain & Manufacturing · 5 actions · Document Upload trigger · Last run 2 min ago' },
  { id: 'pb-cbb-2', name: 'QC Batch Ingestion & Hold',       industry: 'supply_manufacturing',          status: 'deployed', description: 'CBB · Manufacturing · 5 actions · Document Upload (ZIP) trigger · Last run 14 min ago' },
  { id: 'pb-cbb-3', name: 'Disruption Impact & Reroute',     industry: 'supply_manufacturing',           status: 'deployed', description: 'CBB · Supply Chain · 5 actions · API event trigger · Last run 6 min ago' },
  // STP Phase 2 demo playbooks (4 use cases — UC-1 through UC-4).
  { id: 'pb-stp-1', name: 'Policy & Procedure Lookup',       industry: 'nuclear_operations', status: 'deployed', description: 'STP · ChatSTP UC-1 · 3 actions · PolicyAgent · Cited verbatim from policy corpus' },
  { id: 'pb-stp-2', name: 'Equipment PM History',            industry: 'nuclear_operations', status: 'deployed', description: 'STP · ChatSTP UC-2 · 4 actions · MaintenanceAgent · Oracle PMHISTORY + engineer attribution' },
  { id: 'pb-stp-3', name: 'Equipment Issue Analysis',        industry: 'nuclear_operations', status: 'deployed', description: 'STP · ChatSTP UC-3 · 3 actions · DiagnosticsAgent · Failure mode aggregation across WO corpus' },
  { id: 'pb-stp-4', name: 'Predictive Maintenance',          industry: 'nuclear_operations', status: 'deployed', description: 'STP · ChatSTP UC-4 · 5 actions · ReliabilityAgent · ApexSignal RUL + anomaly + risk scoring' },
  // Telecommunications — Verizon Far Edge: the 6 real playbooks are SEEDED in
  // DynamoDB (full_certification_cycle, schema_drift_response, operator_kb_query,
  // wave_deployment_risk_assessment, new_platform_onboarding, playbook_gap_analysis),
  // so the canvas renders them straight from the API — no hardcoded shadows here.
  // Oil & Gas Midstream — EPROD POC (4 proposal use cases + 2 wow use cases).
  { id: 'pb-eprod-1', name: 'Invoice Intelligence',             industry: 'oil_gas_midstream', status: 'deployed', description: 'EPROD · InvoiceAgent · 6 actions · Vendor PDF/DOCX/XLSX → extract + validate against contracts + MSAs · 70-80% review-time reduction' },
  { id: 'pb-eprod-2', name: 'PO-to-Contract Validation',        industry: 'oil_gas_midstream', status: 'deployed', description: 'EPROD · POAgent · 5 actions · Pre-pay PO line-item validation against contracted rates, billing terms, tax codes · cycle weeks → minutes' },
  { id: 'pb-eprod-3', name: 'Non-PO MSA Validation',            industry: 'oil_gas_midstream', status: 'deployed', description: 'EPROD · VendorAgent · 5 actions · At-intake validation of non-PO transactions against active MSAs · audit-ready evidence' },
  { id: 'pb-eprod-4', name: 'Engineering Quote Processing',     industry: 'oil_gas_midstream', status: 'deployed', description: 'EPROD · QuoteAgent · 5 actions · Heterogeneous quote intake → reconcile with historical pricing + PO/invoice chain' },
  { id: 'pb-eprod-5', name: 'FERC Tariff Sheet Validation',     industry: 'oil_gas_midstream', status: 'deployed', description: 'EPROD · TariffAgent · 6 actions · Extract effective FERC tariff + validate every shipper invoice line against gas-day-effective rates · WOW use case' },
  { id: 'pb-eprod-6', name: 'JIB Reconciliation vs AFE',        industry: 'oil_gas_midstream', status: 'deployed', description: 'EPROD · JIBAgent · 6 actions · JV partner JIB statements matched to AFEs + working-interest math + scope-bounds enforcement · WOW use case' },
];

/** Generic playbooks — used ONLY when the API returned zero items (offline mode). */
const GENERIC_SAMPLE_PLAYBOOKS: PlaybookItem[] = [
  { id: 'pb-1',  name: 'Invoice Processing & Validation', industry: 'financial_services',    status: 'deployed', description: 'Bedrock Data Automation · 8 actions · Last run 2 min ago' },
  { id: 'pb-2',  name: 'Loan Application Intake',         industry: 'financial_services',    status: 'deployed', description: 'Bedrock Agents · 12 actions · Last run 1 hr ago' },
  { id: 'pb-3',  name: 'KYC Document Verification',       industry: 'financial_services',    status: 'draft',    description: 'Bedrock Data Automation · 6 actions · Never run' },
  { id: 'pb-4',  name: 'Claims Intake & Triage',          industry: 'insurance_underwriting',status: 'deployed', description: 'Bedrock Agents · 14 actions · Last run 30 min ago' },
  { id: 'pb-5',  name: 'CRE Underwriting Submission',     industry: 'insurance_underwriting',status: 'deployed', description: 'Bedrock Agents · 10 actions · Last run 4 hr ago' },
  { id: 'pb-6',  name: 'RFP Response Generation',         industry: 'aerospace_defense',     status: 'deployed', description: 'Bedrock Agents · 9 actions · Last run 6 hr ago' },
  { id: 'pb-7',  name: 'CNC Code Review & Optimization',  industry: 'aerospace_defense',     status: 'idle',     description: 'Bedrock Agents · 7 actions · Last run 2 days ago' },
  { id: 'pb-8',  name: 'Production Line QC Monitoring',   industry: 'supply_manufacturing',         status: 'deployed', description: 'Bedrock Agents · 9 actions · Last run 18 min ago' },
  { id: 'pb-9',  name: 'Supplier PO Matching',            industry: 'supply_manufacturing',         status: 'deployed', description: 'Bedrock Data Automation · 6 actions · Last run 42 min ago' },
  { id: 'pb-10', name: 'Work Order Routing & Scheduling', industry: 'supply_manufacturing',         status: 'draft',    description: 'Bedrock Agents · 8 actions · Never run' },
];

const CBB_BLUEPRINTS: BlueprintItem[] = [
  { id: 'bp-cbb-order',    name: 'Order Modification Form v2.1', industry: 'supply_manufacturing', field_count: 12, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/order-mod-v2.1' },
  { id: 'bp-cbb-qc',       name: 'QC Certificate v3.0',          industry: 'supply_manufacturing',      field_count: 18, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/qc-cert-v3.0' },
  { id: 'bp-cbb-disrupt',  name: 'Supplier Delay Alert v1.0',    industry: 'supply_manufacturing',       field_count: 14, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/supplier-alert-v1.0' },
  // STP Phase 2 blueprints — 6 document types covering the 4 use cases.
  { id: 'bp-stp-hr-policy',     name: 'STP HR Policy Document',   industry: 'nuclear_operations', field_count: 14, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/hr-policy-v1' },
  { id: 'bp-stp-procedure',     name: 'STP Plant Procedure',       industry: 'nuclear_operations', field_count: 18, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/procedure-v1' },
  { id: 'bp-stp-work-order',    name: 'STP Work Order Record',     industry: 'nuclear_operations', field_count: 16, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/work-order-v1' },
  { id: 'bp-stp-work-package',  name: 'STP Scanned Work Package',  industry: 'nuclear_operations', field_count: 22, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/work-package-v1' },
  { id: 'bp-stp-incident',      name: 'STP Incident / CR Report',  industry: 'nuclear_operations', field_count: 17, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/incident-v1' },
  { id: 'bp-stp-sensor',        name: 'STP Sensor Telemetry Schema', industry: 'nuclear_operations', field_count: 6,  status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/sensor-v1' },
  // Telecommunications — Verizon Far Edge POC (5 blueprints mirroring the JSON on disk).
  { id: 'bp-tel-robot',     name: 'ROBOT Framework Test Output',          industry: 'telecommunications', field_count: 12, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/robot-framework-v1' },
  { id: 'bp-tel-redfish',   name: 'Redfish Schema Diff Analyzer',         industry: 'telecommunications', field_count:  8, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/redfish-schema-v1' },
  { id: 'bp-tel-runbook',   name: 'Upgrade Runbook Extractor',            industry: 'telecommunications', field_count: 10, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/upgrade-runbook-v1' },
  { id: 'bp-tel-kb',        name: 'Known Issues KB Article',              industry: 'telecommunications', field_count: 11, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/known-issues-v1' },
  { id: 'bp-tel-cert-rpt',  name: 'Certification Report Generator',       industry: 'telecommunications', field_count: 18, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/certification-report-v1' },
  // Oil & Gas Midstream — EPROD POC blueprints (4 proposal + 2 wow).
  { id: 'bp-eprod-invoice',  name: 'EPROD Vendor Invoice',                industry: 'oil_gas_midstream', field_count: 14, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/invoice-v1' },
  { id: 'bp-eprod-po',       name: 'EPROD Purchase Order',                industry: 'oil_gas_midstream', field_count: 16, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/purchase-order-v1' },
  { id: 'bp-eprod-msa',      name: 'EPROD Master Service Agreement',      industry: 'oil_gas_midstream', field_count: 12, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/msa-v1' },
  { id: 'bp-eprod-quote',    name: 'EPROD Engineering Quote',             industry: 'oil_gas_midstream', field_count: 13, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/engineering-quote-v1' },
  { id: 'bp-eprod-tariff',   name: 'EPROD FERC Tariff Sheet',             industry: 'oil_gas_midstream', field_count: 15, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/ferc-tariff-v1' },
  { id: 'bp-eprod-jib',      name: 'EPROD JIB Statement',                 industry: 'oil_gas_midstream', field_count: 14, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/jib-statement-v1' },
];

const GENERIC_SAMPLE_BLUEPRINTS: BlueprintItem[] = [
  { id: 'bp-1', name: 'Invoice Blueprint',           industry: 'financial_services',    field_count: 12, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:...' },
  { id: 'bp-2', name: 'Claim Form Blueprint',        industry: 'insurance_underwriting',field_count: 18, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:...' },
  { id: 'bp-3', name: 'Defense Contract Blueprint',  industry: 'aerospace_defense',     field_count: 24, status: 'draft' },
  { id: 'bp-4', name: 'Bill of Materials v2',        industry: 'supply_manufacturing',         field_count: 22, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:...' },
  { id: 'bp-5', name: 'Purchase Order (Supplier) v1', industry: 'supply_manufacturing',        field_count: 16, status: 'deployed', arn: 'arn:aws:bedrock:us-east-1:...' },
  { id: 'bp-6', name: 'Work Order Blueprint',        industry: 'supply_manufacturing',         field_count: 14, status: 'draft' },
];

/**
 * Merges live API data with required demo cards while removing duplicates.
 *
 *  1. CBB demo entries are always included (prepended).
 *  2. API items are deduped by (industry, normalized name) — covers seeders
 *     that inserted rows twice.
 *  3. Generic sample cards are only used as an offline fallback (API empty).
 */
/**
 * Merge live API data with hardcoded sample arrays.
 *
 * Source-of-truth rules:
 *   1. If the API returned ≥1 item → render API data ONLY. Hardcoded
 *      `demoItems` and `offlineFallback` are suppressed entirely. This is
 *      what makes the platform feel "live" — DynamoDB rows are the truth.
 *   2. If the API returned 0 items (or undefined → still loading / offline)
 *      → fall back to demoItems + offlineFallback so the page is never empty.
 *
 * Dedup is applied within each source by `industry::name` so two rows that
 * obviously refer to the same playbook never appear twice.
 *
 * Earlier behavior prepended `demoItems` even when API succeeded, which
 * caused the user-reported "everything looks hardcoded" bug — the demo
 * arrays carried hardcoded ids like `pb-stp-1` that were duplicated by the
 * live UUIDs from DynamoDB. Both rendered. Now: API wins.
 */
function useDedupedList<T extends { id: string; name: string; industry?: string }>(
  apiItems: T[] | undefined,
  demoItems: T[],
  offlineFallback: T[],
): T[] {
  const keyOf = (x: T) =>
    `${(x.industry || 'other').trim().toLowerCase()}::${(x.name || '').trim().toLowerCase()}`;

  const dedup = (rows: T[]): T[] => {
    const seen = new Set<string>();
    const out: T[] = [];
    for (const r of rows) {
      const k = keyOf(r);
      if (seen.has(k)) continue;
      seen.add(k);
      out.push(r);
    }
    return out;
  };

  // Merge order:
  //   1. API items (authoritative — wins on duplicate key)
  //   2. demoItems (priority hardcoded demos — CBB / STP / Telecom)
  //   3. offlineFallback (generic backups — only render if API + demo missed)
  //
  // Previously this returned API items alone when present, which silently
  // suppressed every hardcoded demo entry the moment the backend was up.
  // The new logic lets us ship the platform with the 3 hero demos visible
  // without first having to run the playbook/blueprint seed endpoints.
  if (apiItems && apiItems.length > 0) {
    return dedup([...apiItems, ...demoItems]);
  }
  return dedup([...demoItems, ...offlineFallback]);
}

/* ═════════════════════ CBB blueprint schemas + panel (spec §3.1) ═════════════════════ */
/* Recipe data for CBB playbooks now lives in pages/canvas/playbook/[id].tsx so it can be
 * edited like every other playbook. Blueprint schema panel stays as a quick preview. */

interface BlueprintSchemaField { name: string; type: string; required: boolean; confidence: number }
interface BlueprintSchemaSpec  {
  id: string;
  name: string;
  industry: string;
  confidence: number;
  fields: BlueprintSchemaField[];
}

const CBB_BLUEPRINT_SCHEMAS: Record<string, BlueprintSchemaSpec> = {
  'bp-cbb-order': {
    id: 'bp-cbb-order',
    name: 'Order Modification Form v2.1',
    industry: 'Supply Chain & Manufacturing',
    confidence: 97.4,
    fields: [
      { name: 'order_id',                       type: 'string', required: true, confidence: 99.8 },
      { name: 'original_dimensions.width_in',   type: 'number', required: true, confidence: 98.2 },
      { name: 'original_dimensions.height_in',  type: 'number', required: true, confidence: 98.1 },
      { name: 'requested_dimensions.width_in',  type: 'number', required: true, confidence: 97.6 },
      { name: 'requested_dimensions.height_in', type: 'number', required: true, confidence: 97.4 },
      { name: 'distributor_name',               type: 'string', required: true, confidence: 99.1 },
      { name: 'distributor_id',                 type: 'string', required: false, confidence: 96.2 },
      { name: 'product_sku',                    type: 'string', required: true, confidence: 96.8 },
      { name: 'quantity',                       type: 'number', required: true, confidence: 99.4 },
      { name: 'requested_delivery_date',        type: 'date',   required: false, confidence: 94.3 },
      { name: 'reason',                         type: 'string', required: false, confidence: 89.7 },
      { name: 'contact_email',                  type: 'string', required: true, confidence: 98.6 },
    ],
  },
  'bp-cbb-qc': {
    id: 'bp-cbb-qc',
    name: 'QC Certificate v3.0',
    industry: 'Supply Chain & Manufacturing',
    confidence: 99.1,
    fields: [
      { name: 'lot_id',            type: 'string', required: true, confidence: 99.9 },
      { name: 'material',          type: 'string', required: true, confidence: 99.4 },
      { name: 'supplier_name',     type: 'string', required: true, confidence: 99.2 },
      { name: 'supplier_id',       type: 'string', required: true, confidence: 98.7 },
      { name: 'batch_id',          type: 'string', required: true, confidence: 99.1 },
      { name: 'inspection_date',   type: 'date',   required: true, confidence: 99.3 },
      { name: 'inspector_id',      type: 'string', required: true, confidence: 97.4 },
      { name: 'tensile_strength',  type: 'number', required: true, confidence: 99.6 },
      { name: 'tensile_spec_min',  type: 'number', required: true, confidence: 99.8 },
      { name: 'color_delta_e',     type: 'number', required: true, confidence: 98.9 },
      { name: 'color_threshold',   type: 'number', required: true, confidence: 99.2 },
      { name: 'moisture_pct',      type: 'number', required: false, confidence: 97.1 },
      { name: 'density_gcm3',      type: 'number', required: false, confidence: 96.8 },
      { name: 'quantity_kg',       type: 'number', required: true, confidence: 99.4 },
      { name: 'unit_price_usd',    type: 'number', required: true, confidence: 98.6 },
      { name: 'plant_destination', type: 'string', required: true, confidence: 98.3 },
      { name: 'pass_fail',         type: 'enum',   required: true, confidence: 99.9 },
      { name: 'variance_pct',      type: 'number', required: true, confidence: 99.1 },
    ],
  },
  'bp-cbb-disrupt': {
    id: 'bp-cbb-disrupt',
    name: 'Supplier Delay Alert v1.0',
    industry: 'Supply Chain & Manufacturing',
    confidence: 98.7,
    fields: [
      { name: 'alert_id',           type: 'string', required: true, confidence: 99.9 },
      { name: 'event_type',         type: 'enum',   required: true, confidence: 99.6 },
      { name: 'port',               type: 'string', required: true, confidence: 99.1 },
      { name: 'affected_supplier',  type: 'string', required: true, confidence: 99.3 },
      { name: 'supplier_id',        type: 'string', required: true, confidence: 98.8 },
      { name: 'material',           type: 'string', required: true, confidence: 99.2 },
      { name: 'material_grade',     type: 'string', required: false, confidence: 97.4 },
      { name: 'delay_days',         type: 'number', required: true, confidence: 98.9 },
      { name: 'severity',           type: 'enum',   required: true, confidence: 99.7 },
      { name: 'alert_timestamp',    type: 'date',   required: true, confidence: 99.8 },
      { name: 'expected_recovery',  type: 'date',   required: false, confidence: 96.2 },
      { name: 'source_confidence',  type: 'number', required: true, confidence: 99.5 },
      { name: 'region',             type: 'string', required: true, confidence: 98.7 },
      { name: 'notes',              type: 'string', required: false, confidence: 91.4 },
    ],
  },
};

function SchemaPanel({ blueprint, onClose }: { blueprint: BlueprintSchemaSpec; onClose: () => void }) {
  return (
    <>
      <div
        onClick={onClose}
        style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.25)', zIndex: 95 }}
      />
      <aside
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0, width: 540, zIndex: 96,
          background: '#fff', boxShadow: '-12px 0 32px rgba(15,23,42,.08)',
          display: 'flex', flexDirection: 'column',
        }}
      >
        <div style={{ padding: '18px 22px', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8' }}>Blueprint Schema</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{blueprint.name}</h3>
            </div>
            <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#9ca3af' }}>
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 10, fontSize: 12, color: '#64748b', flexWrap: 'wrap' }}>
            <span className="chip-blue">{blueprint.industry}</span>
            <span>{blueprint.fields.length} fields</span>
            <span style={{ color: '#16a34a', fontWeight: 600 }}>{blueprint.confidence.toFixed(1)}% avg confidence</span>
          </div>
        </div>

        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 0 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#64748b', background: '#f8fafc' }}>
                <th style={{ padding: '10px 16px', fontWeight: 600 }}>Field</th>
                <th style={{ padding: '10px 8px',  fontWeight: 600 }}>Type</th>
                <th style={{ padding: '10px 8px',  fontWeight: 600 }}>Required</th>
                <th style={{ padding: '10px 16px', fontWeight: 600, textAlign: 'right' }}>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {blueprint.fields.map((f) => {
                const confColor = f.confidence >= 95 ? '#16a34a' : f.confidence >= 85 ? '#d97706' : '#dc2626';
                return (
                  <tr key={f.name} style={{ borderTop: '1px solid #f1f5f9' }}>
                    <td className="mono" style={{ padding: '10px 16px', color: '#0f172a' }}>{f.name}</td>
                    <td style={{ padding: '10px 8px' }}>
                      <span style={{
                        fontSize: 10, fontWeight: 600, padding: '2px 6px', borderRadius: 4,
                        background: '#eff6ff', color: '#2563eb',
                      }}>{f.type}</span>
                    </td>
                    <td style={{ padding: '10px 8px' }}>
                      {f.required ? (
                        <span style={{
                          fontSize: 10, fontWeight: 700, padding: '1px 5px', borderRadius: 3,
                          background: '#fee2e2', color: '#b91c1c',
                        }}>YES</span>
                      ) : (
                        <span style={{ fontSize: 11, color: '#94a3b8' }}>—</span>
                      )}
                    </td>
                    <td style={{ padding: '10px 16px', textAlign: 'right', color: confColor, fontWeight: 600 }}>
                      {f.confidence.toFixed(1)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div style={{ padding: '14px 22px', borderTop: '1px solid #f1f5f9', display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary btn-sm" onClick={onClose}>Close</button>
          <button className="btn btn-primary btn-sm">Test Extraction</button>
        </div>
      </aside>
    </>
  );
}
