# APEX Frontend

Next.js 16 + React 18 + TypeScript 5 — the APEX AI Platform web UI.

## Local development

```bash
npm install
npm run dev          # http://localhost:3000
```

The frontend reads `NEXT_PUBLIC_API_URL` to find the FastAPI backend.
Default: `http://localhost:8000/api/v1`.

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## CBB demo mode

Three hero demos are hard-wired for the Cornerstone Building Brands pitch:

| Demo | URL | Flow |
|---|---|---|
| 1 — Zero-Touch Order Mod | `/apex-lens` → select *Order Mod* → opens `/agent-hub?demo=1` | Fabric → Athena → CRM → Teams |
| 2 — QC Batch Ingestion | `/apex-lens` → *QC Batch* → `/agent-hub?demo=2` | Fabric One → Tolerance check → SAP hold → Teams |
| 3 — Disruption Reroute | `/apex-lens` → *Port Strike* → `/agent-hub?demo=3` | Supply Monitor → BOM → Reroute options → Director approval |

Every CBB artifact (3 playbooks, 3 blueprints, 10 actions, 6 connectors, 3 pipelines, 4 exec charts) is seeded from `pages/*.tsx` so the demo works offline.

## Deployment — Vercel

### One-time setup

```bash
npm i -g vercel
vercel login
vercel link                     # links this folder to a Vercel project
```

Then set the backend URL in Vercel:

```bash
vercel env add NEXT_PUBLIC_API_URL production
# paste e.g. https://apex-api.cbts.com/api/v1
```

### Deploy

```bash
./deploy.sh                     # preview deploy
./deploy.sh --prod              # production deploy
```

The script runs `tsc --noEmit`, does a local production build, then pushes to Vercel. The `vercel.json` in this folder pins the framework, region (iad1), security headers, and rewrites `/api/v1/*` to the API host — so the browser can call the backend without CORS configuration.

### CI / GitHub

Vercel auto-deploys every push once the repo is linked:

- `main` → production
- feature branches → preview URL per commit

## Structure

```
src/
  pages/          — Next.js routes (canvas, actions, pipelines, connectors, apex-lens, agent-hub, command-center, ...)
  components/
    AppShell/     — sidebar + topbar + data-source banner
    common/       — Button, Badge, Card, etc.
    BlueprintDesigner/, PlaybookBuilder/, ...
  lib/            — Zustand store, API client
  styles/
    apex.css      — shared design tokens (.card, .btn, .chip-*)
    globals.css   — Tailwind entry
```

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Dev server on :3000 |
| `npm run build` | Production build |
| `npm run start` | Serve the production build |
| `npm run lint` | ESLint |
| `npm test` | Jest + Testing Library |
| `npx tsc --noEmit` | Type check only |

## Troubleshooting

**Sidebar looks broken** — make sure `src/styles/apex.css` is imported from `pages/_app.tsx`.

**"Offline" banner on every page** — `NEXT_PUBLIC_API_URL` is wrong or the backend is down. The UI falls back to sample data so the demo never crashes.

**Charts not rendering on Command Center** — confirm `recharts` is in `package.json` (it is). `npm i` again if you just pulled.
