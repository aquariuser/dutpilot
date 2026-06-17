"""Configuration loading for DUTPilot verification runs."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VerifyConfig:
    dut: Path
    tb: Path
    top: str
    sim: str = "icarus"
    case: str | None = None

    def normalized(self, base_dir: Path | None = None) -> "VerifyConfig":
        base = base_dir or Path.cwd()
        dut = self.dut if self.dut.is_absolute() else (base / self.dut)
        tb = self.tb if self.tb.is_absolute() else (base / self.tb)
        case = self.case or self.top
        return VerifyConfig(
            dut=dut.resolve(),
            tb=tb.resolve(),
            top=self.top,
            sim=self.sim,
            case=case,
        )


def load_config(path: str | Path) -> VerifyConfig:
    config_path = Path(path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    if config_path.suffix.lower() == ".json":
        data = json.loads(config_path.read_text(encoding="utf-8"))
    elif config_path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError as exc:
            data = _load_simple_yaml(config_path.read_text(encoding="utf-8"))
            if data is None:
                raise RuntimeError(
                    "YAML config support requires PyYAML for non-trivial YAML. "
                    "Install it or use CLI arguments/JSON config."
                ) from exc
        else:
            data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported config format: {config_path.suffix}")

    if not isinstance(data, dict):
        raise ValueError("Config file must contain a mapping/object.")

    cfg = config_from_mapping(data)
    return cfg.normalized(config_path.parent)


def config_from_mapping(data: dict[str, Any]) -> VerifyConfig:
    missing = [key for key in ("dut", "tb", "top") if not data.get(key)]
    if missing:
        raise ValueError(f"Missing required config field(s): {', '.join(missing)}")
    return VerifyConfig(
        dut=Path(str(data["dut"])),
        tb=Path(str(data["tb"])),
        top=str(data["top"]),
        sim=str(data.get("sim", "icarus")),
        case=str(data["case"]) if data.get("case") else None,
    )


def config_from_cli(dut: str, tb: str, top: str, sim: str, case: str | None = None) -> VerifyConfig:
    return VerifyConfig(dut=Path(dut), tb=Path(tb), top=top, sim=sim, case=case).normalized()


def _load_simple_yaml(text: str) -> dict[str, str] | None:
    data: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            return None
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if not key or not value or any(token in value for token in ("[", "{", "&", "*")):
            return None
        data[key] = value
    return data
