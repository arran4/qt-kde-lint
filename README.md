# qt-kde-lint

Experimental lint rules for Qt and KDE C++ applications, with an initial focus on catching recurring mistakes produced by LLM-assisted development before they consume another review/fix iteration.

The project is intended to complement, not replace, existing tooling such as `clang-tidy` and Clazy. Rules should prefer existing checks where they already cover the problem, use declarative clang-tidy custom checks where practical, and only introduce compiled checks when the rule genuinely requires them.

## Status

Repository bootstrap in progress. Rules will be introduced incrementally, normally one rule per pull request with positive and negative regression tests and diagnostics written to be useful to both humans and coding agents.
