import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

class TestRunRunner(unittest.TestCase):
    def setUp(self):
        self.script_path = Path(__file__).resolve().parent.parent.parent / "tools" / "run.py"

    def test_missing_args(self):
        result = subprocess.run([sys.executable, str(self.script_path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("At least one of --cpp-paths or --qml-paths must be provided.", result.stderr)

    def test_missing_build_dir_for_cpp(self):
        result = subprocess.run([sys.executable, str(self.script_path), "--cpp-paths", "src"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--build-dir is required when --cpp-paths are provided.", result.stderr)

    def test_missing_compile_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([sys.executable, str(self.script_path), "--cpp-paths", "src", "--build-dir", temp_dir], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("compile_commands.json not found", result.stderr)
