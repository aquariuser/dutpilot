"""Report construction and serialization."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any


SCHEMA_VERSION = "0.1.1"


def build_report(
    *,
    case: str,
    simulator: str,
    status: str,
    stage: str,
    top: str,
    commands: dict[str, str],
    artifacts: dict[str, str],
    markers: dict[str, list[str]],
    errors: list[str],
    warnings: list[str],
    return_codes: dict[str, int | None],
    primary_error: str | None = None,
    next_action_hint: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "case": case,
        "simulator": simulator,
        "status": status,
        "stage": stage,
        "primary_error": primary_error,
        "next_action_hint": next_action_hint,
        "top": top,
        "commands": commands,
        "artifacts": artifacts,
        "markers": markers,
        "errors": errors,
        "warnings": warnings,
        "return_codes": return_codes,
    }


def write_report(report: dict[str, Any], reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / "report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_summary(report: dict[str, Any], reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / "summary.md"
    lines = [
        f"# DUTPilot Summary: {report['case']}",
        "",
        f"- Status: {report['status']}",
        f"- Stage: {report['stage']}",
        f"- Simulator: {report['simulator']}",
        f"- Top: {report['top']}",
        "",
        "## Markers",
        f"- DUTPILOT_PASS: {len(report['markers'].get('pass', []))}",
        f"- DUTPILOT_FAIL: {len(report['markers'].get('fail', []))}",
        "",
        "## Diagnostics",
        f"- Errors: {len(report['errors'])}",
        f"- Warnings: {len(report['warnings'])}",
    ]
    if report["errors"]:
        lines.extend(["", "### Errors"])
        lines.extend(f"- {error}" for error in report["errors"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
