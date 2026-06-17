# DUTPilot

DUTPilot is a CLI-first, agent-friendly RTL simulation harness for running a DUT with a testbench and producing structured artifacts for debugging.

It is currently a simulation wrapper, not a formal verification tool. v0.1 supports an Icarus Verilog backend for Verilog/SystemVerilog testbenches.

## Features

- Run a DUT and testbench from a small YAML or JSON config.
- Stage each run into a standard `dutpilot_runs/<case>/` directory.
- Compile with `iverilog` and simulate with `vvp`.
- Capture `compile.log`, `simulate.log`, and `transcript.log`.
- Parse `DUTPILOT_PASS` and `DUTPILOT_FAIL` markers from testbench output.
- Generate machine-readable `report.json` and human-readable `summary.md`.
- Preserve VCD waveforms under `waves/` for optional inspection.
- Provide agent-friendly next-step hints through `primary_error` and `next_action_hint`.

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/<your-org>/dutpilot.git
cd dutpilot
python3 -m pip install -e .
```

DUTPilot also needs an RTL simulator. For the current Icarus backend, install:

```bash
sudo apt-get update
sudo apt-get install -y iverilog gtkwave
```

`gtkwave` is optional and is only needed for waveform viewing.

## Quick Start

Run the bundled adder example:

```bash
python3 -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

Expected output:

```text
DUTPilot PASS case=adder report=dutpilot_runs/adder/reports/report.json
```

The run artifacts are written under:

```text
dutpilot_runs/adder/
```

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

## Example: adder

The adder example lives in `examples/adder/`:

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

Each verification run creates a standard directory:

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

The main structured report is:

```text
dutpilot_runs/<case>/reports/report.json
```

Important fields include:

- `status`: `pass` or `fail`
- `stage`: `compile` or `simulate`
- `primary_error`: first actionable error or failure marker
- `next_action_hint`: suggested next debugging step
- `markers`: detected `DUTPILOT_PASS` and `DUTPILOT_FAIL` lines
- `artifacts`: relative paths to logs, report files, simulation output, and waveform
- `return_codes`: compile and simulation process return codes

`summary.md` provides a compact human-readable version of the same result.

## Waveform Viewing

If a testbench emits a VCD file into the run directory's `waves/` folder, DUTPilot can launch GTKWave:

```bash
python3 -m dutpilot.cli wave dutpilot_runs/adder
```

The `verify` command never opens GUI tools automatically, so it remains suitable for CI and agent workflows.

## Use With Codex

This repository includes a repo-scoped Codex skill at:

```text
.agents/skills/dutpilot/SKILL.md
```

Codex agents should prefer existing `dutpilot.yaml` files and follow this flow:

```bash
python -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

After a run, inspect:

```text
dutpilot_runs/<case>/reports/report.json
```

Use `status`, `stage`, `primary_error`, and `next_action_hint` to decide the next debugging step. Do not describe DUTPilot results as formal verification; they are simulation results from the supplied testbench.

## Roadmap

- Support multiple DUT/source files and include directories.
- Add compile defines and backend-specific options.
- Add more simulator backends.
- Improve JSON schema documentation and validation.
- Add CI examples for common RTL projects.
- Add richer waveform and artifact discovery.

## License

DUTPilot is released under the MIT License. See `LICENSE` for details.
