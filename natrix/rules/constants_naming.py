from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import Node


@RuleRegistry.register
class ConstantNamingRule(BaseRule):
    """
    Constant Naming Check

    Detect when a constant is not named in UPPER_SNAKE_CASE.
    """

    CODE = "NTX2"
    MESSAGE = "Constant '{}' should be named in UPPER_SNAKE_CASE"

    def __init__(self) -> None:
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_VariableDecl(self, node: Node) -> None:
        if not node.get("is_constant"):
            return

        var_name = node.get("target.id")

        if not var_name.isupper():
            self.add_issue(node, var_name)
