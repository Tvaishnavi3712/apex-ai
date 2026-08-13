/**
 * Human Review — the human-in-the-loop approval queue.
 *
 * Click a pending card → detail panel opens with full context, flagged issues,
 * extracted fields, and a comment box. Approve / Reject / Escalate drives the
 * next pipeline step (animated) and files the decision into History. Items are
 * filterable by state (Pending / Urgent / High / Normal / Approved / Rejected
 * / Escalated).
 */

import React, { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { pushReviewFeedEntry, type ReviewDecision } from '@/lib/reviewFeed';
import { useDemoMode, isIndustryVisible } from '@/lib/demoMode';
import { CwfcuHumanReview } from '@/components/Dashboard/CwfcuHumanReview';
import { BolerHumanReview } from '@/components/Dashboard/BolerHumanReview';
import { VerizonHumanReview } from '@/components/Dashboard/VerizonHumanReview';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/* ═════════════════════ types ═════════════════════ */

type Priority    = 'URGENT' | 'HIGH' | 'NORMAL';
type ReviewState = 'pending' | 'approved' | 'rejected' | 'escalated';

interface NextStep {
  label: string;
  description: string;
  duration_ms: number;
}

interface ExtractedField { k: string; v: string; conf?: number }

interface ReviewItem {
  id: string;
  priority: Priority;
  title: string;
  source: string;
  submitted_at: string;
  playbook: string;
  playbook_id: string;
  amount: string;
  amount_label: string;
  issues: string[];
  reason_tone: 'red' | 'amber' | 'slate';
  extracted: ExtractedField[];
  document_name: string;
  doc_key?: string;              // for the Agent Hub link after approval
  reviewer?: string;
  assigned_to?: string;
  next_on_approve: NextStep;
  next_on_reject:  NextStep;
  next_on_escalate?: NextStep;

  // runtime state (seeded as pending; flipped by user actions)
  state: ReviewState;
  decided_at?: string;
  decided_by?: string;
  comment?: string;
  executing?: { label: string; progress: number }; // progress 0..100 while next step runs
  completed_at?: string;
}

/* ═════════════════════ seed data ═════════════════════ */

const INITIAL_ITEMS: ReviewItem[] = [
  /* ── CBB Demo 1 — Order Mod above tolerance ── */
  {
    id: 'CBB-ORD-1047',
    priority: 'HIGH',
    title: 'Order Modification · Midwest Window & Door',
    source: 'CustomerOpsBot · 7 min ago',
    submitted_at: '09:17:42',
    playbook: 'Zero-Touch Order Modification',
    playbook_id: 'pb-cbb-1',
    amount: '+5.8%',
    amount_label: 'Height variance',
    issues: [
      '⚠ Requested height variance of 5.8% exceeds engineering tolerance (5.0%)',
      '⚠ Production start is in 3 days — any change needs line-manager sign-off',
    ],
    reason_tone: 'amber',
    extracted: [
      { k: 'Order ID',                 v: 'CBB-ORD-1047',                         conf: 99.8 },
      { k: 'Distributor',              v: 'Midwest Window & Door Supply',         conf: 99.1 },
      { k: 'Product SKU',              v: 'CCW-4860-LG',                          conf: 96.8 },
      { k: 'Original dimensions',      v: '48" × 60"',                            conf: 98.1 },
      { k: 'Requested dimensions',     v: '48" × 63.5"',                          conf: 97.4 },
      { k: 'Height variance',          v: '+5.8% (tolerance is ±5%)',             conf: 99.0 },
      { k: 'Quantity',                 v: '24 units',                             conf: 99.4 },
      { k: 'Production start',         v: 'Apr 24, 2026 (in 3 days)',             conf: 95.0 },
      { k: 'Contact email',            v: 'alex.morrison@midwestwindow.com',      conf: 98.6 },
    ],
    document_name: 'Order_Mod_Request_1047.pdf',
    doc_key: 'order_mod',
    next_on_approve: {
      label: 'CRM Update + Notify Distributor',
      description: 'Manager override recorded. Updating Microsoft Dynamics CRM with new dimensions, recalculating lead time, and emailing the distributor with confirmation.',
      duration_ms: 2600,
    },
    next_on_reject: {
      label: 'Decline + Notify Distributor',
      description: 'Emailing distributor with the tolerance rejection reason and suggesting the closest valid dimension.',
      duration_ms: 1800,
    },
    next_on_escalate: {
      label: 'Escalate to VP Operations',
      description: 'Assigning to VP of Operations with a 24-hour SLA clock.',
      duration_ms: 1400,
    },
    state: 'pending',
  },

  /* ── CBB Demo 2 — QC Batch partial hold ── */
  {
    id: 'CBB-QC-B-2142',
    priority: 'URGENT',
    title: 'QC Batch Hold · Ohio Plant 7 · Batch 2142',
    source: 'QCBot · 3 min ago',
    submitted_at: '09:21:05',
    playbook: 'QC Batch Ingestion & Hold',
    playbook_id: 'pb-cbb-2',
    amount: '$32,550',
    amount_label: 'Quarantined value',
    issues: [
      '⚠ LOT-A44 tensile strength 36.5 MPa (spec min 38.0)',
      '⚠ LOT-B12 color ΔE 2.7 (threshold 2.0)',
      '⚠ Plant Line 3 is waiting on these lots for 07:30 AM run',
    ],
    reason_tone: 'red',
    extracted: [
      { k: 'Supplier',           v: 'Apex Vinyl Solutions (SUP-0081)', conf: 99 },
      { k: 'Batch size',         v: '50 certificates',                 conf: 99 },
      { k: 'Passed',             v: '48',                              conf: 99 },
      { k: 'Failed',             v: '2 (LOT-A44, LOT-B12)',            conf: 99 },
      { k: 'LOT-A44 tensile',    v: '36.5 MPa (spec min 38.0)',        conf: 99.6 },
      { k: 'LOT-B12 color ΔE',   v: '2.7 (threshold 2.0)',             conf: 98.9 },
      { k: 'Quarantined value',  v: '$32,550',                         conf: 99 },
      { k: 'Plant destination',  v: 'Ohio Plant 7 · Line 3',            conf: 98.3 },
    ],
    document_name: 'QC_Batch_2142_manifest.zip',
    doc_key: 'qc_batch',
    next_on_approve: {
      label: 'Place SAP hold + Teams alert',
      description: 'Placing SAP S/4HANA inventory hold on LOT-A44 + LOT-B12 and posting to #ohio-plant-7-qc and procurement@cbb.com.',
      duration_ms: 2800,
    },
    next_on_reject: {
      label: 'Manual override release',
      description: 'Clearing holds and logging the override for audit. Requires Plant Manager + QA Director co-sign on next review.',
      duration_ms: 1600,
    },
    next_on_escalate: {
      label: 'Escalate to QA Director',
      description: 'Routing to Sarah Jenkins with photos and tensile report attached.',
      duration_ms: 1400,
    },
    state: 'pending',
  },

  /* ── CBB Demo 3 — Port strike escalation ── */
  {
    id: 'CBB-DIS-4421',
    priority: 'URGENT',
    title: 'Port Strike Reroute · Vinyl Resin',
    source: 'LogisticsBot · 2 min ago',
    submitted_at: '09:22:18',
    playbook: 'Disruption Impact & Reroute',
    playbook_id: 'pb-cbb-3',
    amount: '$1,090,000',
    amount_label: 'Value at risk',
    issues: [
      '⚠ $1.09M revenue at risk across Ohio, Texas, Georgia plants',
      '⚠ Value at risk exceeds Director auto-threshold of $500k',
      '⚠ 7-day supplier delay, 3 affected plants',
    ],
    reason_tone: 'red',
    extracted: [
      { k: 'Alert',            v: 'SC-ALERT-2026-0441 · Port Strike · HIGH',      conf: 99.7 },
      { k: 'Port',             v: 'Port of Savannah, GA',                         conf: 99.1 },
      { k: 'Supplier',         v: 'Chemours Vinyl Resins (SUP-0044)',             conf: 99.3 },
      { k: 'Material',         v: 'Vinyl Resin (PVC Grade A)',                    conf: 99.2 },
      { k: 'Delay',            v: '7 days',                                       conf: 98.9 },
      { k: 'Ohio Plant 7',     v: '1,240 units · $412,000',                       conf: 97.0 },
      { k: 'Texas Plant 14',   v: '980 units · $386,000',                         conf: 97.0 },
      { k: 'Georgia Plant 31', v: '740 units · $292,000',                         conf: 96.0 },
      { k: 'Recommendation',   v: 'Option A — Oxy Vinyls LP · +5% cost · 0-day' },
    ],
    document_name: 'Port_Strike_Alert_VinylResin.xml',
    doc_key: 'port_strike',
    next_on_approve: {
      label: 'Execute Option A (Oxy Vinyls reroute)',
      description: 'Generating PO with Oxy Vinyls LP (+5% cost), notifying 3 plant managers, and updating BOM with the new lead supplier.',
      duration_ms: 3200,
    },
    next_on_reject: {
      label: 'Hold — gather more options',
      description: 'Parking the alert and requesting refreshed supplier capacities. Director will re-review in 4 hours.',
      duration_ms: 1800,
    },
    next_on_escalate: {
      label: 'Escalate to VP Supply Chain',
      description: 'Packaging BOM traversal + all 3 reroute options and sending to VP Supply Chain with a 2-hour clock.',
      duration_ms: 1400,
    },
    state: 'pending',
  },

  /* ── Generic items kept for non-CBB demos ── */
  {
    id: 'WI-3200',
    priority: 'HIGH',
    title: 'Globex Corp Invoice · Q2',
    source: 'InvoiceBot · 18 min ago',
    submitted_at: '09:06:44',
    playbook: 'Invoice Processing & Validation',
    playbook_id: 'pb-1',
    amount: '$87,400',
    amount_label: 'Invoice total',
    issues: [
      '⚠ PO reference PO-2024-0891 not found in ERP',
      '⚠ Amount exceeds auto-approval threshold ($10,000)',
    ],
    reason_tone: 'red',
    extracted: [
      { k: 'Vendor',          v: 'Globex Corp',     conf: 98 },
      { k: 'Invoice #',       v: 'GLX-2024-0441',   conf: 97 },
      { k: 'Invoice date',    v: 'Apr 18, 2026',    conf: 96 },
      { k: 'PO reference',    v: 'PO-2024-0891 ⚠',  conf: 94 },
      { k: 'Subtotal',        v: '$61,800.00',      conf: 99 },
      { k: 'Tax',             v: '$7,035.00',       conf: 98 },
      { k: 'Total',           v: '$87,400.00',      conf: 99 },
      { k: 'Payment terms',   v: 'Net 30',          conf: 95 },
    ],
    document_name: 'Invoice_Globex_GLX-2024-0441.pdf',
    doc_key: 'invoice',
    next_on_approve: {
      label: 'Queue payment · ERP + Slack',
      description: 'Queuing payment in Coupa (Net 30) and notifying AP team in Slack.',
      duration_ms: 2000,
    },
    next_on_reject: {
      label: 'Return to vendor',
      description: 'Emailing Globex AP with the PO-mismatch details and requesting a corrected invoice.',
      duration_ms: 1400,
    },
    state: 'pending',
  },
  {
    id: 'PA-0041',
    priority: 'NORMAL',
    title: 'Prior Auth · MRI',
    source: 'AuthBot · 2 hr ago',
    submitted_at: '07:12:30',
    playbook: 'Prior Authorization',
    playbook_id: 'pb-pa',
    amount: 'MRI',
    amount_label: 'Procedure type',
    issues: [
      'Member eligibility confirmed but procedure requires specialist authorization.',
    ],
    reason_tone: 'slate',
    extracted: [
      { k: 'Member',          v: 'Doe, Jane (MEM-118841)', conf: 99 },
      { k: 'Policy',          v: 'HMO-Gold-2026',           conf: 99 },
      { k: 'Procedure',       v: 'MRI — Lumbar w/o Contrast', conf: 98 },
      { k: 'Ordering Dr.',    v: 'Dr. R. Singh, MD',         conf: 97 },
      { k: 'Justification',   v: 'Radiculopathy 3mo · failed conservative tx', conf: 92 },
    ],
    document_name: 'PA-0041_MRI_request.pdf',
    next_on_approve: {
      label: 'Issue authorization',
      description: 'Generating auth number and notifying ordering provider + member.',
      duration_ms: 1800,
    },
    next_on_reject: {
      label: 'Return for additional records',
      description: 'Sending MD a note requesting additional imaging and PT records.',
      duration_ms: 1200,
    },
    state: 'pending',
  },

  /* ── STP Phase 2 — ReliabilityAgent prediction awaiting human approval ── */
  {
    id: 'STP-RLY-2026-04-30',
    priority: 'URGENT',
    title: 'PM-7B advance · Pump-3A bearing replacement',
    source: 'ReliabilityAgent · 3 min ago',
    submitted_at: '08:14:22',
    playbook: 'Predictive Maintenance',
    playbook_id: 'pb-stp-4',
    amount: '$340,000',
    amount_label: 'Estimated avoidance',
    issues: [
      'P-3A axial vibration trending 0.34 in/s — 13% above 0.30 in/s Tech-Spec limit.',
      'Pattern matches 3 prior bearing-degradation events on this same pump.',
      'ReliabilityAgent recommends PM-7B advance from Day 22 to Day 5.',
    ],
    reason_tone: 'red',
    extracted: [
      { k: 'Equipment',           v: 'P-3A · RCS · Westinghouse Model-93A',     conf: 99 },
      { k: 'Anomaly',             v: 'ANOM-P3A-2026-04-22',                      conf: 99 },
      { k: 'Predicted failure',   v: '11 days (CI 80%: 7-14d, 95%: 5-17d)',     conf: 87 },
      { k: 'Cited prior WOs',     v: 'WO-2025-03311, WO-2025-03987, WO-2026-00188', conf: 99 },
      { k: 'Recommended PM',      v: 'PM-7B (RCP Bearing Inspection / 0PMP-RCS-7B)', conf: 99 },
      { k: 'Avoidance estimate',  v: '$340,000 · 18 outage hours',               conf: 92 },
      { k: 'Audit log',           v: 'AUD-stp-demo-1746068062',                  conf: 99 },
    ],
    document_name: 'STP-RLY-2026-04-30_predictive_alert.pdf',
    doc_key: 'order_mod',
    next_on_approve: {
      label: 'Schedule PM-7B advance',
      description: 'Notifying Operations to schedule PM-7B advance and locking out P-3A per OSHA 1910.147.',
      duration_ms: 2200,
    },
    next_on_reject: {
      label: 'Return to ReliabilityAgent for re-analysis',
      description: 'Re-running RUL prediction with adjusted vibration baseline; alerts engineering.',
      duration_ms: 1600,
    },
    next_on_escalate: {
      label: 'Escalate to System Engineering',
      description: 'Routing to RCS System Engineer for engineering disposition. ASME XI Inspector tagged.',
      duration_ms: 1800,
    },
    state: 'pending',
  },
];

/* ═════════════════════ main component ═════════════════════ */

type FilterKey = 'pending' | 'all' | 'urgent' | 'high' | 'normal' | 'approved' | 'rejected' | 'escalated';

/** Route a review item's playbook to the Agent Hub agent that owns it. */
function playbookToAgent(playbook_id: string): string {
  switch (playbook_id) {
    case 'pb-cbb-1': return 'customerops';
    case 'pb-cbb-2': return 'qcbot';
    case 'pb-cbb-3': return 'logisticsbot';
    case 'pb-1':     return 'invoice';
    case 'pb-pa':    return 'claims';
    default:         return 'invoice';
  }
}

/**
 * Infer the industry of a review item from its id + playbook_id. Used by
 * demoMode to filter out items that don't belong to the active demo.
 */
function inferReviewItemIndustry(item: ReviewItem): string {
  const id  = (item.id || '').toLowerCase();
  const pb  = (item.playbook_id || '').toLowerCase();
  if (id.startsWith('cbb-')   || pb.startsWith('pb-cbb-'))     return 'supply_manufacturing';
  if (id.startsWith('stp-')   || pb.startsWith('pb-stp-')
      || /nuclear|p-3a|edg|pump|reactor/.test(item.title || '')) return 'nuclear_operations';
  if (pb === 'pb-pa' || /policy|underwrit/.test(item.title || ''))   return 'insurance_underwriting';
  if (pb === 'pb-1' || /invoice|vendor/.test(item.title || ''))      return 'financial_services';
  return 'other';
}

/** Coerce a /review-queue API row → ReviewItem. */
function _apiToReviewItem(row: any): ReviewItem | null {
  if (!row || !row.id) return null;
  return {
    id:           row.id,
    priority:     (row.priority || 'NORMAL') as Priority,
    title:        row.title || '',
    source:       row.source || '',
    submitted_at: row.submitted_at || '',
    playbook:     row.playbook || '',
    playbook_id:  row.playbook_id || '',
    amount:       row.amount || '',
    amount_label: row.amount_label || '',
    issues:       Array.isArray(row.issues) ? row.issues : [],
    reason_tone:  (row.reason_tone || 'slate') as ReviewItem['reason_tone'],
    extracted:    Array.isArray(row.extracted) ? row.extracted : [],
    document_name: row.document_name || '',
    doc_key:      row.doc_key,
    next_on_approve:  row.next_on_approve,
    next_on_reject:   row.next_on_reject,
    next_on_escalate: row.next_on_escalate,
    state:        (row.state || 'pending') as ReviewState,
    decided_at:   row.decided_at,
    decided_by:   row.decided_by,
    comment:      row.comment,
  };
}

export default function Review() {
  // CWFCU demo gets a purpose-built Human Review surface — the SAR-2026-0142
  // structuring narrative shown in hitl.html. Generic queue still backs the
  // platform default for every other demo mode.
  const [demoModeTop] = useDemoMode();
  if (demoModeTop === 'cwfcu' || demoModeTop === 'credit_union') {
    return (
      <>
        <Head><title>Human Review · CommunityWide FCU | APEX</title></Head>
        <CwfcuHumanReview />
      </>
    );
  }
  if (demoModeTop === 'boler' || demoModeTop === 'manufacturing_multi_division') {
    return (
      <>
        <Head><title>Human Review · The Boler Company | APEX</title></Head>
        <BolerHumanReview />
      </>
    );
  }
  if (demoModeTop === 'verizon_far_edge' || demoModeTop === 'telecommunications') {
    return (
      <>
        <Head><title>Human Review · Verizon Far Edge | APEX</title></Head>
        <VerizonHumanReview />
      </>
    );
  }
  return <GenericReview />;
}

function GenericReview() {
  // Live review queue from /review-queue. Hardcoded INITIAL_ITEMS is an
  // offline-only fallback used when the API returns nothing.
  const apiQuery = useQuery<{ items: any[] }>({
    queryKey: ['review-queue'],
    queryFn: async () => {
      const r = await fetch(`${API_BASE_URL}/review-queue/?limit=200`);
      if (!r.ok) return { items: [] };
      return r.json();
    },
    retry: false,
    staleTime: 30_000,
  });

  const apiItems = useMemo<ReviewItem[]>(() => {
    const rows = apiQuery.data?.items ?? [];
    return rows.map(_apiToReviewItem).filter((x): x is ReviewItem => x !== null);
  }, [apiQuery.data]);

  // API wins when it returns rows. Otherwise fall back to hardcoded.
  const seed: ReviewItem[] = apiItems.length > 0 ? apiItems : INITIAL_ITEMS;
  const [items, setItems]       = useState<ReviewItem[]>(seed);
  const [filter, setFilter]     = useState<FilterKey>('pending');
  const [openId, setOpenId]     = useState<string | null>(null);
  const [toast, setToast]       = useState<{ msg: string; tone: 'success' | 'info' | 'warn' } | null>(null);

  // Re-seed state when API resolves after first paint.
  useEffect(() => {
    if (apiItems.length > 0) setItems(apiItems);
  }, [apiItems]);

  // Demo-mode filter — collapses the queue to items whose inferred industry
  // matches the active demo. 'all' shows every item.
  const [demoMode] = useDemoMode();
  const itemsInDemoScope = useMemo(
    () => items.filter((i) => isIndustryVisible(inferReviewItemIndustry(i), demoMode)),
    [items, demoMode],
  );

  const counts = useMemo(() => ({
    pending:    itemsInDemoScope.filter(i => i.state === 'pending').length,
    all:        itemsInDemoScope.length,
    urgent:     itemsInDemoScope.filter(i => i.priority === 'URGENT' && i.state === 'pending').length,
    high:       itemsInDemoScope.filter(i => i.priority === 'HIGH'   && i.state === 'pending').length,
    normal:     itemsInDemoScope.filter(i => i.priority === 'NORMAL' && i.state === 'pending').length,
    approved:   itemsInDemoScope.filter(i => i.state === 'approved').length,
    rejected:   itemsInDemoScope.filter(i => i.state === 'rejected').length,
    escalated:  itemsInDemoScope.filter(i => i.state === 'escalated').length,
  }), [itemsInDemoScope]);

  const filtered = itemsInDemoScope.filter((i) => {
    switch (filter) {
      case 'pending':   return i.state === 'pending';
      case 'urgent':    return i.priority === 'URGENT' && i.state === 'pending';
      case 'high':      return i.priority === 'HIGH'   && i.state === 'pending';
      case 'normal':    return i.priority === 'NORMAL' && i.state === 'pending';
      case 'approved':  return i.state === 'approved';
      case 'rejected':  return i.state === 'rejected';
      case 'escalated': return i.state === 'escalated';
      case 'all':
      default:          return true;
    }
  });

  const activeItem = openId ? items.find(i => i.id === openId) ?? null : null;

  const showToast = (msg: string, tone: 'success' | 'info' | 'warn' = 'success') => {
    setToast({ msg, tone });
    window.setTimeout(() => setToast(null), 2600);
  };

  /** Patch a single item immutably. */
  const patchItem = (id: string, patch: Partial<ReviewItem>) =>
    setItems(list => list.map(it => it.id === id ? { ...it, ...patch } : it));

  /** Run the "next step" progress bar then mark the item completed. */
  const runNextStep = (id: string, step: NextStep) => {
    const started = Date.now();
    const tick = () => {
      const pct = Math.min(100, Math.round(((Date.now() - started) / step.duration_ms) * 100));
      patchItem(id, { executing: { label: step.label, progress: pct } });
      if (pct < 100) {
        window.setTimeout(tick, 80);
      } else {
        const finished = new Date();
        patchItem(id, {
          executing: undefined,
          completed_at: finished.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        });
        showToast(`✓ ${id} — ${step.label} complete`);
      }
    };
    tick();
  };

  /* ── decision handlers ── */

  /** Push a feed entry so Agent Hub (and anyone else listening) sees the decision. */
  const publishToFeed = (item: ReviewItem, decision: ReviewDecision, nextStep: string, reviewer: string, comment: string) => {
    pushReviewFeedEntry({
      id:          item.id,
      title:       item.title,
      decision,
      agent_id:    playbookToAgent(item.playbook_id),
      playbook_id: item.playbook_id,
      decided_by:  reviewer || 'You',
      decided_at:  new Date().toISOString(),
      next_step:   nextStep,
      comment:     comment || undefined,
    });
  };

  const approve = (item: ReviewItem, comment: string, reviewer: string) => {
    patchItem(item.id, {
      state:        'approved',
      decided_at:   new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      decided_by:   reviewer || 'You',
      comment,
      executing:    { label: item.next_on_approve.label, progress: 0 },
    });
    publishToFeed(item, 'approved', item.next_on_approve.label, reviewer, comment);
    runNextStep(item.id, item.next_on_approve);
    setOpenId(null);
    showToast(`${item.id} approved — ${item.next_on_approve.label} queued`);
  };

  const reject = (item: ReviewItem, comment: string, reviewer: string) => {
    patchItem(item.id, {
      state:       'rejected',
      decided_at:  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      decided_by:  reviewer || 'You',
      comment,
      executing:   { label: item.next_on_reject.label, progress: 0 },
    });
    publishToFeed(item, 'rejected', item.next_on_reject.label, reviewer, comment);
    runNextStep(item.id, item.next_on_reject);
    setOpenId(null);
    showToast(`${item.id} rejected — ${item.next_on_reject.label}`, 'warn');
  };

  const escalate = (item: ReviewItem, comment: string, reviewer: string) => {
    const nextLabel = item.next_on_escalate?.label ?? 'Escalated to senior reviewer';
    if (!item.next_on_escalate) {
      patchItem(item.id, {
        state: 'escalated',
        decided_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        decided_by: reviewer || 'You',
        comment,
      });
      publishToFeed(item, 'escalated', nextLabel, reviewer, comment);
      setOpenId(null);
      showToast(`${item.id} escalated`, 'info');
      return;
    }
    patchItem(item.id, {
      state:       'escalated',
      decided_at:  new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      decided_by:  reviewer || 'You',
      comment,
      executing:   { label: item.next_on_escalate.label, progress: 0 },
    });
    publishToFeed(item, 'escalated', nextLabel, reviewer, comment);
    runNextStep(item.id, item.next_on_escalate);
    setOpenId(null);
    showToast(`${item.id} escalated — ${item.next_on_escalate.label}`, 'info');
  };

  return (
    <>
      <Head><title>Human Review | APEX</title></Head>

      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Human Review Queue</h2>
        <p style={{ fontSize: 13, color: '#64748b', marginTop: 4 }}>
          Agents route low-confidence or high-value work here. Approve to trigger the next step in the playbook.
        </p>
      </div>

      {/* Filter tabs */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 20, flexWrap: 'wrap', gap: 12,
      }}>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <FilterBtn label={`Pending (${counts.pending})`}      tone="primary" active={filter === 'pending'}   onClick={() => setFilter('pending')} />
          <FilterBtn label={`Urgent (${counts.urgent})`}        tone="danger"  active={filter === 'urgent'}    onClick={() => setFilter('urgent')} />
          <FilterBtn label={`High (${counts.high})`}            tone="neutral" active={filter === 'high'}      onClick={() => setFilter('high')} />
          <FilterBtn label={`Normal (${counts.normal})`}        tone="neutral" active={filter === 'normal'}    onClick={() => setFilter('normal')} />
          <span style={{ borderLeft: '1px solid #e2e8f0', height: 20 }} />
          <FilterBtn label={`Approved (${counts.approved})`}    tone="success" active={filter === 'approved'}  onClick={() => setFilter('approved')} />
          <FilterBtn label={`Rejected (${counts.rejected})`}    tone="neutral" active={filter === 'rejected'}  onClick={() => setFilter('rejected')} />
          <FilterBtn label={`Escalated (${counts.escalated})`}  tone="neutral" active={filter === 'escalated'} onClick={() => setFilter('escalated')} />
          <FilterBtn label={`All (${counts.all})`}              tone="neutral" active={filter === 'all'}       onClick={() => setFilter('all')} />
        </div>
        <div style={{ fontSize: 12, color: '#64748b' }}>
          {counts.pending} pending · {counts.approved + counts.rejected + counts.escalated} decided this session
        </div>
      </div>

      {/* Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(420px,1fr))', gap: 16 }}>
        {filtered.map((item) => (
          <ReviewCard key={item.id} item={item} onOpen={() => setOpenId(item.id)} />
        ))}
        {filtered.length === 0 && (
          <div style={{ gridColumn: '1 / -1', padding: 48, textAlign: 'center', color: '#94a3b8', fontSize: 13 }}>
            Nothing in this bucket right now.
          </div>
        )}
      </div>

      {/* Detail panel */}
      {activeItem && activeItem.state === 'pending' && (
        <DetailPanel
          item={activeItem}
          onClose={() => setOpenId(null)}
          onApprove={approve}
          onReject={reject}
          onEscalate={escalate}
        />
      )}
      {activeItem && activeItem.state !== 'pending' && (
        <DecidedPanel
          item={activeItem}
          onClose={() => setOpenId(null)}
        />
      )}

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: 20, right: 24, zIndex: 200,
          background: toast.tone === 'warn' ? '#7f1d1d' : toast.tone === 'info' ? '#1e3a8a' : '#064e3b',
          color: toast.tone === 'warn' ? '#fee2e2' : toast.tone === 'info' ? '#dbeafe' : '#ecfdf5',
          padding: '10px 16px',
          borderRadius: 8, fontSize: 13, boxShadow: '0 10px 30px rgba(2,6,23,.25)',
        }}>
          {toast.msg}
        </div>
      )}
    </>
  );
}

