from natrix.ast_node import Node
from natrix.rules.common import BaseRule


class PrintLeftRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="warning",
            code="NTX006",
            message="Found a 'print' statement; consider removing it in production code.",
        )

    def visit_Call(self, node: Node):
        func_id = node.get("func.id")
        if func_id == "print":
            self.add_issue(node)
