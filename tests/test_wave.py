import tempfile
from pathlib import Path
import unittest

from dutpilot.wave import WaveError, resolve_wave_file


class WaveTest(unittest.TestCase):
    def test_no_vcd_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(WaveError, "No VCD waveform found"):
                resolve_wave_file(tmp)

    def test_single_vcd(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            waves = run_dir / "waves"
            waves.mkdir()
            wave = waves / "wave.vcd"
            wave.write_text("$date\n$end\n", encoding="utf-8")
            self.assertEqual(resolve_wave_file(run_dir), wave)

    def test_multiple_vcd_requires_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            waves = run_dir / "waves"
            waves.mkdir()
            (waves / "a.vcd").write_text("", encoding="utf-8")
            (waves / "b.vcd").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(WaveError, "Multiple VCD waveforms found"):
                resolve_wave_file(run_dir)

    def test_explicit_relative_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp)
            waves = run_dir / "waves"
            waves.mkdir()
            wave = waves / "wave.vcd"
            wave.write_text("", encoding="utf-8")
            self.assertEqual(resolve_wave_file(run_dir, "waves/wave.vcd"), wave)


if __name__ == "__main__":
    unittest.main()
