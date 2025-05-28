from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class ImplicitExportRule(BaseRule):
    """
    Implicit Export Check

    Detect when the entirety of a module is being exposed using the `__interface__` expression.
    """

    CODE = "NTX9"
    MESSAGE = "Module '{}' is exposing all its functions. Consider exporting them one by one to make the contract more explicit."

    def __init__(self):
        super().__init__(
            severity="important",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_ExportsDecl(self, node):
        if node.get("annotation.attr") != "__interface__":
            return

        module_name = node.get("annotation.value.id")

        self.add_issue(node, module_name)
