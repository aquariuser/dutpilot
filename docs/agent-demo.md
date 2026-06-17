# Agent Demo

## Demo Goal

This demo shows how Codex can use DUTPilot as an agent-callable local skill. Codex calls a deterministic local tool, reads `report.json`, and iterates from real compile or simulation results instead of guessing.

## Recommended Codex Prompt

```text
$dutpilot

Create a 4-bit counter and a self-checking testbench.
Run DUTPilot with Icarus.
Read report.json.
If it fails, fix the RTL or testbench and rerun until status=passed.
```

For the included passing example:

```text
$dutpilot Verify examples/adder/dutpilot.yaml and summarize report.json.
```

For the included repair example:

```text
$dutpilot Run examples/buggy_counter/dutpilot.yaml. Read report.json, explain the mismatch, fix counter.v, and rerun until the provided testbench passes.
```

## Expected Agent Workflow

1. Create or modify RTL.
2. Create or modify a self-checking testbench.
3. Run DUTPilot.
4. Read `dutpilot_runs/<case>/reports/report.json`.
5. Inspect `status` and `stage`.
6. Use `primary_error`, `next_action_hint`, and logs to choose the next action.
7. Fix RTL or testbench.
8. Rerun until the report is passing.

## Example Command

```bash
python3 -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

Then inspect:

```bash
cat dutpilot_runs/adder/reports/report.json
```

## Example Report Interpretation

Passing report:

```text
status=pass, stage=simulate, primary_error=null
```

Interpretation: the DUT passed the provided DUTPilot/Icarus testbench.

Failing report:

```text
status=fail, stage=simulate, primary_error="DUTPILOT_FAIL: ..."
```

Interpretation: the simulator ran, but the self-checking testbench found a mismatch. Inspect the failure marker, then compare DUT behavior with the testbench expectation.

Compile failure:

```text
status=fail, stage=compile
```

Interpretation: inspect `logs/compile.log` before changing behavior.

Inconclusive future report:

```text
status=inconclusive
```

Interpretation: repair the testbench so it emits an explicit `DUTPILOT_PASS` or `DUTPILOT_FAIL`.

Do not call a passing simulation complete verification. Say it passed the provided testbench.
