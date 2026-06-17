# How To Turn A Local Tool Into An Agent Skill

DUTPilot is a concrete example of a general engineering pattern: package a repeatable local workflow so an agent can call it, inspect a structured result, and make bounded decisions.

## The General Pattern

1. Choose a repeatable local workflow.
2. Wrap it behind a CLI.
3. Define stable inputs.
4. Produce structured outputs.
5. Write `SKILL.md`.
6. Define agent decision rules.
7. Provide success and failure examples.

The goal is not to make the agent guess better. The goal is to make the agent use reliable local evidence.

## What DUTPilot Demonstrates

DUTPilot demonstrates:

- CLI: `python3 -m dutpilot.cli verify <config>`.
- `report.json`: stable machine-readable output.
- Testbench contract: explicit `DUTPILOT_PASS` and `DUTPILOT_FAIL` markers.
- Codex skill: `.agents/skills/dutpilot/SKILL.md`.
- Failure-repair loop: run, read report, edit, rerun.

The same structure can wrap non-RTL tools, such as data validators, security scanners, migration assistants, style checkers, code generators, or internal build tools.

## Generic Skill Template

```text
my-tool/
  mytool/
    __init__.py
    cli.py
  .agents/
    skills/
      mytool/
        SKILL.md
  docs/
    agent-contract.md
    agent-demo.md
  examples/
    passing_case/
    failing_case/
```

Recommended CLI shape:

```bash
python3 -m mytool.cli run path/to/config.yaml
```

Recommended report shape:

```json
{
  "status": "fail",
  "stage": "check",
  "primary_error": "expected X, got Y",
  "next_action_hint": "Inspect input normalization.",
  "artifacts": {
    "report_json": "reports/report.json",
    "transcript_log": "logs/transcript.log"
  }
}
```

## Skill Quality Checklist

- Clear trigger: the agent knows when to use the skill.
- Deterministic command: the main command is non-interactive and repeatable.
- Stable inputs: config fields and path rules are documented.
- Machine-readable output: the agent does not scrape arbitrary terminal text.
- Failure handling: status and stage map to concrete next actions.
- Safety limitations: the skill says what not to claim.
- Examples: include both success and failure cases.
- No exaggerated claims: report only what the local tool actually checked.

## Applying The Pattern

When adapting this structure to another field:

1. Start from the real local command users already trust.
2. Add a thin CLI wrapper if needed.
3. Standardize output directories.
4. Emit a JSON report with status, stage, primary error, artifacts, and hints.
5. Write a skill that forces the agent to read the report before acting.
6. Include a failure demo so the repair loop is obvious.

Keep the scope narrow. A high-quality skill is a reliable bridge between an agent and a local tool, not a replacement for the tool.
