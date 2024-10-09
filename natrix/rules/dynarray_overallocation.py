from vyper import ast as vy_ast

from natrix.rules.common import BaseRule


class DynArrayOverallocation(BaseRule):
    # TODO compute threshold in terms of storage slots
    # def __init__(self, allocation_threshold=1000):
    #     self.allocation_threshold = allocation_threshold

    def __init__(self, allocation_threshold=1000):
        super().__init__("Warning", "W1", "{} DynArray has an upper bound of {} which could imply very high gas costs")
        self.allocation_threshold = allocation_threshold

    def visit_Name(self, node: vy_ast.Name):
        if node.id != "DynArray":
            return

        # obtain the limit of the array
        max_length = node.get_ancestor().get_children()[1].get_children()[1]

        var_name = node.get_ancestor().get_ancestor().target.id

        if isinstance(max_length, vy_ast.Int):
            value = max_length.value
            if value >= self.allocation_threshold:
                return max_length.lineno, max_length.col_offset, [var_name, value]
        elif isinstance(max_length, vy_ast.Name):
            value = max_length.get_folded_value().value
            if value >= self.allocation_threshold:
                return max_length.lineno, max_length.col_offset, [var_name, value]
        return None
