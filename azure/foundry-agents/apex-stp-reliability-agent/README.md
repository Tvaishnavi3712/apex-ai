# Apex STP ReliabilityAgent

UC-4 specialist for ChatSTP — predictive-maintenance recommendations from
sensor + failure-history data.

## Required output format (4 lines, no exceptions)

```
<RISK_TIER>
Days-until-failure: <N> days (confidence band <low>-<high>).
Recommended PM: <action>. Avoidance estimate: $<USD>.
[Decision logged to apex.audit_log: <id>]
```

The Audit Lens scrapes the `apex.audit_log` line — the format must match.

## Tools

| Tool | Purpose |
|------|---------|
| `predict_rul(equipment_id, horizon_days=30)` | Days-to-failure + band |
| `detect_anomalies(equipment_id, lookback_days=14)` | Active sensor anomalies |
| `recommend_pm(equipment_id)` | Targeted PM action + avoidance USD |
| `compute_risk_score(equipment_id)` | Tier + audit_log_id |

## Demo question

> Predict failure risk for Pump-3A in next 30 days.

Must cite the seeded `ANOM-P3A-2026-04-22` vibration anomaly and quote the
exact `scripted_message` from the seed corpus.
