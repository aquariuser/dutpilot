# Failure Repair Demo

This demo explains the intended `examples/buggy_counter/` workflow. It demonstrates an agent repair loop. DUTPilot runs the local tool and writes evidence; it does not automatically repair the RTL.

## Run The Demo

```bash
python3 -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

The first run is expected to fail. The decisive stage should be simulation, because the DUT compiles but the self-checking testbench finds a behavior mismatch.

## What To Read

Open:

```text
dutpilot_runs/buggy_counter/reports/report.json
```

Focus on:

- `status`
- `stage`
- `primary_error`
- `next_action_hint`
- `artifacts.transcript_log`

Then inspect the transcript if needed:

```text
dutpilot_runs/buggy_counter/logs/transcript.log
```

## Expected Failure

The testbench expects:

- Reset drives `count=0`.
- Each following clock increments `count` by `1`.

The intentionally buggy RTL does:

```verilog
count <= count + 4'd2;
```

So the first checked increment should produce a `DUTPILOT_FAIL` marker similar to:

```text
DUTPILOT_FAIL: expected count 1, got 2
```

## Agent Repair Steps

The agent should:

1. Run DUTPilot.
2. Read `report.json`.
3. Confirm `status=fail` and `stage=simulate`.
4. Read `primary_error` and transcript evidence.
5. Compare `tb_counter.v` expectations with `counter.v` behavior.
6. Change the counter increment from `+ 4'd2` to `+ 4'd1`.
7. Rerun:

```bash
python3 -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

After the fix, the expected result is `status=pass` in current DUTPilot v0.1.

## Scope

This demo shows the agent repair loop:

```text
run local tool -> read report -> edit code -> rerun
```

It does not show automatic DUTPilot repair, and a passing run only means the design passed the provided DUTPilot/Icarus testbench.
