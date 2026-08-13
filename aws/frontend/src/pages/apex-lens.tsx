/**
 * ApexLens — drop-a-document → watch the agent work → chat about it.
 *
 * Ported from /Users/babbu/Downloads/apex-prototype 2/apex-lens.html (the
 * canonical HTML prototype) plus ApexLens_Implementation_Spec.docx v1.0.
 *
 * 3-column card: [samples + drop zone] · [pipeline + extracted fields] · [results]
 *
 * Animation timing: 5 stages × 800ms. Extracted fields appear after Extract
 * (stage 2). Right-panel results populate after Complete (stage 5). Clicking
 * "Open in Agent Hub" routes to /agent-hub?doc=<type> which triggers the
 * document-context mode on the Agent Hub page.
 *
 * Styling: reuses the shared `.apex-app` CSS classes (card, chip-*, dot-*,
 * work-item, btn-*, animate-pulse). No new CSS needed.
 */

import React, { useEffect, useMemo, useRef, useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { Icon } from '@/components/AppShell/icons';
import { useDemoMode, isIndustryVisible, type DemoMode } from '@/lib/demoMode';
import { brandLabel, brandWordmark, PRODUCT_BRAND_STORAGE_KEY, useProductBrand } from '@/lib/productBrand';

/** Branded browser tab title for ApexLens / Regulus Doc. SSR-safe. */
function __brandedApexLensTitle(): string {
  const brand = (typeof window !== 'undefined'
    ? window.localStorage.getItem(PRODUCT_BRAND_STORAGE_KEY)
    : null) === 'regulus' ? 'regulus' as const : 'apex' as const;
  return `${brandLabel('ApexLens', brand)} | ${brandWordmark(brand)}`;
}

/** Branded in-page H2 for the ApexLens header. SSR-safe. */
function __brandedApexLensH2(): string {
  const brand = (typeof window !== 'undefined'
    ? window.localStorage.getItem(PRODUCT_BRAND_STORAGE_KEY)
    : null) === 'regulus' ? 'regulus' as const : 'apex' as const;
  return brandLabel('ApexLens', brand);
}

/* ──────────────────────── types + data ──────────────────────── */

type SampleKey =
  // CBB demo samples (featured first in the library for the Cornerstone Building Brands demo)
  | 'order_mod' | 'qc_batch' | 'port_strike'
  // Generic samples (kept for non-CBB demos)
  | 'invoice' | 'claim' | 'po' | 'qc' | 'contract' | 'alert'
  // STP Phase 2 — one entry per ChatSTP use case. Each maps 1:1 to a deployed
  // STP playbook + its specialist AgentCore runtime. Filename-based auto-
  // detection in onFileChosen() routes dropped files to the right one.
  | 'stp_policy' | 'stp_pm_history' | 'stp_issue_analysis' | 'stp_predictive'
  // Telecommunications · Verizon Far Edge POC — 4 samples, one per agent.
  // Map: ROBOT XML → CertificationAgent · Redfish diff → SchemaWatchAgent
  //      Upgrade runbook → UpgradeAdvisorAgent · KB article → MentorAgent.
  | 'tel_robot_xml' | 'tel_redfish_diff' | 'tel_upgrade_runbook' | 'tel_kb_article'
  // VERIZON FAR EDGE · 12 REAL firmware certification reports (James Patchett · MTCE Lab)
  // sourced from synthetic-data/verizon_far_edge/real_test_reports/ (anonymized)
  | 'vz_dmtf_e930t' | 'vz_samsung_ssd' | 'vz_bmc_upgrade' | 'vz_ptu_perf'
  | 'vz_sensor_proteus' | 'vz_bios_triton' | 'vz_redfish_proteus' | 'vz_platform_deploy'
  | 'vz_soak_galene' | 'vz_dell_sensor' | 'vz_troubleshoot' | 'vz_flexran'
  // VERIZON CAS · current-gen campaign docs (Dell XR8720t · HPE EL140 Gen12 · WRCP 24.09.301)
  | 'vz_cas_el140' | 'vz_cas_xr8720' | 'vz_cas_playbook_spec' | 'vz_cas_thermal' | 'vz_cas_wrcp'
  // Agentic Enterprise (66 Degrees vendor-neutral demos): inventory alert
  // for the Supply Chain Orchestrator and a sample lease PDF for the CRE
  // Lease Extraction agent. The Cruise Concierge has no Apex Lens sample
  // because it's a chat-only flow.
  | 'ae_inventory_alert' | 'ae_lease_pdf'
  // EPROD · Oil & Gas — Midstream (15 samples). Sourced from
  // synthetic-data/eprod/. Covers AP (invoices, POs, MSAs, engineering
  // quotes) plus the two WOW-use-case docs: FERC tariff sheets and JIB
  // statements.
  | 'eprod_inv_hal' | 'eprod_inv_slb' | 'eprod_inv_bhi' | 'eprod_inv_kiewit'
  | 'eprod_po_epc' | 'eprod_po_chem' | 'eprod_po_ops'
  | 'eprod_msa_hal' | 'eprod_msa_kiewit'
  | 'eprod_quote_fluor' | 'eprod_quote_bechtel'
  | 'eprod_tariff_ngl' | 'eprod_tariff_crude'
  | 'eprod_jib_p66' | 'eprod_jib_targa'
  // CWFCU · Credit Union (22 samples). Sourced from synthetic-data/cwfcu/.
  // 4 CIP packets · 3 SAR filings · 2 CTR filings · 2 CDD reviews ·
  // 5 loan packets · 4 vendor contracts · 2 policy artifacts.
  | 'cwfcu_cip_rosales' | 'cwfcu_cip_nguyen' | 'cwfcu_cip_arrington' | 'cwfcu_cip_okafor'
  | 'cwfcu_sar_structuring' | 'cwfcu_sar_rapid_movement' | 'cwfcu_sar_layering'
  | 'cwfcu_ctr_cash' | 'cwfcu_ctr_wire'
  | 'cwfcu_cdd_04421' | 'cwfcu_cdd_08812'
  | 'cwfcu_loan_auto' | 'cwfcu_loan_heloc_johnson' | 'cwfcu_loan_mortgage_patel' | 'cwfcu_loan_personal_williams' | 'cwfcu_paystub_nguyen'
  | 'cwfcu_contract_fiserv' | 'cwfcu_contract_eltropy' | 'cwfcu_contract_coop' | 'cwfcu_contract_diebold'
  | 'cwfcu_policy_bsa_roster' | 'cwfcu_board_res_vendor_mgmt'
  // BOLER · The Boler Company (14 samples) · sourced from synthetic-data/boler/
  | 'boler_cigna_medical'
  | 'boler_delta_dental'
  | 'boler_fidelity_401k'
  | 'boler_vsp_vision'
  | 'boler_hartford_life'
  | 'boler_cigna_std_ltd'
  | 'boler_exc_chen'
  | 'boler_exc_martinez'
  | 'boler_exc_cigna_drift'
  | 'boler_exc_transfers'
  | 'boler_exc_401k'
  | 'boler_exc_thompson'
  | 'boler_exc_new_hires'
  | 'boler_je_hendrickson'
  // BOLER · 5 complex Excel workbooks (Argos · live demo)
  | 'boler_xlsx_cigna_roster'
  | 'boler_xlsx_hris_master'
  | 'boler_xlsx_division_allocation'
  | 'boler_xlsx_exception_register'
  | 'boler_xlsx_consolidated_je';

interface FieldRow {
  name: string;
  value: string;
  /** null = N/A (no confidence score applicable) */
  conf: number | null;
}

interface Flag {
  color: 'red' | 'amber' | 'green';
  text: string;
}

interface Sample {
  key: SampleKey;
  name: string;
  type: string;
  chipCls: string;              // e.g. 'chip-blue'
  iconBg: string;
  iconColor: string;
  iconPath: string;             // inline SVG path d=""
  fileSize: string;
  agent: string;
  time: string;                 // "4.2s"
  confidence: number;           // 0..100
  /** One sub-label per pipeline stage, shown below the stage node once it completes. */
  subLabels: [string, string, string, string, string];
  fields: FieldRow[];
  flags: Flag[];
  routing: string;
}

// Icon SVG paths for each sample's doc icon (kept inline for parity with prototype).
const ICONS = {
  doc:      'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  clipboard:'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2',
  cart:     'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z',
  chart:    'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  warning:  'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z',
  search:   'M21 21l-4.35-4.35M11 8a3 3 0 100 6 3 3 0 000-6zM11 3a8 8 0 108 8 8 8 0 00-8-8z',
};

// Stage-specific inline SVG paths (the little glyph inside each circle).
const STAGE_ICON_PATHS: [string, string, string, string, string] = [
  // Ingest - cloud_up
  'M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12',
  // Extract - sparkle
  'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z',
  // Validate - check_circle
  'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  // Route - bolt
  'M13 10V3L4 14h7v7l9-11h-7z',
  // Complete - check
  'M5 13l4 4L19 7',
];
const STAGE_LABELS = ['Ingest', 'Extract', 'Validate', 'Route', 'Complete'];

const SAMPLES: Record<SampleKey, Sample> = {
  /* ─── CBB Demo samples (see CBB_Apex_Full_Execution_Plan.docx) ─── */
  order_mod: {
    key: 'order_mod',
    name: 'Order_Mod_Request_1044.pdf',
    type: 'ORDER MOD',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#1d4ed8', iconPath: ICONS.doc,
    fileSize: '847 KB',
    agent: 'CustomerOps',
    time: '4.2s',
    confidence: 97,
    subLabels: [
      'PDF received · 847 KB',
      '12 fields extracted · 97.4% confidence',
      'Constraint check PASSED · 3.3% variance',
      'Auto-approved · CRM update queued',
      'Confirmation email sent · 4.2s total',
    ],
    fields: [
      { name: 'Order ID',         value: 'CBB-ORD-1044',                      conf: 99 },
      { name: 'Distributor',      value: 'Midwest Window & Door Supply',       conf: 99 },
      { name: 'Distributor Tier', value: 'Gold Partner',                       conf: 96 },
      { name: 'Product',          value: 'Commercial Casement Window',         conf: 98 },
      { name: 'Product SKU',      value: 'CCW-4860-LG',                        conf: 97 },
      { name: 'Orig. Dimensions', value: '48" W × 60" H',                      conf: 98 },
      { name: 'New Dimensions',   value: '48" W × 62" H',                      conf: 97 },
      { name: 'Variance',         value: '+3.3% (within 5% tolerance)',        conf: 99 },
      { name: 'Quantity',         value: '24 units',                           conf: 99 },
      { name: 'Production Start', value: 'Apr 28, 2026',                       conf: 95 },
      { name: 'Lead Time',        value: '16 days (was 14)',                   conf: 94 },
      { name: 'Decision',         value: 'AUTO_APPROVED',                      conf: null },
    ],
    flags: [
      { color: 'green', text: 'Engineering constraint check PASSED — 3.3% height variance within 5% tolerance' },
      { color: 'green', text: 'Distributor verified — Gold Partner, Midwest region' },
      { color: 'green', text: 'CRM updated — Microsoft Dynamics record CBB-ORD-1044 reflects new dimensions' },
      { color: 'green', text: 'Confirmation email sent to orders@midwestwindow.com' },
    ],
    routing: '→ AUTO_APPROVED — No human review needed. Lead time recalculated to 16 days.',
  },
  qc_batch: {
    key: 'qc_batch',
    name: 'QC_Batch_50_Certificates.zip',
    type: 'QC BATCH',
    chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '12.4 MB',
    agent: 'QCBot',
    time: '4.2s',
    confidence: 99,
    subLabels: [
      'ZIP received · 50 files',
      '18 fields × 50 certs · 99.1% confidence',
      '2 lots FAILED tolerance · holds placed',
      'ERP hold placed · Plant Manager alerted',
      '48 cleared · 2 quarantined · 4.2s total',
    ],
    fields: [
      { name: 'Supplier',            value: 'Apex Vinyl Solutions (SUP-0081)', conf: 99 },
      { name: 'Material',            value: 'Vinyl Resin Compound',            conf: 99 },
      { name: 'Plant Destination',   value: 'Ohio Plant 7',                    conf: 99 },
      { name: 'Total Certificates',  value: '50',                              conf: 99 },
      { name: 'Passed',              value: '48',                              conf: 99 },
      { name: 'Failed',              value: '2 (LOT-A44, LOT-B12)',            conf: 99 },
      { name: 'Fail #1 — LOT-A44',   value: 'Tensile strength 3.8% below spec · 2,400 kg · $18,600', conf: 97 },
      { name: 'Fail #2 — LOT-B12',   value: 'Color variance > delta-E tolerance · 1,800 kg · $13,950', conf: 96 },
      { name: 'ERP Holds Placed',    value: 'ERP-HOLD-7741, ERP-HOLD-7742',    conf: 99 },
      { name: 'Quarantined Value',   value: '$32,550',                         conf: 99 },
      { name: 'Processing Time',     value: '4.2s for 50 certs (was 2 hrs manual)', conf: null },
      { name: 'Decision',            value: 'PARTIAL_HOLD',                    conf: null },
    ],
    flags: [
      { color: 'red',   text: 'LOT-A44 tensile strength 3.8% below minimum — held pending supplier re-test' },
      { color: 'red',   text: 'LOT-B12 color variance exceeds delta-E threshold — held pending supplier re-test' },
      { color: 'green', text: '48 of 50 lots cleared for production' },
      { color: 'green', text: 'SAP S/4HANA holds placed (ERP-HOLD-7741, ERP-HOLD-7742) — 32,550 USD quarantined value' },
      { color: 'green', text: 'Plant Manager Sarah Jenkins notified via Microsoft Teams (06:15:42)' },
      { color: 'green', text: 'Procurement team notified via email (06:15:43)' },
    ],
    routing: '→ PARTIAL_HOLD — 48 lots cleared. 2 quarantined. Supplier corrective action requested.',
  },
  port_strike: {
    key: 'port_strike',
    name: 'Port_Strike_Alert_VinylResin.xml',
    type: 'DISRUPTION',
    chipCls: 'chip-amber',
    iconBg: '#fffbeb', iconColor: '#d97706', iconPath: ICONS.warning,
    fileSize: '42 KB',
    agent: 'LogisticsBot',
    time: '2.1s',
    confidence: 98,
    subLabels: [
      'XML alert received',
      '14 fields extracted · 98.7% confidence',
      'BOM traversal · 847 nodes · 3 plants',
      'Reroute options generated · Escalated',
      '$1.09M risk quantified · 3 options ready',
    ],
    fields: [
      { name: 'Alert Source',       value: 'Global Supply Chain Monitor API',   conf: 99 },
      { name: 'Event Type',         value: 'Port Strike',                       conf: 99 },
      { name: 'Port',               value: 'Port of Savannah, GA',              conf: 99 },
      { name: 'Affected Supplier',  value: 'Chemours Vinyl Resins (SUP-0044)',  conf: 99 },
      { name: 'Material',           value: 'Vinyl Resin (PVC Grade A)',         conf: 99 },
      { name: 'Delay',              value: '7 days',                            conf: 99 },
      { name: 'Severity',           value: 'HIGH',                              conf: null },
      { name: 'BOM Nodes Traversed',value: '847 (via Amazon Athena, 2.1s)',     conf: 99 },
      { name: 'Plants at Risk',     value: '3 (Ohio, Texas, Georgia)',          conf: 99 },
      { name: 'Ohio Plant 7',       value: '1,240 units · $412,000',            conf: 97 },
      { name: 'Texas Plant 14',     value: '980 units · $386,000',              conf: 97 },
      { name: 'Georgia Plant 31',   value: '740 units · $292,000',              conf: 96 },
      { name: 'Total Value at Risk',value: '$1,090,000',                        conf: 99 },
      { name: 'Decision',           value: 'PENDING_HUMAN_APPROVAL',            conf: null },
    ],
    flags: [
      { color: 'red',   text: '$1.09M revenue at risk across 3 plants' },
      { color: 'red',   text: 'Ohio Plant 7, Texas Plant 14, Georgia Plant 31 all downstream of Chemours' },
      { color: 'amber', text: 'Option A (PREFERRED): Reroute from Oxy Vinyls LP — +5% cost, 0-day delay' },
      { color: 'amber', text: 'Option B (FALLBACK): Resequence Georgia Plant 31 — $0 cost, 2-day delay' },
      { color: 'amber', text: 'Option C (LAST RESORT): Air freight from Formosa — +22% cost, 0-day delay' },
      { color: 'green', text: 'BOM graph traversal completed in 2.1s via Amazon Athena' },
    ],
    routing: '→ ESCALATED to Marcus Webb, Supply Chain Director — 3 ranked reroute options presented',
  },

  /* ─── Generic samples (kept for non-CBB demos) ─── */
  invoice: {
    key: 'invoice',
    name: 'Globex Corp Invoice Q2', type: 'INVOICE', chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#1d4ed8', iconPath: ICONS.doc,
    fileSize: '142 KB',
    agent: 'InvoiceBot', time: '4.2s', confidence: 94,
    subLabels: ['Received', '12 fields found', '4 checks run', 'AP Manager Queue', 'Done in 4.2s'],
    fields: [
      { name: 'Vendor Name',     value: 'Globex Corp',           conf: 98 },
      { name: 'Invoice Number',  value: 'GLX-2024-0441',         conf: 97 },
      { name: 'Invoice Date',    value: 'Apr 18, 2026',          conf: 96 },
      { name: 'Total Amount',    value: '$87,400.00',            conf: 99 },
      { name: 'PO Reference',    value: 'PO-2024-0891 ⚠',        conf: 94 },
      { name: 'Line Item 1',     value: 'Widget A × 200 @ $180', conf: 91 },
      { name: 'Line Item 2',     value: 'Widget B × 120 @ $215', conf: 89 },
      { name: 'Payment Terms',   value: 'Net 30',                conf: 95 },
      { name: 'Tax Amount',      value: '$7,035.00',             conf: 98 },
      { name: 'Approval Status', value: 'Needs Review',          conf: null },
    ],
    flags: [
      { color: 'red',   text: 'PO-2024-0891 not found in ERP — possible typo' },
      { color: 'amber', text: 'Amount $87,400 exceeds $10k auto-approval threshold' },
      { color: 'green', text: 'Vendor verified on approved vendor list' },
      { color: 'green', text: 'No duplicate invoice found in last 90 days' },
    ],
    routing: '→ AP Manager Queue — PO mismatch requires human review',
  },
  claim: {
    key: 'claim',
    name: 'Claim CL-8821 — Water Damage', type: 'CLAIM', chipCls: 'chip-amber',
    iconBg: '#fffbeb', iconColor: '#d97706', iconPath: ICONS.clipboard,
    fileSize: '2.1 MB',
    agent: 'ClaimsBot', time: '5.1s', confidence: 88,
    subLabels: ['Received', '9 fields found', '3 checks run', 'Adjuster Queue', 'Done in 5.1s'],
    fields: [
      { name: 'Claim Number',    value: 'CL-8821',              conf: 99 },
      { name: 'Policy Number',   value: 'POL-2021-44821',       conf: 98 },
      { name: 'Claimant',        value: 'Meridian Properties',  conf: 97 },
      { name: 'Incident Date',   value: 'Apr 12, 2026',         conf: 96 },
      { name: 'Claim Type',      value: 'Water Damage',         conf: 99 },
      { name: 'Claim Value',     value: '$142,000',             conf: 95 },
      { name: 'Deductible',      value: '$5,000',               conf: 97 },
      { name: 'Policy Status',   value: 'Active',               conf: 99 },
      { name: 'Approval Status', value: 'Needs Senior Adjuster',conf: null },
    ],
    flags: [
      { color: 'red',   text: 'Claim value $142,000 requires senior adjuster review' },
      { color: 'amber', text: 'Policy deductible of $5,000 not yet applied' },
      { color: 'green', text: 'Policy active and in good standing' },
      { color: 'green', text: 'No prior claims in last 24 months' },
    ],
    routing: '→ Senior Adjuster Queue — High-value claim requires manual review',
  },
  po: {
    key: 'po',
    name: 'Acme PO #4421 — Rush Order', type: 'PURCHASE ORDER', chipCls: 'chip-purple',
    iconBg: '#f5f3ff', iconColor: '#7c3aed', iconPath: ICONS.cart,
    fileSize: '88 KB',
    agent: 'POBot', time: '3.1s', confidence: 97,
    subLabels: ['Received', '8 fields found', '3 checks run', 'Auto-Approved', 'Done in 3.1s'],
    fields: [
      { name: 'PO Number',     value: 'PO-4421',              conf: 99 },
      { name: 'Vendor',        value: 'Acme Industrial',      conf: 98 },
      { name: 'Order Date',    value: 'Apr 20, 2026',         conf: 99 },
      { name: 'Delivery Date', value: 'Apr 24, 2026 (Rush)',  conf: 97 },
      { name: 'SKU 1',         value: 'ACM-7701 × 500',       conf: 96 },
      { name: 'SKU 2',         value: 'ACM-7702 × 250',       conf: 95 },
      { name: 'SKU 3',         value: 'ACM-7703 × 100',       conf: 94 },
      { name: 'Total Value',   value: '$34,200',              conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'All 3 SKUs found in inventory system' },
      { color: 'amber', text: 'Rush delivery surcharge of $1,200 applied' },
      { color: 'green', text: 'Vendor approved and within credit limit' },
    ],
    routing: '→ Auto-Approved — All checks passed, within threshold',
  },
  qc: {
    key: 'qc',
    name: 'QC Report — Batch 2024-B', type: 'QC REPORT', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '340 KB',
    agent: 'CNCBot', time: '3.8s', confidence: 92,
    subLabels: ['Received', '11 fields found', '5 checks run', 'Plant Manager Notified', 'Done in 3.8s'],
    fields: [
      { name: 'Batch ID',        value: '2024-B',                         conf: 99 },
      { name: 'Plant',           value: 'Houston TX — Line 3',            conf: 98 },
      { name: 'Inspection Date', value: 'Apr 19, 2026',                   conf: 99 },
      { name: 'Units Inspected', value: '2,400',                          conf: 97 },
      { name: 'Pass Rate',       value: '99.2% (2,381/2,400)',            conf: 96 },
      { name: 'Defect 1',        value: 'Surface crack — 12 units',       conf: 94 },
      { name: 'Defect 2',        value: 'Dimensional variance — 7 units', conf: 91 },
      { name: 'Hold Status',     value: 'Partial Hold — 19 units',        conf: null },
    ],
    flags: [
      { color: 'amber', text: '19 units flagged — surface crack and dimensional variance' },
      { color: 'amber', text: 'Partial batch hold applied pending re-inspection' },
      { color: 'green', text: '2,381 units cleared for shipment' },
      { color: 'green', text: 'Defect rate 0.79% — within 1% threshold' },
    ],
    routing: '→ Plant Manager Queue — Partial hold requires sign-off',
  },
  contract: {
    key: 'contract',
    name: 'Vendor Contract — Gulf Coast', type: 'CONTRACT', chipCls: 'chip-purple',
    iconBg: '#fdf4ff', iconColor: '#7e22ce', iconPath: ICONS.doc,
    fileSize: '1.2 MB',
    agent: 'ContractBot', time: '6.2s', confidence: 89,
    subLabels: ['Received', '14 fields found', '6 checks run', 'Legal Review Queue', 'Done in 6.2s'],
    fields: [
      { name: 'Contract ID',    value: 'CTR-2026-GC-041',     conf: 99 },
      { name: 'Vendor',         value: 'Gulf Coast Logistics',conf: 98 },
      { name: 'Effective Date', value: 'May 1, 2026',         conf: 97 },
      { name: 'Expiry Date',    value: 'Apr 30, 2028',        conf: 96 },
      { name: 'Contract Value', value: '$4.2M over 24 months',conf: 94 },
      { name: 'Auto-Renewal',   value: 'Yes — 60-day notice', conf: 91 },
      { name: 'Penalty Clause', value: '2% per week delay',   conf: 88 },
      { name: 'Governing Law',  value: 'Texas',               conf: 97 },
    ],
    flags: [
      { color: 'amber', text: 'Auto-renewal clause — 60-day notice window opens Jun 1, 2027' },
      { color: 'amber', text: 'Penalty clause 2%/week — above standard 1% threshold' },
      { color: 'green', text: 'Vendor insurance certificates verified' },
      { color: 'green', text: 'No conflicting exclusivity clauses found' },
    ],
    routing: '→ Legal Review Queue — Non-standard penalty clause requires approval',
  },
  alert: {
    key: 'alert',
    name: 'Supply Chain Alert — Vinyl Resin', type: 'ALERT', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#dc2626', iconPath: ICONS.warning,
    fileSize: '67 KB',
    agent: 'LogisticsBot', time: '4.7s', confidence: 96,
    subLabels: ['Received', '8 fields found', 'BOM traversal run', '3 Plants Notified', 'Done in 4.7s'],
    fields: [
      { name: 'Alert ID',        value: 'SC-ALERT-2026-0441',           conf: 99 },
      { name: 'Component',       value: 'Vinyl Resin (VR-2201)',         conf: 99 },
      { name: 'Supplier',        value: 'ChemCo Industries',             conf: 98 },
      { name: 'Delay Duration',  value: '7 days',                        conf: 97 },
      { name: 'Affected Plants', value: 'Houston, Dallas, Memphis',      conf: 96 },
      { name: 'Finished Goods',  value: '14 SKUs affected',              conf: 95 },
      { name: 'Revenue at Risk', value: '$1.09M',                        conf: 94 },
      { name: 'Alt Supplier',    value: 'PolySource Inc — 3-day lead',   conf: 91 },
    ],
    flags: [
      { color: 'red',   text: '$1.09M revenue at risk across 3 plants' },
      { color: 'red',   text: 'Houston Line 2 will halt in 48 hours without action' },
      { color: 'amber', text: 'Alt supplier PolySource available — 15% premium' },
      { color: 'green', text: 'Dallas and Memphis have 5-day buffer stock' },
    ],
    routing: '→ Supply Chain Director + 3 Plant Managers notified',
  },

  /* ──────── STP Phase 2 samples ──────── */

  stp_policy: {
    key: 'stp_policy',
    name: 'STP-415 · Business Travel Policy', type: 'POLICY', chipCls: 'chip-blue',
    iconBg: '#eef2ff', iconColor: '#1e3a8a', iconPath: ICONS.doc,
    fileSize: '142 KB',
    agent: 'PolicyAgent', time: '4.2s', confidence: 99,
    subLabels: ['Header parsed', 'Sections indexed', 'Citations cached', 'Verbatim ready', 'Done in 4.2s'],
    fields: [
      { name: 'Doc number',     value: 'STP-415',                                                                conf: 99 },
      { name: 'Title',          value: 'Business Travel & Per-Diem Allowances',                                  conf: 99 },
      { name: 'Revision',       value: 'Rev 4',                                                                  conf: 99 },
      { name: 'Effective date', value: '2024-06-01',                                                             conf: 99 },
      { name: 'Owner',          value: 'STP Finance / Travel Services',                                          conf: 99 },
      { name: 'Section 3.2',    value: '$75/day meal allowance · inclusive of gratuity',                         conf: 99 },
      { name: 'NRC class',      value: 'Public',                                                                 conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'All required header fields present (doc#, rev, effective date, owner)' },
      { color: 'green', text: 'Verbatim citation ready — Section 3.2 quoted directly' },
      { color: 'green', text: 'NRC classification = Public · safe to share with auditors' },
    ],
    routing: '→ PolicyAgent · indexed for verbatim retrieval by ChatSTP',
  },

  stp_pm_history: {
    key: 'stp_pm_history',
    name: 'WO-2026-00871 · P-3A Work Package', type: 'WORK PACKAGE', chipCls: 'chip-blue',
    iconBg: '#eef2ff', iconColor: '#1e3a8a', iconPath: ICONS.clipboard,
    fileSize: '5.7 KB',
    agent: 'MaintenanceAgent', time: '3.1s', confidence: 99,
    subLabels: ['WO matched', 'Engineers attributed', 'eAM cross-ref', 'Sign-offs verified', 'Done in 3.1s'],
    fields: [
      { name: 'WO id',           value: 'WO-2026-00871',                                                          conf: 99 },
      { name: 'Equipment',       value: 'P-3A · RCS · Westinghouse Model-93A',                                    conf: 99 },
      { name: 'Type',            value: 'Preventive · PM-7B (RCP Bearing Inspection)',                            conf: 99 },
      { name: 'Opened / Closed', value: '2026-03-18 08:00 / 14:30 CST',                                           conf: 99 },
      { name: 'Lead engineer',   value: 'Diane Okafor (EMP-1042)',                                                conf: 99 },
      { name: 'Technicians',     value: 'Marcus Holloway (EMP-2117), Jamal Greene (EMP-2243)',                    conf: 99 },
      { name: 'Procedure',       value: '0PMP-RCS-7B Rev 2',                                                      conf: 99 },
      { name: 'Hours charged',   value: '6.5 hr',                                                                 conf: 98 },
      { name: 'Sign-offs',       value: 'Lead + 2 Techs + Ops Review + QA Verification',                          conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'All acceptance criteria met (vibration ≤ 0.20 in/s post-maintenance)' },
      { color: 'green', text: 'Two-person LOTO verification documented per OSHA 1910.147' },
      { color: 'amber', text: 'Post-maintenance vibration 0.21 in/s — within tolerance per ED #ED-2026-014' },
    ],
    routing: '→ MaintenanceAgent · cross-references with engineer_attribution + WP archive',
  },

  stp_issue_analysis: {
    key: 'stp_issue_analysis',
    name: 'P-3A · 9-event Failure-Mode Aggregate', type: 'INCIDENT BUNDLE', chipCls: 'chip-amber',
    iconBg: '#fff7ed', iconColor: '#ea580c', iconPath: ICONS.warning,
    fileSize: '23.4 KB',
    agent: 'DiagnosticsAgent', time: '6.2s', confidence: 94,
    subLabels: ['9 events parsed', 'Modes classified', '5 modes ranked', 'WO citations resolved', 'Done in 6.2s'],
    fields: [
      { name: 'Asset',                 value: 'P-3A (RCS · Westinghouse Model-93A)',                       conf: 99 },
      { name: 'Events analyzed',       value: '9 historical (2021–2026)',                                   conf: 99 },
      { name: 'Top mode',              value: 'bearing_seizure · 33% of events · typical lead 14d',        conf: 95 },
      { name: 'Cited WOs',             value: 'WO-2025-03311, WO-2025-03987, WO-2026-00188',                conf: 99 },
      { name: '#2 mode',               value: 'seal_leak · 22% · typical lead 21d',                         conf: 92 },
      { name: '#3 mode',               value: 'vibration_excursion · 11% · typical lead 10d',               conf: 91 },
      { name: 'Most-cited mitigation', value: 'Replace bearing + verify lube oil quality',                  conf: 96 },
    ],
    flags: [
      { color: 'amber', text: 'Bearing-seizure pattern dominant — 3 events in last 12 months' },
      { color: 'amber', text: 'Common root cause: lube oil contamination (corrected in 2026 chemistry SOP)' },
      { color: 'green', text: 'No fabricated modes — every claim cited by at least one WO id' },
    ],
    routing: '→ DiagnosticsAgent · feeds ReliabilityAgent priors',
  },

  stp_predictive: {
    key: 'stp_predictive',
    name: 'P-3A · Vibration Anomaly · ANOM-P3A-2026-04-22', type: 'SENSOR ALERT', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#dc2626', iconPath: ICONS.warning,
    fileSize: '4.2 KB',
    agent: 'ReliabilityAgent', time: '9.1s', confidence: 87,
    subLabels: ['Anomaly z-score 3.7', 'RUL forecast generated', 'Risk tier set', 'PM advance recommended', 'Done in 9.1s'],
    fields: [
      { name: 'Equipment',             value: 'P-3A · RCS',                                                  conf: 99 },
      { name: 'Anomaly id',            value: 'ANOM-P3A-2026-04-22',                                         conf: 99 },
      { name: 'Sensor channel',        value: 'vibration_axial_in_per_s',                                    conf: 99 },
      { name: 'Current value',         value: '0.34 in/s (Tech-Spec limit 0.30)',                            conf: 98 },
      { name: 'Trend',                 value: 'rising 12% week-over-week',                                   conf: 96 },
      { name: 'Risk tier',             value: 'CRITICAL · z-score 3.7',                                      conf: 95 },
      { name: 'Predicted failure',     value: '11 days (CI 80%: 7-14d)',                                     conf: 87 },
      { name: 'Recommended PM',        value: 'PM-7B advance · Day 22 → Day 5',                              conf: 92 },
      { name: 'Estimated avoidance',   value: '$340,000 + 18 outage hours',                                  conf: 92 },
    ],
    flags: [
      { color: 'red',   text: 'CRITICAL · pattern matches 3 prior bearing-degradation events' },
      { color: 'red',   text: 'Days-to-failure window is shorter than current PM cadence' },
      { color: 'amber', text: 'Recommend HUMAN APPROVAL before PM-7B advance · sent to /review' },
    ],
    routing: '→ ReliabilityAgent · routed to Human Review (URGENT)',
  },

  /* ──────── Telecommunications · Verizon Far Edge POC ──────── */

  tel_robot_xml: {
    key: 'tel_robot_xml',
    name: 'CYCLE-20260115-CAAS-B-2412 · ROBOT Test Output',
    type: 'ROBOT XML', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#b91c1c', iconPath: ICONS.doc,
    fileSize: '104 KB',
    agent: 'CertificationAgent', time: '14.8s', confidence: 99,
    subLabels: ['Suite parsed', '247 tests classified', '12 P1 / 1 P2 / 2 P3', 'JIRA payloads built', 'Done in 14.8s'],
    fields: [
      { name: 'Cycle id',           value: 'CYCLE-20260115-CAAS-B-2412',                       conf: 99 },
      { name: 'Device',             value: 'CaaS-Edge-Node-Type-B',                            conf: 99 },
      { name: 'Firmware',           value: 'Wind River 24.12',                                 conf: 99 },
      { name: 'Region',             value: 'Northeast',                                        conf: 99 },
      { name: 'Total tests',        value: '247',                                              conf: 99 },
      { name: 'Pass / fail / warn', value: '231 / 12 / 4',                                     conf: 99 },
      { name: 'Schema drift events',value: '3 (Redfish v1.14 → v1.16 breaking)',               conf: 98 },
      { name: 'Top failure',        value: 'CU-UP latency 8.3 ms vs 5 ms (KB-2026-0118)',      conf: 95 },
      { name: 'Hours saved',        value: '38.2 hr vs manual 40 hr cycle',                    conf: 96 },
    ],
    flags: [
      { color: 'red',   text: '12 P1 failures · wave deployment HOLD recommended' },
      { color: 'amber', text: '11 of 12 P1s trace to known root causes with documented fixes' },
      { color: 'green', text: 'Audit Lens trace ID DVR-20260115-091422-007 — full reproducibility' },
    ],
    routing: '→ CertificationAgent · 12 JIRA tickets queued + epic APEXVZ-SCHEMA-EPIC-2026-01',
  },

  tel_redfish_diff: {
    key: 'tel_redfish_diff',
    name: 'Redfish v1.14.0 → v1.16.0 · Breaking Change Detection',
    type: 'SCHEMA DIFF', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#b91c1c', iconPath: ICONS.warning,
    fileSize: '8.4 KB',
    agent: 'SchemaWatchAgent', time: '6.2s', confidence: 99,
    subLabels: ['Baseline + current loaded', '3 breaking deltas found', '14 scripts mapped', 'JIRA epic drafted', 'Done in 6.2s'],
    fields: [
      { name: 'Baseline schema',     value: 'Redfish v1.14.0 (Wind River 24.06)',              conf: 99 },
      { name: 'Current schema',      value: 'Redfish v1.16.0 (Wind River 24.12)',              conf: 99 },
      { name: 'Breaking changes',    value: '3 (PowerState · FanSpeeds · IPv6Addresses)',      conf: 99 },
      { name: 'Path migration',      value: 'PowerState → Status.PowerState',                  conf: 99 },
      { name: 'Field rename',        value: 'FanSpeeds[].CurrentReading → Fans[].Reading',     conf: 99 },
      { name: 'New required field',  value: 'IPv6Addresses (was optional)',                    conf: 99 },
      { name: 'Scripts impacted',    value: '14 (6 + 5 + 3)',                                  conf: 99 },
      { name: 'Detection lead time', value: '6 days before scheduled cycle',                    conf: 99 },
      { name: 'Effort to remediate', value: '2.0 hr engineering · deterministic find/replace', conf: 98 },
    ],
    flags: [
      { color: 'red',   text: 'Wave deployment auto-held until epic completes' },
      { color: 'amber', text: 'Same drift pattern historically led to reactive remediation cycles' },
      { color: 'green', text: 'Detection 6 days ahead · enough runway to remediate before cycle' },
    ],
    routing: '→ SchemaWatchAgent · APEXVZ-SCHEMA-EPIC-2026-01 created with 5 subtasks',
  },

  tel_upgrade_runbook: {
    key: 'tel_upgrade_runbook',
    name: 'VZ-Upgrade-Procedures-2026 · Rev 4 (67 pp)',
    type: 'UPGRADE RUNBOOK', chipCls: 'chip-blue',
    iconBg: '#eff6ff', iconColor: '#1e40af', iconPath: ICONS.clipboard,
    fileSize: '67 pp · 412 KB',
    agent: 'UpgradeAdvisorAgent', time: '8.7s', confidence: 96,
    subLabels: ['Procedures indexed', 'Paths cross-referenced', 'Online-risk computed', 'PMT extracted', 'Done in 8.7s'],
    fields: [
      { name: 'Document',         value: 'VZ-Upgrade-Procedures-2026 · Rev 4',                 conf: 99 },
      { name: 'Pages',            value: '67',                                                 conf: 99 },
      { name: 'Owner',            value: 'Cert Team · HQ Planning',                            conf: 99 },
      { name: 'Supported paths',  value: '22.12 → 23.06 → 24.01 → 24.12 (Type-B)',             conf: 98 },
      { name: 'Blocked paths',    value: 'Direct skip > 1 release (e.g. 23.06 → 24.12)',       conf: 99 },
      { name: 'Pre-flight check', value: 'site_readiness_check.yml (15 min per site)',          conf: 96 },
      { name: 'PMT scope',        value: 'post_upgrade_smoke.robot · 12 quick assertions',     conf: 97 },
      { name: 'Rollback',         value: 'rollback_to_checkpoint.yml · BMC snapshot restore',  conf: 99 },
      { name: 'Citation anchor',  value: '§2 · Step-by-step 22.12 → 24.12',                    conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'All 14 sections indexed · citation anchors resolved for MentorAgent' },
      { color: 'green', text: 'Compatibility matrix cross-referenced against current fleet inventory' },
      { color: 'amber', text: 'Northeast 23.06 → 24.01 path flagged · 25% historical failure rate' },
    ],
    routing: '→ UpgradeAdvisorAgent · feeds wave-planning HITL gate',
  },

  tel_kb_article: {
    key: 'tel_kb_article',
    name: 'KB-2026-0118 · CU-UP Latency Under Default RT Tuning',
    type: 'KB ARTICLE', chipCls: 'chip-amber',
    iconBg: '#fff7ed', iconColor: '#ea580c', iconPath: ICONS.doc,
    fileSize: '11.4 KB',
    agent: 'MentorAgent', time: '3.4s', confidence: 92,
    subLabels: ['Article retrieved', 'Symptoms matched', 'Workaround extracted', 'Permanent fix cited', 'Done in 3.4s'],
    fields: [
      { name: 'Article id',         value: 'KB-2026-0118',                                     conf: 99 },
      { name: 'Severity',           value: 'High · production-blocker under sustained load',   conf: 99 },
      { name: 'Affected',           value: 'CaaS-Node-Type-B · Wind River 24.06 + 24.12',      conf: 99 },
      { name: 'Symptom',            value: 'CU-UP P99 latency 6–8 ms vs 5 ms threshold',       conf: 98 },
      { name: 'Root cause',         value: 'kernel.sched_rt_runtime_us default 950000 too low',conf: 95 },
      { name: 'Workaround',         value: 'Set sched_rt_runtime_us=980000 in 99-rt-tune.conf',conf: 99 },
      { name: 'Permanent fix',      value: 'Wind River 25.01 base image (default 980000)',     conf: 96 },
      { name: 'Ansible playbook',   value: 'apex-rt-tune.yml (drops sysctl, reboots in MW)',   conf: 98 },
      { name: 'Cross-ref tickets',  value: 'APEXVZ-2418, APEXVZ-2419 (12 P1 cycle failures)',  conf: 92 },
    ],
    flags: [
      { color: 'amber', text: 'Article matched against 11 of 12 P1 failures in current cycle' },
      { color: 'green', text: 'Workaround pre-validated · 252 Northeast Type-B sites eligible' },
      { color: 'green', text: 'No hallucinations · all facts cite KB-2026-0118 or release notes' },
    ],
    routing: '→ MentorAgent · cited verbatim in 4 ChatVZ responses this week',
  },

  /* ════════ VERIZON FAR EDGE · 12 REAL firmware reports (James Patchett · MTCE Lab) ════════ */

  vz_dmtf_e930t: {
    key: 'vz_dmtf_e930t',
    name: 'HPE_E930t_BMC_1-57_DMTF-conformance-MEAKV-507.md',
    type: 'DMTF CONFORMANCE · REAL', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#b91c1c', iconPath: ICONS.doc,
    fileSize: '96 KB',
    agent: 'CertificationAgent', time: '12.4s', confidence: 98,
    subLabels: ['Redfish-Protocol-Validator v1.2.0 parsed', '430 assertions classified', '7 FAIL triaged', 'Production-irrelevance rule applied', 'Done in 12.4s'],
    fields: [
      { name: 'Platform',       value: 'HPE Edgeline E930t · Sapphire Rapids',                 conf: 99 },
      { name: 'Controller',     value: 'iLO 6 v1.57 · BIOS H11 v1.11',                          conf: 99 },
      { name: 'Test case',      value: 'MEAKV-507 · DMTF Redfish Conformance',                  conf: 99 },
      { name: 'Result summary', value: 'PASS: 392 · FAIL: 7 · WARN: 0 · NOT_TESTED: 31',        conf: 99 },
      { name: 'Failure class',  value: 'WWW-Authenticate header (6) + X.509 IPv6 cert (1)',     conf: 97 },
      { name: 'Triage verdict', value: 'Not relevant to Redfish operation w/ VCPfe in prod',     conf: 96 },
      { name: 'Engineer note',  value: '"marked test passed" — James Patchett, MTCE Lab',       conf: 99 },
      { name: 'Manual effort',  value: '~40 hr/firmware × 42 HPE reports historically',          conf: 95 },
    ],
    flags: [
      { color: 'amber', text: '7 conformance FAILs — all known-benign, recur identically across the fleet' },
      { color: 'green', text: 'Same 7-failure signature on iLO5 3.06 / iLO6 1.60 / ZT BMC — one rule covers all' },
      { color: 'green', text: 'Auto-certified · JIRA evidence attached · matches James’s manual verdict 100%' },
    ],
    routing: '→ CertificationAgent · auto-cert with cited production-irrelevance rule · HITL gate for sign-off',
  },

  vz_samsung_ssd: {
    key: 'vz_samsung_ssd',
    name: 'ZT_Proteus_BMC_46_MEAKV-1792_Samsung_SSD_Temp_Issue.md',
    type: 'PRODUCTION REGRESSION · REAL', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#b91c1c', iconPath: ICONS.warning,
    fileSize: '38 KB',
    agent: 'SchemaWatchAgent', time: '7.1s', confidence: 97,
    subLabels: ['.45 vs .46 BMC compared', 'Samsung PM9A3 thermal read tested', 'Fan-spike regression confirmed', 'Wave block recommended', 'Done in 7.1s'],
    fields: [
      { name: 'Platform',       value: 'ZT Proteus · BMC 0.46 (regression in 0.45)',           conf: 99 },
      { name: 'Test case',      value: 'MEAKV-1792 · Samsung SSD Temperature Issue',            conf: 99 },
      { name: 'Drive',          value: 'SAMSUNG PM9A3 (MZQL21T9HCJR-00A07)',                    conf: 99 },
      { name: 'Failure mode',   value: '.45 BMC cannot read PM9A3 temp → fans spike to 100%',   conf: 98 },
      { name: 'Fix',            value: 'BMC .46 restores thermal read · fans nominal',          conf: 99 },
      { name: 'Repro',          value: 'Lab-confirmed: downgrade .46→.45 reproduces fan spike', conf: 96 },
      { name: 'Blast radius',   value: 'Any subcloud with Samsung PM9A3 drives on BMC .45',     conf: 95 },
      { name: 'Recommendation', value: 'BLOCK .45 deploy to PM9A3 sites · mandate .46',         conf: 97 },
    ],
    flags: [
      { color: 'red',   text: 'BMC .45 = thermal regression · 100% fan utilization on Samsung PM9A3' },
      { color: 'red',   text: 'Wave deployment HOLD for all PM9A3-equipped Proteus subclouds' },
      { color: 'green', text: 'BMC .46 validated fix · lab-reproduced · safe to roll forward' },
    ],
    routing: '→ SchemaWatchAgent · regression flagged · UpgradeAdvisor blocks .45 wave to PM9A3 sites',
  },

  vz_bmc_upgrade: {
    key: 'vz_bmc_upgrade',
    name: 'ZT_Proteus_BMC_46_2105p6_upgrade_to_2112p10.md',
    type: 'UPGRADE VALIDATION · REAL', chipCls: 'chip-blue',
    iconBg: '#eff6ff', iconColor: '#1e40af', iconPath: ICONS.clipboard,
    fileSize: '54 KB',
    agent: 'UpgradeAdvisorAgent', time: '9.3s', confidence: 96,
    subLabels: ['Baseline captured', 'WRCP 21.05p6 → 21.12p10 path validated', 'Alarms reconciled', 'Post-upgrade smoke passed', 'Done in 9.3s'],
    fields: [
      { name: 'Platform',       value: 'ZT Proteus · BMC 0.46 · BIOS 0.23',                     conf: 99 },
      { name: 'Upgrade path',   value: 'WRCP 21.05p6 → 21.12p10 (subcloud)',                    conf: 99 },
      { name: 'Subcloud',       value: 'welktxef-d931856-008 (anonymized OAM/BMC)',             conf: 98 },
      { name: 'Pre-state',      value: 'sync_status out-of-sync (kubernetes + load alarms)',     conf: 97 },
      { name: 'Post-state',     value: 'update 21.05-30 → 21.12-46 completed · apps uploaded',   conf: 98 },
      { name: 'System mode',    value: 'duplex · Standard · system controller distributed',     conf: 99 },
      { name: 'Validation',     value: 'fm alarm-list clean · application-list reconciled',      conf: 96 },
    ],
    flags: [
      { color: 'green', text: 'WRCP 21.05p6 → 21.12p10 path validated end-to-end on Proteus' },
      { color: 'amber', text: 'Pre-upgrade out-of-sync alarms expected · cleared post-upgrade' },
      { color: 'green', text: 'Safe upgrade path · added to compatibility matrix for wave planning' },
    ],
    routing: '→ UpgradeAdvisorAgent · path certified · feeds wave deployment risk model',
  },

  vz_ptu_perf: {
    key: 'vz_ptu_perf',
    name: 'HPE_E930t_BMC_1-57_Performance_testing_MEAKV-642-646.md',
    type: 'PTU PERFORMANCE · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '44 KB',
    agent: 'CertificationAgent', time: '8.8s', confidence: 97,
    subLabels: ['PTU stress harness parsed', 'Thermal + power envelope checked', 'Throttle events scanned', 'Within spec', 'Done in 8.8s'],
    fields: [
      { name: 'Platform',       value: 'HPE Edgeline E930t · Sapphire Rapids',                  conf: 99 },
      { name: 'Controller',     value: 'iLO 6 v1.57 · BIOS H11 v1.11',                          conf: 99 },
      { name: 'Test case',      value: 'MEAKV-642-646 · PTU Performance',                       conf: 99 },
      { name: 'Workload',       value: 'Intel PTU CPU + memory stress · sustained',             conf: 98 },
      { name: 'Thermal',        value: 'No throttle · within Sapphire Rapids envelope',          conf: 97 },
      { name: 'Outcome',        value: 'PASS · power + thermal nominal under load',             conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Performance within spec · no thermal throttle under sustained PTU load' },
      { color: 'green', text: 'Baseline captured for cross-firmware perf regression tracking' },
    ],
    routing: '→ CertificationAgent · perf baseline logged · no action required',
  },

  vz_sensor_proteus: {
    key: 'vz_sensor_proteus',
    name: 'ZT_Proteus_BMC_3_02_Functional_Sensor_MEAKV-1789-1791.md',
    type: 'FUNCTIONAL SENSOR · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '41 KB',
    agent: 'CertificationAgent', time: '6.4s', confidence: 98,
    subLabels: ['IPMI sensor list parsed', 'Thresholds validated', 'PSU + CPU + DIMM temps checked', 'All nominal', 'Done in 6.4s'],
    fields: [
      { name: 'Platform',       value: 'ZT Proteus · BMC 3.02 · BIOS 0.30',                     conf: 99 },
      { name: 'Test case',      value: 'MEAKV-1789-1791 · Functional Sensor / Sensor List',     conf: 99 },
      { name: 'Sensors',        value: 'CPU DTS · PSU temps · DIMM · fan · voltage rails',      conf: 98 },
      { name: 'Thresholds',     value: 'All within OK band · no UNR/UC/LC trips',               conf: 98 },
      { name: 'Outcome',        value: 'PASS · sensor readout complete + accurate',            conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'Full sensor list present + within thresholds on BMC 3.02' },
      { color: 'green', text: 'No missing-sensor regression (contrast w/ Samsung PM9A3 on .45)' },
    ],
    routing: '→ CertificationAgent · sensor cert passed · feeds thermal telemetry model',
  },

  vz_bios_triton: {
    key: 'vz_bios_triton',
    name: 'ZT_Triton_BMC_2_31_Functional-BIOS_testing_MEAKV-508-517.md',
    type: 'FUNCTIONAL BIOS · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '39 KB',
    agent: 'CertificationAgent', time: '7.6s', confidence: 97,
    subLabels: ['BIOS attribute set parsed', 'Redfish BIOS/SD validated', 'PMS attributes checked', 'Settings persist', 'Done in 7.6s'],
    fields: [
      { name: 'Platform',       value: 'ZT Triton · BMC 2.31',                                  conf: 99 },
      { name: 'Test case',      value: 'MEAKV-508-517 · Functional BIOS',                       conf: 99 },
      { name: 'Method',         value: 'Redfish PATCH /Systems/Self/Bios/SD attributes',        conf: 98 },
      { name: 'Attributes',     value: 'PMS012 + power/perf profile knobs validated',          conf: 97 },
      { name: 'Persistence',    value: 'Settings survive host reboot · re-read confirms',       conf: 98 },
      { name: 'Outcome',        value: 'PASS · BIOS attribute control via Redfish working',     conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'BIOS attribute control via Redfish validated on Triton BMC 2.31' },
      { color: 'amber', text: 'Redfish PATCH during host boot returns 503 (retry logic required)' },
    ],
    routing: '→ CertificationAgent · BIOS cert passed · 503-during-boot noted for runbook',
  },

  vz_redfish_proteus: {
    key: 'vz_redfish_proteus',
    name: 'ZT_Proteus_BMC_46_Functional-Redfish_testing_MEAKV-648-655.md',
    type: 'FUNCTIONAL REDFISH · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '43 KB',
    agent: 'CertificationAgent', time: '6.9s', confidence: 98,
    subLabels: ['Redfish endpoints walked', 'Power/thermal/inventory checked', 'Task service validated', 'All responsive', 'Done in 6.9s'],
    fields: [
      { name: 'Platform',       value: 'ZT Proteus · BMC 0.46',                                 conf: 99 },
      { name: 'Test case',      value: 'MEAKV-648-655 · Functional Redfish',                    conf: 99 },
      { name: 'Endpoints',      value: 'Systems · Managers · Chassis · TaskService · Power',    conf: 98 },
      { name: 'Operations',     value: 'GET inventory · Manager.Reset task · power state',      conf: 98 },
      { name: 'Outcome',        value: 'PASS · all Redfish functional endpoints responsive',    conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'Full Redfish functional surface validated on Proteus BMC .46' },
      { color: 'green', text: 'Manager.Reset task lifecycle (New → Completed) verified' },
    ],
    routing: '→ CertificationAgent · Redfish functional cert passed',
  },

  vz_platform_deploy: {
    key: 'vz_platform_deploy',
    name: 'HPE_E930t_BMC_1-57_Platform-deployment_MEAKV-965.md',
    type: 'PLATFORM DEPLOYMENT · REAL', chipCls: 'chip-blue',
    iconBg: '#eff6ff', iconColor: '#1e40af', iconPath: ICONS.clipboard,
    fileSize: '47 KB',
    agent: 'UpgradeAdvisorAgent', time: '10.1s', confidence: 96,
    subLabels: ['WRCP subcloud install parsed', 'Controller + worker enrolled', 'Alarms reconciled', 'Platform healthy', 'Done in 10.1s'],
    fields: [
      { name: 'Platform',       value: 'HPE Edgeline E930t · iLO 6 v1.57',                      conf: 99 },
      { name: 'Test case',      value: 'MEAKV-965 · Platform Deployment',                       conf: 99 },
      { name: 'Stack',          value: 'Wind River Cloud Platform · subcloud install',          conf: 98 },
      { name: 'Topology',       value: 'duplex controllers + worker · distributed cloud',       conf: 98 },
      { name: 'Outcome',        value: 'PASS · subcloud enrolled · platform-integ healthy',     conf: 97 },
    ],
    flags: [
      { color: 'green', text: 'E930t subcloud deployed + enrolled to system controller cleanly' },
      { color: 'green', text: 'Platform-integ alarms cleared post-deploy · ready for workload' },
    ],
    routing: '→ UpgradeAdvisorAgent · deployment certified · subcloud added to fleet inventory',
  },

  vz_soak_galene: {
    key: 'vz_soak_galene',
    name: 'ZT_Galene_BMC_1-13_Soak-test-on-E2E-system.md',
    type: 'SOAK TEST (E2E) · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '52 KB',
    agent: 'CertificationAgent', time: '11.7s', confidence: 96,
    subLabels: ['7-day soak log parsed', 'PTP4L sync errors scanned', 'No drift accumulation', 'E2E stable', 'Done in 11.7s'],
    fields: [
      { name: 'Platform',       value: 'ZT Galene · BMC 1.13',                                  conf: 99 },
      { name: 'Test type',      value: 'Soak Test on E2E system · ~7 days',                      conf: 99 },
      { name: 'Window',         value: 'Apr 8 → Apr 15 2025 (7-day continuous)',                conf: 98 },
      { name: 'Monitored',      value: '/var/log/user.log · PTP4L sync error trend',            conf: 97 },
      { name: 'PTP state',      value: 'FAULTY → LISTENING on INIT_COMPLETE (expected init)',   conf: 96 },
      { name: 'Outcome',        value: 'PASS · no error accumulation over 7-day soak',          conf: 96 },
    ],
    flags: [
      { color: 'green', text: '7-day E2E soak clean · no PTP4L sync error accumulation' },
      { color: 'green', text: 'Galene BMC 1.13 stable for long-duration far-edge deployment' },
    ],
    routing: '→ CertificationAgent · soak cert passed · longevity baseline logged',
  },

  vz_dell_sensor: {
    key: 'vz_dell_sensor',
    name: 'Dell_PowerEdge_R7615_iDRAC_7.10.50.10_Functional-Sensor_MEAKV-1789.md',
    type: 'MULTI-VENDOR SENSOR · REAL', chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.doc,
    fileSize: '36 KB',
    agent: 'CertificationAgent', time: '6.2s', confidence: 98,
    subLabels: ['iDRAC Redfish sensors parsed', 'Cross-vendor schema normalized', 'Thresholds validated', 'All nominal', 'Done in 6.2s'],
    fields: [
      { name: 'Platform',       value: 'Dell PowerEdge R7615 (newest fleet addition)',          conf: 99 },
      { name: 'Controller',     value: 'iDRAC 7.10.50.10 · BIOS 1.8.3',                         conf: 99 },
      { name: 'Test case',      value: 'MEAKV-1789 · Functional Sensor / BMC Sensor Validation',conf: 99 },
      { name: 'Vendor parity',  value: 'iDRAC schema normalized vs HPE iLO + ZT BMC',           conf: 96 },
      { name: 'Outcome',        value: 'PASS · same MEAKV-1789 cert across 3 vendors',          conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Dell R7615 onboarded · same cert catalog works across HPE/ZT/Dell' },
      { color: 'amber', text: 'iDRAC via ProxyJump (vcpe-jumpserver2) · proves cross-vendor reach' },
    ],
    routing: '→ CertificationAgent · multi-vendor cert · one rule-set spans HPE + ZT + Dell',
  },

  vz_troubleshoot: {
    key: 'vz_troubleshoot',
    name: 'ZT_Proteus_BMC_43_troubleshooting.md',
    type: 'TROUBLESHOOTING · REAL', chipCls: 'chip-amber',
    iconBg: '#fff7ed', iconColor: '#ea580c', iconPath: ICONS.warning,
    fileSize: '40 KB',
    agent: 'SchemaWatchAgent', time: '5.8s', confidence: 94,
    subLabels: ['Redfish 503 error parsed', 'AMI service-state diagnosed', 'RedfishDBReset remediation found', 'Root cause logged', 'Done in 5.8s'],
    fields: [
      { name: 'Platform',       value: 'ZT Proteus · BMC 0.43 · early-rev',                     conf: 99 },
      { name: 'Symptom',        value: 'Redfish PATCH → 503 ServiceTemporarilyUnavailable',     conf: 98 },
      { name: 'AMI message',    value: 'Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting', conf: 97 },
      { name: 'Remediation',    value: 'AMIManager.RedfishDBReset (ResetAll) clears stuck DB',  conf: 95 },
      { name: 'Lesson',         value: 'Retry-after-boot + DB reset added to BMC playbook',     conf: 94 },
    ],
    flags: [
      { color: 'amber', text: 'Redfish 503 during host boot / inventory processing — known transient' },
      { color: 'green', text: 'RedfishDBReset remediation captured · folded into BMC playbook KB' },
    ],
    routing: '→ SchemaWatchAgent · transient classified · remediation added to MentorAgent KB',
  },

  vz_flexran: {
    key: 'vz_flexran',
    name: 'HPE_E930t_ILO6_1-60_FlexRAN_settings_MEAKV-1860.md',
    type: 'FLEXRAN SETTINGS · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '38 KB',
    agent: 'CertificationAgent', time: '7.2s', confidence: 96,
    subLabels: ['FlexRAN BIOS profile parsed', 'RT tuning knobs validated', 'C-state + P-state checked', 'RAN-ready', 'Done in 7.2s'],
    fields: [
      { name: 'Platform',       value: 'HPE Edgeline E930t · iLO 6 v1.60',                      conf: 99 },
      { name: 'Test case',      value: 'MEAKV-1860 · FlexRAN Settings',                         conf: 99 },
      { name: 'Profile',        value: 'Intel FlexRAN BIOS profile · RT-optimized',            conf: 97 },
      { name: 'Knobs',          value: 'C-state disable · P-state · uncore freq · HT settings', conf: 96 },
      { name: 'Outcome',        value: 'PASS · FlexRAN BIOS profile applied + verified',        conf: 97 },
    ],
    flags: [
      { color: 'green', text: 'FlexRAN RT BIOS profile validated on E930t iLO6 1.60 · RAN-ready' },
      { color: 'amber', text: 'Ties to KB-2026-0118 RT tuning (sched_rt_runtime_us) for CU-UP latency' },
    ],
    routing: '→ CertificationAgent · FlexRAN cert passed · cross-refs RT-tuning KB',
  },

  /* ════════ VERIZON CAS · current-gen campaign docs (June 2026) ════════ */

  vz_cas_el140: {
    key: 'vz_cas_el140',
    name: 'test-campaign-summary-HPE-EL140-Gen12-2026-06-10.md',
    type: 'NEW PLATFORM ONBOARDING · REAL', chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.clipboard,
    fileSize: '17 KB',
    agent: 'OrchestratorAgent', time: '11.8s', confidence: 97,
    subLabels: ['Blocked MEAKV detected', 'PROPOSED-20→32 designed', 'Executed ×5 iterations', 'Change-spec generated', 'Done in 11.8s'],
    fields: [
      { name: 'Platform',     value: 'HPE ProLiant Compute EL140 Gen12 (NEW)',         conf: 99 },
      { name: 'Controller',   value: 'iLO 7 v1.20.00 · BIOS v1.30 · 273-attr registry', conf: 99 },
      { name: 'Replaces',     value: 'BLOCKED MEAKV-1750 / MEAKV-1793 (unsupported)',   conf: 99 },
      { name: 'Test cases',   value: 'PROPOSED-20 → PROPOSED-32 (13 new, AI-designed)', conf: 98 },
      { name: 'Playbook',     value: '7 CHANGE · 7 NO-CHANGE · 1 VERIFY · 15 roles',    conf: 97 },
      { name: 'Outcome',      value: 'PASS WITH DEVIATIONS · 0 fails',                   conf: 98 },
    ],
    flags: [
      { color: 'amber', text: 'New server type — existing tests + BMC playbook BLOCKED until iLO7 support added' },
      { color: 'green', text: 'AI designed PROPOSED-20→32, ran ×5 iterations, generated the Ansible change-spec' },
      { color: 'amber', text: 'NEBS 62°C inlet threshold unset · new security-hardening role required' },
    ],
    routing: '→ OrchestratorAgent · end-to-end onboarding · HITL gates before every lab action',
  },

  vz_cas_xr8720: {
    key: 'vz_cas_xr8720',
    name: 'test-campaign-summary-Dell-XR8720t-iDRAC-1.30.10.51.md',
    type: 'CAMPAIGN SUMMARY · REAL', chipCls: 'chip-blue',
    iconBg: '#eff6ff', iconColor: '#1e40af', iconPath: ICONS.clipboard,
    fileSize: '14 KB',
    agent: 'CertificationAgent', time: '9.4s', confidence: 98,
    subLabels: ['40 tests parsed', 'MEAKV + PROPOSED classified', '10 deviations triaged', 'All accepted', 'Done in 9.4s'],
    fields: [
      { name: 'Platform',     value: 'Dell XR8720t · 17G DCS · Xeon 6776P-B GNR-D 72c/144t', conf: 99 },
      { name: 'Controller',   value: 'iDRAC 10 (1.30.10.51) · BIOS 1.1.3 · 410-attr',         conf: 99 },
      { name: 'Result',       value: '29 PASS · 10 PASS-DEV · 1 PARTIAL · 0 FAIL',            conf: 99 },
      { name: 'BIOS dev',     value: 'IommuSupport/NumaNodesPerSocket null (GNR-D vs R7615)', conf: 96 },
      { name: 'Conformance',  value: 'MEAKV-507 · 379 pass / 9 benign fails',                 conf: 97 },
      { name: 'LED quirk',    value: 'IndicatorLED "Off" → HTTP 400 (iDRAC10 Lit/Blink only)',conf: 96 },
    ],
    flags: [
      { color: 'green', text: '40 tests · 0 failures · all 10 deviations documented + accepted' },
      { color: 'amber', text: 'GNR-D BIOS attrs differ from AMD R7615 baseline — triaged as benign' },
      { color: 'green', text: 'TLS 1.3 default, TLS 1.0/1.1 rejected (PROPOSED-10 security posture)' },
    ],
    routing: '→ CertificationAgent · current-gen Dell cert · deviations triaged + accepted',
  },

  vz_cas_playbook_spec: {
    key: 'vz_cas_playbook_spec',
    name: 'playbook-change-spec-HPE-EL140-Gen12-2026-06-10.md',
    type: 'ANSIBLE CHANGE-SPEC · REAL', chipCls: 'chip-amber',
    iconBg: '#fff7ed', iconColor: '#ea580c', iconPath: ICONS.doc,
    fileSize: '22 KB',
    agent: 'PlaybookAgent', time: '8.9s', confidence: 96,
    subLabels: ['9 result files read', 'Cross-ref vs live playbook', '7 changes identified', 'Per-change diff + risk', 'Done in 8.9s'],
    fields: [
      { name: 'Target',       value: 'BMC playbook · commit 5ff15f7028 · v1.0-66548',     conf: 99 },
      { name: 'Assessment',   value: '7 CHANGE · 7 NO-CHANGE · 1 VERIFY · 15 role files',   conf: 99 },
      { name: 'New role',     value: 'security-hardening (does NOT exist) — PROPOSED-32',   conf: 98 },
      { name: 'Key change',   value: 'WorkloadProfile=vRAN exact-string (group_vars/HPE)',  conf: 98 },
      { name: 'Cross-plat',   value: 'RegistryPrefixes broadens fix to iLO6 + iLO7',        conf: 96 },
      { name: 'Status',       value: 'DRAFT — pending automation-team review',              conf: 99 },
    ],
    flags: [
      { color: 'amber', text: 'AI-generated Ansible change-spec — each change has current code → required change → reason → risk' },
      { color: 'green', text: 'This is a PROPOSAL — nothing applied until a human approves (HITL gate)' },
      { color: 'amber', text: 'Pulling real e930t reference values exposed iLO6 deviations too — broadened scope' },
    ],
    routing: '→ PlaybookAgent · gap analysis → change-spec · routed to Human Review for sign-off',
  },

  vz_cas_thermal: {
    key: 'vz_cas_thermal',
    name: 'thermal-sensor-comparison-idrac-1.30.10.51-vs-1.30.33.10.md',
    type: 'FIRMWARE DRIFT · REAL', chipCls: 'chip-red',
    iconBg: '#fef2f2', iconColor: '#b91c1c', iconPath: ICONS.warning,
    fileSize: '9 KB',
    agent: 'SchemaWatchAgent', time: '5.6s', confidence: 97,
    subLabels: ['2 iDRAC revs compared', 'Thermal endpoint diffed', 'Threshold drift found', 'NEBS gap flagged', 'Done in 5.6s'],
    fields: [
      { name: 'Platform',     value: 'Dell XR8720t · BIOS 1.1.3 (unchanged)',               conf: 99 },
      { name: 'Compared',     value: 'iDRAC 1.30.10.51 → 1.30.33.10',                       conf: 99 },
      { name: 'Sensors',      value: '2 temp + 16 fan · identical inventory (no new sensors)',conf: 99 },
      { name: 'Drift found',  value: 'Inlet-temp Warning thresholds null → -23°C / 58°C',    conf: 98 },
      { name: 'NEBS',         value: '62°C caution threshold context — populated in newer',  conf: 96 },
    ],
    flags: [
      { color: 'red',   text: 'iDRAC 1.30.10.51 left inlet-temp Warning thresholds NULL — a NEBS caution gap' },
      { color: 'green', text: 'iDRAC 1.30.33.10 populates -23°C / 58°C inlet warnings → roll forward' },
      { color: 'amber', text: 'Golden-config drift: production sites on the older rev are invisible to thermal alarms' },
    ],
    routing: '→ SchemaWatchAgent · firmware drift → golden-config + roll-forward recommendation',
  },

  vz_cas_wrcp: {
    key: 'vz_cas_wrcp',
    name: 'WRCP-24.09.301-platform-certification-campaign',
    type: 'PLATFORM CERT (OS LAYER) · REAL', chipCls: 'chip-green',
    iconBg: '#f0fdf4', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '390 MB campaign',
    agent: 'CertificationAgent', time: '14.2s', confidence: 96,
    subLabels: ['1080 sysbench runs aggregated', 'Latency/network/storage perf', 'K8s conformance', 'Deployment MOPs', 'Done in 14.2s'],
    fields: [
      { name: 'Release',      value: 'Wind River Cloud Platform 24.09.301 (vs 2212 baseline)', conf: 99 },
      { name: 'Layer',        value: 'OS / platform cert (distinct from BMC/firmware)',        conf: 99 },
      { name: 'Performance',  value: '1,080 sysbench runs × 6 HW types · 5 iterations each',    conf: 98 },
      { name: 'Coverage',     value: 'RBAC · K8s CPU Mgr · Redfish · HA · rehoming · sw-update',conf: 97 },
      { name: 'Conformance',  value: 'Kubernetes sonobuoy · deployment MOPs VZFWE-25/26',       conf: 97 },
      { name: 'Test IDs',     value: 'VZFWE-* / VZWFE-* / MEAKV-1658',                          conf: 96 },
    ],
    flags: [
      { color: 'green', text: 'Second cert layer — the OS/platform (WRCP), on top of the BMC/firmware layer' },
      { color: 'green', text: '1080 perf runs × 5 iterations — same multi-iteration rigor as firmware' },
      { color: 'amber', text: 'Deployment MOPs (VZFWE-25/26) + rehoming + software-update procedures captured' },
    ],
    routing: '→ CertificationAgent · platform-layer cert · feeds the same orchestration + golden-config',
  },

  /* ──────── Agentic Enterprise (66 Degrees vendor-neutral demos) ──────── */

  ae_inventory_alert: {
    key: 'ae_inventory_alert',
    name: 'Stockout Alert · SKU-892 · Dallas Promotion', type: 'INVENTORY ALERT', chipCls: 'chip-amber',
    iconBg: '#fff7ed', iconColor: '#ea580c', iconPath: ICONS.warning,
    fileSize: '2.1 KB',
    agent: 'OrchestratorAgent', time: '1.8s', confidence: 98,
    subLabels: ['Inventory checked', 'Supplier ranked', 'PO drafted', 'Approval queued', 'Done in 1.8s'],
    fields: [
      { name: 'SKU',                  value: 'SKU-892 · Wireless Earbuds Pro',                conf: 99 },
      { name: 'Demand',               value: '500 units · Dallas Spring Promotion 2026',      conf: 99 },
      { name: 'Total available',      value: '0 units (across 4 warehouses)',                  conf: 99 },
      { name: 'Recommended supplier', value: 'SUP-321 · Pacific Components Ltd.',              conf: 96 },
      { name: 'Lead time',            value: '3 days (within 11-day window)',                  conf: 99 },
      { name: 'On-time %',            value: '99.4%',                                          conf: 99 },
      { name: 'Defect rate YTD',      value: '0.0%',                                           conf: 99 },
      { name: 'Drafted PO total',     value: '$19,250 (500 × $38.50)',                         conf: 98 },
      { name: 'Approval queue',       value: 'merchandising@example.com (SLA 4h)',             conf: 99 },
    ],
    flags: [
      { color: 'amber', text: 'Total available = 0 — true stockout, not partial' },
      { color: 'green', text: 'Recommended supplier meets the campaign window with margin' },
      { color: 'green', text: 'PO routed to human approver — no auto-purchase per policy' },
    ],
    routing: '→ OrchestratorAgent · PO drafted, queued for human approval',
  },

  ae_lease_pdf: {
    key: 'ae_lease_pdf',
    name: 'Crescent Tower · Aurora Biotech Lease', type: 'COMMERCIAL LEASE', chipCls: 'chip-blue',
    iconBg: '#eff6ff', iconColor: '#2563eb', iconPath: ICONS.doc,
    fileSize: '38.4 KB',
    agent: 'LeaseAgent', time: '3.2s', confidence: 95,
    subLabels: ['OCR complete', 'Entities extracted', 'Confidence checked', 'Indexed to DuckDB', 'Done in 3.2s'],
    fields: [
      { name: 'Tenant name',         value: 'Aurora Biotech Solutions, Inc.',                 conf: 97 },
      { name: 'Landlord',            value: 'Crescent Tower Holdings, LLC',                    conf: 99 },
      { name: 'Premises',            value: '500 Lamar Street, Floor 14, Austin TX 78701',     conf: 96 },
      { name: 'Rentable sq ft',      value: '18,400',                                          conf: 99 },
      { name: 'Commencement',        value: '2024-01-01',                                      conf: 99 },
      { name: 'Expiration',          value: '2026-12-31',                                      conf: 95 },
      { name: 'Base rent',           value: '$48.00/sf/yr · $73,600/mo',                       conf: 96 },
      { name: 'Indemnification',     value: 'Present · 3-yr survival',                          conf: 92 },
      { name: 'Governing law',       value: 'State of Texas',                                  conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'All required fields extracted above 0.7 confidence threshold' },
      { color: 'green', text: 'Indemnification clause matched — discoverable via SQL LIKE \'%indemnify%\'' },
      { color: 'amber', text: 'Expiration in 2026 — renewal-window watch active' },
    ],
    routing: '→ LeaseAgent · indexed into DuckDB `leases` table · ready for SQL queries',
  },

  // EPROD · Oil & Gas — Midstream (15 samples)
  // Sourced from synthetic-data/eprod/. Filenames + descriptions match the
  // EPROD POC content (4 invoices, 3 POs, 2 MSAs, 2 engineering quotes,
  // 2 FERC tariff sheets, 2 JIB statements).
  eprod_inv_hal: {
    key: 'eprod_inv_hal',
    name: 'INV-HAL-2026-04-3847.txt',
    type: 'INVOICE',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '2.6 KB',
    agent: 'InvoiceAgent', time: '3.1s', confidence: 97,
    subLabels: ['Invoice received', 'Header + line items extracted', 'MSA-HAL-2024-03 matched', 'Coding approved', 'Done in 3.1s'],
    fields: [
      { name: 'Vendor',         value: 'Halliburton Energy Services', conf: 99 },
      { name: 'Invoice number', value: 'INV-HAL-2026-04-3847',         conf: 99 },
      { name: 'Invoice date',   value: 'April 2026',                    conf: 98 },
      { name: 'Amount',         value: '$184,500.00',                   conf: 99 },
      { name: 'MSA reference',  value: 'MSA-HAL-2024-03',               conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Rate card on MSA-HAL-2024-03 matches invoice line items' },
      { color: 'green', text: 'Auto-coded to GL — no human review needed' },
    ],
    routing: '→ InvoiceAgent · validates against MSA-HAL-2024-03',
  },
  eprod_inv_slb: {
    key: 'eprod_inv_slb',
    name: 'INV-SLB-2026-05-1129.txt',
    type: 'INVOICE',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '2.8 KB',
    agent: 'InvoiceAgent', time: '2.9s', confidence: 96,
    subLabels: ['Invoice received', 'Line items extracted', 'MSA-SLB-2025-0112 referenced', 'Coding approved', 'Done in 2.9s'],
    fields: [
      { name: 'Vendor',         value: 'Schlumberger',                  conf: 99 },
      { name: 'Invoice number', value: 'INV-SLB-2026-05-1129',          conf: 99 },
      { name: 'Invoice date',   value: 'May 2026',                       conf: 98 },
      { name: 'Amount',         value: '$142,800.00',                    conf: 99 },
      { name: 'MSA reference',  value: 'MSA-SLB-2025-0112',              conf: 97 },
    ],
    flags: [
      { color: 'green', text: 'Rate card on MSA-SLB-2025-0112 matches invoice' },
    ],
    routing: '→ InvoiceAgent · MSA-SLB-2025-0112 reference',
  },
  eprod_inv_bhi: {
    key: 'eprod_inv_bhi',
    name: 'INV-BHI-2026-05-0921.txt',
    type: 'INVOICE',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '2.7 KB',
    agent: 'InvoiceAgent', time: '3.4s', confidence: 92,
    subLabels: ['Invoice received', 'Line items extracted', 'Tax code TX-I mismatch flagged', 'Routed for review', 'Done in 3.4s'],
    fields: [
      { name: 'Vendor',         value: 'Baker Hughes',                  conf: 99 },
      { name: 'Invoice number', value: 'INV-BHI-2026-05-0921',          conf: 99 },
      { name: 'Invoice date',   value: 'May 2026',                       conf: 98 },
      { name: 'Amount',         value: '$87,400.00',                     conf: 99 },
      { name: 'Tax code',       value: 'TX-I (mismatch flag)',           conf: 88 },
    ],
    flags: [
      { color: 'amber', text: 'Tax code TX-I does not match expected jurisdiction — pending tax-team review' },
    ],
    routing: '→ InvoiceAgent · routed to AP analyst for tax code resolution',
  },
  eprod_inv_kiewit: {
    key: 'eprod_inv_kiewit',
    name: 'INV-KIEWIT-2026-05-0114.txt',
    type: 'INVOICE',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '2.9 KB',
    agent: 'InvoiceAgent', time: '3.2s', confidence: 95,
    subLabels: ['Invoice received', 'Progress milestone extracted', 'EPC schedule reconciled', 'Coding approved', 'Done in 3.2s'],
    fields: [
      { name: 'Vendor',         value: 'Kiewit Energy Group',           conf: 99 },
      { name: 'Invoice number', value: 'INV-KIEWIT-2026-05-0114',       conf: 99 },
      { name: 'Project',        value: 'Compressor station — progress billing', conf: 97 },
      { name: 'Amount',         value: '$412,000.00',                    conf: 99 },
      { name: 'MSA reference',  value: 'MSA-KIEWIT-2024-07',             conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Progress milestone matches EPC schedule on MSA-KIEWIT-2024-07' },
    ],
    routing: '→ InvoiceAgent · compressor station progress billing',
  },
  eprod_po_epc: {
    key: 'eprod_po_epc',
    name: 'PO-2026-EPC-4521.txt',
    type: 'PURCHASE ORDER',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.clipboard,
    fileSize: '3.0 KB',
    agent: 'POAgent', time: '2.4s', confidence: 96,
    subLabels: ['PO received', 'MSA-KIEWIT-2024-07 matched', 'Scope validated', 'Approval queued', 'Done in 2.4s'],
    fields: [
      { name: 'PO number',     value: 'PO-2026-EPC-4521',                conf: 99 },
      { name: 'Vendor',        value: 'Kiewit Energy Group',             conf: 99 },
      { name: 'Scope',         value: 'Compressor station civil works',  conf: 97 },
      { name: 'MSA reference', value: 'MSA-KIEWIT-2024-07',              conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Scope on PO matches Schedule B of MSA-KIEWIT-2024-07' },
    ],
    routing: '→ POAgent · references MSA-KIEWIT-2024-07 · compressor station civil works',
  },
  eprod_po_chem: {
    key: 'eprod_po_chem',
    name: 'PO-2026-CHEM-0892.txt',
    type: 'PURCHASE ORDER',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.clipboard,
    fileSize: '2.6 KB',
    agent: 'POAgent', time: '2.2s', confidence: 97,
    subLabels: ['PO received', 'Vendor matched', 'Blanket terms validated', 'Approval queued', 'Done in 2.2s'],
    fields: [
      { name: 'PO number',  value: 'PO-2026-CHEM-0892',                   conf: 99 },
      { name: 'Vendor',     value: 'ChemTreat',                            conf: 99 },
      { name: 'Scope',      value: 'Pipeline chemical treatment program',  conf: 97 },
      { name: 'Term',       value: '12-month blanket',                     conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Blanket-PO terms within approved annual ceiling' },
    ],
    routing: '→ POAgent · ChemTreat · pipeline chemical treatment program · 12-month blanket',
  },
  eprod_po_ops: {
    key: 'eprod_po_ops',
    name: 'PO-2026-OPS-2189.txt',
    type: 'PURCHASE ORDER',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.clipboard,
    fileSize: '2.6 KB',
    agent: 'POAgent', time: '2.3s', confidence: 96,
    subLabels: ['PO received', 'Vendor matched', 'Field-ops scope validated', 'Approval queued', 'Done in 2.3s'],
    fields: [
      { name: 'PO number', value: 'PO-2026-OPS-2189',                conf: 99 },
      { name: 'Vendor',    value: 'Schlumberger',                     conf: 99 },
      { name: 'Scope',     value: 'Slickline + wireline services',    conf: 97 },
      { name: 'Activity',  value: 'Field operations',                  conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Field-ops scope matches MSA rate card' },
    ],
    routing: '→ POAgent · Schlumberger · slickline + wireline · field operations',
  },
  eprod_msa_hal: {
    key: 'eprod_msa_hal',
    name: 'MSA-HAL-2024-03.txt',
    type: 'MSA',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '6.5 KB',
    agent: 'ContractAgent', time: '4.1s', confidence: 96,
    subLabels: ['MSA ingested', 'Scope + rate card extracted', 'Term validated', 'Indexed for AP referencing', 'Done in 4.1s'],
    fields: [
      { name: 'MSA ID',     value: 'MSA-HAL-2024-03',                                    conf: 99 },
      { name: 'Vendor',     value: 'Halliburton Energy Services',                         conf: 99 },
      { name: 'Term',       value: '24 months',                                           conf: 98 },
      { name: 'Scope',      value: 'Slickline, cementing, well intervention',             conf: 97 },
      { name: 'Rate card',  value: 'Included',                                            conf: 99 },
    ],
    flags: [
      { color: 'green', text: 'Rate card extracted — available for invoice validation' },
    ],
    routing: '→ ContractAgent · 24-month MSA · slickline, cementing, well intervention · rate card included',
  },
  eprod_msa_kiewit: {
    key: 'eprod_msa_kiewit',
    name: 'MSA-KIEWIT-2024-07.txt',
    type: 'MSA',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '6.2 KB',
    agent: 'ContractAgent', time: '4.0s', confidence: 95,
    subLabels: ['MSA ingested', 'Schedule B scope extracted', 'EPC milestones indexed', 'Indexed for AP referencing', 'Done in 4.0s'],
    fields: [
      { name: 'MSA ID',     value: 'MSA-KIEWIT-2024-07',                                  conf: 99 },
      { name: 'Vendor',     value: 'Kiewit Energy Group',                                  conf: 99 },
      { name: 'Scope',      value: 'EPC services · compressor stations · pipeline civil', conf: 97 },
      { name: 'Schedule B', value: 'Scope appendix attached',                              conf: 98 },
    ],
    flags: [
      { color: 'green', text: 'Schedule B scope indexed for milestone reconciliation' },
    ],
    routing: '→ ContractAgent · EPC services MSA · compressor stations, pipeline civil works · Schedule B scope',
  },
  eprod_quote_fluor: {
    key: 'eprod_quote_fluor',
    name: 'QUOTE-FLUOR-2026-Q2-0142.txt',
    type: 'ENGINEERING QUOTE',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '5.7 KB',
    agent: 'QuoteAgent', time: '3.6s', confidence: 94,
    subLabels: ['Quote received', 'Scope + effort extracted', 'Mont Belvieu project matched', 'Routed for engineering review', 'Done in 3.6s'],
    fields: [
      { name: 'Quote ID', value: 'QUOTE-FLUOR-2026-Q2-0142',           conf: 99 },
      { name: 'Vendor',   value: 'Fluor',                                conf: 99 },
      { name: 'Scope',    value: 'Process engineering scope',             conf: 96 },
      { name: 'Effort',   value: '12-week engagement',                    conf: 95 },
      { name: 'Project',  value: 'Mont Belvieu expansion',                conf: 96 },
    ],
    flags: [
      { color: 'green', text: 'Scope aligns with Mont Belvieu expansion charter' },
    ],
    routing: '→ QuoteAgent · Fluor process-engineering scope · 12-week effort · Mont Belvieu expansion',
  },
  eprod_quote_bechtel: {
    key: 'eprod_quote_bechtel',
    name: 'QUOTE-BECHTEL-2026-Q1-0089.txt',
    type: 'ENGINEERING QUOTE',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '5.8 KB',
    agent: 'QuoteAgent', time: '3.8s', confidence: 93,
    subLabels: ['Quote received', 'EPC phasing extracted', 'Marine terminal project matched', 'Routed for engineering review', 'Done in 3.8s'],
    fields: [
      { name: 'Quote ID', value: 'QUOTE-BECHTEL-2026-Q1-0089',         conf: 99 },
      { name: 'Vendor',   value: 'Bechtel',                              conf: 99 },
      { name: 'Scope',    value: 'Marine terminal expansion EPC',         conf: 96 },
      { name: 'Phasing',  value: 'Multi-phase delivery',                  conf: 95 },
    ],
    flags: [
      { color: 'green', text: 'EPC phasing aligns with marine-terminal charter' },
    ],
    routing: '→ QuoteAgent · Bechtel · marine terminal expansion EPC · multi-phase delivery',
  },
  eprod_tariff_ngl: {
    key: 'eprod_tariff_ngl',
    name: 'FERC-TARIFF-EPD-NGL-2026-001.txt',
    type: 'TARIFF SHEET',
    chipCls: 'chip-amber',
    iconBg: '#fffbeb', iconColor: '#f59e0b', iconPath: ICONS.doc,
    fileSize: '6.5 KB',
    agent: 'TariffAgent', time: '4.4s', confidence: 96,
    subLabels: ['Tariff received', 'Rate schedule extracted', 'Effective date validated', 'Indexed for gas-day enforcement', 'Done in 4.4s'],
    fields: [
      { name: 'Tariff ID',      value: 'FERC-EPD-NGL-47.12.0',          conf: 99 },
      { name: 'Pipeline',       value: 'Enterprise NGL Pipeline',         conf: 99 },
      { name: 'Effective date', value: '2026-07-01',                       conf: 99 },
      { name: 'Use case',       value: 'WOW · gas-day rate enforcement',  conf: 95 },
    ],
    flags: [
      { color: 'amber', text: 'Rate change effective 2026-07-01 — downstream systems must refresh' },
    ],
    routing: '→ TariffAgent · FERC-EPD-NGL-47.12.0 · effective 2026-07-01 · WOW use case',
  },
  eprod_tariff_crude: {
    key: 'eprod_tariff_crude',
    name: 'FERC-TARIFF-EPD-CRUDE-2026-002.txt',
    type: 'TARIFF SHEET',
    chipCls: 'chip-amber',
    iconBg: '#fffbeb', iconColor: '#f59e0b', iconPath: ICONS.doc,
    fileSize: '6.5 KB',
    agent: 'TariffAgent', time: '4.6s', confidence: 95,
    subLabels: ['Tariff received', 'Routing rules extracted', 'Seaway segment validated', 'Indexed for gas-day enforcement', 'Done in 4.6s'],
    fields: [
      { name: 'Tariff ID',  value: 'FERC-EPD-CRUDE-22.4.0',           conf: 99 },
      { name: 'Pipeline',   value: 'Enterprise Crude Pipeline',         conf: 99 },
      { name: 'Routing',    value: 'Seaway',                             conf: 96 },
      { name: 'Use case',   value: 'WOW · gas-day rate enforcement',    conf: 95 },
    ],
    flags: [
      { color: 'amber', text: 'Seaway routing change — gas-day enforcement engine must be reloaded' },
    ],
    routing: '→ TariffAgent · FERC-EPD-CRUDE-22.4.0 · Seaway routing · gas-day rate enforcement',
  },
  eprod_jib_p66: {
    key: 'eprod_jib_p66',
    name: 'JIB-PHILLIPS66-SWEENY-2026-04.txt',
    type: 'JIB STATEMENT',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#2563eb', iconPath: ICONS.chart,
    fileSize: '5.3 KB',
    agent: 'JIBAgent', time: '4.0s', confidence: 96,
    subLabels: ['JIB received', 'Working-interest split validated', 'AFE-2024-0882 matched', 'Posted to subledger', 'Done in 4.0s'],
    fields: [
      { name: 'Operator',          value: 'Phillips 66 (Sweeny Hub)',  conf: 99 },
      { name: 'Period',            value: 'April 2026',                 conf: 99 },
      { name: 'AFE',               value: 'AFE-2024-0882',              conf: 98 },
      { name: 'Working interest',  value: '50%',                         conf: 99 },
      { name: 'Use case',          value: 'WOW',                         conf: 95 },
    ],
    flags: [
      { color: 'green', text: '50% WI split matches joint-venture agreement' },
    ],
    routing: '→ JIBAgent · April 2026 JIB · AFE-2024-0882 · 50% working interest · WOW use case',
  },
  eprod_jib_targa: {
    key: 'eprod_jib_targa',
    name: 'JIB-TARGA-MONT-BELVIEU-2026-03.txt',
    type: 'JIB STATEMENT',
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#2563eb', iconPath: ICONS.chart,
    fileSize: '4.8 KB',
    agent: 'JIBAgent', time: '4.2s', confidence: 92,
    subLabels: ['JIB received', 'AFE-2025-0341 matched', 'Overrun flagged', 'Routed to JV controller', 'Done in 4.2s'],
    fields: [
      { name: 'Operator',  value: 'Targa (Mont Belvieu)',                  conf: 99 },
      { name: 'Period',    value: 'March 2026',                              conf: 99 },
      { name: 'AFE',       value: 'AFE-2025-0341',                           conf: 98 },
      { name: 'Scope',     value: 'Fractionation expansion',                  conf: 96 },
      { name: 'Variance',  value: 'OVERRUN flag — actual exceeds AFE budget', conf: 90 },
    ],
    flags: [
      { color: 'red', text: 'Overrun against AFE-2025-0341 — routed to JV controller for review' },
    ],
    routing: '→ JIBAgent · March 2026 JIB · AFE-2025-0341 · fractionation expansion · OVERRUN flag',
  },
  /* ─── CWFCU · CommunityWide FCU — 22 credit union sample files ─── */
  cwfcu_cip_rosales: {
    key: 'cwfcu_cip_rosales',
    name: "CIP-MEM-2026-0421-ROSALES.txt",
    type: "CIP PACKET",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '3.8 KB',
    agent: "Member Onboarding Agent", time: "2.4s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 2.4s`],
    fields: [
      { name: "Member", value: "ROSALES, Elena Maria", conf: 99 },
      { name: "Risk tier", value: "LOW", conf: 99 },
      { name: "OFAC", value: "CLEAR", conf: 99 },
      { name: "PEP", value: "NEGATIVE", conf: 99 },
      { name: "Account opened", value: "2026-04-21", conf: 99 }
    ],
    flags: [
      { color: "green", text: "All 14 CIP requirements (31 CFR § 1020.220) verifiably satisfied" },
      { color: "green", text: "100% OFAC + PEP coverage · auto-indexed to NCUA exam folder" }
    ],
    routing: "→ Member Onboarding Agent · LOW-risk · CIP folder indexed · hand-off to Compliance for standard CDD",
  },

  cwfcu_cip_nguyen: {
    key: 'cwfcu_cip_nguyen',
    name: "CIP-MEM-2026-0428-NGUYEN.txt",
    type: "CIP PACKET",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.doc,
    fileSize: '4.1 KB',
    agent: "Member Onboarding Agent", time: "2.7s", confidence: 97,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 2.7s`],
    fields: [
      { name: "Member", value: "NGUYEN, Tuan Khoa", conf: 99 },
      { name: "Risk tier", value: "MEDIUM", conf: 97 },
      { name: "PEP", value: "NEAR-MATCH (dismissed)", conf: 95 },
      { name: "OFAC", value: "CLEAR", conf: 99 },
      { name: "Account opened", value: "2026-04-28", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "PEP near-match dismissed by reviewer · documented" },
      { color: "green", text: "Enhanced monitoring activated · cash threshold $5,000" }
    ],
    routing: "→ Compliance Agent · enhanced monitoring · quarterly CDD touch",
  },

  cwfcu_cip_arrington: {
    key: 'cwfcu_cip_arrington',
    name: "CIP-MEM-2026-0512-ARRINGTON.txt",
    type: "CIP PACKET",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.doc,
    fileSize: '4.6 KB',
    agent: "Member Onboarding Agent", time: "38m", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 38m`],
    fields: [
      { name: "Member", value: "ARRINGTON, Devon C.", conf: 99 },
      { name: "Risk tier", value: "HIGH", conf: 98 },
      { name: "OFAC", value: "NEAR-MATCH (dismissed)", conf: 91 },
      { name: "ChexSystems", value: "Prior closure (2019)", conf: 97 },
      { name: "EDD", value: "Required", conf: 99 }
    ],
    flags: [
      { color: "red", text: "OFAC near-match dismissed · documented" },
      { color: "red", text: "EDD assigned · cash threshold reduced to $3,000" },
      { color: "red", text: "Subject of SAR-2026-0142 (filed Jun 4) — structuring pattern" }
    ],
    routing: "→ Compliance Agent · EDD active · feeds Loan Document Agent enhanced verification",
  },

  cwfcu_cip_okafor: {
    key: 'cwfcu_cip_okafor',
    name: "CIP-MEM-2026-0521-OKAFOR.txt",
    type: "CIP PACKET · BIZ",
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.doc,
    fileSize: '4.1 KB',
    agent: "Member Onboarding Agent", time: "23m", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 23m`],
    fields: [
      { name: "Entity", value: "Okafor Enterprises LLC", conf: 99 },
      { name: "Signer", value: "Okafor, Adaeze C.", conf: 99 },
      { name: "Beneficial Owner", value: "100% — single member", conf: 99 },
      { name: "Risk tier", value: "LOW", conf: 98 },
      { name: "D&B Score", value: "78", conf: 97 }
    ],
    flags: [
      { color: "green", text: "Beneficial ownership rule (31 CFR § 1010.230) verifiably satisfied" },
      { color: "green", text: "Single beneficial owner certified · no ownership obfuscation" }
    ],
    routing: "→ Member Onboarding Agent · Business CIP complete · CDD annual",
  },

  cwfcu_sar_structuring: {
    key: 'cwfcu_sar_structuring',
    name: "SAR-2026-0142-STRUCTURING.txt",
    type: "SAR · DRAFT",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.doc,
    fileSize: '6.0 KB',
    agent: "Compliance Agent", time: "3.0s", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 3.0s`],
    fields: [
      { name: "SAR ID", value: "SAR-2026-0142", conf: 99 },
      { name: "Subject", value: "Member #44821 (Arrington)", conf: 99 },
      { name: "Pattern", value: "Structuring", conf: 98 },
      { name: "Amount", value: "$47,300 / 7 txns", conf: 99 },
      { name: "Status", value: "Pending BSA Officer", conf: 99 }
    ],
    flags: [
      { color: "red", text: "Structuring pattern · 7 cash deposits across 4 branches · 16 days" },
      { color: "amber", text: "Pattern statistical confidence: 96.1%" },
      { color: "green", text: "Linked to CIP-MEM-2026-0512-ARRINGTON (EDD active at onboarding)" }
    ],
    routing: "→ Compliance Agent · narrative drafted · SAR deadline Jun 27, 2026 · awaiting BSA Officer",
  },

  cwfcu_sar_rapid_movement: {
    key: 'cwfcu_sar_rapid_movement',
    name: "SAR-2026-0138-RAPID-MOVEMENT.txt",
    type: "SAR · FILED",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.doc,
    fileSize: '3.0 KB',
    agent: "Compliance Agent", time: "2.8s", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 2.8s`],
    fields: [
      { name: "SAR ID", value: "SAR-2026-0138", conf: 99 },
      { name: "Subject", value: "Member #38204 (Hartley)", conf: 99 },
      { name: "Pattern", value: "Rapid movement (funnel)", conf: 97 },
      { name: "Amount", value: "$18,500 / 12 wires", conf: 99 },
      { name: "Status", value: "FILED Jun 1, 2026", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "22-day in/out wire cycling · $350 net retained" },
      { color: "green", text: "Filed within 30-day window · FinCEN ack received" }
    ],
    routing: "→ Compliance Agent · case closed · NCUA folder indexed",
  },

  cwfcu_sar_layering: {
    key: 'cwfcu_sar_layering',
    name: "SAR-2026-0142-LAYERING.txt",
    type: "SAR · DRAFT",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.doc,
    fileSize: '3.1 KB',
    agent: "Compliance Agent", time: "2.9s", confidence: 95,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 2.9s`],
    fields: [
      { name: "SAR ID", value: "SAR-2026-0141", conf: 99 },
      { name: "Subject", value: "Member #51887 (Berg)", conf: 99 },
      { name: "Pattern", value: "Layering (P2P cycling)", conf: 95 },
      { name: "Amount", value: "$31,200 / 22 txns", conf: 99 },
      { name: "Status", value: "Pending BSA Officer", conf: 99 }
    ],
    flags: [
      { color: "red", text: "22 transactions through 4 prepaid card providers + 7 unrelated peers" },
      { color: "amber", text: "Pattern confidence 94.7%" }
    ],
    routing: "→ Compliance Agent · narrative drafted · SAR deadline Jun 29, 2026",
  },

  cwfcu_ctr_cash: {
    key: 'cwfcu_ctr_cash',
    name: "CTR-2026-05-1187-CASH-DEPOSIT.txt",
    type: "CTR · FILED",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '3.2 KB',
    agent: "Compliance Agent", time: "40s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 40s`],
    fields: [
      { name: "CTR ID", value: "CTR-2026-05-1187", conf: 99 },
      { name: "Member", value: "#29341 (Chen)", conf: 99 },
      { name: "Amount", value: "$12,400", conf: 99 },
      { name: "Type", value: "Cash deposit", conf: 99 },
      { name: "Filing latency", value: "18 hrs 26 min", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Auto-drafted in 40 seconds · BSA Officer approved" },
      { color: "green", text: "Filed well within 15-day FinCEN window" }
    ],
    routing: "→ Compliance Agent · FinCEN ack received · indexed to BSA folder",
  },

  cwfcu_ctr_wire: {
    key: 'cwfcu_ctr_wire',
    name: "CTR-2026-05-1188-WIRE.txt",
    type: "CTR · FILED",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '2.8 KB',
    agent: "Compliance Agent", time: "34s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 34s`],
    fields: [
      { name: "CTR ID", value: "CTR-2026-05-1188", conf: 99 },
      { name: "Member", value: "#08812 (Hartley)", conf: 99 },
      { name: "Amount", value: "$15,000", conf: 99 },
      { name: "Type", value: "Inbound wire", conf: 99 },
      { name: "Filing latency", value: "19 hrs 14 min", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "Wire correlated with SAR-2026-0138 rapid movement pattern" },
      { color: "green", text: "Filed within 15-day window" }
    ],
    routing: "→ Compliance Agent · linked to SAR-0138 case",
  },

  cwfcu_cdd_04421: {
    key: 'cwfcu_cdd_04421',
    name: "CDD-2026-Q2-MEM-04421.txt",
    type: "EDD REVIEW",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.doc,
    fileSize: '3.8 KB',
    agent: "Compliance Agent", time: "4.1s", confidence: 94,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 4.1s`],
    fields: [
      { name: "Member", value: "#39104 (Mendoza)", conf: 99 },
      { name: "Risk tier", value: "HIGH (reaffirmed)", conf: 98 },
      { name: "Wire activity", value: "40 wires · $356K", conf: 97 },
      { name: "New supplier", value: "Mekong Textile (Vietnam)", conf: 94 },
      { name: "Next review", value: "2026-08-14", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "New Vietnamese supplier · 594(a) secondary watchlist · risk-accepted" },
      { color: "green", text: "Source-of-funds documentation verified · purchase orders on file" }
    ],
    routing: "→ Compliance Agent · CDD updated · cash threshold reduced to $3K",
  },

  cwfcu_cdd_08812: {
    key: 'cwfcu_cdd_08812',
    name: "CDD-2026-Q2-MEM-08812.txt",
    type: "CDD REVIEW",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.doc,
    fileSize: '2.8 KB',
    agent: "Compliance Agent", time: "3.8s", confidence: 93,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 3.8s`],
    fields: [
      { name: "Member", value: "#08812 (Hartley)", conf: 99 },
      { name: "Risk tier", value: "MEDIUM → HIGH", conf: 97 },
      { name: "Linked SAR", value: "SAR-2026-0138", conf: 99 },
      { name: "Next review", value: "2026-09-01", conf: 99 },
      { name: "Cash threshold", value: "$3,000 (was $5K)", conf: 99 }
    ],
    flags: [
      { color: "red", text: "Risk tier elevated based on rapid in/out wire pattern" },
      { color: "amber", text: "Member declined to update 2024 tax docs" }
    ],
    routing: "→ Compliance Agent · quarterly cycle · monitoring active",
  },

  cwfcu_loan_auto: {
    key: 'cwfcu_loan_auto',
    name: "LOAN-AUTO-2026-05-0381.txt",
    type: "LOAN · AUTO",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '4.0 KB',
    agent: "Loan Document Agent", time: "15h6m", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 15h6m`],
    fields: [
      { name: "Loan", value: "LN-2026-05-0381", conf: 99 },
      { name: "Member", value: "#29402 (Garcia, L.)", conf: 99 },
      { name: "Type", value: "Auto $28,400", conf: 99 },
      { name: "Decision", value: "APPROVED · funded", conf: 99 },
      { name: "Cycle time", value: "15 hrs 6 min", conf: 99 }
    ],
    flags: [
      { color: "green", text: "All 8 documents extracted at 98.3% packet confidence" },
      { color: "green", text: "Straight-through approval · FICO 762 · LTV 87.1%" }
    ],
    routing: "→ Loan Document Agent · funded · vendor State Farm linked (no new MSA needed)",
  },

  cwfcu_loan_heloc_johnson: {
    key: 'cwfcu_loan_heloc_johnson',
    name: "LOAN-HELOC-2026-05-0441-JOHNSON.txt",
    type: "LOAN · HELOC",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '4.6 KB',
    agent: "Loan Document Agent", time: "PENDING", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in PENDING`],
    fields: [
      { name: "Loan", value: "LN-2026-0441", conf: 99 },
      { name: "Member", value: "#51122 (Johnson, M.)", conf: 99 },
      { name: "Type", value: "HELOC $85,000", conf: 99 },
      { name: "Status", value: "HITL · Missing W-2 2024", conf: 97 },
      { name: "Packet", value: "94% complete", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "2024 W-2 missing · CWAnyWhere reminder cycle active" },
      { color: "green", text: "Appraisal scheduled with Heartland Valuation Jun 10" }
    ],
    routing: "→ Loan Document Agent · HITL queue · waiting member upload + appraisal",
  },

  cwfcu_loan_mortgage_patel: {
    key: 'cwfcu_loan_mortgage_patel',
    name: "LOAN-MORTGAGE-2026-05-0438-PATEL.txt",
    type: "LOAN · MORTGAGE",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '5.1 KB',
    agent: "Loan Document Agent", time: "6d6h", confidence: 94,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 6d6h`],
    fields: [
      { name: "Loan", value: "LN-2026-0438", conf: 99 },
      { name: "Member", value: "#62411 (Patel, A.)", conf: 99 },
      { name: "Type", value: "Mortgage $215,000", conf: 99 },
      { name: "Decision", value: "APPROVED · closed · funded", conf: 99 },
      { name: "HMDA", value: "LAR Code 1", conf: 99 }
    ],
    flags: [
      { color: "green", text: "All 32 documents extracted at 94.1% packet confidence" },
      { color: "green", text: "ATR/QM Compliant · 8 ATR factors verified" },
      { color: "green", text: "HMDA reportable · LAR Code 1 (Conv. 30yr · approved)" }
    ],
    routing: "→ Loan Document Agent · funded Jun 4 · HMDA Q2 batch · indexed to credit risk folder",
  },

  cwfcu_loan_personal_williams: {
    key: 'cwfcu_loan_personal_williams',
    name: "LOAN-PERSONAL-2026-05-0517-WILLIAMS.txt",
    type: "LOAN · PERSONAL",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '3.9 KB',
    agent: "Loan Document Agent", time: "PENDING", confidence: 93,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in PENDING`],
    fields: [
      { name: "Loan", value: "LN-2026-0517", conf: 99 },
      { name: "Member", value: "#38914 (Williams, D.)", conf: 99 },
      { name: "Type", value: "Personal $12,500", conf: 99 },
      { name: "Status", value: "IN PROGRESS · 62% complete", conf: 97 },
      { name: "Income", value: "Self-employed (Schedule C)", conf: 95 }
    ],
    flags: [
      { color: "amber", text: "2025 tax return missing · CWAnyWhere notification sent" },
      { color: "green", text: "Cross-validated 2024 Schedule C against bank deposits 100%" }
    ],
    routing: "→ Loan Document Agent · HITL queue · awaiting tax doc upload",
  },

  cwfcu_paystub_nguyen: {
    key: 'cwfcu_paystub_nguyen',
    name: "PAYSTUB-2026-05-NGUYEN.txt",
    type: "INCOME · SE",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '2.5 KB',
    agent: "Loan Document Agent", time: "2.1s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 2.1s`],
    fields: [
      { name: "Member", value: "#29402 (Nguyen, T.)", conf: 99 },
      { name: "Source", value: "Self-employment / 1099", conf: 99 },
      { name: "Net SE income", value: "$10,402 (May)", conf: 99 },
      { name: "YTD", value: "$52,110", conf: 99 },
      { name: "Bank linked", value: "100% match", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Income deposits 100% matched to bank statements" },
      { color: "green", text: "+6.4% YoY · consistent with stated business growth" }
    ],
    routing: "→ Loan Document Agent · income verification source for future apps",
  },

  cwfcu_contract_fiserv: {
    key: 'cwfcu_contract_fiserv',
    name: "CONTRACT-FISERV-CORE-2024.txt",
    type: "CONTRACT · CORE",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.chart,
    fileSize: '4.2 KB',
    agent: "Vendor & Contract Agent", time: "4.2s", confidence: 97,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 4.2s`],
    fields: [
      { name: "Vendor", value: "Fiserv Solutions LLC", conf: 99 },
      { name: "Annual", value: "$2,100,000", conf: 99 },
      { name: "Renewal", value: "TODAY (Jun 4)", conf: 99 },
      { name: "Rate drift", value: "+5.8% over +3% cap", conf: 97 },
      { name: "Tier", value: "CRITICAL (Tier 1)", conf: 99 }
    ],
    flags: [
      { color: "red", text: "Auto-renewal deadline TODAY · 30-day notice required" },
      { color: "red", text: "Rate drift +2.8 pts over contract cap · $58K/yr exposure" },
      { color: "green", text: "SLA performance 100% Q2 · zero breaches" }
    ],
    routing: "→ Vendor & Contract Agent · escalate to CEO · negotiated rate cap proposed",
  },

  cwfcu_contract_eltropy: {
    key: 'cwfcu_contract_eltropy',
    name: "CONTRACT-ELTROPY-CDUBS-2025.txt",
    type: "CONTRACT · MX",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '3.1 KB',
    agent: "Vendor & Contract Agent", time: "3.7s", confidence: 95,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 3.7s`],
    fields: [
      { name: "Vendor", value: "Eltropy Inc.", conf: 99 },
      { name: "Annual", value: "$180,000", conf: 99 },
      { name: "Renewal", value: "Jul 15 (41 days)", conf: 99 },
      { name: "Rate drift", value: "+4.2% over +3% cap", conf: 96 },
      { name: "Tier", value: "HIGH (Tier 2)", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "Rate drift +1.2 pts over cap · $7.5K/yr exposure" },
      { color: "amber", text: "Data residency board attestation pending Jun 17 meeting" },
      { color: "green", text: "SLA: 99.94% uptime · 1 minor breach with credit applied" }
    ],
    routing: "→ Vendor & Contract Agent · negotiation open · data clause action queued",
  },

  cwfcu_contract_coop: {
    key: 'cwfcu_contract_coop',
    name: "CONTRACT-COOP-SHARED-BRANCH-2023.txt",
    type: "CONTRACT · NETWORK",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '2.6 KB',
    agent: "Vendor & Contract Agent", time: "3.4s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 3.4s`],
    fields: [
      { name: "Vendor", value: "CO-OP Financial Services", conf: 99 },
      { name: "Annual", value: "$432,000", conf: 99 },
      { name: "Status", value: "Auto-renewed (1yr)", conf: 99 },
      { name: "Rate drift", value: "+2.2% (within cap)", conf: 98 },
      { name: "Tier", value: "HIGH (Tier 2)", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Within contract escalation cap" },
      { color: "amber", text: "Q2 2026: 1 P1 incident (2-hr regional outage) · credit applied" },
      { color: "green", text: "PCI-DSS + Network Sec attestations current" }
    ],
    routing: "→ Vendor & Contract Agent · standard renewal · TPRM refresh Q4",
  },

  cwfcu_contract_diebold: {
    key: 'cwfcu_contract_diebold',
    name: "CONTRACT-DIEBOLD-ATM-2024.txt",
    type: "CONTRACT · ATM",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '2.9 KB',
    agent: "Vendor & Contract Agent", time: "3.6s", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 3.6s`],
    fields: [
      { name: "Vendor", value: "Diebold Nixdorf Inc.", conf: 99 },
      { name: "Annual", value: "$353,000", conf: 99 },
      { name: "Coverage", value: "12 ATMs", conf: 99 },
      { name: "Renewal", value: "Sep 15, 2027 (rebid req)", conf: 99 },
      { name: "Tier", value: "HIGH (Tier 2)", conf: 99 }
    ],
    flags: [
      { color: "green", text: "ATM uptime 99.96% · zero P1 incidents" },
      { color: "amber", text: "2 of 14 cassette custodians overdue on P-OPS-227 ack" },
      { color: "green", text: "Cash insurance + dual-control documented" }
    ],
    routing: "→ Vendor & Contract Agent · cassette training ack tracked by Policy & HR",
  },

  cwfcu_policy_bsa_roster: {
    key: 'cwfcu_policy_bsa_roster',
    name: "POLICY-ACK-BSA-2026-Q2-ROSTER.txt",
    type: "POLICY · ACK",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.doc,
    fileSize: '4.1 KB',
    agent: "Policy & HR Agent", time: "5.4s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 5.4s`],
    fields: [
      { name: "Policy", value: "P-COMP-201 BSA/AML 2026", conf: 99 },
      { name: "Completion", value: "62 of 84 (74%)", conf: 99 },
      { name: "Outstanding", value: "22 employees", conf: 99 },
      { name: "Branch tellers overdue", value: "18 of 22", conf: 99 },
      { name: "NCUA exam impact", value: "+9 pts when complete", conf: 99 }
    ],
    flags: [
      { color: "red", text: "22 of 84 employees overdue on BSA/AML training" },
      { color: "red", text: "18 are branch tellers — highest-risk role" },
      { color: "amber", text: "Reminder cycle 3 of 4 sent · escalation Jun 10" }
    ],
    routing: "→ Policy & HR Agent · escalation queue · final reminder Jun 17",
  },

  cwfcu_board_res_vendor_mgmt: {
    key: 'cwfcu_board_res_vendor_mgmt',
    name: "BOARD-RESOLUTION-2026-04-VENDOR-MGMT.txt",
    type: "BOARD RES",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '4.4 KB',
    agent: "Policy & HR Agent", time: "3.2s", confidence: 97,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to NCUA folder', `Done in 3.2s`],
    fields: [
      { name: "Resolution", value: "BOARD-RES-2026-04", conf: 99 },
      { name: "Topic", value: "Vendor Mgmt Policy 2026", conf: 99 },
      { name: "Signatures", value: "5 of 7 received", conf: 99 },
      { name: "Effective", value: "May 1, 2026", conf: 99 },
      { name: "Target completion", value: "Jun 17 board meeting", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "2 of 7 board signatures pending (Patel, Whitmore)" },
      { color: "green", text: "Resolution ratifies APEX SAR/CTR/CDD workflow (per § 5)" },
      { color: "green", text: "Closes 2 NCUA attention items (vendor mgmt + board attestation)" }
    ],
    routing: "→ Policy & HR Agent · awaiting Jun 17 meeting · NCUA exam blocker",
  },

  /* ─── BOLER · The Boler Company — 14 sample files ─── */
  boler_cigna_medical: {
    key: 'boler_cigna_medical',
    name: "Cigna_Medical_Jun2026.txt",
    type: "CARRIER · MEDICAL",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.doc,
    fileSize: '2.9 KB',
    agent: "Benefits Allocation Agent", time: "4.2s", confidence: 97,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 4.2s`],
    fields: [
      { name: "Carrier", value: "Cigna Healthcare", conf: 99 },
      { name: "Total premium", value: "$1,284,320", conf: 99 },
      { name: "Lives", value: "847 employees", conf: 99 },
      { name: "Drift", value: "+4.1% over contract", conf: 96 },
      { name: "Period", value: "June 2026", conf: 99 }
    ],
    flags: [
      { color: "red", text: "Rate drift +4.1% above contracted rate · renewal in 41d" },
      { color: "red", text: "Includes Chen, R. coded to wrong division (EXC-0441)" },
      { color: "red", text: "Includes Martinez, L. duplicate enrollment (EXC-0442)" }
    ],
    routing: "→ Benefits Allocation Agent · ingested + cross-referenced with HRIS · 2 HIGH exceptions surfaced",
  },

  boler_delta_dental: {
    key: 'boler_delta_dental',
    name: "Delta_Dental_Jun2026.txt",
    type: "CARRIER · DENTAL",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '1.9 KB',
    agent: "Benefits Allocation Agent", time: "3.4s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.4s`],
    fields: [
      { name: "Carrier", value: "Delta Dental of Illinois", conf: 99 },
      { name: "Total premium", value: "$187,450", conf: 99 },
      { name: "Lives", value: "831 employees", conf: 99 },
      { name: "Drift", value: "+1.8% over contract", conf: 97 },
      { name: "Period", value: "June 2026", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Within tolerance band (+3% cap) · no Signal alert" },
      { color: "green", text: "16 waivers auto-credited at intake" }
    ],
    routing: "→ Benefits Allocation Agent · ingested clean · routed to JE Agent",
  },

  boler_fidelity_401k: {
    key: 'boler_fidelity_401k',
    name: "Fidelity_401k_Jun2026.txt",
    type: "CARRIER · 401K",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.doc,
    fileSize: '2.6 KB',
    agent: "Benefits Allocation Agent", time: "3.8s", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.8s`],
    fields: [
      { name: "Carrier", value: "Fidelity Workplace", conf: 99 },
      { name: "Total match", value: "$412,880", conf: 99 },
      { name: "Active participants", value: "803", conf: 99 },
      { name: "Match rate (file)", value: "4.5% ⚠", conf: 97 },
      { name: "HR policy match rate", value: "4.0%", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "Match rate mismatch: Fidelity 4.5% vs HR policy 4.0% · $8,240/mo delta" },
      { color: "amber", text: "Flagged as EXC-2026-0445 · Awaiting Benefits Director" },
      { color: "green", text: "Vesting breakdown: 76% fully vested · 18% partial · 6% cliff" }
    ],
    routing: "→ Benefits Allocation Agent · flagged 1 MEDIUM exception · routed to Sarah Mitchell",
  },

  boler_vsp_vision: {
    key: 'boler_vsp_vision',
    name: "VSP_Vision_Jun2026.txt",
    type: "CARRIER · VISION",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '1.7 KB',
    agent: "Benefits Allocation Agent", time: "2.9s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 2.9s`],
    fields: [
      { name: "Carrier", value: "VSP Vision Care", conf: 99 },
      { name: "Total premium", value: "$62,140", conf: 99 },
      { name: "Lives", value: "798 employees", conf: 99 },
      { name: "Drift", value: "+0.2% over contract", conf: 99 },
      { name: "Period", value: "June 2026", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Well within tolerance · no Signal alert" },
      { color: "green", text: "49 waivers credited at intake" },
      { color: "amber", text: "Thompson, D. terminated 5/28 still billed → auto-fixed (EXC-0446)" }
    ],
    routing: "→ Benefits Allocation Agent · ingested clean · routed to JE Agent",
  },

  boler_hartford_life: {
    key: 'boler_hartford_life',
    name: "Hartford_Life_Jun2026.txt",
    type: "CARRIER · LIFE",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '1.9 KB',
    agent: "Benefits Allocation Agent", time: "3.1s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.1s`],
    fields: [
      { name: "Carrier", value: "Hartford Life", conf: 99 },
      { name: "Total premium", value: "$98,760", conf: 99 },
      { name: "Lives", value: "847 (all employees)", conf: 99 },
      { name: "Drift", value: "+0.4% over contract", conf: 98 },
      { name: "Period", value: "June 2026", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Within tolerance · no Signal alert" },
      { color: "green", text: "Basic life is employer-paid · voluntary tiers payroll-deducted" }
    ],
    routing: "→ Benefits Allocation Agent · ingested clean · routed to JE Agent",
  },

  boler_cigna_std_ltd: {
    key: 'boler_cigna_std_ltd',
    name: "Cigna_STD_LTD_Jun2026.txt",
    type: "CARRIER · DISABILITY",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.doc,
    fileSize: '1.6 KB',
    agent: "Benefits Allocation Agent", time: "3.0s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.0s`],
    fields: [
      { name: "Carrier", value: "Cigna Disability Group", conf: 99 },
      { name: "Total premium", value: "$94,450", conf: 99 },
      { name: "STD coverage", value: "100% (847)", conf: 99 },
      { name: "LTD coverage", value: "78% (661)", conf: 99 },
      { name: "Drift", value: "+0.6%", conf: 98 }
    ],
    flags: [
      { color: "green", text: "Within tolerance · no Signal alert" }
    ],
    routing: "→ Benefits Allocation Agent · ingested clean · routed to JE Agent",
  },

  boler_exc_chen: {
    key: 'boler_exc_chen',
    name: "EXC-2026-0441-CHEN-WRONG-DIVISION.txt",
    type: "EXCEPTION · HIGH",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.chart,
    fileSize: '3.8 KB',
    agent: "Exception Resolution Agent", time: "4.7s", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 4.7s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0441", conf: 99 },
      { name: "Subject", value: "Chen, Robert (EMP-4821)", conf: 99 },
      { name: "Type", value: "Wrong division reclass", conf: 98 },
      { name: "Variance", value: "$3,840/mo · $46,080/yr", conf: 99 },
      { name: "Status", value: "Awaiting CFO", conf: 99 }
    ],
    flags: [
      { color: "red", text: "Detected via HRIS cross-reference · 6 benefit lines incorrectly allocated" },
      { color: "amber", text: "Stage 1 approved (Sarah Mitchell) · Stage 2 CFO pending" },
      { color: "green", text: "Recommended action: reclassify to Boler Holdings 6200-004 effective 5/15" }
    ],
    routing: "→ Exception Resolution Agent · CFO HITL queue · 6 hrs to SLA",
  },

  boler_exc_martinez: {
    key: 'boler_exc_martinez',
    name: "EXC-2026-0442-MARTINEZ-DUPLICATE.txt",
    type: "EXCEPTION · HIGH",
    chipCls: 'chip-red',
    iconBg: '#fee2e2', iconColor: '#dc2626', iconPath: ICONS.chart,
    fileSize: '3.8 KB',
    agent: "Exception Resolution Agent", time: "4.4s", confidence: 98,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 4.4s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0442", conf: 99 },
      { name: "Subject", value: "Martinez, L. (EMP-3312)", conf: 99 },
      { name: "Type", value: "Duplicate enrollment", conf: 98 },
      { name: "Variance", value: "$1,240/mo + $5,580 catch-up", conf: 99 },
      { name: "Status", value: "Awaiting CFO", conf: 99 }
    ],
    flags: [
      { color: "red", text: "Terminated 4/30 but Cigna medical file still active" },
      { color: "red", text: "COBRA self-pay should not be in corporate allocation" },
      { color: "green", text: "Recommended: REMOVE from Boler Holdings + Cigna term feed fix" }
    ],
    routing: "→ Exception Resolution Agent · CFO HITL queue · 6 hrs to SLA",
  },

  boler_exc_cigna_drift: {
    key: 'boler_exc_cigna_drift',
    name: "EXC-2026-0443-CIGNA-RATE-DRIFT.txt",
    type: "EXCEPTION · MEDIUM",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '2.3 KB',
    agent: "Signal Agent", time: "3.7s", confidence: 94,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.7s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0443", conf: 99 },
      { name: "Type", value: "Carrier rate drift", conf: 96 },
      { name: "Drift", value: "+4.1% over contract", conf: 97 },
      { name: "Cycle variance", value: "$50,557", conf: 99 },
      { name: "Annual exposure", value: "$606,684", conf: 97 }
    ],
    flags: [
      { color: "red", text: "Renewal in 41 days · no negotiation initiated" },
      { color: "amber", text: "BCBS alternate quote in hand at +2.4% → saves $230K/yr" },
      { color: "green", text: "Recommend: renegotiate before Jul 1 auto-renewal" }
    ],
    routing: "→ Signal Agent · routed to Sarah Mitchell + CFO · Stage 1 pending",
  },

  boler_exc_transfers: {
    key: 'boler_exc_transfers',
    name: "EXC-2026-0444-DIVISION-TRANSFER.txt",
    type: "EXCEPTION · AUTO-FIXED",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '2.5 KB',
    agent: "Benefits Allocation Agent", time: "2.8s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 2.8s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0444", conf: 99 },
      { name: "Type", value: "Division transfers · 4 employees", conf: 97 },
      { name: "Variance auto-fixed", value: "$14,320/mo", conf: 99 },
      { name: "Action", value: "Auto-applied · no human touch", conf: 99 },
      { name: "Status", value: "AUTO-FIXED", conf: 99 }
    ],
    flags: [
      { color: "green", text: "3 of 4 transfers under $5K auto-fix threshold" },
      { color: "green", text: "Kim, Foster, Reilly all auto-reclassified per HRIS source-of-truth" },
      { color: "amber", text: "Chen escalated separately as EXC-0441 HIGH (over $5K)" }
    ],
    routing: "→ Benefits Allocation Agent · auto-fixed · DynamoDB logged · no HITL required",
  },

  boler_exc_401k: {
    key: 'boler_exc_401k',
    name: "EXC-2026-0445-401K-MISMATCH.txt",
    type: "EXCEPTION · MEDIUM",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '2.7 KB',
    agent: "Benefits Allocation Agent", time: "4.1s", confidence: 96,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 4.1s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0445", conf: 99 },
      { name: "Type", value: "401k match rate mismatch", conf: 97 },
      { name: "Fidelity rate (file)", value: "4.5%", conf: 99 },
      { name: "HR policy rate", value: "4.0%", conf: 99 },
      { name: "Monthly delta", value: "$8,240", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "0.5% mismatch · $98,880/yr financial exposure" },
      { color: "amber", text: "Plan document last amended Apr 2024 (no 4.5% authority on file)" },
      { color: "green", text: "Sarah Mitchell follow-up requested · 7d SLA" }
    ],
    routing: "→ Benefits Allocation Agent · routed to Sarah Mitchell · Stage 1 pending",
  },

  boler_exc_thompson: {
    key: 'boler_exc_thompson',
    name: "EXC-2026-0446-THOMPSON-TERMINATED.txt",
    type: "EXCEPTION · AUTO-FIXED",
    chipCls: 'chip-green',
    iconBg: '#dcfce7', iconColor: '#16a34a', iconPath: ICONS.chart,
    fileSize: '1.8 KB',
    agent: "Benefits Allocation Agent", time: "2.4s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 2.4s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0446", conf: 99 },
      { name: "Subject", value: "Thompson, D.", conf: 99 },
      { name: "Type", value: "Terminated still active", conf: 99 },
      { name: "Variance auto-fixed", value: "$420/mo (VSP + Delta)", conf: 99 },
      { name: "Status", value: "AUTO-FIXED", conf: 99 }
    ],
    flags: [
      { color: "green", text: "Auto-fix threshold met · termination cascade applied" },
      { color: "green", text: "Catch-up $420 credit to Boler Mfg Services June JE" }
    ],
    routing: "→ Benefits Allocation Agent · auto-fixed · DynamoDB logged",
  },

  boler_exc_new_hires: {
    key: 'boler_exc_new_hires',
    name: "EXC-2026-0447-NEW-HIRES-NO-CC.txt",
    type: "EXCEPTION · LOW",
    chipCls: 'chip-amber',
    iconBg: '#fef3c7', iconColor: '#d97706', iconPath: ICONS.chart,
    fileSize: '2.0 KB',
    agent: "Benefits Allocation Agent", time: "3.0s", confidence: 95,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.0s`],
    fields: [
      { name: "Exception", value: "EXC-2026-0447", conf: 99 },
      { name: "Type", value: "Missing cost-center · 3 new hires", conf: 97 },
      { name: "Unallocated", value: "$6,840/mo", conf: 99 },
      { name: "Affected", value: "Stanford · Okafor · Lambert", conf: 99 },
      { name: "Status", value: "Awaiting Sarah Mitchell", conf: 99 }
    ],
    flags: [
      { color: "amber", text: "New-hire intake lags carrier enrollment by 5-10 days" },
      { color: "green", text: "Recommend: confirm division assignments with hiring managers + back-allocate" }
    ],
    routing: "→ Benefits Allocation Agent · Stage 1 review pending",
  },

  boler_je_hendrickson: {
    key: 'boler_je_hendrickson',
    name: "JE-2026-06-HENDRICKSON.txt",
    type: "JOURNAL ENTRY",
    chipCls: 'chip-blue',
    iconBg: '#dbeafe', iconColor: '#0f4c81', iconPath: ICONS.chart,
    fileSize: '3.3 KB',
    agent: "Journal Entry Agent", time: "3.4s", confidence: 99,
    subLabels: ['Doc ingested', 'Fields extracted', 'Decision logged', 'Indexed to DynamoDB audit log', `Done in 3.4s`],
    fields: [
      { name: "JE ID", value: "JE-2026-0031", conf: 99 },
      { name: "Division", value: "Hendrickson International", conf: 99 },
      { name: "Total DR/CR", value: "$1,042,800", conf: 99 },
      { name: "Balance", value: "$0 ✓ Balanced", conf: 99 },
      { name: "Status", value: "Awaiting CFO", conf: 99 }
    ],
    flags: [
      { color: "green", text: "DR = CR balance check passed at penny precision" },
      { color: "amber", text: "Stage 2 CFO sign-off pending · 6h to SLA" },
      { color: "green", text: "Auto-distribution to Lisa Tanaka (Hend Controller) on Jun 7" }
    ],
    routing: "→ Journal Entry Agent · approved Stage 1 (Sarah Mitchell) · S3 distribution scheduled",
  },

  /* ─── BOLER · 5 complex Excel workbooks (Argos · live demo) ─── */
  boler_xlsx_cigna_roster: {
    key: 'boler_xlsx_cigna_roster',
    name: "Cigna_Medical_Roster_Jun2026.xlsx",
    type: "EXCEL · CARRIER ROSTER",
    chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.chart,
    fileSize: '66 KB',
    agent: "Benefits Allocation Agent", time: "5.8s", confidence: 98,
    subLabels: ['Workbook ingested', '847 rows extracted', 'Plan-tier × division pivoted', 'Drift analysis flagged', `Done in 5.8s`],
    fields: [
      { name: "Sheets", value: "Roster · Summary · Drift Analysis", conf: 99 },
      { name: "Covered Lives", value: "847 employees", conf: 99 },
      { name: "Total Premium", value: "$1,284,320.00", conf: 99 },
      { name: "Plan Tiers", value: "Premium · Standard · HDHP · Basic", conf: 99 },
      { name: "Drift Detected", value: "356 HTS lives · +$47,640 annualized", conf: 96 },
    ],
    flags: [
      { color: "red", text: "Hendrickson Truck Suspension lives billed +$28–$68 above plan-doc rate (rows 6–410)" },
      { color: "red", text: "EXC-2026-0443 — Cigna carrier drift CRITICAL · $47,640 annual exposure" },
      { color: "amber", text: "Renewal in 41 days — open renegotiation window now" }
    ],
    routing: "→ Benefits Allocation Agent · drift quantified per plan tier · routed to CFO Ziggy Kravitz for renewal posture",
  },

  boler_xlsx_hris_master: {
    key: 'boler_xlsx_hris_master',
    name: "Boler_HRIS_Master_Roster.xlsx",
    type: "EXCEL · HRIS EXPORT",
    chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.chart,
    fileSize: '217 KB',
    agent: "Benefits Allocation Agent", time: "7.1s", confidence: 99,
    subLabels: ['Workday export ingested', '2,847 employees extracted', 'Division × plan election pivoted', '4 transfers detected', `Done in 7.1s`],
    fields: [
      { name: "Sheets", value: "All Employees · By Division · Transfers", conf: 99 },
      { name: "Active Employees", value: "2,847 across 5 divisions", conf: 99 },
      { name: "Internal Transfers (May)", value: "4 · all auto-reclassified", conf: 99 },
      { name: "Terminated (still on May)", value: "Thompson, Greg (EE-101204)", conf: 98 },
      { name: "Source", value: "Workday · effective 2026-06-01", conf: 99 },
    ],
    flags: [
      { color: "green", text: "EXC-2026-0444 auto-resolved — 4 mid-month transfers pro-rated correctly" },
      { color: "amber", text: "EXC-2026-0446 — Thompson terminated 5/22 but still on June Cigna roster" },
      { color: "green", text: "HTS continues to be the largest division at 1,094 lives (38.4%)" }
    ],
    routing: "→ Benefits Allocation Agent · system-of-record for division pro-rating · 99.7% match rate vs carrier roster",
  },

  boler_xlsx_division_allocation: {
    key: 'boler_xlsx_division_allocation',
    name: "Division_Allocation_Jun2026.xlsx",
    type: "EXCEL · ALLOCATION PIVOT",
    chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.chart,
    fileSize: '7 KB',
    agent: "Benefits Allocation Agent", time: "3.9s", confidence: 99,
    subLabels: ['Workbook ingested', '5×6 matrix balanced', 'Variance vs FY budget computed', 'CFO callout staged', `Done in 3.9s`],
    fields: [
      { name: "Sheets", value: "Allocation Matrix · Variance", conf: 99 },
      { name: "Divisions × Carriers", value: "5 × 6 = 30 cells", conf: 99 },
      { name: "Grand Total", value: "$1,284,320.00 — reconciled", conf: 99 },
      { name: "Material Variance Flag", value: "HTS +$24,080 MoM (CFO REVIEW)", conf: 97 },
      { name: "FY Budget Status", value: "4/5 divisions on track · HTS over by 4.4%", conf: 96 },
    ],
    flags: [
      { color: "red", text: "Hendrickson Truck Suspension flagged for CFO review · YTD variance breaches $50K threshold" },
      { color: "amber", text: "Boler Hitch variance $2,414 MoM — Benefits Mgr review (Sarah Mitchell)" },
      { color: "green", text: "Cequent · ROHO · Henderson all balanced within tolerance" }
    ],
    routing: "→ Benefits Allocation Agent · pivot reconciled · CFO callout drafted for Ziggy Kravitz review",
  },

  boler_xlsx_exception_register: {
    key: 'boler_xlsx_exception_register',
    name: "Exception_Register_Jun2026.xlsx",
    type: "EXCEL · EXCEPTIONS REGISTER",
    chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.chart,
    fileSize: '7 KB',
    agent: "Exceptions & Reconciliation Agent", time: "4.6s", confidence: 96,
    subLabels: ['Workbook ingested', '7 exceptions classified', '4 auto-fixed', '3 routed to HITL', `Done in 4.6s`],
    fields: [
      { name: "Sheets", value: "Exception Register · Summary", conf: 99 },
      { name: "Total Exceptions", value: "7 · severity range LOW→CRITICAL", conf: 99 },
      { name: "Auto-Fixed by APEX", value: "4 (transfers, term, new-hire CC)", conf: 99 },
      { name: "HITL — Benefits Mgr", value: "3 (Sarah Mitchell)", conf: 99 },
      { name: "HITL — CFO", value: "1 (Ziggy Kravitz · CRITICAL drift)", conf: 99 },
    ],
    flags: [
      { color: "red", text: "EXC-2026-0443 CRITICAL · Cigna portfolio drift · $47,640 annualized · CFO routing" },
      { color: "red", text: "EXC-2026-0445 HIGH · 401k employer match 4.5% vs plan-doc 4.0% · $11,420 variance" },
      { color: "green", text: "Time-to-auto-fix avg 4.2 min · time-to-HITL-resolution avg 2.8 hours" }
    ],
    routing: "→ Exceptions Agent · all 7 classified · auto-fix log committed · HITL queue staged for Sarah + Ziggy",
  },

  boler_xlsx_consolidated_je: {
    key: 'boler_xlsx_consolidated_je',
    name: "Boler_Consolidated_JE_Jun2026.xlsx",
    type: "EXCEL · JOURNAL ENTRY",
    chipCls: 'chip-purple',
    iconBg: '#f4f1ff', iconColor: '#6c47ff', iconPath: ICONS.chart,
    fileSize: '13 KB',
    agent: "Journal Entry Agent", time: "4.3s", confidence: 99,
    subLabels: ['Workbook ingested', '35 GL lines extracted', 'Debits = Credits balance verified', '5 division splits distributed', `Done in 4.3s`],
    fields: [
      { name: "Sheets", value: "Consolidated JE + 5 division JEs (HTS · BLH · CEQ · RHO · HEN)", conf: 99 },
      { name: "Total Debits", value: "$1,284,320.00", conf: 99 },
      { name: "Total Credits", value: "$1,284,320.00 — ✓ BALANCED", conf: 99 },
      { name: "Approval Chain", value: "Sarah Mitchell ✓ → Ziggy Kravitz ✓", conf: 99 },
      { name: "Distribution Status", value: "5/5 division packets delivered to S3 + SNS acked", conf: 99 },
    ],
    flags: [
      { color: "green", text: "Penny-precise balance check passed · debits = credits across all 35 lines" },
      { color: "green", text: "Two-stage approval complete · audit chain hash-linked in DynamoDB" },
      { color: "green", text: "Per-division packets encrypted with alias/boler-{hts,blh,ceq,rho,hen} KMS keys" }
    ],
    routing: "→ Journal Entry Agent · consolidated JE balanced + approved + distributed to 5 division S3 inboxes",
  },

};

// STP samples first when in stp mode (filter-aware ordering); CBB next; generic last.
const SAMPLE_ORDER: SampleKey[] = [
  'stp_policy', 'stp_pm_history', 'stp_issue_analysis', 'stp_predictive',
  // Verizon Far Edge — 12 REAL firmware reports (featured at top for live demo) + 4 synthetic
  // CAS current-gen onboarding docs first (featured for the orchestration demo)
  'vz_cas_el140', 'vz_cas_playbook_spec', 'vz_cas_xr8720', 'vz_cas_thermal', 'vz_cas_wrcp',
  'vz_dmtf_e930t', 'vz_samsung_ssd', 'vz_bmc_upgrade', 'vz_ptu_perf',
  'vz_sensor_proteus', 'vz_bios_triton', 'vz_redfish_proteus', 'vz_platform_deploy',
  'vz_soak_galene', 'vz_dell_sensor', 'vz_troubleshoot', 'vz_flexran',
  'tel_robot_xml', 'tel_redfish_diff', 'tel_upgrade_runbook', 'tel_kb_article',
  'ae_inventory_alert', 'ae_lease_pdf',
  // EPROD · Oil & Gas — Midstream (15 samples)
  'eprod_inv_hal', 'eprod_inv_slb', 'eprod_inv_bhi', 'eprod_inv_kiewit',
  'eprod_po_epc', 'eprod_po_chem', 'eprod_po_ops',
  'eprod_msa_hal', 'eprod_msa_kiewit',
  'eprod_quote_fluor', 'eprod_quote_bechtel',
  'eprod_tariff_ngl', 'eprod_tariff_crude',
  'eprod_jib_p66', 'eprod_jib_targa',
  'cwfcu_cip_rosales', 'cwfcu_cip_nguyen', 'cwfcu_cip_arrington', 'cwfcu_cip_okafor', 'cwfcu_sar_structuring', 'cwfcu_sar_rapid_movement', 'cwfcu_sar_layering', 'cwfcu_ctr_cash', 'cwfcu_ctr_wire', 'cwfcu_cdd_04421', 'cwfcu_cdd_08812', 'cwfcu_loan_auto', 'cwfcu_loan_heloc_johnson', 'cwfcu_loan_mortgage_patel', 'cwfcu_loan_personal_williams', 'cwfcu_paystub_nguyen', 'cwfcu_contract_fiserv', 'cwfcu_contract_eltropy', 'cwfcu_contract_coop', 'cwfcu_contract_diebold', 'cwfcu_policy_bsa_roster', 'cwfcu_board_res_vendor_mgmt',
  // BOLER · The Boler Company — 5 Excel workbooks (TOP — featured for live Argos/Apex Lens demo) + 14 text samples
  'boler_xlsx_cigna_roster', 'boler_xlsx_hris_master', 'boler_xlsx_division_allocation',
  'boler_xlsx_exception_register', 'boler_xlsx_consolidated_je',
  'boler_cigna_medical', 'boler_delta_dental', 'boler_fidelity_401k', 'boler_vsp_vision',
  'boler_hartford_life', 'boler_cigna_std_ltd',
  'boler_exc_chen', 'boler_exc_martinez', 'boler_exc_cigna_drift', 'boler_exc_transfers',
  'boler_exc_401k', 'boler_exc_thompson', 'boler_exc_new_hires',
  'boler_je_hendrickson',
  'order_mod', 'qc_batch', 'port_strike',
  'invoice', 'claim', 'po', 'qc', 'contract', 'alert',
];

/** Per-sample industry tag — drives the demoMode filter. */
const SAMPLE_INDUSTRY: Record<SampleKey, string> = {
  // CBB demo samples
  order_mod:   'supply_manufacturing',
  qc_batch:    'supply_manufacturing',
  port_strike: 'supply_manufacturing',
  // STP Phase 2
  stp_policy:         'nuclear_operations',
  stp_pm_history:     'nuclear_operations',
  stp_issue_analysis: 'nuclear_operations',
  stp_predictive:     'nuclear_operations',
  // Telecommunications · Verizon Far Edge POC
  tel_robot_xml:       'telecommunications',
  tel_redfish_diff:    'telecommunications',
  tel_upgrade_runbook: 'telecommunications',
  tel_kb_article:      'telecommunications',
  // Verizon Far Edge — 12 real firmware reports
  vz_dmtf_e930t:       'telecommunications',
  vz_samsung_ssd:      'telecommunications',
  vz_bmc_upgrade:      'telecommunications',
  vz_ptu_perf:         'telecommunications',
  vz_sensor_proteus:   'telecommunications',
  vz_bios_triton:      'telecommunications',
  vz_redfish_proteus:  'telecommunications',
  vz_platform_deploy:  'telecommunications',
  vz_soak_galene:      'telecommunications',
  vz_dell_sensor:      'telecommunications',
  vz_troubleshoot:     'telecommunications',
  vz_flexran:          'telecommunications',
  vz_cas_el140:        'telecommunications',
  vz_cas_xr8720:       'telecommunications',
  vz_cas_playbook_spec:'telecommunications',
  vz_cas_thermal:      'telecommunications',
  vz_cas_wrcp:         'telecommunications',
  // Agentic Enterprise — each sample tagged with its specific industry
  // domain so the umbrella `agentic_enterprise` mode shows both, but
  // selecting `supply_chain_orchestrator` shows only the inventory alert
  // and `commercial_real_estate` shows only the lease PDF.
  ae_inventory_alert: 'supply_chain_orchestrator',
  ae_lease_pdf:       'commercial_real_estate',
  // Generic samples — assign an industry so they're hidden in any specific demo
  invoice:     'financial_services',
  claim:       'insurance_underwriting',
  po:          'supply_manufacturing',
  qc:          'supply_manufacturing',
  contract:    'aerospace_defense',
  alert:       'supply_manufacturing',
  // EPROD · Oil & Gas — Midstream (15 samples)
  eprod_inv_hal:       'oil_gas_midstream',
  eprod_inv_slb:       'oil_gas_midstream',
  eprod_inv_bhi:       'oil_gas_midstream',
  eprod_inv_kiewit:    'oil_gas_midstream',
  eprod_po_epc:        'oil_gas_midstream',
  eprod_po_chem:       'oil_gas_midstream',
  eprod_po_ops:        'oil_gas_midstream',
  eprod_msa_hal:       'oil_gas_midstream',
  eprod_msa_kiewit:    'oil_gas_midstream',
  eprod_quote_fluor:   'oil_gas_midstream',
  eprod_quote_bechtel: 'oil_gas_midstream',
  eprod_tariff_ngl:    'oil_gas_midstream',
  eprod_tariff_crude:  'oil_gas_midstream',
  eprod_jib_p66:       'oil_gas_midstream',
  eprod_jib_targa:     'oil_gas_midstream',
  /* CWFCU · 22 credit union samples */
  cwfcu_cip_rosales:           'credit_union',
  cwfcu_cip_nguyen:           'credit_union',
  cwfcu_cip_arrington:           'credit_union',
  cwfcu_cip_okafor:           'credit_union',
  cwfcu_sar_structuring:           'credit_union',
  cwfcu_sar_rapid_movement:           'credit_union',
  cwfcu_sar_layering:           'credit_union',
  cwfcu_ctr_cash:           'credit_union',
  cwfcu_ctr_wire:           'credit_union',
  cwfcu_cdd_04421:           'credit_union',
  cwfcu_cdd_08812:           'credit_union',
  cwfcu_loan_auto:           'credit_union',
  cwfcu_loan_heloc_johnson:           'credit_union',
  cwfcu_loan_mortgage_patel:           'credit_union',
  cwfcu_loan_personal_williams:           'credit_union',
  cwfcu_paystub_nguyen:           'credit_union',
  cwfcu_contract_fiserv:           'credit_union',
  cwfcu_contract_eltropy:           'credit_union',
  cwfcu_contract_coop:           'credit_union',
  cwfcu_contract_diebold:           'credit_union',
  cwfcu_policy_bsa_roster:           'credit_union',
  cwfcu_board_res_vendor_mgmt:           'credit_union',
  /* BOLER · 14 sample files */
  boler_cigna_medical:           'manufacturing_multi_division',
  boler_delta_dental:           'manufacturing_multi_division',
  boler_fidelity_401k:           'manufacturing_multi_division',
  boler_vsp_vision:           'manufacturing_multi_division',
  boler_hartford_life:           'manufacturing_multi_division',
  boler_cigna_std_ltd:           'manufacturing_multi_division',
  boler_exc_chen:           'manufacturing_multi_division',
  boler_exc_martinez:           'manufacturing_multi_division',
  boler_exc_cigna_drift:           'manufacturing_multi_division',
  boler_exc_transfers:           'manufacturing_multi_division',
  boler_exc_401k:           'manufacturing_multi_division',
  boler_exc_thompson:           'manufacturing_multi_division',
  boler_exc_new_hires:           'manufacturing_multi_division',
  boler_je_hendrickson:           'manufacturing_multi_division',
  // BOLER · Excel workbooks
  boler_xlsx_cigna_roster:         'manufacturing_multi_division',
  boler_xlsx_hris_master:           'manufacturing_multi_division',
  boler_xlsx_division_allocation:   'manufacturing_multi_division',
  boler_xlsx_exception_register:    'manufacturing_multi_division',
  boler_xlsx_consolidated_je:       'manufacturing_multi_division',
};

/* ──────────────────────── file preview content ──────────────────────── */

/** Mock raw-content preview for each sample (formatted plain-text that renders
 *  in a monospace reader pane so users can actually *see* the file before
 *  deciding to run a pipeline on it). Each entry matches the fields below it. */
const RAW_CONTENT: Partial<Record<SampleKey, string>> = {
  order_mod: `ORDER MODIFICATION REQUEST
════════════════════════════════════════════════════

From:    orders@midwestwindow.com
Subject: Modification request · CBB-ORD-1044
Date:    April 21, 2026 · 09:12 ET

──────── Original Order ────────
Order ID:          CBB-ORD-1044
Distributor:       Midwest Window & Door Supply (Gold Partner)
Product:           Commercial Casement Window
Product SKU:       CCW-4860-LG
Quantity:          24 units
Dimensions:        48" W × 60" H
Production Start:  April 28, 2026

──────── Requested Changes ────────
New Dimensions:    48" W × 62" H
Reason:            End-customer site survey found an updated header
                   height. Please confirm production can accommodate
                   the 2" increase.

Best regards,
Alex Morrison
Orders Specialist · Midwest Window & Door Supply
`,
  qc_batch: `ARCHIVE MANIFEST — QC_Batch_50_Certificates.zip
════════════════════════════════════════════════════

Source:    Apex Vinyl Solutions supplier portal (SUP-0081)
Material:  Vinyl Resin Compound
Plant:     Ohio Plant 7
Sealed:    April 21, 2026 · 06:00 ET

────── Contents (50 files, 12.4 MB total) ──────
  QC_Cert_LOT-A01.pdf    312 KB    ✓
  QC_Cert_LOT-A02.pdf    298 KB    ✓
  QC_Cert_LOT-A03.pdf    304 KB    ✓
  …
  QC_Cert_LOT-A44.pdf    287 KB    ⚠  tensile flag on cover sheet
  …
  QC_Cert_LOT-B12.pdf    315 KB    ⚠  color delta flag on cover sheet
  …
  QC_Cert_LOT-B48.pdf    290 KB    ✓
`,
  port_strike: `<?xml version="1.0" encoding="UTF-8"?>
<DisruptionAlert source="GlobalSupplyChainMonitor">
  <AlertID>SC-ALERT-2026-0441</AlertID>
  <EventType>PortStrike</EventType>
  <Severity>HIGH</Severity>
  <Port code="KSAV">Port of Savannah, GA</Port>
  <AffectedSupplier>
    <Id>SUP-0044</Id>
    <Name>Chemours Vinyl Resins</Name>
  </AffectedSupplier>
  <Material grade="A">Vinyl Resin (PVC)</Material>
  <DelayDays>7</DelayDays>
  <ExpectedRecovery>2026-04-28</ExpectedRecovery>
  <Confidence>0.99</Confidence>
  <Region>Southeast US</Region>
  <Timestamp>2026-04-21T09:08:00Z</Timestamp>
</DisruptionAlert>
`,
  invoice: `GLOBEX CORPORATION
────────────────────────────────────────
Invoice #:  GLX-2024-0441
Date:       April 18, 2026
Bill To:    Cornerstone Building Brands
            Attn: Accounts Payable
PO Ref:     PO-2024-0891

LINE ITEMS
────────────────────────────────────────
  Widget A        200 @ $180.00    $36,000.00
  Widget B        120 @ $215.00    $25,800.00

  Subtotal                          $61,800.00
  Freight                            $18,565.00
  Tax                                 $7,035.00
  ─────────────────────────────────
  TOTAL                             $87,400.00

Payment Terms: Net 30
`,
  claim: `INSURANCE CLAIM — FNOL FORM
─────────────────────────────────────
Claim #:        CL-8821
Policy #:       POL-2021-44821
Claimant:       Meridian Properties
Incident Type:  Water damage (interior)
Incident Date:  April 12, 2026
Claim Value:    $142,000
Deductible:     $5,000

Narrative:
Flooding from a burst second-floor supply line affected
approx. 1,200 sq ft across 4 rooms. First responder photos
and moisture readings attached (pp. 3–7).
`,
  po: `PURCHASE ORDER
──────────────
PO #:      PO-4421
Vendor:    Acme Industrial
Ordered:   April 20, 2026
Deliver:   April 24, 2026 (RUSH)

  SKU          QTY     UNIT
  ACM-7701     500     $41.20
  ACM-7702     250     $28.40
  ACM-7703     100     $64.00

  Subtotal          $33,000.00
  Rush surcharge     $1,200.00
  ─────────────────────────
  TOTAL             $34,200.00
`,
  qc: `QUALITY CONTROL REPORT
─────────────────────────
Batch:           2024-B
Plant:           Houston TX — Line 3
Inspection:      April 19, 2026
Units inspected: 2,400

Defect summary:
  Surface crack        12 units
  Dimensional drift     7 units
  ─────────────────────────
  Pass rate          99.2% (2,381 / 2,400)

Hold recommendation: partial — 19 units pending re-inspection.
`,
  contract: `VENDOR SERVICES AGREEMENT
──────────────────────────
Contract ID:  CTR-2026-GC-041
Parties:      Cornerstone Building Brands   ("Client")
              Gulf Coast Logistics LLC      ("Vendor")
Effective:    May 1, 2026
Expiry:       April 30, 2028
Value:        $4.2M over 24 months
Auto-renew:   Yes — 60-day notice
Penalty:      2% per week of delay
Governing:    State of Texas

Section 4.2 — Service Credits
If Vendor fails to meet the agreed SLA for two consecutive
reporting periods, Client may invoke service credits …
`,
  alert: `SUPPLY CHAIN ALERT
──────────────────
Alert ID:         SC-ALERT-2026-0441
Component:        Vinyl Resin (VR-2201)
Supplier:         ChemCo Industries
Delay duration:   7 days
Plants affected:  Houston, Dallas, Memphis
SKUs affected:    14
Revenue at risk:  $1.09M
Alternate:        PolySource Inc — 3-day lead, +15% premium
`,
  /* ──────── STP Phase 2 ──────── */
  stp_policy: `STP NUCLEAR — POLICY / PROCEDURE / TECH SPEC
═══════════════════════════════════════════════════════
Document ID:   STP-POL-0PGP03-ZE-0033
Title:         Operational Decision-Making Process (ODMP)
Revision:      Rev 14
Effective:     April 1, 2026
Owner:         Operations · STP Nuclear Operating Company

§ 3.4  Risk-Informed Threshold for Continued Operation
   When a degraded condition is identified during an
   operating cycle, the on-shift Senior Reactor Operator
   shall convene an ODMP review within 24 hours. The
   review must document:
     (a) safety-significance per 10 CFR 50.65,
     (b) defense-in-depth impact,
     (c) compensatory measures, and
     (d) restoration timeline.

§ 3.5  Tech Spec LCO 3.5.2 — ECCS Trains
   With one train of ECCS inoperable, restore the
   inoperable train to OPERABLE status within 7 days
   or be in MODE 3 within the next 6 hours …

[ → Indexed for verbatim citation by PolicyAgent ]
`,
  stp_pm_history: `STP NUCLEAR — WORK PACKAGE PDF
═══════════════════════════════════════════════════════
Work Order:    WO-STP-2025-04412
Equipment:     PUMP-RHR-1A   (Residual Heat Removal Pump 1A)
Train:         A
Performed:     March 14, 2026
Engineer:      J. Whitfield  (Mech Eng II)
PM Type:       PM-18M  (18-month preventive maintenance)
Reference:     0PGP03-ZE-0024  (eAM PM master)

────── Steps Performed ──────
  1. Lockout/tagout per LO-9914
  2. Bearing housing inspection — within tolerance
  3. Mechanical seal replacement — Flowserve P/N 4421-A
  4. Vibration baseline:  axial 0.18 in/s · radial 0.21 in/s
  5. Lube oil sample sent to Predictive Maint. Lab

────── Findings ──────
  • Seal leak rate trending upward since 2024 PM
  • Coupling alignment 0.003" — within spec
  • No abnormal wear indicators

[ → Cross-referenced to eAM record + indexed by MaintenanceAgent ]
`,
  stp_issue_analysis: `STP NUCLEAR — INCIDENT / FAILURE REPORT
═══════════════════════════════════════════════════════
Incident ID:   IR-2026-0188
Equipment:     VALVE-MOV-CV-1234
System:        Component Cooling Water (CCW)
Reported:      April 18, 2026 · 02:14 CDT
Reporter:      Shift Supervisor — D. Alvarez
Status:        Investigation In Progress

────── Symptom ──────
  MOV failed to fully close on auto-signal during
  routine surveillance ST-RT-CCW-001. Stem position
  feedback indicated 6° remaining travel; thermal
  overload tripped after 14s of motor stall.

────── Suspected Root Cause ──────
  Stem packing gland over-tightened during last
  PM (WO-STP-2025-03991, Dec 2025). Packing-induced
  friction exceeded actuator torque budget.

────── Linked Work Orders ──────
  • WO-STP-2025-03991  (PM — packing replacement)
  • WO-STP-2024-09112  (PM — actuator overhaul)
  • WO-STP-2023-04477  (Corrective — limit switch)

[ → Aggregated by DiagnosticsAgent · failure mode tagged ]
`,
  ae_inventory_alert: `INVENTORY SHORTAGE ALERT — AGENTIC ENTERPRISE
═══════════════════════════════════════════════════════
From:    merchandising@example.com
Subject: Stockout — SKU-892 — Dallas Spring Promotion
Date:    May 4, 2026 · 06:42 ET

Heads up — we're short ~500 units of SKU-892 (Wireless
Earbuds Pro) for the Dallas Spring Promotion launching
May 15.  Inventory shows zero across all distribution
centers (DAL-01, MEM-02, LAX-03), and the 12 units in
NJ-04 are already reserved.

The promo is locked.  We need a fast supplier that can
land 500 units in Dallas before May 15.

Resolve and route a draft PO to this address for approval.

— J. Patel, Director of Merchandising
`,
  ae_lease_pdf: `COMMERCIAL LEASE — Aurora Biotech Solutions, Inc.
═══════════════════════════════════════════════════════
LANDLORD:   Crescent Tower Holdings, LLC
TENANT:     Aurora Biotech Solutions, Inc.
PREMISES:   500 Lamar Street, Floor 14, Austin TX 78701
            18,400 rentable square feet

TERM:
  Commencement:  January 1, 2024
  Expiration:    December 31, 2026
  Renewal:       1 × 3-year option (180 days notice)

RENT:
  Base:           $48.00 / sf / yr ($73,600 / month)
  Escalation:     3% / yr

LIABILITY (Article 7 — verbatim):
  "Tenant shall indemnify, defend, and hold harmless
   Landlord, its members, managers, agents, employees,
   and lenders from and against any and all claims,
   demands, losses, damages, liabilities, costs and
   expenses (including reasonable attorneys' fees) …
   The foregoing indemnification obligation shall
   survive the expiration or earlier termination of
   this Lease for a period of three (3) years."

INSURANCE:    $5M per occurrence / $10M aggregate
GOVERNING:    State of Texas
SIGNED:       December 19, 2023
`,
  stp_predictive: `STP NUCLEAR — SENSOR ANOMALY STREAM (24 h)
═══════════════════════════════════════════════════════
Source:    OSI PI Historian · Tag PI:CCW-PMP-1A:VIB
Equipment: PUMP-CCW-1A   (Component Cooling Water Pump 1A)
Window:    2026-04-29 00:00 → 2026-04-30 00:00 CDT

  Timestamp (UTC)        Vib (in/s)   Temp (°F)   ΔP (psi)
  ────────────────────   ──────────   ─────────   ────────
  2026-04-29T04:00:00     0.21         142          18.2
  2026-04-29T08:00:00     0.24         143          18.1
  2026-04-29T12:00:00     0.31  ⚠      147  ⚠       17.9
  2026-04-29T16:00:00     0.38  ⚠      151  ⚠       17.5  ⚠
  2026-04-29T20:00:00     0.46  ⚠⚠     155  ⚠⚠      17.0  ⚠⚠
  2026-04-30T00:00:00     0.52  ⚠⚠     158  ⚠⚠      16.6  ⚠⚠

Anomaly score:    0.87  (HIGH)
Trend:            Monotonic increase — bearing degradation pattern
RUL forecast:     21 days (P10) · 34 days (P50) · 48 days (P90)
PM advance:       Recommended 14-day pull-in vs. scheduled cycle
$ avoidance:      ≈ $480k (forced outage avoided)

[ → ReliabilityAgent: PM advance package drafted for human review ]
`,

  /* ──────── Telecommunications · Verizon Far Edge POC ──────── */

  tel_robot_xml: `VERIZON FAR EDGE — ROBOT FRAMEWORK TEST OUTPUT
═══════════════════════════════════════════════════════════
Cycle id:    CYCLE-20260115-CAAS-B-2412
Device:      CaaS-Edge-Node-Type-B  ·  Wind River 24.12
Region:      Northeast
Started:     2026-01-15T09:14:22Z
Total tests: 247

  Suite                        Pass    Fail    Warn
  ──────────────────────────  ─────   ─────   ─────
  CU-UP Interface                35      2       1
  Redfish API                    34      6       2
  OpenShift Operator             35      0       0
  Wind River CaaS Boot           27      0       1
  Ansible Idempotency            23      0       0
  RT Kernel Latency              17      0       1
  Firmware Signature             14      0       0
  OAM Interface                  21      1       0
  gNB-DU Configuration           16      0       0
  IPv6 Enumeration                9      3       0
  ──────────────────────────  ─────   ─────   ─────
  TOTAL                         231     12       5

Top P1 failures
  s2-t1  PowerState not found at /redfish/v1/Systems/1   (schema drift)
  s2-t2  FanSpeeds[].CurrentReading deprecated           (schema drift)
  s2-t3  IPv6Addresses required field missing            (schema drift)
  s1-t1  CU-UP latency 8.3 ms vs 5 ms threshold          (KB-2026-0118)

[ → CertificationAgent: 12 JIRA tickets queued · epic APEXVZ-SCHEMA-EPIC-2026-01 ]
`,

  tel_redfish_diff: `REDFISH SCHEMA — BREAKING CHANGE DETECTION
═══════════════════════════════════════════════════════════
Baseline:  Redfish v1.14.0  (Wind River 24.06)
Current:   Redfish v1.16.0  (Wind River 24.12)
Detected:  2026-01-12T03:18:44Z   (6 days before scheduled cycle)

  BREAKING CHANGE 1  /redfish/v1/Systems/1
    PowerState  →  Status.PowerState         (path migration)
    Scripts impacted: 6  (power_check.yml, node_health_check.yml,
                         pre_upgrade_validation.yml, post_upgrade_validation.yml,
                         site_readiness_check.yml, wave_deployment_preflight.yml)
    Vendor ref: Wind River 24.12 §3.2.1

  BREAKING CHANGE 2  /redfish/v1/Chassis/1/Thermal
    FanSpeeds[].CurrentReading  →  Fans[].Reading      (rename + restructure)
    Scripts impacted: 5  (thermal_baseline.robot, thermal_regression.robot,
                         thermal_stress_test.robot, fan_speed_monitor.yml,
                         thermal_alert_check.yml)

  BREAKING CHANGE 3  /redfish/v1/Managers/1/EthernetInterfaces/1
    IPv6Addresses (optional)  →  IPv6Addresses (REQUIRED)
    Scripts impacted: 3  (interface_validation.robot,
                         ipv6_enumeration_check.robot, network_baseline.yml)

Total scripts impacted: 14
Effort to remediate:    2.0 hr (deterministic find/replace)
Wave deployment:        HELD until epic APEXVZ-SCHEMA-EPIC-2026-01 completes

[ → SchemaWatchAgent: 5 subtasks created · automation team notified ]
`,

  tel_upgrade_runbook: `VZ-UPGRADE-PROCEDURES-2026 · Rev 4  (excerpt)
═══════════════════════════════════════════════════════════
Owner:    Cert Team · HQ Planning  (J. Patchett · Distinguished Engineer)
Audience: Wave-deployment authorizers, automation engineers
Length:   67 pages   ·   Last revised: 2026-01-08

§1  Supported upgrade paths — CaaS-Node-Type-B
    22.12  →  23.06  →  24.01  →  24.12         ← canonical
    23.06  →  24.06  →  24.12                   ← skip via 24.06 OK
    23.06  →  24.12                             ← BLOCKED  (skip > 1)

§2  Step-by-step  ·  22.12 → 24.12  (single representative path)
    Step 1  Pre-flight  · site_readiness_check.yml  (15 min/site)
    Step 2  Drain        · caas_drain.yml             (workload bleed)
    Step 3  Apply 23.06  · firmware_apply_23_06.yml   (BMC update)
    Step 4  Validate     · post_upgrade_smoke.robot   (12 assertions)
    Step 5  Apply 24.01  · firmware_apply_24_01.yml
    Step 6  Validate     · post_upgrade_smoke.robot
    Step 7  Apply 24.12  · firmware_apply_24_12.yml
    Step 8  Validate     · full certification cycle   (247-test suite)
    Step 9  Uncordon     · caas_uncordon.yml

§3  Online-risk policy
    Type-B nodes in Northeast: max 3-hour outage window per site.
    HITL approval required when site count > 100 OR risk tier=critical.

§4  Rollback  ·  rollback_to_checkpoint.yml
    BMC snapshot taken before each step.   RTO: 25 min per site.

[ → UpgradeAdvisorAgent: full path validated · 25% historical fail rate flagged ]
`,

  tel_kb_article: `KB-2026-0118  ·  CU-UP LATENCY UNDER DEFAULT RT TUNING
═══════════════════════════════════════════════════════════
Severity:   HIGH  ·  production-blocker under sustained load
Affected:   CaaS-Node-Type-B  ·  Wind River 24.06 and 24.12
Status:     Mitigation required  ·  Permanent fix in 25.01
Last revd:  2026-01-08  ·  Cert Team (D. Vargas, RT Kernel SME)

SYMPTOMS
  Sustained CU-UP P99 interface latency drifts from baseline 3.2 ms
  toward 6-8 ms over the first 30 minutes after boot, breaching the
  5 ms certification threshold during the warm-up window.

ROOT CAUSE
  kernel.sched_rt_runtime_us default of 950000 (95% of period)
  leaves insufficient headroom for the CaaS-orchestrator pod
  scheduler under cold-cache conditions on Type-B SKUs.

WORKAROUND  (apply at boot)
  Set kernel.sched_rt_runtime_us = 980000 in
    /etc/sysctl.d/99-rt-tune.conf
  and apply with \`sysctl -p\`.   Effective on next boot.

  Ansible playbook reference:
    apex-rt-tune.yml  (drops the sysctl file and reboots in MW)

PERMANENT FIX
  Wind River 25.01 changes the default to 980000 in the base image.

CROSS-REFERENCED TICKETS
  APEXVZ-2418 · CU-UP latency 8.3 ms on cu_up_interface_0
  APEXVZ-2419 · CU-UP throughput 1.8 Gbps below threshold
  (11 of 12 P1 failures in CYCLE-20260115 trace to this article)

[ → MentorAgent: verbatim citation returned to ChatVZ · audit-trail logged ]
`,

  /* ─── VERIZON FAR EDGE · 12 REAL firmware reports (James Patchett · MTCE Lab) ─── */

  vz_dmtf_e930t: `# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# MEAKV-507 DMTF Conformance test
════════════════════════════════════════════════════════════════════════

Redfish-Protocol-Validator v1.2.0
Service: Edgeline e930t · iLO 6 v1.57

    Summary - PASS: 392, WARN: 0, FAIL: 7, NOT_TESTED: 31

──── THE 7 FAILURES (all known-benign) ─────────────────────────────────
RESP_HEADERS_WWW_AUTHENTICATE
 FAIL GET 401 /redfish/v1/SessionService/Sessions/   WWW-Authenticate header missing
 FAIL GET 401 /redfish/v1/Managers/1/NetworkProtocol/ WWW-Authenticate header missing
 FAIL GET 401 /redfish/v1/Systems/                    WWW-Authenticate header missing
 FAIL GET 401 /redfish/v1/AccountService/Accounts/    WWW-Authenticate header missing
 FAIL POST 401 /redfish/v1/AccountService/Accounts/   WWW-Authenticate header missing
 FAIL GET 401 /redfish/v1/AccountService/             WWW-Authenticate header missing
SEC_CERTS_CONFORM_X509V3
 FAIL  Exception decoding certificate — Address family for IPv6 hostname not supported

──── ENGINEER VERDICT ──────────────────────────────────────────────────
### These failed tests are not relevant to operation of redfish with
### VCPfe in production
### Uploaded files to Jira
### marked test passed
                                              — James Patchett, MTCE Lab

──── APEX CertificationAgent ───────────────────────────────────────────
Recognized 7-failure signature = WWW-Authenticate(6) + X.509-IPv6(1).
This signature recurs IDENTICALLY across iLO5 3.06, iLO6 1.60, ZT BMC.
Rule: "production-irrelevant for VCPfe" → AUTO-CERTIFY, attach evidence.
Verdict matches James's manual decision · routed to HITL for sign-off.
Manual effort saved: ~40 hr/firmware × 42 HPE reports in this corpus.
`,

  vz_samsung_ssd: `# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/16/24 James Patchett
# MEAKV-1792 Samsung SSD Temperature Issue
════════════════════════════════════════════════════════════════════════

### Samsung SSD Temperature issue in BMC
### Drive type: SAMSUNG SSD PM9A3 (MZQL21T9HCJR-00A07)
### In .45 BMC, Samsung temperature could NOT be read,
###   which causes fans to spike to 100% utilization
### Goal: reproduce in lab on .45, prove new .46 BMC fixes it

──── REPRODUCTION (downgrade .46 → .45) ────────────────────────────────
update-bmc-redfish-python v0.45.00 ...
  Model name is Proteus · System Serial 207736270043
  BMC current version is 0.46.00 → installing 0.45.00
  Manager.Reset task issued (TaskState: New)

  >> On .45: PM9A3 thermal sensor reads N/A → fan controller defaults
  >> to FAILSAFE → all fans ramp to 100% (acoustic + power impact)

──── VALIDATION (.46 restores) ─────────────────────────────────────────
  On .46: PM9A3 temperature reads correctly → fans return to nominal
  Lab-confirmed regression + fix.

──── APEX SchemaWatchAgent ─────────────────────────────────────────────
REGRESSION CONFIRMED · BMC .45 thermal read failure on Samsung PM9A3.
Blast radius: every subcloud with PM9A3 drives running BMC .45.
→ UpgradeAdvisor: BLOCK .45 wave deployment to PM9A3-equipped sites.
→ Mandate BMC .46 as minimum for Samsung PM9A3 fleet.
`,

  vz_bmc_upgrade: `# ZT Proteus .46 BMC firmware validation
# ZT Proteus BIOS .23
# 1/29/24 James Patchett
# WRCP 21.05p6 → 21.12p10 subcloud upgrade
════════════════════════════════════════════════════════════════════════

## Target Subcloud welktxef-d931856-008 (anonymized)
## System: duplex · Standard · distributed-cloud subcloud

──── BASELINE (pre-upgrade) ────────────────────────────────────────────
system show → software_version 21.05 · Wind River Cloud Platform 21.05
fm alarm-list:
  280.002  kubernetes sync_status out-of-sync   major
  280.002  load sync_status out-of-sync         major
  (expected during subcloud staging)

──── UPGRADE 21.05p6 → 21.12p10 ────────────────────────────────────────
  ... update from version 21.05-30 to version 21.12-46 completed.
  rook-ceph-apps   1.0-5   manifest.yaml   uploaded → completed

──── POST-UPGRADE VALIDATION ───────────────────────────────────────────
  fm alarm-list → clean
  system application-list → reconciled
  BMC 0.46 · BIOS 0.23 confirmed

──── APEX UpgradeAdvisorAgent ──────────────────────────────────────────
Path WRCP 21.05p6 → 21.12p10 VALIDATED end-to-end on ZT Proteus.
Added to upgrade compatibility matrix → feeds wave-deployment risk model.
`,

  vz_ptu_perf: `# HPE ILO6 1.57 BIOS H11 v1.11
# HPE Sapphire Rapids E930t server
# 3/24/24 James Patchett - MTCE Lab VCPfe
# Performance Test MEAKV-642-646
════════════════════════════════════════════════════════════════════════

Intel PTU (Power Thermal Utility) sustained CPU + memory stress.

  CPU package power ........ within Sapphire Rapids TDP envelope
  Core temps ............... no throttle events observed
  Memory bandwidth ......... nominal under sustained load
  Throttle log ............. clean

Outcome: PASS · platform holds performance under sustained PTU load.

──── APEX CertificationAgent ───────────────────────────────────────────
Perf baseline captured for cross-firmware regression tracking. No action.
`,

  vz_sensor_proteus: `# ZT Proteus 3.02 BMC firmware validation
# ZT Proteus BIOS .30
# 10/17/25 James Patchett
# MEAKV-1789-1791 Functional Sensor / Sensor List
════════════════════════════════════════════════════════════════════════

IPMI sensor list (excerpt):
  CPU_0_DTS_TEMP   -42Cel   OK
  PSU_1_TEMP_2      45Cel   OK   (UNR 92 / UC 97)
  PSU_1_TEMP_1      26Cel   OK   (UNR 60 / UC 64)
  PSU_2_TEMP_2      45Cel   OK
  ...
  (all sensors present + within thresholds)

Outcome: PASS · sensor readout complete + accurate on BMC 3.02.

──── APEX CertificationAgent ───────────────────────────────────────────
No missing-sensor regression (contrast: Samsung PM9A3 on BMC .45).
Feeds thermal telemetry model for fleet-wide anomaly baselining.
`,

  vz_bios_triton: `# ZT Triton 2.31 BMC firmware validation
# 2024 James Patchett
# MEAKV-508-517 Functional BIOS
════════════════════════════════════════════════════════════════════════

Method: Redfish PATCH /redfish/v1/Systems/Self/Bios/SD
  {"Attributes": {"PMS012": "Disable"}}

  >> Settings applied · survive host reboot · re-read confirms persistence
  >> NOTE: PATCH during host boot returns:
     503 Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting
     (retry-after-boot required — folded into BMC playbook)

Outcome: PASS · BIOS attribute control via Redfish working on BMC 2.31.

──── APEX CertificationAgent ───────────────────────────────────────────
BIOS cert passed · 503-during-boot transient noted for runbook.
`,

  vz_redfish_proteus: `# ZT Proteus .46 BMC firmware validation
# 2024 James Patchett
# MEAKV-648-655 Functional Redfish
════════════════════════════════════════════════════════════════════════

Redfish functional surface walked:
  /redfish/v1/Systems        GET inventory ........ OK
  /redfish/v1/Managers       GET + Manager.Reset .. OK (task New→Completed)
  /redfish/v1/Chassis        GET power/thermal .... OK
  /redfish/v1/TaskService    task lifecycle ....... OK

Outcome: PASS · all Redfish functional endpoints responsive on BMC .46.

──── APEX CertificationAgent ───────────────────────────────────────────
Redfish functional cert passed. No conformance triage needed here.
`,

  vz_platform_deploy: `# HPE ILO6 1.57
# HPE Sapphire Rapids E930t server
# 2024 James Patchett
# MEAKV-965 Platform Deployment
════════════════════════════════════════════════════════════════════════

Wind River Cloud Platform subcloud install on E930t:
  duplex controllers + worker enrolled to system controller
  platform-integ alarms cleared post-deploy
  distributed-cloud sync_status → in-sync

Outcome: PASS · subcloud enrolled · platform healthy · ready for workload.

──── APEX UpgradeAdvisorAgent ──────────────────────────────────────────
Deployment certified · subcloud added to fleet inventory for wave planning.
`,

  vz_soak_galene: `# ZT Galene 1.13 BMC firmware validation
# 4/15/25 James Patchett
# Soak Test on E2E system
════════════════════════════════════════════════════════════════════════

## Soak window: 4/08/25 → 4/15/25 (~7 days continuous)
## Monitor: /var/log/user.log for PTP4L sync error accumulation

  2025-04-07 ptp4l port 1: FAULTY → LISTENING on INIT_COMPLETE  (expected init)
  ... 7 days ...
  >> No accumulation of PTP4L sync errors over the soak window.

Outcome: PASS · Galene BMC 1.13 stable for long-duration far-edge deploy.

──── APEX CertificationAgent ───────────────────────────────────────────
Soak cert passed · longevity baseline logged for the fleet.
`,

  vz_dell_sensor: `# Dell iDRAC 7.10.50.10 BIOS 1.8.3
# Dell PowerEdge R7615
# 3/25/26 James Patchett - MTCE Lab VCP100
# Functional Testing - Sensor List / BMC Sensor Validation MEAKV-1789
════════════════════════════════════════════════════════════════════════

## testhost · iDRAC via ProxyJump (vcpe-jumpserver2)

  iDRAC Redfish sensor list parsed + normalized against HPE iLO / ZT BMC.
  All thermal + voltage + fan sensors present + within thresholds.

  >> Dell R7615 = newest fleet addition. SAME MEAKV-1789 cert catalog
  >> runs unchanged across HPE Edgeline, ZT, and Dell.

Outcome: PASS · multi-vendor cert · one rule-set spans 3 vendors.

──── APEX CertificationAgent ───────────────────────────────────────────
Cross-vendor sensor cert passed. The cert catalog is vendor-portable.
`,

  vz_troubleshoot: `# ZT .43 BMC firmware validation
# 8/25/23 James Patchett
# Troubleshooting — Redfish on ZT
════════════════════════════════════════════════════════════════════════

Symptom: Redfish PATCH /Systems/Self/Bios/SD →
  503 "The requested operation is temporarily unavailable since Host
       System Reboot might be in progress ... Redfish Inventory
       processing might be in progress. Please try after sometime."
  code: Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting

Remediation:
  POST /Managers/Self/Actions/Oem/AMIManager.RedfishDBReset
    {"RedfishDBResetType": "ResetAll"}
  → Task created → stuck Redfish DB cleared → PATCH succeeds.

──── APEX SchemaWatchAgent ─────────────────────────────────────────────
Transient classified (host-boot / inventory window). RedfishDBReset
remediation captured → folded into MentorAgent BMC-playbook KB.
`,

  vz_flexran: `# HPE ILO6 1.60
# HPE Sapphire Rapids E930t server
# 2024 James Patchett
# MEAKV-1860 FlexRAN Settings
════════════════════════════════════════════════════════════════════════

Intel FlexRAN RT-optimized BIOS profile validated:
  C-state ............ disabled (deterministic latency)
  P-state ............ fixed
  Uncore frequency ... pinned
  Hyper-Threading .... per FlexRAN spec

Outcome: PASS · FlexRAN BIOS profile applied + verified · RAN-ready.

──── APEX CertificationAgent ───────────────────────────────────────────
FlexRAN cert passed · cross-refs KB-2026-0118 RT-tuning
(kernel.sched_rt_runtime_us) for CU-UP latency under load.
`,

  /* ─── VERIZON CAS · current-gen campaign docs (June 2026) ─── */

  vz_cas_el140: `# HPE EL140 Gen12 — Test Campaign Summary
# Platform: HPE ProLiant Compute EL140 Gen12
# BMC Firmware: iLO 7 v1.20.00 | BIOS: v1.30
# Date: 2026-06-10 · Replaces BLOCKED: MEAKV-1750, MEAKV-1793
════════════════════════════════════════════════════════════════════════

A brand-new server type (iLO 7) that the existing BMC playbook does NOT
support. Existing MEAKV-1750/1793 are BLOCKED. The orchestrator designed
and ran a 13-test campaign (PROPOSED-20→32) against a live lab unit.

──── PROPOSED test outcomes ─────────────────────────────────────────────
  PROPOSED-20  BMC User Account Create      PASS  (iLO7 IDs 65536+)
  PROPOSED-23  NTP Configuration            PASS  (DateTime endpoint on iLO6+iLO7)
  PROPOSED-24  DNS Configuration            PASS-DEV (StaticNameServers 1..3 limit)
  PROPOSED-25  BMC Hostname                 PASS  (NetworkProtocol.HostName)
  PROPOSED-27  Redfish Event Subscription   PASS  (RegistryPrefixes req on iLO6+7)
  PROPOSED-28  NIC/MAC Discovery + BIOS     PASS  (Chassis/1/NetworkAdapters)
  PROPOSED-29  Playbook Gap Analysis        → change-spec (7 changes)
  PROPOSED-30  Secure Boot Cert Install     new TC
  PROPOSED-32  Security Hardening           new role (does not exist)

──── playbook change spec ───────────────────────────────────────────────
  7 CHANGE REQUIRED · 7 NO CHANGE · 1 VERIFY · across 15 role files.

──── compliance gaps ───────────────────────────────────────────────────
  NEBS 62°C inlet ambient caution threshold UNSET (null) on EL140.
  No security-hardening role exists in the playbook.

──── APEX OrchestratorAgent ─────────────────────────────────────────────
Drove the end-to-end run: design → execute ×5 iterations → gap analysis →
change-spec → HITL approval → apply. ~40h manual → ~18m orchestrated.
`,

  vz_cas_xr8720: `# Test Campaign Summary — Dell XR8720t
# BIOS 1.1.3 / iDRAC 1.30.10.51 (iDRAC 10)
# 2026-06-16 → 2026-06-17
════════════════════════════════════════════════════════════════════════
platform: Dell XR8720t · 17G DCS
processor: Intel Xeon 6776P-B (GNR-D) · 72 cores / 144 threads
memory: 256 GB DDR5 ECC 6400 MT/s MaxPerf

  Overall: PASS WITH DEVIATIONS
  40 tests · 29 PASS · 10 PASS-WITH-DEVIATION · 1 PARTIAL · 0 FAIL

──── by category ────────────────────────────────────────────────────────
  Inventory     MEAKV-648→655   PASS (655 PARTIAL: HttpPushUri null — expected)
  Sensors       MEAKV-518→523   PASS · MEAKV-1789 PASS
  BIOS          MEAKV-508→517   PASS / PASS-DEV
  Security      PROPOSED-10/14  PASS (TLS 1.3 default; 1.0/1.1 rejected)
  Conformance   MEAKV-507       PASS-DEV (379 pass / 9 benign fails)
  LED           PROPOSED-13     PASS-DEV (IndicatorLED "Off" → HTTP 400)

──── accepted deviations ────────────────────────────────────────────────
  IommuSupport=null · NumaNodesPerSocket=null · ProcX2Apic=null
  → GNR-D platform differences from the AMD R7615 baseline. VT-d functional
  via ProcVirtualization=Enabled; NUMA topology correct. All triaged benign.

──── APEX CertificationAgent ─────────────────────────────────────────────
Current-gen Dell cert · 0 failures · every deviation documented + accepted.
`,

  vz_cas_playbook_spec: `# BMC Playbook Change Specification
# New Server Type: HPE EL140 Gen12 (iLO 7)
# Playbook: commit 5ff15f7028 / v1.0-66548 / vcpe-jumpserver2
# Status: DRAFT — Pending automation-team review
════════════════════════════════════════════════════════════════════════

Cross-referenced PROPOSED-20→32 results against the live Ansible playbook.

  Role / File                  Assessment        PROPOSED   Why
  ─────────────────────────────────────────────────────────────────────
  group_vars/HPE               CHANGE REQUIRED   P-28       add vRAN var
  check_model                  CHANGE REQUIRED   P-28       no EL140 match
  bios-config                  CHANGE REQUIRED   P-28       WorkloadProfile=vRAN
  mac-discover                 CHANGE REQUIRED   P-28       NIC name fails iLO7
  ilo-hostname                 CHANGE REQUIRED   P-25       NetworkProtocol.HostName
  subscribe-redfish-events     CHANGE REQUIRED   P-27       RegistryPrefixes (iLO6+7)
  security-hardening (NEW)     GAP — DOES NOT    P-32       SNMP/HTTP/IPMI/SSDP
                               EXIST                        disable + login banner
  account-create               NO CHANGE         P-20/21/22 dynamic @odata.id
  set_ilo_sntp_servers.py      NO CHANGE         P-23       targets DateTime
  configure_dns.py             VERIFY REQUIRED   P-24       iLO7 path check

──── CHANGE 1 — group_vars/HPE ──────────────────────────────────────────
  # ADD
  bios_attribute_value_workload_profile_vRAN: vRAN
  Reason: EL140 BIOS rejects any other WorkloadProfile (applies 11 vRAN
  settings atomically). Risk: none — new var only; e910/920/930t unaffected.

──── APEX PlaybookAgent ─────────────────────────────────────────────────
This is a PROPOSAL — nothing is applied until a human approves (HITL gate).
`,

  vz_cas_thermal: `# XR8720t Thermal Sensor Comparison — iDRAC 1.30.10.51 vs 1.30.33.10
# Host: welktxwr-HDM35J4-dl-720x-001 · BIOS 1.1.3 (unchanged)
# Endpoint: GET /redfish/v1/Chassis/System.Embedded.1/Thermal
════════════════════════════════════════════════════════════════════════

Question: does the newer iDRAC expose more thermal sensors?
Answer: No — 2 temp + 16 fan in BOTH. The only change is threshold values.

──── Inlet Temp threshold drift ─────────────────────────────────────────
  Threshold                       1.30.10.51    1.30.33.10
  LowerThresholdNonCritical       null     →    -23 °C   (newly populated)
  UpperThresholdNonCritical       null     →     58 °C   (newly populated)
  UpperThresholdCritical          62 °C         62 °C    (unchanged)

──── why it matters ─────────────────────────────────────────────────────
On 1.30.10.51 the inlet-temp WARNING band is null — production sites on
that rev get NO early caution alarm before the 62°C critical (NEBS context).

──── APEX SchemaWatchAgent ──────────────────────────────────────────────
Firmware drift → golden-config flag · recommend roll-forward to 1.30.33.10.
`,

  vz_cas_wrcp: `# Wind River Cloud Platform 24.09.301 — Platform Certification Campaign
# CAS far-edge · OS/platform layer (distinct from BMC/firmware)
════════════════════════════════════════════════════════════════════════

  1,281 artifacts · 390 MB · vs 2212 baseline

──── coverage ───────────────────────────────────────────────────────────
  Performance   1,080 sysbench runs × 6 HW types × 5 iterations
                (HP E910/Ice/SPR · ZT Ice/SPR/Titan) · latency · network · storage
  Functional    RBAC · K8s CPU Manager · Docker Registry · Redfish API
  Platform      Alarms · Certificates · HA · Power · Rehoming · Software Update
  Conformance   Kubernetes sonobuoy
  Deployment    MOPs VZFWE-25 / VZFWE-26 (Central Controller install runbooks)

──── test IDs ───────────────────────────────────────────────────────────
  VZFWE-13/14/16/25/26/463 · VZWFE-164/202/204/463/489/490/492/649/655 · MEAKV-1658

──── APEX CertificationAgent ─────────────────────────────────────────────
The OS/platform cert layer — same multi-iteration rigor (5 runs each) and
the same orchestration + golden-config as the BMC/firmware layer.
`,

  /* ─── EPROD (Enterprise Products Partners) — 15 midstream sample files ─── */
  eprod_inv_hal: `================================================================================
                            HALLIBURTON ENERGY SERVICES, INC.
                            3000 N. Sam Houston Parkway East
                                  Houston, TX 77032
                            Tax ID: 75-2677995  Phone: (281) 871-2699
================================================================================

INVOICE

Invoice Number:    INV-HAL-2026-04-3847
Invoice Date:      05/02/2026
Service Period:    04/01/2026 - 04/30/2026
PO Number:         PO-2026-INT-3318
MSA Reference:     MSA-HAL-2024-03
Payment Terms:     Net 45
Due Date:          06/16/2026

Bill To:
    Enterprise Products Operating LLC
    Attn: Accounts Payable - Pipeline Integrity
    P.O. Box 4324
    Houston, TX 77210-4324

Remit To:
    Halliburton Energy Services, Inc.
    P.O. Box 301341
    Dallas, TX 75303-1341

--------------------------------------------------------------------------------
LINE  DESCRIPTION                                     QTY    UNIT      TOTAL
--------------------------------------------------------------------------------
 1    Inline Inspection (ILI) - 24" Mainline,         148    miles     128,760.00
      Seminole-Hobbs Lateral, MFL High-Resolution            @ 870.00/mi
 2    NDT Ultrasonic Wall-Thickness Survey,            72    hours      18,360.00
      compressor station discharge piping                    @ 255.00/hr
 3    Integrity Assessment Report & ECDA workup        1     lot        42,500.00
      (External Corrosion Direct Assessment)
 4    Crew Mobilization & Demobilization               2     events     14,800.00
      (Hobbs NM and Mont Belvieu TX)                         @ 7,400.00
 5    Hydrostatic Pressure Test Support,               14    days       80,080.00
      9.6-mile segment, MAOP requalification                 @ 5,720.00/day
--------------------------------------------------------------------------------
                                              Subtotal:      284,500.00
                                              TX State Tax (0.00% - resale):  0.00
                                              TOTAL DUE:    USD 284,500.00
================================================================================

Remarks: Per Section 4.2 of MSA-HAL-2024-03, all rates inclusive of standard
PPE, consumables, and per-diem. Report deliverables transmitted via secure
portal to integrity.engineering@eprod.com on 05/01/2026.

Questions: ar.midstream@halliburton.com  |  Ref: INV-HAL-2026-04-3847
================================================================================
`,

  eprod_inv_slb: `================================================================================
                            SCHLUMBERGER TECHNOLOGY CORPORATION
                                  5599 San Felipe St.
                                  Houston, TX 77056
                       Tax ID: 75-1004429   Phone: (713) 513-2000
================================================================================

INVOICE

Invoice No:        INV-SLB-2026-05-1129
Invoice Date:      05/14/2026
Service Period:    04/15/2026 - 05/12/2026
Customer PO:       PO-2026-CHEM-0892
Project:           NGL Flow Assurance Program - Mont Belvieu Hub
Terms:             Net 30
Due Date:          06/13/2026

Bill To:
    Enterprise Products Partners L.P.
    Accounts Payable Dept.
    1100 Louisiana Street, 10th Floor
    Houston, TX 77002

Remit To: Schlumberger - Lockbox 732149, Dallas TX 75373-2149
Wire: JPMorgan Chase, Acct ********4218, ABA 021000021

--------------------------------------------------------------------------------
LN   DESCRIPTION                                       QTY   UOM     AMOUNT
--------------------------------------------------------------------------------
 1   Corrosion Coupon Pull & Lab Analysis (LPR),       48    each      28,800.00
     14 monitoring stations, ethane-propane service          @ 600.00
 2   Flow Assurance Modeling - OLGA simulation,        220   hours     74,800.00
     Mont Belvieu - Sweeny corridor, multiphase             @ 340.00/hr
 3   Hydrate Inhibitor Field Trial (MEG),               1    lot      112,500.00
     2-week pilot, 18" Y-grade line MP-104 to MP-127
 4   Real-time Multiphase Flow Meter Calibration       12    units     43,200.00
     (Vx-Spectra), pump-station discharge                   @ 3,600.00
 5   Iron-Sulfide Solids Characterization,              1    project   38,000.00
     XRD + SEM analysis, 6 sample matrices
 6   Engineering Report & Mitigation Roadmap,           1    deliv.   115,000.00
     "Sweeny-MtBV Internal Corrosion Strategy 2026"
--------------------------------------------------------------------------------
                                              Subtotal:      412,300.00
                                              Tax (Resale Cert on file):  0.00
                                              TOTAL DUE:    USD 412,300.00
================================================================================

Notes: Deliverables uploaded to Enterprise SharePoint > Integrity > 2026 > Q2.
Field samples retained at SLB Sugar Land lab for 12 months per procedure
QA-MID-2415. Invoice covers all rates per agreed work scope dated 03/28/2026.

Inquiries: midstream-ar.houston@slb.com
================================================================================
`,

  eprod_inv_bhi: `================================================================================
                              BAKER HUGHES OILFIELD OPERATIONS LLC
                                17021 Aldine Westfield Rd
                                   Houston, TX 77073
                       Tax ID: 76-0207995   Phone: (713) 439-8600
================================================================================

INVOICE

Invoice #:         INV-BHI-2026-05-0921
Date Issued:       05/19/2026
Customer:          Enterprise Products Operating LLC
PO Number:         PO-2026-OPS-2189
Ship-To Site:      Sealy Compressor Station, Sealy TX 77474
Terms:             Net 30
Due Date:          06/18/2026

Bill To:
    Enterprise Products Operating LLC
    Attn: AP - Operations & Maintenance
    P.O. Box 4324
    Houston, TX 77210-4324

--------------------------------------------------------------------------------
LN  P/N / DESCRIPTION                              QTY   UNIT $   EXT $
--------------------------------------------------------------------------------
 1  Centrifugal Compressor Impeller, PCL-803,        2    18,400   36,800.00
    stage-2 replacement, P/N BH-IMP-803-S2
 2  Dry Gas Seal Cartridge Assembly (tandem),        4    11,250   45,000.00
    P/N BH-DGS-T22-7B, OEM rebuild
 3  Magnetic Bearing Sensor Kit, axial,              6     2,850   17,100.00
    P/N BH-MBS-AX-04
 4  Lube Oil Filter Element, 10-micron,             24       175    4,200.00
    P/N BH-LOF-10M-A
 5  Field Service Engineer - mechanical,            96       235   22,560.00
    onsite overhaul support, day rate hourly basis
 6  Vibration Analysis (Bently Nevada 3500),         1     8,400    8,400.00
    pre/post-overhaul baseline, full train
 7  Rotor Balance Service (offsite),                 2     6,800   13,600.00
    Houston Service Center, ISO 1940/1 G2.5
 8  Freight - Sealy TX, expedited,                   1     9,090    9,090.00
    HazClass non-regulated
--------------------------------------------------------------------------------
                                              Subtotal:      156,750.00
                                              TX Sales Tax (resale): 0.00
                                              TOTAL DUE:    USD 156,750.00
================================================================================

Warranty: 12 months on rebuilt components per Baker Hughes Standard Terms
(BHST-2024). All work documented in Service Report SR-26-0814 transmitted to
operations.sealy@eprod.com.

Remit: Baker Hughes - Dept CH 14068, Palatine IL 60055-4068
Ref invoice number on all payments.
================================================================================
`,

  eprod_inv_kiewit: `================================================================================
                                KIEWIT ENERGY GROUP INC.
                                  3555 Farnam Street
                                    Omaha, NE 68131
                       Tax ID: 47-0210877   Phone: (402) 346-8535
                            Project Office: Tulsa, OK 74119
================================================================================

PROGRESS INVOICE - PARTIAL PAYMENT

Invoice Number:    INV-KIEWIT-2026-05-0114
Application No:    No. 7 of estimated 11
Period Ending:     05/15/2026
Project:           Seminole Lateral - 12" Construction, MP 22.0 - MP 41.8
Project No:        EPD-LAT-2025-019
Owner PO:          PO-2026-EPC-4521
MSA Reference:     MSA-KIEWIT-2024-07
Terms:             Net 30 (per MSA Sec 8.1)
Due Date:          06/22/2026

Bill To:
    Enterprise Products Operating LLC
    c/o Project Controls - Pipeline Projects
    1100 Louisiana Street
    Houston, TX 77002

--------------------------------------------------------------------------------
LN  WORK DESCRIPTION                              QTY     UOM       AMOUNT
--------------------------------------------------------------------------------
 1  Clearing, Grading & ROW Restoration -         19.8    miles    495,000.00
    period work, MP 22.0 - 41.8 corridor              @ 25,000/mi
 2  Pipe Stringing, Bending, Welding & X-ray      19.8    miles    910,800.00
    (12" Gr X-65, .250 wall), AUT 100%                @ 46,000/mi
 3  Lowering-In, Tie-In Welds (14) & Backfill,    19.8    miles    324,500.00
    including padding and topsoil replacement         @ 16,388/mi
 4  Two HDD crossings (FM-1488, BNSF tracks),      2     each      116,900.00
    bore lengths 740 ft and 1,180 ft                  @ 58,450
--------------------------------------------------------------------------------
                                Subtotal Period Work:    1,847,200.00
                                Less Retainage 10%:       (184,720.00)
                                NET DUE THIS APPLICATION: 1,662,480.00

                                Contract Sum to Date:    18,420,000.00
                                Work Completed to Date:  14,820,500.00 (80.5%)
                                Less Prior Payments:    (12,973,300.00)
                                Less Current Retainage:  (1,482,050.00)
                                BALANCE DUE THIS INVOICE: 1,847,200.00 *

* Subject to AIA G702/G703 cert. Retainage release at substantial completion.
================================================================================

Submitted by: J. McAllister, Project Manager - Kiewit Energy Group
Approved by Owner Engineer: ____________  Date: __________

Remit: Kiewit Energy Group - Lockbox 3540, P.O. Box 3540, Omaha NE 68103
================================================================================
`,

  eprod_po_epc: `================================================================================
                          ENTERPRISE PRODUCTS OPERATING LLC
                              1100 Louisiana Street
                                Houston, TX 77002
                                  (713) 381-6500
================================================================================

                              PURCHASE ORDER

PO Number:         PO-2026-EPC-4521
PO Date:           04/22/2026
Buyer:             M. Reyes, Sr. Procurement Mgr - Major Projects
Cost Center:       MTBV-FRAC-IX
AFE Number:        AFE-MTBV-FRAC9-2026-01
Project:           Mont Belvieu Fractionator IX (NGL Fractionator #9)
MSA Reference:     MSA-KIEWIT-2024-07
Total NTE:         USD 14,200,000.00
Payment Terms:     Net 30, progress billing per Schedule of Values

Vendor:                                    Ship/Site:
    Kiewit Energy Group Inc.                   Enterprise Mont Belvieu Complex
    3555 Farnam Street                         9701 Hatcherville Rd
    Omaha, NE 68131                            Mont Belvieu, TX 77580
    Vendor ID: V-001827

--------------------------------------------------------------------------------
LN  SCOPE / DESCRIPTION                          UOM     QTY      AMOUNT (USD)
--------------------------------------------------------------------------------
 1  FEED Validation & Detailed Engineering -      LS     1.0     2,450,000.00
    Frac IX, 150 MBPD design capacity
 2  Procurement Services (long-lead equipment     LS     1.0     1,150,000.00
    expediting: deethanizer, depropanizer,
    debutanizer towers)
 3  Mechanical Construction - Towers, drums,      LS     1.0     6,800,000.00
    exchangers, piping, structural steel
 4  E&I Construction - cable tray, conduit,       LS     1.0     2,150,000.00
    instrumentation, MCC tie-ins
 5  Commissioning & Startup Support, 90-day       LS     1.0       950,000.00
    field engineering presence
 6  Site indirects, safety, QA/QC,                LS     1.0       700,000.00
    project management
--------------------------------------------------------------------------------
                                              TOTAL PO:       14,200,000.00
================================================================================

Conditions:
1. All work governed by MSA-KIEWIT-2024-07, Sections 1-22.
2. Schedule: NTP 05/01/2026; Mechanical Completion 03/15/2027.
3. Liquidated Damages: $25,000/day after MC target +30 days grace.
4. Performance Bond required: 50% of PO value, Surety A.M. Best A- minimum.
5. Owner-Furnished Equipment list per Attachment B (towers, BMS).
6. Safety compliance: OSHA 1910/1926, EPROD Contractor Safety Manual Rev 9.
7. Submittals via EPROD Aconex portal, project ID MTBV-FRAC9.

Authorized by:  ____________________   Date: ________
                M. Reyes - Buyer

Approved:       ____________________   Date: ________
                D. Patel - VP Major Projects

================================================================================
`,

  eprod_po_chem: `================================================================================
                          ENTERPRISE PRODUCTS OPERATING LLC
                              1100 Louisiana Street
                                Houston, TX 77002
================================================================================

                      BLANKET PURCHASE ORDER (12-MONTH)

PO Number:         PO-2026-CHEM-0892
PO Date:           04/30/2026
Effective Period:  05/01/2026 through 04/30/2027
Buyer:             L. Nguyen, Chemicals Category Mgr
Cost Center:       IC-PIPE-CORR-PROG
AFE Number:        AFE-CORR-2026-PROG
MSA Reference:     MSA-SLB-2023-09
Total Blanket NTE: USD 1,200,000.00 (cumulative draws)
Payment Terms:     Net 30 per invoice draw

Vendor:                                    Ship-To (multi-site):
    Schlumberger Technology Corp.              EPROD Field Sites per Release Schedule
    5599 San Felipe St.                        - Mont Belvieu, TX
    Houston, TX 77056                          - Sealy, TX
    Vendor ID: V-001284                        - Hobbs, NM
                                               - Conway, KS

--------------------------------------------------------------------------------
LN  DESCRIPTION                                   UOM    QTY     UNIT $    EXT
--------------------------------------------------------------------------------
 1  Corrosion Inhibitor - Filming Amine          gallon  72,000   8.20    590,400
    blend, NGL service, drum/tote delivery
 2  Hydrate Inhibitor - MEG (re-gen quality)     gallon  48,000   6.10    292,800
    bulk truck, multi-site
 3  Oxygen Scavenger - Bisulfite-based,          gallon  19,500   7.40    144,300
    aqueous service
 4  On-call Field Service - Chemical Application LS      1.0     172,500  172,500
    Engineer, periodic site visits & dosing
    optimization
--------------------------------------------------------------------------------
                                              BLANKET NTE:    USD 1,200,000.00
================================================================================

Release Mechanism: Site superintendents issue Release-Against-Blanket numbers
(RAB-NNNN) by email to vendor; vendor confirms delivery within 5 business days.
Pricing held firm for full term; force-majeure adjustments per MSA Sec 12.

Reporting: Monthly consumption report by site & line item due 5th of following
month, sent to chemicals.program@eprod.com.

Approved: L. Nguyen ___________   D. Cho (Director, Pipeline Ops) ___________
================================================================================
`,

  eprod_po_ops: `================================================================================
                          ENTERPRISE PRODUCTS OPERATING LLC
                              1100 Louisiana Street
                                Houston, TX 77002
================================================================================

                              PURCHASE ORDER

PO Number:         PO-2026-OPS-2189
PO Date:           05/04/2026
Requisitioned By:  T. Aguilar, Operations Manager - South Texas District
Buyer:             K. Whitfield, Procurement Specialist - O&M
Cost Center:       CS-SEALY-OPS
AFE Number:        AFE-CS-SEALY-OH-2026
Total NTE:         USD 487,000.00
Payment Terms:     Net 30
Required-By Date:  06/30/2026

Vendor:                                    Ship-To:
    Baker Hughes Oilfield Operations LLC       Sealy Compressor Station
    17021 Aldine Westfield Rd                  4488 FM 1458
    Houston, TX 77073                          Sealy, TX 77474
    Vendor ID: V-000914                        Site Contact: R. Ortiz (979) 555-0118

--------------------------------------------------------------------------------
LN  DESCRIPTION                                    QTY    UNIT $    AMOUNT
--------------------------------------------------------------------------------
 1  Centrifugal Compressor Overhaul - Unit C-2,     1      275,000   275,000.00
    PCL-803 train, full mechanical scope per
    Statement of Work SOW-OPS-2189
 2  Spare parts kit per BOM (impellers, seals,      1       86,500    86,500.00
    bearings, gaskets, fasteners)
 3  Field service - mechanical engineers (2),     480          175    84,000.00
    onsite during 21-day outage window, hours
 4  Rotor balance & metallurgical inspection        1       41,500    41,500.00
    (offsite, Houston Service Center)
--------------------------------------------------------------------------------
                                              TOTAL PO:       487,000.00
================================================================================

Special Conditions:
1. Outage window confirmed: 06/08/2026 - 06/28/2026. No deviation w/o owner
   written approval.
2. Vendor responsible for lockout/tagout compliance per EPROD HSE Standard 14.
3. Daily progress reports via email by 0700 to operations.sealy@eprod.com.
4. Spare parts to remain EPROD property; un-used returned for credit.
5. Warranty: 12 months from start-up on labor and OEM-rebuilt parts.

Approved:  T. Aguilar  ___________________   Date: ________
           K. Whitfield ___________________   Date: ________
================================================================================
`,

  eprod_msa_hal: `================================================================================
                       MASTER SERVICE AGREEMENT - MSA-HAL-2024-03
                             PIPELINE INTEGRITY SERVICES
================================================================================

This MASTER SERVICE AGREEMENT ("Agreement") is entered into effective March 18,
2024 (the "Effective Date") by and between:

    ENTERPRISE PRODUCTS OPERATING LLC, a Texas limited liability company with
    offices at 1100 Louisiana Street, Houston, TX 77002 ("Company"); and

    HALLIBURTON ENERGY SERVICES, INC., a Delaware corporation with offices at
    3000 N. Sam Houston Parkway East, Houston, TX 77032 ("Contractor").

Company and Contractor each a "Party" and collectively the "Parties".

RECITALS

WHEREAS Company owns and operates interstate and intrastate liquid and gas
pipelines including NGL, crude, and natural gas systems across Texas, New
Mexico, Oklahoma, Louisiana, and other states; and

WHEREAS Contractor is engaged in providing pipeline integrity, inspection,
non-destructive testing, and related engineering services; and

WHEREAS the Parties desire to establish the terms and conditions under which
Contractor will perform such services from time to time on a call-off basis;

NOW THEREFORE, the Parties agree as follows.

--------------------------------------------------------------------------------
SECTION 1 - TERM
--------------------------------------------------------------------------------
1.1 Initial Term: three (3) years from the Effective Date, expiring March 17,
    2027.
1.2 Renewal: two (2) successive one-year renewal periods at Company's sole
    option exercised by written notice 60 days prior to expiration.
1.3 Termination for Convenience: either Party may terminate on 60 days written
    notice; pending Releases continue to completion.

--------------------------------------------------------------------------------
SECTION 2 - SCOPE OF SERVICES
--------------------------------------------------------------------------------
Services may include but are not limited to:
    (a) Inline Inspection (ILI) - MFL, UT, geometry, caliper, IMU
    (b) Hydrostatic pressure testing per 49 CFR 195 and 192
    (c) Non-Destructive Testing - UT, MT, PT, RT, AUT
    (d) External & Internal Corrosion Direct Assessment (ECDA / ICDA)
    (e) Integrity assessments, dig reports, fitness-for-service evaluations
    (f) Cathodic protection surveys (CIS, DCVG, ACVG)
    (g) Engineering deliverables consistent with API 1163, NACE SP-0102,
        ASME B31.4 / B31.8

--------------------------------------------------------------------------------
SECTION 3 - RATE SCHEDULE (EXHIBIT A SUMMARY)
--------------------------------------------------------------------------------
ILI Services (per mile, includes mobilization on jobs >50 mi):
    8-inch to 12-inch MFL High-Resolution           $   780.00 / mile
    16-inch to 24-inch MFL High-Resolution          $   870.00 / mile
    30-inch to 36-inch MFL High-Resolution          $ 1,020.00 / mile
    Geometry / IMU combo tool (any diameter)        $   340.00 / mile
    UT Wall-Thickness Tool                          $ 1,150.00 / mile

Personnel (straight-time hourly, OT 1.5x, DT 2x):
    NDT Level II Technician                         $   165.00 / hr
    NDT Level III Technician                        $   235.00 / hr
    Integrity Engineer                              $   245.00 / hr
    Sr. Integrity Engineer / Project Lead           $   295.00 / hr
    Crew Foreman                                    $   195.00 / hr

Lump-Sum Deliverables:
    Standard Integrity Assessment Report            $ 42,500.00 / segment
    ECDA Workup (4-step process complete)           $ 38,000.00 / segment
    Fitness-for-Service Calc (API 579 Level 2)      $ 22,500.00 / location

Mobilization / Demobilization: $7,400 per crew per event (waived if continuous
work exceeds 14 days on a single segment).

Rates fixed for first 24 months; CPI-U adjustment thereafter, capped at 4%/yr.

--------------------------------------------------------------------------------
SECTION 4 - PAYMENT TERMS
--------------------------------------------------------------------------------
4.1 Invoicing: monthly, with detailed timesheets and material backup.
4.2 Payment: Net 45 days from receipt of correct invoice.
4.3 Disputed amounts: paid portion not in dispute due on regular schedule;
    disputed portion resolved within 30 days.

--------------------------------------------------------------------------------
SECTION 5 - INSURANCE
--------------------------------------------------------------------------------
Contractor shall maintain Worker's Comp (statutory), Employer's Liability ($1M),
Commercial General Liability ($5M occurrence / $10M aggregate), Auto Liability
($5M), Pollution Legal Liability ($10M), Umbrella ($25M). Company named as
additional insured (except WC). Waivers of subrogation reciprocal.

--------------------------------------------------------------------------------
SECTION 6 - INDEMNITY AND LIABILITY
--------------------------------------------------------------------------------
Knock-for-knock indemnity per Texas Oilfield Anti-Indemnity Act. Each Party
indemnifies the other for its own personnel and property regardless of fault,
to fullest extent permitted by Tex. Civ. Prac. & Rem. Code Ch. 127.

--------------------------------------------------------------------------------
SECTION 7 - SAFETY, COMPLIANCE, AUDIT
--------------------------------------------------------------------------------
Contractor complies with EPROD Contractor Safety Manual Rev 9, OSHA 1910/1926,
49 CFR Parts 192/195, and all applicable PHMSA regulations. Company audit
rights with 10 business days notice.

--------------------------------------------------------------------------------
SECTION 8 - GOVERNING LAW / DISPUTE RESOLUTION
--------------------------------------------------------------------------------
Texas law. Disputes resolved per AAA Commercial Arbitration Rules in Harris
County, TX. Senior-executive negotiation precedent (30 days).

IN WITNESS WHEREOF the Parties have executed this Agreement as of the Effective
Date.

ENTERPRISE PRODUCTS OPERATING LLC          HALLIBURTON ENERGY SERVICES, INC.
By: ___________________________            By: ___________________________
Name: D. Patel                             Name: S. Bhattacharya
Title: VP - Engineering & Construction     Title: VP - North America Pipeline
================================================================================
`,

  eprod_msa_kiewit: `================================================================================
                  MASTER CONSTRUCTION AGREEMENT - MSA-KIEWIT-2024-07
                       PIPELINE CONSTRUCTION & HOT-TAP SERVICES
================================================================================

This MASTER CONSTRUCTION AGREEMENT ("Agreement") is entered into and effective
as of July 1, 2024 (the "Effective Date") between:

    ENTERPRISE PRODUCTS OPERATING LLC ("Company")
    1100 Louisiana Street, Houston, Texas 77002

    KIEWIT ENERGY GROUP INC. ("Contractor")
    3555 Farnam Street, Omaha, Nebraska 68131

The Parties agree as follows.

--------------------------------------------------------------------------------
ARTICLE 1 - TERM
--------------------------------------------------------------------------------
Initial Term: five (5) years from the Effective Date, expiring June 30, 2029.
Optional one-year extensions (up to two) at Company's election with 90-day
written notice.

--------------------------------------------------------------------------------
ARTICLE 2 - SCOPE OF WORK
--------------------------------------------------------------------------------
Contractor may, pursuant to individual Work Releases or Purchase Orders, perform
any of the following on EPROD's NGL, crude, refined products, and natural gas
systems:
    a) Cross-country pipeline construction (4" through 42" diameter)
    b) Hot-tap and stopple services on live pipelines
    c) Station-yard piping, manifold builds, pig launcher/receiver installs
    d) Horizontal directional drilling (HDD), bore crossings, river crossings
    e) Tie-ins, valve replacements, pig launcher modifications
    f) Hydrostatic testing support, dewatering, drying, commissioning
    g) Emergency response and repair construction services

All work performed in accordance with ASME B31.4 / B31.8, API 1104, applicable
PHMSA regulations 49 CFR 192/195, and EPROD Engineering Standards Manual.

--------------------------------------------------------------------------------
ARTICLE 3 - PRICING STRUCTURE
--------------------------------------------------------------------------------

3.1 LUMP-SUM PROJECT RATES (Mainline construction, indicative)

    Diameter / Wall                Per-Mile Lump Sum (open ROW, normal terrain)
    -----------------------       -------------------------------------------
    8"  Gr X-52,  .188" wall      $   1,180,000 / mile
    12" Gr X-65,  .250" wall      $   1,580,000 / mile
    16" Gr X-65,  .312" wall      $   2,020,000 / mile
    20" Gr X-65,  .344" wall      $   2,480,000 / mile
    24" Gr X-70,  .375" wall      $   2,950,000 / mile
    30" Gr X-70,  .438" wall      $   3,720,000 / mile

Lump sums include clearing, grading, stringing, bending, welding (100% AUT),
coating, lowering-in, backfill, ROW restoration, and standard tie-ins. Subject
to adjustment for terrain class (rock, wetland, urban), bore crossings, and
fuel/escalation indices per Exhibit C.

3.2 HOT-TAP SERVICES (lump-sum per tap)
    Up to 6"  on 12"  or smaller carrier         $  78,000
    8"-12"   on 16"-24" carrier                  $ 142,000
    16"      on 30"-36" carrier                  $ 218,000
    24"      on 36"-42" carrier                  $ 365,000
    Stopple isolation premium (per stopple)      $ 195,000

3.3 MULTI-TIER HOURLY RATES (T&M work releases)

    Labor Class             ST $/hr   OT $/hr   DT $/hr
    --------------------    -------   -------   -------
    Laborer                  68.50    102.75    137.00
    Operator (light eqpt)    92.00    138.00    184.00
    Operator (heavy eqpt)   118.50    177.75    237.00
    Welder (CWB-cert)       142.00    213.00    284.00
    Welder Helper            85.00    127.50    170.00
    Pipefitter              128.00    192.00    256.00
    Foreman                 155.00    232.50    310.00
    Superintendent          198.00    297.00    396.00
    Project Manager         245.00    367.50    490.00

Equipment rates per Exhibit D (Blue Book + 18%). Per-diem $185/day where
applicable.

--------------------------------------------------------------------------------
ARTICLE 4 - SCHEDULE AND LIQUIDATED DAMAGES
--------------------------------------------------------------------------------
Schedule set in each Work Release. Liquidated Damages: $25,000/day after agreed
Mechanical Completion +30 days grace, capped at 5% of Work Release value.

--------------------------------------------------------------------------------
ARTICLE 5 - PERFORMANCE & PAYMENT BONDS
--------------------------------------------------------------------------------
For Work Releases exceeding $5,000,000, Contractor provides Performance and
Payment Bonds at 50% and 50% of contract value respectively, surety A.M. Best
A- or better.

--------------------------------------------------------------------------------
ARTICLE 6 - INSURANCE
--------------------------------------------------------------------------------
Same minima as MSA-HAL-2024-03 Section 5, plus Builders Risk for active
construction projects ($10M project value minimum).

--------------------------------------------------------------------------------
ARTICLE 7 - INVOICING / PAYMENT
--------------------------------------------------------------------------------
Progress billing via AIA G702/G703 forms, monthly. Retainage: 10%, released at
Substantial Completion (50%) and Final Acceptance (balance). Net 30 from
receipt of corrected invoice.

--------------------------------------------------------------------------------
ARTICLE 8 - SAFETY
--------------------------------------------------------------------------------
Contractor's TRIR must remain at or below 1.0 trailing 12-month basis to
maintain MSA in good standing.

--------------------------------------------------------------------------------
ARTICLE 9 - INDEMNITY / GOVERNING LAW
--------------------------------------------------------------------------------
Knock-for-knock; Texas law; arbitration AAA Construction Industry Rules,
Harris County, TX.

Signed:
    Company: D. Patel, VP E&C            Contractor: J. McAllister, EVP Energy
    _____________________________        ______________________________
    Date: ____________                   Date: ____________
================================================================================
`,

  eprod_quote_fluor: `================================================================================
                              FLUOR ENTERPRISES, INC.
                                  6700 Las Colinas Blvd.
                                  Irving, TX 75039-2900
                                    (469) 398-7000
================================================================================

                              ENGINEERING QUOTATION

Quote Number:         QUOTE-FLUOR-2026-Q2-0142
Date Issued:          05/06/2026
Validity:             90 days from issue (expires 08/04/2026)
Subject:              Feasibility Study - Permian-to-Mont Belvieu
                      NGL Pipeline Lateral, 280 miles, 16" diameter
Prepared For:         Enterprise Products Operating LLC
                      Attn: M. Reyes, Sr. Procurement Manager
                      1100 Louisiana Street, Houston TX 77002

Reference RFP:        RFP-EPD-FEAS-2026-007
Fluor Project No:     14-8821-FEAS

--------------------------------------------------------------------------------
EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Fluor proposes to perform a Class 4 (AACE) feasibility study for a new 280-mile
16" Y-grade NGL lateral originating at Enterprise's Midland gathering complex
(Midland County, TX) and terminating at the Mont Belvieu fractionation hub
(Chambers County, TX). Design throughput: 230,000 BPD at 1,440 psig MAOP.
The study will deliver routing alternatives, cost estimate (-30%/+50%),
permitting strategy, and execution roadmap to support EPROD's FID decision.

--------------------------------------------------------------------------------
SCOPE OF WORK
--------------------------------------------------------------------------------
Phase A - Routing & Constructability (10 weeks)
  - Three corridor alternatives w/ GIS modeling
  - Land-cover, wetlands, T&E species screen
  - Stakeholder/landowner density analysis
  - Constructability ranking & preferred route

Phase B - Process & Hydraulics (8 weeks)
  - Steady-state and transient hydraulic models
  - Pump station siting (preliminary, 3 locations)
  - MAOP class analysis, surge study
  - Pig launcher/receiver siting

Phase C - Permitting Strategy (6 weeks, in parallel with B)
  - Federal: USACE 404, FERC jurisdictional review
  - State: TCEQ, RRC, GLO crossings
  - County and municipal permits inventory
  - Tribal/cultural resource preliminary survey

Phase D - Cost & Schedule (8 weeks)
  - AACE Class 4 estimate (-30%/+50%)
  - Level-3 schedule, FID through ISD
  - Risk register and Monte Carlo schedule risk

Phase E - Final Report & FID Package (4 weeks)
  - Integrated feasibility report
  - Board-quality executive presentation
  - Recommended path-forward & next-phase scope

--------------------------------------------------------------------------------
DELIVERABLES
--------------------------------------------------------------------------------
D-1   Routing Alternatives Report w/ GIS shapefiles      Wk 10
D-2   Preliminary P&IDs and Hydraulic Model Workbook     Wk 18
D-3   Permitting Strategy Memorandum                     Wk 16
D-4   Class 4 Cost Estimate & Basis-of-Estimate          Wk 26
D-5   Level-3 Project Schedule (Primavera P6 .xer)       Wk 26
D-6   Final Integrated Feasibility Report (PDF + .docx)  Wk 30
D-7   FID-quality executive presentation deck            Wk 30

--------------------------------------------------------------------------------
COMMERCIAL TERMS
--------------------------------------------------------------------------------
Total Fixed Price:    USD 3,400,000.00 (Three Million Four Hundred Thousand)

Payment Milestones:
    M-1  Contract execution / NTP                      15%   $   510,000
    M-2  Phase A complete (Wk 10)                      20%   $   680,000
    M-3  Phases B/C complete (Wk 18)                   25%   $   850,000
    M-4  Phase D complete (Wk 26)                      25%   $   850,000
    M-5  Final report acceptance (Wk 30)               15%   $   510,000

Payment Terms:        Net 30 from invoice receipt.
Currency:             USD; price firm through validity period.
Exclusions:           Field survey (Lidar, civil), geotechnical borings,
                      detailed environmental field studies (Phase 2),
                      easement acquisition. Available as separate quote.

Assumptions:
  - EPROD provides all available existing GIS data, prior route studies,
    landowner records, and operating data within 10 business days of NTP.
  - Two in-person workshops in Houston (Fluor travel included).
  - Up to two estimate revisions included; further revisions T&M per
    Exhibit A rate schedule.

--------------------------------------------------------------------------------
PROPOSED PROJECT TEAM
--------------------------------------------------------------------------------
Project Director:     A. Krishnamurthy, P.E. (28 years midstream)
Lead Process Engr:    M. Tellez, P.E.
Lead Pipeline Engr:   R. Vidrine, P.E.
Permitting Lead:      C. Yamamoto

--------------------------------------------------------------------------------
ACCEPTANCE
--------------------------------------------------------------------------------
This quotation may be accepted by signature below or by issuance of a Purchase
Order referencing QUOTE-FLUOR-2026-Q2-0142.

For Fluor Enterprises Inc.:                For Enterprise Products:
By: ___________________________            By: ___________________________
A. Krishnamurthy                           Date: ____________
Project Director
================================================================================
`,

  eprod_quote_bechtel: `================================================================================
                              BECHTEL ENERGY INC.
                                 3000 Post Oak Blvd.
                                  Houston, TX 77056
                                    (713) 235-2000
================================================================================

                              ENGINEERING QUOTATION

Quote Number:         QUOTE-BECHTEL-2026-Q1-0089
Date Issued:          02/27/2026
Validity:             120 days (expires 06/27/2026)
Subject:              Sweeny Fractionation Complex - Expansion Engineering
                      Frac VIII through Frac X, debottleneck of common
                      utilities and inbound NGL header
Prepared For:         Enterprise Products Operating LLC
                      Attn: D. Patel, VP Engineering & Construction
Bechtel Project No:   26-04421-EXP
Reference RFP:        RFP-EPD-SWEENY-EXP-2026-001

--------------------------------------------------------------------------------
PROJECT BACKGROUND
--------------------------------------------------------------------------------
Enterprise's Sweeny fractionation complex (Brazoria County, TX) currently
operates seven NGL fractionators with combined nameplate ~756 MBPD. EPROD
intends to add Frac VIII (150 MBPD), Frac IX (150 MBPD - design parallel), and
prepare for Frac X. Common-system debottlenecks (inbound 24" Y-grade header,
cooling water, flare, MCC capacity, and product header out to Mont Belvieu
storage) are also in scope.

--------------------------------------------------------------------------------
SCOPE OF SERVICES (Multi-Phase)
--------------------------------------------------------------------------------

PHASE 1 - FEED VALIDATION & GAP ANALYSIS (16 weeks)
  - Review existing FEED packages (Frac VIII completed by others)
  - Heat & material balance reconciliation
  - Tie-in study on common header, utilities, flare
  - Class 3 estimate refresh (-15%/+25%)
  - Risk register and execution-strategy options
  Estimated cost:  USD 1,650,000

PHASE 2 - DETAILED ENGINEERING FRAC IX (52 weeks)
  - Process, mechanical, civil/structural, E&I, piping
  - 3D model (Smart Plant 3D), IFC drawings
  - Equipment specifications, MR packages
  - Procurement support and bid-package issuance
  - Constructability reviews, model reviews (30/60/90)
  Estimated cost:  USD 4,950,000

PHASE 3 - COMMON-SYSTEMS DEBOTTLENECK ENGR (28 weeks, parallel)
  - 24" inbound header hydraulic upgrade study
  - Cooling tower expansion (one new cell)
  - Flare load study and tip replacement design
  - MCC and substation expansion (138/13.8 kV)
  - Detailed engineering and IFC drawings
  Estimated cost:  USD 1,750,000

PHASE 4 - CONSTRUCTION SUPPORT (24 weeks, on call)
  - RFI response, field engineering, redlines
  - Vendor data review for owner-furnished equipment
  - Pre-commissioning and startup engineering support
  Estimated cost:  USD   350,000

                                              TOTAL PROPOSAL: USD 8,700,000.00

--------------------------------------------------------------------------------
SCHEDULE (PRELIMINARY)
--------------------------------------------------------------------------------
NTP target:                 Q3 2026
Phase 1 complete:           Q4 2026
Phase 2 IFC issuance:       Q4 2027 (rolling release Q2-Q4 2027)
Phase 3 IFC issuance:       Q3 2027
Frac IX mech complete:      Q4 2028 (under separate construction contract)

--------------------------------------------------------------------------------
COMMERCIAL TERMS
--------------------------------------------------------------------------------
Pricing structure:    Phase 1 - Lump Sum
                      Phases 2 & 3 - Reimbursable with not-to-exceed (NTE)
                      Phase 4 - T&M per Exhibit A
Payment terms:        Net 30 from invoice receipt
Invoicing:            Monthly, with detailed labor and ODC backup
Currency:             USD, firm through validity period
Travel:               Included in lump sums; reimbursable at cost +0% in
                      Phases 2 - 4 (capped at $250K/yr)

--------------------------------------------------------------------------------
KEY ASSUMPTIONS
--------------------------------------------------------------------------------
  - Frac IX duplicates Frac VIII design with minor delta engineering only.
  - Owner-furnished equipment list per Attachment C; vendor data made
    available to Bechtel no later than 60 days post-NTP for long-leads.
  - Workshare: 60% Houston, 25% Mumbai/Bechtel India, 15% New Delhi.
  - Engineering tools: Smart Plant suite, Aspen HYSYS, AutoPIPE.
  - EPROD provides existing site survey, process licensor docs (Honeywell
    UOP), and operating data history.

--------------------------------------------------------------------------------
EXCLUSIONS
--------------------------------------------------------------------------------
  - Field surveys, geotechnical investigations
  - Permitting / regulatory submissions (TCEQ, USACE)
  - Process licensor fees
  - Construction labor, materials, or subcontracts
  - Owner-furnished equipment costs

--------------------------------------------------------------------------------
ACCEPTANCE
--------------------------------------------------------------------------------
Acceptance by signed return of this quotation or issuance of Purchase Order
referencing QUOTE-BECHTEL-2026-Q1-0089.

Bechtel Energy Inc.                       Enterprise Products Operating LLC
By: ____________________                  By: ____________________
P. Andersson                              Date: ___________
SVP - Energy Business Line
================================================================================
`,

  eprod_tariff_ngl: `================================================================================
                    FEDERAL ENERGY REGULATORY COMMISSION
                          F.E.R.C. NO. 47.12.0
                  Cancels F.E.R.C. NO. 47.11.0 (Original Sheet)

                       ENTERPRISE NGL PIPELINE LP
                  LOCAL AND JOINT PIPELINE TARIFF
                  APPLYING TO THE TRANSPORTATION OF
            NATURAL GAS LIQUIDS (Y-GRADE, PURITY PRODUCTS)
================================================================================

Issued by:            J.A. Teague
                      Senior Vice President, Commercial - NGL Pipelines
                      Enterprise Products Operating LLC, General Partner
                      1100 Louisiana Street, Houston, Texas 77002

Issued:               April 1, 2026
Effective Date:       May 1, 2026
Cancels:              Original Sheet No. 47.11.0 issued February 12, 2026

                              SUMMARY OF CHANGES

This filing implements:
    (i)   Revised distance-based rates per the 2026 FERC Oil Pipeline Index
          (PPI-FG + 0.78%), effective May 1, 2026.
    (ii)  Establishment of a new Term-Shipper category T-1B for 7-year
          commitments at or above 25,000 BPD.
    (iii) Increase in the Fuel & Loss Adjustment Rider (Item 90) from 0.45% to
          0.52% reflecting prior-period reconciliation per Section 9.
    (iv)  Addition of two new receipt points (Loving County RP-148, Reeves
          County RP-149) on Permian gathering interconnect.

================================================================================
ITEM 10 - APPLICATION OF TARIFF
================================================================================

This tariff applies to the transportation of any liquid hydrocarbon mixture
meeting Item 25 Quality Specifications, accepted at any Receipt Point listed
in Item 30 of this tariff and delivered at any Delivery Point listed in
Item 40, subject to the General Rules and Regulations of this Tariff and
49 CFR 195 as applicable.

================================================================================
ITEM 25 - QUALITY SPECIFICATIONS (Y-GRADE)
================================================================================

Methane (C1):                       0.5% mol max
Carbon Dioxide:                     200 ppm max
Hydrogen Sulfide:                   1.0 ppmw max
Total Sulfur:                       30 ppmw max
Water:                              1.0 ppmw max (free water none)
RVP (composite):                    400 psig max
Olefins:                            1.0% mol max
Color (Saybolt):                    +25 minimum

================================================================================
ITEM 50 - TRANSPORTATION RATES (DISTANCE-BASED)
================================================================================

Rates expressed in U.S. Dollars per Barrel per 100 Miles of pipeline
transportation, computed on the shortest practical pipeline route between
Receipt Point and Delivery Point.

Shipper-Category Rate Schedule:

    Category    Description                              Rate ($/bbl/100mi)
    --------    ---------------------------------------  ------------------
    T-1A        7-year Term-Shipper, MVC >= 50,000 BPD   $ 0.4280
    T-1B        7-year Term-Shipper, MVC >= 25,000 BPD   $ 0.4720  *NEW*
    T-2         5-year Term-Shipper, MVC >= 15,000 BPD   $ 0.5180
    T-3         3-year Term-Shipper, MVC >=  7,500 BPD   $ 0.5640
    W-1         Walk-Up Shipper (no MVC)                 $ 0.6920
    P-1         Priority Walk-Up (peak-demand premium)   $ 0.7950
    IA-1        Inter-Affiliate Service                  $ 0.4280
    EX-1        Existing-Contract Grandfather            $ 0.4040

Minimum Volume Commitments (MVC):
   T-1A: 50,000 BPD nominated monthly; deficiency payment 100% of rate
         applied to under-shipped volumes (make-up rights 12 months).
   T-1B: 25,000 BPD; deficiency 100% of rate; make-up rights 9 months.
   T-2:  15,000 BPD; deficiency 100% of rate; make-up rights 6 months.
   T-3:   7,500 BPD; deficiency 100% of rate; make-up rights 3 months.

Minimum Tender:                     1,000 bbl per nomination cycle
Maximum Tender:                     No limit, subject to capacity allocation
Nomination Window:                  25th of month preceding flow month
Pro-rationing:                      Per Item 80 General Rules

================================================================================
ITEM 90 - FUEL & LOSS ADJUSTMENT RIDER
================================================================================

Pipeline retains in-kind, as a fuel and losses allowance, the following
percentage of all volumes received:

    Effective May 1, 2026:          0.52% (zero point five two percent)
    Prior rate (cancelled):         0.45%

The Adjustment Rider is reconciled annually no later than April 30 of the
following year against actual line-fill, fuel consumption, vapor losses, and
LACT-measurement variance. Over- or under-collections roll into the
subsequent year's Rider per the methodology in Appendix C.

================================================================================
ITEM 95 - QUALITY BANK / VARIANCE ADJUSTMENTS
================================================================================

Per Appendix B, a quality bank operates on a monthly basis adjusting each
shipper for composition variance from the common-stream specification.
Component-level pricing references prior-month Mont Belvieu OPIS postings.

================================================================================
ITEM 100 - INCIDENTAL CHARGES
================================================================================

Loading / unloading at Originating Truck Stations    $  0.085 / bbl
Storage in tankage, days 1-5 (per shipment)          waived
Storage in tankage, days 6+ (per shipment)           $  0.020 / bbl-day
Special meter proving (per event)                    $  4,500 / event

================================================================================
ITEM 200 - SAFETY, COMPLIANCE, AND CHANGE OF SERVICE
================================================================================

Carrier reserves the right to refuse transportation of any product not
conforming to specifications. All transportation is subject to the General
Rules and Regulations of this Tariff, 49 CFR Part 195, and applicable
Commission regulations.

                                  -- END OF TARIFF F.E.R.C. NO. 47.12.0 --
================================================================================
`,

  eprod_tariff_crude: `================================================================================
                    FEDERAL ENERGY REGULATORY COMMISSION
                          F.E.R.C. NO. 26.4.0
                  Cancels F.E.R.C. NO. 26.3.0 (Original Sheet)

                     ENTERPRISE CRUDE PIPELINE LLC
                  JOINT LOCAL AND PROPORTIONAL TARIFF
                APPLYING TO THE TRANSPORTATION OF
                    CRUDE PETROLEUM (TEXAS SYSTEM)
================================================================================

Issued by:            M.J. Friedl
                      Vice President, Commercial - Crude Pipelines
                      Enterprise Products Operating LLC, Operator
                      1100 Louisiana Street, Houston, Texas 77002

Issued:               March 1, 2026
Effective Date:       April 1, 2026
Cancels:              Original Sheet No. 26.3.0 issued November 15, 2025

                              SUMMARY OF CHANGES

(i)   Rate adjustment in accordance with FERC Oil Pipeline Index (PPI-FG +
      0.78%), effective April 1, 2026.
(ii)  Addition of Reeves County Receipt Point RC-021 (Pecos River Terminal).
(iii) Quality bank revisions reflecting updated WTI-Midland and DSW
      specifications per Item 60.
(iv)  Establishment of a new Cushing-Terminus Sub-Path with separate Common
      Stream A and Common Stream B handling.

================================================================================
ITEM 10 - APPLICATION OF TARIFF
================================================================================

This tariff applies to the through transportation of crude petroleum
originating at any Receipt Point identified herein for delivery to any
Delivery Point in this Tariff, subject to the General Rules and Regulations,
49 CFR Part 195, and Commission orders.

================================================================================
ITEM 50 - TRANSPORTATION RATES (ORIGIN / DESTINATION PAIRS)
================================================================================

Rates in U.S. Dollars per Barrel, for transportation from indicated Origin to
indicated Destination, subject to Item 60 Quality and Item 80 Pro-rationing
provisions.

PRINCIPAL ORIGINS:
    MID  - Midland Basin Aggregation Pt (Midland Co., TX)
    RC   - Reeves County Receipt Pt RC-021 (Pecos River) *NEW*
    LOV  - Loving County Receipt Pt LOV-04
    GLA  - Glasscock County Receipt Pt GLA-12
    RVR  - Sealy Receiving Stn (Austin Co., TX)

PRINCIPAL DESTINATIONS:
    ECHO - ECHO Terminal, Houston (Harris County, TX)
    GEN  - Genoa Junction (Galveston County, TX)
    SEA  - Sea Robin Terminal (Beaumont, TX)
    CUSH - Cushing, OK (Joint movement via interconnect, see Item 70)

                       Common Stream A (WTI-Midland)
                  -------------------------------------
                  ECHO       GEN        SEA        CUSH
                  ------     ------     ------     ------
    MID    -->    $1.92      $2.04      $2.36      $3.18
    LOV    -->    $2.18      $2.30      $2.62      $3.42
    GLA    -->    $1.84      $1.96      $2.28      $3.10
    RC     -->    $2.42      $2.54      $2.86      $3.66

                       Common Stream B (DSW / Mixed Sweet)
                  -------------------------------------
                  ECHO       GEN        SEA        CUSH
                  ------     ------     ------     ------
    MID    -->    $2.05      $2.18      $2.50      $3.28
    LOV    -->    $2.32      $2.45      $2.77      $3.55

Local injections at RVR Sealy Station: $0.65/bbl flat charge to any
Destination on this Tariff.

================================================================================
ITEM 60 - QUALITY BANK RULES (COMMON-STREAM ADJUSTMENTS)
================================================================================

Common Stream A (WTI-Midland nominal specifications):
    API Gravity:           40.0 deg minimum, 44.0 deg target
    Sulfur:                0.42% mass max
    RVP:                   9.5 psi max
    Pour Point:            -10 deg F max
    BS&W:                  0.5% vol max

Common Stream B (Domestic Sweet "DSW" nominal):
    API Gravity:           38.0 - 42.0 deg
    Sulfur:                0.45% mass max
    RVP:                   9.5 psi max

Quality Bank methodology: Each shipper's monthly receipts are debited or
credited to the common pool based on weighted component value (light ends,
naphtha, middle distillate, gas oil, residuum). Component values referenced
to prior-month Argus / OPIS postings per Appendix B.

Pipeline reserves right to segregate ("batch") any tender exceeding 50,000
bbl that materially exceeds specifications; batch fee $0.18/bbl applies.

================================================================================
ITEM 70 - JOINT MOVEMENTS / INTERCONNECT RATES
================================================================================

Through-rates to Cushing OK include interconnect charges with Plains Pipeline
Basin System; allocation of through-rate per Joint Movement Agreement dated
01/15/2024. Shipper need only nominate at originating EPROD point; downstream
nomination handled by Carrier.

================================================================================
ITEM 80 - PRO-RATIONING
================================================================================

If nominations exceed available capacity at any segment, capacity is
allocated:
    Step 1:   Contract / Term Shipper minimum commitments honored in full
    Step 2:   Remaining capacity allocated pro-rata to non-Term nominations
              based on 12-month rolling historical shipments
    Step 3:   New shippers without history receive minimum 5% of remaining
              capacity at Carrier's discretion

================================================================================
ITEM 90 - LOSS ALLOWANCE
================================================================================

Carrier retains in-kind 0.25% of all volumes received as common loss
allowance, applied per Appendix C.

================================================================================
ITEM 200 - GENERAL
================================================================================

All transportation subject to General Rules and Regulations of this Tariff
and FERC Form 6 reporting. Carrier reserves the right to refuse, segregate,
or batch any tender not meeting Item 60 specifications.

                              -- END OF TARIFF F.E.R.C. NO. 26.4.0 --
================================================================================
`,

  eprod_jib_p66: `================================================================================
                          PHILLIPS 66 COMPANY
                          (Operator - Sweeny Fractionator JV)
                          2331 CityWest Blvd, Houston TX 77042
                          Tax ID: 43-1054019
================================================================================

                    JOINT INTEREST BILLING STATEMENT (JIB)

JIB Statement No:        JIB-PHILLIPS66-SWEENY-2026-04
Billing Month:           April 2026
Issue Date:              May 15, 2026
Property:                Sweeny Fractionator Joint Venture
Property Code:           SWNY-FRAC-JV
Operating Agreement:     JOA dated October 1, 2014, as amended
Non-Operator Billed:     Enterprise Products Operating LLC
Non-Operator Code:       NON-OP-EPD-014
Payment Terms:           Net 15 days from receipt (per JOA Section 7.4)
Due Date:                May 30, 2026

Working Interest Schedule:
    Operator (Phillips 66)                            50.0000%
    Non-Operator (EPROD)                              50.0000%

References - Authorizations For Expenditure (AFE):
    AFE-SWEENY-2024-12   Frac VIII Construction (capital)       Active
    AFE-SWEENY-2025-06   Common-stream debottleneck (capital)   Active
    AFE-SWEENY-OPS-2026  2026 Operating Budget (rolling)        Active

================================================================================
SECTION A - CAPITAL EXPENDITURES (BILLED 50% TO NON-OPERATOR)
================================================================================

Line  AFE                  Description                       Gross     EPROD 50%
----  -------------------  --------------------------------- ---------- ---------
 1    AFE-SWEENY-2024-12   Mechanical equipment - tower      482,400.00 241,200.00
                           internals, Frac VIII deethanizer
 2    AFE-SWEENY-2024-12   Piping & pipe supports (April     318,750.00 159,375.00
                           progress, contractor: Zachry)
 3    AFE-SWEENY-2024-12   Instrumentation & controls -      164,200.00  82,100.00
                           DCS configuration & FATs
 4    AFE-SWEENY-2025-06   24" inbound header replacement,   612,500.00 306,250.00
                           welding & X-ray (Kiewit)
 5    AFE-SWEENY-2025-06   Cooling tower expansion cell,     288,000.00 144,000.00
                           structural & mech (S&B)
 6    AFE-SWEENY-2025-06   E&I tie-ins for new cell           96,400.00  48,200.00

                                  Section A Subtotal:      1,962,250.00 981,125.00

================================================================================
SECTION B - OPERATING EXPENDITURES (BILLED 50% TO NON-OPERATOR)
================================================================================

Line  Account              Description                       Gross     EPROD 50%
----  -------------------  --------------------------------- ---------- ---------
 7    OP-7100              Operations labor (24 FTE-mo)       428,500.00 214,250.00
 8    OP-7200              Maintenance labor & contract M&I   216,300.00 108,150.00
 9    OP-7310              Power purchased (electricity,      485,200.00 242,600.00
                           19,408 MWh @ blended $25/MWh)
10    OP-7320              Natural gas fuel (12,400 MMBtu)     38,440.00  19,220.00
11    OP-7400              Chemicals - corrosion inhibitor,    72,800.00  36,400.00
                           amine make-up, glycol
12    OP-7500              Utilities - water, wastewater,      41,200.00  20,600.00
                           steam allocation
13    OP-7600              Materials & supplies (stockroom)    58,900.00  29,450.00
14    OP-7700              Insurance allocation (Q2 portion)   84,000.00  42,000.00
15    OP-7900              Operator overhead (per JOA          112,400.00  56,200.00
                           Schedule A, COPAS 2005)

                                  Section B Subtotal:      1,537,740.00 768,870.00

================================================================================
SECTION C - SUMMARY & NET DUE
================================================================================

    Capital Expenditures (Section A) - EPROD share         $   981,125.00
    Operating Expenditures (Section B) - EPROD share       $   768,870.00
                                                           ----------------
    Total Current Period (April 2026)                      $ 1,749,995.00

    Plus: Prior period adjustments (Mar 2026 reclass)      $    12,840.00
    Less: Audit credit (2025 COPAS exception items)        $   (28,500.00)
                                                           ----------------
    NET DUE FROM EPROD                                     $ 1,734,335.00

Remit to:
    Phillips 66 Company - Joint Interest Billing
    P.O. Box 730587, Dallas TX 75373-0587
    Reference: SWNY-FRAC-JV / JIB 2026-04

================================================================================
Audit Rights:    Per JOA Section 9.3, Non-Operator retains 24-month audit
                 window from receipt of this statement.
Detail Backup:   Available via P66 Joint Interest Portal, JIB code 2026-04.
Questions:       jib.midstream@p66.com  |  (713) 235-1118
================================================================================
`,

  eprod_jib_targa: `================================================================================
                            TARGA RESOURCES CORP.
                          (Operator - Mont Belvieu Storage JV)
                          811 Louisiana Street, Suite 2100
                                Houston, TX 77002
                                Tax ID: 20-3701075
================================================================================

                    JOINT INTEREST BILLING STATEMENT (JIB)

JIB Statement No:        JIB-TARGA-MONT-BELVIEU-2026-03
Billing Month:           March 2026
Issue Date:              April 22, 2026
Property:                Mont Belvieu Storage JV (Caverns MBV-4, MBV-5, MBV-6)
Property Code:           MBV-STOR-JV
Operating Agreement:     JOA dated June 1, 2020, as amended Mar 2024
Non-Operator Billed:     Enterprise Products Operating LLC
Non-Operator Code:       NON-OP-EPD-022
Payment Terms:           Net 15 days from receipt
Due Date:                May 07, 2026

Working Interest Schedule:
    Non-Operator (EPROD)                              60.0000%
    Operator (Targa)                                  40.0000%

AFE References:
    AFE-MTBV-2025-04     Cavern MBV-6 Lifecycle Workover         Active
    AFE-MTBV-OPS-2026    2026 Operating Budget                    Active

================================================================================
SECTION A - CAPITAL EXPENDITURES (BILLED 60% TO NON-OPERATOR)
================================================================================

Ln  AFE                Description                          Gross    EPROD 60%
--  -----------------  ----------------------------------  ---------  ---------
 1  AFE-MTBV-2025-04   Cavern MBV-6 sonar survey,           38,400    23,040
                       baseline & post-leach comparison
 2  AFE-MTBV-2025-04   Brine system pump retrofit -        184,200   110,520
                       VFD upgrade & motor replacement
 3  AFE-MTBV-2025-04   Wellhead Christmas-tree              92,750    55,650
                       refurbishment, MBV-6A & MBV-6B
 4  AFE-MTBV-2025-04   ESD valve replacement (3 units),    134,500    80,700
                       16" trunnion ball valves
 5  AFE-MTBV-2025-04   Cathodic protection upgrade -        56,300    33,780
                       new rectifier station east yard

                                Section A Subtotal:       506,150    303,690

================================================================================
SECTION B - OPERATING EXPENDITURES (BILLED 60% TO NON-OPERATOR)
================================================================================

Ln  Account            Description                          Gross    EPROD 60%
--  -----------------  ----------------------------------  ---------  ---------
 6  OP-6100            Operations labor (18 FTE-month)     312,800    187,680
 7  OP-6200            Maintenance contract services -      94,200     56,520
                       routine M&I, brine handling
 8  OP-6310            Power purchased (3,840 MWh)          96,000     57,600
 9  OP-6400            Brine disposal / makeup water        72,400     43,440
10  OP-6500            Chemicals - corrosion, biocide       28,900     17,340
11  OP-6700            Site security, perimeter,            42,500     25,500
                       gate operations
12  OP-6900            Operator overhead (COPAS 2005,       46,800     28,080
                       Schedule A)

                                Section B Subtotal:       693,600    416,160

================================================================================
SECTION C - SUMMARY & NET DUE
================================================================================

    Capital Expenditures (Section A) - EPROD share         $ 303,690.00
    Operating Expenditures (Section B) - EPROD share       $ 416,160.00
                                                           --------------
    Total Current Period (March 2026)                      $ 719,850.00

    Plus: Prior period revenue accrual reversal             $   8,420.00
    Less: Credit - Q1 power true-up                         $ (14,300.00)
                                                           --------------
    NET DUE FROM EPROD                                     $ 713,970.00

Remit to:
    Targa Resources - JIB Settlements
    P.O. Box 4346, Department 1242, Houston TX 77210-4346
    Reference: MBV-STOR-JV / JIB 2026-03

================================================================================
Audit Rights:    Per JOA Section 9.3, Non-Operator retains 24-month audit
                 window from receipt of this statement.
Detail Backup:   PDF backup available via Targa Owner Relations Portal.
Questions:       jib.owner.relations@targaresources.com | (713) 584-1118
================================================================================
`,

  /* ─── CWFCU · 22 credit union sample files ─── */
  cwfcu_cip_rosales: `CUSTOMER IDENTIFICATION PROGRAM (CIP) PACKET
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
NCUA Charter #66234  ·  RSSD ID 2842091
═══════════════════════════════════════════════════════════════

Application ID:        CIP-MEM-2026-0421-ROSALES
Submission Channel:    CWAnyWhere mobile app
Submitted:             April 21, 2026 · 09:14:38 ET
Branch of Record:      South Bend Main · 1610 Lincolnway W
Branch Officer:        Diane Okafor (Member Services Lead)
Processing Agent:      Member Onboarding Agent · v2.4.1

──────── APPLICANT INFORMATION ────────
Legal Name:            ROSALES, Elena Maria
Date of Birth:         1991-07-22  (age 34)
Place of Birth:        South Bend, IN (US Citizen)
SSN:                   XXX-XX-4471  (validated via SSA SSNVS)
Address:               2207 Miami St, South Bend, IN 46613-2118
                       USPS DPV: D1 (deliverable, primary)
                       Address tenure: 4y 2mo (verified via LexisNexis)
Phone:                 (574) 555-0182  (mobile · T-Mobile · OK)
Email:                 e.rosales@gmail.com (verified · double opt-in)
Occupation:            RN · Memorial Hospital · South Bend
Employer Tenure:       6 years
Annual Income:         $72,400 (W-2 verified)
Marital Status:        Single

──────── GOVERNMENT ID ────────
ID Type:               Indiana Driver License
ID Number:             IN-2841-7793-22
Issued:                2022-08-04
Expires:               2026-08-04
DLDV API Check:        VERIFIED (AAMVA · matches name + DOB + address)
Photo Match:           97.4% confidence (face scan vs DL photo)
Document Authenticity: GENUINE (Mitek SDK · all 14 features present)

──────── SCREENING RESULTS ────────
OFAC SDN List:         CLEAR  (run 2026-04-21 09:14:42 ET)
OFAC Consolidated:     CLEAR
FinCEN 314(a):         CLEAR
PEP Screening:         NEGATIVE (WorldCheck One v12)
Adverse Media:         CLEAR (Dow Jones RiskCenter)
ChexSystems:           CLEAR (no prior account issues)

──────── RISK ASSESSMENT ────────
Inherent Risk Tier:    LOW
Risk Factors:
  ─ Domestic US citizen
  ─ Stable employment (6y same employer)
  ─ Stable residency (4y same address)
  ─ Standard W-2 income source
  ─ No PEP / no foreign nexus / no sanctions concern
  ─ ChexSystems clean
EDD Required:          NO (standard CDD only)
Annual CDD Refresh:    YES (next: 2027-04-21)

──────── BENEFICIAL OWNERSHIP ────────
Account Type:          Consumer (individual)
Beneficial Owner Rule: NOT APPLICABLE (no legal entity)

──────── DECISION ────────
Account Type Opened:   Share-Savings (regular)
Opening Deposit:       $25.00  (par value share)
Account Number:        XXXXXXXX-44721
Member Since:          2026-04-21
Card Issuance:         CWFCU Visa Debit · auto-shipped

Approved:              Diane Okafor (Member Services Lead) at 09:21:11 ET
Approval Method:       Agent-assisted (HITL touch: 14 sec)
Member Welcome Sent:   2026-04-21 09:21:45 ET (email + push)

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/cip_records/2026-04/
File Hash (SHA-256):   8af2c7e1...c0d4
Immutable Audit ID:    AUDIT-2026-04-21-09:14:38-CIP-44721
Linked SARs:           None
Linked CTRs:           None
Linked Loans:          None

[NCUA examiner can pull this record by name, DOB, or member number.
 All 14 CIP requirements (31 CFR § 1020.220) verifiably satisfied.]
`,

  cwfcu_cip_nguyen: `CUSTOMER IDENTIFICATION PROGRAM (CIP) PACKET
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Application ID:        CIP-MEM-2026-0428-NGUYEN
Submission Channel:    In-Branch (Mishawaka)
Submitted:             April 28, 2026 · 11:42:07 ET
Branch of Record:      Mishawaka Branch · 4406 Grape Rd
Branch Officer:        Marcus Holloway (Senior Member Rep)
Processing Agent:      Member Onboarding Agent · v2.4.1

──────── APPLICANT INFORMATION ────────
Legal Name:            NGUYEN, Tuan Khoa
Date of Birth:         1979-03-14  (age 47)
Place of Birth:        Ho Chi Minh City, Vietnam (Naturalized US Citizen 2008)
SSN:                   XXX-XX-8814  (validated via SSA SSNVS)
Address:               7218 N Logan St, Mishawaka, IN 46545
                       USPS DPV: D1 (deliverable, primary)
                       Address tenure: 9 months (verified via LexisNexis)
Phone:                 (574) 555-3344  (mobile · AT&T · OK)
Email:                 tuan.nguyen.cpa@outlook.com (verified)
Occupation:            Self-employed CPA · Nguyen Tax Services LLC
Annual Income:         $146,800 (Schedule C · 2024 tax return)
Marital Status:        Married

──────── GOVERNMENT ID ────────
ID Type:               US Passport
ID Number:             58XXXXX42
Issued:                2019-11-08
Expires:               2029-11-08
DOS Verification:      VERIFIED (passport matches name + DOB)
Photo Match:           94.1% confidence
Document Authenticity: GENUINE

──────── SCREENING RESULTS ────────
OFAC SDN List:         CLEAR
OFAC Consolidated:     CLEAR
FinCEN 314(a):         CLEAR
PEP Screening:         NEAR-MATCH (88% similarity)
                       ─ Match: "T. Nguyen" · former county commissioner
                       ─ Different jurisdiction (Texas vs Indiana)
                       ─ Different DOB by 8 years
                       ─ DISMISSED BY REVIEWER (Holloway, M.)
Adverse Media:         CLEAR
ChexSystems:           CLEAR

──────── RISK ASSESSMENT ────────
Inherent Risk Tier:    MEDIUM
Risk Factors:
  ─ Self-employed (income complexity)
  ─ Cash-intensive business possible (tax services)
  ─ PEP near-match (dismissed but flagged for awareness)
  ─ Stable US citizenship + clean ChexSystems
  ─ Short address tenure (9mo)
EDD Required:          NO (standard CDD with quarterly refresh)
Annual CDD Refresh:    YES (next: 2027-04-28)
Enhanced Monitoring:   YES (cash deposit threshold $5,000 vs default $10,000)

──────── BENEFICIAL OWNERSHIP ────────
Account Type:          Consumer + Business sub-application linked
Business Entity:       Nguyen Tax Services LLC (Indiana SOS 2019)
Beneficial Owner Rule: Single beneficial owner (100%) — applicant himself

──────── DECISION ────────
Account Type Opened:   Share-Savings + Share-Draft (checking) + Business Sub
Opening Deposit:       $250.00
Account Numbers:       XXXXXXXX-29402 (personal)
                       XXXXXXXX-29403 (business)
Member Since:          2026-04-28

Approved:              Marcus Holloway (Senior Member Rep) at 11:58:33 ET
Approval Method:       Agent-assisted with HITL escalation (PEP near-match)
HITL Touch Time:       47 seconds (PEP dismissal documentation)

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/cip_records/2026-04/
Immutable Audit ID:    AUDIT-2026-04-28-11:42:07-CIP-29402
PEP Dismissal Log:     AUDIT-2026-04-28-11:51:14-PEP-DISMISS-29402
Linked SARs:           None
Linked CTRs:           None  (monitoring threshold reduced to $5K)
Linked Loans:          None

[Enhanced monitoring flag persists on this account. Quarterly CDD touch.]
`,

  cwfcu_cip_arrington: `CUSTOMER IDENTIFICATION PROGRAM (CIP) PACKET
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Application ID:        CIP-MEM-2026-0512-ARRINGTON
Submission Channel:    In-Branch (Granger)
Submitted:             May 12, 2026 · 14:08:51 ET
Branch of Record:      Granger Branch · 7102 Heritage Square Dr
Branch Officer:        Jamal Greene (Member Services)
Processing Agent:      Member Onboarding Agent · v2.4.1

──────── APPLICANT INFORMATION ────────
Legal Name:            ARRINGTON, Devon Christopher
Date of Birth:         1986-09-04  (age 39)
SSN:                   XXX-XX-2204  (validated via SSA SSNVS)
Address:               5814 Bittersweet Rd, Apt 12B, Granger, IN 46530
                       USPS DPV: D2 (deliverable secondary unit)
                       Address tenure: 11 months
Phone:                 (574) 555-9971  (mobile · Verizon)
Email:                 d.arrington86@protonmail.com
Occupation:            Independent Contractor (construction)
Annual Income:         $86,200 (estimated, no W-2 last 18 months)

──────── GOVERNMENT ID ────────
ID Type:               Indiana Driver License
ID Number:             IN-5520-1041-08
Issued:                2023-09-04
Expires:               2027-09-04
DLDV API Check:        VERIFIED
Photo Match:           96.0% confidence
Document Authenticity: GENUINE

──────── SCREENING RESULTS ────────
OFAC SDN List:         NEAR-MATCH (87% similarity)
                       ─ Match: "Devon Arrington" · narcotics-related entry
                       ─ Different DOB (subject is 1971)
                       ─ Different location (CA vs IN)
                       ─ Different middle name
                       ─ DISMISSED BY BSA OFFICER (Williams, A.) at 14:42 ET
OFAC Consolidated:     CLEAR
FinCEN 314(a):         CLEAR
PEP Screening:         NEGATIVE
Adverse Media:         FLAGGED (1 article — 2018 misdemeanor disturbance)
ChexSystems:           PRIOR ACCOUNT CLOSURE (2019, overdrafts)

──────── RISK ASSESSMENT ────────
Inherent Risk Tier:    HIGH
Risk Factors:
  ─ Independent contractor income (cash-intensive)
  ─ Recent address change (11mo)
  ─ OFAC near-match (dismissed but documented)
  ─ Prior ChexSystems closure
  ─ Adverse media (low severity but present)
  ─ No verified W-2 in past 18 months
EDD Required:          YES — Enhanced Due Diligence assigned to Compliance Agent
Annual CDD Refresh:    YES (next: 2026-11-12 — semi-annual)
Enhanced Monitoring:   YES
  ─ Cash deposit threshold: $3,000 (alert)
  ─ Wire activity threshold: any cross-state $5,000+
  ─ Monthly velocity review

──────── BENEFICIAL OWNERSHIP ────────
Account Type:          Consumer (individual)

──────── DECISION ────────
Account Type Opened:   Share-Savings only (no share-draft, no debit until 90d review)
Opening Deposit:       $100.00 cash
Account Number:        XXXXXXXX-44821
Member Since:          2026-05-12

Approved:              Jamal Greene with BSA Officer concurrence (Williams, A.)
Approval Method:       HITL escalation — both OFAC near-match + ChexSystems
HITL Touch Time:       38 minutes (full review + EDD provisioning)

──────── HAND-OFF NOTES ────────
→ Compliance Agent:    EDD assigned. Cash velocity monitoring active.
→ Annual CDD:          Reduced to semi-annual cycle (next 2026-11-12)
→ Loan Document Agent: Will apply enhanced verification on any future loan app
                       (income source-of-funds documentation required)

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/cip_records/2026-05/
Immutable Audit ID:    AUDIT-2026-05-12-14:08:51-CIP-44821
OFAC Dismissal Log:    AUDIT-2026-05-12-14:42:09-OFAC-DISMISS-44821
EDD Assignment Log:    AUDIT-2026-05-12-14:43:11-EDD-44821
Linked SARs:           ⚠ SAR-2026-0142 (filed Jun 4, 2026 — structuring pattern)
Linked CTRs:           None (cash deposits all under $10K threshold)
Linked Loans:          None

[This member (#44821) is the central subject of the SAR-2026-0142
 structuring case demoed during the NCUA exam-readiness walkthrough.]
`,

  cwfcu_cip_okafor: `CUSTOMER IDENTIFICATION PROGRAM (CIP) PACKET
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Application ID:        CIP-MEM-2026-0521-OKAFOR
Submission Channel:    CWAnyWhere mobile app + In-Branch
Submitted:             May 21, 2026 · 08:11:24 ET
Branch of Record:      South Bend Main · 1610 Lincolnway W
Branch Officer:        Diane Okafor (Member Services Lead)
Processing Agent:      Member Onboarding Agent · v2.4.1

──────── APPLICANT INFORMATION ────────
Legal Name:            OKAFOR ENTERPRISES LLC (Business Member)
Account Signer:        OKAFOR, Adaeze Chioma  (sole member of LLC)
Date of Birth:         1981-06-15  (age 44)
SSN (signer):          XXX-XX-7811
EIN (entity):          XX-3947112
Address (business):    442 W Washington St, Suite 280, South Bend, IN 46601
Address (signer):      1118 N Frances St, South Bend, IN 46617
Phone:                 (574) 555-4421  (business landline · CenturyLink)
Email:                 adaeze@okafor-enterprises.com
Entity Type:           Indiana LLC (formed 2022-03-08)
Entity Activity:       Healthcare staffing agency
Annual Revenue:        $1.4M (2024 K-1)
Years in Operation:    4

──────── GOVERNMENT ID (Account Signer) ────────
ID Type:               Indiana Driver License
ID Number:             IN-7740-2241-91
Issued:                2020-06-15
Expires:               2028-06-15
DLDV API Check:        VERIFIED
Photo Match:           98.1% confidence
Document Authenticity: GENUINE

──────── BUSINESS DOCUMENTATION ────────
IRS Form SS-4:         Filed 2022-03-08 (EIN confirmation letter)
Articles of Org:       Indiana SOS filing 2022-03-08
Operating Agreement:   On file (single-member LLC)
2024 Tax Return:       Form 1065 + K-1 verified
Business License:      Indiana Healthcare Staffing License #HCSI-44829

──────── SCREENING RESULTS ────────
OFAC SDN List:         CLEAR (entity + signer)
OFAC Consolidated:     CLEAR
FinCEN 314(a):         CLEAR
PEP Screening:         NEGATIVE
Adverse Media:         CLEAR
ChexSystems (signer):  CLEAR
Dun & Bradstreet:      D&B score 78 (Low risk · Established)

──────── RISK ASSESSMENT ────────
Inherent Risk Tier:    LOW
Risk Factors:
  ─ Established business (4 years)
  ─ Healthcare sector (regulated, low BSA risk)
  ─ Single beneficial owner (no ownership obfuscation)
  ─ Clean signer history
  ─ Strong D&B score
EDD Required:          NO (standard CDD)
Annual CDD Refresh:    YES (next: 2027-05-21)

──────── BENEFICIAL OWNERSHIP RULE ────────
Beneficial Owner(s):   Adaeze Chioma Okafor (100% ownership)
Control Prong:         Adaeze Chioma Okafor (Manager-Member)
Certification:         FinCEN Form CTR certification on file

──────── DECISION ────────
Account Type Opened:   Business Share-Draft (checking) + Business Money Market
Opening Deposit:       $15,000 (commercial check from prior bank — Lakeside Bank)
Account Numbers:       XXXXXXXX-77881 (checking)
                       XXXXXXXX-77882 (money market)
Member Since:          2026-05-21

Approved:              Diane Okafor (Member Services Lead) at 08:39:18 ET
Approval Method:       Agent-assisted (HITL touch: 23 min for entity docs)

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/cip_records/2026-05/
Beneficial Ownership:  ncua-exam-2026/cdd_records/beneficial_owner_certs/
Immutable Audit ID:    AUDIT-2026-05-21-08:11:24-CIP-77881
Linked SARs:           None
Linked CTRs:           None
Linked Loans:          None

[Exemplar business-member CIP packet. All 31 CFR § 1010.230 beneficial
 ownership requirements verifiably satisfied. NCUA examiner-ready.]
`,

  cwfcu_sar_structuring: `FinCEN SAR (Suspicious Activity Report) — Form 111
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
NCUA Charter #66234  ·  RSSD ID 2842091
═══════════════════════════════════════════════════════════════

FILING REFERENCE:      SAR-2026-0142
FinCEN ID (pending):   <auto-assigned on BSA E-Filing submission>
Filing Type:           INITIAL
Detection Mechanism:   ApexAI Compliance Agent — Pattern v3.2 (structuring)
Detection Date:        2026-05-28 03:14:08 ET (last txn ingested)
Drafted By:            Compliance Agent · v2.6.3
Pending BSA Officer:   Adrienne Williams (BSA Officer · NCCO/CAMS)

──────── SUBJECT INFORMATION ────────
Subject Type:          Individual member
Member Number:         #44821
Legal Name:            ARRINGTON, Devon Christopher
Date of Birth:         1986-09-04 (39)
SSN:                   XXX-XX-2204
Address:               5814 Bittersweet Rd, Apt 12B, Granger, IN 46530
Occupation:            Independent Contractor (construction)
Member Since:          2026-05-12 (opened with EDD flag from CIP review)
Account(s):            XXXXXXXX-44821 (Share-Savings)
Risk Tier at Opening:  HIGH (OFAC near-match dismissed + ChexSystems prior)
Enhanced Monitoring:   Active (cash threshold $3,000)

──────── SUSPICIOUS ACTIVITY ────────
Activity Type:         Structuring (avoiding CTR filing threshold)
Suspected Violation:   31 U.S.C. § 5324
Activity Date Range:   2026-05-12  through  2026-05-28  (16 days)
Total Amount:          $47,300.00 (USD)
Transaction Count:     7

──────── TRANSACTION DETAIL ────────
 #   Date         Branch         Amount     Type
 1   2026-05-12   South Bend     $8,900     Cash deposit (Teller 04)
 2   2026-05-14   Mishawaka      $7,200     Cash deposit (Teller 02)
 3   2026-05-16   Granger        $5,800     Cash deposit (Teller 01)
 4   2026-05-18   Elkhart        $6,400     Cash deposit (Teller 07)
 5   2026-05-21   South Bend     $7,800     Cash deposit (Teller 11)
 6   2026-05-24   Mishawaka      $5,900     Cash deposit (Teller 04)
 7   2026-05-28   Granger        $5,300     Cash deposit (Teller 03)
                                ─────────
                                $47,300

──────── PATTERN ANALYSIS ────────
─ All deposits between $5,300 and $8,900 (just under $10,000 CTR trigger)
─ Average deposit interval: 2.7 days (consistent cadence)
─ 4 different branch locations within South Bend MSA
─ No corresponding business deposits to indicate legitimate cash source
─ Member's stated occupation (construction contractor) does not require
  the level of cash handling implied by deposit volume
─ Pattern statistical confidence: 96.1% (CWFCU model · trained on 18mo
  prior structuring SARs across credit union peer cohort)

──────── NARRATIVE (Part IV) ────────
On or about May 12 through May 28, 2026, the subject, account holder
#44821 (ARRINGTON, Devon Christopher), conducted 7 cash deposits totaling
$47,300 at CommunityWide FCU branches across South Bend, Mishawaka,
Elkhart, and Granger, Indiana. Individual transactions ranged from $5,300
to $8,900, structured in amounts to avoid the $10,000 Currency Transaction
Report (CTR) filing threshold under 31 U.S.C. § 5313.

The transaction pattern — multiple cash deposits in similar amounts,
across multiple branches, over a 16-day window with consistent 2-3 day
intervals — is consistent with structuring as defined under 31 U.S.C.
§ 5324. The subject's stated occupation (independent construction
contractor) does not present an apparent business justification for the
geographic and temporal distribution observed.

The subject was opened at CommunityWide FCU on May 12, 2026 with a HIGH
inherent risk tier following an OFAC near-match dismissal and a prior
ChexSystems account closure. Enhanced monitoring with a $3,000 cash
threshold was active throughout the activity period.

CommunityWide FCU's BSA Officer has reviewed the activity and determined
it warrants filing of this Suspicious Activity Report.

──────── ATTACHMENTS ────────
─ Transaction log export (signed XML, 7 entries)
─ CIP packet (CIP-MEM-2026-0512-ARRINGTON)
─ Branch teller worksheets (4 branches, 7 entries)
─ Enhanced monitoring alert log (12 entries)

──────── DECISION TIMELINE ────────
Pattern detected:        2026-05-28 03:14:08 ET (post-deposit reconcile)
Narrative auto-drafted:  2026-05-28 03:14:42 ET (Compliance Agent v2.6.3)
Confidence at draft:     96.1%
Routed to HITL queue:    2026-05-28 03:14:50 ET (priority HIGH)
SAR Deadline:            2026-06-27 (30 days from detection)
Filing Status:           PENDING BSA Officer review (as of Jun 4, 2026)

──────── HAND-OFF NOTES ────────
→ Loan Document Agent: Source-of-funds documentation required on any
                       future loan application from #44821 (already
                       enforced by EDD flag set at CIP onboarding)
→ Policy & HR Agent:   Refresher BSA training trigger — all 4 branch
                       tellers who processed these deposits should
                       attend Q3 advanced structuring detection module

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/sars/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-28-03:14:42-SAR-0142
Confidence Trail:      Pattern v3.2 · Score 0.961 · model log AUDIT-...0142m

[Once filed, this SAR closes 2 NCUA exam attention items:
   1. BSA program effectiveness (pattern detection demonstrated)
   2. Enhanced monitoring on HIGH-risk member (CIP linkage demonstrated)]
`,

  cwfcu_sar_rapid_movement: `FinCEN SAR (Suspicious Activity Report) — Form 111
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

FILING REFERENCE:      SAR-2026-0138
FinCEN ID:             32026031400138
Filing Type:           INITIAL
Filing Status:         FILED (2026-06-01 09:17 ET)
Detection Mechanism:   ApexAI Compliance Agent — Rapid Movement v2.1
Drafted By:            Compliance Agent · v2.6.3 (96.4% confidence)
Approved By:           Adrienne Williams (BSA Officer) at 2026-06-01 09:11

──────── SUBJECT INFORMATION ────────
Member Number:         #38204
Legal Name:            HARTLEY, Russell J.
Date of Birth:         1972-11-08 (53)
Address:               4407 Edison Rd, South Bend, IN 46615
Occupation:            Independent dispatcher (logistics)
Member Since:          2024-08-21
Risk Tier:             MEDIUM (auto-elevated post-pattern)

──────── SUSPICIOUS ACTIVITY ────────
Activity Type:         Rapid movement of funds (in-and-out cycling)
Suspected Violation:   31 U.S.C. § 5318(g)
Activity Date Range:   2026-05-09 through 2026-05-30 (22 days)
Total In:              $18,500.00
Total Out:             $18,150.00 (net retained: $350)
Transaction Count:     12

──────── PATTERN ────────
─ 6 wire-ins ($2,800 to $4,100) from out-of-state senders
─ 6 wire-outs to 4 different recipients within 24 hrs of receipt
─ Mean dwell time: 18 hours
─ All wires under $5,000 threshold
─ No corresponding payroll, invoice, or legitimate business context

──────── NARRATIVE ────────
On or about May 9 through May 30, 2026, the subject (#38204) engaged in
a pattern of rapid funds movement consisting of 6 incoming wire transfers
from senders in Florida, Georgia, and Texas totaling $18,500. Each
incoming wire was followed within 24 hours by an outgoing wire to one of
4 recipients in different jurisdictions. Net retention across all 12
transactions was $350. The pattern is consistent with funnel-account
activity used to obscure the true origin or destination of funds.

──────── HAND-OFF NOTES ────────
→ Compliance Agent:    Member moved to enhanced monitoring queue
→ Loan Document Agent: No active loans · enhanced verification on any future
→ Policy & HR Agent:   No employee impact (member-side activity only)

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/sars/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-30-22:14:08-SAR-0138
Filed Timestamp:       2026-06-01 09:17:33 ET (within 30-day window)

[Closed exemplar — filed, accepted by FinCEN, NCUA folder-indexed.]
`,

  cwfcu_sar_layering: `FinCEN SAR (Suspicious Activity Report) — Form 111
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

FILING REFERENCE:      SAR-2026-0141
Filing Status:         PENDING BSA Officer review
Detection Mechanism:   ApexAI Compliance Agent — Layering Heuristic v1.4
Drafted By:            Compliance Agent · v2.6.3 (94.7% confidence)
Pending BSA Officer:   Adrienne Williams (BSA Officer · NCCO/CAMS)

──────── SUBJECT INFORMATION ────────
Member Number:         #51887
Legal Name:            BERG, Adrian Mark
Date of Birth:         1990-02-19 (36)
Address:               2208 Sunnyside Ct, Mishawaka, IN 46545
Occupation:            E-commerce reseller (self-employed)
Member Since:          2025-11-04
Risk Tier:             MEDIUM (now elevated)

──────── SUSPICIOUS ACTIVITY ────────
Activity Type:         Layering (peer-to-peer cycling through 3+ intermediaries)
Suspected Violation:   31 U.S.C. § 5324
Activity Date Range:   2026-05-04 through 2026-05-30 (27 days)
Total Activity:        $31,200.00
Transaction Count:     22 (Zelle outbound + ACH inbound combined)

──────── PATTERN ANALYSIS ────────
─ 11 Zelle sends to 7 different unrelated peers (avg $2,200)
─ 11 ACH credits from 4 prepaid card providers
─ Peer recipients show no historical relationship (CWFCU + national sample)
─ All sends/receives below FinCEN reporting thresholds
─ Mean dwell time of funds in account: 13.4 hours
─ Pattern consistent with cash-out layering through reload card cycle

──────── NARRATIVE (Part IV) ────────
On or about May 4 through May 30, 2026, the subject (#51887) conducted
22 transactions consistent with layering activity. The subject received
11 ACH credits from four prepaid card / reload card providers totaling
$31,200 and within 24 hours of receipt initiated 11 corresponding Zelle
peer-to-peer transfers to 7 different unrelated peer recipients in
amounts averaging $2,200 each. No corresponding business invoice, payroll
deposit, or legitimate commercial purpose was identified during agent
review. The pattern is consistent with layering activity used to obscure
the original cash source through multiple unrelated intermediaries.

──────── HAND-OFF NOTES ────────
→ Compliance Agent:    Member added to EDD watch — quarterly review cycle
→ Loan Document Agent: Enhanced source-of-funds on any future application
→ Policy & HR Agent:   No employee impact

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/sars/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-30-21:42:08-SAR-0141
SAR Deadline:          2026-06-29 (30 days from detection)
`,

  cwfcu_ctr_cash: `FinCEN Form 112 — Currency Transaction Report (CTR)
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

FILING REFERENCE:      CTR-2026-05-1187
FinCEN ID:             32026053100118733
Filing Status:         FILED (2026-05-30 09:08 ET — within 15-day window)
Auto-Generated By:     Compliance Agent · v2.6.3
Approved By:           Adrienne Williams (BSA Officer) at 2026-05-30 09:04

──────── REPORTING INSTITUTION ────────
Name:                  CommunityWide Federal Credit Union
Address:               1610 Lincolnway W, South Bend, IN 46628
EIN:                   XX-1948822
NCUA Charter:          #66234
RSSD ID:               2842091

──────── TRANSACTION ────────
Date:                  2026-05-29 14:42:08 ET
Type:                  Cash deposit (in)
Amount:                $12,400.00
Currency:              USD
Branch:                Granger Branch · 7102 Heritage Square Dr
Teller:                #11 (Singer, K.)
Verified Counted:      Y (dual-control verification)

──────── PERSON CONDUCTING ────────
Same as person on whose behalf transaction conducted: Y

──────── PERSON ON WHOSE BEHALF ────────
Member Number:         #29341
Legal Name:            CHEN, Robert Theodore
Date of Birth:         1976-04-11 (50)
SSN:                   XXX-XX-1188
Address:               2208 Inverness Rd, Granger, IN 46530
Occupation:            Owner · Chen Family Restaurant Group (LLC)
ID Verified:           Indiana DL #IN-9920-8847-04 (in good standing)
Account(s) Affected:   XXXXXXXX-29341 (Business Share-Draft)

──────── SOURCE-OF-FUNDS CONTEXT ────────
Stated Source:         Weekend cash receipts from 3 restaurant locations
Member History:        Average weekly cash deposit $9,800 (prior 12 mo)
                       Stated source consistent w/ business activity
EDD on file:           NO (LOW-risk tier · business sector match)
Prior CTRs:            7 in trailing 12 mo (consistent volume)
Prior SARs:            None

──────── ANCILLARY INFORMATION ────────
Multiple Transactions: N
Currency Exchange:     N
Armored Car Service:   N
ATM Transaction:       N

──────── PROCESSING TIMELINE ────────
Transaction:           2026-05-29 14:42:08 ET
Auto-drafted by Agent: 2026-05-29 14:42:48 ET (40 sec)
BSA Officer Review:    2026-05-30 09:04 ET (8 min)
Filed to FinCEN:       2026-05-30 09:08:14 ET
Confirmation Received: 2026-05-30 09:08:21 ET (FinCEN ack)
Filing Latency:        18 hrs 26 min  (target ≤ 15 days · well within)

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/ctrs/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-29-14:42:08-CTR-1187
Related Records:       Linked to Member #29341 12-mo CTR history bundle
`,

  cwfcu_ctr_wire: `FinCEN Form 112 — Currency Transaction Report (CTR)
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

FILING REFERENCE:      CTR-2026-05-1188
FinCEN ID:             32026053100118832
Filing Status:         FILED (2026-05-31 11:22 ET)
Auto-Generated By:     Compliance Agent · v2.6.3
Approved By:           Adrienne Williams (BSA Officer) at 2026-05-31 11:19

──────── REPORTING INSTITUTION ────────
Name:                  CommunityWide Federal Credit Union
NCUA Charter:          #66234

──────── TRANSACTION ────────
Date:                  2026-05-30 16:08:14 ET
Type:                  Inbound wire (Fedwire / RTGS)
Amount:                $15,000.00
Currency:              USD
Originator:            CBI Financial Services LLC (Houston, TX)
Originator Bank:       JPMorgan Chase, NA (ABA 021000021)
Beneficiary:           Hartley, Russell J. — Member #08812
Wire Reference:        FW2026-05-30-CW-08812

──────── PERSON ON WHOSE BEHALF ────────
Member Number:         #08812
Legal Name:            HARTLEY, Russell J.
Date of Birth:         1972-11-08
Address:               4407 Edison Rd, South Bend, IN 46615
Occupation:            Independent dispatcher (logistics)
EDD on file:           YES (subject of SAR-2026-0138 rapid movement)
Prior CTRs:            3 in trailing 12 mo

──────── SOURCE-OF-FUNDS CONTEXT ────────
Stated Source:         Per member, "payment for dispatch services rendered"
Member History:        Pattern of wire-in / wire-out cycling (see SAR-0138)
Decision Rationale:    File CTR for transparency · Compliance Agent has
                       parallel SAR-0138 pattern tracking active

──────── PROCESSING TIMELINE ────────
Transaction:           2026-05-30 16:08:14 ET
Auto-drafted:          2026-05-30 16:08:48 ET (34 sec)
BSA Officer Review:    2026-05-31 11:19 ET (19 hrs)
Filed to FinCEN:       2026-05-31 11:22:11 ET
Filing Latency:        19 hrs 14 min

──────── HAND-OFF NOTES ────────
→ Compliance Agent:    Wire correlated with SAR-2026-0138 rapid movement
                       pattern. Subject of ongoing case.
→ Loan Document Agent: Member has no active loans. EDD active on file.

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/ctrs/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-30-16:08:14-CTR-1188
`,

  cwfcu_cdd_04421: `CUSTOMER DUE DILIGENCE (CDD) REVIEW
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
Enhanced Due Diligence Sub-Review
═══════════════════════════════════════════════════════════════

Review ID:             CDD-2026-Q2-MEM-04421
Review Type:           EDD (Enhanced Due Diligence) · Quarterly Refresh
Trigger:               Wire activity to 3 high-risk jurisdictions
                       Initial onboarding risk tier: HIGH
Review Period:         2026-03-01 through 2026-05-31

Conducted By:          Compliance Agent · v2.6.3
Sign-off Pending:      Adrienne Williams (BSA Officer)

──────── MEMBER PROFILE ────────
Member Number:         #39104
Legal Name:            MENDOZA, Carlos Ignacio
Date of Birth:         1968-09-22 (57)
Address:               14422 Coquina Ln, Granger, IN 46530
Member Since:          2023-08-14
Account Type(s):       Share-Draft (checking) + Money Market
Stated Occupation:     Import / export agent (textiles)
Stated Income:         $245,000 annual (Schedule C verified 2024)

──────── RISK FACTORS (At opening) ────────
─ Cross-border business (Mexico, Honduras, Vietnam suppliers)
─ Cash-intensive intermediary role
─ PEP-adjacent (cousin to former Honduran county commissioner)
─ High wire volume (50+ international wires/year)

──────── REVIEW PERIOD ACTIVITY ────────
Wire transfers (in):   18 wires · $182,400 total
                       Originators: 6 entities (4 Mexico, 1 Honduras, 1 PA)
Wire transfers (out):  22 wires · $174,200 total
                       Recipients: 8 entities (5 Mexico, 2 Vietnam, 1 US)
Cash deposits:         3 deposits · $14,200 total (under CTR threshold)
ATM activity:          Normal pattern (US-domestic only)
Card spend:            $48,200 (consistent w/ business travel)

──────── ANOMALIES DETECTED ────────
Q1 (Mar-Apr-May):
  ─ 3 wires to NEW recipients in Vietnam (added Apr 2026)
    Vendor name: "Mekong Textile Trading Co" — appears in OFAC
    594(a) consolidated list as MEDIUM-risk (proliferation finance
    secondary watchlist). NO match to SDN.
    Decision: Documented and risk-accepted. Continued monitoring.

  ─ Average wire size +18% vs trailing 12mo baseline
    Stated cause: Increased Q2 textile orders for holiday season
    Documentation: Customer purchase orders (3) reviewed and on file

──────── CDD UPDATES ────────
Risk Tier Reaffirmed:  HIGH (no change)
Monitoring Frequency:  Quarterly (no change)
Cash Threshold:        Reduce from $5,000 → $3,000 (new alert level)
Wire Threshold:        Add specific alert: any single wire ≥$20,000

──────── ATTACHMENTS ────────
─ Wire transfer log (40 records, signed XML)
─ Vietnamese supplier KYC packets (3 vendors, on file)
─ Updated source-of-funds questionnaire (signed by member 2026-05-28)
─ Mekong Textile Trading Co secondary watchlist review notes

──────── HAND-OFF NOTES ────────
→ Onboarding Agent:    No re-screening triggered (no PEP change)
→ Loan Document Agent: Member has $35K business LOC · enhanced annual review
→ Policy & HR Agent:   Front-line training: international wire scrutiny

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/cdd_records/2026-Q2/
Immutable Audit ID:    AUDIT-2026-06-01-09:14:08-CDD-04421
Annual Review Due:     2026-08-14 (next semi-annual touch)
`,

  cwfcu_cdd_08812: `CUSTOMER DUE DILIGENCE (CDD) REVIEW
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
Annual CDD Refresh
═══════════════════════════════════════════════════════════════

Review ID:             CDD-2026-Q2-MEM-08812
Review Type:           Annual CDD Refresh (Standard)
Review Period:         2025-06-01 through 2026-05-31

Conducted By:          Compliance Agent · v2.6.3
Sign-off Pending:      Adrienne Williams (BSA Officer)

──────── MEMBER PROFILE ────────
Member Number:         #08812
Legal Name:            HARTLEY, Russell J.
Date of Birth:         1972-11-08 (53)
Address:               4407 Edison Rd, South Bend, IN 46615
Member Since:          2024-08-21
Account Type:          Share-Draft (checking) + Share-Savings
Stated Occupation:     Independent dispatcher (logistics)
Stated Income:         $58,400 annual (no 2024 W-2 on file)
Original Risk Tier:    MEDIUM (cash-intensive occupation)

──────── REVIEW PERIOD ACTIVITY ────────
Inbound wires:         15 wires · $42,800 total
Outbound wires:        12 wires · $39,400 total
Cash deposits:         6 deposits · $11,200 total
ATM activity:          Light · primarily local
Card spend:            $18,400 (consistent with stated income)

──────── ANOMALIES DETECTED ────────
─ ⚠ Rapid in/out wire cycling Q2 2026 (see SAR-2026-0138)
─ ⚠ Net retained: 8.2% of inbound (mean dwell time 22 hrs)
─ Pattern not present in 2024 baseline period
─ Stated income inconsistent with implied transaction volume
─ Member declined to update 2024 tax documentation when requested

──────── CDD UPDATES ────────
Risk Tier:             ELEVATED — MEDIUM → HIGH
Monitoring Frequency:  Quarterly (was annual)
Cash Threshold:        $3,000 alert (was $5,000)
Wire Threshold:        Specific alert: any single wire ≥$10,000
Documentation Requested:
  ─ 2024 tax return (member to provide)
  ─ Source of dispatch service income (clients, invoices, contracts)

──────── HAND-OFF NOTES ────────
→ SAR-2026-0138:       Linked to this CDD upgrade decision
→ Loan Document Agent: Enhanced source-of-funds on any future application
→ Onboarding Agent:    No re-screening needed

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/bsa_aml/cdd_records/2026-Q2/
Immutable Audit ID:    AUDIT-2026-06-01-10:22:08-CDD-08812
Next Review Due:       2026-09-01 (quarterly cycle)
`,

  cwfcu_loan_auto: `LOAN APPLICATION PACKET — AUTO
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Loan Reference:        LN-2026-05-0381
Application Channel:   CWAnyWhere mobile app
Submitted:             2026-05-21 18:42:08 ET
Processing Agent:      Loan Document Agent · v2.4.1
Decision Status:       APPROVED · ROUTED TO UNDERWRITER

──────── APPLICANT ────────
Member Number:         #29402
Legal Name:            GARCIA, Lucia Marisol
Date of Birth:         1988-12-04 (37)
Address:               1842 N Hill St, South Bend, IN 46617
Employer:              Memorial Hospital · South Bend (RN, 11 years)
Annual Income:         $89,200 (W-2 verified)
Co-applicant:          None
CIP On File:           ✓ (member since 2014-06-12)
Risk Tier:             LOW
Prior CDD Concerns:    None · annual review current

──────── LOAN REQUEST ────────
Type:                  Auto Loan (new vehicle)
Amount Requested:      $28,400
Term:                  60 months
Rate (offered):        4.75% APR · LOW risk pricing tier
Down Payment:          $4,200 (member savings)

──────── COLLATERAL ────────
Vehicle:               2026 Honda CR-V EX-L (new)
VIN:                   5J6RW2H89PL044128
Dealer:                Gates Honda · South Bend, IN
MSRP:                  $36,200
Purchase Price:        $32,600 (negotiated)
Loan-to-Value:         87.1%

──────── DOCUMENTATION ────────
Loan Application:      ✓ Signed (DocuSign · audit ID 88142)
Indiana DL:            ✓ Verified (in good standing, expires 2027-12-04)
Proof of Income:       ✓ 2 most recent paystubs + 2024 W-2
Employment Verify:     ✓ Memorial Hospital HR confirmation (auto-fetched)
Insurance Binder:      ✓ State Farm Auto · liability + comprehensive
Title:                 ✓ Will issue on closing (clean — new vehicle)
Bill of Sale:          ✓ Gates Honda

──────── AGENT VALIDATION ────────
Income Verification:   PASS (W-2 + paystub cross-check, 100% match)
DTI Calculation:       Front 18.2% · Back 28.7% (within policy)
Credit Pull:           FICO 762 (within LOW tier 720-850)
Collateral Valuation:  ✓ NADA + KBB cross-check (LTV within policy)
OFAC Re-screen:        ✓ Clear
Source of Funds:       ✓ Down payment from share-savings (no anomaly)

──────── EXTRACTION CONFIDENCE ────────
Per-document confidence (n=8 documents):
  ─ Loan App:          99.4%
  ─ DL:                98.1%
  ─ Paystubs:          97.8%
  ─ W-2:               99.2%
  ─ Insurance binder:  96.4%
  ─ Title (forward):   97.1%
  ─ Bill of sale:      98.8%
  ─ Employment verify: 99.8%
Overall packet confidence: 98.3%

──────── DECISION TIMELINE ────────
Submitted:             2026-05-21 18:42:08 ET
Packet ingested:       2026-05-21 18:42:54 ET (46 sec)
Extraction complete:   2026-05-21 18:46:11 ET (3 min 17 sec)
Validation complete:   2026-05-21 18:47:28 ET (1 min 17 sec)
Auto-approval:         2026-05-21 18:47:32 ET
Routed to Underwriter: 2026-05-21 18:47:48 ET (Carrie Mendez · Sr UW)
Underwriter Approve:   2026-05-22 09:48 ET (next-business-day)
Total Cycle Time:      15 hrs 6 min (target ≤ 48 hrs)

──────── HAND-OFF NOTES ────────
→ Vendor Agent:        State Farm appointed (insurance vendor — no new MSA)
→ Closing/Funding:     Scheduled 2026-05-26 14:00 ET at South Bend Main

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/credit_risk/auto/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-21-18:42:08-LN-0381
`,

  cwfcu_loan_heloc_johnson: `LOAN APPLICATION PACKET — HELOC
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Loan Reference:        LN-2026-0441
Application Channel:   CWAnyWhere mobile app
Submitted:             2026-05-30 08:14:18 ET
Processing Agent:      Loan Document Agent · v2.4.1
Decision Status:       PENDING · HITL · Missing W-2 (2024)

──────── APPLICANT ────────
Member Number:         #51122
Legal Name:            JOHNSON, Marcus Antoine
Date of Birth:         1981-04-19 (44)
Address:               5808 Cleveland Rd, Granger, IN 46530
Employer:              St Joseph Regional Med Ctr · IT Director (4 years)
Annual Income:         $94,200 (estimated · W-2 missing)
Co-applicant:          None
CIP On File:           ✓ (member since 2018-03-22)
Risk Tier:             LOW
Prior CDD Concerns:    None · annual review current

──────── LOAN REQUEST ────────
Type:                  HELOC (Home Equity Line of Credit)
Amount Requested:      $85,000
Term:                  10-year draw / 20-year repay
Rate (offered):        Prime + 1.0% APR variable
Use of Funds:          Home renovation (kitchen + primary bath)

──────── COLLATERAL ────────
Property:              5808 Cleveland Rd, Granger, IN 46530
Type:                  Single-family residence (4BR/3BA, built 2008)
Tax Assessment 2025:   $342,500
Estimated Value:       $385,000 (member-stated · appraisal pending)
Mortgage Balance:      $192,400 (Notre Dame FCU · refi 2022)
Estimated Equity:      $192,600
HELOC LTV (target):    ≤ 85% combined · 72% w/ requested $85K

──────── DOCUMENTATION ────────
Loan Application:      ✓ Signed (DocuSign · audit ID 88301)
Indiana DL:            ✓ Verified (expires 2029-04-19)
2025 Paystubs:         ✓ 3 most recent (Apr, May 1, May 16)
2024 W-2:              ✗ MISSING ← BLOCKER
2024 Tax Return:       ✓ Form 1040 + Schedule 1 (no W-2 attached)
First-Mortgage Statement: ✓ (Notre Dame FCU current as of May 2026)
Title Search:          ◐ Ordered 2026-05-30 · expected 2026-06-04
Property Tax Receipt:  ✓ 2025 paid in full
HOI Binder:            ✓ State Farm · effective 2026-04-01

──────── AGENT VALIDATION ────────
Income Verification:   INCOMPLETE — W-2 missing for 2024
  ─ Paystubs verify YTD 2026 income
  ─ Tax return shows $94,200 AGI but no W-2 attached
  ─ Underwriting policy requires 2 years W-2 evidence
DTI Calculation:       Front 21.4% · Back 39.8% (within HELOC policy)
                       Note: DTI uses unverified income — will recalc
                       after W-2 receipt
Credit Pull:           FICO 742 (within LOW tier)
Property Valuation:    Appraisal scheduled Jun 10 (Heartland Valuation)
OFAC Re-screen:        ✓ Clear
Source of Funds:       N/A (no member contribution)

──────── MISSING DOC ROUTING ────────
Item:                  2024 W-2 (employer: St Joseph Regional)
Notification Sent:     ✓ CWAnyWhere push + email at 2026-05-30 09:42 ET
Reminder #1:           ✓ Sent 2026-06-01 09:00 ET
Reminder #2:           Scheduled 2026-06-04 09:00 ET
Escalation:            Branch officer call follow-up scheduled 2026-06-08

──────── PACKET CONFIDENCE ────────
Completeness:          94% (1 of 16 required docs missing)
Extracted accuracy:    96.7% across 15 received documents

──────── DECISION TIMELINE ────────
Submitted:             2026-05-30 08:14:18 ET
Extraction complete:   2026-05-30 08:18:42 ET
Missing-doc flagged:   2026-05-30 09:41 ET (auto-routed to HITL queue)
Status:                PENDING member upload + appraisal

──────── HAND-OFF NOTES ────────
→ Vendor Agent:        Heartland Valuation engaged (appraisal SOW)
→ Member:              CWAnyWhere reminder cycle active
→ Underwriter:         Queue position: hold until W-2 + appraisal complete

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/credit_risk/heloc/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-30-08:14:18-LN-0441
HITL Status:           IN QUEUE · Priority MEDIUM · Wait 5d 6h
`,

  cwfcu_loan_mortgage_patel: `LOAN APPLICATION PACKET — MORTGAGE
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Loan Reference:        LN-2026-0438
Application Channel:   Encompass LOS adapter (CWFCU mortgage workflow)
Submitted:             2026-05-29 10:08:42 ET
Processing Agent:      Loan Document Agent · v2.4.1
Decision Status:       APPROVED · CLOSED · FUNDED 2026-06-04

──────── APPLICANT ────────
Member Number:         #62411
Legal Name:            PATEL, Anita Vinayak
Date of Birth:         1984-07-08 (41)
Address (current):     2104 Riverview Dr, South Bend, IN 46614 (will sell)
Employer:              Indiana University Health · Physician, Internal Med (8 years)
Annual Income:         $245,000 (W-2 verified)
Co-applicant:          PATEL, Anand (spouse) · IT consultant · $112K
CIP On File:           ✓ (member since 2017-09-11)
Risk Tier:             LOW

──────── LOAN REQUEST ────────
Type:                  Mortgage (purchase)
Amount Requested:      $215,000 (purchase $278,400 · down $63,400)
Term:                  30-year fixed
Rate (locked):         6.75% APR (rate-lock 2026-05-29 to 2026-07-29)
Use of Funds:          Purchase principal residence

──────── COLLATERAL ────────
Property:              4814 Briarwood Ln, Granger, IN 46530
Type:                  Single-family residence (3BR/3BA, built 1998)
Purchase Price:        $278,400
Appraisal Value:       $282,000 (Lakeside Appraisal · 2026-05-25)
LTV:                   76.2%

──────── DOCUMENTATION (32 items, all complete) ────────
Loan Application URLA:       ✓
2 yrs W-2 (2023, 2024):      ✓
2 yrs Tax Returns:           ✓
60-day Paystubs:             ✓ (5 paystubs, both applicants)
Bank Statements (90d):       ✓ (CWFCU + Notre Dame FCU verified)
Credit Report:               ✓ FICO 782 (LOW tier)
Property Appraisal:          ✓ $282K
Title Insurance:             ✓ Indiana Title Co
HOI Binder:                  ✓ State Farm
Flood Cert:                  ✓ Not in flood zone
Purchase Agreement:          ✓ Signed
Earnest Money Receipt:       ✓ $5,000
Source-of-Funds (down):      ✓ CWFCU share-savings + Notre Dame FCU
                             ✓ Schedule SOF questionnaire signed
Survey:                      ✓ (Heritage Surveying)
Termite Inspection:          ✓ Clear
HOA Doc Review:              ✓ Briarwood HOA dues $42/mo
Real Estate Settlement (RESPA): ✓
TRID Disclosures:            ✓ All three required
Verification of Employment:  ✓ IU Health HR + IT consulting client
Mortgage Insurance:          N/A (LTV < 80%)

──────── AGENT VALIDATION ────────
Income Verification:   PASS (W-2 + paystub + VOE 100% match)
DTI Calculation:       Front 32.1% · Back 38.4%
                       Within QM safe-harbor (≤ 43%)
Credit Pull:           FICO 782 · No derogatory items
Collateral:            Appraisal supports purchase ($282K vs $278.4K)
OFAC Re-screen:        ✓ Clear (both applicants)
Source of Funds:       ✓ Verified from CWFCU + Notre Dame
ATR/QM Compliance:     ✓ Qualified Mortgage · 8 ATR factors verified
Fair Lending Check:    ✓ Comparator analysis · within policy

──────── EXTRACTION CONFIDENCE ────────
Per-document confidence (n=32):
  Min:    91.2% (HOA bylaws, scanned PDF)
  Max:    99.6% (URLA, fillable form)
  Mean:   94.7%
Overall packet confidence: 94.1% (target ≥ 92%)

──────── DECISION TIMELINE ────────
Submitted:             2026-05-29 10:08:42 ET
Packet ingested:       2026-05-29 10:09:18 ET (36 sec)
Extraction complete:   2026-05-29 10:42:11 ET (33 min · 32 docs)
Validation complete:   2026-05-29 10:48:33 ET (6 min)
Auto-approval:         2026-05-29 10:48:42 ET
Routed to Underwriter: 2026-05-29 10:49 ET
Underwriter Approve:   2026-05-30 14:18 ET
Clear to Close:        2026-06-02 09:42 ET
Closing:               2026-06-04 14:00 ET
Funded:                2026-06-04 16:18 ET
Total Cycle Time:      6 days 6 hrs (target ≤ 10 days)

──────── HAND-OFF NOTES ────────
→ Vendor Agent:        Lakeside Appraisal SOW · Indiana Title Co contract
                       both linked to vendor risk register Q2 review
→ Member Onboarding:   Spouse Anand Patel added as joint member (linked)
→ Compliance:          Source-of-funds doc indexed to BSA folder

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/credit_risk/mortgage/2026-Q2/
Immutable Audit ID:    AUDIT-2026-05-29-10:08:42-LN-0438
HMDA Reportable:       YES · LAR Code 1 (Conv. 30yr · approved)
HMDA Filing Queue:     Q2 2026 batch (filing Jul 2026)
`,

  cwfcu_loan_personal_williams: `LOAN APPLICATION PACKET — PERSONAL
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Loan Reference:        LN-2026-0517
Application Channel:   CWAnyWhere mobile app
Submitted:             2026-06-02 19:08:33 ET
Processing Agent:      Loan Document Agent · v2.4.1
Decision Status:       IN PROGRESS · 62% packet complete

──────── APPLICANT ────────
Member Number:         #38914
Legal Name:            WILLIAMS, Darnell J.
Date of Birth:         1993-02-22 (33)
Address:               1944 W Ireland Rd, South Bend, IN 46614
Employer:              Self-employed · Williams Photography LLC
Annual Income:         $52,400 (Schedule C, self-reported)
CIP On File:           ✓ (member since 2022-11-14)
Risk Tier:             MEDIUM (self-employed, income volatility)

──────── LOAN REQUEST ────────
Type:                  Personal (unsecured)
Amount Requested:      $12,500
Term:                  36 months
Rate (offered):        9.95% APR
Use of Funds:          Equipment purchase (camera + lighting)

──────── DOCUMENTATION (8 of 13 received) ────────
Loan Application:      ✓
Indiana DL:            ✓ Verified (expires 2027-02-22)
2025 Tax Return:       ✗ NOT RECEIVED ← BLOCKER
2024 Tax Return:       ✓ Schedule C ($48,200 net)
2026 YTD P&L:          ✓ Self-prepared (Quickbooks export)
Bank Statements (90d): ✓ CWFCU verified
Credit Pull:           ✓ FICO 684 (MEDIUM tier · 660-719)
Business License:      ✓ Indiana SOS
Equipment Quote:       ✓ B&H Photo ($14,200 itemized)
2 most recent paystubs: N/A (self-employed)
Schedule SE:           ✗ NOT RECEIVED ← Recommended
Insurance (business):  ✗ NOT REQUIRED FOR THIS LOAN
References:            ✓ 2 client invoices on file

──────── AGENT VALIDATION (in progress) ────────
Income Verification:   PARTIAL (Schedule C 2024 + Q1 2026 P&L only)
                       ─ 2025 tax return required to confirm income trend
DTI Calculation:       Estimated Front 14.2% · Back 31.4% (under unverified)
                       Will recalc with 2025 return
Credit Pull:           FICO 684 (within MEDIUM tier)
Source of Funds:       Personal loan · no member SOF required
OFAC Re-screen:        ✓ Clear

──────── MISSING DOC ROUTING ────────
Item #1:               2025 Tax Return (Form 1040 + Schedule C)
Notification:          ✓ Sent CWAnyWhere 2026-06-02 19:42 ET
Reminder #1:           Scheduled 2026-06-04 09:00 ET
Item #2:               Schedule SE (recommend self-employment tax doc)
Notification:          Bundled with item #1 reminder

──────── PACKET CONFIDENCE ────────
Completeness:          62%
Extracted accuracy:    93.2% across 8 received documents

──────── DECISION TIMELINE ────────
Submitted:             2026-06-02 19:08:33 ET
Extraction complete:   2026-06-02 19:14:08 ET
Missing-doc flagged:   2026-06-02 19:42 ET
Status:                IN PROGRESS (member upload pending)

──────── HAND-OFF NOTES ────────
→ Member:              Encouraged to upload via CWAnyWhere
→ Compliance Agent:    Self-employed flag → routine SOF check on disbursement
→ Underwriter:         Hold until missing docs received

──────── NCUA EXAM FOLDER INDEX ────────
Folder Path:           ncua-exam-2026/credit_risk/personal/2026-Q2/
Immutable Audit ID:    AUDIT-2026-06-02-19:08:33-LN-0517
HITL Status:           IN QUEUE · Priority LOW · Wait 36 hrs
`,

  cwfcu_paystub_nguyen: `PAYSTUB · EXTRACTION REFERENCE
═══════════════════════════════════════════════════════════════
Supporting document for self-employed CDD case
═══════════════════════════════════════════════════════════════

Source Document:       NGUYEN Tax Services LLC — Member draw statement
Document Type:         Self-employment income summary
Reference Period:      May 1 — May 31, 2026
Extracted By:          Loan Document Agent · v2.4.1

──────── HEADER ────────
Filer / Member:        Nguyen, Tuan K.  (Member #29402)
SSN:                   XXX-XX-8814
Entity:                Nguyen Tax Services LLC (Indiana)
EIN:                   XX-3947112
Pay Period:            2026-05-01 → 2026-05-31

──────── EARNINGS ────────
Gross Receipts:        $14,820.00
─ Tax prep fees:       $11,200 (43 returns @ $260 avg)
─ Advisory fees:       $2,400 (8 consultations @ $300)
─ Bookkeeping retainers: $1,220 (2 clients monthly)

Operating Expenses:    $4,418.00
─ Office rent:         $1,850
─ Software (TaxWise + QBO):  $618
─ Marketing:           $200
─ Vehicle/Travel:      $1,750

Net Self-Employment Income: $10,402.00

──────── YTD SUMMARY (2026 through May 31) ────────
Gross YTD:             $74,200.00
Expenses YTD:          $22,090.00
Net YTD:               $52,110.00 (annualized $125,064)

──────── BANK DEPOSIT LINK ────────
Linked Deposits to CWFCU Account #29402:
  ─ 2026-05-04 · $5,200 (5 client checks batch)
  ─ 2026-05-11 · $3,400 (tax-prep batch)
  ─ 2026-05-18 · $4,700 (bookkeeping + 2 returns)
  ─ 2026-05-25 · $1,520 (final May intake)
  Total deposited: $14,820.00 (100% match to gross receipts)

──────── AGENT VALIDATION ────────
Cross-reference:       ✓ Deposits match gross receipts (100%)
Source consistency:    ✓ Tax prep fees consistent w/ Schedule C 2024
Anomaly flags:         None
Trend:                 +6.4% YoY growth (consistent w/ stated business)

──────── HAND-OFF NOTES ────────
→ Compliance Agent:    Cash deposit pattern consistent — no SAR concern
→ Use case:            Self-employment income verification for any
                       future loan / HELOC application from Member #29402
`,

  cwfcu_contract_fiserv: `VENDOR CONTRACT · CORE BANKING SERVICES
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
NCUA Third-Party Risk Register Entry
═══════════════════════════════════════════════════════════════

Contract ID:           VND-FISERV-CORE-2024
Vendor:                Fiserv Solutions LLC  (Brookfield, WI)
Vendor Tier:           CRITICAL (Tier 1)
Service Category:      Core Banking Platform (Cleartouch / DNA)
Vendor Risk Score:     38 / 100 (LOW · long-relationship + strong SLAs)

────────  CONTRACT TERMS  ────────
Effective:             2024-07-01
Initial Term:          2 years (2024-07-01 → 2026-07-01)
Renewal Window:        2026-06-04 → 2026-06-30 (30-day notice)
Auto-Renewal:          YES — 24 months unless 30-day notice provided
                       ⚠ Notice deadline TODAY (Jun 4, 2026)
Annual Value:          $2,100,000 / yr
Total Contract Value:  $4,200,000 (initial) → $4,830,000 (proposed)
Rate Escalator:        +3% / yr cap (per § 11.2)
Termination for Cause: 30-day notice + cure period

────────  SLA SUMMARY  ────────
Uptime Guarantee:      99.95% (4 hr 22 min/mo max downtime)
P1 Response:           1 hour
P2 Response:           4 hours
Performance Credits:   Up to 10% of monthly fee for breach
Data Recovery (DR):    RTO 4 hr · RPO 1 hr (full DR test annual)

────────  PERFORMANCE Q2 2026  ────────
Uptime:                99.97% (target ✓)
P1 Incidents:          0 (target ≤ 2/qtr ✓)
P2 Incidents:          3 (target ≤ 8/qtr ✓)
Average Ticket TTR:    2.4 hrs (target ≤ 4 hrs ✓)
SLA Breaches YTD:      0
Credits Owed:          $0

────────  RATE DRIFT MONITORING ────────
Contracted Rate:       +3.0% annual cap
Q2 2026 Billed:        $185,400 / month (was $175,200 baseline)
Drift:                 +5.8% vs baseline (+2.8 pts over cap)
Estimated Exposure:    $58,200 / yr if uncontested
Renewal Negotiation:   Open · CW FCU position: cap @ +2% or no renewal

────────  POLICY OBLIGATIONS TRIGGERED  ────────
1. Annual InfoSec Cert (per § 7.4):
   ─ All 84 employees with CWFCU credentials must complete
   ─ Current completion: 78 / 84 (93%)
   ─ Hand-off → Policy & HR Agent for ack tracking

2. Annual BSA Training Refresher (per § 9.1):
   ─ Required for employees touching Fiserv member-data systems
   ─ Current completion: 62 / 84 (74%) ← NCUA exam attention item
   ─ 22 employees overdue · auto-reminder cycle active

3. Vendor Data Residency Attestation (per § 14.3):
   ─ Annual board attestation of data residency
   ─ Board resolution BOARD-RES-2026-04 (in progress)
   ─ Awaiting 2 of 7 board signatures

────────  KEY RENEWAL CONSIDERATIONS  ────────
If APPROVE today:
  ─ Rate locked +2.4% (vs current escalator +3%)
  ─ 2-yr term locked through 2028-07-01
  ─ Negotiated SLA tightened (P1 → 30 min, was 1 hr)
  ─ Estimated 2-yr savings vs auto-renewal: $116K

If DELAY 30 days:
  ─ Auto-renewal triggers at standard escalator +5.8%
  ─ Lost negotiation leverage on rate cap
  ─ Estimated 2-yr cost increase: $76K higher
  ─ NCUA exam: potential vendor mgmt finding (no TPRM refresh)

If REPLACE:
  ─ Migration cost estimated $1.4M
  ─ 6-9 month implementation timeline
  ─ Member impact: temporary down during cutover
  ─ NOT RECOMMENDED for this cycle

────────  HAND-OFF NOTES  ────────
→ Compliance Agent:    Data residency attestation indexed to BSA folder
→ Loan Document Agent: No direct loan impact
→ Policy & HR Agent:   BSA training + InfoSec acks tracked separately

────────  NCUA EXAM FOLDER INDEX  ────────
Folder Path:           ncua-exam-2026/third_party_risk/critical_vendors/
Immutable Audit ID:    AUDIT-2024-07-01-12:00:00-VND-FISERV-CORE
TPRM Refresh Due:      2026-06-30 · pending decision
`,

  cwfcu_contract_eltropy: `VENDOR CONTRACT · MEMBER ENGAGEMENT (CHATBOT)
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Contract ID:           VND-ELTROPY-CDUBS-2025
Vendor:                Eltropy Inc.  (Milpitas, CA)
Vendor Tier:           HIGH (Tier 2 · member-facing)
Service Category:      C-Dubs Chatbot (digital member engagement)
Vendor Risk Score:     42 / 100 (MEDIUM)

────────  CONTRACT TERMS  ────────
Effective:             2024-07-15
Initial Term:          2 years (2024-07-15 → 2026-07-15)
Renewal Window:        2026-05-15 → 2026-07-15
Auto-Renewal:          NO (explicit renewal required)
Notice Required:       60 days
Notice Deadline:       2026-05-15 (passed — in negotiation)
Current Annual Value:  $180,000 / yr
Proposed Renewal:      $192,000 / yr (+6.7%) · 2-yr term
Rate Escalator:        +3% / yr cap

────────  SLA SUMMARY  ────────
Uptime:                99.90% guaranteed
Response Time (P95):   ≤ 200 ms
P1 Response:           2 hours
Performance Credits:   5% of monthly fee for first SLA miss

────────  PERFORMANCE Q2 2026  ────────
Uptime:                99.94% (target ✓)
P95 Response Time:     208 ms (target 200 ms — minor breach)
P1 Incidents:          0
P2 Incidents:          2
SLA Breaches YTD:      1 (Jun 1, 2026 · 38 min P95 elevation · credit applied)

────────  RATE DRIFT MONITORING  ────────
Contracted Rate:       +3.0% cap
Q2 2026 Billed:        $15,150 / mo (was $14,520)
Drift:                 +4.2% over baseline (+1.2 pts over cap)
Estimated Exposure:    $7,560 / yr if uncontested

────────  POLICY OBLIGATIONS TRIGGERED  ────────
1. Data Residency Clause (§ 12.4):
   ─ All member chat transcripts stored in US-only region
   ─ Annual board attestation required
   ─ Status: PENDING — board action requested at Jun 17 meeting

2. PII Handling Training (§ 8.2):
   ─ Member-services staff (24 employees) annual cert
   ─ Status: 24/24 complete

────────  MEMBER METRICS Q2 2026  ────────
Active C-Dubs Sessions:   18,400 / mo (+14% YoY)
Auth Success Rate:        78%
Digital Containment:      62% (resolved without agent transfer)
Member NPS (chat):        61 (industry avg 52)

────────  HAND-OFF NOTES  ────────
→ Policy & HR Agent:   Annual PII training acks current
→ Compliance Agent:    Data residency attestation queued for board

────────  NCUA EXAM FOLDER INDEX  ────────
Folder Path:           ncua-exam-2026/third_party_risk/tier2_vendors/
Immutable Audit ID:    AUDIT-2024-07-15-12:00:00-VND-ELTROPY
`,

  cwfcu_contract_coop: `VENDOR CONTRACT · SHARED BRANCH NETWORK
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Contract ID:           VND-COOP-SHARED-2023
Vendor:                CO-OP Financial Services  (Rancho Cucamonga, CA)
Vendor Tier:           HIGH (Tier 2 · member-facing)
Service Category:      Shared Branching Network + Card Processing
Vendor Risk Score:     35 / 100 (LOW)

────────  CONTRACT TERMS  ────────
Effective:             2023-04-01
Initial Term:          3 years (2023-04-01 → 2026-04-01)
Auto-Renewal:          YES (1 year increments, opt-out 60d notice)
Status:                AUTO-RENEWED on 2026-04-01 → 2027-04-01
Annual Value:          $432,000 / yr
Rate Escalator:        +2.5% / yr cap

────────  SLA SUMMARY  ────────
Uptime:                99.85%
Card Auth Response:    ≤ 800 ms
Performance Credits:   Standard CUSO terms

────────  PERFORMANCE Q2 2026  ────────
Uptime:                99.91% (target ✓)
Card Auth (P95):       412 ms (target 800 ms ✓)
Shared-branch txns:    11,800 / mo from CW members at other CUs
Reciprocal txns:       9,200 / mo at CW branches from other CUs
P1 Incidents:          1 (Jun 2 · 2-hr regional outage IN/MI · credit $850)
SLA Breaches YTD:      1 (above incident)

────────  RATE DRIFT MONITORING  ────────
Contracted Rate:       +2.5% cap
Q2 2026 Billed:        $36,800 / mo (was $36,000)
Drift:                 +2.2% over baseline (within cap)
Status:                ✓ COMPLIANT

────────  POLICY OBLIGATIONS  ────────
1. Annual Network Security Cert (§ 6.1) — 6 IT staff acks · COMPLETE
2. PCI-DSS Attestation (§ 7.3) — annual · COMPLETE
3. Disaster Recovery Joint Test (§ 11.4) — annual · last Mar 2026 (PASS)

────────  HAND-OFF NOTES  ────────
→ Policy & HR Agent:   Network sec cert + PCI acks current
→ Loan Document Agent: No direct loan impact

────────  NCUA EXAM FOLDER INDEX  ────────
Folder Path:           ncua-exam-2026/third_party_risk/tier2_vendors/
Immutable Audit ID:    AUDIT-2023-04-01-12:00:00-VND-COOP-SHARED
`,

  cwfcu_contract_diebold: `VENDOR CONTRACT · ATM SERVICES + CASSETTE LOGISTICS
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
═══════════════════════════════════════════════════════════════

Contract ID:           VND-DIEBOLD-ATM-2024
Vendor:                Diebold Nixdorf Inc.  (North Canton, OH)
Vendor Tier:           HIGH (Tier 2 · physical operations)
Service Category:      ATM Hardware + Cassette Logistics + Maintenance
Vendor Risk Score:     40 / 100 (LOW)

────────  CONTRACT TERMS  ────────
Effective:             2024-09-15
Initial Term:          3 years (2024-09-15 → 2027-09-15)
Auto-Renewal:          NO (RFP / re-bid required)
Annual Value:          $353,000 / yr
Coverage:              12 ATMs (4 branch + 8 standalone)
Rate Escalator:        +3.5% / yr cap

────────  SLA SUMMARY  ────────
ATM Uptime:            99.96% per machine
Cash Replenishment:    Same-day for branch ATMs, next-day for standalone
Maintenance Response:  4 hr P1, 24 hr P2
Performance Credits:   Per-ATM per-hour-downtime credits

────────  PERFORMANCE Q2 2026  ────────
ATM Uptime:            99.96% (avg across 12 ATMs)
Avg Ticket TTR:        1.8 hrs (target 4 hr ✓)
P1 Incidents:          0
P2 Incidents:          5 (paper jams, card-reader cleanings · routine)
SLA Breaches YTD:      0

────────  CASSETTE LOGISTICS ────────
Cash Cycles / Month:   28 (branch ATMs · 2x weekly)
                       16 (standalone ATMs · 1x weekly)
Cash Insurance:        $750K per location (Berkshire commercial)
Dual-Control:          Enforced (CW + Diebold custodian present)

────────  POLICY OBLIGATIONS TRIGGERED  ────────
1. Annual Cash-Handling Training (§ 7.2 + CWFCU policy P-OPS-227):
   ─ 14 employees handle ATM cassette logistics
   ─ Current ack status: 12 / 14 (86%) ← 2 overdue
   ─ Hand-off → Policy & HR Agent (in queue)

2. Quarterly Key-Custodian Acknowledgment Refresh (§ 9.4):
   ─ 4 custodians (1 per branch)
   ─ Q2 2026 status: 4 / 4 acknowledged · COMPLETE

3. Annual Third-Party Security Training (§ 11.1):
   ─ All 84 CW employees · 78 / 84 complete (93%)

────────  HAND-OFF NOTES  ────────
→ Policy & HR Agent:   P-OPS-227 ack tracking · 2 overdue tellers
→ Compliance Agent:    Cash insurance + dual-control logged BSA folder

────────  NCUA EXAM FOLDER INDEX  ────────
Folder Path:           ncua-exam-2026/third_party_risk/tier2_vendors/
Immutable Audit ID:    AUDIT-2024-09-15-12:00:00-VND-DIEBOLD
`,

  cwfcu_policy_bsa_roster: `POLICY ACKNOWLEDGMENT ROSTER — BSA/AML TRAINING 2026
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
Policy: P-COMP-201 (BSA/AML Updated Procedures · Annual)
Reporting Period: 2026 Annual Training Cycle
═══════════════════════════════════════════════════════════════

Tracking Source:       APEX Policy & HR Agent · v2.4.1
Generated:             2026-06-04 09:00 ET (daily refresh)
NCUA Exam Folder:      ncua-exam-2026/hr_policy/training_records/2026/

──────── PROGRAM SUMMARY ────────
Total Employees:       84
Completed:             62 (74%)
Outstanding:           22
Original Deadline:     2026-05-31
Reminders Sent:        2 rounds (May 31 + Jun 3)
Escalation Trigger:    Jun 10 (to dept managers)
Final Deadline:        2026-07-15 (NCUA exam window opens Jul 21)

──────── COMPLETED (62) — BY DEPARTMENT ────────
Lending (12 of 12 · 100%):
  ✓ Patel, A.  ✓ Mendez, C.  ✓ Greene, J.  ✓ Holloway, M.  ✓ Singer, K.
  ✓ Patel, S.  ✓ Williams, A. ✓ Chen, R.   ✓ Rosales, E.  ✓ Brown, P.
  ✓ Garcia, T. ✓ Johnson, L.

Operations (24 of 24 · 100%):
  ✓ Rodriguez, M. ✓ Okafor, A. ✓ Walsh, B. ✓ Park, J. ✓ + 20 others

Member Services (23 of 24 · 96%):
  ✓ 23 acknowledged
  ✗ 1 OUTSTANDING: Carter, R.

IT / InfoSec (6 of 6 · 100%):
  ✓ Vargas, D. ✓ Singh, R. ✓ + 4 others

Compliance (4 of 4 · 100%):
  ✓ Williams, A. ✓ Bryant, N. ✓ Kim, M. ✓ Lopez, F.

Branch (Tellers, 9 of 14 · 64%):
  ✓ 9 acknowledged · 5 OUTSTANDING

Collections (2 of 2 · 100%)
Executive (5 of 5 · 100%)

──────── OUTSTANDING (22) — BY DEPARTMENT ────────
Member Services (1):
  ✗ Carter, R. (Member Rep · South Bend)

Branch / Tellers (18) — HIGHEST RISK ROLE:
  ✗ Murphy, K. (Teller · South Bend)
  ✗ Diaz, L. (Teller · South Bend)
  ✗ Thompson, B. (Teller · Mishawaka)
  ✗ Watson, T. (Teller · Mishawaka)
  ✗ Hernandez, R. (Teller · Mishawaka)
  ✗ Webb, K. (Teller · Mishawaka)
  ✗ Olsen, P. (Teller · Granger)
  ✗ Reilly, S. (Teller · Granger)
  ✗ Powell, J. (Teller · Granger)
  ✗ Coleman, D. (Teller · Granger)
  ✗ Stewart, J. (Teller · Elkhart)
  ✗ Adams, B. (Teller · Elkhart)
  ✗ Carlson, M. (Teller · Elkhart)
  ✗ Edwards, T. (Teller · Elkhart)
  ✗ Quintero, A. (Teller · Elkhart)
  ✗ Howard, J. (Sr Teller · South Bend)
  ✗ Hayes, D. (Sr Teller · Mishawaka)
  ✗ Bell, S. (Sr Teller · Granger)

Loan Officers (2):
  ✗ Reeves, A.  ✗ Bostick, T.

Collections (1):
  ✗ Pearson, M.

──────── REMINDER STATUS ────────
Cycle 1 sent:          2026-05-25  (early notice · 32 outstanding)
Cycle 2 sent:          2026-05-31  (deadline · 28 outstanding)
Cycle 3 sent:          2026-06-03  (overdue · 22 outstanding)
Cycle 4 scheduled:     2026-06-10  (manager escalation)
Final escalation:      2026-06-17  (to VP Operations · Rodriguez, M.)
Forecast completion:   18/22 by Jun 10 · 22/22 by Jun 17 (per pace model)

──────── NCUA EXAM IMPACT ────────
Policy & HR contribution to NCUA exam readiness: 88%
This roster's contribution if all 22 complete: +9 pts → 97%
Required by NCUA exam window: ALL 22 complete by Jul 15

──────── HAND-OFF NOTES ────────
→ Compliance Agent:    Notified · BSA program effectiveness depends on 100%
→ Branch Managers:     CC'd on Jun 10 escalation
→ HR Director:         Final escalation Jun 17 (if needed)

──────── AUDIT TRAIL ────────
Each acknowledgment: DocuSign signature + IP + timestamp + module score
Module pass score:   ≥ 80% (12 of 15 questions)
Avg score (62 complete): 91.4%
Avg time-to-complete:    47 min (target 45-60 min)
`,

  cwfcu_board_res_vendor_mgmt: `BOARD RESOLUTION — VENDOR MANAGEMENT POLICY ADOPTION
═══════════════════════════════════════════════════════════════
CommunityWide Federal Credit Union  ·  South Bend, Indiana
Board of Directors · Resolution Reference: BOARD-RES-2026-04
═══════════════════════════════════════════════════════════════

Tracking Source:       APEX Policy & HR Agent · v2.4.1
Indexed:               2026-04-18 (board meeting date)
NCUA Exam Folder:      ncua-exam-2026/hr_policy/board_resolutions/

──────── RESOLUTION TEXT ────────
WHEREAS, the Board of Directors of CommunityWide Federal Credit Union
("CommunityWide FCU" or the "Credit Union") has reviewed proposed
updates to the Credit Union's Vendor Management Policy ("Policy") to
align with NCUA's 2026 Supervisory Priorities Letter, FFIEC IT Examination
Handbook (June 2024 update), and the Credit Union's expanded use of
third-party AI agents for compliance support; and

WHEREAS, the proposed Policy has been reviewed by the Credit Union's
Audit Committee, Legal Counsel, and Compliance Officer; and

WHEREAS, the proposed Policy strengthens third-party risk management
through APEX-supported continuous monitoring, automated SLA reporting,
quarterly Tier 1 vendor reviews, and annual board attestation of all
Tier 1 and Tier 2 vendor risk assessments;

NOW THEREFORE BE IT RESOLVED, that the Board of Directors hereby:

  1. ADOPTS the updated Vendor Management Policy (the "2026 Vendor
     Management Policy"), effective May 1, 2026;

  2. AUTHORIZES the Chief Executive Officer to designate the Director
     of Compliance as Vendor Risk Officer responsible for execution
     of the Policy;

  3. DIRECTS that APEX Vendor & Contract Agent maintain continuous
     monitoring of all 47 active vendor contracts, with quarterly
     scorecards delivered to the Audit Committee;

  4. REQUIRES annual board attestation of Tier 1 vendor risk dossiers
     (currently: Fiserv, CO-OP, Diebold, Eltropy) before NCUA exam
     window opens each year;

  5. RATIFIES the use of APEX agent-generated SAR narratives,
     CTR auto-filings, and CDD reviews, with the understanding that
     final filing decisions remain with the BSA Officer.

──────── BOARD SIGNATORIES ────────
Required (7 board members):
  ✓ Hernandez, R.       Board Chair                 SIGNED 2026-04-19
  ✓ Coleman, T.         Vice Chair                  SIGNED 2026-04-19
  ✓ Wexler, P.          Treasurer                   SIGNED 2026-04-20
  ✓ Lin, K.             Secretary                   SIGNED 2026-04-21
  ✓ Chen, A.            Director (Member)           SIGNED 2026-04-22
  ✗ Patel, S.           Director (At-large)         PENDING
  ✗ Whitmore, E.        Director (Community Rep)    PENDING

Status:                5 of 7 signatures collected
Target Completion:     Jun 17, 2026 board meeting (next regular)

──────── REMINDER STATUS ────────
Cycle 1 sent:          2026-04-22 (DocuSign)
Cycle 2 sent:          2026-05-29 (DocuSign + email + phone)
Cycle 3 sent:          2026-06-01 (escalation to Board Chair)
Forecast completion:   By Jun 17, 2026 meeting (confirmed by Chair)

──────── NCUA EXAM IMPACT ────────
Policy & HR contribution: This resolution closes 2 NCUA attention items:
  ─ Updated vendor risk management policy (NCUA 2026 priority #4)
  ─ Board-level attestation of Tier 1 vendor reviews

Critical: Must be fully executed before NCUA exam window opens Jul 21.

──────── HAND-OFF NOTES ────────
→ Vendor Agent:       Resolution adoption confirmed · executing per § 3
→ Compliance Agent:   APEX usage in BSA workflow ratified (per § 5)
                      Indexed to BSA/AML folder
→ Board Chair:        Reminded to circulate at Jun 17 meeting

──────── AUDIT TRAIL ────────
Resolution drafted:    2026-04-12 by Legal Counsel (Bryant, N.)
Board meeting:         2026-04-18 (in-person, South Bend HQ)
Motion proposed:       Coleman, T. (Vice Chair)
Motion seconded:       Wexler, P. (Treasurer)
Vote outcome:          7 yes · 0 no · 0 abstain
Effective:             2026-05-01
Immutable Audit ID:    AUDIT-2026-04-18-14:42:08-BOARD-RES-04
`,
  /* ─── BOLER · 14 sample files ─── */
  boler_cigna_medical: `CIGNA HEALTHCARE — MEDICAL PREMIUM INVOICE
═══════════════════════════════════════════════════════════════
Group:           The Boler Company (Master Group #4421-887)
Period:          June 1-30, 2026
Statement Date:  May 28, 2026 · Due Jun 15, 2026
Carrier Contact: Patricia Reyes · cigna_groups@cigna.com

─────────────── SUMMARY ───────────────
Total Premium:     $1,284,320.00
Total Lives:       847 employees (612 medical-only · 235 with dependents)
Allocation Period: June 2026 (premium month)
Average per EE:    $1,516.32

─────────────── DIVISION BREAKDOWN ───────────────
Hendrickson Intl       412 EE × avg $1,725 = $710,800.00 (55.4% of total)
Boler Mfg Services     156 EE × avg $1,600 = $249,600.00 (19.4%)
Boler Holdings         124 EE × avg $1,600 = $198,400.00 (15.4%)
Boler Real Estate       89 EE × avg $713   = $63,440.00  (4.9%)
Corporate/Shared        66 EE × avg $941   = $62,080.00  (4.8%)

─────────────── COVERAGE TIER BREAKDOWN ───────────────
EE-only PPO         412 employees × $637/mo  = $262,444 (contract rate $612 · +4.1%)
EE+Spouse PPO       183 employees × $1,195   = $218,685 (contract rate $1,148 · +4.1%)
EE+Children PPO     108 employees × $1,053   = $113,724 (contract rate $1,012 · +4.1%)
Family PPO          122 employees × $1,753   = $213,866 (contract rate $1,684 · +4.1%)
EE-only HDHP         22 employees × $483     = $10,626  (contract rate $464 · +4.1%)

⚠ RATE DRIFT NOTICE: Billed rates are +4.1% above contracted rate card.
   Contract: $612/$1,148/$1,012/$1,684/$464 (Apr 2024 - Jul 2026)
   Billed:   $637/$1,195/$1,053/$1,753/$483 (Jun 2026)
   Cumulative drift since Jan 2026: +4.1% (was +0.5% in January)
   APEX Signal Agent has flagged this for negotiation review.

─────────────── EXCEPTIONS ───────────────
Martinez, Laura (EMP-3312) appears in this invoice ($1,240/mo for EE+Spouse PPO)
AND in the Cigna COBRA billing file separately. Status: TERMINATED 04/30/2026.
→ Cross-flagged as EXC-2026-0442 by APEX Benefits Allocation Agent.

Chen, Robert (EMP-4821) listed under cost center 6200-001 (Hendrickson Intl)
BUT HRIS shows transferred to Boler Holdings (CC 6200-004) effective 05/15/2026.
→ Cross-flagged as EXC-2026-0441 by APEX Benefits Allocation Agent.

─────────────── REMITTANCE ───────────────
Payable to:   Cigna Health and Life Insurance Company
Method:        ACH to Cigna Premium Collections (acct ending 4421)
Reference:    BOLER-JUN26-MEDICAL
Cycle:         Monthly billing — auto-debit on file
`,

  boler_delta_dental: `DELTA DENTAL — GROUP PREMIUM INVOICE
═══════════════════════════════════════════════════════════════
Group:           The Boler Company (Group #DD-9928-412)
Period:          June 1-30, 2026
Statement Date:  May 28, 2026
Carrier Contact: Marcus Liu · groups@deltadental.com

─────────────── SUMMARY ───────────────
Total Premium:     $187,450.00
Total Lives:       831 employees (16 employees waived dental)
Average per EE:    $225.57

─────────────── DIVISION BREAKDOWN ───────────────
Hendrickson Intl       406 EE  $126,800.00
Boler Mfg Services     154 EE  $49,800.00
Boler Holdings         121 EE  $39,600.00
Boler Real Estate       87 EE  $28,400.00
Corporate/Shared        63 EE  $21,080.00
Adjustments              -     -$78,230.00 (16 waivers prorated)

─────────────── COVERAGE TIER ───────────────
EE-only PPO         598 employees × $208/mo  = $124,384
EE+Family PPO       233 employees × $271/mo  = $63,143
                                              ────────
                                              $187,527
Less wave-off credit: $77 → $187,450 net

─────────────── DRIFT NOTICE ───────────────
Rate drift this cycle: +1.8% above contract.
Contract rate (Apr 2024 - Jul 2026): $204/$266
Billed rate (Jun 2026):              $208/$271

Within tolerance band (+3% contracted cap). No Signal alert generated.
Trending: +1.8% over 6 months — monitor at next renewal.

─────────────── REMITTANCE ───────────────
Payable to:   Delta Dental of Illinois
Reference:    BOLER-JUN26-DENTAL
Method:        ACH (auto-debit on file)
`,

  boler_fidelity_401k: `FIDELITY INVESTMENTS — 401(k) EMPLOYER MATCH CONTRIBUTION
═══════════════════════════════════════════════════════════════
Plan:            The Boler Company 401(k) Retirement Plan
Plan #:          88-441208
Period:          June 1-30, 2026
Statement Date:  Jun 2, 2026
Plan Sponsor:    The Boler Company · EIN 36-XXXXXXX
Recordkeeper:    Fidelity Workplace Investing

─────────────── EMPLOYER MATCH SUMMARY ───────────────
Total Employer Match:    $412,880.00
Match Rate Applied:       4.5% of eligible compensation ⚠
Eligible Comp Base:       $9,175,111.11
Active Participants:      803 employees (44 not enrolled · auto-enroll opt-out)

─────────────── DIVISION BREAKDOWN ───────────────
Hendrickson Intl       388 EE  $167,000
Boler Mfg Services     149 EE  $79,200
Boler Holdings         119 EE  $63,000
Boler Real Estate       85 EE  $44,800
Corporate/Shared        62 EE  $33,200
                                ────────
                                $387,200
Catch-up + reconciliation:      $25,680
                                ────────
Total                           $412,880

─────────────── DISCREPANCY ALERT ───────────────
⚠ MATCH RATE MISMATCH

  Fidelity carrier file applies:    4.5%
  Boler HR policy (P-COMP-401K-2024): 4.0%
  Delta:                              0.5%

Financial impact at 4.5%: $412,880
Financial impact at 4.0%: $367,000
Monthly delta:             $45,880  (excludes catch-up/reconciliation)
Cycle-relevant delta:      $8,240   (per APEX calc — net of reconciliation)

Root cause options:
  1. Fidelity rate card auto-incremented (plan amendment Apr 2026?)
  2. HR policy was updated but not propagated to allocation system

→ Flagged as EXC-2026-0445 by APEX Benefits Allocation Agent.
→ Sarah Mitchell (Benefits Director) follow-up requested.

─────────────── CONTRIBUTION BREAKDOWN BY VESTING ───────────────
Fully vested (5+ years):      $312,400  (76% of total)
Partially vested:             $76,200   (18%)
Cliff-vested 3-yr:            $24,280   (6%)

─────────────── REMITTANCE ───────────────
Method:       ACH from Boler operating account → Fidelity Trust
Reference:    BOLER-401K-JUN26
Settlement:   T+1 (Jun 3, 2026)
`,

  boler_vsp_vision: `VSP VISION CARE — GROUP PREMIUM INVOICE
═══════════════════════════════════════════════════════════════
Group:           The Boler Company (VSP Group #VSP-08841)
Period:          June 1-30, 2026
Statement Date:  May 30, 2026

─────────────── SUMMARY ───────────────
Total Premium:     $62,140.00
Total Lives:       798 employees (49 employees waived vision)
Average per EE:    $77.87

─────────────── DIVISION BREAKDOWN ───────────────
Hendrickson Intl       391 EE  $38,200
Boler Mfg Services     150 EE  $15,720
Boler Holdings         120 EE  $12,480
Boler Real Estate       85 EE  $8,910
Corporate/Shared        62 EE  $6,610
Waiver adjust            -      -$19,780 (49 waivers credited)

─────────────── COVERAGE TIER ───────────────
EE-only Choice         574 employees × $58/mo  = $33,292
EE+Family Choice       224 employees × $134/mo = $30,016
                                                ────────
                                                $63,308
Wave-off credit: $1,168 → $62,140 net

─────────────── DRIFT NOTICE ───────────────
Rate drift this cycle: +0.2% above contract
Status: Well within tolerance. No Signal alert.

─────────────── REMITTANCE ───────────────
Payable to:   Vision Service Plan Insurance Co
Reference:    BOLER-JUN26-VISION
Method:        ACH
`,

  boler_hartford_life: `HARTFORD LIFE — GROUP TERM LIFE & AD&D INVOICE
═══════════════════════════════════════════════════════════════
Group:           The Boler Company (Hartford Policy #HL-44178)
Period:          June 1-30, 2026
Statement Date:  May 28, 2026

─────────────── SUMMARY ───────────────
Total Premium:     $98,760.00
Total Lives:       847 employees (full population — basic life is non-elective)
Average per EE:    $116.60

─────────────── DIVISION BREAKDOWN ───────────────
Hendrickson Intl       412 EE  $48,200
Boler Mfg Services     156 EE  $18,400
Boler Holdings         124 EE  $14,640
Boler Real Estate       89 EE  $10,520
Corporate/Shared        66 EE  $7,000

─────────────── COVERAGE TIERS ───────────────
Basic Life @ $50K     847 employees × $4.65/mo  = $3,938 (employer-paid)
Voluntary Life avg    624 employees × $98/mo    = $61,152 (employee-paid · payroll deducted)
Voluntary AD&D avg    412 employees × $52/mo    = $21,424 (employee-paid · payroll deducted)
Spouse/Child rider    298 employees × $42/mo    = $12,516 (employee-paid)
                                                  ────────
                                                  $99,030

Adjustments for 5 new hires (partial month): -$270 → $98,760 net

─────────────── DRIFT NOTICE ───────────────
Rate drift this cycle: +0.4% above contract.
Status: Within tolerance. No Signal alert.

─────────────── REMITTANCE ───────────────
Payable to:   Hartford Life and Accident Insurance
Reference:    BOLER-JUN26-LIFE
Method:        ACH (auto-debit)
`,

  boler_cigna_std_ltd: `CIGNA — SHORT-TERM + LONG-TERM DISABILITY INVOICE
═══════════════════════════════════════════════════════════════
Group:           The Boler Company (Disability Policy #CD-77182)
Period:          June 1-30, 2026
Statement Date:  May 30, 2026

─────────────── SUMMARY ───────────────
Total Premium:     $94,450.00
Total Lives:       847 employees (all employees auto-enrolled in STD; LTD opt-in)
Coverage Mix:      STD 100% · LTD 78%

─────────────── DIVISION BREAKDOWN ───────────────
Hendrickson Intl       412 EE  $46,200
Boler Mfg Services     156 EE  $17,640
Boler Holdings         124 EE  $14,040
Boler Real Estate       89 EE  $10,080
Corporate/Shared        66 EE  $6,490

─────────────── COVERAGE TIERS ───────────────
STD (66.7% / 26 wks)   847 × $52/mo  = $44,044
LTD (60% / Soc Sec int) 661 × $78/mo  = $51,558
Coverage adjustments:  -$1,152 (5 new hires partial month)
                                       ────────
                                       $94,450 net

─────────────── DRIFT NOTICE ───────────────
Rate drift this cycle: +0.6% above contract.
Status: Within tolerance.

─────────────── REMITTANCE ───────────────
Payable to:   Cigna Disability Group
Reference:    BOLER-JUN26-DISABILITY
Method:        ACH
`,

  boler_exc_chen: `APEX EXCEPTION RECORD · HIGH PRIORITY
═══════════════════════════════════════════════════════════════
The Boler Company · June 2026 Benefits Cycle
═══════════════════════════════════════════════════════════════

EXCEPTION ID:     EXC-2026-0441
Type:             Reclassification Error
Severity:         HIGH
Detection Time:   June 6, 2026 · 09:41:03 ET
Detection Agent:  Benefits Allocation Agent (BEN)
Status:           AWAITING CFO SIGN-OFF

─────────────── SUBJECT ───────────────
Employee Name:     Chen, Robert
Employee ID:       EMP-4821
Hire Date:         2018-03-14
Current Division:  Boler Holdings (effective 2026-05-15)
Carrier File Coding: Hendrickson Intl (INCORRECT)
Cost Center:       6200-001 → should be 6200-004
Job Title:         Senior Engineering Manager
Manager:           Patel, Anita (EMP-2104)

─────────────── DETECTION DETAIL ───────────────
Source Cross-References:
  • HRIS (Workday)     :  Boler Holdings (CC 6200-004) effective 2026-05-15
  • Cigna Medical      :  Hendrickson Intl (CC 6200-001) — MISMATCH
  • Delta Dental       :  Hendrickson Intl (CC 6200-001) — MISMATCH
  • Fidelity 401k       :  Hendrickson Intl (CC 6200-001) — MISMATCH
  • VSP Vision         :  Hendrickson Intl (CC 6200-001) — MISMATCH
  • Hartford Life      :  Hendrickson Intl (CC 6200-001) — MISMATCH
  • Cigna STD/LTD      :  Hendrickson Intl (CC 6200-001) — MISMATCH

All 6 benefit lines incorrectly allocated to Hendrickson Intl.

─────────────── FINANCIAL IMPACT ───────────────
Per-month misallocation:       $3,840.00
  • Cigna Medical (Family PPO):  $1,753.00
  • Delta Dental (Family):       $271.00
  • Fidelity 401k (match):        $1,420.00 (4.5% × $31,560 monthly comp)
  • VSP Vision (Family):          $134.00
  • Hartford Basic Life:           $4.65
  • Cigna STD/LTD:                $257.35

Catch-up (May 15-31 prorate):  $1,920.00 (16 days)
Annualized if not corrected:   $46,080.00

─────────────── RECOMMENDED ACTION ───────────────
  - REMOVE: Hendrickson Intl · Cost Center 6200-001 · $3,840/mo
  + ADD:    Boler Holdings · Cost Center 6200-004 · $3,840/mo

Effective date: 2026-05-15 (backdated to actual transfer date)
Catch-up adjustment: $1,920 prorate posted to June JE

─────────────── ROUTING ───────────────
  • Detected by:      Benefits Allocation Agent (96.1% confidence)
  • Routed to:        Exception Resolution Agent for HITL queue
  • Step Functions:   approval-workflow-v2.boler.us-east-1
  • Stage 1:          Sarah Mitchell (Benefits Director) — APPROVED 2026-06-05 09:22
  • Stage 2:          Ziggy Kravitz (CFO) — PENDING
  • Notification:     SES email + SNS push sent 2026-06-06 09:41
  • SLA:               24 hours (current age: 18 hrs · 6 hrs remaining)

─────────────── AUDIT TRAIL ───────────────
  2026-06-03 09:14:22 · Carrier file ingested
  2026-06-03 11:32:07 · HRIS cross-reference completed
  2026-06-03 11:32:14 · Mismatch detected (BEN)
  2026-06-05 09:22:14 · Stage 1 approved (Sarah Mitchell)
  2026-06-06 09:38:22 · Stage 2 notification sent (SES + SNS)
  2026-06-06 09:41:03 · Routed to CFO HITL queue

Storage: DynamoDB · partition=2026-06 · sort=EXC-0441
Encryption: KMS · CMK rotated quarterly
Retention: 7 years per Boler SOC 2 policy
`,

  boler_exc_martinez: `APEX EXCEPTION RECORD · HIGH PRIORITY
═══════════════════════════════════════════════════════════════
The Boler Company · June 2026 Benefits Cycle
═══════════════════════════════════════════════════════════════

EXCEPTION ID:     EXC-2026-0442
Type:             Duplicate Enrollment
Severity:         HIGH
Detection Time:   June 6, 2026 · 09:38:14 ET
Detection Agent:  Benefits Allocation Agent (BEN)
Status:           AWAITING CFO SIGN-OFF

─────────────── SUBJECT ───────────────
Employee Name:     Martinez, Laura
Employee ID:       EMP-3312
Hire Date:         2019-09-08
Termination Date:  2026-04-30
Last Division:     Boler Holdings (CC 6200-004)

─────────────── DETECTION DETAIL ───────────────
Cross-Reference:   Cigna Medical file + Cigna COBRA file

Source A: Cigna_Medical_Jun2026.csv
  Status:         ACTIVE
  Plan:            EE+Spouse PPO
  Premium:         $1,195/mo
  Cost Center:     6200-004 (Boler Holdings) — INVALID per HRIS

Source B: Cigna_COBRA_Jun2026.csv
  Status:         COBRA continuation
  Plan:            EE+Spouse PPO
  Premium:         $1,195/mo (self-pay)
  Coverage:        Through 2026-10-31 (6mo elected)

HRIS (Workday):    TERMINATED 2026-04-30 · severance package paid

─────────────── ANALYSIS ───────────────
Active medical billing of $1,240/mo (avg after Boler holdings allocation share)
is INVALID — terminated employees should not have employer-paid medical
allocated to corporate cost centers. COBRA continuation is self-pay only.

Likely root cause: Cigna's termination feed to APEX failed (last Tuesday's
batch) and the May 30 carrier file still includes Martinez. APEX detected
via Cigna COBRA cross-reference at intake on Jun 3.

─────────────── FINANCIAL IMPACT ───────────────
Per-month overcharge:          $1,240.00
Cycle-cumulative (Apr 30 → Jun 5):  $5,580.00 (5 weeks)
Annualized if not corrected:    $14,880.00

─────────────── RECOMMENDED ACTION ───────────────
  - REMOVE: Active Medical · $1,240/mo · Boler Holdings (INVALID)
  + COBRA is self-pay — remove from corporate allocation entirely

Effective date: 2026-05-01 (next billing cycle after termination)
Catch-up adjustment: $5,580 credit posted to Boler Holdings June JE
Cigna notification: Carrier termination feed re-confirmed

─────────────── ROUTING ───────────────
  • Detected by:      Benefits Allocation Agent (98.4% confidence)
  • Routed to:        Exception Resolution Agent for HITL queue
  • Step Functions:   approval-workflow-v2.boler.us-east-1
  • Stage 1:          Sarah Mitchell — APPROVED 2026-06-05 09:22
  • Stage 2:          Ziggy Kravitz (CFO) — PENDING
  • Notification:     SES email + SNS push sent 2026-06-06 09:38
  • SLA:               24 hours (current age: 18 hrs · 6 hrs remaining)

─────────────── HAND-OFF ───────────────
→ Once CFO approves, JE Agent regenerates Boler Holdings JE
  (subtracts $1,240 from June + $5,580 prior-period adjustment)
→ HR notified via Teams to follow up with Cigna on termination feed
→ Power BI dashboard auto-refreshes for division CFO reporting

Storage: DynamoDB · partition=2026-06 · sort=EXC-0442
Audit ID: AUDIT-2026-06-06-09:38:14-EXC-0442
`,

  boler_exc_cigna_drift: `APEX EXCEPTION RECORD · MEDIUM PRIORITY
═══════════════════════════════════════════════════════════════
EXCEPTION ID:     EXC-2026-0443
Type:             Carrier Rate Drift
Severity:         MEDIUM
Detection Time:   June 6, 2026 · 09:35:14 ET
Detection Agent:  Signal Agent (SIG)
Status:           AWAITING BENEFITS DIRECTOR REVIEW

─────────────── DETECTION ───────────────
Cigna medical premium drift: +4.1% above contracted rate card
Trailing 90-day pattern: +0.5% → +1.2% → +1.8% → +2.6% → +3.4% → +4.1%
Affected division (highest exposure): Boler Holdings
Cycle variance: $2,180

─────────────── FINANCIAL IMPACT ───────────────
This cycle (June 2026):       $50,557 over contracted rate
Year-to-date (Jan-Jun):       $182,400 cumulative drift
Full-year if unresolved:      $606,684 exposure
3-yr exposure (if pattern continues): $1.82M

─────────────── CONTRACT CONTEXT ───────────────
Contract:       Cigna Healthcare PPO + HDHP (Apr 2024 - Jul 2026)
Annual cap:     +2.5% escalator
Current drift:   +4.1% (+1.6 points over cap)
Renewal window:  May 1 - Jul 1, 2026 (41 days remaining)
Auto-renewal:   Triggers if no 30-day notice

─────────────── RECOMMENDED ACTION ───────────────
1. Initiate Cigna renegotiation BEFORE Jul 1 auto-renewal
2. Target: cap at +2.5% (the contracted escalator) or lower
3. Alternative: BCBS Illinois quote in hand at +2.4% → est $230K/yr saving
4. Backup: 30-day non-renewal notice if Cigna won't move

─────────────── ROUTING ───────────────
  • Detected by:      Signal Agent (rate-drift watcher)
  • Routed to:        Benefits Director (Sarah Mitchell) — Stage 1
  • Step Functions:   approval-workflow-v2.boler.us-east-1
  • Stage 1:          Sarah Mitchell — PENDING
  • Stage 2:          Ziggy Kravitz (CFO) — if escalated
  • Notification:     SES email + SNS push sent 2026-06-06 09:35

Storage: DynamoDB · partition=2026-06 · sort=EXC-0443
Audit ID: AUDIT-2026-06-06-09:35:14-EXC-0443
`,

  boler_exc_transfers: `APEX EXCEPTION RECORD · MEDIUM PRIORITY · AUTO-FIXED
═══════════════════════════════════════════════════════════════
EXCEPTION ID:     EXC-2026-0444
Type:             Division Transfer Misallocation
Severity:         MEDIUM
Detection Time:   June 6, 2026 · 09:22:14 ET
Detection Agent:  Benefits Allocation Agent (BEN)
Status:           AUTO-FIXED (no human review required)

─────────────── DETECTION ───────────────
4 employees transferred between divisions on or after 2026-05-15
were still coded to their prior division in all carrier files.

Employees affected (anonymized):
  EMP-2241  Kim, Susan         Mfg Services → Real Estate    eff. 2026-05-22
  EMP-3091  Foster, Marcus     Corporate → Hendrickson        eff. 2026-05-28
  EMP-5184  Reilly, Dana       Boler Holdings → Mfg Services eff. 2026-05-30
  EMP-4821  Chen, Robert       Hendrickson → Boler Holdings eff. 2026-05-15  ← ALSO EXC-0441

Note: EMP-4821 (Chen) escalated separately as EXC-0441 HIGH due to $3,840/mo exposure.
The other 3 transfers were under $5K each and auto-fixed per Boler reclassification policy.

─────────────── AUTO-FIX APPLIED ───────────────
EMP-2241 Kim:           - Mfg Services 6200-004 · $1,920/mo  → + Real Estate 6200-002 · $1,920/mo
EMP-3091 Foster:        - Corporate 6200-005 · $2,440/mo     → + Hendrickson Intl 6200-001 · $2,440/mo
EMP-5184 Reilly:        - Boler Holdings 6200-003 · $1,920/mo  → + Mfg Services 6200-004 · $1,920/mo

Total auto-fixed: $14,320/mo
Effective dates honored: each employee's actual transfer date.
Catch-up prorate calculations applied to June JEs.

─────────────── FINANCIAL IMPACT ───────────────
Per-month misallocation (auto-corrected): $14,320
Annualized: $171,840 if not detected
Time-to-detect: < 24hr (vs ~30 days manual)

─────────────── ROUTING ───────────────
  • Detected by:      Benefits Allocation Agent
  • Auto-fix policy:   Below $5K/mo per employee + clear HRIS source-of-truth
  • Approval log:      Logged to DynamoDB (no human approval needed per policy)
  • Notification:     Confirmation email to Sarah Mitchell + audit log

Storage: DynamoDB · partition=2026-06 · sort=EXC-0444
Audit ID: AUDIT-2026-06-06-09:22:14-EXC-0444-AUTOFIX
`,

  boler_exc_401k: `APEX EXCEPTION RECORD · MEDIUM PRIORITY
═══════════════════════════════════════════════════════════════
EXCEPTION ID:     EXC-2026-0445
Type:             Rate Card / Policy Mismatch
Severity:         MEDIUM
Detection Time:   June 6, 2026 · 09:31:08 ET
Detection Agent:  Benefits Allocation Agent (BEN)
Status:           AWAITING BENEFITS DIRECTOR REVIEW

─────────────── DETECTION ───────────────
Fidelity 401k carrier file applies employer match rate of 4.5%.
Boler HR policy document P-COMP-401K-2024 specifies match rate of 4.0%.

The 0.5% delta produces:
  - Monthly delta: $8,240
  - YTD impact (Jan-Jun): $49,440
  - Full-year if unresolved: $98,880
  - 3-yr cumulative: $296,640

─────────────── EVIDENCE ───────────────
Source A (Fidelity_401k_Jun2026.csv · line 1):
  "Employer Match Rate Applied: 4.5%"

Source B (HR policy P-COMP-401K-2024.pdf · §3.2):
  "The Boler Company will match 100% of employee contributions up to 4.0% of
   eligible compensation."

Source C (Plan Document for 88-441208 · Schedule B):
  Last amendment date: 2024-04-01
  Match formula: 100% × first 4.0% of compensation
  Note: No amendment on file for 4.5% increase.

─────────────── ROOT CAUSE OPTIONS ───────────────
1. Fidelity rate card was auto-incremented (typical 4.0% → 4.5% bump from prior plan)
2. HR policy was updated to 4.5% but the policy document + allocation system not synced
3. Plan administrator error — 4.5% applied without plan amendment

─────────────── RECOMMENDED ACTION ───────────────
Sarah Mitchell (Benefits Director) follow-up within 7 days:
  1. Contact Fidelity Relationship Manager (Reggie Park) to confirm match rate authority
  2. Review HR/Benefits Committee minutes for any approved 4.5% amendment
  3. Reconcile prior periods + adjust if applicable
  4. Update P-COMP-401K-2024 OR roll back Fidelity rate

If 4.5% is intentional: amend plan document + restate YTD.
If 4.0% is correct: file correction with Fidelity + claw back overpayment.

─────────────── ROUTING ───────────────
  • Detected by:      Benefits Allocation Agent (cross-reference engine)
  • Routed to:        Sarah Mitchell (Benefits Director) — Stage 1
  • Confidence:       96.1%

Storage: DynamoDB · partition=2026-06 · sort=EXC-0445
Audit ID: AUDIT-2026-06-06-09:31:08-EXC-0445
`,

  boler_exc_thompson: `APEX EXCEPTION RECORD · LOW PRIORITY · AUTO-FIXED
═══════════════════════════════════════════════════════════════
EXCEPTION ID:     EXC-2026-0446
Type:             Terminated Employee — Benefits Still Active
Severity:         LOW
Detection Time:   June 5, 2026 · 09:18:33 ET
Detection Agent:  Benefits Allocation Agent (BEN)
Status:           AUTO-FIXED

─────────────── DETECTION ───────────────
Thompson, D. (EMP-7142)
Last division:    Boler Mfg Services (CC 6200-004)
Termination date: 2026-05-28

Carrier files still showing active billing for Thompson:
  • VSP Vision:     $134/mo (Family tier)
  • Delta Dental:   $286/mo (Family tier)

Total: $420/mo unauthorized billing.

─────────────── AUTO-FIX APPLIED ───────────────
Per Boler auto-fix policy: termination + <$500/mo + no prior SAR/EDD → auto-resolve.

  • VSP Vision  · $134/mo REMOVED · backdated to 2026-05-29
  • Delta Dental · $286/mo REMOVED · backdated to 2026-05-29
  • Catch-up credit: $420 to Boler Mfg Services June JE

Termination cascade triggered for remaining carriers (Cigna, Hartford, Fidelity)
— all already correctly showing TERMINATED status. Only VSP + Delta were lagging.

─────────────── ROUTING ───────────────
  • Detected by:      Benefits Allocation Agent
  • Auto-fix policy:   Below threshold + clear HRIS source-of-truth
  • Notification:     Confirmation email to Sarah Mitchell

Storage: DynamoDB · partition=2026-06 · sort=EXC-0446
Audit ID: AUDIT-2026-06-05-09:18:33-EXC-0446-AUTOFIX
`,

  boler_exc_new_hires: `APEX EXCEPTION RECORD · LOW PRIORITY
═══════════════════════════════════════════════════════════════
EXCEPTION ID:     EXC-2026-0447
Type:             Missing Cost Center Assignment
Severity:         LOW
Detection Time:   June 6, 2026 · 09:14:22 ET
Detection Agent:  Benefits Allocation Agent (BEN)
Status:           AWAITING BENEFITS DIRECTOR REVIEW

─────────────── DETECTION ───────────────
3 new hires appear in carrier files for the June cycle but have no
cost center assignment in HRIS or the allocation system.

Affected:
  EMP-9112  Stanford, Tyrell    Hire date: 2026-05-19 · Division: TBD
  EMP-9113  Okafor, Adaeze     Hire date: 2026-05-22 · Division: TBD
  EMP-9114  Lambert, Jenna     Hire date: 2026-05-26 · Division: TBD

Total unallocated: $6,840/mo (3 × Cigna Family + dental + 401k starter match)

─────────────── ROOT CAUSE ───────────────
New-hire benefits intake portal collects standard enrollment but the
"division assignment + cost center" step is HR-driven and lags carrier
enrollment by ~5-10 days.

─────────────── RECOMMENDED ACTION ───────────────
Sarah Mitchell to confirm with hiring managers:
  • Stanford → likely Hendrickson Intl (CC 6200-001)
  • Okafor → likely Mfg Services (CC 6200-004)
  • Lambert → likely Real Estate (CC 6200-002)

Once confirmed, allocate $6,840/mo to correct cost centers (catch-up to hire date).

─────────────── ROUTING ───────────────
  • Detected by:      Benefits Allocation Agent
  • Routed to:        Sarah Mitchell (Benefits Director) — Stage 1
  • Notification:     SES email

Storage: DynamoDB · partition=2026-06 · sort=EXC-0447
Audit ID: AUDIT-2026-06-06-09:14:22-EXC-0447
`,

  boler_je_hendrickson: `JOURNAL ENTRY · Hendrickson International · June 2026
═══════════════════════════════════════════════════════════════
The Boler Company · Benefits Allocation Cycle
═══════════════════════════════════════════════════════════════

JE ID:           JE-2026-0031
Division:        Hendrickson International
Period:          June 2026
Posting Date:    Scheduled Jun 7, 2026 · 08:00 ET
Cost Center:     6200-001 (master)
Approver:        Stage 2 CFO sign-off pending (Ziggy Kravitz)
Generated By:    Journal Entry Agent (JE)
Generation Time: 2026-06-06 08:47:00 ET

──── ENTRY DETAIL ────

DR  6200-001 · Benefits Expense — Medical          $624,480.00
DR  6200-002 · Benefits Expense — Dental             $91,840.00
DR  6200-003 · Benefits Expense — 401k Match        $201,760.00
DR  6200-004 · Benefits Expense — Vision/Life/LTD   $124,720.00
                                                  ─────────────
TOTAL DR                                          $1,042,800.00

CR  2100-001 · Benefits Payable — Cigna                       $710,800.00
CR  2100-002 · Benefits Payable — Delta Dental                $91,840.00
CR  2100-003 · Benefits Payable — Fidelity 401k              $167,000.00
CR  2100-004 · Benefits Payable — VSP Vision                  $38,200.00
CR  2100-005 · Benefits Payable — Hartford Life               $4,800.00
CR  2100-006 · Benefits Payable — Cigna STD/LTD              $30,160.00
                                                            ─────────────
TOTAL CR                                                    $1,042,800.00

──── BALANCE CHECK ────
DR = $1,042,800.00
CR = $1,042,800.00
Balance: $0.00 ✓ VALID

──── ALLOCATION KEY ────
Employees: 412 (pre Chen reclassification: 413)
Per-employee average: $2,532/mo benefits cost

──── SUPPORTING DETAIL ────
Source files (all from S3 restricted intake bucket):
  1. Cigna_Medical_Jun2026.csv     · $710,800
  2. Delta_Dental_Jun2026.csv      · $91,840
  3. Fidelity_401k_Jun2026.csv     · $167,000
  4. VSP_Vision_Jun2026.csv         · $38,200
  5. Hartford_Life_Jun2026.csv      · $4,800
  6. Cigna_STD_LTD_Jun2026.csv      · $30,160

──── APPROVAL CHAIN ────
Stage 1:  APPROVED · Jun 5, 09:22 · Sarah Mitchell (Benefits Director)
Stage 2:  PENDING  · Ziggy Kravitz (CFO) · Due Jun 6 · 24hr SLA · 6h remaining
Stage 3:  SCHEDULED · Jun 7 08:00 · Auto-distribution to Lisa Tanaka (Hend Controller)

──── DISTRIBUTION ────
Destination:    s3://boler-je-distribution/2026-06/hendrickson/
Method:         Step Functions auto-distribution + SES notification + SNS push
Recipients:     Lisa Tanaka (Division Controller) + Sarah Mitchell + Accounting team

──── AUDIT TRAIL ────
2026-06-03 11:42 · JE auto-generated by JE Agent
2026-06-05 09:22 · Stage 1 approval (Sarah Mitchell)
2026-06-06 08:47 · Stage 2 routed to CFO

Storage: DynamoDB · partition=2026-06 · sort=JE-HEND-006
Audit ID: AUDIT-2026-06-06-08:47:00-JE-HENDRICKSON
Encryption: KMS · CMK rotated quarterly
`,

  /* ─── BOLER · Excel workbook previews (rendered as monospace tables) ─── */

  boler_xlsx_cigna_roster: `CIGNA HEALTHCARE — MEDICAL PREMIUM ROSTER (Excel · 3 sheets · 66 KB)
════════════════════════════════════════════════════════════════════════
File:        Cigna_Medical_Roster_Jun2026.xlsx
Sheets:      Roster (847 rows) · Summary (5×4 pivot) · Drift Analysis (4 rows)
Invoice:     CIG-MED-2026-06-1847
Period:      Jun 1–30, 2026
Group #:     CIG-BOL-44731
TIN:         36-4729183

┌──── SHEET 1 · ROSTER (847 rows) ─────────────────────────────────────┐
│ Member ID  │ Name            │ Division  │ Plan    │ Premium  │ Drift│
├────────────┼─────────────────┼───────────┼─────────┼──────────┼──────┤
│ EE-100001  │ Smith, James    │ HTS       │ Premium │ $1,908   │+68bp │
│ EE-100002  │ Johnson, Mary   │ BLH       │ Standard│ $1,485   │  —   │
│ EE-100003  │ Williams, John  │ HTS       │ Premium │ $1,908   │+68bp │
│ EE-100004  │ Brown, Patricia │ HTS       │ HDHP    │ $1,156   │+41bp │
│ EE-100005  │ Jones, Robert   │ CEQ       │ Standard│ $1,485   │  —   │
│   …        │   … (842 more)  │   …       │   …     │   …      │  …   │
│                                                    TOTAL: $1,284,320 │
└──────────────────────────────────────────────────────────────────────┘

┌──── SHEET 2 · SUMMARY (Plan Tier × Division) ────────────────────────┐
│ Division   │  Premium  │  Standard │   HDHP   │  Basic  │   Total   │
├────────────┼───────────┼───────────┼──────────┼─────────┼───────────┤
│ HTS        │  $167,729 │  $207,228 │  $78,955 │ $39,478 │  $493,180 │
│ BLH        │   $96,486 │  $119,193 │  $45,397 │ $22,698 │  $283,844 │
│ CEQ        │   $81,560 │  $100,768 │  $38,376 │ $19,188 │  $239,892 │
│ RHO        │   $54,170 │   $66,915 │  $25,491 │ $12,745 │  $159,321 │
│ HEN        │   $36,704 │   $45,338 │  $17,272 │  $8,636 │  $107,950 │
└──────────────────────────────────────────────────────────────────────┘

┌──── SHEET 3 · DRIFT ANALYSIS (the demo hero moment) ─────────────────┐
│ Plan Tier │ Plan-Doc Rate │ Billed Rate │ Drift bps │ Lives │ Impact│
├───────────┼───────────────┼─────────────┼───────────┼───────┼───────┤
│ Premium   │      $1,840   │    $1,908   │ +369 bps  │  114  │ $7,752│
│ Standard  │      $1,485   │    $1,539   │ +364 bps  │  148  │ $7,992│
│ HDHP      │      $1,115   │    $1,156   │ +368 bps  │   64  │ $2,624│
│ Basic     │        $920   │      $948   │ +304 bps  │   30  │   $840│
│                                       Monthly impact: $19,208       │
│                                       Annualized:    $230,496       │
│                                                                     │
│ RECOMMENDATION: Open Cigna renewal renegotiation 90 days early.     │
│ Renewal is Q4 2026. Window closes in 41 days.                       │
└──────────────────────────────────────────────────────────────────────┘
`,

  boler_xlsx_hris_master: `THE BOLER COMPANY — HRIS MASTER ROSTER (Excel · 3 sheets · 217 KB)
════════════════════════════════════════════════════════════════════════
File:        Boler_HRIS_Master_Roster.xlsx
Source:      Workday export
Effective:   2026-06-01
Sheets:      All Employees (2,847 rows) · By Division (5+totals) · Transfers (4 rows)

┌──── SHEET 1 · ALL EMPLOYEES (2,847 rows) ────────────────────────────┐
│ Employee ID │ Name            │ Division               │ Hire   │ %  │
├─────────────┼─────────────────┼────────────────────────┼────────┼────┤
│ EE-100001   │ Smith, James    │ Hendrickson Truck Susp │ 2007   │ 6% │
│ EE-100002   │ Johnson, Mary   │ Boler Hitch            │ 2019   │ 4% │
│ EE-100003   │ Williams, John  │ Hendrickson Truck Susp │ 2014   │ 8% │
│ EE-100004   │ Brown, Patricia │ Hendrickson Truck Susp │ 2021   │ 0% │
│ EE-101204   │ Thompson, Greg  │ ROHO Group · TERM 5/22 │ 2009   │ 5% │
│   …         │   (2,842 more)  │   …                    │   …    │ …  │
└──────────────────────────────────────────────────────────────────────┘

┌──── SHEET 2 · BY DIVISION (allocation source of truth) ──────────────┐
│ Division                       │ Code │ Lives │  %    │ Salary $    │
├────────────────────────────────┼──────┼───────┼───────┼─────────────┤
│ Hendrickson Truck Suspension   │ HTS  │ 1,094 │ 38.4% │ $90,143,400 │
│ Boler Hitch                    │ BLH  │   629 │ 22.1% │ $44,784,800 │
│ Cequent Performance            │ CEQ  │   532 │ 18.7% │ $40,857,600 │
│ ROHO Group                     │ RHO  │   353 │ 12.4% │ $24,322,000 │
│ Henderson Wheel                │ HEN  │   239 │  8.4% │ $17,719,800 │
│                          TOTAL │ ALL  │ 2,847 │ 100%  │$217,827,600 │
└──────────────────────────────────────────────────────────────────────┘

┌──── SHEET 3 · TRANSFERS (May 2026) · all auto-reclassified ──────────┐
│ Employee     │ From → To                                  │ Effective │
├──────────────┼────────────────────────────────────────────┼───────────┤
│ Chen, R.     │ Boler Hitch → Hendrickson Truck Suspension │ 2026-05-05│
│ Tanaka, Y.   │ Cequent → Boler Hitch                      │ 2026-05-12│
│ Okonkwo, D.  │ ROHO → Henderson                           │ 2026-05-18│
│ Petrova, A.  │ Hendrickson → Cequent                      │ 2026-05-27│
│                                              EXC-2026-0444 · AUTO-FIX│
└──────────────────────────────────────────────────────────────────────┘
`,

  boler_xlsx_division_allocation: `DIVISION ALLOCATION — JUNE 2026 (Excel · 2 sheets · 7 KB)
════════════════════════════════════════════════════════════════════════
File:    Division_Allocation_Jun2026.xlsx
Sheets:  Allocation Matrix (6 carriers × 5 divisions) · Variance

┌──── SHEET 1 · ALLOCATION MATRIX ($1,284,320 total) ──────────────────┐
│ Carrier         │   HTS    │   BLH    │   CEQ    │  RHO    │   HEN  │
├─────────────────┼──────────┼──────────┼──────────┼─────────┼────────┤
│ Cigna Medical   │ $342,316 │ $197,015 │ $166,693 │$110,539 │ $74,938│
│ Delta Dental    │  $40,432 │  $23,265 │  $19,684 │ $13,055 │  $8,851│
│ VSP Vision      │  $11,838 │   $6,810 │   $5,762 │  $3,821 │  $2,592│
│ Fidelity 401k   │  $70,043 │  $40,290 │  $34,082 │ $22,580 │ $15,316│
│ Hartford Life   │  $13,326 │   $7,661 │   $6,481 │  $4,302 │  $2,917│
│ Cigna STD/LTD   │  $15,225 │   $8,803 │   $7,466 │  $4,959 │  $3,358│
├─────────────────┼──────────┼──────────┼──────────┼─────────┼────────┤
│ TOTAL           │ $493,180 │ $283,844 │ $240,168 │$159,256 │$107,872│
│ %               │   38.4%  │   22.1%  │   18.7%  │  12.4%  │   8.4% │
└──────────────────────────────────────────────────────────────────────┘
                                                  GRAND TOTAL: $1,284,320

┌──── SHEET 2 · VARIANCE (June vs May + FY Budget) ────────────────────┐
│ Division │ May 2026 │ Jun 2026 │ MoM $    │ FY Budget    │ Status   │
├──────────┼──────────┼──────────┼──────────┼──────────────┼──────────┤
│ HTS      │ $469,100 │ $493,180 │ +$24,080 │ $5,640,000   │ CFO ⚠    │
│ BLH      │ $281,430 │ $283,844 │  +$2,414 │ $3,360,000   │ Bens Mgr │
│ CEQ      │ $235,870 │ $240,168 │  +$4,298 │ $2,820,000   │ OK       │
│ RHO      │ $158,610 │ $159,256 │    +$646 │ $1,920,000   │ OK       │
│ HEN      │ $105,890 │ $107,872 │  +$1,982 │ $1,260,000   │ OK       │
└──────────────────────────────────────────────────────────────────────┘

CFO CALLOUT: Hendrickson Truck Suspension YTD variance breaches $50K
material-variance threshold. Routing JE to Ziggy Kravitz for sign-off.
`,

  boler_xlsx_exception_register: `EXCEPTION REGISTER — JUNE 2026 (Excel · 2 sheets · 7 KB)
════════════════════════════════════════════════════════════════════════
File:        Exception_Register_Jun2026.xlsx
Sheets:      Exception Register (7 rows) · Summary (9 KPIs)
Total Exceptions:  7
Auto-Fixed:        4
HITL — Sarah:      3 (Benefits Manager)
HITL — Ziggy:      1 (CFO)

┌──── SHEET 1 · EXCEPTION REGISTER ────────────────────────────────────┐
│ Exception ID       │ Type                │ Severity │  Variance     │
├────────────────────┼─────────────────────┼──────────┼───────────────┤
│ EXC-2026-0441      │ wrong_division      │   HIGH   │    $2,840.00  │
│ EXC-2026-0442      │ duplicate_cobra     │   HIGH   │   -$1,485.00  │
│ EXC-2026-0443      │ carrier_drift       │ CRITICAL │   $47,640.00  │
│ EXC-2026-0444      │ auto_fixed_transfer │   LOW    │    $1,240.00  │
│ EXC-2026-0445      │ k401_rate_mismatch  │   HIGH   │   $11,420.00  │
│ EXC-2026-0446      │ terminated_on_roster│  MEDIUM  │    $1,840.00  │
│ EXC-2026-0447      │ new_hire_no_cc      │   LOW    │        $0.00  │
└──────────────────────────────────────────────────────────────────────┘

┌──── ROUTING DECISIONS ───────────────────────────────────────────────┐
│ EXC-0441 → Sarah Mitchell  · pending HITL · confidence 0.94          │
│ EXC-0442 → Sarah Mitchell  · pending HITL · confidence 0.97          │
│ EXC-0443 → Ziggy Kravitz   · pending CFO  · confidence 0.98          │
│ EXC-0444 → AUTO-FIX        · RESOLVED 03:47 ET                       │
│ EXC-0445 → Sarah Mitchell  · pending HITL · confidence 0.94          │
│ EXC-0446 → AUTO-FIX        · RESOLVED 03:52 ET                       │
│ EXC-0447 → AUTO-FIX        · RESOLVED 03:58 ET                       │
└──────────────────────────────────────────────────────────────────────┘

┌──── SHEET 2 · SUMMARY KPIs ──────────────────────────────────────────┐
│ Total $ Variance Identified:        $63,255                           │
│ Avg Confidence Score:                 96.4%                          │
│ Time-to-Auto-Fix (avg):             4.2 minutes                      │
│ Time-to-HITL-Resolution (avg):      2.8 hours                        │
│ Annual Run-Rate Value (savings):    $671,000                         │
└──────────────────────────────────────────────────────────────────────┘
`,

  boler_xlsx_consolidated_je: `CONSOLIDATED JOURNAL ENTRY — JE-2026-06-CONSOLIDATED (Excel · 6 sheets · 13 KB)
════════════════════════════════════════════════════════════════════════
File:           Boler_Consolidated_JE_Jun2026.xlsx
Sheets:         Consolidated JE · JE-HTS · JE-BLH · JE-CEQ · JE-RHO · JE-HEN
Period:         June 2026
Total Debits:   $1,284,320.00
Total Credits:  $1,284,320.00   ✓ BALANCED to the penny
Stage 1 ✓:      Sarah Mitchell · 2026-06-05 03:42 ET
Stage 2 ✓:      Ziggy Kravitz · 2026-06-05 04:08 ET
Distributed:    2026-06-05 04:11 ET to 5 division S3 inboxes

┌──── SHEET 1 · CONSOLIDATED JE (35 GL lines) ─────────────────────────┐
│ GL Code     │ Description                  │ Division │ Debit       │
├─────────────┼──────────────────────────────┼──────────┼─────────────┤
│ 6210-HTS    │ Health Insurance — Medical   │ HTS      │ $342,316.48 │
│ 6220-HTS    │ Health Insurance — Dental    │ HTS      │  $40,432.62 │
│ 6230-HTS    │ Health Insurance — Vision    │ HTS      │  $11,837.68 │
│ 6310-HTS    │ 401(k) ER Contribution       │ HTS      │  $70,043.20 │
│ 6410-HTS    │ Group Life Insurance         │ HTS      │  $13,325.92 │
│ 6420-HTS    │ Group Disability Insurance   │ HTS      │  $15,224.96 │
│ … (continues per-division for BLH/CEQ/RHO/HEN)                      │
│ 2310-HTS    │ Accrued Benefits Payable     │ HTS      │ (CR $493,180)│
│ 2310-BLH    │ Accrued Benefits Payable     │ BLH      │ (CR $283,844)│
│ 2310-CEQ    │ Accrued Benefits Payable     │ CEQ      │ (CR $240,168)│
│ 2310-RHO    │ Accrued Benefits Payable     │ RHO      │ (CR $159,256)│
│ 2310-HEN    │ Accrued Benefits Payable     │ HEN      │ (CR $107,872)│
├─────────────┼──────────────────────────────┼──────────┼─────────────┤
│                                  BALANCE: $0.00 ✓ BALANCED          │
└──────────────────────────────────────────────────────────────────────┘

┌──── DISTRIBUTION RECEIPTS (per-division S3 + SNS) ───────────────────┐
│ HTS │ s3://apex-boler-division-inbox/HTS/2026-06/  · KMS:alias/boler-hts │
│ BLH │ s3://apex-boler-division-inbox/BLH/2026-06/  · KMS:alias/boler-blh │
│ CEQ │ s3://apex-boler-division-inbox/CEQ/2026-06/  · KMS:alias/boler-ceq │
│ RHO │ s3://apex-boler-division-inbox/RHO/2026-06/  · KMS:alias/boler-rho │
│ HEN │ s3://apex-boler-division-inbox/HEN/2026-06/  · KMS:alias/boler-hen │
│                            All 5 SNS notifications ACK'd by controllers│
└──────────────────────────────────────────────────────────────────────┘
`,
};

/* ──────────────────────── pipeline selector ──────────────────────── */

interface PipelineOption {
  id: SampleKey;
  name: string;
  industry: string;
  description: string;
  stages: string;           // short "Extract → Validate → Route" summary
}

/** The pipelines a user can pick to process an uploaded or previewed file.
 *  The id is a SampleKey so the existing animation + results panel can be
 *  reused verbatim. */
const PIPELINE_OPTIONS: PipelineOption[] = [
  { id: 'order_mod',   name: 'Zero-Touch Order Modification', industry: 'Supply Chain & Manufacturing · CBB', description: 'Parse modification PDFs, validate tolerance, update Dynamics CRM, notify distributor.', stages: 'Ingest → Extract → Validate → CRM Update → Notify' },
  { id: 'qc_batch',    name: 'QC Batch Ingestion & Hold',      industry: 'Manufacturing · CBB',     description: 'Unpack certificates, check tensile + color against Fabric One, place SAP holds.',       stages: 'Ingest → Extract → Tolerance → ERP Hold → Teams Alert' },
  { id: 'port_strike', name: 'Disruption Impact & Reroute',    industry: 'Supply Chain · CBB',      description: 'Traverse BOM, project impact, rank reroutes, escalate to Director when > $500k.',      stages: 'Ingest → Analyze → Predict → Generate → Escalate' },
  { id: 'invoice',     name: 'Invoice Processing & Validation',industry: 'Financial Services',     description: 'Extract line items, PO match, duplicate check, auto-approve under $10k.',               stages: 'Ingest → Extract → PO Match → Decision → Notify' },
  { id: 'claim',       name: 'Claims Intake & Triage',         industry: 'Commercial Insurance',   description: 'FNOL extraction, policy lookup, deductible + fraud checks, route to adjuster.',          stages: 'Ingest → Extract → Validate → Route → Notify' },
  { id: 'po',          name: 'PO Auto-Approval',               industry: 'Procurement',            description: 'Match POs against inventory, vendor, and credit checks; auto-approve if clean.',         stages: 'Ingest → Extract → Validate → Approve → Notify' },
  { id: 'qc',          name: 'QC Report Triage',               industry: 'Supply Chain & Manufacturing', description: 'Extract defects, apply partial holds, notify plant manager.',                             stages: 'Ingest → Extract → Validate → Route → Notify' },
  { id: 'contract',    name: 'Contract Clause Review',         industry: 'Legal',                  description: 'Pull key clauses, flag non-standard penalties + auto-renewal, route to legal.',           stages: 'Ingest → Extract → Validate → Route → Notify' },
  { id: 'alert',       name: 'Supply Alert Broadcast',         industry: 'Supply Chain & Manufacturing', description: 'Classify alert, map to affected plants, notify ops.',                                    stages: 'Ingest → Extract → Analyze → Route → Notify' },

  /* ──────── STP Phase 2 — one option per ChatSTP use case ──────── */
  { id: 'stp_policy',         name: 'Policy & Procedure Lookup',    industry: 'Nuclear Operations · STP',
    description: 'Index policy/procedure/Tech Spec documents. PolicyAgent returns verbatim citations on demand.',
    stages: 'Ingest → Header parse → Section index → Verbatim store → PolicyAgent ready' },
  { id: 'stp_pm_history',     name: 'Equipment PM History',         industry: 'Nuclear Operations · STP',
    description: 'Parse work-package PDFs + match WO to engineer attribution. MaintenanceAgent retrieves the right PM history.',
    stages: 'Ingest → WO match → Engineer attribute → eAM cross-ref → MaintenanceAgent index' },
  { id: 'stp_issue_analysis', name: 'Equipment Issue Analysis',     industry: 'Nuclear Operations · STP',
    description: 'Analyse incident reports + scanned work packages. DiagnosticsAgent aggregates failure modes with cited WOs.',
    stages: 'Ingest → Mode classify → Aggregate → Cite WOs → DiagnosticsAgent ready' },
  { id: 'stp_predictive',     name: 'Predictive Maintenance',       industry: 'Nuclear Operations · STP',
    description: 'Score sensor anomaly streams. ReliabilityAgent generates RUL forecast + PM advance with $ avoidance.',
    stages: 'Ingest → Anomaly score → RUL forecast → Risk tier → PM recommend → Human review' },

  /* ──────── Telecommunications · Verizon Far Edge POC ──────── */
  { id: 'tel_robot_xml',      name: 'Full Certification Cycle',     industry: 'Telecommunications · Verizon',
    description: 'Parse ROBOT XML output, classify P1/P2/P3 failures, build JIRA payloads, generate cert report.',
    stages: 'Ingest XML → Classify Failures → Schema Drift → JIRA Tickets → Cert Report' },
  { id: 'tel_redfish_diff',   name: 'Schema Drift Response',        industry: 'Telecommunications · Verizon',
    description: 'Compare baseline + current Redfish schemas, surface breaking changes, map impact across 47 scripts.',
    stages: 'Fetch Schema → Diff Baseline → Map Script Impact → Open JIRA Epic → Notify Team' },
  { id: 'tel_upgrade_runbook',name: 'Upgrade Path Validation',      industry: 'Telecommunications · Verizon',
    description: 'Validate firmware upgrade path against compatibility matrix, surface historical failure rate, HITL gate.',
    stages: 'Load Inventory → Match Path → Compute Risk → Historical Lookup → HITL Wave Approval' },
  { id: 'tel_kb_article',     name: 'KB Citation Q&A',              industry: 'Telecommunications · Verizon',
    description: 'MentorAgent answers operator questions with verbatim citations from runbooks, release notes, KB.',
    stages: 'Embed Query → Hybrid Retrieve → Rerank → Cite Verbatim → Audit-Trail Log' },

  /* ──────── Agentic Enterprise (66 Degrees vendor-neutral) ──────── */
  { id: 'ae_inventory_alert', name: 'Supply Chain Orchestrator',     industry: 'Agentic Enterprise',
    description: 'Multi-agent orchestrator: detect shortage, rank suppliers, draft PO, route to human approval.',
    stages: 'Check Inventory → Rank Suppliers → Draft PO → Submit for Approval' },
  { id: 'ae_lease_pdf',       name: 'Lease Extraction',              industry: 'Agentic Enterprise',
    description: 'Document AI extracts tenant + expiration + liability clause, indexes to DuckDB, supports SQL queries.',
    stages: 'Extract → Confidence Check → Index DuckDB → Run SQL Query' },
];

/** Default pipeline recommendation per sample (id equals key in the current
 *  build, but this keeps the concept separate so CBB samples can still show a
 *  "recommended" chip). */
const RECOMMENDED_PIPELINE: Record<SampleKey, SampleKey> = {
  order_mod: 'order_mod', qc_batch: 'qc_batch', port_strike: 'port_strike',
  invoice: 'invoice', claim: 'claim', po: 'po', qc: 'qc', contract: 'contract', alert: 'alert',
  stp_policy: 'stp_policy', stp_pm_history: 'stp_pm_history',
  stp_issue_analysis: 'stp_issue_analysis', stp_predictive: 'stp_predictive',
  tel_robot_xml: 'tel_robot_xml', tel_redfish_diff: 'tel_redfish_diff',
  tel_upgrade_runbook: 'tel_upgrade_runbook', tel_kb_article: 'tel_kb_article',
  // Verizon Far Edge — 12 real reports → map to the existing telecom pipeline options
  // Cert work → Full Certification Cycle · regressions → Schema Drift · upgrades → Upgrade path
  vz_dmtf_e930t: 'tel_robot_xml', vz_samsung_ssd: 'tel_redfish_diff',
  vz_bmc_upgrade: 'tel_upgrade_runbook', vz_ptu_perf: 'tel_robot_xml',
  vz_sensor_proteus: 'tel_robot_xml', vz_bios_triton: 'tel_robot_xml',
  vz_redfish_proteus: 'tel_robot_xml', vz_platform_deploy: 'tel_upgrade_runbook',
  vz_soak_galene: 'tel_robot_xml', vz_dell_sensor: 'tel_robot_xml',
  vz_troubleshoot: 'tel_redfish_diff', vz_flexran: 'tel_robot_xml',
  vz_cas_el140: 'tel_robot_xml', vz_cas_xr8720: 'tel_robot_xml',
  vz_cas_playbook_spec: 'tel_upgrade_runbook', vz_cas_thermal: 'tel_redfish_diff',
  vz_cas_wrcp: 'tel_robot_xml',
  ae_inventory_alert: 'ae_inventory_alert', ae_lease_pdf: 'ae_lease_pdf',
  // EPROD · invoices + POs use the generic invoice / po pipelines as a sensible
  // default. MSAs, quotes, tariff sheets and JIB statements don't have a
  // dedicated pipeline yet — fall back to the contract pipeline so the
  // "Run pipeline" link still has a valid target.
  eprod_inv_hal: 'invoice', eprod_inv_slb: 'invoice',
  eprod_inv_bhi: 'invoice', eprod_inv_kiewit: 'invoice',
  eprod_po_epc:  'po',      eprod_po_chem:   'po',     eprod_po_ops: 'po',
  eprod_msa_hal: 'contract', eprod_msa_kiewit: 'contract',
  eprod_quote_fluor: 'contract', eprod_quote_bechtel: 'contract',
  eprod_tariff_ngl: 'contract', eprod_tariff_crude: 'contract',
  eprod_jib_p66:   'contract', eprod_jib_targa:    'contract',
  /* CWFCU · 22 credit union samples */
  cwfcu_cip_rosales:           'cwfcu_cip_rosales',
  cwfcu_cip_nguyen:           'cwfcu_cip_rosales',
  cwfcu_cip_arrington:           'cwfcu_cip_rosales',
  cwfcu_cip_okafor:           'cwfcu_cip_rosales',
  cwfcu_sar_structuring:           'cwfcu_sar_structuring',
  cwfcu_sar_rapid_movement:           'cwfcu_sar_structuring',
  cwfcu_sar_layering:           'cwfcu_sar_structuring',
  cwfcu_ctr_cash:           'cwfcu_ctr_cash',
  cwfcu_ctr_wire:           'cwfcu_ctr_cash',
  cwfcu_cdd_04421:           'cwfcu_cdd_04421',
  cwfcu_cdd_08812:           'cwfcu_cdd_04421',
  cwfcu_loan_auto:           'cwfcu_loan_auto',
  cwfcu_loan_heloc_johnson:           'cwfcu_loan_auto',
  cwfcu_loan_mortgage_patel:           'cwfcu_loan_auto',
  cwfcu_loan_personal_williams:           'cwfcu_loan_auto',
  cwfcu_paystub_nguyen:           'cwfcu_loan_auto',
  cwfcu_contract_fiserv:           'cwfcu_contract_fiserv',
  cwfcu_contract_eltropy:           'cwfcu_contract_fiserv',
  cwfcu_contract_coop:           'cwfcu_contract_fiserv',
  cwfcu_contract_diebold:           'cwfcu_contract_fiserv',
  cwfcu_policy_bsa_roster:           'cwfcu_policy_bsa_roster',
  cwfcu_board_res_vendor_mgmt:           'cwfcu_board_res_vendor_mgmt',
  /* BOLER · 14 sample files */
  boler_cigna_medical:           'boler_cigna_medical',
  boler_delta_dental:           'boler_delta_dental',
  boler_fidelity_401k:           'boler_fidelity_401k',
  boler_vsp_vision:           'boler_vsp_vision',
  boler_hartford_life:           'boler_hartford_life',
  boler_cigna_std_ltd:           'boler_cigna_std_ltd',
  boler_exc_chen:           'boler_exc_chen',
  boler_exc_martinez:           'boler_exc_martinez',
  boler_exc_cigna_drift:           'boler_exc_cigna_drift',
  boler_exc_transfers:           'boler_exc_transfers',
  boler_exc_401k:           'boler_exc_401k',
  boler_exc_thompson:           'boler_exc_thompson',
  boler_exc_new_hires:           'boler_exc_new_hires',
  boler_je_hendrickson:           'boler_je_hendrickson',
  // BOLER · 5 Excel workbooks — recommend the 4-stage JE distribution pipeline
  boler_xlsx_cigna_roster:           'boler_xlsx_cigna_roster',
  boler_xlsx_hris_master:             'boler_xlsx_hris_master',
  boler_xlsx_division_allocation:     'boler_xlsx_division_allocation',
  boler_xlsx_exception_register:      'boler_xlsx_exception_register',
  boler_xlsx_consolidated_je:         'boler_xlsx_consolidated_je',
};

/** Map an ApexLens sample to the Agent Hub demo param. CBB samples use
 *  ?demo=1/2/3 (matches the spec's §3.6 pre-loaded chats); everything else
 *  falls back to the legacy ?doc= param. */
const AGENT_HUB_LINK: Record<SampleKey, string> = {
  order_mod:   '/agent-hub?demo=1',
  qc_batch:    '/agent-hub?demo=2',
  port_strike: '/agent-hub?demo=3',
  invoice:     '/agent-hub?doc=invoice',
  claim:       '/agent-hub?doc=claim',
  po:          '/agent-hub?doc=po',
  qc:          '/agent-hub?doc=qc',
  contract:    '/agent-hub?doc=contract',
  alert:       '/agent-hub?doc=alert',
  // STP Phase 2 — route each sample to its dedicated AgentCore runtime via
  // the demoMode=stp param on Agent Hub.
  stp_policy:         '/agent-hub?demoMode=stp&doc=stp_policy',
  stp_pm_history:     '/agent-hub?demoMode=stp&doc=stp_pm_history',
  stp_issue_analysis: '/agent-hub?demoMode=stp&doc=stp_issue_analysis',
  stp_predictive:     '/agent-hub?demoMode=stp&doc=stp_predictive',
  // Telecommunications · Verizon Far Edge POC — each sample maps to its
  // dedicated Verizon agent (CertificationAgent · SchemaWatchAgent ·
  // UpgradeAdvisorAgent · MentorAgent).
  tel_robot_xml:       '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  tel_redfish_diff:    '/agent-hub?demoMode=verizon_far_edge&agent=schemawatch-agent',
  tel_upgrade_runbook: '/agent-hub?demoMode=verizon_far_edge&agent=upgrade-advisor-agent',
  tel_kb_article:      '/agent-hub?demoMode=verizon_far_edge&agent=mentor-agent',
  // Verizon Far Edge — 12 real reports → route to the owning agent
  vz_dmtf_e930t:       '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_samsung_ssd:      '/agent-hub?demoMode=verizon_far_edge&agent=schemawatch-agent',
  vz_bmc_upgrade:      '/agent-hub?demoMode=verizon_far_edge&agent=upgrade-advisor-agent',
  vz_ptu_perf:         '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_sensor_proteus:   '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_bios_triton:      '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_redfish_proteus:  '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_platform_deploy:  '/agent-hub?demoMode=verizon_far_edge&agent=upgrade-advisor-agent',
  vz_soak_galene:      '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_dell_sensor:      '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_troubleshoot:     '/agent-hub?demoMode=verizon_far_edge&agent=schemawatch-agent',
  vz_flexran:          '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_cas_el140:        '/agent-hub?demoMode=verizon_far_edge&agent=verizon-orchestrator-agent',
  vz_cas_xr8720:       '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  vz_cas_playbook_spec:'/agent-hub?demoMode=verizon_far_edge&agent=playbook-agent',
  vz_cas_thermal:      '/agent-hub?demoMode=verizon_far_edge&agent=schemawatch-agent',
  vz_cas_wrcp:         '/agent-hub?demoMode=verizon_far_edge&agent=certification-agent',
  // Agentic Enterprise (66 Degrees vendor-neutral demos) — each sample
  // routes to its dedicated agent in Agent Hub.
  ae_inventory_alert: '/agent-hub?demoMode=agentic_enterprise&agent=orchestrator-agent',
  ae_lease_pdf:       '/agent-hub?demoMode=agentic_enterprise&agent=lease-agent',
  // EPROD · Oil & Gas — Midstream. Route every sample to the EPROD demo
  // workspace in Agent Hub via demoMode=oil_gas_midstream.
  eprod_inv_hal:       '/agent-hub?demoMode=oil_gas_midstream&doc=invoice',
  eprod_inv_slb:       '/agent-hub?demoMode=oil_gas_midstream&doc=invoice',
  eprod_inv_bhi:       '/agent-hub?demoMode=oil_gas_midstream&doc=invoice',
  eprod_inv_kiewit:    '/agent-hub?demoMode=oil_gas_midstream&doc=invoice',
  eprod_po_epc:        '/agent-hub?demoMode=oil_gas_midstream&doc=purchase_order',
  eprod_po_chem:       '/agent-hub?demoMode=oil_gas_midstream&doc=purchase_order',
  eprod_po_ops:        '/agent-hub?demoMode=oil_gas_midstream&doc=purchase_order',
  eprod_msa_hal:       '/agent-hub?demoMode=oil_gas_midstream&doc=msa',
  eprod_msa_kiewit:    '/agent-hub?demoMode=oil_gas_midstream&doc=msa',
  eprod_quote_fluor:   '/agent-hub?demoMode=oil_gas_midstream&doc=engineering_quote',
  eprod_quote_bechtel: '/agent-hub?demoMode=oil_gas_midstream&doc=engineering_quote',
  eprod_tariff_ngl:    '/agent-hub?demoMode=oil_gas_midstream&doc=tariff_sheet',
  eprod_tariff_crude:  '/agent-hub?demoMode=oil_gas_midstream&doc=tariff_sheet',
  eprod_jib_p66:       '/agent-hub?demoMode=oil_gas_midstream&doc=jib_statement',
  eprod_jib_targa:     '/agent-hub?demoMode=oil_gas_midstream&doc=jib_statement',
  // CWFCU · CommunityWide Federal Credit Union — every sample routes to
  // its primary handling agent in the CWFCU demo workspace.
  cwfcu_cip_rosales:        '/agent-hub?demoMode=cwfcu&agent=cwfcu-onboarding-agent',
  cwfcu_cip_nguyen:         '/agent-hub?demoMode=cwfcu&agent=cwfcu-onboarding-agent',
  cwfcu_cip_arrington:      '/agent-hub?demoMode=cwfcu&agent=cwfcu-onboarding-agent',
  cwfcu_cip_okafor:         '/agent-hub?demoMode=cwfcu&agent=cwfcu-onboarding-agent',
  cwfcu_sar_structuring:    '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_sar_rapid_movement: '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_sar_layering:       '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_ctr_cash:           '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_ctr_wire:           '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_cdd_04421:          '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_cdd_08812:          '/agent-hub?demoMode=cwfcu&agent=cwfcu-compliance-agent',
  cwfcu_loan_auto:          '/agent-hub?demoMode=cwfcu&agent=cwfcu-loan-agent',
  cwfcu_loan_heloc_johnson: '/agent-hub?demoMode=cwfcu&agent=cwfcu-loan-agent',
  cwfcu_loan_mortgage_patel:'/agent-hub?demoMode=cwfcu&agent=cwfcu-loan-agent',
  cwfcu_loan_personal_williams: '/agent-hub?demoMode=cwfcu&agent=cwfcu-loan-agent',
  cwfcu_paystub_nguyen:     '/agent-hub?demoMode=cwfcu&agent=cwfcu-loan-agent',
  cwfcu_contract_fiserv:    '/agent-hub?demoMode=cwfcu&agent=cwfcu-vendor-agent',
  cwfcu_contract_eltropy:   '/agent-hub?demoMode=cwfcu&agent=cwfcu-vendor-agent',
  cwfcu_contract_coop:      '/agent-hub?demoMode=cwfcu&agent=cwfcu-vendor-agent',
  cwfcu_contract_diebold:   '/agent-hub?demoMode=cwfcu&agent=cwfcu-vendor-agent',
  cwfcu_policy_bsa_roster:  '/agent-hub?demoMode=cwfcu&agent=cwfcu-policy-agent',
  cwfcu_board_res_vendor_mgmt: '/agent-hub?demoMode=cwfcu&agent=cwfcu-policy-agent',
  /* BOLER · 14 sample files */
  boler_cigna_medical:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_delta_dental:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_fidelity_401k:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_vsp_vision:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_hartford_life:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_cigna_std_ltd:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_exc_chen:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_exc_martinez:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_exc_cigna_drift:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_exc_transfers:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_exc_401k:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_exc_thompson:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_exc_new_hires:           '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_je_hendrickson:           '/agent-hub?demoMode=boler&agent=boler-je-agent',
  // BOLER · Excel workbooks → route to the appropriate agent
  boler_xlsx_cigna_roster:           '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_xlsx_hris_master:             '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_xlsx_division_allocation:     '/agent-hub?demoMode=boler&agent=boler-benefits-agent',
  boler_xlsx_exception_register:      '/agent-hub?demoMode=boler&agent=boler-exception-agent',
  boler_xlsx_consolidated_je:         '/agent-hub?demoMode=boler&agent=boler-je-agent',
};

/* ──────────────────────── animation state ──────────────────────── */

type StageState = 'pending' | 'active' | 'done';

interface PipelineStatus {
  stages: [StageState, StageState, StageState, StageState, StageState];
  lines:  [boolean, boolean, boolean, boolean];
  subs:   [string, string, string, string, string];
}
const INITIAL_STATUS: PipelineStatus = {
  stages: ['pending', 'pending', 'pending', 'pending', 'pending'],
  lines:  [false, false, false, false],
  subs:   ['', '', '', '', ''],
};

/* ──────────────────────── component ──────────────────────── */

interface UploadedFileInfo {
  name: string;
  size: string;      // human-readable
}

export default function ApexLensPage() {
  const router = useRouter();
  // Live-reactive brand for the in-page heading.
  const [brand] = useProductBrand();
  const apexLensLabel = brandLabel('ApexLens', brand);

  // Demo-mode aware sample list. STP demo currently has no bespoke Lens
  // samples, so we surface a curated fallback so the page isn't empty.
  const [demoMode] = useDemoMode();
  const visibleSamples: SampleKey[] = useMemo(() => {
    if (demoMode === 'all') return SAMPLE_ORDER;
    return SAMPLE_ORDER.filter((k) => isIndustryVisible(SAMPLE_INDUSTRY[k], demoMode));
  }, [demoMode]);

  // Two separate selections:
  //   previewKey — what the center column is showing in read-only preview mode
  //   runningKey — the pipeline currently animating (set by "Run pipeline")
  // When runningKey is set, it also governs the right-column results.
  const [previewKey, setPreviewKey] = useState<SampleKey | null>(null);
  const [runningKey, setRunningKey] = useState<SampleKey | null>(null);

  const [status, setStatus]                 = useState<PipelineStatus>(INITIAL_STATUS);
  const [fieldsVisible, setFieldsVisible]   = useState(false);
  const [resultsVisible, setResultsVisible] = useState(false);
  const timeoutsRef = useRef<ReturnType<typeof setTimeout>[]>([]);

  // Upload flow: captured file metadata + pipeline selection modal.
  const [uploadedFile, setUploadedFile] = useState<UploadedFileInfo | null>(null);
  const [chooserOpen, setChooserOpen]   = useState(false);

  const previewSample = previewKey ? SAMPLES[previewKey] : null;
  const runningSample = runningKey ? SAMPLES[runningKey] : null;
  // The center + right columns show the pipeline once a run has started; until
  // then they show whichever sample is being previewed.
  const displaySample = runningSample ?? previewSample;

  useEffect(() => () => {
    timeoutsRef.current.forEach(clearTimeout);
  }, []);

  /** Open a sample in read-only preview mode (does NOT run the pipeline). */
  const previewSampleFile = (key: SampleKey) => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];
    setPreviewKey(key);
    setRunningKey(null);
    setStatus(INITIAL_STATUS);
    setFieldsVisible(false);
    setResultsVisible(false);
  };

  /** Kick off the 5-stage pipeline animation for a sample. */
  const runPipeline = (key: SampleKey) => {
    timeoutsRef.current.forEach(clearTimeout);
    timeoutsRef.current = [];

    const s = SAMPLES[key];
    setPreviewKey(key);
    setRunningKey(key);
    setStatus(INITIAL_STATUS);
    setFieldsVisible(false);
    setResultsVisible(false);

    // Ref animation: at delay (i+1)*800, set stage i (0-indexed) active and
    // mark stage i-1 done with its sub-label. At i=4 also mark stage 4 done.
    const delays = [800, 1600, 2400, 3200, 4000];
    delays.forEach((delay, i) => {
      timeoutsRef.current.push(
        setTimeout(() => {
          setStatus((prev) => {
            const stages = [...prev.stages] as PipelineStatus['stages'];
            const lines  = [...prev.lines]  as PipelineStatus['lines'];
            const subs   = [...prev.subs]   as PipelineStatus['subs'];
            if (i > 0) {
              stages[i - 1] = 'done';
              lines[i - 1]  = true;
              subs[i - 1]   = s.subLabels[i - 1];
            }
            stages[i] = i === 4 ? 'done' : 'active';
            if (i === 4) {
              subs[4]  = s.subLabels[4];
              lines[3] = true;
            }
            return { stages, lines, subs };
          });
          if (i === 1) setFieldsVisible(true);
          if (i === 4) setResultsVisible(true);
        }, delay),
      );
    });
  };

  /** Uploading a real file: we don't know the content, so ask the user which
   *  pipeline to run before triggering the animation. */
  const onFileChosen = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const f = files[0];
    setUploadedFile({ name: f.name, size: humanSize(f.size) });
    setChooserOpen(true);
  };

  const confirmPipelineChoice = (pipelineId: SampleKey) => {
    setChooserOpen(false);
    runPipeline(pipelineId);
  };

  return (
    <>
      <Head><title>{__brandedApexLensTitle()}</title></Head>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>{apexLensLabel}</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>
            Drop a document. The agent sees everything.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            className="btn btn-secondary"
            onClick={() => document.getElementById('apex-file-input')?.click()}
          >
            <Icon name="upload" className="" style={{ width: 16, height: 16 }} />
            Upload File
          </button>
          <button className="btn btn-primary">
            <Icon name="refresh" className="" style={{ width: 16, height: 16 }} />
            View History
          </button>
        </div>
      </div>

      {/* Three-column card */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '300px 1fr 320px',
          height: 'calc(100vh - 200px)',
          background: '#fff',
          borderRadius: 16,
          border: '1px solid #f1f5f9',
          overflow: 'hidden',
        }}
      >
        {/* LEFT */}
        <LeftColumn
          activeKey={previewKey}
          runningKey={runningKey}
          onPreview={previewSampleFile}
          onRun={runPipeline}
          onDrop={onFileChosen}
          visibleSamples={visibleSamples}
        />

        {/* CENTER */}
        <div style={{
          borderLeft: '1px solid #f1f5f9',
          borderRight: '1px solid #f1f5f9',
          display: 'flex',
          flexDirection: 'column',
          background: '#f8fafc',
          overflow: 'hidden',
        }}>
          {displaySample && runningKey ? (
            <>
              <DocBar sample={displaySample} />
              <PipelineBar status={status} />
              <ExtractedFields fields={displaySample.fields} visible={fieldsVisible} />
            </>
          ) : displaySample ? (
            <FilePreview
              sample={displaySample}
              onRun={() => runPipeline(displaySample.key)}
            />
          ) : (
            <CenterEmptyState />
          )}
        </div>

        {/* RIGHT */}
        <div
          className="light-scroll"
          style={{ display: 'flex', flexDirection: 'column', overflowY: 'auto' }}
        >
          {runningSample && resultsVisible ? (
            <ResultsPanel
              sample={runningSample}
              onOpenHub={() => router.push(AGENT_HUB_LINK[runningSample.key])}
            />
          ) : previewSample && !runningKey ? (
            <PreviewSidePanel
              sample={previewSample}
              onRun={() => runPipeline(previewSample.key)}
            />
          ) : (
            <RightEmptyState />
          )}
        </div>
      </div>

      {/* Pipeline chooser — shown after an upload */}
      {chooserOpen && uploadedFile && (
        <PipelineChooser
          file={uploadedFile}
          demoMode={demoMode}
          onClose={() => { setChooserOpen(false); setUploadedFile(null); }}
          onChoose={confirmPipelineChoice}
        />
      )}
    </>
  );
}

function humanSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/* ──────────────────────── LEFT column ──────────────────────── */

function LeftColumn({
  activeKey, runningKey, onPreview, onRun, onDrop, visibleSamples,
}: {
  activeKey: SampleKey | null;
  runningKey: SampleKey | null;
  onPreview: (k: SampleKey) => void;
  onRun:     (k: SampleKey) => void;
  onDrop: (files: FileList | null) => void;
  visibleSamples: SampleKey[];
}) {
  const [dragOver, setDragOver] = useState(false);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Drop zone */}
      <div style={{ padding: 16, borderBottom: '1px solid #f8fafc' }}>
        <div
          style={{
            fontSize: 11, fontWeight: 700, letterSpacing: '.1em',
            textTransform: 'uppercase', color: '#94a3b8', marginBottom: 12,
          }}
        >
          Drop Zone
        </div>
        <div
          onClick={() => document.getElementById('apex-file-input')?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            onDrop(e.dataTransfer.files);
          }}
          style={{
            border: `2px dashed ${dragOver ? '#2563eb' : '#e2e8f0'}`,
            borderRadius: 14,
            padding: '28px 16px',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all .2s',
            background: dragOver ? '#eff6ff' : '#fafafa',
          }}
        >
          <Icon name="cloud_up" className="" style={{ width: 40, height: 40, color: '#cbd5e1' }} />
          <p style={{ fontSize: 13, fontWeight: 600, color: '#374151', marginTop: 10 }}>
            Drop a document here
          </p>
          <p style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
            PDF · DOCX · ZIP · XML · PNG · TIFF · TXT · JSON · CSV
          </p>
          <button
            className="btn btn-primary btn-sm"
            style={{ marginTop: 14 }}
            onClick={(e) => { e.stopPropagation(); document.getElementById('apex-file-input')?.click(); }}
          >
            Browse Files
          </button>
          <input
            id="apex-file-input"
            type="file"
            style={{ display: 'none' }}
            accept=".pdf,.docx,.png,.tiff,.zip,.xml,.txt,.json,.csv"
            onChange={(e) => onDrop(e.target.files)}
          />
        </div>
      </div>

      <div style={{ padding: '12px 16px', borderBottom: '1px solid #f8fafc' }}>
        <div style={{
          fontSize: 11, fontWeight: 700, letterSpacing: '.1em',
          textTransform: 'uppercase', color: '#94a3b8',
        }}>
          Sample Documents
        </div>
      </div>

      <div className="light-scroll" style={{ flex: 1, overflowY: 'auto' }}>
        {visibleSamples.map((key) => (
          <SampleRow
            key={key}
            sample={SAMPLES[key]}
            active={activeKey === key}
            running={runningKey === key}
            onPreview={() => onPreview(key)}
            onRun={() => onRun(key)}
          />
        ))}
      </div>
    </div>
  );
}

function SampleRow({
  sample, active, running, onPreview, onRun,
}: {
  sample: Sample;
  active: boolean;
  running: boolean;
  onPreview: () => void;
  onRun: () => void;
}) {
  return (
    <div
      onClick={onPreview}
      className={`work-item ${active ? 'active' : ''}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 6,
        padding: '13px 16px',
        cursor: 'pointer',
        background: active ? '#eff6ff' : 'transparent',
        borderLeft: active ? '3px solid #3b82f6' : '3px solid transparent',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{
          width: 36, height: 36, borderRadius: 10, background: sample.iconBg,
          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
        }}>
          <svg style={{ width: 18, height: 18, color: sample.iconColor }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={sample.iconPath} />
          </svg>
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: 13, fontWeight: 600, color: '#0f172a',
            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
          }}>
            {sample.name}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 3 }}>
            <span className={sample.chipCls} style={{ fontSize: 10 }}>{sample.type}</span>
            <span style={{ fontSize: 11, color: '#94a3b8' }}>{sample.fileSize}</span>
          </div>
        </div>
        <Icon
          name="arrow_right"
          className=""
          style={{ width: 14, height: 14, color: active ? '#3b82f6' : '#cbd5e1', flexShrink: 0 }}
        />
      </div>
      {/* Sub-link: click-through to run the pipeline for this file. */}
      <div style={{ paddingLeft: 48, display: 'flex', alignItems: 'center', gap: 8 }}>
        <button
          type="button"
          onClick={(e) => { e.stopPropagation(); onRun(); }}
          style={{
            fontSize: 11, fontWeight: 600,
            color: running ? '#059669' : '#2563eb',
            background: 'transparent', border: 'none',
            padding: 0, cursor: 'pointer', textDecoration: 'underline',
          }}
          title={`Run ${PIPELINE_OPTIONS.find((p) => p.id === sample.key)?.name ?? 'pipeline'}`}
        >
          {running ? '● pipeline running' : 'Run pipeline →'}
        </button>
      </div>
    </div>
  );
}

/* ──────────────────────── CENTER column ──────────────────────── */

function CenterEmptyState() {
  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 16, padding: 40,
    }}>
      <svg style={{ width: 64, height: 64, color: '#e2e8f0' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={ICONS.search} />
      </svg>
      <div style={{ textAlign: 'center' }}>
        <p style={{ fontSize: 15, fontWeight: 600, color: '#374151' }}>Select a document to begin</p>
        <p style={{ fontSize: 13, color: '#94a3b8', marginTop: 6 }}>
          Choose from the sample library or drop a file
        </p>
      </div>
    </div>
  );
}

function DocBar({ sample }: { sample: Sample }) {
  return (
    <div style={{
      padding: '14px 20px',
      borderBottom: '1px solid #e2e8f0',
      background: '#fff',
      display: 'flex',
      alignItems: 'center',
      gap: 10,
    }}>
      <svg style={{ width: 16, height: 16, color: '#6b7280' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={ICONS.doc} />
      </svg>
      <span style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{sample.name}</span>
      <span className={sample.chipCls} style={{ fontSize: 10 }}>{sample.type}</span>
      <span style={{ fontSize: 12, color: '#64748b', marginLeft: 'auto' }}>Agent: {sample.agent}</span>
    </div>
  );
}

function PipelineBar({ status }: { status: PipelineStatus }) {
  return (
    <div style={{
      padding: '24px 20px',
      background: '#fff',
      borderBottom: '1px solid #f1f5f9',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'center', gap: 0 }}>
        {STAGE_LABELS.map((label, i) => (
          <React.Fragment key={label}>
            <StageNode
              state={status.stages[i]}
              label={label}
              sub={status.subs[i]}
              iconPath={STAGE_ICON_PATHS[i]}
            />
            {i < STAGE_LABELS.length - 1 && (
              <div
                style={{
                  width: 48,
                  height: 2,
                  marginTop: 22,
                  background: status.lines[i] ? '#059669' : '#e2e8f0',
                  transition: 'background .4s',
                  flexShrink: 0,
                }}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

function StageNode({ state, label, sub, iconPath }: {
  state: StageState;
  label: string;
  sub: string;
  iconPath: string;
}) {
  // Done circles swap to a bold checkmark; active circles keep their original icon + pulse.
  const isDone   = state === 'done';
  const isActive = state === 'active';
  const bg       = isDone ? '#059669' : isActive ? '#2563eb' : '#f1f5f9';
  const border   = isDone ? '#059669' : isActive ? '#2563eb' : '#e2e8f0';
  const iconColor= isDone || isActive ? '#fff' : '#94a3b8';
  const labelColor = isDone ? '#065f46' : isActive ? '#1e40af' : '#94a3b8';
  const checkPath = 'M5 13l4 4L19 7';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, minWidth: 80 }}>
      <div
        className={isActive ? 'animate-pulse' : ''}
        style={{
          width: 44, height: 44, borderRadius: '50%',
          background: bg, border: `2px solid ${border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all .4s',
        }}
      >
        <svg style={{ width: 20, height: 20, color: iconColor }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={isDone ? 2.5 : 2} d={isDone ? checkPath : iconPath} />
        </svg>
      </div>
      <div style={{ fontSize: 11, fontWeight: 600, color: labelColor, textAlign: 'center' }}>
        {label}
      </div>
      <div style={{ fontSize: 10, color: '#64748b', textAlign: 'center', minHeight: 14 }}>
        {sub}
      </div>
    </div>
  );
}

function ExtractedFields({ fields, visible }: { fields: FieldRow[]; visible: boolean }) {
  return (
    <div
      className="light-scroll"
      style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px 20px',
        opacity: visible ? 1 : 0,
        transition: 'opacity .6s',
      }}
    >
      <div style={{
        fontSize: 11, fontWeight: 700, letterSpacing: '.1em',
        textTransform: 'uppercase', color: '#94a3b8', marginBottom: 12,
      }}>
        Extracted Fields
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {fields.map((f) => (
          <FieldCard key={f.name} field={f} />
        ))}
      </div>
    </div>
  );
}

function FieldCard({ field }: { field: FieldRow }) {
  const isNA = field.conf === null;
  const confColor =
    isNA               ? '#94a3b8'
  : field.conf! >= 90  ? '#16a34a'
  : field.conf! >= 70  ? '#d97706'
  :                      '#dc2626';

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '8px 12px', background: '#fff',
      border: '1px solid #f1f5f9', borderRadius: 10,
    }}>
      <span style={{ fontSize: 12, color: '#64748b', minWidth: 110, flexShrink: 0 }}>
        {field.name}
      </span>
      <span style={{ fontSize: 12, fontWeight: 500, color: '#0f172a', flex: 1, wordBreak: 'break-word' }}>
        {field.value}
      </span>
      {!isNA && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
          <div style={{ width: 60, height: 4, background: '#e2e8f0', borderRadius: 99, overflow: 'hidden' }}>
            <div style={{
              height: '100%', width: `${field.conf}%`,
              background: confColor, borderRadius: 99,
              transition: 'width .4s',
            }} />
          </div>
          <span className="mono" style={{ fontSize: 10, color: confColor, fontWeight: 600, minWidth: 26, textAlign: 'right' }}>
            {field.conf}%
          </span>
        </div>
      )}
    </div>
  );
}

/* ──────────────────────── RIGHT column ──────────────────────── */

function RightEmptyState() {
  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', padding: 32, textAlign: 'center', gap: 12,
    }}>
      <svg style={{ width: 48, height: 48, color: '#e2e8f0' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={ICONS.clipboard} />
      </svg>
      <p style={{ fontSize: 13, color: '#94a3b8' }}>Results will appear here after processing</p>
    </div>
  );
}

function ResultsPanel({ sample, onOpenHub }: { sample: Sample; onOpenHub: () => void }) {
  const confColor = sample.confidence >= 90 ? '#16a34a'
                  : sample.confidence >= 70 ? '#d97706'
                  :                           '#dc2626';
  return (
    <>
      <SectionHeader label="Document Summary">
        <SummaryRow k="Document" v={sample.name} bold />
        <SummaryRow k="Agent"   v={sample.agent} />
        <SummaryRow k="Processing Time" v={sample.time} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 0' }}>
          <span style={{ fontSize: 12, color: '#64748b' }}>Confidence</span>
          <span style={{ fontSize: 18, fontWeight: 800, color: confColor }}>
            {sample.confidence}%
          </span>
        </div>
      </SectionHeader>

      <SectionHeader label="Validation Flags">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {sample.flags.map((f, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <span className={`dot-${f.color}`} style={{ marginTop: 3, flexShrink: 0 }} />
              <span style={{ fontSize: 12, color: '#374151', lineHeight: 1.5 }}>{f.text}</span>
            </div>
          ))}
        </div>
      </SectionHeader>

      <SectionHeader label="Routing Decision">
        <div style={{ fontSize: 13, color: '#0f172a', fontWeight: 500 }}>
          {sample.routing}
        </div>
      </SectionHeader>

      <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8, marginTop: 'auto' }}>
        <button
          className="btn btn-primary"
          onClick={onOpenHub}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          <Icon name="tray" className="" style={{ width: 16, height: 16 }} />
          Open in Agent Hub
        </button>
        <button className="btn btn-secondary" style={{ width: '100%', justifyContent: 'center' }}>
          <Icon name="download" className="" style={{ width: 16, height: 16 }} />
          Download Report
        </button>
      </div>
    </>
  );
}

function SectionHeader({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ padding: 16, borderBottom: '1px solid #f8fafc' }}>
      <div style={{
        fontSize: 11, fontWeight: 700, letterSpacing: '.1em',
        textTransform: 'uppercase', color: '#94a3b8', marginBottom: 10,
      }}>
        {label}
      </div>
      {children}
    </div>
  );
}

/* ──────────────────────── FILE preview (center) ──────────────────────── */

function FilePreview({ sample, onRun }: { sample: Sample; onRun: () => void }) {
  const raw = RAW_CONTENT[sample.key] ?? '(no preview available)';
  const recommended = PIPELINE_OPTIONS.find((p) => p.id === RECOMMENDED_PIPELINE[sample.key]);

  return (
    <>
      {/* Header — same chrome as the running DocBar so the layout doesn't jump */}
      <div style={{
        padding: '14px 20px',
        borderBottom: '1px solid #e2e8f0',
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
      }}>
        <svg style={{ width: 16, height: 16, color: '#6b7280' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={ICONS.doc} />
        </svg>
        <span style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{sample.name}</span>
        <span className={sample.chipCls} style={{ fontSize: 10 }}>{sample.type}</span>
        <span style={{ fontSize: 12, color: '#64748b', marginLeft: 'auto' }}>{sample.fileSize}</span>
      </div>

      {/* Recommended pipeline banner + run CTA */}
      <div style={{
        padding: '14px 20px',
        background: '#fff',
        borderBottom: '1px solid #f1f5f9',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        flexWrap: 'wrap',
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8' }}>
            Recommended pipeline
          </div>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', marginTop: 2 }}>
            {recommended?.name ?? 'No pipeline matched'}
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
            {recommended?.stages}
          </div>
        </div>
        <button className="btn btn-primary" onClick={onRun}>
          <Icon name="bolt" className="" style={{ width: 16, height: 16 }} />
          Run Pipeline
        </button>
      </div>

      {/* Raw content viewer */}
      <div
        className="light-scroll"
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: 20,
        }}
      >
        <div
          className="mono"
          style={{
            background: '#fff',
            border: '1px solid #e2e8f0',
            borderRadius: 12,
            padding: 20,
            fontSize: 12,
            lineHeight: 1.65,
            color: '#1f2937',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            minHeight: '100%',
          }}
        >
          {raw}
        </div>
      </div>
    </>
  );
}

/* ──────────────────────── preview side panel (right) ──────────────────────── */

function PreviewSidePanel({ sample, onRun }: { sample: Sample; onRun: () => void }) {
  const recommended = PIPELINE_OPTIONS.find((p) => p.id === RECOMMENDED_PIPELINE[sample.key]);
  return (
    <>
      <SectionHeader label="File">
        <SummaryRow k="Name" v={sample.name} bold />
        <SummaryRow k="Type" v={sample.type} />
        <SummaryRow k="Size" v={sample.fileSize} />
      </SectionHeader>

      <SectionHeader label="Recommended Pipeline">
        <div style={{ fontSize: 13, fontWeight: 600, color: '#0f172a', marginBottom: 4 }}>
          {recommended?.name ?? '—'}
        </div>
        <div style={{ fontSize: 12, color: '#64748b', lineHeight: 1.5 }}>
          {recommended?.description}
        </div>
        <div className="mono" style={{ fontSize: 11, color: '#94a3b8', marginTop: 8 }}>
          {recommended?.stages}
        </div>
      </SectionHeader>

      <SectionHeader label="What the agent will do">
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {sample.subLabels.map((label, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
              <span style={{
                width: 20, height: 20, borderRadius: 6, background: '#eff6ff',
                color: '#1d4ed8', fontSize: 11, fontWeight: 700,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
              }}>{i + 1}</span>
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: '#0f172a' }}>{STAGE_LABELS[i]}</div>
                <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{label}</div>
              </div>
            </div>
          ))}
        </div>
      </SectionHeader>

      <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 8, marginTop: 'auto' }}>
        <button
          className="btn btn-primary"
          onClick={onRun}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          <Icon name="bolt" className="" style={{ width: 16, height: 16 }} />
          Run Pipeline
        </button>
        <div style={{ fontSize: 11, color: '#94a3b8', textAlign: 'center' }}>
          Processing completes in ~{sample.time}. The agent will then be
          available in Agent Hub for conversation.
        </div>
      </div>
    </>
  );
}

/* ──────────────────────── pipeline chooser modal (uploads) ──────────────────────── */

function PipelineChooser({
  file, demoMode, onClose, onChoose,
}: {
  file: UploadedFileInfo;
  demoMode: DemoMode;
  onClose: () => void;
  onChoose: (id: SampleKey) => void;
}) {
  // Restrict the chooser to pipelines visible in the active demoMode so an
  // STP user doesn't see CBB / Financial Services rows (and vice versa).
  const visibleOptions = useMemo(
    () => (demoMode === 'all'
      ? PIPELINE_OPTIONS
      : PIPELINE_OPTIONS.filter((p) =>
          isIndustryVisible(SAMPLE_INDUSTRY[p.id], demoMode))),
    [demoMode],
  );

  const guessed = guessPipelineForFilename(file.name, demoMode);
  // If the guessed pipeline isn't visible (e.g. CBB guess in STP mode),
  // fall back to the first visible option so the modal opens with a sane
  // pre-selection.
  const initial = visibleOptions.some((p) => p.id === guessed)
    ? guessed
    : (visibleOptions[0]?.id ?? guessed);
  const [selected, setSelected] = useState<SampleKey>(initial);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal"
        style={{ padding: 0, width: 680, maxWidth: '94vw' }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', textTransform: 'uppercase', color: '#94a3b8' }}>File uploaded</div>
            <h3 style={{ fontSize: 17, fontWeight: 700, color: '#0f172a', marginTop: 4 }}>{file.name}</h3>
            <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
              {file.size} · Select a pipeline to process this file
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', fontSize: 22, padding: 0, lineHeight: 1 }}
            aria-label="Close"
          >×</button>
        </div>

        {/* Options list */}
        <div className="light-scroll" style={{ maxHeight: 'min(60vh, 440px)', overflowY: 'auto', padding: 12 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {visibleOptions.map((p) => {
              const picked = selected === p.id;
              const guess  = guessed === p.id;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setSelected(p.id)}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '20px 1fr auto',
                    gap: 14, alignItems: 'center',
                    padding: '12px 16px',
                    borderRadius: 12,
                    border: `1px solid ${picked ? '#2563eb' : '#e2e8f0'}`,
                    background: picked ? '#eff6ff' : '#fff',
                    textAlign: 'left',
                    cursor: 'pointer',
                  }}
                >
                  <span style={{
                    width: 16, height: 16, borderRadius: '50%',
                    border: `2px solid ${picked ? '#2563eb' : '#cbd5e1'}`,
                    background: picked ? '#2563eb' : '#fff',
                    boxShadow: picked ? 'inset 0 0 0 3px #fff' : 'none',
                    flexShrink: 0,
                  }} />
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{p.name}</span>
                      {guess && <span className="chip-blue" style={{ fontSize: 9 }}>RECOMMENDED</span>}
                    </div>
                    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 2 }}>{p.industry}</div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>{p.description}</div>
                    <div className="mono" style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>{p.stages}</div>
                  </div>
                  <Icon name="arrow_right" className="" style={{ width: 14, height: 14, color: picked ? '#2563eb' : '#cbd5e1', flexShrink: 0 }} />
                </button>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid #f1f5f9', display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={() => onChoose(selected)}>
            <Icon name="bolt" className="" style={{ width: 16, height: 16 }} />
            Run {visibleOptions.find((p) => p.id === selected)?.name}
          </button>
        </div>
      </div>
    </div>
  );
}

/** Guess a reasonable pipeline from the uploaded filename.
 *  STP patterns are checked FIRST so a file named `STP-POL-…pdf` or
 *  `WO-STP-…pdf` routes to the Nuclear agents even when "po" or "qc" appear
 *  later in the same filename. */
function guessPipelineForFilename(name: string, demoMode?: string): SampleKey {
  const n = name.toLowerCase();

  // ── Agentic Enterprise patterns (66 Degrees vendor-neutral) ──
  // Lease / commercial real estate documents → LeaseAgent
  if (/lease|landlord|tenant|premises|sublease|cre[-_]?lease/.test(n))
    return 'ae_lease_pdf';
  // Inventory / stockout / supply alerts → OrchestratorAgent
  if (/stockout|inventory[_\s-]?alert|shortage|sku[-_]?alert|reorder/.test(n))
    return 'ae_inventory_alert';

  // ── STP Phase 2 patterns (Nuclear Operations) ──
  // Policy / procedure / Tech Spec → PolicyAgent
  if (/stp[-_]?pol|policy|procedure|tech[_\s-]?spec|0pgp03|odmp/.test(n))
    return 'stp_policy';
  // Work-package / WO PDF / PM history → MaintenanceAgent
  if (/\bwo[-_]|work[_\s-]?(order|package)|pm[_\s-]?history|eam/.test(n))
    return 'stp_pm_history';
  // Incident / failure report → DiagnosticsAgent
  if (/incident|failure|issue[_\s-]?report|root[_\s-]?cause|\bir[-_]\d/.test(n))
    return 'stp_issue_analysis';
  // Sensor / anomaly / vibration / RUL → ReliabilityAgent
  if (/sensor|anomaly|vibration|telemetry|pi[_\s-]?historian|\brul\b|predictive/.test(n))
    return 'stp_predictive';

  // ── CBB / generic patterns ──
  if (/invoice|bill|receipt/.test(n))                  return 'invoice';
  if (/claim|fnol/.test(n))                            return 'claim';
  if (/\bpo\b|purchase[_\s-]?order/.test(n))           return 'po';
  if (/qc[_\s-]?batch|certificates?\.zip$/.test(n))    return 'qc_batch';
  if (/qc|quality|defect/.test(n))                     return 'qc';
  if (/contract|agreement|msa/.test(n))                return 'contract';
  if (/order[_\s-]?mod|modification/.test(n))          return 'order_mod';
  if (/port|strike|disruption/.test(n))                return 'port_strike';
  if (/alert/.test(n))                                 return 'alert';

  // Demo-mode aware default: in STP mode, favour PolicyAgent so an
  // unrecognised filename lands on a Nuclear agent (not a CBB one).
  if (demoMode === 'stp') return 'stp_policy';
  // Default to the Cornerstone flagship flow during the CBB demo window.
  return 'order_mod';
}

function SummaryRow({ k, v, bold }: { k: string; v: string; bold?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, padding: '4px 0', gap: 8 }}>
      <span style={{ color: '#64748b', flexShrink: 0 }}>{k}</span>
      <span
        style={{
          fontWeight: bold ? 600 : 500,
          color: '#0f172a',
          textAlign: 'right',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {v}
      </span>
    </div>
  );
}
