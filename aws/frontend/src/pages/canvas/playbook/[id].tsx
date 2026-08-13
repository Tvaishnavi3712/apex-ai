/**
 * Playbook Detail — overview + editor for a single playbook.
 *
 * Tabs (all editable):
 *   Intent & Output | Recipe | Actions | Triggers | Run History
 *
 * Data source PRIORITY (DO NOT REGRESS — see aws/CLAUDE.md "No hardcoding"):
 *   1. /api/v1/playbooks/{id}  — real DynamoDB row (always tried first)
 *   2. CBB_PLAYBOOK_DATA / DEFAULT_PLAYBOOK — offline-only fallback,
 *      only consulted when the API call fails or the row genuinely doesn't
 *      exist. NEVER prepended to live data; never the primary source.
 *
 * The detail page used to silently fall back to a hardcoded "Invoice
 * Processing" shape for any id that wasn't a CBB demo. That meant clicking
 * any STP / financial / healthcare playbook showed invoice content. Fixed —
 * see git blame on this file for the date the rewire landed.
 */

import React, { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useQuery } from '@tanstack/react-query';
import { humanizeName } from '@/lib/humanize';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type Tab = 'intent' | 'recipe' | 'actions' | 'blueprints' | 'triggers' | 'runs';
type ActionTag = 'extract' | 'validate' | 'route' | 'notify';

/**
 * Turn a free-text intent statement into clean bullet points.
 * Splits on explicit lines / bullet markers first; otherwise on sentence
 * boundaries. Strips leading markers and collapses whitespace.
 */
