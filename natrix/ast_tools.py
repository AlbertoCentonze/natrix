import subprocess

import json
from natrix.ast_node import Node


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
    def visit(self, node: Node):
        ast_type = node.ast_type
        if ast_type:
            method_name = f"visit_{ast_type}"
            visitor = getattr(self, method_name, None)
            if visitor:
                visitor(node)

        if len(node.children) > 0:
            for child in node.children:
                self.visit(child)
