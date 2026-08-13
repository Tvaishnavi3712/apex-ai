/**
 * Demo-mode utility — per-industry view filter.
 *
 * Type: `DemoMode = 'all' | <industry_key>` where industry_key is one of the
 * 13 platform industries. Selecting a specific industry collapses every page
 * (Canvas, Actions, Agents, Agent Hub, Apex Lens, Apex Signal, Pipelines,
 * Review, Command Center) to that industry's content only. The full
 * multi-industry data is still in memory — we just don't render the rest.
 *
 * Resolution order (first hit wins):
 *   1. localStorage `apex.demoMode`        — set by the Settings page picker.
 *   2. NEXT_PUBLIC_APEX_DEMO env var       — set at build time / via .env.local.
 *   3. 'all'                                — every industry visible (default).
 *
 * The legacy literal 'stp' is still accepted as an alias for
 * 'nuclear_operations' so existing URL params + bookmarks keep working.
 */

import { useEffect, useState } from 'react';

/** All industry keys recognised by the platform. Keep in sync with backend
 *  services/action_registry.py::INDUSTRY_ACTIONS keys. */
export const INDUSTRY_KEYS = [
  'all',
  'financial_services',
  'healthcare_payers',
  'healthcare_providers',
  'healthcare_clinical',
  'insurance_underwriting',
  'aerospace_defense',
  'supply_manufacturing',
  'manufacturing',
  'supply_chain',
  'hr',
  'retail',
  'cpg',
  'contact_center',
  'airlines',
  'nuclear_operations',
  // Vendor-neutral umbrella for the 66 Degrees / Agentic Enterprise demo
  // (3 use cases: supply chain orchestrator, cruise concierge, CRE lease
  // extraction). Activating this mode also flips the UI into vendor-neutral
  // skin — see AppShell + AppTopbar for the brand swap. Each use case ALSO
  // exists as its own industry domain below so a user can drill into one
  // use case at a time and see only its dashboard / command center / apex
  // signal / playbooks / blueprints / actions.
  'agentic_enterprise',
  'supply_chain_orchestrator', // UC-1 — Supply Chain Orchestrator
  'hospitality',               // UC-2 — Cruise Concierge / Hospitality
  'commercial_real_estate',    // UC-3 — Lease Extraction / CRE
  // Telecommunications — first-class industry. Covers carrier far-edge
  // certification, RAN ops, network deployment, and field operations.
  // Customer demos under this industry: verizon_far_edge (Verizon HQ
  // Planning POC). Future: att_, tmobile_, vodafone_ etc.
  'telecommunications',
  // Verizon Far Edge — customer-specific demo mode under telecommunications.
  // 4 agents: CertificationAgent, SchemaWatchAgent, UpgradeAdvisorAgent,
  // MentorAgent. Anchor: James Patchett · Distinguished Engineer · HQ Planning.
  'verizon_far_edge',
  // Oil & Gas Midstream — first-class industry for pipeline/NGL/crude
  // operators. Covers AP/Procurement document workflows AND midstream-specific
  // patterns (FERC tariff validation, JIB reconciliation, AFE tracking).
  // Customer demos under this industry: eprod (Enterprise Products Partners).
  'oil_gas_midstream',
  // EPROD — Enterprise Products Partners. Demo anchor for the POC:
  // 4 proposal use cases (Invoice Intelligence, PO-to-Contract, Non-PO MSA,
  // Engineering Quote) + 2 wow use cases (FERC Tariff Sheet, JIB Reconciliation).
  'eprod',
  // Credit Union — first-class industry for NCUA-chartered federal credit
  // unions. Covers BSA/AML, CIP/CDD, loan origination, third-party (vendor)
  // risk, and policy/HR compliance. Customer demos under this industry:
  // cwfcu (CommunityWide FCU).
  'credit_union',
  // CWFCU — CommunityWide Federal Credit Union demo anchor. 5 connected
  // agents: MemberOnboardingAgent, ComplianceAgent, LoanDocumentAgent,
  // VendorContractAgent, PolicyHRAgent. Story: "One member. One exam.
  // Five agents working together." NCUA exam readiness 87% → 97%.
  'cwfcu',
  // Manufacturing · Multi-Division — first-class industry for multi-entity
  // manufacturing holding companies running benefits allocation across
  // multiple legal entities / divisions. Covers carrier-file extraction,
  // division reclassification, exception detection, two-stage approval,
  // and journal-entry distribution. Runs entirely on AWS (S3 + Lambda +
  // Step Functions + Bedrock + DynamoDB + SES + SNS + QuickSight). Customer
  // demos under this industry: boler (The Boler Company).
  'manufacturing_multi_division',
  // Boler — The Boler Company demo anchor. 5 agents: BenefitsAllocationAgent
  // (BEN), ExceptionResolutionAgent (EXC), JournalEntryAgent (JE),
  // SignalAgent (SIG), AuditLensAgent (AUD). Story: "Benefits Allocation
  // Intelligence — from 3.5 days manual Excel cleanup to 4.2 hrs end-to-end
  // automated, all inside your AWS account."
  'boler',
] as const;

