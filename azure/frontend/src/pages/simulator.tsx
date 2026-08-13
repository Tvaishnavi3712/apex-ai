/**
 * What-If Simulator — live crisis rehearsal for the C-suite.
 *
 * All data comes from the backend:
 *   • GET  /api/v1/simulator/scenarios     — list of injectable crises
 *   • POST /api/v1/simulator/run/{id}      — dispatches the scenario to the
 *                                             Logistics Foundry Agent Service runtime and
 *                                             returns its real reasoning trace
 *                                             + final mitigation summary.
 */

import React, { useEffect, useState } from 'react';
import Head from 'next/head';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useDemoMode } from '@/lib/demoMode';
import { VerizonSimulator } from '@/components/Dashboard/VerizonSimulator';

/** Scenarios seeded by backend/scripts/seed_killer_features.py — protected from delete. */
const SEED_IDS = new Set(['port-strike-savannah', 'aluminum-tariff-30', 'supplier-bankruptcy', 'cyber-ransomware-vendor']);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ═════════════════════ types (mirror backend) ═════════════════════ */

interface Exposure {
  plant: string;
  units: number;
  usd:   number;
}

interface RerouteOption {
  rank:            string;
  tier:            string;   // PREFERRED | FALLBACK | LAST_RESORT
  supplier:        string;
  cost_delta_pct:  number;
  delay_days:      number;
  capacity:        string;
  notes:           string;
}

interface Scenario {
  scenario_id:   string;
  label:         string;
  tagline:       string;
  severity:      string;     // HIGH | MEDIUM | CRITICAL
  region:        string;
  material:      string;
  delay_days:    number;
  exposures:     Exposure[];
  options:       RerouteOption[];
  director:      string;
  agent_id:      string;
}

interface ReasoningStep {
  step:    number;
  kind:    string;           // thought | action | observation | answer
  text:    string;
  action?: string;
}

interface RunResponse {
  scenario_id:   string;
  status:        'complete' | 'foundry_agent_offline';
  reasoning:     ReasoningStep[];
  actions_taken: string[];
  final_answer:  string;
  latency_ms:    number;
  agent_id:      string;
}

/* ═════════════════════ component ═════════════════════ */

// Top-level dispatcher — Verizon Far Edge gets its own firmware/field war-game.
// Split per-branch so hook ordering stays stable (rules-of-hooks).
export default function SimulatorPage() {
  const [demoMode] = useDemoMode();
  if (demoMode === 'verizon_far_edge' || demoMode === 'telecommunications') {
    return <VerizonSimulator />;
  }
  return <GenericSimulatorPage />;
}

