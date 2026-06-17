---
name: dutpilot
description: Use this skill before writing Verilog/SystemVerilog testbenches whenever the task asks to implement, simulate, verify, test, debug, or validate RTL. This skill defines the required self-checking testbench contract, DUTPILOT_PASS/DUTPILOT_FAIL markers, DUTPilot CLI commands, and report.json interpretation rules.
---

# DUTPilot Skill

DUTPilot is a repo-local example of an agent-callable skill around a deterministic local CLI. The concrete domain is RTL simulation with Icarus Verilog, but the skill is also a template for wrapping any vertical-domain local tool.

Use the tool output as evidence. Do not infer correctness from source text alone. DUTPilot does not understand arbitrary RTL functionality by itself; the self-checking testbench encodes the expected behavior, and DUTPilot runs the simulation, parses markers/logs, and writes `report.json`.

## When To Use This Skill

Use this skill before writing Verilog/SystemVerilog testbenches whenever the task involves:

- Writing Verilog/SystemVerilog RTL that should be simulated, verified, tested, debugged, or validated.
- Writing or debugging self-checking testbenches.
- Running DUTPilot with an existing `dutpilot.yaml`.
- Interpreting `dutpilot_runs/<case>/reports/report.json`.
- Iterating based on compile or simulation failures.
- Demonstrating how Codex can call a deterministic local tool and use its structured report.

Do not use this skill for unrelated HDL discussion unless DUTPilot execution, testbench creation, or report inspection is part of the task.

## Required Inputs

DUTPilot needs:

- DUT file, for example `counter.v`.
- Testbench file, for example `tb_counter.v`.
- Top testbench module, for example `tb_counter`.
- Simulator backend, currently `icarus`.
- Optional `dutpilot.yaml`; prefer it when present.

Typical config:

```yaml
case: counter
dut: counter.v
tb: tb_counter.v
top: tb_counter
sim: icarus
```

Paths inside `dutpilot.yaml` are resolved relative to the config file.

## Testbench Contract

When creating a testbench for DUTPilot, do not create a stimulus-only bench. The testbench must be self-checking before it is useful to the agent.

A DUTPilot-compatible testbench must:

- Derive expected behavior from the user request, specification, RTL comments, interface semantics, or explicit assumptions.
- Apply stimulus and compare DUT outputs against expected results.
- Print `DUTPILOT_FAIL: <reason>` on every detected mismatch.
- After a mismatch, call `$fatal`, `$error` followed by termination, or `$finish`.
- Print `DUTPILOT_PASS` only after all intended checks pass.
- Call `$finish` on the successful path.
- Prefer writing a VCD waveform to `waves/wave.vcd`.

Recommended waveform pattern:

```verilog
$dumpfile("waves/wave.vcd");
$dumpvars(0, <tb_top>);
```

If expected behavior is unclear, the agent must either ask the user for the missing specification or write only a minimal smoke test and clearly state that the testbench is not complete functional validation.

Bad example, stimulus-only and not DUTPilot-compatible:

```verilog
initial begin
    a = 1;
    b = 2;
    #10;
    $finish;
end
```

Good example, self-checking with explicit markers:

```verilog
initial begin
    a = 1;
    b = 2;
    #1;
    if (sum !== 3) begin
        $display("DUTPILOT_FAIL: expected sum=3, got %0d", sum);
        $fatal;
    end
    $display("DUTPILOT_PASS");
    $finish;
end
```

## Workflow

Recommended order:

1. Identify whether the task involves RTL implementation, simulation, verification, testbench creation, debugging, or validation.
2. Read and apply the DUTPilot testbench contract before writing the testbench.
3. Write or update the RTL.
4. Write a DUTPilot-compatible self-checking testbench.
5. Create or update `dutpilot.yaml`.
6. Run:

```bash
python3 -m dutpilot.cli verify <dutpilot.yaml>
```

Or:

```bash
python3 -m dutpilot.cli verify --dut <dut.v> --tb <tb.v> --top <tb_top> --sim icarus
```

7. Read:

```text
dutpilot_runs/<case>/reports/report.json
```

8. Decide next steps from `status`, `stage`, `primary_error`, and `next_action_hint`.
9. If failed, modify the RTL or testbench and rerun.
10. Only when `report.json` has `status=pass` in current DUTPilot v0.1, or `status=passed` in a future schema, say it passed the current testbench.

## Commands

Prefer an existing config:

```bash
python3 -m dutpilot.cli verify <dutpilot.yaml>
```

Example:

```bash
python3 -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

Without a config:

```bash
python3 -m dutpilot.cli verify --dut <dut.v> --tb <tb.v> --top <tb_top> --sim icarus
```

Intentional failure demo:

```bash
python3 -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

Open a VCD only when the user asks:

```bash
python3 -m dutpilot.cli wave <run_dir>
```

`verify` must stay non-interactive and must not open GUI tools.

## Report Inspection

Always read the report before making claims:

```text
dutpilot_runs/<case>/reports/report.json
```

When needed, also inspect:

- `dutpilot_runs/<case>/reports/summary.md`
- `dutpilot_runs/<case>/logs/transcript.log`
- `dutpilot_runs/<case>/logs/compile.log`
- `dutpilot_runs/<case>/logs/simulate.log`
- `dutpilot_runs/<case>/waves/wave.vcd`

Important report fields:

- `status`: current v0.1 emits `pass` or `fail`.
- `stage`: current v0.1 emits `compile` or `simulate`.
- `primary_error`: first actionable failure or `null`.
- `next_action_hint`: suggested next step.
- `errors`: parsed simulator diagnostics.
- `warnings`: parsed warnings.
- `markers`: parsed `DUTPILOT_PASS` and `DUTPILOT_FAIL` lines.
- `artifacts`: paths to generated files.
- `return_codes`: compile and simulation return codes.

## Decision Rules

- If `status=pass` or a future report says `status=passed`, only say the RTL passed the provided DUTPilot/Icarus testbench.
- If `stage=compile`, fix syntax errors, missing files, top/module mismatches, compile order, or unsupported constructs first.
- If `stage=simulate` or a future report says `stage=simulation`, inspect `primary_error`, failure markers, RTL behavior, and testbench expectations.
- If a future report says `status=inconclusive`, fix the testbench so it produces a clear `DUTPILOT_PASS` or `DUTPILOT_FAIL`.
- If a future report says `stage=timeout`, inspect clock generation, reset release, wait conditions, and whether `$finish` is reachable.
- If a future report says `stage=tool_missing`, install or configure the required local tool before editing RTL.
- If no `DUTPILOT_PASS` appears, treat the run as failed even when process return codes are zero.
- After editing RTL or testbench code, rerun the same DUTPilot command and reread `report.json`.

## What Not To Claim

Do not claim the RTL is fully verified or formally verified.

Only say it passed the provided DUTPilot/Icarus testbench. Be explicit about scope when reporting results.

## References

- Root testbench contract: `../../../docs/testbench-contract.md`
- Testbench marker and waveform expectations: `references/testbench-contract.md`
- Report fields and decision guidance: `references/report-schema.md`
- Agent contract: `../../../docs/agent-contract.md`
- Agent demo: `../../../docs/agent-demo.md`
- Failure repair demo: `../../../docs/failure-repair-demo.md`

## Helper Script

For the common Icarus path, this helper may be used:

```bash
.agents/skills/dutpilot/scripts/verify_icarus.sh path/to/dutpilot.yaml
```

The script prints the result and report path. Read the report JSON afterward.
