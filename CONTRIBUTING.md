# Contributing

`qt-kde-lint` is intended to turn repeated Qt/KDE mistakes into precise, testable diagnostics without duplicating checks already provided by the compiler, clang-tidy, or Clazy.

## Before adding a rule

1. Confirm the pattern represents a real defect or high-value maintainability problem rather than merely a personal style preference.
2. Search existing clang-tidy and Clazy checks first.
3. Reduce the problem to a minimal bad example and at least one close correct example.
4. Prefer a declarative query-based clang-tidy check when it can express the rule precisely.
5. Do not broaden a matcher merely to catch more examples if that creates credible false positives.

## Pull request scope

A new lint rule should normally be one pull request containing:

- `rules/<rule-name>.json`;
- `tests/<rule-name>/bad.cpp`;
- `tests/<rule-name>/good.cpp`;
- documentation or evidence where useful.

Infrastructure, documentation, and CI work may be grouped separately.

## Diagnostics

Diagnostics should be useful without prior knowledge of this repository. Prefer wording that answers:

- what is wrong;
- why it matters in Qt/KDE code;
- what repair is normally appropriate.

Avoid diagnostics that only restate a style preference or assume the reader already knows the rule.

## Testing

Run:

```sh
python3 tools/build_config.py --output build/.clang-tidy
python3 tools/test_rules.py --clang-tidy clang-tidy-23
```

Every rule must have a triggering and non-triggering fixture. Additional fixtures are encouraged when a matcher has important boundaries.

## Upstreaming

If a rule proves generally applicable to Qt code rather than being specific to this project's corpus, consider proposing it to Clazy or clang-tidy. The local rule may remain as an incubator until upstream support is available in the toolchain used by consumers.
