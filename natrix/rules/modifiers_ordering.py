from natrix.ast_node import FunctionDefNode
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class ModifiersOrderingRule(BaseRule):
    """
    Modifiers Ordering Check

    Enforce consistent ordering of function modifiers in Vyper contracts.
    The recommended order is: visibility, mutability, security.
    """

    CODE = "NTX12"
    MESSAGE = "Function '{}' has modifiers in incorrect order. Expected order: visibility (@external/@internal/@deploy), mutability (@pure/@view/@nonpayable/@payable), security (@nonreentrant). Found: {}"

    # Define the correct order of modifier categories
    VISIBILITY_MODIFIERS = {"external", "internal", "deploy"}
    MUTABILITY_MODIFIERS = {"pure", "view", "nonpayable", "payable"}
    SECURITY_MODIFIERS = {"nonreentrant"}

    # Define the expected order: visibility -> mutability -> security
    MODIFIER_ORDER = [VISIBILITY_MODIFIERS, MUTABILITY_MODIFIERS, SECURITY_MODIFIERS]

    def __init__(self):
        super().__init__(
            severity="style",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode):
        # Skip interface functions
        if node.is_from_interface:
            return

        modifiers = node.modifiers
        if not modifiers:
            return

        # Categorize modifiers
        categorized = []
        for modifier in modifiers:
            for idx, category in enumerate(self.MODIFIER_ORDER):
                if modifier in category:
                    categorized.append((idx, modifier))
                    break

        # Check if they are in order
        if not self._is_ordered(categorized):
            self.add_issue(
                node, node.get("name"), ", ".join(f"@{mod}" for mod in modifiers)
            )

    def _is_ordered(self, categorized_modifiers):
        """Check if the categorized modifiers are in the correct order."""
        if len(categorized_modifiers) <= 1:
            return True

        for i in range(1, len(categorized_modifiers)):
            if categorized_modifiers[i][0] < categorized_modifiers[i - 1][0]:
                return False
        return True
