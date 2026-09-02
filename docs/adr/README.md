# Architecture Decision Records (ADRs)

This directory contains the Architecture Decision Records for the Apex AI Platform.

An ADR is a short document that captures **one** significant architecture decision:
the context that forced it, the decision itself, and the consequences we accepted.

## When to write an ADR

Write an ADR when a change is **architecturally significant** — i.e. it is hard to
reverse later and affects more than one component. Examples:

- Choosing or replacing a cloud service / runtime / data store
- Changing the multi-cloud structure or provider-abstraction approach
- Introducing a new cross-cutting pattern (auth, logging, deployment, agent routing)

Do **not** write ADRs for routine implementation details, bug fixes, or config tweaks.

## How to add an ADR

1. Copy [`template.md`](template.md) to `ADR-NNN-short-kebab-title.md`
   (use the next free number — see the index below).
2. Fill in every section. Keep it short — one page max.
3. Status starts as **Proposed**. It becomes **Accepted** when the PR merges.
4. Add a row to the index below.
5. Reference the ADR in your PR description.

ADRs are **immutable once Accepted**. If a decision changes, write a new ADR that
**supersedes** the old one — never edit history.

## Status lifecycle

`Proposed` → `Accepted` → `Deprecated` or `Superseded by ADR-NNN`

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](ADR-001-aws-reference-implementation.md) | AWS as the reference implementation | Accepted |
| [ADR-002](ADR-002-multi-cloud-provider-abstraction.md) | Multi-cloud provider abstraction approach | Accepted |
| [ADR-003](ADR-003-agent-runtime-strategy.md) | Agent runtime strategy across clouds | Accepted |
