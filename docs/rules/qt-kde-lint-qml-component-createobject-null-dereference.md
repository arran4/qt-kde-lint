# qt-kde-lint-qml-component-createobject-null-dereference

This rule warns when a QML `Component.createObject()` result is dereferenced directly or assigned to a local variable and then dereferenced without an intervening null guard (e.g. `if (menu)` or `if (!menu) return;`).

## qmllint coverage

The native Qt 6 `qmllint` utility does not provide equivalent coverage.
It does not warn that `createObject` might return `null`. It will only complain about type-checking issues (e.g. `Property "open" not found on type "QObject"`), missing the primary risk of null dereferencing the returned object.
