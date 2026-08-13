/**
 * Orchestration — top-level OPERATE surface.
 *
 * The agent-orchestration run (multi-iteration test campaigns, the
 * Reporting/Correlation vs Direct-Lab-Action tier split, and HITL gates).
 * Currently powers the Verizon Far Edge demo; other demo modes get a
 * "not available in this mode" placeholder so the nav item is always safe.
 */
import React, { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useDemoMode } from '@/lib/demoMode';
import { VerizonOrchestration } from '@/components/Dashboard/VerizonOrchestration';
import { VerizonParallelOnboarding } from '@/components/Dashboard/VerizonParallelOnboarding';
import { VerizonPipelineTrigger } from '@/components/Dashboard/VerizonPipelineTrigger';

type VZView = 'parallel' | 'campaign' | 'trigger';

export default function OrchestrationPage() {
  const [demoMode] = useDemoMode();
  const [view, setView] = useState<VZView>('parallel');
  const isVZ = demoMode === 'verizon_far_edge' || demoMode === 'telecommunications';

  if (isVZ) {
    const tab = (key: VZView, label: string) => (
      <button
        onClick={() => setView(key)}
        style={{
          fontSize: 13, fontWeight: 700, padding: '7px 16px', borderRadius: 8, cursor: 'pointer',
          border: `1px solid ${view === key ? '#ee0000' : '#cbd5e1'}`,
          background: view === key ? '#ee0000' : '#fff',
          color: view === key ? '#fff' : '#475569',
        }}
      >{label}</button>
    );
    return (
      <>
        <Head><title>Orchestration · Verizon Far Edge | APEX</title></Head>
        <div style={{ background: '#f0f4f8' }}>
          <div style={{ maxWidth: 1600, margin: '0 auto', padding: '20px 32px 0', display: 'flex', gap: 10, alignItems: 'center' }}>
            {tab('parallel', '⚡ Parallel Onboarding')}
            {tab('trigger', '📥 S3 → Apex → Jira')}
            {tab('campaign', 'Single Campaign')}
          </div>
        </div>
        {view === 'parallel' ? <VerizonParallelOnboarding /> : view === 'trigger' ? <VerizonPipelineTrigger /> : <VerizonOrchestration />}
      </>
    );
  }

  return (
    <>
      <Head><title>Orchestration | APEX</title></Head>
      <div style={{ padding: '40px 32px', maxWidth: 720, margin: '0 auto' }}>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.14em', textTransform: 'uppercase', color: '#6c47ff' }}>
          Operate · Orchestration
        </div>
        <h1 style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 26, fontWeight: 800, color: '#0f172a', margin: '8px 0 10px' }}>
          Agent Orchestration
        </h1>
        <p style={{ fontSize: 14, color: '#475569', lineHeight: 1.6, marginBottom: 18 }}>
          Run multi-step agent campaigns through multiple iterations, with a clean separation
          between <strong>read-only Reporting&nbsp;&amp;&nbsp;Correlation</strong> and{' '}
          <strong>Direct Lab Actions</strong> that execute on live hardware — every direct
          action gated by human approval.
        </p>
        <div style={{
          padding: 20, borderRadius: 12, background: '#f8fafc', border: '1px dashed #cbd5e1',
          fontSize: 13.5, color: '#64748b', lineHeight: 1.6,
        }}>
          A live orchestration run is configured for the{' '}
          <strong style={{ color: '#0f172a' }}>Verizon Far Edge</strong> demo (new-platform
          onboarding — HPE EL140 Gen12). Switch demo mode in{' '}
          <Link href="/settings" style={{ color: '#6c47ff', fontWeight: 600 }}>Settings</Link>{' '}
          to <em>Verizon Far Edge Operations</em>, then return here to run it.
        </div>
      </div>
    </>
  );
}
