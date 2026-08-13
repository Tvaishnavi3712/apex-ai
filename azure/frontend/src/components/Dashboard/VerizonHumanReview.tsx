/**
 * VerizonHumanReview — HITL approval surface for Verizon Far Edge firmware cert.
 *
 * The headline review: the CertificationAgent has triaged the 7 DMTF Redfish
 * conformance failures on HPE E930t iLO6 1.57 as production-irrelevant and
 * wants to auto-certify. James Patchett (MTCE Lab) reviews the AI's verdict
 * and signs off — exactly the "marked test passed" judgment from the real
 * report, now with an approval gate + audit trail.
 *
 * Self-contained (mirrors BolerHumanReview): renders from a hardcoded,
 * Verizon-specific queue so the demo always works offline. Approve/Reject/
 * Override fire toasts and log to the (mock) audit trail.
 *
 * Routing:
 *   /review                       → defaults to the DMTF triage gate
 *   /review?item=GATE-DMTF-E930T  → opens that specific gate
 */
import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/router';
import { useCwfcuToast } from './cwfcuToast';

interface ConformanceFailure {
  result: string; method: string; status: string; uri: string; rule: string;
}

interface ReviewGate {
  id: string;
  severity: 'CERTIFY' | 'BLOCK' | 'WATCH';
  agent: string;
  platform: string;
  firmware: string;
  meakv: string;
  title: string;
  summary: string;
  verdict: string;
  rationale: string;
  failures?: ConformanceFailure[];
  metrics: Array<{ label: string; value: string; tone?: string }>;
  approveLabel: string;
  rejectLabel: string;
  assignee: string;
}

