# `qt-kde-lint-knotification-notifyrc-wiring`

This rule is a candidate and currently acts as a placeholder for a complex KDE project-level check.

## Candidate

Add a KDE project-level consistency check between notification events referenced from C++ and the application's installed `.notifyrc` metadata.

For example, code like:
```cpp
auto *notification = new KNotification(QStringLiteral("AuthError"));
```
should be backed by an installed notification configuration containing the corresponding event section, e.g. `[Event/AuthError]`, for the component/application identity used by the notification.

## Repeated evidence

`kgithub-notify` repeatedly lost or repaired desktop notification behavior because the C++ event definitions and KDE metadata were incomplete or disagreed:

- **kgithub-notify #48 — missing notifications: add notifyrc**
  https://github.com/arran4/kgithub-notify/pull/48
  `KNotification` was in use but the application did not have the required registered event metadata installed; the fix added `kgithub-notify.notifyrc` with `NewNotification` and installed it.
- **kgithub-notify #55 — align application name with notifyrc**
  https://github.com/arran4/kgithub-notify/pull/55
  Notifications were missing because application/desktop identity did not align with the installed notification configuration.
- **kgithub-notify #69 — desktop notification setup at startup**
  https://github.com/arran4/kgithub-notify/pull/69
  The repair explicitly set `KNotification::setComponentName("kgithub-notify")` so notification events resolve against the intended `.notifyrc` metadata, and moved app identity setup earlier.
- **kgithub-notify #139 — manually install notifyrc**
  https://github.com/arran4/kgithub-notify/pull/139
  The app needed a user-facing workaround to copy the bundled `.notifyrc` to the standard KDE data location when it was not otherwise recognized.
- **kgithub-notify #209 — native KDE auth-error notification**
  https://github.com/arran4/kgithub-notify/pull/209
  Introducing event ID `AuthError` also required adding `[Event/AuthError]` to `kgithub-notify.notifyrc`.

The history shows both failure directions: notification code without usable metadata, and new event identifiers that need corresponding metadata entries.

## Generality

**KDE-wide.** Applicable to projects using `KNotification` and `.notifyrc` event definitions.

Bug-family confidence: **very high**.
Project-checker confidence: **high** for literal event IDs and repository-owned metadata.

## Candidate checks

1. Extract literal `KNotification` event IDs from constructors/factory calls.
2. Find the applicable `.notifyrc` file(s).
3. Require a matching `[Event/<id>]` section for each literal event used in code.
4. Optionally detect stale event sections never referenced by code (informational only; events may be triggered elsewhere).
5. Verify the `.notifyrc` file is included in the build/install metadata.
6. Cross-check explicit `KNotification::setComponentName()` with the notification metadata/application identity when determinable.

Dynamic event IDs should not be guessed.

## Precision

Only report hard errors when both sides are under project control and the relationship is unambiguous. Libraries may intentionally send notifications against another component's metadata, and generated/dynamic event names may not be enumerable statically.

## Existing tooling

This is cross-file KDE metadata validation, not something clang-tidy/Clazy normally performs.

## Implementation tier

**Project-level KDE checker** parsing C++ literals, `.notifyrc`, and CMake/install metadata.

## Possible diagnostics

> KNotification event AuthError is used in C++ but no [Event/AuthError] entry exists in the installed notification metadata for this component.

> This .notifyrc defines notification events, but the file is not installed/bundled by the current build configuration.
