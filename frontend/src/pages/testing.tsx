/**
 * Testing — extraction test sandbox.
 * Ported from apex-prototype 2/testing.html.
 *
 * Pick a blueprint, upload a document, view extraction results.
 * All data is mocked inline to mirror the HTML prototype.
 */

import React, { useRef, useState } from 'react';
import Head from 'next/head';
import { Icon } from '@/components/AppShell/icons';

interface ExtractionField {
  key: string;
  value: string;
  confidence: number;
  bold?: boolean;
}

const BLUEPRINTS = [
  'EPROD Vendor Invoice — Oil & Gas Midstream',
  'EPROD Purchase Order — Oil & Gas Midstream',
  'EPROD Master Service Agreement — Oil & Gas Midstream',
  'EPROD Engineering Quote — Oil & Gas Midstream',
  'EPROD FERC Tariff Sheet — Oil & Gas Midstream ⭐',
  'EPROD JIB Statement — Oil & Gas Midstream ⭐',
  'Invoice Blueprint v2 — Financial Services',
  'Claim Form Blueprint — Insurance',
  'Defense Contract Blueprint — A&D',
  'KYC Document Blueprint — Financial Services',
  'PO Blueprint — Manufacturing',
];

const SAMPLE_RESULT: { filename: string; blueprint: string; fields: ExtractionField[] } = {
  filename: 'sample_invoice_acme.pdf',
  blueprint: 'Invoice Blueprint v2',
  fields: [
    { key: 'vendor_name',    value: 'ACME Corp',      confidence: 97 },
    { key: 'invoice_number', value: 'ACM-2024-3201',  confidence: 99 },
    { key: 'invoice_date',   value: '2026-04-18',     confidence: 98 },
    { key: 'total_amount',   value: '$4,250.00',      confidence: 96, bold: true },
    { key: 'po_reference',   value: 'PO-2024-0788',   confidence: 91 },
    { key: 'line_items',     value: '3 items',        confidence: 84 },
  ],
};

export default function TestingPage() {
  const [blueprint, setBlueprint] = useState(BLUEPRINTS[0]);
  const [filename, setFilename] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<typeof SAMPLE_RESULT | null>(SAMPLE_RESULT);
  const [dragOver, setDragOver] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  function handleFile(f: File | null) {
    if (!f) return;
    setFilename(f.name);
  }

  function runTest() {
    setRunning(true);
    setTimeout(() => {
      setResult({ ...SAMPLE_RESULT, filename: filename || SAMPLE_RESULT.filename });
      setRunning(false);
    }, 800);
  }

  return (
    <>
      <Head><title>Testing | APEX</title></Head>

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700, color: '#0f172a' }}>Testing</h2>
          <p style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>Test extraction blueprints against sample documents</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* ─────────── Left: test setup ─────────── */}
        <div>
          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Test Extraction</h3>
            <p style={{ fontSize: 13, color: '#64748b', marginBottom: 20 }}>Upload a document and test it against a blueprint</p>

            <div style={{ marginBottom: 16 }}>
              <label className="label">Blueprint</label>
              <select
                className="select"
                value={blueprint}
                onChange={(e) => setBlueprint(e.target.value)}
              >
                {BLUEPRINTS.map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>

            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                handleFile(e.dataTransfer.files?.[0] || null);
              }}
              onClick={() => fileInput.current?.click()}
              style={{
                border: `2px dashed ${dragOver ? '#93c5fd' : '#e2e8f0'}`,
                borderRadius: 14,
                padding: 32,
                textAlign: 'center',
                marginBottom: 16,
                cursor: 'pointer',
                transition: 'border-color .15s',
              }}
            >
              <div style={{ fontSize: 24, marginBottom: 8 }}>📄</div>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', marginBottom: 4 }}>
                {filename ? filename : 'Drop test document here'}
              </p>
              <p style={{ fontSize: 12, color: '#94a3b8' }}>PDF, PNG, JPG, TIFF</p>
              <input
                ref={fileInput}
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,.tiff"
                style={{ display: 'none' }}
                onChange={(e) => handleFile(e.target.files?.[0] || null)}
              />
            </div>

            <button
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={runTest}
              disabled={running}
            >
              {running ? (
                <>
                  <Icon name="refresh" className="animate-spin" style={{ width: 16, height: 16 }} /> Running...
                </>
              ) : (
                <>
                  <Icon name="play" style={{ width: 16, height: 16 }} /> Run Extraction Test
                </>
              )}
            </button>
          </div>

          <div className="card" style={{ padding: 20 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <Icon name="info" style={{ width: 16, height: 16, color: '#64748b' }} />
              <h4 style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>Testing Notes</h4>
            </div>
            <ul style={{ fontSize: 12, color: '#64748b', lineHeight: 1.6, paddingLeft: 18 }}>
              <li>Uploads are processed by Azure AI Document Intelligence.</li>
              <li>Results include per-field confidence scores.</li>
              <li>Fields below 85% confidence are flagged for review.</li>
            </ul>
          </div>
        </div>

        {/* ─────────── Right: results ─────────── */}
        <div>
          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Extraction Results</h3>
            <p style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>
              {result ? `${result.filename} · ${result.blueprint}` : 'Run a test to see results'}
            </p>

            {result && (
              <>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    background: '#f0fdf4',
                    border: '1px solid #bbf7d0',
                    borderRadius: 12,
                    padding: '12px 16px',
                    marginBottom: 16,
                  }}
                >
                  <Icon name="check_circle" style={{ width: 16, height: 16, color: '#16a34a', flexShrink: 0 }} />
                  <span style={{ fontSize: 13, color: '#15803d', fontWeight: 500 }}>
                    Extraction successful · {result.fields.length}/{result.fields.length} fields · avg confidence{' '}
                    {Math.round(result.fields.reduce((s, f) => s + f.confidence, 0) / result.fields.length)}%
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {result.fields.map((f) => (
                    <div key={f.key} className="field-row" style={{ justifyContent: 'space-between' }}>
                      <span className="mono" style={{ fontSize: 12, color: '#374151' }}>{f.key}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 12, fontWeight: f.bold ? 600 : 500, color: '#0f172a' }}>{f.value}</span>
                        <span
                          style={{
                            fontSize: 11,
                            fontWeight: 600,
                            color: f.confidence >= 95 ? '#16a34a' : f.confidence >= 85 ? '#d97706' : '#dc2626',
                          }}
                        >
                          {f.confidence}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'flex', gap: 8, marginTop: 20 }}>
                  <button className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Export JSON</button>
                  <button className="btn btn-secondary btn-sm" style={{ flex: 1, justifyContent: 'center' }}>Re-run</button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