const GATES: ReviewGate[] = [
  {
    id: 'GATE-PLAYBOOK-EL140',
    severity: 'CERTIFY',
    agent: 'PlaybookAgent',
    platform: 'HPE ProLiant Compute EL140 Gen12',
    firmware: 'iLO 7 v1.20.00 · BIOS v1.30',
    meakv: 'PROPOSED-29 · BMC Playbook Gap Analysis',
    title: 'Approve 7 Ansible playbook changes for iLO7 support',
    summary:
      'EL140 Gen12 is a new server type the BMC playbook does not support (MEAKV-1750/1793 BLOCKED). ' +
      'PlaybookAgent cross-referenced PROPOSED-20→32 results against the live playbook (commit 5ff15f7028) ' +
      'and proposes 7 CHANGE REQUIRED · 7 NO-CHANGE · 1 VERIFY across 15 role files. Nothing is applied until you approve.',
    verdict: 'AI VERDICT — 7 changes required · low risk · all evidence-linked.',
    rationale:
      'Each change maps to a PROPOSED test result. WorkloadProfile must be exact string "vRAN" (iLO7 rejects ' +
      'others); subscribe-redfish-events needs RegistryPrefixes (broadens to iLO6 too); a net-new security-hardening ' +
      'role is required (SNMP/HTTP/IPMI/SSDP disable + login banner). No existing e910/920/930t flow is affected.',
    failures: [
      { result: 'CHANGE', method: 'group_vars/HPE',          status: 'P-28', uri: 'Add bios_attribute_value_workload_profile_vRAN: vRAN', rule: 'iLO7 rejects other WorkloadProfile values' },
      { result: 'CHANGE', method: 'check_model',             status: 'P-28', uri: 'Add EL140 match condition',                            rule: 'No EL140 case today' },
      { result: 'CHANGE', method: 'bios-config',             status: 'P-28', uri: 'WorkloadProfile=vRAN; absent attrs break PATCH',       rule: 'Atomic 11-setting vRAN profile' },
      { result: 'CHANGE', method: 'mac-discover',            status: 'P-28', uri: 'Use Chassis/1/NetworkAdapters (E830/E825)',           rule: 'iLO7 NIC name match fails on Systems/1' },
      { result: 'CHANGE', method: 'ilo-hostname',            status: 'P-25', uri: 'Target NetworkProtocol.HostName',                     rule: 'OEM EthernetInterfaces path fails on iLO7' },
      { result: 'CHANGE', method: 'subscribe-redfish-events',status: 'P-27', uri: 'EventTypes → RegistryPrefixes',                       rule: 'Required on iLO6 + iLO7' },
      { result: 'CHANGE', method: 'security-hardening (NEW)', status: 'P-32', uri: 'New role — SNMP/HTTP/IPMI/SSDP disable + banner',     rule: 'Role does not exist yet' },
    ],
    metrics: [
      { label: 'Change required', value: '7', tone: '#d97706' },
      { label: 'No change', value: '7', tone: '#16a34a' },
      { label: 'Role files', value: '15' },
    ],
    approveLabel: '✓ Approve changes · open PR',
    rejectLabel: 'Reject — send back to lab',
    assignee: 'James Patchett · MTCE Lab VCPfe',
  },
  {
    id: 'GATE-DMTF-E930T',
    severity: 'CERTIFY',
    agent: 'CertificationAgent',
    platform: 'HPE Edgeline E930t · Sapphire Rapids',
    firmware: 'iLO 6 v1.57 · BIOS H11 v1.11',
    meakv: 'MEAKV-507 · DMTF Redfish Conformance',
    title: 'Auto-certify 7 DMTF conformance failures as production-irrelevant',
    summary:
      'Redfish-Protocol-Validator v1.2.0 reported PASS: 392 · FAIL: 7 · WARN: 0 · NOT_TESTED: 31. ' +
      'CertificationAgent classified all 7 failures as known-benign for VCPfe production operation and ' +
      'recommends AUTO-CERTIFY with cited rationale.',
    verdict: 'AI VERDICT — CERTIFY (auto). Confidence 96%.',
    rationale:
      'The 7-failure signature (6× WWW-Authenticate header missing on 401 responses + 1× X.509 cert ' +
      'decode on IPv6 hostname) recurs IDENTICALLY across iLO5 3.06, iLO6 1.60, and ZT BMC in the corpus. ' +
      'None affects Redfish operation with VCPfe in production. This matches James Patchett\'s historical ' +
      '"marked test passed" decision on every prior occurrence.',
    failures: [
      { result: 'FAIL', method: 'GET',  status: '401', uri: '/redfish/v1/SessionService/Sessions/',    rule: 'WWW-Authenticate header missing' },
      { result: 'FAIL', method: 'GET',  status: '401', uri: '/redfish/v1/Managers/1/NetworkProtocol/',  rule: 'WWW-Authenticate header missing' },
      { result: 'FAIL', method: 'GET',  status: '401', uri: '/redfish/v1/Systems/',                     rule: 'WWW-Authenticate header missing' },
      { result: 'FAIL', method: 'GET',  status: '401', uri: '/redfish/v1/AccountService/Accounts/',     rule: 'WWW-Authenticate header missing' },
      { result: 'FAIL', method: 'POST', status: '401', uri: '/redfish/v1/AccountService/Accounts/',     rule: 'WWW-Authenticate header missing' },
      { result: 'FAIL', method: 'GET',  status: '401', uri: '/redfish/v1/AccountService/',              rule: 'WWW-Authenticate header missing' },
      { result: 'FAIL', method: '—',    status: '—',   uri: 'X.509 cert decode (IPv6)',                  rule: 'Address family for hostname not supported' },
    ],
    metrics: [
      { label: 'Pass / Fail', value: '392 / 7', tone: '#16a34a' },
      { label: 'Triaged benign', value: '7 / 7', tone: '#16a34a' },
      { label: 'Manual effort saved', value: '~40 hr' },
    ],
    approveLabel: '✓ Certify (sign off)',
    rejectLabel: 'Reject — keep ticket open',
    assignee: 'James Patchett · MTCE Lab VCPfe',
  },
  {
    id: 'GATE-SAMSUNG-SSD',
    severity: 'BLOCK',
    agent: 'SchemaWatchAgent',
    platform: 'ZT Proteus subclouds w/ Samsung PM9A3',
    firmware: 'BMC 0.45 (regression) → 0.46 (fix)',
    meakv: 'MEAKV-1792 · Samsung SSD Temperature',
    title: 'Block BMC .45 wave deployment to Samsung PM9A3 sites',
    summary:
      'BMC .45 cannot read the SAMSUNG PM9A3 (MZQL21T9HCJR-00A07) temperature → fan controller failsafe → ' +
      '100% fan utilization. Lab-reproduced by downgrading .46 → .45. BMC .46 restores the read.',
    verdict: 'AI VERDICT — BLOCK .45 wave to PM9A3 sites. Confidence 97%.',
    rationale:
      'Deploy-blocking thermal regression confirmed in lab. Blast radius: every subcloud with PM9A3 drives ' +
      'on BMC .45. UpgradeAdvisor recommends mandating BMC .46 as the minimum for the Samsung PM9A3 fleet.',
    metrics: [
      { label: 'Regression', value: 'BMC .45', tone: '#dc2626' },
      { label: 'Validated fix', value: 'BMC .46', tone: '#16a34a' },
      { label: 'Fan spike', value: '100%', tone: '#dc2626' },
    ],
    approveLabel: '✓ Approve wave block',
    rejectLabel: 'Override — allow .45 (not recommended)',
    assignee: 'James Patchett · MTCE Lab VCPfe',
  },
  {
    id: 'GATE-BMC43-503',
    severity: 'WATCH',
    agent: 'SchemaWatchAgent',
    platform: 'ZT Proteus · early-rev',
    firmware: 'BMC 0.43',
    meakv: 'Redfish troubleshooting',
    title: 'Classify Redfish 503-during-boot as transient (BMC .43)',
    summary:
      'Redfish PATCH /Systems/Self/Bios/SD returns 503 Ami.1.0.ServiceTemporarilyUnavailableDueToHostBooting ' +
      'during host reboot / inventory processing. Remediation: AMIManager.RedfishDBReset (ResetAll), then retry.',
    verdict: 'AI VERDICT — Transient, not a defect. Add retry to BMC playbook.',
    rationale:
      'Occurs only during the host-boot / Redfish-inventory window. RedfishDBReset clears the stuck DB and the ' +
      'PATCH succeeds. Captured into the MentorAgent BMC-playbook KB for operator self-service.',
    metrics: [
      { label: 'Classification', value: 'Transient' },
      { label: 'Remediation', value: 'RedfishDBReset' },
      { label: 'KB updated', value: 'Yes', tone: '#16a34a' },
    ],
    approveLabel: '✓ Accept classification',
    rejectLabel: 'Escalate — treat as defect',
    assignee: 'James Patchett · MTCE Lab VCPfe',
  },
];

