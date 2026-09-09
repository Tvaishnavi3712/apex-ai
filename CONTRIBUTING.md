# Contributing to Apex AI Platform

Thanks for contributing. This repo contains the per-cloud builds of the Apex
AI Platform (`aws/` reference implementation, `azure/` port — see
[ADR-001](docs/adr/ADR-001-aws-reference-implementation.md)).

## Branches

- Branch from `main` using the Jira key: `feat/APEX-XX-short-title` or
  `fix/APEX-XX-short-title`.
- Keep branches short-lived; open a PR as soon as the change is reviewable.

## Pull requests

- Every PR uses the pull request template (`.github/PULL_REQUEST_TEMPLATE.md`).
  Fill in all sections: summary, linked issue, test evidence, security
  considerations, and the pre-merge checklist.
- Link the Jira issue with a closing keyword (`Closes APEX-XX`).
- If your change touches a shared concept (routers, services, actions SDK),
  check whether the other cloud build needs the matching port before closing
  the ticket.

## Code review

- Any PR containing AI-generated code is reviewed against
  [`docs/code-review-rubric.md`](docs/code-review-rubric.md). The rubric covers
  hallucinated API usage, swallowed exceptions, unexercised error paths,
  cross-cloud duplication, fabricated defaults, and behaviour-asserting tests.
- Reviewers must complete the rubric walkthrough (see the rubric's training
  section) before picking up AWS review stories.

## Architecture Decision Records (ADRs)

We record significant architecture decisions as ADRs in
[`docs/adr/`](docs/adr/). The process is defined in
[`docs/adr/README.md`](docs/adr/README.md); in short:

1. **When:** the decision is architecturally significant — hard to reverse and
   affects more than one component (cloud service choices, multi-cloud
   structure, runtime strategy, cross-cutting patterns). Not for bug fixes or
   routine implementation details.
2. **How:** copy [`docs/adr/template.md`](docs/adr/template.md) to
   `docs/adr/ADR-NNN-short-title.md` (next free number), fill in Context /
   Decision / Alternatives / Consequences, and add a row to the index in
   `docs/adr/README.md`.
3. **Status:** ADRs enter as `Proposed` and become `Accepted` when the PR
   merges. Accepted ADRs are immutable — a changed decision gets a new ADR
   that supersedes the old one.

Existing foundational decisions:

- [ADR-001 — AWS as the reference implementation](docs/adr/ADR-001-aws-reference-implementation.md)
- [ADR-002 — Multi-cloud provider abstraction approach](docs/adr/ADR-002-multi-cloud-provider-abstraction.md)
- [ADR-003 — Agent runtime strategy across clouds](docs/adr/ADR-003-agent-runtime-strategy.md)

## Local development

- AWS build: `cd aws && ./start.sh` (backend :8000, frontend :3000).
- Azure build: see `azure/README_AZURE.md` (backend :8002, frontend :3002;
  seed via the `/api/v1/playbooks/seed` + `/api/v1/blueprints/seed` endpoints).
- Both builds run fully offline via per-service mocks — no cloud credentials
  are required for local work.
