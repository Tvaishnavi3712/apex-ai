# ADR-003: Agent runtime strategy across clouds

- **Status:** Accepted
- **Date:** 2026-08-14
- **Deciders:** Apex accelerator team
- **Ticket:** APEX-14

## Context

Agents are the product's core artifact, and each cloud offers a different
native agent runtime. Two hard constraints shape the strategy:

1. **Provider-native execution matters in front of customers.** On AWS the
   story is Bedrock AgentCore; on Azure it is the AI Foundry Agent Service.
   Abstracting both behind one runtime would erase the provider-native value
   proposition.
2. **Demos must never depend on cloud availability.** Engineers run without
   credentials, runtimes have cold starts (observed >30s on AgentCore), and a
   live demo cannot afford either.

## Decision

**A three-tier strategy: cloud-native runtime per provider, per-cloud agent
packages built from shared definitions, and a deterministic in-process
simulator as the universal fallback.**

### Tier 1 — Cloud-native runtime per provider

| Cloud | Runtime | Where it lives |
|---|---|---|
| AWS | **Bedrock AgentCore** | Agent packages in `aws/agentcore-agents/` (32 packages); invoked via `AgentCoreService` (`aws/backend/services/agentcore.py`) which shells out to `aws bedrock-agentcore invoke-agent-runtime`; deployed runtime ARNs registered in `AGENT_ARNS`; deploy via `deploy_*.py` scripts |
| Azure | **Azure AI Foundry Agent Service** | Agent packages in `azure/foundry-agents/` (32 packages, same agent set); `foundry_runtime.py` provides the primitives (`FoundryAgentApp`, `Agent`, `tool`) with in-process Azure OpenAI function calling; provision via `deploy_foundry_agents.py --all` |
| GCP (future) | **Vertex AI Agent Engine** (anticipated) | `gcp/` is a placeholder today. A GCP build adopts this ADR by adding: a runtime adapter service, a `gcp/agents/` package dir, deploy scripts, and simulator entries — following the existing two-build pattern |

### Tier 2 — Per-cloud agent packages, shared definitions

The same 32 agents exist as `apex-*` packages in both `agentcore-agents/` and
`foundry-agents/`. Agent *definitions* (name, instructions, tools, model tier)
are the shared contract; the packaging (entrypoint, runtime SDK calls) is
provider-specific. The backend seeds agent records from `DEFAULT_AGENTS` and
routes by agent name/alias, so callers never care which runtime answers.

### Tier 3 — In-process simulator fallback (always on)

Every agent also answers through a deterministic in-process simulator with no
network hop: the routing cascade in `aws/backend/services/agentcore.py`
(`invoke_agent`) and the shared `azure/backend/services/agent_simulators.py`.
Simulators are anchored on the versioned synthetic-data corpora
(`synthetic-data/<domain>/`) so demo answers are realistic, sub-50ms, and
identical offline.

Routing rule: hard-route known demo agent IDs to the correct simulator or
runtime (the `*_AGENT_IDS` sets), fall back to the registered runtime ARN, and
fail honestly for unknown IDs — never silently answer with the wrong demo's
data. Live runtimes can be toggled per agent family (precedent:
`ENABLE_EPROD_AGENTCORE = False` keeps EPROD on the simulator while its
AgentCore cold-start issue is debugged).

## Alternatives considered

- **Single portable runtime (e.g. self-hosted LangGraph) on all clouds** —
  rejected: erases the Bedrock AgentCore / AI Foundry story that sells the
  platform; adds a runtime we must operate everywhere.
- **Runtime-only, no simulators** — rejected: cold starts and credential
  requirements make live demos and laptop development fragile.
- **Simulators-only (never deploy real runtimes)** — rejected: the deployed
  AgentCore/Foundry runtimes are the technical proof for customers; simulators
  alone would be vaporware.

## Consequences

**Positive:**
- Provider-native demos on each cloud, with a zero-dependency offline path
  that is always available mid-presentation.
- Adding GCP is a mechanical extension of an existing pattern, not a redesign.
- Runtime problems degrade gracefully to simulators instead of failing.

**Negative / accepted trade-offs:**
- Three tiers must be kept consistent per agent (definition, package,
  simulator branch). Mitigation: agent name/alias routing sets and shared
  synthetic-data corpora keep the tiers anchored to one source.
- Simulator answers are deterministic snapshots; they can drift from what the
  live runtime would say. Accepted: simulators exist for demo reliability,
  not production correctness.
