from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import Node


@RuleRegistry.register
class PrintLeftRule(BaseRule):
    """
    Print Left Check

    Detect when a 'print' statement is used in the code.
    """

    CODE = "NTX6"
    MESSAGE = "Found a 'print' statement; consider removing it in production code."

    def __init__(self) -> None:
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_Call(self, node: Node) -> None:
        func_id = node.get("func.id")
        if func_id == "print":
            self.add_issue(node)
