from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule


class ImplicitPureRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="style",
            code="NTX005",
            message="Function '{}' does not access state but is not marked as 'pure'.",
        )

    def visit_FunctionDef(self, node: FunctionDefNode):
        if node.is_constructor or "pure" in node.modifiers:
            return

        accesses = node.memory_accesses
        read = any(access.type == "read" for access in accesses)
        write = any(access.type == "write" for access in accesses)

        if not read and not write:
            self.add_issue(node, node.get("name"))
