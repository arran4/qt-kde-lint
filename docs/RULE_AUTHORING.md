# Rule authoring contract

Every rule should be understandable as an independent review unit.

## Naming

Rule definitions use a stable `Name` beginning with `qt-kde-lint-`, for example:

```text
qt-kde-lint-qobject-parent
```

clang-tidy exposes query-based checks with the `custom-` module prefix, so the emitted check name is:

```text
custom-qt-kde-lint-qobject-parent
```

Do not rename a published rule merely to improve wording. A stable diagnostic identifier is useful to CI suppressions, documentation, humans, and coding agents.

## Definition

A rule file is `rules/<Name>.json` with the shape:

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

## Required tests

Each rule gets `tests/<Name>/` containing at minimum:

- `bad.cpp` — must emit `[custom-<Name>]`;
- `good.cpp` — must not emit that diagnostic.

Use minimal local type declarations where possible instead of making the regression suite depend on a complete Qt/KDE SDK. The matcher should rely on semantic properties represented in the AST rather than filesystem-specific header paths whenever practical.

If one bad/good pair does not describe an important boundary, add numbered fixtures (`bad-2.cpp`, `good-2.cpp`, etc.).

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

Before merging, compare against current clang-tidy and Clazy checks. If an existing rule catches the same defect with comparable precision and diagnostics, enable or document that rule rather than adding a duplicate here.

## QML rules

QML rules are implemented in Python in `tools/qml_linter.py` rather than JSON.

They must follow these architecture constraints:
1. `tree-sitter-qmljs` is the canonical parsing path for QML files.
2. Rules must be registered with the `@register_rule` decorator and take a `QmlLintContext` object to reuse shared AST facilities.
3. Rules should never create parallel regex parsers or read file strings manually. Use tree-sitter AST traversal.
4. Each rule still requires `bad.qml` and `good.qml` tests in `tests/qml/<Name>/`.
