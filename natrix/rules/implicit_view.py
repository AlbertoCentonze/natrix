from natrix.ast_node import Node
from natrix.rules.common import BaseRule
from natrix.rules.storage_analysis import get_memory_accesses


class ImplicitViewRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="style",
            code="NTX004",
            message="Function '{}' reads contract state but is not marked as 'view'.",
        )

    def visit_FunctionDef(self, node: Node):
        if node.is_constructor or "view" in node.modifiers:
            return

        accesses = get_memory_accesses(node)
        read = any(access.type == "read" for access in accesses)
        write = any(access.type == "write" for access in accesses)

        if read and not write:
            self.add_issue(node, node.get("name"))
