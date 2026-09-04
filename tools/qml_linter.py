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
        """Extract the variable name and assigned value from a lexical/variable declaration.

        Note: If a declaration contains multiple variables (e.g. `let x = 1, y = 2`),
        this helper currently only returns the first one.
        """
        if node.type in ('lexical_declaration', 'variable_declaration'):
            for child in node.children:
                if child.type == 'variable_declarator':
                    ident = None
                    val = None
                    for var_child in child.children:
                        if var_child.type == 'identifier':
                            ident = var_child
                        elif var_child.type == '=':
                            continue
                        else:
                            val = var_child
                    if ident:
                        return ident, val
        return None, None



    def get_assignment_expression(self, node):
        """Extract the left and right side of a plain assignment expression.

        Returns (left_node, right_node) if this is a plain '=' assignment.
        Returns (None, None) for compound assignments (e.g. '+=') or non-assignments.
        """
        if node.type == 'augmented_assignment_expression':
            return None, None

        if node.type == 'assignment_expression':
            left = None
            right = None
            is_plain_assignment = False
            for child in node.children:
                if child.type == '=':
                    is_plain_assignment = True
                    continue
                # If we hit an operator like '+=' or '-=', it's not a plain assignment
                if child.type in ('+=', '-=', '*=', '/=', '%=', '<<=', '>>=', '>>>=', '&=', '^=', '|='):
                    return None, None

                if not left:
                    left = child
                else:
                    right = child
            if is_plain_assignment:
                return left, right
        return None, None



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


@register_rule
def qt_kde_lint_qml_component_createobject_null_dereference(context):
    context.find_components()

    def visit(node):
        if node.type == 'call_expression':
            member_expr, receiver, prop_ident, args = context.get_call_expression(node)
            if member_expr and prop_ident and prop_ident.text == b'createObject':
                if receiver and receiver.text in context.known_components:
                    # Check parent hierarchy for member_expression, ignoring parenthesized_expression
                    parent = node.parent
                    while parent and parent.type == 'parenthesized_expression':
                        parent = parent.parent

                    if parent and parent.type == 'member_expression':
                        is_optional = False
                        for child in parent.children:
                            if child.type == 'optional_chain' or child.text == b'?.':
                                is_optional = True
                                break
                        if not is_optional:
                            context.report_issue(
                                node,
                                "qt-kde-lint-qml-component-createobject-null-dereference",
                                "Component.createObject() can return null. Check the result (or use a null-safe operation) before accessing the dynamically created object."
                            )

        var_name = None
        val_expr = None

        ident, val = context.get_local_variable_declaration(node)
        if ident and val:
            var_name = ident.text
            val_expr = val
        elif node.type == 'expression_statement':
            for child in node.children:
                if child.type == 'assignment_expression':
                    left, right = context.get_assignment_expression(child)
                    if left and left.type == 'identifier' and right:
                        var_name = left.text
                        val_expr = right

        if var_name and val_expr:
            # Strip parenthesized expressions from val_expr
            while val_expr.type == 'parenthesized_expression':
                for child in val_expr.children:
                    if child.type != '(' and child.type != ')':
                        val_expr = child
                        break

            if val_expr.type == 'call_expression':
                member_expr, receiver, prop_ident, args = context.get_call_expression(val_expr)
                if member_expr and prop_ident and prop_ident.text == b'createObject':
                    if receiver and receiver.text in context.known_components:
                        parent = node.parent
                        if parent and parent.type in ('statement_block', 'program'):
                            siblings = parent.children
                            try:
                                idx = siblings.index(node)
                            except ValueError:
                                idx = -1

                            if idx != -1:
                                for i in range(idx + 1, len(siblings)):
                                    sibling = siblings[i]

                                    def find_refs(n, refs):
                                        if n.type == 'if_statement':
                                            cond = None
                                            for c in n.children:
                                                if c.type == 'parenthesized_expression':
                                                    cond = c
                                                    break

                                            mentions_var = [False]
                                            def check_mention(nn):
                                                if nn.type == 'identifier' and nn.text == var_name:
                                                    mentions_var[0] = True
                                            if cond:
                                                context.walk(cond, check_mention)

                                            if mentions_var[0]:
                                                is_negated = [False]
                                                def check_neg(nn):
                                                    if nn.type == 'unary_expression':
                                                        for c in nn.children:
                                                            if c.type == '!' or c.text == b'!':
                                                                is_negated[0] = True
                                                context.walk(cond, check_neg)

                                                has_return = [False]
                                                def check_return(nn):
                                                    if nn.type == 'return_statement':
                                                        has_return[0] = True
                                                context.walk(n, check_return)

                                                if has_return[0] and is_negated[0]:
                                                    refs['early_return'] = True
                                                else:
                                                    refs['guarded'] = True
                                                return

                                        if n.type == 'member_expression':
                                            rec = None
                                            for c in n.children:
                                                if c.type == 'identifier':
                                                    rec = c
                                                    break
                                            if rec and rec.text == var_name:
                                                is_optional = False
                                                for c in n.children:
                                                    if c.type == 'optional_chain' or c.text == b'?.':
                                                        is_optional = True
                                                        break
                                                if not is_optional:
                                                    refs['unsafe_derefs'].append(n)

                                        for child in n.children:
                                            find_refs(child, refs)

                                    refs = {'unsafe_derefs': [], 'early_return': False, 'guarded': False}
                                    find_refs(sibling, refs)

                                    if refs['early_return']:
                                        break

                                    if refs['guarded']:
                                        pass
                                    elif refs['unsafe_derefs']:
                                        context.report_issue(
                                            sibling,
                                            "qt-kde-lint-qml-component-createobject-null-dereference",
                                            "Component.createObject() can return null. Check the result (or use a null-safe operation) before accessing the dynamically created object."
                                        )
                                        break


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
