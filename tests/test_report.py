import tempfile
from pathlib import Path
import unittest
import json

from dutpilot.report import build_report, write_report, write_summary


class ReportTest(unittest.TestCase):
    def test_report_contains_required_fields(self):
        report = build_report(
            case="adder",
            simulator="icarus",
            status="pass",
            stage="simulate",
            top="tb_adder",
            commands={"compile": "iverilog", "simulate": "vvp"},
            artifacts={"report_json": "reports/report.json", "wave": "dutpilot_runs/adder/waves/wave.vcd"},
            markers={"pass": ["DUTPILOT_PASS"], "fail": []},
            errors=[],
            warnings=[],
            return_codes={"compile": 0, "simulate": 0},
        )
        for key in (
            "schema_version",
            "case",
            "simulator",
            "status",
            "stage",
            "primary_error",
            "next_action_hint",
            "top",
            "commands",
            "artifacts",
            "markers",
            "errors",
            "warnings",
            "return_codes",
        ):
            self.assertIn(key, report)

    def test_write_report_and_summary(self):
        report = build_report(
            case="adder",
            simulator="icarus",
            status="pass",
            stage="simulate",
            top="tb_adder",
            commands={"compile": "iverilog", "simulate": "vvp"},
            artifacts={"report_json": "reports/report.json", "wave": "dutpilot_runs/adder/waves/wave.vcd"},
            markers={"pass": ["DUTPILOT_PASS"], "fail": []},
            errors=[],
            warnings=[],
            return_codes={"compile": 0, "simulate": 0},
        )
        with tempfile.TemporaryDirectory() as tmp:
            reports_dir = Path(tmp)
            report_path = write_report(report, reports_dir)
            summary_path = write_summary(report, reports_dir)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "pass")
            self.assertIn("DUTPilot Summary", summary_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
