# qt-kde-lint-qml-transient-object-leak

Identifies when `Component.createObject()` is called inside a repeatable interaction handler (e.g., `onClicked`, `onTapped`, `onTriggered`) and its returned object reference is only held locally without an explicit `destroy()` path or scope escape.

## Why is this a problem?

When a transient object (like a dynamically created `Menu` or `Popup`) is instantiated in an interaction handler and not destroyed, every click/interaction may cause memory leaks a new instance of the object. Over time, this accumulates, causing memory bloat and potential UI/performance degradation.

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
