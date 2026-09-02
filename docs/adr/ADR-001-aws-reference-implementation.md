# ADR-001: AWS as the reference implementation

- **Status:** Accepted
- **Date:** 2026-08-14
- **Deciders:** Apex accelerator team
- **Ticket:** APEX-14

## Context

The repository ships the same Apex AI Platform as parallel per-cloud builds:
`aws/`, `azure/`, and a placeholder `gcp/`. The AWS and Azure builds are near
mirrors — same FastAPI backend shape (22 API routers), same Next.js frontend,
same playbooks / blueprints / actions layout — but they are not identical, and
every feature currently has to be designed once and then ported.

Without a designated lead build, product decisions risk being made twice with
subtle divergence, and "which copy is correct?" becomes a recurring question
during demos and customer work.

## Decision

**The `aws/` build is the reference implementation.** New features, demo
scenarios, API surface changes, and data-model changes are designed and land in
`aws/` first. The `azure/` build is a deliberate port that tracks the AWS
reference; `gcp/` remains a placeholder until a runtime decision is made (see
ADR-003).

### The Azure divergence is explicitly acknowledged

`azure/` is a **port, not a byte-for-byte mirror**. Known, accepted divergences:

| Concern | AWS (`aws/`) | Azure (`azure/`) |
|---|---|---|
| Table store | `services/dynamodb.py` (DynamoDB + in-memory mock) | `services/cosmos.py` (Cosmos DB NoSQL) + `services/local_store.py` (disk-persisted mock) |
| Object store | `services/s3.py` (S3) | `services/blob.py` (Blob Storage) |
| LLM | Bedrock (`services/bedrock_claude.py`) | Azure OpenAI (`services/azure_openai.py`, tiered: fast / balanced / quality) |
| Agent runtime | Bedrock AgentCore (`services/agentcore.py`) | AI Foundry Agent Service (`services/foundry_agent.py`); cloud-neutral reasoning split out into `services/agent_simulators.py` |
| Predictive ML | SageMaker (`services/sagemaker.py`) | Azure ML (`services/azure_ml.py`) + shared `services/prediction_base.py` |
| Queue | SQS (`services/sqs.py`) | Service Bus (`services/queue.py`) |
| Admin router | `api/aws_admin.py` | `api/azure_admin.py` |
| Ports | 3000 / 8000 | 3002 / 8002 (side-by-side local runs) |
| Auth | IAM / boto3 credential chain | Microsoft Entra ID, `DefaultAzureCredential`, no keys |
| Infra | CloudFormation (`aws/infrastructure/*.yaml`) | Bicep (`azure/infrastructure/azure/main.bicep`) |

Azure-specific constraints (e.g. the `Deny-PublicPaaSEndpoints` landing-zone
policy forcing local dev onto the persisted mock store) are documented in
`azure/README_AZURE.md`, which is the authoritative delta document.

## Alternatives considered

- **Two co-equal reference builds** — rejected: doubles design effort and
  guarantees drift; there is no arbiter when the builds disagree.
- **Single build with deploy-time cloud flags** — rejected here; see ADR-002
  for why the platform uses per-cloud sibling builds instead.

## Consequences

**Positive:**
- One source of truth for product and API decisions — the AWS build.
- Demo scenarios and seeded content are defined once, then ported.
- Code review is simpler: reviewers evaluate the AWS change first.

**Negative / accepted trade-offs:**
- The Azure build temporarily lags the reference whenever a feature lands;
  lag is tracked via `azure/README_AZURE.md` ("Still to build" section).
- Contributors must check whether a change needs an Azure port before
  closing a ticket that touches shared concepts.