export type DemoMode = typeof INDUSTRY_KEYS[number] | 'stp';

/** Friendly label per industry — what the dropdown shows. */
export const INDUSTRY_LABELS: Record<DemoMode, string> = {
  all:                    'All Industries',
  financial_services:     'Financial Services',
  healthcare_payers:      'Healthcare Payers',
  healthcare_providers:   'Healthcare Providers',
  healthcare_clinical:    'Healthcare Clinical',
  insurance_underwriting: 'Insurance Underwriting',
  aerospace_defense:      'Aerospace & Defense',
  supply_manufacturing:   'Supply Chain & Manufacturing',
  manufacturing:          'Supply Chain & Manufacturing',
  supply_chain:           'Supply Chain & Manufacturing',
  hr:                     'HR / Recruitment',
  retail:                 'Retail',
  cpg:                    'CPG',
  contact_center:         'Contact Center',
  airlines:               'Airlines',
  nuclear_operations:     'Nuclear Operations & Reliability (STP)',
  stp:                    'Nuclear Operations & Reliability (STP)',
  agentic_enterprise:        'Agentic Enterprise Demo',
  supply_chain_orchestrator: 'Supply Chain Orchestrator',
  hospitality:               'Hospitality & Travel',
  commercial_real_estate:    'Commercial Real Estate',
  telecommunications:        'Telecommunications',
  verizon_far_edge:          'Verizon Far Edge Operations',
  oil_gas_midstream:         'Oil & Gas — Midstream',
  eprod:                     'Enterprise Products Partners (EPROD)',
  credit_union:              'Credit Union',
  cwfcu:                     'CommunityWide FCU',
  manufacturing_multi_division: 'Manufacturing · Multi-Division',
  boler:                     'The Boler Company',
};

/** Industries surfaced in the Settings dropdown (intentionally narrow scope —
 *  only the demos we've actually built end-to-end). The platform supports
 *  all 13 industries internally; this list is what the user picks from. */
export const INDUSTRY_DROPDOWN_ORDER: DemoMode[] = [
  'all',
  'supply_manufacturing',       // CBB demo (Cornerstone Building Brands)
  'nuclear_operations',         // STP demo (South Texas Project Phase 2)
  // 3 vendor-neutral use cases as their own industry domains. The
  // `agentic_enterprise` umbrella key still exists in INDUSTRY_KEYS for
  // legacy URL/env support, but is intentionally NOT shown in the dropdown
  // — users select one specific use case at a time.
  'supply_chain_orchestrator',  // UC-1
  'hospitality',                // UC-2
  'commercial_real_estate',     // UC-3
  'telecommunications',         // Industry — telco / carrier ops
  'verizon_far_edge',           // Customer demo under telecommunications · James Patchett
  'oil_gas_midstream',          // Industry — pipeline / NGL / crude midstream operators
  'eprod',                      // Customer demo under oil_gas_midstream · Enterprise Products Partners
  'credit_union',               // Industry — NCUA-chartered credit unions
  'cwfcu',                      // Customer demo under credit_union · CommunityWide FCU
  'manufacturing_multi_division', // Industry — multi-entity manufacturing benefits ops
  'boler',                      // Customer demo under manufacturing_multi_division · The Boler Company
];

