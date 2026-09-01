# Regression tests

Declarative rule fixtures live in `tests/<rule-name>/`.

At minimum every rule must contain:

- `bad.cpp`, which emits `[custom-<rule-name>]`;
- `good.cpp`, which does not emit that diagnostic.

Additional `bad-*.cpp` and `good-*.cpp` fixtures are automatically included by the test runner.

Shared lightweight declarations that model Qt/KDE types without requiring the full SDK may live in `tests/include/`. They should model only the semantics required by the AST matcher and should not be mistaken for API compatibility shims.

`tests/harness/` contains tests for the repository's own rule/config tooling rather than lint rules.