const sevFill = (s: string) =>
  s === 'BLOCK'   ? { bg: '#fef2f2', color: '#dc2626' }
: s === 'WATCH'   ? { bg: '#fffbeb', color: '#d97706' }
: { bg: '#f0fdf4', color: '#16a34a' };

export function VerizonHumanReview() {
  const router = useRouter();
  const { Toast, push } = useCwfcuToast();
  const itemParam = (router.query.item as string | undefined) || undefined;

  const [selectedId, setSelectedId] = useState<string>(itemParam || 'GATE-PLAYBOOK-EL140');
  const [decided, setDecided] = useState<Record<string, string>>({});
  const selected = GATES.find((g) => g.id === selectedId) || GATES[0];

  const auditTrail = useMemo(() => ([
    { time: '15:19:37', date: 'real report', action: 'Redfish-Protocol-Validator v1.2.0 ran', detail: 'E930t iLO6 1.57 · 430 assertions' , tone: 'blue' },
    { time: '15:19:41', date: 'auto', action: 'CertificationAgent classified 7 FAILs', detail: 'WWW-Authenticate(6) + X.509-IPv6(1) → benign', tone: 'green' },
    { time: '15:19:42', date: 'auto', action: 'Production-irrelevance rule applied', detail: 'matches James\'s historical verdict', tone: 'green' },
    { time: 'now',      date: 'HITL',  action: 'Routed to James Patchett for sign-off', detail: 'cert gate GATE-DMTF-E930T', tone: 'amber' },
  ]), []);

  const decide = (kind: 'approve' | 'reject', gate: ReviewGate) => {
    setDecided((prev) => ({ ...prev, [gate.id]: kind }));
    if (kind === 'approve') {
      push({
        tone: 'success',
        title: `${gate.id} — ${gate.severity === 'CERTIFY' ? 'Certified' : gate.severity === 'BLOCK' ? 'Wave block approved' : 'Classification accepted'}`,
        detail: 'Decision hash-chained to Cosmos DB audit log · JIRA evidence attached · SES notification sent',
      });
    } else {
      push({
        tone: 'warn',
        title: `${gate.id} — ${gate.severity === 'CERTIFY' ? 'Rejected · ticket stays open' : 'Overridden'}`,
        detail: 'Routed back to cert queue · engineer note required · audit logged',
      });
    }
  };

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', color: '#0d1120', padding: 24 }}>
      <Toast />

      <div style={{ marginBottom: 20 }}>
        <div style={{ fontFamily: 'Space Grotesk, sans-serif', fontSize: 24, fontWeight: 800 }}>
          Human Review — Firmware Certification HITL
        </div>
        <div style={{ fontSize: 13, color: '#7a8fa6', marginTop: 4 }}>
          {GATES.length} cert gates · Verizon Far Edge · reviewer: James Patchett (MTCE Lab VCPfe) ·
          {' '}real corpus: 118 firmware reports
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr 320px', gap: 20 }}>

        {/* LEFT — gate queue */}
        <div style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 18, height: 'fit-content' }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: '#cd040b', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 12 }}>
            Cert Gates · {GATES.length}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {GATES.map((g) => {
              const sev = sevFill(g.severity);
              const isSel = g.id === selectedId;
              const dec = decided[g.id];
              return (
                <button
                  key={g.id}
                  onClick={() => {
                    setSelectedId(g.id);
                    router.replace({ pathname: '/review', query: { item: g.id } }, undefined, { shallow: true });
                  }}
                  style={{
                    textAlign: 'left', cursor: 'pointer', padding: '10px 12px', borderRadius: 8,
                    border: '1px solid', borderColor: isSel ? '#cd040b' : '#e8ecf0',
                    background: isSel ? '#fff5f5' : '#fff',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{ fontSize: 9, fontWeight: 700, padding: '2px 6px', borderRadius: 3, background: sev.bg, color: sev.color }}>
                      {g.severity}
                    </span>
                    <span style={{ fontSize: 11, color: '#7a8fa6' }}>{g.id}</span>
                    {dec && (
                      <span style={{ marginLeft: 'auto', fontSize: 9, fontWeight: 700, color: dec === 'approve' ? '#16a34a' : '#d97706' }}>
                        {dec === 'approve' ? '✓ DONE' : 'RETURNED'}
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: 12.5, fontWeight: 600, lineHeight: 1.35 }}>{g.title}</div>
                  <div style={{ fontSize: 11, color: '#7a8fa6', marginTop: 4 }}>{g.platform}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* CENTER — approval window */}
        <div style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 24 }}>
          <ApprovalWindow gate={selected} decided={decided[selected.id]} onDecide={decide} />
        </div>

        {/* RIGHT — fleet context + audit */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 18 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#cd040b', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 12 }}>
              Fleet Context
            </div>
            {[
              ['Vendors', 'HPE Edgeline · ZT · Dell'],
              ['Platforms', 'E910t/E920t/E930t · Proteus/Triton/Galene · R7615'],
              ['Controllers', 'iLO5/iLO6 · ZT BMC · iDRAC'],
              ['Stack', 'Wind River Cloud Platform (WRCP)'],
              ['Reports in corpus', '118 (real · MTCE Lab)'],
            ].map(([k, v]) => (
              <div key={k} style={{ padding: '7px 0', borderBottom: '1px solid #f5f7fa' }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '.06em' }}>{k}</div>
                <div style={{ fontSize: 12, color: '#0d1120', marginTop: 2 }}>{v}</div>
              </div>
            ))}
          </div>

          <div style={{ background: '#fff', border: '1px solid #e8ecf0', borderRadius: 12, padding: 18 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#cd040b', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 12 }}>
              Audit Trail
            </div>
            {auditTrail.map((a, i) => (
              <div key={i} style={{ padding: '8px 0', borderBottom: i < auditTrail.length - 1 ? '1px solid #f5f7fa' : 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                  <span style={{ fontSize: 10.5, fontWeight: 700, color: a.tone === 'green' ? '#16a34a' : a.tone === 'amber' ? '#d97706' : '#2563eb' }}>
                    {a.date}
                  </span>
                  <span style={{ fontSize: 10, color: '#9ca3af' }}>{a.time}</span>
                </div>
                <div style={{ fontSize: 11.5, fontWeight: 600, lineHeight: 1.3 }}>{a.action}</div>
                <div style={{ fontSize: 10.5, color: '#7a8fa6', marginTop: 2, lineHeight: 1.4 }}>{a.detail}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function ApprovalWindow({ gate, decided, onDecide }: {
  gate: ReviewGate; decided?: string;
  onDecide: (kind: 'approve' | 'reject', gate: ReviewGate) => void;
}) {
  const sev = sevFill(gate.severity);
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6 }}>
        <span style={{ fontSize: 11, fontWeight: 700, padding: '4px 10px', borderRadius: 4, background: sev.bg, color: sev.color }}>
          {gate.severity}
        </span>
        <span style={{ fontSize: 13, fontWeight: 700 }}>{gate.id}</span>
        <span style={{ fontSize: 11.5, color: '#7a8fa6', marginLeft: 'auto' }}>
          Reviewer: <strong style={{ color: '#0d1120' }}>{gate.assignee}</strong>
        </span>
      </div>

      <h2 style={{ fontSize: 18, fontWeight: 700, margin: '4px 0 4px' }}>{gate.title}</h2>
      <div style={{ fontSize: 12, color: '#475569', marginBottom: 4 }}>
        {gate.platform} · {gate.firmware} · {gate.meakv} · {gate.agent}
      </div>

      <div style={{ background: '#f8f9fc', border: '1px solid #e8ecf0', borderRadius: 8, padding: 14, margin: '12px 0', fontSize: 12.5, lineHeight: 1.55 }}>
        {gate.summary}
      </div>

      {/* AI verdict */}
      <div style={{ background: '#0d1f35', borderRadius: 8, padding: 14, marginBottom: 14 }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: '#5eead4', marginBottom: 6 }}>{gate.verdict}</div>
        <div style={{ fontSize: 11.5, color: '#cbd5e1', lineHeight: 1.6 }}>{gate.rationale}</div>
      </div>

      {/* Detail table — conformance failures OR playbook changes */}
      {gate.failures && (() => {
        const isChanges = gate.failures.some((f) => f.result === 'CHANGE');
        const hdr = isChanges
          ? ['', 'Role / File', 'Ref', 'Change', 'Reason']
          : ['', 'Method', 'Code', 'URI', 'Rule'];
        const title = isChanges ? 'The 7 playbook changes (evidence-linked)' : 'The 7 failures (all known-benign)';
        return (
        <div style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 10.5, fontWeight: 700, color: '#cd040b', letterSpacing: '.08em', textTransform: 'uppercase', marginBottom: 6 }}>
            {title}
          </div>
          <div style={{ border: '1px solid #e8ecf0', borderRadius: 8, overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
              <thead>
                <tr style={{ background: '#f8f9fc' }}>
                  {hdr.map((h) => (
                    <th key={h} style={{ textAlign: 'left', padding: '6px 8px', color: '#6b7280', fontWeight: 700 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {gate.failures.map((f, i) => (
                  <tr key={i} style={{ borderTop: '1px solid #f0f2f5' }}>
                    <td style={{ padding: '5px 8px', color: f.result === 'CHANGE' ? '#d97706' : '#dc2626', fontWeight: 700 }}>{f.result}</td>
                    <td style={{ padding: '5px 8px', fontFamily: 'monospace' }}>{f.method}</td>
                    <td style={{ padding: '5px 8px', fontFamily: 'monospace' }}>{f.status}</td>
                    <td style={{ padding: '5px 8px', fontFamily: 'monospace', color: '#475569' }}>{f.uri}</td>
                    <td style={{ padding: '5px 8px', color: '#6b7280' }}>{f.rule}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        );
      })()}

      {/* Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 18 }}>
        {gate.metrics.map((m) => (
          <div key={m.label} style={{ background: '#f8f9fc', border: '1px solid #e8ecf0', borderRadius: 6, padding: '8px 12px' }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: '#9ca3af', textTransform: 'uppercase', letterSpacing: '.06em' }}>{m.label}</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: m.tone || '#0d1120', marginTop: 3 }}>{m.value}</div>
          </div>
        ))}
      </div>

      {/* Action buttons */}
      <div style={{ paddingTop: 16, borderTop: '1px solid #e8ecf0', display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        <button
          onClick={() => onDecide('approve', gate)}
          disabled={decided === 'approve'}
          style={{
            fontSize: 12.5, fontWeight: 600, padding: '9px 18px', borderRadius: 8,
            cursor: decided === 'approve' ? 'default' : 'pointer', border: 'none',
            background: decided === 'approve' ? '#9ca3af' : '#cd040b', color: '#fff',
          }}
        >
          {decided === 'approve' ? '✓ Signed off' : gate.approveLabel}
        </button>
        <button
          onClick={() => onDecide('reject', gate)}
          style={{
            fontSize: 12.5, fontWeight: 600, padding: '9px 16px', borderRadius: 8, cursor: 'pointer',
            border: '1px solid #fed7aa', background: '#fff7ed', color: '#ea580c',
          }}
        >
          {gate.rejectLabel}
        </button>
        {decided && (
          <span style={{ fontSize: 11.5, color: decided === 'approve' ? '#16a34a' : '#d97706', fontWeight: 600 }}>
            {decided === 'approve' ? 'Decision recorded · audit-logged' : 'Returned to cert queue'}
          </span>
        )}
      </div>

      <div style={{ marginTop: 12, fontSize: 10.5, color: '#9ca3af', fontStyle: 'italic' }}>
        Decision hash-chained to Cosmos DB audit log · IAM role: FirmwareCertApprover · JIRA evidence auto-attached
      </div>
    </div>
  );
}
