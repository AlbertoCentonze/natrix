from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import FunctionDefNode


@RuleRegistry.register
class MemoryExpansionRule(BaseRule):
    """
    Memory Expansion Check

    Detect when memory expansion is too big compared to the specified threshold.
    This can be useful to spot when dynarrays with a large number of elements
    are being passed by value.
    """

    CODE = "NTX1"
    MESSAGE = "Function '{}' has a large frame size of {} bytes."

    def __init__(self, max_frame_size: int = 20_000) -> None:
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.max_frame_size = max_frame_size

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        # FunctionDef can also appear in inline interfaces,
        # however this rule is not relevant for them.
        if node.is_from_interface:
            return

        function_name = node.get("name")
        # The compiler adds numbers to function names in metadata
        # (e.g., "dispatch_fees (12)")
        # We need to find the matching entry
        # TODO numbering is introduced in case of function names overlapping
        # across modules. We currently don't support this case.
        frame_size = None
        for func_key in self.compiler_output.get("metadata.function_info", {}):
            if func_key.startswith(f"{function_name} ("):
                frame_size = self.compiler_output.get(
                    f"metadata.function_info.{func_key}.frame_info.frame_size"
                )
                break

        # This rule can't check all the functions because the compiler
        # erases functions that are unused directly in the module.
        # (i.e. functions imported by other modules).
        # TODO codegen some wrapper function that fakes usage.
        if frame_size is not None and frame_size > self.max_frame_size:
            # Add an issue if the frame size exceeds the threshold
            self.add_issue(node, function_name, frame_size)
