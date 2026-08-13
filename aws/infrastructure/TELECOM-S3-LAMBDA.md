# Verizon Far Edge · Path B — S3 + Lambda trigger

This stack creates the **real cloud-trigger** path for the Full Certification
Cycle demo. Drop a ROBOT XML into the S3 bucket and the pipeline fires
automatically — same orchestrator, same SSE stream, same JIRA output as
the UI upload path.

## Architecture

```
  Engineer            S3 bucket                Lambda                APEX backend
  ───────             ─────────                ──────                ────────────
   cp foo.xml ──►  apex-vz-cycles-*  ──► apex-vz-cycle-trigger ──► POST /telecommunications/cycle-start
                   (cycles/*.xml)        (Python 3.11 · 30 s)        ?s3_key=cycles/foo.xml
                                                                              │
                                                                              ▼
                                                                       5-stage pipeline
                                                                              │
                                                                              ▼
                                                                       Real JIRA tickets
```

## One-command deploy

```bash
# Option A — auto-detect a running ngrok tunnel on localhost:4040
./infrastructure/deploy_path_b.sh --auto-ngrok

# Option B — paste a known backend URL
./infrastructure/deploy_path_b.sh --backend-url https://my-backend.example.com/api/v1

# Option C — interactive (script prompts)
./infrastructure/deploy_path_b.sh
```

The script does the safe preflight you'd otherwise type 8 times:

1. Validates `aws sts get-caller-identity` (creds work)
2. Validates `sam --version` (SAM CLI present)
3. Validates the CFN template (`sam validate`)
4. Auto-detects ngrok if `--auto-ngrok`
5. Re-uses an existing bucket name if you've deployed before (avoids
   "BucketAlreadyExists" on update)
6. Shows the deploy summary
7. Asks for **explicit y/N** before running `sam deploy`

## Prerequisites (one-time setup)

```bash
# 1. AWS CLI configured (creds that can deploy a SAM stack)
aws configure

# 2. SAM CLI
brew install aws-sam-cli

# 3. ngrok — to expose your laptop's :8000 backend to AWS Lambda
brew install ngrok
ngrok config add-authtoken <your-token>      # one-time

# Start a tunnel BEFORE running deploy_path_b.sh --auto-ngrok
ngrok http 8000
```

> If you have a permanent backend URL (e.g. behind ALB / API Gateway), skip
> ngrok and pass `--backend-url` directly.

## Smoke test

After deploy, drop a ROBOT XML and watch the Lambda fire:

```bash
./infrastructure/test_path_b.sh
```

This:
- Resolves the bucket + lambda names from CFN outputs
- Copies the bundled v2412 ROBOT XML to `s3://<bucket>/cycles/<timestamp>.xml`
- Tails the Lambda's CloudWatch logs in real time (`aws logs tail --follow`)

You'll see (in order):
```
2026-05-19T... triggering cycle for s3://apex-vz-cycles-.../cycles/...test.xml
2026-05-19T... requested  https://your-ngrok-url/api/v1/telecommunications/cycle-start
2026-05-19T... preview    event: cycle_start...
2026-05-19T... status     200
```

And then on the APEX UI at `/canvas/playbook/pb-tel-1-run` you'll see
the same 5-stage timeline tick through that you'd see for a manual
file drop — proof that both Path A and Path B converge on the same
orchestrator.

## Teardown

```bash
./infrastructure/deploy_path_b.sh --teardown
```

Empties the S3 bucket first (CFN can't delete a non-empty bucket), then
`aws cloudformation delete-stack`. Asks y/N before anything destructive.

## Files

| File | Purpose |
|---|---|
| `telecom-s3-lambda.yaml` | SAM CFN template — defines bucket + Lambda + event |
| `telecom_cycle_lambda/cycle_trigger.py` | Lambda handler (stdlib only, < 100 lines) |
| `telecom_cycle_lambda/requirements.txt` | Empty — no deps |
| `deploy_path_b.sh` | One-command deploy wrapper with preflight |
| `test_path_b.sh` | Smoke test — drop XML, tail Lambda logs |
| `TELECOM-S3-LAMBDA.md` | This doc |

## Cost

Free-tier covers this comfortably:
- Lambda: ~1 invocation per cycle × 30 s × 256 MB → well within 1M req/mo + 400K GB-sec/mo
- S3: a few KB per cycle, single bucket → pennies/mo
- CloudWatch Logs: 14-day retention, ~1 KB/cycle → essentially free

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Lambda fires but APEX never receives | Backend URL unreachable from AWS | Use `ngrok http 8000`; redeploy with `--auto-ngrok` |
| 502 from APEX in Lambda logs | Backend down or wrong port | Restart `uvicorn`; confirm `/health` returns 200 |
| `aws s3 cp` succeeds but Lambda never fires | S3 event filter mismatch (prefix `cycles/`, suffix `.xml`) | Confirm upload path |
| Tickets not appearing in JIRA | Backend in mock mode | Confirm `JIRA_URL` + `JIRA_TOKEN` set in `backend/.env`; restart backend |
| `BucketAlreadyExists` on deploy | Bucket name globally taken (S3 is global) | Edit deploy script — use a different suffix |
