/**
 * Multi-LLM configuration utility.
 *
 * Mirrors the demoMode.ts pattern: localStorage-backed, custom-event broadcast,
 * SSR-safe, exposed via React hook.
 *
 * The config object is keyed:
 *
 *   {
 *     "chatstp":             { "routing":        "amazon.nova-micro-v1:0" },
 *     "policy-agent":        { "tool_selection": "amazon.nova-lite-v1:0",
 *                              "synthesis":      "us.anthropic.claude-sonnet-4-5-v1" },
 *     "maintenance-agent":   { "tool_selection": "us.anthropic.claude-haiku-3-5-v1",
 *                              "synthesis":      "us.anthropic.claude-haiku-3-5-v1" },
 *     "diagnostics-agent":   { ... },
 *     "reliability-agent":   { ... }
 *   }
 *
 * Only slots the user explicitly customized appear here. Backend resolves
 * missing slots to the registry default.
 */

import { useEffect, useState } from 'react';

export type SlotKey = 'routing' | 'tool_selection' | 'synthesis';

/** {agent_id: {slot_key: model_id}} — only customized slots */
export type LLMConfig = Record<string, Partial<Record<SlotKey, string>>>;

/** Full backend strategy preset shape (mirrors model_registry.list_presets) */
export interface StrategyPreset {
  id: string;
  display_name: string;
  icon: string;
  description: string;
  overrides: LLMConfig;
  estimated_query_cost_usd: number;
}

/** Single dropdown option (mirrors ModelSpec.to_dict) */
export interface ModelOption {
  id: string;
  display_name: string;
  family: string;
  input_cost_per_1m_usd: number;
  output_cost_per_1m_usd: number;
  avg_latency_ms: number;
  suited_for: string[];
  description: string;
  estimated_query_cost_usd: number;
}

/** Single agent slot (mirrors AgentSlot in registry) */
export interface AgentSlotSpec {
  key: SlotKey;
  label: string;
  task_tag: string;
  default_id: string;
  default_model: ModelOption | null;
}

/** Full agent card spec (mirrors AgentSpec.to_dict) */
export interface AgentSpec {
  id: string;
  display_name: string;
  use_case: string;
  description: string;
  why: string;
  slots: AgentSlotSpec[];
}

export const LLM_CONFIG_STORAGE_KEY = 'apex.llmConfig';
export const LLM_PRESET_STORAGE_KEY = 'apex.llmPresetId';

/**
 * Cost-Optimized preset hard-coded here so the frontend can default to it
 * before /llm/presets has loaded. Mirrors backend services/model_registry.py
 * — keep in sync if the registry's preset values change.
 */
const COST_OPTIMIZED_DEFAULT: LLMConfig = {
  'chatstp':            { 'routing': 'amazon.nova-micro-v1:0' },
  'policy-agent':       { 'tool_selection': 'amazon.nova-lite-v1:0', 'synthesis': 'us.anthropic.claude-haiku-3-5-v1' },
  'maintenance-agent':  { 'tool_selection': 'amazon.nova-lite-v1:0', 'synthesis': 'us.anthropic.claude-haiku-3-5-v1' },
  'diagnostics-agent':  { 'tool_selection': 'amazon.nova-lite-v1:0', 'synthesis': 'us.anthropic.claude-haiku-3-5-v1' },
  'reliability-agent':  { 'tool_selection': 'amazon.nova-lite-v1:0', 'synthesis': 'us.anthropic.claude-sonnet-4-5-v1' },
};

/** First-run default applied when localStorage is empty. Set to Cost-Optimized
 *  so demos hit the cheap+fast path out of the box. Users can switch via
 *  Settings → Agent Models → Quality-First if they want full Opus. */
const APPLY_FIRST_RUN_DEFAULT = true;

/** SSR-safe load. Returns Cost-Optimized defaults on first run, or {} when
 *  the user has explicitly cleared via "Reset all to default". */
export function getLLMConfig(): LLMConfig {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.localStorage.getItem(LLM_CONFIG_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return parsed && typeof parsed === 'object' ? (parsed as LLMConfig) : {};
    }
    // First-run path — seed with Cost-Optimized defaults so latency is low
    // and the cost estimator immediately shows the savings narrative.
    if (APPLY_FIRST_RUN_DEFAULT) {
      window.localStorage.setItem(LLM_CONFIG_STORAGE_KEY, JSON.stringify(COST_OPTIMIZED_DEFAULT));
      window.localStorage.setItem(LLM_PRESET_STORAGE_KEY, 'cost_optimized');
      return COST_OPTIMIZED_DEFAULT;
    }
    return {};
  } catch {
    return {};
  }
}

