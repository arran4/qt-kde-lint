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


    def get_implications(node, var_name, assumption):
        while node.type == 'parenthesized_expression':
            for c in node.children:
                if c.type not in ('(', ')'):
                    node = c
                    break

        if node.type == 'identifier' and node.text == var_name:
            if assumption == 'truthy':
                return 'proves_non_null'
            return 'unknown'

        if node.type == 'unary_expression':
            op = None
            arg = None
            for c in node.children:
                if c.type == '!': op = c
                elif c.type not in ('!', 'comment'): arg = c
            if op and arg:
                if assumption == 'truthy':
                    return get_implications(arg, var_name, 'falsy')
                else:
                    return get_implications(arg, var_name, 'truthy')

        if node.type == 'binary_expression':
            left = None
            op = None
            right = None
            for c in node.children:
                if c.type in ('!=', '!==', '==', '===', '&&', '||'): op = c
            if op:
                left = node.children[0]
                right = node.children[-1]

                if op.type in ('&&', '||'):
                    if op.type == '&&':
                        if assumption == 'truthy':
                            l_imp = get_implications(left, var_name, 'truthy')
                            if l_imp != 'unknown': return l_imp
                            return get_implications(right, var_name, 'truthy')
                        else:
                            l_imp = get_implications(left, var_name, 'falsy')
                            r_imp = get_implications(right, var_name, 'falsy')
                            if l_imp != 'unknown' and l_imp == r_imp: return l_imp
                            return 'unknown'
                    elif op.type == '||':
                        if assumption == 'falsy':
                            l_imp = get_implications(left, var_name, 'falsy')
                            if l_imp != 'unknown': return l_imp
                            return get_implications(right, var_name, 'falsy')
                        else:
                            l_imp = get_implications(left, var_name, 'truthy')
                            r_imp = get_implications(right, var_name, 'truthy')
                            if l_imp != 'unknown' and l_imp == r_imp: return l_imp
                            return 'unknown'

                if op.type in ('!=', '!==', '==', '==='):
                    is_var_null_check = False
                    if (left.type == 'identifier' and left.text == var_name and (right.type == 'null' or right.text == b'null')) or                        (right.type == 'identifier' and right.text == var_name and (left.type == 'null' or left.text == b'null')):
                        is_var_null_check = True

                    if is_var_null_check:
                        if op.type in ('!=', '!=='):
                            if assumption == 'truthy':
                                return 'proves_non_null'
                            else:
                                return 'proves_null'
                        else:
                            if assumption == 'truthy':
                                return 'proves_null'
                            else:
                                return 'proves_non_null'

        return 'unknown'

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

                                    def find_refs(n, out_issues, proven_non_null=False):
                                        if n.type in ('assignment_expression', 'augmented_assignment_expression'):
                                            left = n.children[0]
                                            if left.type == 'identifier' and left.text == var_name:
                                                right = n.children[-1] if len(n.children) > 2 else None
                                                if right:
                                                    find_refs(right, out_issues, proven_non_null)
                                                return "ELIMINATED"

                                        if n.type == 'binary_expression':
                                            op_node = None
                                            for c in n.children:
                                                if c.type in ('&&', '||'): op_node = c
                                            if op_node:
                                                left = n.children[0]
                                                right = n.children[-1]

                                                left_state = find_refs(left, out_issues, proven_non_null)
                                                if left_state != "LIVE":
                                                    return left_state

                                                if op_node.type == '&&':
                                                    l_imp = get_implications(left, var_name, 'truthy')
                                                    right_proven = proven_non_null or (l_imp == 'proves_non_null')
                                                    right_state = find_refs(right, out_issues, right_proven)
                                                    if right_state != "LIVE":
                                                        return right_state
                                                    return "LIVE"
                                                elif op_node.type == '||':
                                                    l_imp = get_implications(left, var_name, 'falsy')
                                                    right_proven = proven_non_null or (l_imp == 'proves_non_null')
                                                    right_state = find_refs(right, out_issues, right_proven)
                                                    if right_state != "LIVE":
                                                        return right_state
                                                    return "LIVE"

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

                                            if cond:
                                                cond_state = find_refs(cond, out_issues, proven_non_null)
                                                if cond_state != "LIVE":
                                                    return cond_state

                                                cond_truthy = get_implications(cond, var_name, 'truthy')
                                                cond_falsy = get_implications(cond, var_name, 'falsy')
                                            else:
                                                cond_truthy = 'unknown'
                                                cond_falsy = 'unknown'

                                            cons_state = "LIVE"
                                            alt_state = "LIVE"

                                            cons_issues = []
                                            alt_issues = []

                                            cons_proven = proven_non_null or (cond_truthy == 'proves_non_null')
                                            alt_proven = proven_non_null or (cond_falsy == 'proves_non_null')

                                            if consequence:
                                                cons_state = find_refs(consequence, cons_issues, cons_proven)
                                                if always_returns(consequence):
                                                    cons_state = "EXITED"
                                            else:
                                                if cond_truthy == 'proves_non_null':
                                                    cons_state = "ELIMINATED"

                                            if alternative:
                                                alt_state = find_refs(alternative, alt_issues, alt_proven)
                                                if always_returns(alternative):
                                                    alt_state = "EXITED"
                                            else:
                                                if cond_falsy == 'proves_non_null':
                                                    alt_state = "ELIMINATED"

                                            if cond_truthy == 'proves_non_null':
                                                cons_issues.clear()
                                                if consequence and always_returns(consequence):
                                                    cons_state = "EXITED"
                                                elif cons_state != "EXITED":
                                                    cons_state = "ELIMINATED"
                                            elif cond_falsy == 'proves_non_null':
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
                                                find_refs(child, out_issues, proven_non_null)
                                            return "LIVE"

                                        if n.type in ('do_statement', 'try_statement'):
                                            for child in n.children:
                                                find_refs(child, out_issues, proven_non_null)
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
                                                if not is_optional and not proven_non_null:
                                                    out_issues.append(n)

                                        for child in n.children:
                                            child_state = find_refs(child, out_issues, proven_non_null)
                                            if child_state != "LIVE":
                                                return child_state

                                        return "LIVE"


                                    out_issues = []

                                    if sibling.type == 'expression_statement' and sibling.children[0].type in ('assignment_expression', 'augmented_assignment_expression'):
                                        left = sibling.children[0].children[0]
                                        if left.type == 'identifier' and left.text == var_name:
                                            right = sibling.children[0].children[-1] if len(sibling.children[0].children) > 2 else None
                                            if right:
                                                find_refs(right, out_issues, False)
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

    # Collect all IDs in the file to know what is a "long-lived" parent
    all_ids = set()
    def collect_ids(node):
        if node.type == 'ui_object_initializer':
            val_node = context.get_property_binding(node, b'id')
            if val_node:
                for exp_child in val_node.children:
                    if exp_child.type == 'identifier':
                        all_ids.add(exp_child.text)
    context.walk(context.tree.root_node, collect_ids)

    def is_long_lived_parent(node):
        if node.type == 'identifier':
            # parent is considered long-lived
            if node.text == b'parent':
                return True
            # known IDs are considered long-lived
            if node.text in all_ids:
                return True
        return False

    def is_repeatable_handler(node):
        if node.type == 'ui_binding':
            ident = node.children[0]
            if ident.type == 'identifier':
                text = ident.text.decode('utf-8')
                if text in ('onClicked', 'onTapped', 'onTriggered', 'onPressed', 'onReleased', 'onDoubleClicked', 'onPressAndHold'):
                    return True
        return False

    def is_qt_create_component(call_node):
        # Qt.createComponent("...")
        if call_node.type == 'call_expression':
            member_expr, receiver, prop_ident, args = context.get_call_expression(call_node)
            if member_expr and prop_ident and prop_ident.text == b'createComponent':
                if receiver and receiver.text == b'Qt':
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

        # track local variables in this block
        local_vars = set()
        def collect_locals(n):
            if n.type in ('lexical_declaration', 'variable_declaration'):
                var_name, _ = context.get_local_variable_declaration(n)
                if var_name:
                    local_vars.add(var_name.text)
        context.walk(stmt_block, collect_locals)

        def find_leaks(n):
            if n.type in ('lexical_declaration', 'variable_declaration'):
                var_name, var_val = context.get_local_variable_declaration(n)
                if var_name and var_val and var_val.type == 'call_expression':
                    member_expr, receiver, prop_ident, args = context.get_call_expression(var_val)
                    is_creation = False
                    parent_arg = None

                    if member_expr and prop_ident and prop_ident.text == b'createObject':
                        if args and len(args.children) > 2: # '(' arg ')'
                            parent_arg = args.children[1]

                        # case 1: known component ID
                        if receiver and receiver.text in context.known_components:
                            is_creation = True

                        # case 2: Qt.createComponent(...).createObject(...)
                        elif receiver and receiver.type == 'call_expression':
                            if is_qt_create_component(receiver):
                                is_creation = True

                        # case 3: local variable that holds Qt.createComponent
                        elif receiver and receiver.type == 'identifier' and receiver.text in local_vars:
                            # Verify if it was assigned Qt.createComponent
                            def find_assignment(v_n):
                                if v_n.type in ('lexical_declaration', 'variable_declaration'):
                                    v_name, v_val_n = context.get_local_variable_declaration(v_n)
                                    if v_name and v_name.text == receiver.text and v_val_n and v_val_n.type == 'call_expression':
                                        if is_qt_create_component(v_val_n):
                                            return True
                                return False

                            is_comp = False
                            def walk_and_find(sn):
                                nonlocal is_comp
                                if find_assignment(sn):
                                    is_comp = True
                            context.walk(stmt_block, walk_and_find)
                            if is_comp:
                                is_creation = True

                        # case 4: member expression directly e.g. Qt.createComponent("...").createObject(parent)
                        elif member_expr and member_expr.children[0].type == 'call_expression':
                            if is_qt_create_component(member_expr.children[0]):
                                is_creation = True

                    if is_creation:
                        if not parent_arg or not is_long_lived_parent(parent_arg):
                            # if parent is not clearly long-lived, we do NOT warn (conservative)
                            return

                        var_text = var_name.text
                        is_safe = False

                        def find_uses(u):
                            nonlocal is_safe
                            if is_safe: return

                            # Check direct call: u.destroy()
                            if u.type == 'call_expression':
                                m_expr, rec, p_ident, func_args = context.get_call_expression(u)
                                if rec and rec.text == var_text and p_ident and p_ident.text == b'destroy':
                                    is_safe = True
                                    return

                                # Check if it's `.connect(var.destroy)`
                                if p_ident and p_ident.text == b'connect' and func_args:
                                    for arg_child in func_args.children:
                                        if arg_child.type == 'member_expression':
                                            if len(arg_child.children) >= 3:
                                                r = arg_child.children[0]
                                                p = arg_child.children[-1]
                                                if r.type == 'identifier' and r.text == var_text and p.type == 'property_identifier' and p.text == b'destroy':
                                                    is_safe = True
                                                    return

                            # Check assignment to another variable/property
                            if u.type in ('assignment_expression', 'augmented_assignment_expression'):
                                right = u.children[-1]
                                left = u.children[0]
                                if right.type == 'identifier' and right.text == var_text:
                                    # ONLY safe if assigning to a NON-LOCAL property/variable
                                    if left.type == 'identifier':
                                        if left.text in local_vars:
                                            # local alias, not safe
                                            pass
                                        else:
                                            is_safe = True
                                            return
                                    elif left.type == 'member_expression':
                                        # find root receiver of member expression
                                        root = left
                                        while root.type == 'member_expression' and len(root.children) > 0:
                                            root = root.children[0]
                                        if root.type == 'identifier' and root.text in local_vars:
                                            # member of a local variable, not safe
                                            pass
                                        else:
                                            is_safe = True
                                            return
                                    else:
                                        is_safe = True
                                        return

                            # Check if it is passed to array.push() or similar that escapes scope
                            if u.type == 'call_expression':
                                m_expr, rec, p_ident, func_args = context.get_call_expression(u)
                                if func_args:
                                    for arg_child in func_args.children:
                                        if arg_child.type == 'identifier' and arg_child.text == var_text:
                                            # Is it a method call on a known retaining object? e.g. myArray.push(u)
                                            if m_expr and p_ident and p_ident.text in (b'push', b'append', b'insert'):
                                                # Need to find root of rec if it's a member expression
                                                root_rec = rec
                                                while root_rec and root_rec.type == 'member_expression' and len(root_rec.children) > 0:
                                                    root_rec = root_rec.children[0]
                                                if root_rec and root_rec.type == 'identifier' and root_rec.text not in local_vars:
                                                    is_safe = True
                                                    return

                        context.walk(stmt_block, find_uses)

                        if not is_safe:
                            context.report_issue(
                                n,
                                "qt-kde-lint-qml-transient-object-leak",
                                "Transient object created via createObject() under a long-lived parent in a repeatable handler without an explicit destruction path or scope escape. This may cause memory leaks across multiple interactions."
                            )

        context.walk(stmt_block, find_leaks)

    context.walk(context.tree.root_node, visit)


