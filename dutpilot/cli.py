"""DUTPilot command line interface."""

from __future__ import annotations

import argparse
import sys

from .config import config_from_cli, load_config
from .runner import verify
from .wave import open_wave


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dutpilot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_parser = subparsers.add_parser("verify", help="Run an RTL verification case.")
    verify_parser.add_argument("config", nargs="?", help="Path to dutpilot.yaml or JSON config.")
    verify_parser.add_argument("--dut", help="DUT Verilog/SystemVerilog file.")
    verify_parser.add_argument("--tb", help="Testbench file.")
    verify_parser.add_argument("--top", help="Testbench top module.")
    verify_parser.add_argument("--sim", default="icarus", help="Simulator backend. Default: icarus.")
    verify_parser.add_argument("--case", help="Run case name. Default: top module name.")

    wave_parser = subparsers.add_parser("wave", help="Open a run VCD waveform with GTKWave.")
    wave_parser.add_argument("run_dir", help="DUTPilot run directory.")
    wave_parser.add_argument("--file", help="VCD file path, absolute or relative to run_dir.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "verify":
            if args.config:
                config = load_config(args.config)
            else:
                missing = [name for name in ("dut", "tb", "top") if getattr(args, name) is None]
                if missing:
                    parser.error("verify requires either a config file or --dut --tb --top")
                config = config_from_cli(args.dut, args.tb, args.top, args.sim, args.case)
            code, report = verify(config)
            print(f"DUTPilot {report['status'].upper()} case={report['case']} report={report['artifacts']['run_dir']}/reports/report.json")
            return code
        if args.command == "wave":
            vcd_file = open_wave(args.run_dir, args.file)
            print(f"Opened waveform: {vcd_file}")
            return 0
    except Exception as exc:
        print(f"dutpilot: error: {exc}", file=sys.stderr)
        return 2

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