function GenericSimulatorPage() {
  const qc = useQueryClient();
  const scenariosQ = useQuery<Scenario[]>({
    queryKey: ['simulator-scenarios'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/simulator/scenarios`);
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  const scenarios = scenariosQ.data ?? [];
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [newOpen, setNewOpen]       = useState(false);
  const selected = scenarios.find((s) => s.scenario_id === selectedId) ?? scenarios[0] ?? null;

  const deleteScenario = async (scenarioId: string) => {
    if (!confirm(`Delete scenario "${scenarioId}"? This can't be undone.`)) return;
    try {
      const r = await fetch(`${API_BASE_URL}/simulator/scenarios/${encodeURIComponent(scenarioId)}`, { method: 'DELETE' });
      if (!r.ok) throw new Error(`status ${r.status}`);
      await qc.invalidateQueries({ queryKey: ['simulator-scenarios'] });
      if (selectedId === scenarioId) setSelectedId(null);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('[Simulator] delete failed', e);
      alert(`Delete failed: ${e instanceof Error ? e.message : 'Unknown error'}`);
    }
  };

  // Initialise selection once scenarios load.
  useEffect(() => {
    if (!selectedId && scenarios.length > 0) {
      setSelectedId(scenarios[0].scenario_id);
    }
  }, [scenarios, selectedId]);

  // Run state
  const [runState, setRunState] = useState<
    | { kind: 'idle' }
    | { kind: 'running'; shown: ReasoningStep[]; startedAt: number }
    | { kind: 'done';    response: RunResponse }
    | { kind: 'error';   message: string }
  >({ kind: 'idle' });

  const runSim = async () => {
    if (!selected) {
      // eslint-disable-next-line no-console
      console.warn('[Simulator] runSim called with no selected scenario');
      return;
    }
    // eslint-disable-next-line no-console
    console.info('[Simulator] dispatching', selected.scenario_id);
    setRunState({ kind: 'running', shown: [], startedAt: Date.now() });
    try {
      const r = await fetch(`${API_BASE_URL}/simulator/run/${selected.scenario_id}`, { method: 'POST' });
      if (!r.ok) {
        const body = await r.text().catch(() => '');
        throw new Error(`${r.status} ${r.statusText} ${body.slice(0, 200)}`);
      }
      const data = (await r.json()) as RunResponse;

      // Animate the steps in as the user watches, using timestamps proportional
      // to the real latency so it feels live but never faster than the real
      // Foundry Agent Service call. If latency_ms is large, we cap the reveal at ~6s total.
      const totalReveal = Math.min(6000, Math.max(1200, data.reasoning.length * 450));
      const perStep = data.reasoning.length > 0 ? totalReveal / data.reasoning.length : 0;

      if (data.reasoning.length === 0) {
        setRunState({ kind: 'done', response: data });
        return;
      }
      const buffer: ReasoningStep[] = [];
      data.reasoning.forEach((step, i) => {
        setTimeout(() => {
          buffer.push(step);
          setRunState((cur) =>
            cur.kind === 'running'
              ? { kind: 'running', shown: [...buffer], startedAt: cur.startedAt }
              : cur,
          );
          if (i === data.reasoning.length - 1) {
            setTimeout(() => setRunState({ kind: 'done', response: data }), 260);
          }
        }, Math.round((i + 1) * perStep));
      });
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('[Simulator] run failed', e);
      setRunState({ kind: 'error', message: e instanceof Error ? e.message : 'Request failed' });
    }
  };

  const resetSim = () => setRunState({ kind: 'idle' });

  const totalVar = selected ? selected.exposures.reduce((s, e) => s + e.usd, 0) : 0;
  const isRunning = runState.kind === 'running';
  const shownSteps =
    runState.kind === 'running' ? runState.shown :
    runState.kind === 'done'    ? runState.response.reasoning :
    [];
  const finalAnswer = runState.kind === 'done' ? runState.response.final_answer : '';
  const runLatency  = runState.kind === 'done' ? runState.response.latency_ms   : 0;
  const runStatus   = runState.kind === 'done' ? runState.response.status       : null;

  return (
    <>
      <Head><title>Simulator | APEX</title></Head>

      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #0b1220 0%, #111827 55%, #0b1220 100%)',
        borderRadius: 20,
        padding: '22px 24px',
        marginBottom: 20,
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div aria-hidden style={{ position: 'absolute', top: -60, right: -60, width: 220, height: 220, borderRadius: '50%', background: 'radial-gradient(closest-side, rgba(124,58,237,.16), transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.18em', textTransform: 'uppercase', color: '#a78bfa' }}>
              What-If Simulator
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>
              Inject a crisis. Watch agents mitigate it live.
            </div>
            <div style={{ fontSize: 12, color: '#cbd5e1', marginTop: 4 }}>
              Agentic war-gaming for the C-suite — dispatches to the Logistics Foundry Agent Service runtime and streams its real reasoning trace back.
            </div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button
              onClick={resetSim}
              disabled={isRunning || runState.kind === 'idle'}
              style={{
                padding: '8px 16px', fontSize: 13, fontWeight: 600,
                background: 'rgba(148,163,184,.15)', color: '#e2e8f0',
                border: '1px solid rgba(148,163,184,.25)', borderRadius: 10,
                cursor: 'pointer', opacity: isRunning ? 0.5 : 1,
              }}
            >Reset</button>
            <button
              onClick={runSim}
              disabled={isRunning || !selected}
              style={{
                padding: '8px 18px', fontSize: 13, fontWeight: 700,
                background: isRunning ? 'rgba(139,92,246,.4)' : 'linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%)',
                color: '#fff', border: 'none', borderRadius: 10,
                cursor: (isRunning || !selected) ? 'not-allowed' : 'pointer',
                boxShadow: isRunning ? 'none' : '0 10px 24px rgba(124,58,237,.35)',
              }}
            >
              {isRunning ? 'Simulating…' : '▶  Run Simulation'}
            </button>
          </div>
        </div>
      </div>

      {/* 3-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr 360px', gap: 16 }}>
        {/* LEFT — Inject Crisis */}
        <section style={{
          background: '#0b1220', color: '#e2e8f0',
          borderRadius: 16, padding: 18, height: 'fit-content',
          position: 'sticky', top: 16,
          boxShadow: '0 10px 30px rgba(2,6,23,.3)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#60a5fa' }}>
              Inject Crisis
            </div>
            <button
              onClick={() => setNewOpen(true)}
              style={{
                fontSize: 11, fontWeight: 700,
                padding: '5px 10px', borderRadius: 8,
                background: 'rgba(96,165,250,.12)', color: '#60a5fa',
                border: '1px solid rgba(96,165,250,.35)',
                cursor: 'pointer',
              }}
            >+ New Crisis</button>
          </div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 14 }}>
            {scenariosQ.isLoading ? 'Loading scenarios…' : `${scenarios.length} scenario${scenarios.length === 1 ? '' : 's'} · persisted in Cosmos DB`}
          </div>

          {scenariosQ.error && (
            <div style={{ padding: 10, borderRadius: 8, background: 'rgba(239,68,68,.1)', border: '1px solid rgba(239,68,68,.3)', color: '#fca5a5', fontSize: 11 }}>
              Failed to load scenarios. Is the backend running?
              <div className="mono" style={{ marginTop: 4 }}>{String(scenariosQ.error)}</div>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {scenarios.map((s) => {
              const isCustom = !SEED_IDS.has(s.scenario_id);
              return (
                <div
                  key={s.scenario_id}
                  style={{
                    position: 'relative',
                    padding: '12px 14px',
                    borderRadius: 12,
                    background: selected?.scenario_id === s.scenario_id ? 'rgba(59,130,246,.15)' : 'rgba(30,41,59,.45)',
                    border: `1px solid ${selected?.scenario_id === s.scenario_id ? '#3b82f6' : 'rgba(148,163,184,.15)'}`,
                    color: '#f1f5f9',
                    cursor: 'pointer',
                  }}
                  onClick={() => { setSelectedId(s.scenario_id); resetSim(); }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6, marginBottom: 4 }}>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>{s.label}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      {isCustom && (
                        <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 4, background: 'rgba(139,92,246,.18)', color: '#c4b5fd', letterSpacing: '.06em' }}>
                          CUSTOM
                        </span>
                      )}
                      <SeverityPill severity={s.severity} />
                      {isCustom && (
                        <button
                          aria-label="Delete scenario"
                          title="Delete this scenario"
                          onClick={(e) => { e.stopPropagation(); deleteScenario(s.scenario_id); }}
                          style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: '#fca5a5', padding: 0, fontSize: 14, lineHeight: 1,
                          }}
                        >×</button>
                      )}
                    </div>
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.45 }}>{s.tagline}</div>
                </div>
              );
            })}
          </div>
        </section>

        {/* CENTER — Live reasoning */}
        <section style={{
          background: '#0b1220', color: '#e2e8f0',
          borderRadius: 16, padding: 20, minHeight: 520,
          boxShadow: '0 10px 30px rgba(2,6,23,.3)',
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#34d399' }}>
                Live Agent Reasoning
              </div>
              <div style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>{selected?.label ?? '—'}</div>
              {selected && (
                <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>
                  Severity {selected.severity} · Region {selected.region} · Material {selected.material} · Delay {selected.delay_days}d
                </div>
              )}
              {runState.kind === 'done' && (
                <div style={{ fontSize: 11, color: '#cbd5e1', marginTop: 4 }}>
                  Foundry Agent Service · {runLatency} ms · {runStatus === 'foundry_agent_offline' ? 'offline (returned fallback)' : 'complete'}
                </div>
              )}
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 10, color: '#94a3b8', letterSpacing: '.12em', textTransform: 'uppercase', fontWeight: 700 }}>
                Total VaR
              </div>
              <div style={{ fontFamily: "'JetBrains Mono', ui-monospace, monospace", fontSize: 24, fontWeight: 800, color: '#f8fafc' }}>
                ${totalVar.toLocaleString()}
              </div>
            </div>
          </div>

          {/* Exposure strip */}
          {selected && (
            <div style={{ display: 'grid', gridTemplateColumns: `repeat(${selected.exposures.length}, 1fr)`, gap: 8, marginBottom: 16 }}>
              {selected.exposures.map((e) => (
                <div key={e.plant} style={{ padding: 10, background: 'rgba(30,41,59,.6)', borderRadius: 10, border: '1px solid rgba(148,163,184,.12)' }}>
                  <div style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600 }}>{e.plant}</div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginTop: 2 }} className="mono">${e.usd.toLocaleString()}</div>
                  <div style={{ fontSize: 10, color: '#94a3b8' }}>{e.units.toLocaleString()} units at risk</div>
                </div>
              ))}
            </div>
          )}

          {/* Reasoning stream */}
          <div style={{
            borderRadius: 12,
            background: 'rgba(30,41,59,.45)',
            border: '1px solid rgba(148,163,184,.12)',
            padding: 14,
            minHeight: 260,
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
            fontSize: 12, lineHeight: 1.65,
          }}>
            {runState.kind === 'idle' && (
              <div style={{ color: '#94a3b8' }}>
                <div>&gt; standing by · click <span style={{ color: '#a78bfa', fontWeight: 600 }}>▶ Run Simulation</span> to dispatch this scenario to the Logistics Foundry Agent Service runtime.</div>
                <div style={{ color: '#64748b', marginTop: 6 }}># The real trace (thoughts + tool calls + observations + final answer) streams here.</div>
              </div>
            )}
            {runState.kind === 'error' && (
              <div style={{ color: '#fca5a5' }}>
                Simulation failed: <span className="mono">{runState.message}</span>
              </div>
            )}
            {shownSteps.map((s, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, padding: '3px 0' }}>
                <span style={{ color: KIND_COLOR[s.kind] ?? '#94a3b8', minWidth: 76, fontSize: 10, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase' }}>
                  {s.kind}{s.action ? ` · ${s.action}` : ''}
                </span>
                <span style={{ color: '#e2e8f0', whiteSpace: 'pre-wrap', flex: 1 }}>{s.text}</span>
              </div>
            ))}
            {isRunning && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, paddingTop: 4 }}>
                <span style={{ minWidth: 76 }} />
                <TypingDotsDark />
              </div>
            )}
            {runState.kind === 'done' && finalAnswer && (
              <div style={{
                marginTop: 14, padding: 12, borderRadius: 10,
                background: 'rgba(124,58,237,.12)',
                border: '1px solid rgba(124,58,237,.35)',
                color: '#e9d5ff', whiteSpace: 'pre-wrap',
              }}>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#c4b5fd', marginBottom: 6 }}>
                  Agent summary
                </div>
                <div>{finalAnswer}</div>
              </div>
            )}
          </div>
        </section>

        {/* RIGHT — Mitigation Playbook */}
        <section style={{
          background: '#0b1220', color: '#e2e8f0',
          borderRadius: 16, padding: 18, minHeight: 520,
          boxShadow: '0 10px 30px rgba(2,6,23,.3)',
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#fbbf24' }}>
            Mitigation Playbook
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>
            {selected?.options.length ? `${selected.options.length} ranked options · persisted` : 'Select a scenario'}
          </div>
          {selected && (
            <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2, marginBottom: 14 }}>
              Escalates to <span style={{ color: '#f1f5f9', fontWeight: 600 }}>{selected.director}</span>
            </div>
          )}

          {selected && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 12 }}>
              {selected.options.map((o) => <OptionCard key={o.rank} opt={o} />)}
              <button
                disabled={runState.kind !== 'done'}
                style={{
                  marginTop: 8, padding: '10px 14px',
                  background: runState.kind === 'done'
                    ? 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)'
                    : 'rgba(34,197,94,.25)',
                  color: '#fff', fontWeight: 700, fontSize: 13,
                  border: 'none', borderRadius: 10,
                  cursor: runState.kind === 'done' ? 'pointer' : 'not-allowed',
                  boxShadow: runState.kind === 'done' ? '0 10px 24px rgba(22,163,74,.3)' : 'none',
                }}
              >
                {runState.kind === 'done'
                  ? 'Approve Option A + dispatch playbook'
                  : 'Run simulation to enable approval'}
              </button>
            </div>
          )}
        </section>
      </div>

      {newOpen && (
        <NewScenarioModal
          onClose={() => setNewOpen(false)}
          onCreated={async (created) => {
            await qc.invalidateQueries({ queryKey: ['simulator-scenarios'] });
            setSelectedId(created.scenario_id);
            setNewOpen(false);
            resetSim();
          }}
        />
      )}
    </>
  );
}

