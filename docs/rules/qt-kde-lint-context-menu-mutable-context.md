# `qt-kde-lint-context-menu-mutable-context`

Investigate whether a useful Qt rule can detect deferred UI actions whose callback reads mutable transient context from an owning object instead of snapshotting the value that the action was created for.

## What is diagnosed

This issue identifies the pattern where an event handler (like `contextMenuEvent` or a hit-test result slot) assigns a context-specific value to a member variable, and then connects a `QAction::triggered` signal to a deferred callback (lambda or slot) that reads this member variable.

## Why

Context-menu construction often updates some mutable member (such as `mCurrentUrl` from a hit test). If an action's `triggered` callback reads that member instead of capturing its value at the time the menu was built, it risks reading stale data. This occurs because `triggered` is deferred until after the menu event loop finishes, and the mutable member could be overwritten by subsequent hit tests, other UI events, or a second context menu invocation before the first action executes.

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

No existing built-in clang-tidy or Clazy checks adequately identify this specific deferred context-menu pattern.

## Precision boundaries and False Positives

A naive rule such as “QAction-triggered lambdas must not read members” is unusably noisy. It flags perfectly legitimate callbacks such as `[this] { use(mPersistentSetting); }`, where the member is stable state and has nothing to do with transient context-menu/hit-test state.

A high-precision formulation requires distinguishing between "stable state" and "transient state". This likely requires data-flow analysis to ensure:

1. an action is created/inserted while handling a context-menu or hit-test result;
2. a member variable is assigned a value from this transient context within the same scope;
3. a callback is deferred until `QAction::triggered`;
4. the callback reads that specific mutable member whose value was just assigned;
5. no value snapshot is captured by the callback.

## Technical Limitation and Proposed Architecture Change

Because this requires real data-flow (tracking member assignments vs reads across scopes) and cannot be accurately expressed as a high-precision declarative `clang-query` AST matcher, this issue is kept as mined evidence and cannot be implemented as a JSON rule. Attempts to use AST matchers either produce massive false positives (flagging all member accesses) or miss the canonical member-slot form entirely.

Following `docs/ARCHITECTURE.md`, this rule must be implemented at the compiled custom-check layer. However, the repository currently lacks the infrastructure for compiled checks.

**Proposed Architecture Change:** To support precise static rules like this one, the repository needs a CMake build system configured against LLVM/Clang development headers to build custom clang-tidy plugins (`.so` or `.dll`). The testing scripts would then need to be updated to use the `-load` parameter to load these plugins. Until this machinery is established, this rule remains documented but unimplemented.

## Repair direction

Safer context-specific actions often capture the hit-test/event value by value in a lambda:

```cpp
connect(action, &QAction::triggered, this, [this, url = currentUrl]() {
    use(url);
});
```
