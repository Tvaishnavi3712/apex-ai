# APEX Developer Training — Starter Package

You are building two agent workflows from scratch. Everything here is either a
contract you must satisfy or a tool that tells you whether you have.

## What you have been given

| | |
|---|---|
| `*/playbooks/*.yaml` | The business rules. Read these first — they are the requirements. |
| `*/sample-files/*.expected.json` | **The specification.** Each carries a `_training` block naming the expected outcome. |
| `*/actions/*/handler.py` | Signatures, schemas and utilities. The bodies are yours to write. |
| `scripts/verify_training_setup.py` | The grader. 33 checks. |
| `scripts/seed_training_data.py` | Fixture data for the tables your handlers read. |

## Getting started

```bash
python3 scripts/seed_training_data.py --cloud local
export USE_LOCAL_MOCK=true
python3 scripts/verify_training_setup.py
```

Everything fails on the first run. That is the starting line.

## The loop

1. Read the playbook. The recipe tells you the order of operations and where to stop.
2. Open a handler. Read the `@apex_action` schema — that is your input and output contract.
3. Implement the body against the TODO specification.
4. Run the harness. Fix what is red.
5. Repeat until 33 of 33.

## Rules

- **Do not change function signatures or `@apex_action` schemas.** The harness
  calls those signatures and other actions depend on the output shape.
- **Do not edit the fixtures.** If a check fails, your handler is wrong, not the test.
- Coerce every numeric input. Your table store returns `Decimal`, blueprints
  return strings, and humans type `"$1,234.50"`. A `_f()` helper is provided —
  use it everywhere.
- Never fail open on an identity or safety check. An unreachable vendor master
  means "unknown vendor", not "vendor fine".

## Done means

```
ALL CHECKS PASSED — 33 of 33
```

...and you can answer these without looking anything up:

1. Why do the duplicate and remit-to checks run *before* the three-way match?
2. Why is `MATH_ERROR` never auto-resolved, even for trivial amounts?
3. Why are appetite and capacity separate actions rather than one score?
4. Why is `sub_04` a referral and not a decline?
5. `inv_06` reconciles perfectly against its PO. Why is it still blocked?
6. Why does the playbook recipe tell the agent *not* to reason about tolerance bands?

The six questions matter more than the code.
