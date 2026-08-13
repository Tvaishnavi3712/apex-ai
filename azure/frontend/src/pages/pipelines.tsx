/**
 * Pipelines — interactive automation pipelines.
 *
 * Implements Apex_Pipelines_Interactive_Spec.docx (v1.0, Apr 2026).
 *
 * Modes:
 *   'list'   — default grid of pipeline cards with filter chips + Run/Open buttons
 *   'editor' — replaces main content with a pipeline editor for one pipeline
 *   (the 'wizard' overlay can open on top of either mode)
 *
 * Overlays:
 *   stage panel (right-slide, 380px) — Config / Schema / History tabs
 *   wizard modal (center, 720px)     — 4-step new-pipeline flow
 *   run output panel (right-slide)   — JSON output + stage results after a run
 *   toast (top-right)                — 2-second status notifications
 *
 * This is a demo prototype — all data is in-memory (PIPELINES mutates in
 * response to wizard/editor actions). No backend calls are required.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import { useQuery } from '@tanstack/react-query';
import { Icon } from '@/components/AppShell/icons';
import { useDemoMode } from '@/lib/demoMode';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ═════════════════════ types ═════════════════════ */

type StageKind =
  | 'extract' | 'validate' | 'decide' | 'classify' | 'execute'
  | 'score'   | 'calculate'| 'model'  | 'notify'   | 'generate'
  | 'lookup'  | 'predict'  | 'analyze'| 'check';

interface StageConfig {
  /** snake_case identifier shown as the action name, e.g. `bda_document_extract` */
  actionName: string;
  timeoutSeconds: number;
  retryOnFailure: boolean;
  maxRetries: number;
  confidenceThreshold: number;     // 0..100
  inputMapping: string;            // JSON string
  outputMapping: string;           // JSON string
  condition?: string;              // optional plain-English / expression
}

interface Stage {
  id: string;
  kind: StageKind;
  label: string;
  /** Per-stage editable config surfaced in the right panel. */
  config: StageConfig;
}

type IndustryKey =
  | 'Financial Services'
  | 'Commercial Insurance'
  | 'Healthcare Payers'
  | 'Aerospace & Defense'
  | 'Supply Chain & Manufacturing'
  | 'Nuclear Operations & Reliability'
  | 'Telecommunications'
  | 'Supply Chain Orchestrator'
  | 'Hospitality & Travel'
  | 'Commercial Real Estate'
  | 'Oil & Gas — Midstream'
  | 'Credit Union'
  | 'Manufacturing · Multi-Division';

type FilterKey =
  | 'All' | 'Financial' | 'Insurance' | 'Healthcare' | 'Aerospace'
  | 'Supply Chain & Manufacturing' | 'Nuclear Operations' | 'Telecommunications'
  | 'Supply Chain Orchestrator' | 'Hospitality & Travel' | 'Commercial Real Estate'
  | 'Oil & Gas — Midstream'
  | 'Credit Union'
  | 'Manufacturing · Multi-Division';

interface PipelineStats {
  avgLatency: string;
  accuracy?: string;
  autoApprove?: string;
  lastRun: string;
}

interface Pipeline {
  id: string;
  name: string;
  industry: IndustryKey;
  throughput: string;
  status: 'Active' | 'Deploying' | 'Draft';
  stages: Stage[];
  stats: PipelineStats;
}

/* ═════════════════════ stage-type theme ═════════════════════ */

const STAGE_TYPES: Record<StageKind, { label: string; bg: string; border: string; color: string }> = {
  extract:   { label: 'Extract',   bg: '#eff6ff', border: '#bfdbfe', color: '#3b82f6' },
  analyze:   { label: 'Analyze',   bg: '#eff6ff', border: '#bfdbfe', color: '#3b82f6' },
  validate:  { label: 'Validate',  bg: '#f0fdf4', border: '#bbf7d0', color: '#16a34a' },
  check:     { label: 'Check',     bg: '#f0fdf4', border: '#bbf7d0', color: '#16a34a' },
  decide:    { label: 'Decide',    bg: '#fdf4ff', border: '#e9d5ff', color: '#7c3aed' },
  classify:  { label: 'Classify',  bg: '#fdf4ff', border: '#e9d5ff', color: '#7c3aed' },
  notify:    { label: 'Notify',    bg: '#fffbeb', border: '#fde68a', color: '#d97706' },
  generate:  { label: 'Generate',  bg: '#fffbeb', border: '#fde68a', color: '#d97706' },
  score:     { label: 'Score',     bg: '#fff7ed', border: '#fed7aa', color: '#ea580c' },
  calculate: { label: 'Calculate', bg: '#fff7ed', border: '#fed7aa', color: '#ea580c' },
  model:     { label: 'Model',     bg: '#fff7ed', border: '#fed7aa', color: '#ea580c' },
  execute:   { label: 'Execute',   bg: '#f0fdfa', border: '#99f6e4', color: '#0f766e' },
  lookup:    { label: 'Lookup',    bg: '#f0fdfa', border: '#99f6e4', color: '#0f766e' },
  predict:   { label: 'Predict',   bg: '#f0fdfa', border: '#99f6e4', color: '#0f766e' },
};

const STAGE_KIND_OPTIONS: StageKind[] = [
  'extract', 'analyze', 'validate', 'check', 'decide', 'classify',
  'notify', 'generate', 'score', 'calculate', 'model',
  'execute', 'lookup', 'predict',
];

/* ═════════════════════ helpers ═════════════════════ */

const newStageId = () => `s-${Math.random().toString(36).slice(2, 9)}`;

const defaultConfig = (actionName: string, kind: StageKind): StageConfig => ({
  actionName,
  timeoutSeconds: 30,
  retryOnFailure: true,
  maxRetries: 3,
  confidenceThreshold: 85,
  inputMapping: JSON.stringify({ source: 'pipeline.context' }, null, 2),
  outputMapping: JSON.stringify({ result: `context.${actionName}_result` }, null, 2),
  condition: undefined,
});

const mkStage = (kind: StageKind, label: string, actionName: string): Stage => ({
  id: newStageId(),
  kind,
  label,
  config: defaultConfig(actionName, kind),
});

/* ═════════════════════ initial pipeline data ═════════════════════ */