/* ═════════════════════ card ═════════════════════ */

function ReviewCard({ item, onOpen }: { item: ReviewItem; onOpen: () => void }) {
  const chipClass =
    item.priority === 'URGENT' ? 'chip-red' :
    item.priority === 'HIGH'   ? 'chip-amber' :
    'chip-gray';

  const variantClass =
    item.state === 'approved'  ? '' :
    item.state === 'rejected'  ? ' urgent' :
    item.priority === 'URGENT' ? ' urgent' :
    item.priority === 'HIGH'   ? ' warning' :
    '';

  const reasonBg =
    item.reason_tone === 'red'   ? '#fef2f2' :
    item.reason_tone === 'amber' ? '#fffbeb' :
    '#f8fafc';
  const reasonTitleColor =
    item.reason_tone === 'red'   ? '#dc2626' :
    item.reason_tone === 'amber' ? '#d97706' :
    '#64748b';

  return (
    <div
      className={`review-card${variantClass}`}
      onClick={onOpen}
      style={{ cursor: 'pointer' }}
      role="button"
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
            <span className={chipClass}>{item.priority}</span>
            <span className="mono" style={{ fontSize: 11, color: '#94a3b8' }}>{item.id}</span>
            {item.state === 'approved'  && <span className="chip-green">✓ Approved</span>}
            {item.state === 'rejected'  && <span className="chip-red">✕ Rejected</span>}
            {item.state === 'escalated' && <span className="chip-amber">↑ Escalated</span>}
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: '#0f172a' }}>{item.title}</div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{item.source}</div>
          <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>{item.playbook}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 20, fontWeight: 800, color: '#0f172a' }}>{item.amount}</div>
          <div style={{ fontSize: 11, color: '#94a3b8' }}>{item.amount_label}</div>
        </div>
      </div>

      {item.state === 'pending' && (
        <div style={{ background: reasonBg, borderRadius: 10, padding: 12, marginBottom: 14 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: reasonTitleColor, marginBottom: 6 }}>
            Flagged Issues
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {item.issues.map((issue, idx) => (
              <div key={idx} style={{ fontSize: 12, color: '#374151' }}>{issue}</div>
            ))}
          </div>
        </div>
      )}

      {item.state !== 'pending' && (
        <div style={{ background: item.state === 'approved' ? '#f0fdf4' : item.state === 'rejected' ? '#fef2f2' : '#fffbeb', borderRadius: 10, padding: 12, marginBottom: 14 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: item.state === 'approved' ? '#166534' : item.state === 'rejected' ? '#991b1b' : '#92400e', marginBottom: 6 }}>
            {item.state === 'approved' ? 'Approved' : item.state === 'rejected' ? 'Rejected' : 'Escalated'}
            {item.decided_by && ` · ${item.decided_by}`}
            {item.decided_at && ` · ${item.decided_at}`}
          </div>
          {item.comment && (
            <div style={{ fontSize: 12, color: '#374151', marginBottom: 6, fontStyle: 'italic' }}>
              &ldquo;{item.comment}&rdquo;
            </div>
          )}
          {item.executing && (
            <div style={{ marginTop: 6 }}>
              <div style={{ fontSize: 11, color: '#64748b', marginBottom: 4 }}>
                Running next step: <strong>{item.executing.label}</strong> · {item.executing.progress}%
              </div>
              <div style={{ height: 6, background: '#e2e8f0', borderRadius: 99, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${item.executing.progress}%`, background: '#059669', borderRadius: 99, transition: 'width .1s linear' }} />
              </div>
            </div>
          )}
          {item.completed_at && (
            <div style={{ fontSize: 11, color: '#16a34a', marginTop: 6, fontWeight: 600 }}>
              ✓ Next step completed at {item.completed_at}
            </div>
          )}
        </div>
      )}

      {item.state === 'pending' && (
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            className="btn btn-sm"
            style={{ flex: 1, justifyContent: 'center', background: '#059669', color: '#fff', borderColor: '#059669' }}
            onClick={(e) => { e.stopPropagation(); onOpen(); }}
          >
            Review → Approve
          </button>
          <button
            className="btn btn-secondary btn-sm"
            style={{ flex: 1, justifyContent: 'center' }}
            onClick={(e) => { e.stopPropagation(); onOpen(); }}
          >
            Details
          </button>
        </div>
      )}

      {item.state !== 'pending' && item.doc_key && (
        <Link
          href={`/agent-hub?doc=${item.doc_key}`}
          className="btn btn-secondary btn-sm"
          style={{ width: '100%', justifyContent: 'center' }}
          onClick={(e) => e.stopPropagation()}
        >
          Chat with agent about this
        </Link>
      )}
    </div>
  );
}

/* ═════════════════════ pending detail panel ═════════════════════ */

function DetailPanel({
  item, onClose, onApprove, onReject, onEscalate,
}: {
  item: ReviewItem;
  onClose: () => void;
  onApprove:  (item: ReviewItem, comment: string, reviewer: string) => void;
  onReject:   (item: ReviewItem, comment: string, reviewer: string) => void;
  onEscalate: (item: ReviewItem, comment: string, reviewer: string) => void;
}) {
  // Default reviewer name flips by demo mode so the right person's name
  // appears on each customer's demo. STP → Prasad Kalva, Verizon → James Patchett.
  // Add additional customer mappings here as new demos are run.
  const [demoMode] = useDemoMode();
  const defaultReviewer = (
    demoMode === 'nuclear_operations' || demoMode === 'stp'
      ? 'Prasad Kalva'
      : demoMode === 'verizon_far_edge' || demoMode === 'telecommunications'
        ? 'James Patchett'
        : 'Babbu Singh'
  );
  const KNOWN_DEFAULTS = ['Babbu Singh', 'Prasad Kalva', 'James Patchett'];
  const [comment, setComment]   = useState('');
  const [reviewer, setReviewer] = useState(defaultReviewer);
  const [confirm, setConfirm]   = useState<'approve' | 'reject' | 'escalate' | null>(null);

  // If the user flips demo mode while a detail panel is open, sync the
  // reviewer field — but only if they haven't manually edited it. Skip
  // the sync when reviewer differs from every known default (= user edit).
  useEffect(() => {
    if (KNOWN_DEFAULTS.includes(reviewer)) {
      setReviewer(defaultReviewer);
    }
  }, [defaultReviewer]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <div
        onClick={onClose}
        style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.35)', zIndex: 95 }}
      />
      <aside
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0, width: 640, maxWidth: '94vw', zIndex: 96,
          background: '#fff', display: 'flex', flexDirection: 'column',
          boxShadow: '-12px 0 32px rgba(15,23,42,.15)',
        }}
      >
        {/* Header */}
        <div style={{ padding: '18px 24px', borderBottom: '1px solid #f1f5f9' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                <span className={item.priority === 'URGENT' ? 'chip-red' : item.priority === 'HIGH' ? 'chip-amber' : 'chip-gray'}>{item.priority}</span>
                <span className="mono" style={{ fontSize: 11, color: '#94a3b8' }}>{item.id}</span>
                <span style={{ fontSize: 11, color: '#94a3b8' }}>· submitted {item.submitted_at}</span>
              </div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>{item.title}</h3>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
                Playbook: <Link href={`/canvas/playbook/${item.playbook_id}`} style={{ color: '#2563eb', textDecoration: 'underline' }}>{item.playbook}</Link>
              </div>
            </div>
            <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', fontSize: 22, padding: 0, lineHeight: 1 }}>×</button>
          </div>
        </div>

        {/* Body (scrollable) */}
        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto' }}>
          {/* Flagged issues */}
          <SectionLabel>Flagged Issues</SectionLabel>
          <div style={{ padding: '0 24px 16px' }}>
            <div style={{
              background: item.reason_tone === 'red' ? '#fef2f2' : item.reason_tone === 'amber' ? '#fffbeb' : '#f8fafc',
              borderRadius: 10, padding: 14,
            }}>
              {item.issues.map((issue, idx) => (
                <div key={idx} style={{ fontSize: 13, color: '#374151', marginBottom: idx === item.issues.length - 1 ? 0 : 6 }}>{issue}</div>
              ))}
            </div>
          </div>

          {/* Extracted fields */}
          <SectionLabel>Extracted Fields</SectionLabel>
          <div style={{ padding: '0 24px 16px' }}>
            <div style={{
              border: '1px solid #f1f5f9', borderRadius: 10, overflow: 'hidden',
            }}>
              {item.extracted.map((f, idx) => (
                <div
                  key={idx}
                  style={{
                    display: 'grid', gridTemplateColumns: '140px 1fr 60px',
                    gap: 10, padding: '10px 14px', alignItems: 'center',
                    borderBottom: idx === item.extracted.length - 1 ? 'none' : '1px solid #f1f5f9',
                    fontSize: 12,
                  }}
                >
                  <span style={{ color: '#64748b' }}>{f.k}</span>
                  <span className="mono" style={{ color: '#0f172a' }}>{f.v}</span>
                  <span style={{
                    textAlign: 'right', fontWeight: 600,
                    color: f.conf === undefined || f.conf === null ? '#94a3b8' :
                           f.conf >= 95 ? '#16a34a' :
                           f.conf >= 85 ? '#d97706' : '#dc2626',
                  }}>
                    {f.conf === undefined || f.conf === null ? '—' : `${f.conf.toFixed(0)}%`}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Document */}
          <SectionLabel>Document</SectionLabel>
          <div style={{ padding: '0 24px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
            <svg style={{ width: 18, height: 18, color: '#6b7280' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="mono" style={{ fontSize: 12, color: '#0f172a' }}>{item.document_name}</span>
            {item.doc_key && (
              <Link href={`/apex-lens?doc=${item.doc_key}`} className="btn btn-secondary btn-sm" style={{ marginLeft: 'auto' }}>
                Open in ApexLens
              </Link>
            )}
          </div>

          {/* Next step pill row */}
          <SectionLabel>What happens next</SectionLabel>
          <div style={{ padding: '0 24px 16px', display: 'grid', gap: 10 }}>
            <NextStepCard tone="green"  title="If Approved"   step={item.next_on_approve} />
            <NextStepCard tone="red"    title="If Rejected"   step={item.next_on_reject} />
            {item.next_on_escalate && (
              <NextStepCard tone="amber" title="If Escalated" step={item.next_on_escalate} />
            )}
          </div>

          {/* Reviewer + comment */}
          <SectionLabel>Reviewer note</SectionLabel>
          <div style={{ padding: '0 24px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
            <input
              className="input"
              value={reviewer}
              onChange={(e) => setReviewer(e.target.value)}
              placeholder="Reviewer name"
              style={{ fontSize: 13 }}
            />
            <textarea
              className="textarea"
              rows={3}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Add a note for the audit log (visible on the decided item)"
              style={{ fontSize: 13 }}
            />
          </div>
        </div>

        {/* Footer actions */}
        <div style={{ padding: '14px 20px', borderTop: '1px solid #f1f5f9', display: 'flex', gap: 10 }}>
          <button
            className="btn btn-secondary"
            onClick={() => setConfirm('escalate')}
            disabled={!item.next_on_escalate}
            style={{ flex: 1, justifyContent: 'center' }}
            title={item.next_on_escalate ? 'Escalate to senior reviewer' : 'No escalation path'}
          >
            ↑ Escalate
          </button>
          <button
            className="btn"
            onClick={() => setConfirm('reject')}
            style={{ flex: 1, justifyContent: 'center', background: '#fee2e2', color: '#dc2626', borderColor: '#fecaca' }}
          >
            ✕ Reject
          </button>
          <button
            className="btn"
            onClick={() => setConfirm('approve')}
            style={{ flex: 1, justifyContent: 'center', background: '#059669', color: '#fff', borderColor: '#059669' }}
          >
            ✓ Approve
          </button>
        </div>
      </aside>

      {/* Confirm modal */}
      {confirm && (
        <div className="modal-overlay" onClick={() => setConfirm(null)} style={{ zIndex: 110 }}>
          <div className="modal" style={{ padding: 28 }} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
              {confirm === 'approve'  && 'Approve and run next step?'}
              {confirm === 'reject'   && 'Reject and trigger reject path?'}
              {confirm === 'escalate' && 'Escalate to senior reviewer?'}
            </h3>
            <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>
              {confirm === 'approve'  && item.next_on_approve.description}
              {confirm === 'reject'   && item.next_on_reject.description}
              {confirm === 'escalate' && item.next_on_escalate?.description}
            </p>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setConfirm(null)}>Cancel</button>
              <button
                className="btn btn-primary"
                onClick={() => {
                  if (confirm === 'approve')  onApprove(item, comment, reviewer);
                  if (confirm === 'reject')   onReject(item, comment, reviewer);
                  if (confirm === 'escalate') onEscalate(item, comment, reviewer);
                  setConfirm(null);
                }}
                style={
                  confirm === 'reject'
                    ? { background: '#dc2626', color: '#fff', borderColor: '#dc2626' }
                    : confirm === 'escalate'
                      ? { background: '#d97706', color: '#fff', borderColor: '#d97706' }
                      : { background: '#059669', color: '#fff', borderColor: '#059669' }
                }
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/* ═════════════════════ decided detail panel (read-only) ═════════════════════ */

function DecidedPanel({ item, onClose }: { item: ReviewItem; onClose: () => void }) {
  const toneBg =
    item.state === 'approved' ? '#f0fdf4' :
    item.state === 'rejected' ? '#fef2f2' : '#fffbeb';
  const toneTitle =
    item.state === 'approved' ? '#166534' :
    item.state === 'rejected' ? '#991b1b' : '#92400e';
  const stateLabel = item.state === 'approved' ? 'Approved' : item.state === 'rejected' ? 'Rejected' : 'Escalated';

  return (
    <>
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.35)', zIndex: 95 }} />
      <aside
        style={{
          position: 'fixed', top: 0, right: 0, bottom: 0, width: 560, maxWidth: '94vw', zIndex: 96,
          background: '#fff', display: 'flex', flexDirection: 'column',
          boxShadow: '-12px 0 32px rgba(15,23,42,.15)',
        }}
      >
        <div style={{ padding: '18px 24px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
              <span className={item.state === 'approved' ? 'chip-green' : item.state === 'rejected' ? 'chip-red' : 'chip-amber'}>{stateLabel}</span>
              <span className="mono" style={{ fontSize: 11, color: '#94a3b8' }}>{item.id}</span>
            </div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>{item.title}</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', fontSize: 22, padding: 0, lineHeight: 1 }}>×</button>
        </div>

        <div className="light-scroll" style={{ flex: 1, overflowY: 'auto', padding: '16px 24px' }}>
          <div style={{ background: toneBg, borderRadius: 10, padding: 14, marginBottom: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: toneTitle, marginBottom: 6 }}>
              {stateLabel}{item.decided_by && ` by ${item.decided_by}`}{item.decided_at && ` at ${item.decided_at}`}
            </div>
            {item.comment && (
              <div style={{ fontSize: 13, color: '#374151', fontStyle: 'italic' }}>
                &ldquo;{item.comment}&rdquo;
              </div>
            )}
          </div>

          {item.executing && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, color: '#0f172a', fontWeight: 600, marginBottom: 4 }}>
                Running next step: {item.executing.label}
              </div>
              <div style={{ height: 8, background: '#e2e8f0', borderRadius: 99, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${item.executing.progress}%`, background: '#059669', borderRadius: 99, transition: 'width .1s linear' }} />
              </div>
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>{item.executing.progress}% complete</div>
            </div>
          )}

          {item.completed_at && (
            <div style={{ fontSize: 13, color: '#16a34a', fontWeight: 600, marginBottom: 16 }}>
              ✓ Next step completed at {item.completed_at}
            </div>
          )}

          <SectionLabel>Extracted Fields</SectionLabel>
          <div style={{ border: '1px solid #f1f5f9', borderRadius: 10, overflow: 'hidden', marginBottom: 16 }}>
            {item.extracted.map((f, idx) => (
              <div
                key={idx}
                style={{
                  display: 'grid', gridTemplateColumns: '140px 1fr',
                  gap: 10, padding: '10px 14px', alignItems: 'center',
                  borderBottom: idx === item.extracted.length - 1 ? 'none' : '1px solid #f1f5f9',
                  fontSize: 12,
                }}
              >
                <span style={{ color: '#64748b' }}>{f.k}</span>
                <span className="mono" style={{ color: '#0f172a' }}>{f.v}</span>
              </div>
            ))}
          </div>

          {item.doc_key && (
            <Link href={`/agent-hub?doc=${item.doc_key}`} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              Chat with agent about this item
            </Link>
          )}
        </div>
      </aside>
    </>
  );
}

