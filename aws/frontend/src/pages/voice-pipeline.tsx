/**
 * Voice Pipeline — upload/record audio, transcription output, extracted entities.
 * Ported from apex-prototype 2/voice-pipeline.html.
 */

import React from 'react';
import Head from 'next/head';

interface Transcription { filename: string; meta: string }
const TRANSCRIPTIONS: Transcription[] = [
  { filename: 'call_2024_0420_001.mp3',     meta: '2 min · InvoiceBot · 2 hr ago' },
  { filename: 'intake_recording_apr18.wav', meta: '8 min · IntakeBot · Yesterday' },
];

interface Entity { label: string; value: string; valueColor?: string; valueWeight?: number; chip?: boolean }
const ENTITIES: Entity[] = [
  { label: 'Caller',        value: 'Sarah / Globex Corp' },
  { label: 'Invoice #',     value: 'GLX-2024-0441' },
  { label: 'Amount',        value: '$87,400', valueWeight: 600 },
  { label: 'PO Reference',  value: 'PO-2024-0891 \u26A0', valueColor: '#dc2626' },
  { label: 'Intent',        value: 'Status inquiry', chip: true },
];

const MIC_ICON = (
  <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
  </svg>
);

const PLAY_ICON = (
  <svg style={{ width: 16, height: 16 }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

export default function VoicePipeline() {
  return (
    <>
      <Head><title>Voice Pipeline | APEX</title></Head>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        {/* LEFT column */}
        <div>
          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>Voice Processing</h3>
            <p style={{ fontSize: 13, color: '#64748b', marginBottom: 20 }}>
              Upload or record audio for AI transcription and processing
            </p>

            <div
              style={{
                border: '2px dashed #e2e8f0',
                borderRadius: 14,
                padding: 36,
                textAlign: 'center',
                marginBottom: 16,
                cursor: 'pointer',
              }}
              onMouseOver={(e) => (e.currentTarget.style.borderColor = '#93c5fd')}
              onMouseOut={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
            >
              <div style={{ width: 48, height: 48, borderRadius: 14, background: '#f5f3ff', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
                <svg style={{ width: 24, height: 24, color: '#7c3aed' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', marginBottom: 4 }}>
                Drop audio file or click to upload
              </p>
              <p style={{ fontSize: 12, color: '#94a3b8' }}>MP3, WAV, MP4, WEBM — up to 500MB</p>
            </div>

            <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
              <button className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>
                {MIC_ICON}
                Record Live
              </button>
              <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
                {PLAY_ICON}
                Process Demo
              </button>
            </div>

            <div>
              <label className="label">Route to Agent</label>
              <select className="select">
                <option>InvoiceBot — Financial Services</option>
                <option>ClaimsBot — Insurance</option>
                <option>IntakeBot — Contact Center</option>
                <option>CNCBot — Manufacturing</option>
              </select>
            </div>
          </div>

          <div className="card" style={{ padding: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '.06em', color: '#94a3b8', marginBottom: 12 }}>
              Recent Transcriptions
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {TRANSCRIPTIONS.map((t) => (
                <div key={t.filename} className="field-row" style={{ justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500, color: '#0f172a' }}>{t.filename}</div>
                    <div style={{ fontSize: 11, color: '#94a3b8' }}>{t.meta}</div>
                  </div>
                  <span className="chip-green">Done</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT column */}
        <div>
          <div className="card" style={{ padding: 24, marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 16 }}>Transcription Output</h3>
            <div style={{ background: '#f8fafc', borderRadius: 12, padding: 16, marginBottom: 16, minHeight: 160 }}>
              <p style={{ fontSize: 13, color: '#374151', lineHeight: 1.7 }}>
                &ldquo;Hi, this is Sarah from Globex Corp. I&apos;m calling about invoice number GLX-2024-0441 for $87,400.
                We sent it last week but haven&apos;t received confirmation. The PO reference should be PO-2024-0891.
                Can you please check on the status?&rdquo;
              </p>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <MetaRow k="Confidence" v="96%"          vColor="#16a34a" vWeight={600} />
              <MetaRow k="Duration"   v="0:32"         vColor="#0f172a" vWeight={600} />
              <MetaRow k="Language"   v="English (US)" vColor="#0f172a" vWeight={600} />
            </div>
          </div>

          <div className="card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>Extracted Entities</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {ENTITIES.map((e) => (
                <div key={e.label} className="field-row" style={{ justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 12, color: '#64748b' }}>{e.label}</span>
                  {e.chip ? (
                    <span className="chip-blue">{e.value}</span>
                  ) : (
                    <span style={{ fontSize: 13, fontWeight: e.valueWeight || 500, color: e.valueColor || '#0f172a' }}>
                      {e.value}
                    </span>
                  )}
                </div>
              ))}
            </div>
            <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: 16 }}>
              Route to InvoiceBot
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

function MetaRow({ k, v, vColor, vWeight }: { k: string; v: string; vColor: string; vWeight: number }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
      <span style={{ color: '#64748b' }}>{k}</span>
      <span style={{ fontWeight: vWeight, color: vColor }}>{v}</span>
    </div>
  );
}
