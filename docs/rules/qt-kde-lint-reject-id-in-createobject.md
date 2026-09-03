# qt-kde-lint-reject-id-in-createobject

Detects QML/JavaScript code that tries to assign an `id` through the property map passed to `Component.createObject()`.

## Problem

Qt documents that dynamically-created QML objects do not have a QML `id`. The second argument to `createObject()` is a map of properties, and `id` is not a runtime QML property. Assigning it has no effect and often indicates a misunderstanding of object ownership and lifecycle in QML.

Example of problematic code:
```qml
const menu = linkMenuComponent.createObject(parent, {
    id: "linkMenu",
    url: foundLink,
});
```

## Solution

Remove the `id` key. If you need to refer to the dynamically created instance later, retain the returned object reference in a JavaScript variable or a QML `property`.

## Implementation Notes

This rule is implemented in Python (`tools/qml_linter.py`) using `tree-sitter` and `tree-sitter-qmljs` to parse the QML AST.

*Heuristic:* To avoid false positives on unrelated objects that happen to have a `createObject` method (like a custom `factory.createObject`), the linter employs a conservative two-pass AST collection strategy. First, it collects the IDs of all inline `Component { id: ... }` object definitions within the file. Then, it only flags `.createObject(...)` calls whose receiver resolves to one of those explicitly collected `Component` IDs. Uncertain or dynamic component-producing expressions are intentionally skipped to preserve the repository's precision-first policy.

*Existing Tooling:* `qmllint 1.0` (as distributed with Qt 6.4.2) was explicitly tested and does **not** currently diagnose this issue. `qmllint` does not flag `id` within a property map passed to `createObject`, validating the need for this custom lint rule.
