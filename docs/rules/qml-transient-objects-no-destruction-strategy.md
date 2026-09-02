# Candidate rule: flag transient QML objects created repeatedly without a destruction strategy

- **Status**: Not planned

## Rationale

This candidate rule aimed to flag dynamically created QML objects (e.g., from repeated interaction handlers) that are neither explicitly destroyed nor retained for deliberate reuse, leading to accumulation until the parent object is destroyed.

However, implementing this rule effectively requires QML AST and lifetime reasoning to differentiate between objects intentionally kept alive for the lifetime of their parent and those that are leaked from transient interactions. A simple rule without such reasoning would be overly broad and result in a high rate of false positives.

The current analysis stack for this project relies on Clang tooling (`clang-query` and `clang-tidy`), which provides robust C++ AST parsing and matching capabilities but does not support parsing or reasoning about QML. Adding dedicated QML parsing infrastructure is outside the scope of the initial ruleset.

Because a low-false-positive formulation cannot be demonstrated using the existing toolchain, the implementation of this rule is not planned.
