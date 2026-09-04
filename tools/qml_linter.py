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

    def always_returns(node):
        if node.type in ('return_statement', 'throw_statement', 'break_statement', 'continue_statement'):
            return True
        if node.type in ('statement_block', 'else_clause'):
            for c in node.children:
                if always_returns(c):
                    return True
        if node.type == 'if_statement':
            cons = None
            alt = None
            for c in node.children:
                if c.type not in ('if', 'else', 'parenthesized_expression', 'comment'):
                    if cons is None:
                        cons = c
                    else:
                        alt = c
            if cons and alt:
                return always_returns(cons) and always_returns(alt)
            return False
        return False

    def is_shadowed(node, name):
        curr = node.parent
        while curr:
            if curr.type in ('statement_block', 'program'):
                for c in curr.children:
                    if c.type in ('lexical_declaration', 'variable_declaration'):
                        for decl in c.children:
                            if decl.type == 'variable_declarator':
                                ident = decl.children[0]
                                if ident.type == 'identifier' and ident.text == name:
                                    return True
                    if c.type == 'function_declaration':
                        for f_child in c.children:
                            if f_child.type == 'identifier' and f_child.text == name:
                                return True
            elif curr.type == 'function_declaration':
                for c in curr.children:
                    if c.type == 'formal_parameters':
                        for param in c.children:
                            if param.type == 'identifier' and param.text == name:
                                return True
                            if param.type == 'assignment_pattern':
                                if param.children[0].type == 'identifier' and param.children[0].text == name:
                                    return True
            elif curr.type == 'ui_object_initializer':
                for c in curr.children:
                    if c.type == 'ui_property':
                        for p_child in c.children:
                            if p_child.type == 'identifier' and p_child.text == name:
                                return True
            curr = curr.parent
        return False

    def visit(node):
        if node.type == 'call_expression':
            member_expr, receiver, prop_ident, args = context.get_call_expression(node)
            if member_expr and prop_ident and prop_ident.text == b'createObject':
                if receiver and receiver.text in context.known_components:
                    if is_shadowed(node, receiver.text):
                        pass
                    else:
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
                if child.type in ('assignment_expression', 'augmented_assignment_expression'):
                    left = child.children[0]
                    right = child.children[-1] if len(child.children) > 2 else None
                    if left.type == 'identifier' and right:
                        var_name = left.text
                        val_expr = right

        if var_name and val_expr:
            while val_expr.type == 'parenthesized_expression':
                for child in val_expr.children:
                    if child.type != '(' and child.type != ')':
                        val_expr = child
                        break

            if val_expr.type == 'call_expression':
                member_expr, receiver, prop_ident, args = context.get_call_expression(val_expr)
                if member_expr and prop_ident and prop_ident.text == b'createObject':
                    if receiver and receiver.text in context.known_components:
                        if is_shadowed(val_expr, receiver.text):
                            return
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

                                    # State tracked per path branch
                                    # LIVE: Original nullable value may reach here
                                    # ELIMINATED: Reassigned or explicitly proven non-null
                                    # EXITED: Flow exits (return/break/throw)
                                    # UNCERTAIN: Flow uncertainty creates an analysis barrier

                                    def find_refs(n, out_issues):
                                        if n.type in ('assignment_expression', 'augmented_assignment_expression'):
                                            left = n.children[0]
                                            if left.type == 'identifier' and left.text == var_name:
                                                right = n.children[-1] if len(n.children) > 2 else None
                                                if right:
                                                    find_refs(right, out_issues)
                                                return "ELIMINATED"

                                        if n.type == 'if_statement':
                                            cond = None
                                            consequence = None
                                            alternative = None

                                            for c in n.children:
                                                if c.type == 'parenthesized_expression':
                                                    cond = c
                                                elif c.type not in ('if', 'else', 'parenthesized_expression', 'comment'):
                                                    if consequence is None:
                                                        consequence = c
                                                    else:
                                                        alternative = c

                                            cond_status = 'unknown'
                                            if cond:
                                                expr = cond
                                                while expr.type == 'parenthesized_expression':
                                                    for c in expr.children:
                                                        if c.type not in ('(', ')'):
                                                            expr = c
                                                            break

                                                def safe_cond_derefs(cond_node):
                                                    if cond_node.type == 'binary_expression':
                                                        op_node = None
                                                        for c in cond_node.children:
                                                            if c.type in ('&&', '||'): op_node = c
                                                        if op_node:
                                                            if op_node.type == '&&':
                                                                left_cond = cond_node.children[0]
                                                                is_left_proves_non_null = False
                                                                if left_cond.type == 'identifier' and left_cond.text == var_name:
                                                                    is_left_proves_non_null = True
                                                                elif left_cond.type == 'binary_expression':
                                                                    for c in left_cond.children:
                                                                        if c.type in ('!=', '!=='):
                                                                            l2 = left_cond.children[0]
                                                                            r2 = left_cond.children[-1]
                                                                            if (l2.type == 'identifier' and l2.text == var_name and (r2.type == 'null' or r2.text == b'null')) or (r2.type == 'identifier' and r2.text == var_name and (l2.type == 'null' or l2.text == b'null')):
                                                                                is_left_proves_non_null = True
                                                                                break
                                                                if is_left_proves_non_null:
                                                                    return True
                                                    return False

                                                if safe_cond_derefs(expr):
                                                    cond_status = 'proves_non_null'
                                                else:
                                                    cond_state = find_refs(cond, out_issues)
                                                    if cond_state != "LIVE":
                                                        return cond_state

                                                if cond_status == 'unknown':
                                                    if expr.type == 'identifier' and expr.text == var_name:
                                                        cond_status = 'proves_non_null'
                                                    elif expr.type == 'unary_expression':
                                                        op = None
                                                        arg = None
                                                        for c in expr.children:
                                                            if c.type == '!': op = c
                                                            elif c.type == 'identifier': arg = c
                                                        if op and arg and arg.text == var_name:
                                                            cond_status = 'proves_null'
                                                    elif expr.type == 'binary_expression':
                                                        left = None
                                                        op = None
                                                        right = None
                                                        for c in expr.children:
                                                            if c.type in ('==', '===', '!=', '!=='):
                                                                op = c
                                                            elif not op:
                                                                left = c
                                                            else:
                                                                right = c
                                                        if left and right and op:
                                                            is_left_var = (left.type == 'identifier' and left.text == var_name)
                                                            is_right_var = (right.type == 'identifier' and right.text == var_name)
                                                            is_left_null = (left.type == 'null' or left.text == b'null')
                                                            is_right_null = (right.type == 'null' or right.text == b'null')

                                                            if (is_left_var and is_right_null) or (is_left_null and is_right_var):
                                                                if op.type in ('==', '==='):
                                                                    cond_status = 'proves_null'
                                                                elif op.type in ('!=', '!=='):
                                                                    cond_status = 'proves_non_null'

                                            cons_state = "LIVE"
                                            alt_state = "LIVE"

                                            cons_issues = []
                                            alt_issues = []

                                            if consequence:
                                                cons_state = find_refs(consequence, cons_issues)
                                                if always_returns(consequence):
                                                    cons_state = "EXITED"
                                            else:
                                                if cond_status == 'proves_non_null':
                                                    cons_state = "ELIMINATED"

                                            if alternative:
                                                alt_state = find_refs(alternative, alt_issues)
                                                if always_returns(alternative):
                                                    alt_state = "EXITED"
                                            else:
                                                if cond_status == 'proves_null':
                                                    alt_state = "ELIMINATED"

                                            if cond_status == 'proves_non_null':
                                                cons_issues.clear()
                                                if consequence and always_returns(consequence):
                                                    cons_state = "EXITED"
                                                elif cons_state != "EXITED":
                                                    cons_state = "ELIMINATED"
                                            elif cond_status == 'proves_null':
                                                alt_issues.clear()
                                                if alternative and always_returns(alternative):
                                                    alt_state = "EXITED"
                                                elif alt_state != "EXITED":
                                                    alt_state = "ELIMINATED"

                                            out_issues.extend(cons_issues)
                                            out_issues.extend(alt_issues)

                                            if cons_state == "UNCERTAIN" or alt_state == "UNCERTAIN":
                                                return "UNCERTAIN"

                                            if cons_state in ("ELIMINATED", "EXITED") and alt_state in ("ELIMINATED", "EXITED"):
                                                if cons_state == "EXITED" and alt_state == "EXITED":
                                                    return "EXITED"
                                                return "ELIMINATED"

                                            return "LIVE"

                                        if n.type in ('while_statement', 'for_statement', 'for_in_statement', 'switch_statement'):
                                            for child in n.children:
                                                find_refs(child, out_issues)
                                            return "LIVE"

                                        if n.type in ('do_statement', 'try_statement'):
                                            for child in n.children:
                                                find_refs(child, out_issues)
                                            return "UNCERTAIN"

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
                                                    out_issues.append(n)

                                        for child in n.children:
                                            child_state = find_refs(child, out_issues)
                                            if child_state != "LIVE":
                                                return child_state

                                        return "LIVE"

                                    out_issues = []

                                    if sibling.type == 'expression_statement' and sibling.children[0].type in ('assignment_expression', 'augmented_assignment_expression'):
                                        left = sibling.children[0].children[0]
                                        if left.type == 'identifier' and left.text == var_name:
                                            right = sibling.children[0].children[-1] if len(sibling.children[0].children) > 2 else None
                                            if right:
                                                find_refs(right, out_issues)
                                            break
                                        else:
                                            state = find_refs(sibling, out_issues)
                                    else:
                                        state = find_refs(sibling, out_issues)

                                    if out_issues:
                                        context.report_issue(
                                            sibling,
                                            "qt-kde-lint-qml-component-createobject-null-dereference",
                                            "Component.createObject() can return null. Check the result (or use a null-safe operation) before accessing the dynamically created object."
                                        )
                                        break

                                    if state in ("ELIMINATED", "EXITED", "UNCERTAIN"):
                                        break


    context.walk(context.tree.root_node, visit)


