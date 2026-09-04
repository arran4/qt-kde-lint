# qt-kde-lint-action-semantic-context

Warns when the text label of an Action lacks a semantic context. Translators benefit from semantic hints, particularly when the text might have different meanings depending on where it appears in the UI (e.g., in a menu vs on a button).

By providing an `@action` context in the `i18nc()` or `i18ndc()` call, translators can provide more accurate localizations.

## QML Rule Boundary
The QML implementation of this rule specifically targets `Action` and `Kirigami.Action` objects in `.qml` files.

Because we prefer precision over recall, the rule deliberately does *not* trigger on generic identifiers ending in `.Action` (like `MyControls.Action`) unless they are resolved to known KDE/Qt actions. This keeps false positives low.

The rule correctly recommends `i18nc` instead of `i18n`, and `i18ndc` instead of `i18nd`. It ignores translations that already have a context.

## Relation to C++ Rule
This QML rule directly parallels the C++ `qt-kde-lint-action-semantic-context` rule, which flags the usage of `i18n()` (without context) inside `QAction` constructors and related QAction setter/adder methods like `QAction::setText` or `QMenu::addAction`. Both use the same diagnostic ID for consistent reporting across both C++ and QML runtimes.

## Existing Tooling Assessment
Prior to adding this rule to `qml_linter.py`, an assessment was made on whether `qmllint` or standard `KI18n` toolings support this semantic action diagnostic natively. Existing KDE static analysis and localization extractors (`xgettext` based) primarily focus on extracting strings and diagnosing syntax errors, but do not statically enforce the usage of context arguments specifically bounded by `Action` types in QML or C++. Thus, this rule adds valuable coverage that doesn't duplicate existing `qmllint` coverage.
