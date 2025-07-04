from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import FunctionDefNode


@RuleRegistry.register
class ImplicitViewRule(BaseRule):
    """
    Implicit View Decorator Check

    Detect when view functions are missing the '@view' decorator.
    """

    CODE = "NTX4"
    MESSAGE = "Function '{}' reads contract state but is not marked as 'view'."

    def __init__(self) -> None:
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        if (
            node.is_constructor
            or "view" in node.modifiers
            or "pure" in node.modifiers
            or node.is_from_interface
        ):
            return

        accesses = node.memory_accesses
        read = any(access.type == "read" for access in accesses)
        write = any(access.type == "write" for access in accesses)

        if read and not write:
            self.add_issue(node, node.get("name"))
