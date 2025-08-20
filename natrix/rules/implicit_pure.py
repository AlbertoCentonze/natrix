from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import (
    BaseRule,
    RuleRegistry,
    _get_staticcall_function_mutability,
)

if TYPE_CHECKING:
    from natrix.ast_node import FunctionDefNode


@RuleRegistry.register
class ImplicitPureRule(BaseRule):
    """
    Implicit Pure Decorator Check

    Detect when pure functions are missing the '@pure' decorator.
    """

    CODE = "NTX5"
    MESSAGE = "Function '{}' does not access state but is not marked as 'pure'."

    def __init__(self) -> None:
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        if node.is_constructor or "pure" in node.modifiers or node.is_from_interface:
            return

        accesses = node.memory_accesses
        read = any(access.type == "read" for access in accesses)
        write = any(access.type == "write" for access in accesses)
        extcalls = node.get_descendants(node_type="ExtCall")
        staticcalls = node.get_descendants(node_type="StaticCall")

        # If there are extcalls, the function is not pure
        if extcalls:
            return

        # If there are staticcalls, check if ALL of them are to pure functions
        if staticcalls:
            all_pure = True
            for staticcall in staticcalls:
                mutability = _get_staticcall_function_mutability(staticcall)
                if mutability != "pure":
                    all_pure = False
                    break

            # If not all staticcalls are pure, this function is not pure
            if not all_pure:
                return

        if not read and not write:
            self.add_issue(node, node.get("name"))
