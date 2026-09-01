#!/usr/bin/env python3
"""Run positive and negative regression fixtures for QML rules."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import the actual linter logic so we don't duplicate
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qml_linter import QML_RULES

def fixtures(directory: Path, prefix: str) -> list[Path]:
    return sorted(directory.glob(f"{prefix}*.qml"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests-dir", type=Path, default=Path("tests"))
    args = parser.parse_args()

    failures: list[str] = []
    tested_rules = 0

    for name, checker in QML_RULES.items():
        tested_rules += 1
        rule_tests = args.tests_dir / name

        bad = fixtures(rule_tests, "bad")
        good = fixtures(rule_tests, "good")

        if not bad:
            failures.append(f"{name}: missing tests/{name}/bad*.qml fixture")
        if not good:
            failures.append(f"{name}: missing tests/{name}/good*.qml fixture")

        if not bad or not good:
            continue

        for source in bad:
            content = source.read_text(encoding="utf-8")
            if not checker(content):
                failures.append(f"{name}: {source} did not emit warning")

        for source in good:
            content = source.read_text(encoding="utf-8")
            issues = checker(content)
            if issues:
                failures.append(f"{name}: {source} unexpectedly emitted warning on lines {issues}")

    if failures:
        print("\n\n".join(failures))
        return 1

    if tested_rules == 0:
        print("no QML declarative rules yet; QML rule harness is ready")
    else:
        print(f"all {tested_rules} QML declarative rule(s) passed regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
