/**
 * Actions — Action Gallery. Ported from apex-prototype 2/actions.html.
 *
 * Data policy: if the /actions API returns real actions, we group those
 * by industry. Otherwise we fall back to the HTML sample data so the
 * page still looks right in local dev without the backend.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import { useQuery } from '@tanstack/react-query';
import { DataSourceBanner, type DataSource } from '@/components/AppShell/DataSourceBanner';
import { useDemoMode } from '@/lib/demoMode';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type ActionType = 'extract' | 'validate' | 'route' | 'notify' | 'execute' | 'store' | 'classify';
type TypeFilter = 'all' | ActionType;
type IndustryKey =
  | 'all'                          // core / cross-domain actions reusable everywhere
  | 'financial'
  | 'healthcare'
  | 'insurance'
  | 'aerospace'
  | 'supply_manufacturing'
  | 'nuclear'
  | 'telecommunications'           // Carrier far-edge / RAN / network deployment
  | 'oil_gas_midstream'            // Pipeline / NGL / crude midstream operators — EPROD demo
  // Agentic Enterprise — 3 specific industry domains. Each domain matches
  // its own actions PLUS core/all actions (handled in the demoMode filter
  // by `a.industry !== 'all'`).
  | 'supply_chain_orchestrator'    // UC-1
  | 'hospitality'                  // UC-2
  | 'commercial_real_estate';      // UC-3

/** A JSON-Schema-ish leaf used by the backend's action registry:
 *   { field_name: { type: "string", description?: "..." } }
 * Some actions return primitives (e.g. { type: "string" }); others return
 * nested objects. We accept both. */
export type SchemaField =
  | { type?: string; description?: string; [k: string]: unknown }
  | string; // tolerant for older records

export type ActionSchema = Record<string, SchemaField>;

interface ActionItem {
  id: string;
  name: string;
  description: string;
  type: ActionType;
  industry: IndustryKey;
  runs: number;
  active: boolean;
  section: string; // "Core Actions", "Financial Services", etc
  sectionKey: IndustryKey;
  input_schema?: ActionSchema;
  output_schema?: ActionSchema;
  /** CBB demos this action powers, e.g. [1, 3] → "Demos 1, 3". Undefined if not CBB-relevant. */
  usedInDemos?: number[];
}

interface DetailTab {
  id: 'schema' | 'test' | 'usage' | 'code';
  label: string;
}

export default function ActionsPage() {
  const [activeType, setActiveType] = useState<TypeFilter>('all');
  const [activeIndustry, setActiveIndustry] = useState<IndustryKey>('all');
  const [search, setSearch] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [selected, setSelected] = useState<ActionItem | null>(null);
  const [detailTab, setDetailTab] = useState<DetailTab['id']>('schema');
  // Demo-mode filter: when 'stp', collapse the gallery to Nuclear Operations
  // (+ core actions) only. Re-renders automatically when the user flips the
  // toggle in Settings — see lib/demoMode.ts custom event.
  const [demoMode] = useDemoMode();

  // The sticky-positioned right panel only sticks WITHIN its grid cell. If
  // the user clicks an action card that's far down the page (e.g. the
  // Agentic Enterprise sections that render below Core/CBB), the gallery
  // pushes the right column's grid cell taller than the viewport — sticky
  // anchors at top:80 of the cell, but that anchor is below what the user
  // sees. Net effect: clicking the card "did nothing" visually because the
  // panel was below the fold.
  // Fix: scroll the panel container into view on every selection change.
  const detailPanelRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (!selected) return;
    detailPanelRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, [selected?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Data sources are MERGED, not ranked, so one source can't mask another:
  //   • Registry  (/actions/registry/discover?fresh=true) — source of truth for
  //     schemas, descriptions, handler paths. Re-parsed from disk every call.
  //   • Cosmos DB  (/actions/)                              — source of truth for
  //     invocation_count and any custom actions that only exist in the DB
  //     (e.g. insurance actions added via /actions/seed-insurance).
  //   • Sample    (SAMPLE_ACTIONS in this file)            — offline fallback.
  //
  // We fetch both; if the registry has an entry, it wins on schema/description
  // but inherits runs count from Cosmos DB. Actions present only in Cosmos DB
  // are carried through unchanged. Only when both fail do we return 'mock'.
  const q = useQuery<{ items: ActionItem[]; source: DataSource }>({
    queryKey: ['actions'],
    queryFn: async () => {
      const [registryActions, dbActions] = await Promise.all([
        fetchRegistryActions(),
        fetchDbActions(),
      ]);

      if (registryActions.length === 0 && dbActions.length === 0) {
        return { items: [], source: 'mock' as DataSource };
      }

      // Index DB actions by id so we can graft invocation counts onto registry rows.
      const dbById = new Map(dbActions.map((a) => [a.id, a]));
      const merged: ActionItem[] = registryActions.map((reg) => {
        const db = dbById.get(reg.id);
        if (!db) return reg;
        dbById.delete(reg.id);
        return {
          ...reg,
          // Runs + active come from DB when it has them (registry doesn't track runs).
          runs: db.runs || reg.runs,
          active: db.active,
        };
      });

      // Carry forward DB-only actions (e.g. cre.* seeded via seed-insurance).
      dbById.forEach((extra) => merged.push(extra));

      // If Cosmos DB was the sole contributor, label it 'api'; otherwise the
      // schemas came from the registry so label honestly.
      const source: DataSource =
        registryActions.length === 0 ? 'api' : 'registry';

      return { items: merged, source };
    },
    retry: false,
    staleTime: 0,
    refetchOnMount: 'always',
  });

  const source: DataSource = q.isLoading ? 'loading' : (q.data?.source ?? 'mock');

  // Merge strategy:
  //   • No API data → render the full SAMPLE_ACTIONS set (offline mode).
  //   • API data present → render API rows PLUS the 14 CBB demo actions
  //     (cbb-*) which are Foundry Agent Service Strands tools, not Lambda handlers,
  //     and therefore not surfaced by the registry. Dedup by lowercased
  //     name so a same-name backend handler wins.
  //
  // Agentic Enterprise actions used to live in SAMPLE_ACTIONS (ae-*) but
  // are now seeded into Cosmos DB via /api/v1/actions/seed-agentic-enterprise
  // so they come through the standard API path identical to every other
  // industry — same shape, same render path, same click handler.
  const all: ActionItem[] = useMemo(() => {
    const apiItems = q.data?.items ?? [];
    if (apiItems.length === 0) return SAMPLE_ACTIONS;
    // Merge in every hero-demo entry that the registry doesn't already cover.
    // Prefixes:
    //   • cbb-*  (CBB Foundry Agent Service Strands tools — not Lambda handlers)
    //   • stp-*  (STP nuclear demo)
    //   • tel-*  (Verizon Telecommunications — 12 actions)
    //   • core-7..11 (telecom-introduced platform actions: jira_create_ticket,
    //                 jira_create_epic, site_inventory_load, wave_authorization,
    //                 audit_log_emit). Earlier core-1..6 already come through
    //                 the registry — including them here would dedup harmlessly,
    //                 but we keep the prefix scoped to avoid noise.
    const demoOnly = SAMPLE_ACTIONS.filter((a) => {
      if (a.id.startsWith('cbb-')) return true;
      if (a.id.startsWith('stp-')) return true;
      if (a.id.startsWith('tel-')) return true;
      // Only the *new* core entries (core-7 and above). core-1..6 are already
      // served by the registry.
      const m = a.id.match(/^core-(\d+)$/);
      if (m && parseInt(m[1], 10) >= 7) return true;
      return false;
    });
    const seen = new Set(apiItems.map((a) => a.name.toLowerCase()));
    const extras = demoOnly.filter((a) => !seen.has(a.name.toLowerCase()));
    return [...apiItems, ...extras];
  }, [q.data]);

  // Map demoMode (canonical industry key) → short IndustryKey used by this
  // page's local taxonomy. Lets the `=== 'stp'` legacy carry over cleanly.
  const demoModeIndustryFilter: IndustryKey | null =
    demoMode === 'all'                       ? null
  : demoMode === 'nuclear_operations'        ? 'nuclear'
  : demoMode === 'stp'                       ? 'nuclear'
  : demoMode === 'financial_services'        ? 'financial'
  : demoMode === 'insurance_underwriting'    ? 'insurance'
  : demoMode === 'aerospace_defense'         ? 'aerospace'
  : demoMode === 'supply_manufacturing'      ? 'supply_manufacturing'
  : demoMode === 'manufacturing'             ? 'supply_manufacturing'
  : demoMode === 'supply_chain'              ? 'supply_manufacturing'
  // Agentic Enterprise — each use case collapses to its own action set.
  // Core actions still flow through because the demoMode filter below
  // explicitly lets `a.industry === 'all'` rows pass.
  : demoMode === 'supply_chain_orchestrator' ? 'supply_chain_orchestrator'
  : demoMode === 'hospitality'               ? 'hospitality'
  : demoMode === 'commercial_real_estate'    ? 'commercial_real_estate'
  : demoMode === 'telecommunications'        ? 'telecommunications'
  : demoMode === 'verizon_far_edge'          ? 'telecommunications'
  : demoMode === 'oil_gas_midstream'         ? 'oil_gas_midstream'
  : demoMode === 'eprod'                     ? 'oil_gas_midstream'
  : (demoMode.startsWith('healthcare')       ? 'healthcare' : null);

  // Apply filters
  const filtered = useMemo(() => {
    const term = search.trim().toLowerCase();
    return all.filter((a) => {
      // Demo mode collapses to a single industry (plus core/all reusables).
      if (demoModeIndustryFilter
          && a.industry !== demoModeIndustryFilter
          && a.industry !== 'all') return false;
      if (activeType !== 'all' && a.type !== activeType) return false;
      if (activeIndustry !== 'all' && a.industry !== activeIndustry) return false;
      if (term && !(a.name.toLowerCase().includes(term) || a.description.toLowerCase().includes(term))) return false;
      return true;
    });
  }, [all, activeType, activeIndustry, search, demoModeIndustryFilter]);

  // Group by section
  const sections = useMemo(() => {
    const groups: Record<string, ActionItem[]> = {};
    filtered.forEach((a) => {
      (groups[a.section] = groups[a.section] || []).push(a);
    });
    return Object.entries(groups);
  }, [filtered]);

  // Counts by type for the hero cards
  const counts = useMemo(() => {
    const c: Record<TypeFilter, number> = {
      all: all.length,
      extract: 0, validate: 0, route: 0, notify: 0, execute: 0, store: 0, classify: 0,
    };
    all.forEach((a) => {
      c[a.type] = (c[a.type] || 0) + 1;
    });
    return c;
  }, [all]);

  return (
    <>
      <Head><title>Actions | APEX</title></Head>

      <DataSourceBanner
        source={source}
        entity="actions"
        hint={source === 'mock'
          ? 'Start backend: cd backend && uvicorn main:app --reload'
          : 'Schemas + descriptions come from the handler files. Run curl -X POST http://localhost:8000/api/v1/actions/registry/register-all to also persist invocation counts to Cosmos DB.'}
      />

      {/* Page Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 28 }}>
        <div>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: '#0f172a', letterSpacing: '-.02em' }}>Action Gallery</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>Reusable atomic operations that power every Playbook and Pipeline</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn btn-primary">
          <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Action
        </button>
      </div>

      {/* Action Type Hero Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7,1fr)', gap: 10, marginBottom: 28 }}>
        {TYPE_CARDS.map((t) => (
          <TypeHeroCard
            key={t.key}
            data={t}
            active={activeType === t.key}
            count={counts[t.key] ?? 0}
            onClick={() => setActiveType(t.key)}
          />
        ))}
      </div>

      {/* Search + Industry Filter Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
        <div style={{ position: 'relative', flex: 1, maxWidth: 360 }}>
          <svg
            style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', width: 16, height: 16, color: '#9ca3af' }}
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search actions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px 10px 36px',
              fontSize: 13,
              background: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: 12,
              outline: 'none',
              fontFamily: 'inherit',
              color: '#111827',
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = '#93c5fd'; e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59,130,246,.1)'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.boxShadow = 'none'; }}
          />
        </div>
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {INDUSTRY_FILTERS
            // Demo mode collapses the visible industry chips to:
            //   • All Industries  (always visible — lets the user widen back)
            //   • The active demoMode's industry (so the user can confirm it)
            // 'core' / 'all' actions are still rendered in the gallery
            // because the demoModeIndustryFilter explicitly admits them.
            .filter((ind) => {
              if (!demoModeIndustryFilter) return true;        // all-industries mode
              return ind.key === 'all' || ind.key === demoModeIndustryFilter;
            })
            .map((ind) => (
              <IndustryButton
                key={ind.key}
                label={ind.label}
                active={activeIndustry === ind.key}
                onClick={() => setActiveIndustry(ind.key)}
              />
            ))}
        </div>
        <div style={{ marginLeft: 'auto', fontSize: 13, color: '#94a3b8' }}>
          Showing {filtered.length} action{filtered.length === 1 ? '' : 's'}
        </div>
      </div>


      {/* Main layout: Gallery + Detail Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 20, alignItems: 'start' }}>
        {/* Gallery */}
        <div>
          {sections.length === 0 && (
            <div style={{ padding: 40, textAlign: 'center', color: '#94a3b8', fontSize: 14 }}>
              No actions match the current filters.
            </div>
          )}
          {sections.map(([section, items]) => (
            <ActionSection
              key={section}
              section={section}
              sectionKey={items[0]?.sectionKey || 'all'}
              items={items}
              selectedId={selected?.id}
              onSelect={(a) => { setSelected(a); setDetailTab('schema'); }}
            />
          ))}
        </div>

        {/* Detail Panel (sticky). The wrapping div uses an explicit ref so
            we can scroll it into view when the user clicks an action card
            from below the fold — the panel was getting selected correctly
            but the user's viewport was scrolled past it (sticky positioning
            only kicks in within the grid cell). The useEffect above
            scrollIntoView's this div on every selection change. */}
        <div
          ref={detailPanelRef}
          style={{ position: 'sticky', top: 80, minHeight: 200, scrollMarginTop: 80 }}
        >
          {!selected ? (
            <EmptyDetail />
          ) : (
            <FilledDetail
              // key ensures TestTab/UsageTab local state resets on action switch
              key={selected.id}
              action={selected}
              tab={detailTab}
              onTab={setDetailTab}
              onClose={() => setSelected(null)}
            />
          )}
        </div>
      </div>

      {showCreate && <CreateActionModal onClose={() => setShowCreate(false)} />}
    </>
  );
}

/* ─────────── type hero card ─────────── */

function TypeHeroCard({
  data, active, count, onClick,
}: {
  data: TypeCardSpec;
  active: boolean;
  count: number;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        textAlign: 'center',
        padding: '16px 10px',
        borderRadius: 14,
        cursor: 'pointer',
        border: active ? '1.5px solid #0f172a' : '1.5px solid #e2e8f0',
        background: active ? '#0f172a' : '#fff',
        transition: 'all .15s',
      }}
    >
      <div
        style={{
          width: 38, height: 38, borderRadius: 10,
          background: active ? 'rgba(255,255,255,.1)' : data.iconBg,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 8px',
        }}
      >
        <svg style={{ width: 18, height: 18, color: active ? '#fff' : data.iconColor }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={data.iconPath} />
        </svg>
      </div>
      <div style={{ fontSize: 12, fontWeight: 700, color: active ? '#fff' : '#0f172a' }}>{data.label}</div>
      <div style={{ fontSize: 11, color: active ? 'rgba(255,255,255,.5)' : '#94a3b8', marginTop: 2 }}>
        {count} action{count === 1 ? '' : 's'}
      </div>
    </div>
  );
}