@register_rule
def qt_kde_lint_action_semantic_context(context):
    def visit(node):
        if node.type == 'ui_object_definition':
            # Check if this object is an Action or Kirigami.Action strictly
            is_action = False
            for child in node.children:
                if child.type == 'identifier' and child.text == b'Action':
                    is_action = True
                    break
                elif child.type == 'nested_identifier':
                    # Check strictly for Kirigami.Action
                    parts = []
                    def get_parts(n):
                        if n.type == 'identifier':
                            parts.append(n.text)
                        for c in n.children:
                            get_parts(c)
                    get_parts(child)
                    if parts == [b'Kirigami', b'Action']:
                        is_action = True
                        break

            if is_action:
                # Find its text property
                for child in node.children:
                    if child.type == 'ui_object_initializer':
                        val_node = context.get_property_binding(child, b'text')
                        if val_node:
                            # val_node is an expression_statement
                            for exp_child in val_node.children:
                                if exp_child.type == 'call_expression':
                                    ident = exp_child.children[0]
                                    if ident.type == 'identifier' and ident.text in (b'i18n', b'i18nd', b'ki18n', b'ki18nd'):
                                        # Determine the suggested function
                                        call_name = ident.text.decode('utf-8')
                                        sugg = call_name.replace('i18n', 'i18nc')
                                        if call_name == 'i18nd': sugg = 'i18ndc'
                                        if call_name == 'ki18nd': sugg = 'ki18ndc'
                                        if call_name == 'ki18n': sugg = 'ki18nc'
                                        # Actually it's simple: just append 'c' to the call name
                                        sugg = call_name + 'c'

                                        # It's missing context
                                        context.report_issue(
                                            exp_child,
                                            "qt-kde-lint-action-semantic-context",
                                            f'UI action labels translated with plain {call_name}() lack semantic context. Prefer {sugg}() with a semantic context such as "@action" to aid translators.'
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
