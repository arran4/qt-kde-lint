# Rule documentation

Contains documentation for rules.

## QML Rules

QML lint rules are written in Python using `tree-sitter-qmljs` to provide reliable AST-based checks.

When writing a new QML rule, you must use the `QmlLintContext` and its shared helper methods (e.g., `walk`, `find_object_definition`, `get_call_expression`, etc.) instead of creating your own regex, string scanning, or AST parsing functions. This ensures that QML rules benefit from the shared infrastructure and are less likely to incorrectly match comments or string literals as executable QML/JavaScript.

The linter does not perform speculative static type analysis or comprehensive semantic checks; if a condition cannot be cleanly recognized from the AST, the issue should remain unresolved rather than guessed.
