from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class ImplicitInternalRule(BaseRule):
    """
    Implicit Internal Decorator Check

    Detect when internal functions are missing the '@internal' decorator.
    """

    CODE = "NTX3"
    MESSAGE = "Internal function '{}' is missing the '@internal' decorator."

    def __init__(self):
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode):
        print(f"Checking function: {node.get('name')}")
        print(f"{node.is_runtime_code=}")
        print(f"{node.is_external=}")
        if (
            # not an internal function
            not node.is_runtime_code
            or node.is_external
            # explicit internal
            or "internal" in node.modifiers
        ):
            return

        self.add_issue(node, node.get("name"))
