import sys
import tree_sitter_qmljs
from tree_sitter import Language, Parser

import warnings

class QmlLintContext:
    def __init__(self, filepath, tree):
        self.filepath = filepath
        self.tree = tree
        self.known_components = set()
        self._components_resolved = False
        self.issues = []

    def walk(self, node, callback):
        """Generic AST traversal: visits node and all its descendants recursively."""
        callback(node)
        for child in node.children:
            self.walk(child, callback)

    def find_object_definition(self, node, expected_type):
        '''Find if a node is a UI object definition of a specific type.'''
        if node.type == 'ui_object_definition':
            for child in node.children:
                if child.type == 'identifier' and child.text == expected_type:
                    return True
        return False

    def get_property_binding(self, node, property_name):
        '''Get the value node for a specific property binding in an object initializer.'''
        if node.type == 'ui_object_initializer':
            for stmt in node.children:
                if stmt.type == 'ui_binding':
                    key_node = None
                    val_node = None
                    for binding_child in stmt.children:
                        if binding_child.type == 'identifier':
                            key_node = binding_child
                        elif binding_child.type == 'expression_statement':
                            val_node = binding_child
                    if key_node and key_node.text == property_name and val_node:
                        return val_node
        return None

    def get_call_expression(self, node):
        '''Extract member expression, receiver, and arguments from a call expression.'''
        if node.type != 'call_expression':
            return None, None, None, None

        member_expr = None
        args = None
        for child in node.children:
            if child.type == 'member_expression':
                member_expr = child
            elif child.type == 'arguments':
                args = child

        if not member_expr:
            return None, None, None, None

        receiver = None
        prop_ident = None
        for child in member_expr.children:
            if child.type == 'identifier':
                receiver = child
            elif child.type == 'property_identifier':
                prop_ident = child

        return member_expr, receiver, prop_ident, args

    def find_components(self):
        '''Find and collect known Component IDs in the AST.'''
        if self._components_resolved:
            return self.known_components

        def collect_components(node):
            if self.find_object_definition(node, b'Component'):
                # Find its initializer block `{ ... }`
                for child in node.children:
                    if child.type == 'ui_object_initializer':
                        # Look for an `id` binding
                        val_node = self.get_property_binding(child, b'id')
                        if val_node:
                            # The id value is an identifier in the expression statement
                            for exp_child in val_node.children:
                                if exp_child.type == 'identifier':
                                    self.known_components.add(exp_child.text)

        self.walk(self.tree.root_node, collect_components)
        self._components_resolved = True
        return self.known_components


    def get_local_variable_declaration(self, node):
        '''Extract the variable name and assigned value from a lexical declaration.'''
        if node.type == 'lexical_declaration':
            for child in node.children:
                if child.type == 'variable_declarator':
                    ident = None
                    val = None
                    for var_child in child.children:
                        if var_child.type == 'identifier':
                            ident = var_child
                        elif var_child.type != '=' and var_child.type != 'identifier':
                            val = var_child
                    if ident:
                        return ident, val
        return None, None

    def get_assignment_expression(self, node):
        '''Extract the left and right side of an assignment expression.'''
        if node.type == 'assignment_expression':
            left = None
            right = None
            for child in node.children:
                if child.type == '=':
                    continue
                if not left:
                    left = child
                else:
                    right = child
            return left, right
        return None, None

    def find_all(self, node, node_type, callback):
        '''Walk block/lexical scope finding nodes of a specific type.'''
        if node.type == node_type:
            callback(node)
        for child in node.children:
            self.find_all(child, node_type, callback)


    def report_issue(self, node, rule_name, message):
        """Report a linting issue at the node's location."""
        self.issues.append(f"{self.filepath}:{node.start_point[0] + 1}: [custom-{rule_name}] {message}")

_RULES = []

def register_rule(rule_func):
    _RULES.append(rule_func)
    return rule_func

@register_rule
def qt_kde_lint_reject_id_in_createobject(context):
    context.find_components()

    def visit(node):
        member_expr, receiver, prop_ident, args = context.get_call_expression(node)
        if member_expr and prop_ident and prop_ident.text == b'createObject':
            if receiver and receiver.text in context.known_components:
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
                                            context.report_issue(
                                                node,
                                                "qt-kde-lint-reject-id-in-createobject",
                                                "id is not a runtime QML property and cannot be assigned through Component.createObject(). Remove it; keep the returned object in a JavaScript/property reference if you need to refer to the instance."
                                            )

    context.walk(context.tree.root_node, visit)

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

    context = QmlLintContext(filepath, tree)
    for rule in _RULES:
        rule(context)

    return context.issues

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
