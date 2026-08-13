/**
 * Agent Hub — 3-column agent chat surface.
 *
 * Two modes:
 *   1. Default: pick an agent from the left list, see its intro + scripted
 *      handoff chat in the center, document detail on the right.
 *   2. Document context mode: triggered by navigating from ApexLens with
 *      a `?doc=<type>` query param (invoice|claim|po|qc|contract|alert).
 *      Auto-selects the matching agent, shows a blue context banner over
 *      the chat, pre-loads 3 messages (file bubble → agent analysis →
 *      follow-up prompt), and swaps the quick-reply chips for
 *      doc-specific ones. Typed questions are answered via a small
 *      keyword matcher so the demo is fully interactive.
 *
 * Spec: ApexLens_Implementation_Spec.docx §4 + §7 (CBTS v1.0, Apr 2026).
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { Icon } from '@/components/AppShell/icons';
import { buildModelOverridesPayload } from '@/lib/llmConfig';
import { ProactiveAlertBanner } from '@/components/AgentHub/ProactiveAlertBanner';
import { useDemoMode, isIndustryVisible } from '@/lib/demoMode';
import { brandLabel, brandWordmark, PRODUCT_BRAND_STORAGE_KEY } from '@/lib/productBrand';

/** Render a browser <title> that respects the persisted product brand.
 *  Uses localStorage directly so we don't need to thread the hook through
 *  this very-large component. (SSR-safe: defaults to 'apex' on the server.) */
function __brandedHeadTitle(rawLabel: string): string {
  const brand = (typeof window !== 'undefined'
    ? window.localStorage.getItem(PRODUCT_BRAND_STORAGE_KEY)
    : null) === 'regulus' ? 'regulus' as const : 'apex' as const;
  return `${brandLabel(rawLabel, brand)} | ${brandWordmark(brand)}`;
}
import {
  readReviewFeed,
  subscribeToReviewFeed,
  type ReviewFeedEntry,
} from '@/lib/reviewFeed';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ──────────────────────── types + data ──────────────────────── */

type AgentStatus = 'active' | 'busy' | 'idle';
type DocKey =
  // CBB demo contexts
  | 'order_mod' | 'qc_batch' | 'port_strike'
  // Generic contexts
  | 'invoice' | 'claim' | 'po' | 'qc' | 'contract' | 'alert';

/** CBB demo # (1|2|3) → DocKey. */
const DEMO_TO_DOC: Record<string, DocKey> = {
  '1': 'order_mod',
  '2': 'qc_batch',
  '3': 'port_strike',
};

interface UIAgent {
  id: string;
  code: string;
  name: string;
  status: AgentStatus;
  detail: string;
  iconBg: string;
  iconColor: string;
}

interface Flag { color: 'red' | 'amber' | 'green'; text: string }

interface DocContext {
  /** Agent id in AGENTS[] that owns this doc type. */
  agentId: string;
  name: string;
  type: string;
  typeChip: string;
  fileSize: string;
  confidence: number;
  analysis: React.ReactNode;      // rich HTML for the agent's opening message
  flags: Flag[];
  routing: string;
  followUp: string;               // second agent message after the analysis
  quickReplies: string[];         // context-aware quick-reply chip labels
}

/** Per-agent industry tag — used by the demoMode filter to collapse the
 *  picker to nuclear_operations only when demoMode='stp'. */
type AgentIndustry = 'nuclear_operations' | 'supply_manufacturing'
                   | 'financial_services' | 'healthcare_payers' | 'manufacturing'
                   | 'aerospace_defense' | 'insurance_underwriting'
                   | 'agentic_enterprise'
                   | 'supply_chain_orchestrator'
                   | 'hospitality'
                   | 'commercial_real_estate'
                   | 'telecommunications'
                   | 'oil_gas_midstream'
                   | 'credit_union'
                   | 'manufacturing_multi_division';

interface UIAgentWithIndustry extends UIAgent {
  industry: AgentIndustry;
}

const AGENTS: UIAgentWithIndustry[] = [
  // ─── STP Phase 2 agents (router + 4 specialists) ───
  // ChatSTP listed first so it's the default selection in STP demo mode.
  { id: 'chatstp',           code: 'STP', name: 'ChatSTP',          status: 'active', detail: 'Router · Policy / Maintenance / Diagnostics / Reliability',
    iconBg: '#eef2ff', iconColor: '#1e3a8a', industry: 'nuclear_operations' },
  { id: 'policy-agent',      code: 'POL', name: 'PolicyAgent',       status: 'active', detail: 'UC-1 · Policy + procedure citation',
    iconBg: '#dbeafe', iconColor: '#1d4ed8', industry: 'nuclear_operations' },
  { id: 'maintenance-agent', code: 'MNT', name: 'MaintenanceAgent',  status: 'active', detail: 'UC-2 · PM history + engineer attribution',
    iconBg: '#dcfce7', iconColor: '#16a34a', industry: 'nuclear_operations' },
  { id: 'diagnostics-agent', code: 'DGN', name: 'DiagnosticsAgent',  status: 'active', detail: 'UC-3 · Failure-mode aggregation',
    iconBg: '#fef3c7', iconColor: '#d97706', industry: 'nuclear_operations' },
  { id: 'reliability-agent', code: 'RLY', name: 'ReliabilityAgent',  status: 'busy',   detail: 'UC-4 · Predictive maintenance + RUL',
    iconBg: '#fee2e2', iconColor: '#dc2626', industry: 'nuclear_operations' },

  // ─── CBB demo agents ───
  { id: 'customerops', code: 'COP', name: 'CustomerOps Agent', status: 'active', detail: 'Order mods · CRM · triage',      iconBg: '#dbeafe', iconColor: '#1d4ed8', industry: 'supply_manufacturing' },
  { id: 'qcbot',       code: 'QC',  name: 'QC Agent',          status: 'active', detail: 'QC ingest · tolerance · holds',  iconBg: '#dcfce7', iconColor: '#16a34a', industry: 'supply_manufacturing' },
  { id: 'logisticsbot',code: 'LOG', name: 'Logistics Agent',   status: 'busy',   detail: 'BOM · reroute · mitigation',     iconBg: '#fef3c7', iconColor: '#d97706', industry: 'supply_manufacturing' },
  // ─── Generic agents (other demos) ───
  { id: 'invoice',  code: 'INV', name: 'Invoice Agent',   status: 'active', detail: '142 docs today',  iconBg: '#dbeafe', iconColor: '#1d4ed8', industry: 'financial_services' },
  { id: 'claims',   code: 'CLM', name: 'Claims Agent',    status: 'active', detail: '67 docs today',   iconBg: '#f5f3ff', iconColor: '#7c3aed', industry: 'healthcare_payers' },
  { id: 'po',       code: 'PO',  name: 'PO Agent',        status: 'active', detail: '38 POs today',    iconBg: '#ede9fe', iconColor: '#7c3aed', industry: 'manufacturing' },
  { id: 'cnc',      code: 'CNC', name: 'CNC Agent',       status: 'idle',   detail: 'Idle',            iconBg: '#f0fdf4', iconColor: '#16a34a', industry: 'aerospace_defense' },
  { id: 'contract', code: 'CTR', name: 'Contract Agent',  status: 'active', detail: '11 contracts',    iconBg: '#fdf4ff', iconColor: '#7e22ce', industry: 'aerospace_defense' },
  { id: 'logistics',code: 'LG2', name: 'Logistics Agent (general)', status: 'busy', detail: 'Processing',  iconBg: '#fef2f2', iconColor: '#dc2626', industry: 'supply_manufacturing' },
  { id: 'rfp',      code: 'RFP', name: 'RFP Agent',       status: 'busy',   detail: 'Processing',      iconBg: '#fff7ed', iconColor: '#ea580c', industry: 'aerospace_defense' },

  // ─── Agentic Enterprise (66 Degrees vendor-neutral demos) ───
  // Each agent is tagged with its specific industry domain so the Agent Hub
  // picker collapses to ONLY this agent when that domain is selected. The
  // umbrella `agentic_enterprise` mode catches all three via the MATCH_TABLE
  // in lib/demoMode.ts.
  { id: 'orchestrator-agent', code: 'ORC', name: 'OrchestratorAgent', status: 'active', detail: 'UC-1 · Supply chain orchestrator',
    iconBg: '#eef2ff', iconColor: '#1e3a8a', industry: 'supply_chain_orchestrator' },
  { id: 'concierge-agent',    code: 'CON', name: 'ConciergeAgent',    status: 'active', detail: 'UC-2 · Cruise concierge + RAG + handoff',
    iconBg: '#dcfce7', iconColor: '#16a34a', industry: 'hospitality' },
  { id: 'lease-agent',        code: 'LSE', name: 'LeaseAgent',        status: 'active', detail: 'UC-3 · Lease extraction → DuckDB',
    iconBg: '#fef3c7', iconColor: '#d97706', industry: 'commercial_real_estate' },

  // ─── Verizon Far Edge (POC for James Patchett · HQ Planning) ───
  // 4 specialist agents — no separate router; the demoMode collapses the
  // picker and each agent has its own corpus + quick-reply set.
  { id: 'verizon-orchestrator-agent', code: 'ORC', name: 'OrchestratorAgent',
    status: 'active', detail: 'UC-0 · Drives the end-to-end cert run · multi-iteration + HITL',
    iconBg: '#f5f3ff', iconColor: '#6c47ff', industry: 'telecommunications' },
  { id: 'certification-agent',   code: 'CRT', name: 'CertificationAgent',
    status: 'active', detail: 'UC-1 · Firmware report → cert · ~15 min vs 40 hrs',
    iconBg: '#dbeafe', iconColor: '#1d4ed8', industry: 'telecommunications' },
  { id: 'playbook-agent',        code: 'PBK', name: 'PlaybookAgent',
    status: 'active', detail: 'UC-5 · Gap analysis → Ansible change-spec for new platforms',
    iconBg: '#ecfeff', iconColor: '#0891b2', industry: 'telecommunications' },
  { id: 'schemawatch-agent',     code: 'SCW', name: 'SchemaWatchAgent',
    status: 'active', detail: 'UC-2 · Redfish drift detection · 6 days proactive',
    iconBg: '#fef3c7', iconColor: '#d97706', industry: 'telecommunications' },
  { id: 'upgrade-advisor-agent', code: 'UPG', name: 'UpgradeAdvisorAgent',
    status: 'active', detail: 'UC-3 · Path validation + historical risk · HITL',
    iconBg: '#dcfce7', iconColor: '#16a34a', industry: 'telecommunications' },
  { id: 'mentor-agent',          code: 'MTR', name: 'MentorAgent',
    status: 'active', detail: 'UC-4 · KB Q&A · verbatim citations only',
    iconBg: '#f5f3ff', iconColor: '#7c3aed', industry: 'telecommunications' },

  // ─── EPROD (Enterprise Products Partners) — midstream POC ───
  // 6 agents covering AP / Procurement / Operations use cases.
  { id: 'eprod-invoice-agent',  code: 'INV', name: 'InvoiceAgent (EPROD)',
    status: 'active', detail: 'Midstream vendor invoice extraction + MSA validation',
    iconBg: '#dbeafe', iconColor: '#1d4ed8', industry: 'oil_gas_midstream' },
  { id: 'eprod-po-agent',       code: 'PO',  name: 'POAgent (EPROD)',
    status: 'active', detail: 'PO-to-Contract / MSA scope + rate validation',
    iconBg: '#ede9fe', iconColor: '#7c3aed', industry: 'oil_gas_midstream' },
  { id: 'eprod-vendor-agent',   code: 'VND', name: 'VendorAgent (EPROD)',
    status: 'active', detail: 'Non-PO MSA validation + vendor onboarding compliance',
    iconBg: '#dcfce7', iconColor: '#16a34a', industry: 'oil_gas_midstream' },
  { id: 'eprod-quote-agent',    code: 'QTE', name: 'QuoteAgent (EPROD)',
    status: 'active', detail: 'Engineering quote processing + reconciliation',
    iconBg: '#fef3c7', iconColor: '#d97706', industry: 'oil_gas_midstream' },
  { id: 'eprod-tariff-agent',   code: 'TRF', name: 'TariffAgent (EPROD)',
    status: 'active', detail: 'WOW · FERC tariff sheet validation + index cycles',
    iconBg: '#fee2e2', iconColor: '#dc2626', industry: 'oil_gas_midstream' },
  { id: 'eprod-jib-agent',      code: 'JIB', name: 'JIBAgent (EPROD)',
    status: 'active', detail: 'WOW · JIB statement reconciliation vs AFE',
    iconBg: '#fdf4ff', iconColor: '#7e22ce', industry: 'oil_gas_midstream' },

  // ─── CWFCU (CommunityWide Federal Credit Union) — 5 connected agents ───
  // Colors mirror docs/discovery/cwfcu/agent-hub.html badge gradients.
  // Story: "One member · One exam · Five agents working together."
  // Hand-off chain: Onboarding → Compliance → Loan → Vendor → Policy.
  { id: 'cwfcu-onboarding-agent', code: 'ONB', name: 'Member Onboarding Agent',
    status: 'active', detail: 'CIP · OFAC screening · PEP check · Account opening',
    iconBg: '#dcfce7', iconColor: '#10b981', industry: 'credit_union' },
  { id: 'cwfcu-compliance-agent', code: 'COM', name: 'Compliance Agent',
    status: 'active', detail: 'BSA/AML · SAR narratives · CTR · CDD · NCUA exam prep',
    iconBg: '#ede9fe', iconColor: '#6c47ff', industry: 'credit_union' },
  { id: 'cwfcu-loan-agent',       code: 'LDA', name: 'Loan Document Agent',
    status: 'active', detail: 'Auto / HELOC / Mortgage / Personal · packet validation',
    iconBg: '#dbeafe', iconColor: '#0ea5e9', industry: 'credit_union' },
  { id: 'cwfcu-vendor-agent',     code: 'VND', name: 'Vendor & Contract Agent',
    status: 'active', detail: 'Third-party risk · 47 contracts · SLA · renewal watch',
    iconBg: '#fef3c7', iconColor: '#f59e0b', industry: 'credit_union' },
  { id: 'cwfcu-policy-agent',     code: 'POL', name: 'Policy & HR Agent',
    status: 'active', detail: 'Policy acks · BSA training · 84 employees · board docs',
    iconBg: '#fee2e2', iconColor: '#ef4444', industry: 'credit_union' },

  // ─── BOLER (The Boler Company) — Manufacturing · Multi-Division demo ───
  // 5 agents covering benefits allocation across 5 divisions / 847 employees.
  // Colors mirror docs/discovery/boler/agent-hub.html badge gradients.
  // Story: "From 3.5 days manual Excel to 4.2 hrs automated — all in your AWS."
  { id: 'boler-benefits-agent',  code: 'BEN', name: 'Benefits Allocation Agent',
    status: 'active', detail: 'Carrier extract · reclassification · exception detect',
    iconBg: '#ede9fe', iconColor: '#6c47ff', industry: 'manufacturing_multi_division' },
  { id: 'boler-exception-agent', code: 'EXC', name: 'Exception Resolution Agent',
    status: 'active', detail: 'HITL exception review + Step Functions approval routing',
    iconBg: '#fee2e2', iconColor: '#ef4444', industry: 'manufacturing_multi_division' },
  { id: 'boler-je-agent',         code: 'JE', name: 'Journal Entry Agent',
    status: 'active', detail: 'Division JE generation + S3 distribution',
    iconBg: '#dcfce7', iconColor: '#00c4a0', industry: 'manufacturing_multi_division' },
  { id: 'boler-signal-agent',     code: 'SIG', name: 'Signal Agent',
    status: 'active', detail: 'Predictive benefits intelligence + rate forecasting',
    iconBg: '#fef3c7', iconColor: '#f59e0b', industry: 'manufacturing_multi_division' },
  { id: 'boler-audit-agent',      code: 'AUD', name: 'Audit Lens Agent',
    status: 'active', detail: 'Governance · lineage · DynamoDB audit trail',
    iconBg: '#dbeafe', iconColor: '#2563eb', industry: 'manufacturing_multi_division' },
];

const STATUS_COLOR: Record<AgentStatus, string> = { active: '#22c55e', busy: '#f59e0b', idle: '#94a3b8' };

const QUEUE = [
  { id: 'WI-3200', title: 'Globex Invoice',  detail: 'Needs Review · $87,400',       tone: 'amber' as const, highlight: true },
  { id: 'CL-8821', title: 'Claim Review',    detail: 'Needs Review · High priority', tone: 'amber' as const },
  { id: 'WI-3205', title: 'ACME Contract',   detail: 'Processing...',                tone: 'blue'  as const },
];

