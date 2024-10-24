from natrix.rules.common import BaseRule
from dpath import get


class MemoryExpansionRule(BaseRule):
    def __init__(self, max_frame_size=1024):
        super().__init__(
            severity="warning",
            code="MEMORY_EXPANSION",
            message="Function '{}' has a large frame size of {} bytes.",
        )
        self.max_frame_size = max_frame_size

    def visit_FunctionDef(self, node):
        function_name = get(node, "name")
        frame_info = get(
            self.compiler_output, f"metadata/function_info/{function_name}/frame_info"
        )
        frame_size = get(frame_info, "frame_size")

        if frame_size > self.max_frame_size:
            # Add an issue if the frame size exceeds the threshold
            self.add_issue(node, function_name, frame_size)

        # Continue visiting the function body if needed
        self.visit(get(node, "body"))
