import ast
import os
import subprocess
import json
import re
from natrix.ast_node import Node

VYPER_VERSION = "0.4.0"


def _check_vyper_version():
    """
    Check if vyper is installed and at the required version.
    Raises an exception if vyper is not available or not at the correct version.
    """
    try:
        result = subprocess.run(["vyper", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception("Vyper compiler not available")

        # Extract version number
        version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
        if not version_match:
            raise Exception("Could not determine Vyper version")

        version = version_match.group(1)
        if version != VYPER_VERSION:
            raise Exception(f"Vyper version must be {VYPER_VERSION}, found {version}")
    except FileNotFoundError:
        raise Exception(
            f"Vyper compiler not found. Please ensure Vyper {VYPER_VERSION} is installed and available in your PATH."
        )


def _obtain_sys_path():
    """
    Obtain all the system paths in which the compiler would
    normally look for modules. This allows to lint vyper files
    that import a module that is installed as a virtual environment
    dependency.
    """
    command = ["python", "-c", "import sys; print(sys.path)"]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    # Remove the first element of the list which is an empty string.
    paths = ast.literal_eval(stdout)[1:]

    # Remove paths that do not exist as the vyper compiler will throw an error.
    valid_paths = [path for path in paths if os.path.exists(path)]

    return valid_paths


def vyper_compile(filename, formatting):
    _check_vyper_version()

    # For each path add a '-p /the/path' flag to the compiler
    paths = [item for p in _obtain_sys_path() for item in ["-p", p]]
    command = ["vyper", "-f", formatting, filename] + paths

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    try:
        return json.loads(stdout)
    except Exception:
        # TODO change error level
        raise Exception(
            f"Something went wrong when compiling the vyper file '{filename}'. The compiler returned the following error: \n {stderr}"
        )


def parse_file(file_path):
    ast = vyper_compile(file_path, "annotated_ast")
    metadata = vyper_compile(file_path, "metadata")

    ast["metadata"] = metadata
    return ast


class VyperASTVisitor:
    def visit(self, node: Node):
        ast_type = node.ast_type
        if ast_type:
            method_name = f"visit_{ast_type}"
            visitor = getattr(self, method_name, None)
            if visitor:
                visitor(node)

        if node.children:
            for child in node.children:
                self.visit(child)
