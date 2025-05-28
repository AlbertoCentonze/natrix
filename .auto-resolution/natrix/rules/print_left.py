from natrix.ast_node import Node
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class PrintLeftRule(BaseRule):
    """
    Print Left Check

    Detect when a 'print' statement is used in the code.
    """

    CODE = "NTX6"
    MESSAGE = "Found a 'print' statement; consider removing it in production code."

    def __init__(self):
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_Call(self, node: Node):
        func_id = node.get("func.id")
        if func_id == "print":
            self.add_issue(node)
