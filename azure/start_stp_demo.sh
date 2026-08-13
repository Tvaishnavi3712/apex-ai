#!/bin/bash
# ============================================================================
# STP Demo Startup — one command, everything ready in ~20 seconds.
#
#   ./start_stp_demo.sh           # full start: backend + frontend + prewarmer
#   ./start_stp_demo.sh --quick   # skip prewarmer (use if runtimes already warm)
#   ./start_stp_demo.sh --stop    # stop everything started by this script
#
# What this script does:
#   1. Verifies AWS creds + 5 STP Foundry Agent Service runtimes are READY
#   2. Starts the FastAPI backend on :8000 (kills any existing uvicorn)
#   3. Fires one prewarm pass against all 5 runtimes (cuts first-query latency
#      from ~25s → ~12s) and continues prewarming every 4 min in background
#   4. Starts the Next.js frontend on :3000
#   5. Opens browser to http://localhost:3000/agent-hub?demoMode=stp
#      (Settings → Demo Mode is auto-set to STP via the URL param hook)
#
# Logs go to /tmp/apex-stp-{backend,frontend,prewarmer}.log so the terminal
# stays uncluttered during the demo.
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
SLATE='\033[1;34m'    # STP slate-blue
DIM='\033[2m'
NC='\033[0m'

PIDFILE_BACKEND="/tmp/apex-stp-backend.pid"
PIDFILE_FRONTEND="/tmp/apex-stp-frontend.pid"
PIDFILE_PREWARMER="/tmp/apex-stp-prewarmer.pid"

QUICK=0
STOP=0
for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=1 ;;
    --stop)  STOP=1  ;;
    -h|--help)
      sed -n '2,20p' "$0" | sed 's/^# \?//'
      exit 0
      ;;
  esac
done

# ─── Stop mode ──────────────────────────────────────────────────────────────
if [ "$STOP" = 1 ]; then
  echo -e "${YELLOW}Stopping STP demo…${NC}"
  for pidfile in "$PIDFILE_BACKEND" "$PIDFILE_FRONTEND" "$PIDFILE_PREWARMER"; do
    if [ -f "$pidfile" ]; then
      pid=$(cat "$pidfile")
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null && echo "  ✓ killed pid $pid"
      fi
      rm -f "$pidfile"
    fi
  done
  pkill -f "uvicorn main:app" 2>/dev/null || true
  pkill -f "next dev" 2>/dev/null || true
  pkill -f "prewarm_stp_runtimes" 2>/dev/null || true
  echo -e "${GREEN}stopped.${NC}"
  exit 0
fi

# ─── Banner ─────────────────────────────────────────────────────────────────
echo -e "${SLATE}"
cat <<'BANNER'
══════════════════════════════════════════════════════════
  STP NUCLEAR · ChatSTP Phase 2 — Apex Demo
  Starting full demo environment…
══════════════════════════════════════════════════════════
BANNER
echo -e "${NC}"

# ─── Step 1: Pre-flight ─────────────────────────────────────────────────────
echo -e "${BLUE}[1/5]${NC} Pre-flight checks…"

if ! command -v aws >/dev/null 2>&1; then
  echo -e "  ${RED}✗${NC} aws CLI not on PATH" ; exit 1
fi
ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
if [ "$ACCOUNT" != "457795063704" ]; then
  echo -e "  ${YELLOW}⚠${NC} Expected AWS account 457795063704, got '$ACCOUNT'"
  echo -e "  ${DIM}Run 'aws configure' or 'export AWS_PROFILE=…' first${NC}"
  exit 1
fi
echo -e "  ${GREEN}✓${NC} AWS account: $ACCOUNT"

if [ ! -d backend/venv ]; then
  echo -e "  ${RED}✗${NC} backend/venv missing — run 'cd backend && python3 -m venv venv && pip install -r requirements.txt'"
  exit 1
fi
echo -e "  ${GREEN}✓${NC} backend venv found"

if [ ! -d frontend/node_modules ]; then
  echo -e "  ${YELLOW}⚠${NC} frontend/node_modules missing — running npm install (this takes ~60s)"
  (cd frontend && npm install) >/dev/null 2>&1
fi
echo -e "  ${GREEN}✓${NC} frontend deps installed"

# ─── Step 2: Verify 5 STP runtimes are READY ────────────────────────────────
echo -e "${BLUE}[2/5]${NC} Verifying 5 Foundry Agent Service runtimes…"

