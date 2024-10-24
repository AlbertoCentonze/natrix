import vvm
import json


def parse_source(source: str):
    pass  # TODO


def parse_file(file_path):
    vvm.install_vyper("0.4.0")
    output = vvm.compile_files([file_path], output_format="annotated_ast", vyper_version="0.4.0")
    metadata = vvm.compile_files([file_path], output_format="metadata", vyper_version="0.4.0")
    # convert ast from string to python dict
    output = json.loads(output)
    output["metadata"] = metadata
    return output


class VyperASTVisitor:
    def visit(self, node):
        if isinstance(node, dict):
            ast_type = node.get('ast_type')
            if ast_type:
                method_name = f'visit_{ast_type}'
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
