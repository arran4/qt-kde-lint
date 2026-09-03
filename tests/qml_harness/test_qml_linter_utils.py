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


    def test_get_assignment_expression(self):
        code = b"Item { Component.onCompleted: { x = 42; y += 1; } }"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)

        found_plain = False
        found_compound = False

        def visitor(node):
            nonlocal found_plain, found_compound
            if node.type in ('assignment_expression', 'augmented_assignment_expression'):
                left, right = context.get_assignment_expression(node)
                if left and left.text == b'x' and right and right.text == b'42':
                    found_plain = True
                if not left and not right:
                    found_compound = True

        context.walk(tree.root_node, visitor)
        self.assertTrue(found_plain)
        self.assertTrue(found_compound)

    def test_get_local_variable_declaration(self):
        code = b"Item { Component.onCompleted: { const x = 42; let y; } }"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)

        found_x = False
        found_y = False

        def visitor(node):
            nonlocal found_x, found_y
            if node.type == 'lexical_declaration':
                ident, val = context.get_local_variable_declaration(node)
                if ident and ident.text == b'x' and val and val.text == b'42':
                    found_x = True
                if ident and ident.text == b'y' and val is None:
                    found_y = True

        context.walk(tree.root_node, visitor)
        self.assertTrue(found_x)
        self.assertTrue(found_y)

    def test_find_object_definition(self):
        code = b"Item { id: root; Rectangle { width: 100 } }"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)

        found_item = False
        found_rectangle = False

        def visitor(node):
            nonlocal found_item, found_rectangle
            if context.find_object_definition(node, b'Item'):
                found_item = True
            if context.find_object_definition(node, b'Rectangle'):
                found_rectangle = True

        context.walk(context.tree.root_node, visitor)
        self.assertTrue(found_item)
        self.assertTrue(found_rectangle)

    def test_get_property_binding(self):
        code = b"Item { width: 100 }"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)

        found_width = False

        def visitor(node):
            nonlocal found_width
            if node.type == 'ui_object_initializer':
                val = context.get_property_binding(node, b'width')
                if val and val.text == b'100':
                    found_width = True

        context.walk(context.tree.root_node, visitor)
        self.assertTrue(found_width)

    def test_get_call_expression(self):
        code = b"Item { Component.onCompleted: myComponent.createObject(parent) }"
        tree = self.parser.parse(code)
        context = QmlLintContext("test.qml", tree)

        found_call = False

        def visitor(node):
            nonlocal found_call
            if node.type == 'call_expression':
                member, receiver, prop, args = context.get_call_expression(node)
                if receiver and receiver.text == b'myComponent' and prop and prop.text == b'createObject':
                    found_call = True

        context.walk(context.tree.root_node, visitor)
        self.assertTrue(found_call)

if __name__ == '__main__':
    unittest.main()