# Quick, single-call list — much faster than 5 individual get-agent-runtime calls
runtimes_json=$(aws azure-ai-foundry-control list-agent-runtimes --region us-east-1 2>/dev/null)
ready_count=$(echo "$runtimes_json" | python3 -c "
import json, sys
d = json.load(sys.stdin)
c = sum(1 for r in d.get('agentRuntimes', [])
        if r['agentRuntimeName'].startswith('apex_stp_') and r.get('status') == 'READY')
print(c)
")
if [ "$ready_count" != "5" ]; then
  echo -e "  ${RED}✗${NC} Only $ready_count/5 STP runtimes READY"
  echo -e "  ${DIM}Re-deploy: cd foundry_agent-agents && python3 deploy_stp_agents.py --apply${NC}"
  exit 1
fi
echo -e "  ${GREEN}✓${NC} 5/5 STP runtimes READY (us-east-1, v2+)"

# ─── Step 3: Backend ────────────────────────────────────────────────────────
echo -e "${BLUE}[3/5]${NC} Starting FastAPI backend on :8000…"

# Kill any existing uvicorn so we can rebind
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 1

(cd backend && source venv/bin/activate && \
  nohup uvicorn main:app --port 8000 --host 127.0.0.1 \
  > /tmp/apex-stp-backend.log 2>&1 &
  echo $! > "$PIDFILE_BACKEND")

# Wait for /llm/models to respond (proves multi-LLM endpoints + chat are up)
for i in 1 2 3 4 5 6 7 8; do
  sleep 1
  if curl -s http://localhost:8000/api/v1/llm/models -o /dev/null -w "%{http_code}" 2>/dev/null | grep -q "200"; then
    echo -e "  ${GREEN}✓${NC} backend healthy (took ${i}s)"
    break
  fi
  if [ "$i" = "8" ]; then
    echo -e "  ${RED}✗${NC} backend didn't come up — see /tmp/apex-stp-backend.log"
    exit 1
  fi
done

# ─── Step 4: Prewarmer (optional) ───────────────────────────────────────────
if [ "$QUICK" = 0 ]; then
  echo -e "${BLUE}[4/5]${NC} Pre-warming 5 STP runtimes…"

  pkill -f "prewarm_stp_runtimes" 2>/dev/null || true
  sleep 0.5

  # First prewarm pass synchronously so we see the latency numbers
  # before the demo starts. ~12s typical (5 runtimes × ~2.5s each).
  (cd foundry_agent-agents && python3 prewarm_stp_runtimes.py --once 2>&1) | sed 's/^/    /'

  # Then keep it running every 4 min
  (cd foundry_agent-agents && nohup python3 prewarm_stp_runtimes.py --watch \
    > /tmp/apex-stp-prewarmer.log 2>&1 &
    echo $! > "$PIDFILE_PREWARMER")
  echo -e "  ${GREEN}✓${NC} prewarmer running (every 4 min) — pid $(cat $PIDFILE_PREWARMER)"
else
  echo -e "${BLUE}[4/5]${NC} ${DIM}Prewarmer skipped (--quick mode)${NC}"
fi

# ─── Step 5: Frontend ───────────────────────────────────────────────────────
echo -e "${BLUE}[5/5]${NC} Starting Next.js frontend on :3000…"

pkill -f "next dev" 2>/dev/null || true
sleep 1

(cd frontend && nohup npm run dev \
  > /tmp/apex-stp-frontend.log 2>&1 &
  echo $! > "$PIDFILE_FRONTEND")

# Wait for Next.js to bind (it takes 5-15s on first compile)
for i in 1 2 3 4 5 6 7 8 9 10 12 14 16 18 20 25 30; do
  sleep 1
  if curl -s -o /dev/null http://localhost:3000 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} frontend healthy (took ${i}s)"
    break
  fi
done

# ─── Open browser ───────────────────────────────────────────────────────────
demo_url="http://localhost:3000/agent-hub?demoMode=stp"
echo
echo -e "${SLATE}══════════════════════════════════════════════════════════${NC}"
echo -e "${SLATE}  STP DEMO READY${NC}"
echo -e "${SLATE}══════════════════════════════════════════════════════════${NC}"
echo -e "  Browser → ${GREEN}$demo_url${NC}"
echo -e "  Backend → ${DIM}http://localhost:8000/docs${NC}"
echo
echo -e "  Logs:"
echo -e "    backend    → /tmp/apex-stp-backend.log"
echo -e "    frontend   → /tmp/apex-stp-frontend.log"
[ "$QUICK" = 0 ] && echo -e "    prewarmer  → /tmp/apex-stp-prewarmer.log"
echo
echo -e "  Stop everything: ${YELLOW}./start_stp_demo.sh --stop${NC}"
echo -e "${SLATE}══════════════════════════════════════════════════════════${NC}"

# Open browser (macOS / Linux)
if command -v open >/dev/null 2>&1; then
  open "$demo_url" 2>/dev/null && echo -e "  Browser opened automatically." || echo -e "  ${DIM}Open the URL above manually.${NC}"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$demo_url" 2>/dev/null && echo -e "  Browser opened automatically." || echo -e "  ${DIM}Open the URL above manually.${NC}"
else
  echo -e "  ${DIM}Open the URL above manually.${NC}"
fi
