#!/usr/bin/env bash
# Deploy the APEX frontend (Next.js) to Vercel.
#
# Usage:
#   ./deploy.sh            — deploy preview
#   ./deploy.sh --prod     — deploy to production
#
# Prereqs:
#   npm i -g vercel
#   vercel login
#   vercel link            # one-time: link this folder to the Vercel project
#
# Environment variables set on Vercel (Settings → Environment Variables):
#   NEXT_PUBLIC_API_URL    — FastAPI base URL, e.g. https://apex-api.cbts.com/api/v1
set -euo pipefail

cd "$(dirname "$0")"

# Preflight: node + vercel CLI
command -v node   >/dev/null || { echo "✗ node not installed";   exit 1; }
command -v vercel >/dev/null || { echo "✗ vercel CLI missing — run: npm i -g vercel"; exit 1; }

echo "→ Installing dependencies"
npm ci --no-audit --no-fund

echo "→ TypeScript check"
npx tsc --noEmit

echo "→ Local production build (smoke test)"
NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000/api/v1}" npm run build

if [[ "${1:-}" == "--prod" ]]; then
  echo "→ Deploying to Vercel production"
  vercel deploy --prod --yes
else
  echo "→ Deploying Vercel preview"
  vercel deploy --yes
fi

echo "✓ Done"
