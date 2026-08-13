/**
 * Apex Prototypes Hub
 * Entry point for the new design language demos.
 */
import Link from 'next/link';
import {
  CommandLineIcon,
  Squares2X2Icon,
  ChartBarSquareIcon,
  SparklesIcon,
  ArrowRightIcon,
  WrenchScrewdriverIcon,
  BoltIcon,
  EyeIcon,
  ShieldCheckIcon,
} from '@heroicons/react/24/outline';

const prototypes = [
  {
    href: '/prototypes/command-bar',
    name: 'Command Bar',
    tag: '⌘K Spotlight',
    desc: 'A floating, keyboard-first entry point for Ask · Run · Build · Find. Sets the "AI-native" tone.',
    icon: CommandLineIcon,
    metric: 'Signature moment',
  },
  {
    href: '/prototypes/flow-canvas',
    name: 'Flow Canvas',
    tag: 'Playbook Builder',
    desc: 'Replaces list-based playbooks with a draggable node graph. Trigger → Extract → Decide → Act.',
    icon: Squares2X2Icon,
    metric: 'Biggest visual payoff',
  },
  {
    href: '/prototypes/mission-control',
    name: 'Mission Control',
    tag: 'Command Center',
    desc: 'Two-tone dashboard: live throughput sparkline, accuracy gauge, cost meter, activity heatmap.',
    icon: ChartBarSquareIcon,
    metric: 'Operator dashboard',
  },
];

const ZONES = [
  { key: 'build',   label: 'Build',   desc: 'Canvas · blueprints · playbooks · actions', icon: WrenchScrewdriverIcon, items: ['Canvas', 'Blueprint Designer', 'Action Library'] },
  { key: 'run',     label: 'Run',     desc: 'Agent Hub · chat · work queue · review',    icon: BoltIcon,              items: ['Chat', 'Work Queue', 'Human Review'] },
  { key: 'observe', label: 'Observe', desc: 'Command Center · metrics · logs · audit',   icon: EyeIcon,               items: ['Mission Control', 'Logs', 'Audit Trail'] },
  { key: 'govern',  label: 'Govern',  desc: 'Connectors · team · security · settings',   icon: ShieldCheckIcon,       items: ['Connectors', 'Team', 'Security'] },
];

