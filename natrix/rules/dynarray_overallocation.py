from vyper.semantics.analysis.common import VyperNodeVisitorBase
from vyper import ast as vy_ast

code = """MAX_LENGTH: constant(uint256) = 1
y: DynArray[uint256, MAX_LENGTH]"""


class DynArrayOverallocation(VyperNodeVisitorBase):
    def __init__(self, allocation_threshold=1000):
        self.allocation_threshold = allocation_threshold
        self.result = []

    def __call__(self, ast):
        self.ast = ast
        self.visit(self.ast)

    # TODO refactor visit into a generic subclass
    # there's nothing specific to this rule
    def visit(self, node, **kwargs):
        for c in node.get_children():
            self.visit(c)

        for class_ in node.__class__.mro():
            ast_type = class_.__name__

            visitor_fn = getattr(self, f"visit_{ast_type}", None)
            if visitor_fn and (result := visitor_fn(node)) is not None:
                self.result.append(result)

        return node

    def visit_Name(self, node: vy_ast.Name):
        if node.id != "DynArray":
            return

        # obtain the limit of the array
        max_length = node.get_ancestor().get_children()[1].get_children()[1]

        if isinstance(max_length, vy_ast.Int):
            value = max_length.value
            if  value >= self.allocation_threshold:
                return value, max_length
        elif isinstance(max_length, vy_ast.Name):
            value = max_length.get_folded_value().value
            if value >= self.allocation_threshold:
                return value, max_length
        return None