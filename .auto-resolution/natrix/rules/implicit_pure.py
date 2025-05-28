from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class ImplicitPureRule(BaseRule):
    """
    Implicit Pure Decorator Check

    Detect when pure functions are missing the '@pure' decorator.
    """

    CODE = "NTX5"
    MESSAGE = "Function '{}' does not access state but is not marked as 'pure'."

    def __init__(self):
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode):
        if node.is_constructor or "pure" in node.modifiers:
            return

        accesses = node.memory_accesses
        read = any(access.type == "read" for access in accesses)
        write = any(access.type == "write" for access in accesses)

        if not read and not write:
            self.add_issue(node, node.get("name"))