const DOC_CONTEXTS: Record<DocKey, DocContext> = {
  /* ═══════════════ CBB demo contexts (see CBB_Apex_Full_Execution_Plan.docx §3.6) ═══════════════ */
  order_mod: {
    agentId: 'customerops',
    name: 'Order Mod Request CBB-ORD-1044',
    type: 'ORDER MOD',
    typeChip: 'chip-blue',
    fileSize: '847 KB',
    confidence: 97,
    analysis: (
      <>
        I&apos;ve processed the <strong>Order Modification Request for CBB-ORD-1044</strong> from Midwest Window &amp; Door Supply.
        Dimensions extracted: Original 48×60 → Requested 48×62. Engineering constraint check: <strong>PASSED</strong> (3.3% variance, within 5% tolerance).
        CRM updated. New lead time: 16 days. Confirmation email sent to <span className="mono">orders@midwestwindow.com</span>.
      </>
    ),
    flags: [
      { color: 'green', text: 'Engineering constraint check PASSED (3.3% variance, within 5% tolerance)' },
      { color: 'green', text: 'Distributor verified — Midwest Window & Door Supply, Gold Partner' },
      { color: 'green', text: 'CRM updated — Microsoft Dynamics record CBB-ORD-1044 reflects new dimensions' },
      { color: 'green', text: 'Confirmation email sent to orders@midwestwindow.com' },
    ],
    routing: 'Decision: AUTO_APPROVED · New lead time: 16 days · No human review needed',
    followUp:
      'Ask me anything about this order — I can show the dimension comparison, explain what would have happened if tolerance was exceeded, pull the distributor history, or re-run the pricing.',
    quickReplies: [
      'Show me original vs new dimensions',
      'What if the dimensions were outside tolerance?',
      'Show distributor history',
      'Open in CRM',
    ],
  },
  qc_batch: {
    agentId: 'qcbot',
    name: 'QC Batch — 50 certs from Apex Vinyl Solutions',
    type: 'QC BATCH',
    typeChip: 'chip-green',
    fileSize: '12.4 MB',
    confidence: 99,
    analysis: (
      <>
        QC Batch processing complete. <strong>50 certificates</strong> from Apex Vinyl Solutions processed in 4.2 seconds.
        Result: <strong>48 PASSED · 2 FAILED</strong> tolerance checks.
        Failed lots: <strong>LOT-A44</strong> (tensile strength 3.8% below spec) and <strong>LOT-B12</strong> (color variance exceeds delta-E threshold).
        ERP holds placed: HOLD-7741 and HOLD-7742 in SAP S/4HANA. Plant Manager <strong>Sarah Jenkins</strong> at Ohio Plant 7 notified via Microsoft Teams at 06:15 AM.
      </>
    ),
    flags: [
      { color: 'red',   text: 'LOT-A44 held — tensile strength 3.8% below minimum spec (2,400 kg · $18,600)' },
      { color: 'red',   text: 'LOT-B12 held — color variance exceeds delta-E threshold (1,800 kg · $13,950)' },
      { color: 'green', text: '48 of 50 lots cleared for production' },
      { color: 'green', text: 'SAP S/4HANA holds placed (ERP-HOLD-7741, ERP-HOLD-7742)' },
      { color: 'green', text: 'Plant Manager Sarah Jenkins notified via Teams · Procurement notified via email' },
    ],
    routing: 'Decision: PARTIAL_HOLD · Quarantined value: $32,550 · Production impact: minimal',
    followUp:
      'I can break down the financial impact, show who was alerted, draft the supplier corrective-action request, or pull the full tolerance report.',
    quickReplies: [
      'What is the financial impact?',
      'Who was alerted?',
      'Draft corrective action request',
      'Show tolerance report',
    ],
  },
  port_strike: {
    agentId: 'logisticsbot',
    name: 'Port Strike Alert — Vinyl Resin (Chemours)',
    type: 'DISRUPTION',
    typeChip: 'chip-amber',
    fileSize: '42 KB',
    confidence: 98,
    analysis: (
      <>
        <strong>DISRUPTION ALERT:</strong> Port strike at Port of Savannah, GA affecting Chemours Vinyl Resins.
        Material: Vinyl Resin (PVC Grade A) · Delay: <strong>7 days</strong> · Severity: <strong>HIGH</strong>.
        BOM traversal complete: <strong>847 nodes</strong> analyzed across 93 plants.
        3 plants at risk: <strong>Ohio Plant 7</strong>, <strong>Texas Plant 14</strong>, <strong>Georgia Plant 31</strong>.
        Total value at risk: <strong>$1,090,000</strong>.
      </>
    ),
    flags: [
      { color: 'red',   text: '$1.09M revenue at risk across 3 plants' },
      { color: 'red',   text: 'Ohio Plant 7 (1,240 units · $412k) + Texas Plant 14 (980 · $386k) + Georgia Plant 31 (740 · $292k)' },
      { color: 'amber', text: 'Option A (PREFERRED) — Reroute from Oxy Vinyls LP · +5% cost · 0-day delay' },
      { color: 'amber', text: 'Option B (FALLBACK) — Resequence Georgia Plant 31 · $0 cost · 2-day delay' },
      { color: 'amber', text: 'Option C (LAST RESORT) — Air freight from Formosa · +22% cost · 0-day delay' },
    ],
    routing: 'Decision: PENDING_HUMAN_APPROVAL · Escalated to Marcus Webb, Supply Chain Director',
    followUp:
      'I can walk through the rerouting options, approve one and notify Marcus, or show the BOM impact tree. What would you like to do?',
    quickReplies: [
      'What are my rerouting options?',
      'Approve Option A and notify Marcus Webb',
      'Show BOM impact',
      'Compare cost deltas',
    ],
  },

  /* ═══════════════ Generic contexts (kept for other demos) ═══════════════ */
  invoice: {
    agentId: 'invoice',
    name: 'Globex Corp Invoice Q2',
    type: 'INVOICE',
    typeChip: 'chip-blue',
    fileSize: '142 KB',
    confidence: 94,
    analysis: (
      <>I've processed <strong>Globex Corp Invoice Q2</strong> (GLX-2024-0441). Here's what I found:</>
    ),
    flags: [
      { color: 'red',   text: 'PO-2024-0891 not found in ERP — possible typo' },
      { color: 'amber', text: 'Amount $87,400 exceeds $10k auto-approval threshold' },
      { color: 'green', text: 'Vendor verified on approved vendor list' },
      { color: 'green', text: 'No duplicate invoice found in last 90 days' },
    ],
    routing: 'Confidence: 94% · Routed to AP Manager Queue',
    followUp:
      'What would you like to know? I can explain any flag, look up the PO, check vendor history, or approve/reject this invoice.',
    quickReplies: [
      'Why was this flagged?',
      'Look up PO-2024-0891',
      'Approve invoice',
      'Reject invoice',
    ],
  },
  claim: {
    agentId: 'claims',
    name: 'Claim CL-8821 — Water Damage',
    type: 'CLAIM',
    typeChip: 'chip-amber',
    fileSize: '2.1 MB',
    confidence: 88,
    analysis: (
      <>I've processed <strong>Claim CL-8821</strong> for water damage at Meridian Properties.</>
    ),
    flags: [
      { color: 'red',   text: 'Claim value $142,000 requires senior adjuster review' },
      { color: 'amber', text: 'Policy deductible of $5,000 not yet applied' },
      { color: 'green', text: 'Policy active and in good standing' },
      { color: 'green', text: 'No prior claims in last 24 months' },
    ],
    routing: 'Confidence: 88% · Routed to Senior Adjuster Queue',
    followUp:
      'I can pull the policy details, check claim history, calculate the net payout after deductible, or assign an adjuster.',
    quickReplies: [
      'Calculate net payout',
      'Check policy history',
      'Assign to adjuster',
      'Request more docs',
    ],
  },
  po: {
    agentId: 'po',
    name: 'Acme PO #4421 — Rush Order',
    type: 'PURCHASE ORDER',
    typeChip: 'chip-purple',
    fileSize: '88 KB',
    confidence: 97,
    analysis: (
      <>I've processed <strong>Acme PO #4421</strong> — a rush order with 3 SKUs totaling $34,200.</>
    ),
    flags: [
      { color: 'green', text: 'All 3 SKUs found in inventory system' },
      { color: 'amber', text: 'Rush delivery surcharge of $1,200 applied' },
      { color: 'green', text: 'Vendor approved and within credit limit' },
    ],
    routing: 'Confidence: 97% · Auto-Approved',
    followUp:
      'Want me to confirm inventory counts, validate the product codes, or flag this for manual review?',
    quickReplies: [
      'Check inventory',
      'Validate product codes',
      'Approve PO',
      'Flag for review',
    ],
  },
  qc: {
    agentId: 'cnc',
    name: 'QC Report — Batch 2024-B',
    type: 'QC REPORT',
    typeChip: 'chip-green',
    fileSize: '340 KB',
    confidence: 92,
    analysis: (
      <>I've processed the <strong>QC Report for Batch 2024-B</strong> (Houston, Line 3). 99.2% pass rate with 19 flagged units.</>
    ),
    flags: [
      { color: 'amber', text: '19 units flagged — surface crack (12) + dimensional variance (7)' },
      { color: 'amber', text: 'Partial batch hold applied pending re-inspection' },
      { color: 'green', text: '2,381 units cleared for shipment' },
      { color: 'green', text: 'Defect rate 0.79% — within 1% threshold' },
    ],
    routing: 'Confidence: 92% · Plant Manager notified',
    followUp:
      'I can show the defect details per unit, hold the full batch, notify the plant manager, or release the cleared units.',
    quickReplies: [
      'Show defect details',
      'Hold batch',
      'Notify plant manager',
      'Release batch',
    ],
  },
  contract: {
    agentId: 'contract',
    name: 'Vendor Contract — Gulf Coast',
    type: 'CONTRACT',
    typeChip: 'chip-purple',
    fileSize: '1.2 MB',
    confidence: 89,
    analysis: (
      <>I've processed the <strong>Gulf Coast Logistics contract</strong> — a $4.2M, 24-month deal with an auto-renewal clause.</>
    ),
    flags: [
      { color: 'amber', text: 'Auto-renewal clause — 60-day notice window opens Jun 1, 2027' },
      { color: 'amber', text: 'Penalty clause 2%/week — above standard 1% threshold' },
      { color: 'green', text: 'Vendor insurance certificates verified' },
      { color: 'green', text: 'No conflicting exclusivity clauses found' },
    ],
    routing: 'Confidence: 89% · Routed to Legal Review Queue',
    followUp:
      'Want me to highlight the key clauses, check the renewal date, flag risks, or draft a negotiation response?',
    quickReplies: [
      'Highlight key clauses',
      'Check renewal date',
      'Flag risks',
      'Send for signature',
    ],
  },
  alert: {
    agentId: 'logistics',
    name: 'Supply Chain Alert — Vinyl Resin',
    type: 'ALERT',
    typeChip: 'chip-red',
    fileSize: '67 KB',
    confidence: 96,
    analysis: (
      <>Supply chain alert: <strong>7-day delay on vinyl resin</strong> from ChemCo puts $1.09M at risk across 3 plants.</>
    ),
    flags: [
      { color: 'red',   text: '$1.09M revenue at risk across 3 plants' },
      { color: 'red',   text: 'Houston Line 2 will halt in 48 hours without action' },
      { color: 'amber', text: 'Alt supplier PolySource available — 15% premium' },
      { color: 'green', text: 'Dallas and Memphis have 5-day buffer stock' },
    ],
    routing: 'Confidence: 96% · Supply Chain Director + 3 Plant Managers notified',
    followUp:
      'I can traverse the BOM to show finished-good impact, find alt suppliers, resequence production, or draft the plant-manager notification.',
    quickReplies: [
      'Traverse BOM impact',
      'Find alt suppliers',
      'Resequence production',
      'Notify plants',
    ],
  },
};

const DEFAULT_QUICK_REPLIES = ["Show today's queue", 'Upload invoice', 'Approval stats'];

/**
 * Per-agent quick-reply chips — shown when no document context is loaded.
 * Each list is 10 demo-tested questions that hit the agent's actual corpus.
 * Carefully ordered so the first 3-4 always work cold; later ones exercise
 * context inference (e.g., "this pump") that depends on prior turns.
 *
 * Verified live against the deployed STP AgentCore runtimes 2026-05-05.
 */
