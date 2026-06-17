# Build Your Own Agent Skill

DUTPilot is a concrete example of a general pattern: wrap a local domain tool so an agent can call it reliably, inspect structured output, and choose the next action.

## The Pattern

1. Pick a narrow local tool.
2. Define stable inputs.
3. Provide one non-interactive command.
4. Write artifacts to a predictable directory.
5. Emit a machine-readable report.
6. Teach the agent decision rules in `SKILL.md`.
7. Include passing and failing examples.

## 1. Pick a Narrow Tool

The tool should do one thing well. DUTPilot runs a DUT and self-checking testbench. Other good candidates:

- Schema validators.
- Project migration checkers.
- Hardware lint wrappers.
- Internal build/test runners.
- Data quality checks.
- Static analysis tools.

Avoid making the skill depend on open-ended human interaction.

## 2. Define Inputs

Use a small config file when possible:

```yaml
case: my_case
input: path/to/input
mode: strict
```

Document required fields, relative path behavior, defaults, and unsupported cases.

## 3. Define Commands

Give the agent a canonical command:

```bash
python -m mytool.cli verify path/to/config.yaml
```

The command should:

- Be deterministic enough for automation.
- Return non-zero on failure.
- Avoid GUI launch or prompts.
- Write logs and reports before exiting.

## 4. Define Outputs

Prefer a run directory:

```text
tool_runs/<case>/
  logs/
  reports/
  artifacts/
```

Always include a structured report:

```json
{
  "status": "fail",
  "stage": "check",
  "primary_error": "expected X, got Y",
  "next_action_hint": "Inspect input normalization."
}
```

The report lets the agent make decisions without scraping arbitrary terminal output.

## 5. Write Decision Rules

In the skill, tell the agent exactly how to react:

- What status values mean.
- Which log to inspect for each stage.
- Which errors are actionable.
- When to edit files.
- When to stop and ask the user.
- What claims are not allowed.

DUTPilot explicitly forbids calling simulation results formal verification. Your skill should include similar domain-specific guardrails.

## 6. Include Examples

Include at least:

- One passing example.
- One failing example with a clear repair path.
- A sample prompt.
- A sample report interpretation.

Examples convert the skill from documentation into an executable pattern.

## DUTPilot Mapping

DUTPilot implements the pattern as:

- Skill: `.agents/skills/dutpilot/SKILL.md`
- Tool command: `python -m dutpilot.cli verify <config>`
- Config: `dutpilot.yaml`
- Run directory: `dutpilot_runs/<case>/`
- Report: `reports/report.json`
- Passing example: `examples/adder/`
- Failing example: `examples/buggy_counter/`

Use this structure as a template for other local tools.