const INITIAL_PIPELINES: Pipeline[] = [
  /* ═══════════════ CBB Demo pipelines (see CBB_Apex_Full_Execution_Plan.docx §3.3) ═══════════════ */
  {
    id: 'pipe-cbb-order-mod',
    name: 'Order Modification Pipeline',
    industry: 'Supply Chain & Manufacturing', // CBB Zero-Touch Order Modification playbook
    throughput: '320 mods/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'BDA Blueprint',      'bda_document_extract'),
      mkStage('execute',  'Athena Query',       'athena_federated_query'),
      mkStage('validate', 'Constraint Check',   'engineering_constraint_check'),
      mkStage('execute',  'CRM Update',         'crm_order_update'),
      mkStage('notify',   'Email Confirmation', 'email_send'),
    ],
    stats: { avgLatency: '4.2s', accuracy: '97.4%', autoApprove: '92%', lastRun: '2 min ago' },
  },
  {
    id: 'pipe-cbb-qc',
    name: 'QC Batch Ingestion Pipeline',
    industry: 'Supply Chain & Manufacturing',
    throughput: '50 certs / batch',
    status: 'Active',
    stages: [
      mkStage('extract',  'BDA Batch (50 PDFs)', 'bda_document_extract'),
      mkStage('validate', 'Fabric Tolerance',    'fabric_tolerance_check'),
      mkStage('decide',   'Auto Hold',           'auto_hold_decision'),
      mkStage('execute',  'ERP Inventory Hold',  'erp_inventory_hold'),
      mkStage('notify',   'Teams Alert',         'teams_alert'),
    ],
    stats: { avgLatency: '4.2s', accuracy: '99.1%', autoApprove: '96%', lastRun: '14 min ago' },
  },
  {
    id: 'pipe-cbb-disruption',
    name: 'Supply Chain Disruption Pipeline',
    industry: 'Supply Chain & Manufacturing',
    throughput: 'Event-driven',
    status: 'Active',
    stages: [
      mkStage('analyze',  'BOM Graph Traverse',    'bom_graph_traverse'),
      mkStage('predict',  'Financial Impact',      'predict_financial_impact'),
      mkStage('generate', 'Reroute Options',       'reroute_options_generate'),
      mkStage('decide',   'Escalate to Human',     'escalate_decision'),
      mkStage('notify',   'Supply Chain Director', 'teams_alert'),
    ],
    stats: { avgLatency: '2.1s', accuracy: '98.7%', lastRun: '6 min ago' },
  },

  /* ═══════════════ Generic pipelines ═══════════════ */
  {
    id: 'pipe-invoice',
    name: 'Invoice Processing Pipeline',
    industry: 'Financial Services',
    throughput: '142 docs/hr',
    status: 'Active',
    stages: [
      mkStage('extract',  'BDA Blueprint', 'bda_document_extract'),
      mkStage('validate', 'PO Match',      'po_match'),
      mkStage('validate', 'Dup Check',     'duplicate_check'),
      mkStage('decide',   'Auto Decision', 'auto_approval_decision'),
      mkStage('notify',   'Slack + ERP',   'notify_slack_erp'),
    ],
    stats: { avgLatency: '8.2s', accuracy: '97.2%', autoApprove: '78%', lastRun: '2 min ago' },
  },
  {
    id: 'pipe-cre',
    name: 'CRE Underwriting Pipeline',
    industry: 'Commercial Insurance',
    throughput: '28 submissions/hr',
    status: 'Active',
    stages: [
      mkStage('extract',   'Submission',    'cre_document_extract'),
      mkStage('score',     'Risk Score',    'cre_risk_score'),
      mkStage('calculate', 'Premium',       'cre_premium_calculate'),
      mkStage('model',     'CAT Model',     'cre_cat_model'),
      mkStage('decide',    'Auto Decision', 'cre_auto_decision'),
    ],
    stats: { avgLatency: '14.7s', accuracy: '95.8%', autoApprove: '62%', lastRun: '18 min ago' },
  },
  {
    id: 'pipe-prior-auth',
    name: 'Prior Authorization Pipeline',
    industry: 'Healthcare Payers',
    throughput: '64 auths/hr',
    status: 'Active',
    stages: [
      mkStage('extract',  'Auth Extract',     'auth_extract'),
      mkStage('validate', 'Eligibility',      'eligibility_verify'),
      mkStage('execute',  'Criteria Eval',    'criteria_evaluate'),
      mkStage('classify', 'Clinical Route',   'clinical_route'),
      mkStage('execute',  'Auth Decision',    'auth_decision'),
      mkStage('notify',   'Send',             'notification_send'),
    ],
    stats: { avgLatency: '6.1s', accuracy: '96.5%', autoApprove: '71%', lastRun: '4 min ago' },
  },
  {
    id: 'pipe-rfp',
    name: 'RFP Response Pipeline',
    industry: 'Aerospace & Defense',
    throughput: '4 RFPs/day',
    status: 'Active',
    stages: [
      mkStage('analyze',  'RFP Analysis',    'rfp_analysis'),
      mkStage('lookup',   'Contracts',       'contract_lookup'),
      mkStage('predict',  'Pricing',         'predict_pricing'),
      mkStage('generate', 'RFP Response',    'generate_rfp_response'),
      mkStage('check',    'ITAR Compliance', 'itar_compliance_check'),
    ],
    stats: { avgLatency: '42s', accuracy: '91.4%', autoApprove: '68%', lastRun: '3 hr ago' },
  },
  {
    id: 'pipe-supplier',
    name: 'Supplier Performance Pipeline',
    industry: 'Supply Chain & Manufacturing',
    throughput: '12 reports/day',
    status: 'Active',
    stages: [
      mkStage('execute',  'Delivery Metrics',   'delivery_metrics'),
      mkStage('execute',  'Quality Metrics',    'quality_metrics'),
      mkStage('execute',  'Cost Analysis',      'cost_analysis'),
      mkStage('generate', 'Scorecard',          'scorecard_generate'),
      mkStage('execute',  'Improvement Plan',   'improvement_plan'),
    ],
    stats: { avgLatency: '3.8s', accuracy: '94.3%', lastRun: '12 hr ago' },
  },

  /* ═══════════════ Manufacturing pipelines (generic) ═══════════════ */
  {
    id: 'pipe-mfg-qc-line',
    name: 'Production Line QC Pipeline',
    industry: 'Supply Chain & Manufacturing',
    throughput: '210 inspections/hr',
    status: 'Active',
    stages: [
      mkStage('extract',  'QC Form Extract',      'bda_document_extract'),
      mkStage('validate', 'Tolerance Check',      'fabric_tolerance_check'),
      mkStage('decide',   'Pass / Hold / Reject', 'auto_hold_decision'),
      mkStage('execute',  'SAP Inventory Update', 'erp_inventory_hold'),
      mkStage('notify',   'Plant Supervisor',     'teams_alert'),
    ],
    stats: { avgLatency: '3.4s', accuracy: '98.2%', autoApprove: '88%', lastRun: '9 min ago' },
  },
  {
    id: 'pipe-mfg-po-match',
    name: 'Supplier PO Match Pipeline',
    industry: 'Supply Chain & Manufacturing',
    throughput: '95 POs/hr',
    status: 'Active',
    stages: [
      mkStage('extract',  'PO Extract',       'bda_document_extract'),
      mkStage('lookup',   'Open PO Lookup',   'athena_federated_query'),
      mkStage('validate', 'Three-Way Match',  'po_match'),
      mkStage('decide',   'Auto Approval',    'auto_approval_decision'),
      mkStage('notify',   'Procurement Team', 'email_send'),
    ],
    stats: { avgLatency: '5.9s', accuracy: '96.7%', autoApprove: '81%', lastRun: '22 min ago' },
  },
  {
    id: 'pipe-mfg-workorder',
    name: 'Work Order Routing Pipeline',
    industry: 'Supply Chain & Manufacturing',
    throughput: '48 WOs/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Work Order',       'bda_document_extract'),
      mkStage('analyze',  'Capacity Check',   'bom_graph_traverse'),
      mkStage('generate', 'Routing Plan',     'reroute_options_generate'),
      mkStage('decide',   'Schedule Slot',    'escalate_decision'),
      mkStage('execute',  'ERP Dispatch',     'erp_inventory_hold'),
    ],
    stats: { avgLatency: '7.1s', accuracy: '95.4%', autoApprove: '74%', lastRun: '1 hr ago' },
  },

  /* ═══════════════ STP Phase 2 demo pipelines (4 use cases) ═══════════════ */
  {
    id: 'pipe-stp-policy',
    name: 'Policy & Procedure Lookup',
    industry: 'Nuclear Operations & Reliability',
    throughput: '24 queries/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Intent Classify',     'intent_classify'),
      mkStage('execute',  'Policy Search',       'policy_search'),
      mkStage('extract',  'Cite Extract',        'policy_cite_extract'),
      mkStage('notify',   'Verbatim Response',   'email_send'),
    ],
    stats: { avgLatency: '3.2s', accuracy: '99.0%', autoApprove: '100%', lastRun: '14 min ago' },
  },
  {
    id: 'pipe-stp-pm-history',
    name: 'Equipment PM History',
    industry: 'Nuclear Operations & Reliability',
    throughput: '18 lookups/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Intent Classify',     'intent_classify'),
      mkStage('execute',  'Oracle PM Lookup',    'oracle_pm_lookup'),
      mkStage('execute',  'Engineer Attribution','engineer_attribution'),
      mkStage('execute',  'WP PDF Fetch',        'wp_attachment_fetch'),
    ],
    stats: { avgLatency: '4.8s', accuracy: '97.4%', autoApprove: '95%', lastRun: '3 min ago' },
  },
  {
    id: 'pipe-stp-issue-analysis',
    name: 'Equipment Issue Analysis',
    industry: 'Nuclear Operations & Reliability',
    throughput: '12 analyses/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Intent Classify',     'intent_classify'),
      mkStage('analyze',  'WP Corpus Search',    'wp_corpus_search'),
      mkStage('analyze',  'Failure Modes',       'failure_mode_aggregate'),
      mkStage('notify',   'Ranked Findings',     'email_send'),
    ],
    stats: { avgLatency: '6.2s', accuracy: '94.2%', autoApprove: '88%', lastRun: '7 min ago' },
  },
  {
    id: 'pipe-stp-predictive',
    name: 'Predictive Maintenance',
    industry: 'Nuclear Operations & Reliability',
    throughput: '8 alerts/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Intent Classify',     'intent_classify'),
      mkStage('analyze',  'Anomaly Detect',      'anomaly_detect'),
      mkStage('analyze',  'RUL Predict',         'rul_predict'),
      mkStage('analyze',  'Risk Score',          'risk_score_compute'),
      mkStage('decide',   'PM Recommendation',   'pm_recommend'),
    ],
    stats: { avgLatency: '9.1s', accuracy: '91.8%', autoApprove: '72%', lastRun: '11 min ago' },
  },

  /* ═══════════════ Telecommunications — Verizon Far Edge POC (3 pipelines) ═══════════════ */
  {
    id: 'pipe-tel-certification',
    name: 'Full Certification Cycle',
    industry: 'Telecommunications',
    throughput: '12 cycles/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Parse ROBOT XML',       'parse_robot_output'),
      mkStage('analyze',  'Classify Failures',     'classify_failures'),
      mkStage('validate', 'Schema Drift Check',    'detect_schema_drift'),
      mkStage('execute',  'Build JIRA Tickets',    'jira_create_ticket'),
      mkStage('notify',   'Cert Report Generate',  'certification_report'),
    ],
    stats: { avgLatency: '14.8m', accuracy: '99.2%', autoApprove: '88%', lastRun: '32 min ago' },
  },
  {
    id: 'pipe-tel-wave-risk',
    name: 'Wave Deployment Risk Assessment',
    industry: 'Telecommunications',
    throughput: '4 waves/day',
    status: 'Active',
    stages: [
      mkStage('lookup',   'Load Site Inventory',   'site_inventory_load'),
      mkStage('analyze',  'Risk Scoring',          'compute_risk_scores'),
      mkStage('analyze',  'Pattern Match',         'pattern_match_january_2026'),
      mkStage('validate', 'Upgrade Path Check',    'validate_upgrade_path'),
      mkStage('decide',   'HITL Wave Approval',    'wave_authorization'),
    ],
    stats: { avgLatency: '8.2s', accuracy: '96.4%', autoApprove: '74%', lastRun: '8 min ago' },
  },
  {
    id: 'pipe-tel-schema-drift',
    name: 'Schema Drift Response',
    industry: 'Telecommunications',
    throughput: '4 sweeps/day',
    status: 'Active',
    stages: [
      mkStage('lookup',   'Fetch Live Schema',     'redfish_schema_fetch'),
      mkStage('analyze',  'Diff vs Baseline',      'detect_schema_drift'),
      mkStage('execute',  'Map Script Impact',     'script_impact_map'),
      mkStage('execute',  'Open JIRA Epic',        'jira_create_epic'),
      mkStage('notify',   'Alert Automation Team', 'teams_alert'),
    ],
    stats: { avgLatency: '6.4s', accuracy: '98.8%', autoApprove: '92%', lastRun: '2 hr ago' },
  },
  {
    id: 'pipe-tel-mentor',
    name: 'Operator Knowledge Q&A',
    industry: 'Telecommunications',
    throughput: '142 queries/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Intent Classify',           'intent_classify'),
      mkStage('analyze',  'Mentor Query (Apex Lens)',  'mentor_query'),
      mkStage('validate', 'Production-Change Flag',    'production_change_flag'),
      mkStage('notify',   'Audit Lens Emit',           'audit_log_emit'),
    ],
    stats: { avgLatency: '5.8s', accuracy: '94.0%', autoApprove: '88%', lastRun: '6 min ago' },
  },
  {
    id: 'pipe-tel-onboarding',
    name: 'New-Platform Onboarding (Orchestrated) ⭐',
    industry: 'Telecommunications',
    throughput: '2 platforms certifying',
    status: 'Active',
    stages: [
      mkStage('analyze',  'Design Test Coverage',  'design_test_coverage'),
      mkStage('execute',  'Run × 5 Iterations',    'run_test_iterations'),
      mkStage('analyze',  'Gap Analysis',          'analyze_playbook_gaps'),
      mkStage('decide',   'HITL · Approve Changes','apply_playbook_change'),
      mkStage('notify',   'Cert Report + Audit',   'certification_report'),
    ],
    stats: { avgLatency: '18m', accuracy: '100%', autoApprove: '—', lastRun: '4 min ago' },
  },
  {
    id: 'pipe-tel-playbook-gap',
    name: 'BMC Playbook Gap Analysis → Change-Spec',
    industry: 'Telecommunications',
    throughput: 'Per new platform',
    status: 'Active',
    stages: [
      mkStage('analyze',  'Inventory Results',     'analyze_playbook_gaps'),
      mkStage('analyze',  'Assess Each Role',      'analyze_playbook_gaps'),
      mkStage('extract',  'Draft Changes',         'draft_playbook_change'),
      mkStage('decide',   'HITL · Sign-Off',       'apply_playbook_change'),
      mkStage('execute',  'Commit + Open PR',      'apply_playbook_change'),
    ],
    stats: { avgLatency: '8.9s', accuracy: '100%', autoApprove: '—', lastRun: '4 min ago' },
  },

  /* ═══════════════ Agentic Enterprise — UC-1 Supply Chain Orchestrator ═══════════════ */
  {
    id: 'pipe-ae-supply-orchestrator',
    name: 'Supply Chain Orchestrator',
    industry: 'Supply Chain Orchestrator',
    throughput: '12 plans/day',
    status: 'Active',
    stages: [
      mkStage('lookup',  'Check Inventory',           'check_inventory'),
      mkStage('analyze', 'Find Alternative Supplier', 'find_alternative_supplier'),
      mkStage('generate','Draft Purchase Order',      'draft_purchase_order'),
      mkStage('notify',  'Submit for Approval',       'submit_for_approval'),
    ],
    stats: { avgLatency: '1.8s', accuracy: '98.4%', autoApprove: '0%', lastRun: '4 min ago' },
  },
  /* ═══════════════ Agentic Enterprise — UC-2 Cruise Concierge ═══════════════ */
  {
    id: 'pipe-ae-cruise-concierge',
    name: 'Cruise Concierge',
    industry: 'Hospitality & Travel',
    throughput: '430 chats/day',
    status: 'Active',
    stages: [
      mkStage('score',    'Sentiment Score',     'sentiment_score'),
      mkStage('classify', 'Intent Classify',     'intent_classify'),
      mkStage('lookup',   'RAG FAQ Lookup',      'rag_faq_lookup'),
      mkStage('execute',  'Booking Modify',      'booking_modify'),
      mkStage('notify',   'Agent Assist Handoff','agent_assist_handoff'),
    ],
    stats: { avgLatency: '0.9s', accuracy: '96.7%', autoApprove: '88%', lastRun: '38 sec ago' },
  },
  /* ═══════════════ Agentic Enterprise — UC-3 Lease Extraction ═══════════════ */
  {
    id: 'pipe-ae-lease-extraction',
    name: 'Lease Extraction',
    industry: 'Commercial Real Estate',
    throughput: '92 leases/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Lease Extract',  'lease_extract'),
      mkStage('validate', 'Confidence Check','confidence_check'),
      mkStage('execute',  'Index to DuckDB','lease_index'),
      mkStage('execute',  'Run SQL Query',  'duckdb_query'),
    ],
    stats: { avgLatency: '3.2s', accuracy: '94.8%', autoApprove: '78%', lastRun: '2 min ago' },
  },

  /* ═══════════════ EPROD — Oil & Gas Midstream (6 use cases) ═══════════════ */
  {
    id: 'pipe-eprod-invoice',
    name: 'Invoice Intelligence',
    industry: 'Oil & Gas — Midstream',
    throughput: '186 invoices/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Ingest',         'eprod_invoice_ingest'),
      mkStage('extract',  'Extract',        'eprod_invoice_extract'),
      mkStage('validate', 'MSA Match',      'eprod_msa_match'),
      mkStage('decide',   'HITL Gate',      'eprod_hitl_gate'),
      mkStage('execute',  'ERP Writeback',  'eprod_erp_writeback'),
    ],
    stats: { avgLatency: '6.8s', accuracy: '96.4%', autoApprove: '82%', lastRun: '11 min ago' },
  },
  {
    id: 'pipe-eprod-po',
    name: 'PO-to-Contract Validation',
    industry: 'Oil & Gas — Midstream',
    throughput: '124 POs/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Parse PO',           'eprod_po_parse'),
      mkStage('validate', 'MSA Scope Check',    'eprod_msa_scope_check'),
      mkStage('validate', 'Rate Validation',    'eprod_rate_validate'),
      mkStage('validate', 'Tax Validation',     'eprod_tax_validate'),
      mkStage('execute',  'Procurement Route',  'eprod_procurement_route'),
    ],
    stats: { avgLatency: '5.4s', accuracy: '97.1%', autoApprove: '79%', lastRun: '23 min ago' },
  },
  {
    id: 'pipe-eprod-vendor',
    name: 'Non-PO MSA Validation',
    industry: 'Oil & Gas — Midstream',
    throughput: '92 intakes/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Intake',          'eprod_intake_parse'),
      mkStage('lookup',   'MSA Lookup',      'eprod_msa_lookup'),
      mkStage('validate', 'Scope Check',     'eprod_scope_check'),
      mkStage('execute',  'Approval Route',  'eprod_approval_route'),
    ],
    stats: { avgLatency: '4.1s', accuracy: '95.8%', autoApprove: '74%', lastRun: '42 min ago' },
  },
  {
    id: 'pipe-eprod-quote',
    name: 'Engineering Quote Processing',
    industry: 'Oil & Gas — Midstream',
    throughput: '38 quotes/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'Quote Parse',          'eprod_quote_parse'),
      mkStage('analyze',  'Historical Compare',   'eprod_historical_compare'),
      mkStage('execute',  'Procurement Route',    'eprod_quote_route'),
      mkStage('execute',  'PO Chain Link',        'eprod_po_chain_link'),
    ],
    stats: { avgLatency: '7.6s', accuracy: '93.2%', autoApprove: '66%', lastRun: '1 hr ago' },
  },
  {
    id: 'pipe-eprod-tariff',
    name: 'FERC Tariff Sheet Validation ⭐',
    industry: 'Oil & Gas — Midstream',
    throughput: '64 validations/day',
    status: 'Active',
    stages: [
      mkStage('extract',  'FERC Ingest',          'eprod_ferc_ingest'),
      mkStage('analyze',  'PPI-FG Track',         'eprod_ppi_fg_track'),
      mkStage('validate', 'Shipper Invoice Match','eprod_shipper_invoice_match'),
      mkStage('analyze',  'Variance Detect',      'eprod_variance_detect'),
      mkStage('decide',   'HITL Escalate',        'eprod_hitl_escalate'),
    ],
    stats: { avgLatency: '8.9s', accuracy: '98.1%', autoApprove: '71%', lastRun: '17 min ago' },
  },
  {
    id: 'pipe-eprod-jib',
    name: 'JIB Reconciliation vs AFE ⭐',
    industry: 'Oil & Gas — Midstream',
    throughput: '88 statements/day',
    status: 'Active',
    stages: [
      mkStage('extract',   'JIB Parse',            'eprod_jib_parse'),
      mkStage('lookup',    'AFE Lookup',           'eprod_afe_lookup'),
      mkStage('calculate', 'Partner Share Compute','eprod_partner_share_compute'),
      mkStage('analyze',   'Overrun Detect',       'eprod_overrun_detect'),
      mkStage('decide',    'JV Escalate',          'eprod_jv_escalate'),
    ],
    stats: { avgLatency: '10.4s', accuracy: '96.8%', autoApprove: '68%', lastRun: '5 min ago' },
  },

  /* ═══════════════════ CWFCU · Credit Union (8 pipelines) ═══════════════════
   * 5 agent-aligned playbooks + 1 cross-agent NCUA assembly playbook.
   * Maps 1:1 to playbooks/credit_union/ pb-cwfcu-1..8.
   */
  {
    id: 'pipe-cwfcu-cip-onboarding',
    name: 'New Member CIP Onboarding',
    industry: 'Credit Union',
    throughput: '204 members/mo',
    status: 'Active',
    stages: [
      mkStage('extract',  'CIP Ingest',      'cip_ingest'),
      mkStage('validate',  'ID Verify (DLDV)', 'verify_government_id'),
      mkStage('check',  'OFAC + PEP Screen','ofac_screen'),
      mkStage('analyze', 'Risk Tier Calc',  'cip_calculate_risk_tier'),
      mkStage('decide',  'Approve / HITL',  'cip_approval_route'),
    ],
    stats: { avgLatency: '11.4 min', accuracy: '97.2%', autoApprove: '78%', lastRun: '2 min ago' },
  },
  {
    id: 'pipe-cwfcu-bsa-aml',
    name: 'BSA/AML Transaction Monitoring + SAR Draft ⭐',
    industry: 'Credit Union',
    throughput: '142 SARs/mo',
    status: 'Active',
    stages: [
      mkStage('analyze', 'Transaction Stream', 'monitor_transactions'),
      mkStage('analyze', 'Pattern Detection',  'detect_pattern'),
      mkStage('lookup',  'Member Context',     'pull_member_context'),
      mkStage('extract', 'SAR Draft (FinCEN)', 'draft_sar_narrative'),
      mkStage('decide',  'BSA Officer Review', 'route_to_bsa_officer'),
    ],
    stats: { avgLatency: '3.0s', accuracy: '96.1%', autoApprove: '0%', lastRun: '14 min ago' },
  },
  {
    id: 'pipe-cwfcu-ctr',
    name: 'CTR Auto-Filing',
    industry: 'Credit Union',
    throughput: '47 CTRs/mo',
    status: 'Active',
    stages: [
      mkStage('analyze', 'Cash Threshold ≥ $10K','detect_ctr_threshold'),
      mkStage('extract', 'Form 112 Draft',       'draft_ctr'),
      mkStage('decide',  'BSA Officer Review',   'bsa_officer_review'),
      mkStage('notify',  'FinCEN E-Filing',      'fincen_submit'),
    ],
    stats: { avgLatency: '40s', accuracy: '99.4%', autoApprove: '94%', lastRun: '8 min ago' },
  },
  {
    id: 'pipe-cwfcu-cdd',
    name: 'CDD / EDD Periodic Review',
    industry: 'Credit Union',
    throughput: '68,889 members tracked',
    status: 'Active',
    stages: [
      mkStage('lookup',  'Schedule Cohort',     'cdd_schedule'),
      mkStage('extract', 'Activity Summary',    'pull_activity_summary'),
      mkStage('analyze', 'Anomaly Detection',   'detect_anomalies'),
      mkStage('check',  'OFAC + PEP Rescreen', 'rescreen'),
      mkStage('decide',  'Risk Tier Update',    'cdd_assemble_packet'),
    ],
    stats: { avgLatency: '4.1s', accuracy: '94.7%', autoApprove: '82%', lastRun: '3 min ago' },
  },
  {
    id: 'pipe-cwfcu-loan',
    name: 'Loan Packet Validation (Auto / HELOC / Mortgage / Personal)',
    industry: 'Credit Union',
    throughput: '318 packets/mo',
    status: 'Active',
    stages: [
      mkStage('extract',  'Packet Ingest',     'loan_ingest'),
      mkStage('extract', 'BDA Doc Extract',   'loan_extract'),
      mkStage('analyze', 'Income X-Validate', 'loan_cross_validate_income'),
      mkStage('calculate','DTI + LTV',         'calculate_dti_ltv'),
      mkStage('decide',  'Route to UW',       'loan_route'),
    ],
    stats: { avgLatency: '1.4 days', accuracy: '93.8%', autoApprove: '94%', lastRun: '6 min ago' },
  },
  {
    id: 'pipe-cwfcu-vendor',
    name: 'Vendor Contract Renewal + SLA Watch',
    industry: 'Credit Union',
    throughput: '47 contracts monitored',
    status: 'Active',
    stages: [
      mkStage('analyze', 'Contract Monitor',     'vendor_monitor'),
      mkStage('analyze', 'Rate Drift Detect',    'detect_rate_drift'),
      mkStage('analyze', 'SLA Breach Detect',    'detect_sla_breach'),
      mkStage('extract', 'Renewal Brief',        'assemble_renewal_brief'),
      mkStage('notify',  'Policy Obligation →',  'trigger_policy_obligations'),
    ],
    stats: { avgLatency: '3.7s', accuracy: '91.4%', autoApprove: '64%', lastRun: '11 min ago' },
  },
  {
    id: 'pipe-cwfcu-policy',
    name: 'Policy Ack + BSA Training Tracking',
    industry: 'Credit Union',
    throughput: '84 employees tracked',
    status: 'Active',
    stages: [
      mkStage('analyze', 'Daily Roster Scan',    'policy_ack_track'),
      mkStage('analyze', 'Overdue Detect',       'policy_detect_overdue'),
      mkStage('notify',  'Auto Reminders',       'policy_send_reminders'),
      mkStage('decide',  'Escalation Cascade',   'policy_escalate'),
    ],
    stats: { avgLatency: '5.4s', accuracy: '98.8%', autoApprove: '92%', lastRun: '9 min ago' },
  },
  {
    id: 'pipe-cwfcu-ncua-exam',
    name: 'NCUA Exam Readiness Folder Assembly ⭐',
    industry: 'Credit Union',
    throughput: 'Continuous · every 15 min',
    status: 'Active',
    stages: [
      mkStage('lookup',  'Aggregate Folder %',  'ncua_aggregate_scores'),
      mkStage('analyze', 'Blocker Identify',    'ncua_identify_blockers'),
      mkStage('analyze', 'Trajectory Forecast', 'ncua_forecast_trajectory'),
      mkStage('extract', 'Bundle (PDF/JSON)',   'ncua_assemble_bundle'),
    ],
    stats: { avgLatency: '12s', accuracy: '100%', autoApprove: '—', lastRun: '< 1 min ago' },
  },

  /* ─────────── Boler · Manufacturing · Multi-Division (4 pipelines) ─────────── */
  {
    id: 'pipe-boler-carrier-ingest',
    name: 'Carrier File Ingest + Extraction',
    industry: 'Manufacturing · Multi-Division',
    throughput: '6 carrier files / month · 2,847 lives',
    status: 'Active',
    stages: [
      mkStage('extract', 'S3 Drop Detect',      'carrier_file_detect'),
      mkStage('extract', 'BDA Carrier Extract', 'carrier_file_extract'),
      mkStage('analyze', 'Roster Match (EE ID)','match_employee_roster'),
      mkStage('lookup',  'Division Lookup',     'lookup_division'),
      mkStage('decide',  'Stage for Allocation','stage_for_allocation'),
    ],
    stats: { avgLatency: '2.8s', accuracy: '99.7%', autoApprove: '96%', lastRun: '4 min ago' },
  },
  {
    id: 'pipe-boler-exception-detection',
    name: 'Exception Detection + Auto-Reclassification',
    industry: 'Manufacturing · Multi-Division',
    throughput: '7 exceptions/mo · 4 auto-fixed',
    status: 'Active',
    stages: [
      mkStage('analyze', 'Variance Scan',        'detect_exception'),
      mkStage('analyze', 'Carrier Rate Drift',   'detect_carrier_drift'),
      mkStage('lookup',  'HRIS Cross-Check',     'hris_cross_check'),
      mkStage('extract', 'Reclassification Brief','draft_reclassification'),
      mkStage('decide',  'Auto-Fix vs HITL',     'route_exception'),
    ],
    stats: { avgLatency: '3.6s', accuracy: '97.2%', autoApprove: '57%', lastRun: '< 1 min ago' },
  },
  {
    id: 'pipe-boler-2stage-approval',
    name: 'Two-Stage Approval (Benefits → CFO)',
    industry: 'Manufacturing · Multi-Division',
    throughput: 'Monthly close cycle',
    status: 'Active',
    stages: [
      mkStage('extract', 'Allocation Bundle',    'assemble_allocation_bundle'),
      mkStage('decide',  'Benefits Mgr Review',  'benefits_manager_review'),
      mkStage('analyze', 'Material Variance Flag','flag_material_variance'),
      mkStage('decide',  'CFO Sign-Off',         'cfo_signoff'),
      mkStage('notify',  'Audit Trail Commit',   'commit_audit_trail'),
    ],
    stats: { avgLatency: '1.1 days', accuracy: '100%', autoApprove: '—', lastRun: '2 hr ago' },
  },
  {
    id: 'pipe-boler-je-distribution',
    name: 'JE Generation + S3 Distribution ⭐',
    industry: 'Manufacturing · Multi-Division',
    throughput: '5 divisions × 12 months · $15.4M/yr',
    status: 'Active',
    stages: [
      mkStage('extract',   'Draft Journal Entry', 'draft_journal_entry'),
      mkStage('calculate', 'Division Splits',     'compute_division_splits'),
      mkStage('analyze',   'GL Code Validate',    'validate_gl_codes'),
      mkStage('extract',   'Per-Division Files',  'generate_division_files'),
      mkStage('notify',    'S3 Distribute',       'distribute_to_division_s3'),
    ],
    stats: { avgLatency: '18s', accuracy: '100%', autoApprove: '100%', lastRun: '6 min ago' },
  },
];

