# qt-kde-lint-qml-transient-object-leak

Identifies when `Component.createObject()` is called inside a repeatable interaction handler (e.g., `onClicked`, `onTapped`, `onTriggered`) and its returned object reference is only held locally without an explicit `destroy()` path or scope escape.

## Why is this a problem?

When a transient object (like a dynamically created `Menu` or `Popup`) is instantiated in an interaction handler and not destroyed, every click/interaction potentially accumulates instances under the long-lived parent. Over time, this accumulates, causing memory bloat and potential UI/performance degradation.

## Examples

### Bad

```qml
Button {
    onClicked: {
        let menu = myComponent.createObject(parent);
        menu.popup();
        // The local 'menu' reference vanishes, but the object itself lives on indefinitely.
    }
}
```

### Good

```qml
Button {
    onClicked: {
        let menu = myComponent.createObject(parent);
        if (menu) {
            menu.onClosed.connect(menu.destroy);
            menu.popup();
        }
    }
}
```

```qml
Button {
    onClicked: {
        let menu = myComponent.createObject(parent);
        if (menu) {
            menu.popup();
            menu.destroy();
        }
    }
}
```


## Supported Boundary

This rule is designed to be highly precise and conservative:
- It only warns inside repeatable interaction handlers (e.g., `onClicked`, `onTapped`).
- It only flags statically recognized `Component.createObject(...)` or `Qt.createComponent(...).createObject(...)` patterns.
- It requires a clearly long-lived parent (`parent` or a locally recognized `id`). Dynamic or uncertain parents are excluded and will not trigger a warning.
- It requires the result to be stored in a local-only variable.
- It only recognizes concrete destruction/escape patterns: an explicit `destroy()` call, passing `<obj>.destroy` directly to a `.connect(...)` call, or assignment/push to a non-local property or array. Arbitrary function calls (like `console.log`) or storing a bare reference to `<obj>.destroy` do not count as a valid escape.
