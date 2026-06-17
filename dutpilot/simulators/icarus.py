"""Icarus Verilog backend."""

from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import stat
import subprocess
import tarfile
import tempfile
import urllib.request

from ..config import VerifyConfig
from ..project import ProjectLayout
from .base import CommandResult


class IcarusSimulator:
    name = "icarus"
    oss_cad_cache = Path.home() / ".cache" / "dutpilot" / "oss-cad-suite"

    def __init__(self, config: VerifyConfig, layout: ProjectLayout):
        self.config = config
        self.layout = layout

    @property
    def compile_command(self) -> str:
        return (
            f"iverilog -g2012 -s {self.config.top} -o build/sim.out "
            f"src/{self.layout.dut_path.name} tb/{self.layout.tb_path.name}"
        )

    @property
    def run_command(self) -> str:
        return "vvp build/sim.out"

    def ensure_installed(self) -> None:
        if shutil.which("iverilog") and shutil.which("vvp"):
            return
        if self._activate_cached_oss_cad_suite():
            return
        self._install_icarus()
        if not (shutil.which("iverilog") and shutil.which("vvp")):
            raise RuntimeError("iverilog/vvp are not available after installation attempt.")

    def _install_icarus(self) -> None:
        apt_error: Exception | None = None
        apt_get = shutil.which("apt-get")
        if apt_get:
            prefix: list[str] = []
            if hasattr(os, "geteuid") and os.geteuid() != 0:
                sudo = shutil.which("sudo")
                if sudo:
                    prefix = [sudo, "-n"]
            try:
                update_cmd = prefix + [apt_get, "update"]
                install_cmd = prefix + [apt_get, "install", "-y", "iverilog"]
                subprocess.run(update_cmd, check=True)
                subprocess.run(install_cmd, check=True)
                return
            except (OSError, subprocess.CalledProcessError) as exc:
                apt_error = exc

        try:
            self._install_oss_cad_suite()
        except Exception as exc:
            if apt_error is not None:
                raise RuntimeError(
                    "Automatic apt-get install failed, and user-space OSS CAD Suite install also failed: "
                    f"{exc}"
                ) from apt_error
            raise

    def _activate_cached_oss_cad_suite(self) -> bool:
        bin_dir = self.oss_cad_cache / "bin"
        if (bin_dir / "iverilog").exists() and (bin_dir / "vvp").exists():
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}" + os.environ.get("PATH", "")
            return True
        return False

    def _install_oss_cad_suite(self) -> None:
        asset = self._latest_oss_cad_asset()
        archive_name = asset["name"]
        url = asset["browser_download_url"]
        cache_root = self.oss_cad_cache.parent
        cache_root.mkdir(parents=True, exist_ok=True)
        archive_path = cache_root / archive_name

        if not archive_path.exists():
            with urllib.request.urlopen(url, timeout=60) as response:
                with archive_path.open("wb") as output:
                    shutil.copyfileobj(response, output)

        with tempfile.TemporaryDirectory(dir=cache_root) as tmp:
            tmp_path = Path(tmp)
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(tmp_path, filter="data")
            extracted = tmp_path / "oss-cad-suite"
            if not extracted.exists():
                candidates = [path for path in tmp_path.iterdir() if path.is_dir()]
                if not candidates:
                    raise RuntimeError("OSS CAD Suite archive did not contain an install directory.")
                extracted = candidates[0]
            if self.oss_cad_cache.exists():
                shutil.rmtree(self.oss_cad_cache)
            shutil.move(str(extracted), self.oss_cad_cache)

        if not self._activate_cached_oss_cad_suite():
            raise RuntimeError("OSS CAD Suite installed, but iverilog/vvp were not found in its bin directory.")

    @staticmethod
    def _latest_oss_cad_asset() -> dict[str, str]:
        api_url = "https://api.github.com/repos/YosysHQ/oss-cad-suite-build/releases/latest"
        request = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            release = json.loads(response.read().decode("utf-8"))
        for asset in release.get("assets", []):
            name = asset.get("name", "")
            if name.startswith("oss-cad-suite-linux-x64-") and name.endswith(".tgz"):
                return {"name": name, "browser_download_url": asset["browser_download_url"]}
        raise RuntimeError("Could not find a linux-x64 OSS CAD Suite asset in the latest release.")

    def write_scripts(self) -> None:
        self._write_script(self.layout.scripts_dir / "compile_icarus.sh", self.compile_command)
        self._write_script(self.layout.scripts_dir / "run_icarus.sh", self.run_command)

    @staticmethod
    def _write_script(path: Path, command: str) -> None:
        content = "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/..\"\n" + command + "\n"
        path.write_text(content, encoding="utf-8")
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def compile(self) -> CommandResult:
        return self._run_script("compile_icarus.sh", self.layout.logs_dir / "compile.log")

    def simulate(self) -> CommandResult:
        return self._run_script("run_icarus.sh", self.layout.logs_dir / "simulate.log")

    def _run_script(self, script_name: str, log_path: Path) -> CommandResult:
        result = subprocess.run(
            ["bash", f"scripts/{script_name}"],
            cwd=self.layout.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
        return CommandResult(result.returncode, result.stdout, result.stderr)
