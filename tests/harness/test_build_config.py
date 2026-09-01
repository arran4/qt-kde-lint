from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from build_config import RuleError, build_config, load_rules  # noqa: E402


class BuildConfigTests(unittest.TestCase):
    def write_rule(self, directory: Path, name: str, **overrides: object) -> Path:
        rule = {
            "Name": name,
            "Query": 'match functionDecl().bind("problem")',
            "Diagnostic": [
                {
                    "BindName": "problem",
                    "Message": "example diagnostic",
                    "Level": "Warning",
                }
            ],
        }
        rule.update(overrides)
        path = directory / f"{name}.json"
        path.write_text(json.dumps(rule), encoding="utf-8")
        return path

    def test_builds_custom_check_glob(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            self.write_rule(directory, "qt-kde-lint-example")
            rules = load_rules(directory.glob("*.json"))
            config = build_config(rules)
            self.assertEqual(config["Checks"], "-*,custom-qt-kde-lint-*")
            self.assertEqual(config["CustomChecks"][0]["Name"], "qt-kde-lint-example")

    def test_requires_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            name = "qt-kde-lint-example"
            self.write_rule(
                directory,
                name,
                Diagnostic=[
                    {
                        "BindName": "problem",
                        "Message": "only a note",
                        "Level": "Note",
                    }
                ],
            )
            with self.assertRaisesRegex(RuleError, "at least one diagnostic"):
                load_rules(directory.glob("*.json"))

    def test_requires_filename_to_match_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            path = self.write_rule(directory, "qt-kde-lint-example")
            path.rename(directory / "wrong-name.json")
            with self.assertRaisesRegex(RuleError, "filename must match"):
                load_rules(directory.glob("*.json"))


if __name__ == "__main__":
    unittest.main()
