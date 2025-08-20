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
        extcalls = node.get_descendants(node_type="ExtCall")
        staticcalls = node.get_descendants(node_type="StaticCall")

        # Check staticcalls for view function calls
        has_view_staticcalls = False
        if staticcalls:
            all_pure = True
            for staticcall in staticcalls:
                mutability = _get_staticcall_function_mutability(staticcall)
                if mutability == "view":
                    has_view_staticcalls = True
                    all_pure = False
                elif mutability != "pure":
                    all_pure = False

            # If all staticcalls are pure, let implicit_pure handle this
            if all_pure:
                return

        # Function needs @view if it:
        # 1. Reads from storage, OR
        # 2. Makes staticcalls to view functions
        # AND doesn't write to storage or make extcalls
        if (read or has_view_staticcalls) and not (write or extcalls):
            self.add_issue(node, node.get("name"))
