from natrix.rules.common import BaseRule
from dpath import get


class ImplicitViewRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="style",
            code="NTX004",
            message="Function '{}' reads contract state but is not marked as 'view'.",
        )

    def visit_FunctionDef(self, node):
        # Check if the function is already marked as 'view'
        has_view_decorator = any(
            decorator["id"] == "view"
            for decorator in get(node, "decorator_list", default=[])
        )

        # If the function has a 'view' decorator, no issue needs to be added
        if has_view_decorator:
            return

        # Check if the function reads state variables (self.<variable>) without modifying them
        reads_state = False
        modifies_state = False

        for stmt in get(node, "body", default=[]):
            # Check for any assignment to 'self.<variable>', indicating state modification
            if stmt["ast_type"] == "Assign":
                target = get(stmt, "target")
                if (
                    target["ast_type"] == "Attribute"
                    and target["value"]["id"] == "self"
                ):
                    modifies_state = True
                    break

            # Check for any attribute access to 'self.<variable>', indicating state read
            if stmt["ast_type"] == "Return":
                value = get(stmt, "value")
                if value["ast_type"] == "Attribute" and value["value"]["id"] == "self":
                    reads_state = True

        # If it reads state but does not modify it, it should be marked as 'view'
        if reads_state and not modifies_state:
            function_name = get(node, "name")
            self.add_issue(node, function_name)
