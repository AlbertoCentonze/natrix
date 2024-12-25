import ast
import os
import subprocess

import json
from natrix.ast_node import Node


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
    # For each path add a '-p /the/path' flag to the compiler
    paths = [item for p in _obtain_sys_path() for item in ["-p", p]]

    # We run vyper from 'uv tool'. This allows us to easily switch the compiler version
    # and have it downloaded and cached on any system.
    # We use the offline mode to allow vyper to run even when the computer is not
    # connected to the internet, if the correct vyper version was already downloaded.
    command = ["uvx", "vyper@0.4.0", "-f", formatting, filename] + paths

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    try:
        return json.loads(stdout)
    except Exception:
        # TODO change error level
        raise Exception(
            f"Something went wrong when compiling the vyper file. The compiler returned the following error: \n {stderr}"
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
