# Verizon Far Edge — Demo Test Files

Four ROBOT Framework XML files. Drag any of these into the Run page or upload via `aws s3 cp` to trigger a certification cycle.

## Files

| File | Tests | Failures | Result | When to use |
|---|---|---|---|---|
| `robot_output_caas_node_v2412_full.xml` | 248 | 12 fail · 5 warn | **FAIL — hold wave** | **★ Default demo file ★** Wind River 24.12 cycle with 3 breaking Redfish schema changes. Generates 17 JIRA tickets. |
| `robot_output_caas_node_v2406_baseline.xml` | 247 | 0 | **PROCEED** | The clean baseline. Use this to show the green-path scenario — 247/247 pass, no tickets created, pipeline completes in 2 seconds. |
| `robot_output_caas_node_v2312_historical.xml` | 247 | 14 fail | **FAIL** | An earlier cycle that should have been held under a stricter cert gate. Use this for the "high-risk Type-B pattern" narrative. |
| `robot_output_partial_run.xml` | 147 | 8 fail | **FAIL — incomplete** | A truncated cycle (147/247 tests) — useful to show how the platform handles incomplete inputs gracefully. |

## How to use

### Path A — UI upload (drag/drop)

1. Open http://localhost:3000/canvas/playbook/pb-tel-1-run
2. Drag any `.xml` file into the dropzone
3. Watch the 5-stage timeline tick through
4. Click any ticket card's "Open in JIRA →" link

### Path B — S3 trigger (`aws s3 cp`)

```bash
aws s3 cp verizon-test-data/robot_output_caas_node_v2412_full.xml \
  s3://apex-vz-cycles-457795063704/cycles/
```

Wait ~20 sec. Refresh JIRA. 17 new tickets appear.

## File details

### `robot_output_caas_node_v2412_full.xml` (the hero demo)

This is the file that lands the wow moment. It contains:
- 14 P1 failures (CU-UP latency, schema drift, IPv6 enumeration, OAM packet loss, RT kernel)
- 1 P2 failure (ChassisIntrusion regression)
- 2 P3 borderline findings (jitter, LDAP latency)
- 3 breaking Redfish schema changes (v1.14.0 → v1.16.0)
- 14 scripts impacted by the drift

When the pipeline runs against this file:
- 17 real JIRA tickets get created
- Each gets the right team label (vendor-engineering, automation-team, security-team, ran-team, oam-team)
- The cert report recommends **HOLD** (wave deployment blocked)
- Schema drift is surfaced with its 14-script impact map

### `robot_output_caas_node_v2406_baseline.xml` (the green-path)

The clean cycle that ran before the schema drift hit. All 247 tests pass. Use this to demonstrate:
- The platform handles success as well as failure
- The pipeline completes in ~2 seconds when there's nothing to do
- The cert report recommends **PROCEED**

### `robot_output_caas_node_v2312_historical.xml` (the cautionary tale)

An Oct 2025 historical Type-B Northeast cycle. 14 failures (94.3% pass rate). Under a temporarily-reduced 60% gate this cycle would clear — but the failure pattern is the exact predictor APEX surfaces today. Use this for the "high-risk pattern caught pre-wave" story arc.

### `robot_output_partial_run.xml` (the edge case)

A truncated cycle that stopped at 147/247 tests. Useful to show the platform doesn't choke on incomplete inputs — it processes what it has and surfaces the incompleteness in the report.

---

**For the demo script, see:** `~/Downloads/APEX_VPSales_Demo_Script.docx` and `~/Downloads/APEX_VPSales_OnePager.docx`.
