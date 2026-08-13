#!/usr/bin/env bash
#
# Path B (S3 + Lambda) deploy wrapper for the Verizon Far Edge demo.
#
# This script does the safe preflight you'd otherwise type 8 times in a row,
# then runs `sam deploy` against the CFN template at telecom-s3-lambda.yaml.
#
# It will NOT deploy anything without explicit confirmation — every
# destructive step prompts y/N first. Safe to run repeatedly.
#
# Usage:
#   ./deploy_path_b.sh                       # interactive
#   ./deploy_path_b.sh --backend-url <URL>   # skip the URL prompt
#   ./deploy_path_b.sh --auto-ngrok          # auto-detect + use local ngrok
#   ./deploy_path_b.sh --teardown            # delete the stack + bucket

set -euo pipefail

# ─── Defaults ────────────────────────────────────────────────────────────
STACK_NAME="apex-vz-telecom-cycle"
TEMPLATE_FILE="$(dirname "$0")/telecom-s3-lambda.yaml"
BUCKET_NAME_DEFAULT="apex-vz-cycles-$(date +%s)"
REGION_DEFAULT="us-east-1"

# ─── Args ────────────────────────────────────────────────────────────────
BACKEND_URL=""
AUTO_NGROK=false
TEARDOWN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend-url) BACKEND_URL="$2"; shift 2 ;;
    --auto-ngrok)  AUTO_NGROK=true;  shift   ;;
    --teardown)    TEARDOWN=true;    shift   ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# ─── Color helpers ───────────────────────────────────────────────────────
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; B='\033[1;34m'; N='\033[0m'
info()  { echo -e "${B}▸${N} $*"; }
ok()    { echo -e "${G}✓${N} $*"; }
warn()  { echo -e "${Y}⚠${N} $*"; }
err()   { echo -e "${R}✗${N} $*"; }
ask()   { read -r -p "$(echo -e "${Y}?${N} $1 [y/N]: ")" reply; [[ "$reply" =~ ^[Yy]$ ]]; }

# ─── Teardown branch ─────────────────────────────────────────────────────
if $TEARDOWN; then
  warn "About to DELETE stack '$STACK_NAME' (S3 bucket + Lambda + logs)."
  if ! ask "Continue?"; then exit 0; fi
  # Empty the bucket first — CFN can't delete a non-empty bucket.
  BUCKET=$(aws cloudformation describe-stack-resource --stack-name "$STACK_NAME" \
            --logical-resource-id IngestBucket --query 'StackResourceDetail.PhysicalResourceId' \
            --output text 2>/dev/null || echo "")
  if [[ -n "$BUCKET" ]]; then
    info "Emptying bucket s3://$BUCKET ..."
    aws s3 rm "s3://$BUCKET" --recursive --quiet || true
  fi
  info "Deleting stack..."
  aws cloudformation delete-stack --stack-name "$STACK_NAME"
  aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME"
  ok "Stack '$STACK_NAME' deleted."
  exit 0
fi

# ─── Preflight ───────────────────────────────────────────────────────────
echo
echo "━━━ Preflight check ━━━"

# AWS CLI
if ! command -v aws >/dev/null 2>&1; then
  err "AWS CLI not found. Install: brew install awscli"; exit 1
fi
AWS_IDENTITY=$(aws sts get-caller-identity --output json 2>/dev/null || echo "")
if [[ -z "$AWS_IDENTITY" ]]; then
  err "AWS credentials not configured. Run: aws configure"; exit 1
fi
ACCOUNT=$(echo "$AWS_IDENTITY" | python3 -c "import sys,json; print(json.load(sys.stdin)['Account'])")
USER=$(echo "$AWS_IDENTITY" | python3 -c "import sys,json; print(json.load(sys.stdin)['Arn'].split('/')[-1])")
ok "AWS account: $ACCOUNT  user: $USER"

# SAM CLI
if ! command -v sam >/dev/null 2>&1; then
  err "SAM CLI not found. Install: brew install aws-sam-cli"; exit 1
fi
ok "SAM CLI: $(sam --version 2>&1 | head -1)"

# Template
if [[ ! -f "$TEMPLATE_FILE" ]]; then
  err "Template missing: $TEMPLATE_FILE"; exit 1
fi
info "Validating template..."
if sam validate --template-file "$TEMPLATE_FILE" --region "$REGION_DEFAULT" >/dev/null 2>&1; then
  ok "Template valid: $TEMPLATE_FILE"
