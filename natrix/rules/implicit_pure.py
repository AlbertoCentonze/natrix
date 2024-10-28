from natrix.rules.common import BaseRule
from dpath import get


class ImplicitPureRule(BaseRule):
    def __init__(self, max_frame_size=20_000):
        super().__init__(
            severity="style",
            code="NTX005",
            message="Function '{}' does not access state but is not marked as 'pure'.",
        )

    def visit_FunctionDef(self, node):
        # Check if the function already has the 'pure' decorator
        has_pure_decorator = any(
            decorator["id"] == "pure"
            for decorator in get(node, "decorator_list", default=[])
        )

        # If the function has a 'pure' decorator, no issue needs to be added
        if has_pure_decorator:
            return

        # Check for any 'self' references in the function body
        references_self = False
        for stmt in get(node, "body", default=[]):
            # Check if 'self' is referenced in any expression within the function
            if "self" in self._find_name_references(stmt):
                references_self = True
                break

        # If there are no references to 'self', the function should be marked as 'pure'
        if not references_self:
            function_name = get(node, "name")
            self.add_issue(node, function_name)

    def _find_name_references(self, node):
        """Recursively find all 'Name' identifiers within a node."""
        references = set()
        if get(node, "ast_type", default=None) == "Name":
            references.add(get(node, "id", default=""))
        elif isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    references.update(self._find_name_references(value))
        elif isinstance(node, list):
            for item in node:
                references.update(self._find_name_references(item))
        return references
