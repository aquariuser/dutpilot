import tempfile
from pathlib import Path
import unittest

from dutpilot.config import VerifyConfig
from dutpilot.project import create_project


class ProjectTest(unittest.TestCase):
    def test_create_project_copies_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dut = root / "adder.v"
            tb = root / "tb_adder.v"
            dut.write_text("module adder; endmodule\n", encoding="utf-8")
            tb.write_text("module tb_adder; endmodule\n", encoding="utf-8")

            config = VerifyConfig(dut=dut, tb=tb, top="tb_adder", case="case1")
            layout = create_project(config, root / "runs")

            self.assertTrue((layout.src_dir / "adder.v").exists())
            self.assertTrue((layout.tb_dir / "tb_adder.v").exists())
            self.assertTrue(layout.build_dir.exists())
            self.assertTrue(layout.logs_dir.exists())
            self.assertTrue(layout.reports_dir.exists())
            self.assertTrue(layout.scripts_dir.exists())
            self.assertTrue(layout.waves_dir.exists())


if __name__ == "__main__":
    unittest.main()
