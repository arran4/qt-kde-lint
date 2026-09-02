#!/usr/bin/env python3
"""Run positive and negative regression fixtures for every QML declarative rule."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def run_fixture(linter: Path, source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "python3",
            str(linter),
            str(source)
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def fixtures(directory: Path, prefix: str) -> list[Path]:
    return sorted(directory.glob(f"{prefix}*.qml"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--linter", type=Path, default=Path("tools/qml_linter.py"))
    parser.add_argument("--tests-dir", type=Path, default=Path("tests/qml"))
    args = parser.parse_args()

    if not args.tests_dir.exists():
        print("no qml tests directory yet; rule harness is ready")
        return 0

    failures: list[str] = []

    rules = [d.name for d in args.tests_dir.iterdir() if d.is_dir()]

    if not rules:
        print("no QML declarative rules yet; rule harness is ready")
        return 0

    for rule_name in rules:
        marker = f"[custom-{rule_name}]"
        rule_tests = args.tests_dir / rule_name
        bad = fixtures(rule_tests, "bad")
        good = fixtures(rule_tests, "good")

        if not bad:
            failures.append(f"{rule_name}: missing tests/qml/{rule_name}/bad*.qml fixture")
        if not good:
            failures.append(f"{rule_name}: missing tests/qml/{rule_name}/good*.qml fixture")
        if not bad or not good:
            continue

        for source in bad:
            result = run_fixture(args.linter, source)
            if marker not in result.stdout or result.returncode == 0:
                failures.append(
                    f"{rule_name}: {source} did not emit {marker} or did not exit with error (exit code {result.returncode})\n--- qml_linter output ---\n{result.stdout}\n{result.stderr}"
                )

        for source in good:
            result = run_fixture(args.linter, source)
            if marker in result.stdout or result.returncode != 0:
                failures.append(
                    f"{rule_name}: {source} unexpectedly emitted {marker} or failed (exit code {result.returncode})\n--- qml_linter output ---\n{result.stdout}\n{result.stderr}"
                )

    if failures:
        print("\n\n".join(failures))
        return 1

    print(f"all {len(rules)} QML declarative rule(s) passed regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
