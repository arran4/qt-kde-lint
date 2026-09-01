#!/usr/bin/env python3
"""Run positive and negative regression fixtures for every declarative rule."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from build_config import RuleError, build_config, load_rules


def run_fixture(clang_tidy: str, config_path: Path, source: Path, include_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            clang_tidy,
            "--experimental-custom-checks",
            f"--config-file={config_path}",
            str(source),
            "--",
            "-std=c++20",
            f"-I{include_dir}",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def fixtures(directory: Path, prefix: str) -> list[Path]:
    return sorted(directory.glob(f"{prefix}*.cpp"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clang-tidy", default="clang-tidy-23")
    parser.add_argument("--rules-dir", type=Path, default=Path("rules"))
    parser.add_argument("--tests-dir", type=Path, default=Path("tests"))
    args = parser.parse_args()

    try:
        rules = load_rules(args.rules_dir.glob("*.json"))
    except RuleError as exc:
        parser.error(str(exc))

    if not rules:
        print("no declarative rules yet; rule harness is ready")
        return 0

    failures: list[str] = []
    include_dir = args.tests_dir / "include"

    with tempfile.TemporaryDirectory(prefix="qt-kde-lint-") as temp_dir:
        config_path = Path(temp_dir) / ".clang-tidy"
        config_path.write_text(json.dumps(build_config(rules), indent=2) + "\n", encoding="utf-8")

        for rule in rules:
            name = rule["Name"]
            marker = f"[custom-{name}]"
            rule_tests = args.tests_dir / name
            bad = fixtures(rule_tests, "bad")
            good = fixtures(rule_tests, "good")

            if not bad:
                failures.append(f"{name}: missing tests/{name}/bad*.cpp fixture")
            if not good:
                failures.append(f"{name}: missing tests/{name}/good*.cpp fixture")
            if not bad or not good:
                continue

            for source in bad:
                result = run_fixture(args.clang_tidy, config_path, source, include_dir)
                if marker not in result.stdout:
                    failures.append(
                        f"{name}: {source} did not emit {marker}\n--- clang-tidy output ---\n{result.stdout}"
                    )

            for source in good:
                result = run_fixture(args.clang_tidy, config_path, source, include_dir)
                if marker in result.stdout:
                    failures.append(
                        f"{name}: {source} unexpectedly emitted {marker}\n--- clang-tidy output ---\n{result.stdout}"
                    )

    if failures:
        print("\n\n".join(failures))
        return 1

    print(f"all {len(rules)} declarative rule(s) passed regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
