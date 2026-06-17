# Agent Demo

This demo shows how Codex should use DUTPilot as a local skill.

## Recommended Prompt

```text
Use the DUTPilot skill to validate examples/adder/dutpilot.yaml.
Run the tool, read report.json, and tell me whether the supplied simulation testbench passed.
Do not describe the result as formal verification.
```

For repair workflows:

```text
Use the DUTPilot skill to run examples/buggy_counter/dutpilot.yaml.
Read the DUTPilot report, identify the failing RTL behavior, fix the bug, and rerun until report.json says pass.
```

## Agent Flow

1. Read `.agents/skills/dutpilot/SKILL.md`.
2. Prefer the existing `dutpilot.yaml`.
3. Run the verification command.
4. Open `dutpilot_runs/<case>/reports/report.json`.
5. Decide from `status`, `stage`, `primary_error`, and `next_action_hint`.
6. Inspect logs or waveforms only when the report points there.

## Passing Example

Run:

```bash
python -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

Then read:

```bash
cat dutpilot_runs/adder/reports/report.json
```

Decision logic:

```text
if status == "pass":
    report that the adder testbench simulation passed
elif stage == "compile":
    inspect logs/compile.log
elif primary_error contains "DUTPILOT_FAIL":
    inspect the failure marker and DUT behavior
else:
    inspect simulate.log, transcript.log, and wave if present
```

## What Codex Should Say

A good final answer is evidence-based:

```text
DUTPilot reports status=pass at stage=simulate for case=adder.
The supplied testbench emitted DUTPILOT_PASS and no errors were parsed.
This means the adder passed this simulation testbench; it is not formal verification.
```

Avoid:

```text
The adder is formally verified.
```
