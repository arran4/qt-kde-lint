# `qt-kde-lint-proxy-index-source-model`

**Status**: Unimplementable as a declarative JSON query.

Detect Qt model/view code where a `QModelIndex` originating from a `QSortFilterProxyModel` (or a stack of proxy models) is used as though its row/index belonged directly to the underlying source model without first mapping it through `mapToSource()`.

## Typical bad shape

```cpp
const QModelIndex index = view->currentIndex();
auto item = sourceModel->item(index.row());
```

when `view->model()` is a proxy model.

## Repeated evidence

This has caused real wrong-item behavior repeatedly in the mined repositories:

- **kjules #86 — editing incorrect items in sorted/filtered UI lists**
  https://github.com/arran4/kjules/pull/86
  The PR explicitly says errors, drafts, and templates code assumed the UI row matched the source-model row, and repaired context menus/activation paths by mapping proxy indexes to source indexes.
- The follow-up discussion confirms the purpose of `proxy->mapToSource(index)` was to target the correct absolute item regardless of sorting/filtering:
  https://github.com/arran4/kjules/pull/86#issuecomment-4197037430
- **kjules #354 — stacked proxy models**
  https://github.com/arran4/kjules/pull/354
  The PR explicitly records another round of index-mapping bugs and fixes mapping all the way through `BranchListProxyModel -> SourceFilterProxyModel -> SourceModel`.
- **kjules #61 — Follow action**
  https://github.com/arran4/kjules/pull/61
  The implementation had to explicitly map selected proxy rows to source rows before retrieving raw session data.
- **kbrowserselect #99** also maps a view index through proxy models before retrieving the underlying intent:
  https://github.com/arran4/kbrowserselect/pull/99

This is therefore not a one-off implementation mistake; it is a recurring Qt model/view failure mode in generated code.

## Generality

**Very general: Qt model/view-wide.** Any application using `QSortFilterProxyModel`, custom proxy models, sorting or filtering can hit this.

Bug-family confidence: **high**.
Static-rule confidence: **medium-high** if provenance can be established; low if reduced to a naive `index.row()` heuristic.

## Precision requirements

Do **not** warn merely because `QModelIndex::row()` is called in code that also has a proxy model.

A useful checker needs to establish a relationship such as:

1. an index comes from a view whose model is a proxy, or from a proxy-returning API;
2. that index (or its `.row()`) then flows into a different/source model API;
3. no corresponding `mapToSource()` chain occurred.

Stacked proxies need special attention: mapping through only one layer can still be wrong.

## Existing tooling

A search of the current Clazy source/check catalogue did not find a `QSortFilterProxyModel` / `mapToSource` check. This should still be rechecked before implementation.

## Implementation tier

Likely a **compiled clang-tidy/Clazy-style C++ check** rather than a JSON query rule because useful precision requires local provenance/data-flow reasoning. A `clang-query` declarative AST matcher cannot express the data flow necessary to reliably track the origin of the `QModelIndex` from a proxy to its misuse in a source model without generating unacceptable false positives.

## Possible diagnostic

> This QModelIndex comes from a proxy model but is being used against a different/source model. Map it through the proxy chain with `mapToSource()` before using the index or row with the source model; sorting/filtering can otherwise target the wrong item.
