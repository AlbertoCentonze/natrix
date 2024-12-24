from natrix.rules.common import BaseRule


class ImplicitExportRule(BaseRule):
    def __init__(self):
        super().__init__(
            severity="important",
            code="NTX00TODO",
            message="Module '{}' is exposing all its functions. Consider exporting them one by one to make"
            "the contract more explicit.",
        )

    def visit_ExportsDecl(self, node):
        if node.get("annotation.attr") != "__interface__":
            return

        module_name = node.get("annotation.value.id")

        self.add_issue(node, module_name)
