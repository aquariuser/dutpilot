---
name: dutpilot
description: Use this skill when a user asks Codex to run, inspect, debug, or repair a Verilog/SystemVerilog DUT with the local DUTPilot RTL simulation harness. DUTPilot is also a reference pattern for wrapping a local domain tool as an agent-callable skill.
---

# DUTPilot Skill

DUTPilot is a repo-local, agent-callable harness around a small RTL simulation tool. The simulator backend is intentionally narrow; the main purpose is to demonstrate a reliable skill contract for local tools.

Use this skill to run the tool, read the structured report, and make decisions from evidence. Do not describe DUTPilot results as formal verification. DUTPilot reports simulation results from the provided self-checking testbench.

## Trigger

Use this skill when the user asks to:

- Validate a DUT/testbench with DUTPilot.
- Run `dutpilot.yaml`.
- Inspect a DUTPilot `report.json`.
- Debug a `DUTPILOT_FAIL`, compile error, simulation error, or missing pass marker.
- Repair RTL and rerun the local simulation harness.
- Demonstrate how a local tool can be exposed to Codex as a skill.

Do not use this skill for unrelated HDL design work unless the user wants DUTPilot to run or inspect a DUTPilot report.

## Inputs

Preferred input is an existing config file:

```text
path/to/dutpilot.yaml
```

Required config fields:

```yaml
case: <case_name>
dut: <dut_file.v>
tb: <testbench_file.v>
top: <testbench_top_module>
sim: icarus
```

If no config exists, the command-line equivalent requires:

- `--dut path/to/dut.v`
- `--tb path/to/tb.v`
- `--top tb_top`
- `--sim icarus`
- optional `--case case_name`

The testbench should be self-checking and print:

- `DUTPILOT_PASS` on success.
- `DUTPILOT_FAIL: <reason>` before `$fatal` or `$finish` on failure.

For VCD output, write:

```verilog
$dumpfile("waves/wave.vcd");
$dumpvars(0, <tb_top>);
```

## Commands

Use `python`, not `python3`, in this repo unless the user explicitly asks for `python3`.

Read the config before running when possible:

```bash
python -m dutpilot.cli verify path/to/dutpilot.yaml
```

Without a config:

```bash
python -m dutpilot.cli verify --dut path/to/dut.v --tb path/to/tb.v --top tb_top --sim icarus
```

For the adder smoke test:

```bash
python -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

For the intentional failure demo:

```bash
python -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

If waveform inspection is useful and a VCD exists, open it only when the user asks:

```bash
python -m dutpilot.cli wave <run_dir>
```

`verify` must remain CI/agent-friendly and must not auto-open GUI tools.

## Outputs

Each run writes:

```text
dutpilot_runs/<case>/
  src/
  tb/
  build/
  logs/
  reports/
  scripts/
  waves/
```

Always read the structured report before making claims:

```text
dutpilot_runs/<case>/reports/report.json
```

Important report fields:

- `status`: `pass` or `fail`
- `stage`: `compile` or `simulate`
- `primary_error`: first actionable error or failure marker, or `null`
- `next_action_hint`: concise suggested next step
- `markers`: detected `DUTPILOT_PASS` and `DUTPILOT_FAIL` lines
- `errors`: parsed simulator errors/fatals/syntax diagnostics
- `warnings`: parsed warnings
- `return_codes`: compile and simulation return codes
- `artifacts`: paths to logs, report, summary, simulation binary, and optional wave

## Decision Rules

1. If `status == "pass"`, say the supplied simulation testbench passed. Mention scope when relevant. Do not call it formal proof or exhaustive verification.
2. If `stage == "compile"`, inspect `logs/compile.log` first and fix syntax, missing module, or compile option issues.
3. If `stage == "simulate"` and `primary_error` contains `DUTPILOT_FAIL`, use that failure reason as the primary debugging target.
4. If simulation failed without a fail marker, inspect `logs/simulate.log`, `logs/transcript.log`, and the waveform path if present.
5. If no `DUTPILOT_PASS` appears, treat the run as failed even if process return codes are zero.
6. When repairing code, keep edits scoped to the DUT or testbench needed for the reported failure, then rerun and reread `report.json`.
7. When reporting results, cite `status`, `stage`, and `primary_error` or state that `primary_error` is `null`.

## References

- Testbench marker and waveform expectations: `references/testbench-contract.md`
- Report fields and decision guidance: `references/report-schema.md`
- Agent contract: `../../../docs/agent-contract.md`
- Failure repair demo: `../../../docs/failure-repair-demo.md`

## Helper Script

For the common Icarus path, this helper may be used:

```bash
.agents/skills/dutpilot/scripts/verify_icarus.sh path/to/dutpilot.yaml
```

The script prints the verification result and report path. Read the report JSON afterward before making claims about pass/fail or next steps.
