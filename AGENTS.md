# AGENTS.md

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
