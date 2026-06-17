# Failure Repair Demo

`examples/buggy_counter/` is intentionally wrong. It exists to demonstrate how an agent should use DUTPilot evidence to repair RTL.

## Expected Failure

Run:

```bash
python -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

The testbench expects a counter to increment by one on each enabled clock. The DUT increments by two, so the first checked count should fail.

Expected report location:

```text
dutpilot_runs/buggy_counter/reports/report.json
```

The report should have:

- `status`: `fail`
- `stage`: `simulate`
- `primary_error`: a `DUTPILOT_FAIL` marker describing the count mismatch

## Codex Repair Flow

Codex should:

1. Read `.agents/skills/dutpilot/SKILL.md`.
2. Run the existing config.
3. Read `dutpilot_runs/buggy_counter/reports/report.json`.
4. Use `primary_error` and `markers.fail` as the main debugging target.
5. Inspect `examples/buggy_counter/counter.v` and `examples/buggy_counter/tb_counter.v`.
6. Make the smallest RTL edit that matches the testbench expectation.
7. Rerun the same command.
8. Read the new `report.json`.
9. Stop when `status == "pass"`.

## Report Reading Logic

Use this decision model:

```text
if status == "pass":
    report simulation pass for the supplied testbench
elif stage == "compile":
    inspect compile.log and fix syntax or missing module issues
elif primary_error contains "DUTPILOT_FAIL":
    inspect the named failing behavior in the DUT/testbench
else:
    inspect simulate.log, transcript.log, and wave if present
```

Do not claim the fixed counter is formally verified. The correct statement is that it passed the supplied self-checking simulation testbench.
