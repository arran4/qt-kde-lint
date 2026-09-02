from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))


class TestRulesTests(unittest.TestCase):
    def test_missing_fixture_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)
            rules_dir = temp_dir / "rules"
            rules_dir.mkdir()
            tests_dir = temp_dir / "tests"
            tests_dir.mkdir()

            rule_path = rules_dir / "qt-kde-lint-example.json"
            rule_path.write_text('{"Name": "qt-kde-lint-example", "Query": "match anything()", "Diagnostic": [{"BindName": "p", "Level": "Warning", "Message": "m"}]}')

            # Directory does not even have any cpp files.
            rule_test_dir = tests_dir / "qt-kde-lint-example"
            rule_test_dir.mkdir()

            result = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "test_rules.py"), "--rules-dir", str(rules_dir), "--tests-dir", str(tests_dir)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing tests/qt-kde-lint-example/bad*.cpp fixture", result.stdout)
            self.assertIn("missing tests/qt-kde-lint-example/good*.cpp fixture", result.stdout)


if __name__ == "__main__":
    unittest.main()
