/**
 * Settings — platform configuration.
 * Ported from apex-prototype 2/settings.html.
 *
 * Left nav rail of sections; right column shows forms per section.
 * All data is mocked inline.
 */

import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { Icon } from '@/components/AppShell/icons';
import {
  useDemoMode, type DemoMode,
  INDUSTRY_DROPDOWN_ORDER, INDUSTRY_LABELS, INDUSTRY_DROPDOWN_HINTS,
} from '@/lib/demoMode';
import { AgentModelsPanel } from '@/components/Settings/AgentModelsPanel';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

type Section = 'general' | 'models' | 'security' | 'notifications' | 'billing' | 'team';

const SECTIONS: { id: Section; label: string }[] = [
  { id: 'general',       label: 'General' },
  { id: 'models',        label: 'AI Models' },
  { id: 'security',      label: 'Security' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'billing',       label: 'Billing' },
  { id: 'team',          label: 'Team' },
];

export default function SettingsPage() {
  const [section, setSection] = useState<Section>('general');

  return (
    <>
      <Head><title>Settings | APEX</title></Head>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Settings</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>Configure the APEX AI Platform</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr', gap: 24 }}>
        {/* ─────────── left rail ─────────── */}
        <div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {SECTIONS.map((s) => {
              const active = section === s.id;
              return (
                <button
                  key={s.id}
                  onClick={() => setSection(s.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '10px 14px',
                    borderRadius: 12,
                    border: active ? '1px solid rgba(245,158,11,.2)' : '1px solid transparent',
                    background: active ? 'rgba(245,158,11,.1)' : 'transparent',
                    color: active ? '#d97706' : '#374151',
                    fontSize: 14,
                    fontWeight: 500,
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all .15s',
                  }}
                  onMouseOver={(e) => { if (!active) e.currentTarget.style.background = '#f8fafc'; }}
                  onMouseOut={(e) => { if (!active) e.currentTarget.style.background = 'transparent'; }}
                >
                  {s.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* ─────────── right content ─────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {section === 'general'       && <GeneralSection />}
          {section === 'models'        && <ModelsSection />}
          {section === 'security'      && <SecuritySection />}
          {section === 'notifications' && <NotificationsSection />}
          {section === 'billing'       && <BillingSection />}
          {section === 'team'          && <TeamSection />}
        </div>
      </div>
    </>
  );
}

/* ─────────── General ─────────── */

function GeneralSection() {
  const [humanReview, setHumanReview] = useState(true);
  const [auditLogging, setAuditLogging] = useState(true);
  // Demo-mode toggle — overrides NEXT_PUBLIC_APEX_DEMO env var per-browser via
  // localStorage. When set to 'stp', every industry-aware page (Canvas, Actions,
  // Agents, Pipelines) collapses its filter to the Nuclear Operations domain.
  const [demoMode, setDemoMode] = useDemoMode();

  return (
    <>
      <DemoModeCard mode={demoMode} onChange={setDemoMode} />
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 16 }}>Platform Settings</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label className="label">Platform Name</label>
            <input className="input" type="text" defaultValue="APEX AI Platform" />
          </div>
          <div>
            <label className="label">AWS Region</label>
            <select className="select" defaultValue="us-east-1">
              <option value="us-east-1">us-east-1 (N. Virginia)</option>
              <option value="us-west-2">us-west-2 (Oregon)</option>
              <option value="eu-west-1">eu-west-1 (Ireland)</option>
            </select>
          </div>
          <div>
            <label className="label">Default Industry</label>
            <select className="select" defaultValue="financial_services">
              <option value="financial_services">Financial Services</option>
              <option value="insurance_underwriting">Insurance</option>
              <option value="aerospace_defense">Aerospace &amp; Defense</option>
              <option value="supply_manufacturing">Supply Chain &amp; Manufacturing</option>
              <option value="nuclear_operations">Nuclear Operations &amp; Reliability</option>
            </select>
          </div>
          <ToggleRow
            title="Human Review Required"
            desc="Always route low-confidence extractions to human review"
            on={humanReview}
            onChange={setHumanReview}
          />
          <ToggleRow
            title="Audit Logging"
            desc="Log all agent decisions to Cosmos DB"
            on={auditLogging}
            onChange={setAuditLogging}
          />
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 20, gap: 10 }}>
          <button className="btn btn-secondary">Cancel</button>
          <button className="btn btn-primary">Save Settings</button>
        </div>
      </div>
      <AgentModelsPanel />
      <ModelsSection />
    </>
  );
}

/* ─────────── Demo Mode card ─────────── */
/**
 * Two-state picker that overrides the NEXT_PUBLIC_APEX_DEMO env var per browser.
 *
 * 'all'  — full multi-industry platform view (default)
 * 'stp'  — collapse every industry-aware filter to Nuclear Operations only.
 *           Use this when running the STP demo so the audience never sees
 *           non-relevant industries in dropdowns or grids.
 *
 * Selection is persisted in localStorage; demoMode.ts re-broadcasts the
 * change via a custom event so all subscribed components re-render
 * immediately (no hard reload needed).
 */
/**
 * Demo Mode card — single dropdown picks which industry the platform UI
 * collapses to. Default 'All Industries' shows everything; selecting any
 * specific industry filters Canvas, Actions, Agents, Agent Hub, ApexSignal,
 * Apex Lens, Pipelines, Review, and Command Center to that industry only.
 *
 * Backend data is unchanged — this is a per-browser display filter.
 */
function DemoModeCard({ mode, onChange }: { mode: DemoMode; onChange: (m: DemoMode) => void }) {
  const isFiltered = mode !== 'all';
  const accent = mode === 'nuclear_operations' || mode === 'stp' ? '#1e3a8a'
               : mode === 'supply_manufacturing' || mode === 'manufacturing' || mode === 'supply_chain' ? '#16a34a'
               : '#475569';

  return (
    <div
      className="card"
      style={{
        padding: 24,
        border: isFiltered ? `1px solid ${accent}` : '1px solid #f1f5f9',
        background: isFiltered ? `${accent}0d` : '#fff',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 10 }}>
            Demo Mode
            {isFiltered && (
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: '.08em',
                  padding: '2px 8px',
                  borderRadius: 4,
                  background: accent,
                  color: '#fff',
                  textTransform: 'uppercase',
                }}
              >
                {INDUSTRY_LABELS[mode] || mode} active
              </span>
            )}
          </h3>
          <p style={{ fontSize: 13, color: '#64748b', lineHeight: 1.5, marginBottom: 14 }}>
            Pick which industry domain the platform shows. Filters Canvas, Actions, Agents, Agent Hub,
            ApexSignal, Apex Lens, Pipelines, Human Review, and Command Center to that industry only.
            Backend data is unchanged; this is a per-browser display filter. Overrides the
            <code className="mono"> NEXT_PUBLIC_APEX_DEMO </code> env var.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxWidth: 480 }}>
            <label style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8' }}>
              Industry view
            </label>
            <select
              value={mode}
              onChange={(e) => onChange(e.target.value as DemoMode)}
              style={{
                padding: '10px 12px',
                fontSize: 13,
                fontWeight: 600,
                fontFamily: 'inherit',
                color: '#0f172a',
                background: '#fff',
                border: `1.5px solid ${isFiltered ? accent : '#e2e8f0'}`,
                borderRadius: 10,
                cursor: 'pointer',
                outline: 'none',
              }}
            >
              {INDUSTRY_DROPDOWN_ORDER.map((m) => {
                const hint = INDUSTRY_DROPDOWN_HINTS[m];
                return (
                  <option key={m} value={m}>
                    {INDUSTRY_LABELS[m] || m}{hint ? `  —  ${hint}` : ''}
                  </option>
                );
              })}
            </select>
            <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, lineHeight: 1.5 }}>
              {INDUSTRY_DROPDOWN_HINTS[mode] || 'Full platform view across every industry domain.'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ToggleRow({
  title, desc, on, onChange,
}: { title: string; desc: string; on: boolean; onChange: (v: boolean) => void }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 14, background: '#f8fafc', borderRadius: 12 }}>
      <div>
        <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>{title}</div>
        <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{desc}</div>
      </div>
      <div
        onClick={() => onChange(!on)}
        style={{
          width: 44,
          height: 24,
          background: on ? '#2563eb' : '#cbd5e1',
          borderRadius: 99,
          position: 'relative',
          cursor: 'pointer',
          transition: 'background .15s',
        }}
      >
        <div
          style={{
            width: 18,
            height: 18,
            background: '#fff',
            borderRadius: '50%',
            position: 'absolute',
            left: on ? 'auto' : 3,
            right: on ? 3 : 'auto',
            top: 3,
            boxShadow: '0 1px 3px rgba(0,0,0,.2)',
            transition: 'left .15s, right .15s',
          }}
        />
      </div>
    </div>
  );
}

