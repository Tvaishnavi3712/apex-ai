# Apex ChatSTP Router

The user-facing entry agent for STP demos. Classifies queries and delegates to
one of the four specialist agents (PolicyAgent, MaintenanceAgent,
DiagnosticsAgent, ReliabilityAgent).

## How delegation works

Two paths, in priority order:

1. **Foundry Agent Service runtime** — invokes the specialist's runtime ARN via
   `azure_openai-foundry_agent.invoke_agent_runtime`. Configure ARNs via:
   - `APEX_STP_POLICY_ARN`
   - `APEX_STP_MAINTENANCE_ARN`
   - `APEX_STP_DIAGNOSTICS_ARN`
   - `APEX_STP_RELIABILITY_ARN`

   The deploy script writes a paste-ready env block once all four
   specialists are READY.

2. **In-process fallback** — when no ARN is set (e.g. local dev), the router
   imports the specialist's `invoke()` directly. The Dockerfile copies all
   four specialist folders into `/app` to make this work in the container.

## Tools

| Tool | Purpose |
|------|---------|
| `classify_intent(query)` | Heuristic classifier (policy / maintenance / diagnostics / reliability / off_topic / unclear) |
| `delegate_to_policy(query)` | UC-1 specialist |
| `delegate_to_maintenance(query)` | UC-2 specialist |
| `delegate_to_diagnostics(query)` | UC-3 specialist |
| `delegate_to_reliability(query)` | UC-4 specialist |

## Demo behavior

- All 4 demo questions are classified + delegated correctly.
- Off-topic ("how's the weather?") returns the polite redirect:
  `I'm focused on STP plant operations — try asking me about a policy, equipment, or maintenance.`

## Test locally

```bash
cd foundry_agent-agents/apex-stp-chatstp-router
python test_local.py    # uses in-process fallback
```
