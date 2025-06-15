from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import FunctionDefNode


@RuleRegistry.register
class ImplicitInternalRule(BaseRule):
    """
    Implicit Internal Decorator Check

    Detect when internal functions are missing the '@internal' decorator.
    """

    CODE = "NTX3"
    MESSAGE = "Internal function '{}' is missing the '@internal' decorator."

    def __init__(self) -> None:
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        if (
            # not an internal function
            not node.is_runtime_code
            or node.is_external
            # explicit internal
            or "internal" in node.modifiers
        ):
            return

        self.add_issue(node, node.get("name"))
