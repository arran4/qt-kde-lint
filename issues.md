# Issues

This file documents issues that have been considered but not implemented, along with the reasoning.

## Issue #5: candidate rule: flag transient QML objects created repeatedly without a destruction strategy

- **Status**: Not planned
- **Reasoning**: This rule requires QML AST/lifetime reasoning to avoid high false-positive rates when differentiating between objects intentionally kept alive and those that are leaked from transient interactions. The current analysis stack relies on Clang tooling (`clang-query`/`clang-tidy`), which provides C++ AST parsing but does not support QML. Implementing a low-false-positive formulation is currently not feasible without adding dedicated QML parsing infrastructure. Therefore, this issue is closed as not planned for the initial ruleset.
