# Apex STP MaintenanceAgent

UC-2 specialist for ChatSTP — equipment PM history with engineer attribution.

## What it does

- Looks up the last preventive maintenance for any equipment tag (e.g. `P-3A`).
- Resolves the lead engineer + technician roster from the personnel directory.
- Returns the S3 path to the work-package PDF for the chat UI to render.
- Refuses to invent equipment IDs — if the user says "the pump", it asks
  "Which pump? P-3A, P-3B, or P-3C?".

## Tools

| Tool | Purpose |
|------|---------|
| `lookup_pm_history(equipment_id, lookback_days=365)` | Last-N PMs for an asset |
| `get_engineer_attribution(wo_id)` | Lead engineer + techs for a WO |
| `fetch_work_package(wo_id)` | S3 path/HTTPS link to PDF |

## Demo question

> When was the last PM on Pump-3A and who worked on it?

Expected pattern:

```
Last PM on P-3A: 2026-03-18
Performed by: Diane Okafor (lead) + Marcus Holloway, Jamal Greene
Scope: Bearing oil sample, vibration baseline, seal-cavity inspection
Work package: s3://apex-stp-work-packages/2026/WO-2026-00871.pdf
```

## Test locally

```bash
cd foundry_agent-agents/apex-stp-maintenance-agent
python test_local.py
```
