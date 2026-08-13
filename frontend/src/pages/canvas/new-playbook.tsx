/**
 * New Playbook — 4-step wizard.
 * Ported from apex-prototype 2/new-playbook.html.
 */

import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

type Step = 1 | 2 | 3 | 4;

export default function NewPlaybookPage() {
  const [step, setStep] = useState<Step>(1);
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [actionFilter, setActionFilter] = useState<'all' | 'extract' | 'validate' | 'route' | 'notify'>('all');
  const [selected, setSelected] = useState<Record<string, boolean>>({});

  const goStep = (n: Step) => {
    setStep(n);
    if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const stepClass = (i: number) =>
    `step ${i < step ? 'step-done' : i === step ? 'step-active' : 'step-pending'}`;

  const lineClass = (i: number) => `step-line${i < step ? ' step-line-done' : ''}`;

  const toggleSelected = (key: string) => setSelected((s) => ({ ...s, [key]: !s[key] }));

  return (
    <>
      <Head><title>New Playbook | APEX</title></Head>

      {/* Back link */}
      <div style={{ marginBottom: 24 }}>
        <Link href="/canvas" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, color: '#64748b', textDecoration: 'none' }}>
          <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          Back to Canvas
        </Link>
      </div>

      {/* Step bar */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32 }}>
        <div className={stepClass(1)}><div className="step-num">1</div><div className="step-label">Define</div></div>
        <div className={lineClass(1)} />
        <div className={stepClass(2)}><div className="step-num">2</div><div className="step-label">Recipe</div></div>
        <div className={lineClass(2)} />
        <div className={stepClass(3)}><div className="step-num">3</div><div className="step-label">Actions</div></div>
        <div className={lineClass(3)} />
        <div className={stepClass(4)}><div className="step-num">4</div><div className="step-label">Deploy</div></div>
      </div>

      {/* Step 1: Define */}
      {step === 1 && (
        <div style={{ maxWidth: 720 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Define Your Playbook</h2>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 24 }}>Give your playbook a name, describe its purpose, and choose its industry domain.</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div>
                <label className="label">Playbook Name *</label>
                <input className="input" type="text" placeholder="e.g., Invoice Processing & Validation" />
              </div>
              <div>
                <label className="label">Description</label>
                <textarea className="textarea" rows={3} placeholder="Brief summary for the catalog..." />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label className="label">Industry Domain *</label>
                  <select className="select" defaultValue="">
                    <option value="">Select industry...</option>
                    <option>Financial Services</option>
                    <option>Insurance Underwriting</option>
                    <option>Commercial Insurance (CRE)</option>
                    <option>Healthcare Payers</option>
                    <option>Healthcare Providers</option>
                    <option>Aerospace &amp; Defense</option>
                    <option>Real Estate</option>
                    <option>Supply Chain &amp; Manufacturing</option>
                    <option>HR / Recruitment</option>
                    <option>Contact Center</option>
                    <option>General</option>
                  </select>
                </div>
                <div>
                  <label className="label">Persona Tag</label>
                  <select className="select" defaultValue="Business Analyst / Ops Lead">
                    <option>Business Analyst / Ops Lead</option>
                    <option>Operations Specialist</option>
                    <option>Platform Engineer</option>
                    <option>Executive / Commander</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Intent <span style={{ color: '#94a3b8', fontWeight: 400 }}>(plain English — no coding required)</span></label>
                <textarea className="textarea" rows={5} placeholder="e.g., Process incoming vendor invoices by extracting line items, validating amounts against purchase orders, checking for duplicates, and routing for approval if the amount exceeds $10,000. Auto-approve invoices under $10,000 with confidence above 90%." />
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 8, fontSize: 12, color: '#7c3aed', cursor: 'pointer' }}>
                  <svg style={{ width: 14, height: 14 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                  Generate recipe with AI from this intent
                </div>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={() => goStep(2)}>
              Continue to Recipe
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Recipe */}
      {step === 2 && (
        <div style={{ maxWidth: 720 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>Recipe</h2>
                <p style={{ fontSize: 14, color: '#64748b', marginTop: 2 }}>Step-by-step instructions in natural language. Markdown supported.</p>
              </div>
              <button style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 14px', background: '#f5f3ff', color: '#7c3aed', border: '1px solid #ddd6fe', borderRadius: 10, fontSize: 13, fontWeight: 500, cursor: 'pointer' }}>
                <svg style={{ width: 14, height: 14 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                AI Generate
              </button>
            </div>
            <textarea
              className="textarea"
              rows={14}
              style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}
              defaultValue={`## Invoice Processing Recipe

### Step 1: Document Ingestion
- Receive document from Blob trigger or API upload
- Detect document type (invoice, PO, receipt)
- Route non-invoice documents to fallback handler

### Step 2: Data Extraction
- Use BDA Blueprint \`invoice-blueprint-v2\` to extract:
  - Vendor name, address, tax ID
  - Invoice number, date, due date
  - Line items (description, qty, unit price, total)
  - Invoice total, tax amount, PO reference

### Step 3: Validation
- Match invoice PO reference against ERP system
- Check amount variance (tolerance: ±10%)
- Verify vendor is on approved vendor list
- Check for duplicate invoice numbers (last 90 days)

### Step 4: Decision Logic
- IF confidence ≥ 90% AND amount ≤ $10,000 → Auto-approve
- IF confidence ≥ 90% AND amount > $10,000 → Route to manager approval
- IF confidence < 90% OR validation fails → Route to human review queue
- IF duplicate detected → Reject and notify AP team

### Step 5: Output
- Write approved invoices to ERP via Salesforce connector
- Send Slack notification to AP team with summary
- Log all decisions to Cosmos DB audit trail`}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn btn-secondary" onClick={() => goStep(1)}>← Back</button>
            <button className="btn btn-primary" onClick={() => goStep(3)}>
              Continue to Actions
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Actions */}
      {step === 3 && (
        <div style={{ maxWidth: 860 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Attach Actions</h2>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 20 }}>Select actions from the gallery. These will execute in the order shown.</p>

            {/* Selected Actions */}
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#64748b', marginBottom: 10 }}>Selected Actions (5)</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {SELECTED_ACTIONS.map((a, i) => (
                  <div key={a.name} className="field-row" style={{ justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 24, height: 24, borderRadius: 6, background: a.numBg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, fontWeight: 700, color: a.numColor, flexShrink: 0 }}>{i + 1}</div>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>{a.name}</div>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>{a.desc}</div>
                      </div>
                    </div>
                    <span className={`tag tag-${a.tag}`}>{a.tagLabel}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Gallery */}
            <div style={{ borderTop: '1px solid #f1f5f9', paddingTop: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#64748b', marginBottom: 12 }}>Add from Gallery</div>
              <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
                {(['all', 'extract', 'validate', 'route', 'notify'] as const).map((f) => (
                  <button
                    key={f}
                    className={`tab ${actionFilter === f ? 'active' : ''}`}
                    style={{ fontSize: 12, padding: '5px 12px' }}
                    onClick={() => setActionFilter(f)}
                  >
                    {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10 }}>
                {GALLERY.map((g) => (
                  <div
                    key={g.name}
                    className={`action-card ${selected[g.name] ? 'selected' : ''}`}
                    onClick={() => toggleSelected(g.name)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>{g.name}</span>
                      <span className={`tag tag-${g.tag}`}>{g.tagLabel}</span>
                    </div>
                    <p style={{ fontSize: 12, color: '#64748b' }}>{g.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn btn-secondary" onClick={() => goStep(2)}>← Back</button>
            <button className="btn btn-primary" onClick={() => goStep(4)}>
              Review &amp; Deploy
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Deploy */}
      {step === 4 && (
        <div style={{ maxWidth: 720 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Review &amp; Deploy</h2>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 24 }}>Review your playbook configuration before deploying.</p>

            <div style={{ background: '#f8fafc', borderRadius: 14, padding: 20, marginBottom: 20 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <SummaryCell label="Name" value="Invoice Processing & Validation" />
                <SummaryCell label="Industry" value="Financial Services" />
                <SummaryCell label="Actions" value="5 actions configured" />
                <SummaryCell label="Persona" value="Business Analyst / Ops Lead" />
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="label">Deploy Target</label>
              <div style={{ display: 'flex', gap: 12 }}>
                <label style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10, padding: 14, border: '1px solid #e2e8f0', borderRadius: 12, cursor: 'pointer', background: '#f8fafc' }}>
                  <input type="radio" name="deploy-target" value="staging" defaultChecked style={{ accentColor: '#2563eb' }} />
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>Staging</div>
                    <div style={{ fontSize: 11, color: '#94a3b8' }}>Test before production</div>
                  </div>
                </label>
                <label style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 10, padding: 14, border: '1px solid #e2e8f0', borderRadius: 12, cursor: 'pointer', background: '#f8fafc' }}>
                  <input type="radio" name="deploy-target" value="production" style={{ accentColor: '#2563eb' }} />
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>Production</div>
                    <div style={{ fontSize: 11, color: '#94a3b8' }}>Deploy immediately</div>
                  </div>
                </label>
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="label">Agent Name <span style={{ color: '#94a3b8', fontWeight: 400 }}>(auto-generated)</span></label>
              <input className="input" type="text" defaultValue="InvoiceProcessingBot" />
            </div>

            <button
              className="btn btn-lg"
              style={{ width: '100%', justifyContent: 'center', background: '#059669', color: '#fff', borderColor: '#059669' }}
              onClick={() => setShowDeployModal(true)}
            >
              <svg style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
              Deploy Playbook &amp; Create Agent
            </button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <button className="btn btn-secondary" onClick={() => goStep(3)}>← Back</button>
          </div>
        </div>
      )}

      {/* Deploy Success Modal */}
      {showDeployModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ padding: 32, textAlign: 'center' }}>
            <div style={{ width: 56, height: 56, borderRadius: '50%', background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <svg style={{ width: 28, height: 28, color: '#16a34a' }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 8 }}>Playbook Deployed!</h3>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 16 }}>
              Agent <strong>InvoiceProcessingBot</strong> is now running in staging.
            </p>
            <div style={{ background: '#f8fafc', borderRadius: 12, padding: 14, marginBottom: 20, textAlign: 'left' }}>
              <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>Agent ID</div>
              <div className="mono" style={{ fontSize: 12, color: '#374151' }}>agent-inv-proc-20240420-001</div>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Link href="/canvas" className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>Back to Canvas</Link>
              <Link href="/agent-hub" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>View in Agent Hub</Link>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function SummaryCell({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>{value}</div>
    </div>
  );
}

const SELECTED_ACTIONS = [
  { name: 'financial.invoice_extract',    desc: 'Extract invoice data using BDA blueprint',      tag: 'extract',  tagLabel: 'Extract',  numBg: '#eff6ff', numColor: '#2563eb' },
  { name: 'financial.po_match',           desc: 'Match invoice against purchase order',           tag: 'validate', tagLabel: 'Validate', numBg: '#f0fdf4', numColor: '#16a34a' },
  { name: 'financial.duplicate_check',    desc: 'Check for duplicate invoice numbers',            tag: 'validate', tagLabel: 'Validate', numBg: '#f0fdf4', numColor: '#16a34a' },
  { name: 'core.human_review_request',    desc: 'Escalate to human reviewer when confidence is low', tag: 'route', tagLabel: 'Route',   numBg: '#fdf4ff', numColor: '#86198f' },
  { name: 'core.slack_notify',            desc: 'Send Slack notification to AP team',             tag: 'notify',   tagLabel: 'Notify',   numBg: '#fffbeb', numColor: '#b45309' },
];

const GALLERY = [
  { name: 'financial.payment_process',  desc: 'Process payment via ERP connector',         tag: 'execute',  tagLabel: 'Execute' },
  { name: 'core.write_cosmos_db',        desc: 'Persist extracted data to Cosmos DB',        tag: 'store',    tagLabel: 'Store' },
  { name: 'core.email_notify',          desc: 'Send email notification via SES',           tag: 'notify',   tagLabel: 'Notify' },
  { name: 'core.invoke_lambda',         desc: 'Invoke custom Azure Functions function',         tag: 'execute',  tagLabel: 'Execute' },
  { name: 'core.classify_document',     desc: 'Auto-classify document type and route',     tag: 'classify', tagLabel: 'Classify' },
  { name: 'core.validate_rules',        desc: 'Check data against business rules',         tag: 'validate', tagLabel: 'Validate' },
];
