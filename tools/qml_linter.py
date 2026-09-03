import sys
import tree_sitter_qmljs
from tree_sitter import Language, Parser

import warnings

def check_qml(filepath):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            language = Language(tree_sitter_qmljs.language())
        except Exception:
            # Compatibility with older tree-sitter bindings
            import tree_sitter
            language = tree_sitter.Language(tree_sitter_qmljs.language(), "qmljs")

    parser = Parser(language)

    with open(filepath, 'rb') as f:
        tree = parser.parse(f.read())

    known_components = set()

    # Pass 1: Collect Component IDs
    def collect_components(node):
        if node.type == 'ui_object_definition':
            # Check if this object is a Component
            is_component_def = False
            for child in node.children:
                if child.type == 'identifier' and child.text == b'Component':
                    is_component_def = True
                    break

            if is_component_def:
                # Find its initializer block `{ ... }`
                for child in node.children:
                    if child.type == 'ui_object_initializer':
                        # Look for an `id` binding
                        for stmt in child.children:
                            if stmt.type == 'ui_binding':
                                key_node = None
                                val_node = None
                                for binding_child in stmt.children:
                                    if binding_child.type == 'identifier':
                                        key_node = binding_child
                                    elif binding_child.type == 'expression_statement':
                                        val_node = binding_child
                                if key_node and key_node.text == b'id' and val_node:
                                    # The id value is an identifier in the expression statement
                                    for exp_child in val_node.children:
                                        if exp_child.type == 'identifier':
                                            known_components.add(exp_child.text)
        for child in node.children:
            collect_components(child)

    collect_components(tree.root_node)

    issues = []

    # Pass 2: Check createObject calls
    def visit(node):
        if node.type == 'call_expression':
            # Check if it's createObject
            member_expr = None
            for child in node.children:
                if child.type == 'member_expression':
                    member_expr = child
                    break

            if member_expr:
                prop_ident = None
                for child in member_expr.children:
                    if child.type == 'property_identifier':
                        prop_ident = child
                        break

                if prop_ident and prop_ident.text == b'createObject':
                    # Check receiver
                    receiver = None
                    for child in member_expr.children:
                        if child.type == 'identifier':
                            receiver = child
                            break

                    is_component = False
                    if receiver:
                        # Match if the receiver is a known Component ID
                        if receiver.text in known_components:
                            is_component = True

                    if not is_component:
                        # Skip if receiver doesn't resolve to a known component id
                        for child in node.children:
                            visit(child)
                        return

                    # Now check arguments
                    args = None
                    for child in node.children:
                        if child.type == 'arguments':
                            args = child
                            break

                    if args:
                        for arg_child in args.children:
                            if arg_child.type == 'object':
                                # This is the properties object
                                for obj_child in arg_child.children:
                                    if obj_child.type == 'pair':
                                        key_node = obj_child.children[0]
                                        key_text = key_node.text
                                        if key_node.type == 'string':
                                            # Strip quotes
                                            key_text = key_text.strip(b'"\'')
                                        if key_node.type == 'property_identifier' or key_node.type == 'string':
                                            if key_text == b'id':
                                                issues.append(f"{filepath}:{node.start_point[0] + 1}: [custom-qt-kde-lint-reject-id-in-createobject] id is not a runtime QML property and cannot be assigned through Component.createObject(). Remove it; keep the returned object in a JavaScript/property reference if you need to refer to the instance.")

        for child in node.children:
            visit(child)

    visit(tree.root_node)

    return issues

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: qml_linter.py <file1.qml> ...")
        sys.exit(1)

    has_issues = False
    for filepath in sys.argv[1:]:
        issues = check_qml(filepath)
        for issue in issues:
            print(issue)
            has_issues = True

    if has_issues:
        sys.exit(1)