/** Optional dropdown sub-labels — extra context shown next to the industry name. */
export const INDUSTRY_DROPDOWN_HINTS: Partial<Record<DemoMode, string>> = {
  all:                       'Show every demo + every industry',
  supply_manufacturing:      'CBB · Cornerstone Building Brands',
  nuclear_operations:        'STP Phase 2 · South Texas Project',
  agentic_enterprise:        '66 Degrees umbrella · vendor-neutral · all 3 use cases',
  supply_chain_orchestrator: 'UC-1 · multi-agent inventory + PO orchestrator',
  hospitality:               'UC-2 · cruise concierge + RAG + handoff',
  commercial_real_estate:    'UC-3 · lease extraction → DuckDB queries',
  telecommunications:        'Carrier far-edge cert · RAN ops · network deployment',
  verizon_far_edge:          'Verizon POC · ROBOT + Redfish + Ansible · 4 agents',
  oil_gas_midstream:         'Pipeline / NGL / crude · FERC tariff · JIB · AFE',
  eprod:                     'EPROD POC · 4 AP use cases + Tariff + JIB · 6 agents',
  credit_union:              'NCUA · BSA/AML · CIP · CDD · Loan ops · Vendor risk',
  cwfcu:                     'CommunityWide FCU · 5 connected agents · NCUA exam ready',
  manufacturing_multi_division: 'Multi-entity benefits · 5 agents · 3.5 days → 4.2 hrs',
  boler:                     'The Boler Company · 5 divisions · 847 employees · runs in your AWS',
};

/** localStorage key — keep in sync with the Settings page UI control. */
export const DEMO_MODE_STORAGE_KEY = 'apex.demoMode';

/** Industries that should match each `DemoMode` value when filtering data.
 *  Handles cross-industry merges (manufacturing + supply_chain →
 *  supply_manufacturing) and the `stp` alias for nuclear_operations. */
const MATCH_TABLE: Record<DemoMode, ReadonlySet<string>> = {
  all:                    new Set([]),  // 'all' shortcuts in isIndustryVisible
  financial_services:     new Set(['financial_services', 'core']),
  healthcare_payers:      new Set(['healthcare_payers', 'core']),
  healthcare_providers:   new Set(['healthcare_providers', 'core']),
  healthcare_clinical:    new Set(['healthcare_clinical', 'core']),
  insurance_underwriting: new Set(['insurance_underwriting', 'core']),
  aerospace_defense:      new Set(['aerospace_defense', 'core']),
  // Supply chain + manufacturing collapse to a single demo-domain
  supply_manufacturing:   new Set(['supply_manufacturing', 'manufacturing', 'supply_chain', 'supply', 'core']),
  manufacturing:          new Set(['supply_manufacturing', 'manufacturing', 'supply_chain', 'supply', 'core']),
  supply_chain:           new Set(['supply_manufacturing', 'manufacturing', 'supply_chain', 'supply', 'core']),
  hr:                     new Set(['hr', 'core']),
  retail:                 new Set(['retail', 'core']),
  cpg:                    new Set(['cpg', 'core']),
  contact_center:         new Set(['contact_center', 'core']),
  airlines:               new Set(['airlines', 'core']),
  nuclear_operations:     new Set(['nuclear_operations', 'nuclear', 'core']),
  stp:                    new Set(['nuclear_operations', 'nuclear', 'core']),
  // ─── Agentic Enterprise (66 Degrees vendor-neutral) ───
  // The umbrella `agentic_enterprise` matches its 3 sub-domains so the demo
  // mode shows ALL three use cases (orchestrator, hospitality, CRE) under
  // one toggle. Each sub-domain matches only itself, so picking a specific
  // use case in the dropdown collapses the whole platform (dashboard, command
  // center, apex signal, playbooks, blueprints, actions, agents, pipelines)
  // to that one use case's content.
  agentic_enterprise:        new Set([
                               'agentic_enterprise',
                               'supply_chain_orchestrator',
                               'hospitality',
                               'commercial_real_estate',
                               'cre',
                               'core',
                             ]),
  supply_chain_orchestrator: new Set(['supply_chain_orchestrator', 'core']),
  hospitality:               new Set(['hospitality', 'travel', 'core']),
  commercial_real_estate:    new Set([
                               'commercial_real_estate',
                               'cre',
                               'real_estate',
                               'core',
                             ]),
  // Telecommunications — first-class industry. Matches every telco-tagged
  // record (telecommunications, telco, far_edge) plus the verizon-flavored
  // customer demos. Picking 'Telecommunications' in the dropdown shows the
  // generic carrier view; picking 'Verizon Far Edge Operations' shows the
  // same content branded for the Verizon demo.
  telecommunications:        new Set([
                               'telecommunications',
                               'telco',
                               'far_edge',
                               'verizon_far_edge',
                               'verizon',
                               'core',
                             ]),
  // Verizon Far Edge — customer-specific demo mode. Inherits the full
  // telecommunications match set so a Verizon viewer sees the same
  // playbooks/blueprints/actions as the generic telco view.
  verizon_far_edge:          new Set([
                               'telecommunications',
                               'telco',
                               'far_edge',
                               'verizon_far_edge',
                               'verizon',
                               'core',
                             ]),
  // Oil & Gas Midstream — first-class industry. Matches every midstream-tagged
  // record (oil_gas_midstream, midstream, energy) plus the EPROD customer demo.
  // Picking 'Oil & Gas — Midstream' shows the generic midstream view; picking
  // 'Enterprise Products Partners' shows the same content branded for EPROD.
  oil_gas_midstream:         new Set([
                               'oil_gas_midstream',
                               'midstream',
                               'energy',
                               'oil_gas',
                               'eprod',
                               'core',
                             ]),
  eprod:                     new Set([
                               'oil_gas_midstream',
                               'midstream',
                               'energy',
                               'oil_gas',
                               'eprod',
                               'core',
                             ]),
  // Credit Union — first-class industry. Matches every CU-tagged record
  // (credit_union, ncua, cu) plus the cwfcu customer demo. Picking
  // 'Credit Union' shows the generic CU view; picking 'CommunityWide FCU'
  // shows the same content branded for CWFCU.
  credit_union:              new Set([
                               'credit_union',
                               'cu',
                               'ncua',
                               'cwfcu',
                               'core',
                             ]),
  cwfcu:                     new Set([
                               'credit_union',
                               'cu',
                               'ncua',
                               'cwfcu',
                               'core',
                             ]),
  // Manufacturing · Multi-Division — first-class industry. Matches every
  // multi-entity-manufacturing-tagged record + the boler customer demo.
  manufacturing_multi_division: new Set([
                               'manufacturing_multi_division',
                               'multi_division',
                               'benefits_allocation',
                               'boler',
                               'core',
                             ]),
  boler:                     new Set([
                               'manufacturing_multi_division',
                               'multi_division',
                               'benefits_allocation',
                               'boler',
                               'core',
                             ]),
};

