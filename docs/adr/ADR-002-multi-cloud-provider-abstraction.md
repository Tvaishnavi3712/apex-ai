# ADR-002: Multi-cloud provider abstraction approach

- **Status:** Accepted
- **Date:** 2026-08-14
- **Deciders:** Apex accelerator team
- **Ticket:** APEX-14

## Context

Apex is sold as a multi-cloud platform: the same product must run credibly on
AWS today, on Azure today, and on GCP later. The naive approaches each have a
real cost:

- A single codebase with a unified cloud-abstraction library tends to collapse
  to the lowest common denominator of each provider, and demo scenarios need
  provider-native depth (e.g. Bedrock AgentCore runtimes, Azure landing-zone
  policy constraints).
- Fully separate forks per cloud diverge immediately and unmaintainably.

The platform's primary use today is **demo and accelerator work**, where
iteration speed and provider-native fidelity matter more than binary-level
code reuse.

## Decision

**Per-cloud sibling builds (`aws/`, `azure/`, later `gcp/`) with mirrored
structure and thin per-service adapter modules** — not a unified abstraction
library, and not deploy-time cloud flags in one tree.

Concretely:

1. **Mirrored layout.** Both builds keep the same directory shape and the same
   API surface (the 22 routers match 1:1; `aws_admin.py` ↔ `azure_admin.py` is
   the only intentional rename). A file you know in one build exists at the
   same path in the other.

2. **Thin service adapters.** Each cloud dependency is isolated in one module
   with a matching counterpart:
   `dynamodb.py` ↔ `cosmos.py` · `s3.py` ↔ `blob.py` ·
   `bedrock_claude.py` ↔ `azure_openai.py` · `agentcore.py` ↔ `foundry_agent.py`
   · `sagemaker.py` ↔ `azure_ml.py` · `sqs.py` ↔ `queue.py`.
   Router and business logic call the adapter; they never import a cloud SDK
   directly.

3. **Cloud-neutral logic is shared by shape.** Reasoning that has no cloud
   dependency lives in modules that are near-identical across builds
   (`services/agent_simulators.py`, `services/prediction_base.py`,
   `services/list_cache.py`, `services/virtual_fields.py`), with the adapters
   supplying only the transport.

4. **Action handlers stay declarative.** The Actions SDK
   (`actions/sdk/base.py`, `@apex_action`) is provider-shaped; the Azure build
   adds compatibility shims (`actions/sdk/azure_llm.py`,
   `actions/sdk/azure_data.py`) so an industry action handler body does not
   change between clouds.

5. **Every adapter has a local mock.** `USE_LOCAL_MOCK` (AWS in-memory mock) and
   `local_store.py` (Azure disk-persisted mock) mean any build runs fully
   offline on a laptop — demos never require cloud credentials.

## Alternatives considered

- **Unified cloud-abstraction library (one codebase)** — rejected: forces
  lowest-common-denominator semantics, hides provider-native capabilities the
  demos depend on, and adds an abstraction layer to maintain that customers
  will never see.
- **One codebase with deploy-time provider flags** — rejected: conditional
  provider branches rot quickly and make every change a matrix test.
- **Fully independent forks** — rejected: no structural parity, guaranteed
  unbounded drift, no shared review vocabulary.

## Consequences

**Positive:**
- Full provider-native fidelity on each cloud (real Bedrock / real Foundry).
- New cloud = new sibling build following the mirror; the onboarding path is
  mechanical and reviewable.
- Offline-first: per-service mocks keep every demo runnable with no creds.

**Negative / accepted trade-offs:**
- Cross-cloud features are implemented twice (once per build). Mitigation:
  mirrored structure makes ports mechanical; ADR-001 makes AWS the reference
  so ports have a single source.
- Adapter parity is a convention, not enforced by a compiler. Mitigation:
  the 1:1 router surface and adapter naming table in ADR-001 are the review
  checklist for ports.