@register_rule
def qt_kde_lint_qml_transient_object_leak(context):
    context.find_components()

    def is_repeatable_handler(node):
        if node.type == 'ui_binding':
            ident = node.children[0]
            if ident.type == 'identifier':
                text = ident.text.decode('utf-8')
                if text in ('onClicked', 'onTapped', 'onTriggered', 'onPressed', 'onReleased', 'onDoubleClicked', 'onPressAndHold'):
                    return True
        return False

    def visit(node):
        if not is_repeatable_handler(node):
            return

        stmt_block = None
        for child in node.children:
            if child.type == 'statement_block':
                stmt_block = child
                break

        if not stmt_block:
            return

        def find_leaks(n):
            if n.type in ('lexical_declaration', 'variable_declaration'):
                var_name, var_val = context.get_local_variable_declaration(n)
                if var_name and var_val and var_val.type == 'call_expression':
                    member_expr, receiver, prop_ident, args = context.get_call_expression(var_val)
                    if member_expr and prop_ident and prop_ident.text == b'createObject':
                        if receiver and receiver.text in context.known_components:
                            var_text = var_name.text
                            is_safe = False

                            def find_uses(u):
                                nonlocal is_safe
                                if is_safe: return

                                # Check direct call: u.destroy()
                                if u.type == 'call_expression':
                                    m_expr, rec, p_ident, _ = context.get_call_expression(u)
                                    if rec and rec.text == var_text and p_ident and p_ident.text == b'destroy':
                                        is_safe = True
                                        return

                                # Check assignment to another variable/property
                                if u.type in ('assignment_expression', 'augmented_assignment_expression'):
                                    right = u.children[-1]
                                    if right.type == 'identifier' and right.text == var_text:
                                        is_safe = True
                                        return

                                # Check if it is passed to array.push() or similar that escapes scope
                                if u.type == 'call_expression':
                                    _, _, _, func_args = context.get_call_expression(u)
                                    if func_args:
                                        for arg_child in func_args.children:
                                            if arg_child.type == 'identifier' and arg_child.text == var_text:
                                                is_safe = True
                                                return

                                # Check m.onClosed.connect(m.destroy) or similar property access
                                if u.type == 'member_expression':
                                    if len(u.children) >= 3:
                                        rec = u.children[0]
                                        prop = u.children[-1]
                                        if rec.type == 'identifier' and rec.text == var_text and prop.type == 'property_identifier' and prop.text == b'destroy':
                                            is_safe = True
                                            return

                            context.walk(stmt_block, find_uses)

                            if not is_safe:
                                context.report_issue(
                                    n,
                                    "qt-kde-lint-qml-transient-object-leak",
                                    "Transient object created via Component.createObject() in a repeatable handler without an explicit destruction path or scope escape. This may cause memory leaks across multiple interactions."
                                )

        context.walk(stmt_block, find_leaks)

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
