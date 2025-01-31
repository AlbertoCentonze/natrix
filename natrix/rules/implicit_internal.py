from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule


class ImplicitInternalRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="style",
            code="NTX003",
            message="Internal function '{}' is missing the '@internal' decorator.",
        )

    def visit_FunctionDef(self, node: FunctionDefNode):
        if (
            node.is_constructor
            or node.is_from_interface
            or "external" in node.modifiers
            or "internal" in node.modifiers
        ):
            return

        self.add_issue(node, node.get("name"))
