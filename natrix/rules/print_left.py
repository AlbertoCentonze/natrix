from natrix.ast_tools import get
from natrix.rules.common import BaseRule


class PrintLeftRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="warning",
            code="NTX006",
            message="Found a 'print' statement; consider removing it in production code.",
        )

    def visit_Call(self, node):
        func_id = get(node, "func.id")
        if func_id == "print":
            self.add_issue(node)
        # Continue visiting child nodes if necessary
        self.generic_visit(node)
