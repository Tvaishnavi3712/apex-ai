# Code Review Rubric — AI-Generated Code

**Status:** Active
**Ticket:** APEX-18
**Applies to:** every pull request that contains AI-generated code

## Why this rubric exists

Standard code review habits assume a human author who understood the problem
they were solving. That assumption does not hold for AI-generated code. A
generator produces code that is plausible, idiomatic, and can be confidently
wrong — it does not know our APIs, our repo layout, or whether the code it
wrote has ever actually run. Reviewing AI-generated code therefore means
verifying things a human author could be trusted to have checked. This rubric
is that verification list.

For every PR containing AI-generated code, the reviewer walks each check below.
A check that cannot be confirmed becomes a question or a blocker — never
silence.

## The checks

### 1. Hallucinated or non-existent API usage

AI models invent methods, parameters, endpoints, and even whole SDKs that look
exactly right.

- Verify every external call (AWS/Azure SDK, third-party library, HTTP
  endpoint) exists in the version pinned in `requirements.txt` /
  `package.json`. Check the official docs or the installed package — not your
  memory.
- Confirm every import resolves and every signature matches: parameter names,
  order, return shape.
- Red flags: methods you "think you've seen", ARNs/endpoints/constants that
  look official but appear in no documentation, APIs from a different SDK major
  version than the one we pin.
- Evidence required: the code actually runs (a test, a script, or a recorded
  local run). A read-through alone cannot clear this check.

### 2. Silently swallowed exceptions

Generators love making errors disappear so the happy path reads cleanly.

- Search the diff for: bare `except:`, `except Exception: pass`, catch blocks
  that only log, empty `catch {}`, `try`/`except` wrapped around code that
  should fail loudly, and error returns quietly converted to `None` or an empty
  list.
- Every caught exception must be handled meaningfully, re-raised, or logged
  with enough context to diagnose the failure — and the choice must make sense
  for the caller, not just for the diff.

### 3. Plausible-looking but unexercised error paths

Error branches are where never-run generated code hides.

- For every error or fallback branch in the diff, ask: what evidence shows this
  path has ever executed? Accept a test, a forced-failure run, or a log line
  from a real run — nothing else.
- Check the error handling matches the failure it claims to handle; generated
  code routinely handles the wrong failure very convincingly.
- No evidence = require a test or a manual forced-failure run before approving.

### 4. Duplicated logic across the AWS and Azure action directories

This repo mirrors functionality across **16 AWS action directories** under
`aws/actions/` and **22 Azure action directories** under `azure/actions/`
(see [ADR-001](adr/ADR-001-aws-reference-implementation.md) and
[ADR-002](adr/ADR-002-multi-cloud-provider-abstraction.md)).

- For any change inside `aws/actions/` or `azure/actions/`, open the sibling
  cloud folder: does equivalent logic exist there? Should this change be
  mirrored, or is the difference deliberate?
- Deliberate divergence belongs in the thin per-service adapters per ADR-002.
  Business logic copied between clouds without a stated reason is a blocker.
- A fix applied to one cloud and silently forgotten in the other is a finding
  even when the PR "works".

### 5. Hardcoded values and fabricated defaults

Generators fill gaps with invented values instead of asking.

- Look for hardcoded regions, bucket/table names, endpoints, ARNs, ports,
  timeouts, magic numbers, and anything credential-shaped.
- For every default value, ask: does this trace to a real requirement or config
  (`.env`, settings, an ADR), or did the generator make it up? Fabricated
  defaults presented as real configuration are a blocker.
- Anything secret-shaped is an automatic blocker — see the secrets checkbox in
  the PR template.

### 6. Tests assert behaviour, not restate the implementation

Generated tests often re-implement the code's internals and then assert that
the code does what the code does — a tautology that can never fail.

- For each test in the diff, ask: would this test fail if the implementation
  were wrong? If it mirrors the implementation line-for-line, or mocks the very
  thing being tested, it proves nothing.
- Require assertions on observable behaviour: outputs, state changes, API
  responses, side effects — not on internal call sequences, unless the call
  sequence *is* the contract.
- A diff whose tests cover only the happy path sends you back to check 3.

## Findings and severity

| Severity | Meaning | Examples |
|---|---|---|
| **Blocker** | Must be fixed before merge | Hallucinated API, swallowed exception hiding a real failure, secret-shaped value, fabricated default presented as real config |
| **Question** | Author must answer with evidence | Unexercised error path, unexplained cross-cloud divergence |
| **Note** | Improvement, not gating | Clearer naming, missing comment on a deliberate choice |

## Training requirement

No AWS review story may start until every reviewer has completed a walkthrough
of this rubric. Training is one session where the team reviews a real
AI-generated PR against all six checks together. Record completion here:

| Reviewer | Trained on (date) | Session lead |
|---|---|---|
| | | |

## Related

- `.github/PULL_REQUEST_TEMPLATE.md` — the AI-generated code checkbox every PR
  already carries
- [ADR-001](adr/ADR-001-aws-reference-implementation.md) and
  [ADR-002](adr/ADR-002-multi-cloud-provider-abstraction.md) — the cloud
  structure the duplication check refers to