export default function PrototypesHub() {
  return (
    <div className="apex-proto apex-proto-backdrop page-enter">
      <div className="mx-auto max-w-6xl px-8 py-16">
        {/* Header */}
        <div className="flex items-center gap-4 mb-3">
          <div className="apex-mark apex-mark-spin" />
          <span className="t-micro">Apex · Design System v2</span>
        </div>
        <h1 className="t-display mb-3">A new visual language for Apex.</h1>
        <p className="t-body t-dim max-w-2xl mb-12">
          Four drop-in prototypes that demonstrate tokens, dark-first surfaces, agent presence,
          and a signature AI-native interaction pattern. Nothing in the existing app changes until
          you decide to promote a prototype.
        </p>

        {/* Token preview */}
        <div className="surface p-6 mb-12 rail">
          <div className="flex items-center justify-between mb-5">
            <div>
              <div className="t-micro mb-1">Foundation</div>
              <div className="t-title">Design tokens are live</div>
            </div>
            <span className="chip chip-on">
              <span className="dot dot-ok" />
              globals.css
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <TokenChip label="Surface 0" value="#0a0e17" swatch="bg-[#0a0e17] border border-white/10" />
            <TokenChip label="Surface 1" value="#111725" swatch="bg-[#111725] border border-white/10" />
            <TokenChip label="Accent" value="#5b8cff" swatch="bg-[#5b8cff]" />
            <TokenChip label="Accent 2" value="#8b5cf6" swatch="bg-[#8b5cf6]" />
            <TokenChip label="OK" value="#3ecf8e" swatch="bg-[#3ecf8e]" />
            <TokenChip label="Warn" value="#f0b429" swatch="bg-[#f0b429]" />
            <TokenChip label="Err" value="#ff6b6b" swatch="bg-[#ff6b6b]" />
            <TokenChip label="Ink muted" value="#8a93a6" swatch="bg-[#8a93a6]" />
          </div>
        </div>

        {/* Prototype grid */}
        <div className="grid md:grid-cols-3 gap-5">
          {prototypes.map((p) => (
            <Link
              key={p.href}
              href={p.href}
              className="surface p-6 rail persona-card hover:border-[color:var(--accent-ring)] transition-colors group"
            >
              <div className="flex items-start justify-between mb-5">
                <div className="h-10 w-10 rounded-xl flex items-center justify-center surface-2">
                  <p.icon className="h-5 w-5 text-[color:var(--accent-ink)]" />
                </div>
                <span className="group-badge" style={{ color: 'var(--accent-ink)', borderColor: 'var(--accent-ring)', background: 'rgba(91,140,255,0.08)' }}>
                  {p.metric}
                </span>
              </div>
              <div className="t-micro mb-1">{p.tag}</div>
              <div className="t-title mb-2">{p.name}</div>
              <p className="t-body t-dim mb-6">{p.desc}</p>
              <div className="flex items-center gap-2 text-[color:var(--accent-ink)] text-sm font-medium">
                Open prototype
                <ArrowRightIcon className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>

        {/* 4-zone IA preview */}
        <div className="mt-16">
          <div className="flex items-end justify-between mb-5">
            <div>
              <div className="t-micro mb-1">Promotion preview</div>
              <div className="t-title">Four-zone information architecture</div>
              <p className="t-body t-dim mt-1">Collapses 12 scattered nav items into a clear mental model.</p>
            </div>
            <span className="chip">Not yet live in app</span>
          </div>
          <div className="grid md:grid-cols-4 gap-4">
            {ZONES.map((z, idx) => (
              <div key={z.key} className="surface p-5 persona-card relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="h-9 w-9 rounded-lg surface-2 flex items-center justify-center">
                    <z.icon className="h-4 w-4 text-[color:var(--accent-ink)]" />
                  </div>
                  <span className="t-num text-[10px] t-dim">0{idx + 1}</span>
                </div>
                <div className="t-title text-base mb-1">{z.label}</div>
                <p className="t-body t-dim mb-4">{z.desc}</p>
                <ul className="space-y-1.5">
                  {z.items.map((it) => (
                    <li key={it} className="flex items-center gap-2 text-xs t-dim">
                      <span className="dot dot-idle" />
                      {it}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Footer hints */}
        <div className="mt-16 grid md:grid-cols-2 gap-4">
          <div className="surface-2 p-5 flex items-center gap-3">
            <SparklesIcon className="h-5 w-5 text-[color:var(--accent-ink)] flex-shrink-0" />
            <div className="t-body t-dim">
              These prototypes live alongside the existing app. Only
              <span className="t-num text-[color:var(--ink)]"> globals.css </span>
              was touched — additive, scoped to <span className="t-num text-[color:var(--ink)]">.apex-proto</span>.
            </div>
          </div>
          <div className="surface-2 p-5 flex items-center gap-3">
            <CommandLineIcon className="h-5 w-5 text-[color:var(--accent-ink)] flex-shrink-0" />
            <div className="t-body t-dim">
              Try the Command Bar anywhere:
              <span className="kbd ml-2">⌘</span>
              <span className="kbd">K</span>
              <span className="ml-2">— works on <Link href="/prototypes/command-bar" className="underline hover:text-[color:var(--accent-ink)]">/command-bar</Link>.</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function TokenChip({ label, value, swatch }: { label: string; value: string; swatch: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`h-8 w-8 rounded-lg ${swatch}`} />
      <div>
        <div className="t-micro">{label}</div>
        <div className="t-num text-xs t-dim">{value}</div>
      </div>
    </div>
  );
}
