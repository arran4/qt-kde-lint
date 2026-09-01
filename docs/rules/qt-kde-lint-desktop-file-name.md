# qt-kde-lint-desktop-file-name

## Rationale
Add Qt/KDE application-identity checks covering `QCoreApplication`/`QGuiApplication`, `KAboutData`, installed `.desktop` metadata, and related KDE component identifiers.

The highest-confidence C++ sub-rule is direct and documented by Qt: `desktopFileName` is the base name without the trailing `.desktop` extension. A literal ending in `.desktop` passed to `QGuiApplication::setDesktopFileName()` should be diagnosed. More generally, project-level validation should ensure the basename chosen in C++ corresponds to the installed desktop entry and is not contradicted by multiple different identities.

Current Qt documentation states that `QGuiApplication::setDesktopFileName()` expects the desktop entry basename without the `.desktop` extension.

## Evidence
Application identity repeatedly broke desktop integration in mined repositories:
* kgithub-notify #55 — missing notifications due to identity mismatch required aligning application name / desktop-file identity with the installed notification metadata.
* kgithub-notify #69 — initialize identity before QApplication and align notification component explicitly with project metadata.
* kgithub-notify #71 — Naming mismatches affected application association and notifications.
* kgithub-notify #106 — duplicate identity setters caused DBus/portal registration failure.
* kllamabooks qt-kde-lint#18 — attempted application registration fix that incorrectly changed `setDesktopFileName` to include `.desktop`.

## Check (Implementation Guidance)
Due to limitations in Clang AST matchers for querying the exact string value of `StringLiteral` nodes declaratively without writing a compiled C++ check, this rule cannot be purely implemented as a JSON rule at this time. It should be implemented in future tooling.

The ideal check would:
1. Warn if a literal passed to `QGuiApplication::setDesktopFileName()` ends in `.desktop`.
2. If a repository desktop entry exists, verify the configured basename matches an installed `<basename>.desktop` file.
3. Detect conflicting repeated literal calls to `setDesktopFileName()` / `setApplicationName()` in startup code.
4. Optionally compare `KAboutData` desktop-file/component identity with Qt identity where both are explicitly supplied.
5. Cross-reference notification/KXMLGUI identity only when their framework semantics require the same component.

**Diagnostic Message Example:**
`QGuiApplication::setDesktopFileName() expects the desktop entry basename without the .desktop extension. Pass org.example.App, not org.example.App.desktop.`