const ENV_DEFAULT_RAW = (process.env.NEXT_PUBLIC_APEX_DEMO || 'all').toLowerCase();
const ENV_DEFAULT: DemoMode = (INDUSTRY_KEYS as readonly string[]).includes(ENV_DEFAULT_RAW)
  ? (ENV_DEFAULT_RAW as DemoMode)
  : ENV_DEFAULT_RAW === 'stp' ? 'nuclear_operations' : 'all';

/** Normalize legacy 'stp' alias to canonical 'nuclear_operations'. */
function normalize(mode: string): DemoMode {
  if (mode === 'stp') return 'nuclear_operations';
  if ((INDUSTRY_KEYS as readonly string[]).includes(mode)) return mode as DemoMode;
  return 'all';
}

/** SSR-safe load. Returns the env-var default when no override is set. */
export function getDemoMode(): DemoMode {
  if (typeof window === 'undefined') return ENV_DEFAULT;
  try {
    const stored = window.localStorage.getItem(DEMO_MODE_STORAGE_KEY);
    if (stored) return normalize(stored);
  } catch {
    // localStorage can throw in private-browsing / sandboxed iframes
  }
  return ENV_DEFAULT;
}

/** Persist a new demo mode and notify any listeners on this tab. */
export function setDemoMode(mode: DemoMode): void {
  if (typeof window === 'undefined') return;
  const canonical = normalize(mode);
  try {
    window.localStorage.setItem(DEMO_MODE_STORAGE_KEY, canonical);
  } catch {
    // see getDemoMode
  }
  // Custom event so React components listening via useDemoMode() re-render
  // immediately, without waiting for a full route change.
  window.dispatchEvent(new CustomEvent('apex-demo-mode-change', { detail: canonical }));
}

