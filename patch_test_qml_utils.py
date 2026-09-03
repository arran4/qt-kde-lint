import re

with open('tests/qml_harness/test_qml_linter_utils.py', 'r') as f:
    content = f.read()

# Make sure the import works regardless of where the test is run
content = content.replace("sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tools')))",
                         "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'tools')))")

with open('tests/qml_harness/test_qml_linter_utils.py', 'w') as f:
    f.write(content)
