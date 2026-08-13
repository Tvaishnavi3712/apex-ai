/**
 * Settings → Agent Models panel.
 *
 * 5 agent cards (router + 4 specialists). Each card has 1-2 dropdowns
 * (the "slots" returned by /api/v1/llm/agents). Three preset buttons one-click
 * fill in every dropdown. A live cost-per-query estimator at the bottom shows
 * the projected cost vs the Quality-First baseline.
 *
 * Per-browser persistence via lib/llmConfig.ts (localStorage). When config
 * changes, custom event broadcast triggers any subscribed component to
 * re-render — including the chat client which attaches model_overrides
 * on every /chat/invoke call.
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  useLLMConfig,
  type LLMConfig, type SlotKey, type StrategyPreset,
  type ModelOption, type AgentSpec,
} from '@/lib/llmConfig';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function AgentModelsPanel() {
  const { config, activePresetId, setSlot, applyPreset, reset } = useLLMConfig();

  // Load registry data — models, agents, presets
  const modelsQ  = useQuery<{ models: ModelOption[] }>({
    queryKey: ['llm-models'],
    queryFn: async () => (await fetch(`${API_BASE_URL}/llm/models`)).json(),
    staleTime: 60_000,
  });
  const agentsQ  = useQuery<{ agents: AgentSpec[] }>({
    queryKey: ['llm-agents'],
    queryFn: async () => (await fetch(`${API_BASE_URL}/llm/agents`)).json(),
    staleTime: 60_000,
  });
  const presetsQ = useQuery<{ presets: StrategyPreset[] }>({
    queryKey: ['llm-presets'],
    queryFn: async () => (await fetch(`${API_BASE_URL}/llm/presets`)).json(),
    staleTime: 60_000,
  });

  // Live cost estimator — refresh whenever config changes
  const [costEstimate, setCostEstimate] = useState<{
    total_cost_usd: number;
    breakdown: Array<{ step: string; agent: string; slot: string; model_display: string; cost_usd: number }>;
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/llm/estimate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ overrides: config, intent: 'predictive_maintenance' }),
        });
        if (!r.ok || cancelled) return;
        const j = await r.json();
        if (!cancelled) setCostEstimate(j);
      } catch {
        // ignore — UI shows '—' if we can't reach the backend
      }
    })();
    return () => { cancelled = true; };
  }, [config]);

  const models    = modelsQ.data?.models ?? [];
  const agents    = agentsQ.data?.agents ?? [];
  const presets   = presetsQ.data?.presets ?? [];
  const baselineCost = useMemo(
    () => presets.find((p) => p.id === 'quality_first')?.estimated_query_cost_usd ?? 0,
    [presets]
  );
  const savings = useMemo(() => {
    if (!costEstimate || !baselineCost) return 0;
    return Math.round(((baselineCost - costEstimate.total_cost_usd) / baselineCost) * 100);
  }, [costEstimate, baselineCost]);

  if (agentsQ.isLoading || modelsQ.isLoading) {
    return (
      <div className="card" style={{ padding: 24, color: '#94a3b8' }}>
        Loading model registry…
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: 24 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16, gap: 12, flexWrap: 'wrap' }}>
        <div>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>
            Agent Models
            {activePresetId && (
              <span style={{
                marginLeft: 10, fontSize: 10, fontWeight: 700, letterSpacing: '.08em',
                padding: '2px 8px', borderRadius: 4,
                background: '#7c3aed', color: '#fff',
              }}>
                {presets.find((p) => p.id === activePresetId)?.display_name?.toUpperCase() || 'PRESET'}
              </span>
            )}
            {!activePresetId && Object.keys(config).length > 0 && (
              <span style={{
                marginLeft: 10, fontSize: 10, fontWeight: 700, letterSpacing: '.08em',
                padding: '2px 8px', borderRadius: 4,
                background: '#475569', color: '#fff',
              }}>
                CUSTOM
              </span>
            )}
          </h3>
          <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.5 }}>
            Pick which LLM powers each agent. Saved per browser. Backend honors choices on the next chat invocation.
          </p>
        </div>
        <button
          onClick={reset}
          style={{
            padding: '6px 12px', fontSize: 12, fontWeight: 500,
            background: 'transparent', border: '1px solid #e2e8f0',
            borderRadius: 8, cursor: 'pointer', color: '#64748b',
          }}
        >
          Reset all to default
        </button>
      </div>

      {/* Preset buttons */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 20 }}>
        {presets.map((p) => (
          <PresetButton
            key={p.id}
            preset={p}
            active={activePresetId === p.id}
            onClick={() => applyPreset(p)}
          />
        ))}
      </div>

      {/* Agent cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 16 }}>
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            config={config}
            models={models}
            onSlotChange={setSlot}
          />
        ))}
      </div>

      {/* Cost estimator footer */}
      {costEstimate && (
        <div style={{
          padding: '14px 18px', borderRadius: 12,
          background: 'linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%)',
          border: '1px solid #bbf7d0',
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16,
        }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#16a34a' }}>
              Avg cost / query
            </div>
            <div className="mono" style={{ fontSize: 22, fontWeight: 800, color: '#0f172a', marginTop: 4 }}>
              ${costEstimate.total_cost_usd.toFixed(4)}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#dc2626' }}>
              Quality-First baseline
            </div>
            <div className="mono" style={{ fontSize: 22, fontWeight: 800, color: '#dc2626', marginTop: 4, opacity: 0.7 }}>
              ${baselineCost.toFixed(4)}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#2563eb' }}>
              Savings
            </div>
            <div className="mono" style={{ fontSize: 22, fontWeight: 800, color: '#2563eb', marginTop: 4 }}>
              {savings > 0 ? `↓ ${savings}%` : '—'}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ──────────────────────────── preset button ──────────────────────────── */

function PresetButton({
  preset, active, onClick,
}: { preset: StrategyPreset; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: '14px 16px', textAlign: 'left',
        borderRadius: 12, fontFamily: 'inherit', cursor: 'pointer',
        border: active ? '1.5px solid #7c3aed' : '1.5px solid #e2e8f0',
        background: active ? 'linear-gradient(135deg, #faf5ff, #f3e8ff)' : '#fff',
        transition: 'all .15s',
      }}
    >
      <div style={{ fontSize: 12, fontWeight: 700, color: active ? '#7c3aed' : '#0f172a' }}>
        <span style={{ marginRight: 6 }}>{preset.icon}</span>{preset.display_name}
      </div>
      <div className="mono" style={{ fontSize: 11, color: '#16a34a', marginTop: 4, fontWeight: 600 }}>
        ${preset.estimated_query_cost_usd.toFixed(4)} / query
      </div>
      <div style={{ fontSize: 10, color: '#64748b', marginTop: 6, lineHeight: 1.4 }}>
        {preset.description}
      </div>
    </button>
  );
}

/* ──────────────────────────── agent card ──────────────────────────── */

function AgentCard({
  agent, config, models, onSlotChange,
}: {
  agent: AgentSpec;
  config: LLMConfig;
  models: ModelOption[];
  onSlotChange: (agentId: string, slot: SlotKey, modelId: string) => void;
}) {
  // Only models suited for this slot's task tag, but always include the
  // current pick (in case it's outside the suited set — rare but possible).
  const allModelIds = useMemo(() => new Set(models.map((m) => m.id)), [models]);

  const currentSlotPick = (slotKey: string): string => {
    return config[agent.id]?.[slotKey as SlotKey] ?? agent.slots.find((s) => s.key === slotKey)!.default_id;
  };

  const currentSlotCost = (slotKey: string): number => {
    const id = currentSlotPick(slotKey);
    const m = models.find((mm) => mm.id === id);
    if (!m) return 0;
    // Per-slot rough estimate (tool selection: 1.5K in / 200 out; synth: 2.5K in / 400 out)
    if (slotKey === 'synthesis') {
      return (m.input_cost_per_1m_usd * 2500 + m.output_cost_per_1m_usd * 400) / 1_000_000;
    }
    return (m.input_cost_per_1m_usd * 1500 + m.output_cost_per_1m_usd * 200) / 1_000_000;
  };

  const cardCost = agent.slots.reduce((sum, s) => sum + currentSlotCost(s.key), 0);

  return (
    <div style={{
      padding: '14px 18px', borderRadius: 12,
      background: '#fff', border: '1px solid #f1f5f9',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 10 }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a' }}>
            {agent.display_name}
            <span style={{
              marginLeft: 8, fontSize: 10, fontWeight: 600, letterSpacing: '.04em',
              padding: '1px 6px', borderRadius: 4,
              background: '#f1f5f9', color: '#475569',
            }}>
              {agent.use_case}
            </span>
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{agent.description}</div>
        </div>
        <div className="mono" style={{ fontSize: 12, color: '#16a34a', fontWeight: 700 }}>
          ${cardCost.toFixed(4)}/query
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {agent.slots.map((slot) => {
          const currentId = currentSlotPick(slot.key);
          const cost = currentSlotCost(slot.key);
          // Filter dropdown to models suited for this task — but include current pick
          const options = models.filter(
            (m) => m.suited_for.includes(slot.task_tag) || m.id === currentId
          );
          return (
            <div key={slot.key} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <label style={{
                fontSize: 11, fontWeight: 600, color: '#64748b',
                minWidth: 110, flexShrink: 0,
              }}>
                {slot.label}:
              </label>
              <select
                value={currentId}
                onChange={(e) => onSlotChange(agent.id, slot.key, e.target.value)}
                style={{
                  flex: 1, padding: '6px 10px', fontSize: 12,
                  background: '#fff', border: '1px solid #e2e8f0', borderRadius: 8,
                  fontFamily: 'inherit', cursor: 'pointer',
                }}
              >
                {options.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.display_name}  ·  ${m.input_cost_per_1m_usd}/M in
                  </option>
                ))}
              </select>
              <span className="mono" style={{ fontSize: 11, color: '#94a3b8', minWidth: 70, textAlign: 'right' }}>
                ${cost.toFixed(4)}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{
        fontSize: 11, color: '#64748b', lineHeight: 1.5, marginTop: 10,
        padding: '8px 10px', background: '#f8fafc', borderRadius: 6,
        borderLeft: '3px solid #cbd5e1',
      }}>
        <span style={{ fontWeight: 700, color: '#475569' }}>Why: </span>
        {agent.why}
      </div>
    </div>
  );
}
