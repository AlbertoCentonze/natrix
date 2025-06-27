from __future__ import annotations

from typing import TYPE_CHECKING

from natrix.rules.common import BaseRule, RuleRegistry

if TYPE_CHECKING:
    from natrix.ast_node import Node


@RuleRegistry.register
class UnusedImportsRule(BaseRule):
    """
    Unused Imports Check

    Detects imports that are defined but never used in the contract.
    This helps identify unnecessary dependencies and keep the codebase clean.

    Example:
        from ethereum.ercs import IERC20  # This import will be reported if never used
    """

    CODE = "NTX14"
    MESSAGE = "Import '{}' is not used."

    def __init__(self) -> None:
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )
        self.imports: dict[str, Node] = {}
        self.used_names: set[str] = set()

    def before_traversal(self) -> None:
        """Reset state before each analysis."""
        self.imports = {}
        self.used_names = set()

    def visit_ImportFrom(self, node: Node) -> None:
        """Track import statements during traversal."""
        # Get the imported name (either alias or actual name)
        import_name = node.get("alias") or node.get("name")
        if import_name:
            self.imports[import_name] = node

    def visit_Name(self, node: Node) -> None:
        """Track all name usages in the contract."""
        name_id = node.get("id")
        if name_id:
            self.used_names.add(name_id)

    def after_traversal(self) -> None:
        """After traversal, report unused imports."""
        for import_name, import_node in self.imports.items():
            if import_name not in self.used_names:
                self.add_issue(import_node, import_name)