/**
 * Returns true if the given industry key should be visible in the current
 * demo mode. Use this everywhere you need to filter dropdowns, grids, lists.
 *
 * Examples:
 *   isIndustryVisible('financial_services')    // depends on current mode
 *   isIndustryVisible('nuclear_operations', 'stp')  // true (alias resolved)
 *   isIndustryVisible(undefined)              // false (no industry tag)
 */
export function isIndustryVisible(
  industryKey: string | undefined | null,
  mode?: DemoMode,
): boolean {
  const m = mode ?? getDemoMode();
  if (m === 'all') return true;
  if (!industryKey) return false;
  const key = industryKey.toLowerCase();
  return MATCH_TABLE[m]?.has(key) ?? false;
}

/** Friendly label lookup — falls back to a Title-Cased version of the key. */
export function labelForMode(mode: DemoMode): string {
  return INDUSTRY_LABELS[mode] || mode
    .split('_').map((s) => s[0].toUpperCase() + s.slice(1)).join(' ');
}

/* ───────────────────── vendor-neutral skin ─────────────────────
 *
 * The Agentic Enterprise demo mode is presented in interviews where APEX
 * and CBTS branding must be hidden. When this skin is active:
 *   - The "APEX" wordmark in the topbar becomes "Enterprise Agent Hub"
 *   - The CBTS footer text is suppressed
 *   - Page titles ("APEX | …") render as ("Enterprise Agent Hub | …")
 *   - Demo-mode pill / accent bar uses neutral slate instead of CBTS blue
 *
 * One helper, one rule. Keep all skin decisions behind this function so a
 * future "vendor-neutral for some other partner" mode is a one-line change.
 */
export function isVendorNeutralSkin(mode: DemoMode): boolean {
  return mode === 'agentic_enterprise';
}

/** Brand wordmark to use in the topbar / page title. */
export function brandName(mode: DemoMode): string {
  return isVendorNeutralSkin(mode) ? 'Enterprise Agent Hub' : 'APEX';
}

/** Tagline shown under the brand. */
export function brandTagline(mode: DemoMode): string {
  return isVendorNeutralSkin(mode)
    ? 'Agentic Systems  ·  Human-Agent Collaboration  ·  Unified Data Foundation'
    : 'Enterprise Document Intelligence & Workflow Automation';
}

/* ──────────────────────── React hook ──────────────────────── */

export function useDemoMode(): [DemoMode, (m: DemoMode) => void] {
  // CRITICAL: initialize with the SSR-safe default (env var, no localStorage)
  // so the first client render matches the server-rendered HTML. Reading
  // localStorage in the initial state would diverge from the server output
  // and trigger a React hydration mismatch error on every page that uses
  // this hook (Layout, Dashboard, Apex Lens, Pipelines, …).
  const [mode, setMode] = useState<DemoMode>(ENV_DEFAULT);

  // After mount: reconcile to the actual stored value (localStorage) and
  // honour any ?demoMode=<industry> URL param. Both run on the client only,
  // so they can't cause SSR drift.
  useEffect(() => {
    if (typeof window === 'undefined') return;
    // 1) URL-param bootstrap (e.g. start_stp_demo.sh opens
    //    http://localhost:3000/agent-hub?demoMode=stp)
    try {
      const sp = new URLSearchParams(window.location.search);
      const param = sp.get('demoMode');
      if (param) {
        const canonical = normalize(param);
        if (canonical !== getDemoMode()) {
          setDemoMode(canonical);
          setMode(canonical);
          return;  // setDemoMode already broadcast — no further sync needed
        }
      }
    } catch { /* ignore */ }
    // 2) Sync to whatever's persisted (might differ from ENV_DEFAULT)
    const stored = getDemoMode();
    if (stored !== mode) setMode(stored);
    // We intentionally only run this on mount — the listeners below keep us
    // in sync afterwards.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const onChange = () => setMode(getDemoMode());
    const onStorage = (e: StorageEvent) => {
      if (e.key === DEMO_MODE_STORAGE_KEY) setMode(getDemoMode());
    };
    window.addEventListener('apex-demo-mode-change', onChange);
    window.addEventListener('storage', onStorage);
    return () => {
      window.removeEventListener('apex-demo-mode-change', onChange);
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  return [mode, setDemoMode];
}
