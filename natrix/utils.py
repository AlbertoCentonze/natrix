import vyper.ast as vy_ast
from vyper.semantics.analysis.constant_folding import constant_fold


def parse_file_to_ast(file_path):
    content = None

    with open(file_path, "r") as file:
        content = file.read()

    ast = vy_ast.parse_to_ast(content, resolved_path=file_path[2:])
    constant_fold(ast)
    return ast


def parse_source_to_ast(source):
    ast = vy_ast.parse_to_ast(source)
    constant_fold(ast)
    return ast
