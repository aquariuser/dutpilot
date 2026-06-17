"""Waveform discovery and GTKWave launching."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


class WaveError(RuntimeError):
    pass


def resolve_wave_file(run_dir: str | Path, file: str | Path | None = None) -> Path:
    run_path = Path(run_dir)
    waves_dir = run_path / "waves"

    if file is not None:
        file_path = Path(file)
        if not file_path.is_absolute():
            file_path = run_path / file_path
        if not file_path.exists():
            raise WaveError(f"VCD waveform not found: {file_path}")
        if file_path.suffix.lower() != ".vcd":
            raise WaveError(f"Waveform file must be a .vcd file: {file_path}")
        return file_path

    if not waves_dir.exists():
        raise WaveError(f"No VCD waveform found under {waves_dir}")

    vc_files = sorted(path for path in waves_dir.rglob("*.vcd") if path.is_file())
    if not vc_files:
        raise WaveError(f"No VCD waveform found under {waves_dir}")
    if len(vc_files) > 1:
        listed = "\n".join(f"  {path}" for path in vc_files)
        raise WaveError(
            "Multiple VCD waveforms found. Please specify one with --file:\n" + listed
        )
    return vc_files[0]


def open_wave(run_dir: str | Path, file: str | Path | None = None) -> Path:
    vcd_file = resolve_wave_file(run_dir, file)
    gtkwave = shutil.which("gtkwave")
    if not gtkwave:
        raise WaveError("GTKWave not found. Please install GTKWave or open the VCD manually.")
    subprocess.Popen([gtkwave, str(vcd_file)])
    return vcd_file
