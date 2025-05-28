from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule, RuleRegistry


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

    def __init__(self, max_frame_size=20_000):
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.max_frame_size = max_frame_size

    def visit_FunctionDef(self, node: FunctionDefNode):
        # FunctionDef can also appear in inline interfaces,
        # however this rule is not relevant for them.
        if node.is_from_interface:
            return

        function_name = node.get("name")
        frame_size = self.compiler_output.get(
            f"metadata.function_info.{function_name}.frame_info.frame_size"
        )

        if frame_size > self.max_frame_size:
            # Add an issue if the frame size exceeds the threshold
            self.add_issue(node, function_name, frame_size)
