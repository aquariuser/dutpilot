# DUTPilot

DUTPilot is a reference implementation of an agent-callable local skill. It uses RTL simulation as a concrete example to show how AI agents can call deterministic local tools, read structured reports, and iterate based on real execution results.

The current v0.1 tool can run a Verilog/SystemVerilog DUT with a self-checking testbench through Icarus Verilog, generate a standard run directory, and write logs, `wave.vcd`, `report.json`, and `summary.md`. That RTL flow is the example domain. The main point of the repository is the reusable agent skill pattern.

## What Is DUTPilot?

DUTPilot is not just an FPGA or RTL utility. It is a compact reference project for packaging a vertical-domain local workflow as:

- A deterministic CLI tool.
- A repo-scoped Codex skill.
- A structured report contract.
- A failure-repair loop driven by real execution results.

RTL/Icarus simulation is the sample workflow because it is easy to demonstrate: a DUT either compiles and passes the provided self-checking testbench, or it produces concrete logs and failure markers for the agent to inspect.

DUTPilot does not prove complete RTL correctness. A passing run means the design passed the provided DUTPilot/Icarus testbench.

## Why This Project Exists

Large language models should not decide whether RTL is correct by guessing from source text alone. Local tools should perform the real execution. The agent should write code, run the tool, read the structured result, and iterate based on evidence.

DUTPilot demonstrates this closed loop:

```text
LLM + local deterministic tool + structured report
```

In this loop:

- The local tool compiles and simulates the design.
- The testbench checks expected behavior.
- `report.json` summarizes status, stage, errors, artifacts, and next actions.
- Codex reads the report and decides whether to explain, inspect logs, or repair code.

The same approach can apply to many domains: migration checkers, linters, internal validators, data quality tools, hardware flows, build systems, or any workflow where an agent should rely on execution instead of speculation.

## Agent-Callable Local Tool Pattern

DUTPilot follows a general pattern:

1. Define stable inputs.
2. Expose a CLI command.
3. Run deterministic local tools.
4. Emit a machine-readable report.
5. Let the agent decide the next step.

For DUTPilot, the mapping is:

- Stable input: `dutpilot.yaml` or explicit `--dut`, `--tb`, `--top`, `--sim`.
- CLI command: `python3 -m dutpilot.cli verify <dutpilot.yaml>`.
- Local tool: Icarus Verilog through `iverilog` and `vvp`.
- Report: `dutpilot_runs/<case>/reports/report.json`.
- Agent decision: inspect `status`, `stage`, `primary_error`, and `next_action_hint`.

## Quick Start

Run the passing adder example:

```bash
python3 -m dutpilot.cli verify examples/adder/dutpilot.yaml
```

Expected result:

```text
DUTPilot PASS case=adder report=dutpilot_runs/adder/reports/report.json
```

Inspect the report:

```bash
cat dutpilot_runs/adder/reports/report.json
```

## Use With Codex

The repo-scoped skill lives at:

```text
.agents/skills/dutpilot/SKILL.md
```

Example prompt:

```text
$dutpilot Verify examples/adder/dutpilot.yaml and summarize report.json.
```

Repair-loop prompt:

```text
$dutpilot Run examples/buggy_counter/dutpilot.yaml. Read report.json, identify the failing behavior, fix the RTL, and rerun until the provided DUTPilot/Icarus testbench passes.
```

Codex should:

1. Read the skill instructions.
2. Prefer an existing `dutpilot.yaml`.
3. Run DUTPilot.
4. Read `report.json`.
5. Decide from the real execution result.
6. Avoid saying the RTL is fully verified.

## report.json Contract

The main report is:

```text
dutpilot_runs/<case>/reports/report.json
```

Key fields:

- `status`: whether the run passed or failed. DUTPilot v0.1 emits `pass` or `fail`.
- `stage`: where the decisive result occurred. DUTPilot v0.1 uses `compile` or `simulate`.
- `primary_error`: first actionable error, failure marker, or `null`.
- `next_action_hint`: concise guidance for the agent's next step.

Supporting fields include `errors`, `warnings`, `markers`, `artifacts`, `commands`, and `return_codes`.

See `docs/agent-contract.md` for the full contract.

## Failure-Repair Loop

`examples/buggy_counter/` is intentionally wrong. The testbench expects a 4-bit counter to increment by one each cycle, while the DUT increments by two.

Run:

```bash
python3 -m dutpilot.cli verify examples/buggy_counter/dutpilot.yaml
```

The first run should fail during simulation and write a report under:

```text
dutpilot_runs/buggy_counter/reports/report.json
```

See `docs/failure-repair-demo.md` for the expected repair loop.

## Build Your Own Skill

DUTPilot is meant to be copied as a pattern:

- Put the local tool behind a stable CLI.
- Define an input contract.
- Emit a structured report.
- Write a skill that tells Codex when to run the tool and how to interpret the result.
- Include passing and failing examples.

See `docs/build-your-own-skill.md`.

## Installation

Clone and install in editable mode:

```bash
git clone git@github.com:aquariuser/dutpilot.git
cd dutpilot
python3 -m pip install -e .
```

Install the sample RTL backend dependencies:

```bash
sudo apt-get update
sudo apt-get install -y iverilog gtkwave
```

`gtkwave` is optional and only needed for waveform viewing.

## CLI Usage

Use a config:

```bash
python3 -m dutpilot.cli verify path/to/dutpilot.yaml
```

Or pass files directly:

```bash
python3 -m dutpilot.cli verify \
  --dut path/to/dut.v \
  --tb path/to/tb.v \
  --top tb_top \
  --sim icarus
```

Open an existing VCD when requested:

```bash
python3 -m dutpilot.cli wave dutpilot_runs/adder
```

## Roadmap

Future directions could include:

- Additional examples of agent-callable local tools.
- More skill templates and contract patterns.
- Optional Verilator or ModelSim backends.
- MCP integration for richer tool discovery.
- More detailed report schemas.

These are future possibilities, not current v0.1 features.

## License

DUTPilot is released under the MIT License. See `LICENSE`.
