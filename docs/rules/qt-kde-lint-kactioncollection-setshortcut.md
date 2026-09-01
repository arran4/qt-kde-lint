# qt-kde-lint-kactioncollection-setshortcut

## Motivation
Detect a `QAction` owned/registered by a KDE `KActionCollection` whose default shortcut is assigned with `QAction::setShortcut()` / `setShortcuts()` instead of `KActionCollection::setDefaultShortcut()` / `setDefaultShortcuts()`.

Actions controlled by `KActionCollection` must expose framework-managed defaults so KDE shortcut configuration continues to work. Using `setShortcut()` on them causes `kf.xmlgui` shortcut warnings at runtime.

### Examples
Bad:
```cpp
QAction *zoomIn = actionCollection()->addAction(QStringLiteral("zoom_in"));
zoomIn->setShortcut(QKeySequence::ZoomIn);
```

Preferred KDE form:
```cpp
QAction *zoomIn = actionCollection()->addAction(QStringLiteral("zoom_in"));
actionCollection()->setDefaultShortcut(zoomIn, QKeySequence::ZoomIn);
```

### Reference
See https://github.com/arran4/qt-kde-lint/issues/12
