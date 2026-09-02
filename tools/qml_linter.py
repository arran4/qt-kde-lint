#!/usr/bin/env python3
"""Linter for QML files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def test_qml_rule_createobject_null_deref(source: str) -> list[int]:
    """
    Check QML for unsafe createObject() dereferences.
    Returns list of line numbers (1-based) where issues are found.
    """
    issues = set()
    lines = source.split('\n')

    def replacer(match):
        return ' ' * len(match.group(0))

    source_clean = re.sub(r'/\*.*?\*/', replacer, source, flags=re.DOTALL)
    source_clean = re.sub(r'(^\s*|(?<=\s))//.*$', replacer, source_clean, flags=re.MULTILINE)

    def offset_to_line(offset: int) -> int:
        return source[:offset].count('\n') + 1

    for match in re.finditer(r'\.createObject\s*\([^)]*\)\s*\.(?!\?)', source_clean):
        issues.add(offset_to_line(match.start()))

    assign_iter = re.finditer(r'(?:const|let|var|property\s+(?:\w+))?\s*([a-zA-Z_$][0-9a-zA-Z_$]*)\s*=\s*(?:[a-zA-Z_$][0-9a-zA-Z_$]*\.)?createObject\s*\(', source_clean)

    for match in assign_iter:
        var_name = match.group(1)
        parens = 1
        i = match.end()
        while i < len(source_clean) and parens > 0:
            if source_clean[i] == '(': parens += 1
            elif source_clean[i] == ')': parens -= 1
            i += 1

        while i < len(source_clean) and source_clean[i] in " \t\n\r;":
            i += 1

        if i < len(source_clean):
            # Is it immediately dereferenced?
            next_text = source_clean[i:i+50]
            if re.match(rf'^{var_name}\s*\.(?!\?)', next_text):
                issues.add(offset_to_line(i))
            else:
                # The prompt explicitly required warning on:
                # const menu = comp.createObject(parent);
                # if (menu) { doSomething(); }
                # menu.popup(); // WARN!
                # Because it's an unsafe access in the same scope, even if checked earlier but the access itself isn't protected.

                # Search for all accesses in the block
                # To be precise, just look ahead until end of block `}` or next assignment
                look_ahead = source_clean[i:i+300]
                # we just need to ensure we don't warn if the access is INSIDE an `if (menu)` block
                # A simple regex for this narrow usecase without a full parser:

                # Iterate over all usages
                usage_iter = re.finditer(rf'\b{var_name}\b', look_ahead)
                for usage_match in usage_iter:
                    usage_idx = usage_match.start()
                    prefix = look_ahead[:usage_idx]

                    # Is it dereferenced unsafely?
                    postfix = look_ahead[usage_match.end():usage_match.end()+10]
                    if re.match(r'^\s*\.(?!\?)', postfix):
                        # It is dereferenced. Is it safe?
                        # It's safe if it's strictly inside an `if` block for this variable
                        # Check last guard
                        safe = False
                        guards = list(re.finditer(rf'\bif\s*\([^)]*\b{var_name}\b[^)]*\)', prefix))
                        if guards:
                            last_guard = guards[-1]
                            between = look_ahead[last_guard.end():usage_idx]
                            open_b = between.count('{')
                            close_b = between.count('}')
                            if open_b > close_b:
                                safe = True
                            if open_b == 0 and ';' not in between:
                                safe = True

                        if not safe:
                            issues.add(offset_to_line(i + usage_idx))
                            break # Once we found an unsafe one, done

    return sorted(list(issues))


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
