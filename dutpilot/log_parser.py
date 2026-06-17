"""Small parser for DUTPilot markers and simulator diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
import re


ERROR_RE = re.compile(r"\b(error|syntax error|fatal)\b", re.IGNORECASE)
WARNING_RE = re.compile(r"\bwarning\b", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedLog:
    markers: dict[str, list[str]]
    errors: list[str]
    warnings: list[str]


def parse_logs(*logs: str) -> ParsedLog:
    markers: dict[str, list[str]] = {"pass": [], "fail": []}
    errors: list[str] = []
    warnings: list[str] = []

    for log in logs:
        for raw_line in log.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if "DUTPILOT_PASS" in line:
                markers["pass"].append(line)
            if "DUTPILOT_FAIL" in line:
                markers["fail"].append(line)
            if ERROR_RE.search(line):
                errors.append(line)
            if WARNING_RE.search(line):
                warnings.append(line)

    return ParsedLog(markers=markers, errors=errors, warnings=warnings)
