"""Run directory creation and input staging."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil

from .config import VerifyConfig


@dataclass(frozen=True)
class ProjectLayout:
    root: Path
    src_dir: Path
    tb_dir: Path
    build_dir: Path
    logs_dir: Path
    reports_dir: Path
    scripts_dir: Path
    waves_dir: Path
    dut_path: Path
    tb_path: Path


def create_project(config: VerifyConfig, runs_root: str | Path = "dutpilot_runs") -> ProjectLayout:
    if not config.dut.exists():
        raise FileNotFoundError(f"DUT file not found: {config.dut}")
    if not config.tb.exists():
        raise FileNotFoundError(f"Testbench file not found: {config.tb}")

    case = config.case or config.top
    root = Path(runs_root) / case
    layout = ProjectLayout(
        root=root,
        src_dir=root / "src",
        tb_dir=root / "tb",
        build_dir=root / "build",
        logs_dir=root / "logs",
        reports_dir=root / "reports",
        scripts_dir=root / "scripts",
        waves_dir=root / "waves",
        dut_path=root / "src" / config.dut.name,
        tb_path=root / "tb" / config.tb.name,
    )

    for directory in (
        layout.src_dir,
        layout.tb_dir,
        layout.build_dir,
        layout.logs_dir,
        layout.reports_dir,
        layout.scripts_dir,
        layout.waves_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    shutil.copy2(config.dut, layout.dut_path)
    shutil.copy2(config.tb, layout.tb_path)
    return layout
