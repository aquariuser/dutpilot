# AGENTS.md

## RTL Simulation Verification Rule

For any task involving Verilog/SystemVerilog RTL implementation, simulation, verification, debugging, or testbench creation, use the repo-scoped `dutpilot` workflow.

Before writing a testbench, follow the DUTPilot self-checking testbench contract. A DUTPilot-compatible testbench must:

- Compare DUT outputs against expected behavior.
- Print `DUTPILOT_FAIL: <reason>` on mismatch.
- Print `DUTPILOT_PASS` only after all checks pass.
- Call `$finish`.
- Preferably dump `waves/wave.vcd`.

Do not treat a stimulus-only testbench as DUTPilot verification. Do not claim the RTL is `fully verified` or `formally verified`. Only say it `passed the provided DUTPilot/Icarus testbench`.

## DUTPilot Verification Workflow

Use the repo-scoped `dutpilot` skill for Verilog/SystemVerilog RTL simulation verification tasks.

Preferred flow:

1. Use `python`.
2. Prefer an existing `dutpilot.yaml`.
3. Run:

```bash
python -m dutpilot.cli verify path/to/dutpilot.yaml
```

4. Read `<run_dir>/reports/report.json`.
5. Decide next steps from `status`, `stage`, `primary_error`, and `next_action_hint`.
6. Do not characterize DUTPilot results as formal verification; they are simulation results from the provided testbench.

For adder example validation:

```bash
python -m dutpilot.cli verify examples/adder/dutpilot.yaml
```
