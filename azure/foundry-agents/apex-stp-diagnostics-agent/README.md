# Apex STP DiagnosticsAgent

UC-3 specialist for ChatSTP — common-issue analysis across the STP work-package
corpus.

## What it does

- Searches the work-package corpus for a specific asset.
- Aggregates failure modes ranked by frequency (top 5).
- Cites at least 3 specific WO IDs as evidence per failure mode.
- Returns "No failure history indexed for this asset" if the corpus is empty —
  never fabricates failure modes.

## Tools

| Tool | Purpose |
|------|---------|
| `search_work_packages(equipment_id, optional_topic)` | Filter WO corpus |
| `aggregate_failure_modes(equipment_ids, system_id)` | Rank + cite evidence |

## Demo question

> What are the most common issues with Pump-3A?

Expected pattern (top 5 failure modes ranked by frequency for P-3A):

```
Top issues for P-3A:
1. Vibration above limit (axial) (33% of 9 events) — typical lead time 5 days,
   mitigation: Re-baseline coupling alignment; replace bearings if pattern persists.
   Cited from: WO-2025-03311, WO-2025-03987, WO-2026-00188
2. Mechanical seal cavity leak (22% of 9 events) — ...
...
```

## Test locally

```bash
cd foundry_agent-agents/apex-stp-diagnostics-agent
python test_local.py
```
