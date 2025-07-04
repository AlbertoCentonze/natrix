from __future__ import annotations

from natrix.ast_node import FunctionDefNode, Node
from natrix.rules.common import BaseRule, RuleRegistry


@RuleRegistry.register
class UnusedArgRule(BaseRule):
    """
    Unused Argument Check

    Detects arguments that are declared but never used within a function.

    Example:
        def example_function(unused_arg: uint256): # This line will be reported.
            pass
    """

    CODE = "NTX10"
    MESSAGE = "Function '{}' argument '{}' is never used."

    def __init__(self) -> None:
        super().__init__(
            severity="warning",
            code=self.CODE,
            message=self.MESSAGE,
        )

    def visit_FunctionDef(self, node: FunctionDefNode) -> None:
        # Skip interface function definitions
        if node.is_from_interface:
            return

        # Collect declared arguments in a dictionary, {arg_name: arg_node}
        declared_args = {}
        for arg_info in node.get("args.args"):
            arg_node = Node(arg_info)
            arg_name = arg_node.get("arg")
            if arg_name is not None:
                declared_args[arg_name] = arg_node

        # Gather all 'Name' nodes to see which arguments actually appear
        # in the function body
        all_names = node.get_descendants(node_type="Name")
        for name_node in all_names:
            used_name = name_node.get("id")
            declared_args.pop(used_name, None)  # Remove used arguments

        # Report any remaining arguments that were never used
        for unused_arg, arg_node in declared_args.items():
            # Note the first argument is the node defining the argument itself,
            # so the issue's reported position is the line where the arg is declared.
            self.add_issue(arg_node, node.get("name"), unused_arg)
