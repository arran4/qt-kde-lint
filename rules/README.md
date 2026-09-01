# Declarative rules

Each `*.json` file in this directory is one LLVM query-based custom clang-tidy check definition.

Rules must follow [`docs/RULE_AUTHORING.md`](../docs/RULE_AUTHORING.md). In particular, the filename must exactly match the rule's `Name`, names begin with `qt-kde-lint-`, and every rule must have positive and negative regression fixtures under `tests/<Name>/`.

Do not add a local rule when current clang-tidy or Clazy already provides materially equivalent coverage.
