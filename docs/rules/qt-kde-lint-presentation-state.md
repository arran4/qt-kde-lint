# qt-kde-lint-presentation-state

## Candidate

Investigate a high-precision rule for Qt UI/application code that infers semantic application state by comparing presentation text, placeholder content, window titles, label text, or model display strings against magic literals instead of querying actual state.

Examples of the broader anti-pattern:
```cpp
if (documentText == QStringLiteral("*Generating document...*")) {
    // infer generation state
}

if (windowTitle().contains(QStringLiteral(" (Models)"))) {
    // infer model/category state
}
```

Such code breaks when wording, localization, formatting, failure handling or display conventions change.

## Repeated evidence

`kllamabooks` repeatedly had behavior coupled to presentation strings and later had to migrate away from it:
- **#185 — migrate generation UI state checks to backend state**
  https://github.com/arran4/kllamabooks/pull/185
  The PR explicitly removes checks for injected placeholder strings such as `*Generating merge...*` / `*Generating document...*` and switches behavior to `BookDatabase::isGenerating()` and queue-item state. It also updates AGENTS.md to document not using UI logic properties to determine state.
- **#213 — remove brittle placeholder string match**
  https://github.com/arran4/kllamabooks/pull/213
  A further bug existed because the Regenerate button depended on matching generation placeholder text; failed generation could leave the placeholder behind and the UI would infer the wrong state.
- **#136 — remove title-string state detection**
  https://github.com/arran4/kllamabooks/pull/136
  Logic relying on a `" (Models)"` marker in the displayed title was removed in favor of database flags.

These are distinct code paths but the same architectural mistake: display text became a hidden state variable.

## Generality

Moderately general: Qt/C++ UI applications, but the underlying principle is broader than Qt.

Bug-family confidence: high.
Static-rule confidence: low-medium unless narrowed to obvious UI getters/roles.

## Potential high-precision scope

A general “never compare strings” rule would be unusable. Possible Qt-specific candidates are conditional expressions comparing a literal against values obtained directly from presentation APIs such as:
- `QLabel::text()`
- `QAbstractButton::text()`
- `QWidget::windowTitle()`
- `QStandardItem::text()` / `QTreeWidgetItem::text()`
- `QModelIndex::data(Qt::DisplayRole).toString()`
- placeholder/status text placed into an editor and subsequently used as a state sentinel.

Even those can be legitimate (searching UI content, tests, text editors), so implementation should require evidence that the comparison controls non-presentation behavior or should initially remain an advisory/investigation check.

Localization provides an additional signal: comparing translated display text against a fixed literal is especially suspicious.

## Existing tooling

This is an application-architecture/static-semantics problem rather than a standard compiler/Clazy warning.

## Implementation tier

Probably a compiled data-flow check, if a defensible narrow version can be found. It may ultimately be better represented as a documented mined pattern rather than an enabled default rule.

## Outcome criteria

Only implement if bad/good fixtures can distinguish semantic-state misuse from legitimate text processing with low false positives.

## Possible diagnostic

> Application behavior is being selected by comparing UI/display text to a magic string. Presentation text can change independently of state (including through localization or error handling); keep semantic state separately and render the text from that state.