/* ═════════════════════ industry theme (cards) ═════════════════════ */

const INDUSTRY_THEME: Record<IndustryKey, { bg: string; color: string; path: string }> = {
  'Financial Services': {
    bg: '#eff6ff', color: '#2563eb',
    path: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  'Commercial Insurance': {
    bg: '#f5f3ff', color: '#7c3aed',
    path: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  },
  'Healthcare Payers': {
    bg: '#fef2f2', color: '#dc2626',
    path: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  },
  'Aerospace & Defense': {
    bg: '#fff7ed', color: '#ea580c',
    path: 'M12 19l9 2-9-18-9 18 9-2zm0 0v-8',
  },
  'Supply Chain & Manufacturing': {
    bg: '#f0fdfa', color: '#0f766e',
    path: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  },
  'Nuclear Operations & Reliability': {
    bg: '#eef2ff', color: '#1e3a8a',
    path: 'M12 2a10 10 0 100 20 10 10 0 000-20zm-7.5 7.5l15 5m0-5l-15 5M12 12m-3 0a3 3 0 106 0 3 3 0 10-6 0',
  },
  'Telecommunications': {
    bg: '#fef2f2', color: '#b91c1c',
    path: 'M8.111 16.404a5.5 5.5 0 010-7.778m7.778 0a5.5 5.5 0 010 7.778m-9.9 2.121a8.5 8.5 0 010-12.02m12.02 0a8.5 8.5 0 010 12.02M12 14a2 2 0 100-4 2 2 0 000 4z',
  },
  'Supply Chain Orchestrator': {
    bg: '#f0fdfa', color: '#0f766e',
    path: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  },
  'Hospitality & Travel': {
    bg: '#f5f3ff', color: '#7c3aed',
    path: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  },
  'Commercial Real Estate': {
    bg: '#f0f9ff', color: '#0369a1',
    path: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  },
  'Oil & Gas — Midstream': {
    bg: '#fffbeb', color: '#b45309',
    path: 'M3 12l9-9 9 9M5 10v10a1 1 0 001 1h12a1 1 0 001-1V10',
  },
  'Credit Union': {
    bg: '#ede9fe', color: '#6c47ff',
    path: 'M3 21h18M3 10h18M5 6l7-3 7 3M4 10v11m16-11v11M8 14v3m4-3v3m4-3v3',
  },
  'Manufacturing · Multi-Division': {
    bg: '#ede9fe', color: '#6c47ff',
    path: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10',
  },
};

const INDUSTRY_CHIP_CLASS: Record<IndustryKey, string> = {
  'Financial Services':                 'chip-blue',
  'Commercial Insurance':               'chip-purple',
  'Healthcare Payers':                  'chip-red',
  'Aerospace & Defense':                'chip-amber',
  'Supply Chain & Manufacturing':       'chip-green',
  'Nuclear Operations & Reliability':   'chip-blue',
  'Telecommunications':                 'chip-red',
  'Supply Chain Orchestrator':          'chip-green',
  'Hospitality & Travel':               'chip-purple',
  'Commercial Real Estate':             'chip-blue',
  'Oil & Gas — Midstream':              'chip-amber',
  'Credit Union':                       'chip-purple',
  'Manufacturing · Multi-Division':     'chip-purple',
};

const FILTERS: FilterKey[] = [
  'All', 'Financial', 'Insurance', 'Healthcare', 'Aerospace',
  'Supply Chain & Manufacturing', 'Nuclear Operations', 'Telecommunications',
  'Supply Chain Orchestrator', 'Hospitality & Travel', 'Commercial Real Estate',
  'Oil & Gas — Midstream',
  'Credit Union',
  'Manufacturing · Multi-Division',
];
const FILTER_MATCH: Record<FilterKey, (i: IndustryKey) => boolean> = {
  'All':                           () => true,
  'Financial':                     (i) => i === 'Financial Services',
  'Insurance':                     (i) => i === 'Commercial Insurance',
  'Healthcare':                    (i) => i === 'Healthcare Payers',
  'Aerospace':                     (i) => i === 'Aerospace & Defense',
  'Supply Chain & Manufacturing':  (i) => i === 'Supply Chain & Manufacturing',
  'Nuclear Operations':            (i) => i === 'Nuclear Operations & Reliability',
  'Telecommunications':            (i) => i === 'Telecommunications',
  'Supply Chain Orchestrator':     (i) => i === 'Supply Chain Orchestrator',
  'Hospitality & Travel':          (i) => i === 'Hospitality & Travel',
  'Commercial Real Estate':        (i) => i === 'Commercial Real Estate',
  'Oil & Gas — Midstream':         (i) => i === 'Oil & Gas — Midstream',
  'Credit Union':                  (i) => i === 'Credit Union',
  'Manufacturing · Multi-Division': (i) => i === 'Manufacturing · Multi-Division',
};

/** Convert "elapsed milliseconds" into a "Just now / X sec ago / X min ago"
 *  short string. Used to render the cert pipeline's lastRun from /cycle-history.
 */
function _humanizeAgo(ms: number): string {
  if (ms < 0) return 'Just now';
  const sec = Math.floor(ms / 1000);
  if (sec < 5)    return 'Just now';
  if (sec < 60)   return `${sec} sec ago`;
  const min = Math.floor(sec / 60);
  if (min < 60)   return `${min} min ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24)    return `${hr} hr ago`;
  const day = Math.floor(hr / 24);
  return `${day} day${day === 1 ? '' : 's'} ago`;
}


/** Map demoMode → which IndustryKey rows are visible. */
function isPipelineVisibleInDemoMode(industry: IndustryKey, mode: string): boolean {
  if (mode === 'all') return true;
  if (mode === 'nuclear_operations' || mode === 'stp') return industry === 'Nuclear Operations & Reliability';
  if (mode === 'supply_manufacturing' || mode === 'manufacturing' || mode === 'supply_chain') return industry === 'Supply Chain & Manufacturing';
  if (mode === 'financial_services') return industry === 'Financial Services';
  if (mode === 'insurance_underwriting') return industry === 'Commercial Insurance';
  if (mode.startsWith('healthcare')) return industry === 'Healthcare Payers';
  if (mode === 'aerospace_defense') return industry === 'Aerospace & Defense';
  if (mode === 'telecommunications' || mode === 'verizon_far_edge') return industry === 'Telecommunications';
  // EPROD — both the industry parent ('oil_gas_midstream') and the customer
  // demo ('eprod') match the 6 EPROD pipelines.
  if (mode === 'oil_gas_midstream' || mode === 'eprod') return industry === 'Oil & Gas — Midstream';
  // CWFCU — both the industry parent ('credit_union') and customer demo
  // ('cwfcu') match the 8 CWFCU pipelines.
  if (mode === 'credit_union' || mode === 'cwfcu') return industry === 'Credit Union';
  // Boler — Manufacturing · Multi-Division
  if (mode === 'manufacturing_multi_division' || mode === 'boler') return industry === 'Manufacturing · Multi-Division';
  // Agentic Enterprise umbrella matches all 3 sub-domains; specific sub-modes
  // match only their own pipeline.
  if (mode === 'agentic_enterprise') {
    return industry === 'Supply Chain Orchestrator'
        || industry === 'Hospitality & Travel'
        || industry === 'Commercial Real Estate';
  }
  if (mode === 'supply_chain_orchestrator') return industry === 'Supply Chain Orchestrator';
  if (mode === 'hospitality')               return industry === 'Hospitality & Travel';
  if (mode === 'commercial_real_estate')    return industry === 'Commercial Real Estate';
  return false;
}

/* ═════════════════════ run/toast state ═════════════════════ */

interface StageRun {
  state: 'pending' | 'running' | 'done';
  durationMs?: number;
}

interface RunState {
  pipelineId: string;
  startedAt: number;
  stageRuns: StageRun[];
  completed: boolean;
}

interface Toast { message: string; kind: 'success' | 'error' | 'info' }

type Tab = 'config' | 'schema' | 'history';

/* ═════════════════════ main component ═════════════════════ */

/** Map a backend `/pipelines/details` row → frontend Pipeline type. */
function _apiToPipeline(row: any): Pipeline | null {
  if (!row || !row.id) return null;
  const industry = (row.industry_label || '').trim() as IndustryKey;
  // Only accept industries this page knows about
  const knownIndustries: IndustryKey[] = [
    'Financial Services', 'Commercial Insurance', 'Healthcare Payers',
    'Aerospace & Defense', 'Supply Chain & Manufacturing',
    'Nuclear Operations & Reliability', 'Telecommunications',
  ];
  if (!knownIndustries.includes(industry)) return null;
  const stages = Array.isArray(row.stages)
    ? row.stages.map((s: any) => ({
        id: s.id || `stage-${s.action || s.label || Math.random()}`,
        kind: s.type || 'execute',
        label: s.label || s.action || '',
        action: s.action || '',
        config: s.config || {},
        schema: s.schema || {},
      }))
    : [];
  const stats = row.stats || {};
  return {
    id:         row.id,
    name:       row.name || '',
    industry,
    throughput: row.throughput || '',
    status:     (row.status || 'Active') as Pipeline['status'],
    stages,
    stats: {
      avgLatency: stats.avg_latency  ?? stats.avgLatency  ?? '—',
      accuracy:   stats.accuracy     ?? '—',
      autoApprove: stats.auto_approve ?? stats.autoApprove ?? '—',
      lastRun:    stats.last_run     ?? stats.lastRun    ?? '—',
    },
  };
}

export default function PipelinesPage() {
  // Live pipelines from the backend `/pipelines/details` endpoint. The
  // hardcoded INITIAL_PIPELINES is now an offline-only fallback that's
  // suppressed when the API returns ≥1 row.
  const detailsQuery = useQuery<{ items: any[] }>({
    queryKey: ['pipelines-details'],
    queryFn: async () => {
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/pipelines/details?limit=200`);
      if (!r.ok) return { items: [] };
      return r.json();
    },
    retry: false,
    staleTime: 30_000,
  });

  // Live telecom cycle history — used to override the hardcoded "Last run"
  // on the cert pipeline (pipe-tel-certification) so the Pipelines page
  // reflects what actually happened, not a stale sample timestamp.
  // Polls every 10 sec so a fresh cycle shows up within ~10 sec of completing.
  const telecomHistoryQuery = useQuery<{ items: any[] }>({
    queryKey: ['telecom-cycle-history'],
    queryFn: async () => {
      const r = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/telecommunications/cycle-history?limit=5`);
      if (!r.ok) return { items: [] };
      return r.json();
    },
    retry: false,
    staleTime: 10_000,
    refetchInterval: 10_000,
  });

  const apiPipelines = useMemo<Pipeline[]>(() => {
    const rows = detailsQuery.data?.items ?? [];
    return rows.map(_apiToPipeline).filter((p): p is Pipeline => p !== null);
  }, [detailsQuery.data]);

  // Merge: API rows win on duplicate id, but the hardcoded INITIAL_PIPELINES
  // for hero demos (CBB / STP / Telecom) always flow through so the user
  // sees them even when only some pipelines are seeded in Cosmos DB.
  const mergedInitial: Pipeline[] = useMemo(() => {
    if (apiPipelines.length === 0) return INITIAL_PIPELINES;
    const seen = new Set(apiPipelines.map((p) => p.id));
    const extras = INITIAL_PIPELINES.filter((p) => !seen.has(p.id));
    return [...apiPipelines, ...extras];
  }, [apiPipelines]);
  // Patch the cert pipeline with live cycle history. If a telecom cycle
  // completed recently, replace the hardcoded "Last run: 32 min ago" with
  // the actual time-ago + tick the throughput by 1 cycle.
  const pipelinesWithLiveHistory: Pipeline[] = useMemo(() => {
    const items = telecomHistoryQuery.data?.items ?? [];
    if (items.length === 0) return mergedInitial;
    const latest = items[0];
    const endedAt = latest.ended_at as number | undefined;
    if (!endedAt) return mergedInitial;
    const ago = _humanizeAgo(Date.now() - endedAt);
    const triggerSuffix = latest.trigger === 's3_event' ? ' (Blob trigger)' : '';
    return mergedInitial.map((p) => {
      if (p.id !== 'pipe-tel-certification') return p;
      return {
        ...p,
        stats: {
          ...p.stats,
          lastRun: `${ago}${triggerSuffix}`,
        },
      };
    });
  }, [mergedInitial, telecomHistoryQuery.data]);

  const [pipelines, setPipelines] = useState<Pipeline[]>(pipelinesWithLiveHistory);

  // Re-sync pipelines state when either the base pipelines or the cycle
  // history changes — both feed into pipelinesWithLiveHistory.
  useEffect(() => {
    setPipelines(pipelinesWithLiveHistory);
  }, [pipelinesWithLiveHistory]);
  const [filter, setFilter] = useState<FilterKey>('All');
  const [mode, setMode] = useState<'list' | 'editor'>('list');
  const [editorId, setEditorId] = useState<string | null>(null);
  const [stagePanel, setStagePanel] = useState<{ pipelineId: string; stageId: string; tab: Tab } | null>(null);
  const [runs, setRuns] = useState<Record<string, RunState>>({});
  const [toast, setToast] = useState<Toast | null>(null);
  const [runOutput, setRunOutput] = useState<string | null>(null); // pipelineId whose output to show
  const [wizardOpen, setWizardOpen] = useState(false);

  // Stable refs to cancel animation timers if user navigates away.
  const timersRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  // Demo-mode filter applies BEFORE the in-page chip filter — anything
  // outside the active industry is invisible regardless of chip choice.
  const [demoMode] = useDemoMode();
  const visible = useMemo(
    () => pipelines
      .filter((p) => isPipelineVisibleInDemoMode(p.industry, demoMode))
      .filter((p) => FILTER_MATCH[filter](p.industry)),
    [pipelines, filter, demoMode],
  );

  // When the demo mode flips, reset the chip filter to 'All' so the user
  // doesn't end up on a chip that's now empty.
  useEffect(() => { setFilter('All'); }, [demoMode]);

  const activePanelStage = stagePanel
    ? pipelines.find((p) => p.id === stagePanel.pipelineId)?.stages?.find((s) => s.id === stagePanel.stageId) || null
    : null;

  const activePanelPipeline = stagePanel
    ? pipelines.find((p) => p.id === stagePanel.pipelineId) || null
    : null;

  const editorPipeline = editorId ? pipelines.find((p) => p.id === editorId) || null : null;

  const showToast = (message: string, kind: Toast['kind'] = 'success') => {
    setToast({ message, kind });
    setTimeout(() => setToast(null), 2000);
  };

  const updateStage = (pipelineId: string, stageId: string, patch: Partial<StageConfig>) => {
    setPipelines((all) => all.map((p) => {
      if (p.id !== pipelineId) return p;
      return {
        ...p,
        stages: p.stages.map((s) => s.id === stageId ? { ...s, config: { ...s.config, ...patch } } : s),
      };
    }));
  };

  const runPipeline = (pipelineId: string) => {
    const pipeline = pipelines.find((p) => p.id === pipelineId);
    if (!pipeline) return;

    // Cancel any prior run for this pipeline.
    const started = Date.now();
    setRuns((r) => ({
      ...r,
      [pipelineId]: {
        pipelineId,
        startedAt: started,
        stageRuns: pipeline.stages.map(() => ({ state: 'pending' })),
        completed: false,
      },
    }));

    // Walk stages sequentially: for each, mark running, wait 800-1400ms, mark done.
    let cumulative = 0;
    pipeline.stages.forEach((_, idx) => {
      const duration = 800 + Math.floor(Math.random() * 600);
      const tRunning = cumulative;
      const tDone = cumulative + duration;
      cumulative = tDone;

      timersRef.current.push(setTimeout(() => {
        setRuns((r) => {
          const prev = r[pipelineId];
          if (!prev) return r;
          const stageRuns = prev.stageRuns.slice();
          stageRuns[idx] = { state: 'running' };
          return { ...r, [pipelineId]: { ...prev, stageRuns } };
        });
      }, tRunning));

      timersRef.current.push(setTimeout(() => {
        setRuns((r) => {
          const prev = r[pipelineId];
          if (!prev) return r;
          const stageRuns = prev.stageRuns.slice();
          stageRuns[idx] = { state: 'done', durationMs: duration };
          const isLast = idx === pipeline.stages.length - 1;
          return {
            ...r,
            [pipelineId]: { ...prev, stageRuns, completed: isLast },
          };
        });
        if (idx === pipeline.stages.length - 1) {
          showToast(`${pipeline.name} completed`, 'success');
        }
      }, tDone));
    });
  };

  return (
    <>
      <Head><title>Pipelines | APEX</title></Head>

      {mode === 'list' && (
        <ListMode
          pipelines={visible}
          filter={filter}
          setFilter={setFilter}
          onOpen={(id) => { setEditorId(id); setMode('editor'); }}
          onRun={runPipeline}
          runs={runs}
          onStageClick={(pipelineId, stageId) => setStagePanel({ pipelineId, stageId, tab: 'config' })}
          onViewOutput={(id) => setRunOutput(id)}
          onNewPipeline={() => setWizardOpen(true)}
          onRunAll={() => { visible.forEach((p) => runPipeline(p.id)); showToast(`Running ${visible.length} pipelines`, 'info'); }}
        />
      )}

      {mode === 'editor' && editorPipeline && (
        <EditorMode
          pipeline={editorPipeline}
          onBack={() => { setMode('list'); setEditorId(null); }}
          onRun={() => runPipeline(editorPipeline.id)}
          runState={runs[editorPipeline.id]}
          onStageClick={(stageId) => setStagePanel({ pipelineId: editorPipeline.id, stageId, tab: 'config' })}
          onStageDelete={(stageId) => {
            setPipelines((all) => all.map((p) =>
              p.id === editorPipeline.id ? { ...p, stages: p.stages.filter((s) => s.id !== stageId) } : p,
            ));
            showToast('Stage removed');
          }}
          onStageInsert={(afterIndex, kind, label, actionName) => {
            setPipelines((all) => all.map((p) => {
              if (p.id !== editorPipeline.id) return p;
              const newStage = mkStage(kind, label, actionName);
              const stages = p.stages.slice();
              stages.splice(afterIndex + 1, 0, newStage);
              return { ...p, stages };
            }));
            showToast('Stage added');
          }}
          onStageMove={(stageId, direction) => {
            setPipelines((all) => all.map((p) => {
              if (p.id !== editorPipeline.id) return p;
              const i = p.stages.findIndex((s) => s.id === stageId);
              if (i < 0) return p;
              const j = direction === 'up' ? i - 1 : i + 1;
              if (j < 0 || j >= p.stages.length) return p;
              const stages = p.stages.slice();
              [stages[i], stages[j]] = [stages[j], stages[i]];
              return { ...p, stages };
            }));
          }}
        />
      )}

      {/* Right-side stage detail panel */}
      {stagePanel && activePanelStage && activePanelPipeline && (
        <StageDetailPanel
          stage={activePanelStage}
          pipelineName={activePanelPipeline.name}
          tab={stagePanel.tab}
          onTab={(t) => setStagePanel({ ...stagePanel, tab: t })}
          onClose={() => setStagePanel(null)}
          onSave={(patch) => {
            updateStage(stagePanel.pipelineId, stagePanel.stageId, patch);
            showToast('Saved ✓');
          }}
          onDelete={() => {
            setPipelines((all) => all.map((p) =>
              p.id === stagePanel.pipelineId
                ? { ...p, stages: p.stages.filter((s) => s.id !== stagePanel.stageId) }
                : p,
            ));
            setStagePanel(null);
            showToast('Stage deleted');
          }}
        />
      )}

      {/* Run output panel */}
      {runOutput && (
        <RunOutputPanel
          pipeline={pipelines.find((p) => p.id === runOutput)!}
          runState={runs[runOutput]}
          onClose={() => setRunOutput(null)}
        />
      )}

      {wizardOpen && (
        <NewPipelineWizard
          onCancel={() => setWizardOpen(false)}
          onDeploy={(draft) => {
            const id = `pipe-${Math.random().toString(36).slice(2, 8)}`;
            const newPipeline: Pipeline = {
              id,
              name: draft.name,
              industry: draft.industry,
              throughput: 'New — awaiting first run',
              status: 'Deploying',
              stages: draft.stages,
              stats: { avgLatency: '—', lastRun: 'Never' },
            };
            setPipelines((all) => [newPipeline, ...all]);
            setWizardOpen(false);
            showToast(`Deploying ${draft.name}…`, 'info');
            // Transition to Active after 2s per spec
            timersRef.current.push(setTimeout(() => {
              setPipelines((all) => all.map((p) => p.id === id ? { ...p, status: 'Active' } : p));
              showToast(`${draft.name} deployed`, 'success');
            }, 2000));
          }}
        />
      )}

      {toast && <ToastBubble toast={toast} />}
    </>
  );
}

/* ═════════════════════ LIST MODE ═════════════════════ */

function ListMode({
  pipelines, filter, setFilter,
  onOpen, onRun, onStageClick, onViewOutput, onNewPipeline, onRunAll,
  runs,
}: {
  pipelines: Pipeline[];
  filter: FilterKey;
  setFilter: (f: FilterKey) => void;
  onOpen: (id: string) => void;
  onRun: (id: string) => void;
  onStageClick: (pipelineId: string, stageId: string) => void;
  onViewOutput: (id: string) => void;
  onNewPipeline: () => void;
  onRunAll: () => void;
  runs: Record<string, RunState>;
}) {
  // FEATURE 3 — Workflow Debt Eliminator toggle.
  const [valueMapView, setValueMapView] = useState(false);
  return (
    <>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 18 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Pipelines</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>
            Industry-specific automation pipelines built from chained action factories
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-success" onClick={onRunAll}>
            <Icon name="play" className="" style={{ width: 15, height: 15 }} />
            Run All
          </button>
          <button className="btn btn-primary" onClick={onNewPipeline}>
            <Icon name="plus" className="" style={{ width: 15, height: 15 }} />
            New Pipeline
          </button>
        </div>
      </div>

      {/* Filter chips + Value Map toggle */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, marginBottom: 20, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                padding: '7px 14px',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                borderRadius: 99,
                border: `1px solid ${filter === f ? '#2563eb' : '#e2e8f0'}`,
                background: filter === f ? '#2563eb' : '#fff',
                color: filter === f ? '#fff' : '#475569',
                transition: 'all .15s',
              }}
            >
              {f}
            </button>
          ))}
        </div>
        <ValueMapSwitch active={valueMapView} onChange={setValueMapView} />
      </div>

      {/* Cards */}
      {valueMapView ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {pipelines.length === 0 ? (
            <div className="card" style={{ padding: 32, textAlign: 'center', color: '#94a3b8' }}>
              No pipelines match this filter.
            </div>
          ) : pipelines.map((p) => (
            <ValueMapCard key={p.id} pipeline={p} />
          ))}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {pipelines.length === 0 ? (
            <div className="card" style={{ padding: 32, textAlign: 'center', color: '#94a3b8' }}>
              No pipelines match this filter.
            </div>
          ) : pipelines.map((p) => (
            <PipelineCard
              key={p.id}
              pipeline={p}
              run={runs[p.id]}
              onOpen={() => onOpen(p.id)}
              onRun={() => onRun(p.id)}
              onStageClick={(stageId) => onStageClick(p.id, stageId)}
              onViewOutput={() => onViewOutput(p.id)}
            />
          ))}
        </div>
      )}
    </>
  );
}

function ValueMapSwitch({ active, onChange }: { active: boolean; onChange: (v: boolean) => void }) {
  const opts: { key: boolean; label: string }[] = [
    { key: false, label: 'Pipeline view' },
    { key: true,  label: 'Value Map' },
  ];
  return (
    <div style={{
      display: 'inline-flex', background: '#f1f5f9', borderRadius: 10, padding: 4, gap: 2,
      border: '1px solid #e2e8f0',
    }}>
      {opts.map((o) => (
        <button
          key={String(o.key)}
          onClick={() => onChange(o.key)}
          style={{
            padding: '6px 14px',
            fontSize: 12,
            fontWeight: 600,
            borderRadius: 8,
            border: 'none',
            cursor: 'pointer',
            background: active === o.key ? '#fff' : 'transparent',
            color: active === o.key ? '#0f172a' : '#64748b',
            boxShadow: active === o.key ? '0 1px 2px rgba(15,23,42,.08)' : 'none',
          }}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

function PipelineCard({
  pipeline, run, onOpen, onRun, onStageClick, onViewOutput,
}: {
  pipeline: Pipeline;
  run?: RunState;
  onOpen: () => void;
  onRun: () => void;
  onStageClick: (stageId: string) => void;
  onViewOutput: () => void;
}) {
  const theme = INDUSTRY_THEME[pipeline.industry];
  const chipClass = INDUSTRY_CHIP_CLASS[pipeline.industry];
  const running = run && !run.completed && run.stageRuns.some((s) => s.state !== 'pending');
  const completed = run && run.completed;
  const progressPct = run ? (run.stageRuns.filter((s) => s.state === 'done').length / run.stageRuns.length) * 100 : 0;

  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #f8fafc', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10, background: theme.bg,
            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
          }}>
            <svg style={{ width: 18, height: 18, color: theme.color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.path} />
            </svg>
          </div>
          <div style={{ minWidth: 0 }}>
            <button
              onClick={onOpen}
              style={{
                background: 'none', border: 'none', padding: 0, cursor: 'pointer',
                fontWeight: 700, fontSize: 16, color: '#0f172a', textAlign: 'left',
              }}
            >
              {pipeline.name}
            </button>
            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
              <span className={chipClass} style={{ fontSize: 10, marginRight: 8 }}>{pipeline.industry}</span>
              {pipeline.throughput}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
          <span className={completed ? 'chip-green' : running ? 'chip-amber' : 'chip-green'}>
            {completed ? '✓ Completed' : running ? '⟳ Running…' : pipeline.status}
          </span>
          <button className="btn btn-secondary btn-sm" onClick={onOpen}>Open</button>
          <button
            className={running ? 'btn btn-secondary btn-sm' : 'btn btn-success btn-sm'}
            onClick={onRun}
            disabled={!!running}
            style={running ? { opacity: 0.7 } : undefined}
          >
            {running ? '⟳ Running…' : '▶ Run'}
          </button>
        </div>
      </div>

      {/* Stage flow */}
      <div style={{ padding: '16px 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, overflowX: 'auto', paddingBottom: 6 }}>
          {pipeline.stages.map((s, i) => {
            const stageRun = run?.stageRuns[i];
            return (
              <React.Fragment key={s.id}>
                <StageChip
                  stage={s}
                  runState={stageRun}
                  onClick={() => onStageClick(s.id)}
                />
                {i < pipeline.stages.length - 1 && <div className="pipeline-arrow">→</div>}
              </React.Fragment>
            );
          })}
        </div>

        {/* Progress bar + View Output */}
        {run && (
          <div style={{ marginTop: 12 }}>
            <div className="progress-bar" style={{ height: 4 }}>
              <div
                className="progress-fill"
                style={{
                  width: `${progressPct}%`,
                  background: completed ? '#059669' : '#2563eb',
                }}
              />
            </div>
            {completed && (
              <div style={{ marginTop: 10, display: 'flex', gap: 10, alignItems: 'center' }}>
                <button
                  onClick={onViewOutput}
                  className="btn btn-secondary btn-sm"
                >
                  <Icon name="eye" className="" style={{ width: 13, height: 13 }} />
                  View Output
                </button>
                <span style={{ fontSize: 11, color: '#64748b' }}>
                  Completed in {(run.stageRuns.reduce((a, r) => a + (r.durationMs || 0), 0) / 1000).toFixed(1)}s
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stats footer */}
      <div style={{
        padding: '12px 20px',
        background: '#f8fafc',
        display: 'flex', alignItems: 'center', gap: 24, flexWrap: 'wrap',
      }}>
        <StatItem label="Avg latency" value={pipeline.stats.avgLatency} />
        {pipeline.stats.accuracy && <StatItem label="Accuracy" value={pipeline.stats.accuracy} color="#16a34a" />}
        {pipeline.stats.autoApprove && <StatItem label="Auto-approve" value={pipeline.stats.autoApprove} />}
        <StatItem label="Last run" value={pipeline.stats.lastRun} />
      </div>
    </div>
  );
}

function StatItem({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div style={{ fontSize: 12, color: '#64748b' }}>
      {label}: <strong style={{ color: color || '#0f172a' }}>{value}</strong>
    </div>
  );
}

function StageChip({ stage, runState, onClick }: { stage: Stage; runState?: StageRun; onClick: () => void }) {
  const theme = STAGE_TYPES[stage.kind];
  const isRunning = runState?.state === 'running';
  const isDone    = runState?.state === 'done';

  return (
    <button
      type="button"
      onClick={onClick}
      className={`pipeline-stage ${isRunning ? 'animate-pulse' : ''}`}
      style={{
        background: isDone ? '#dcfce7' : isRunning ? '#dbeafe' : theme.bg,
        border: `1px solid ${isDone ? '#16a34a' : isRunning ? '#2563eb' : theme.border}`,
        cursor: 'pointer',
        textAlign: 'center',
        minWidth: 118,
        transition: 'all .2s',
      }}
      onMouseOver={(e) => {
        if (!isRunning && !isDone) {
          e.currentTarget.style.transform = 'translateY(-1px)';
          e.currentTarget.style.boxShadow = `0 4px 10px ${theme.color}22`;
        }
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{
        fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
        letterSpacing: '.06em',
        color: isDone ? '#15803d' : isRunning ? '#1d4ed8' : theme.color,
        marginBottom: 4,
      }}>
        {isDone ? '✓ Done' : isRunning ? '⟳ Running' : theme.label}
      </div>
      <div style={{ fontSize: 12, fontWeight: 600, color: isDone ? '#166534' : '#0f172a' }}>
        {stage.label}
      </div>
      {runState?.durationMs !== undefined && (
        <div style={{ fontSize: 10, color: '#64748b', marginTop: 3 }}>
          {(runState.durationMs / 1000).toFixed(1)}s
        </div>
      )}
    </button>
  );
}

/* ═════════════════════ EDITOR MODE ═════════════════════ */

function EditorMode({
  pipeline, onBack, onRun, runState,
  onStageClick, onStageDelete, onStageInsert, onStageMove,
}: {
  pipeline: Pipeline;
  onBack: () => void;
  onRun: () => void;
  runState?: RunState;
  onStageClick: (stageId: string) => void;
  onStageDelete: (stageId: string) => void;
  onStageInsert: (afterIndex: number, kind: StageKind, label: string, actionName: string) => void;
  onStageMove: (stageId: string, direction: 'up' | 'down') => void;
}) {
  const [addAt, setAddAt] = useState<number | null>(null);
  const theme = INDUSTRY_THEME[pipeline.industry];
  const chipClass = INDUSTRY_CHIP_CLASS[pipeline.industry];
  const running = runState && !runState.completed && runState.stageRuns.some((s) => s.state !== 'pending');

  return (
    <>
      <button
        onClick={onBack}
        style={{ background: 'none', border: 'none', padding: 0, color: '#2563eb', cursor: 'pointer', fontSize: 13, marginBottom: 14 }}
      >
        ← Back to Pipelines
      </button>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 12, background: theme.bg,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <svg style={{ width: 20, height: 20, color: theme.color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.path} />
            </svg>
          </div>
          <div>
            <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>{pipeline.name}</h2>
            <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span className={chipClass} style={{ fontSize: 10 }}>{pipeline.industry}</span>
              <span className="chip-green" style={{ fontSize: 10 }}>{pipeline.status}</span>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>{pipeline.stages.length} stages</span>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="btn btn-secondary">Save</button>
          <button className="btn btn-success btn-lg" onClick={onRun} disabled={running}>
            <Icon name="play" className="" style={{ width: 16, height: 16 }} />
            {running ? 'Running…' : 'Run Pipeline'}
          </button>
        </div>
      </div>

      {/* Stage canvas */}
      <div className="card" style={{ padding: 24, marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 14 }}>
          Stages
        </div>
        <div style={{ display: 'flex', alignItems: 'stretch', gap: 0, overflowX: 'auto', paddingBottom: 8 }}>
          {pipeline.stages.map((stage, i) => {
            const stageRun = runState?.stageRuns[i];
            return (
              <React.Fragment key={stage.id}>
                <EditorStageCard
                  stage={stage}
                  number={i + 1}
                  runState={stageRun}
                  canMoveUp={i > 0}
                  canMoveDown={i < pipeline.stages.length - 1}
                  onClick={() => onStageClick(stage.id)}
                  onDelete={() => {
                    if (confirm(`Remove stage "${stage.label}"?`)) onStageDelete(stage.id);
                  }}
                  onMoveUp={() => onStageMove(stage.id, 'up')}
                  onMoveDown={() => onStageMove(stage.id, 'down')}
                />
                {i < pipeline.stages.length - 1 && (
                  <InsertStageGap onClick={() => setAddAt(i)} />
                )}
              </React.Fragment>
            );
          })}
          <div style={{ display: 'flex', alignItems: 'center', paddingLeft: 8 }}>
            <button
              onClick={() => setAddAt(pipeline.stages.length - 1)}
              style={{
                border: '2px dashed #cbd5e1',
                background: 'transparent',
                borderRadius: 12,
                padding: '22px 16px',
                minWidth: 140,
                minHeight: 110,
                cursor: 'pointer',
                color: '#64748b',
                fontSize: 12,
                fontWeight: 600,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 6,
              }}
            >
              <Icon name="plus" className="" style={{ width: 18, height: 18 }} />
              Add Stage
            </button>
          </div>
        </div>
      </div>

      {addAt !== null && (
        <InsertStageModal
          onCancel={() => setAddAt(null)}
          onConfirm={(kind, label, actionName) => {
            onStageInsert(addAt, kind, label, actionName);
            setAddAt(null);
          }}
        />
      )}

      {/* Pipeline settings */}
      <PipelineSettings pipeline={pipeline} />
    </>
  );
}

function EditorStageCard({
  stage, number, runState,
  canMoveUp, canMoveDown,
  onClick, onDelete, onMoveUp, onMoveDown,
}: {
  stage: Stage;
  number: number;
  runState?: StageRun;
  canMoveUp: boolean;
  canMoveDown: boolean;
  onClick: () => void;
  onDelete: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
}) {
  const theme = STAGE_TYPES[stage.kind];
  const isRunning = runState?.state === 'running';
  const isDone    = runState?.state === 'done';

  return (
    <div
      style={{
        minWidth: 180,
        maxWidth: 180,
        background: isDone ? '#dcfce7' : isRunning ? '#dbeafe' : theme.bg,
        border: `1.5px solid ${isDone ? '#16a34a' : isRunning ? '#2563eb' : theme.border}`,
        borderRadius: 14,
        padding: 14,
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
        position: 'relative',
        cursor: 'pointer',
        transition: 'all .15s',
      }}
      onClick={onClick}
      className={isRunning ? 'animate-pulse' : ''}
    >
      {/* Number + type badge */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600 }}>#{number}</span>
        <span style={{
          fontSize: 9, fontWeight: 700, letterSpacing: '.06em',
          padding: '2px 6px', borderRadius: 4,
          background: theme.color, color: '#fff',
        }}>
          {theme.label.toUpperCase()}
        </span>
      </div>

      {/* Name */}
      <div style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', lineHeight: 1.25 }}>
        {stage.label}
      </div>
      <div className="mono" style={{ fontSize: 10, color: '#64748b', wordBreak: 'break-all' }}>
        {stage.config.actionName}
      </div>

      {/* Action buttons */}
      <div
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', gap: 2 }}>
          <IconBtn disabled={!canMoveUp} onClick={onMoveUp} title="Move left">←</IconBtn>
          <IconBtn disabled={!canMoveDown} onClick={onMoveDown} title="Move right">→</IconBtn>
        </div>
        <div style={{ display: 'flex', gap: 2 }}>
          <IconBtn onClick={onClick} title="Edit">
            <Icon name="pencil" className="" style={{ width: 12, height: 12 }} />
          </IconBtn>
          <IconBtn onClick={onDelete} title="Delete" danger>
            <Icon name="trash" className="" style={{ width: 12, height: 12 }} />
          </IconBtn>
        </div>
      </div>

      {runState?.durationMs !== undefined && (
        <div style={{ fontSize: 10, color: '#64748b' }}>
          {(runState.durationMs / 1000).toFixed(1)}s
        </div>
      )}
    </div>
  );
}

function IconBtn({ children, onClick, disabled, title, danger }: {
  children: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
  title?: string;
  danger?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      style={{
        width: 22, height: 22, borderRadius: 5,
        border: 'none',
        background: 'transparent',
        color: danger ? '#dc2626' : '#64748b',
        cursor: disabled ? 'not-allowed' : 'pointer',
        fontSize: 12,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        opacity: disabled ? 0.3 : 1,
      }}
      onMouseOver={(e) => { if (!disabled) e.currentTarget.style.background = danger ? '#fee2e2' : '#f1f5f9'; }}
      onMouseOut={(e)  => { e.currentTarget.style.background = 'transparent'; }}
    >
      {children}
    </button>
  );
}

function InsertStageGap({ onClick }: { onClick: () => void }) {
  const [hover, setHover] = useState(false);
  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'flex', alignItems: 'center', position: 'relative',
        minWidth: hover ? 80 : 40, transition: 'min-width .2s',
      }}
    >
      <div style={{ flex: 1, height: 2, background: '#e2e8f0' }} />
      {hover && (
        <button
          onClick={onClick}
          style={{
            position: 'absolute', left: '50%', top: '50%',
            transform: 'translate(-50%, -50%)',
            width: 28, height: 28, borderRadius: '50%',
            border: '2px solid #2563eb', background: '#fff',
            color: '#2563eb', cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 14, fontWeight: 700,
          }}
          title="Insert stage here"
        >
          +
        </button>
      )}
      {!hover && <div style={{ color: '#cbd5e1', padding: '0 6px' }}>→</div>}
    </div>
  );
}

function InsertStageModal({
  onCancel, onConfirm,
}: {
  onCancel: () => void;
  onConfirm: (kind: StageKind, label: string, actionName: string) => void;
}) {
  const [kind, setKind] = useState<StageKind>('execute');
  const [label, setLabel] = useState('');
  const [actionName, setActionName] = useState('');

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 420 }}>
        <div style={{ padding: '18px 22px', borderBottom: '1px solid #f1f5f9' }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>Insert Stage</h3>
        </div>
        <div style={{ padding: 22, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label className="label">Action type</label>
            <select className="select" value={kind} onChange={(e) => setKind(e.target.value as StageKind)}>
              {STAGE_KIND_OPTIONS.map((k) => (
                <option key={k} value={k}>{STAGE_TYPES[k].label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Display label</label>
            <input
              className="input"
              value={label}
              placeholder="e.g. Fraud Check"
              onChange={(e) => setLabel(e.target.value)}
            />
          </div>
          <div>
            <label className="label">Action name (snake_case)</label>
            <input
              className="input mono"
              value={actionName}
              placeholder="e.g. fraud_check"
              onChange={(e) => setActionName(e.target.value)}
            />
          </div>
        </div>
        <div style={{ padding: '14px 22px', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
          <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
          <button
            className="btn btn-primary"
            disabled={!label.trim() || !actionName.trim()}
            onClick={() => onConfirm(kind, label.trim(), actionName.trim())}
          >
            Insert Stage
          </button>
        </div>
      </div>
    </div>
  );
}

function PipelineSettings({ pipeline }: { pipeline: Pipeline }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="card" style={{ overflow: 'hidden' }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          width: '100%', padding: '14px 20px',
          background: 'transparent', border: 'none',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          cursor: 'pointer',
          borderBottom: open ? '1px solid #f1f5f9' : 'none',
        }}
      >
        <span style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>Pipeline Settings</span>
        <span style={{ fontSize: 12, color: '#94a3b8' }}>{open ? '▾' : '▸'}</span>
      </button>
      {open && (
        <div style={{ padding: 20, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <div>
            <label className="label">Description</label>
            <textarea
              className="textarea"
              rows={3}
              defaultValue={`Automated ${pipeline.name.toLowerCase()} for ${pipeline.industry}.`}
            />
          </div>
          <div>
            <label className="label">Trigger</label>
            <select className="select" defaultValue="document">
              <option value="document">Document Upload</option>
              <option value="schedule">Schedule</option>
              <option value="api">API Event</option>
              <option value="manual">Manual</option>
            </select>
          </div>
          <div>
            <label className="label">On-success Slack channel</label>
            <input className="input" defaultValue="#ap-team" />
          </div>
          <div>
            <label className="label">On-failure email</label>
            <input className="input" defaultValue="ops@apex.ai" />
          </div>
          <div>
            <label className="label">SLA target (seconds)</label>
            <input className="input" type="number" defaultValue={15} />
          </div>
        </div>
      )}
    </div>
  );
}

/* ═════════════════════ STAGE DETAIL PANEL ═════════════════════ */

function StageDetailPanel({
  stage, pipelineName, tab, onTab, onClose, onSave, onDelete,
}: {
  stage: Stage;
  pipelineName: string;
  tab: Tab;
  onTab: (t: Tab) => void;
  onClose: () => void;
  onSave: (patch: Partial<StageConfig>) => void;
  onDelete: () => void;
}) {
  // Local form state initialized from the stage config
  const [cfg, setCfg] = useState<StageConfig>(stage.config);
  const theme = STAGE_TYPES[stage.kind];

  // Reset form when a different stage is opened.
  React.useEffect(() => { setCfg(stage.config); }, [stage.id]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      {/* Dark overlay */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.15)',
          zIndex: 95,
        }}
      />
      {/* Panel */}
      <div
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0, width: 420,
          background: '#fff', borderLeft: '1px solid #e2e8f0',
          boxShadow: '-8px 0 24px rgba(15,23,42,.06)',
          zIndex: 96, display: 'flex', flexDirection: 'column',
        }}
      >
        {/* Header */}
        <div style={{ padding: '18px 22px', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10 }}>
            <div style={{ minWidth: 0 }}>
              <span style={{
                fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                letterSpacing: '.06em', padding: '3px 8px', borderRadius: 6,
                background: theme.bg, color: theme.color, border: `1px solid ${theme.border}`,
              }}>
                {theme.label}
              </span>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginTop: 8 }}>
                {stage.label}
              </div>
              <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 2 }}>
                {pipelineName}
              </div>
            </div>
            <button
              onClick={onClose}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#9ca3af' }}
              aria-label="Close"
            >
              <svg style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tabs */}
          <div style={{ display: 'flex', marginTop: 14, gap: 4 }}>
            {(['config', 'schema', 'history'] as const).map((t) => (
              <button
                key={t}
                onClick={() => onTab(t)}
                style={{
                  padding: '8px 14px',
                  fontSize: 12,
                  fontWeight: 600,
                  background: 'none',
                  border: 'none',
                  borderBottom: tab === t ? '2px solid #2563eb' : '2px solid transparent',
                  color: tab === t ? '#2563eb' : '#94a3b8',
                  cursor: 'pointer',
                  textTransform: 'capitalize',
                }}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Body */}
        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 22 }}>
          {tab === 'config'  && <ConfigTab cfg={cfg} setCfg={setCfg} />}
          {tab === 'schema'  && <SchemaTab stage={stage} />}
          {tab === 'history' && <HistoryTab stage={stage} />}
        </div>

        {/* Footer */}
        {tab === 'config' && (
          <div style={{
            padding: '14px 22px', borderTop: '1px solid #f1f5f9',
            display: 'flex', justifyContent: 'space-between', gap: 10,
          }}>
            <button className="btn btn-danger btn-sm" onClick={onDelete}>Delete Stage</button>
            <button className="btn btn-primary" onClick={() => onSave(cfg)}>
              Save Changes
            </button>
          </div>
        )}
      </div>
    </>
  );
}

function ConfigTab({ cfg, setCfg }: { cfg: StageConfig; setCfg: (c: StageConfig) => void }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <Field label="Action Name">
        <input
          className="input mono"
          value={cfg.actionName}
          onChange={(e) => setCfg({ ...cfg, actionName: e.target.value })}
        />
      </Field>

      <Field label="Timeout (seconds)">
        <input
          className="input"
          type="number"
          min={5}
          max={300}
          value={cfg.timeoutSeconds}
          onChange={(e) => setCfg({ ...cfg, timeoutSeconds: Number(e.target.value) || 30 })}
        />
      </Field>

      <Field label="Retry on failure" inline>
        <Toggle
          checked={cfg.retryOnFailure}
          onChange={(v) => setCfg({ ...cfg, retryOnFailure: v })}
        />
      </Field>

      {cfg.retryOnFailure && (
        <Field label="Max retries">
          <input
            className="input"
            type="number"
            min={1}
            max={10}
            value={cfg.maxRetries}
            onChange={(e) => setCfg({ ...cfg, maxRetries: Number(e.target.value) || 3 })}
          />
        </Field>
      )}

      <Field label={`Confidence threshold (${cfg.confidenceThreshold}%)`}>
        <input
          type="range"
          min={0}
          max={100}
          value={cfg.confidenceThreshold}
          onChange={(e) => setCfg({ ...cfg, confidenceThreshold: Number(e.target.value) })}
          style={{ width: '100%' }}
        />
      </Field>

      <Field label="Input mapping (JSON)">
        <textarea
          className="textarea mono"
          rows={4}
          value={cfg.inputMapping}
          onChange={(e) => setCfg({ ...cfg, inputMapping: e.target.value })}
          style={{ fontSize: 11 }}
        />
      </Field>

      <Field label="Output mapping (JSON)">
        <textarea
          className="textarea mono"
          rows={4}
          value={cfg.outputMapping}
          onChange={(e) => setCfg({ ...cfg, outputMapping: e.target.value })}
          style={{ fontSize: 11 }}
        />
      </Field>

      <Field label="Condition (optional)">
        <textarea
          className="textarea"
          rows={2}
          placeholder="e.g. if confidence < 0.7"
          value={cfg.condition || ''}
          onChange={(e) => setCfg({ ...cfg, condition: e.target.value || undefined })}
        />
      </Field>
    </div>
  );
}

function Field({ label, children, inline }: { label: string; children: React.ReactNode; inline?: boolean }) {
  if (inline) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
        <label className="label" style={{ margin: 0 }}>{label}</label>
        {children}
      </div>
    );
  }
  return (
    <div>
      <label className="label">{label}</label>
      {children}
    </div>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      role="switch"
      aria-checked={checked}
      style={{
        width: 38, height: 22, borderRadius: 11,
        background: checked ? '#2563eb' : '#cbd5e1',
        border: 'none', cursor: 'pointer',
        position: 'relative',
        transition: 'background .15s',
      }}
    >
      <span style={{
        position: 'absolute', top: 2, left: checked ? 18 : 2,
        width: 18, height: 18, borderRadius: '50%', background: '#fff',
        transition: 'left .15s', boxShadow: '0 1px 3px rgba(0,0,0,.2)',
      }} />
    </button>
  );
}

function SchemaTab({ stage }: { stage: Stage }) {
  // Synthesize sample schema fields based on the stage kind so every stage
  // has something meaningful in the Schema tab even without a real backend.
  const samples = schemaSamplesFor(stage.kind);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>
          Input Schema
        </div>
        <SchemaRows rows={samples.input} direction="in" />
      </div>
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 8 }}>
          Output Schema
        </div>
        <SchemaRows rows={samples.output} direction="out" />
      </div>
    </div>
  );
}

interface SchemaRow { name: string; type: string; required?: boolean; description: string }

function SchemaRows({ rows, direction }: { rows: SchemaRow[]; direction: 'in' | 'out' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {rows.map((r) => (
        <div
          key={r.name}
          style={{
            padding: '8px 12px',
            background: direction === 'out' ? '#f0fdf4' : '#f8fafc',
            border: '1px solid #f1f5f9',
            borderRadius: 10,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span className="mono" style={{ fontSize: 12, color: direction === 'out' ? '#15803d' : '#1e40af' }}>
              {r.name}
            </span>
            <div style={{ display: 'flex', gap: 6 }}>
              {direction === 'in' && r.required && (
                <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 5px', borderRadius: 3, background: '#fee2e2', color: '#b91c1c' }}>
                  REQ
                </span>
              )}
              <span style={{ fontSize: 10, fontWeight: 600, padding: '2px 6px', borderRadius: 4, background: '#eff6ff', color: '#2563eb' }}>
                {r.type}
              </span>
            </div>
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>{r.description}</div>
        </div>
      ))}
    </div>
  );
}

function schemaSamplesFor(kind: StageKind): { input: SchemaRow[]; output: SchemaRow[] } {
  const base: Record<string, { input: SchemaRow[]; output: SchemaRow[] }> = {
    extract: {
      input:  [
        { name: 'document_uri',  type: 'string', required: true,  description: 'blob URI of the source document' },
        { name: 'blueprint_id',  type: 'string', required: true,  description: 'BDA blueprint identifier' },
        { name: 'language_hint', type: 'string', required: false, description: 'Optional ISO 639-1 code' },
      ],
      output: [
        { name: 'fields',            type: 'object',  description: 'Key/value map of extracted fields' },
        { name: 'confidence_scores', type: 'object',  description: 'Confidence per field' },
        { name: 'page_count',        type: 'integer', description: 'Number of pages processed' },
      ],
    },
    validate: {
      input:  [
        { name: 'record',  type: 'object', required: true, description: 'Record to validate' },
        { name: 'ruleset', type: 'string', required: true, description: 'Ruleset identifier' },
      ],
      output: [
        { name: 'valid',      type: 'boolean', description: 'Whether all checks passed' },
        { name: 'violations', type: 'array',   description: 'List of violated rules' },
      ],
    },
    decide: {
      input:  [
        { name: 'signals',   type: 'object', required: true, description: 'Aggregated inputs from upstream stages' },
        { name: 'policy_id', type: 'string', required: true, description: 'Decision policy identifier' },
      ],
      output: [
        { name: 'decision',   type: 'string', description: 'One of: approve, reject, review' },
        { name: 'reason',     type: 'string', description: 'Human-readable rationale' },
        { name: 'confidence', type: 'number', description: 'Decision confidence 0..1' },
      ],
    },
    notify: {
      input:  [
        { name: 'channel',   type: 'string', required: true,  description: 'Slack channel or email' },
        { name: 'template',  type: 'string', required: true,  description: 'Template identifier' },
        { name: 'variables', type: 'object', required: false, description: 'Template variables' },
      ],
      output: [
        { name: 'delivered',  type: 'boolean', description: 'Whether the notification was sent' },
        { name: 'message_id', type: 'string',  description: 'Provider message id' },
      ],
    },
  };

  const mapped: Record<StageKind, { input: SchemaRow[]; output: SchemaRow[] }> = {
    extract:   base.extract, analyze:   base.extract,
    validate:  base.validate, check:    base.validate,
    decide:    base.decide,   classify: base.decide,
    notify:    base.notify,   generate: base.notify,
    score:     base.decide,   calculate:base.decide, model: base.decide,
    execute:   base.validate, lookup:   base.extract, predict: base.decide,
  };
  return mapped[kind] || base.validate;
}

function HistoryTab({ stage }: { stage: Stage }) {
  // Generate deterministic sample runs based on the stage id so the data feels real
  const runs = useMemo(() => sampleHistory(stage.id), [stage.id]);

  return (
    <div>
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10 }}>
        Last {runs.length} runs
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {runs.map((r) => (
          <div
            key={r.id}
            style={{
              padding: '10px 12px',
              background: '#fff',
              border: '1px solid #f1f5f9',
              borderRadius: 10,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
              <span className="mono" style={{ fontSize: 11, color: '#0f172a' }}>{r.id}</span>
              <span className={`chip-${r.status === 'success' ? 'green' : r.status === 'timeout' ? 'amber' : 'red'}`} style={{ fontSize: 10 }}>
                {r.status === 'success' ? 'Success' : r.status === 'timeout' ? 'Timeout' : 'Failed'}
              </span>
            </div>
            <div style={{ fontSize: 11, color: '#64748b', display: 'flex', gap: 14, flexWrap: 'wrap' }}>
              <span>{r.timestamp}</span>
              <span>{r.duration}</span>
              <span>conf {r.confidence}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function sampleHistory(seed: string) {
  const now = Date.now();
  const status: Array<'success' | 'timeout' | 'failed'> = ['success', 'success', 'success', 'timeout', 'success'];
  return [0, 1, 2, 3, 4].map((i) => {
    const offset = (i + 1) * 900 * 1000 + (seed.length * 7 * (i + 1));
    const d = new Date(now - offset);
    const dur = (1 + (i % 3) * 0.6).toFixed(1);
    const conf = (0.88 + ((seed.charCodeAt(0) + i) % 10) / 100).toFixed(3);
    return {
      id: `run-${4400 + (seed.length * 17 % 200) + i}`,
      timestamp: d.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
      duration: `${dur}s`,
      status: status[i],
      confidence: conf,
    };
  });
}

/* ═════════════════════ RUN OUTPUT PANEL ═════════════════════ */

function RunOutputPanel({ pipeline, runState, onClose }: {
  pipeline: Pipeline;
  runState?: RunState;
  onClose: () => void;
}) {
  const totalMs = runState?.stageRuns?.reduce((a, r) => a + (r.durationMs || 0), 0) || 0;
  const output = sampleOutputFor(pipeline);

  return (
    <>
      <div
        onClick={onClose}
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.15)', zIndex: 95 }}
      />
      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0, width: 520,
        background: '#fff', borderLeft: '1px solid #e2e8f0',
        boxShadow: '-8px 0 24px rgba(15,23,42,.06)',
        zIndex: 96, display: 'flex', flexDirection: 'column',
      }}>
        <div style={{ padding: '18px 22px', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8' }}>
                Run Output
              </div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginTop: 4 }}>
                {pipeline.name}
              </h3>
            </div>
            <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#9ca3af' }}>
              <svg style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Summary */}
          <div style={{ display: 'flex', gap: 14, marginTop: 12, fontSize: 12, color: '#64748b', flexWrap: 'wrap' }}>
            <span><strong style={{ color: '#0f172a' }}>{String(output.run_id)}</strong></span>
            <span>·</span>
            <span>{(totalMs / 1000).toFixed(1)}s total</span>
            <span>·</span>
            <span className="chip-green" style={{ fontSize: 10 }}>SUCCESS</span>
            <span>·</span>
            <span>{Number(output.records_processed)} record{Number(output.records_processed) === 1 ? '' : 's'}</span>
          </div>
        </div>

        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 22 }}>
          {/* Stage results table */}
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10 }}>
            Stage Results
          </div>
          <div style={{ overflowX: 'auto', marginBottom: 22 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: '#64748b' }}>
                  <th style={{ padding: '6px 8px', fontWeight: 600 }}>Stage</th>
                  <th style={{ padding: '6px 8px', fontWeight: 600 }}>Type</th>
                  <th style={{ padding: '6px 8px', fontWeight: 600 }}>Duration</th>
                  <th style={{ padding: '6px 8px', fontWeight: 600 }}>Conf</th>
                </tr>
              </thead>
              <tbody>
                {pipeline.stages.map((s, i) => {
                  const sr = runState?.stageRuns[i];
                  return (
                    <tr key={s.id} style={{ borderTop: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '8px', color: '#0f172a', fontWeight: 500 }}>{s.label}</td>
                      <td style={{ padding: '8px', color: '#64748b' }}>{STAGE_TYPES[s.kind].label}</td>
                      <td style={{ padding: '8px', color: '#64748b' }}>
                        {sr?.durationMs !== undefined ? `${(sr.durationMs / 1000).toFixed(1)}s` : '—'}
                      </td>
                      <td style={{ padding: '8px', color: '#16a34a', fontWeight: 600 }}>
                        {(0.9 + (i % 5) / 100).toFixed(3)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* JSON output */}
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10 }}>
            Output Preview
          </div>
          <pre className="mono" style={{
            fontSize: 11, background: '#eff6ff', padding: 14, borderRadius: 10,
            color: '#1e40af', overflowX: 'auto', lineHeight: 1.5,
            border: '1px solid #bfdbfe',
          }}>
            {JSON.stringify(output, null, 2)}
          </pre>

          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.06em', textTransform: 'uppercase', color: '#94a3b8', marginTop: 22, marginBottom: 8 }}>
            Errors / Warnings
          </div>
          <div style={{
            padding: '10px 12px', background: '#f0fdf4',
            border: '1px solid #bbf7d0', borderRadius: 10,
            fontSize: 12, color: '#15803d',
          }}>
            ✓ No errors or warnings.
          </div>
        </div>

        <div style={{
          padding: '14px 22px', borderTop: '1px solid #f1f5f9',
          display: 'flex', gap: 8, justifyContent: 'flex-end',
        }}>
          <button className="btn btn-secondary">
            <Icon name="download" className="" style={{ width: 14, height: 14 }} />
            Download Report
          </button>
          <a href="/agent-hub?doc=invoice" className="btn btn-primary">
            <Icon name="inbox" className="" style={{ width: 14, height: 14 }} />
            Send to Agent Hub
          </a>
        </div>
      </div>
    </>
  );
}

function sampleOutputFor(pipeline: Pipeline): Record<string, unknown> {
  // A realistic JSON envelope shaped by pipeline type.
  const shared = {
    run_id: `run-${(pipeline.id.length * 37 + 3999) % 9999}`,
    pipeline: pipeline.name,
    started_at: new Date().toISOString(),
    status: 'success',
    records_processed: 1,
  };

  /* ─── CBB Demo output payloads (from CBB_Apex_Full_Execution_Plan.docx §2) ─── */
  if (pipeline.id === 'pipe-cbb-order-mod') {
    return {
      ...shared,
      distributor: { name: 'Midwest Window & Door Supply', id: 'DIST-4421', tier: 'Gold Partner' },
      order: {
        id: 'CBB-ORD-1044',
        product: 'Commercial Casement Window',
        product_sku: 'CCW-4860-LG',
        original_dimensions: { width_in: 48, height_in: 60 },
        requested_dimensions: { width_in: 48, height_in: 62 },
        quantity: 24,
        production_start: '2026-04-28',
        lead_time_days: 16,
      },
      validation: { constraint_check: 'PASS', variance_pct: 3.3, max_allowed_variance_pct: 5.0 },
      extraction: { confidence: 0.974, fields_extracted: 12, blueprint: 'Order Modification Form v2.1' },
      decision: 'AUTO_APPROVED',
      crm_updated: true,
      confirmation_email_sent: true,
      email_recipient: 'orders@midwestwindow.com',
    };
  }
  if (pipeline.id === 'pipe-cbb-qc') {
    return {
      ...shared,
      supplier: { name: 'Apex Vinyl Solutions', id: 'SUP-0081', material: 'Vinyl Resin Compound', plant_destination: 'Ohio Plant 7' },
      batch_summary: {
        total_certificates: 50,
        passed: 48,
        failed: 2,
        processing_time_ms: 4200,
        blueprint: 'QC Certificate v3.0',
      },
      failed_lots: [
        {
          lot_id: 'LOT-A44',
          variance_pct: 3.8,
          tolerance_max_pct: 2.0,
          failure_reason: 'Tensile strength 3.8% below minimum spec',
          erp_hold_id: 'ERP-HOLD-7741',
          quantity_kg: 2400,
          estimated_value_usd: 18600,
        },
        {
          lot_id: 'LOT-B12',
          variance_pct: 2.9,
          tolerance_max_pct: 2.0,
          failure_reason: 'Color variance exceeds acceptable delta-E threshold',
          erp_hold_id: 'ERP-HOLD-7742',
          quantity_kg: 1800,
          estimated_value_usd: 13950,
        },
      ],
      notifications_sent: [
        { recipient: 'Sarah Jenkins', role: 'Plant Manager, Ohio Plant 7', channel: 'Microsoft Teams', at: '06:15:42Z' },
        { recipient: 'procurement@cbb.com', role: 'Procurement Team', channel: 'Email', at: '06:15:43Z' },
      ],
      decision: 'PARTIAL_HOLD',
      production_impact: '48 lots cleared. 2 lots quarantined pending supplier re-test.',
    };
  }
  if (pipeline.id === 'pipe-cbb-disruption') {
    return {
      ...shared,
      alert: {
        source: 'Global Supply Chain Monitor API',
        event_type: 'Port Strike',
        port: 'Port of Savannah, GA',
        affected_supplier: 'Chemours Vinyl Resins',
        supplier_id: 'SUP-0044',
        material: 'Vinyl Resin (PVC Grade A)',
        delay_days: 7,
        severity: 'HIGH',
      },
      bom_traversal: {
        query_engine: 'Azure Synapse',
        nodes_traversed: 847,
        traversal_time_ms: 2100,
        affected_products: ['Commercial Casement Windows', 'Vinyl Siding Panels', 'Exterior Door Frames'],
        affected_plants: [
          { plant_id: 'PLT-007', name: 'Ohio Plant 7',    units_at_risk: 1240, value_usd: 412000 },
          { plant_id: 'PLT-014', name: 'Texas Plant 14',  units_at_risk: 980,  value_usd: 386000 },
          { plant_id: 'PLT-031', name: 'Georgia Plant 31',units_at_risk: 740,  value_usd: 292000 },
        ],
        total_value_at_risk_usd: 1090000,
      },
      rerouting_options: [
        { option: 'A', label: 'Reroute from Supplier Y',          supplier: 'Oxy Vinyls LP',     cost_delta_pct: 5.0,  delay_days: 0, recommendation: 'PREFERRED'   },
        { option: 'B', label: 'Resequence Production at Plant Z', plant:    'Georgia Plant 31',  cost_delta_pct: 0.0,  delay_days: 2, recommendation: 'FALLBACK'    },
        { option: 'C', label: 'Emergency Air Freight',            supplier: 'Formosa Plastics',  cost_delta_pct: 22.0, delay_days: 0, recommendation: 'LAST_RESORT' },
      ],
      decision: 'PENDING_HUMAN_APPROVAL',
      escalated_to: 'Marcus Webb, Supply Chain Director',
    };
  }

  if (pipeline.id === 'pipe-invoice') {
    return {
      ...shared,
      output: {
        invoice_number: 'GLX-2024-0441',
        vendor: 'Globex Corp',
        amount: 87400.0,
        decision: 'AUTO_APPROVED',
        routed_to: 'AP Manager Queue',
        notifications_sent: ['slack:#ap-team', 'erp:SAP-S4HANA'],
      },
    };
  }
  if (pipeline.id === 'pipe-cre') {
    return {
      ...shared,
      output: {
        submission_id: 'CRE-2026-0191',
        insured: 'Meridian Properties',
        tiv: 12400000,
        risk_tier: 'Preferred',
        premium: 42600,
        cat_pml_1_in_100: 1.8,
        decision: 'AUTO_BIND',
      },
    };
  }
  if (pipeline.id === 'pipe-prior-auth') {
    return {
      ...shared,
      output: {
        auth_id: 'AUTH-8821',
        member_id: 'MEM-1001',
        service: 'MRI Lumbar Spine',
        eligibility: 'active',
        criteria_met: true,
        decision: 'APPROVED',
        notification: 'sent:provider+member',
      },
    };
  }
  if (pipeline.id === 'pipe-rfp') {
    return {
      ...shared,
      output: {
        rfp_id: 'RFP-AF-2026-0044',
        win_probability: 0.72,
        suggested_price: 4820000,
        itar_compliant: true,
        response_doc: 's3://apex-rfps/out/RFP-AF-2026-0044.pdf',
      },
    };
  }
  return {
    ...shared,
    output: {
      scorecard_id: 'SC-2026-04-21',
      suppliers_evaluated: 42,
      top_performers: ['UPS', 'FedEx'],
      improvement_actions: ['Review Continental on delivery windows'],
    },
  };
}

/* ═════════════════════ TOAST ═════════════════════ */

function ToastBubble({ toast }: { toast: Toast }) {
  const bg =
    toast.kind === 'success' ? '#16a34a'
  : toast.kind === 'error'   ? '#dc2626'
  :                            '#2563eb';
  return (
    <div
      style={{
        position: 'fixed', top: 80, right: 24, zIndex: 120,
        background: bg, color: '#fff',
        padding: '10px 16px', borderRadius: 10,
        fontSize: 13, fontWeight: 500,
        boxShadow: '0 10px 25px rgba(15,23,42,.2)',
        animation: 'apex-pulse .3s ease-out',
      }}
    >
      {toast.message}
    </div>
  );
}

/* ═════════════════════ NEW PIPELINE WIZARD ═════════════════════ */

type TriggerKind = 'document' | 'schedule' | 'api' | 'manual';
type DeployTarget = 'staging' | 'production';

interface WizardDraft {
  name: string;
  description: string;
  industry: IndustryKey;
  trigger: TriggerKind;
  fileTypes: string[];
  connector: string;
  cron: string;
  eventType: string;
  stages: Stage[];
  deployTo: DeployTarget;
}

const EMPTY_DRAFT: WizardDraft = {
  name: '',
  description: '',
  industry: 'Financial Services',
  trigger: 'document',
  fileTypes: ['PDF'],
  connector: 'S3',
  cron: '0 9 * * *',
  eventType: 'invoice.received',
  stages: [],
  deployTo: 'staging',
};

function NewPipelineWizard({ onCancel, onDeploy }: {
  onCancel: () => void;
  onDeploy: (draft: WizardDraft) => void;
}) {
  const [step, setStep] = useState<1 | 2 | 3 | 4>(1);
  const [draft, setDraft] = useState<WizardDraft>(EMPTY_DRAFT);

  const canProceed = (() => {
    if (step === 1) return draft.name.trim().length > 0;
    if (step === 2) return draft.stages.length >= 2;
    if (step === 3) return true;
    return true;
  })();

  const onDiscard = () => {
    if (draft.name.trim() || draft.stages.length > 0) {
      if (!confirm('Discard changes?')) return;
    }
    onCancel();
  };

  return (
    <div className="modal-overlay" onClick={onDiscard} style={{ alignItems: 'flex-start', paddingTop: 40 }}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 720, maxHeight: 'calc(100vh - 80px)', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {/* Header with step indicator */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>New Pipeline</h3>
            <button onClick={onDiscard} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4, color: '#9ca3af' }}>
              <svg style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <StepIndicator current={step} onStepClick={(s) => { if (s <= step) setStep(s); }} />
        </div>

        {/* Body */}
        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
          {step === 1 && <WizardStep1 draft={draft} setDraft={setDraft} />}
          {step === 2 && <WizardStep2 draft={draft} setDraft={setDraft} />}
          {step === 3 && <WizardStep3 draft={draft} setDraft={setDraft} />}
          {step === 4 && <WizardStep4 draft={draft} setDraft={setDraft} />}
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 24px', borderTop: '1px solid #f1f5f9',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <button
            className="btn btn-secondary"
            disabled={step === 1}
            onClick={() => setStep((s) => (s > 1 ? (s - 1) as 1 | 2 | 3 | 4 : s))}
            style={step === 1 ? { opacity: 0.5 } : undefined}
          >
            Back
          </button>
          <div style={{ fontSize: 12, color: '#94a3b8' }}>Step {step} of 4</div>
          {step < 4 ? (
            <button
              className="btn btn-primary"
              disabled={!canProceed}
              onClick={() => setStep((s) => (s + 1) as 1 | 2 | 3 | 4)}
              style={!canProceed ? { opacity: 0.5 } : undefined}
            >
              Next →
            </button>
          ) : (
            <button
              className="btn btn-primary btn-lg"
              onClick={() => onDeploy(draft)}
            >
              Deploy Pipeline
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function StepIndicator({ current, onStepClick }: { current: 1 | 2 | 3 | 4; onStepClick: (s: 1 | 2 | 3 | 4) => void }) {
  const steps: Array<{ n: 1 | 2 | 3 | 4; label: string }> = [
    { n: 1, label: 'Name & Industry' },
    { n: 2, label: 'Add Stages' },
    { n: 3, label: 'Configure Triggers' },
    { n: 4, label: 'Review & Deploy' },
  ];
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
      {steps.map((s, i) => {
        const isDone = s.n < current;
        const isCurrent = s.n === current;
        const bg = isDone ? '#059669' : isCurrent ? '#2563eb' : '#f1f5f9';
        const color = isDone || isCurrent ? '#fff' : '#94a3b8';
        return (
          <React.Fragment key={s.n}>
            <button
              onClick={() => onStepClick(s.n)}
              disabled={!isDone && !isCurrent}
              style={{
                display: 'flex', alignItems: 'center', gap: 8,
                background: 'none', border: 'none',
                cursor: s.n <= current ? 'pointer' : 'default',
                padding: 0,
              }}
            >
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: bg, color,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, fontWeight: 700,
              }}>
                {isDone ? '✓' : s.n}
              </div>
              <span style={{
                fontSize: 12,
                fontWeight: isCurrent ? 700 : 500,
                color: isDone ? '#065f46' : isCurrent ? '#1e40af' : '#94a3b8',
              }}>
                {s.label}
              </span>
            </button>
            {i < steps.length - 1 && (
              <div style={{
                flex: 1, height: 2,
                background: s.n < current ? '#059669' : '#e2e8f0',
                margin: '0 12px',
              }} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}

function WizardStep1({ draft, setDraft }: { draft: WizardDraft; setDraft: (d: WizardDraft) => void }) {
  const industries: IndustryKey[] = ['Financial Services', 'Commercial Insurance', 'Healthcare Payers', 'Aerospace & Defense', 'Supply Chain & Manufacturing'];
  const triggers: Array<{ k: TriggerKind; label: string }> = [
    { k: 'document', label: 'Document Upload' },
    { k: 'schedule', label: 'Schedule' },
    { k: 'api',      label: 'API Event' },
    { k: 'manual',   label: 'Manual' },
  ];
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div>
        <label className="label">Pipeline Name <span style={{ color: '#dc2626' }}>*</span></label>
        <input
          className="input"
          placeholder="e.g. Claims Triage Pipeline"
          value={draft.name}
          onChange={(e) => setDraft({ ...draft, name: e.target.value })}
        />
      </div>
      <div>
        <label className="label">Description</label>
        <textarea
          className="textarea"
          rows={3}
          placeholder="What does this pipeline automate?"
          value={draft.description}
          onChange={(e) => setDraft({ ...draft, description: e.target.value })}
        />
      </div>
      <div>
        <label className="label">Industry</label>
        <select
          className="select"
          value={draft.industry}
          onChange={(e) => setDraft({ ...draft, industry: e.target.value as IndustryKey })}
        >
          {industries.map((i) => <option key={i} value={i}>{i}</option>)}
        </select>
      </div>
      <div>
        <label className="label">Trigger Type</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {triggers.map((t) => (
            <button
              key={t.k}
              onClick={() => setDraft({ ...draft, trigger: t.k })}
              style={{
                padding: '12px 14px',
                border: `1.5px solid ${draft.trigger === t.k ? '#2563eb' : '#e2e8f0'}`,
                background: draft.trigger === t.k ? '#eff6ff' : '#fff',
                borderRadius: 10,
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: 13,
                fontWeight: 500,
                color: draft.trigger === t.k ? '#1e40af' : '#334155',
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function WizardStep2({ draft, setDraft }: { draft: WizardDraft; setDraft: (d: WizardDraft) => void }) {
  const [draggingIdx, setDraggingIdx] = useState<number | null>(null);

  const addStage = () => {
    setDraft({
      ...draft,
      stages: [
        ...draft.stages,
        mkStage('execute', `Stage ${draft.stages.length + 1}`, `stage_${draft.stages.length + 1}`),
      ],
    });
  };
  const removeStage = (idx: number) => {
    setDraft({ ...draft, stages: draft.stages.filter((_, i) => i !== idx) });
  };
  const updateStageField = (idx: number, patch: Partial<Stage>) => {
    setDraft({
      ...draft,
      stages: draft.stages.map((s, i) => i === idx ? { ...s, ...patch } : s),
    });
  };
  const onDragStart = (idx: number) => setDraggingIdx(idx);
  const onDragOver = (e: React.DragEvent) => e.preventDefault();
  const onDrop = (dropIdx: number) => {
    if (draggingIdx === null || draggingIdx === dropIdx) {
      setDraggingIdx(null);
      return;
    }
    const next = draft.stages.slice();
    const [moved] = next.splice(draggingIdx, 1);
    next.splice(dropIdx, 0, moved);
    setDraft({ ...draft, stages: next });
    setDraggingIdx(null);
  };

  return (
    <div>
      <p style={{ fontSize: 13, color: '#64748b', marginBottom: 14 }}>
        Add at least 2 stages. Drag the <span className="mono">⠿</span> handle to reorder.
      </p>

      {draft.stages.length === 0 && (
        <button
          onClick={addStage}
          style={{
            width: '100%',
            border: '2px dashed #cbd5e1',
            background: 'transparent',
            borderRadius: 12,
            padding: 32,
            cursor: 'pointer',
            color: '#64748b',
            fontSize: 14,
            fontWeight: 600,
            marginBottom: 12,
          }}
        >
          + Add First Stage
        </button>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 12 }}>
        {draft.stages.map((stage, idx) => {
          const theme = STAGE_TYPES[stage.kind];
          return (
            <div
              key={stage.id}
              draggable
              onDragStart={() => onDragStart(idx)}
              onDragOver={onDragOver}
              onDrop={() => onDrop(idx)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                background: '#fff',
                border: `1.5px solid ${draggingIdx === idx ? '#2563eb' : '#e2e8f0'}`,
                borderRadius: 10,
                padding: '10px 12px',
                cursor: 'grab',
                opacity: draggingIdx === idx ? 0.6 : 1,
              }}
            >
              <span style={{ fontSize: 16, color: '#94a3b8', userSelect: 'none' }}>⠿</span>
              <span style={{
                fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 4,
                background: theme.bg, color: theme.color, border: `1px solid ${theme.border}`,
                textTransform: 'uppercase', letterSpacing: '.06em',
                minWidth: 76, textAlign: 'center',
              }}>
                {theme.label}
              </span>
              <select
                className="select"
                value={stage.kind}
                onChange={(e) => updateStageField(idx, { kind: e.target.value as StageKind })}
                style={{ width: 130, padding: '6px 10px', fontSize: 12 }}
              >
                {STAGE_KIND_OPTIONS.map((k) => (
                  <option key={k} value={k}>{STAGE_TYPES[k].label}</option>
                ))}
              </select>
              <input
                className="input"
                placeholder="Stage label"
                value={stage.label}
                onChange={(e) => updateStageField(idx, { label: e.target.value })}
                style={{ flex: 1, padding: '6px 10px', fontSize: 12 }}
              />
              <input
                className="input mono"
                placeholder="action_name"
                value={stage.config.actionName}
                onChange={(e) => updateStageField(idx, { config: { ...stage.config, actionName: e.target.value } })}
                style={{ flex: 1, padding: '6px 10px', fontSize: 11 }}
              />
              <button
                onClick={() => removeStage(idx)}
                style={{
                  background: 'transparent', border: 'none',
                  color: '#dc2626', cursor: 'pointer', padding: 4,
                  fontSize: 16,
                }}
                title="Remove"
              >
                ×
              </button>
            </div>
          );
        })}
      </div>

      {draft.stages.length > 0 && (
        <button onClick={addStage} className="btn btn-secondary btn-sm">
          <Icon name="plus" className="" style={{ width: 13, height: 13 }} />
          Add Stage
        </button>
      )}

      {draft.stages.length > 0 && draft.stages.length < 2 && (
        <div style={{ marginTop: 12, fontSize: 12, color: '#d97706' }}>
          At least 2 stages are required to proceed.
        </div>
      )}
    </div>
  );
}

function WizardStep3({ draft, setDraft }: { draft: WizardDraft; setDraft: (d: WizardDraft) => void }) {
  const fileTypeOpts = ['PDF', 'DOCX', 'PNG', 'TIFF', 'CSV'];
  const connectors = ['S3', 'SharePoint', 'Email', 'Manual Upload'];

  const toggleFileType = (t: string) => {
    const has = draft.fileTypes.includes(t);
    setDraft({
      ...draft,
      fileTypes: has ? draft.fileTypes.filter((x) => x !== t) : [...draft.fileTypes, t],
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ fontSize: 13, color: '#64748b' }}>
        Configure how this pipeline is triggered.
      </div>

      {draft.trigger === 'document' && (
        <>
          <div>
            <label className="label">Accepted file types</label>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
              {fileTypeOpts.map((t) => (
                <label key={t} style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '6px 12px', borderRadius: 8,
                  border: `1px solid ${draft.fileTypes.includes(t) ? '#2563eb' : '#e2e8f0'}`,
                  background: draft.fileTypes.includes(t) ? '#eff6ff' : '#fff',
                  cursor: 'pointer', fontSize: 12,
                  color: draft.fileTypes.includes(t) ? '#1e40af' : '#334155',
                  fontWeight: 500,
                }}>
                  <input
                    type="checkbox"
                    checked={draft.fileTypes.includes(t)}
                    onChange={() => toggleFileType(t)}
                  />
                  {t}
                </label>
              ))}
            </div>
          </div>
          <div>
            <label className="label">Source connector</label>
            <select
              className="select"
              value={draft.connector}
              onChange={(e) => setDraft({ ...draft, connector: e.target.value })}
            >
              {connectors.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </>
      )}

      {draft.trigger === 'schedule' && (
        <div>
          <label className="label">Cron expression</label>
          <input
            className="input mono"
            value={draft.cron}
            onChange={(e) => setDraft({ ...draft, cron: e.target.value })}
          />
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 6 }}>
            {humanCron(draft.cron)}
          </div>
        </div>
      )}

      {draft.trigger === 'api' && (
        <>
          <div>
            <label className="label">Webhook URL (auto-generated)</label>
            <input
              className="input mono"
              readOnly
              value={`https://api.apex.ai/v1/webhooks/${draft.name.trim().toLowerCase().replace(/\s+/g, '-') || 'new-pipeline'}`}
              style={{ background: '#f8fafc' }}
            />
          </div>
          <div>
            <label className="label">Event type</label>
            <input
              className="input mono"
              value={draft.eventType}
              onChange={(e) => setDraft({ ...draft, eventType: e.target.value })}
            />
          </div>
        </>
      )}

      {draft.trigger === 'manual' && (
        <div style={{
          padding: 14, background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 10,
          fontSize: 13, color: '#1e40af',
        }}>
          This pipeline will only run when triggered manually from the Run button.
        </div>
      )}
    </div>
  );
}

