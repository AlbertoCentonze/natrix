from natrix.rules.common import BaseRule
from dpath import get


class PrintLeftRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="warning",
            code="NTX006",
            message="Found a 'print' statement; consider removing it in production code.",
        )

    def visit_Name(self, node):
        # Check if the name identifier is 'print'
        if get(node, "id", default="") == "print":
            self.add_issue(node)
