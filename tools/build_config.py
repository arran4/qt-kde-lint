#!/usr/bin/env python3
"""Validate rule definitions and emit one clang-tidy configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

PREFIX = "qt-kde-lint-"


class RuleError(ValueError):
    pass


def load_rules(paths: Iterable[Path]) -> list[dict]:
    rules: list[dict] = []
    names: set[str] = set()

    for path in sorted(paths):
        try:
            rule = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuleError(f"{path}: cannot load rule: {exc}") from exc

        if not isinstance(rule, dict):
            raise RuleError(f"{path}: rule must be a JSON object")

        name = rule.get("Name")
        query = rule.get("Query")
        diagnostics = rule.get("Diagnostic")

        if not isinstance(name, str) or not name.startswith(PREFIX):
            raise RuleError(f"{path}: Name must begin with {PREFIX!r}")
        if path.stem != name:
            raise RuleError(f"{path}: filename must match Name ({name}.json)")
        if name in names:
            raise RuleError(f"{path}: duplicate rule name {name}")
        names.add(name)

        if not isinstance(query, str) or "match" not in query:
            raise RuleError(f"{path}: Query must be a non-empty clang-query match expression")
        if not isinstance(diagnostics, list) or not diagnostics:
            raise RuleError(f"{path}: Diagnostic must be a non-empty list")

        warning_count = 0
        for index, diagnostic in enumerate(diagnostics):
            if not isinstance(diagnostic, dict):
                raise RuleError(f"{path}: Diagnostic[{index}] must be an object")
            bind_name = diagnostic.get("BindName")
            message = diagnostic.get("Message")
            level = diagnostic.get("Level")
            if not isinstance(bind_name, str) or not bind_name:
                raise RuleError(f"{path}: Diagnostic[{index}].BindName must be non-empty")
            if not isinstance(message, str) or not message.strip():
                raise RuleError(f"{path}: Diagnostic[{index}].Message must be non-empty")
            if level not in {"Warning", "Note"}:
                raise RuleError(f"{path}: Diagnostic[{index}].Level must be Warning or Note")
            if level == "Warning":
                warning_count += 1

        if warning_count == 0:
            raise RuleError(f"{path}: at least one diagnostic must have Level=Warning")

        unknown = set(rule) - {"Name", "Query", "Diagnostic"}
        if unknown:
            raise RuleError(f"{path}: unsupported fields: {', '.join(sorted(unknown))}")

        rules.append(rule)

    return rules


def build_config(rules: list[dict]) -> dict:
    return {
        "Checks": "-*,custom-qt-kde-lint-*",
        "CustomChecks": rules,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules-dir", type=Path, default=Path("rules"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        rules = load_rules(args.rules_dir.glob("*.json"))
    except RuleError as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build_config(rules), indent=2) + "\n", encoding="utf-8")
    print(f"generated {args.output} with {len(rules)} rule(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