/** Persist + broadcast. */
export function setLLMConfig(cfg: LLMConfig): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(LLM_CONFIG_STORAGE_KEY, JSON.stringify(cfg));
  } catch {
    // private-browsing / sandboxed iframes can throw
  }
  window.dispatchEvent(new CustomEvent('apex-llm-config-change', { detail: cfg }));
}

/** Override a single (agent, slot) cell. */
export function setLLMSlot(agentId: string, slot: SlotKey, modelId: string): void {
  const cfg = getLLMConfig();
  cfg[agentId] = { ...(cfg[agentId] || {}), [slot]: modelId };
  setLLMConfig(cfg);
  // Custom preset → "Custom"
  setActivePresetId(null);
}

/** Track which named preset was last applied (so the UI can show "Custom" otherwise). */
export function getActivePresetId(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage.getItem(LLM_PRESET_STORAGE_KEY);
  } catch {
    return null;
  }
}
export function setActivePresetId(id: string | null): void {
  if (typeof window === 'undefined') return;
  try {
    if (id) window.localStorage.setItem(LLM_PRESET_STORAGE_KEY, id);
    else window.localStorage.removeItem(LLM_PRESET_STORAGE_KEY);
  } catch {
    // ignore
  }
  window.dispatchEvent(new CustomEvent('apex-llm-preset-change', { detail: id }));
}

/** Apply a full preset's overrides — overwrites all customizations. */
export function applyPreset(preset: StrategyPreset): void {
  setLLMConfig(preset.overrides);
  setActivePresetId(preset.id);
}

/** Reset to registry defaults (clears localStorage). */
export function resetLLMConfig(): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.removeItem(LLM_CONFIG_STORAGE_KEY);
  } catch {
    // ignore
  }
  setActivePresetId(null);
  window.dispatchEvent(new CustomEvent('apex-llm-config-change', { detail: {} }));
}

/* ──────────────────────── React hook ──────────────────────── */

/**
 * Re-renders the calling component whenever the LLM config OR active preset id
 * changes (in this tab via custom event, or cross-tab via storage event).
 */
export function useLLMConfig(): {
  config: LLMConfig;
  activePresetId: string | null;
  setConfig: (cfg: LLMConfig) => void;
  setSlot: (agentId: string, slot: SlotKey, modelId: string) => void;
  applyPreset: (preset: StrategyPreset) => void;
  reset: () => void;
} {
  const [config, setConfig] = useState<LLMConfig>(() => getLLMConfig());
  const [activePresetId, setPresetId] = useState<string | null>(() => getActivePresetId());

  useEffect(() => {
    const onConfig = () => setConfig(getLLMConfig());
    const onPreset = () => setPresetId(getActivePresetId());
    const onStorage = (e: StorageEvent) => {
      if (e.key === LLM_CONFIG_STORAGE_KEY) setConfig(getLLMConfig());
      if (e.key === LLM_PRESET_STORAGE_KEY) setPresetId(getActivePresetId());
    };
    window.addEventListener('apex-llm-config-change', onConfig);
    window.addEventListener('apex-llm-preset-change', onPreset);
    window.addEventListener('storage', onStorage);
    return () => {
      window.removeEventListener('apex-llm-config-change', onConfig);
      window.removeEventListener('apex-llm-preset-change', onPreset);
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  return {
    config,
    activePresetId,
    setConfig: (cfg) => { setLLMConfig(cfg); setActivePresetId(null); },
    setSlot: setLLMSlot,
    applyPreset,
    reset: resetLLMConfig,
  };
}

/**
 * Helper for chat callers: build the model_overrides payload to attach to
 * /chat/invoke and /chat/sessions/{id}/messages requests so backend agents
 * pick the right AzureOpenAIModel.
 *
 * Returns undefined when no customizations are active (saves bytes on the wire).
 */
export function buildModelOverridesPayload(): LLMConfig | undefined {
  const cfg = getLLMConfig();
  if (Object.keys(cfg).length === 0) return undefined;
  return cfg;
}