function IndustryButton({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '7px 14px',
        borderRadius: 10,
        fontSize: 12,
        fontWeight: 600,
        cursor: 'pointer',
        border: '1px solid #e2e8f0',
        background: active ? '#0f172a' : '#fff',
        color: active ? '#fff' : '#475569',
        transition: 'all .15s',
      }}
    >
      {label}
    </button>
  );
}

/* ─────────── sections & cards ─────────── */

function ActionSection({
  section, sectionKey, items, selectedId, onSelect,
}: {
  section: string;
  sectionKey: IndustryKey;
  items: ActionItem[];
  selectedId?: string;
  onSelect: (a: ActionItem) => void;
}) {
  const theme = SECTION_THEME[sectionKey] || SECTION_THEME.all;
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
        <div
          style={{
            width: 28, height: 28, borderRadius: 8,
            background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <svg style={{ width: 14, height: 14, color: theme.color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.iconPath} />
          </svg>
        </div>
        <h3 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>{section}</h3>
        <span
          style={{
            fontSize: 11, color: '#94a3b8', background: '#f8fafc',
            border: '1px solid #f1f5f9', padding: '2px 8px', borderRadius: 99,
          }}
        >
          {items.length} action{items.length === 1 ? '' : 's'}
        </span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12, marginBottom: 28 }}>
        {items.map((a) => (
          <ActionCard
            key={a.id}
            action={a}
            selected={a.id === selectedId}
            onClick={() => onSelect(a)}
          />
        ))}
      </div>
    </div>
  );
}

