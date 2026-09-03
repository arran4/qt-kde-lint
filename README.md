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

LLVM/clang-tidy 23 or newer with query-based custom checks enabled is required for C++ rules.

For QML rules, Python 3 dependencies in `requirements-qml.txt` are required.

```sh
python3 tools/build_config.py --output build/.clang-tidy
python3 tools/test_rules.py --clang-tidy clang-tidy-23
pip install -r requirements-qml.txt
python3 tools/test_qml_rules.py
```

### Consumer Integration

Downstream projects using `qt-kde-lint` should invoke both the C++ and QML lint passes. Check out this repository (e.g., into `.qt-kde-lint`) as part of your CI pipeline.

For C++, use standard `clang-tidy` integration pointing to the generated `.clang-tidy` config.

For QML, consumers must install the required parser dependencies and invoke `qml_linter.py` across their QML files as a separate merge-blocking step:

```sh
pip install -r .qt-kde-lint/requirements-qml.txt
find src -name "*.qml" -print0 | xargs -0 -r python3 .qt-kde-lint/tools/qml_linter.py
```

Query-based custom checks currently require `--experimental-custom-checks`. The CI workflow pins the intended clang-tidy major rather than relying on the GitHub runner default.

## GitHub Actions integration

`qt-kde-lint` is intended to run as an additional static-analysis pass in the same CI pipeline that already builds Qt/KDE code. It should **not** replace the project's normal compiler warnings, `.clang-tidy`, Clazy, `cppcheck`, formatting, build, or tests.

The instructions below are intended to work with common Qt/KDE GitHub Actions layouts, including:

- a dedicated C++/Qt lint job that already creates `compile_commands.json` and runs clang-tidy;
- a combined build/test job where static analysis is currently limited to formatting or `cppcheck`;
- container-based jobs using a KDE/openSUSE, Debian, Ubuntu, or similar build environment.

A consumer workflow needs three things:

1. a CMake compilation database generated with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`;
2. clang-tidy 23 or newer, because query-based custom checks are currently experimental;
3. a checkout of this repository so `tools/build_config.py` can generate the custom-check configuration.

The generated configuration intentionally enables only `custom-qt-kde-lint-*`. Run it as a **second clang-tidy pass** rather than supplying it to the project's normal clang-tidy invocation, otherwise the generated `Checks: -*,custom-qt-kde-lint-*` setting would replace the project's normal check selection.

### Minimal addition to an existing Qt/C++ lint job

If a lint job already configures the project with `CMAKE_EXPORT_COMPILE_COMMANDS=ON`, add the following after configuration and after any existing clang-tidy/Clazy checks:

```yaml
      - name: Check out qt-kde-lint
        uses: actions/checkout@v4
        with:
          repository: arran4/qt-kde-lint
          # Pin a release tag or commit for reproducible CI once releases exist.
          ref: main
          path: .qt-kde-lint

      - name: Generate qt-kde-lint configuration
        run: |
          python3 .qt-kde-lint/tools/build_config.py \
            --rules-dir .qt-kde-lint/rules \
            --output build/qt-kde-lint.clang-tidy

      - name: Run qt-kde-lint
        run: |
          clang-tidy-23 --version
          find src tests bench -type f \
            \( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' \) \
            -print0 2>/dev/null \
            | xargs -0 -r clang-tidy-23 \
                --experimental-custom-checks \
                --config-file=build/qt-kde-lint.clang-tidy \
                -p build
```

Adjust the source directories for the project. Running translation units from the compilation database is sufficient to analyze code in included headers as well; there is normally no need to invoke clang-tidy separately on every header.

Do **not** append `|| true` to the qt-kde-lint step. A diagnostic is supposed to fail automated testing so the mistake is repaired before merge.

The project's configure command must include the compilation database flag, for example:

```yaml
      - name: Configure CMake
        run: cmake -B build -S . -G Ninja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

### Keep the existing lint pass separate

A workflow that already runs clang-tidy should normally look conceptually like this:

```yaml
      - name: Configure CMake
        run: cmake -B build -S . -G Ninja \
          -DCMAKE_BUILD_TYPE=Release \
          -DQT_MAJOR_VERSION=6 \
          -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

      - name: Existing clang-tidy and Clazy checks
        run: run-clang-tidy -p build src tests

      - name: Check out qt-kde-lint
        uses: actions/checkout@v4
        with:
          repository: arran4/qt-kde-lint
          ref: main
          path: .qt-kde-lint

      - name: qt-kde-lint
        run: |
          python3 .qt-kde-lint/tools/build_config.py \
            --rules-dir .qt-kde-lint/rules \
            --output build/qt-kde-lint.clang-tidy
          find src tests -type f \
            \( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' \) \
            -print0 2>/dev/null \
            | xargs -0 -r clang-tidy-23 \
                --experimental-custom-checks \
                --config-file=build/qt-kde-lint.clang-tidy \
                -p build
```

The important point is that the project's normal `.clang-tidy` remains authoritative for its existing checks, while qt-kde-lint supplies a separate generated configuration containing only this project's custom checks.

### Separate analysis job when the build job does not run clang-tidy

If the existing build/test job does not export a compilation database, adding a sibling analysis job is often less disruptive than changing the build pipeline. The analysis job only needs enough Qt/KF development dependencies for CMake to configure successfully and clang-tidy to parse the actual translation units.

For example:

```yaml
  qt-kde-lint:
    name: qt-kde-lint
    runs-on: ubuntu-latest
    container:
      # Use an image/repository combination that actually provides clang-tidy-23.
      image: debian:sid
    steps:
      - run: |
          apt-get update
          apt-get install -y \
            git python3 cmake ninja-build build-essential clang-tidy-23 \
            qt6-base-dev qt6-svg-dev qt6-tools-dev qt6-tools-dev-tools \
            libkf6coreaddons-dev libkf6xmlgui-dev libkf6configwidgets-dev \
            libkf6i18n-dev
          # Add the same extra Qt/KF/project development packages needed by
          # the repository's normal CMake configure step.

      - uses: actions/checkout@v4

      - name: Check out qt-kde-lint
        uses: actions/checkout@v4
        with:
          repository: arran4/qt-kde-lint
          ref: main
          path: .qt-kde-lint

      - name: Configure CMake for analysis
        run: cmake -S . -B build -G Ninja \
          -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

      - name: Run qt-kde-lint
        run: |
          clang-tidy-23 --version
          python3 .qt-kde-lint/tools/build_config.py \
            --rules-dir .qt-kde-lint/rules \
            --output build/qt-kde-lint.clang-tidy
          find src tests -type f \
            \( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' \) \
            -print0 2>/dev/null \
            | xargs -0 -r clang-tidy-23 \
                --experimental-custom-checks \
                --config-file=build/qt-kde-lint.clang-tidy \
                -p build
```

Keep the normal build/test job on its preferred distribution if desired. The analysis job only needs to configure the project successfully and expose the same headers, generated files, include paths, compile definitions, and language options closely enough for clang-tidy to parse the real build.

### Installing clang-tidy 23

Do not assume that an image's unversioned `clang-tidy` or `clang-tools` package is new enough. Verify the major version explicitly.

This repository's own CI uses the LLVM apt repository on Ubuntu 24.04:

```yaml
      - name: Install LLVM 23 clang-tidy
        run: |
          wget -q https://apt.llvm.org/llvm.sh
          chmod +x llvm.sh
          sudo ./llvm.sh 23
          sudo apt-get install -y clang-tidy-23
          clang-tidy-23 --version
```

On an image where `clang-tidy-23` is available directly, install the versioned package and still call the versioned executable:

```yaml
      - run: apt-get update && apt-get install -y python3 clang-tidy-23
      - run: clang-tidy-23 --version
```

If the normal Qt/KDE build image does not provide clang-tidy 23 yet, keep the existing lint/build job unchanged and add a dedicated qt-kde-lint job using an LLVM-23-capable image with the same project development dependencies. Do not silently fall back to clang-tidy 22 or older: those versions do not provide the custom-check interface this repository currently targets.

### CI enforcement

For automated testing, qt-kde-lint must run in a job that actually executes for pull requests and pushes where code checks are expected.

Avoid these patterns for the qt-kde-lint step:

```yaml
if: false
```

and:

```sh
clang-tidy-23 ... || true
```

Either makes the integration informational rather than protective. The intended behavior is:

1. CMake configuration fails if the project cannot be analyzed correctly;
2. qt-kde-lint diagnostics make the step fail;
3. that job is included in the repository's required GitHub status checks before merge.

Existing legacy/static-analysis steps may temporarily soft-fail while their warning backlog is being migrated, but qt-kde-lint rules are intended to be low-noise enough to be merge-blocking from the point they are adopted.

### Why checkout the rules instead of copying them into each project?

Keeping the rule definitions in this repository means every consumer runs the same rule IDs, diagnostics, regression-tested matchers, and fixes. Once stable releases/tags exist, consumers should pin the checkout to a tag or commit and update it deliberately, rather than duplicating rule JSON into each Qt/KDE repository.

A reusable/composite GitHub Action may be added later to hide the checkout/config-generation boilerplate. Until that exists, the explicit steps above make the compiler version, compilation database, and rule source visible in each consuming workflow.

## Status

The repository is being built incrementally. Infrastructure changes may share a PR, but actual lint rules should normally remain one rule per PR so their evidence, tests, false-positive tradeoffs, and history stay independently reviewable.

## License

A project license has not yet been selected. This is being left explicit rather than inferring a license from other repositories which use differing licenses.
