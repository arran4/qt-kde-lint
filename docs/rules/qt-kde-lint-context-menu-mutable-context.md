# `qt-kde-lint-context-menu-mutable-context`

Warns when a deferred UI action callback reads a mutable member variable that was recently assigned a value from a transient context (such as a context-menu hit test), instead of snapshotting the value.

## Why

Context-menu construction often updates some mutable member (such as `mCurrentUrl` from a hit test). If an action's `triggered` callback reads that member instead of capturing its value at the time the menu was built, it risks reading stale data. This occurs because the user-triggered action executes later than the context-producing code and depends on mutable shared state that may no longer represent the action's intended context.

Typical bug shape:

```cpp
// Context-menu construction updates some mutable member such as mCurrentUrl.
mCurrentUrl = event->url();
menu.addAction(sharedAction);
connect(sharedAction, &QAction::triggered, this, &Viewer::slotCopyLink);

void Viewer::slotCopyLink()
{
    use(mCurrentUrl); // Danger: may no longer represent the menu item that was clicked
}
```

## Evidence

KDE Akregator MR !67 reworked its WebEngine context-menu actions to fix exactly this problem:

- https://invent.kde.org/pim/akregator/-/merge_requests/67
- merged commit: KDE/akregator@cd92c01

The patch removes shared `KActionCollection` actions/slots that operated through `mCurrentUrl` and creates menu-local actions whose lambdas capture `url = mCurrentUrl` or `imageUrl` by value.

The resulting safer pattern remains in current Akregator:
https://github.com/KDE/akregator/blob/0b08fb8f5d07e0810a2c4e26e35b2a827744ab01/src/frame/webengine/akrwebengineviewer.cpp

Generality:
Moderately general: Qt event-driven UI code, especially context menus / hit testing / WebEngine. The underlying stale-context bug is not KDE-specific.

## Existing tooling

No existing built-in clang-tidy or Clazy checks adequately identify this specific deferred context-menu pattern. A naive check for reading any member via `this` produces unacceptable false positives for stable state access.

## Implemented Rule Boundaries

The declarative rule specifically targets the correlation of the transient assignment and the subsequent deferred read. It will emit a warning when:

1. A `QAction::triggered` signal is connected to a lambda or slot.
2. The callback reads a specific member variable.
3. That *same* member variable was assigned a value within the surrounding function scope of the `connect` call.

The rule successfully ignores stable state (member variables read in callbacks that were *not* assigned in the local transient scope) and unrelated member assignments.

**Limitations**:
- Because it is a structural AST matcher, it detects assignments and reads within the same surrounding function declaration. More complex cross-function data-flow paths might not be caught by this declarative subset, but the rule catches the primary motivated defect shape with high precision.

## Repair direction

Safer context-specific actions often capture the hit-test/event value by value in a lambda:

```cpp
connect(action, &QAction::triggered, this, [this, url = currentUrl]() {
    use(url);
});
```
