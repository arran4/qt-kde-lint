# candidate rule: validate KXMLGUI `.rc` discovery, naming and install/resource wiring

## Candidate

Add a KDE project-level check that validates the cross-file wiring required for `KXmlGuiWindow` XMLGUI resources to actually be discoverable at runtime.

The checker should relate C++ `setXMLFile()` / `setupGUI()` usage, application/component identity, `.rc` filenames, Qt resources and CMake installation paths rather than treating each file in isolation.

## Repeated evidence

Missing menus/toolbars repeatedly came from correctly-looking C++ whose XMLGUI resource could not actually be found:

- **kjules #312 — Qt6/KF6 XMLGUI RC loading**
  https://github.com/arran4/kjules/pull/312
  The application component name was `org.kde.kjules` while the XMLGUI resource was named for `kjules`; the repair changed the component identity used for XMLGUI lookup and used the expected bare `.rc` filenames.
- **kbrowserselect #42** — added/registers the XMLGUI resource and explicitly wires `setXMLFile()` during the KDE port.
  https://github.com/arran4/kbrowserselect/pull/42
- **kbrowserselect #117** — Rules/History windows had missing menus and needed `.rc` resources.
  https://github.com/arran4/kbrowserselect/pull/117
- **kbrowserselect #118** — missing install/wiring for a main-window UI resource caused the expected XMLGUI structure not to appear.
  https://github.com/arran4/kbrowserselect/pull/118
- **kbrowserselect #124** — missing menus were repaired by embedding the `.rc` file under the required KXMLGUI resource prefix.
  https://github.com/arran4/kbrowserselect/pull/124
- **kgithub-notify #142/#144/#145/#233** repeatedly added or corrected `.rc` mappings while converting windows to proper `KXmlGuiWindow` usage.
  https://github.com/arran4/kgithub-notify/pull/142
  https://github.com/arran4/kgithub-notify/pull/144
  https://github.com/arran4/kgithub-notify/pull/145
  https://github.com/arran4/kgithub-notify/pull/233

This is separate from the C++ rule about manually constructing menus/toolbars: a window can use `actionCollection()` correctly and still get an empty UI if its XML file is undiscoverable.

## Generality

**KDE-wide.** Applicable to any application using KXMLGUI resources.

Bug-family confidence: **very high**.
Project-checker confidence: **high**, because much of the required relationship is deterministic.

## Candidate checks

Depending on project style, validate some/all of:

1. every explicit `setXMLFile("foo.rc")` refers to a repository/build resource that exists;
2. the `.rc` file is installed or embedded under a KXMLGUI-recognized location/prefix;
3. application/component name and automatic XMLGUI filename conventions agree when automatic lookup is used;
4. actions referenced by `<Action name="...">` exist in the corresponding `KActionCollection`;
5. actions registered in the collection but intended for persistent menu/toolbar placement are not silently absent due to a spelling mismatch;
6. CMake resource/install declarations actually include the `.rc` file.

The exact set should be based on current KF6 conventions rather than hard-coding historical KF5 paths.

## Precision

This should parse XML/CMake/resource metadata rather than grep for filenames. Projects can intentionally load XML from nonstandard paths, so explicit `setXMLFile()` configuration should be respected.

## Implementation tier

**Project-level KDE checker**, not clang-tidy. It needs C++, XML and build/resource metadata together.

## Possible diagnostics

> `foo.rc` is selected as this KXmlGuiWindow's XMLGUI file but is not installed/embedded in a location KXMLGUI can discover.

> XMLGUI references action `open_thing`, but no action with that name is registered in this window's `KActionCollection`.

> This window relies on automatic XMLGUI lookup, but the component/application name and available `.rc` basename do not agree.