/* ═════════════════════ sub-components ═════════════════════ */

const KIND_COLOR: Record<string, string> = {
  thought:     '#a78bfa',
  action:      '#22d3ee',
  observation: '#60a5fa',
  answer:      '#fbbf24',
};

function SeverityPill({ severity }: { severity: string }) {
  const map: Record<string, { bg: string; color: string; label: string }> = {
    MEDIUM:   { bg: 'rgba(245,158,11,.18)', color: '#fbbf24', label: 'MEDIUM' },
    HIGH:     { bg: 'rgba(239,68,68,.18)',  color: '#f87171', label: 'HIGH' },
    CRITICAL: { bg: 'rgba(220,38,38,.25)',  color: '#fca5a5', label: 'CRITICAL' },
  };
  const m = map[severity] ?? { bg: 'rgba(148,163,184,.18)', color: '#cbd5e1', label: severity };
  return (
    <span style={{
      fontSize: 9, fontWeight: 700, letterSpacing: '.08em',
      padding: '2px 6px', borderRadius: 4,
      background: m.bg, color: m.color,
    }}>{m.label}</span>
  );
}

function OptionCard({ opt }: { opt: RerouteOption }) {
  const tierColor: Record<string, { bg: string; bd: string; text: string }> = {
    PREFERRED:   { bg: 'rgba(34,197,94,.15)',  bd: '#22c55e', text: '#86efac' },
    FALLBACK:    { bg: 'rgba(59,130,246,.15)', bd: '#3b82f6', text: '#93c5fd' },
    LAST_RESORT: { bg: 'rgba(239,68,68,.15)',  bd: '#ef4444', text: '#fca5a5' },
  };
  const c = tierColor[opt.tier] ?? tierColor.FALLBACK;
  return (
    <div style={{
      padding: 14, borderRadius: 12,
      background: c.bg, border: `1px solid ${c.bd}55`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: c.text, letterSpacing: '.08em' }}>
          Option {opt.rank} · {opt.tier}
        </span>
        <span style={{ fontSize: 10, color: '#94a3b8' }}>capacity {opt.capacity}</span>
      </div>
      <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9' }}>{opt.supplier}</div>
      <div style={{ display: 'flex', gap: 14, marginTop: 6, fontSize: 12, color: '#cbd5e1' }}>
        <span><span className="mono" style={{ color: '#f1f5f9', fontWeight: 700 }}>{opt.cost_delta_pct > 0 ? `+${opt.cost_delta_pct}%` : `${opt.cost_delta_pct}%`}</span> cost</span>
        <span><span className="mono" style={{ color: '#f1f5f9', fontWeight: 700 }}>{opt.delay_days}d</span> delay</span>
      </div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, lineHeight: 1.5 }}>{opt.notes}</div>
    </div>
  );
}