const AGENT_QUICK_REPLIES: Record<string, string[]> = {
  // ─── ChatSTP — router demo, spans all 4 specialist domains ───
  chatstp: [
    'What is the alert vibration limit for an RCP?',
    'When was the last PM on P-3A?',
    'Has it had any failures recently?',
    'Predict the next failure on this pump.',
    'Should I advance the next PM?',
    'Who needs to approve that recommendation?',
    'What is the meal allowance per STP-415?',
    'List the top 3 failure modes on RCS pumps.',
    'Pull up WO-2026-00871.',
    'Summarize what we discussed about P-3A.',
  ],

  // ─── PolicyAgent (UC-1) — verbatim policy citations ───
  'policy-agent': [
    'What is the meal allowance for business travel?',
    'What does STP-415 say about lodging reimbursement?',
    'Show me the radiation work permit briefing requirements.',
    'What are the fitness-for-duty rules for licensed operators?',
    'Cite the procedure for reactor coolant pump vibration monitoring.',
    'What is the lockout/tagout requirement for pump maintenance?',
    'How long must we retain maintenance records?',
    'Are there policies on overtime for mechanical staff?',
    'What is the corrective action program review cadence?',
    'List the top 5 STP policy documents you have indexed.',
  ],

  // ─── MaintenanceAgent (UC-2) — PM history with engineer attribution ───
  'maintenance-agent': [
    'When was the last PM on P-3A and who performed it?',
    'Show me the maintenance history for P-3A in the past year.',
    'Who was the lead engineer on the most recent P-3A work package?',
    'What were the findings from the last P-3A bearing inspection?',
    'Walk me through the LOTO sign-offs on the latest P-3A work order.',
    'How many hours did the last P-3A PM consume?',
    'Pull up WO-2026-00871. What were the acceptance criteria?',
    'Has P-3A had any deferred maintenance items recently?',
    "What's scheduled next for P-3A and when's it due?",
    'Compare P-3A maintenance frequency to P-3B and P-3C.',
  ],

  // ─── DiagnosticsAgent (UC-3) — failure-mode aggregation, cited WOs ───
  'diagnostics-agent': [
    'What is the most common failure mode on P-3A?',
    'Show the failure-mode breakdown across all RCS pumps.',
    'Have we seen the same bearing issue on other pumps?',
    'What is the typical lead time before an axial-vibration failure?',
    'List the open Condition Reports referencing P-3A.',
    'What corrective actions usually resolve a mechanical-seal cavity leak?',
    'Which work orders cite vibration-above-limit as a finding?',
    'Compare P-3A failure history to P-3B and P-3C.',
    'Is there a recurring pattern between bearing oil over-temp and seal leaks?',
    'Top 3 failure modes by frequency, with cited WOs.',
  ],

  // ─── ReliabilityAgent (UC-4) — predictive maintenance + RUL ───
  'reliability-agent': [
    'What is the failure risk for P-3A in the next 30 days?',
    'Compute the RUL forecast for P-3A with 80% and 95% confidence bands.',
    'Are any anomalies active on P-3A right now?',
    'Should we advance the next PM on P-3A? Why or why not?',
    'Estimate the dollar avoidance if we advance the bearing replacement.',
    'Compare the predicted failure date against the scheduled PM date.',
    'Walk me through the sensor channels driving the current risk tier.',
    "What's the routing for the PM-advance recommendation? Who approves?",
    'Has the anomaly score been rising or falling over the past 7 days?',
    "If we don't act, what's the worst-case outcome and on what date?",
  ],

  // ═══════════════ VERIZON FAR EDGE — POC for James Patchett ═══════════════
  // 10 questions per agent, scoped to the actual corpus we ship in
  // synthetic-data/verizon_far_edge/. Each set leads with a deterministic
  // question that always works, then exercises context inference.

  // ─── OrchestratorAgent (UC-0) — drives the end-to-end run ───
  'verizon-orchestrator-agent': [
    'Onboard the HPE EL140 Gen12 (iLO7) — it is a new server type.',
    'Run the full cert campaign through 5 iterations.',
    'Which steps are read-only correlation vs direct lab actions?',
    'How many HITL gates are in this run and why?',
    'Show the orchestration plan for the EL140 onboarding.',
    'What did the 5 iterations of PROPOSED-20→28 find?',
    'Summarize the end-to-end run for Bob.',
    'How long did this take vs the manual 40-hour baseline?',
    'Certify the Dell XR8720t (iDRAC 10) next.',
    'What got human-approved in this campaign?',
  ],

  // ─── CertificationAgent (UC-1) — firmware cert report in ~15 min ───
  // Leads with REAL corpus questions (James Patchett's 118 MTCE Lab reports).
  'certification-agent': [
    'Triage the DMTF conformance failures on HPE E930t iLO6 1.57.',
    'Why are the 7 Redfish conformance failures safe to certify?',
    'Show the PTU performance result for E930t (MEAKV-642-646).',
    'Run the functional sensor cert for ZT Proteus BMC 3.02.',
    'Validate the functional Redfish surface on ZT Proteus BMC .46.',
    'Certify the Dell PowerEdge R7615 sensor list (multi-vendor).',
    'Show the 7-day Galene soak test result.',
    'What is the wave deployment recommendation across the fleet?',
    'How many hours does APEX save across all 118 reports?',
    'Show the FlexRAN BIOS profile cert on E930t iLO6 1.60.',
  ],

  // ─── SchemaWatchAgent (UC-2) — regression + Redfish drift detection ───
  'schemawatch-agent': [
    'Show the Samsung PM9A3 thermal regression on BMC .45.',
    'Why do fans spike to 100% on BMC .45 with Samsung drives?',
    'Explain the Redfish 503 transient on ZT Proteus BMC .43.',
    'What firmware should we block from the next deployment wave?',
    'Watch for Redfish schema drift across the firmware revs.',
    'Which BMC version is the minimum safe for Samsung PM9A3 sites?',
    'How was the PM9A3 thermal regression reproduced in the lab?',
    'Show the RedfishDBReset remediation for the stuck DB.',
    'What is the blast radius of the BMC .45 thermal bug?',
    'Hand the block list to UpgradeAdvisor for wave planning.',
  ],

  // ─── UpgradeAdvisorAgent (UC-3) — path validation + historical risk ───
  'upgrade-advisor-agent': [
    'Validate the WRCP 21.05p6 → 21.12p10 path on ZT Proteus.',
    'Why block BMC .45 from the deployment wave?',
    'Score the risk of the Proteus subcloud upgrade path.',
    'Show the platform deployment readiness for HPE E930t (MEAKV-965).',
    'What alarms are expected during the 21.05p6 → 21.12p10 upgrade?',
    'Which firmware paths are wave-eligible right now?',
    'Why does the Samsung PM9A3 case require a HITL gate?',
    'Show the post-upgrade validation for the Proteus subcloud.',
    'Compare the risk of BMC .45 vs .46 deployment.',
    'Add the validated upgrade path to the compatibility matrix.',
  ],

  // ─── PlaybookAgent (UC-5) — gap analysis → Ansible change-spec ───
  'playbook-agent': [
    'Generate the BMC playbook change-spec for the HPE EL140 (iLO7).',
    'How many Ansible roles need changes for iLO7 support?',
    'Which roles need NO change and why?',
    'Show the WorkloadProfile=vRAN change for group_vars/HPE.',
    'Why does subscribe-redfish-events need RegistryPrefixes?',
    'What new role does the EL140 require that does not exist yet?',
    'Which deviations also affect iLO6 (e930t)?',
    'Show the ilo-hostname change for iLO7.',
    'What is the risk of each playbook change?',
    'Open a PR with the 7 approved changes.',
  ],

  // ─── MentorAgent (UC-4) — KB Q&A with verbatim citations ───
  'mentor-agent': [
    'Is there a known issue with Samsung PM9A3 on ZT BMC?',
    'How do I fix the Redfish 503 error during host boot?',
    'Are the DMTF conformance failures a real problem?',
    'How do I work around KB-2026-0118 (CU-UP RT latency)?',
    'What is the validated WRCP upgrade path for far edge?',
    'Cite the WWW-Authenticate conformance failure explanation.',
    'What BMC version fixes the Samsung thermal read issue?',
    'How do I roll back BMC firmware after a failed upgrade?',
    'Explain the RT kernel tuning fix for CU-UP latency.',
    'What is the standard practice for DMTF cert false positives?',
  ],

  // ═══════════════ EPROD — Enterprise Products Partners (midstream POC) ═══════════════
  // 10 questions per agent. Anchored to midstream AP / Procurement / Operations
  // terminology: AFE, JIB, MSA, FERC tariff, working interest, NGL fractionation,
  // Mont Belvieu / Sweeny corridor vendors (Halliburton, Kiewit, Fluor, Targa,
  // Phillips 66, Baker Hughes, Schlumberger).

  // ─── InvoiceAgent (EPROD) — midstream vendor invoice extraction + validation ───
  'eprod-invoice-agent': [
    'Show me all Halliburton invoices over $50K from April 2026 without a matching PO.',
    'Which invoices this month had rate variances vs MSA-HAL-2024-03?',
    'Extract line items from the latest Baker Hughes NDT invoice for the Mont Belvieu hot-tap.',
    'Validate invoice INV-SLB-26-0418 against the Schlumberger rate card.',
    'How many AP invoices are blocked on missing AFE references this week?',
    'Which Kiewit invoices billed above their MSA escalation cap?',
    'Flag invoices charging operating-class rates against a capital AFE.',
    'Compare the May 2026 Targa Mont Belvieu fractionation invoices to April 2026.',
    'List invoices coded to the Sweeny marine terminal cost center over $25K.',
    'Which Fluor invoices reference scope outside their executed MSA Schedule B?',
  ],

  // ─── POAgent (EPROD) — PO-to-Contract / MSA validation ───
  'eprod-po-agent': [
    'What POs are referencing MSA-KIEWIT-2024-07 but billing outside Schedule B scope?',
    'Show me POs where the unit rate is more than 5% above the contracted rate.',
    'Which open POs against Halliburton exceed the $250K approval threshold without VP sign-off?',
    'List POs tied to AFE-2026-014 (Sweeny compressor station expansion) and their commitment-to-date.',
    'Compare PO PO-26-0419-FLR against the Fluor engineering rate card for senior process engineers.',
    'Which POs lack a valid MSA reference and need procurement remediation?',
    'Show me POs issued in Q2 2026 for pipeline integrity inspection services.',
    'Flag POs with unit-of-measure mismatches between PO header and MSA rate sheet.',
    'How much remaining commitment is left on the Bechtel marine terminal PO?',
    'Which POs are charging capital scope to an operating AFE bucket?',
  ],

  // ─── VendorAgent (EPROD) — non-PO MSA validation + vendor onboarding ───
  'eprod-vendor-agent': [
    'Is there an active MSA for vendor PIPETECH SVCS LLC?',
    'Which non-PO transactions in May 2026 lacked MSA validation?',
    'Show me vendors onboarded in 2026 missing W-9 or insurance certificates.',
    'List vendors with expired indemnity clauses on their active MSA.',
    'Which vendors have processed over $1M in non-PO spend year-to-date?',
    'Validate that BAKER HUGHES MSA-BH-2025-11 covers downhole NDT services in the Tulsa region.',
    'Flag vendors invoicing into Mont Belvieu cost centers without a Texas-qualified COI on file.',
    'How many vendors have MSAs auto-renewing in the next 90 days?',
    'Which vendors charge above-market rates on non-PO maintenance work?',
    'Compare onboarding compliance for new vendors added in Q1 2026 vs Q2 2026.',
  ],

  // ─── QuoteAgent (EPROD) — engineering quote processing + reconciliation ───
  'eprod-quote-agent': [
    'Compare the Fluor Q2 quote against historical engineering rates for similar scope.',
    'Which engineering quotes are still open beyond their validity period?',
    'Reconcile QUOTE-BECHTEL-26-031 against the executed PO for the Sweeny compressor skid.',
    'Show me quotes received this month for pipeline integrity studies.',
    'Which Kiewit quotes have escalation clauses tied to PPI-FG above 4%?',
    'List engineering quotes over $500K awaiting capital review board approval.',
    'Compare quoted senior PE hourly rates across Fluor, Bechtel, and Worley for the past 12 months.',
    'How many quotes were rejected for scope-creep flags in May 2026?',
    'Which quotes reference AFE-2026-022 (Houston gathering expansion)?',
    'Validate the Worley quote against MSA rate-card unit prices for hot-tap engineering.',
  ],

  // ─── TariffAgent (EPROD) — FERC tariff sheet validation (WOW use case) ───
  'eprod-tariff-agent': [
    'What is the effective FERC NGL tariff for May 27, 2026?',
    'Which shipper invoices billed above the gas-day effective rate this month?',
    'When is the next FERC index cycle effective date?',
    'Show me Bbl/100 mi rates for T-1, T-2, and Walk-up shippers on the Mont Belvieu lateral.',
    'Validate the fuel adjustment rider on the April 2026 ethane tariff sheet.',
    'Which tariff sheets are pending PPI-FG index escalation this quarter?',
    'Compare the proposed July 2026 tariff vs the currently effective rate for propane service.',
    'How many shipper invoices applied the wrong tariff revision in May 2026?',
    'List all tariffs filed under FERC docket numbers in the past 6 months.',
    'Flag tariff sheets where the fuel-adjustment percentage exceeds the rider cap.',
  ],

  // ─── JIBAgent (EPROD) — JIB statement reconciliation vs AFE (WOW use case) ───
  'eprod-jib-agent': [
    "What is EPROD's partner share of the April 2026 Phillips 66 Sweeny JIB?",
    'Which capital charges on the Targa Mont Belvieu JIB exceeded their AFE-approved amount?',
    'Show me JIB charges that fall outside the JV agreement scope.',
    'Reconcile JIB-PSX-SWEENY-26-04 against AFE-2026-008 and flag overruns by line.',
    'What is the working-interest split on the Sweeny fractionation joint venture for May 2026?',
    'Which JIB line items lack supporting vendor invoice backup?',
    'How much have partners over-billed EPROD year-to-date on the Mont Belvieu JOA?',
    'Compare capital vs operating charges on the Targa JIB for Q1 2026 vs Q2 2026.',
    'List JIB charges where the partner share exceeds the JOA-defined approval threshold.',
    'Flag JIB entries citing AFEs that are already closed or fully spent.',
  ],

  /* ════════════════════════════════════════════════════════════════════════
   *  CWFCU — CommunityWide Federal Credit Union demo (5 agents × 10 questions)
   *
   *  Questions are anchored in the demo corpus:
   *    • Members: #44821 (structuring), #39104 (high-risk CDD), #29341 (CTR),
   *      Anderson (PEP), Torres (Onboarding), Williams (re-upload)
   *    • Loans: LN-2026-0438 (Patel mortgage), LN-2026-0441 (Johnson HELOC)
   *    • Vendors: Fiserv (27d), Eltropy (41d), CO-OP, Diebold, Jack Henry
   *    • Regulatory anchors: NCUA 2026 supervisory priorities, FinCEN AML/CFT
   *      final rule, CFPB small business lending rule, STP/BSA training
   *    • Exam date: July 21, 2026 (47 days out) · readiness 87% → target 97%
   * ════════════════════════════════════════════════════════════════════════ */

  // ─── MemberOnboardingAgent (CW FCU) — CIP · OFAC · PEP · account opening ───
  'cwfcu-onboarding-agent': [
    'Show all pending onboarding applications for this week.',
    'Which new members have PEP flags from the past 30 days?',
    "What's our average onboarding time this month?",
    'List members with address verification failures in May 2026.',
    'Show OFAC screening log for June 2026 and any near-matches.',
    'How many accounts were opened today across all branches?',
    'Approve onboarding ONB-2026-0200 (Anderson, P.) — low-risk PEP review complete.',
    'Walk me through the CIP packet for Torres, R. — what triggered OFAC clear?',
    'Which onboarding applications need a re-upload from the member?',
    "Summarize this week's new-member risk distribution (low/medium/high).",
  ],

  // ─── ComplianceAgent (CW FCU) — BSA/AML · SAR · CTR · CDD · NCUA exam ───
  // 6 of these come straight from the chips block in agent-hub.html.
  'cwfcu-compliance-agent': [
    "What's our current NCUA exam readiness score?",
    'Show members with enhanced due diligence flags.',
    'Which CTRs are pending filing this week?',
    'Summarize BSA/AML training completion status.',
    'Flag any CDD records missing annual review.',
    'What documents are missing from the exam folder?',
    'Show me all members with open SAR reviews from the past 30 days and their risk level.',
    'Draft the SAR narrative for member #44821 structuring pattern.',
    'Summarize CTR filings for May 2026 — were any filed outside the 15-day window?',
    'List CDD records missing annual review in the past 90 days.',
  ],

  // ─── LoanDocumentAgent (CW FCU) — extraction · underwriting · missing docs ───
  'cwfcu-loan-agent': [
    'Show all loans with missing documents in the HITL queue.',
    "What's our average doc-to-decision time this month?",
    'List loans where income verification failed.',
    'Which loan types have the highest exception rate?',
    'Flag any applications with expired ID documents.',
    'Show me the underwriting checklist for LN-2026-0441 (Johnson HELOC).',
    'Walk me through the missing-W-2 case for the Johnson packet.',
    "What's the straight-through approval rate for auto loans in May 2026?",
    'Summarize the Patel mortgage packet LN-2026-0438 — why was it approved?',
    'Compare loan packet extraction accuracy across auto, HELOC, mortgage, and personal.',
  ],

  // ─── VendorContractAgent (CW FCU) — third-party risk · 47 contracts · SLA ───
  // 6 of these come straight from the chips block in agent-hub.html.
  'cwfcu-vendor-agent': [
    'Which contracts expire in the next 90 days?',
    'Show Fiserv SLA performance for Q2 2026.',
    'What vendors are missing third-party risk assessments?',
    'Generate renewal brief for the Eltropy contract.',
    'Which vendors have SLA breaches this month?',
    'Show total annual vendor spend by category.',
    'Walk me through the Fiserv renewal decision — what changes if we delay 30 days?',
    'List vendors with rate drift over the contract escalation cap.',
    "What's the policy obligation chain triggered by the Diebold ATM SOW?",
    'Compare CO-OP shared-branch vs Diebold ATM SLA performance year-to-date.',
  ],

  // ─── PolicyHRAgent (CW FCU) — acks · training · board resolutions · audit ───
  'cwfcu-policy-agent': [
    "Which employees haven't completed BSA training?",
    'Show policy acknowledgment completion by department.',
    "What's our NCUA exam readiness contribution from policy / HR?",
    'List board resolutions missing signatures from the past 90 days.',
    'Which policies are below 80% acknowledgment completion?',
    'Generate the HR audit summary for the NCUA exam.',
    'Send reminders to the 22 employees overdue on BSA training.',
    'Show me board resolution BOARD-RES-2026-04 (Vendor Management Policy) ack status.',
    'Which policy obligations were triggered by vendor contracts this quarter?',
    'List employees who reviewed FinCEN AML/CFT updated procedures.',
  ],

  /* ════════════════════════════════════════════════════════════════════════
   *  BOLER — The Boler Company demo (5 agents × 8 questions)
   *
   *  Questions anchor on the June 2026 cycle corpus:
   *    • 847 employees across 5 divisions
   *      (Hendrickson Intl 412 · Boler Real Estate 89 · Boler Holdings 124 ·
   *       Boler Mfg Services 156 · Corporate/Shared Svcs 66)
   *    • 6 carrier files (Cigna Medical, Delta Dental, Fidelity 401k, VSP Vision,
   *      Hartford Life, Cigna STD/LTD)
   *    • 7 exceptions (Chen R wrong-division, Martinez L duplicate COBRA, etc.)
   *    • 4 Signal alerts (Cigna rate drift, 401k mismatch, Hendrickson growth,
   *      Step Functions SLA)
   *    • CFO: Ziggy Kravitz · Benefits Director: Sarah Mitchell
   *    • $2.14M total · 4.2 hr processing · Stage 2 of 3 approval
   * ════════════════════════════════════════════════════════════════════════ */

  // ─── BenefitsAllocationAgent (BEN) — carrier extract + allocation ───
  'boler-benefits-agent': [
    'Show me all HIGH exceptions in the June cycle with the dollar variance for each.',
    'What is the total allocation for Hendrickson International this month and how does it compare to last month?',
    'Show me all employees in Hendrickson with Cigna medical over $800/mo.',
    'Which employees changed divisions this month and need reallocation?',
    'Generate the journal entry summary for all 5 divisions.',
    "What's the projected full-year benefits cost for Boler Holdings?",
    'Show me the Cigna rate card vs. billed amounts for June 2026.',
    'Which divisions are over budget YTD?',
  ],

  // ─── ExceptionResolutionAgent (EXC) — HITL queue + approval routing ───
  'boler-exception-agent': [
    'Walk me through EXC-2026-0441 (Chen, Robert) — wrong division reclassification.',
    'Apply the reclassification for Chen — move him from Hendrickson to Boler Holdings.',
    'Show me the duplicate enrollment case for Martinez, Laura (EXC-2026-0442).',
    'Which exceptions are still awaiting CFO sign-off and what is the total variance?',
    'How many exceptions has APEX auto-fixed without human review this cycle?',
    "What's the resolution time SLA for HIGH-severity exceptions?",
    'Show me the 401k match rate mismatch exception (Fidelity 4.5% vs HR 4.0%).',
    'Generate a summary of all 7 exceptions for the CFO sign-off package.',
  ],

  // ─── JournalEntryAgent (JE) — division JE generation + S3 distribution ───
  'boler-je-agent': [
    'Generate the Hendrickson International journal entry for June 2026.',
    'Show me the JE preview for all 5 divisions.',
    'Which divisions have approved JEs ready for distribution?',
    "What's the GL coding breakdown for Boler Holdings?",
    'Confirm the JE for Hendrickson balances ($1,042,800 DR = CR).',
    'Show me the cost-center breakdown across 6200-001 through 6200-005.',
    'When will the JEs be distributed to division controllers?',
    'Generate a CSV export of all 5 division JEs for the Accounting team.',
  ],

  // ─── SignalAgent (SIG) — predictive benefits intelligence ───
  'boler-signal-agent': [
    "What's the Cigna carrier rate drift over the past 90 days?",
    'When does our Cigna contract renew and what is our negotiation leverage?',
    'Show me the projected division budget variance for the full year 2026.',
    "What's the Open Enrollment impact forecast for November 2026?",
    'Which carriers are trending above our contracted rate?',
    'Forecast the Hendrickson headcount growth impact on Q3 benefits.',
    'Show me the 401k match rate mismatch financial exposure.',
    'Generate a Signal Brief for the CFO covering all 4 active signals.',
  ],

  // ─── AuditLensAgent (AUD) — governance + DynamoDB lineage ───
  'boler-audit-agent': [
    'Show me the full audit trail for the June 2026 cycle.',
    'When were the 6 carrier files ingested and what was the total amount?',
    'Who approved Stage 1 of the June cycle and what was their decision?',
    'Show me the audit entry for EXC-0441 reclassification.',
    "What's our audit coverage percentage for the June cycle?",
    'Generate a SOC 2 audit-ready export for the June 2026 benefits cycle.',
    'List all stage-2-approval-pending items and their age in hours.',
    'Show me the lineage for the Cigna medical $1,284,320 allocation.',
  ],
};

/* ───────────────── ChatSTP routing classifier ─────────────────
 *
 * The deployed ChatSTP runtime synthesizes the answer in one call without
 * surfacing its routing decision in the response payload (the reasoning[]
 * field comes back empty). For the demo we want the audience to SEE which
 * specialist would have answered, so we run the same intent classification
 * client-side on the user's prompt and tag the response.
 *
 * Keywords are derived from the actual STP corpus + the 50 vetted demo
 * questions. Match precedence: most-specific signals first.
 *
 * If you add new intents to ChatSTP, add the keyword bucket here too so
 * the routing badge stays accurate.
 */
type RoutedAgent = 'PolicyAgent' | 'MaintenanceAgent' | 'DiagnosticsAgent' | 'ReliabilityAgent' | 'ChatSTP';

interface RoutingDecision {
  agent: RoutedAgent | string;   // STP router agents OR a directly-selected specialist agent
  intent: string;        // e.g. "policy_lookup"
  confidence: number;    // 0..1 — high if specific keyword hit, lower if fallthrough
  rationale: string;     // human-readable reason for the route
  label?: string;        // display label override (for non-router specialist agents)
  code?: string;         // avatar code override
}

function classifyIntent(prompt: string): RoutingDecision {
  const p = prompt.toLowerCase();

  // ─── ReliabilityAgent (predictive) ───
  if (/\b(rul|risk|forecast|predict|anomal|advance.*(pm|maintenance)|estimate.*avoid|sensor|trend|p50|p90|days[-\s]until|when.*fail)/i.test(p)) {
    return { agent: 'ReliabilityAgent', intent: 'predictive_maintenance', confidence: 0.94,
      rationale: 'Question asks for forecast / risk / RUL / PM advance — domain of ReliabilityAgent.' };
  }

  // ─── DiagnosticsAgent (failure-mode aggregation) ───
  if (/\b(failure[-\s]mode|failed before|seen.*before|recurring|pattern|root[-\s]cause|why did|how often|cited.*wo|seizure|lead time|across.*pumps?|compare.*history|condition report|cr-\d|recurrence|aggregate)/i.test(p)) {
    return { agent: 'DiagnosticsAgent', intent: 'failure_analysis', confidence: 0.92,
      rationale: 'Question is about failure-mode patterns or historical analysis — DiagnosticsAgent.' };
  }

  // ─── MaintenanceAgent (PM history, work packages) ───
  if (/\b(pm history|last pm|next pm|work order|work package|wo[-\s]?\d|loto|sign[-\s]?off|engineer.*perform|hours.*charged|deferred|maintenance history|inspection|acceptance criteria|mechanical seal|coupling alignment|bearing inspection)/i.test(p)) {
    return { agent: 'MaintenanceAgent', intent: 'equipment_pm_history', confidence: 0.93,
      rationale: 'Question references work orders / PM scope / sign-offs — MaintenanceAgent.' };
  }

  // ─── PolicyAgent (verbatim cites) ───
  if (/\b(policy|procedure|stp[-\s]?\d|cite|verbatim|tech[-\s]?spec|lco|cfr|allowance|reimburs|fitness for duty|radiation work permit|rwp|retention|records|compliance|guideline|approver|cadence|review.*frequency)/i.test(p)) {
    return { agent: 'PolicyAgent', intent: 'policy_lookup', confidence: 0.92,
      rationale: 'Question asks for a procedure / policy quote with provenance — PolicyAgent.' };
  }

  // ─── Multi-domain / synthesis / unclear ───
  if (/\b(summari[sz]e|recap|overview|across.*(everything|all)|what have we discussed)/i.test(p)) {
    return { agent: 'ChatSTP', intent: 'cross_domain_synthesis', confidence: 0.78,
      rationale: 'Question spans multiple domains — ChatSTP synthesizes across specialists.' };
  }

  // Default fallback — ChatSTP handles directly with broad context
  return { agent: 'ChatSTP', intent: 'general_query', confidence: 0.55,
    rationale: 'No strong signal — ChatSTP handles directly without delegation.' };
}

/** Visual color theme per routed agent (matches the LEFT-rail agent
 *  picker so the routing chip in the chat looks like the same agent
 *  badge the user already sees). */
const ROUTED_AGENT_THEME: Record<RoutedAgent, { bg: string; color: string; label: string; code: string }> = {
  PolicyAgent:       { bg: '#dbeafe', color: '#1d4ed8', label: 'PolicyAgent',       code: 'POL' },
  MaintenanceAgent:  { bg: '#dcfce7', color: '#16a34a', label: 'MaintenanceAgent',  code: 'MNT' },
  DiagnosticsAgent:  { bg: '#fef3c7', color: '#d97706', label: 'DiagnosticsAgent',  code: 'DGN' },
  ReliabilityAgent:  { bg: '#fee2e2', color: '#dc2626', label: 'ReliabilityAgent',  code: 'RLY' },
  ChatSTP:           { bg: '#eef2ff', color: '#1e3a8a', label: 'ChatSTP',           code: 'STP' },
};

/* ───────────────── Lineage / audit history ─────────────────
 *
 * One entry per (user prompt, agent response) pair. Used by the right-panel
 * "History" tab to show the full audibility trail: every question, every
 * routing decision, every model, every component touched, every reply.
 *
 * The same payload backs the Audit Lens — these LineageEntry rows are
 * the human-readable companion to the cryptographic audit log on the
 * server (S3 + DynamoDB).
 */
interface LineageEntry {
  id: string;                       // unique per turn
  timestamp: string;                // ISO 8601
  prompt: string;                   // user's verbatim question
  agentSelected: string;            // which agent the user had selected
  routing: RoutingDecision;         // who ChatSTP would route to
  response: string;                 // first 400 chars of the agent reply
  durationMs: number;               // wall-clock latency
  source: 'agentcore' | 'simulator' | 'mock';
  modelUsed?: string;               // backend-reported model id when available
  toolsCalled: string[];            // actions_taken from the agent response
  reasoningSteps: number;           // count of reasoning steps
}

/** Coerce backend actions_taken entries (which may be strings OR objects like
 *  {name, result, ts}) into display strings, so they never get rendered as a
 *  raw object (React crashes on object children). */
function normalizeActions(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((a) => {
    if (typeof a === 'string') return a;
    if (a && typeof a === 'object') {
      const o = a as Record<string, any>;
      const name = o.name || o.action || o.tool || 'action';
      return o.result ? `${name} · ${o.result}` : String(name);
    }
    return String(a);
  });
}

/**
 * Demo files surfaced in the right-panel "File" tab when nothing has been
 * clicked yet. Each entry maps to a real file under
 * synthetic-data/<folder>/, served by the backend
 * /api/v1/documents/demo-preview endpoint.
 *
 * Adding a new demo file: drop it under synthetic-data/<folder>/, add the
 * entry below with a friendly label. The backend whitelist already
 * accepts any .txt/.md/.json file in the registered folder.
 */
