# Rule authoring contract

Every rule should be understandable as an independent review unit.

## Naming

Rule definitions use a stable `Name` beginning with `qt-kde-lint-`, for example:

```text
qt-kde-lint-qobject-parent
```

clang-tidy exposes C++ query-based checks with the `custom-` module prefix, so the emitted check name is:

```text
custom-qt-kde-lint-qobject-parent
```

Do not rename a published rule merely to improve wording. A stable diagnostic identifier is useful to CI suppressions, documentation, humans, and coding agents.

## Definition (C++)

A C++ rule file is `rules/<Name>.json` with the shape:

```json
{
  "Name": "qt-kde-lint-example",
  "Query": "match ...",
  "Diagnostic": [
    {
      "BindName": "problem",
      "Message": "Explain what is wrong, why it matters, and the usual repair direction.",
      "Level": "Warning"
    }
  ]
}
```

Additional `Note` diagnostics are encouraged when pointing at a related declaration or ownership/lifetime participant materially improves the explanation.

## Definition (QML)

QML rules do not use the `rules/*.json` format. They are implemented purely as Python functions registered inside `tools/qml_linter.py`. The same stable naming prefix (`qt-kde-lint-`) applies. The diagnostic message must be defined alongside the rule function.

## Required tests

Each rule gets `tests/<Name>/` containing at minimum:

- `bad.cpp` (or `bad*.qml` for QML rules) — must emit a warning for the diagnostic;
- `good.cpp` (or `good*.qml` for QML rules) — must not emit that diagnostic.

Use minimal local type declarations where possible instead of making the regression suite depend on a complete Qt/KDE SDK. The C++ matcher should rely on semantic properties represented in the AST rather than filesystem-specific header paths whenever practical.

If one bad/good pair does not describe an important boundary, add numbered or named fixtures (e.g., `bad_direct.qml`, `good_guard.qml`).

## Evidence

A rule PR should link or describe the defects that motivated it. When mining generated pull requests, preserve enough information to answer:

- what the generated code did;
- what review or subsequent correction showed was wrong;
- whether the problem occurred more than once;
- whether an existing checker already catches it;
- what false-positive cases were considered.

A rule may be valuable after one occurrence when the defect is severe and the matcher is unambiguous, but recurrence is stronger evidence.

## Diagnostic quality

Diagnostics are part of the product. They should generally contain:

1. the problematic construct;
2. the Qt/KDE consequence or risk;
3. the usual direction for correction.

They should not demand a mechanically specific fix when multiple ownership, threading, lifetime, or API designs may be valid.

## Precision policy

Prefer precision over recall. Do not merge a rule with obvious false positives merely because it catches a common generated pattern. Narrow it, split it into multiple rules, or leave it as review guidance until static analysis can express it safely.

## Existing-tool check

Before merging, compare against current clang-tidy and Clazy (or qmllint for QML) checks. If an existing rule catches the same defect with comparable precision and diagnostics, enable or document that rule rather than adding a duplicate here.