function TypingDotsDark() {
  return (
    <div style={{ display: 'inline-flex', gap: 5 }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: 6, height: 6, borderRadius: '50%',
            background: '#60a5fa',
            animation: `dvrpulse 1.1s ${i * 0.15}s infinite ease-in-out`,
            opacity: 0.35,
          }}
        />
      ))}
      <style>{`
        @keyframes dvrpulse {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
          30%           { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

/* ═════════════════════ New Scenario modal ═════════════════════ */

type ModalExposure = { plant: string; units: string; usd: string };
type ModalOption   = {
  rank:  'A' | 'B' | 'C';
  tier:  'PREFERRED' | 'FALLBACK' | 'LAST_RESORT';
  supplier: string;
  cost_delta_pct: string;
  delay_days: string;
  capacity: 'SUFFICIENT' | 'PARTIAL' | 'LIMITED';
  notes: string;
};

function emptyOption(rank: 'A' | 'B' | 'C', tier: ModalOption['tier']): ModalOption {
  return { rank, tier, supplier: '', cost_delta_pct: '0', delay_days: '0', capacity: 'SUFFICIENT', notes: '' };
}

function NewScenarioModal({
  onClose, onCreated,
}: {
  onClose: () => void;
  onCreated: (s: Scenario) => void;
}) {
  const [label,      setLabel]      = useState('');
  const [tagline,    setTagline]    = useState('');
  const [severity,   setSeverity]   = useState<'MEDIUM' | 'HIGH' | 'CRITICAL'>('HIGH');
  const [region,     setRegion]     = useState('North America');
  const [material,   setMaterial]   = useState('');
  const [delayDays,  setDelayDays]  = useState('7');
  const [director,   setDirector]   = useState('Marcus Webb · SVP Supply Chain');
  const [agentId,    setAgentId]    = useState<'logisticsbot' | 'customerops' | 'qcbot'>('logisticsbot');
  const [exposures,  setExposures]  = useState<ModalExposure[]>([{ plant: '', units: '0', usd: '0' }]);
  const [options,    setOptions]    = useState<ModalOption[]>([
    emptyOption('A', 'PREFERRED'),
    emptyOption('B', 'FALLBACK'),
    emptyOption('C', 'LAST_RESORT'),
  ]);
  const [busy, setBusy] = useState(false);
  const [err, setErr]   = useState<string | null>(null);

  const submit = async () => {
    if (!label.trim()) { setErr('Label is required.'); return; }
    setBusy(true); setErr(null);
    const payload = {
      label:      label.trim(),
      tagline:    tagline.trim(),
      severity,
      region:     region.trim(),
      material:   material.trim(),
      delay_days: Math.max(0, parseInt(delayDays || '0', 10) || 0),
      director:   director.trim(),
      agent_id:   agentId,
      exposures:  exposures
        .filter((e) => e.plant.trim())
        .map((e) => ({
          plant: e.plant.trim(),
          units: Math.max(0, parseInt(e.units || '0', 10) || 0),
          usd:   Math.max(0, parseFloat(e.usd || '0') || 0),
        })),
      options:    options
        .filter((o) => o.supplier.trim())
        .map((o) => ({
          rank:           o.rank,
          tier:           o.tier,
          supplier:       o.supplier.trim(),
          cost_delta_pct: parseFloat(o.cost_delta_pct || '0') || 0,
          delay_days:     Math.max(0, parseInt(o.delay_days || '0', 10) || 0),
          capacity:       o.capacity,
          notes:          o.notes.trim(),
        })),
    };
    try {
      const r = await fetch(`${API_BASE_URL}/simulator/scenarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!r.ok) {
        const body = await r.text().catch(() => '');
        throw new Error(`${r.status} ${body.slice(0, 160)}`);
      }
      const created = (await r.json()) as Scenario;
      onCreated(created);
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Request failed');
      setBusy(false);
    }
  };

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 200,
        background: 'rgba(2,6,23,.6)',
        display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
        padding: 40, overflowY: 'auto',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 760, maxWidth: '96vw',
          background: '#0b1220', color: '#e2e8f0',
          borderRadius: 18, border: '1px solid rgba(148,163,184,.18)',
          boxShadow: '0 20px 60px rgba(2,6,23,.5)',
          padding: 24,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 14, gap: 10 }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.18em', textTransform: 'uppercase', color: '#a78bfa' }}>
              Inject New Crisis
            </div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>Design the scenario</h3>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
              Persisted to Cosmos DB. Re-runnable by anyone on this environment. Seeded demos are protected.
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: 22, cursor: 'pointer', padding: 0, lineHeight: 1 }}>×</button>
        </div>

        {/* Core fields */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 14 }}>
          <DarkField label="Label">
            <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="e.g. FX swing +10% CAD/USD" style={darkInput} />
          </DarkField>
          <DarkField label="Severity">
            <select value={severity} onChange={(e) => setSeverity(e.target.value as 'MEDIUM' | 'HIGH' | 'CRITICAL')} style={darkInput}>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </DarkField>
          <DarkField label="Tagline (one-liner shown on card)">
            <input value={tagline} onChange={(e) => setTagline(e.target.value)} placeholder="Short problem statement" style={darkInput} />
          </DarkField>
          <DarkField label="Region">
            <input value={region} onChange={(e) => setRegion(e.target.value)} style={darkInput} />
          </DarkField>
          <DarkField label="Material / Asset">
            <input value={material} onChange={(e) => setMaterial(e.target.value)} placeholder="e.g. Aluminum extrusions" style={darkInput} />
          </DarkField>
          <DarkField label="Delay (days)">
            <input value={delayDays} onChange={(e) => setDelayDays(e.target.value)} inputMode="numeric" style={darkInput} />
          </DarkField>
          <DarkField label="Escalate to">
            <input value={director} onChange={(e) => setDirector(e.target.value)} placeholder="e.g. Marcus Webb · SVP Supply Chain" style={darkInput} />
          </DarkField>
          <DarkField label="Agent (routes to Foundry Agent Service)">
            <select value={agentId} onChange={(e) => setAgentId(e.target.value as 'logisticsbot' | 'customerops' | 'qcbot')} style={darkInput}>
              <option value="logisticsbot">Logistics Agent</option>
              <option value="customerops">CustomerOps Agent</option>
              <option value="qcbot">QC Agent</option>
            </select>
          </DarkField>
        </div>

        {/* Exposures */}
        <DarkSection
          title="Exposure by plant"
          subtitle="Rows with an empty plant name are ignored."
          onAdd={() => setExposures((list) => [...list, { plant: '', units: '0', usd: '0' }])}
        >
          {exposures.map((e, i) => (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr 28px', gap: 8, marginBottom: 6 }}>
              <input placeholder="Plant" value={e.plant} onChange={(ev) => setExposures((l) => l.map((x, j) => j === i ? { ...x, plant: ev.target.value } : x))} style={darkInput} />
              <input placeholder="Units" value={e.units} onChange={(ev) => setExposures((l) => l.map((x, j) => j === i ? { ...x, units: ev.target.value } : x))} style={darkInput} />
              <input placeholder="USD at risk" value={e.usd} onChange={(ev) => setExposures((l) => l.map((x, j) => j === i ? { ...x, usd: ev.target.value } : x))} style={darkInput} />
              <button onClick={() => setExposures((l) => l.filter((_, j) => j !== i))} style={darkTrash} title="Remove row">×</button>
            </div>
          ))}
        </DarkSection>

        {/* Options */}
        <DarkSection
          title="Mitigation options (A / B / C)"
          subtitle="Rows with an empty supplier are ignored."
          onAdd={null}
        >
          {options.map((o, i) => (
            <div key={i} style={{ padding: 10, borderRadius: 10, background: 'rgba(30,41,59,.55)', border: '1px solid rgba(148,163,184,.12)', marginBottom: 8 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '90px 130px 1fr 120px', gap: 8, marginBottom: 6 }}>
                <DarkMiniField label="Rank">
                  <select value={o.rank} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, rank: ev.target.value as 'A' | 'B' | 'C' } : x))} style={darkInput}>
                    <option>A</option><option>B</option><option>C</option>
                  </select>
                </DarkMiniField>
                <DarkMiniField label="Tier">
                  <select value={o.tier} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, tier: ev.target.value as ModalOption['tier'] } : x))} style={darkInput}>
                    <option value="PREFERRED">PREFERRED</option>
                    <option value="FALLBACK">FALLBACK</option>
                    <option value="LAST_RESORT">LAST_RESORT</option>
                  </select>
                </DarkMiniField>
                <DarkMiniField label="Supplier / Action">
                  <input value={o.supplier} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, supplier: ev.target.value } : x))} style={darkInput} />
                </DarkMiniField>
                <DarkMiniField label="Capacity">
                  <select value={o.capacity} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, capacity: ev.target.value as ModalOption['capacity'] } : x))} style={darkInput}>
                    <option value="SUFFICIENT">SUFFICIENT</option>
                    <option value="PARTIAL">PARTIAL</option>
                    <option value="LIMITED">LIMITED</option>
                  </select>
                </DarkMiniField>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '110px 110px 1fr', gap: 8 }}>
                <DarkMiniField label="Cost Δ %">
                  <input value={o.cost_delta_pct} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, cost_delta_pct: ev.target.value } : x))} style={darkInput} />
                </DarkMiniField>
                <DarkMiniField label="Delay days">
                  <input value={o.delay_days} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, delay_days: ev.target.value } : x))} style={darkInput} />
                </DarkMiniField>
                <DarkMiniField label="Notes">
                  <input value={o.notes} onChange={(ev) => setOptions((l) => l.map((x, j) => j === i ? { ...x, notes: ev.target.value } : x))} style={darkInput} />
                </DarkMiniField>
              </div>
            </div>
          ))}
        </DarkSection>

        {err && (
          <div style={{ marginTop: 10, padding: 10, borderRadius: 8, background: 'rgba(239,68,68,.12)', border: '1px solid rgba(239,68,68,.4)', color: '#fca5a5', fontSize: 12 }}>
            {err}
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 16 }}>
          <button onClick={onClose} disabled={busy}
            style={{ padding: '8px 14px', fontSize: 13, fontWeight: 600, borderRadius: 10,
              background: 'rgba(148,163,184,.12)', color: '#e2e8f0',
              border: '1px solid rgba(148,163,184,.22)', cursor: 'pointer' }}
          >Cancel</button>
          <button onClick={submit} disabled={busy}
            style={{ padding: '8px 18px', fontSize: 13, fontWeight: 700, borderRadius: 10,
              background: busy ? 'rgba(124,58,237,.4)' : 'linear-gradient(135deg, #7c3aed 0%, #3b82f6 100%)',
              color: '#fff', border: 'none', cursor: busy ? 'not-allowed' : 'pointer',
              boxShadow: busy ? 'none' : '0 10px 24px rgba(124,58,237,.35)' }}
          >{busy ? 'Saving…' : 'Create & use'}</button>
        </div>
      </div>
    </div>
  );
}