const DEMO_PREVIEW_FILES: Array<{ folder: string; filename: string; label: string }> = [
  { folder: 'nuclear_operations', filename: 'STP-OP-2204_RCS_Surveillance_Rev6.txt',
    label: '📄 STP-OP-2204 · RCS Surveillance · Rev 6 (12 pp)' },
  { folder: 'nuclear_operations', filename: 'WO-2026-00871_PUMP-RCP-1A_Work_Package.txt',
    label: '🔧 WO-2026-00871 · P-3A Work Package (13 pp)' },
  { folder: 'nuclear_operations', filename: 'CR-2026-0188_PUMP-CCW-1A_Bearing_Seizure_Incident.txt',
    label: '⚠ CR-2026-0188 · CCW Pump Bearing Seizure (14 pp)' },
  { folder: 'nuclear_operations', filename: 'SENSOR-PUMP-CCW-1A_Anomaly_Stream_2026-05.txt',
    label: '📈 SENSOR · CCW Pump Anomaly Stream · May 2026 (11 pp)' },

  // ─── Verizon Far Edge demo files (POC for James Patchett) ───
  { folder: 'verizon_far_edge', filename: 'VZ-RUNBOOK-CAAS-v24-excerpt.txt',
    label: '📘 VZ-RUNBOOK-CAAS-v24 · CaaS Node Deployment Runbook (48 pp)' },
  { folder: 'verizon_far_edge', filename: 'WindRiver-24.12-ReleaseNotes-excerpt.txt',
    label: '🛰  Wind River 24.12 · Release Notes (41 pp)' },
  { folder: 'verizon_far_edge', filename: 'VZ-KB-Known-Issues-excerpt.txt',
    label: '📚 VZ-KB · Known Issues KB (94 pp · incl. high-risk Type-B RCAs)' },
  { folder: 'verizon_far_edge', filename: 'VZ-Upgrade-Procedures-2026-excerpt.txt',
    label: '⬆ VZ-Upgrade-Procedures · 2026 · Rev 4 (67 pp)' },
  { folder: 'verizon_far_edge', filename: 'VZ-Redfish-Integration-Guide-excerpt.txt',
    label: '🔌 VZ-Redfish-Integration-Guide · v3 (32 pp)' },
  { folder: 'verizon_far_edge', filename: 'VZ-RT-Kernel-Errata-excerpt.txt',
    label: '⚙ VZ-RT-Kernel-Errata · Rev 8 (19 pp)' },
  { folder: 'verizon_far_edge', filename: 'VZ-OpenShift-Operator-Guide-excerpt.txt',
    label: '☁ VZ-OpenShift-Operator-Guide · v5 (35 pp)' },
  { folder: 'verizon_far_edge', filename: 'VZ-Ansible-Playbook-Catalog-excerpt.txt',
    label: '🧰 VZ-Ansible-Playbook-Catalog · v6 (28 pp)' },
];

/** Resolve quick-reply chips for the current selection. Doc context wins
 *  (most specific); per-agent map next; final fallback is the generic set. */
function resolveQuickChips(
  agentId: string | undefined,
  ctx: DocContext | null,
): string[] {
  if (ctx) return ctx.quickReplies;
  if (agentId && AGENT_QUICK_REPLIES[agentId]) return AGENT_QUICK_REPLIES[agentId];
  return DEFAULT_QUICK_REPLIES;
}

/* ──────────────────────── chat message model ──────────────────────── */

interface ChatMessage {
  id: string;                    // local render key
  backend_id?: string;           // real message_id from /chat backend (enables DVR lookup)
  who: 'user' | 'agent' | 'file';
  time: string;
  content: React.ReactNode;
}

/* ──────────────────────── component ──────────────────────── */