else
  err "Template validation failed. Re-running with full output:"
  sam validate --template-file "$TEMPLATE_FILE" --region "$REGION_DEFAULT"
  exit 1
fi

# ─── Backend URL resolution ──────────────────────────────────────────────
if [[ -z "$BACKEND_URL" ]] && $AUTO_NGROK; then
  info "Auto-detecting ngrok..."
  # ngrok's local API returns active tunnels on http://127.0.0.1:4040/api/tunnels
  if NGROK_JSON=$(curl -s --max-time 2 http://127.0.0.1:4040/api/tunnels 2>/dev/null); then
    NGROK_URL=$(echo "$NGROK_JSON" | python3 -c "
import sys, json
try:
    t = json.load(sys.stdin).get('tunnels', [])
    https = [x for x in t if x.get('proto') == 'https']
    print(https[0]['public_url'] if https else '')
except Exception:
    pass
" 2>/dev/null)
    if [[ -n "$NGROK_URL" ]]; then
      BACKEND_URL="${NGROK_URL}/api/v1"
      ok "Detected ngrok tunnel: $BACKEND_URL"
    else
      warn "ngrok running but no https tunnel found."
    fi
  else
    warn "ngrok not running. Start with: ngrok http 8000"
  fi
fi

if [[ -z "$BACKEND_URL" ]]; then
  echo
  warn "Backend URL not set. The Lambda needs to POST to your APEX backend."
  echo "  Options:"
  echo "    1. Run  'ngrok http 8000'  in another terminal, then re-run with --auto-ngrok"
  echo "    2. Pass --backend-url https://<your-deployed-backend>/api/v1"
  echo "    3. Skip Path B for now — Path A (UI upload) already works."
  read -r -p "Enter backend URL (or blank to abort): " BACKEND_URL
  [[ -z "$BACKEND_URL" ]] && { warn "Aborted."; exit 0; }
fi

# Sanity: must contain /api/v1
if [[ "$BACKEND_URL" != *"/api/v1"* ]]; then
  warn "Backend URL doesn't contain '/api/v1'. Common mistake — appending it."
  BACKEND_URL="${BACKEND_URL%/}/api/v1"
  ok "Adjusted: $BACKEND_URL"
fi

# ─── Bucket name resolution ──────────────────────────────────────────────
# If a previous deploy exists, reuse its bucket name (avoids the
# "BucketAlreadyExists" failure on update).
EXISTING_BUCKET=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
                    --query 'Stacks[0].Outputs[?OutputKey==`IngestBucketName`].OutputValue | [0]' \
                    --output text 2>/dev/null || echo "")
if [[ -n "$EXISTING_BUCKET" && "$EXISTING_BUCKET" != "None" ]]; then
  BUCKET_NAME="$EXISTING_BUCKET"
  ok "Re-using existing bucket: $BUCKET_NAME"
else
  BUCKET_NAME="apex-vz-cycles-${ACCOUNT}"
  info "New bucket name: $BUCKET_NAME"
fi

# ─── Summary + confirm ───────────────────────────────────────────────────
echo
echo "━━━ Deploy summary ━━━"
echo "  Stack       : $STACK_NAME"
echo "  Region      : $REGION_DEFAULT"
echo "  Template    : $TEMPLATE_FILE"
echo "  Bucket name : $BUCKET_NAME"
echo "  Backend URL : $BACKEND_URL"
echo

if ! ask "Proceed with sam deploy?"; then warn "Cancelled."; exit 0; fi

# ─── Build + Deploy ──────────────────────────────────────────────────────
echo
info "Running sam build..."
sam build --template-file "$TEMPLATE_FILE" >/tmp/sam_build.log 2>&1 \
  || { err "sam build failed:"; tail -30 /tmp/sam_build.log; exit 1; }
ok "sam build complete."

info "Running sam deploy..."
sam deploy \
  --stack-name        "$STACK_NAME" \
  --region            "$REGION_DEFAULT" \
  --capabilities      CAPABILITY_IAM \
  --resolve-s3 \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset \
  --parameter-overrides \
      ApexBackendUrl="$BACKEND_URL" \
      IngestBucketName="$BUCKET_NAME"

echo
ok "Deploy complete."
echo
info "Outputs:"
aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table
echo
ok "Test it:  ./infrastructure/test_path_b.sh"