function ActionCard({ action, selected, onClick }: { action: ActionItem; selected: boolean; onClick: () => void }) {
  const theme = TYPE_THEME[action.type];
  return (
    <div
      onClick={onClick}
      style={{
        background: '#fff',
        border: selected ? '1.5px solid #3b82f6' : '1.5px solid #f1f5f9',
        boxShadow: selected ? '0 0 0 3px rgba(59,130,246,.15)' : undefined,
        borderRadius: 16,
        padding: 18,
        cursor: 'pointer',
        transition: 'all .18s',
        position: 'relative',
      }}
      onMouseOver={(e) => {
        if (selected) return;
        e.currentTarget.style.borderColor = '#bfdbfe';
        e.currentTarget.style.boxShadow = '0 6px 20px rgba(59,130,246,.1)';
        e.currentTarget.style.transform = 'translateY(-2px)';
      }}
      onMouseOut={(e) => {
        if (selected) return;
        e.currentTarget.style.borderColor = '#f1f5f9';
        e.currentTarget.style.boxShadow = '';
        e.currentTarget.style.transform = '';
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
        <div
          style={{
            width: 40, height: 40, borderRadius: 12,
            background: theme.iconBg, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <svg style={{ width: 20, height: 20, color: theme.iconColor }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.iconPath} />
          </svg>
        </div>
        <span className={`tag tag-${action.type}`}>{cap(action.type)}</span>
      </div>
      <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>{action.name}</div>
      <div style={{ fontSize: 12, color: '#64748b', lineHeight: 1.5, marginBottom: 12 }}>{action.description}</div>
      {action.usedInDemos && action.usedInDemos.length > 0 && (
        <div style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span
            style={{
              fontSize: 9, fontWeight: 700, letterSpacing: '.08em',
              padding: '2px 6px', borderRadius: 4,
              background: '#0f172a', color: '#f8fafc',
            }}
          >
            CBB DEMO{action.usedInDemos.length > 1 ? 'S' : ''} · {action.usedInDemos.join(', ')}
          </span>
        </div>
      )}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: '#94a3b8' }}>
          <svg style={{ width: 12, height: 12 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          {action.runs.toLocaleString()} runs
        </div>
        <span className="chip-green" style={{ fontSize: 10 }}>{action.active ? 'Active' : 'Draft'}</span>
      </div>
    </div>
  );
}

/* ─────────── detail panel ─────────── */

function EmptyDetail() {
  return (
    <div
      style={{
        background: '#fff',
        border: '1.5px dashed #e2e8f0',
        borderRadius: 20,
        padding: '40px 24px',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: 56, height: 56, borderRadius: 16, background: '#f8fafc',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          margin: '0 auto 16px',
        }}
      >
        <svg style={{ width: 28, height: 28, color: '#cbd5e1' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <div style={{ fontSize: 15, fontWeight: 600, color: '#64748b', marginBottom: 6 }}>Select an action</div>
      <div style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.5 }}>
        Click any action card to view details, schema, and run a live test
      </div>
    </div>
  );
}

function FilledDetail({
  action, tab, onTab, onClose,
}: {
  action: ActionItem;
  tab: DetailTab['id'];
  onTab: (t: DetailTab['id']) => void;
  onClose: () => void;
}) {
  // Defensive theme lookup: falls back to 'execute' if a future action
  // arrives with an unknown type. Keeps the panel from white-screening on
  // schema drift between backend and frontend ActionType enum.
  const safeTheme = TYPE_THEME[action.type] || TYPE_THEME.execute;

  return (
    <div
      style={{
        background: '#fff',
        border: '1.5px solid #f1f5f9',
        borderRadius: 20,
        overflow: 'hidden',
        boxShadow: '0 4px 24px rgba(0,0,0,.06)',
      }}
    >
      {/* Header */}
      <div style={{ padding: '20px 20px 16px', borderBottom: '1px solid #f8fafc' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
          <div
            style={{
              width: 44, height: 44, borderRadius: 13,
              background: safeTheme.iconBg, display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <svg style={{ width: 22, height: 22, color: safeTheme.iconColor }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={safeTheme.iconPath} />
            </svg>
          </div>
          <button
            onClick={onClose}
            style={{ padding: 6, background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', borderRadius: 8 }}
            onMouseOver={(e) => (e.currentTarget.style.background = '#f8fafc')}
            onMouseOut={(e) => (e.currentTarget.style.background = 'none')}
          >
            <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div style={{ fontSize: 16, fontWeight: 800, color: '#0f172a', marginBottom: 4 }}>{action.name}</div>
        <div style={{ fontSize: 12, color: '#64748b', lineHeight: 1.5, marginBottom: 10 }}>{action.description}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className={`tag tag-${action.type}`}>{cap(action.type)}</span>
          <span className="chip-green" style={{ fontSize: 10 }}>Active · v2.1.0</span>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #f8fafc' }}>
        {(['schema', 'test', 'code', 'usage'] as const).map((k) => (
          <button
            key={k}
            onClick={() => onTab(k)}
            style={{
              flex: 1,
              padding: 10,
              fontSize: 12,
              fontWeight: 600,
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: tab === k ? '#2563eb' : '#94a3b8',
              borderBottom: tab === k ? '2px solid #2563eb' : '2px solid transparent',
            }}
          >
            {k === 'schema' ? 'Schema' : k === 'test' ? 'Test Runner' : k === 'code' ? 'Code' : 'Usage'}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'schema' && <SchemaTab action={action} />}
      {tab === 'test'   && <TestTab   action={action} />}
      {tab === 'code'   && <CodeTab   action={action} />}
      {tab === 'usage'  && <UsageTab  action={action} />}

      {/* Footer actions */}
      <div style={{ padding: '14px 16px', borderTop: '1px solid #f8fafc', display: 'flex', gap: 8 }}>
        <button
          className="btn btn-secondary btn-sm"
          style={{ flex: 1, justifyContent: 'center' }}
          onClick={() => onTab('code')}
          title="Open the Code tab with the Python handler source"
        >
          <svg style={{ width: 13, height: 13 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          View Code
        </button>
        <a
          className="btn btn-secondary btn-sm"
          style={{ flex: 1, justifyContent: 'center' }}
          href={awsConsoleUrl(action)}
          target="_blank"
          rel="noopener noreferrer"
          title="Open the backing AWS resource in a new tab"
        >
          <svg style={{ width: 13, height: 13 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          AWS Console
        </a>
        <button className="btn btn-primary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>
          <svg style={{ width: 13, height: 13 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add to Playbook
        </button>
      </div>
    </div>
  );
}

function SchemaTab({ action }: { action: ActionItem }) {
  const hasAny = !!(action.input_schema || action.output_schema);
  return (
    <div style={{ padding: 16 }}>
      <SchemaSection
        label="Input Parameters"
        schema={action.input_schema}
        emptyHint="No input schema registered for this action."
      />
      <div style={{ marginTop: 14 }}>
        <SchemaSection
          label="Output Fields"
          schema={action.output_schema}
          emptyHint="No output schema registered for this action."
          output
        />
      </div>
      {!hasAny && (
        <div
          style={{
            marginTop: 14,
            padding: 12,
            background: '#fffbeb',
            border: '1px solid #fde68a',
            borderRadius: 10,
            color: '#92400e',
            fontSize: 12,
            lineHeight: 1.6,
          }}
        >
          This action's handler file doesn't declare a schema via
          <code
            className="mono"
            style={{
              display: 'inline-block',
              margin: '0 4px',
              padding: '1px 6px',
              background: '#fff',
              border: '1px solid #fde68a',
              borderRadius: 4,
            }}
          >
            @apex_action(...)
          </code>
          or a <code className="mono">Args:</code> / <code className="mono">Returns:</code> docstring,
          so nothing could be extracted. Add either one to show real fields here.
        </div>
      )}
    </div>
  );
}

function SchemaSection({
  label, schema, emptyHint, output,
}: { label: string; schema?: ActionSchema; emptyHint: string; output?: boolean }) {
  const fields = schema ? Object.entries(schema) : [];
  return (
    <div>
      <div
        style={{
          display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
          marginBottom: 8,
        }}
      >
        <div
          style={{
            fontSize: 11, fontWeight: 700, textTransform: 'uppercase',
            letterSpacing: '.06em', color: '#94a3b8',
          }}
        >
          {label}
        </div>
        <span
          style={{
            fontSize: 10, color: '#94a3b8',
            fontFamily: 'JetBrains Mono, monospace',
          }}
        >
          {fields.length} {fields.length === 1 ? 'field' : 'fields'}
        </span>
      </div>
      {fields.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {fields.map(([name, spec]) => (
            <SchemaRow key={name} name={name} field={spec} output={output} />
          ))}
        </div>
      ) : (
        <div
          style={{
            padding: '10px 12px',
            fontSize: 12,
            color: '#94a3b8',
            background: '#f8fafc',
            border: '1px dashed #e2e8f0',
            borderRadius: 8,
            fontStyle: 'italic',
          }}
        >
          {emptyHint}
        </div>
      )}
    </div>
  );
}

function SchemaRow({ name, field, output }: { name: string; field: SchemaField; output?: boolean }) {
  const type = typeof field === 'string' ? field : (field?.type as string) || 'any';
  const description = typeof field === 'object' ? (field?.description as string | undefined) : undefined;

  const typeColors: Record<string, { bg: string; color: string }> = {
    string:  { bg: '#eff6ff', color: '#2563eb' },
    number:  { bg: '#f0fdf4', color: '#16a34a' },
    integer: { bg: '#f0fdf4', color: '#16a34a' },
    boolean: { bg: '#fef3c7', color: '#b45309' },
    object:  { bg: '#f5f3ff', color: '#7c3aed' },
    array:   { bg: '#fdf4ff', color: '#a21caf' },
    any:     { bg: '#f1f5f9', color: '#475569' },
  };
  const tc = typeColors[type] || typeColors.any;

  return (
    <div
      style={{
        padding: '8px 12px',
        background: output ? '#f0fdf4' : '#f8fafc',
        borderRadius: 8,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
        <span
          className="mono"
          style={{
            fontSize: 12,
            color: output ? '#15803d' : '#1e40af',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {name}
        </span>
        <span
          style={{
            flexShrink: 0,
            fontSize: 10,
            background: tc.bg,
            color: tc.color,
            padding: '2px 6px',
            borderRadius: 4,
            fontWeight: 600,
          }}
        >
          {type}
        </span>
      </div>
      {description && (
        <div
          style={{
            marginTop: 4,
            fontSize: 11,
            color: '#64748b',
            lineHeight: 1.4,
          }}
        >
          {description}
        </div>
      )}
    </div>
  );
}

/* =================== TEST RUNNER =================== */

/** Envelope shape returned by POST /api/v1/actions/registry/invoke/{action_id}. */
interface InvokeEnvelope {
  action_id: string;
  status: 'success' | 'error';
  ok: boolean;
  result: Record<string, unknown> | null;
  error: string | null;
  error_type: 'not_found' | 'load_failed' | 'bad_arguments' | 'runtime' | null;
  traceback: string | null;
  duration_ms: number;
}

type InputMode = 'form' | 'json';

/**
 * TestTab — invokes the selected action with user-supplied inputs and
 * renders the real response. No more mock data.
 */
function TestTab({ action }: { action: ActionItem }) {
  const [mode, setMode] = useState<InputMode>('form');
  const [formValues, setFormValues] = useState<Record<string, unknown>>(() =>
    defaultValuesForSchema(action.input_schema),
  );
  const [jsonText, setJsonText] = useState<string>(() =>
    JSON.stringify(defaultValuesForSchema(action.input_schema), null, 2),
  );
  const [envelope, setEnvelope] = useState<InvokeEnvelope | null>(null);
  const [running, setRunning] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const hasSchema = !!action.input_schema;

  // Identify required fields that are currently empty — used to disable Run.
  const missingRequired = hasSchema
    ? Object.entries(action.input_schema!).reduce<string[]>((acc, [name, field]) => {
        const spec = typeof field === 'object' ? field : {};
        const required = (spec as { required?: boolean }).required;
        if (!required) return acc;
        const v = mode === 'form' ? formValues[name] : undefined;
        if (mode === 'form' && (v === undefined || v === null || v === '')) acc.push(name);
        return acc;
      }, [])
    : [];

  const buildPayload = (): Record<string, unknown> | null => {
    if (mode === 'json') {
      try {
        const parsed = JSON.parse(jsonText || '{}');
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed;
        setLocalError('Top-level JSON must be an object.');
        return null;
      } catch (e) {
        setLocalError(`Invalid JSON: ${(e as Error).message}`);
        return null;
      }
    }
    // Strip empties for optional fields; coerce types on the way out.
    const out: Record<string, unknown> = {};
    const schema = action.input_schema || {};
    Object.entries(formValues).forEach(([k, v]) => {
      const field = schema[k];
      const t = typeof field === 'object' ? (field as { type?: string }).type : undefined;
      if (v === undefined || v === null || v === '') return;
      if (t === 'number' || t === 'integer') {
        const n = Number(v);
        out[k] = Number.isFinite(n) ? n : v;
      } else if (t === 'boolean') {
        out[k] = !!v;
      } else if (t === 'object' || t === 'array') {
        if (typeof v === 'string') {
          try {
            out[k] = JSON.parse(v);
          } catch {
            out[k] = v;
          }
        } else {
          out[k] = v;
        }
      } else {
        out[k] = v;
      }
    });
    return out;
  };

  const run = async () => {
    setLocalError(null);
    const payload = buildPayload();
    if (payload === null) return;

    setRunning(true);
    setEnvelope(null);
    try {
      const r = await fetch(
        `${API_BASE_URL}/actions/registry/invoke/${encodeURIComponent(action.id)}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        },
      );
      const data = (await r.json()) as InvokeEnvelope | { detail?: string };
      if (!r.ok) {
        setLocalError((data as { detail?: string }).detail || `HTTP ${r.status}`);
        return;
      }
      setEnvelope(data as InvokeEnvelope);
    } catch (e) {
      setLocalError(`Network error: ${(e as Error).message}`);
    } finally {
      setRunning(false);
    }
  };

  const copyResponse = () => {
    if (!envelope) return;
    const text = envelope.ok
      ? JSON.stringify(envelope.result ?? {}, null, 2)
      : envelope.error || '';
    if (text) navigator.clipboard?.writeText(text);
  };

  return (
    <div style={{ padding: 16 }}>
      {/* Input mode tabs */}
      {hasSchema && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
          <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>
            Input
          </div>
          <div style={{ display: 'flex', gap: 4, background: '#f1f5f9', borderRadius: 8, padding: 2 }}>
            {(['form', 'json'] as const).map((m) => (
              <button
                key={m}
                onClick={() => {
                  if (mode === m) return;
                  if (m === 'json') {
                    // Sync form → json when switching
                    setJsonText(JSON.stringify(formValues, null, 2));
                  } else {
                    // Sync json → form where possible
                    try {
                      const parsed = JSON.parse(jsonText);
                      if (parsed && typeof parsed === 'object') setFormValues(parsed);
                    } catch { /* keep existing form values */ }
                  }
                  setMode(m);
                }}
                style={{
                  padding: '4px 10px',
                  fontSize: 11,
                  fontWeight: 600,
                  background: mode === m ? '#fff' : 'transparent',
                  color: mode === m ? '#0f172a' : '#64748b',
                  border: 'none',
                  borderRadius: 6,
                  cursor: 'pointer',
                  boxShadow: mode === m ? '0 1px 2px rgba(0,0,0,.08)' : 'none',
                }}
              >
                {m === 'form' ? 'Form' : 'JSON'}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Form or JSON input */}
      {hasSchema && mode === 'form' ? (
        <InputForm
          schema={action.input_schema!}
          values={formValues}
          onChange={setFormValues}
        />
      ) : (
        <textarea
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          spellCheck={false}
          style={{
            width: '100%',
            height: hasSchema ? 140 : 120,
            padding: 10,
            fontSize: 12,
            fontFamily: 'JetBrains Mono, monospace',
            background: '#0d1117',
            color: '#e2e8f0',
            border: '1px solid #374151',
            borderRadius: 10,
            outline: 'none',
            resize: 'vertical',
            lineHeight: 1.6,
          }}
        />
      )}

      {/* Validation hint */}
      {mode === 'form' && missingRequired.length > 0 && (
        <div style={{ marginTop: 8, fontSize: 11, color: '#b45309' }}>
          Required fields missing: <span className="mono">{missingRequired.join(', ')}</span>
        </div>
      )}

      {/* Run button */}
      <button
        onClick={run}
        disabled={running || (mode === 'form' && missingRequired.length > 0)}
        className="btn btn-primary"
        style={{
          width: '100%',
          justifyContent: 'center',
          marginTop: 12,
          marginBottom: 12,
          opacity: running || (mode === 'form' && missingRequired.length > 0) ? 0.6 : 1,
          cursor: running || (mode === 'form' && missingRequired.length > 0) ? 'not-allowed' : 'pointer',
        }}
      >
        {running ? (
          <svg className="animate-spin" style={{ width: 15, height: 15 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        ) : (
          <svg style={{ width: 15, height: 15 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )}
        {running ? 'Running…' : 'Run Test'}
      </button>

      {localError && (
        <div
          style={{
            background: '#fef2f2',
            border: '1px solid #fecaca',
            color: '#b91c1c',
            borderRadius: 10,
            padding: 10,
            fontSize: 12,
            marginBottom: 12,
          }}
        >
          {localError}
        </div>
      )}

      {/* Response rendering */}
      {envelope && <InvokeResult envelope={envelope} onCopy={copyResponse} />}
    </div>
  );
}

/** Dynamic form generator — one widget per field type. */
function InputForm({
  schema, values, onChange,
}: {
  schema: ActionSchema;
  values: Record<string, unknown>;
  onChange: (next: Record<string, unknown>) => void;
}) {
  const entries = Object.entries(schema);
  if (entries.length === 0) {
    return (
      <div style={{ fontSize: 12, color: '#94a3b8', fontStyle: 'italic', padding: '8px 2px' }}>
        This action takes no inputs.
      </div>
    );
  }

  const set = (k: string, v: unknown) => onChange({ ...values, [k]: v });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {entries.map(([name, field]) => {
        const spec = typeof field === 'object' ? field : { type: field };
        const type = (spec as { type?: string }).type || 'string';
        const description = (spec as { description?: string }).description;
        const required = (spec as { required?: boolean }).required;
        const value = values[name];

        return (
          <div key={name}>
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                fontSize: 11,
                fontWeight: 600,
                color: '#334155',
                marginBottom: 4,
              }}
            >
              <span className="mono" style={{ color: '#0f172a' }}>{name}</span>
              <span
                style={{
                  fontSize: 9,
                  background: required ? '#fee2e2' : '#f1f5f9',
                  color: required ? '#b91c1c' : '#64748b',
                  padding: '1px 5px',
                  borderRadius: 3,
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  letterSpacing: '.06em',
                }}
              >
                {type}{required ? ' · req' : ''}
              </span>
            </label>

            {(type === 'boolean') ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <input
                  type="checkbox"
                  checked={!!value}
                  onChange={(e) => set(name, e.target.checked)}
                  style={{ width: 16, height: 16 }}
                />
                <span style={{ fontSize: 12, color: '#64748b' }}>
                  {value ? 'true' : 'false'}
                </span>
              </div>
            ) : (type === 'number' || type === 'integer') ? (
              <input
                type="number"
                value={value === undefined ? '' : String(value)}
                onChange={(e) => set(name, e.target.value === '' ? undefined : e.target.value)}
                step={type === 'integer' ? 1 : 'any'}
                className="input"
                style={{ fontSize: 12, padding: '7px 10px' }}
                placeholder={description || undefined}
              />
            ) : (type === 'object' || type === 'array') ? (
              <textarea
                value={typeof value === 'string' ? value : JSON.stringify(value ?? (type === 'array' ? [] : {}), null, 2)}
                onChange={(e) => set(name, e.target.value)}
                spellCheck={false}
                style={{
                  width: '100%',
                  minHeight: 60,
                  padding: 8,
                  fontSize: 11,
                  fontFamily: 'JetBrains Mono, monospace',
                  background: '#0d1117',
                  color: '#e2e8f0',
                  border: '1px solid #374151',
                  borderRadius: 8,
                  outline: 'none',
                  lineHeight: 1.5,
                  resize: 'vertical',
                }}
                placeholder={type === 'array' ? '[]' : '{}'}
              />
            ) : (
              <input
                type="text"
                value={value === undefined || value === null ? '' : String(value)}
                onChange={(e) => set(name, e.target.value === '' ? undefined : e.target.value)}
                className="input"
                style={{ fontSize: 12, padding: '7px 10px' }}
                placeholder={description || undefined}
              />
            )}

            {description && type !== 'object' && type !== 'array' && (
              <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 3, lineHeight: 1.4 }}>
                {description}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

/** Render the invoke envelope: success with JSON, error with type + traceback. */
function InvokeResult({ envelope, onCopy }: { envelope: InvokeEnvelope; onCopy: () => void }) {
  const ok = envelope.ok;
  return (
    <div style={{ background: '#0d1117', borderRadius: 10, padding: 12, border: '1px solid #374151' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, fontWeight: 700, color: ok ? '#22c55e' : '#f87171' }}>
          <svg style={{ width: 14, height: 14 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {ok ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            )}
          </svg>
          {ok ? 'SUCCESS' : (envelope.error_type || 'ERROR').toUpperCase().replace('_', ' ')}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span className="mono" style={{ fontSize: 10, color: '#6b7280' }}>
            {envelope.duration_ms}ms
          </span>
          <button
            onClick={onCopy}
            title="Copy response"
            style={{
              padding: 3,
              background: 'none',
              border: '1px solid #374151',
              borderRadius: 4,
              cursor: 'pointer',
              color: '#94a3b8',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <svg style={{ width: 11, height: 11 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
      </div>

      {ok ? (
        <pre
          className="mono"
          style={{
            fontSize: 11,
            color: '#a3e635',
            whiteSpace: 'pre-wrap',
            lineHeight: 1.6,
            margin: 0,
            maxHeight: 360,
            overflow: 'auto',
          }}
        >
          {JSON.stringify(envelope.result ?? {}, null, 2)}
        </pre>
      ) : (
        <div>
          <div
            className="mono"
            style={{
              fontSize: 12,
              color: '#fca5a5',
              whiteSpace: 'pre-wrap',
              lineHeight: 1.5,
              padding: '6px 0',
            }}
          >
            {envelope.error || 'Unknown error'}
          </div>
          {envelope.error_type && (
            <div
              style={{
                fontSize: 10,
                color: '#94a3b8',
                marginTop: 6,
                padding: '6px 8px',
                background: 'rgba(148,163,184,.08)',
                borderRadius: 6,
                lineHeight: 1.5,
              }}
            >
              {HINT_FOR_ERROR[envelope.error_type]}
            </div>
          )}
          {envelope.traceback && (
            <details style={{ marginTop: 8 }}>
              <summary style={{ fontSize: 10, color: '#6b7280', cursor: 'pointer', userSelect: 'none' }}>
                Traceback
              </summary>
              <pre
                className="mono"
                style={{
                  fontSize: 10,
                  color: '#9ca3af',
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.5,
                  margin: '6px 0 0 0',
                  maxHeight: 240,
                  overflow: 'auto',
                }}
              >
                {envelope.traceback}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

const HINT_FOR_ERROR: Record<NonNullable<InvokeEnvelope['error_type']>, string> = {
  not_found:
    "This action isn't registered in the in-memory registry. Check INDUSTRY_ACTIONS in backend/services/action_registry.py.",
  load_failed:
    "Python couldn't import the handler file. Usually this means a missing dependency (boto3, structlog, etc.) in the backend venv.",
  bad_arguments:
    "The handler's function signature doesn't match the payload. Check that the input field names match the function's parameters.",
  runtime:
    "The handler ran but raised an exception. Inspect the traceback — common culprits are missing AWS credentials or missing Cosmos DB tables in local dev.",
};

/** Build an empty-but-typed default for each field in the schema. */
function defaultValuesForSchema(schema?: ActionSchema): Record<string, unknown> {
  if (!schema) return {};
  const out: Record<string, unknown> = {};
  for (const [name, field] of Object.entries(schema)) {
    const type = typeof field === 'object' ? (field as { type?: string }).type : String(field);
    if (type === 'boolean') out[name] = false;
    else if (type === 'number' || type === 'integer') out[name] = undefined;
    else if (type === 'array') out[name] = [];
    else if (type === 'object') out[name] = {};
    else out[name] = '';
  }
  return out;
}

/* =================== USAGE =================== */

interface PlaybookLite {
  id?: string;
  playbook_id?: string;
  name?: string;
  industry?: string;
  status?: string;
  actions?: Array<{ action_id?: string; handler?: string; name?: string }>;
}

/* ══════════════════════════ Code tab ══════════════════════════ */

/**
 * AWS Console deep-link for an action. Actions map to Lambda functions named
 * `apex-<industry>-<action_name>`; store actions also get a Cosmos DB link.
 *
 * Region is pulled from NEXT_PUBLIC_AWS_REGION so non-us-east-1 deploys still
 * get the right URL.
 */
function awsConsoleUrl(action: ActionItem): string {
  const region = process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1';
  const fnName = lambdaFunctionName(action);
  if (action.type === 'store') {
    return `https://${region}.console.aws.amazon.com/cosmos_dbv2/home?region=${region}#table?name=ApexResults`;
  }
  return `https://${region}.console.aws.amazon.com/lambda/home?region=${region}#/functions/${fnName}`;
}

function lambdaFunctionName(action: ActionItem): string {
  const slug = action.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
  const domain = action.industry === 'all' ? 'core' : action.industry;
  return `apex-${domain}-${slug}`;
}

/**
 * Synthesize a realistic Python handler snippet for the action. The content
 * is templated from the action's type + name so every action shows *something*
 * concrete, not a placeholder.
 */
function codeForAction(action: ActionItem): string {
  const slug  = action.name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
  const id    = `${action.industry === 'all' ? 'core' : action.industry}.${slug}`;
  const desc  = action.description.replace(/"/g, '\\"');

  switch (action.type) {
    case 'extract':
      return [
        'from apex.sdk import apex_action',
        'from apex.core.bda import extract_document',
        '',
        `@apex_action(id="${id}", type="extract", blueprint_required=True)`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    blueprint_id = event["blueprint_id"]',
        '    s3_uri       = event["s3_uri"]',
        '',
        '    result = extract_document(s3_uri, blueprint_id)',
        '    return {',
        '        "fields":       result.fields,',
        '        "confidence":   result.confidence,',
        '        "extracted_at": result.timestamp,',
        '    }',
      ].join('\n');

    case 'validate':
      return [
        'from apex.sdk import apex_action, ValidationError',
        '',
        `@apex_action(id="${id}", type="validate")`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    payload = event["payload"]',
        '    rules   = event.get("rules", [])',
        '',
        '    failures = []',
        '    for rule in rules:',
        '        if not rule.matches(payload):',
        '            failures.append({"rule": rule.id, "message": rule.error_message})',
        '',
        '    if failures:',
        '        raise ValidationError(failures)',
        '    return {"pass": True, "checks_run": len(rules)}',
      ].join('\n');

    case 'route':
      return [
        'from apex.sdk import apex_action',
        'from apex.core.routing import route_to',
        '',
        `@apex_action(id="${id}", type="route")`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    decision = evaluate(event["features"])',
        '    target   = {',
        '        "AUTO":     "auto-approve-queue",',
        '        "MANAGER":  "manager-review-queue",',
        '        "HUMAN":    "human-review-queue",',
        '    }[decision]',
        '',
        '    route_to(target, event["work_item_id"], reason=decision)',
        '    return {"decision": decision, "routed_to": target}',
      ].join('\n');

    case 'notify':
      return [
        'from apex.sdk import apex_action',
        'from apex.core.messaging import send',
        '',
        `@apex_action(id="${id}", type="notify")`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    send(',
        '        channel  = event["channel"],     # e.g. "#ohio-plant-7-qc"',
        '        template = event["template"],',
        '        payload  = event["payload"],',
        '    )',
        '    return {"sent": True, "channel": event["channel"]}',
      ].join('\n');

    case 'execute':
      return [
        'from apex.sdk import apex_action',
        'from apex.core.aws import lambda_invoke',
        '',
        `@apex_action(id="${id}", type="execute")`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    response = lambda_invoke(',
        `        function_name = "${lambdaFunctionName(action)}",`,
        '        payload       = event["payload"],',
        '    )',
        '    return {',
        '        "status":   response["status"],',
        '        "output":   response["payload"],',
        '        "duration": response["duration_ms"],',
        '    }',
      ].join('\n');

    case 'store':
      return [
        'from apex.sdk import apex_action',
        'from apex.core.aws import dynamo_write',
        '',
        `@apex_action(id="${id}", type="store")`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    dynamo_write(',
        '        table   = "ApexResults",',
        '        pk      = event["work_item_id"],',
        '        payload = event["payload"],',
        '        ttl     = event.get("ttl_days", 90) * 86_400,',
        '    )',
        '    return {"stored": True}',
      ].join('\n');

    case 'classify':
    default:
      return [
        'from apex.sdk import apex_action',
        'from apex.core.ml import classifier',
        '',
        `@apex_action(id="${id}", type="classify")`,
        'def handler(event, context):',
        `    """${desc}"""`,
        '    label, score = classifier(',
        `        model = "${slug}",`,
        '        text  = event["text"],',
        '    )',
        '    return {"label": label, "confidence": round(score, 4)}',
      ].join('\n');
  }
}

function CodeTab({ action }: { action: ActionItem }) {
  const code = codeForAction(action);
  const fnName = lambdaFunctionName(action);

  return (
    <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0 }}>
          <div className="mono" style={{ fontSize: 11, color: '#64748b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            handlers/{action.industry === 'all' ? 'core' : action.industry}/{fnName.replace(/^apex-/, '')}.py
          </div>
          <div style={{ fontSize: 11, color: '#94a3b8' }}>
            Lambda: <span className="mono" style={{ color: '#0f172a' }}>{fnName}</span> · Python 3.11 · 512 MB · 30s
          </div>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => { navigator.clipboard?.writeText(code); }}
          title="Copy code to clipboard"
        >
          Copy
        </button>
      </div>

      <div
        style={{
          background: '#0d1117',
          borderRadius: 12,
          padding: 16,
          overflow: 'auto',
          maxHeight: 340,
          border: '1px solid #1f2937',
        }}
      >
        <pre
          className="mono"
          style={{
            fontSize: 12, lineHeight: 1.55, color: '#e6edf3',
            margin: 0, whiteSpace: 'pre', tabSize: 4,
          }}
        >
          {code}
        </pre>
      </div>

      <div style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.5 }}>
        The full handler is in the <code style={{ fontSize: 11 }}>aws/actions/</code> package in the repo.
        For runtime logs, dead-letter queue, or IAM role, click <strong>AWS Console</strong> below.
      </div>
    </div>
  );
}

function UsageTab({ action }: { action: ActionItem }) {
  const q = useQuery<PlaybookLite[]>({
    queryKey: ['playbooks-for-usage'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/playbooks?limit=500`);
      if (!r.ok) return [];
      const j = await r.json();
      return (Array.isArray(j) ? j : j.playbooks || j.items || []) as PlaybookLite[];
    },
    retry: false,
  });

  // Playbook uses this action if any of its action references match by
  // id (industry.name), bare name, or handler path.
  const playbooksUsing = (q.data || []).filter((pb) =>
    (pb.actions || []).some((ref) => {
      const candidates = [ref.action_id, ref.handler, ref.name].filter(Boolean) as string[];
      return candidates.some((c) =>
        c === action.id || c === action.name || c.endsWith(`.${action.name}`),
      );
    }),
  );

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 16 }}>
        <MiniStat
          value={action.runs.toLocaleString()}
          label="Total Runs"
          hint="From Cosmos DB invocation_count"
        />
        <MiniStat
          value={String(playbooksUsing.length)}
          label="Playbooks Using"
          hint="Playbooks referencing this action"
        />
        <MiniStat
          value={action.active ? 'Active' : 'Inactive'}
          label="Status"
          valueColor={action.active ? '#16a34a' : '#94a3b8'}
        />
        <MiniStat
          value={cap(action.industry === 'all' ? 'core' : action.industry)}
          label="Industry"
        />
      </div>

      <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8', marginBottom: 8 }}>
        Used In Playbooks
      </div>

      {q.isLoading ? (
        <div style={{ fontSize: 12, color: '#94a3b8', padding: 10 }}>Loading…</div>
      ) : playbooksUsing.length === 0 ? (
        <div
          style={{
            fontSize: 12,
            color: '#94a3b8',
            padding: '10px 12px',
            background: '#f8fafc',
            border: '1px dashed #e2e8f0',
            borderRadius: 8,
            lineHeight: 1.5,
            fontStyle: 'italic',
          }}
        >
          No playbook currently references <span className="mono" style={{ fontStyle: 'normal' }}>{action.id}</span>.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {playbooksUsing.map((pb) => (
            <UsageRow
              key={pb.playbook_id || pb.id || pb.name}
              name={pb.name || pb.playbook_id || 'Unnamed playbook'}
              industry={pb.industry || 'general'}
              status={pb.status || 'draft'}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function MiniStat({
  value, label, valueColor, hint,
}: {
  value: string;
  label: string;
  valueColor?: string;
  hint?: string;
}) {
  return (
    <div
      style={{ background: '#f8fafc', borderRadius: 10, padding: 12, textAlign: 'center' }}
      title={hint}
    >
      <div style={{ fontSize: 20, fontWeight: 800, color: valueColor || '#0f172a' }}>{value}</div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{label}</div>
    </div>
  );
}

function UsageRow({ name, industry, status }: { name: string; industry: string; status: string }) {
  const chip =
    status === 'active'     ? 'chip-green' :
    status === 'deployed'   ? 'chip-green' :
    status === 'draft'      ? 'chip-gray'  :
    status === 'archived'   ? 'chip-red'   :
                              'chip-blue';
  const industryLabel =
    industry === 'financial_services'                                           ? 'Financial' :
    industry === 'insurance_underwriting'                                       ? 'Insurance' :
    industry === 'aerospace_defense'                                            ? 'Aerospace' :
    industry === 'telecommunications'                                           ? 'Telecommunications' :
    industry === 'oil_gas_midstream'                                            ? 'Oil & Gas — Midstream' :
    industry === 'nuclear_operations'                                           ? 'Nuclear Operations' :
    industry.startsWith('healthcare')                                           ? 'Healthcare' :
    (industry === 'manufacturing' || industry === 'supply_chain'
      || industry === 'supply' || industry === 'supply_manufacturing')          ? 'Supply Chain & Manufacturing' :
    cap(industry.replace(/_/g, ' '));

  return (
    <div
      style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '8px 12px', background: '#f8fafc', borderRadius: 8, gap: 10,
      }}
    >
      <span
        style={{
          fontSize: 12,
          fontWeight: 500,
          color: '#0f172a',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {name}
      </span>
      <span className={chip} style={{ fontSize: 10, flexShrink: 0 }}>{industryLabel}</span>
    </div>
  );
}

/* ─────────── create action modal ─────────── */

function CreateActionModal({ onClose }: { onClose: () => void }) {
  return (
    <div
      style={{
        display: 'flex', position: 'fixed', inset: 0,
        background: 'rgba(0,0,0,.5)', alignItems: 'center', justifyContent: 'center',
        zIndex: 100, padding: 32,
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#fff', borderRadius: 20, width: '100%', maxWidth: 520,
          boxShadow: '0 20px 60px rgba(0,0,0,.2)',
        }}
      >
        <div
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '20px 24px', borderBottom: '1px solid #f1f5f9',
          }}
        >
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a' }}>Create Custom Action</h2>
            <p style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>Define a new reusable Lambda-backed action</p>
          </div>
          <button
            onClick={onClose}
            style={{ padding: 7, background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', borderRadius: 8 }}
          >
            <svg style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label className="label">
              Action Name{' '}
              <span style={{ fontFamily: 'monospace', fontSize: 11, color: '#94a3b8' }}>(snake_case)</span>
            </label>
            <input type="text" className="input" placeholder="my_custom_action" />
          </div>
          <div>
            <label className="label">Display Name</label>
            <input type="text" className="input" placeholder="My Custom Action" />
          </div>
          <div>
            <label className="label">Description</label>
            <textarea className="textarea" rows={2} placeholder="Describe what this action does..." />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label">Action Type</label>
              <select className="select">
                <option>Extract</option>
                <option>Validate</option>
                <option>Route</option>
                <option>Notify</option>
                <option>Execute</option>
                <option>Store</option>
              </select>
            </div>
            <div>
              <label className="label">Industry</label>
              <select className="select">
                <option>Core</option>
                <option>Financial Services</option>
                <option>Healthcare</option>
                <option>Insurance</option>
                <option>Aerospace &amp; Defense</option>
                <option>Manufacturing</option>
              </select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10, paddingTop: 4 }}>
            <button onClick={onClose} className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>
              Cancel
            </button>
            <button onClick={onClose} className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
              Create Action
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ─────────── helpers ─────────── */

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

/** Hit /actions/registry/discover?fresh=true and return a flat list of actions. */
async function fetchRegistryActions(): Promise<ActionItem[]> {
  try {
    const r = await fetch(`${API_BASE_URL}/actions/registry/discover?fresh=true`);
    if (!r.ok) return [];
    const data = await r.json();
    const flat: Array<Record<string, unknown>> = [];
    const byIndustry = (data.actions_by_industry || {}) as Record<string, Array<Record<string, unknown>>>;
    for (const arr of Object.values(byIndustry)) flat.push(...arr);
    return mapApiActions(flat);
  } catch {
    return [];
  }
}

/** Hit /actions/ (Cosmos DB) and return a flat list. */
async function fetchDbActions(): Promise<ActionItem[]> {
  try {
    const r = await fetch(`${API_BASE_URL}/actions/`);
    if (!r.ok) return [];
    const data = await r.json();
    return mapApiActions(Array.isArray(data) ? data : data.items || []);
  } catch {
    return [];
  }
}

/**
 * CBB demo → action names mapping. If a live action record (from the registry
 * or Cosmos DB) matches one of these names, the UI will tag it with the
 * corresponding demo chip — so the 10 CBB hero actions stay visually called
 * out regardless of data source.
 */
const CBB_ACTION_DEMOS: Record<string, number[]> = {
  bda_document_extract:        [1, 2, 3],
  athena_federated_query:      [1, 3],
  fabric_tolerance_check:      [2],
  bom_graph_traverse:          [3],
  erp_inventory_hold:          [2],
  crm_order_update:            [1],
  reroute_options_generate:    [3],
  email_send:                  [1, 2],
  teams_alert:                 [2, 3],
  sentiment_analyze:           [1],
  engineering_constraint_check:[1],
  auto_hold_decision:          [2],
  predict_financial_impact:    [3],
  escalate_decision:           [1, 2, 3],
};

function mapApiActions(items: Array<Record<string, unknown>>): ActionItem[] {
  // Best-effort mapping from backend action records to the UI shape.
  // If the backend fields don't match, callers can still fall back to
  // SAMPLE_ACTIONS since we throw if the mapped list is empty.
  return items.map((raw, i) => {
    const category = (raw.category as string) || 'core';
    const name = (raw.display_name as string) || (raw.name as string) || 'Untitled Action';
    const nameSlug = name.toLowerCase().replace(/[\s-]+/g, '_');
    // Actions referenced in the 3 CBB playbooks (all live under Supply Chain
    // & Manufacturing). Force the tag so the domain filter surfaces them,
    // even when the backend returns a generic `core` category.
    const demoTags  = CBB_ACTION_DEMOS[nameSlug] || CBB_ACTION_DEMOS[name] || undefined;
    const industry: IndustryKey = demoTags
      ? 'supply_manufacturing'
      : toIndustryKey((raw.industry as string) || category);
    const type = toActionType((raw.category as string) || (raw.type as string) || 'execute');
    const input_schema  = raw.input_schema  as ActionSchema | undefined;
    const output_schema = raw.output_schema as ActionSchema | undefined;
    return {
      id: (raw.action_id as string) || (raw.id as string) || `act-${i}`,
      name,
      description: (raw.description as string) || '',
      type,
      industry,
      runs: (raw.invocation_count as number) || 0,
      active: (raw.status as string) === 'active' || !raw.status,
      section: demoTags
        ? 'CBB Actions'
        : (industry === 'all' ? 'Core Actions' : SECTION_LABEL[industry] || 'Other'),
      sectionKey: industry,
      input_schema:  input_schema  && Object.keys(input_schema).length  > 0 ? input_schema  : undefined,
      output_schema: output_schema && Object.keys(output_schema).length > 0 ? output_schema : undefined,
      usedInDemos: demoTags,
    };
  });
}

function toActionType(s: string): ActionType {
  const k = s.toLowerCase();
  if (k.includes('extract')) return 'extract';
  if (k.includes('validat')) return 'validate';
  if (k.includes('rout')) return 'route';
  if (k.includes('notif')) return 'notify';
  if (k.includes('stor')) return 'store';
  if (k.includes('classif')) return 'classify';
  return 'execute';
}

function toIndustryKey(s: string): IndustryKey {
  const k = s.toLowerCase();
  // Specific Agentic Enterprise keys MUST be checked BEFORE the generic
  // 'supply' / 'manufactur' fallback — otherwise 'supply_chain_orchestrator'
  // collapses to 'supply_manufacturing'.
  if (k === 'supply_chain_orchestrator') return 'supply_chain_orchestrator';
  if (k === 'hospitality' || k === 'travel') return 'hospitality';
  if (k === 'commercial_real_estate' || k === 'cre' || k === 'real_estate') return 'commercial_real_estate';
  // Telecommunications first-class industry (Verizon Far Edge launch customer).
  // Accept the canonical key + the category alias + the legacy verizon_far_edge
  // tag so old records keep resolving.
  if (k === 'telecommunications' || k === 'telco' || k === 'telco_far_edge' || k === 'far_edge' || k === 'verizon_far_edge' || k === 'verizon') return 'telecommunications';
  // Oil & Gas Midstream — EPROD launch customer.
  if (k === 'oil_gas_midstream' || k === 'midstream' || k === 'oil_gas' || k === 'eprod' || k === 'energy' || k === 'midstream_document_intelligence') return 'oil_gas_midstream';
  if (k.includes('financ')) return 'financial';
  if (k.includes('health')) return 'healthcare';
  if (k.includes('insur')) return 'insurance';
  if (k.includes('aero')) return 'aerospace';
  if (k.includes('manufactur') || k.includes('supply') || k === 'supply_chain' || k.includes('logistic')) return 'supply_manufacturing';
  if (k.includes('nuclear') || k.includes('reactor') || k.includes('reliab')) return 'nuclear';
  return 'all';
}

/* ─────────── data: static UI config ─────────── */

interface TypeCardSpec {
  key: TypeFilter;
  label: string;
  iconBg: string;
  iconColor: string;
  iconPath: string;
}

const TYPE_CARDS: TypeCardSpec[] = [
  { key: 'all',      label: 'All',      iconBg: '#f1f5f9', iconColor: '#475569', iconPath: 'M4 6h16M4 10h16M4 14h16M4 18h16' },
  { key: 'extract',  label: 'Extract',  iconBg: '#eff6ff', iconColor: '#2563eb', iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  { key: 'validate', label: 'Validate', iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  { key: 'route',    label: 'Route',    iconBg: '#fdf4ff', iconColor: '#7c3aed', iconPath: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4' },
  { key: 'notify',   label: 'Notify',   iconBg: '#fffbeb', iconColor: '#d97706', iconPath: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
  { key: 'execute',  label: 'Execute',  iconBg: '#eef2ff', iconColor: '#4338ca', iconPath: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { key: 'store',    label: 'Store',    iconBg: '#f0fdfa', iconColor: '#0f766e', iconPath: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4' },
];

const TYPE_THEME: Record<ActionType, { iconBg: string; iconColor: string; iconPath: string }> = {
  extract:  { iconBg: '#eff6ff', iconColor: '#2563eb', iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
  validate: { iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  route:    { iconBg: '#fdf4ff', iconColor: '#7c3aed', iconPath: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4' },
  notify:   { iconBg: '#fffbeb', iconColor: '#d97706', iconPath: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  execute:  { iconBg: '#eef2ff', iconColor: '#4338ca', iconPath: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' },
  store:    { iconBg: '#f0fdfa', iconColor: '#0f766e', iconPath: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4' },
  classify: { iconBg: '#f1f5f9', iconColor: '#475569', iconPath: 'M4 6h16M4 10h16M4 14h16M4 18h16' },
};

const INDUSTRY_FILTERS: Array<{ key: IndustryKey; label: string }> = [
  { key: 'all',                       label: 'All Industries' },
  { key: 'financial',                 label: 'Financial' },
  { key: 'healthcare',                label: 'Healthcare' },
  { key: 'insurance',                 label: 'Insurance' },
  { key: 'aerospace',                 label: 'Aerospace' },
  { key: 'supply_manufacturing',      label: 'Supply Chain & Manufacturing' },
  { key: 'nuclear',                   label: 'Nuclear Operations' },
  { key: 'telecommunications',        label: 'Telecommunications' },
  { key: 'oil_gas_midstream',         label: 'Oil & Gas — Midstream' },
  { key: 'supply_chain_orchestrator', label: 'Supply Chain Orchestrator' },
  { key: 'hospitality',               label: 'Hospitality & Travel' },
  { key: 'commercial_real_estate',    label: 'Commercial Real Estate' },
];

const SECTION_LABEL: Record<IndustryKey, string> = {
  all:                       'Core Actions',
  financial:                 'Financial Services',
  healthcare:                'Healthcare',
  insurance:                 'Insurance',
  aerospace:                 'Aerospace & Defense',
  supply_manufacturing:      'Supply Chain & Manufacturing',
  nuclear:                   'Nuclear Operations & Reliability',
  telecommunications:        'Telecommunications',
  oil_gas_midstream:         'Oil & Gas — Midstream',
  supply_chain_orchestrator: 'Supply Chain Orchestrator',
  hospitality:               'Hospitality & Travel',
  commercial_real_estate:    'Commercial Real Estate',
};

const SECTION_THEME: Record<IndustryKey, { bg: string; color: string; iconPath: string }> = {
  all:           { bg: '#f1f5f9', color: '#475569', iconPath: 'M13 10V3L4 14h7v7l9-11h-7z' },
  financial:     { bg: '#eff6ff', color: '#2563eb', iconPath: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  healthcare:    { bg: '#fdf4ff', color: '#7c3aed', iconPath: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  insurance:     { bg: '#f5f3ff', color: '#7c3aed', iconPath: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
  aerospace:     { bg: '#fff7ed', color: '#ea580c', iconPath: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8' },
  supply_manufacturing: { bg: '#f0fdfa', color: '#0f766e', iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
  // Nuclear Operations — slate-blue + atom-orbit icon (Heroicons "academic-cap"
  // would also work, but the orbital ring reads "reactor/atomic" most clearly).
  nuclear:       { bg: '#eef2ff', color: '#1e3a8a', iconPath: 'M12 12m-3 0a3 3 0 106 0 3 3 0 10-6 0M12 2a10 10 0 100 20 10 10 0 000-20zm-7.5 7.5l15 5m0-5l-15 5' },
  // Telecommunications — red accent + signal-tower icon (carrier far-edge).
  telecommunications: { bg: '#fef2f2', color: '#b91c1c', iconPath: 'M8.111 16.404a5.5 5.5 0 010-7.778m7.778 0a5.5 5.5 0 010 7.778m-9.9 2.121a8.5 8.5 0 010-12.02m12.02 0a8.5 8.5 0 010 12.02M12 14a2 2 0 100-4 2 2 0 000 4z' },
  // Oil & Gas Midstream — deep green accent + pipeline/droplet icon (EPROD demo).
  oil_gas_midstream:  { bg: '#ecfdf5', color: '#047857', iconPath: 'M5 12h14m-7-7l7 7-7 7' },
  // Agentic Enterprise — 3 specific industry domains.
  supply_chain_orchestrator: { bg: '#f0fdfa', color: '#0f766e', iconPath: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  hospitality:               { bg: '#f5f3ff', color: '#7c3aed', iconPath: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  commercial_real_estate:    { bg: '#f0f9ff', color: '#0369a1', iconPath: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
};

/* ─────────── HTML fallback sample data ─────────── */

const SAMPLE_ACTIONS: ActionItem[] = [
  /* ═══ CBB Demo actions (spec §3.2) ═══ */
  // All 14 CBB actions belong to the 3 CBB playbooks that live under the
  // Supply Chain & Manufacturing domain (Zero-Touch Order Mod, QC Batch,
  // Disruption Reroute), so they carry that domain tag — ensures the
  // Supply Chain & Manufacturing filter actually surfaces them.
  { id: 'cbb-1',  name: 'bda_document_extract',        description: 'Extract structured fields from PDFs using the specified Blueprint schema (BDA)',                              type: 'extract',  industry: 'supply_manufacturing', runs: 24891, active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1,2,3] },
  { id: 'cbb-2',  name: 'athena_federated_query',      description: 'Run a federated SQL query against CBB\'s S3 data lake via Azure Synapse',                                     type: 'execute',  industry: 'supply_manufacturing', runs: 7840,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1,3] },
  { id: 'cbb-3',  name: 'fabric_tolerance_check',      description: 'Cross-reference extracted specs against engineering tolerances in Azure Fabric One',                          type: 'validate', industry: 'supply_manufacturing', runs: 3120,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [2] },
  { id: 'cbb-4',  name: 'bom_graph_traverse',          description: 'Traverse the Bill of Materials graph to find all products affected by a material delay',                       type: 'execute',  industry: 'supply_manufacturing', runs: 412,   active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [3] },
  { id: 'cbb-5',  name: 'erp_inventory_hold',          description: 'Place a hold on specified inventory lots in SAP S/4HANA ERP',                                                  type: 'execute',  industry: 'supply_manufacturing', runs: 892,   active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [2] },
  { id: 'cbb-6',  name: 'crm_order_update',            description: 'Update an order record in Microsoft Dynamics CRM and recalculate lead time',                                   type: 'execute',  industry: 'supply_manufacturing', runs: 4210,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1] },
  { id: 'cbb-7',  name: 'reroute_options_generate',    description: 'Evaluate alternative suppliers and generate ranked rerouting options',                                         type: 'execute',  industry: 'supply_manufacturing', runs: 141,   active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [3] },
  { id: 'cbb-8',  name: 'email_send',                  description: 'Send a templated email via SendGrid to a distributor or internal team',                                        type: 'notify',   industry: 'supply_manufacturing', runs: 18220, active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1,2] },
  { id: 'cbb-9',  name: 'teams_alert',                 description: 'Send a structured alert to a Microsoft Teams channel',                                                        type: 'notify',   industry: 'supply_manufacturing', runs: 9402,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [2,3] },
  { id: 'cbb-10', name: 'sentiment_analyze',           description: 'Analyze email tone and urgency, classify as Low/Medium/High priority',                                         type: 'classify', industry: 'supply_manufacturing', runs: 5110,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1] },
  { id: 'cbb-11', name: 'engineering_constraint_check', description: 'Verify requested order dimensions against engineering tolerances (default ±5%)',                              type: 'validate', industry: 'supply_manufacturing', runs: 3840,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1] },
  { id: 'cbb-12', name: 'auto_hold_decision',          description: 'Decide between partial_hold, full_hold, or auto_clear based on QC failure pattern',                            type: 'route',    industry: 'supply_manufacturing', runs: 1244,  active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [2] },
  { id: 'cbb-13', name: 'predict_financial_impact',    description: 'Project total revenue at risk across affected plants using BOM + unit price data',                             type: 'execute',  industry: 'supply_manufacturing', runs: 188,   active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [3] },
  { id: 'cbb-14', name: 'escalate_decision',           description: 'Route to a human approver when value_at_risk or variance thresholds are exceeded',                             type: 'route',    industry: 'supply_manufacturing', runs: 962,   active: true, section: 'CBB Actions', sectionKey: 'supply_manufacturing', usedInDemos: [1,2,3] },

  /* ═══ Generic actions ═══ */
  // Core
  { id: 'core-1', name: 'BDA Document Extraction',   description: 'Extract structured fields from documents using Amazon Azure AI Document Intelligence', type: 'extract',  industry: 'all', runs: 24891, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-2', name: 'Confidence Threshold Check', description: 'Validate extraction confidence score against configurable thresholds', type: 'validate', industry: 'all', runs: 18340, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-3', name: 'Human Review Router',        description: 'Route documents to human review queue based on confidence or business rules', type: 'route', industry: 'all', runs: 9102, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-4', name: 'SNS Event Publisher',        description: 'Publish processing events and alerts to SNS topics for downstream consumers', type: 'notify', industry: 'all', runs: 7450, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-5', name: 'Cosmos DB Result Writer',     description: 'Persist extraction results and audit trail to Cosmos DB with TTL support', type: 'store', industry: 'all', runs: 15220, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-6', name: 'Lambda Function Invoker',    description: 'Invoke custom Azure Functions functions with typed input/output schema mapping', type: 'execute', industry: 'all', runs: 5890, active: true, section: 'Core Actions', sectionKey: 'all' },

  // Financial Services
  { id: 'fin-1',  name: 'PO Match Validator',         description: 'Match invoice PO references against ERP purchase orders with tolerance rules', type: 'validate', industry: 'financial', runs: 11200, active: true, section: 'Financial Services', sectionKey: 'financial' },
  { id: 'fin-2',  name: 'Invoice Line Item Parser',   description: 'Extract individual line items, quantities, unit prices from vendor invoices', type: 'extract', industry: 'financial', runs: 8740, active: true, section: 'Financial Services', sectionKey: 'financial' },
  { id: 'fin-3',  name: 'AP Approval Router',         description: 'Route invoices to correct AP approver based on amount thresholds and vendor tier', type: 'route', industry: 'financial', runs: 6310, active: true, section: 'Financial Services', sectionKey: 'financial' },

  // Healthcare
  { id: 'hc-1',   name: 'EOB Data Extractor',         description: 'Extract claim details, member info, and payment data from Explanation of Benefits docs', type: 'extract', industry: 'healthcare', runs: 5670, active: true, section: 'Healthcare', sectionKey: 'healthcare' },
  { id: 'hc-2',   name: 'ICD-10 Code Validator',      description: 'Validate ICD-10 diagnosis codes against current code set with payer-specific rules', type: 'validate', industry: 'healthcare', runs: 4120, active: true, section: 'Healthcare', sectionKey: 'healthcare' },
  { id: 'hc-3',   name: 'Prior Auth Router',          description: 'Route prior authorization requests to correct clinical review team by specialty', type: 'route', industry: 'healthcare', runs: 3880, active: true, section: 'Healthcare', sectionKey: 'healthcare' },

  // Manufacturing
  { id: 'mfg-1',  name: 'Work Order Scheduler',       description: 'Assign work orders to plant lines based on machine capacity and queue depth', type: 'route',    industry: 'supply_manufacturing', runs: 3210, active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },
  { id: 'mfg-2',  name: 'Defect Classifier',           description: 'Classify QC defects (surface crack, dimensional drift, contamination) from inspection photos', type: 'classify', industry: 'supply_manufacturing', runs: 2140, active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },
  { id: 'mfg-3',  name: 'Three-Way PO Match',          description: 'Reconcile vendor invoice vs. open PO vs. goods-receipt note before payment', type: 'validate', industry: 'supply_manufacturing', runs: 4420, active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },

  // Supply Chain
  { id: 'sup-1',  name: 'Supplier Risk Score',         description: 'Score supplier reliability using delivery history, financial health, and geographic risk', type: 'execute',  industry: 'supply_manufacturing', runs: 1820, active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },
  { id: 'sup-2',  name: 'Shipment ETA Predictor',      description: 'Predict arrival time from AIS, carrier telemetry, port congestion, and weather feeds',   type: 'execute',  industry: 'supply_manufacturing', runs: 1520, active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },
  { id: 'sup-3',  name: 'Inventory Reorder Trigger',   description: 'Emit reorder events when on-hand stock falls below dynamic safety level',                  type: 'notify',   industry: 'supply_manufacturing', runs: 990,  active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },
  { id: 'sup-4',  name: 'Logistics Alert Classifier',  description: 'Classify incoming logistics alerts (delay, damage, theft, weather) from carrier feeds',    type: 'classify', industry: 'supply_manufacturing', runs: 1340, active: true, section: 'Supply Chain & Manufacturing', sectionKey: 'supply_manufacturing' },

  // Telecommunications — Verizon Far Edge POC (12 actions = 6 agent-implementing
  // + 6 supporting actions referenced by the playbook recipes).
  { id: 'tel-1',  name: 'parse_robot_output',          description: 'Parse a ROBOT Framework XML test output into structured test results + suite metadata (CertificationAgent)',                       type: 'extract',  industry: 'telecommunications', runs: 248,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-2',  name: 'classify_failures',           description: 'Apply Verizon Far Edge classification rules (latency / schema_drift / regression / investigate) to parsed test results',          type: 'classify', industry: 'telecommunications', runs: 248,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-3',  name: 'detect_schema_drift',         description: 'Compare baseline + current Redfish schemas and emit breaking changes with their script-impact map (SchemaWatchAgent)',            type: 'validate', industry: 'telecommunications', runs:  72,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-4',  name: 'validate_upgrade_path',       description: 'Validate firmware upgrade path against compatibility matrix; surface historical failure rate (UpgradeAdvisorAgent)',              type: 'validate', industry: 'telecommunications', runs: 1840, active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-5',  name: 'compute_risk_scores',         description: 'ApexSignal wave-risk scoring — scores every site in the inventory, surfaces historical wave incident patterns, produces wave plan', type: 'execute',  industry: 'telecommunications', runs:  41,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-6',  name: 'mentor_query',                description: 'KB Q&A with verbatim citations across runbooks, release notes, known-issues KB, upgrade procedures (MentorAgent)',               type: 'execute',  industry: 'telecommunications', runs: 3210, active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  // ─── Supporting actions referenced by the telecom playbook recipes ───
  { id: 'tel-7',  name: 'certification_report',        description: 'Emit final cycle report (PDF + JSON) — exec summary, failure analysis, schema-drift summary, deployment recommendation, Audit Lens trail', type: 'notify',   industry: 'telecommunications', runs:  41,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-8',  name: 'pattern_match',               description: 'Match every site against the historical outage signature (Type-B + 23.06 + Northeast) and surface pattern hits',           type: 'validate', industry: 'telecommunications', runs:  84,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-9',  name: 'redfish_schema_fetch',        description: 'Pull live Redfish schema from a representative CaaS node via mutual TLS — used by SchemaWatchAgent every 6 hours',               type: 'extract',  industry: 'telecommunications', runs: 124,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-10', name: 'script_impact_map',           description: 'Walk the 47-script automation catalog → emit deterministic find/replace remediation operations per breaking change',              type: 'route',    industry: 'telecommunications', runs:  18,  active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-11', name: 'intent_classify',             description: 'Classify an inbound telecom Q&A as knowledge / action / status — used by MentorAgent before retrieval kicks off',                 type: 'classify', industry: 'telecommunications', runs: 3210, active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },
  { id: 'tel-12', name: 'production_change_flag',      description: 'Surface senior-engineer review recommendation when a mentor question implies acting on the answer (rollback / upgrade / workaround)', type: 'validate', industry: 'telecommunications', runs: 1840, active: true, section: 'Telecommunications', sectionKey: 'telecommunications' },

  // ─── Core actions used by every telecom playbook (industry: 'all' so they
  //     show in every demo mode, not only Verizon Far Edge) ───
  { id: 'core-7',  name: 'jira_create_ticket',         description: 'Open a single JIRA ticket with auto-assigned team, severity label, KB anchor, and apex-auto-generated tag',                       type: 'route',  industry: 'all', runs: 4218, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-8',  name: 'jira_create_epic',           description: 'Open a JIRA epic with subtasks per impacted artefact — used by SchemaWatchAgent for drift remediation bundles',                  type: 'route',  industry: 'all', runs:  84, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-9',  name: 'site_inventory_load',        description: 'Load a customer site inventory CSV (16,247 rows for Verizon) into memory — used by ApexSignal risk-scoring pipelines',          type: 'extract',industry: 'all', runs:  62, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-10', name: 'wave_authorization',         description: 'Final wave plan + HITL gate decision — emits the Audit Lens authorization event signed by the approving Distinguished Engineer', type: 'route',  industry: 'all', runs:  18, active: true, section: 'Core Actions', sectionKey: 'all' },
  { id: 'core-11', name: 'audit_log_emit',             description: 'Emit an immutable DVR-{ts} event into the Audit Lens — every agent decision lands here for governance replay',                   type: 'notify', industry: 'all', runs: 17800, active: true, section: 'Core Actions', sectionKey: 'all' },

];
