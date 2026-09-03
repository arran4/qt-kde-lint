import unittest
import tree_sitter_qmljs
from tree_sitter import Language, Parser
import sys
import os

# Add tools directory to path to import QmlLintContext
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tools')))
from qml_linter import QmlLintContext

class TestQmlLinterUtils(unittest.TestCase):
    def setUp(self):
        try:
            language = Language(tree_sitter_qmljs.language())
        except Exception:
            import tree_sitter
            language = tree_sitter.Language(tree_sitter_qmljs.language(), "qmljs")
        self.parser = Parser(language)

    def test_find_components(self):
        code = b"""
        Item {
            Component { id: myComponent1; Item {} }
            Item {
                Component { id: myComponent2; Rectangle {} }
            }
            Component { objectName: "noId" }
        }
        """
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)
        components = context.find_components()
        self.assertEqual(components, {b'myComponent1', b'myComponent2'})

    def test_walk(self):
        code = b"Item { id: root }"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)

        node_types = []
        def visitor(node):
            node_types.append(node.type)

        context.walk(tree.root_node, visitor)
        self.assertIn('ui_object_definition', node_types)
        self.assertIn('ui_binding', node_types)

    def test_report_issue(self):
        code = b"Item {}"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)
        context.report_issue(tree.root_node, "test-rule", "test message")

        self.assertEqual(len(context.issues), 1)
        self.assertEqual(context.issues[0], "test.qml:1: [custom-test-rule] test message")

if __name__ == '__main__':
    unittest.main()
