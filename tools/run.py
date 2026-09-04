#!/usr/bin/env python3
"""Canonical runner for qt-kde-lint consumer integration."""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

def get_clang_tidy_version(executable: str) -> int:
    try:
        output = subprocess.run([executable, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout
        match = re.search(r"LLVM version (\d+)", output)
        if match:
            return int(match.group(1))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return -1

def run_in_chunks(cmd_base: list, files: list, chunk_size=500) -> bool:
    has_failures = False
    for i in range(0, len(files), chunk_size):
        chunk = files[i:i+chunk_size]
        result = subprocess.run(cmd_base + chunk)
        if result.returncode != 0:
            has_failures = True
    return has_failures

def main() -> int:
    parser = argparse.ArgumentParser(description="Run qt-kde-lint checks on C++ and/or QML sources.")
    parser.add_argument("--build-dir", type=Path, help="Build directory containing compile_commands.json")
    parser.add_argument("--clang-tidy", default="clang-tidy-23", help="clang-tidy executable")
    parser.add_argument("--cpp-paths", nargs="*", default=[], type=str, help="C++ source paths")
    parser.add_argument("--qml-paths", nargs="*", default=[], type=str, help="QML source paths")

    args = parser.parse_args()

    if not args.cpp_paths and not args.qml_paths:
        parser.error("At least one of --cpp-paths or --qml-paths must be provided.")

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    has_failures = False

    if args.cpp_paths:
        if not args.build_dir:
            parser.error("--build-dir is required when --cpp-paths are provided.")

        compile_commands = args.build_dir / "compile_commands.json"
        if not compile_commands.exists():
            print(f"Error: compile_commands.json not found in {args.build_dir}", file=sys.stderr)
            return 1

        version = get_clang_tidy_version(args.clang_tidy)
        if version == -1:
            print(f"Error: clang-tidy executable '{args.clang_tidy}' not found or invalid.", file=sys.stderr)
            return 1
        elif version < 23:
            print(f"Error: qt-kde-lint requires clang-tidy version >= 23, but '{args.clang_tidy}' is version {version}.", file=sys.stderr)
            return 1

        cpp_files = []
        for path_str in args.cpp_paths:
            path = Path(path_str)
            if path.is_file():
                cpp_files.append(str(path))
            elif path.is_dir():
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.endswith((".cpp", ".cc", ".cxx")):
                            cpp_files.append(os.path.join(root, file))

        if not cpp_files:
            print("No C++ files found in the provided --cpp-paths.", file=sys.stderr)
            return 1

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "qt-kde-lint.clang-tidy"
            build_config_cmd = [
                sys.executable, str(script_dir / "build_config.py"),
                "--rules-dir", str(repo_root / "rules"),
                "--output", str(config_file)
            ]
            try:
                subprocess.run(build_config_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except subprocess.CalledProcessError:
                print("Error: Failed to generate clang-tidy configuration.", file=sys.stderr)
                return 1

            clang_tidy_cmd = [
                args.clang_tidy,
                "--experimental-custom-checks",
                f"--config-file={config_file}",
                "-p", str(args.build_dir)
            ]

            if run_in_chunks(clang_tidy_cmd, cpp_files):
                has_failures = True

    if args.qml_paths:
        try:
            import tree_sitter_qmljs
        except ImportError:
            print("Error: Python QML parser dependencies are unavailable. Please install them.", file=sys.stderr)
            return 1

        qml_files = []
        for path_str in args.qml_paths:
            path = Path(path_str)
            if path.is_file():
                qml_files.append(str(path))
            elif path.is_dir():
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.endswith(".qml"):
                            qml_files.append(os.path.join(root, file))

        if not qml_files:
            print("No QML files found in the provided --qml-paths.", file=sys.stderr)
            return 1

        qml_linter_cmd = [
            sys.executable, str(script_dir / "qml_linter.py")
        ]

        if run_in_chunks(qml_linter_cmd, qml_files):
            has_failures = True

    return 1 if has_failures else 0

if __name__ == "__main__":
    sys.exit(main())
