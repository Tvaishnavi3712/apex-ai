/**
 * Command Bar (⌘K Spotlight) Prototype
 * Signature AI-native entry point.
 */
import { useEffect, useRef, useState } from 'react';
import {
  MagnifyingGlassIcon,
  SparklesIcon,
  BoltIcon,
  Squares2X2Icon,
  FolderIcon,
  DocumentTextIcon,
  PlayCircleIcon,
  ArrowRightIcon,
  CommandLineIcon,
} from '@heroicons/react/24/outline';

type TabKey = 'ask' | 'run' | 'build' | 'find';

const TABS: { key: TabKey; label: string; icon: typeof SparklesIcon }[] = [
  { key: 'ask', label: 'Ask', icon: SparklesIcon },
  { key: 'run', label: 'Run', icon: BoltIcon },
  { key: 'build', label: 'Build', icon: Squares2X2Icon },
  { key: 'find', label: 'Find', icon: FolderIcon },
];

type Result = { icon: typeof SparklesIcon; title: string; sub: string; kbd?: string; group: 'recent' | 'suggested' };

const RESULTS: Record<TabKey, Result[]> = {
  ask: [
    { group: 'recent',    icon: SparklesIcon, title: 'How is the InvoiceBot performing today?', sub: 'Asked 12m ago', kbd: '↵' },
    { group: 'suggested', icon: SparklesIcon, title: 'Summarise all flagged claims in the last 24h', sub: 'Suggested · ClaimsBot' },
    { group: 'suggested', icon: SparklesIcon, title: 'Why did the contract extraction fail on lot 8821?', sub: 'Suggested · ContractBot' },
  ],
  run: [
    { group: 'recent',    icon: PlayCircleIcon, title: 'Run playbook · invoice_processing', sub: 'Ran 2h ago · 4 steps', kbd: '↵' },
    { group: 'suggested', icon: PlayCircleIcon, title: 'Run playbook · prior_auth_triage', sub: 'Healthcare Payers · 6 steps' },
    { group: 'suggested', icon: BoltIcon, title: 'Reprocess work item WI-3192', sub: 'Last error: schema mismatch' },
  ],
  build: [
    { group: 'recent',    icon: Squares2X2Icon, title: 'New blueprint from PDF…', sub: 'Used yesterday', kbd: '↵' },
    { group: 'suggested', icon: Squares2X2Icon, title: 'New playbook from template', sub: 'Canvas · 24 templates' },
    { group: 'suggested', icon: DocumentTextIcon, title: 'New action handler', sub: 'Python · Lambda · @apex_action' },
  ],
  find: [
    { group: 'recent',    icon: FolderIcon, title: 'invoice_processing.yaml', sub: 'Opened 3m ago', kbd: '↵' },
    { group: 'suggested', icon: FolderIcon, title: 'invoice.json', sub: 'blueprints/financial_services/' },
    { group: 'suggested', icon: DocumentTextIcon, title: 'WI-3192 · Acme Invoice #44-123', sub: 'Work Queue · flagged' },
  ],
};

const MODE_COPY: Record<TabKey, { title: string; desc: string; example: string }> = {
  ask:   { title: 'Ask',   desc: 'Natural-language questions about your data, agents, and runs.', example: '“How is InvoiceBot doing today?”' },
  run:   { title: 'Run',   desc: 'Trigger playbooks, reprocess work items, or kick off an action.', example: 'Run invoice_processing' },
  build: { title: 'Build', desc: 'Jump into Canvas to create a blueprint, playbook, or action.',   example: 'New blueprint from PDF' },
  find:  { title: 'Find',  desc: 'Jump to any file, work item, agent, or log line in seconds.',    example: 'invoice_processing.yaml' },
};

