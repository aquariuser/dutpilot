# DUTPilot Agent Contract

DUTPilot defines a small, explicit contract between an agent and a local domain tool. The tool performs execution. The agent decides what to do next from structured output.

## Input Contract

Preferred input is a `dutpilot.yaml` next to the DUT and testbench:

```yaml
case: adder
dut: adder.v
tb: tb_adder.v
top: tb_adder
sim: icarus
```

Fields:

- `case`: run name and `dutpilot_runs/<case>` directory name.
- `dut`: path to the design under test, relative to the config file unless absolute.
- `tb`: path to the self-checking testbench, relative to the config file unless absolute.
- `top`: top-level testbench module passed to `iverilog -s`.
- `sim`: simulator backend. v0.1 supports `icarus`.

The testbench owns stimulus and checking. It should print exactly one success marker on pass:

```text
DUTPILOT_PASS
```

On a checked failure, it should print:

```text
DUTPILOT_FAIL: <reason>
```

Then terminate with `$fatal` or `$finish`.

## Command Contract

The agent should prefer an existing config:

```bash
python -m dutpilot.cli verify path/to/dutpilot.yaml
```

When no config exists:

```bash
python -m dutpilot.cli verify \
  --dut path/to/dut.v \
  --tb path/to/tb.v \
  --top tb_top \
  --sim icarus \
  --case case_name
```

The command must be non-interactive. It should write artifacts and exit with:

- `0` when the parsed report status is `pass`.
- non-zero when the parsed report status is `fail`.

The command must not open GUI tools. Waveform viewing is a separate explicit command:

```bash
python -m dutpilot.cli wave dutpilot_runs/<case>
```

## Output Report Contract

The agent must read:

```text
dutpilot_runs/<case>/reports/report.json
```

Required fields:

- `schema_version`: report schema version.
- `case`: run case.
- `simulator`: backend name.
- `status`: `pass` or `fail`.
- `stage`: decisive stage, usually `compile` or `simulate`.
- `primary_error`: first actionable failure or `null`.
- `next_action_hint`: short recommended next step.
- `top`: testbench top module.
- `commands`: compile and simulation commands.
- `artifacts`: generated files and run directory.
- `markers`: detected `DUTPILOT_PASS` and `DUTPILOT_FAIL` lines.
- `errors`: simulator error, fatal, or syntax diagnostics.
- `warnings`: parsed warnings.
- `return_codes`: compile and simulation process return codes.

The report is the source of truth for agent decisions. Raw logs are supporting evidence.

## Agent Decision Rules

- If `status == "pass"`, report that the supplied simulation testbench passed.
- Never describe a pass as formal verification, proof, exhaustive verification, or complete RTL correctness.
- If `stage == "compile"`, inspect `artifacts.compile_log` first.
- If `stage == "simulate"` and `primary_error` contains `DUTPILOT_FAIL`, debug the named behavior.
- If return codes are zero but no `DUTPILOT_PASS` marker exists, treat the run as failed.
- If a waveform exists, use it only when needed or requested.
- After any RTL/testbench edit, rerun the same command and reread `report.json`.
- Final answers should include `status`, `stage`, and the relevant failure or pass evidence.