/* ═════════════════════ helpers ═════════════════════ */

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      padding: '16px 24px 8px',
      fontSize: 11, fontWeight: 700, letterSpacing: '.08em',
      textTransform: 'uppercase', color: '#94a3b8',
    }}>
      {children}
    </div>
  );
}

function NextStepCard({
  tone, title, step,
}: {
  tone: 'green' | 'red' | 'amber';
  title: string;
  step: NextStep;
}) {
  const bg    = tone === 'green' ? '#f0fdf4' : tone === 'red' ? '#fef2f2' : '#fffbeb';
  const color = tone === 'green' ? '#166534' : tone === 'red' ? '#991b1b' : '#92400e';
  const accent= tone === 'green' ? '#059669' : tone === 'red' ? '#dc2626' : '#d97706';
  return (
    <div style={{ background: bg, borderRadius: 10, padding: 12, border: `1px solid ${accent}20` }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color, letterSpacing: '.05em', textTransform: 'uppercase' }}>{title}</span>
        <span style={{ fontSize: 11, color: '#64748b' }}>· ~{Math.round(step.duration_ms / 1000)}s</span>
      </div>
      <div style={{ fontSize: 13, color: '#0f172a', fontWeight: 600 }}>{step.label}</div>
      <div style={{ fontSize: 12, color: '#475569', marginTop: 2 }}>{step.description}</div>
    </div>
  );
}

function FilterBtn({
  label, tone, active, onClick,
}: {
  label: string;
  tone: 'primary' | 'danger' | 'success' | 'neutral';
  active: boolean;
  onClick: () => void;
}) {
  const activeStyle: Record<string, React.CSSProperties> = {
    primary: { background: '#eff6ff', color: '#2563eb', borderColor: '#bfdbfe' },
    danger:  { background: '#fee2e2', color: '#dc2626', borderColor: '#fecaca' },
    success: { background: '#dcfce7', color: '#166534', borderColor: '#bbf7d0' },
    neutral: { background: '#eff6ff', color: '#2563eb', borderColor: '#bfdbfe' },
  };
  const inactive: React.CSSProperties | undefined =
    tone === 'danger'  ? { background: '#fef2f2', color: '#dc2626', borderColor: '#fecaca' } :
    tone === 'success' ? { background: '#f0fdf4', color: '#166534', borderColor: '#bbf7d0' } :
    undefined;
  const style = active ? activeStyle[tone] : inactive;
  return (
    <button className="btn btn-secondary btn-sm" style={style} onClick={onClick}>
      {label}
    </button>
  );
}
