/**
 * Mission Control Prototype
 * Command Center redesign — two-tone, operator-grade dashboard.
 */
import {
  ArrowTrendingUpIcon,
  CpuChipIcon,
  CurrencyDollarIcon,
  FireIcon,
  BoltIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowUpRightIcon,
  ArrowDownRightIcon,
  RocketLaunchIcon,
} from '@heroicons/react/24/outline';

const THROUGHPUT = [
  42, 48, 55, 49, 62, 68, 72, 80, 78, 84, 92, 96,
  104, 112, 108, 118, 124, 130, 128, 136, 140, 138, 142, 150,
];

const ACTIVITY = [
  { agent: 'InvoiceBot',    ok: true,  t: '12s ago',  msg: 'Processed WI-3201 · confidence 0.97' },
  { agent: 'ClaimsBot',     ok: true,  t: '41s ago',  msg: 'Approved claim CL-8821' },
  { agent: 'ContractBot',   ok: false, t: '1m ago',   msg: 'Flagged lot 8821 for human review · schema mismatch' },
  { agent: 'InvoiceBot',    ok: true,  t: '1m ago',   msg: 'Processed WI-3200 · confidence 0.94' },
  { agent: 'IntakeBot',     ok: true,  t: '2m ago',   msg: 'Routed patient 4421 to triage' },
  { agent: 'CNCBot',        ok: true,  t: '3m ago',   msg: 'Reviewed CNC code 77-A · OK' },
];

