# `qt-kde-lint-context-menu-mutable-context`

Investigate whether a useful Qt rule can detect deferred UI actions whose callback reads mutable transient context from an owning object instead of snapshotting the value that the action was created for.

## Why

Context-menu construction often updates some mutable member (such as `mCurrentUrl` from a hit test). If an action's `triggered` callback reads that member instead of capturing its value, it may read stale data if the member is updated again before the action is triggered or while another context menu is open.

Typical shape:

```cpp
// Context-menu construction updates some mutable member such as mCurrentUrl.
menu.addAction(sharedAction);
connect(sharedAction, &QAction::triggered, this, &Viewer::slotCopyLink);

void Viewer::slotCopyLink()
{
    use(mCurrentUrl); // may no longer represent the menu item that was clicked
}
```

## Evidence

KDE Akregator MR !67 reworked its WebEngine context-menu actions in exactly this direction:

- https://invent.kde.org/pim/akregator/-/merge_requests/67
- merged commit: KDE/akregator@cd92c01

The patch removes shared `KActionCollection` actions/slots that operated through `mCurrentUrl` and creates menu-local actions whose lambdas capture `url = mCurrentUrl` or `imageUrl` by value.

The resulting pattern remains in current Akregator:
https://github.com/KDE/akregator/blob/0b08fb8f5d07e0810a2c4e26e35b2a827744ab01/src/frame/webengine/akrwebengineviewer.cpp

Generality:
Moderately general: Qt event-driven UI code, especially context menus / hit testing / WebEngine. The underlying stale-context bug is not KDE-specific.

## Existing tooling

A naive rule such as “QAction-triggered lambdas must not read members” would be unusably noisy. A high-precision formulation likely requires data-flow analysis to ensure:

1. action is created/inserted while handling a context-menu or hit-test result;
2. callback is deferred until `QAction::triggered`;
3. callback reads a mutable member whose value is assigned from the transient event/hit-test context;
4. no value snapshot is captured by the callback.

Because this requires real data-flow and cannot be easily expressed as a high-precision `clang-query` AST matcher, this issue is kept as mined evidence and is not planned as a declarative rule.

## Repair direction

Safer context-specific actions often capture the hit-test/event value by value:

```cpp
connect(action, &QAction::triggered, this, [this, url = currentUrl]() {
    use(url);
});
```