function humanCron(cron: string): string {
  // Very small cron humanizer for the prototype — supports the most common patterns.
  const daily = /^0\s+(\d{1,2})\s+\*\s+\*\s+\*$/.exec(cron);
  if (daily) {
    const h = Number(daily[1]);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const h12 = h === 0 ? 12 : h > 12 ? h - 12 : h;
    return `Every day at ${h12}:00 ${ampm}`;
  }
  if (cron === '*/15 * * * *') return 'Every 15 minutes';
  if (cron === '0 * * * *') return 'Every hour on the hour';
  return 'Custom schedule';
}

function WizardStep4({ draft, setDraft }: { draft: WizardDraft; setDraft: (d: WizardDraft) => void }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ padding: 18, background: '#f8fafc' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a' }}>{draft.name || '(unnamed)'}</div>
            <div style={{ marginTop: 6, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
              <span className={INDUSTRY_CHIP_CLASS[draft.industry]} style={{ fontSize: 10 }}>{draft.industry}</span>
              <span className="chip-blue" style={{ fontSize: 10 }}>Trigger: {draft.trigger}</span>
              <span style={{ fontSize: 12, color: '#64748b' }}>{draft.stages.length} stages</span>
            </div>
            {draft.description && (
              <p style={{ fontSize: 13, color: '#475569', marginTop: 10, lineHeight: 1.5 }}>
                {draft.description}
              </p>
            )}
          </div>
        </div>

        {/* Stage chip row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 16, overflowX: 'auto', paddingBottom: 4 }}>
          {draft.stages.map((s, i) => (
            <React.Fragment key={s.id}>
              <div className="pipeline-stage" style={{
                background: STAGE_TYPES[s.kind].bg,
                border: `1px solid ${STAGE_TYPES[s.kind].border}`,
                minWidth: 110,
              }}>
                <div style={{
                  fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                  letterSpacing: '.06em', color: STAGE_TYPES[s.kind].color,
                  marginBottom: 4,
                }}>
                  {STAGE_TYPES[s.kind].label}
                </div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{s.label}</div>
              </div>
              {i < draft.stages.length - 1 && <div className="pipeline-arrow">→</div>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Deploy target */}
      <div>
        <label className="label">Deployment target</label>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <DeployOption
            target="staging"
            active={draft.deployTo === 'staging'}
            chipClass="chip-amber"
            chipLabel="Staging"
            description="Deploy to a non-production environment for smoke testing."
            onClick={() => setDraft({ ...draft, deployTo: 'staging' })}
          />
          <DeployOption
            target="production"
            active={draft.deployTo === 'production'}
            chipClass="chip-green"
            chipLabel="Production"
            description="Deploy live. Real documents will flow through immediately."
            onClick={() => setDraft({ ...draft, deployTo: 'production' })}
          />
        </div>
      </div>
    </div>
  );
}

function DeployOption({ target, active, chipClass, chipLabel, description, onClick }: {
  target: DeployTarget;
  active: boolean;
  chipClass: string;
  chipLabel: string;
  description: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      style={{
        padding: 14,
        border: `1.5px solid ${active ? '#2563eb' : '#e2e8f0'}`,
        background: active ? '#eff6ff' : '#fff',
        borderRadius: 12, cursor: 'pointer', textAlign: 'left',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <span className={chipClass} style={{ fontSize: 10 }}>{chipLabel}</span>
        {active && <span style={{ fontSize: 11, color: '#2563eb', fontWeight: 600 }}>Selected</span>}
      </div>
      <div style={{ fontSize: 12, color: '#475569', lineHeight: 1.5 }}>{description}</div>
    </button>
  );
}

/* ═════════════════════ FEATURE 3 — Workflow Debt Eliminator ═════════════════════ */

interface ValueMapRow {
  metric: string;
  legacy: string;
  apex: string;
  saving: string;
}

/**
 * Before vs After card for a single pipeline. All data comes from
 * GET /api/v1/pipelines/{id}/value-map — the backend reads the playbook's
 * `value_map` blob from Cosmos DB (patched onto the 3 CBB playbooks by the
 * seeder) or synthesises from stage count if missing.
 */
function ValueMapCard({ pipeline }: { pipeline: Pipeline }) {
  const theme = INDUSTRY_THEME[pipeline.industry];
  const stageCount = pipeline.stages.length;
  const q = useQuery<ValueMap>({
    // Include name + stage count in the cache key so renames/stage edits
    // refetch instead of serving stale synthesised maps.
    queryKey: ['value-map', pipeline.id, pipeline.name, stageCount],
    queryFn: async () => {
      // URLSearchParams safely encodes names with `&`, `#`, spaces, etc.
      const params = new URLSearchParams({
        name:   pipeline.name,
        stages: String(stageCount),
      });
      const r = await fetch(
        `${API_BASE_URL}/pipelines/${encodeURIComponent(pipeline.id)}/value-map?${params.toString()}`,
      );
      if (!r.ok) throw new Error(`status ${r.status}`);
      return r.json();
    },
    retry: 1,
  });

  if (q.isLoading) {
    return (
      <div className="card" style={{ padding: 24, color: '#94a3b8', fontSize: 13 }}>
        Loading value map for <span className="mono">{pipeline.id}</span>…
      </div>
    );
  }
  if (q.error || !q.data) {
    // Backend no longer 404s — it always synthesises on miss. Reaching this
    // branch means the fetch itself failed (server unreachable, CORS,
    // malformed JSON). Offer a retry.
    return (
      <div className="card" style={{ padding: 24, background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', fontSize: 13 }}>
        <div style={{ marginBottom: 10 }}>
          Couldn&rsquo;t reach the value-map service for <span className="mono">{pipeline.id}</span>.
          {q.error instanceof Error && (
            <span style={{ color: '#7f1d1d', marginLeft: 6 }} className="mono">({q.error.message})</span>
          )}
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => q.refetch()}
          style={{ background: '#fff' }}
        >
          Retry
        </button>
      </div>
    );
  }
  const data = q.data;

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 34, height: 34, borderRadius: 10, background: theme.bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg style={{ width: 17, height: 17, color: theme.color }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={theme.path} />
            </svg>
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>{pipeline.name}</div>
            <div style={{ fontSize: 12, color: '#94a3b8' }}>{pipeline.industry} · workflow-debt comparison</div>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 11, color: '#94a3b8', letterSpacing: '.08em', textTransform: 'uppercase', fontWeight: 600 }}>
            Workflow Debt Eliminated
          </div>
          <div style={{ fontSize: 15, fontWeight: 800, color: '#16a34a', marginTop: 2 }}>{data.headline}</div>
        </div>
      </div>

      {/* Comparison grid */}
      <div style={{ padding: 20 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr 1fr 160px', gap: 0, borderRadius: 12, overflow: 'hidden', border: '1px solid #f1f5f9' }}>
          {/* Header row */}
          <div style={{ ...vmHead, background: '#f8fafc' }}>Metric</div>
          <div style={{ ...vmHead, background: '#fef2f2', color: '#991b1b' }}>Legacy Process</div>
          <div style={{ ...vmHead, background: '#f0fdf4', color: '#166534' }}>Apex Agentic Process</div>
          <div style={{ ...vmHead, background: '#eff6ff', color: '#1d4ed8', textAlign: 'right', paddingRight: 16 }}>Saving</div>

          {data.rows.map((row, i) => (
            <React.Fragment key={row.metric}>
              <div style={{ ...vmCell, borderTop: '1px solid #f1f5f9', fontWeight: 600, color: '#0f172a', background: i % 2 === 0 ? '#fff' : '#fcfcfd' }}>
                {row.metric}
              </div>
              <div style={{ ...vmCell, borderTop: '1px solid #f1f5f9', color: '#991b1b', background: i % 2 === 0 ? '#fff' : '#fcfcfd' }}>
                <span style={{ textDecoration: 'line-through', opacity: .7 }}>{row.legacy}</span>
              </div>
              <div style={{ ...vmCell, borderTop: '1px solid #f1f5f9', color: '#166534', fontWeight: 600, background: i % 2 === 0 ? '#fff' : '#fcfcfd' }}>
                {row.apex}
              </div>
              <div style={{ ...vmCell, borderTop: '1px solid #f1f5f9', color: '#1d4ed8', fontWeight: 700, textAlign: 'right', paddingRight: 16, background: i % 2 === 0 ? '#fff' : '#fcfcfd' }}>
                {row.saving}
              </div>
            </React.Fragment>
          ))}
        </div>

        <div style={{ marginTop: 14, padding: 12, background: '#0b1220', borderRadius: 10, color: '#e2e8f0', fontSize: 12, display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 14 }}>✦</span>
          <span>{data.narrative}</span>
        </div>
      </div>
    </div>
  );
}

const vmHead: React.CSSProperties = {
  padding: '10px 16px', fontSize: 11, fontWeight: 700, letterSpacing: '.06em',
  textTransform: 'uppercase', color: '#475569',
};
const vmCell: React.CSSProperties = {
  padding: '10px 16px', fontSize: 13, lineHeight: 1.45,
};

interface ValueMap {
  headline: string;
  rows: ValueMapRow[];
  narrative: string;
}

/* Value Map is served by GET /api/v1/pipelines/{id}/value-map — no local fallback. */
