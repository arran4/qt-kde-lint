#!/usr/bin/env python3
"""Linter for QML files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

def test_qml_rule_createobject_null_deref(source: str) -> list[int]:
    """
    Check QML for unsafe createObject() dereferences.
    Returns list of line numbers (1-based) where issues are found.
    """
    issues = []
    lines = source.split('\n')

    direct_pattern = re.compile(r'\.createObject\s*\([^)]*\)\s*\.(?!\?)')

    assign_pattern = re.compile(r'(?:const|let|var|property\s+(?:\w+))?\s*([a-zA-Z_$][0-9a-zA-Z_$]*)\s*=\s*(?:[a-zA-Z_$][0-9a-zA-Z_$]*\.)?createObject\s*\(')

    for i, line in enumerate(lines):
        if direct_pattern.search(line):
            issues.append(i + 1)
            continue

        match = assign_pattern.search(line)
        if match:
            var_name = match.group(1)
            safe = False
            for j in range(i + 1, min(i + 15, len(lines))):
                next_line = lines[j]

                # If there's an explicit if check for the var, mark as safe
                if re.search(rf'\bif\s*\(\s*{var_name}\s*\)', next_line):
                    safe = True

                # Check for usage
                if re.search(rf'\b{var_name}\b', next_line):
                    # Is it dereferenced unsafely?
                    if not safe and re.search(rf'\b{var_name}\s*\.(?!\?)', next_line):
                        if '?.' not in next_line:
                            issues.append(j + 1)
                            break

    return issues


QML_RULES = {
    "qt-kde-lint-qml-component-createobject-null-dereference": test_qml_rule_createobject_null_deref
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint QML files for qt-kde-lint rules.")
    parser.add_argument("files", nargs="+", type=Path, help="QML files to lint")
    args = parser.parse_args()

    failures = 0

    for file_path in args.files:
        if not file_path.is_file():
            print(f"Error: {file_path} is not a file.")
            failures += 1
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            failures += 1
            continue

        for rule_name, checker in QML_RULES.items():
            issues = checker(content)
            for line_no in issues:
                print(f"{file_path}:{line_no}: warning: {rule_name}")
                failures += 1

    return 1 if failures > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
