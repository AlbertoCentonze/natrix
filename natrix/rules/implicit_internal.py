from natrix.rules.common import BaseRule
from dpath import get


class ImplicitInternalRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="style",
            code="NTX003",
            message="Internal function '{}' is missing the '@internal' decorator.",
        )

    def visit_FunctionDef(self, node):
        if self.is_constructor(node):
            return

        # Check if the function is internal by examining if it has no 'external' decorator
        is_internal = not any(
            decorator["id"] == "external"
            for decorator in get(node, "decorator_list", default=[])
        )

        # Check if the function already has an 'internal' decorator
        has_internal_decorator = any(
            decorator["id"] == "internal"
            for decorator in get(node, "decorator_list", default=[])
        )

        # Function should be flagged if it is internal and missing the @internal decorator
        if is_internal and not has_internal_decorator:
            function_name = get(node, "name")
            self.add_issue(node, function_name)