/* ─────────── Models ─────────── */

interface RegistryModel {
  id: string;
  display_name: string;
  family: string;
  input_cost_per_1m_usd: number;
  output_cost_per_1m_usd: number;
  avg_latency_ms: number;
  suited_for: string[];
  description: string;
}

function ModelsSection() {
  // Pull the live model registry — this surfaces every Azure OpenAI model AND
  // OpenAI / Azure OpenAI catalog entries, so the picker reflects the
  // platform's actual choices instead of hardcoded Anthropic stubs.
  const [models, setModels] = useState<RegistryModel[]>([]);
  const [extractionModel, setExtractionModel] = useState('us.anthropic.claude-haiku-3-5-v1');
  const [reasoningModel,  setReasoningModel]  = useState('us.anthropic.claude-sonnet-4-5-v1');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/llm/models`);
        if (!r.ok || cancelled) return;
        const j = await r.json();
        if (!cancelled) setModels(j.models || []);
      } catch { /* ignore — keeps the hardcoded defaults visible */ }
    })();
    return () => { cancelled = true; };
  }, []);

  // Family display order — Anthropic first (default), then OpenAI, then Amazon, then others.
  const familyOrder: Record<string, number> = {
    anthropic: 0, openai: 1, amazon: 2, mistral: 3, deepseek: 4,
  };
  const sortedModels = [...models].sort((a, b) => {
    const fa = familyOrder[a.family] ?? 99;
    const fb = familyOrder[b.family] ?? 99;
    if (fa !== fb) return fa - fb;
    return a.input_cost_per_1m_usd - b.input_cost_per_1m_usd;
  });

  // Group by family for the optgroup labels in the dropdown.
  const familyLabel: Record<string, string> = {
    anthropic: 'Anthropic Claude',
    openai:    'OpenAI',
    amazon:    'Amazon Nova / Titan',
    mistral:   'Mistral',
    deepseek:  'DeepSeek',
  };
  const grouped = sortedModels.reduce<Record<string, RegistryModel[]>>((acc, m) => {
    (acc[m.family] = acc[m.family] || []).push(m);
    return acc;
  }, {});

  const renderOptions = () =>
    Object.entries(grouped).map(([fam, ms]) => (
      <optgroup key={fam} label={familyLabel[fam] || fam}>
        {ms.map((m) => (
          <option key={m.id} value={m.id}>
            {m.display_name}  ·  ${m.input_cost_per_1m_usd}/M in  ·  ${m.output_cost_per_1m_usd}/M out
          </option>
        ))}
      </optgroup>
    ));

  return (
    <div className="card" style={{ padding: 24 }}>
      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>AI Model Configuration</h3>
      <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>
        Choose default models for document extraction and reasoning. Spans Anthropic Claude, OpenAI GPT, Amazon Nova, Mistral, and DeepSeek — pick whichever fits your tenant.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <ModelPickerRow
          title="Extraction Model"
          subtitle="Drives Apex Lens extraction + low-cost classification."
          value={extractionModel}
          onChange={setExtractionModel}
          renderOptions={renderOptions}
          modelDisplay={sortedModels.find((m) => m.id === extractionModel)?.display_name}
        />
        <ModelPickerRow
          title="Reasoning Model"
          subtitle="Powers agent synthesis + multi-step reasoning."
          value={reasoningModel}
          onChange={setReasoningModel}
          renderOptions={renderOptions}
          modelDisplay={sortedModels.find((m) => m.id === reasoningModel)?.display_name}
        />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 14, background: '#f8fafc', borderRadius: 12 }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>Confidence Threshold</div>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 1 }}>Auto-approve above this score</div>
          </div>
          <input
            type="number"
            defaultValue="0.90"
            step="0.01"
            min="0"
            max="1"
            style={{
              width: 80,
              padding: '6px 10px',
              border: '1px solid #e2e8f0',
              borderRadius: 8,
              fontSize: 13,
              textAlign: 'center',
              fontFamily: 'inherit',
            }}
          />
        </div>
      </div>
    </div>
  );
}

function ModelRow({ title, subtitle, mono, button }: { title: string; subtitle: string; mono?: boolean; button: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: 14, background: '#f8fafc', borderRadius: 12 }}>
      <div>
        <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>{title}</div>
        <div className={mono ? 'mono' : ''} style={{ fontSize: 12, color: '#94a3b8', marginTop: 1 }}>{subtitle}</div>
      </div>
      <button className="btn btn-secondary btn-sm">{button}</button>
    </div>
  );
}

interface ModelPickerRowProps {
  title: string;
  subtitle: string;
  value: string;
  onChange: (next: string) => void;
  renderOptions: () => React.ReactNode;
  modelDisplay?: string;
}

function ModelPickerRow({ title, subtitle, value, onChange, renderOptions, modelDisplay }: ModelPickerRowProps) {
  return (
    <div style={{ padding: 14, background: '#f8fafc', borderRadius: 12, display: 'flex', flexDirection: 'column', gap: 10 }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16 }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{title}</div>
          <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 1 }}>{subtitle}</div>
        </div>
        {modelDisplay && (
          <div
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: '#1d4ed8',
              background: '#dbeafe',
              padding: '4px 10px',
              borderRadius: 999,
              whiteSpace: 'nowrap',
              flexShrink: 0,
            }}
            title={value}
          >
            {modelDisplay}
          </div>
        )}
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: '100%',
          padding: '8px 10px',
          border: '1px solid #e2e8f0',
          borderRadius: 8,
          fontSize: 13,
          fontFamily: 'inherit',
          background: '#ffffff',
          color: '#0f172a',
          cursor: 'pointer',
        }}
      >
        {renderOptions()}
      </select>
    </div>
  );
}

/* ─────────── Security ─────────── */

function SecuritySection() {
  const [mfa, setMfa] = useState(true);
  const [sso, setSso] = useState(false);

  return (
    <div className="card" style={{ padding: 24 }}>
      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Security & Authentication</h3>
      <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>Manage authentication, access controls, and audit trails</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <ToggleRow title="Multi-Factor Authentication" desc="Require MFA for all platform administrators" on={mfa} onChange={setMfa} />
        <ToggleRow title="SSO (SAML 2.0)" desc="Sign in with your corporate identity provider" on={sso} onChange={setSso} />
        <div>
          <label className="label">Session Timeout (minutes)</label>
          <input className="input" type="number" defaultValue={60} />
        </div>
        <div>
          <label className="label">Allowed IP Ranges (CIDR)</label>
          <textarea className="textarea" rows={3} defaultValue="10.0.0.0/8&#10;192.168.0.0/16" />
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 20, gap: 10 }}>
        <button className="btn btn-secondary">Cancel</button>
        <button className="btn btn-primary">Save</button>
      </div>
    </div>
  );
}

/* ─────────── Notifications ─────────── */

function NotificationsSection() {
  const [email, setEmail] = useState(true);
  const [slack, setSlack] = useState(false);
  const [webhook, setWebhook] = useState(false);

  return (
    <div className="card" style={{ padding: 24 }}>
      <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Notifications</h3>
      <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>Choose how you want to be notified about agent events</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <ToggleRow title="Email Notifications"  desc="Send a digest to admin@acme.com"     on={email}   onChange={setEmail} />
        <ToggleRow title="Slack Notifications"  desc="Post to #apex-alerts"                on={slack}   onChange={setSlack} />
        <ToggleRow title="Webhook Notifications" desc="POST events to a custom endpoint"   on={webhook} onChange={setWebhook} />
        <div>
          <label className="label">Webhook URL</label>
          <input className="input" type="url" placeholder="https://example.com/webhooks/apex" disabled={!webhook} />
        </div>
      </div>
    </div>
  );
}

/* ─────────── Billing ─────────── */

function BillingSection() {
  return (
    <>
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Current Plan</h3>
        <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>You&apos;re on the Enterprise plan</p>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 16, background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 12 }}>
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: '#1d4ed8' }}>Enterprise</div>
            <div style={{ fontSize: 12, color: '#3b82f6', marginTop: 2 }}>Unlimited agents · priority support</div>
          </div>
          <button className="btn btn-secondary btn-sm">Manage Plan</button>
        </div>
      </div>
      <div className="card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 16 }}>Usage This Month</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 12 }}>
          <UsageStat label="Documents Processed" value="12,482" />
          <UsageStat label="Agent Runtime (hrs)" value="186" />
          <UsageStat label="Azure AI Cost"        value="$1,240.55" />
        </div>
      </div>
    </>
  );
}

function UsageStat({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ padding: 14, background: '#f8fafc', borderRadius: 12 }}>
      <div style={{ fontSize: 11, color: '#64748b', textTransform: 'uppercase', letterSpacing: '.05em', fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{value}</div>
    </div>
  );
}

/* ─────────── Team ─────────── */

const TEAM: { name: string; email: string; role: string; status: 'active' | 'invited' }[] = [
  { name: 'CBTS Admin',    email: 'admin@cbts.com',       role: 'Owner',     status: 'active' },
  { name: 'Sarah Johnson', email: 'sarah@acme.com',       role: 'Admin',     status: 'active' },
  { name: 'Marc Lee',      email: 'marc@acme.com',        role: 'Developer', status: 'active' },
  { name: 'Priya Patel',   email: 'priya@acme.com',       role: 'Viewer',    status: 'invited' },
];

function TeamSection() {
  return (
    <div className="card" style={{ padding: 24 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>Team Members</h3>
          <p style={{ fontSize: 13, color: '#64748b', marginTop: 2 }}>Manage access and roles for your team</p>
        </div>
        <button className="btn btn-primary btn-sm">
          <Icon name="plus" style={{ width: 14, height: 14 }} /> Invite
        </button>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {TEAM.map((m) => (
          <div key={m.email} className="field-row" style={{ justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 11,
                  fontWeight: 700,
                  color: '#fff',
                }}
              >
                {m.name.split(' ').map((p) => p[0]).join('').slice(0, 2)}
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>{m.name}</div>
                <div style={{ fontSize: 12, color: '#94a3b8' }}>{m.email}</div>
              </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="chip-gray">{m.role}</span>
              <span className={m.status === 'active' ? 'chip-green' : 'chip-amber'}>
                {m.status === 'active' ? 'Active' : 'Invited'}
              </span>
              <button className="btn btn-secondary btn-sm">Manage</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
