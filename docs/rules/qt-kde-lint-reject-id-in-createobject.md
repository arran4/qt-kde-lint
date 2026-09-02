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

*Heuristic:* To avoid false positives on unrelated objects that happen to have a `createObject` method (like a custom `factory.createObject`), the linter employs a conservative heuristic: it only flags calls where the receiver's name ends in `Component` or `component` (e.g., `linkMenuComponent`, `component`).

*Existing Tooling:* The standard `qmllint` (as of Qt 6) was tested and does **not** currently diagnose this issue. `qmllint` does not flag `id` within a property map passed to `createObject`, validating the need for this custom lint rule.
