import unittest
import tree_sitter_qmljs
from tree_sitter import Language, Parser
import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools')))

from qml_linter import QmlLintContext

class TestQmlLinterCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.language = Language(tree_sitter_qmljs.language())
        except Exception:
            import tree_sitter
            cls.language = tree_sitter.Language(tree_sitter_qmljs.language(), "qmljs")
        cls.parser = Parser(cls.language)

    def parse_code(self, code):
        tree = self.parser.parse(code.encode('utf-8'))
        return QmlLintContext("test.qml", tree)

    def test_find_object_definition(self):
        context = self.parse_code("Item { id: root; Rectangle { width: 100 } }")

        found_item = False
        found_rectangle = False

        def check(node):
            nonlocal found_item, found_rectangle
            if context.find_object_definition(node, b'Item'):
                found_item = True
            if context.find_object_definition(node, b'Rectangle'):
                found_rectangle = True

        context.walk(context.tree.root_node, check)
        self.assertTrue(found_item)
        self.assertTrue(found_rectangle)

    def test_get_property_binding(self):
        context = self.parse_code("Item { width: 100 }")

        found_width = False

        def check(node):
            nonlocal found_width
            if node.type == 'ui_object_initializer':
                val = context.get_property_binding(node, b'width')
                if val and val.text == b'100':
                    found_width = True

        context.walk(context.tree.root_node, check)
        self.assertTrue(found_width)

    def test_find_components(self):
        context = self.parse_code("Item { Component { id: myComponent } }")
        components = context.find_components()
        self.assertIn(b'myComponent', components)

    def test_get_call_expression(self):
        context = self.parse_code("Item { Component.onCompleted: myComponent.createObject(parent) }")

        found_call = False

        def check(node):
            nonlocal found_call
            if node.type == 'call_expression':
                member, receiver, prop, args = context.get_call_expression(node)
                if receiver and receiver.text == b'myComponent' and prop and prop.text == b'createObject':
                    found_call = True

        context.walk(context.tree.root_node, check)
        self.assertTrue(found_call)

    def test_get_local_variable_declaration(self):
        context = self.parse_code("Item { Component.onCompleted: { const x = 42; } }")

        found_var = False

        def check(node):
            nonlocal found_var
            ident, val = context.get_local_variable_declaration(node)
            if ident and ident.text == b'x' and val and val.text == b'42':
                found_var = True

        context.walk(context.tree.root_node, check)
        self.assertTrue(found_var)

    def test_get_assignment_expression(self):
        context = self.parse_code("Item { Component.onCompleted: { x = 42; } }")

        found_assign = False

        def check(node):
            nonlocal found_assign
            left, right = context.get_assignment_expression(node)
            if left and left.text == b'x' and right and right.text == b'42':
                found_assign = True

        context.walk(context.tree.root_node, check)
        self.assertTrue(found_assign)

if __name__ == '__main__':
    unittest.main()
