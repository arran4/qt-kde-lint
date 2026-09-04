import sys
import tree_sitter_qmljs
from tree_sitter import Language, Parser

language = Language(tree_sitter_qmljs.language())
parser = Parser(language)

code = b"""
import QtQuick

Item {
    Component { id: comp; Rectangle {} }

    function test(useFallback) {
        var menu = comp.createObject(parent);
        if (useFallback) {
            menu = fallback;
        } else {
            return;
        }
        menu.popup();
    }
}
"""
tree = parser.parse(code)
def walk(node, level=0):
    print("  " * level + node.type + " " + (node.text.decode('utf-8') if not node.children else ""))
    for child in node.children:
        walk(child, level + 1)
walk(tree.root_node)
