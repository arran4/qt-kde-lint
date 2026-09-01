# `qt-kde-lint-qthread-create-immediate-start`

Warn when code immediately calls `start()` on the pointer returned by `QThread::create()` and then discards that pointer.

## Why

`QThread::create()` creates and returns a `QThread` object. Starting that object without retaining the returned pointer leaves no owner or handle through which the caller can manage the `QThread` object's lifetime. Qt's QThread documentation recommends arranging deletion after completion, commonly by connecting `QThread::finished` to `QObject::deleteLater`.

The diagnostic deliberately targets only the unambiguous chained form:

```cpp
QThread::create([] { doWork(); })->start();
```

It does not diagnose retaining the returned pointer and starting it later.

## Evidence

This pattern was found while reviewing generated asynchronous-thread code in `arran4/kjules` PR #305. Review feedback required keeping the `QThread *`, arranging `finished` -> `deleteLater`, and only then starting it:

- https://github.com/arran4/kjules/pull/305
- https://github.com/arran4/kjules/pull/305#discussion_r3323827134

The final PR code uses the managed form in its thread benchmark.

## Existing tooling

The current Clazy check catalogue contains numerous thread-, QObject-, connect-, and lifetime-related checks, but no check specifically covering an immediately discarded `QThread::create()` result. No current built-in clang-tidy check was found that is Qt-specific enough to cover this expression.

This local rule is intentionally narrower than a general QThread lifetime analysis. A broader lifetime rule should only be added if additional evidence can be matched without materially increasing false positives.

## Repair direction

Retain the returned pointer and define its ownership/lifetime before starting the thread. A common fire-and-clean-up pattern is:

```cpp
auto *thread = QThread::create([] { doWork(); });
QObject::connect(thread, &QThread::finished, thread, &QObject::deleteLater);
thread->start();
```

Project-specific ownership or cancellation requirements may call for a different lifetime strategy.
