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

    def replacer(match):
        return ' ' * len(match.group(0))

    source_clean = re.sub(r'/\*.*?\*/', replacer, source, flags=re.DOTALL)
    source_clean = re.sub(r'(^\s*|(?<=\s))//.*$', replacer, source_clean, flags=re.MULTILINE)

    def offset_to_line(offset: int) -> int:
        return source[:offset].count('\n') + 1

    # We want to identify Component ids first. This helps avoid warning on unrelated createObject calls.
    # We will search for Component { id: some_name }
    component_ids = set()
    for match in re.finditer(r'\bComponent\s*\{[^}]*id\s*:\s*([a-zA-Z_$][0-9a-zA-Z_$]*)', source_clean):
        component_ids.add(match.group(1))

    # Pattern for `.createObject(`
    create_iter = re.finditer(r'\b([a-zA-Z_$][0-9a-zA-Z_$]*)\.createObject\s*\(', source_clean)

    for match in create_iter:
        comp_id = match.group(1)
        # Check if the caller is a known Component ID
        if comp_id not in component_ids:
            continue

        start = match.end()
        # Find the matching closing parenthesis for createObject(...)
        parens = 1
        i = start
        while i < len(source_clean) and parens > 0:
            if source_clean[i] == '(': parens += 1
            elif source_clean[i] == ')': parens -= 1
            i += 1

        # i is now immediately after `)`
        if i >= len(source_clean):
            continue

        # Is this a direct dereference? e.g. `.popup()`
        # Skip whitespace/newlines
        j = i
        while j < len(source_clean) and source_clean[j] in " \t\n\r":
            j += 1

        if j < len(source_clean):
            # Check for direct dot (but not question dot)
            if source_clean[j] == '.' and (j+1 >= len(source_clean) or source_clean[j+1] != '?'):
                # But wait, what if it was `?.`? In QML/JS it's `?.` not `.?`.
                # If `source_clean[j] == '.'`, we must ensure the char BEFORE it wasn't `?`
                # But we skipped spaces. So `?.` would have `?` skipped? No, `?` is not a space.
                # If it's a direct deref, it's just `.`
                issues.add(offset_to_line(j))
                continue
            elif source_clean[j] == '?':
                # Safe deref `?.`
                continue

        # Look backwards to see if it's an assignment
        # E.g. `const menu = comp.createObject(`
        # We can just check the line containing the `createObject`
        line_start = source_clean.rfind('\n', 0, match.start()) + 1
        line_text = source_clean[line_start:match.start()]

        assign_match = re.search(r'(?:const|let|var|property\s+(?:\w+))?\s*([a-zA-Z_$][0-9a-zA-Z_$]*)\s*=\s*$', line_text)
        if assign_match:
            var_name = assign_match.group(1)

            # Now `i` is after the `)` of `createObject(...)`.
            # Find the end of this assignment statement (next `;` or newline)
            while i < len(source_clean) and source_clean[i] not in ";\n":
                i += 1

            # Skip spaces/newlines/semicolons to get to the NEXT statement
            while i < len(source_clean) and source_clean[i] in " \t\n\r;":
                i += 1

            # Now `i` points to the start of the next statement.
            # Does this NEXT statement unconditionally dereference the variable?
            # Must exactly match `var_name.` without `?`
            next_text = source_clean[i:i+50]
            if re.match(rf'^{var_name}\s*\.(?!\?)', next_text):
                issues.add(offset_to_line(i))

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
                print(f"{file_path}:{line_no}: warning: {rule_name}: Component.createObject() can return null. Check the result (or use a null-safe operation) before accessing the dynamically created object.")
                failures += 1

    return 1 if failures > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
