# `qt-kde-lint-context-menu-mutable-context`

Warns when a deferred UI action callback reads a mutable member variable that was recently assigned a value from a transient context source (such as a context-menu hit test parameter), instead of snapshotting the value.

## Why

Context-menu construction often updates some mutable member (such as `mCurrentUrl` from an event hit test). If an action's `triggered` callback reads that member instead of capturing its value at the time the menu was built, it risks reading stale data. This occurs because the user-triggered action executes later than the context-producing code and depends on mutable shared state that may no longer represent the action's intended context.

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

Because establishing the difference between stable and transient state requires data-flow analysis that declarative rules cannot express accurately, this rule targets a highly precise, deliberately narrow structural subset using AST matchers. It will emit a warning when all the following conditions are met within the same enclosing function:

1. The enclosing function is a recognized context handler (e.g., `contextMenuEvent`, `slotHitTestResult`, `slotContextMenu`).
2. A member variable is assigned a value derived from a parameter of that function (identifying a transient context source).
3. A `QAction::triggered` signal is connected to a lambda or member-slot callback.
4. The callback reads the *exact same* member variable that was assigned.

The rule successfully ignores stable persistent state (member variables assigned without a parameter source or outside recognized handlers) and unrelated member assignments. It supports both lambda closures and canonical member-slot targets.

**Limitations**:
- The rule is explicitly narrow to avoid false positives (low recall, high precision). It relies on specific function names and parameter-derived assignments to identify transient context. If transient state is stored in a complex way across translation units, this declarative check will miss it.

## Repair direction

Safer context-specific actions often capture the hit-test/event value by value in a lambda:

```cpp
connect(action, &QAction::triggered, this, [this, url = currentUrl]() {
    use(url);
});
```
