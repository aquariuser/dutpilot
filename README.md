# DUTPilot

DUTPilot is an agent-callable local skill reference project: it shows how to wrap a focused command-line tool with a Codex skill, stable inputs, repeatable commands, and machine-readable outputs.

The sample domain is RTL simulation. The current tool runs a Verilog/SystemVerilog DUT with a self-checking testbench through Icarus Verilog, then writes logs, waveforms, `report.json`, and `summary.md`. The broader purpose is the skill pattern, not simulator coverage.

DUTPilot reports simulation results from the supplied testbench. It is not a formal verification tool.

## Why This Project Exists

Agents are most useful when they can call local tools that return structured evidence instead of vague terminal output. DUTPilot demonstrates that pattern in a small, inspectable project:

- A domain tool owns execution and artifact layout.
- A repo-scoped skill tells Codex when and how to call the tool.
- A report file gives the agent stable fields for decisions.
- Examples show both passing and failing workflows.

The same pattern can be reused for linters, migration tools, design checkers, data validators, hardware flows, internal CLIs, or any local tool that benefits from agent orchestration.

## Agent Skill Pattern

DUTPilot uses this contract:

- Trigger: a user asks to validate, debug, or repair an RTL DUT/testbench with DUTPilot.
- Inputs: `dutpilot.yaml` or explicit `--dut`, `--tb`, `--top`, and `--sim icarus`.
- Command: `python -m dutpilot.cli verify <config>`.
- Outputs: `dutpilot_runs/<case>/reports/report.json`, logs, summary, optional VCD.
- Decision: Codex reads `status`, `stage`, `primary_error`, and `next_action_hint` before explaining or editing code.

The repo skill lives at:

```text
.agents/skills/dutpilot/SKILL.md
```

See `docs/agent-contract.md` and `docs/build-your-own-skill.md` for the reusable pattern.

## Features

- Repo-scoped Codex skill for an agent-callable local tool.
- Small YAML/JSON config for repeatable runs.
- Standard run directory under `dutpilot_runs/<case>/`.
- Icarus Verilog compile and simulation sample backend.
- Self-checking testbench markers: `DUTPILOT_PASS` and `DUTPILOT_FAIL`.
- Structured `report.json` for agent decisions.
- Human-readable `summary.md`.
- Optional VCD waveform output and GTKWave launch command.
- Passing and failing examples for agent demos.

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/aquariuser/dutpilot.git
cd dutpilot
python3 -m pip install -e .
```

Install Icarus Verilog for the sample RTL flow:

```bash
sudo apt-get update
sudo apt-get install -y iverilog gtkwave
```

`gtkwave` is optional and only needed for waveform viewing.

## Quick Start

Run the passing adder example:

```bash
python3 -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

Expected output:

```text
DUTPilot PASS case=adder report=dutpilot_runs/adder/reports/report.json
```

Inspect the structured report:

```bash
cat dutpilot_runs/adder/reports/report.json
```

Run the intentionally failing counter demo:

```bash
python3 -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

Use `dutpilot_runs/buggy_counter/reports/report.json` to identify the failure and guide a repair.

## CLI Usage

Use a config file:

```bash
python3 -m dutpilot.cli verify path/to/dutpilot.yaml
```

Or pass files directly:

```bash
python3 -m dutpilot.cli verify \
  --dut path/to/dut.v \
  --tb path/to/tb.v \
  --top tb_top \
  --sim icarus \
  --case my_case
```

Open a waveform from a run directory:

```bash
python3 -m dutpilot.cli wave dutpilot_runs/adder
```

Select a specific VCD file:

```bash
python3 -m dutpilot.cli wave dutpilot_runs/adder --file waves/wave.vcd
```

## Example: Adder

The passing example lives in `examples/adder/`:

```text
examples/adder/
  adder.v
  tb_adder.v
  dutpilot.yaml
```

The config is intentionally small:

```yaml
case: adder
dut: adder.v
tb: tb_adder.v
top: tb_adder
sim: icarus
```

The testbench writes `waves/wave.vcd`, prints `DUTPILOT_PASS` on success, and prints `DUTPILOT_FAIL` before terminating on a checked failure.

## Report Output

Each verification run creates:

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

The main report is:

```text
dutpilot_runs/<case>/reports/report.json
```

Important fields:

- `status`: `pass` or `fail`
- `stage`: `compile` or `simulate`
- `primary_error`: first actionable error or failure marker
- `next_action_hint`: suggested next debugging step
- `markers`: detected pass/fail marker lines
- `artifacts`: paths to logs, reports, simulation output, and waveform
- `return_codes`: compile and simulation return codes

## Waveform Viewing

If a testbench emits a VCD file into `waves/`, DUTPilot can launch GTKWave:

```bash
python3 -m dutpilot.cli wave dutpilot_runs/adder
```

The `verify` command never opens GUI tools automatically, so it remains suitable for CI and agent workflows.

## Use With Codex

Ask Codex to use the repo skill:

```text
Use the DUTPilot skill to run examples/buggy_counter/dutpilot.yaml, read report.json, explain the failure, fix the RTL, and rerun until the report passes.
```

Codex should:

1. Read `.agents/skills/dutpilot/SKILL.md`.
2. Prefer an existing `dutpilot.yaml`.
3. Run `python -m dutpilot.cli verify <config>`.
4. Read `<run_dir>/reports/report.json`.
5. Decide from `status`, `stage`, `primary_error`, and `next_action_hint`.
6. Avoid calling a passing simulation formal verification.

See `docs/agent-demo.md` and `docs/failure-repair-demo.md`.

## Roadmap

- Improve this repository as a skill authoring reference.
- Add more failure/repair examples.
- Document additional agent contract patterns.
- Keep the RTL simulator backend intentionally small.

Non-goals for this reference project include adding Verilator, ModelSim, or broad HDL project management features.

## License

DUTPilot is released under the MIT License. See `LICENSE` for details.
