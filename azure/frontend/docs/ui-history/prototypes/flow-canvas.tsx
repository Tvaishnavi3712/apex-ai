/**
 * Flow Canvas Prototype
 * Node-based playbook designer. Static SVG — no react-flow dependency.
 */
import { useState } from 'react';
import {
  CloudArrowUpIcon,
  DocumentMagnifyingGlassIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  ArrowsRightLeftIcon,
  CheckBadgeIcon,
  HandRaisedIcon,
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon,
  ArrowsPointingOutIcon,
  BoltIcon,
  PlayIcon,
  ChevronDoubleRightIcon,
  ChevronDoubleLeftIcon,
} from '@heroicons/react/24/outline';

type NodeDef = {
  id: string;
  kind: 'trigger' | 'extract' | 'enrich' | 'validate' | 'decide' | 'act' | 'human';
  title: string;
  sub: string;
  x: number;
  y: number;
  icon: typeof CloudArrowUpIcon;
  status: 'idle' | 'running' | 'ok' | 'warn';
  conf?: number; // 0..1
};

const NODES: NodeDef[] = [
  { id: 'n1', kind: 'trigger',  title: 'S3 Upload',         sub: 'apex-documents-incoming', x: 60,  y: 220, icon: CloudArrowUpIcon,          status: 'ok',      conf: 1.0  },
  { id: 'n2', kind: 'extract',  title: 'Extract Invoice',   sub: 'BDA Blueprint · invoice', x: 320, y: 220, icon: DocumentMagnifyingGlassIcon, status: 'running', conf: 0.97 },
  { id: 'n3', kind: 'enrich',   title: 'Vendor Lookup',     sub: 'Cosmos DB · vendors',      x: 590, y: 120, icon: UserCircleIcon,            status: 'ok',      conf: 0.99 },
  { id: 'n4', kind: 'validate', title: 'Validate Rules',    sub: 'Business rules · 14',     x: 590, y: 320, icon: ShieldCheckIcon,           status: 'warn',    conf: 0.82 },
  { id: 'n5', kind: 'decide',   title: 'Route Decision',    sub: 'Confidence · threshold',  x: 860, y: 220, icon: ArrowsRightLeftIcon,       status: 'idle',    conf: 0.94 },
  { id: 'n6', kind: 'act',      title: 'Auto-Approve',      sub: 'Post to ERP',             x: 1120, y: 120, icon: CheckBadgeIcon,           status: 'idle' },
  { id: 'n7', kind: 'human',    title: 'Human Review',      sub: 'Queue · AP team',         x: 1120, y: 320, icon: HandRaisedIcon,           status: 'idle' },
];

const EDGES: [string, string, boolean?][] = [
  ['n1', 'n2', true],
  ['n2', 'n3', true],
  ['n2', 'n4'],
  ['n3', 'n5'],
  ['n4', 'n5'],
  ['n5', 'n6'],
  ['n5', 'n7'],
];

const KIND_LABEL: Record<NodeDef['kind'], string> = {
  trigger: 'Trigger', extract: 'Extract', enrich: 'Enrich',
  validate: 'Validate', decide: 'Decide', act: 'Act', human: 'Human',
};

