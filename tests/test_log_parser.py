import unittest

from dutpilot.log_parser import parse_logs


class LogParserTest(unittest.TestCase):
    def test_pass_and_warning_markers(self):
        parsed = parse_logs("warning: minor\nDUTPILOT_PASS\n")
        self.assertEqual(parsed.markers["pass"], ["DUTPILOT_PASS"])
        self.assertEqual(parsed.markers["fail"], [])
        self.assertEqual(parsed.errors, [])
        self.assertEqual(parsed.warnings, ["warning: minor"])

    def test_fail_and_errors(self):
        parsed = parse_logs("DUTPILOT_FAIL: bad sum\nsyntax error\nFatal: stop\n")
        self.assertEqual(parsed.markers["fail"], ["DUTPILOT_FAIL: bad sum"])
        self.assertEqual(len(parsed.errors), 2)


if __name__ == "__main__":
    unittest.main()