function intentToBullets(text: string): string[] {
  const raw = (text || '').trim();
  if (!raw) return [];
  // If the author used line breaks or bullet markers, honor them.
  const byLine = raw
    .split(/\r?\n+/)
    .map((l) => l.replace(/^\s*[-*•·]\s*/, '').trim())
    .filter(Boolean);
  if (byLine.length > 1) return byLine;
  // Otherwise split a single paragraph into sentences.
  return raw
    .split(/(?<=[.!?])\s+(?=[A-Z0-9"'(])/)
    .map((s) => s.trim().replace(/^\s*[-*•·]\s*/, ''))
    .filter(Boolean);
}

interface OutputField  { name: string; type: string }
interface ActionEntry  { name: string; desc: string; tag: ActionTag; tagLabel: string }
interface TriggerEntry { label: string; detail: string; active: boolean }
interface RunEntry     { id: string; title: string; meta: string; dot: 'green'|'amber'|'red'; result: string; tone: string; chipCls: string; conf: string }

interface BlueprintField { name: string; type: string; required: boolean; confidence: number }
interface BlueprintRef {
  id: string;
  name: string;
  version: string;
  industry_label: string;
  field_count: number;
  confidence_pct: string;
  used_in_steps: number[];           // which recipe steps use this blueprint (1-indexed)
  description: string;
  fields: BlueprintField[];
  arn?: string;
}

interface PlaybookData {
  name: string;
  industry_label: string;
  description: string;
  status_label: string;
  status_chip: string;                // 'chip-green' | 'chip-amber' | 'chip-gray'
  actions_count_label: string;
  last_run_label: string;
  version: string;
  accuracy_pct: string;
  deploy_agent_name: string;
  intent: string;
  output_fields: OutputField[];
  recipe: string;
  actions: ActionEntry[];
  blueprints: BlueprintRef[];
  triggers: TriggerEntry[];
  runs: RunEntry[];
}

export default function PlaybookDetailPage() {
  const router = useRouter();
  const id = typeof router.query.id === 'string' ? router.query.id : '';

  // Live API call — always the source of truth when the backend is reachable.
  // Falls back to the local registry only on 404 / network failure so the
  // page still renders for offline dev. No more silent invoice fallback.
  const apiQuery = useQuery<any>({
    queryKey: ['playbook', id],
    queryFn: async () => {
      if (!id) return null;
      const r = await fetch(`${API_BASE_URL}/playbooks/${encodeURIComponent(id)}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    },
    enabled: !!id,
    retry: false,
    staleTime: 30_000,
  });

  // Pull every blueprint in the same industry as this playbook. The backend's
  // Playbook model doesn't carry direct blueprint references — but blueprints
  // are filed by industry, and any document the playbook's actions touch
  // comes from that industry's blueprint pack. Fetching the industry's full
  // blueprint set is the correct narrow scope.
  const playbookIndustry = apiQuery.data?.industry || '';
  const bpQuery = useQuery<any[]>({
    queryKey: ['playbook-blueprints', playbookIndustry],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/blueprints?limit=500`);
      if (!r.ok) return [];
      const j = await r.json();
      const all: any[] = Array.isArray(j) ? j : (j.blueprints || j.items || []);
      return all.filter((b) => (b.industry || '') === playbookIndustry);
    },
    enabled: !!playbookIndustry,
    retry: false,
    staleTime: 30_000,
  });

  // Live cycle history for the cert cycle playbook (pb-tel-1). Polls every
  // 10 sec so a fresh cycle shows up in the Runs tab within ~10 sec.
  // No-op for any other playbook id.
  const telecomCycleHistory = useQuery<{ items: any[] }>({
    queryKey: ['telecom-cycle-history', id],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/telecommunications/cycle-history?limit=10`);
      if (!r.ok) return { items: [] };
      return r.json();
    },
    enabled: id === 'pb-tel-1',
    retry: false,
    staleTime: 10_000,
    refetchInterval: 10_000,
  });

  const pb = useMemo<PlaybookData>(() => {
    let base: PlaybookData;
    if (apiQuery.data) {
      base = _apiToPlaybookData(apiQuery.data);
      // Merge in the live blueprints once they've arrived.
      if (bpQuery.data && bpQuery.data.length > 0) {
        base.blueprints = bpQuery.data.map((b: any) => _apiToBlueprintRef(b, base.actions));
      }
    } else if (apiQuery.isError) {
      // Hardcoded fallback ONLY when the API genuinely failed.
      base = lookupPlaybook(id);
    } else {
      // While loading, render an empty skeleton — never the invoice fallback.
      base = EMPTY_PLAYBOOK;
    }

    // For pb-tel-1 only — replace base.runs with live cycle history when
    // available. Falls through to whatever runs the lookup/API gave us
    // when there's no cycle history yet (fresh backend after restart).
    if (id === 'pb-tel-1') {
      const items = telecomCycleHistory.data?.items ?? [];
      if (items.length > 0) {
        base = { ...base, runs: items.map(_cycleToRunEntry) };
      }
    }
    return base;
  }, [apiQuery.data, apiQuery.isError, bpQuery.data, id, telecomCycleHistory.data]);

  const [tab, setTab] = useState<Tab>('intent');

  // Editable state — seeded from the lookup, resets when the id changes.
  const [intent,      setIntent]      = useState<string>(pb.intent);
  const [recipe,      setRecipe]      = useState<string>(pb.recipe);
  const [outputs,     setOutputs]     = useState<OutputField[]>(pb.output_fields);
  const [actionsList, setActionsList] = useState<ActionEntry[]>(pb.actions);
  const [blueprints, setBlueprints]   = useState<BlueprintRef[]>(pb.blueprints);
  const [triggers,    setTriggers]    = useState<TriggerEntry[]>(pb.triggers);

  useEffect(() => {
    setIntent(pb.intent);
    setRecipe(pb.recipe);
    setOutputs(pb.output_fields);
    setActionsList(pb.actions);
    setBlueprints(pb.blueprints);
    setTriggers(pb.triggers);
  }, [pb]);

  const [showDeployModal, setShowDeployModal] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const showToast = (msg: string) => {
    setToast(msg);
    window.setTimeout(() => setToast(null), 2200);
  };

  /* ─────────── tab-level edit helpers ─────────── */

  const updateOutput = (i: number, patch: Partial<OutputField>) =>
    setOutputs((list) => list.map((f, idx) => idx === i ? { ...f, ...patch } : f));
  const addOutput    = () => setOutputs((list) => [...list, { name: 'new_field', type: 'string' }]);
  const removeOutput = (i: number) => setOutputs((list) => list.filter((_, idx) => idx !== i));

  const updateAction = (i: number, patch: Partial<ActionEntry>) =>
    setActionsList((list) => list.map((a, idx) => idx === i ? { ...a, ...patch } : a));
  const removeAction = (i: number) => setActionsList((list) => list.filter((_, idx) => idx !== i));
  const moveAction   = (i: number, dir: -1 | 1) => setActionsList((list) => {
    const j = i + dir;
    if (j < 0 || j >= list.length) return list;
    const next = list.slice();
    [next[i], next[j]] = [next[j], next[i]];
    return next;
  });
  const addAction = () => setActionsList((list) => [
    ...list,
    { name: 'new.action', desc: 'Describe what this action does', tag: 'extract', tagLabel: 'Extract' },
  ]);

  const updateTrigger = (i: number, patch: Partial<TriggerEntry>) =>
    setTriggers((list) => list.map((t, idx) => idx === i ? { ...t, ...patch } : t));
  const removeTrigger = (i: number) => setTriggers((list) => list.filter((_, idx) => idx !== i));
  // Trigger picker — opens a modal pulled from the catalog (70+ sources)
  const [triggerPickerOpen, setTriggerPickerOpen] = useState(false);
  const addTrigger = () => setTriggerPickerOpen(true);
  const addTriggerFromCatalog = (entry: import('@/lib/connectorCatalog').ConnectorEntry) => {
    setTriggers((list) => [
      ...list,
      {
        label:  `${entry.name} · ${entry.triggerType || 'event'}`,
        detail: entry.triggerExample || `${entry.id}://`,
        active: true,
      },
    ]);
    setTriggerPickerOpen(false);
    showToast(`Added ${entry.name} trigger`);
  };

  const saveDraft = () => showToast(`Saved draft of "${pb.name}"`);

  return (
    <>
      <Head><title>Playbook · {pb.name} | APEX</title></Head>

      {/* Back + actions */}
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Link href="/canvas" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, color: '#64748b', textDecoration: 'none' }}>
          <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          Back to Canvas
        </Link>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary btn-sm" onClick={saveDraft}>Save Draft</button>
          <button className="btn btn-primary btn-sm" onClick={() => setShowDeployModal(true)}>
            <svg style={{ width: 14, height: 14 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
            Deploy Agent
          </button>
        </div>
      </div>

      {/* Header card */}
      <div className="card" style={{ padding: 24, marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>{pb.name}</h2>
              <span className={pb.status_chip}>{pb.status_label}</span>
            </div>
            <p style={{ fontSize: 14, color: '#64748b', maxWidth: 600 }}>{pb.description}</p>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>{pb.industry_label}</span>
              <span style={{ color: '#e2e8f0' }}>·</span>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>{pb.actions_count_label}</span>
              <span style={{ color: '#e2e8f0' }}>·</span>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>{pb.last_run_label}</span>
              <span style={{ color: '#e2e8f0' }}>·</span>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>{pb.version}</span>
              {id && (
                <>
                  <span style={{ color: '#e2e8f0' }}>·</span>
                  <span className="mono" style={{ fontSize: 11, color: '#94a3b8' }}>id: {id}</span>
                </>
              )}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 28, fontWeight: 800, color: '#0f172a' }}>{pb.accuracy_pct}</div>
            <div style={{ fontSize: 12, color: '#16a34a', fontWeight: 500 }}>Accuracy (7d)</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tab-bar" style={{ width: 'fit-content', marginBottom: 24 }}>
        <button className={`tab ${tab === 'intent'     ? 'active' : ''}`} onClick={() => setTab('intent')}>Intent &amp; Output</button>
        <button className={`tab ${tab === 'recipe'     ? 'active' : ''}`} onClick={() => setTab('recipe')}>Recipe</button>
        <button className={`tab ${tab === 'actions'    ? 'active' : ''}`} onClick={() => setTab('actions')}>Actions ({actionsList.length})</button>
        <button className={`tab ${tab === 'blueprints' ? 'active' : ''}`} onClick={() => setTab('blueprints')}>Blueprints ({blueprints.length})</button>
        <button className={`tab ${tab === 'triggers'   ? 'active' : ''}`} onClick={() => setTab('triggers')}>Triggers</button>
        <button className={`tab ${tab === 'runs'       ? 'active' : ''}`} onClick={() => setTab('runs')}>Run History</button>
      </div>

      {/* Intent tab */}
      {tab === 'intent' && (
        <div style={{ maxWidth: 760 }}>
          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8', marginBottom: 10 }}>Intent</div>
            <textarea
              className="textarea"
              rows={6}
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              placeholder="Describe what this playbook should accomplish in plain English. Use new lines or sentences — each becomes a bullet above."
            />
            <div style={{ marginTop: 10, fontSize: 11, color: '#94a3b8' }}>
              {intent.length} characters · {intent.trim().split(/\s+/).filter(Boolean).length} words · {intentToBullets(intent).length} bullets
            </div>
          </div>
          <div className="card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Output Format</div>
              <button className="btn btn-secondary btn-sm" onClick={addOutput}>+ Add Field</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {outputs.length === 0 && (
                <div style={{ fontSize: 12, color: '#94a3b8', padding: 12 }}>No output fields yet.</div>
              )}
              {outputs.map((f, i) => (
                <div key={i} className="field-row" style={{ gap: 10, alignItems: 'center' }}>
                  <input
                    className="input"
                    value={f.name}
                    onChange={(e) => updateOutput(i, { name: e.target.value })}
                    style={{ flex: 2, fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}
                  />
                  <select
                    className="input"
                    value={f.type}
                    onChange={(e) => updateOutput(i, { type: e.target.value })}
                    style={{ width: 130 }}
                  >
                    {['string', 'number', 'boolean', 'date', 'enum', 'object', 'array'].map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => removeOutput(i)}
                    title="Remove field"
                    style={{ padding: '6px 10px' }}
                  >×</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recipe tab */}
      {tab === 'recipe' && (
        <div style={{ maxWidth: 820 }}>
          <div className="card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
              <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Recipe (Markdown)</div>
              <button className="btn btn-secondary btn-sm" onClick={() => setRecipe(pb.recipe)}>Reset</button>
            </div>
            <textarea
              className="textarea"
              rows={24}
              value={recipe}
              onChange={(e) => setRecipe(e.target.value)}
              style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}
            />
          </div>
        </div>
      )}

      {/* Actions tab */}
      {tab === 'actions' && (
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f8fafc' }}>
            <div style={{ fontSize: 13, color: '#64748b' }}>
              {actionsList.length} action{actionsList.length === 1 ? '' : 's'} · drag-free reorder via ↑ / ↓
            </div>
            <button className="btn btn-primary btn-sm" onClick={addAction}>+ Add Action</button>
          </div>
          <div>
            {actionsList.map((a, i) => {
              const colors = TAG_COLORS[a.tag] || TAG_COLORS.extract;
              return (
                <div
                  key={i}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '36px 1fr 140px auto',
                    gap: 12,
                    alignItems: 'center',
                    padding: '14px 20px',
                    borderBottom: i === actionsList.length - 1 ? 'none' : '1px solid #f8fafc',
                  }}
                >
                  <div style={{ width: 28, height: 28, borderRadius: 8, background: colors.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: colors.color }}>{i + 1}</div>
                  <div>
                    <input
                      className="input"
                      value={a.name}
                      onChange={(e) => updateAction(i, { name: e.target.value })}
                      style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13, marginBottom: 4 }}
                    />
                    <input
                      className="input"
                      value={a.desc}
                      onChange={(e) => updateAction(i, { desc: e.target.value })}
                      style={{ fontSize: 12, color: '#64748b' }}
                    />
                  </div>
                  <select
                    className="input"
                    value={a.tag}
                    onChange={(e) => {
                      const nextTag = e.target.value as ActionTag;
                      updateAction(i, { tag: nextTag, tagLabel: TAG_COLORS[nextTag].label });
                    }}
                  >
                    {(Object.keys(TAG_COLORS) as ActionTag[]).map((t) => (
                      <option key={t} value={t}>{TAG_COLORS[t].label}</option>
                    ))}
                  </select>
                  <div style={{ display: 'flex', gap: 4 }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => moveAction(i, -1)} disabled={i === 0} title="Move up" style={{ padding: '4px 8px' }}>↑</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => moveAction(i,  1)} disabled={i === actionsList.length - 1} title="Move down" style={{ padding: '4px 8px' }}>↓</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => removeAction(i)} title="Remove" style={{ padding: '4px 8px' }}>×</button>
                  </div>
                </div>
              );
            })}
            {actionsList.length === 0 && (
              <div style={{ padding: 24, fontSize: 13, color: '#94a3b8' }}>No actions yet. Click <strong>+ Add Action</strong> to build the recipe.</div>
            )}
          </div>
        </div>
      )}

      {/* Blueprints tab */}
      {tab === 'blueprints' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {blueprints.length === 0 && (
            <div className="card" style={{ padding: 24, textAlign: 'center' }}>
              <div style={{ fontSize: 13, color: '#64748b', marginBottom: 12 }}>
                This playbook doesn&apos;t reference any extraction blueprints yet.
              </div>
              <Link href="/canvas/new-blueprint" className="btn btn-primary btn-sm">+ New Blueprint</Link>
            </div>
          )}

          {blueprints.map((bp) => (
            <div key={bp.id} className="card" style={{ overflow: 'hidden' }}>
              {/* Header */}
              <div style={{
                display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
                padding: '18px 22px', borderBottom: '1px solid #f1f5f9', gap: 16, flexWrap: 'wrap',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flex: 1, minWidth: 260 }}>
                  <div style={{
                    width: 44, height: 44, borderRadius: 12, background: '#eff6ff',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: '#2563eb', fontWeight: 700, fontSize: 11, flexShrink: 0,
                  }}>
                    {bp.name.split(/\s+/).slice(0, 2).map((w) => w[0]).join('').toUpperCase()}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                      <span style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>{bp.name}</span>
                      <span className="chip-blue" style={{ fontSize: 10 }}>{bp.version}</span>
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{bp.description}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 6, fontSize: 11, color: '#94a3b8', flexWrap: 'wrap' }}>
                      <span>{bp.industry_label}</span>
                      <span style={{ color: '#e2e8f0' }}>·</span>
                      <span>{bp.field_count} fields</span>
                      <span style={{ color: '#e2e8f0' }}>·</span>
                      <span style={{ color: '#16a34a', fontWeight: 600 }}>{bp.confidence_pct} avg confidence</span>
                      {bp.used_in_steps.length > 0 && (
                        <>
                          <span style={{ color: '#e2e8f0' }}>·</span>
                          <span>Used in step{bp.used_in_steps.length === 1 ? '' : 's'} {bp.used_in_steps.join(', ')}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <Link href={`/canvas/blueprint/${bp.id}`} className="btn btn-secondary btn-sm">View Schema</Link>
                  <Link href={`/canvas/blueprint/${bp.id}`} className="btn btn-primary btn-sm">Edit Blueprint</Link>
                </div>
              </div>

              {/* Field preview table */}
              <div style={{ padding: 0 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                  <thead>
                    <tr style={{ textAlign: 'left', color: '#64748b', background: '#f8fafc' }}>
                      <th style={{ padding: '10px 20px', fontWeight: 600 }}>Field</th>
                      <th style={{ padding: '10px 8px',  fontWeight: 600, width: 120 }}>Type</th>
                      <th style={{ padding: '10px 8px',  fontWeight: 600, width: 100 }}>Required</th>
                      <th style={{ padding: '10px 20px', fontWeight: 600, textAlign: 'right', width: 120 }}>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bp.fields.map((f) => {
                      const confColor = f.confidence >= 95 ? '#16a34a' : f.confidence >= 85 ? '#d97706' : '#dc2626';
                      return (
                        <tr key={f.name} style={{ borderTop: '1px solid #f1f5f9' }}>
                          <td className="mono" style={{ padding: '10px 20px', color: '#0f172a' }}>{f.name}</td>
                          <td style={{ padding: '10px 8px' }}>
                            <span style={{
                              fontSize: 10, fontWeight: 600, padding: '2px 6px', borderRadius: 4,
                              background: '#eff6ff', color: '#2563eb',
                            }}>{f.type}</span>
                          </td>
                          <td style={{ padding: '10px 8px' }}>
                            {f.required ? (
                              <span style={{ fontSize: 10, fontWeight: 700, padding: '1px 5px', borderRadius: 3, background: '#fee2e2', color: '#b91c1c' }}>YES</span>
                            ) : (
                              <span style={{ fontSize: 11, color: '#94a3b8' }}>—</span>
                            )}
                          </td>
                          <td style={{ padding: '10px 20px', textAlign: 'right', color: confColor, fontWeight: 600 }}>
                            {f.confidence.toFixed(1)}%
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* ARN */}
              {bp.arn && (
                <div
                  className="mono"
                  style={{
                    padding: '10px 22px',
                    background: '#f8fafc',
                    borderTop: '1px solid #f1f5f9',
                    fontSize: 11,
                    color: '#64748b',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {bp.arn}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Triggers tab */}
      {tab === 'triggers' && (
        <div style={{ maxWidth: 760 }}>
          <div className="card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Active Triggers</div>
              <button className="btn btn-primary btn-sm" onClick={addTrigger}>+ Add Trigger</button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {triggers.map((t, i) => (
                <div key={i} className="field-row" style={{ alignItems: 'center', gap: 12 }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <input
                      className="input"
                      value={t.label}
                      onChange={(e) => updateTrigger(i, { label: e.target.value })}
                      style={{ fontSize: 13, fontWeight: 500, marginBottom: 4 }}
                    />
                    <input
                      className="input"
                      value={t.detail}
                      onChange={(e) => updateTrigger(i, { detail: e.target.value })}
                      style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: '#64748b' }}
                    />
                  </div>
                  <button
                    className={t.active ? 'chip-green' : 'chip-gray'}
                    onClick={() => updateTrigger(i, { active: !t.active })}
                    style={{ border: 'none', cursor: 'pointer' }}
                    title="Toggle active"
                  >
                    {t.active ? 'Active' : 'Disabled'}
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={() => removeTrigger(i)} style={{ padding: '4px 10px' }}>×</button>
                </div>
              ))}
              {triggers.length === 0 && (
                <div style={{ fontSize: 12, color: '#94a3b8' }}>No triggers yet.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Runs tab */}
      {tab === 'runs' && (
        <div className="card" style={{ overflow: 'hidden' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {pb.runs.map((r, i) => (
              <div
                key={r.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '14px 20px',
                  borderBottom: i === pb.runs.length - 1 ? 'none' : '1px solid #f8fafc',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span className={`dot-${r.dot}`} />
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{r.id} · {r.title}</div>
                    <div style={{ fontSize: 12, color: '#94a3b8' }}>{r.meta}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 12, color: r.tone, fontWeight: 600 }}>{r.result}</span>
                  <span className={r.chipCls}>{r.conf}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Deploy Agent Modal */}
      {showDeployModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ padding: 28 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Deploy Agent</h3>
              <button onClick={() => setShowDeployModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', fontSize: 20 }}>✕</button>
            </div>
            <div style={{ marginBottom: 16 }}>
              <label className="label">Agent Name</label>
              <input className="input" type="text" defaultValue={pb.deploy_agent_name} />
            </div>
            <div style={{ marginBottom: 20 }}>
              <label className="label">Deploy Target</label>
              <div style={{ display: 'flex', gap: 10 }}>
                <label style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, padding: 12, border: '1px solid #e2e8f0', borderRadius: 10, cursor: 'pointer' }}>
                  <input type="radio" name="dt" defaultChecked style={{ accentColor: '#2563eb' }} />
                  <span style={{ fontSize: 13, fontWeight: 500 }}>Staging</span>
                </label>
                <label style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8, padding: 12, border: '1px solid #e2e8f0', borderRadius: 10, cursor: 'pointer' }}>
                  <input type="radio" name="dt" style={{ accentColor: '#2563eb' }} />
                  <span style={{ fontSize: 13, fontWeight: 500 }}>Production</span>
                </label>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <button className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center' }} onClick={() => setShowDeployModal(false)}>Cancel</button>
              <Link href="/agents" className="btn" style={{ flex: 1, justifyContent: 'center', background: '#059669', color: '#fff', borderColor: '#059669' }}>
                Deploy Agent
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 20, right: 24, zIndex: 200,
          background: '#064e3b', color: '#ecfdf5', padding: '10px 16px',
          borderRadius: 8, fontSize: 13, boxShadow: '0 10px 30px rgba(2,6,23,.25)',
        }}>
          ✓ {toast}
        </div>
      )}

      {triggerPickerOpen && (
        <TriggerPicker
          onClose={() => setTriggerPickerOpen(false)}
          onPick={addTriggerFromCatalog}
        />
      )}
    </>
  );
}

/* ═════════════════════ Trigger picker modal ═════════════════════
 * Catalog-driven picker showing 70+ source systems an APEX playbook can be
 * triggered by. Categories are sticky-rendered as headers; users can search,
 * pick a source, and the trigger is added with a sensible default detail
 * (e.g. an S3 bucket path with a recursive glob for AWS S3). All categories are
 * collapsible so the modal stays scannable. */
function TriggerPicker({ onClose, onPick }: {
  onClose: () => void;
  onPick: (entry: import('@/lib/connectorCatalog').ConnectorEntry) => void;
}) {
  const { TRIGGER_SOURCES, groupTriggersByCategory } = require('@/lib/connectorCatalog');
  const [query, setQuery] = useState('');
  const grouped: Record<string, any[]> = groupTriggersByCategory();
  const q = query.trim().toLowerCase();
  const orderedCategories = [
    'Object Storage', 'File Sharing', 'Streaming & Eventing',
    'Databases & CDC', 'Email & Messaging', 'Webhooks & APIs', 'Schedule',
    'File Transfer', 'CRM', 'ERP', 'HRIS', 'ITSM & Ops',
    'Document Repositories', 'Identity & Auth', 'Voice & Contact Center',
    'Industrial / OT', 'Financial & Compliance', 'AWS Services',
    'Azure Services', 'GCP Services', 'AI / ML Services',
    'Data Warehouses', 'Data Lakes & Lakehouses',
  ].filter((c) => grouped[c] && grouped[c].length > 0);

  const filterMatch = (e: any) =>
    !q || e.name.toLowerCase().includes(q) ||
    e.tagline.toLowerCase().includes(q) ||
    e.code.toLowerCase().includes(q) ||
    (e.triggerType && e.triggerType.includes(q));

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
        background: 'rgba(15,23,42,.55)', display: 'flex',
        alignItems: 'center', justifyContent: 'center', zIndex: 200,
        padding: 24,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: '#fff', borderRadius: 14, width: 880, maxHeight: '88vh',
          boxShadow: '0 24px 64px rgba(0,0,0,.25)', display: 'flex',
          flexDirection: 'column', fontFamily: 'Inter, sans-serif',
        }}
      >
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #e8ecf0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
            <div>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>
                Add Trigger Source
              </div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
                {TRIGGER_SOURCES.length} sources can trigger this playbook — pick one to wire up.
              </div>
            </div>
            <button
              onClick={onClose}
              style={{
                background: '#f3f4f6', border: 'none', borderRadius: 6,
                width: 28, height: 28, cursor: 'pointer', color: '#64748b',
                fontSize: 16, lineHeight: 1,
              }}
            >×</button>
          </div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search sources (s3, sharepoint, kafka, fincen, webhook…)"
            autoFocus
            style={{
              width: '100%', padding: '10px 14px', fontSize: 13,
              border: '1px solid #e2e8f0', borderRadius: 8, outline: 'none',
              color: '#0f172a', background: '#f8fafc',
            }}
          />
        </div>

        {/* Body — grouped grid */}
        <div style={{ overflowY: 'auto', padding: '8px 24px 24px' }}>
          {orderedCategories.map((cat) => {
            const matches = (grouped[cat] || []).filter(filterMatch);
            if (matches.length === 0) return null;
            return (
              <div key={cat} style={{ marginTop: 20 }}>
                <div style={{
                  fontSize: 10, fontWeight: 700, letterSpacing: '.12em',
                  textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10,
                }}>
                  {cat} · {matches.length}
                </div>
                <div style={{
                  display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 10,
                }}>
                  {matches.map((e: any) => (
                    <button
                      key={e.id}
                      onClick={() => onPick(e)}
                      style={{
                        textAlign: 'left', border: '1px solid #e8ecf0', borderRadius: 10,
                        padding: '10px 12px', background: '#fff', cursor: 'pointer',
                        display: 'flex', gap: 10, alignItems: 'center', transition: 'box-shadow .15s, border-color .15s',
                      }}
                      onMouseEnter={(ev) => {
                        const el = ev.currentTarget;
                        el.style.boxShadow = '0 4px 12px rgba(108,71,255,0.10)';
                        el.style.borderColor = '#c7d2fe';
                      }}
                      onMouseLeave={(ev) => {
                        const el = ev.currentTarget;
                        el.style.boxShadow = 'none';
                        el.style.borderColor = '#e8ecf0';
                      }}
                    >
                      <div style={{
                        width: 34, height: 34, borderRadius: 8,
                        background: e.iconBg, color: e.iconColor,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 10, fontWeight: 700, flexShrink: 0,
                      }}>
                        {e.code}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {e.name}
                        </div>
                        <div style={{ fontSize: 11, color: '#94a3b8', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {e.tagline}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ═════════════════════ lookups + data ═════════════════════ */

const TAG_COLORS: Record<ActionTag, { bg: string; color: string; label: string }> = {
  extract:  { bg: '#eff6ff', color: '#2563eb', label: 'Extract'  },
  validate: { bg: '#f0fdf4', color: '#16a34a', label: 'Validate' },
  route:    { bg: '#fdf4ff', color: '#86198f', label: 'Route'    },
  notify:   { bg: '#fffbeb', color: '#b45309', label: 'Notify'   },
};

/** Convert a cycle-history record (from /telecommunications/cycle-history)
 *  into the RunEntry shape the Runs tab renders. */
function _cycleToRunEntry(item: any): RunEntry {
  const status = String(item.status || '—');
  const isProceed = status.startsWith('PROCEED');
  const isHold    = status.startsWith('FAIL') || status.startsWith('HOLD');
  const dot:  'green'|'amber'|'red' = isHold ? 'red' : (isProceed ? 'green' : 'amber');
  const tone: string                = isHold ? '#dc2626' : (isProceed ? '#16a34a' : '#d97706');
  const chip: string                = isHold ? 'chip-red' : (isProceed ? 'chip-green' : 'chip-amber');

  // human-readable time-ago
  const endedAt = Number(item.ended_at || 0);
  const sec = Math.max(0, Math.floor((Date.now() - endedAt) / 1000));
  const ago = sec < 5 ? 'just now'
            : sec < 60 ? `${sec} sec ago`
            : sec < 3600 ? `${Math.floor(sec/60)} min ago`
            : sec < 86400 ? `${Math.floor(sec/3600)} hr ago`
            : `${Math.floor(sec/86400)} day ago`;

  const durationMs = Number(item.duration_ms || 0);
  const durHuman = durationMs < 1000
    ? `${durationMs} ms`
    : durationMs < 60_000
      ? `${(durationMs / 1000).toFixed(1)} sec`
      : `${(durationMs / 60_000).toFixed(1)} min`;

  const triggerSuffix = item.trigger === 's3_event'
    ? ' · S3 trigger'
    : item.trigger === 'ui_upload' ? ' · UI upload' : '';

  return {
    id:      `CYCLE-${item.cycle_id || '?'}`,
    title:   `${item.device || 'CaaS Node'} · ${item.firmware || ''}`.trim(),
    meta:    `${status} · ${ago} · ${durHuman}${triggerSuffix}`,
    dot,
    result:  `${item.passed ?? '?'}/${item.total ?? '?'} pass · ${item.tickets_count ?? 0} JIRA tickets`,
    tone,
    chipCls: chip,
    conf:    item.total ? ((item.passed ?? 0) / item.total).toFixed(2) : '—',
  };
}


function lookupPlaybook(id: string): PlaybookData {
  // Lookup order: CBB → STP → Telecom → safe "not found" stub.
  // We deliberately AVOID falling through to invoice content — per the
  // CLAUDE.md ZERO-HARDCODING RULE, unknown ids must render an explicit
  // "not found" message rather than silently misattribute content from
  // another industry to the user's actual workflow.
  return CBB_PLAYBOOK_DATA[id]
      ?? STP_PLAYBOOK_DATA[id]
      ?? TELCO_PLAYBOOK_DATA[id]
      ?? EPROD_PLAYBOOK_DATA[id]
      ?? DEFAULT_PLAYBOOK;
}

/** Empty skeleton used while the API call is in flight. Never the invoice fallback. */
const EMPTY_PLAYBOOK: PlaybookData = {
  name: 'Loading…',
  industry_label: '',
  description: '',
  status_label: 'Loading',
  status_chip: 'chip-gray',
  actions_count_label: '— actions',
  last_run_label: '',
  version: '—',
  accuracy_pct: '—',
  deploy_agent_name: '',
  intent: '',
  output_fields: [],
  recipe: '',
  actions: [],
  blueprints: [],
  triggers: [],
  runs: [],
};

/**
 * Coerce a backend Playbook row → the rich PlaybookData shape this page renders.
 *
 * The backend's Playbook model is a flat-ish dict (see
 * aws/backend/models/playbook.py). Some fields don't exist on the backend
 * (last_run_label, accuracy_pct, deploy_agent_name) — synthesise sensible
 * defaults derived from what IS present rather than fabricating numbers.
 */
/**
 * Coerce a backend Blueprint row → BlueprintRef (the shape the playbook
 * detail page's Blueprints tab renders). Walks the playbook's action
 * references to figure out which recipe step likely uses this blueprint —
 * extract / validate steps that mention BDA or matching naming conventions.
 */
function _apiToBlueprintRef(api: any, playbookActions: ActionEntry[]): BlueprintRef {
  // schema_fields shape: [{name, type, description, required}, ...]
  const rawFields: any[] = Array.isArray(api?.schema_fields) ? api.schema_fields : [];
  const fields: BlueprintField[] = rawFields.map((f) => ({
    name:       f.name || '(unnamed)',
    type:       f.type || 'string',
    required:   !!f.required,
    confidence: typeof f.confidence === 'number' ? f.confidence : 95,
  }));

  // Average confidence across required fields (rough quality signal).
  const reqs = fields.filter((f) => f.required);
  const avgConf = reqs.length > 0
    ? reqs.reduce((s, f) => s + f.confidence, 0) / reqs.length
    : (fields.length > 0 ? fields.reduce((s, f) => s + f.confidence, 0) / fields.length : 95);

  // Industry display label
  const industryKey = (api.industry || '').toLowerCase();
  const industryLabel =
    industryKey === 'nuclear_operations'    ? 'Nuclear Operations & Reliability' :
    industryKey === 'telecommunications'    ? 'Telecommunications' :
    industryKey === 'supply_manufacturing'
    || industryKey === 'manufacturing'
    || industryKey === 'supply_chain'        ? 'Supply Chain & Manufacturing' :
    industryKey === 'financial_services'    ? 'Financial Services' :
    industryKey === 'aerospace_defense'     ? 'Aerospace & Defense' :
    industryKey === 'insurance_underwriting'? 'Commercial Insurance' :
    industryKey.startsWith('healthcare')    ? 'Healthcare' :
    humanizeName(industryKey);

  // Which recipe steps (1-indexed) use this blueprint? Look at the playbook's
  // action list — extract/validate actions that share the blueprint's
  // document_type root word (e.g. "policy" → policy_search, policy_cite_extract).
  const docType = (api.document_type || api.name || '').toLowerCase();
  const docRoot = docType.split('_')[0];
  const used_in_steps: number[] = [];
  if (docRoot) {
    playbookActions.forEach((a, idx) => {
      if (a.tag !== 'extract' && a.tag !== 'validate') return;
      if ((a.name || '').toLowerCase().includes(docRoot)) {
        used_in_steps.push(idx + 1);
      }
    });
  }

  return {
    id:             api.blueprint_id || api.id || '',
    name:           humanizeName(api.name) || api.name || '(unnamed blueprint)',
    version:        api.version || api?.bdaSchema?.version || 'v1.0',
    industry_label: industryLabel,
    field_count:    fields.length,
    confidence_pct: `${avgConf.toFixed(1)}%`,
    used_in_steps,
    description:    api.description || '',
    fields,
    arn:            api.bda_blueprint_arn || api.arn || '',
  };
}

function _apiToPlaybookData(api: any): PlaybookData {
  if (!api) return EMPTY_PLAYBOOK;

  // Map raw `actions` array → frontend ActionEntry list. Backend rows look
  // like { name, action_id, description, required } — map name → tag by
  // simple keyword inspection (matches the registry's category convention).
  const actions: ActionEntry[] = Array.isArray(api.actions)
    ? api.actions.map((a: any): ActionEntry => {
        const ref = (a.action_id || a.handler || a.name || '').toLowerCase();
        const tag: ActionTag =
          ref.includes('extract') || ref.includes('lookup') || ref.includes('fetch') ? 'extract'
        : ref.includes('valid') || ref.includes('check') || ref.includes('verify')   ? 'validate'
        : ref.includes('notif') || ref.includes('email') || ref.includes('alert')    ? 'notify'
        : 'route';
        return {
          name:     a.action_id || a.name || '(unnamed)',
          desc:     a.description || '',
          tag,
          tagLabel: tag.charAt(0).toUpperCase() + tag.slice(1),
        };
      })
    : [];

  // Output schema — backend returns `output: [{name, type, description}, ...]`
  const outputs: OutputField[] = Array.isArray(api.output)
    ? api.output.map((f: any) => ({
        name: f.name || f.field || '(field)',
        type: f.type || 'string',
      }))
    : [];

  // Industry label — backend stores key, derive friendly label.
  const industryLabel = (() => {
    const k = (api.industry || '').toLowerCase();
    if (k === 'nuclear_operations')    return 'Nuclear Operations & Reliability';
    if (k === 'telecommunications')    return 'Telecommunications';
    if (k === 'supply_manufacturing'
     || k === 'manufacturing'
     || k === 'supply_chain')          return 'Supply Chain & Manufacturing';
    if (k === 'financial_services')    return 'Financial Services';
    if (k === 'insurance_underwriting')return 'Commercial Insurance';
    if (k.startsWith('healthcare'))    return 'Healthcare';
    if (k === 'aerospace_defense')     return 'Aerospace & Defense';
    if (!k) return '';
    return k.split('_').map((s: string) => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
  })();

  // Status chip class
  const statusChipMap: Record<string, string> = {
    deployed: 'chip-green', active: 'chip-green',
    draft:    'chip-gray',  archived: 'chip-red',
    failed:   'chip-red',
  };
  const status = (api.status || 'draft').toLowerCase();

  return {
    // Title-case the snake_case backend name. See lib/humanize.ts.
    name: humanizeName(api.name) || api.name || '(unnamed playbook)',
    industry_label: industryLabel,
    description: api.description || api.intent?.split('\n')[0] || '',
    status_label: status.charAt(0).toUpperCase() + status.slice(1),
    status_chip:  statusChipMap[status] || 'chip-gray',
    actions_count_label: `${actions.length} action${actions.length === 1 ? '' : 's'}`,
    last_run_label: api.last_run ? `Last run: ${api.last_run}` : 'Never run',
    version: api.version || 'v1.0.0',
    accuracy_pct: api.accuracy != null ? `${(api.accuracy * 100).toFixed(1)}%` : '—',
    deploy_agent_name: api.agent_name || api.name?.replace(/[_-]/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase()) || '',
    intent: api.intent || '',
    output_fields: outputs,
    recipe:        api.recipe || '',
    actions,
    // Backend Playbook model doesn't carry rich blueprint refs or run history
    // — leave empty rather than synthesise. Tabs render their own empty states.
    blueprints: [],
    triggers:   Array.isArray(api.triggers) ? api.triggers.map((t: any) => {
      // Seeded triggers store extras under `config`; UI-added ones are flat.
      const cfg = t.config || {};
      const TYPE_LABEL: Record<string, string> = {
        gcs: 'GCP Cloud Storage', s3: 'AWS S3', azure_blob: 'Azure Blob Storage',
        eventbridge: 'EventBridge', sqs: 'SQS', schedule: 'Schedule', api: 'API',
      };
      return {
        label:  cfg.label || t.label || TYPE_LABEL[t.type] || t.type || 'Trigger',
        detail: cfg.detail || t.detail || cfg.pattern || cfg.bucket || cfg.path
                || cfg.endpoint || cfg.watch_path || t.bucket || t.path || '',
        active: t.active ?? true,
      };
    }) : [],
    runs: [],
  };
}

const CBB_PLAYBOOK_DATA: Record<string, PlaybookData> = {
  'pb-cbb-1': {
    name: 'Zero-Touch Order Modification',
    industry_label: 'Supply Chain & Manufacturing · CBB',
    description:
      'Parses order-modification PDFs from distributor emails, looks up the original order, validates dimensions against engineering tolerances, updates Dynamics CRM, and emails the distributor — fully hands-off when the check passes.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 2 min ago',
    version: 'v1.3.0',
    accuracy_pct: '97.4%',
    deploy_agent_name: 'CustomerOpsBot',
    intent:
      'When a distributor submits an order modification via email (PDF attachment), extract the requested dimensions, SKU, and quantity. Look up the original order in the CBB data lake (Athena) and validate that the new dimensions stay within ±5% of the originals. If within tolerance and the order is not yet in production, update the order in Microsoft Dynamics CRM, recalculate lead time, and email the distributor with a confirmation PDF. If outside tolerance OR production has already started, route to Customer Ops for human review.',
    output_fields: [
      { name: 'order_id',              type: 'string'  },
      { name: 'modification_status',   type: 'enum'    },
      { name: 'tolerance_delta_pct',   type: 'number'  },
      { name: 'updated_dimensions',    type: 'object'  },
      { name: 'lead_time_days',        type: 'number'  },
      { name: 'distributor_notified',  type: 'boolean' },
    ],
    recipe:
`## Zero-Touch Order Modification Recipe

### Step 1 · EXTRACT — bda_document_extract
- Blueprint: Order Modification Form v2.1
- Input:  uploaded PDF
- Output: order_id, dimensions, distributor_id

### Step 2 · EXECUTE — athena_federated_query
- Query:  SELECT * FROM cbb_orders WHERE order_id = {{order_id}}
- Output: original_order, production_status, production_start_date

### Step 3 · VALIDATE — engineering_constraint_check
- Rule:   abs(new_height - orig_height) / orig_height <= 0.05
- If FAIL: route to Human Review queue
- If PASS: continue to Step 4

### Step 4 · EXECUTE — crm_order_update
- System: Microsoft Dynamics CRM
- Action: Update dimensions, recalculate lead time
- Output: updated_order_confirmation

### Step 5 · NOTIFY — email_send
- To:       {{distributor_email}}
- Template: order_modification_confirmation
- Attach:   updated_order_summary.pdf`,
    actions: [
      { name: 'cbb.bda_document_extract',   desc: 'Parse Order Modification Form v2.1 from email PDF',  tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'cbb.athena_federated_query', desc: 'Look up original order in CBB Data Lake (Athena)',   tag: 'validate', tagLabel: 'Validate' },
      { name: 'cbb.engineering_constraint', desc: 'Enforce ±5% dimensional tolerance',                  tag: 'validate', tagLabel: 'Validate' },
      { name: 'cbb.crm_order_update',       desc: 'Update order in Microsoft Dynamics CRM',              tag: 'route',    tagLabel: 'Route'    },
      { name: 'cbb.email_send',             desc: 'Email confirmation with updated_order_summary.pdf',  tag: 'notify',   tagLabel: 'Notify'   },
    ],
    blueprints: [
      {
        id: 'bp-cbb-order',
        name: 'Order Modification Form v2.1',
        version: 'v2.1',
        industry_label: 'Supply Chain & Manufacturing · CBB',
        field_count: 12,
        confidence_pct: '97.4%',
        used_in_steps: [1],
        description: 'Parses distributor-submitted order modification PDFs. Extracts order ID, original + requested dimensions, product SKU, quantity, contact info, and reason — used by Step 1 (bda_document_extract).',
        arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/order-mod-v2.1',
        fields: [
          { name: 'order_id',                       type: 'string',  required: true,  confidence: 99.8 },
          { name: 'original_dimensions.width_in',   type: 'number',  required: true,  confidence: 98.2 },
          { name: 'original_dimensions.height_in',  type: 'number',  required: true,  confidence: 98.1 },
          { name: 'requested_dimensions.width_in',  type: 'number',  required: true,  confidence: 97.6 },
          { name: 'requested_dimensions.height_in', type: 'number',  required: true,  confidence: 97.4 },
          { name: 'distributor_name',               type: 'string',  required: true,  confidence: 99.1 },
          { name: 'distributor_id',                 type: 'string',  required: false, confidence: 96.2 },
          { name: 'product_sku',                    type: 'string',  required: true,  confidence: 96.8 },
          { name: 'quantity',                       type: 'number',  required: true,  confidence: 99.4 },
          { name: 'requested_delivery_date',        type: 'date',    required: false, confidence: 94.3 },
          { name: 'reason',                         type: 'string',  required: false, confidence: 89.7 },
          { name: 'contact_email',                  type: 'string',  required: true,  confidence: 98.6 },
        ],
      },
    ],
    triggers: [
      { label: 'Email Intake',     detail: 'orders@cbb.com (PDF attachment)', active: true  },
      { label: 'S3 Bucket Upload', detail: 's3://cbb-orders-incoming/mods/*', active: true  },
      { label: 'API Endpoint',     detail: 'POST /api/v1/cbb/order-modify',   active: false },
    ],
    runs: [
      { id: 'CBB-ORD-1044', title: 'Morrison Supply',       meta: 'Completed · 2 min ago · 4.2s',    dot: 'green', result: 'Auto-approved · +3.3% tolerance',          tone: '#16a34a', chipCls: 'chip-green', conf: '0.97' },
      { id: 'CBB-ORD-1039', title: 'Western Building Supply', meta: 'Completed · 18 min ago · 3.9s', dot: 'green', result: 'Auto-approved · +1.1% tolerance',          tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'CBB-ORD-1036', title: 'Contractor Direct',      meta: 'Needs Review · 41 min ago · 5.7s', dot: 'amber', result: 'Routed to Customer Ops · +6.8% (exceeds)', tone: '#d97706', chipCls: 'chip-amber', conf: '0.85' },
    ],
  },

  'pb-cbb-2': {
    name: 'QC Batch Ingestion & Hold',
    industry_label: 'Supply Chain & Manufacturing · CBB · Ohio Plant 7',
    description:
      'Accepts a ZIP of ~50 supplier QC certificates, extracts lot-level data, validates tensile strength and color delta-E against Fabric One specs, places SAP inventory holds on failing lots, and alerts QC + Procurement in Teams.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 14 min ago',
    version: 'v2.0.1',
    accuracy_pct: '99.1%',
    deploy_agent_name: 'QCBot',
    intent:
      'Every morning at 6:00 AM Ohio Plant 7 QC team receives a ZIP of ~50 QC certificates from upstream suppliers. The agent unpacks the ZIP, extracts lot_id, tensile_strength, color_delta_e, and supplier_id for each certificate, checks them against the Azure Fabric One Lakehouse spec (tensile_strength ≥ spec_min AND color_delta_e ≤ 2.0), places an inventory hold in SAP S/4HANA on any lot that fails, and posts a summary to the #ohio-plant-7-qc Teams channel and procurement@cbb.com.',
    output_fields: [
      { name: 'batch_id',           type: 'string'  },
      { name: 'total_certs',        type: 'number'  },
      { name: 'passed_count',       type: 'number'  },
      { name: 'failed_lot_ids',     type: 'array'   },
      { name: 'hold_ids',           type: 'array'   },
      { name: 'quarantined_value',  type: 'number'  },
      { name: 'teams_alerted',      type: 'boolean' },
    ],
    recipe:
`## QC Batch Ingestion & Hold Recipe

### Step 1 · EXTRACT — bda_document_extract
- Blueprint: QC Certificate v3.0
- Input:     50 PDF certificates (unzipped)
- Output:    lot_id, tensile_strength, color_delta_e, supplier_id × 50

### Step 2 · VALIDATE — fabric_tolerance_check
- System: Azure Fabric One Lakehouse
- Rule:   tensile_strength >= spec_min AND color_delta_e <= 2.0
- Output: pass_fail × 50, variance_pct × 50

### Step 3 · DECIDE — auto_hold_decision
- If ANY fail → partial_hold = true
- If ALL pass → auto_clear = true

### Step 4 · EXECUTE — erp_inventory_hold
- System: SAP S/4HANA
- Action: Place inventory hold on failing lot_ids
- Output: hold_ids (one per failing lot)

### Step 5 · NOTIFY — teams_alert
- Channels: #ohio-plant-7-qc AND procurement@cbb.com
- Payload:  failed lot_ids, failure reasons, hold_ids, quarantined value`,
    actions: [
      { name: 'cbb.bda_document_extract',   desc: 'Extract QC Certificate v3.0 fields from 50 PDFs',      tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'cbb.fabric_tolerance_check', desc: 'Compare tensile + color against Fabric One specs',      tag: 'validate', tagLabel: 'Validate' },
      { name: 'cbb.auto_hold_decision',     desc: 'Flag lots for hold vs auto-clear',                      tag: 'route',    tagLabel: 'Route'    },
      { name: 'cbb.erp_inventory_hold',     desc: 'Place SAP S/4HANA hold on failing lots',                tag: 'route',    tagLabel: 'Route'    },
      { name: 'cbb.teams_alert',            desc: 'Notify #ohio-plant-7-qc + procurement@cbb.com',          tag: 'notify',   tagLabel: 'Notify'   },
    ],
    blueprints: [
      {
        id: 'bp-cbb-qc',
        name: 'QC Certificate v3.0',
        version: 'v3.0',
        industry_label: 'Supply Chain & Manufacturing · CBB',
        field_count: 18,
        confidence_pct: '99.1%',
        used_in_steps: [1],
        description: 'Supplier QC certificate schema covering lot identity, material, supplier, inspection data, tensile + color measurements, and pass/fail status. Applied to every PDF unzipped in Step 1.',
        arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/qc-cert-v3.0',
        fields: [
          { name: 'lot_id',            type: 'string', required: true,  confidence: 99.9 },
          { name: 'material',          type: 'string', required: true,  confidence: 99.4 },
          { name: 'supplier_name',     type: 'string', required: true,  confidence: 99.2 },
          { name: 'supplier_id',       type: 'string', required: true,  confidence: 98.7 },
          { name: 'batch_id',          type: 'string', required: true,  confidence: 99.1 },
          { name: 'inspection_date',   type: 'date',   required: true,  confidence: 99.3 },
          { name: 'inspector_id',      type: 'string', required: true,  confidence: 97.4 },
          { name: 'tensile_strength',  type: 'number', required: true,  confidence: 99.6 },
          { name: 'tensile_spec_min',  type: 'number', required: true,  confidence: 99.8 },
          { name: 'color_delta_e',     type: 'number', required: true,  confidence: 98.9 },
          { name: 'color_threshold',   type: 'number', required: true,  confidence: 99.2 },
          { name: 'moisture_pct',      type: 'number', required: false, confidence: 97.1 },
          { name: 'density_gcm3',      type: 'number', required: false, confidence: 96.8 },
          { name: 'quantity_kg',       type: 'number', required: true,  confidence: 99.4 },
          { name: 'unit_price_usd',    type: 'number', required: true,  confidence: 98.6 },
          { name: 'plant_destination', type: 'string', required: true,  confidence: 98.3 },
          { name: 'pass_fail',         type: 'enum',   required: true,  confidence: 99.9 },
          { name: 'variance_pct',      type: 'number', required: true,  confidence: 99.1 },
        ],
      },
    ],
    triggers: [
      { label: 'Document Upload (ZIP)', detail: 'SharePoint → /qc/batches/daily/*.zip', active: true  },
      { label: 'Scheduled · 06:00 ET',  detail: 'Weekdays — poll supplier portal',      active: true  },
      { label: 'API Endpoint',          detail: 'POST /api/v1/cbb/qc-batch',             active: false },
    ],
    runs: [
      { id: 'CBB-QC-B-2141', title: 'Ohio Plant 7 · Batch 2141', meta: 'Completed · 14 min ago · 4.1s',  dot: 'amber', result: '48 passed · 2 HOLDS · $32,550 quarantined', tone: '#d97706', chipCls: 'chip-amber', conf: '0.99' },
      { id: 'CBB-QC-B-2140', title: 'Ohio Plant 7 · Batch 2140', meta: 'Completed · 1 day ago · 3.8s',    dot: 'green', result: '50 passed · auto-clear',                    tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'CBB-QC-B-2139', title: 'Ohio Plant 7 · Batch 2139', meta: 'Completed · 2 days ago · 4.4s',   dot: 'green', result: '49 passed · 1 HOLD · $7,200 quarantined',   tone: '#d97706', chipCls: 'chip-amber', conf: '0.98' },
    ],
  },

  'pb-cbb-3': {
    name: 'Disruption Impact & Reroute',
    industry_label: 'Supply Chain & Manufacturing · CBB',
    description:
      'Consumes Global Supply Chain Monitor alerts (port strikes, supplier delays, etc.), traverses the BOM graph to find affected products and plants, projects financial impact, generates ranked reroute options, and routes high-value disruptions to the Supply Chain Director for approval.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 6 min ago',
    version: 'v1.1.0',
    accuracy_pct: '98.7%',
    deploy_agent_name: 'LogisticsBot',
    intent:
      'When Global Supply Chain Monitor emits a disruption alert (port strike, supplier delay, natural disaster), traverse the CBB BOM graph in Athena to find every affected product and plant, project the total financial value at risk, generate three ranked reroute options (PREFERRED / FALLBACK / LAST_RESORT) based on alternate suppliers, capacities, and cost deltas. If value_at_risk > $500k, escalate to Supply Chain Director (Marcus Webb) via Teams with approval buttons; otherwise auto-dispatch the preferred option.',
    output_fields: [
      { name: 'alert_id',                type: 'string' },
      { name: 'affected_products',       type: 'array'  },
      { name: 'affected_plants',         type: 'array'  },
      { name: 'value_at_risk_usd',       type: 'number' },
      { name: 'reroute_options',         type: 'array'  },
      { name: 'decision',                type: 'enum'   },
      { name: 'approver',                type: 'string' },
    ],
    recipe:
`## Disruption Impact & Reroute Recipe

### Step 1 · ANALYZE — bom_graph_traverse
- Engine:  Amazon Athena (federated BOM graph)
- Input:   affected_supplier, material
- Output:  affected_products, affected_plants[], units_at_risk

### Step 2 · PREDICT — predict_financial_impact
- Input:  affected_plants[], current prices
- Output: total_value_at_risk_usd

### Step 3 · GENERATE — reroute_options_generate
- Inputs:  alt_suppliers, capacities, cost_deltas
- Output:  3 ranked options (PREFERRED / FALLBACK / LAST_RESORT)

### Step 4 · DECIDE — escalate_decision
- Rule: value_at_risk > $500k → escalate_to_human
- Target: Marcus Webb, Supply Chain Director

### Step 5 · NOTIFY — teams_alert
- Channels: #supply-chain-leadership
- Attach:   full impact + 3 reroute options + approval buttons`,
    actions: [
      { name: 'cbb.bom_graph_traverse',         desc: 'Walk BOM graph to find affected products + plants', tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'cbb.predict_financial_impact',   desc: 'Project total $ at risk from disruption',            tag: 'validate', tagLabel: 'Validate' },
      { name: 'cbb.reroute_options_generate',   desc: 'Rank 3 alt-supplier plans by cost + capacity',       tag: 'route',    tagLabel: 'Route'    },
      { name: 'cbb.escalate_decision',          desc: 'Escalate to Director when > $500k at risk',          tag: 'route',    tagLabel: 'Route'    },
      { name: 'cbb.teams_alert',                desc: 'Post to #supply-chain-leadership with approvals',    tag: 'notify',   tagLabel: 'Notify'   },
    ],
    blueprints: [
      {
        id: 'bp-cbb-disrupt',
        name: 'Supplier Delay Alert v1.0',
        version: 'v1.0',
        industry_label: 'Supply Chain & Manufacturing · CBB',
        field_count: 14,
        confidence_pct: '98.7%',
        used_in_steps: [1],
        description: 'Parses GSM XML alerts (port strikes, supplier delays, natural disasters). Provides the supplier + material + severity signal the BOM traversal step needs in Step 1.',
        arn: 'arn:aws:bedrock:us-east-1:CBB:blueprint/supplier-alert-v1.0',
        fields: [
          { name: 'alert_id',           type: 'string', required: true,  confidence: 99.9 },
          { name: 'event_type',         type: 'enum',   required: true,  confidence: 99.6 },
          { name: 'port',               type: 'string', required: true,  confidence: 99.1 },
          { name: 'affected_supplier',  type: 'string', required: true,  confidence: 99.3 },
          { name: 'supplier_id',        type: 'string', required: true,  confidence: 98.8 },
          { name: 'material',           type: 'string', required: true,  confidence: 99.2 },
          { name: 'material_grade',     type: 'string', required: false, confidence: 97.4 },
          { name: 'delay_days',         type: 'number', required: true,  confidence: 98.9 },
          { name: 'severity',           type: 'enum',   required: true,  confidence: 99.7 },
          { name: 'alert_timestamp',    type: 'date',   required: true,  confidence: 99.8 },
          { name: 'expected_recovery',  type: 'date',   required: false, confidence: 96.2 },
          { name: 'source_confidence',  type: 'number', required: true,  confidence: 99.5 },
          { name: 'region',             type: 'string', required: true,  confidence: 98.7 },
          { name: 'notes',              type: 'string', required: false, confidence: 91.4 },
        ],
      },
    ],
    triggers: [
      { label: 'API Event',        detail: 'POST /api/v1/cbb/disruption-alert (GSM)', active: true  },
      { label: 'Scheduled Polling',detail: 'Every 10 min — GSM REST /alerts?since=',  active: true  },
      { label: 'Email Intake',     detail: 'logistics-alerts@cbb.com',                 active: false },
    ],
    runs: [
      { id: 'CBB-DIS-4421', title: 'Shanghai port strike · Vinyl Resin', meta: 'Escalated · 6 min ago · 2.1s',  dot: 'red',   result: '$1.09M at risk · ESCALATED to M. Webb',      tone: '#dc2626', chipCls: 'chip-red',   conf: '0.99' },
      { id: 'CBB-DIS-4417', title: 'Rotterdam weather delay',            meta: 'Auto-dispatched · 3 hr ago · 1.8s', dot: 'green', result: '$78k at risk · PREFERRED reroute sent',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.97' },
      { id: 'CBB-DIS-4412', title: 'Acme Steel supplier delay',          meta: 'Auto-dispatched · 1 day ago · 2.4s', dot: 'green', result: '$212k at risk · FALLBACK reroute sent',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.98' },
    ],
  },
};

// ─────────────────────── STP · Nuclear Operations (ChatSTP UC-1..4) ───────────────────────
// 4 playbooks mirror the YAML on disk under playbooks/nuclear_operations/.
// These render correctly when API isn't seeded or returns 404.

const STP_PLAYBOOK_DATA: Record<string, PlaybookData> = {
  'pb-stp-1': {
    name: 'Policy & Procedure Lookup',
    industry_label: 'Nuclear Operations & Reliability · STP',
    description:
      'Operator-facing knowledge lookup. Routes a plain-language question to the STP policy corpus and returns a verbatim-cited answer — no paraphrasing, every claim anchored to a specific procedure section.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '3 actions',
    last_run_label: 'Last run: 14 min ago',
    version: 'v1.0.0',
    accuracy_pct: '99.0%',
    deploy_agent_name: 'PolicyAgent',
    intent:
      'When an STP operator asks a procedural or regulatory question, classify the intent (policy_lookup vs. equipment_lookup vs. predictive_maintenance), search the policy + Tech Spec + 10 CFR 50 corpus, extract the verbatim passage(s) that answer the question, and return the answer with section-level citations (e.g. "STP-OP-2204 §6.3, step 4"). Never paraphrase. If no high-confidence match exists, say so explicitly rather than invent an answer.',
    output_fields: [
      { name: 'question',          type: 'string' },
      { name: 'answer_verbatim',   type: 'string' },
      { name: 'citations',         type: 'array'  },
      { name: 'confidence',        type: 'number' },
      { name: 'source_docs',       type: 'array'  },
    ],
    recipe:
`## Policy & Procedure Lookup Recipe

### Step 1 · EXTRACT — intent_classify
- Classifier: regex + keyword match → policy_lookup / equipment / predictive
- If intent != policy_lookup, hand off to the correct ChatSTP agent.

### Step 2 · EXECUTE — policy_search
- Corpus: STP procedures (OP, SP, AOP, EOP) + Tech Specs + 10 CFR 50 + Reg Guides
- Retrieval: hybrid (BM25 + semantic) — top_k=5
- Filter: confidence >= 0.85 OR explicit "no match" envelope

### Step 3 · EXTRACT — policy_cite_extract
- For each matched passage, extract verbatim text + section anchor
- Compose final answer: lead with the answer, citations underneath
- Render in operator-friendly format (short paragraphs, monospace citations)`,
    actions: [
      { name: 'nuclear_operations.intent_classify',     desc: 'Classify the inbound question type (policy / equipment / predictive)', tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'nuclear_operations.policy_search',       desc: 'Hybrid search of STP procedure + Tech Spec + 10 CFR 50 corpus',         tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.policy_cite_extract', desc: 'Pull verbatim text + section anchor; never paraphrase',                  tag: 'extract',  tagLabel: 'Extract'  },
    ],
    blueprints: [
      {
        id: 'bp-stp-procedure',
        name: 'STP Plant Procedure',
        version: 'v1.0',
        industry_label: 'Nuclear Operations & Reliability · STP',
        field_count: 18,
        confidence_pct: '99.0%',
        used_in_steps: [2, 3],
        description: 'Parses STP operations, surveillance, abnormal, and emergency procedures (STP-OP-*, STP-SP-*, STP-AOP-*, STP-EOP-*). Extracts section structure, LCO references, AOTs, and sign-off chain.',
        arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/procedure-v1',
        fields: [
          { name: 'procedure_id',       type: 'string', required: true,  confidence: 100  },
          { name: 'revision',           type: 'string', required: true,  confidence: 99.8 },
          { name: 'title',              type: 'string', required: true,  confidence: 99.6 },
          { name: 'sections',           type: 'array',  required: true,  confidence: 98.7 },
          { name: 'lco_references',     type: 'array',  required: false, confidence: 96.4 },
          { name: 'allowed_outage_time', type: 'string', required: false, confidence: 97.1 },
          { name: 'sign_off_chain',     type: 'array',  required: false, confidence: 95.2 },
          { name: 'mode_applicability', type: 'array',  required: true,  confidence: 98.8 },
        ],
      },
    ],
    triggers: [
      { label: 'ChatSTP Message',    detail: 'Routed via ChatSTP intent classifier', active: true  },
      { label: 'API Endpoint',       detail: 'POST /api/v1/agents/PolicyAgent/invoke', active: true  },
      { label: 'Voice Pipeline',     detail: 'Whisper transcript → policy_lookup intent', active: false },
    ],
    runs: [
      { id: 'STP-POL-2418', title: 'RCP vibration alert limit lookup', meta: 'Completed · 14 min ago · 3.2s', dot: 'green', result: 'STP-OP-2204 §6.3 cited verbatim · 0.99 conf',  tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'STP-POL-2417', title: 'LCO applicable to MODE 1 RCP loss', meta: 'Completed · 38 min ago · 2.9s', dot: 'green', result: 'TS 3.4.4 cited verbatim',                     tone: '#16a34a', chipCls: 'chip-green', conf: '0.98' },
      { id: 'STP-POL-2416', title: 'RCS leak rate SR frequency',         meta: 'Completed · 1 hr ago · 3.4s',   dot: 'green', result: 'SR 3.4.13.1 cited verbatim',                 tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
    ],
  },

  'pb-stp-2': {
    name: 'Equipment PM History',
    industry_label: 'Nuclear Operations & Reliability · STP',
    description:
      'Looks up the maintenance history of a piece of plant equipment (e.g. P-3A RCP). Pulls preventive-maintenance records from Oracle PMHISTORY, attributes each event to the responsible engineer, and surfaces relevant work-package attachments.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '4 actions',
    last_run_label: 'Last run: 3 min ago',
    version: 'v1.0.0',
    accuracy_pct: '97.4%',
    deploy_agent_name: 'MaintenanceAgent',
    intent:
      'When an STP operator asks about the maintenance history of a specific piece of equipment, classify the intent, look up the equipment in Oracle PMHISTORY, attribute every maintenance event to the responsible engineer (via the personnel attribution table), and surface scanned work-package PDF attachments. Format the answer as a chronological event list with engineer initials + WP attachment links.',
    output_fields: [
      { name: 'equipment_id',     type: 'string' },
      { name: 'pm_events',        type: 'array'  },
      { name: 'engineer_history', type: 'array'  },
      { name: 'wp_attachments',   type: 'array'  },
      { name: 'last_pm_date',     type: 'date'   },
    ],
    recipe:
`## Equipment PM History Recipe

### Step 1 · EXTRACT — intent_classify
- Classifier: regex + keyword match → equipment_lookup intent
- Extract: equipment_id (e.g. P-3A, P-3B, P-3C)

### Step 2 · EXECUTE — oracle_pm_lookup
- System: Oracle PMHISTORY (read-only)
- Query:  SELECT * FROM pm_events WHERE equipment_id = :id ORDER BY event_date DESC

### Step 3 · EXECUTE — engineer_attribution
- Joins pm_events.performed_by → personnel.engineer_initials
- Output: human-readable engineer column on each event

### Step 4 · EXECUTE — wp_attachment_fetch
- For each pm_event with attachment_ref, fetch from S3
- Format: [WP-{year}-{seq}] (clickable in chat UI)`,
    actions: [
      { name: 'nuclear_operations.intent_classify',       desc: 'Classify intent + extract equipment_id',                            tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'nuclear_operations.oracle_pm_lookup',      desc: 'Pull PM history from Oracle PMHISTORY (read-only)',                   tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.engineer_attribution',  desc: 'Join PM events with personnel table for engineer attribution',       tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.wp_attachment_fetch',   desc: 'Fetch scanned work-package PDFs from S3 by attachment_ref',           tag: 'extract',  tagLabel: 'Extract'  },
    ],
    blueprints: [
      {
        id: 'bp-stp-work-order',
        name: 'STP Work Order Record',
        version: 'v1.0',
        industry_label: 'Nuclear Operations & Reliability · STP',
        field_count: 16,
        confidence_pct: '97.4%',
        used_in_steps: [2, 3],
        description: 'Parses STP work order records from Oracle PMHISTORY. Captures equipment_id, work_type, performed_by, dates, parts used, post-maintenance test results, and attachment references.',
        arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/work-order-v1',
        fields: [
          { name: 'work_order_id',         type: 'string', required: true,  confidence: 100  },
          { name: 'equipment_id',          type: 'string', required: true,  confidence: 99.8 },
          { name: 'work_type',             type: 'enum',   required: true,  confidence: 98.4 },
          { name: 'performed_by',          type: 'string', required: true,  confidence: 96.7 },
          { name: 'start_date',            type: 'date',   required: true,  confidence: 99.2 },
          { name: 'completion_date',       type: 'date',   required: true,  confidence: 99.2 },
          { name: 'duration_hours',        type: 'number', required: false, confidence: 95.4 },
          { name: 'parts_consumed',        type: 'array',  required: false, confidence: 93.7 },
          { name: 'pmt_result',            type: 'enum',   required: true,  confidence: 97.8 },
          { name: 'attachment_refs',       type: 'array',  required: false, confidence: 94.1 },
        ],
      },
    ],
    triggers: [
      { label: 'ChatSTP Message',  detail: 'Routed via ChatSTP intent classifier', active: true  },
      { label: 'API Endpoint',     detail: 'POST /api/v1/agents/MaintenanceAgent/invoke', active: true  },
    ],
    runs: [
      { id: 'STP-EQH-1842', title: 'P-3A history past 24 months',  meta: 'Completed · 3 min ago · 4.8s', dot: 'green', result: '7 PM events · 3 engineers · 2 WP attachments', tone: '#16a34a', chipCls: 'chip-green', conf: '0.98' },
      { id: 'STP-EQH-1841', title: 'P-3B last PM date',             meta: 'Completed · 22 min ago · 4.1s', dot: 'green', result: '2024-11-08 · J. Reyes',                          tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'STP-EQH-1840', title: 'CCW-1A entire history',          meta: 'Completed · 51 min ago · 5.4s', dot: 'green', result: '14 events · 5 engineers · 4 WP attachments',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.97' },
    ],
  },

  'pb-stp-3': {
    name: 'Equipment Issue Analysis',
    industry_label: 'Nuclear Operations & Reliability · STP',
    description:
      'Aggregates failure modes across the work-order corpus for a given piece of equipment. Returns ranked findings (most common failure mode, recurrence interval, last similar event) to support reliability decisions.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '3 actions',
    last_run_label: 'Last run: 7 min ago',
    version: 'v1.0.0',
    accuracy_pct: '94.2%',
    deploy_agent_name: 'DiagnosticsAgent',
    intent:
      'When an STP operator asks about the failure pattern or recurring issues on a piece of equipment, walk the work-package corpus, aggregate by failure mode (bearing wear, seal leak, vibration, etc.), compute recurrence intervals, and surface the top 3 most-common failure modes with their last occurrence date. Anchor every finding to specific WP IDs so the operator can drill down.',
    output_fields: [
      { name: 'equipment_id',          type: 'string' },
      { name: 'failure_modes',         type: 'array'  },
      { name: 'recurrence_interval_d', type: 'number' },
      { name: 'top_finding',           type: 'object' },
      { name: 'source_wps',            type: 'array'  },
    ],
    recipe:
`## Equipment Issue Analysis Recipe

### Step 1 · EXTRACT — intent_classify
- Classifier: regex + keyword match → issue_analysis intent

### Step 2 · ANALYZE — wp_corpus_search
- Corpus: scanned work packages (~12,000 docs in S3)
- Retrieval: semantic + keyword hybrid, filtered by equipment_id
- top_k: 20 most-recent or most-relevant

### Step 3 · ANALYZE — failure_mode_aggregate
- Cluster by failure mode keyword/embedding
- Compute recurrence interval (median days between same-mode events)
- Rank by frequency × severity weight
- Output: top 3 findings with WP citations`,
    actions: [
      { name: 'nuclear_operations.intent_classify',          desc: 'Classify intent + extract equipment_id',                          tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'nuclear_operations.wp_corpus_search',         desc: 'Hybrid search of scanned WP corpus (~12K docs)',                  tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.failure_mode_aggregate',   desc: 'Cluster failures by mode, compute recurrence + rank',             tag: 'validate', tagLabel: 'Validate' },
    ],
    blueprints: [
      {
        id: 'bp-stp-work-package',
        name: 'STP Scanned Work Package',
        version: 'v1.0',
        industry_label: 'Nuclear Operations & Reliability · STP',
        field_count: 22,
        confidence_pct: '94.2%',
        used_in_steps: [2, 3],
        description: 'OCR + structured extraction from scanned STP work packages. Captures equipment_id, failure mode codes, narrative description, LOTO sign-offs, parts list, post-maintenance test results, and the responsible engineer.',
        arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/work-package-v1',
        fields: [
          { name: 'wp_id',              type: 'string', required: true,  confidence: 99.4 },
          { name: 'equipment_id',       type: 'string', required: true,  confidence: 98.7 },
          { name: 'failure_mode',       type: 'string', required: true,  confidence: 92.1 },
          { name: 'narrative',          type: 'string', required: true,  confidence: 94.4 },
          { name: 'loto_steps',         type: 'array',  required: false, confidence: 89.7 },
          { name: 'parts_consumed',     type: 'array',  required: false, confidence: 91.4 },
          { name: 'pmt_result',         type: 'enum',   required: true,  confidence: 96.2 },
          { name: 'engineer_initials',  type: 'string', required: true,  confidence: 95.4 },
        ],
      },
    ],
    triggers: [
      { label: 'ChatSTP Message',  detail: 'Routed via ChatSTP intent classifier', active: true  },
      { label: 'API Endpoint',     detail: 'POST /api/v1/agents/DiagnosticsAgent/invoke', active: true  },
    ],
    runs: [
      { id: 'STP-ISS-944', title: 'P-3A recurring issues',           meta: 'Completed · 7 min ago · 6.2s', dot: 'green', result: 'Top: bearing wear · 84d median recurrence · 4 WPs', tone: '#16a34a', chipCls: 'chip-green', conf: '0.94' },
      { id: 'STP-ISS-943', title: 'CCW-1A failure pattern',           meta: 'Completed · 28 min ago · 7.1s', dot: 'green', result: 'Top: seal leak · 142d median recurrence · 6 WPs', tone: '#16a34a', chipCls: 'chip-green', conf: '0.92' },
      { id: 'STP-ISS-942', title: 'AFW-2 vibration history',          meta: 'Completed · 1 hr ago · 5.8s',   dot: 'green', result: 'No recurring pattern · isolated 2024 event',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.96' },
    ],
  },

  'pb-stp-4': {
    name: 'Predictive Maintenance',
    industry_label: 'Nuclear Operations & Reliability · STP',
    description:
      'ApexSignal RUL forecast + composite risk scoring per piece of equipment. Surfaces a 4-line operator-facing recommendation: risk tier, days-until-failure with confidence band, recommended PM action, and the auto-log entry id.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 11 min ago',
    version: 'v1.0.0',
    accuracy_pct: '91.8%',
    deploy_agent_name: 'ReliabilityAgent',
    intent:
      'For a given piece of plant equipment, detect anomalies in the recent sensor window, forecast remaining useful life (RUL) with 80% and 95% confidence intervals, compute a composite risk score (0–100), and translate it into a concrete PM action with avoidance USD estimate. Format strictly as 4 lines: RISK_TIER, predicted failure, recommended action, audit_log id.',
    output_fields: [
      { name: 'equipment_id',         type: 'string' },
      { name: 'risk_tier',            type: 'enum'   },
      { name: 'risk_score',           type: 'number' },
      { name: 'days_until_failure',   type: 'number' },
      { name: 'confidence_80',        type: 'array'  },
      { name: 'confidence_95',        type: 'array'  },
      { name: 'recommended_action',   type: 'string' },
      { name: 'avoidance_usd',        type: 'number' },
      { name: 'audit_log_id',         type: 'string' },
    ],
    recipe:
`## Predictive Maintenance Recipe

### Step 1 · EXTRACT — intent_classify
- Confirm: intent == predictive_maintenance, extract equipment_id

### Step 2 · ANALYZE — anomaly_detect
- Window: lookback_days=14 (cached for tonight; live SageMaker tomorrow)
- Output: anomaly_count + per-sensor anomaly events

### Step 3 · ANALYZE — rul_predict
- Horizon: 30 days
- Confidence: P10 / P50 / P90 + 80% and 95% bands

### Step 4 · ANALYZE — risk_score_compute
- Inputs: anomalies, RUL, PM gap, criticality tier
- Output: 0–100 composite, tier (CRITICAL/HIGH/MODERATE/LOW)

### Step 5 · DECIDE — pm_recommend
- Translate risk + failure mode → concrete PM action
- Estimate avoidance USD + downtime hours
- Emit audit_log entry → Audit Lens trace`,
    actions: [
      { name: 'nuclear_operations.intent_classify',     desc: 'Confirm predictive_maintenance intent + extract equipment_id',     tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'nuclear_operations.anomaly_detect',      desc: 'Detect anomalies in 14-day sensor window',                          tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.rul_predict',         desc: 'Forecast remaining useful life with confidence bands',              tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.risk_score_compute',  desc: 'Composite 0–100 score + risk tier',                                  tag: 'validate', tagLabel: 'Validate' },
      { name: 'nuclear_operations.pm_recommend',        desc: 'Translate score → concrete PM action + avoidance USD',              tag: 'route',    tagLabel: 'Route'    },
    ],
    blueprints: [
      {
        id: 'bp-stp-sensor',
        name: 'STP Sensor Telemetry Schema',
        version: 'v1.0',
        industry_label: 'Nuclear Operations & Reliability · STP',
        field_count: 6,
        confidence_pct: '99.8%',
        used_in_steps: [2, 3],
        description: 'Schema for sensor telemetry streams used by ApexSignal (vibration, oil analysis, thermography, process trends). Used by anomaly_detect and rul_predict.',
        arn: 'arn:aws:bedrock:us-east-1:STP:blueprint/sensor-v1',
        fields: [
          { name: 'equipment_id',  type: 'string', required: true,  confidence: 99.9 },
          { name: 'sensor_type',   type: 'enum',   required: true,  confidence: 99.8 },
          { name: 'timestamp',     type: 'date',   required: true,  confidence: 99.9 },
          { name: 'value',         type: 'number', required: true,  confidence: 99.8 },
          { name: 'unit',          type: 'string', required: true,  confidence: 99.7 },
          { name: 'baseline',      type: 'number', required: false, confidence: 97.4 },
        ],
      },
    ],
    triggers: [
      { label: 'ChatSTP Message',  detail: 'Routed via ChatSTP intent classifier', active: true  },
      { label: 'Scheduled Sweep',  detail: 'Daily at 06:00 CT — top critical asset list', active: true  },
      { label: 'API Endpoint',     detail: 'POST /api/v1/agents/ReliabilityAgent/invoke', active: true  },
    ],
    runs: [
      { id: 'STP-PRD-2218', title: 'P-3A RUL forecast',  meta: 'Completed · 11 min ago · 9.1s', dot: 'amber', result: 'HIGH · 18d (80% CI 12–24d) · advance PM by 30 days', tone: '#d97706', chipCls: 'chip-amber', conf: '0.92' },
      { id: 'STP-PRD-2217', title: 'P-3B RUL forecast',  meta: 'Completed · 42 min ago · 8.4s', dot: 'green', result: 'LOW · 124d (80% CI 102–158d) · no action',           tone: '#16a34a', chipCls: 'chip-green', conf: '0.95' },
      { id: 'STP-PRD-2216', title: 'CCW-1A RUL forecast', meta: 'Completed · 1 hr ago · 9.6s',   dot: 'red',   result: 'CRITICAL · 4d (80% CI 2–7d) · IMMEDIATE PM',         tone: '#dc2626', chipCls: 'chip-red',   conf: '0.91' },
    ],
  },
};

// ─────────────────────── Telecommunications · Verizon Far Edge POC ───────────────────────
// 3 playbooks mirror the YAML on disk under playbooks/telecommunications/.
// These render correctly when API isn't seeded or returns 404.

const TELCO_PLAYBOOK_DATA: Record<string, PlaybookData> = {
  'pb-tel-1': {
    name: 'Full Certification Cycle',
    industry_label: 'Telecommunications · Verizon Far Edge',
    description: 'Parses ROBOT Framework XML output from a Verizon far-edge CaaS certification run, classifies every failure (latency / schema_drift / regression / investigate), opens JIRA tickets with KB-anchored root causes, and emits a deployment recommendation (PROCEED / HOLD).',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 32 min ago',
    version: 'v1.0.0',
    accuracy_pct: '99.2%',
    deploy_agent_name: 'CertificationAgent',
    intent:
      'When a Verizon far-edge certification run completes, ingest the ROBOT XML output. For every failing test, classify the failure type (latency_threshold_breach / schema_drift_failure / regression_failure / investigate), match against the Known Issues KB, attach the recommended remediation, and open a JIRA ticket auto-assigned to the right team (vendor-engineering, automation-team, security-team, etc.). For runs with > 20 P1 failures OR > 5 schema-drift breaking changes, pause for HITL approval from James Patchett (Distinguished Engineer, HQ Planning). The output is a deployment recommendation: PROCEED, CONDITIONAL, or HOLD, plus a complete cycle report logged to the Audit Lens.',
    output_fields: [
      { name: 'cycle_id',                   type: 'string'  },
      { name: 'total_tests',                type: 'number'  },
      { name: 'pass_count',                 type: 'number'  },
      { name: 'fail_count',                 type: 'number'  },
      { name: 'p1_count',                   type: 'number'  },
      { name: 'p2_count',                   type: 'number'  },
      { name: 'deployment_recommendation',  type: 'enum'    },
      { name: 'jira_tickets_opened',        type: 'array'   },
      { name: 'audit_lens_event_ids',       type: 'array'   },
      { name: 'hours_saved_vs_manual',      type: 'number'  },
    ],
    recipe:
`## Full Certification Cycle Recipe

### Step 1 · EXTRACT — parse_robot_output
- Input:    ROBOT Framework XML output file (~100 KB · 247 tests)
- Parser:   robot.api.ExecutionResult — extracts every <test> + <kw> node
- Output:   test_results[] (id, name, status, library, message), suite metadata,
            total/pass/fail/warn counts

### Step 2 · CLASSIFY — classify_failures
- Rules:    latency_threshold_breach · schema_drift_failure · regression_failure
            · investigate (catch-all for unknown patterns)
- Severity: P1 (production-blocker) · P2 (cycle-blocker) · P3 (monitor)
- KB lookup: cross-reference Known Issues KB for matching kb_id

### Step 3 · VALIDATE — detect_schema_drift
- Compare:   live Redfish schema vs. baseline_version stored in /data/baseline
- Output:    breaking_changes[] with field-level diffs + script-impact map
- If breaking_changes_count > 5 → HITL gate fires

### Step 4 · ROUTE — build_jira_tickets
- One ticket per P1 / P2 failure; bundle related drifts under epic
- Auto-assign by team rules:
  · latency_threshold_breach → vendor-engineering@verizon.com
  · schema_drift_failure     → automation-team@verizon.com
  · security-related        → security-team@verizon.com
- Label every ticket apex-auto-generated + do-not-close-without-apex-review

### Step 5 · NOTIFY — certification_report_emit
- Format:   PDF + JSON, one of each per cycle
- Channels: #apex-vz-certification (Slack), james.patchett@verizon.com (email)
- Audit Lens event_id linked to every line in the report`,
    actions: [
      { name: 'telecommunications.parse_robot_output',     desc: 'Ingest ROBOT XML → structured test_results + suite metadata',                       tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'telecommunications.classify_failures',      desc: 'Apply Verizon classification rules + KB matching to every failing test',           tag: 'validate', tagLabel: 'Validate' },
      { name: 'telecommunications.detect_schema_drift',    desc: 'Compare baseline + live Redfish schemas — emit breaking-change map',               tag: 'validate', tagLabel: 'Validate' },
      { name: 'core.jira_create_ticket',                   desc: 'Open one JIRA ticket per failure, auto-assigned to the right team',                tag: 'route',    tagLabel: 'Route'    },
      { name: 'telecommunications.certification_report',   desc: 'Emit PDF + JSON cycle report, link to Audit Lens event_ids',                       tag: 'notify',   tagLabel: 'Notify'   },
    ],
    blueprints: [
      {
        id: 'bp-tel-robot',
        name: 'ROBOT Framework Test Output',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 12,
        confidence_pct: '99.4%',
        used_in_steps: [1, 2],
        description: 'Parses Verizon Far Edge ROBOT Framework XML. Extracts every test_case (id, name, status, library, keyword args, messages), suite-level totals, and metadata (device, firmware, cycle_id, region, operator).',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/robot-framework-v1',
        fields: [
          { name: 'cycle_id',               type: 'string',  required: true,  confidence: 99.9 },
          { name: 'device_under_test',      type: 'string',  required: true,  confidence: 99.7 },
          { name: 'firmware_version',       type: 'string',  required: true,  confidence: 99.6 },
          { name: 'total_tests',            type: 'number',  required: true,  confidence: 100  },
          { name: 'passed_tests',           type: 'number',  required: true,  confidence: 100  },
          { name: 'failed_tests',           type: 'number',  required: true,  confidence: 100  },
          { name: 'warn_tests',             type: 'number',  required: true,  confidence: 100  },
          { name: 'test_results',           type: 'array',   required: true,  confidence: 99.2 },
          { name: 'region',                 type: 'string',  required: false, confidence: 97.4 },
          { name: 'operator',               type: 'string',  required: false, confidence: 96.8 },
          { name: 'start_time',             type: 'date',    required: true,  confidence: 99.1 },
          { name: 'end_time',               type: 'date',    required: true,  confidence: 99.1 },
        ],
      },
      {
        id: 'bp-tel-cert-rpt',
        name: 'Certification Report Generator',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 18,
        confidence_pct: '99.0%',
        used_in_steps: [5],
        description: 'Generates the final cycle report (PDF + JSON). Includes executive summary, per-test failure analysis, schema_drift summary, deployment recommendation, and the Audit Lens governance trail.',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/certification-report-v1',
        fields: [
          { name: 'report_id',                   type: 'string', required: true,  confidence: 100  },
          { name: 'cycle_id',                    type: 'string', required: true,  confidence: 99.9 },
          { name: 'overall_status',              type: 'enum',   required: true,  confidence: 100  },
          { name: 'deployment_recommendation',   type: 'enum',   required: true,  confidence: 99.4 },
          { name: 'p1_count',                    type: 'number', required: true,  confidence: 100  },
          { name: 'p2_count',                    type: 'number', required: true,  confidence: 100  },
          { name: 'p3_count',                    type: 'number', required: true,  confidence: 100  },
          { name: 'failure_analysis',            type: 'array',  required: true,  confidence: 98.7 },
          { name: 'schema_drift_summary',        type: 'array',  required: false, confidence: 97.8 },
          { name: 'jira_tickets_opened',         type: 'array',  required: true,  confidence: 99.6 },
          { name: 'audit_lens_event_ids',        type: 'array',  required: true,  confidence: 100  },
          { name: 'hours_saved_vs_manual',       type: 'number', required: true,  confidence: 99.0 },
        ],
      },
    ],
    triggers: [
      { label: 'ROBOT Run Webhook', detail: 'POST /api/v1/telecommunications/cycle-complete (Jenkins)', active: true  },
      { label: 'S3 Bucket Upload',  detail: 's3://verizon-far-edge-robot/output/*.xml',                  active: true  },
      { label: 'Manual Trigger',    detail: 'Re-run via Pipeline Editor "Run All"',                     active: false },
    ],
    runs: [
      { id: 'CYCLE-20260115-CAAS-B-2412', title: 'CaaS-Node-Type-B · Wind River 24.12 · Northeast', meta: 'HOLD · 32 min ago · 14.8 min',           dot: 'red',   result: '231/247 PASS · 14 P1 · 12 JIRA tickets', tone: '#dc2626', chipCls: 'chip-red',   conf: '0.99' },
      { id: 'CYCLE-20260114-CAAS-A-2412', title: 'CaaS-Node-Type-A · Wind River 24.12 · Midwest',    meta: 'PROCEED · 14 hr ago · 11.2 min',         dot: 'green', result: '247/247 PASS · 0 failures',              tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'CYCLE-20251020-CAAS-B-2406', title: 'CaaS-Node-Type-B · Wind River 24.06 · Northeast', meta: 'PROCEED · 87 days ago · 11.2 min · baseline', dot: 'green', result: '247/247 PASS · clean baseline',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
    ],
  },

  'pb-tel-2': {
    name: 'Wave Deployment Risk Assessment',
    industry_label: 'Telecommunications · Verizon Far Edge',
    description: 'Scores every site in the 16,247-site Verizon far-edge inventory against firmware, age, incident history, and Maintenance-Rule signals. Surfaces sites matching known high-risk Type-B Northeast deployment patterns. Holds wave authorization at HITL when any site lands in the critical tier.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 8 min ago',
    version: 'v1.0.0',
    accuracy_pct: '96.4%',
    deploy_agent_name: 'ApexSignal / UpgradeAdvisorAgent',
    intent:
      'Before any wave deployment, score every site in the wave inventory. Compute a composite 0–1 risk score from current_firmware, device_age_months, incident_count_12m, last_cert_status, and SLA tier. Tier sites (low / medium / high / critical) and identify any site matching the known high-risk Type-B Northeast pattern (Type-B + 23.06 + Northeast). For any wave that touches a site in the critical tier, pause for HITL approval from James Patchett (Distinguished Engineer, HQ Planning). For wave_3 (critical sites), require additional vendor pre-engagement before authorization. Output: full wave plan + risk-tier counts + recommended action.',
    output_fields: [
      { name: 'wave_id',                       type: 'string'  },
      { name: 'total_sites_scored',            type: 'number'  },
      { name: 'tier_counts',                   type: 'object'  },
      { name: 'january_2026_pattern_matches',  type: 'number'  },
      { name: 'wave_assignments',              type: 'object'  },
      { name: 'critical_clusters',             type: 'object'  },
      { name: 'recommended_action',            type: 'enum'    },
      { name: 'hitl_required',                 type: 'boolean' },
    ],
    recipe:
`## Wave Deployment Risk Assessment Recipe

### Step 1 · LOOKUP — site_inventory_load
- Source: synthetic-data/verizon_far_edge/inventory/verizon_site_inventory_wave1.csv
- Output: 16,247 site rows (region, device, firmware, age, incidents, SLA)

### Step 2 · ANALYZE — compute_risk_scores
- Feature weights:
  · current_firmware == 23.06  → +0.35
  · device_age_months > 36     → +0.15 (per +12mo)
  · incident_count_12m > 3     → +0.20
  · last_cert_status == FAIL   → +0.25
  · last_cert_status == CONDITIONAL → +0.10
- Output: risk_score (0–1) per site, tier classification

### Step 3 · ANALYZE — pattern_match_january_2026
- Match rule: device_type == 'CaaS-Node-Type-B' AND
              current_firmware == '23.06' AND
              region == 'Northeast'
- Surface 252 matched sites — every one of these has James Patchett's
  signature in the Audit Lens as a known historical pattern.

### Step 4 · VALIDATE — validate_upgrade_path
- For each site, validate target firmware path against compatibility matrix
- Surface historical_failure_rate from the rolling 24-month dataset

### Step 5 · DECIDE — wave_authorization
- Gate: any tier == critical → HITL approval required
- Gate: any pattern-match site → additional vendor pre-engagement
- Audit Lens event logged for every authorization decision`,
    actions: [
      { name: 'core.site_inventory_load',                  desc: 'Load 16,247-site inventory CSV into memory',                                 tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'telecommunications.compute_risk_scores',    desc: 'ApexSignal — composite risk score + tier per site',                          tag: 'validate', tagLabel: 'Validate' },
      { name: 'telecommunications.pattern_match',          desc: 'Match every site against known high-risk Type-B Northeast deployment patterns', tag: 'validate', tagLabel: 'Validate' },
      { name: 'telecommunications.validate_upgrade_path',  desc: 'Per-site upgrade path validity + historical failure rate lookup',            tag: 'validate', tagLabel: 'Validate' },
      { name: 'core.wave_authorization',                   desc: 'Final wave plan + HITL gate decision + Audit Lens event',                    tag: 'route',    tagLabel: 'Route'    },
    ],
    blueprints: [
      {
        id: 'bp-tel-runbook',
        name: 'Upgrade Runbook Extractor',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 10,
        confidence_pct: '97.8%',
        used_in_steps: [4],
        description: 'Extracts supported upgrade-path steps from VZ-Upgrade-Procedures-2026 (Rev 4). Returns valid + skip + blocked target firmware versions per device type and source firmware.',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/upgrade-runbook-v1',
        fields: [
          { name: 'device_type',         type: 'string', required: true,  confidence: 99.4 },
          { name: 'source_firmware',     type: 'string', required: true,  confidence: 99.6 },
          { name: 'valid_targets',       type: 'array',  required: true,  confidence: 98.2 },
          { name: 'skip_targets',        type: 'array',  required: false, confidence: 95.4 },
          { name: 'blocked_targets',     type: 'array',  required: false, confidence: 97.1 },
          { name: 'estimated_duration',  type: 'string', required: false, confidence: 92.8 },
          { name: 'rollback_supported',  type: 'boolean',required: true,  confidence: 99.0 },
          { name: 'pre_check_required',  type: 'array',  required: true,  confidence: 96.7 },
          { name: 'post_check_required', type: 'array',  required: true,  confidence: 96.7 },
          { name: 'reference_section',   type: 'string', required: true,  confidence: 98.9 },
        ],
      },
    ],
    triggers: [
      { label: 'Wave Plan Created',     detail: 'POST /api/v1/waves (wave_id, target_firmware, regions[])',     active: true  },
      { label: 'Inventory Refresh',     detail: 'Daily at 06:00 EST — re-score every site against latest data', active: true  },
      { label: 'Manual Recompute',      detail: 'Pipeline Editor → Run All',                                     active: false },
    ],
    runs: [
      { id: 'WAVE-2026-Q1-NE-PLANNED', title: '16,247-site Q1 Continental Refresh',     meta: 'HOLD · 8 min ago · 8.2s',     dot: 'red',   result: '414 critical · 252 pattern matches · WAVE HELD',           tone: '#dc2626', chipCls: 'chip-red',   conf: '0.96' },
      { id: 'WAVE-2025-Q4-CON',        title: '252-site Northeast 23.06→24.01 holdover', meta: 'CONDITIONAL · 4 days ago · 6.4s', dot: 'amber', result: '61% pass rate · proceeded under reduced gate · linked to IR-2026-0114', tone: '#d97706', chipCls: 'chip-amber', conf: '0.61' },
      { id: 'WAVE-2025-Q3-WIDE',       title: '8,140-site Continental 24.01→24.06',     meta: 'PROCEED · 5 mo ago · 9.1s',   dot: 'green', result: '93% pass · proceeded with follow-up · 11 incidents within 30d', tone: '#16a34a', chipCls: 'chip-green', conf: '0.93' },
    ],
  },

  'pb-tel-3': {
    name: 'Schema Drift Response',
    industry_label: 'Telecommunications · Verizon Far Edge',
    description: 'Compares the live Redfish schema against the baseline every 6 hours. When breaking changes appear, generates a deterministic find/replace remediation map across the 47-script automation catalog and opens a tracked JIRA epic before the next certification cycle runs.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '5 actions',
    last_run_label: 'Last run: 2 hr ago',
    version: 'v1.0.0',
    accuracy_pct: '98.8%',
    deploy_agent_name: 'SchemaWatchAgent',
    intent:
      'Every 6 hours, fetch the live Redfish schema from a representative Verizon CaaS node and diff it against the APEX-maintained baseline (currently v1.14.0). When breaking changes are detected (field renames, path migrations, newly-required fields), walk the 47-script automation catalog and identify every playbook + ROBOT test that references the affected endpoint or field. Build a remediation map of deterministic find/replace operations, open a JIRA epic with one sub-task per impacted script, notify the automation team via Slack #apex-vz-schema-watch + email, and pause any in-flight wave authorization that touches an impacted script. Detection-to-remediation SLA: 5 minutes.',
    output_fields: [
      { name: 'baseline_version',          type: 'string'  },
      { name: 'current_version',           type: 'string'  },
      { name: 'breaking_changes_count',    type: 'number'  },
      { name: 'scripts_impacted_count',    type: 'number'  },
      { name: 'remediation_map_id',        type: 'string'  },
      { name: 'jira_epic_key',             type: 'string'  },
      { name: 'estimated_remediation_hours', type: 'number' },
      { name: 'days_before_next_cycle',    type: 'number'  },
    ],
    recipe:
`## Schema Drift Response Recipe

### Step 1 · LOOKUP — redfish_schema_fetch
- Source:   live Redfish endpoint on a representative CaaS-Node-Type-B
- Auth:     mutual TLS w/ Verizon Far Edge CA root cert
- Output:   schema_blob (JSON) + version string

### Step 2 · ANALYZE — detect_schema_drift
- Compare:  current schema vs. baseline (default: v1.14.0)
- Classify changes:
  · field_rename             (BREAKING)
  · path_migration           (BREAKING)
  · new_required_field       (BREAKING)
  · field_added_optional     (NON-BREAKING)
  · field_removed            (BREAKING)
- Output: breaking_changes[] + non_breaking_changes[]

### Step 3 · EXECUTE — script_impact_map
- Walk 47-script catalog → ansible_robot_catalog.json
- For each breaking change, find every script that references the impacted
  endpoint or field. Generate a deterministic find/replace operation.
- Output: remediation_map_id (one per breaking change)

### Step 4 · EXECUTE — jira_create_epic
- Open epic APEXVZ-SCHEMA-EPIC-{cycle_id} with one subtask per impacted script
- Auto-assign by team rules (automation-team, security-team, ran-team)
- Link epic to wave plan(s) it would block

### Step 5 · NOTIFY — schema_drift_alert
- Slack: #apex-vz-schema-watch (formatted block with breaking changes)
- Email: automation-team@verizon.com + james.patchett@verizon.com
- Audit Lens: DVR-{timestamp}-SCHEMA event with full diff payload`,
    actions: [
      { name: 'telecommunications.redfish_schema_fetch',   desc: 'Pull live Redfish schema from a representative CaaS node via mTLS',          tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'telecommunications.detect_schema_drift',    desc: 'Compare current vs. baseline schema — emit breaking change list',           tag: 'validate', tagLabel: 'Validate' },
      { name: 'telecommunications.script_impact_map',      desc: 'Walk 47-script catalog → deterministic find/replace remediation map',       tag: 'route',    tagLabel: 'Route'    },
      { name: 'core.jira_create_epic',                     desc: 'Open JIRA epic w/ one subtask per impacted script, auto-assigned by team',   tag: 'route',    tagLabel: 'Route'    },
      { name: 'core.teams_alert',                          desc: 'Slack #apex-vz-schema-watch + email automation team + James Patchett',       tag: 'notify',   tagLabel: 'Notify'   },
    ],
    blueprints: [
      {
        id: 'bp-tel-redfish',
        name: 'Redfish Schema Diff Analyzer',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 8,
        confidence_pct: '98.8%',
        used_in_steps: [1, 2],
        description: 'Compares two Redfish schema snapshots and emits a structured diff (renames, relocations, new-required fields). Tracks every breaking change with a stable id (SCHEMA-DRIFT-001 etc.) so subsequent runs deduplicate cleanly.',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/redfish-schema-v1',
        fields: [
          { name: 'baseline_version',       type: 'string',  required: true,  confidence: 99.6 },
          { name: 'current_version',        type: 'string',  required: true,  confidence: 99.6 },
          { name: 'breaking_changes',       type: 'array',   required: true,  confidence: 98.4 },
          { name: 'non_breaking_changes',   type: 'array',   required: false, confidence: 97.2 },
          { name: 'change_type',            type: 'enum',    required: true,  confidence: 98.9 },
          { name: 'endpoint_path',          type: 'string',  required: true,  confidence: 99.7 },
          { name: 'field_old',              type: 'string',  required: false, confidence: 97.4 },
          { name: 'field_new',              type: 'string',  required: false, confidence: 97.4 },
        ],
      },
      {
        id: 'bp-tel-kb',
        name: 'Known Issues KB Article',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 11,
        confidence_pct: '96.4%',
        used_in_steps: [4, 5],
        description: 'Parses Verizon Known Issues KB articles (KB-2026-*) to surface remediation steps + permanent-fix versions. Used by the schema-drift response and the certification cycle to attach KB references to ticket descriptions.',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/known-issues-v1',
        fields: [
          { name: 'kb_id',                  type: 'string', required: true,  confidence: 100  },
          { name: 'title',                  type: 'string', required: true,  confidence: 99.4 },
          { name: 'severity',               type: 'enum',   required: true,  confidence: 99.0 },
          { name: 'affected_devices',       type: 'array',  required: true,  confidence: 97.6 },
          { name: 'affected_firmware',      type: 'array',  required: true,  confidence: 98.1 },
          { name: 'symptoms',               type: 'string', required: true,  confidence: 96.4 },
          { name: 'root_cause',             type: 'string', required: true,  confidence: 95.1 },
          { name: 'workaround',             type: 'string', required: true,  confidence: 96.7 },
          { name: 'permanent_fix_version',  type: 'string', required: false, confidence: 94.8 },
          { name: 'linked_jira_tickets',    type: 'array',  required: false, confidence: 92.4 },
          { name: 'related_kb_ids',         type: 'array',  required: false, confidence: 91.0 },
        ],
      },
    ],
    triggers: [
      { label: 'Scheduled Sweep',     detail: 'Every 6 hours (00:00 / 06:00 / 12:00 / 18:00 UTC)',       active: true  },
      { label: 'Pre-Cycle Trigger',   detail: 'Auto-runs before any /telecommunications/cycle-start',    active: true  },
      { label: 'Manual Force',        detail: 'POST /api/v1/telecommunications/schema-drift-check',     active: false },
    ],
    runs: [
      { id: 'SCHEMA-20260115-001', title: 'v1.14.0 → v1.16.0 drift detected',   meta: 'Active · 2 hr ago · 6.4s',  dot: 'red',   result: '3 breaking changes · 14 scripts · epic opened APEXVZ-SCHEMA-EPIC-2026-01', tone: '#dc2626', chipCls: 'chip-red',   conf: '0.99' },
      { id: 'SCHEMA-20260114-019', title: 'v1.14.0 stable check',                meta: 'Clean · 8 hr ago · 5.8s',   dot: 'green', result: 'no drift · 0 changes',                                                       tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'SCHEMA-20260114-018', title: 'v1.14.0 stable check',                meta: 'Clean · 14 hr ago · 5.9s',  dot: 'green', result: 'no drift · 0 changes',                                                       tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
    ],
  },

  'pb-tel-4': {
    name: 'Operator Knowledge Q&A',
    industry_label: 'Telecommunications · Verizon Far Edge',
    description:
      'Operator-facing knowledge Q&A over the Verizon Far Edge document corpus. Answers with verbatim citations only — never paraphrases. Flags production-changing questions for senior-engineer review before the user acts on the answer.',
    status_label: 'Active',
    status_chip: 'chip-green',
    actions_count_label: '4 actions',
    last_run_label: 'Last run: 6 min ago',
    version: 'v1.0.0',
    accuracy_pct: '94.0%',
    deploy_agent_name: 'MentorAgent',
    intent:
      'When a Verizon engineer asks a question about a procedure, a known issue, a Wind River release behavior, or an upgrade path, route to MentorAgent. MentorAgent retrieves the top-k most relevant passages from the Apex Lens index (8 indexed documents, 364 pages, 2,418 chunks), extracts verbatim citations with section anchors, and returns the answer with explicit source attribution. When the question implies a production change (rollback / upgrade / workaround), set production_change_safety_flag=true so the UI surfaces a senior-engineer review recommendation before the user acts. Confidence floor 0.50 — below that, return "no high-confidence match" rather than guess.',
    output_fields: [
      { name: 'question',                       type: 'string'  },
      { name: 'answer',                         type: 'string'  },
      { name: 'citations',                      type: 'array'   },
      { name: 'confidence',                     type: 'number'  },
      { name: 'production_change_safety_flag',  type: 'boolean' },
      { name: 'review_recommended',             type: 'string'  },
      { name: 'audit_log_id',                   type: 'string'  },
    ],
    recipe:
`## Operator Knowledge Q&A Recipe

### Step 1 · EXTRACT — intent_classify
- Classifier: regex + keyword match → knowledge / action / status
- If intent != knowledge, hand off to the correct telecom agent.

### Step 2 · EXECUTE — mentor_query
- Index: Apex Lens manifest (8 docs · 364 pages · 2,418 chunks)
- Retrieval: hybrid (keyword + semantic) — top_k=5
- Confidence floor: 0.50 — below that, return "no high-confidence match"
- Output: passages[] with {document, section, page, verbatim_text}

### Step 3 · VALIDATE — production_change_flag
- Surface flag when the question implies acting on the answer:
  · rollback / downgrade / apply workaround / override gate / force upgrade
- When flag is set, append a senior-engineer review recommendation
- Specifically for 22.12→24.12 paths, always recommend SE review

### Step 4 · NOTIFY — audit_log_emit
- Emit immutable DVR-{timestamp}-MENTOR event into the Audit Lens
- Capture: question, answer hash, citation list, confidence,
  production_change_safety_flag, reviewer recommendation`,
    actions: [
      { name: 'telecommunications.intent_classify',         desc: 'Classify the inbound question (knowledge / action / status)',                  tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'telecommunications.mentor_query',            desc: 'Hybrid retrieval over the Apex Lens index → verbatim passages + citations',    tag: 'validate', tagLabel: 'Validate' },
      { name: 'telecommunications.production_change_flag',  desc: 'Surface senior-engineer review recommendation on production-changing queries',  tag: 'validate', tagLabel: 'Validate' },
      { name: 'core.audit_log_emit',                        desc: 'Emit immutable DVR-{ts}-MENTOR event for the Q&A round-trip',                   tag: 'notify',   tagLabel: 'Notify'   },
    ],
    blueprints: [
      {
        id: 'bp-tel-kb',
        name: 'Known Issues KB Article',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 11,
        confidence_pct: '96.4%',
        used_in_steps: [2],
        description: 'Parses Verizon Known Issues KB articles (KB-2026-*). Surfaces severity, affected devices/firmware, symptoms, root cause, workaround, permanent-fix version, and linked JIRA tickets — used by MentorAgent to anchor every answer to a specific KB entry.',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/known-issues-v1',
        fields: [
          { name: 'kb_id',                  type: 'string', required: true,  confidence: 100  },
          { name: 'title',                  type: 'string', required: true,  confidence: 99.4 },
          { name: 'severity',               type: 'enum',   required: true,  confidence: 99.0 },
          { name: 'affected_devices',       type: 'array',  required: true,  confidence: 97.6 },
          { name: 'affected_firmware',      type: 'array',  required: true,  confidence: 98.1 },
          { name: 'symptoms',               type: 'string', required: true,  confidence: 96.4 },
          { name: 'root_cause',             type: 'string', required: true,  confidence: 95.1 },
          { name: 'workaround',             type: 'string', required: true,  confidence: 96.7 },
          { name: 'permanent_fix_version',  type: 'string', required: false, confidence: 94.8 },
          { name: 'linked_jira_tickets',    type: 'array',  required: false, confidence: 92.4 },
          { name: 'related_kb_ids',         type: 'array',  required: false, confidence: 91.0 },
        ],
      },
      {
        id: 'bp-tel-runbook',
        name: 'Upgrade Runbook Extractor',
        version: 'v1.0',
        industry_label: 'Telecommunications · Verizon Far Edge',
        field_count: 10,
        confidence_pct: '97.8%',
        used_in_steps: [2, 3],
        description: 'Extracts supported upgrade-path steps from VZ-Upgrade-Procedures-2026 (Rev 4). Returns valid + skip + blocked target firmware versions per device type — used by MentorAgent to answer upgrade-path questions.',
        arn: 'arn:aws:bedrock:us-east-1:VZ:blueprint/upgrade-runbook-v1',
        fields: [
          { name: 'device_type',         type: 'string', required: true,  confidence: 99.4 },
          { name: 'source_firmware',     type: 'string', required: true,  confidence: 99.6 },
          { name: 'valid_targets',       type: 'array',  required: true,  confidence: 98.2 },
          { name: 'skip_targets',        type: 'array',  required: false, confidence: 95.4 },
          { name: 'blocked_targets',     type: 'array',  required: false, confidence: 97.1 },
          { name: 'rollback_supported',  type: 'boolean',required: true,  confidence: 99.0 },
          { name: 'pre_check_required',  type: 'array',  required: true,  confidence: 96.7 },
          { name: 'post_check_required', type: 'array',  required: true,  confidence: 96.7 },
          { name: 'reference_section',   type: 'string', required: true,  confidence: 98.9 },
        ],
      },
    ],
    triggers: [
      { label: 'ChatSTP Message',  detail: 'Routed via the telecom intent classifier',                  active: true  },
      { label: 'API Endpoint',     detail: 'POST /api/v1/agents/MentorAgent/invoke',                    active: true  },
      { label: 'Slack Mention',    detail: '#apex-vz-mentor — @MentorAgent <question>',                active: true  },
    ],
    runs: [
      { id: 'MENTOR-20260115-3127', title: 'Upgrade path 22.12 → 24.12 on Type-B', meta: 'Completed · 6 min ago · 7.2s',  dot: 'amber', result: '3 citations · conf 0.92 · SE review flagged (production change)', tone: '#d97706', chipCls: 'chip-amber', conf: '0.92' },
      { id: 'MENTOR-20260115-3122', title: 'What triggers high-risk Type-B classification?', meta: 'Completed · 38 min ago · 5.4s', dot: 'green', result: '3 citations · top: VZ-KB §KB-2025-0288 · conf 0.75',                   tone: '#16a34a', chipCls: 'chip-green', conf: '0.75' },
      { id: 'MENTOR-20260115-3118', title: 'KB-2026-0118 workaround?',             meta: 'Completed · 1 hr ago · 4.8s',   dot: 'green', result: '3 citations · top: VZ-RT-Kernel-Errata · ERR-RT-002 · conf 0.96',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.96' },
    ],
  },
};

// ─────────────────────── Oil & Gas Midstream · EPROD ───────────────────────
// 6 playbooks mirror the YAML on disk under playbooks/oil_gas_midstream/.
// These render correctly when the API is unreachable. Per CLAUDE.md, the API
// path is still the primary — this fallback only fires when apiQuery.isError.

const EPROD_PLAYBOOK_DATA: Record<string, PlaybookData> = {
  'pb-eprod-1': {
    name: 'Invoice Intelligence',
    industry_label: 'Oil & Gas Midstream · EPROD',
    description:
      'Vendor invoice extraction + MSA rate validation for EPROD AP (Halliburton, Schlumberger, Baker Hughes, Kiewit). 75% review-time reduction with audit-ready evidence on every decision.',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    actions_count_label: '7 actions',
    last_run_label: 'Last run: 9 min ago',
    version: 'v1.0.0',
    accuracy_pct: '96.8%',
    deploy_agent_name: 'InvoiceAgent',
    intent:
      'Process every vendor invoice landing in the EPROD AP intake bucket. Extract vendor, invoice number, line items, asset codes, MSA references, amounts, and tax codes via BDA. Validate billed unit rates against the vendor\'s active MSA rate card and flag any line item whose rate variance exceeds 2%. Route every invoice over $50K with no PO reference to a human reviewer. Never write to the ERP without explicit human approval — the agent only stages an ERP write-back in the queue. Every decision is logged to Audit Lens.',
    output_fields: [
      { name: 'processed_invoice',     type: 'object' },
      { name: 'rate_variance_report',  type: 'object' },
      { name: 'routing_decision',      type: 'string' },
      { name: 'audit_lens_event',      type: 'object' },
    ],
    recipe:
`## EPROD Invoice Intelligence Recipe

### Step 1 · EXTRACT — extract_invoice
- Source: S3 drop in apex-eprod-invoices-incoming
- BDA blueprint: bp-eprod-invoice (14 fields)
- Validate confidence >= 90% on vendor + invoice_number + total

### Step 2 · LOOKUP — lookup_msa_rate_card
- Resolve vendor → active MSA via vendor_id
- Pull the MSA rate card (unit rates per service/asset code)
- If no active MSA → halt and route to AP Lead

### Step 3 · VALIDATE — validate_rate_variance
- For each line item: compare billed_rate vs msa_rate_for_asset_code
- Compute variance_pct = (billed - msa) / msa
- Flag if any line variance > 2%

### Step 4 · VALIDATE — check_duplicate_invoice
- Query AP history for same vendor + invoice_number in 18-month window

### Step 5 · DECIDE — route_hitl_or_approve
- If total > $50K AND no PO → HITL
- If any variance > 2% → HITL
- Otherwise auto-approve

### Step 6 · EXECUTE — erp_writeback_queue
- Stage in write-back queue (NEVER commit without human)

### Step 7 · AUDIT — audit_lens_log
- Immutable record with invoice id, decisions, variance, reviewer`,
    actions: [
      { name: 'oil_gas_midstream.extract_invoice',         desc: 'BDA extraction of vendor, invoice fields, line items, asset codes',    tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.lookup_msa_rate_card',    desc: 'Resolve the active MSA + rate card for the invoicing vendor',          tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.validate_rate_variance',  desc: 'Compute per-line variance vs MSA card; flag any > 2%',                  tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.check_duplicate_invoice', desc: 'Search for same vendor + invoice_number in last 18 months',             tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.route_hitl_or_approve',   desc: 'Auto-approve if gates pass; otherwise route to AP reviewer queue',      tag: 'route',    tagLabel: 'Route'    },
      { name: 'oil_gas_midstream.erp_writeback_queue',     desc: 'Stage the invoice in the ERP write-back queue (human approves commit)', tag: 'route',    tagLabel: 'Route'    },
      { name: 'oil_gas_midstream.audit_lens_log',          desc: 'Immutable audit-trail log entry with all decisions + sources',          tag: 'extract',  tagLabel: 'Extract'  },
    ],
    blueprints: [
      { id: 'bp-eprod-invoice', name: 'EPROD Vendor Invoice', version: 'v1.0', industry_label: 'Oil & Gas Midstream · EPROD',
        field_count: 14, confidence_pct: '96.8%', used_in_steps: [1, 2, 3],
        description: 'Vendor invoice schema covering header, line items, asset code, MSA reference, and tax code for EPROD accounts payable.',
        arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/invoice-v1',
        fields: [
          { name: 'vendor_name',     type: 'string', required: true,  confidence: 99.4 },
          { name: 'invoice_number',  type: 'string', required: true,  confidence: 99.1 },
          { name: 'invoice_date',    type: 'date',   required: true,  confidence: 98.7 },
          { name: 'po_reference',    type: 'string', required: false, confidence: 96.2 },
          { name: 'msa_reference',   type: 'string', required: true,  confidence: 97.8 },
          { name: 'asset_code',      type: 'string', required: true,  confidence: 98.4 },
          { name: 'line_items',      type: 'array',  required: true,  confidence: 95.1 },
          { name: 'total',           type: 'number', required: true,  confidence: 99.6 },
          { name: 'tax_code',        type: 'string', required: true,  confidence: 97.2 },
        ],
      },
    ],
    triggers: [
      { label: 'S3 invoice drop',  detail: 's3://apex-eprod-invoices-incoming/invoices/',  active: true  },
      { label: 'API endpoint',     detail: 'POST /api/v1/eprod/invoices',                   active: true  },
    ],
    runs: [
      { id: 'EPROD-INV-1842', title: 'Halliburton wireline svc · 12 lines', meta: 'Completed · 9 min ago · 6.4s',  dot: 'green', result: 'auto_approve · all lines within MSA',           tone: '#16a34a', chipCls: 'chip-green', conf: '0.97' },
      { id: 'EPROD-INV-1841', title: 'Baker Hughes pump rebuild',             meta: 'Completed · 24 min ago · 7.2s', dot: 'amber', result: 'HITL · line 4 variance 3.8% above MSA',         tone: '#d97706', chipCls: 'chip-amber', conf: '0.93' },
      { id: 'EPROD-INV-1840', title: 'Schlumberger logging run · $84K',      meta: 'Completed · 1 hr ago · 8.1s',   dot: 'amber', result: 'HITL · no PO, total > $50K threshold',          tone: '#d97706', chipCls: 'chip-amber', conf: '0.96' },
    ],
  },

  'pb-eprod-2': {
    name: 'PO-to-Contract Validation',
    industry_label: 'Oil & Gas Midstream · EPROD',
    description:
      'Pre-pay PO line-item validation against MSA scope, contracted rates, and tax codes. Validation cycle weeks → minutes.',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    actions_count_label: '7 actions',
    last_run_label: 'Last run: 12 min ago',
    version: 'v1.0.0',
    accuracy_pct: '98.1%',
    deploy_agent_name: 'POAgent',
    intent:
      'Validate every purchase order at issuance, not at audit. For each PO line, confirm the item falls within the vendor MSA\'s Schedule B scope, validate unit pricing against contracted rates with ±5% tolerance, and confirm the tax code matches the asset\'s classification (TX-E exempt vs TX-I industrial). Flag rate mismatches, scope-out items, and tax-code errors. Push exceptions to the procurement_exceptions queue within minutes.',
    output_fields: [
      { name: 'po_validation_report', type: 'object' },
      { name: 'exception_list',       type: 'array'  },
      { name: 'approval_routing',     type: 'string' },
      { name: 'audit_lens_event',     type: 'object' },
    ],
    recipe:
`## EPROD PO-to-Contract Validation Recipe

### Step 1 · EXTRACT — extract_po_lines
- Source: SAP MM PO release event or PO PDF drop
- Capture: vendor, msa_ref, asset_code, line items[], tax_code

### Step 2 · LOOKUP — lookup_msa_scope
- Resolve vendor → active MSA → Schedule B scope categories
- Build lookup map: asset_code → in_scope?

### Step 3 · VALIDATE — validate_rate_variance
- For each line: compare unit_price vs msa_rate_for_asset_code
- Flag if abs(variance) > 5%

### Step 4 · VALIDATE — check_tax_code
- Map asset_code → expected tax_code (TX-E vs TX-I)

### Step 5 · DECIDE — check_approval_threshold
- PO total vs vendor DOA limit
- > $250K → director_review regardless

### Step 6 · ROUTE — route_exception
- Any flag → procurement_exceptions queue with reason codes`,
    actions: [
      { name: 'oil_gas_midstream.extract_po_lines',         desc: 'BDA extraction of PO header + line items + asset codes',          tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.lookup_msa_scope',         desc: 'Resolve vendor MSA + Schedule B scope categories',                  tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.validate_rate_variance',   desc: 'Per-line rate comparison vs contracted MSA rates (±5%)',           tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.check_tax_code',           desc: 'Validate tax code matches asset classification',                    tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.check_approval_threshold', desc: 'Compare PO total vs vendor delegation-of-authority limits',         tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.route_exception',          desc: 'Push flagged lines to procurement_exceptions SQS queue',            tag: 'route',    tagLabel: 'Route'    },
      { name: 'oil_gas_midstream.audit_lens_log',           desc: 'Immutable validation event for compliance reporting',               tag: 'extract',  tagLabel: 'Extract'  },
    ],
    blueprints: [
      { id: 'bp-eprod-po', name: 'EPROD Purchase Order', version: 'v1.0', industry_label: 'Oil & Gas Midstream · EPROD',
        field_count: 16, confidence_pct: '98.1%', used_in_steps: [1, 2],
        description: 'PO schema covering header, line items, MSA reference, asset code, tax code, and approval chain.',
        arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/purchase-order-v1',
        fields: [
          { name: 'po_number',         type: 'string', required: true, confidence: 99.6 },
          { name: 'vendor_name',       type: 'string', required: true, confidence: 99.2 },
          { name: 'msa_reference',     type: 'string', required: true, confidence: 98.4 },
          { name: 'asset_code',        type: 'string', required: true, confidence: 98.7 },
          { name: 'line_items',        type: 'array',  required: true, confidence: 96.8 },
          { name: 'tax_code',          type: 'string', required: true, confidence: 97.1 },
          { name: 'total',             type: 'number', required: true, confidence: 99.7 },
          { name: 'approval_chain',    type: 'array',  required: true, confidence: 95.4 },
        ],
      },
    ],
    triggers: [
      { label: 'SAP PO release',  detail: 'EventBridge SAP.PO.Released',          active: true  },
      { label: 'API endpoint',    detail: 'POST /api/v1/eprod/po/validate',        active: true  },
    ],
    runs: [
      { id: 'EPROD-PO-1244', title: 'Kiewit pipe coating · 8 lines',  meta: 'Completed · 12 min ago · 5.1s', dot: 'green', result: 'auto_approve · in-scope, rates within 1.2%',    tone: '#16a34a', chipCls: 'chip-green', conf: '0.98' },
      { id: 'EPROD-PO-1243', title: 'Halliburton frac sand · $186K',  meta: 'Completed · 38 min ago · 4.8s', dot: 'amber', result: 'exception · line 3 out-of-scope per MSA §3.4',  tone: '#d97706', chipCls: 'chip-amber', conf: '0.94' },
      { id: 'EPROD-PO-1242', title: 'Emerson DCS upgrade · $312K',    meta: 'Completed · 1 hr ago · 5.6s',   dot: 'amber', result: 'director_review · over $250K threshold',         tone: '#d97706', chipCls: 'chip-amber', conf: '0.97' },
    ],
  },

  'pb-eprod-3': {
    name: 'Non-PO MSA Validation',
    industry_label: 'Oil & Gas Midstream · EPROD',
    description:
      'At-intake validation of non-PO transactions against active vendor MSAs — audit-ready evidence captured automatically.',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    actions_count_label: '6 actions',
    last_run_label: 'Last run: 18 min ago',
    version: 'v1.0.0',
    accuracy_pct: '97.4%',
    deploy_agent_name: 'VendorAgent',
    intent:
      'For every non-PO transaction (direct services, emergency work, retainer draws), confirm an active MSA exists for the vendor, validate that the requested scope is covered, check the requestor\'s approval threshold, and document audit-ready evidence (MSA section reference + scope match rationale). Flag any transaction with no MSA on file, expired MSA, or scope mismatch. The output is a fully-documented validation packet — not just a yes/no.',
    output_fields: [
      { name: 'msa_validation_packet', type: 'object' },
      { name: 'routing_decision',      type: 'string' },
      { name: 'audit_evidence_pack',   type: 'object' },
    ],
    recipe:
`## EPROD Non-PO MSA Validation Recipe

### Step 1 · EXTRACT — intake_non_po
- Source: ServiceNow request, AP intake form, or email parse

### Step 2 · LOOKUP — find_active_msa
- Search vendor MSAs where effective_date <= today < expiration_date
- If none → reject_no_msa with explicit reason

### Step 3 · VALIDATE — validate_scope_match
- Semantic match: requested scope vs MSA Schedule B
- Output: matched_section (e.g. "MSA-HAL-2024 §3.4 Wireline Services")

### Step 4 · DECIDE — check_approval_threshold
- Compare amount vs requestor.doa_limit

### Step 5 · DOCUMENT — document_audit_evidence
- Generate PDF: cover page + scope match notes + cited MSA excerpts
- Persist to s3://apex-eprod-audit/non-po-evidence/

### Step 6 · ROUTE — route_or_approve
- All gates clean → auto_approve + audit pack archived`,
    actions: [
      { name: 'oil_gas_midstream.intake_non_po',            desc: 'Parse the non-PO request (form, email, or API call)',                  tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.find_active_msa',          desc: 'Resolve vendor → active (non-expired) MSA',                             tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.validate_scope_match',     desc: 'Compare requested scope vs MSA scope categories; cite section',         tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.check_approval_threshold', desc: 'Validate requestor DOA covers the amount',                              tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.document_audit_evidence',  desc: 'Generate audit-ready PDF bundle with MSA pages + match notes',           tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.route_or_approve',         desc: 'Auto-approve clean txns; route to scope review otherwise',              tag: 'route',    tagLabel: 'Route'    },
    ],
    blueprints: [
      { id: 'bp-eprod-msa', name: 'EPROD Master Service Agreement', version: 'v1.0', industry_label: 'Oil & Gas Midstream · EPROD',
        field_count: 12, confidence_pct: '97.4%', used_in_steps: [2, 3],
        description: 'MSA schema covering identity, term, scope, rate card, billing terms, indemnity, and approval thresholds.',
        arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/msa-v1',
        fields: [
          { name: 'msa_id',              type: 'string', required: true, confidence: 99.8 },
          { name: 'vendor_name',         type: 'string', required: true, confidence: 99.4 },
          { name: 'effective_date',      type: 'date',   required: true, confidence: 98.6 },
          { name: 'expiration_date',     type: 'date',   required: true, confidence: 98.4 },
          { name: 'scope_categories',    type: 'array',  required: true, confidence: 96.7 },
          { name: 'rate_card',           type: 'array',  required: true, confidence: 95.8 },
          { name: 'approval_thresholds', type: 'array',  required: true, confidence: 97.1 },
        ],
      },
    ],
    triggers: [
      { label: 'ServiceNow request', detail: 'EventBridge ServiceNow.NonPORequest',  active: true  },
      { label: 'API endpoint',       detail: 'POST /api/v1/eprod/non-po/validate',    active: true  },
    ],
    runs: [
      { id: 'EPROD-NPO-624', title: 'Pipeline integrity inspection',    meta: 'Completed · 18 min ago · 6.7s', dot: 'green', result: 'auto_approve · matched MSA-HAL-2024 §4.1',    tone: '#16a34a', chipCls: 'chip-green', conf: '0.98' },
      { id: 'EPROD-NPO-623', title: 'Emergency wireline retrieval',     meta: 'Completed · 42 min ago · 5.4s', dot: 'green', result: 'auto_approve · audit pack archived',          tone: '#16a34a', chipCls: 'chip-green', conf: '0.97' },
      { id: 'EPROD-NPO-622', title: 'Specialty welding contractor',      meta: 'Completed · 1 hr ago · 7.1s',   dot: 'red',   result: 'reject_no_msa · vendor not in MSA registry',  tone: '#dc2626', chipCls: 'chip-red',   conf: '0.99' },
    ],
  },

  'pb-eprod-4': {
    name: 'Engineering Quote Processing',
    industry_label: 'Oil & Gas Midstream · EPROD',
    description:
      'Heterogeneous quote intake (Fluor, Bechtel, Emerson) → reconciled with historical pricing + linked to PO/invoice chain for full quote-to-pay traceability.',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    actions_count_label: '6 actions',
    last_run_label: 'Last run: 27 min ago',
    version: 'v1.0.0',
    accuracy_pct: '94.6%',
    deploy_agent_name: 'QuoteAgent',
    intent:
      'Process engineering quotes from Fluor, Bechtel, Emerson, and other EPC vendors. Extract scope description, milestones, unit pricing, validity window, and exclusions. Compare against the trailing 12-month historical pricing for similar scope. Flag quotes priced >10% above the historical average. Link the quote to the downstream PO + invoice chain so the full quote-to-pay history is audit-traceable.',
    output_fields: [
      { name: 'quote_extract',              type: 'object' },
      { name: 'historical_variance',         type: 'object' },
      { name: 'quote_chain_link',            type: 'object' },
      { name: 'procurement_recommendation',  type: 'string' },
    ],
    recipe:
`## EPROD Engineering Quote Processing Recipe

### Step 1 · EXTRACT — extract_quote_scope
- Source: vendor email PDF or portal upload
- BDA blueprint: bp-eprod-quote (13 fields)

### Step 2 · LOOKUP — lookup_historical_pricing
- Window: trailing 12 months
- Filter: same vendor + scope_category + asset_code
- Aggregate: median, P25, P75 of unit prices

### Step 3 · COMPUTE — compute_variance_vs_historical
- Per milestone: variance_pct = (quote_price - historical_median) / median

### Step 4 · LINK — link_to_po_chain
- Store quote_id in quote_to_pay_chain index

### Step 5 · DECIDE — route_procurement_decision
- variance <= 10% → approve_for_negotiation
- 10% < variance <= 25% → negotiate
- variance > 25% → reject + re-RFQ

### Step 6 · AUDIT — audit_lens_log`,
    actions: [
      { name: 'oil_gas_midstream.extract_quote_scope',            desc: 'BDA extraction of quote — scope, milestones, prices, validity',   tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.lookup_historical_pricing',      desc: 'Pull last 12 months of POs/invoices for same scope_category',     tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.compute_variance_vs_historical', desc: 'Per-milestone variance % vs historical median',                    tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.link_to_po_chain',               desc: 'Persist quote_id → eventual PO/invoice relationship',              tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.route_procurement_decision',     desc: 'approve / negotiate / reject with variance rationale',             tag: 'route',    tagLabel: 'Route'    },
      { name: 'oil_gas_midstream.audit_lens_log',                 desc: 'Quote-to-pay audit trail event',                                   tag: 'extract',  tagLabel: 'Extract'  },
    ],
    blueprints: [
      { id: 'bp-eprod-quote', name: 'EPROD Engineering Quote', version: 'v1.0', industry_label: 'Oil & Gas Midstream · EPROD',
        field_count: 13, confidence_pct: '94.6%', used_in_steps: [1],
        description: 'Engineering quote schema covering vendor, scope, milestone pricing, total estimate, validity, terms, and exclusions.',
        arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/engineering-quote-v1',
        fields: [
          { name: 'quote_number',     type: 'string', required: true, confidence: 99.1 },
          { name: 'vendor_name',      type: 'string', required: true, confidence: 99.4 },
          { name: 'project_name',     type: 'string', required: true, confidence: 97.6 },
          { name: 'milestones',       type: 'array',  required: true, confidence: 93.2 },
          { name: 'total_estimate',   type: 'number', required: true, confidence: 99.4 },
          { name: 'validity_until',   type: 'date',   required: true, confidence: 96.8 },
          { name: 'exclusions',       type: 'array',  required: true, confidence: 89.7 },
        ],
      },
    ],
    triggers: [
      { label: 'S3 quote drop',     detail: 's3://apex-eprod-quotes-incoming/quotes/',     active: true  },
      { label: 'API endpoint',      detail: 'POST /api/v1/eprod/quotes',                    active: true  },
    ],
    runs: [
      { id: 'EPROD-QT-318', title: 'Fluor compressor station retrofit',  meta: 'Completed · 27 min ago · 8.1s',  dot: 'green', result: 'approve · variance 3.4% vs 12-mo median',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.95' },
      { id: 'EPROD-QT-317', title: 'Bechtel pipeline ROW · 14 miles',     meta: 'Completed · 1 hr ago · 9.4s',     dot: 'amber', result: 'negotiate · variance 17% above historical',    tone: '#d97706', chipCls: 'chip-amber', conf: '0.92' },
      { id: 'EPROD-QT-316', title: 'Emerson DCS migration',                meta: 'Completed · 3 hr ago · 7.8s',    dot: 'green', result: 'approve · within range, validity 90 days',     tone: '#16a34a', chipCls: 'chip-green', conf: '0.96' },
    ],
  },

  'pb-eprod-5': {
    name: 'FERC Tariff Sheet Validation',
    industry_label: 'Oil & Gas Midstream · EPROD',
    description:
      'WOW · Extract effective FERC tariff + validate every shipper invoice line against gas-day-effective rates. Calculate monthly overbilling exposure across Enterprise NGL, Seaway Crude, Acadian Gas, Panhandle Eastern, Texas Eastern.',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    actions_count_label: '7 actions',
    last_run_label: 'Last run: 4 min ago',
    version: 'v1.0.0',
    accuracy_pct: '99.2%',
    deploy_agent_name: 'TariffAgent',
    intent:
      'Track every FERC tariff filing for the pipelines EPROD ships on (Enterprise NGL, Seaway Crude, Acadian Gas, Panhandle Eastern, Texas Eastern). Index the BLS PPI-FG series for next-cycle rate prediction (annual July 1 indexed adjustment). For every shipper invoice line, resolve the gas-day-effective tariff and validate the billed rate. Flag any rate > 1.5% above the effective FERC rate as overbilling. Compute rolling monthly overbilling exposure across all pipelines and surface to Treasury + Regulatory Affairs.',
    output_fields: [
      { name: 'ferc_tariff_index',           type: 'object' },
      { name: 'invoice_validation_report',    type: 'object' },
      { name: 'monthly_overbilling_exposure', type: 'number' },
      { name: 'escalation_packet',            type: 'object' },
    ],
    recipe:
`## EPROD FERC Tariff Sheet Validation Recipe (WOW use case)

### Step 1 · EXTRACT — extract_ferc_tariff
- Source: FERC.gov filing alerts → S3 ingestion of tariff PDFs
- BDA blueprint: bp-eprod-tariff (15 fields)

### Step 2 · INDEX — index_ppi_fg
- Pull BLS PPI-FG monthly series
- Compute YoY index → forecast July 1 annual adjustment

### Step 3 · LOOKUP — lookup_gas_day_rate
- Resolve effective tariff for gas_day + zone

### Step 4 · VALIDATE — validate_shipper_invoice_rate
- Compare billed_rate vs effective_ferc_rate
- Tolerance: 1.5% (FERC settlement convention)

### Step 5 · COMPUTE — compute_variance
- Per-line variance_pct + variance_usd

### Step 6 · AGGREGATE — compute_monthly_exposure
- Sum variance_usd across flagged lines per month + pipeline

### Step 7 · ESCALATE — escalate_hitl
- Monthly exposure > $250K → director_packet`,
    actions: [
      { name: 'oil_gas_midstream.extract_ferc_tariff',           desc: 'BDA extraction of FERC tariff sheet — rate schedules + effective dates', tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.index_ppi_fg',                  desc: 'Index BLS PPI-FG series for July 1 rate prediction',                     tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.lookup_gas_day_rate',           desc: 'Resolve the effective tariff rate for a gas day + zone',                  tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.validate_shipper_invoice_rate', desc: 'Compare billed rate vs gas-day-effective FERC rate',                      tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.compute_variance',              desc: 'Per-line variance % vs FERC; flag if > 1.5%',                              tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.compute_monthly_exposure',      desc: 'Aggregate USD overbilling across flagged lines per month',                 tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.escalate_hitl',                 desc: 'Director escalation with docket + tariff page citation',                   tag: 'route',    tagLabel: 'Route'    },
    ],
    blueprints: [
      { id: 'bp-eprod-tariff', name: 'EPROD FERC Tariff Sheet', version: 'v1.0', industry_label: 'Oil & Gas Midstream · EPROD',
        field_count: 15, confidence_pct: '99.2%', used_in_steps: [1, 3],
        description: 'FERC tariff schema covering docket, pipeline, commodity, effective window, zones, rate schedules, commodity + reservation charges, fuel retention, surcharges, PPI-FG indexing, and applicable shippers.',
        arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/ferc-tariff-v1',
        fields: [
          { name: 'tariff_id',           type: 'string', required: true, confidence: 99.8 },
          { name: 'ferc_docket',         type: 'string', required: true, confidence: 99.4 },
          { name: 'pipeline_name',       type: 'string', required: true, confidence: 99.6 },
          { name: 'effective_date',      type: 'date',   required: true, confidence: 99.2 },
          { name: 'zones',               type: 'array',  required: true, confidence: 97.4 },
          { name: 'rate_schedules',      type: 'array',  required: true, confidence: 96.8 },
          { name: 'commodity_charges',   type: 'array',  required: true, confidence: 96.2 },
          { name: 'reservation_charges', type: 'array',  required: true, confidence: 96.4 },
        ],
      },
    ],
    triggers: [
      { label: 'FERC filing alert',  detail: 's3://apex-eprod-ferc-tariffs/tariffs/',  active: true  },
      { label: 'Monthly aggregation',detail: 'Cron · 0 6 1 * * (1st of month, 06:00 CT)', active: true  },
    ],
    runs: [
      { id: 'EPROD-FERC-091', title: 'Seaway Crude shipper bill — Mar',     meta: 'Completed · 4 min ago · 11.2s', dot: 'red',   result: 'CRITICAL · $312K overbilling exposure',          tone: '#dc2626', chipCls: 'chip-red',   conf: '0.99' },
      { id: 'EPROD-FERC-090', title: 'Acadian Gas tariff RP24-118',          meta: 'Completed · 38 min ago · 8.4s', dot: 'green', result: 'extracted · 4 zones · 12 rate schedules',        tone: '#16a34a', chipCls: 'chip-green', conf: '0.99' },
      { id: 'EPROD-FERC-089', title: 'Panhandle Eastern · gas-day audit',     meta: 'Completed · 2 hr ago · 9.6s',   dot: 'amber', result: '$84K monthly exposure · below escalation',       tone: '#d97706', chipCls: 'chip-amber', conf: '0.98' },
    ],
  },

  'pb-eprod-6': {
    name: 'JIB Reconciliation vs AFE',
    industry_label: 'Oil & Gas Midstream · EPROD',
    description:
      'WOW · JIB partner statements matched to AFEs + working-interest math + AFE-bounds enforcement. Catches AFE overruns before they\'re paid.',
    status_label: 'Deployed',
    status_chip: 'chip-green',
    actions_count_label: '7 actions',
    last_run_label: 'Last run: 22 min ago',
    version: 'v1.0.0',
    accuracy_pct: '98.4%',
    deploy_agent_name: 'JIBAgent',
    intent:
      'Reconcile Joint Interest Billing (JIB) statements from JV operators (Phillips 66 Sweeny, Targa Mont Belvieu, EPROD-operated). For every JIB charge, match to its underlying AFE (Authorization for Expenditure), validate the working-interest split per the JOA, apply EPROD\'s partner share, and check whether the cumulative charges have breached the AFE remaining balance. Flag any JIB charge that would push cumulative-to-date above the AFE ceiling — critical overruns requiring escalation to Joint Venture Accounting before the next billing cycle closes.',
    output_fields: [
      { name: 'jib_recon_report',     type: 'object' },
      { name: 'afe_balance_status',   type: 'object' },
      { name: 'overrun_flags',        type: 'array'  },
      { name: 'jv_escalation_packet', type: 'object' },
    ],
    recipe:
`## EPROD JIB Reconciliation vs AFE Recipe (WOW use case)

### Step 1 · EXTRACT — extract_jib_statement
- Source: monthly JIB statement PDF/CSV from JV operator
- BDA blueprint: bp-eprod-jib (14 fields)

### Step 2 · LOOKUP — lookup_afe_balance
- Pull current AFE record from JV accounting ERP
- Compute remaining_balance = afe_ceiling - cumulative_charges_to_date

### Step 3 · COMPUTE — compute_partner_share
- From JOA: working_interest_pct (e.g. EPROD 35%)
- partner_share = gross_charge * wi_pct

### Step 4 · VALIDATE — check_jib_vs_afe
- Would (cumulative_to_date + this_jib_share) breach the ceiling?

### Step 5 · FLAG — flag_afe_overrun
- Critical: breach > 5% of AFE → critical_overrun

### Step 6 · ESCALATE — escalate_jv_accounting
- Critical flags → JV Accounting packet with JOA section + AFE history
- Block payment until reviewed

### Step 7 · AUDIT — audit_lens_log`,
    actions: [
      { name: 'oil_gas_midstream.extract_jib_statement',  desc: 'BDA extraction of JIB statement — JV, operator, AFE refs, charges',  tag: 'extract',  tagLabel: 'Extract'  },
      { name: 'oil_gas_midstream.lookup_afe_balance',     desc: 'Resolve AFE record + remaining balance per JV ERP',                   tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.compute_partner_share',  desc: 'Apply working-interest pct from JOA to gross charges',                 tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.check_jib_vs_afe',       desc: 'Validate cumulative JIB <= AFE ceiling per line',                      tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.flag_afe_overrun',       desc: 'Flag lines breaching AFE balance with overrun USD',                    tag: 'validate', tagLabel: 'Validate' },
      { name: 'oil_gas_midstream.escalate_jv_accounting', desc: 'JV escalation packet with JOA + AFE citations',                         tag: 'route',    tagLabel: 'Route'    },
      { name: 'oil_gas_midstream.audit_lens_log',         desc: 'Audit trail for JV partner reconciliation',                            tag: 'extract',  tagLabel: 'Extract'  },
    ],
    blueprints: [
      { id: 'bp-eprod-jib', name: 'EPROD JIB Statement', version: 'v1.0', industry_label: 'Oil & Gas Midstream · EPROD',
        field_count: 14, confidence_pct: '98.4%', used_in_steps: [1, 2],
        description: 'JIB statement schema covering JV, operator, AFE references, working-interest math, capital + operating charges, partner share, prior-period adjustments, and cumulative position.',
        arn: 'arn:aws:bedrock:us-east-1:EPROD:blueprint/jib-statement-v1',
        fields: [
          { name: 'statement_id',           type: 'string', required: true, confidence: 99.8 },
          { name: 'jv_name',                type: 'string', required: true, confidence: 99.4 },
          { name: 'operator',               type: 'string', required: true, confidence: 99.2 },
          { name: 'afe_reference',          type: 'string', required: true, confidence: 98.7 },
          { name: 'working_interest_pct',   type: 'number', required: true, confidence: 99.1 },
          { name: 'capital_charges',        type: 'array',  required: true, confidence: 96.8 },
          { name: 'operating_charges',      type: 'array',  required: true, confidence: 96.4 },
          { name: 'partner_share',          type: 'number', required: true, confidence: 99.2 },
          { name: 'cumulative_to_date',     type: 'number', required: true, confidence: 98.4 },
        ],
      },
    ],
    triggers: [
      { label: 'S3 JIB drop',        detail: 's3://apex-eprod-jib-incoming/jib-statements/', active: true  },
      { label: 'Weekly sweep',       detail: 'Cron · 0 6 * * MON (Monday 06:00)',             active: true  },
    ],
    runs: [
      { id: 'EPROD-JIB-518', title: 'Sweeny Frac · Phillips 66 · Mar',  meta: 'Completed · 22 min ago · 9.1s',  dot: 'red',   result: 'CRITICAL · AFE-2025-014 overrun 7.2%',             tone: '#dc2626', chipCls: 'chip-red',   conf: '0.99' },
      { id: 'EPROD-JIB-517', title: 'Mont Belvieu · Targa · Mar',         meta: 'Completed · 1 hr ago · 8.4s',     dot: 'green', result: 'clean · WI 32% · within AFE',                       tone: '#16a34a', chipCls: 'chip-green', conf: '0.98' },
      { id: 'EPROD-JIB-516', title: 'EPROD-op Gulf Coast JV · Feb',        meta: 'Completed · 3 hr ago · 10.2s',   dot: 'amber', result: 'warning · 2.1% over AFE on op-exp line',           tone: '#d97706', chipCls: 'chip-amber', conf: '0.97' },
    ],
  },
};

// ─────────────────────── Safe fallback for unknown ids ───────────────────────
// Per the CLAUDE.md ZERO-HARDCODING RULE: never silently render content from
// the wrong domain. When an id doesn't match any known map AND the API failed,
// render an explicit "not found" stub so the user sees the truth instead of
// invoice processing being misattributed to their actual workflow.

const DEFAULT_PLAYBOOK: PlaybookData = {
  name: 'Playbook not found',
  industry_label: '',
  description: 'No playbook matches this id, and the platform API is unreachable. Verify the id in the URL, or seed the playbook into DynamoDB via POST /api/v1/playbooks/seed?industry=<industry>.',
  status_label: 'Unknown',
  status_chip: 'chip-gray',
  actions_count_label: '— actions',
  last_run_label: '',
  version: '—',
  accuracy_pct: '—',
  deploy_agent_name: '',
  intent: '',
  output_fields: [],
  recipe: '',
  actions: [],
  blueprints: [],
  triggers: [],
  runs: [],
};
