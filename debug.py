import sys
import tree_sitter_qmljs
from tree_sitter import Language, Parser
from tools.qml_linter import qt_kde_lint_qml_component_createobject_null_dereference, QmlLintContext, _RULES

language = Language(tree_sitter_qmljs.language())
parser = Parser(language)

with open('tests/qml/qt-kde-lint-qml-component-createobject-null-dereference/good_all_paths_exit.qml', 'rb') as f:
    tree = parser.parse(f.read())

context = QmlLintContext('tests/qml/qt-kde-lint-qml-component-createobject-null-dereference/good_all_paths_exit.qml', tree)
qt_kde_lint_qml_component_createobject_null_dereference(context)

for issue in context.issues:
    print(issue)
