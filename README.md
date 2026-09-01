# qt-kde-lint

Lint rules for Qt and KDE applications, initially focused on catching recurring mistakes introduced by LLM-assisted development before they require another review/fix iteration.

The project complements existing static analysis rather than replacing it:

1. use compiler diagnostics and existing `clang-tidy` checks;
2. use Clazy for established Qt-specific checks;
3. add a `qt-kde-lint` declarative check only when the problem is not already covered;
4. add a compiled clang-tidy/Clazy-style check only when a declarative AST matcher is insufficient.

The first implementation target is LLVM 23's experimental query-based clang-tidy custom checks. This keeps most project-specific rules as data rather than another C++ linter binary.

## Rule policy

Rules are intentionally high precision. A missed instance is preferable to a noisy rule that teaches humans or coding agents to ignore the linter.

Each new rule should normally be introduced in its own pull request and include:

- evidence or motivation for the recurring problem;
- a stable rule name;
- a diagnostic that explains the problem, consequence, and repair direction;
- at least one example that must trigger;
- at least one nearby/correct example that must not trigger;
- a note when an existing Clazy or clang-tidy check was considered and found insufficient.

See [`docs/RULE_AUTHORING.md`](docs/RULE_AUTHORING.md) for the contract.

## Layout

- `rules/` — declarative custom-check definitions, one JSON file per rule. JSON is used because it can be validated with Python's standard library and emitted as YAML-compatible clang-tidy configuration.
- `tests/<rule-name>/` — positive and negative regression fixtures for each rule.
- `tools/build_config.py` — validates rules and generates a clang-tidy configuration.
- `tools/test_rules.py` — runs every rule's regression fixtures.
- `docs/` — architecture and rule-authoring rationale.

## Local development

LLVM/clang-tidy 23 or newer with query-based custom checks enabled is required.

```sh
python3 tools/build_config.py --output build/.clang-tidy
python3 tools/test_rules.py --clang-tidy clang-tidy-23
```

Query-based custom checks currently require `--experimental-custom-checks`. The CI workflow pins the intended clang-tidy major rather than relying on the GitHub runner default.

## Status

The repository is being built incrementally. Infrastructure changes may share a PR, but actual lint rules should normally remain one rule per PR so their evidence, tests, false-positive tradeoffs, and history stay independently reviewable.

## License

A project license has not yet been selected. This is being left explicit rather than inferring a license from other repositories which use differing licenses.
