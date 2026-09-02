# Architecture

## Goal

Catch predictable Qt/KDE defects early, especially recurring mistakes from coding agents, while retaining the parsers, AST, compile database support, suppression mechanisms, and ecosystem integration already provided by Clang tooling.

## Analysis layers

`qt-kde-lint` assumes a layered analysis stack:

1. compiler warnings;
2. built-in clang-tidy checks;
3. Clazy checks for established Qt semantics;
4. declarative `qt-kde-lint` checks;
5. compiled custom checks only where the previous layers cannot express the rule precisely.

A new rule should live at the lowest existing layer that can implement it accurately. Duplication is a maintenance cost and usually produces conflicting diagnostics.

## Declarative rules

LLVM 23 introduced experimental query-based clang-tidy custom checks. They are based on clang-query/AST matcher syntax and can emit warnings and associated notes. They deliberately do not target complex analysis or fix-its.

This is the preferred implementation for local C++ rules because it keeps each check reviewable as a small data file and avoids maintaining another Clang-based executable.

The upstream feature is experimental, so this repository pins a tested LLVM major and keeps rule definitions isolated from the generated clang-tidy configuration. If LLVM changes the configuration schema, the generator can adapt without rewriting the evidence and test layout for every rule.

## Rule definition format

Each `rules/*.json` file (for C++) or `rules/qml/*.json` file (for QML) is one object corresponding to an entry in clang-tidy's `CustomChecks` array. Required fields are:

- `Name` — must begin with `qt-kde-lint-`;
- `Query` — clang-query text containing a `match` expression (for C++ rules, dummy for QML rules);
- `Diagnostic` — one or more bound-node diagnostics, including at least one warning.

The generated clang-tidy check name is `custom-<Name>`.

JSON is intentional: it is a strict, dependency-free authoring subset that can be loaded and validated by Python's standard library. The generated top-level configuration is also emitted as JSON, which LLVM's YAML configuration parser accepts.

## Compiled rules

A compiled extension should be introduced only with a concrete example that requires capabilities such as control-flow reasoning, preprocessing callbacks, substantial cross-node state, or fix-its that cannot be represented by a query-based check.

Compiled checks should remain out-of-tree unless/until an upstream destination is appropriate.

## Non-C++ rules

Qt/KDE projects also contain CMake, QML, desktop files, AppStream metadata, DBus XML, KConfig data, and CI configuration. These should not be forced through clang-tidy. If recurring mistakes are found there, this repository may gain thin format-specific rule runners while retaining the same principles: stable rule IDs, high precision, explanatory diagnostics, and positive/negative regression tests. For QML rules, they are placed in `rules/qml/` to separate them from C++ AST match rules.
