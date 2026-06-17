# DUTPilot Testbench Contract

DUTPilot does not generate or repair a complete testbench. The testbench is responsible for applying stimulus, checking outputs, and producing explicit result markers.

## Required Markers

- On success, print `DUTPILOT_PASS`.
- On failure, print `DUTPILOT_FAIL: <reason>` and then call `$fatal` or `$finish`.

The log parser treats these markers as the primary test intent. Simulator syntax errors, runtime fatal messages, and non-zero return codes still make the run fail.

## Waveforms

For VCD output, write under the run directory `waves/` path. The standard filename is:

```verilog
$dumpfile("waves/wave.vcd");
$dumpvars(0, <tb_top>);
```

DUTPilot does not automatically inject waveform dumping into arbitrary user testbenches. If no VCD is produced, `python -m dutpilot.cli wave <run_dir>` should report that no waveform was found.

## Scope

Treat DUTPilot results as simulation evidence only. Do not claim formal proof, exhaustive verification, UVM compliance, or complete RTL correctness from a passing run.
