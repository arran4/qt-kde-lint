1. **Fix Member Assignment Escape:**
   - In `tools/qml_linter.py`, when handling `assignment_expression` where `right` is `var_text`:
     - If `left` is `identifier` and `left.text` is in `local_vars`, NOT safe.
     - If `left` is `member_expression`:
       - Find the root receiver of this member expression. For example, in `holder.value.foo`, `holder` is the root.
       - If the root receiver is an `identifier` and its `text` is in `local_vars`, it means the assignment is to a property of a local object. This should NOT be safe.
       - Otherwise, it is safe (assignment to a non-local property).
     - Otherwise, it is safe (non-local variable).

2. **Add Fixtures:**
   - BAD fixture: `bad_local_member_alias.qml` testing `let holder = {}; let p = ...; holder.value = p`.
   - GOOD fixture: `good_nonlocal_member_assignment.qml` testing `rootItem.saved = p`.

3. **Tests:**
   - Run the tests.

4. **Reply & Submit.**