export default function FlowCanvasPrototype() {
  const [selected, setSelected] = useState<string>('n2');
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const sel = NODES.find((n) => n.id === selected)!;

  return (
    <div className="apex-proto apex-proto-backdrop min-h-screen flex flex-col page-enter">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-8 py-4 border-b border-[color:var(--surface-border)]">
        <div className="flex items-center gap-3">
          <div className="apex-mark apex-mark-sm apex-mark-spin" />
          <div>
            <div className="t-micro">Canvas · Playbook</div>
            <div className="t-title">invoice_processing</div>
          </div>
          <span className="chip chip-on ml-3"><span className="dot dot-think" /> Deployed</span>
          <span className="chip">Financial Services</span>
          <span className="chip t-num">v1.0.0</span>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn"><PlayIcon className="h-4 w-4" /> Test run</button>
          <button className="btn btn-primary"><BoltIcon className="h-4 w-4" /> Deploy</button>
        </div>
      </div>

      {/* Body: canvas + inspector */}
      <div className="flex-1 flex min-h-0">
        {/* Canvas */}
        <div className="flex-1 relative">
          <div className="absolute inset-0 overflow-auto dark-scrollbar">
          <svg width="1380" height="560" className="block mx-auto mt-8">
            {/* Grid */}
            <defs>
              <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="1" fill="rgba(255,255,255,0.05)" />
              </pattern>
              <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.2)" />
              </marker>
              <marker id="arrow-active" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#5b8cff" />
              </marker>
            </defs>
            <rect width="1380" height="560" fill="url(#grid)" />

            {/* Edges */}
            {EDGES.map(([from, to, active], i) => {
              const a = NODES.find((n) => n.id === from)!;
              const b = NODES.find((n) => n.id === to)!;
              const x1 = a.x + 240; // right side of node
              const y1 = a.y + 36;
              const x2 = b.x;
              const y2 = b.y + 36;
              const mx = (x1 + x2) / 2;
              const d = `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
              return (
                <path
                  key={i}
                  d={d}
                  className={active ? 'edge edge-active' : 'edge'}
                  markerEnd={active ? 'url(#arrow-active)' : 'url(#arrow)'}
                />
              );
            })}
          </svg>

          {/* Nodes overlaid */}
          <div className="absolute top-0 left-0 mt-8 pointer-events-none" style={{ width: 1380, height: 560, marginLeft: 'max(0px, calc((100% - 1380px) / 2))' }}>
            <div className="relative" style={{ width: 1380, height: 560 }}>
              {NODES.map((n) => (
                <button
                  key={n.id}
                  onClick={() => setSelected(n.id)}
                  className={`node rail absolute text-left pointer-events-auto ${selected === n.id ? 'node-active' : ''}`}
                  style={{ left: n.x, top: n.y, width: 240 }}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="t-micro">{KIND_LABEL[n.kind]}</span>
                    <div className="flex items-center gap-1.5">
                      {n.conf !== undefined && (
                        <span className="t-num text-[10px] t-dim">{(n.conf * 100).toFixed(0)}%</span>
                      )}
                      <StatusDot status={n.status} />
                    </div>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded-lg surface-2 flex items-center justify-center">
                      <n.icon className="h-4 w-4 text-[color:var(--accent-ink)]" />
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-medium truncate" style={{ color: 'var(--ink)' }}>{n.title}</div>
                      <div className="text-xs t-dim truncate">{n.sub}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          </div>

          {/* Canvas controls (bottom-left, pinned) */}
          <div className="absolute bottom-5 left-5 inline-flex items-center gap-1 surface-hi px-2 py-1.5 rounded-full z-10">
            <button className="h-7 w-7 rounded-full hover:bg-white/5 flex items-center justify-center"><MagnifyingGlassPlusIcon className="h-4 w-4 t-dim" /></button>
            <button className="h-7 w-7 rounded-full hover:bg-white/5 flex items-center justify-center"><MagnifyingGlassMinusIcon className="h-4 w-4 t-dim" /></button>
            <span className="t-num text-xs t-dim px-2">100%</span>
            <button className="h-7 w-7 rounded-full hover:bg-white/5 flex items-center justify-center"><ArrowsPointingOutIcon className="h-4 w-4 t-dim" /></button>
            <span className="w-px h-4 bg-white/10 mx-1" />
            <span className="flex items-center gap-3 px-2 text-[11px] t-dim">
              <span className="flex items-center gap-1.5"><span className="dot dot-ok" /> Ready</span>
              <span className="flex items-center gap-1.5"><span className="dot dot-think" /> Running</span>
              <span className="flex items-center gap-1.5"><span className="dot dot-warn" /> Needs review</span>
              <span className="flex items-center gap-1.5"><span className="dot dot-idle" /> Idle</span>
            </span>
          </div>

          {/* Minimap (bottom-right) */}
          <div className="absolute bottom-5 right-5 surface-hi p-2 rounded-xl" style={{ width: 180, height: 100 }}>
            <svg width="160" height="84" viewBox="0 0 1280 560" preserveAspectRatio="xMidYMid meet">
              {EDGES.map(([from, to], i) => {
                const a = NODES.find((n) => n.id === from)!;
                const b = NODES.find((n) => n.id === to)!;
                return <line key={i} x1={a.x + 120} y1={a.y + 36} x2={b.x + 120} y2={b.y + 36} stroke="rgba(255,255,255,0.15)" strokeWidth="6" />;
              })}
              {NODES.map((n) => (
                <rect key={n.id} x={n.x} y={n.y} width="240" height="72" rx="12"
                  fill={n.id === selected ? '#5b8cff' : 'rgba(255,255,255,0.18)'} />
              ))}
            </svg>
          </div>
        </div>

        {/* Inspector toggle (when collapsed) */}
        {!inspectorOpen && (
          <button
            onClick={() => setInspectorOpen(true)}
            className="self-center mr-2 h-10 w-6 rounded-l-lg surface-2 flex items-center justify-center hover:border-[color:var(--accent-ring)] transition-colors"
            title="Open inspector"
          >
            <ChevronDoubleLeftIcon className="h-3.5 w-3.5 t-dim" />
          </button>
        )}

        {/* Inspector */}
        <aside
          className="border-l border-[color:var(--surface-border)] flex flex-col overflow-y-auto dark-scrollbar transition-[width] duration-200 ease-out"
          style={{ width: inspectorOpen ? 360 : 0, overflow: inspectorOpen ? 'auto' : 'hidden' }}
        >
          <div className="p-5 border-b border-[color:var(--surface-border)] flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="t-micro mb-1">{KIND_LABEL[sel.kind]} node</div>
              <div className="t-title mb-1 truncate">{sel.title}</div>
              <div className="t-body t-dim truncate">{sel.sub}</div>
            </div>
            <button
              onClick={() => setInspectorOpen(false)}
              className="h-7 w-7 rounded-lg hover:bg-white/5 flex items-center justify-center flex-shrink-0"
              title="Collapse inspector"
            >
              <ChevronDoubleRightIcon className="h-4 w-4 t-dim" />
            </button>
          </div>
          <div className="p-5 space-y-5">
            <Field label="Action ID" value={`financial_services.${sel.kind === 'extract' ? 'invoice_extract' : sel.id}`} />
            <Field label="Runtime" value="Foundry Agent Service · Strands" />
            <Field label="Model" value="us.anthropic.claude-opus-4-6-v1" />
            <Field label="Required" value="true" />
            <div>
              <div className="t-micro mb-2">Last 24h</div>
              <div className="surface-2 p-4">
                <div className="flex items-baseline justify-between mb-3">
                  <div className="t-num text-2xl" style={{ color: 'var(--ink)' }}>1,284</div>
                  <span className="chip chip-on t-num">+12.4%</span>
                </div>
                <Sparkline values={[18, 24, 22, 30, 28, 35, 32, 42, 38, 44, 48, 52]} />
              </div>
            </div>
            <div>
              <div className="t-micro mb-2">Tools available</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="chip">bda_extract</span>
                <span className="chip">s3_read</span>
                <span className="chip">dynamo_put</span>
                <span className="chip">notify</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function StatusDot({ status }: { status: NodeDef['status'] }) {
  const cls =
    status === 'running' ? 'dot-think'
    : status === 'ok'    ? 'dot-ok'
    : status === 'warn'  ? 'dot-warn'
    : 'dot-idle';
  return <span className={`dot ${cls}`} />;
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="t-micro mb-1">{label}</div>
      <div className="t-num text-sm" style={{ color: 'var(--ink)' }}>{value}</div>
    </div>
  );
}

function Sparkline({ values }: { values: number[] }) {
  const w = 280, h = 60, pad = 4;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const pts = values.map((v, i) => {
    const x = pad + (i * (w - pad * 2)) / (values.length - 1);
    const y = h - pad - ((v - min) / (max - min || 1)) * (h - pad * 2);
    return `${x},${y}`;
  });
  const d = `M ${pts.join(' L ')}`;
  const area = `${d} L ${w - pad},${h - pad} L ${pad},${h - pad} Z`;
  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`}>
      <defs>
        <linearGradient id="spk" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#5b8cff" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#5b8cff" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#spk)" />
      <path d={d} fill="none" stroke="#5b8cff" strokeWidth="1.5" />
    </svg>
  );
}
