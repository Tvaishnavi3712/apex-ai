/**
 * New Blueprint — 4-step wizard.
 * Ported from apex-prototype 2/new-blueprint.html.
 */

import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

type Step = 1 | 2 | 3 | 4;

interface FieldRow {
  name: string;
  desc: string;
  type: 'string' | 'number' | 'date' | 'boolean' | 'array';
  confidence: number;
}

export default function NewBlueprintPage() {
  const [step, setStep] = useState<Step>(1);
  const [uploaded, setUploaded] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [fields, setFields] = useState<FieldRow[]>(INITIAL_FIELDS);

  const goStep = (n: Step) => {
    setStep(n);
    if (typeof window !== 'undefined') window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const stepClass = (i: number) =>
    `step ${i < step ? 'step-done' : i === step ? 'step-active' : 'step-pending'}`;

  const lineClass = (i: number) => `step-line${i < step ? ' step-line-done' : ''}`;

  const updateField = (idx: number, patch: Partial<FieldRow>) => {
    setFields((f) => f.map((row, i) => (i === idx ? { ...row, ...patch } : row)));
  };
  const removeField = (idx: number) => setFields((f) => f.filter((_, i) => i !== idx));

  return (
    <>
      <Head><title>New Blueprint | APEX</title></Head>

      {/* Back link */}
      <div style={{ marginBottom: 24 }}>
        <Link href="/canvas" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14, color: '#64748b', textDecoration: 'none' }}>
          <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
          Back to Canvas
        </Link>
      </div>

      {/* Step bar */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32 }}>
        <div className={stepClass(1)}><div className="step-num">1</div><div className="step-label">Document Type</div></div>
        <div className={lineClass(1)} />
        <div className={stepClass(2)}><div className="step-num">2</div><div className="step-label">Upload Sample</div></div>
        <div className={lineClass(2)} />
        <div className={stepClass(3)}><div className="step-num">3</div><div className="step-label">Map Fields</div></div>
        <div className={lineClass(3)} />
        <div className={stepClass(4)}><div className="step-num">4</div><div className="step-label">Deploy to BDA</div></div>
      </div>

      {/* Step 1 */}
      {step === 1 && (
        <div style={{ maxWidth: 720 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Define Document Type</h2>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 24 }}>Tell APEX what kind of document this blueprint will extract data from.</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
              <div>
                <label className="label">Blueprint Name *</label>
                <input className="input" type="text" placeholder="e.g., Invoice Blueprint v2" />
              </div>
              <div>
                <label className="label">Description</label>
                <textarea className="textarea" rows={2} placeholder="Brief description of what this blueprint extracts..." />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label className="label">Document Type *</label>
                  <select className="select" defaultValue="Invoice">
                    <option value="">Select type...</option>
                    <option>Invoice</option>
                    <option>Receipt</option>
                    <option>Purchase Order</option>
                    <option>Bank Statement</option>
                    <option>Contract</option>
                    <option>Claim Form</option>
                    <option>Insurance Application</option>
                    <option>Underwriting Submission</option>
                    <option>Medical Record</option>
                    <option>Property Appraisal</option>
                    <option>Defense Contract</option>
                    <option>Work Order</option>
                    <option>RFP / Proposal</option>
                    <option>Engineering Specification</option>
                    <option>Other</option>
                  </select>
                </div>
                <div>
                  <label className="label">Industry *</label>
                  <select className="select" defaultValue="Financial Services">
                    <option value="">Select industry...</option>
                    <option>Financial Services</option>
                    <option>Insurance Underwriting</option>
                    <option>Commercial Insurance (CRE)</option>
                    <option>Healthcare Payers</option>
                    <option>Aerospace &amp; Defense</option>
                    <option>Real Estate</option>
                    <option>Supply Chain &amp; Manufacturing</option>
                    <option>General</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Quick Select</label>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10 }}>
                  <div style={{ padding: 14, border: '2px solid #3b82f6', borderRadius: 12, textAlign: 'center', cursor: 'pointer', background: '#eff6ff' }}>
                    <div style={{ fontSize: 20, marginBottom: 4 }}>🧾</div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#1d4ed8' }}>Invoice</div>
                  </div>
                  <div style={{ padding: 14, border: '1px solid #e2e8f0', borderRadius: 12, textAlign: 'center', cursor: 'pointer' }}>
                    <div style={{ fontSize: 20, marginBottom: 4 }}>📋</div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#64748b' }}>Claim Form</div>
                  </div>
                  <div style={{ padding: 14, border: '1px solid #e2e8f0', borderRadius: 12, textAlign: 'center', cursor: 'pointer' }}>
                    <div style={{ fontSize: 20, marginBottom: 4 }}>📄</div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#64748b' }}>Contract</div>
                  </div>
                  <div style={{ padding: 14, border: '1px solid #e2e8f0', borderRadius: 12, textAlign: 'center', cursor: 'pointer' }}>
                    <div style={{ fontSize: 20, marginBottom: 4 }}>🏥</div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: '#64748b' }}>Medical Record</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={() => goStep(2)}>
              Continue
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Step 2 */}
      {step === 2 && (
        <div style={{ maxWidth: 720 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Upload Sample Document</h2>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 24 }}>Upload a sample document so APEX can detect fields automatically using AI.</p>

            <div style={{ border: '2px dashed #e2e8f0', borderRadius: 16, padding: 48, textAlign: 'center', cursor: 'pointer', transition: 'all .15s', marginBottom: 20 }}>
              <div style={{ width: 56, height: 56, borderRadius: 16, background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                <svg style={{ width: 28, height: 28, color: '#3b82f6' }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
              </div>
              <p style={{ fontSize: 15, fontWeight: 600, color: '#0f172a', marginBottom: 6 }}>Drop your document here</p>
              <p style={{ fontSize: 13, color: '#94a3b8', marginBottom: 16 }}>PDF, PNG, JPG, TIFF — up to 50MB</p>
              <button className="btn btn-secondary" onClick={() => setUploaded(true)}>Browse Files</button>
            </div>

            {uploaded && (
              <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 12, padding: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 8, background: '#dcfce7', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <svg style={{ width: 18, height: 18, color: '#16a34a' }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>sample_invoice_acme.pdf</div>
                    <div style={{ fontSize: 11, color: '#16a34a' }}>Uploaded · 2.4 MB</div>
                  </div>
                </div>
                <button onClick={() => setUploaded(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', padding: 4 }}>✕</button>
              </div>
            )}

            <div style={{ background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 12, padding: 14 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                <svg style={{ width: 16, height: 16, color: '#d97706', flexShrink: 0, marginTop: 1 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                <p style={{ fontSize: 13, color: '#92400e' }}>APEX will use <strong>Amazon Azure AI Document Intelligence</strong> to analyze your document and suggest field definitions automatically. You can review and edit them in the next step.</p>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn btn-secondary" onClick={() => goStep(1)}>← Back</button>
            <button className="btn btn-primary" onClick={() => { setUploaded(true); goStep(3); }}>
              Analyze Document with AI
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Step 3 */}
      {step === 3 && (
        <div style={{ maxWidth: 860 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a' }}>Field Mapping</h2>
                <p style={{ fontSize: 14, color: '#64748b', marginTop: 2 }}>AI detected 12 fields. Review, edit, or add more.</p>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-secondary btn-sm">
                  <svg style={{ width: 14, height: 14 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                  Add Field
                </button>
                <button style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 12px', background: '#f5f3ff', color: '#7c3aed', border: '1px solid #ddd6fe', borderRadius: 8, fontSize: 12, fontWeight: 500, cursor: 'pointer' }}>
                  <svg style={{ width: 14, height: 14 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
                  AI Suggest More
                </button>
              </div>
            </div>

            <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: 12, padding: '12px 16px', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
              <svg style={{ width: 16, height: 16, color: '#2563eb', flexShrink: 0 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
              <p style={{ fontSize: 13, color: '#1e40af' }}>Azure AI Document Intelligence analyzed <strong>sample_invoice_acme.pdf</strong> and detected 12 fields with an average confidence of 94%.</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1.5fr 1fr 80px 32px', gap: 12, padding: '8px 14px' }}>
                <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Field Name</div>
                <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Description</div>
                <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Type</div>
                <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8' }}>Confidence</div>
                <div />
              </div>
              {fields.map((f, idx) => {
                const green = f.confidence >= 90;
                const barColor = green ? '#22c55e' : '#f59e0b';
                const trackColor = green ? '#dcfce7' : '#fef3c7';
                const textColor = green ? '#16a34a' : '#d97706';
                return (
                  <div key={idx} className="field-row" style={{ display: 'grid', gridTemplateColumns: '2fr 1.5fr 1fr 80px 32px', gap: 12, alignItems: 'center' }}>
                    <input
                      className="input mono"
                      style={{ padding: '6px 10px', fontSize: 13 }}
                      value={f.name}
                      onChange={(e) => updateField(idx, { name: e.target.value })}
                    />
                    <input
                      className="input"
                      style={{ padding: '6px 10px', fontSize: 13 }}
                      value={f.desc}
                      onChange={(e) => updateField(idx, { desc: e.target.value })}
                    />
                    <select
                      className="select"
                      style={{ padding: '6px 10px', fontSize: 13 }}
                      value={f.type}
                      onChange={(e) => updateField(idx, { type: e.target.value as FieldRow['type'] })}
                    >
                      <option value="string">string</option>
                      <option value="number">number</option>
                      <option value="date">date</option>
                      <option value="boolean">boolean</option>
                      <option value="array">array</option>
                    </select>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: textColor, marginBottom: 3 }}>{f.confidence}%</div>
                      <div className="confidence-bar" style={{ width: '100%', background: trackColor }}>
                        <div className="confidence-bar" style={{ width: `${f.confidence}%`, background: barColor }} />
                      </div>
                    </div>
                    <button
                      onClick={() => removeField(idx)}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', fontSize: 16 }}
                    >
                      ✕
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <button className="btn btn-secondary" onClick={() => goStep(2)}>← Back</button>
            <button className="btn btn-primary" onClick={() => goStep(4)}>
              Review &amp; Deploy to BDA
              <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Step 4 */}
      {step === 4 && (
        <div style={{ maxWidth: 720 }}>
          <div className="card" style={{ padding: 28, marginBottom: 20 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Deploy to Azure AI Document Intelligence</h2>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 24 }}>Review your blueprint schema and deploy it to AWS Azure OpenAI.</p>

            <div style={{ background: '#f8fafc', borderRadius: 14, padding: 20, marginBottom: 20 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <SummaryCell label="Blueprint Name" value="Invoice Blueprint v2" />
                <SummaryCell label="Document Type" value="Invoice" />
                <SummaryCell label="Fields" value="12 fields mapped" />
                <SummaryCell label="Target Stage" value="DEVELOPMENT" />
              </div>
            </div>

            <div style={{ marginBottom: 20 }}>
              <label className="label">Schema Preview (JSON)</label>
              <div style={{ background: '#0d1117', borderRadius: 12, padding: 16, overflowX: 'auto' }}>
                <pre className="mono" style={{ fontSize: 12, color: '#e6edf3', margin: 0 }}>{SCHEMA_PREVIEW}</pre>
              </div>
            </div>

            <button
              className="btn btn-lg"
              style={{ width: '100%', justifyContent: 'center', background: '#059669', color: '#fff', borderColor: '#059669' }}
              onClick={() => setShowModal(true)}
            >
              <svg style={{ width: 18, height: 18 }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
              Deploy to Amazon Azure AI Document Intelligence
            </button>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <button className="btn btn-secondary" onClick={() => goStep(3)}>← Back</button>
          </div>
        </div>
      )}

      {/* Deploy Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal" style={{ padding: 32, textAlign: 'center' }}>
            <div style={{ width: 56, height: 56, borderRadius: '50%', background: '#f0fdf4', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
              <svg style={{ width: 28, height: 28, color: '#16a34a' }} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            </div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#0f172a', marginBottom: 8 }}>Blueprint Deployed!</h3>
            <p style={{ fontSize: 14, color: '#64748b', marginBottom: 16 }}>Your blueprint is now live in Amazon Azure AI Document Intelligence.</p>
            <div style={{ background: '#f8fafc', borderRadius: 12, padding: 14, marginBottom: 20, textAlign: 'left' }}>
              <div style={{ fontSize: 11, color: '#94a3b8', marginBottom: 4 }}>BDA Blueprint ARN</div>
              <div className="mono" style={{ fontSize: 11, color: '#374151', wordBreak: 'break-all' }}>azure-docintel/457795063704/blueprint/inv-bp-v2-20240420</div>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <Link href="/canvas" className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>Back to Canvas</Link>
              <Link href="/testing" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>Test Extraction</Link>
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

const INITIAL_FIELDS: FieldRow[] = [
  { name: 'vendor_name',    desc: 'Vendor / supplier name',        type: 'string', confidence: 97 },
  { name: 'invoice_number', desc: 'Unique invoice identifier',     type: 'string', confidence: 99 },
  { name: 'invoice_date',   desc: 'Date of invoice issuance',      type: 'date',   confidence: 98 },
  { name: 'total_amount',   desc: 'Total invoice amount (USD)',    type: 'number', confidence: 96 },
  { name: 'line_items',     desc: 'Array of line item objects',    type: 'array',  confidence: 84 },
  { name: 'po_reference',   desc: 'Purchase order reference number', type: 'string', confidence: 91 },
];

const SCHEMA_PREVIEW = `{
  "blueprint_id": "inv-bp-v2",
  "name": "Invoice Blueprint v2",
  "document_type": "invoice",
  "industry": "financial_services",
  "fields": [
    { "name": "vendor_name",    "type": "string",  "required": true  },
    { "name": "invoice_number", "type": "string",  "required": true  },
    { "name": "invoice_date",   "type": "date",    "required": true  },
    { "name": "total_amount",   "type": "number",  "required": true  },
    { "name": "line_items",     "type": "array",   "required": false },
    { "name": "po_reference",   "type": "string",  "required": false }
  ]
}`;
