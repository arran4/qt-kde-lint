# qt-kde-lint-ambiguous-qeventloop-timeout

## Rationale
Code using a local `QEventLoop` that sets up an asynchronous operation's completion signal AND a `QTimer::singleShot` timeout, both to trigger `quit()`, creates an ambiguous loop exit.
If the loop is quit, it could be because the operation completed, or because the timeout expired.
Using the result of the asynchronous operation immediately after `exec()` without checking whether the completion signal actually occurred is unsafe, since the timeout path could have been hit and the operation may not have a valid result.

## Evidence
Found twice in KDE KWeather MR !162 / its merged KRunner implementation:
* https://invent.kde.org/utilities/kweather/-/merge_requests/162
* merged commit: KDE/kweather@ac960a5
* source: https://github.com/KDE/kweather/blob/ac960a53d7ebb6ac0f71b2269f0b235def01e92f/src/krunner/kweatherrunner.cpp

## Check
The check looks for the pattern where:
1. A local `QEventLoop` is declared.
2. `QTimer::singleShot(..., &loop, &QEventLoop::quit)` is called.
3. `connect(sender, ..., &loop, &QEventLoop::quit)` is called.
4. `loop.exec()` is called.
5. The `sender` object is used outside the `connect` call within the same compound block (this usually indicates reading `result()` or `error()`).

If you handle this correctly (e.g., using a boolean `finished` flag set via a lambda), the direct connection to `&QEventLoop::quit` isn't made, or the `sender` isn't blindly used.