export default function CommandBarPrototype() {
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<TabKey>('ask');
  const [q, setQ] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 60);
  }, [open]);

  const results = RESULTS[tab].filter((r) =>
    q ? r.title.toLowerCase().includes(q.toLowerCase()) : true,
  );

  return (
    <div className="apex-proto apex-proto-backdrop page-enter">
      <div className="mx-auto max-w-6xl px-8 py-16 relative">
        {/* Hero */}
        <div className="flex items-center gap-3 mb-3">
          <div className="apex-mark apex-mark-spin" />
          <span className="t-micro">Prototype 01 · Command Bar</span>
        </div>
        <h1 className="t-display mb-3">One keystroke to all of Apex.</h1>
        <p className="t-body t-dim max-w-2xl mb-10">
          A floating pill at the top of every page. Press{' '}
          <span className="kbd">⌘</span> <span className="kbd">K</span> anywhere to open.
          Four modes — Ask, Run, Build, Find — make the same bar useful to business users,
          operators, and builders.
        </p>

        {/* The pill (always visible) */}
        <button
          onClick={() => setOpen(true)}
          className="cmd-pill w-full max-w-xl mx-auto flex items-center gap-3 px-5 py-3.5 text-left"
        >
          <MagnifyingGlassIcon className="h-4 w-4 t-dim" />
          <span className="t-body t-dim flex-1">Ask Apex anything…</span>
          <span className="flex items-center gap-1">
            <span className="kbd">⌘</span>
            <span className="kbd">K</span>
          </span>
        </button>

        {/* Open CTA */}
        <div className="mt-6 flex items-center justify-center gap-2 t-body t-dim">
          <CommandLineIcon className="h-4 w-4" />
          Press <span className="kbd">⌘</span><span className="kbd">K</span> anywhere to open — or
          <button onClick={() => setOpen(true)} className="underline hover:text-[color:var(--accent-ink)] transition-colors">click the pill</button>.
        </div>

        {/* 4-mode explainer */}
        <div className="mt-16">
          <div className="t-micro mb-4">Four modes · one bar</div>
          <div className="grid md:grid-cols-4 gap-4">
            {TABS.map((t) => {
              const copy = MODE_COPY[t.key];
              return (
                <div key={t.key} className="surface rail p-5 persona-card">
                  <div className="flex items-center justify-between mb-4">
                    <div className="h-9 w-9 rounded-lg surface-2 flex items-center justify-center">
                      <t.icon className="h-4 w-4 text-[color:var(--accent-ink)]" />
                    </div>
                    <span className="group-badge" style={{ color: 'var(--accent-ink)', borderColor: 'var(--accent-ring)', background: 'rgba(91,140,255,0.08)' }}>
                      {t.key.toUpperCase()}
                    </span>
                  </div>
                  <div className="t-title mb-1.5">{copy.title}</div>
                  <p className="t-body t-dim mb-4">{copy.desc}</p>
                  <div className="t-num text-xs t-dim border-l-2 pl-3" style={{ borderColor: 'var(--accent-ring)' }}>
                    {copy.example}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Keyboard cheat sheet */}
        <div className="mt-10 surface-2 p-5 flex flex-wrap items-center gap-6 text-xs t-dim">
          <div className="flex items-center gap-2"><span className="kbd">⌘</span><span className="kbd">K</span> Open</div>
          <div className="flex items-center gap-2"><span className="kbd">↑</span><span className="kbd">↓</span> Navigate</div>
          <div className="flex items-center gap-2"><span className="kbd">⇥</span> Switch mode</div>
          <div className="flex items-center gap-2"><span className="kbd">↵</span> Select</div>
          <div className="flex items-center gap-2"><span className="kbd">⌘</span><span className="kbd">↵</span> Run in background</div>
          <div className="flex items-center gap-2"><span className="kbd">ESC</span> Close</div>
        </div>
      </div>

      {/* Full-screen overlay */}
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center pt-[14vh] px-4"
          style={{ background: 'rgba(5, 8, 14, 0.6)', backdropFilter: 'blur(6px)' }}
          onClick={() => setOpen(false)}
        >
          <div
            className="w-full max-w-2xl surface-hi"
            style={{ boxShadow: 'var(--elev-2), var(--glow)' }}
            onClick={(e) => e.stopPropagation()}
          >
            <SpotlightContents
              tab={tab}
              setTab={setTab}
              q={q}
              setQ={setQ}
              results={results}
              inputRef={inputRef}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function SpotlightContents({
  tab, setTab, q, setQ, results, inputRef, inline,
}: {
  tab: TabKey;
  setTab: (t: TabKey) => void;
  q: string;
  setQ: (s: string) => void;
  results: Result[];
  inputRef: React.RefObject<HTMLInputElement>;
  inline?: boolean;
}) {
  return (
    <>
      {/* Input row */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-[color:var(--surface-border)]">
        <MagnifyingGlassIcon className="h-5 w-5 t-dim" />
        <input
          ref={inputRef}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder={`${tab === 'ask' ? 'Ask Apex anything' : tab === 'run' ? 'Run a playbook, action, or work item' : tab === 'build' ? 'Build a blueprint, playbook, or action' : 'Find files, work items, or agents'}…`}
          className="flex-1 bg-transparent outline-none text-[15px] placeholder:text-[color:var(--ink-dim)]"
          style={{ color: 'var(--ink)' }}
          readOnly={inline}
        />
        <span className="kbd">ESC</span>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 px-3 pt-3">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`chip ${tab === t.key ? 'chip-on' : ''}`}
          >
            <t.icon className="h-3.5 w-3.5" />
            {t.label}
          </button>
        ))}
      </div>

      {/* Results (grouped) */}
      <div className="p-3 max-h-[50vh] overflow-y-auto dark-scrollbar">
        {results.length === 0 ? (
          <div className="px-3 py-10 text-center t-body t-dim">No matches for “{q}”.</div>
        ) : (
          <>
            {(['recent', 'suggested'] as const).map((g) => {
              const group = results.filter((r) => r.group === g);
              if (!group.length) return null;
              return (
                <div key={g} className="mb-2">
                  <div className="t-micro px-3 pb-2 pt-1">{g === 'recent' ? 'Recent' : 'Suggested'}</div>
                  <ul className="space-y-1">
                    {group.map((r, i) => {
                      const isFirst = g === 'recent' && i === 0;
                      return (
                        <li
                          key={`${g}-${i}`}
                          className={`flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer ${isFirst ? 'chip-on' : 'hover:bg-white/[0.03]'}`}
                        >
                          <r.icon className="h-4 w-4 t-dim" />
                          <div className="flex-1 min-w-0">
                            <div className="text-sm truncate" style={{ color: 'var(--ink)' }}>{r.title}</div>
                            <div className="text-xs t-dim truncate">{r.sub}</div>
                          </div>
                          {r.kbd && <span className="kbd">{r.kbd}</span>}
                          <ArrowRightIcon className="h-4 w-4 t-dim" />
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-5 py-3 border-t border-[color:var(--surface-border)] text-xs t-dim">
        <div className="flex items-center gap-3">
          <span><span className="kbd">↑</span> <span className="kbd">↓</span> navigate</span>
          <span><span className="kbd">↵</span> select</span>
          <span><span className="kbd">⇥</span> switch mode</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="dot dot-think" /> Apex is ready
        </div>
      </div>
    </>
  );
}