export default function MissionControlPrototype() {
  return (
    <div className="apex-proto apex-proto-backdrop min-h-screen page-enter">
      <div className="mx-auto max-w-[1400px] px-8 py-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-3">
            <div className="apex-mark apex-mark-spin" />
            <div>
              <div className="t-micro">Prototype 03 · Mission Control</div>
              <div className="t-title">Command Center</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="chip chip-on"><span className="dot dot-think" /> Live</span>
            <span className="chip t-num">us-east-1</span>
            <span className="chip">Last 24h</span>
            <span className="chip">Last 7d</span>
          </div>
        </div>
        <p className="t-body t-dim mb-8">Six metrics, one screen. Two-tone palette. Tabular numerics. Nothing moves unless data changes.</p>

        {/* Top KPI strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
          <Kpi label="Docs today"     value="18,412" delta="+12.4%" trend="up"   ok    icon={ArrowTrendingUpIcon} />
          <Kpi label="Accuracy"       value="96.4%"  delta="+0.3pt" trend="up"   ok    icon={CheckCircleIcon} />
          <Kpi label="Avg cost / doc" value="$1.42"  delta="-8.1%"  trend="down" ok    icon={CurrencyDollarIcon} />
          <Kpi label="P95 latency"    value="3.1s"   delta="+0.2s"  trend="up"   warn  icon={CpuChipIcon} />
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-12 gap-4">
          {/* Throughput sparkline */}
          <section className="surface rail col-span-12 lg:col-span-8 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="t-micro mb-1">Throughput · docs per hour</div>
                <div className="flex items-baseline gap-3">
                  <span className="t-num t-title">150</span>
                  <span className="t-body t-dim">now</span>
                  <span className="chip chip-on t-num">+12.4%</span>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="chip chip-on">24h</span>
                <span className="chip">7d</span>
                <span className="chip">30d</span>
              </div>
            </div>
            <BigSparkline values={THROUGHPUT} />
            <div className="flex justify-between mt-2 t-num text-xs t-dim">
              <span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>now</span>
            </div>
          </section>

          {/* Accuracy gauge */}
          <section className="surface rail col-span-12 md:col-span-6 lg:col-span-4 p-5">
            <div className="t-micro mb-1">Accuracy</div>
            <div className="t-body t-dim mb-4">Target ≥ 95%</div>
            <Gauge value={0.964} />
            <div className="grid grid-cols-3 gap-2 mt-5 text-center">
              <div>
                <div className="t-micro">Extract</div>
                <div className="t-num text-sm">97.1%</div>
              </div>
              <div>
                <div className="t-micro">Validate</div>
                <div className="t-num text-sm">96.8%</div>
              </div>
              <div>
                <div className="t-micro">Decide</div>
                <div className="t-num text-sm">94.9%</div>
              </div>
            </div>
          </section>

          {/* Cost meter */}
          <section className="surface rail col-span-12 md:col-span-6 lg:col-span-4 p-5">
            <div className="flex items-center justify-between mb-1">
              <div className="t-micro">Cost per document</div>
              <CurrencyDollarIcon className="h-4 w-4 t-dim" />
            </div>
            <div className="t-body t-dim mb-5">Target ≤ $2.00</div>
            <div className="flex items-baseline gap-2 mb-3">
              <span className="t-num text-3xl" style={{ color: 'var(--ink)' }}>$1.42</span>
              <span className="t-body t-dim">avg</span>
            </div>
            <CostBar value={1.42} target={2.0} max={3.0} />
            <div className="grid grid-cols-3 gap-3 mt-5">
              <CostBreak label="BDA"   value="$0.82" pct={58} />
              <CostBreak label="Model" value="$0.48" pct={34} />
              <CostBreak label="Infra" value="$0.12" pct={8}  />
            </div>
          </section>

          {/* Agent status */}
          <section className="surface rail col-span-12 lg:col-span-4 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="t-micro">Agents</div>
                <div className="t-title">13 deployed</div>
              </div>
              <BoltIcon className="h-4 w-4 t-dim" />
            </div>
            <ul className="space-y-3">
              {[
                { name: 'InvoiceBot',    status: 'think', sub: 'processing 4 items' },
                { name: 'ClaimsBot',     status: 'ok',    sub: 'idle · ready' },
                { name: 'ContractBot',   status: 'warn',  sub: '1 item flagged' },
                { name: 'IntakeBot',     status: 'ok',    sub: 'idle · ready' },
                { name: 'CNCBot',        status: 'think', sub: 'processing 2 items' },
              ].map((a) => (
                <li key={a.name} className="flex items-center gap-3">
                  <span className={`dot dot-${a.status}`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm" style={{ color: 'var(--ink)' }}>{a.name}</div>
                    <div className="text-xs t-dim truncate">{a.sub}</div>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          {/* Activity heatmap */}
          <section className="surface rail col-span-12 lg:col-span-8 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="t-micro mb-1">Activity · last 7 days</div>
                <div className="t-title">38,211 runs</div>
              </div>
              <div className="flex items-center gap-2 t-dim text-xs">
                <span>less</span>
                {[0.1, 0.3, 0.5, 0.75, 1].map((v, i) => (
                  <span
                    key={i}
                    className="grid-cell"
                    style={{ width: 12, height: 12, background: `rgba(91,140,255,${v})` }}
                  />
                ))}
                <span>more</span>
              </div>
            </div>
            <Heatmap />
          </section>

          {/* Activity feed */}
          <section className="surface rail col-span-12 lg:col-span-4 p-5">
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="t-micro">Live activity</div>
                <div className="t-title">Stream</div>
              </div>
              <span className="chip chip-on"><span className="dot dot-think" /> Live</span>
            </div>
            <ul className="-mx-2">
              {ACTIVITY.map((a, i) => (
                <li
                  key={i}
                  className="group flex items-start gap-3 px-2 py-2 rounded-lg hover:bg-white/[0.03] transition-colors cursor-pointer"
                >
                  {a.ok ? (
                    <CheckCircleIcon className="h-4 w-4 mt-0.5 flex-shrink-0" style={{ color: 'var(--ok)' }} />
                  ) : (
                    <ExclamationTriangleIcon className="h-4 w-4 mt-0.5 flex-shrink-0" style={{ color: 'var(--warn)' }} />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm font-medium" style={{ color: 'var(--ink)' }}>{a.agent}</span>
                      <span className="t-num text-xs t-dim">{a.t}</span>
                    </div>
                    <div className="text-xs t-dim truncate">{a.msg}</div>
                  </div>
                  <ArrowUpRightIcon className="h-3.5 w-3.5 mt-1 t-dim opacity-0 group-hover:opacity-100 transition-opacity" />
                </li>
              ))}
            </ul>
            <div className="mt-3 pt-3 border-t border-[color:var(--surface-border)] text-xs text-center">
              <span className="t-dim">Updated </span>
              <span className="t-num" style={{ color: 'var(--accent-ink)' }}>just now</span>
            </div>
          </section>

          {/* SLA row */}
          <section className="surface rail col-span-12 p-5">
            <div className="flex items-center justify-between mb-5">
              <div>
                <div className="t-micro">SLA · by playbook</div>
                <div className="t-title">On-time delivery</div>
              </div>
              <FireIcon className="h-4 w-4 t-dim" />
            </div>
            <div className="grid md:grid-cols-3 gap-4">
              <Sla name="invoice_processing"   pct={0.98} target={0.95} />
              <Sla name="prior_auth_triage"    pct={0.92} target={0.95} />
              <Sla name="contract_ingest"      pct={0.87} target={0.90} />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function Kpi({
  label, value, delta, trend, ok, warn, icon: Icon,
}: { label: string; value: string; delta: string; trend: 'up' | 'down'; ok?: boolean; warn?: boolean; icon: typeof ArrowTrendingUpIcon }) {
  const Trend = trend === 'up' ? ArrowUpRightIcon : ArrowDownRightIcon;
  return (
    <div className="surface rail p-5 persona-card">
      <div className="flex items-center justify-between mb-3">
        <span className="t-micro">{label}</span>
        <Icon className="h-4 w-4 t-dim" />
      </div>
      <div className="flex items-baseline gap-3">
        <span className="t-num" style={{ fontSize: 26, lineHeight: 1, color: 'var(--ink)' }}>{value}</span>
        <span
          className={`chip t-num inline-flex items-center gap-1 ${ok && !warn ? 'chip-on' : ''}`}
          style={warn ? { color: 'var(--warn)', borderColor: 'rgba(240,180,41,0.35)', background: 'rgba(240,180,41,0.1)' } : {}}
        >
          <Trend className="h-3 w-3" />
          {delta}
        </span>
      </div>
    </div>
  );
}

type Event = { i: number; label: string; kind: 'deploy' | 'incident' };

function BigSparkline({ values }: { values: number[] }) {
  const w = 960, h = 160, pad = 6;
  const events: Event[] = [
    { i: 7,  label: 'ContractBot v1.2', kind: 'deploy' },
    { i: 14, label: 'Schema mismatch',  kind: 'incident' },
  ];
  const max = Math.max(...values);
  const min = Math.min(...values);
  const pts = values.map((v, i) => {
    const x = pad + (i * (w - pad * 2)) / (values.length - 1);
    const y = h - pad - ((v - min) / (max - min || 1)) * (h - pad * 2) - 20;
    return [x, y];
  });
  const d = `M ${pts.map(p => p.join(',')).join(' L ')}`;
  const area = `${d} L ${w - pad},${h - pad} L ${pad},${h - pad} Z`;
  const last = pts[pts.length - 1];
  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id="spk2" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%"  stopColor="#5b8cff" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#5b8cff" stopOpacity="0" />
        </linearGradient>
      </defs>
      {/* gridlines */}
      {[0.25, 0.5, 0.75].map((g) => (
        <line key={g} x1={pad} x2={w - pad} y1={h * g} y2={h * g}
              stroke="rgba(255,255,255,0.05)" strokeDasharray="2 4" />
      ))}
      <path d={area} fill="url(#spk2)" />
      <path d={d} fill="none" stroke="#5b8cff" strokeWidth="2" />
      <circle cx={last[0]} cy={last[1]} r="5" fill="#5b8cff" />
      <circle cx={last[0]} cy={last[1]} r="9" fill="#5b8cff" fillOpacity="0.2" />

      {/* event markers */}
      {events.map((e, idx) => {
        const [x, y] = pts[e.i];
        const color = e.kind === 'deploy' ? '#3ecf8e' : '#f0b429';
        return (
          <g key={idx}>
            <line x1={x} x2={x} y1={y} y2={h - pad} stroke={color} strokeDasharray="3 3" strokeOpacity="0.5" />
            <circle cx={x} cy={y} r="4" fill={color} />
            <circle cx={x} cy={y} r="8" fill={color} fillOpacity="0.2" />
            <rect x={x - 60} y={8} width="120" height="18" rx="9" fill="rgba(255,255,255,0.06)" stroke={color} strokeOpacity="0.4" />
            <text x={x} y={20} textAnchor="middle" fontSize="10" fill={color} fontFamily="Inter, sans-serif">{e.label}</text>
          </g>
        );
      })}
    </svg>
  );
}

function Gauge({ value }: { value: number }) {
  const r = 70, c = 2 * Math.PI * r;
  const dash = c * value;
  return (
    <div className="relative flex items-center justify-center">
      <svg width="180" height="180" viewBox="0 0 180 180">
        <circle cx="90" cy="90" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="10" />
        <circle cx="90" cy="90" r={r} fill="none" stroke="url(#gauge)" strokeWidth="10"
                strokeDasharray={`${dash} ${c}`} strokeLinecap="round"
                transform="rotate(-90 90 90)" />
        <defs>
          <linearGradient id="gauge" x1="0" x2="1">
            <stop offset="0%" stopColor="#5b8cff" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute text-center">
        <div className="t-num" style={{ fontSize: 32, color: 'var(--ink)' }}>{(value * 100).toFixed(1)}%</div>
        <div className="t-micro">extraction</div>
      </div>
    </div>
  );
}

function CostBar({ value, target, max }: { value: number; target: number; max: number }) {
  const pct = (value / max) * 100;
  const tgt = (target / max) * 100;
  return (
    <div className="relative h-2 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
      <div
        className="absolute top-0 left-0 h-full rounded-full"
        style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #5b8cff, #8b5cf6)' }}
      />
      <div
        className="absolute -top-1 h-4 w-0.5"
        style={{ left: `${tgt}%`, background: 'var(--ink-muted)' }}
        title="target"
      />
    </div>
  );
}

function CostBreak({ label, value, pct }: { label: string; value: string; pct: number }) {
  return (
    <div>
      <div className="t-micro mb-1">{label}</div>
      <div className="t-num text-sm mb-1.5" style={{ color: 'var(--ink)' }}>{value}</div>
      <div className="h-1 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: '#5b8cff' }} />
      </div>
    </div>
  );
}

function Heatmap() {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  // seeded pseudo-random to keep layout stable
  const seed = (d: number, h: number) => ((d * 31 + h * 17) % 100) / 100;
  return (
    <div className="space-y-1.5">
      {days.map((d, di) => (
        <div key={d} className="flex items-center gap-2">
          <span className="t-micro w-8">{d}</span>
          <div className="flex gap-1 flex-1">
            {Array.from({ length: 24 }).map((_, hi) => {
              const v = Math.min(1, 0.15 + seed(di, hi) * (hi > 8 && hi < 19 ? 1.1 : 0.5));
              return (
                <div
                  key={hi}
                  className="grid-cell"
                  style={{ flex: 1, height: 18, background: `rgba(91,140,255,${v.toFixed(2)})` }}
                  title={`${d} ${hi}:00`}
                />
              );
            })}
          </div>
        </div>
      ))}
      <div className="flex items-center gap-2 pt-1">
        <span className="t-micro w-8" />
        <div className="flex gap-1 flex-1 t-num text-[10px] t-dim">
          {[0, 6, 12, 18, 23].map((h, i, a) => (
            <span key={h} style={{ flex: 1, textAlign: i === 0 ? 'left' : i === a.length - 1 ? 'right' : 'center' }}>{`${h}:00`}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

function Sla({ name, pct, target }: { name: string; pct: number; target: number }) {
  const missed = pct < target;
  return (
    <div className="surface-2 p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="t-num text-sm" style={{ color: 'var(--ink)' }}>{name}</span>
        <span className={`chip ${missed ? '' : 'chip-on'} t-num`}
              style={missed ? { color: 'var(--warn)', borderColor: 'rgba(240,180,41,0.35)', background: 'rgba(240,180,41,0.1)' } : {}}>
          {(pct * 100).toFixed(1)}%
        </span>
      </div>
      <div className="relative h-1.5 rounded-full" style={{ background: 'rgba(255,255,255,0.06)' }}>
        <div className="absolute top-0 left-0 h-full rounded-full"
             style={{ width: `${pct * 100}%`, background: missed ? 'var(--warn)' : 'linear-gradient(90deg,#5b8cff,#8b5cf6)' }} />
        <div className="absolute -top-0.5 h-2.5 w-0.5"
             style={{ left: `${target * 100}%`, background: 'var(--ink-muted)' }} />
      </div>
      <div className="flex justify-between t-num text-[10px] t-dim mt-1">
        <span>0%</span><span>target {(target * 100).toFixed(0)}%</span><span>100%</span>
      </div>
    </div>
  );
}