export default function AgentHub() {
  const router = useRouter();
  // Accept ?demo=1|2|3 (CBB-specific), ?doc=<key> (generic), and ?agent=<id>
  // (direct agent landing — used by Agentic Enterprise lens links).
  const demoParam = typeof router.query.demo === 'string' ? (router.query.demo as string) : undefined;
  const rawDocParam = typeof router.query.doc === 'string' ? (router.query.doc as DocKey) : undefined;
  const agentParam = typeof router.query.agent === 'string' ? (router.query.agent as string) : undefined;
  const docParam: DocKey | undefined = demoParam && DEMO_TO_DOC[demoParam]
    ? DEMO_TO_DOC[demoParam]
    : rawDocParam;
  const ctx = docParam && DOC_CONTEXTS[docParam] ? DOC_CONTEXTS[docParam] : null;

  // Demo-mode filter — collapses the left-rail agent picker to whichever
  // industry is selected in Settings. 'all' shows every agent.
  const [demoMode] = useDemoMode();
  const visibleAgents = AGENTS.filter((a) => isIndustryVisible(a.industry, demoMode));

  // Pick the default selection: STP demo lands on ChatSTP, supply chain
  // demo lands on customerops, agentic_enterprise lands on OrchestratorAgent,
  // all-industries lands on invoice.
  const defaultByMode =
    demoMode === 'nuclear_operations' || demoMode === 'stp' ? 'chatstp'
    : demoMode === 'supply_manufacturing' || demoMode === 'manufacturing' || demoMode === 'supply_chain' ? 'customerops'
    : demoMode === 'agentic_enterprise'        ? 'orchestrator-agent'
    : demoMode === 'supply_chain_orchestrator' ? 'orchestrator-agent'
    : demoMode === 'hospitality'               ? 'concierge-agent'
    : demoMode === 'commercial_real_estate'    ? 'lease-agent'
    : demoMode === 'verizon_far_edge'          ? 'certification-agent'
    : demoMode === 'eprod' || demoMode === 'oil_gas_midstream' ? 'eprod-invoice-agent'
    : demoMode === 'cwfcu' || demoMode === 'credit_union' ? 'cwfcu-compliance-agent'
    : demoMode === 'boler' || demoMode === 'manufacturing_multi_division' ? 'boler-benefits-agent'
    : 'invoice';
  // ?agent=<id> takes priority over ?doc=, then doc context's agentId, then default.
  const initialSelected = agentParam || (ctx ? ctx.agentId : defaultByMode);
  const [selected, setSelected] = useState<string>(initialSelected);

  // When demo mode changes, reset selection to the default for the new mode
  // if the currently-selected agent isn't visible in the new mode. Prevents
  // ChatSTP from "sticking" when the user switches from STP → EPROD demo.
  useEffect(() => {
    if (!visibleAgents.find((a) => a.id === selected)) {
      setSelected(defaultByMode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoMode]);

  const agent = visibleAgents.find((a) => a.id === selected)
              || AGENTS.find((a) => a.id === selected)
              || visibleAgents[0]
              || AGENTS[0];

  // Rebuild when the URL doc param changes so arriving from ApexLens after a
  // different sample swaps the whole context cleanly. Also wire the file
  // bubble's onClick to open the right-panel File preview tab — clicking
  // a file in the chat shows its source content on the right.
  const initialMessages = useMemo<ChatMessage[]>(() => {
    const demoFile = lookupDemoFileForContext(ctx, agent.id);
    const onFileClick = demoFile
      ? () => openFilePreview(demoFile.folder, demoFile.filename)
      : undefined;
    return buildInitialMessages(agent, ctx, onFileClick);
    // Re-derive only when the doc param string changes — agent follows ctx.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [docParam]);

  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [contextCleared, setContextCleared] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // AgentCore runtime state.
  // status: 'checking'  — ping in flight (start state)
  //         'connected' — backend /chat/sessions succeeded → reasoning lives in AgentCore
  //         'offline'   — backend didn't respond → fall back to local mock so chat still works
  //         'deploying' — user clicked Deploy AgentCore; runs a 5-step fake animation
  const [agentCoreStatus, setAgentCoreStatus] = useState<'checking' | 'connected' | 'offline' | 'deploying'>('checking');
  const [sessionId,       setSessionId]       = useState<string | null>(null);
  const [deployOpen,      setDeployOpen]      = useState(false);

  // FEATURE 2 — Audit Lens: right-panel tab + per-message reasoning timeline.
  const [rightTab, setRightTab]       = useState<'context' | 'file' | 'history' | 'dvr'>('context');
  // Full audibility trail — one entry per round-trip (user prompt + agent
  // response). The History tab on the right renders these as an expandable
  // timeline showing routing, model used, tools called, latency, source.
  const [lineage, setLineage]         = useState<LineageEntry[]>([]);
  // File-preview state — when a user clicks a file bubble in the chat,
  // we fetch the synthetic doc content from the backend and render it
  // in monospace in the right-panel "File" tab. The Agent Hub becomes a
  // 3-pane document workbench: agents on the left, conversation in the
  // middle, source document on the right.
  const [previewFile, setPreviewFile] = useState<{
    name: string;
    content: string;
    folder: string;
    sizeBytes: number;
  } | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);
  // Remember which tab the user was on BEFORE clicking a file, so the
  // "Close preview" button on the File tab can return them to that tab
  // (Context, History, or DVR) — preserving the screen state they had
  // before the preview interrupted them.
  const [tabBeforePreview, setTabBeforePreview] = useState<'context' | 'file' | 'history' | 'dvr'>('context');

  /** Fetch a demo doc by (folder, filename) and switch the right panel
   *  to the File tab. Used by file-card onClick handlers. */
  const openFilePreview = async (folder: string, filename: string) => {
    setPreviewError(null);
    setPreviewLoading(true);
    // Remember where we were so we can return on close — but only if we
    // weren't already on the File tab (avoids overwriting on re-open).
    setRightTab((prev) => {
      if (prev !== 'file') setTabBeforePreview(prev);
      return 'file';
    });
    try {
      const r = await fetch(
        `${API_BASE_URL}/documents/demo-preview/${encodeURIComponent(folder)}/${encodeURIComponent(filename)}`,
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const j = await r.json();
      setPreviewFile({
        name: j.filename,
        content: j.content,
        folder: j.folder,
        sizeBytes: j.size_bytes,
      });
    } catch (e) {
      setPreviewError(`Could not load preview for ${filename}: ${(e as Error).message}`);
      setPreviewFile(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  /** Clear the previewed file and either collapse back to the file
   *  picker (if we were already on the File tab) or jump back to the
   *  tab the user was on before they clicked the file. */
  const closeFilePreview = (returnToPrevious: boolean) => {
    setPreviewFile(null);
    setPreviewError(null);
    setPreviewLoading(false);
    if (returnToPrevious) {
      setRightTab(tabBeforePreview);
    }
  };
  const [dvrMessageId, setDvrMessageId] = useState<string | null>(null);

  // PER-AGENT chat persistence. The chat history used to be flat-reset
  // whenever the user clicked a different agent in the left rail —
  // they'd lose their conversation. Now we stash each agent's
  // messages keyed by agent.id so flipping back restores the chat.
  // The user gets explicit control via the "Clear" button in the chat
  // header — that empties the current agent's stash and resets to the
  // intro greeting.
  const messagesByAgentRef = useRef<Record<string, ChatMessage[]>>({});

  // When doc/demo param changes, reset messages + selected agent + context.
  useEffect(() => {
    if (ctx) setSelected(ctx.agentId);
    setMessages(initialMessages);
    setContextCleared(false);
    // Stash the freshly-derived messages under the active agent so
    // future "switch back to this agent" calls restore them.
    messagesByAgentRef.current[ctx?.agentId ?? selected] = initialMessages;
  }, [docParam, demoParam]); // eslint-disable-line react-hooks/exhaustive-deps

  // When the user picks a DIFFERENT agent from the sidebar (no URL change),
  // (a) save the OUTGOING agent's messages, then (b) restore the incoming
  // agent's prior messages — or build a fresh intro if this is the first
  // time we're seeing them.
  const lastSelectedRef = useRef(selected);
  useEffect(() => {
    if (lastSelectedRef.current === selected) return;
    const prevAgent = lastSelectedRef.current;
    lastSelectedRef.current = selected;
    if (ctx && ctx.agentId === selected) return;       // same as URL selection

    // (a) Stash outgoing agent's chat — but only if it has more than
    // the intro message (i.e. user has actually had a conversation).
    setMessages((current) => {
      messagesByAgentRef.current[prevAgent] = current;
      return current;
    });

    // (b) Restore the new agent's prior chat OR build a fresh intro.
    const fresh = AGENTS.find(a => a.id === selected) || AGENTS[0];
    const stashed = messagesByAgentRef.current[selected];
    if (stashed && stashed.length > 0) {
      setMessages(stashed);
    } else {
      const built = buildInitialMessages(fresh, null);
      messagesByAgentRef.current[selected] = built;
      setMessages(built);
    }
    setContextCleared(true);
  }, [selected]); // eslint-disable-line react-hooks/exhaustive-deps

  /** Clear the current agent's chat — wipes the stash for that agent
   *  and rebuilds the intro greeting. The "Clear" button in the chat
   *  header is the only way to invoke this; switching agents now
   *  PRESERVES history. */
  const clearChat = () => {
    const fresh = AGENTS.find(a => a.id === selected) || AGENTS[0];
    const built = buildInitialMessages(fresh, null);
    messagesByAgentRef.current[selected] = built;
    setMessages(built);
    setLineage([]);  // also clear lineage for this session
  };

  // Autoscroll to bottom on new messages.
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, isTyping]);

  // Try to open a backend chat session for the selected agent. Determines
  // whether AgentCore reasoning orchestration is reachable (pill turns green).
  useEffect(() => {
    let cancelled = false;
    setAgentCoreStatus('checking');
    setSessionId(null);

    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 4000);

    (async () => {
      try {
        const r = await fetch(
          `${API_BASE_URL}/chat/sessions?agent_id=${encodeURIComponent(selected)}&user_id=web-ui`,
          { method: 'POST', signal: controller.signal },
        );
        if (!r.ok) throw new Error(`status ${r.status}`);
        const j = await r.json() as { session_id: string };
        if (!cancelled) {
          setSessionId(j.session_id || null);
          setAgentCoreStatus(j.session_id ? 'connected' : 'offline');
        }
      } catch {
        if (!cancelled) setAgentCoreStatus('offline');
      } finally {
        window.clearTimeout(timer);
      }
    })();

    return () => { cancelled = true; controller.abort(); window.clearTimeout(timer); };
  }, [selected]);

  // Subscribe to the shared review feed. When a reviewer approves/rejects an
  // item on /review, the matching agent sees a system message land in its
  // chat. On mount we also replay any pre-existing recent entries for the
  // selected agent so the hand-off never looks empty.
  useEffect(() => {
    const recent = readReviewFeed().filter(e => e.agent_id === selected).slice(0, 3);
    if (recent.length > 0) {
      const systemMsgs: ChatMessage[] = recent.reverse().map((e) => ({
        id: `feed-${e.id}-${e.decision}`,
        who: 'agent',
        time: `${agent.name} · review hand-off`,
        content: renderReviewHandoff(e),
      }));
      setMessages((m) => [...m, ...systemMsgs]);
    }

    const unsub = subscribeToReviewFeed((entry) => {
      if (entry.agent_id !== selected) return;
      setMessages((m) => [
        ...m,
        {
          id: `feed-${entry.id}-${entry.decision}-${Date.now()}`,
          who: 'agent',
          time: `${agent.name} · review hand-off · just now`,
          content: renderReviewHandoff(entry),
        },
      ]);
    });
    return unsub;
  }, [selected]); // eslint-disable-line react-hooks/exhaustive-deps

  const activeCtx = contextCleared ? null : ctx;
  // Quick-reply chips: doc context first (most specific), then per-agent
  // canned demo questions, then the generic default. The per-agent map
  // is the new STP demo path — 10 vetted questions per specialist agent
  // plus 10 router questions for ChatSTP that demonstrate context
  // inference across follow-up turns.
  const activeChips = resolveQuickChips(agent.id, activeCtx);

  /**
   * Send a user message: call the backend AgentCore endpoint when it's
   * reachable; otherwise fall back to the local mock so the demo never
   * dead-ends. Either way the user sees their message + a response.
   */
  /** Append a row to the audibility trail. Called on every round-trip
   *  so the History tab and the Audit Lens see every Q&A pair. */
  const appendLineage = (entry: LineageEntry) => {
    setLineage((prev) => [...prev, entry]);
  };

  const sendMessage = async (text: string) => {
    const clean = text.trim();
    if (!clean) return;

    // Classify the routing decision client-side so we can show a "→ X"
    // badge above the agent response. ONLY the ChatSTP router actually
    // delegates — for every other (directly-selected) specialist agent the
    // badge should confirm THAT agent handled it, not invent a ChatSTP route.
    const routing: RoutingDecision = selected === 'chatstp'
      ? classifyIntent(clean)
      : {
          agent: agent.name,
          label: agent.name,
          code: agent.code,
          intent: 'direct_handling',
          confidence: 0.97,
          rationale: `${agent.name} handled this request directly — no router delegation.`,
        };
    const startedAt = Date.now();

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      who: 'user',
      time: 'You · just now',
      content: <p style={{ fontSize: 14 }}>{clean}</p>,
    };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setIsTyping(true);

    const backendReady = agentCoreStatus === 'connected' && sessionId;
    if (backendReady) {
      try {
        const overrides = buildModelOverridesPayload();
        const r = await fetch(
          `${API_BASE_URL}/chat/sessions/${sessionId}/messages?content=${encodeURIComponent(clean)}`,
          {
            method: 'POST',
            headers: overrides ? { 'Content-Type': 'application/json' } : {},
            body: overrides ? JSON.stringify({ model_overrides: overrides }) : undefined,
          },
        );
        if (r.ok) {
          const j = await r.json() as { agent_response?: { content?: string; message_id?: string; reasoning?: unknown[]; actions_taken?: string[] } };
          const body = j.agent_response?.content?.trim();
          const backendId = j.agent_response?.message_id;
          if (body) {
            const durationMs = Date.now() - startedAt;
            const tools = normalizeActions(j.agent_response?.actions_taken);
            const reasoningCount = (j.agent_response?.reasoning as unknown[])?.length || 0;

            setMessages((m) => [...m, {
              id: `a-${Date.now()}`,
              backend_id: backendId,
              who: 'agent',
              time: `${agent.name} · AgentCore · just now`,
              content: (
                <>
                  <RoutingBadge routing={routing} latencyMs={durationMs} />
                  <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55, whiteSpace: 'pre-wrap', marginTop: 6 }}>{body}</p>
                </>
              ),
            }]);

            appendLineage({
              id: `lin-${Date.now()}`,
              timestamp: new Date().toISOString(),
              prompt: clean,
              agentSelected: agent.name,
              routing,
              response: body.slice(0, 400),
              durationMs,
              source: 'agentcore',
              modelUsed: undefined,
              toolsCalled: tools,
              reasoningSteps: reasoningCount,
            });

            setIsTyping(false);
            return;
          }
        }
      } catch {
        // fall through to mock
      }
    }

    // Mock fallback — always returns something so the chat never stalls.
    window.setTimeout(() => {
      const response = getMockResponse(clean, activeCtx);
      const durationMs = Date.now() - startedAt;
      const agentMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        who: 'agent',
        time: `${agent.name} · just now`,
        content: (
          <>
            <RoutingBadge routing={routing} latencyMs={durationMs} />
            <div style={{ marginTop: 6 }}>{response}</div>
          </>
        ),
      };
      setMessages((m) => [...m, agentMsg]);

      // Best-effort lineage entry — extract a string preview from the React
      // node so the History tab has something to render.
      const responsePreview = typeof response === 'string'
        ? response
        : 'Mock response (offline mode).';

      appendLineage({
        id: `lin-${Date.now()}`,
        timestamp: new Date().toISOString(),
        prompt: clean,
        agentSelected: agent.name,
        routing,
        response: responsePreview.slice(0, 400),
        durationMs,
        source: 'mock',
        toolsCalled: [],
        reasoningSteps: 0,
      });

      setIsTyping(false);
    }, 900);
  };

  /** Fake AgentCore deploy animation — 5 steps over ~4s, then flips to connected. */
  const deployAgentCore = () => {
    setAgentCoreStatus('deploying');
    const steps = [
      'Packaging Python 3.11 runtime',
      'Uploading handler to Bedrock AgentCore',
      'Configuring IAM role + VPC endpoints',
      'Provisioning Claude Opus 4 inference profile',
      'Warming up agent runtime',
    ];
    steps.forEach((label, i) => {
      window.setTimeout(() => {
        setMessages((m) => [...m, {
          id: `deploy-${i}-${Date.now()}`,
          who: 'agent',
          time: `AgentCore · deploy ${i + 1}/${steps.length}`,
          content: (
            <p style={{ fontSize: 13, color: '#0f172a', lineHeight: 1.55 }}>
              <span style={{ color: '#d97706' }}>●</span>{' '}
              <span className="mono" style={{ color: '#475569' }}>{label}</span>
            </p>
          ),
        }]);
      }, (i + 1) * 750);
    });
    window.setTimeout(() => {
      setAgentCoreStatus('connected');
      setSessionId(`deployed-${Date.now()}`);
      setMessages((m) => [...m, {
        id: `deploy-done-${Date.now()}`,
        who: 'agent',
        time: `AgentCore · ready`,
        content: (
          <p style={{ fontSize: 13, color: '#0f172a', lineHeight: 1.55 }}>
            <span style={{ color: '#16a34a' }}>✓</span>{' '}
            <strong>AgentCore online.</strong> Reasoning now routed through Claude Opus 4. Ask me anything about this work item.
          </p>
        ),
      }]);
      setDeployOpen(false);
    }, steps.length * 750 + 600);
  };

  return (
    <>
      <Head><title>{__brandedHeadTitle('Agent Hub')}</title></Head>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '248px minmax(0, 1fr) 300px',
        gap: 0,
        height: 'calc(100vh - 128px)',
        background: '#fff',
        borderRadius: 16,
        border: '1px solid #f1f5f9',
        overflow: 'hidden',
      }}>
        {/* LEFT — agent selector + queue */}
        <div style={{ borderRight: '1px solid #f1f5f9', display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
          <div style={{ padding: 16, borderBottom: '1px solid #f8fafc' }}>
            <div style={{ position: 'relative' }}>
              <input type="text" className="input" placeholder="Search agents..." style={{ paddingLeft: 34, fontSize: 13 }} />
              <Icon name="search" className="" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', width: 15, height: 15, color: '#9ca3af' }} />
            </div>
          </div>
          <div className="light-scroll" style={{ flex: 1, minHeight: 0, overflowY: 'auto' }}>
            <SideLabel>Active Agents</SideLabel>
            {visibleAgents.map((a) => (
              <AgentRow key={a.id} agent={a} active={a.id === selected} onClick={() => setSelected(a.id)} />
            ))}
            <SideLabel>Work Queue</SideLabel>
            {QUEUE.map((q) => (
              <div
                key={q.id}
                style={{
                  padding: '10px 12px',
                  cursor: 'pointer',
                  borderLeft: q.highlight ? '3px solid #f59e0b' : 'none',
                }}
                onMouseOver={(e) => (e.currentTarget.style.background = q.highlight ? '#fffbeb' : '#f8fafc')}
                onMouseOut={(e) => (e.currentTarget.style.background = '')}
              >
                <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{q.id} · {q.title}</div>
                <div
                  className={q.tone === 'blue' ? 'animate-pulse' : ''}
                  style={{ fontSize: 11, color: q.tone === 'blue' ? '#3b82f6' : '#d97706', marginTop: 2 }}
                >
                  {q.detail}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CENTER — chat */}
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0, overflow: 'hidden' }}>
          {/* Chat header */}
          <div style={{ padding: '16px 20px', borderBottom: '1px solid #f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: agent.iconBg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, color: agent.iconColor }}>
                {agent.code}
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>{agent.name}</div>
                <div style={{ fontSize: 12, color: STATUS_COLOR[agent.status], fontWeight: 500 }}>
                  ● {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)} · {activeCtx ? activeCtx.name : agent.detail}
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <AgentCorePill
                status={agentCoreStatus}
                onDeploy={() => setDeployOpen(true)}
              />
              <button
                className="btn btn-secondary btn-sm"
                onClick={clearChat}
                title="Clear this agent's chat history. Switching agents preserves chat — use this to start fresh."
              >
                Clear Chat
              </button>
              <button className="btn btn-secondary btn-sm">Upload Doc</button>
              <button className="btn btn-secondary btn-sm">View Queue</button>
            </div>
          </div>

          {/* Document context banner (only when ?doc=...) */}
          {activeCtx && (
            <div style={{
              background: '#eff6ff',
              borderBottom: '1px solid #bfdbfe',
              padding: '10px 20px',
              display: 'flex',
              alignItems: 'center',
              gap: 10,
            }}>
              <Icon name="doc" className="" style={{ width: 16, height: 16, color: '#2563eb' }} />
              <span style={{ fontSize: 13, fontWeight: 600, color: '#1e40af' }}>Context:</span>
              <span style={{ fontSize: 13, color: '#1d4ed8' }}>{activeCtx.name}</span>
              <span className={activeCtx.typeChip} style={{ fontSize: 10 }}>{activeCtx.type}</span>
              <span
                onClick={() => setContextCleared(true)}
                style={{
                  fontSize: 11,
                  color: '#94a3b8',
                  marginLeft: 'auto',
                  cursor: 'pointer',
                  userSelect: 'none',
                }}
              >
                ✕ Clear context
              </span>
            </div>
          )}

          {/* Messages (flex:1 with minHeight:0 so it can actually shrink and keep the composer pinned) */}
          <div
            ref={scrollRef}
            className="light-scroll"
            style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: 20, display: 'flex', flexDirection: 'column', gap: 16, background: '#f8fafc' }}
          >
            {/* Proactive alert — only renders when STP demo mode is active.
                Self-polls /signals/stp/proactive-alert and surfaces the
                ReliabilityAgent banner ~90s into the session. The CTA
                pre-fills the chat input with the predictive query. */}
            <ProactiveAlertBanner
              sessionId={sessionId || `local-${selected}`}
              onCta={(suggestedQuery) => {
                setInput(suggestedQuery);
                // Auto-submit so the chat fires immediately on click
                window.setTimeout(() => sendMessage(suggestedQuery), 100);
              }}
            />
            {messages.map((m) =>
              m.who === 'file' ? (
                <FileBubble key={m.id} time={m.time}>{m.content}</FileBubble>
              ) : (
                <div
                  key={m.id}
                  onClick={() => {
                    if (m.who !== 'agent') return;
                    // Prefer the real backend message_id so the DVR endpoint
                    // can look up persisted reasoning; fall back to local id.
                    setDvrMessageId(m.backend_id ?? m.id);
                    setRightTab('dvr');
                  }}
                  style={{ cursor: m.who === 'agent' ? 'pointer' : 'default' }}
                  title={m.who === 'agent' ? 'Click to inspect reasoning in Audit Lens →' : undefined}
                >
                  <ChatMsg
                    who={m.who}
                    time={m.time}
                    avatar={m.who === 'agent' ? { code: agent.code, bg: agent.iconBg, color: agent.iconColor } : undefined}
                  >
                    {m.content}
                  </ChatMsg>
                </div>
              ),
            )}

            {isTyping && (
              <ChatMsg
                who="agent"
                avatar={{ code: agent.code, bg: agent.iconBg, color: agent.iconColor }}
                time={`${agent.name} · typing…`}
              >
                <TypingDots />
              </ChatMsg>
            )}
          </div>

          {/* Composer (flex-shrink:0 so it never gets squeezed out of view) */}
          <div style={{ padding: '16px 20px', borderTop: '1px solid #f1f5f9', background: '#fff', flexShrink: 0 }}>
            <form
              onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
              style={{ display: 'flex', gap: 10, alignItems: 'center' }}
            >
              <input
                type="text"
                className="input"
                placeholder={`Ask ${agent.name} anything...`}
                style={{ flex: 1 }}
                value={input}
                onChange={(e) => setInput(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={isTyping || !input.trim()}>
                <Icon name="send" className="" style={{ width: 16, height: 16 }} />
              </button>
            </form>
            <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
              {activeChips.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  disabled={isTyping}
                  style={{
                    padding: '5px 12px',
                    background: '#f1f5f9',
                    border: 'none',
                    borderRadius: 8,
                    fontSize: 12,
                    color: '#374151',
                    cursor: isTyping ? 'not-allowed' : 'pointer',
                    opacity: isTyping ? 0.6 : 1,
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT — work item detail + Audit Lens (tabbed) */}
        <div style={{ borderLeft: '1px solid #f1f5f9', display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
          {/* Tab bar */}
          <div style={{ display: 'flex', borderBottom: '1px solid #f1f5f9' }}>
            {(['context', 'file', 'history', 'dvr'] as const).map((k) => {
              const label = k === 'context' ? 'Context'
                : k === 'file'    ? 'File'
                : k === 'history' ? `History${lineage.length ? ` (${lineage.length})` : ''}`
                : 'Audit Lens';
              return (
                <button
                  key={k}
                  onClick={() => setRightTab(k)}
                  style={{
                    flex: 1,
                    padding: '12px 6px',
                    background: rightTab === k ? '#fff' : '#f8fafc',
                    border: 'none',
                    borderBottom: rightTab === k ? '2px solid #2563eb' : '2px solid transparent',
                    color: rightTab === k ? '#2563eb' : '#64748b',
                    fontSize: 10,
                    fontWeight: 700,
                    letterSpacing: '.04em',
                    textTransform: 'uppercase',
                    cursor: 'pointer',
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>

          {rightTab === 'context' && (() => {
            // Compute the context payload dynamically. Priority order:
            //   1. activeCtx (set by Apex Lens drop) — most specific
            //   2. previewFile (user clicked a file in the File tab)
            //   3. Last lineage entry (most-recent Q&A round-trip)
            //   4. Selected agent's default context (per-agent intro card)
            //   5. Final fallback: gentle empty state (NOT the hardcoded
            //      Globex invoice that used to leak through)
            const ctxView = computeContextView({
              activeCtx,
              previewFile,
              lineage,
              agentId: agent.id,
              agentName: agent.name,
              demoMode,
            });
            return (
              <>
                <div style={{ padding: 16, borderBottom: '1px solid #f8fafc' }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>
                    {ctxView.title}
                  </div>
                  {ctxView.subtitle && (
                    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                      {ctxView.subtitle}
                    </div>
                  )}
                  <span
                    className={ctxView.chipClass}
                    style={{ marginTop: 8, display: 'inline-block' }}
                  >
                    {ctxView.chipLabel}
                  </span>
                </div>
                <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {ctxView.flags.length > 0 && (
                    <div>
                      <MiniLabel>{ctxView.flagsLabel}</MiniLabel>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                        {ctxView.flags.map((f, i) => (
                          <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                            <span className={`dot-${f.color}`} style={{ marginTop: 3, flexShrink: 0 }} />
                            <span style={{ fontSize: 12, color: '#374151', lineHeight: 1.45 }}>{f.text}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {ctxView.routing && (
                    <div>
                      <MiniLabel>Routing</MiniLabel>
                      <div style={{ fontSize: 12, color: '#0f172a', fontWeight: 500, lineHeight: 1.5 }}>
                        {ctxView.routing}
                      </div>
                    </div>
                  )}

                  {ctxView.facts.length > 0 && (
                    <div>
                      <MiniLabel>{ctxView.factsLabel || 'Key Facts'}</MiniLabel>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                        {ctxView.facts.map((f, i) => (
                          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', gap: 8, fontSize: 11 }}>
                            <span style={{ color: '#64748b', flexShrink: 0 }}>{f.label}</span>
                            <span style={{ color: '#0f172a', fontWeight: 500, textAlign: 'right', wordBreak: 'break-word' }}>{f.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {ctxView.primaryAction && (
                      <Link href={ctxView.primaryAction.href} className="btn btn-primary btn-sm" style={{ justifyContent: 'center' }}>
                        {ctxView.primaryAction.label}
                      </Link>
                    )}
                    {ctxView.secondaryAction && (
                      <Link href={ctxView.secondaryAction.href} className="btn btn-secondary btn-sm" style={{ justifyContent: 'center' }}>
                        {ctxView.secondaryAction.label}
                      </Link>
                    )}
                  </div>
                </div>
              </>
            );
          })()}

          {rightTab === 'file' && (
            <>
              {/* Header: filename + size + folder + close/collapse controls */}
              <div style={{ padding: '12px 14px', borderBottom: '1px solid #f8fafc' }}>
                {previewFile ? (
                  <>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', wordBreak: 'break-all', flex: 1, minWidth: 0 }}>
                        {previewFile.name}
                      </div>
                      <div style={{ display: 'flex', gap: 4, flexShrink: 0 }}>
                        <button
                          onClick={() => closeFilePreview(false)}
                          title="Collapse preview — return to the file list (stay on File tab)"
                          style={{
                            fontSize: 10,
                            fontWeight: 600,
                            color: '#475569',
                            background: '#f1f5f9',
                            border: '1px solid #cbd5e1',
                            borderRadius: 6,
                            padding: '4px 8px',
                            cursor: 'pointer',
                            lineHeight: 1,
                          }}
                          onMouseOver={(e) => { e.currentTarget.style.background = '#e2e8f0'; }}
                          onMouseOut={(e) => { e.currentTarget.style.background = '#f1f5f9'; }}
                        >
                          ▾ Collapse
                        </button>
                        <button
                          onClick={() => closeFilePreview(true)}
                          title={`Close preview — return to ${tabBeforePreview === 'file' ? 'list' : tabBeforePreview} tab`}
                          style={{
                            fontSize: 10,
                            fontWeight: 600,
                            color: '#fff',
                            background: '#2563eb',
                            border: '1px solid #2563eb',
                            borderRadius: 6,
                            padding: '4px 8px',
                            cursor: 'pointer',
                            lineHeight: 1,
                          }}
                          onMouseOver={(e) => { e.currentTarget.style.background = '#1d4ed8'; }}
                          onMouseOut={(e) => { e.currentTarget.style.background = '#2563eb'; }}
                        >
                          ✕ Close
                        </button>
                      </div>
                    </div>
                    <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 4, display: 'flex', gap: 10 }}>
                      <span>{(previewFile.sizeBytes / 1024).toFixed(1)} KB</span>
                      <span>·</span>
                      <span style={{ fontFamily: 'monospace' }}>{previewFile.folder}</span>
                      <span>·</span>
                      <span>verified source</span>
                    </div>
                  </>
                ) : previewLoading ? (
                  <div style={{ fontSize: 13, color: '#64748b' }}>Loading…</div>
                ) : (
                  <div style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.5 }}>
                    Click any file bubble in the chat to preview it here.
                    Demo files include the STP procedure, work package,
                    incident report, and sensor anomaly stream.
                  </div>
                )}
              </div>

              {/* Preview body or quick-pick when nothing loaded */}
              {previewError && (
                <div style={{ padding: 12, fontSize: 12, color: '#dc2626', background: '#fef2f2', borderBottom: '1px solid #fecaca' }}>
                  {previewError}
                </div>
              )}

              {!previewFile && !previewLoading && !previewError && (
                <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 14 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>
                    Demo Files (click to preview)
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {DEMO_PREVIEW_FILES.filter((f) => {
                      // Collapse the demo-file picker to only the active demo
                      // mode's folder so the operator doesn't see STP docs
                      // when running Verizon (and vice versa). 'all' shows all.
                      if (demoMode === 'all') return true;
                      if (demoMode === 'verizon_far_edge')   return f.folder === 'verizon_far_edge';
                      if (demoMode === 'nuclear_operations' || demoMode === 'stp') return f.folder === 'nuclear_operations';
                      return true;
                    }).map((f) => (
                      <button
                        key={f.filename}
                        onClick={() => openFilePreview(f.folder, f.filename)}
                        style={{
                          textAlign: 'left',
                          padding: '8px 10px',
                          fontSize: 11,
                          fontFamily: 'monospace',
                          color: '#1e40af',
                          background: '#eff6ff',
                          border: '1px solid #bfdbfe',
                          borderRadius: 6,
                          cursor: 'pointer',
                        }}
                        onMouseOver={(e) => { e.currentTarget.style.background = '#dbeafe'; }}
                        onMouseOut={(e) => { e.currentTarget.style.background = '#eff6ff'; }}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {previewFile && (
                <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', overflowX: 'auto', minHeight: 0 }}>
                  <pre
                    style={{
                      margin: 0,
                      padding: 14,
                      fontFamily: "'JetBrains Mono', 'Consolas', monospace",
                      fontSize: 10,
                      lineHeight: 1.5,
                      color: '#0f172a',
                      whiteSpace: 'pre',
                      background: '#fafbfc',
                    }}
                  >
                    {previewFile.content}
                  </pre>
                </div>
              )}
            </>
          )}

          {rightTab === 'history' && (
            <>
              <div style={{ padding: '12px 14px', borderBottom: '1px solid #f8fafc' }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a' }}>
                  Audit Lineage
                </div>
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2 }}>
                  {lineage.length} round-trip{lineage.length === 1 ? '' : 's'} this session
                </div>
              </div>
              <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 10 }}>
                {lineage.length === 0 ? (
                  <div style={{ padding: 14, fontSize: 12, color: '#94a3b8', lineHeight: 1.6, fontStyle: 'italic' }}>
                    Ask any question and the full lineage — routing decision,
                    specialist agent, intent class, model used, tools called,
                    latency, and source — will appear here as a timestamped
                    audit trail.
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {[...lineage].reverse().map((e, idx) => {
                      const theme = ROUTED_AGENT_THEME[e.routing.agent as RoutedAgent]
                        ?? { bg: '#eef2ff', color: '#4338ca', label: e.routing.label || String(e.routing.agent), code: e.routing.code || '' };
                      const turnNo = lineage.length - idx;
                      return (
                        <div
                          key={e.id}
                          style={{
                            border: '1px solid #e2e8f0',
                            borderLeft: `3px solid ${theme.color}`,
                            borderRadius: 8,
                            padding: 10,
                            background: '#fff',
                          }}
                        >
                          <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginBottom: 6 }}>
                            <span style={{ fontSize: 10, fontWeight: 700, color: '#475569', fontFamily: 'monospace' }}>
                              #{turnNo} · {new Date(e.timestamp).toLocaleTimeString()}
                            </span>
                            <span
                              style={{
                                fontSize: 9, fontWeight: 700, padding: '2px 6px',
                                borderRadius: 4, background: theme.bg, color: theme.color,
                              }}
                            >
                              {theme.label}
                            </span>
                          </div>
                          <div style={{ fontSize: 11, color: '#0f172a', fontWeight: 600, marginBottom: 4 }}>
                            ❓ {e.prompt}
                          </div>
                          <div style={{ fontSize: 10, color: '#475569', lineHeight: 1.55, marginBottom: 6 }}>
                            {e.response.slice(0, 220)}{e.response.length >= 220 ? '…' : ''}
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, fontSize: 9, color: '#94a3b8' }}>
                            <span>intent: <strong style={{ color: '#475569' }}>{e.routing.intent}</strong></span>
                            <span>·</span>
                            <span>conf: <strong style={{ color: '#475569' }}>{(e.routing.confidence * 100).toFixed(0)}%</strong></span>
                            <span>·</span>
                            <span>{(e.durationMs / 1000).toFixed(2)}s</span>
                            <span>·</span>
                            <span>{e.source}</span>
                            {e.toolsCalled.length > 0 && (
                              <>
                                <span>·</span>
                                <span>tools: {e.toolsCalled.length}</span>
                              </>
                            )}
                            {e.reasoningSteps > 0 && (
                              <>
                                <span>·</span>
                                <span>steps: {e.reasoningSteps}</span>
                              </>
                            )}
                          </div>
                          {e.toolsCalled.length > 0 && (
                            <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                              {e.toolsCalled.map((t, i) => (
                                <span
                                  key={i}
                                  style={{
                                    fontSize: 9, padding: '1px 5px', borderRadius: 3,
                                    background: '#f1f5f9', color: '#475569', fontFamily: 'monospace',
                                  }}
                                >
                                  {t}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </>
          )}

          {rightTab === 'dvr' && (
            <GovernanceDvr
              sessionId={sessionId}
              messageId={dvrMessageId}
              agentName={agent.name}
              ctxAgentId={activeCtx?.agentId ?? selected}
            />
          )}
        </div>
      </div>

      {/* AgentCore deploy modal */}
      {deployOpen && (
        <div className="modal-overlay" onClick={() => (agentCoreStatus !== 'deploying' ? setDeployOpen(false) : null)}>
          <div className="modal" style={{ padding: 28, maxWidth: 560 }} onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
              <div>
                <h3 style={{ fontSize: 17, fontWeight: 700, color: '#0f172a' }}>Deploy Bedrock AgentCore</h3>
                <p style={{ fontSize: 13, color: '#64748b', marginTop: 6, lineHeight: 1.55 }}>
                  Packages this agent&rsquo;s Strands runtime to <span className="mono">bedrock-agentcore-control</span> so reasoning runs
                  in AWS with Claude Opus 4 instead of the local mock. Takes ~4 seconds.
                </p>
              </div>
              <button
                onClick={() => setDeployOpen(false)}
                disabled={agentCoreStatus === 'deploying'}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', fontSize: 22, padding: 0, lineHeight: 1 }}
              >×</button>
            </div>

            <div
              className="mono"
              style={{ fontSize: 11, color: '#64748b', background: '#f8fafc', padding: 10, borderRadius: 8, marginTop: 16, marginBottom: 20 }}
            >
              aws bedrock-agentcore-control create-agent-runtime<br />
              &nbsp;&nbsp;--agent-name apex-{selected}<br />
              &nbsp;&nbsp;--role-arn arn:aws:iam::&lt;ACCOUNT&gt;:role/AmazonBedrockAgentCoreSDKRuntime<br />
              &nbsp;&nbsp;--model us.anthropic.claude-opus-4-6-v1
            </div>

            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setDeployOpen(false)} disabled={agentCoreStatus === 'deploying'}>Cancel</button>
              <button
                className="btn btn-primary"
                onClick={deployAgentCore}
                disabled={agentCoreStatus === 'deploying' || agentCoreStatus === 'connected'}
              >
                {agentCoreStatus === 'deploying' ? 'Deploying…' :
                 agentCoreStatus === 'connected' ? 'Already connected' : 'Deploy'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/* ──────────────────────── AgentCore status pill ──────────────────────── */

function AgentCorePill({
  status, onDeploy,
}: {
  status: 'checking' | 'connected' | 'offline' | 'deploying';
  onDeploy: () => void;
}) {
  const common: React.CSSProperties = {
    display: 'inline-flex', alignItems: 'center', gap: 6,
    fontSize: 11, fontWeight: 600, padding: '5px 10px', borderRadius: 999,
    border: '1px solid transparent',
  };

  if (status === 'connected') {
    return (
      <span style={{ ...common, background: '#f0fdf4', color: '#166534', borderColor: '#bbf7d0' }} title="Reasoning via Bedrock AgentCore · Claude Opus 4">
        <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 0 4px #bbf7d0' }} />
        AgentCore · Connected
      </span>
    );
  }
  if (status === 'deploying') {
    return (
      <span style={{ ...common, background: '#fff7ed', color: '#9a3412', borderColor: '#fed7aa' }}>
        <span className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: '#f97316' }} />
        AgentCore · Deploying…
      </span>
    );
  }
  if (status === 'checking') {
    return (
      <span style={{ ...common, background: '#f1f5f9', color: '#475569', borderColor: '#e2e8f0' }}>
        <span className="animate-pulse" style={{ width: 8, height: 8, borderRadius: '50%', background: '#94a3b8' }} />
        AgentCore · Checking…
      </span>
    );
  }
  // offline
  return (
    <button
      type="button"
      onClick={onDeploy}
      style={{ ...common, background: '#fef2f2', color: '#b91c1c', borderColor: '#fecaca', cursor: 'pointer' }}
      title="AgentCore runtime not reachable. Click to deploy."
    >
      <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#dc2626' }} />
      Deploy AgentCore
    </button>
  );
}

/* ──────────────────────── review-hand-off renderer ──────────────────────── */

function renderReviewHandoff(e: ReviewFeedEntry): React.ReactNode {
  const icon = e.decision === 'approved' ? '✓'
             : e.decision === 'rejected' ? '✕'
             : '↑';
  const tone = e.decision === 'approved' ? '#16a34a'
             : e.decision === 'rejected' ? '#dc2626'
             : '#d97706';
  const label = e.decision === 'approved' ? 'approved'
              : e.decision === 'rejected' ? 'rejected'
              : 'escalated';
  const when = new Date(e.decided_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return (
    <div style={{ fontSize: 13, color: '#0f172a', lineHeight: 1.55 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4, color: tone, fontWeight: 600 }}>
        <span style={{ fontSize: 14 }}>{icon}</span>
        <span>{e.decided_by} {label} <span className="mono">{e.id}</span> at {when}</span>
      </div>
      <div style={{ fontSize: 12, color: '#475569', marginBottom: 4 }}>
        <strong>{e.title}</strong>
      </div>
      <div style={{ fontSize: 12, color: '#0f172a' }}>
        Next step: <span className="mono">{e.next_step}</span>
      </div>
      {e.comment && (
        <div style={{ fontSize: 12, color: '#475569', marginTop: 6, fontStyle: 'italic' }}>
          &ldquo;{e.comment}&rdquo;
        </div>
      )}
    </div>
  );
}

/* ──────────────────────── initial messages builder ──────────────────────── */

/* ───────────────── Dynamic Context-tab payload ─────────────────
 *
 * The Context tab on the right used to render a hardcoded "WI-3200 ·
 * Globex Invoice" card whenever there was no Apex-Lens-supplied ctx.
 * That meant a user chatting with PolicyAgent in STP demo mode saw
 * unrelated AP invoice content — confusing during demos.
 *
 * computeContextView() picks the most-specific signal available and
 * builds a fresh ContextView from it. The `activeCtx` from Apex Lens
 * still wins. Below that, the function leans on the active preview
 * file, the last lineage entry, then the selected agent's domain.
 * If nothing is available, it returns an empty-state hint — never the
 * hardcoded invoice.
 */
interface ContextFact { label: string; value: string; }
interface ContextAction { href: string; label: string; }
interface ContextView {
  title: string;
  subtitle?: string;
  chipClass: string;
  chipLabel: string;
  flags: Flag[];
  flagsLabel: string;
  routing?: string;
  facts: ContextFact[];
  factsLabel?: string;
  primaryAction?: ContextAction;
  secondaryAction?: ContextAction;
}

function computeContextView(input: {
  activeCtx: DocContext | null;
  previewFile: { name: string; folder: string; sizeBytes: number; content: string } | null;
  lineage: LineageEntry[];
  agentId: string;
  agentName: string;
  demoMode: string;
}): ContextView {
  const { activeCtx, previewFile, lineage, agentId, agentName, demoMode } = input;

  // Priority 1: Apex Lens supplied a doc context — render that verbatim.
  if (activeCtx) {
    return {
      title: activeCtx.name,
      chipClass: activeCtx.typeChip,
      chipLabel: activeCtx.type,
      flags: activeCtx.flags,
      flagsLabel: 'Validation',
      routing: activeCtx.routing,
      facts: [],
      primaryAction: { href: '/review', label: 'Review & Decide' },
      secondaryAction: { href: '/apex-lens', label: 'Back to ApexLens' },
    };
  }

  // Priority 2: User clicked a demo file in the File tab — surface its
  // metadata as the active context.
  if (previewFile) {
    const sizeKb = (previewFile.sizeBytes / 1024).toFixed(1);
    const lineCount = previewFile.content.split('\n').length;
    return {
      title: previewFile.name,
      subtitle: `Loaded from ${previewFile.folder} · ${sizeKb} KB · ~${lineCount} lines`,
      chipClass: 'chip-blue',
      chipLabel: 'Demo Document · Verified Source',
      flags: [
        { color: 'green', text: 'Source document loaded with content hash for audit trail' },
        { color: 'green', text: 'Verbatim citation available — agent quotes preserve line numbers' },
        { color: 'green', text: 'Document indexed; ask the agent any question grounded in this file' },
      ],
      flagsLabel: 'Source Status',
      routing: `Indexed → ${agentName} · ready for verbatim Q&A`,
      facts: [
        { label: 'Folder', value: previewFile.folder },
        { label: 'Size', value: `${sizeKb} KB` },
        { label: 'Lines', value: String(lineCount) },
      ],
      factsLabel: 'File Metadata',
    };
  }

  // Priority 3: Lineage exists — show the most recent round-trip's
  // routing decision + key signals so the audience always sees an
  // up-to-date snapshot of "what just happened."
  if (lineage.length > 0) {
    const last = lineage[lineage.length - 1];
    const theme = ROUTED_AGENT_THEME[last.routing.agent as RoutedAgent]
      ?? { bg: '#eef2ff', color: '#4338ca', label: last.routing.label || String(last.routing.agent), code: last.routing.code || '' };
    return {
      title: `Last query → ${theme.label}`,
      subtitle: new Date(last.timestamp).toLocaleTimeString(),
      chipClass: 'chip-blue',
      chipLabel: `Intent · ${last.routing.intent}`,
      flags: [
        { color: 'green', text: `"${last.prompt.slice(0, 90)}${last.prompt.length > 90 ? '…' : ''}"` },
        { color: last.routing.confidence > 0.85 ? 'green' : 'amber', text: `Confidence: ${(last.routing.confidence * 100).toFixed(0)}% · ${last.routing.rationale}` },
        { color: last.source === 'agentcore' ? 'green' : 'amber', text: `Served by: ${last.source}` },
      ],
      flagsLabel: 'Last Round-Trip',
      routing: `Routed to ${theme.label} (${last.routing.intent}) · ${(last.durationMs / 1000).toFixed(2)}s`,
      facts: [
        { label: 'Turns this session', value: String(lineage.length) },
        { label: 'Tools called',       value: last.toolsCalled.length ? last.toolsCalled.join(', ') : '—' },
        { label: 'Reasoning steps',    value: String(last.reasoningSteps) },
      ],
      factsLabel: 'Telemetry',
      primaryAction: { href: '/review', label: 'Open Human Review Queue' },
    };
  }

  // Priority 4: Per-agent default — describe what the selected agent does
  // and what data sources it can reach. This is what the user sees on a
  // fresh chat with no questions asked yet.
  const agentDefaults: Record<string, ContextView> = {
    chatstp: {
      title: 'ChatSTP — Unified Router',
      subtitle: 'One chat, four specialists. Click a quick-reply to start.',
      chipClass: 'chip-blue',
      chipLabel: 'ROUTER · STP Phase 2',
      flags: [
        { color: 'green', text: 'Classifies your intent and delegates to the right specialist' },
        { color: 'green', text: 'Carries equipment context across follow-up turns' },
        { color: 'green', text: 'Every routing decision shown in the History tab' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Will delegate to PolicyAgent · MaintenanceAgent · DiagnosticsAgent · ReliabilityAgent',
      facts: [
        { label: 'Delegates to',  value: '4 specialists' },
        { label: 'Context model', value: '12-turn rolling history' },
        { label: 'Cost strategy', value: 'Haiku for classify · Sonnet/Opus for synthesis' },
      ],
      factsLabel: 'Profile',
    },
    'policy-agent': {
      title: 'PolicyAgent — Verbatim Citations',
      subtitle: 'Search the STP procedure & policy corpus with provenance.',
      chipClass: 'chip-blue',
      chipLabel: 'UC-1 · Policy Lookup',
      flags: [
        { color: 'green', text: 'Returns verbatim quotes — never paraphrases' },
        { color: 'green', text: 'Cites doc-number, section, and effective date' },
        { color: 'green', text: 'Refuses to answer when source is missing (no hallucinations)' },
      ],
      flagsLabel: 'Guarantees',
      routing: 'Sources: STP procedures (STP-OP-*, STP-MNT-*, STP-415, STP-RAD-*)',
      facts: [
        { label: 'Corpus',           value: 'STP procedure library' },
        { label: 'Citation format',  value: 'doc-number § section (effective date)' },
        { label: 'Confidence floor', value: '0.85 — below routes to human reviewer' },
      ],
      factsLabel: 'Profile',
    },
    'maintenance-agent': {
      title: 'MaintenanceAgent — PM History',
      subtitle: 'Equipment work-order history with engineer attribution.',
      chipClass: 'chip-green',
      chipLabel: 'UC-2 · Equipment PM',
      flags: [
        { color: 'green', text: 'Pulls work-order metadata from Oracle eAM mirror' },
        { color: 'green', text: 'Shows engineer attribution + LOTO sign-offs' },
        { color: 'green', text: 'Cross-references work packages by equipment tag' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Sources: Oracle PMHISTORY · scanned work-package PDFs · eAM mirror',
      facts: [
        { label: 'Equipment tagged', value: 'P-3A, P-3B, P-3C and others' },
        { label: 'Compliance',       value: 'OSHA 1910.147 LOTO verification surfaced per WO' },
      ],
      factsLabel: 'Profile',
    },
    'diagnostics-agent': {
      title: 'DiagnosticsAgent — Failure-Mode Aggregation',
      subtitle: 'Pattern detection across the work-package corpus.',
      chipClass: 'chip-amber',
      chipLabel: 'UC-3 · Diagnostics',
      flags: [
        { color: 'green', text: 'Aggregates failure modes by frequency, lead time, mitigation' },
        { color: 'green', text: 'Cites the actual WOs that established the pattern' },
        { color: 'green', text: 'Flags recurrence across sister equipment' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Sources: Condition Reports · Corrective Action Records · scanned WO corpus',
      facts: [
        { label: 'Indexed events', value: '12+ failure events across RCS pumps' },
        { label: 'Top failure',    value: 'Vibration above limit (axial) · 33% of events' },
      ],
      factsLabel: 'Profile',
    },
    'reliability-agent': {
      title: 'ReliabilityAgent — Predictive Maintenance',
      subtitle: 'RUL forecast + failure-mode classification + PM advance.',
      chipClass: 'chip-red',
      chipLabel: 'UC-4 · Predictive',
      flags: [
        { color: 'green', text: 'Bayesian survival model trained on STP failure history' },
        { color: 'green', text: 'P10 / P50 / P90 confidence bands on RUL forecast' },
        { color: 'amber', text: 'PM advance recommendations always go to 4-of-4 human approval' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Sources: Bently Nevada 3500 · OSI PI Historian · Oracle PMHISTORY',
      facts: [
        { label: 'Model',          value: 'Bayesian survival · Gamma prior' },
        { label: 'Cross-validation', value: 'MAE 4.7 days · RMSE 6.8 days' },
        { label: 'Approval needed', value: '4-of-4 (Maint Mgr · Ops Mgr · Plant Mgr · Component Eng)' },
      ],
      factsLabel: 'Profile',
    },

    // ─── CWFCU agents — right-rail Context tab defaults ───
    'cwfcu-onboarding-agent': {
      title: 'Member Onboarding Agent — CIP & OFAC',
      subtitle: 'Front door for every new member · feeds risk into Compliance.',
      chipClass: 'chip-green',
      chipLabel: 'CW FCU · CIP · OFAC',
      flags: [
        { color: 'green', text: 'Verifies ID, screens OFAC + PEP, validates address' },
        { color: 'green', text: 'Generates exam-ready CIP record on every approval' },
        { color: 'amber', text: 'High-risk profiles trigger enhanced monitoring downstream' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Sends risk scores to Compliance Agent · Feeds CIP records into NCUA exam folder',
      facts: [
        { label: 'New members 30d',  value: '204 onboarded' },
        { label: 'OFAC coverage',    value: '100%' },
        { label: 'CIP exam folder',  value: '100% complete' },
      ],
      factsLabel: 'Profile',
    },
    'cwfcu-compliance-agent': {
      title: 'Compliance Agent — BSA/AML · SAR · NCUA',
      subtitle: 'Continuously updated exam folder. SAR narratives, CTRs, CDD reviews.',
      chipClass: 'chip-purple',
      chipLabel: 'CW FCU · BSA/AML · NCUA',
      flags: [
        { color: 'green', text: 'Drafts FinCEN-compliant SAR narratives (96.1% accuracy)' },
        { color: 'green', text: 'Auto-files CTRs within the 15-day window' },
        { color: 'green', text: 'Maintains the NCUA exam BSA/AML folder in real time' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Receives risk scores from Onboarding · Sends loan-risk flags to Loan Document Agent · Feeds BSA training reqs to Policy & HR',
      facts: [
        { label: 'SARs indexed',     value: '142 this month' },
        { label: 'CDD records',      value: '68,889 members' },
        { label: 'Exam folder',      value: '87% complete' },
        { label: 'Exam in',          value: '47 days' },
      ],
      factsLabel: 'Profile',
    },
    'cwfcu-loan-agent': {
      title: 'Loan Document Agent — Packets & Underwriting',
      subtitle: 'Auto / HELOC / Mortgage / Personal · missing-doc routing.',
      chipClass: 'chip-blue',
      chipLabel: 'CW FCU · Lending',
      flags: [
        { color: 'green', text: 'Extracts every field from the loan packet (93.8% accuracy)' },
        { color: 'green', text: 'Validates income docs + flags missing items with specific checklist' },
        { color: 'amber', text: 'High-risk member packets get enhanced verification checklist' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Receives risk flags from Compliance · Feeds credit-risk folder into NCUA exam · Triggers vendor engagement (appraiser/title)',
      facts: [
        { label: 'Loan packets 30d', value: '318 processed' },
        { label: 'Straight-through', value: '93.8%' },
        { label: 'Avg doc → decision', value: '1.4 days (was 6.2)' },
      ],
      factsLabel: 'Profile',
    },
    'cwfcu-vendor-agent': {
      title: 'Vendor & Contract Agent — Third-Party Risk',
      subtitle: '47 active vendor contracts · SLA · renewals · price drift.',
      chipClass: 'chip-amber',
      chipLabel: 'CW FCU · Vendor Risk',
      flags: [
        { color: 'amber', text: 'Fiserv core banking auto-renewal deadline TODAY' },
        { color: 'green', text: 'Monitors every contract for expiry, SLA breach, rate drift' },
        { color: 'green', text: 'Assembles third-party risk dossier on every vendor automatically' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Receives loan-triggered vendors (appraiser, title, insurance) · Sends policy obligations to Policy & HR',
      facts: [
        { label: 'Active contracts', value: '47 monitored' },
        { label: 'Renewals 30d',     value: '3 due' },
        { label: 'Critical alerts',  value: 'Fiserv · TODAY' },
      ],
      factsLabel: 'Profile',
    },
    'cwfcu-policy-agent': {
      title: 'Policy & HR Agent — The Closer',
      subtitle: 'Policy acks + training + board docs across 84 employees.',
      chipClass: 'chip-red',
      chipLabel: 'CW FCU · HR / Policy',
      flags: [
        { color: 'green', text: 'Tracks every policy acknowledgment + sends automated reminders' },
        { color: 'amber', text: '22 of 84 employees overdue on BSA/AML training' },
        { color: 'green', text: 'Maintains the HR/Policy section of the NCUA exam folder' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Receives policy obligations from Vendor Agent + BSA training reqs from Compliance · Closes the NCUA exam folder',
      facts: [
        { label: 'Employees tracked', value: '84' },
        { label: 'BSA training',      value: '74% complete (62/84)' },
        { label: 'Ack rate',          value: '98.8%' },
      ],
      factsLabel: 'Profile',
    },

    // ─── Boler agents — right-rail Context tab defaults ───
    'boler-benefits-agent': {
      title: 'Benefits Allocation Agent — Carrier Extract & Reclassification',
      subtitle: 'Extracts 6 carrier files · reclassifies 847 employees across 5 divisions.',
      chipClass: 'chip-purple',
      chipLabel: 'Boler · Benefits',
      flags: [
        { color: 'green', text: 'Extracts every field via Lambda + Amazon Bedrock' },
        { color: 'green', text: 'Detects wrong-division coding, duplicate enrollments, terminated-but-active' },
        { color: 'amber', text: '3.5 days manual baseline → 4.2 hrs automated (-95%)' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Sends exceptions to Exception Resolution Agent · Feeds JE Agent on approval · Logs every decision to DynamoDB',
      facts: [
        { label: 'Employees covered', value: '847' },
        { label: 'Carrier files',     value: '6 (Cigna, Delta, Fidelity, VSP, Hartford, Cigna STD/LTD)' },
        { label: 'Accuracy',          value: '96.1%' },
        { label: 'Processing time',   value: '4.2 hrs (was 3.5 days)' },
      ],
      factsLabel: 'Profile',
    },
    'boler-exception-agent': {
      title: 'Exception Resolution Agent — HITL Decision Surface',
      subtitle: 'Routes exceptions through 2-stage approval via Step Functions.',
      chipClass: 'chip-red',
      chipLabel: 'Boler · HITL',
      flags: [
        { color: 'red',   text: '2 HIGH exceptions awaiting CFO sign-off ($5,080/mo variance)' },
        { color: 'green', text: 'Auto-fixes division-transfer + terminated-employee exceptions' },
        { color: 'green', text: 'Step Functions orchestration · SLA enforcement · SES + SNS notifications' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Receives from Benefits Agent · Routes to Sarah Mitchell (Benefits Dir) Stage 1 → Ziggy Kravitz (CFO) Stage 2',
      facts: [
        { label: 'Exceptions in queue', value: '7 (2 HIGH · 3 MEDIUM · 2 LOW)' },
        { label: 'Variance flagged',    value: '$28,120' },
        { label: 'Auto-fix rate',       value: '29% (2 of 7 this cycle)' },
        { label: 'Accuracy',            value: '98.2%' },
      ],
      factsLabel: 'Profile',
    },
    'boler-je-agent': {
      title: 'Journal Entry Agent — Division JE Generation',
      subtitle: '5 division journal entries · GL-coded · ready for distribution.',
      chipClass: 'chip-green',
      chipLabel: 'Boler · GL Posting',
      flags: [
        { color: 'green', text: 'Auto-generates GL-coded JEs for all 5 divisions' },
        { color: 'green', text: 'Validates DR/CR balance before distribution' },
        { color: 'green', text: 'Distributes to controller via S3 · audit-logged to DynamoDB' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Receives approved allocations from Exception Agent · Sends final JEs via S3 + SES to division controllers',
      facts: [
        { label: 'JEs generated',     value: '5 divisions' },
        { label: 'Cost-center range', value: '6200-001 through 6200-005' },
        { label: 'Accuracy',          value: '99.1%' },
        { label: 'HITL queue',        value: '0' },
      ],
      factsLabel: 'Profile',
    },
    'boler-signal-agent': {
      title: 'Signal Agent — Predictive Benefits Intelligence',
      subtitle: 'Rate drift · budget forecasts · open-enrollment projections.',
      chipClass: 'chip-amber',
      chipLabel: 'Boler · Signal',
      flags: [
        { color: 'red',   text: 'Cigna rate drift +4.1% vs contract · renewal in 41 days' },
        { color: 'amber', text: '401k match rate mismatch · $8,240 delta · Fidelity 4.5% vs HR 4.0%' },
        { color: 'green', text: 'Open Enrollment impact forecast: net -$22K/yr projected savings' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Pulls from carrier rate cards + HRIS + DynamoDB · Sends alerts to Exception Agent + CFO via SNS',
      facts: [
        { label: 'Active signals',    value: '4' },
        { label: 'Variance caught',   value: '$28,120' },
        { label: 'Forecast horizon',  value: '12 months' },
        { label: 'Model confidence',  value: '89%' },
      ],
      factsLabel: 'Profile',
    },
    'boler-audit-agent': {
      title: 'Audit Lens Agent — Governance & Lineage',
      subtitle: 'DynamoDB immutable log · 100% decision coverage.',
      chipClass: 'chip-blue',
      chipLabel: 'Boler · Audit',
      flags: [
        { color: 'green', text: 'Every allocation, reclassification, and approval logged to DynamoDB' },
        { color: 'green', text: '100% decision coverage · SOC 2 audit-ready' },
        { color: 'green', text: 'Lineage graph from carrier file → JE → division controller' },
      ],
      flagsLabel: 'Capabilities',
      routing: 'Subscribes to every agent · Indexes to DynamoDB audit ledger · Surfaces to AuditLens tab',
      facts: [
        { label: 'Records logged',    value: '847 employees · 6 files · 3 stages · 7 exceptions' },
        { label: 'Coverage',          value: '100%' },
        { label: 'Storage',           value: 'Amazon DynamoDB · KMS encrypted' },
      ],
      factsLabel: 'Profile',
    },
  };

  const def = agentDefaults[agentId];
  if (def) return def;

  // Priority 5: True empty state — user is on a generic / non-STP agent
  // with no context yet. No more invoice fallback.
  return {
    title: agentName,
    subtitle: `Demo mode: ${demoMode}`,
    chipClass: 'chip-gray',
    chipLabel: 'Ready',
    flags: [
      { color: 'green', text: 'Ask a question or click a quick-reply chip below the chat' },
      { color: 'green', text: 'Drop a file from Apex Lens to load it as conversation context' },
    ],
    flagsLabel: 'How to start',
    facts: [],
  };
}

/** Heuristic: map a DocContext or chat-bubble file name to the demo
 *  file under synthetic-data so the right-panel preview can find it.
 *  Returns null if no match — the file card stays non-clickable.
 *  Drop new entries here when you add a new demo doc. */
function lookupDemoFileForContext(ctx: DocContext | null, agentId?: string): { folder: string; filename: string } | null {
  if (!ctx && !agentId) return null;
  const name = (ctx?.name || '').toLowerCase();
  const aid = (agentId || ctx?.agentId || '').toLowerCase();

  // Filename / context-name signatures
  if (name.includes('stp-415') || name.includes('policy') || name.includes('procedure'))
    return { folder: 'nuclear_operations', filename: 'STP-OP-2204_RCS_Surveillance_Rev6.txt' };
  if (name.includes('wo-') || name.includes('work package') || name.includes('pm history'))
    return { folder: 'nuclear_operations', filename: 'WO-2026-00871_PUMP-RCP-1A_Work_Package.txt' };
  if (name.includes('cr-') || name.includes('incident') || name.includes('seizure'))
    return { folder: 'nuclear_operations', filename: 'CR-2026-0188_PUMP-CCW-1A_Bearing_Seizure_Incident.txt' };
  if (name.includes('sensor') || name.includes('anomaly') || name.includes('rul'))
    return { folder: 'nuclear_operations', filename: 'SENSOR-PUMP-CCW-1A_Anomaly_Stream_2026-05.txt' };

  // Agent-id fallback — open the most-likely doc for each STP specialist
  if (aid.includes('policy'))      return { folder: 'nuclear_operations', filename: 'STP-OP-2204_RCS_Surveillance_Rev6.txt' };
  if (aid.includes('maintenance')) return { folder: 'nuclear_operations', filename: 'WO-2026-00871_PUMP-RCP-1A_Work_Package.txt' };
  if (aid.includes('diagnostics')) return { folder: 'nuclear_operations', filename: 'CR-2026-0188_PUMP-CCW-1A_Bearing_Seizure_Incident.txt' };
  if (aid.includes('reliability')) return { folder: 'nuclear_operations', filename: 'SENSOR-PUMP-CCW-1A_Anomaly_Stream_2026-05.txt' };

  // Verizon Far Edge — agent-id heuristics → most-relevant runbook excerpt
  if (aid.includes('certification')) return { folder: 'verizon_far_edge', filename: 'VZ-RUNBOOK-CAAS-v24-excerpt.txt' };
  if (aid.includes('schemawatch'))   return { folder: 'verizon_far_edge', filename: 'WindRiver-24.12-ReleaseNotes-excerpt.txt' };
  if (aid.includes('upgrade'))       return { folder: 'verizon_far_edge', filename: 'VZ-Upgrade-Procedures-2026-excerpt.txt' };
  if (aid.includes('mentor'))        return { folder: 'verizon_far_edge', filename: 'VZ-KB-Known-Issues-excerpt.txt' };

  return null;
}

function buildInitialMessages(
  agent: UIAgent,
  ctx: DocContext | null,
  onFileClick?: () => void,
): ChatMessage[] {
  if (!ctx) {
    // Per-agent intro message — keyed off the agent id so each agent
    // introduces itself with its actual capabilities (not "your AI invoice
    // processing agent" by default).
    const introByAgent = AGENT_INTROS[agent.id] ?? AGENT_INTROS_DEFAULT(agent.name);
    return [
      {
        id: 'intro',
        who: 'agent',
        time: `${agent.name} · just now`,
        content: introByAgent,
      },
    ];
  }

  // Document context mode: file bubble + analysis + follow-up prompt.
  return [
    {
      id: 'file',
      who: 'file',
      time: 'You · uploaded from ApexLens',
      content: (
        <FileCardContent
          name={ctx.name}
          type={ctx.type}
          chip={ctx.typeChip}
          size={ctx.fileSize}
          onClick={onFileClick}
        />
      ),
    },
    {
      id: 'analysis',
      who: 'agent',
      time: `${agent.name} · just now`,
      content: (
        <>
          <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 10 }}>{ctx.analysis}</p>
          <div style={{ background: '#fff', borderRadius: 10, padding: 12, marginBottom: 8 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {ctx.flags.map((f, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                  <span className={`dot-${f.color}`} style={{ marginTop: 5, flexShrink: 0 }} />
                  <span style={{ fontSize: 13, color: '#374151' }}>{f.text}</span>
                </div>
              ))}
            </div>
          </div>
          <p style={{ fontSize: 12, color: '#64748b' }}>{ctx.routing}</p>
        </>
      ),
    },
    {
      id: 'follow',
      who: 'agent',
      time: `${agent.name} · just now`,
      content: <p style={{ fontSize: 14, color: '#0f172a' }}>{ctx.followUp}</p>,
    },
  ];
}

/* ──────────────────────── per-agent intros (no-doc-context) ────────────────────────
 *
 * When the user opens Agent Hub directly (no ?doc= or sample drop), each agent
 * gets its own intro so the chat opens with content that matches the agent's
 * actual capabilities. Keyed by agent id.
 *
 * Adding a new agent? Add a key here. The default fallback is intentionally
 * generic so unmapped agents still render something sane.
 */
const AGENT_INTROS_DEFAULT = (name: string): React.ReactNode => (
  <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 8 }}>
    Hello! I'm <strong>{name}</strong>. Ask me anything about my domain and I'll do my best.
  </p>
);

const AGENT_INTROS: Record<string, React.ReactNode> = {
  // ── Agentic Enterprise (66 Degrees vendor-neutral demos) ──
  'orchestrator-agent': (
    <>
      <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 8 }}>
        I'm <strong>OrchestratorAgent</strong>, the supply-chain orchestrator. Tell me about a stockout or campaign shortage and I'll:
      </p>
      <ul style={{ fontSize: 13, color: '#374151', marginLeft: 16, lineHeight: 1.7 }}>
        <li>Check inventory across all warehouses</li>
        <li>Rank approved suppliers by lead time, on-time %, and defect rate</li>
        <li>Draft a purchase order with line items and INCOTERMS</li>
        <li>Route the PO to a human approver — never auto-submit</li>
      </ul>
      <p style={{ fontSize: 12, color: '#64748b', marginTop: 10 }}>
        Try: <em>"We are short 500 units of SKU-892 for the Dallas promotion. Resolve this."</em>
      </p>
    </>
  ),
  'concierge-agent': (
    <>
      <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 8 }}>
        Welcome to Coral Star Cruises — I'm <strong>ConciergeAgent</strong>. I can help with:
      </p>
      <ul style={{ fontSize: 13, color: '#374151', marginLeft: 16, lineHeight: 1.7 }}>
        <li>Booking modifications (date changes, cabin upgrades)</li>
        <li>Onboard policies (pool hours, dining, gratuities, Wi-Fi)</li>
        <li>Cancellation and refund tiers</li>
        <li>Connecting you with a human guest-services specialist</li>
      </ul>
      <p style={{ fontSize: 12, color: '#64748b', marginTop: 10 }}>
        Try: <em>"What are the pool hours?"</em> or <em>"I'd like to change my sail date to June 28."</em>
      </p>
    </>
  ),
  'lease-agent': (
    <>
      <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 8 }}>
        I'm <strong>LeaseAgent</strong>. Drop a commercial lease or ask me to extract one and I'll:
      </p>
      <ul style={{ fontSize: 13, color: '#374151', marginLeft: 16, lineHeight: 1.7 }}>
        <li>Pull the tenant name, expiration date, and liability clause</li>
        <li>Score per-field confidence and flag low-confidence extractions</li>
        <li>Index the structured row into the DuckDB <code>leases</code> table</li>
        <li>Run SQL queries against the table on demand</li>
      </ul>
      <p style={{ fontSize: 12, color: '#64748b', marginTop: 10 }}>
        Try: <em>"Extract this lease."</em> Then: <em>"SELECT tenant_name, expiration_date FROM leases WHERE liability_clause LIKE '%indemnify%'"</em>
      </p>
    </>
  ),

};

const DEFAULT_FLAGS: Flag[] = [
  { color: 'amber', text: 'Amount $87,400 exceeds auto-approval threshold of $10,000' },
  { color: 'amber', text: 'PO reference PO-2024-0891 not found in ERP' },
  { color: 'green', text: 'Vendor verified on approved list' },
  { color: 'green', text: 'No duplicate invoice found' },
];

/* ──────────────────────── keyword-based mock responses (spec §7) ──────────────────────── */

function getMockResponse(input: string, ctx: DocContext | null): React.ReactNode {
  const q = input.toLowerCase();

  /* ───── CBB Demo 1 (CustomerOps / Order Mod) ───── */
  if (ctx?.agentId === 'customerops') {
    if (q.includes('dimension') || q.includes('original') || q.includes('new')) {
      return (
        <>
          <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 8 }}>
            <strong>Original:</strong> Width 48&quot; × Height 60&quot;<br />
            <strong>Requested:</strong> Width 48&quot; × Height 62&quot;<br />
            <strong>Delta:</strong> +2&quot; height (+3.3%)
          </p>
          <p style={{ fontSize: 13, color: '#374151', lineHeight: 1.55 }}>
            This falls within the acceptable variance for the <span className="mono">CCW-4860-LG</span> product line.
            No structural re-engineering required. Production can proceed as scheduled on <strong>April 28</strong>.
          </p>
        </>
      );
    }
    if (q.includes('outside') || q.includes('tolerance') || q.includes('exceed')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          If the variance exceeded <strong>5%</strong>, I would automatically route the request to the Human Review queue
          and flag it for your engineering team. The distributor would receive an automated acknowledgment stating
          that their request is under review, with an estimated response time of <strong>4 business hours</strong>.
        </p>
      );
    }
    if (q.includes('distributor') || q.includes('midwest') || q.includes('history')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          <strong>Midwest Window &amp; Door Supply</strong> (DIST-4421) — Gold Partner since 2019.
          127 orders in the last 12 months, $4.2M revenue, 2.1 day avg lead-time responsiveness.
          Zero late-payment incidents. Primary contact: Sam Torres, <span className="mono">orders@midwestwindow.com</span>.
        </p>
      );
    }
    if (q.includes('crm') || q.includes('dynamics')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          CBB-ORD-1044 in Microsoft Dynamics CRM has been updated:<br />
          · Product dimensions: 48&quot; × 62&quot; (was 48&quot; × 60&quot;)<br />
          · Lead time: 16 days (was 14)<br />
          · Status: Scheduled for Apr 28, 2026<br />
          · Change history entry logged at 08:42:17 AM by <span className="mono">apex.customerops</span>.
        </p>
      );
    }
  }

  /* ───── CBB Demo 2 (QC Agent / QC Batch) ───── */
  if (ctx?.agentId === 'qcbot') {
    if (q.includes('financial') || q.includes('impact') || q.includes('value')) {
      return (
        <>
          <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 8 }}>
            <strong>LOT-A44:</strong> 2,400 kg quarantined · Estimated value <strong>$18,600</strong><br />
            <strong>LOT-B12:</strong> 1,800 kg quarantined · Estimated value <strong>$13,950</strong><br />
            <strong>Total quarantined value:</strong> $32,550
          </p>
          <p style={{ fontSize: 13, color: '#374151', lineHeight: 1.55 }}>
            Production impact: minimal. Ohio Plant 7 has <strong>6 days</strong> of buffer stock remaining.
            Recommended action: issue supplier corrective action request to Apex Vinyl Solutions within 24 hours.
          </p>
        </>
      );
    }
    if (q.includes('alert') || q.includes('who') || q.includes('notified')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          Two notifications were sent automatically:<br />
          1. <strong>Sarah Jenkins</strong> (Plant Manager, Ohio Plant 7) via Microsoft Teams at 06:15:42 AM<br />
          2. <span className="mono">procurement@cbb.com</span> via email at 06:15:43 AM<br />
          Both notifications included the lot IDs, failure reasons, and ERP hold numbers.
        </p>
      );
    }
    if (q.includes('corrective') || q.includes('supplier') || q.includes('apex vinyl')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          Draft sent to your review queue. Key points: tensile-strength + color variance failures,
          both traceable to batches shipped Apr 18–19. Requesting: (a) root-cause analysis within 72h,
          (b) replacement shipment within 10 business days, (c) re-inspection by third-party QA for the next 3 batches.
        </p>
      );
    }
    if (q.includes('tolerance') || q.includes('report')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          Full tolerance report is attached to the work item. Highlights: LOT-A44 tensile strength 47.3 MPa
          (min 49.2 MPa, 3.8% below); LOT-B12 delta-E 2.4 (threshold 2.0). 48 passing lots show mean tensile
          51.7 MPa and mean delta-E 1.2 — well within spec.
        </p>
      );
    }
  }

  /* ───── CBB Demo 3 (Logistics Agent / Port Strike) ───── */
  if (ctx?.agentId === 'logisticsbot') {
    if (q.includes('option') || q.includes('rerout')) {
      return (
        <>
          <p style={{ fontSize: 14, color: '#0f172a', marginBottom: 10 }}>
            I&apos;ve identified <strong>3 options</strong> ranked by recommendation:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <OptionBox
              tag="OPTION A — PREFERRED"
              tagColor="#15803d"
              body="Reroute from Oxy Vinyls LP · Cost delta +5% · Delay 0 days · Capacity available. This is the recommended path. Oxy Vinyls can fulfill the full volume within 48 hours."
            />
            <OptionBox
              tag="OPTION B — FALLBACK"
              tagColor="#b45309"
              body="Resequence production at Georgia Plant 31 · Cost delta $0 · Delay 2 days · No new supplier required. Shifts production schedule to use existing buffer stock at Plant 31."
            />
            <OptionBox
              tag="OPTION C — LAST RESORT"
              tagColor="#b91c1c"
              body="Emergency air freight from Formosa Plastics · Cost delta +22% · Delay 0 days. Only recommended if Options A and B are unavailable."
            />
          </div>
        </>
      );
    }
    if ((q.includes('approve') && q.includes('option a')) || q.includes('option a')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          <strong>Option A approved.</strong> Rerouting order placed with Oxy Vinyls LP. Supply Chain Director
          <strong> Marcus Webb</strong> notified via email and Teams. Updated production schedules sent to
          Ohio Plant 7, Texas Plant 14, and Georgia Plant 31.<br /><br />
          <strong>Estimated cost impact:</strong> +$54,500 (5% of $1.09M at risk). <strong>Avoided delay:</strong> 7 days.
        </p>
      );
    }
    if (q.includes('bom') || q.includes('impact') || q.includes('tree')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          BOM traversal found 847 downstream nodes. Finished goods touched: Commercial Casement Windows,
          Vinyl Siding Panels, Exterior Door Frames. Plants consumed: Ohio Plant 7 (41% of at-risk units),
          Texas Plant 14 (35%), Georgia Plant 31 (24%).
        </p>
      );
    }
    if (q.includes('cost') || q.includes('compare')) {
      return (
        <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
          Cost comparison at $1.09M exposure:<br />
          · Option A: +$54,500 (5%) · 0 delay<br />
          · Option B: $0 (no supplier change) · 2-day delay — production slip absorbed by Georgia Plant 31 buffer<br />
          · Option C: +$239,800 (22%) · 0 delay — only if A and B fail
        </p>
      );
    }
  }

  // Invoice-specific rules from §7 — only fire when the invoice context is active
  // (or when no context, to keep default chat useful for the Globex scenario).
  const invoiceMode = !ctx || ctx.agentId === 'invoice';

  if (invoiceMode && (q.includes('po') || q.includes('purchase order') || q.includes('mismatch'))) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        <strong>PO-2024-0891</strong> was not found in your ERP system. The closest match is
        <strong> PO-2024-0819</strong> (Globex Corp, $82,000, Apr 10) — the last 2 digits differ,
        suggesting a typo. I recommend contacting Globex to confirm before approving.
      </p>
    );
  }
  if (invoiceMode && (q.includes('approve') || q.includes('approval'))) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        To approve this invoice I need a valid PO reference. Would you like me to:{' '}
        <strong>(A)</strong> match against PO-2024-0819 and flag the discrepancy, or{' '}
        <strong>(B)</strong> request a corrected invoice from Globex Corp?
      </p>
    );
  }
  if (invoiceMode && (q.includes('reject') || q.includes('decline'))) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        I've marked invoice <strong>GLX-2024-0441</strong> as <em>Rejected</em>. Reason: PO reference
        not found. A rejection notice has been queued for Globex Corp. The invoice has been moved to
        the Rejected archive.
      </p>
    );
  }
  if (invoiceMode && (q.includes('vendor') || q.includes('globex'))) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        <strong>Globex Corp</strong> has been an approved vendor since 2019. 47 invoices totaling
        $2.1M. Avg processing time 2.3 days. No fraud flags. Payment terms: Net 30. Primary contact:
        Sarah Chen, <span className="mono">AP@globex.com</span>.
      </p>
    );
  }
  if (invoiceMode && (q.includes('threshold') || q.includes('amount') || q.includes('87'))) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        Your auto-approval threshold is <strong>$10,000</strong>. This invoice for{' '}
        <strong>$87,400</strong> exceeds it by 774%. Invoices above $10k require AP Manager approval
        per your policy (Settings → Approval Rules).
      </p>
    );
  }
  if (invoiceMode && (q.includes('today') || q.includes('queue') || q.includes('stats'))) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        Today&rsquo;s Invoice Agent stats: <strong>142</strong> invoices processed, <strong>128</strong>{' '}
        auto-approved (90.1%), <strong>14</strong> routed for review. Avg confidence 96.2%, avg
        processing time 3.8s.
      </p>
    );
  }

  // Context-aware fallbacks for other doc types — lean on the ctx.followUp.
  if (ctx) {
    return (
      <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
        I hear you. Based on the flags on <strong>{ctx.name}</strong>, the most useful next step is
        probably one of: {ctx.quickReplies.join(', ')}. Tap any chip below and I'll run that for you.
      </p>
    );
  }

  // Generic fallback
  return (
    <p style={{ fontSize: 14, color: '#0f172a', lineHeight: 1.55 }}>
      I can answer questions about this document, run validations, or route it. Try one of the
      quick replies below — or tell me what you want to do in plain English.
    </p>
  );
}

/* ──────────────────────── sub-components ──────────────────────── */

function SideLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ padding: '10px 12px' }}>
      <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '.1em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 6 }}>
        {children}
      </div>
    </div>
  );
}

function AgentRow({ agent, active, onClick }: { agent: UIAgent; active: boolean; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      style={{
        padding: '10px 12px',
        cursor: 'pointer',
        background: active ? '#eff6ff' : 'transparent',
        borderLeft: active ? '3px solid #3b82f6' : 'none',
      }}
      onMouseOver={(e) => { if (!active) e.currentTarget.style.background = '#f8fafc'; }}
      onMouseOut={(e)  => { if (!active) e.currentTarget.style.background = ''; }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 32, height: 32, borderRadius: 10, background: agent.iconBg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: agent.iconColor, flexShrink: 0 }}>
          {agent.code}
        </div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{agent.name}</div>
          <div style={{ fontSize: 11, color: STATUS_COLOR[agent.status], fontWeight: 500 }}>
            {agent.status === 'idle' ? '○' : '●'} {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)} · {agent.detail}
          </div>
        </div>
      </div>
    </div>
  );
}

function ChatMsg({ who, avatar, time, children }: {
  who: 'agent' | 'user';
  avatar?: { code: string; bg: string; color: string };
  time: string;
  children: React.ReactNode;
}) {
  if (who === 'user') {
    return (
      <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', flexDirection: 'row-reverse' }}>
        <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, color: '#fff', flexShrink: 0 }}>CB</div>
        <div style={{ maxWidth: '80%' }}>
          <div className="chat-bubble-user">{children}</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4, textAlign: 'right' }}>{time}</div>
        </div>
      </div>
    );
  }
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
      <div style={{ width: 28, height: 28, borderRadius: 8, background: avatar?.bg || '#dbeafe', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, color: avatar?.color || '#1d4ed8', flexShrink: 0 }}>
        {avatar?.code || '?'}
      </div>
      <div style={{ maxWidth: '94%', flex: 1, minWidth: 0 }}>
        <div className="chat-bubble-agent">{children}</div>
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{time}</div>
      </div>
    </div>
  );
}

function FileBubble({ time, children }: { time: string; children: React.ReactNode }) {
  // Render the "file upload" indicator right-aligned (user-side) like a sent
  // attachment. The inner content is a white card — not a colored bubble.
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', flexDirection: 'row-reverse' }}>
      <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg,#3b82f6,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 700, color: '#fff', flexShrink: 0 }}>CB</div>
      <div style={{ maxWidth: '80%' }}>
        {children}
        <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4, textAlign: 'right' }}>{time}</div>
      </div>
    </div>
  );
}

/** Inline routing badge shown above each agent response. Surfaces which
 *  specialist would have answered, the intent class, and the latency.
 *  Click toggles the rationale row underneath. */
function RoutingBadge({ routing, latencyMs }: { routing: RoutingDecision; latencyMs: number }) {
  const [expanded, setExpanded] = React.useState(false);
  const theme = ROUTED_AGENT_THEME[routing.agent as RoutedAgent]
    ?? { bg: '#eef2ff', color: '#4338ca', label: routing.label || String(routing.agent), code: routing.code || '' };
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 4 }}>
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        style={{
          alignSelf: 'flex-start',
          display: 'inline-flex',
          alignItems: 'center',
          gap: 8,
          padding: '4px 10px',
          background: theme.bg,
          color: theme.color,
          fontSize: 11,
          fontWeight: 700,
          borderRadius: 999,
          border: `1px solid ${theme.color}33`,
          cursor: 'pointer',
          letterSpacing: '.02em',
        }}
        title="Click to show routing rationale"
      >
        <span style={{ opacity: 0.7 }}>routed →</span>
        <span>{routing.label || theme.label}</span>
        <span style={{ opacity: 0.55, fontWeight: 500 }}>· {routing.intent}</span>
        <span style={{ opacity: 0.55, fontWeight: 500 }}>
          · conf {(routing.confidence * 100).toFixed(0)}%
        </span>
        <span style={{ opacity: 0.55, fontWeight: 500 }}>
          · {(latencyMs / 1000).toFixed(1)}s
        </span>
      </button>
      {expanded && (
        <div
          style={{
            fontSize: 11,
            color: '#475569',
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: 6,
            padding: '6px 10px',
            marginLeft: 4,
            lineHeight: 1.55,
          }}
        >
          {routing.rationale}
        </div>
      )}
    </div>
  );
}

function FileCardContent({ name, type, chip, size, onClick }: {
  name: string; type: string; chip: string; size: string;
  /** When provided, the card becomes clickable and renders a "Preview"
   *  affordance. Used to open the right-panel File preview tab. */
  onClick?: () => void;
}) {
  const isClickable = !!onClick;
  return (
    <div
      onClick={onClick}
      style={{
        background: '#fff',
        border: '1px solid #e2e8f0',
        borderRadius: 12,
        padding: '10px 12px',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        minWidth: 240,
        cursor: isClickable ? 'pointer' : 'default',
        transition: 'all .15s',
      }}
      onMouseOver={(e) => {
        if (!isClickable) return;
        e.currentTarget.style.borderColor = '#bfdbfe';
        e.currentTarget.style.boxShadow = '0 2px 8px rgba(59,130,246,.1)';
      }}
      onMouseOut={(e) => {
        if (!isClickable) return;
        e.currentTarget.style.borderColor = '#e2e8f0';
        e.currentTarget.style.boxShadow = '';
      }}
      title={isClickable ? 'Click to preview the source document on the right' : undefined}
    >
      <div style={{
        width: 32, height: 32, borderRadius: 8, background: '#dbeafe',
        display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
      }}>
        <Icon name="doc" className="" style={{ width: 16, height: 16, color: '#1d4ed8' }} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{
          fontSize: 12, fontWeight: 600, color: '#0f172a',
          whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
        }}>
          {name}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
          <span className={chip} style={{ fontSize: 10 }}>{type}</span>
          <span style={{ fontSize: 11, color: '#94a3b8' }}>{size}</span>
          {isClickable && (
            <span style={{ marginLeft: 'auto', fontSize: 10, color: '#2563eb', fontWeight: 600 }}>
              Preview →
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4, padding: '2px 0' }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="animate-pulse"
          style={{
            width: 7, height: 7, borderRadius: '50%',
            background: '#94a3b8',
            animationDelay: `${i * 0.15}s`,
          }}
        />
      ))}
    </div>
  );
}

function MiniLabel({ children }: { children: React.ReactNode }) {
  return <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8', marginBottom: 8 }}>{children}</div>;
}

function OptionBox({ tag, tagColor, body }: { tag: string; tagColor: string; body: string }) {
  return (
    <div
      style={{
        background: '#fff',
        border: '1px solid #e2e8f0',
        borderLeft: `3px solid ${tagColor}`,
        borderRadius: 10,
        padding: '10px 12px',
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: '.06em',
          color: tagColor,
          marginBottom: 6,
        }}
      >
        {tag}
      </div>
      <div style={{ fontSize: 13, color: '#334155', lineHeight: 1.5 }}>{body}</div>
    </div>
  );
}

/* ═════════════════════ FEATURE 2 — Audit Lens ═════════════════════ */

interface DvrStep {
  step:   number;
  kind:   'thought' | 'action' | 'observation' | 'answer';
  text:   string;
  action?: string;                  // tool name when kind='action'
  input?:  unknown;
  output?: unknown;
}

interface DvrResponse {
  session_id:     string;
  message_id:     string;
  agent_id:       string;
  asked_at:       string | null;
  asked:          string | null;
  answered_at:    string | null;
  reasoning:      DvrStep[];
  actions_taken:  string[];
  model:          string;
}

function GovernanceDvr({ sessionId, messageId, agentName }: {
  sessionId: string | null;
  messageId: string | null;
  agentName: string;
  ctxAgentId: string;
}) {
  const [state, setState] = useState<
    | { kind: 'idle' }
    | { kind: 'loading' }
    | { kind: 'error';  message: string }
    | { kind: 'ready';  data: DvrResponse }
  >({ kind: 'idle' });

  useEffect(() => {
    if (!messageId || !sessionId) {
      setState({ kind: 'idle' });
      return;
    }
    let cancel = false;
    setState({ kind: 'loading' });
    (async () => {
      try {
        const r = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages/${messageId}/dvr`);
        if (!r.ok) throw new Error(`status ${r.status}`);
        const j = (await r.json()) as DvrResponse;
        if (!cancel) setState({ kind: 'ready', data: j });
      } catch (e) {
        if (!cancel) setState({ kind: 'error', message: e instanceof Error ? e.message : 'Request failed' });
      }
    })();
    return () => { cancel = true; };
  }, [sessionId, messageId]);

  if (!messageId) {
    return (
      <div style={{ flex: 1, padding: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 10, color: '#64748b' }}>
        <svg style={{ width: 40, height: 40, color: '#cbd5e1' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <div style={{ fontSize: 13, fontWeight: 600, color: '#374151' }}>Audit Lens</div>
        <div style={{ fontSize: 12, maxWidth: 240, lineHeight: 1.5 }}>
          Click any agent message to rewind the reasoning that produced it — document reads, policies evaluated, tools invoked, decisions made.
        </div>
      </div>
    );
  }

  if (state.kind === 'loading') {
    return (
      <div style={{ flex: 1, padding: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 10, color: '#64748b' }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: '#374151' }}>Loading reasoning trace…</div>
        <TypingDots />
      </div>
    );
  }

  if (state.kind === 'error') {
    return (
      <div style={{ flex: 1, padding: 24, color: '#64748b' }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: '#b91c1c', letterSpacing: '.06em', textTransform: 'uppercase', marginBottom: 4 }}>Audit Lens unavailable</div>
        <div style={{ fontSize: 12, lineHeight: 1.5 }}>
          Could not fetch the reasoning trace for this message from the backend.
          <div className="mono" style={{ marginTop: 6, fontSize: 11, color: '#94a3b8' }}>{state.message}</div>
          <div style={{ marginTop: 8, fontSize: 11 }}>
            Traces only exist for messages produced by the AgentCore backend. Local fallback messages (offline mode) don&apos;t have a persisted trace.
          </div>
        </div>
      </div>
    );
  }

  const data = state.kind === 'ready' ? state.data : null;
  if (!data) return null;
  const steps = data.reasoning || [];
  const asked = data.asked || '—';
  const when  = data.answered_at ? new Date(data.answered_at).toLocaleString() : '';

  return (
    <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 4 }}>
        Reasoning Trace
      </div>
      <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>
        Q: <span style={{ color: '#475569', fontWeight: 500 }}>{asked}</span>
      </div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 6 }}>
        Agent: {agentName} · Model: <span className="mono">{data.model}</span>
      </div>
      {when && <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 12 }}>Answered at {when}</div>}

      {steps.length === 0 && (
        <div style={{ fontSize: 12, color: '#64748b', padding: 12, background: '#f8fafc', borderRadius: 8, marginBottom: 12 }}>
          The AgentCore runtime answered without emitting a structured reasoning trace.
          Ask a more complex question (e.g. tool-using prompts) and Audit Lens will capture every step.
        </div>
      )}

      <ol
        className="dvr-timeline"
        style={{ listStyle: 'none', padding: 0, margin: 0, position: 'relative' }}
      >
        {steps.length > 0 && (
          <div aria-hidden style={{ position: 'absolute', left: 12, top: 12, bottom: 12, width: 2, background: '#e2e8f0' }} />
        )}
        {steps.map((s, i) => (
          <DvrStepRow key={i} step={s} first={i === 0} last={i === steps.length - 1} />
        ))}
      </ol>

      {data.actions_taken && data.actions_taken.length > 0 && (
        <div style={{ marginTop: 12, padding: 10, borderRadius: 8, background: '#f1f5f9' }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#475569', marginBottom: 4 }}>
            Tools called
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {normalizeActions(data.actions_taken).map((a, i) => (
              <span key={i} className="chip-blue mono" style={{ fontSize: 10 }}>{a}</span>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: 16, padding: 12, background: '#f0fdf4', borderRadius: 10, border: '1px solid #bbf7d0' }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: '#166534', letterSpacing: '.06em', textTransform: 'uppercase' }}>
          Audit-ready
        </div>
        <div style={{ fontSize: 12, color: '#14532d', marginTop: 4, lineHeight: 1.5 }}>
          Steps are persisted per message in DynamoDB. Export or ship them to your SIEM.
        </div>
        <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
          <button
            className="btn btn-secondary btn-sm"
            style={{ flex: 1, justifyContent: 'center', background: '#fff' }}
            onClick={() => {
              const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
              const url = URL.createObjectURL(blob);
              const a = document.createElement('a'); a.href = url; a.download = `dvr-${data.message_id}.json`;
              a.click(); URL.revokeObjectURL(url);
            }}
          >Export JSON</button>
          <button
            className="btn btn-secondary btn-sm"
            style={{ flex: 1, justifyContent: 'center', background: '#fff' }}
            onClick={() => {
              navigator.clipboard?.writeText(JSON.stringify(data, null, 2));
            }}
          >Copy</button>
        </div>
      </div>
    </div>
  );
}

function DvrStepRow({ step, first, last }: { step: DvrStep; first: boolean; last: boolean }) {
  const tone = {
    thought:     { dot: '#7c3aed', chip: 'chip-purple', label: 'Thought' },
    action:      { dot: '#0f766e', chip: 'chip-green',  label: 'Tool Call' },
    observation: { dot: '#3b82f6', chip: 'chip-blue',   label: 'Result' },
    answer:      { dot: '#f59e0b', chip: 'chip-amber',  label: 'Answer' },
  }[step.kind];

  return (
    <li style={{
      position: 'relative',
      paddingLeft: 34,
      paddingTop: first ? 0 : 14,
      paddingBottom: last ? 0 : 14,
    }}>
      <span style={{
        position: 'absolute', left: 5, top: first ? 2 : 16,
        width: 16, height: 16, borderRadius: '50%',
        background: '#fff', border: `3px solid ${tone.dot}`,
        boxShadow: '0 0 0 3px #fff',
      }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span className="mono" style={{ fontSize: 11, color: '#64748b' }}>#{step.step}</span>
        <span className={tone.chip} style={{ fontSize: 10 }}>{tone.label}</span>
        {step.action && (
          <span className="mono" style={{ fontSize: 11, color: '#0f766e' }}>{step.action}</span>
        )}
      </div>
      <div style={{ fontSize: 13, color: '#0f172a', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>{step.text}</div>
    </li>
  );
}