const darkInput: React.CSSProperties = {
  width: '100%',
  background: 'rgba(15,23,42,.55)',
  color: '#f1f5f9',
  border: '1px solid rgba(148,163,184,.2)',
  borderRadius: 8,
  padding: '8px 10px',
  fontSize: 13,
  fontFamily: 'inherit',
  outline: 'none',
};

const darkTrash: React.CSSProperties = {
  background: 'rgba(148,163,184,.12)',
  color: '#fca5a5',
  border: '1px solid rgba(148,163,184,.22)',
  borderRadius: 8,
  cursor: 'pointer',
  fontSize: 14,
};

function DarkField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label style={{ display: 'block' }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 4 }}>{label}</div>
      {children}
    </label>
  );
}

function DarkMiniField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label style={{ display: 'block' }}>
      <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 3 }}>{label}</div>
      {children}
    </label>
  );
}

function DarkSection({ title, subtitle, onAdd, children }: {
  title: string; subtitle?: string;
  onAdd: (() => void) | null;
  children: React.ReactNode;
}) {
  return (
    <div style={{ marginTop: 14, padding: 12, borderRadius: 12, background: 'rgba(30,41,59,.35)', border: '1px solid rgba(148,163,184,.12)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <div>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#cbd5e1' }}>{title}</div>
          {subtitle && <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{subtitle}</div>}
        </div>
        {onAdd && (
          <button onClick={onAdd} style={{ fontSize: 11, fontWeight: 700, color: '#60a5fa', background: 'rgba(96,165,250,.12)', border: '1px solid rgba(96,165,250,.3)', borderRadius: 6, padding: '4px 10px', cursor: 'pointer' }}>
            + Add row
          </button>
        )}
      </div>
      {children}
    </div>
  );
}
