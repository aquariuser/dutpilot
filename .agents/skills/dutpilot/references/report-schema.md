# DUTPilot Report Schema

Reports are written to:

```text
<run_dir>/reports/report.json
```

## Core Fields

- `schema_version`: report schema version.
- `case`: run case name.
- `simulator`: backend name, currently `icarus`.
- `status`: `pass` or `fail`.
- `stage`: latest decisive stage, usually `compile` or `simulate`.
- `primary_error`: first actionable error or failure marker, or `null` on pass.
- `next_action_hint`: short suggested next action.
- `top`: top testbench module.
- `commands`: compile and simulate commands.
- `artifacts`: generated files, including logs, report, summary, binary, and optional `wave`.
- `markers`: parsed `DUTPILOT_PASS` and `DUTPILOT_FAIL` lines.
- `errors`: parsed simulator error/fatal/syntax lines.
- `warnings`: parsed warnings.
- `return_codes`: compile and simulate process return codes.

## Decision Guidance

- If `status == "pass"`, the simulation testbench passed. Mention the scope of the testbench; do not call it formal verification.
- If `stage == "compile"`, inspect `logs/compile.log` first.
- If `stage == "simulate"` and `primary_error` contains `DUTPILOT_FAIL`, debug the testbench assertion or DUT behavior named in the failure reason.
- If `stage == "simulate"` with no failure marker, inspect `logs/simulate.log`, `logs/transcript.log`, and `artifacts.wave` if present.
- Use `next_action_hint` as the concise next-step summary unless local evidence points to a more specific fix.
