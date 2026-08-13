# Apex Action Test Scripts

This folder holds the **manual test plan** for every action handler in the
Apex platform, rendered as a Word document.

## Files

| File | What it is |
|---|---|
| [`generate_test_script.py`](generate_test_script.py) | Generator. Reads the live action registry and renders the test plan. |
| `Apex_Action_Test_Script.docx` | The rendered test plan. **Regenerate** instead of hand-editing. |

## How to regenerate

Any time a new action handler is added, or an existing handler's input/output
schema changes, re-run the generator:

```bash
cd aws/backend
source venv/bin/activate
python ../test-scripts/generate_test_script.py
```

The generator:

1. Calls `reload_registry()` so any newly-added handler is picked up from disk.
2. Walks every registered action, extracts its real `input_schema` +
   `output_schema` (via the AST extractor in
   `backend/services/action_schema_extractor.py`).
3. Writes an updated `Apex_Action_Test_Script.docx` right here in this folder.

Commit the updated `.docx` alongside the handler change.

## What's in the document

- **Overview + prerequisites** — how to bring the stack up and provision the
  Cosmos DB tables every handler expects.
- **Testing methodology** — UI + CLI test patterns, pass criteria.
- **Action catalog** — one section per industry, then one sub-section per
  action, each with:
  - Meta table (action ID, industry, category, handler path).
  - Input parameters table (field · type · required · description).
  - Output fields table (field · type · description).
  - "Sample test values" with happy-path JSON inputs + expected outcomes —
    the inputs match the sample rows that
    [`backend/services/aws_provisioner.py`](../backend/services/aws_provisioner.py)
    seeds into Cosmos DB, so they'll actually succeed against your AWS account.
- **Troubleshooting** — what the different `error_type` values mean
  (`runtime`, `load_failed`, `not_found`, `bad_arguments`).

## Adding scenarios for a new action

To add happy-path test scenarios for a newly-added action:

1. Seed sample data for it in [`aws_provisioner.py`](../backend/services/aws_provisioner.py)
   (add a new `TableSpec` or append items to an existing table).
2. Run the provisioner so the rows land in your AWS account:
   ```bash
   curl -X POST 'http://localhost:8000/api/v1/aws/provision?region=us-east-1'
   ```
3. Add an entry keyed by the new `action_id` to the `SCENARIO` dict at the
   top of `generate_test_script.py`.
4. Re-run the generator.

If you skip step 3, the action will still appear in the document with its
schema — just without pre-written happy-path scenarios.
