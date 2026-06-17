"""End-to-end verification orchestration."""

from __future__ import annotations

from pathlib import Path

from .config import VerifyConfig
from .log_parser import parse_logs
from .project import create_project
from .report import build_report, write_report, write_summary
from .simulators.icarus import IcarusSimulator


def _primary_error(errors: list[str], markers: dict[str, list[str]], status: str) -> str | None:
    if markers.get("fail"):
        return markers["fail"][0]
    if errors:
        return errors[0]
    if status == "fail":
        return "Simulation did not produce DUTPILOT_PASS."
    return None


def _next_action_hint(status: str, stage: str, primary_error: str | None) -> str:
    if status == "pass":
        return "Review report artifacts and waveform if needed."
    if stage == "compile":
        return "Inspect compile.log and fix RTL/testbench syntax, missing modules, or compile options."
    if primary_error and "DUTPILOT_FAIL" in primary_error:
        return "Inspect the testbench failure marker and compare expected versus observed DUT behavior."
    return "Inspect simulate.log, transcript.log, and waves/wave.vcd if available."


def verify(config: VerifyConfig) -> tuple[int, dict]:
    if config.sim != "icarus":
        raise ValueError("First-stage MVP only supports --sim icarus.")

    layout = create_project(config)
    simulator = IcarusSimulator(config, layout)
    simulator.ensure_installed()
    simulator.write_scripts()

    compile_result = simulator.compile()
    simulate_result = None
    stage = "compile"

    if compile_result.returncode == 0:
        stage = "simulate"
        simulate_result = simulator.simulate()

    compile_log = (layout.logs_dir / "compile.log").read_text(encoding="utf-8")
    simulate_log = ""
    if simulate_result is not None:
        simulate_log = (layout.logs_dir / "simulate.log").read_text(encoding="utf-8")
    transcript = compile_log + simulate_log
    (layout.logs_dir / "transcript.log").write_text(transcript, encoding="utf-8")

    parsed = parse_logs(compile_log, simulate_log)
    simulate_rc = simulate_result.returncode if simulate_result is not None else None
    if compile_result.returncode != 0:
        status = "fail"
        stage = "compile"
    elif simulate_rc != 0:
        status = "fail"
        stage = "simulate"
    elif parsed.markers["fail"]:
        status = "fail"
        stage = "simulate"
    elif parsed.markers["pass"] and not parsed.errors:
        status = "pass"
        stage = "simulate"
    else:
        status = "fail"
        stage = "simulate"

    primary_error = _primary_error(parsed.errors, parsed.markers, status)
    report = build_report(
        case=config.case or config.top,
        simulator=simulator.name,
        status=status,
        stage=stage,
        primary_error=primary_error,
        next_action_hint=_next_action_hint(status, stage, primary_error),
        top=config.top,
        commands={"compile": simulator.compile_command, "simulate": simulator.run_command},
        artifacts={
            "run_dir": str(layout.root),
            "compile_log": str(Path("logs") / "compile.log"),
            "simulate_log": str(Path("logs") / "simulate.log"),
            "transcript_log": str(Path("logs") / "transcript.log"),
            "report_json": str(Path("reports") / "report.json"),
            "summary_md": str(Path("reports") / "summary.md"),
            "sim_out": str(Path("build") / "sim.out"),
            "wave": str(layout.root / "waves" / "wave.vcd"),
        },
        markers=parsed.markers,
        errors=parsed.errors,
        warnings=parsed.warnings,
        return_codes={"compile": compile_result.returncode, "simulate": simulate_rc},
    )
    write_report(report, layout.reports_dir)
    write_summary(report, layout.reports_dir)
    return (0 if status == "pass" else 1), report
