---
name: dutpilot
description: Use this skill for Verilog/SystemVerilog RTL simulation verification with DUTPilot, especially when validating a DUT and testbench using Icarus Verilog, running iverilog/vvp, inspecting DUTPILOT_PASS or DUTPILOT_FAIL markers, generating report.json, or opening VCD waveforms.
---

# DUTPilot

DUTPilot is a CLI-first RTL simulation wrapper for agent-friendly Verilog/SystemVerilog verification. Use it to run a provided DUT and testbench, inspect simulator logs, and decide the next debugging step from structured reports.

Do not describe DUTPilot results as formal verification. DUTPilot v0.1.x is simulation-based checking with user-provided or existing testbenches.

## Workflow

1. Use `python`, not `python3`, in this repo.
2. Prefer an existing `dutpilot.yaml` when present. Read it before constructing CLI flags.
3. Run verification:

```bash
python -m dutpilot.cli verify path/to/dutpilot.yaml
```

Or, if no config exists:

```bash
python -m dutpilot.cli verify --dut path/to/dut.v --tb path/to/tb.v --top tb_top --sim icarus
```

4. Read `<run_dir>/reports/report.json`.
5. Decide next action from `status`, `stage`, `primary_error`, and `next_action_hint`.
6. If waveform inspection is useful and VCD exists, open it only when the user asks or the task is interactive:

```bash
python -m dutpilot.cli wave <run_dir>
```

`verify` must remain CI/agent-friendly and should not auto-open GUI tools.

## References

- Testbench marker and waveform expectations: `references/testbench-contract.md`
- Report fields and decision guidance: `references/report-schema.md`

## Script

For the common Icarus path, use:

```bash
.agents/skills/dutpilot/scripts/verify_icarus.sh path/to/dutpilot.yaml
```

The script prints the verification result and report path. Read the report JSON afterward before making claims about pass/fail or next steps.
