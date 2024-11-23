from dpath import get
import subprocess
import json


def vyper_compile(filename, formatting):
    command = ["uvx", "vyper@0.4.0", "-f", formatting, filename]

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    return json.loads(stdout)


def parse_file(file_path):
    ast = vyper_compile(file_path, "annotated_ast")
    metadata = vyper_compile(file_path, "metadata")

    ast["metadata"] = metadata
    return ast


class VyperASTVisitor:
    def visit(self, node):
        if isinstance(node, dict):
            ast_type = get(node, "ast_type", default=None)
            if ast_type:
                method_name = f"visit_{ast_type}"
                visitor = getattr(self, method_name, self.generic_visit)
                return visitor(node)
            else:
                return self.generic_visit(node)
        elif isinstance(node, list):
            for item in node:
                self.visit(item)

    def generic_visit(self, node):
        # Recursively visit all child nodes
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                self.visit(value)

    def is_constructor(self, node):
        if not isinstance(node, dict):
            return False

        is_function = get(node, "ast_type", default=None) == "FunctionDef"
        is_constructor = get(node, "name", default=None) == "__init__"

        return is_function and is_constructor
